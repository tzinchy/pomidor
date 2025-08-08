import pandas as pd
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from repository.database import project_managment_session
from repository.oracledb import OracleClient
from depends import get_oracle_client
from sqlalchemy import text
from pytz import timezone

class Spd1Repository:

    def __init__(self):
        self.db = project_managment_session
        self.tz = timezone('Europe/Moscow')

    async def insert_data(self, df):

        for col in ['APPDATE', 'PGUDATE', 'CREATEDATE', 'SIGNEDDOCDATE']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')  # если ещё не datetime
                df[col] = df[col].dt.tz_localize('Europe/Moscow', ambiguous='NaT', nonexistent='NaT')

        df = df.astype(object).where(pd.notnull(df), None)
        ### ДОПИСАТЬ!!!
        sql = '''
            INSERT INTO public.spd1 
                (offer_id, 
                appid, 
                appname, 
                appdate, 
                pgudate, 
                kpu_num, 
                cad_num, 
                docname, 
                signstatus, 
                createdate, 
                signeddocname, 
                signeddocdate, 
                updated_at)
            VALUES 
                (:offer_id, 
                :APPID, 
                :APPNAME, 
                :APPDATE, 
                :PGUDATE, 
                :ACTDOCNUM, 
                :CADNUM, 
                :DOCNAME, 
                :SIGNSTATUS, 
                :CREATEDATE, 
                :SIGNEDDOCNAME, 
                :SIGNEDDOCDATE, 
                now())
            ON CONFLICT (offer_id, appid) DO UPDATE
            SET
                appname = EXCLUDED.appname,
                appdate = EXCLUDED.appdate,
                pgudate = EXCLUDED.pgudate,
                kpu_num = EXCLUDED.kpu_num,
                cad_num = EXCLUDED.cad_num,
                docname = EXCLUDED.docname,
                signstatus = EXCLUDED.signstatus,
                createdate = EXCLUDED.createdate,
                signeddocname = EXCLUDED.signeddocname,
                signeddocdate = EXCLUDED.signeddocdate,
                updated_at = NOW();
            '''
        
                # Приводим DataFrame в список словарей (list[dict]), подходящих под named params
        records = df.to_dict(orient='records')
        try:
            async with self.db() as session:
                async with session.begin():
                    for record in records:
                        await session.execute(text(sql), record)
                        return 200, 'data has been inserted'
        except Exception as e:
            raise HTTPException(500, details=str(e))
        

    async def get_spd_1_orders(self, 
                               df: pd.DataFrame = pd.DataFrame(), 
                               client: OracleClient = None, 
                               search_by_appid :bool = False):
        print(f'SPD1Repository.get_spd_1_orders search_by_appid: {search_by_appid}')
        if search_by_appid:
            print(f'SPD1Repository.get_spd_1_orders search_by_appid is True')
            search_id = 'a.appid'
            df_col = 'appid'
        else:
            search_id = 'sdk.ACTDOCNUM'
            df_col = 'kpu'

        ids = df[df_col].tolist()
        if search_by_appid:
            df = df.drop([df_col], axis=1)
        print(f'SPD1Repository.get_spd_1_orders ids are: {ids}')
        binds = ", ".join([f":{i}" for i in range(len(ids))])
        params = {str(i): id_ for i, id_ in enumerate(ids)}

        sql = f"""
        SELECT a.appid, a.APPNAME, a.APPDATE, a.PGUDATE,
            sdk.actdocnum, f.CADNUM, a2.DOCNAME, a2.SIGNSTATUS, a2.CREATEDATE,
            a2.SIGNEDDOCNAME, a2.SIGNEDDOCDATE
        FROM GOSUSLDOC.APPLICATIONS a
        LEFT JOIN GOSUSLDOC.APPLICATIONS_DK sdk ON a.APPID = sdk.APPID
        LEFT JOIN GOSUSLDOC.FLATS f ON a.APPID = f.APPID
        LEFT JOIN GOSUSLDOC.APPDOCS a2 ON a.APPID = a2.APPID
        WHERE a.REGID = 934 AND {search_id} IN ({binds})
        ORDER BY a.PGUDATE DESC
        """
        result = await run_in_threadpool(
        lambda: client.fetchall(sql, params)
        )

        df_spd = pd.DataFrame(result)

        df = df.merge(df_spd, how='inner', left_on='kpu', right_on='ACTDOCNUM')
        print(df.columns)
        return df
    

    async def get_docs_for_update(self):
        '''
        Get appids where sign status is not 0 (rejected) and which have no signdocdate/name
        Anyway this is equally means that this order has "in work" status
        '''

        sql = '''
            SELECT kpu_num, offer_id, appid from public.spd1
            WHERE 
            signeddocdate IS NULL
            AND signeddocname IS NULL
            AND (signstatus <> 0 OR signstatus IS NULL)
        '''
        try:
            async with self.db() as session:
                async with session.begin():
                    result = await session.execute(text(sql))
                    rows = result.all()  # список кортежей
                    df = pd.DataFrame(rows, columns=["kpu", "offer_id", "appid"])
                    return df
        except Exception as e:
            print(f"Ошибка при получении документов: {e}")
            return pd.DataFrame()  # возвращаем пустой DataFrame, чтобы не падало