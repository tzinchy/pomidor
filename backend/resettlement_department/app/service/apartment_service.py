from repository.apartment_repository import ApartmentRepository

class ApartmentService:
    @staticmethod
    async def get_district(apart_type: str):
        """
        Получить список районов.
        """
        return await ApartmentRepository.get_districts(apart_type)

    @staticmethod
    async def get_municipal_districts(apart_type: str, districts: list[str]):
        """
        Получить список областей по районам.
        """
        return await ApartmentRepository.get_municipal_district(apart_type, districts)

    @staticmethod
    async def get_house_addresses(apart_type: str, areas: list[str]):
        """
        Получить список адресов домов по районам и областям.
        """
        return await ApartmentRepository.get_house_addresses(apart_type,  areas)
    
    @staticmethod
    async def get_apartments(apart_type: str, house_addresses: list[str]):
        """
        Получаем все квартиры по улице
        """
        return await ApartmentRepository.get_apartments(apart_type, house_addresses)

    @staticmethod
    async def get_apartment_by_id(apartment_id, apart_type): 
        """
        Получить всю информацию по квартире
        """
        return await ApartmentRepository.get_apartment_by_id(apartment_id, apart_type)
