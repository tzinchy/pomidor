import os
from pathlib import Path

import pandas as pd
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from repository.order_repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    async def get_excel_order(self):
        try:
            folders = [Path("uploads")]
            for folder in folders:
                folder.mkdir(parents=True, exist_ok=True)

            output_path = os.path.join(os.getcwd(), "././uploads", "order_decisions.xlsx")
            rows, cols = await self.repository.get_excel_order()
            if rows:
                df = pd.DataFrame(rows, columns=cols)
            else:
                df = pd.DataFrame([], columns=cols)
            df.drop(columns=["created_at", "updated_at"], inplace=True)

            print("DataFrame created:")
            print(df)
            await run_in_threadpool(df.to_excel, output_path, index=False)
            print(f"Data successfully saved to {output_path}")
            return {"filepath": output_path}
        except Exception as e:
            return {"error": str(e)}
        
    async def get_stat(self):
        return await self.repository.get_stat()