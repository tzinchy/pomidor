from repository.apartment import FamilyStructureRepository, NewApartmentRepository
from pydantic import BaseModel

class FamilyStructureService:
    @staticmethod
    async def fetch_family_structures_with_needs() -> list:
        """
        Service to fetch family structures with apartment needs.
        """
        return await FamilyStructureRepository.get_family_structures_with_apartment_needs()

class NewApartmentService:
    @staticmethod
    async def fetch_new_apartments() -> list:
        """
        Service to fetch new apartment data.
        """
        return await NewApartmentRepository.get_new_apartments()
    

class ApartTypeResponse(BaseModel):
    apart_type: str

class ApartTypeService:
    _current_apart_type: str = "FamilyStructure"

    @classmethod
    def get_apart_type(cls) -> str:
        return cls._current_apart_type

    @classmethod
    def set_apart_type(cls, apart_type: str):
        if apart_type not in ["FamilyStructure", "NewApartment"]:
            raise ValueError("Invalid apart_type")
        cls._current_apart_type = apart_type

