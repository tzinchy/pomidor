from typing import Optional, List
from repository.apartment_repository import ApartmentRepository

class ApartmentService:
    def __init__(self, repository: ApartmentRepository):
        self.apartment_repository = repository

    async def get_district(self, apart_type: str):
        """Получить список районов."""
        return await self.apartment_repository.get_districts(apart_type)

    async def get_municipal_districts(self, apart_type: str, districts: List[str]):
        """Получить список областей по районам."""
        return await self.apartment_repository.get_municipal_district(
            apart_type, districts
        )

    async def get_house_addresses(self, apart_type: str, municipal_districts: List[str]):
        """Получить список адресов домов по районам и областям."""
        return await self.apartment_repository.get_house_addresses(apart_type, municipal_districts)

    async def get_apartments(
        self,
        apart_type: str,
        house_addresses: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        municipal_districts: Optional[List[str]] = None,
        floor: Optional[int] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        area_type: str = "full_living_area",
        room_count: Optional[List[int]] = None  # Добавляем новый параметр
    ):
        return await self.apartment_repository.get_apartments(
            apart_type=apart_type,
            house_addresses=house_addresses,
            districts=districts,
            municipal_districts=municipal_districts,
            floor=floor,
            min_area=min_area,
            max_area=max_area,
            area_type=area_type,
            room_count=room_count  # Передаем новый параметр
        )

    async def get_apartment_by_id(self, apartment_id, apart_type):
        """Получить всю информацию по квартире."""
        return await self.apartment_repository.get_apartment_by_id(apartment_id, apart_type)
    
    async def get_house_address_with_room_count(self, apart_type):
        result = await self.apartment_repository.get_house_address_with_room_count(apart_type)
        formatted_result = []
        for address, room_counts in result:
            room_details = ", ".join(f"{room} к. - {count}" for room, count in room_counts.items())
            formatted_result.append((address, room_details))
        return formatted_result
    '''
    async def switch_apartment_needs(self, first_apartment_id, second_apartment_id):
        return await self.apartment_repository.switch_apartment(self, first_apartment_id, second_apartment_id)
    '''
