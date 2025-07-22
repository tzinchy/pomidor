from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


class OrderRepository:
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_excel_order(self):
        query = text("""SELECT 
                        od.*,
                        COALESCE(na_by_cad.house_address, na_by_unom.house_address) AS house_address,
                        COALESCE(na_by_cad.apart_number, na_by_unom.apart_number) AS apart_number,
                        COALESCE(na_by_cad.new_apart_id, na_by_unom.new_apart_id) AS new_apart_id
                    FROM 
                        order_decisions od
                    LEFT JOIN (
                        SELECT DISTINCT ON (cad_num) cad_num, house_address, apart_number, new_apart_id
                        FROM new_apart
                        ORDER BY cad_num
                    ) na_by_cad ON od.cad_num = na_by_cad.cad_num
                    LEFT JOIN (
                        SELECT DISTINCT ON (unom, un_kv) unom, un_kv, house_address, apart_number, new_apart_id
                        FROM new_apart
                        ORDER BY unom, un_kv
                    ) na_by_unom ON od.unom = na_by_unom.unom AND od.un_kv = na_by_unom.un_kv;""")
        results_list = []
        column_names = []

        async with self.db() as session:
            result_proxy = await session.execute(query)
            column_names = list(result_proxy.keys())
            results_list = result_proxy.all()
        return results_list, column_names

    async def get_stat(self):
        query = text(
            """
            SELECT COUNT(*), 'кпу' FROM old_apart 
            UNION 
            SELECT COUNT(*), 'ресурс' FROM new_apart 
            UNION 
            SELECT COUNT(*), 'выписки' FROM order_decisions
            UNION 
            SELECT COUNT(*), 'подборы' FROM offer
            ORDER BY 2
            """
        )
        stat = {}
        async with self.db() as session:
            result = await session.execute(query)
        for v, k in result:
            stat[k] = v
        return stat
