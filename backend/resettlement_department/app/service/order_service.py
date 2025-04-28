import os
from pathlib import Path

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
            print(output_path)
            await self.repository.get_excel_order(output_path)

            return FileResponse(
                path=output_path,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename="order_decisions.xlsx",
            )
        except Exception as e:
            return {"error": str(e)}
        
    async def get_stat(self):
        return await self.repository.get_stat()