import json

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


class OrderRepository:
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_excel_order(self, filepath):
        query = text("SELECT * FROM public.order_decisions")
        results_list = []
        column_names = []

        async with self.db() as session:
            result_proxy = await session.execute(query)
            column_names = list(result_proxy.keys())
            results_list = result_proxy.all()

        if results_list:
            df = pd.DataFrame(results_list, columns=column_names)
        else:
            df = pd.DataFrame([], columns=column_names)
        df.drop(columns=["created_at", "updated_at"], inplace=True)

        print("DataFrame created:")
        print(df)
        df.to_excel(filepath, index=False)
        print(f"Data successfully saved to {filepath}")
    
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
