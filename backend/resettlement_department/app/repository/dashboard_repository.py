from repository.database import get_db_connection_dashboard
from utils.sql_reader import read_sql_query, async_read_sql_query
from core.config import RENOVATION_FILE_PATH, RECOMMENDATION_DASHBOARD_FILE_PATH
from core.logger import logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# add comment for test deploy
class DashboardRepository:
    def __init__(self, db : sessionmaker): 
        self.db = db

    def get_tables_data(self) -> list[tuple]:
        conn = get_db_connection_dashboard()
        cursor = conn.cursor()
        query = read_sql_query(f"{RENOVATION_FILE_PATH}/DashboardTables.sql")
        logger.query(query)
        cursor.execute(query)

        _building_info = cursor.fetchall()
        print(_building_info)
        return _building_info

    def get_dashboard_details(self):
        conn = get_db_connection_dashboard()
        cursor = conn.cursor()
        query = read_sql_query(f"{RENOVATION_FILE_PATH}/Dashboard.sql")
        logger.query(query)
        cursor.execute(query)

        _dashboard_data = cursor.fetchall()

        return _dashboard_data

    def get_building_details(self, building_id: int):
        conn = get_db_connection_dashboard()
        cursor = conn.cursor()
        query = read_sql_query(f"{RENOVATION_FILE_PATH}/BuildingDetails.sql")
        params = (building_id,)
        logger.query(query, params)
        cursor.execute(query, params)
        _building_data = cursor.fetchall()

        return _building_data

    async def get_district_and_municipal_district_attempt(self): 
        async with self.db() as session: 
            query = await async_read_sql_query(f"{RECOMMENDATION_DASHBOARD_FILE_PATH}/DistrictAndMunicipalDistrict.sql")
            result = await session.execute(text(query))
            return result.fetchall()
        
    async def get_house_address_with_attempt(self): 
        async with self.db() as session: 
            query = await async_read_sql_query(f"{RECOMMENDATION_DASHBOARD_FILE_PATH}/HouseAddressWithAttempt.sql")
            result = await session.execute(text(query))
            return result.fetchall()

    async def get_district_with_attempt(self): 
        async with self.db() as session: 
            query = await async_read_sql_query(f"{RECOMMENDATION_DASHBOARD_FILE_PATH}/District.sql")
            result = await session.execute(text(query))
            return result.fetchall()