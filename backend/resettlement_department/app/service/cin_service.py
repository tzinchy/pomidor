import os
from pathlib import Path

import pandas as pd
from fastapi.concurrency import run_in_threadpool
from repository.cin_repository import CinRepository
from fastapi import HTTPException, status
from typing import Optional, List

class CinService:
    def __init__(self, repository: CinRepository):
        self.repository = repository

    async def get_cin(self):
        return await self.repository.get_cin()
    
    async def update_cin(self, cin):
        return await self.repository.update_cin(cin=cin)
    
    async def create_cin(self, cin):
        try:
            return await self.repository.create_cin(cin)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_cin_district(self, apart_type: str):
        return await self.repository.get_cin_districts()

    async def get_cin_municipal_districts(self, apart_type: str, districts: List[str]):
        return await self.repository.get_cin_municipal_district(
            districts=districts
        )

    async def get_cin_house_addresses(
        self, apart_type: str, municipal_districts: List[str] = None, district : List[str] = None
    ):
        return await self.repository.get_cin_house_addresses(
            municipal_districts, district=district
        )

