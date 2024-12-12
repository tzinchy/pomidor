from sqlalchemy import text
from database import async_session_maker
from models.apartment import FamilyStructureWithApartmentNeeds, NewApartment

class FamilyStructureRepository:
    @staticmethod
    async def get_family_structures_with_apartment_needs() -> list[FamilyStructureWithApartmentNeeds]:
        """
        Fetch family structures with apartment needs from the database.
        """
        async with async_session_maker() as session:
            query = text("""
                SELECT affair_id, district, house_address, apart_number 
                FROM public.family_structure
                JOIN public.family_apartment_needs USING (affair_id)
            """)
            result = await session.execute(query)
            rows = result.fetchall()
            return [FamilyStructureWithApartmentNeeds(**dict(row)) for row in rows]

class NewApartmentRepository:
    @staticmethod
    async def get_new_apartments() -> list[NewApartment]:
        """
        Fetch new apartment data from the database.
        """
        async with async_session_maker() as session:
            query = text("""
                SELECT up_id, district, area, house_address 
                FROM new_apart
            """)
            result = await session.execute(query)
            rows = result.fetchall()
            return [NewApartment(**dict(row)) for row in rows]
