import os
from pathlib import Path

import pandas as pd
from fastapi.concurrency import run_in_threadpool
from repository.cin_repository import CinRepository


class CinService:
    def __init__(self, repository: CinRepository):
        self.repository = repository

    async def get_cin(self):
        return await self.repository.get_cin()