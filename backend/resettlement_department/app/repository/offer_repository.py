from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


class OfferRepository:
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_excel_offer(self):
        query = text("""WITH offer_unnst AS (
                SELECT offer_id, affair_id, KEY::bigint as new_apart_id, VALUE->>'outcoming_date' as outcoming_date, (value->>'status_id')::int as status_id
                from offer,
                jsonb_each (new_aparts)
            )
            select offer_id, outcoming_date, old_apart.affair_id, old_apart.house_address as old_house_address, old_apart.apart_number as old_apart_number, old_apart.fio as fio, 
            new_apart.new_apart_id, new_apart.house_address as new_apart_house_address, new_apart.apart_number, status
            from offer_unnst
            left join old_apart on old_apart.affair_id = offer_unnst.affair_id 
            left join new_apart on new_apart.new_apart_id = offer_unnst.new_apart_id
            left join status on status.status_id = offer_unnst.status_id
            ;""")
        results_list = []
        column_names = []

        async with self.db() as session:
            result_proxy = await session.execute(query)
            column_names = list(result_proxy.keys())
            results_list = result_proxy.all()
            print(results_list, column_names)
        return results_list, column_names

    async def use_strict_update_offer_status(self):
        async with self.db() as session:
            await session.execute(text("UPDATE offer SET updated_at = NOW()"))
        return {"done": "ok"}
