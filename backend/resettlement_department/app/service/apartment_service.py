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
        room_count: Optional[List[int]] = None,
        is_queue : bool = None,
        is_private : bool = None
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
            room_count=room_count,
            is_queue=is_queue,
            is_private=is_private
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
    
    async def switch_apartment(self, first_apartment_id, second_apartment_id):
        return await self.apartment_repository.switch_apartment(first_apartment_id, second_apartment_id)
    
    async def manual_matching(self, old_apart_id, new_apart_id): 
        return await self.apartment_repository.manual_matching(old_apart_id, new_apart_id)
    
    async def get_void_aparts_for_apartment(self, apartmentd_id):
        return await self.apartment_repository.get_void_aparts_for_apartment(apartmentd_id)
    
    async def cancell_matching_for_apart(self, ):
        return await self.apartment_repository()
