import os
from pathlib import Path

import pandas as pd
from fastapi.concurrency import run_in_threadpool
from repository.spd1_repository import Spd1Repository
from repository.oracledb import OracleClient

class Spd1Service:
    def __init__(self, repository: Spd1Repository = Spd1Repository(), client: OracleClient = None):
        self.repository = repository
        self.client = client

    async def update_data(self):

        docs_to_update = await self.repository.get_docs_for_update()
        if not docs_to_update.empty:
            return await self.repository.insert_data(await self.repository.get_spd_1_orders(df=docs_to_update, client=self.client, search_by_appid=True))

        else:
            return 200, 'No data to update'