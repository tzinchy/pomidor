from typing import List, Optional

from fastapi import HTTPException
from fastapi import status as http_status
from handlers.httpexceptions import NotFoundException
from repository.new_apart_repository import NewApartRepository
from repository.old_apart_repository import OldApartRepository
from schema.apartment import ApartTypeSchema
from schema.status import Status


class ApartService:
    def __init__(
        self,
        old_apart_repository: OldApartRepository,
        new_apart_repositroy: NewApartRepository,
    ):
        self.old_apart_repository = old_apart_repository
        self.new_apart_repository = new_apart_repositroy

    async def get_district(self, apart_type: str):
        try:
            if apart_type == ApartTypeSchema.OLD:
                return await self.old_apart_repository.get_districts()
            elif apart_type == ApartTypeSchema.NEW:
                return await self.new_apart_repository.get_districts()
            else:
                raise NotFoundException
        except Exception as error:
            raise HTTPException(detail=error, status_code=http_status.HTTP_409_CONFLICT)

    async def get_municipal_districts(self, apart_type: str, districts: List[str]):
        try:
            if apart_type == ApartTypeSchema.OLD:
                return await self.old_apart_repository.get_municipal_district(
                    districts=districts
                )
            elif apart_type == ApartTypeSchema.NEW:
                return await self.new_apart_repository.get_municipal_district(
                    districts=districts
                )
            else:
                raise NotFoundException
        except Exception as error:
            raise HTTPException(detail=error, status_code=http_status.HTTP_409_CONFLICT)

    async def get_house_addresses(
        self, apart_type: str, municipal_districts: List[str]
    ):
        if apart_type == ApartTypeSchema.OLD:
            return await self.old_apart_repository.get_house_addresses(
                municipal_districts
            )
        elif apart_type == ApartTypeSchema.NEW:
            return await self.new_apart_repository.get_house_addresses(
                municipal_districts
            )
        else:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)

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
        is_queue: bool = None,
        is_private: bool = None,
    ):
        if apart_type == ApartTypeSchema.OLD:
            return await self.old_apart_repository.get_apartments(
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
                is_private=is_private,
            )
        elif apart_type == ApartTypeSchema.NEW:
            return await self.new_apart_repository.get_apartments(
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
                is_private=is_private,
            )
        else:
            raise NotFoundException

    async def get_apartment_by_id(self, apart_id: int, apart_type: str):
        if apart_type == ApartTypeSchema.OLD:
            return await self.old_apart_repository.get_apartment_by_id(
                apart_id=apart_id
            )
        elif apart_type == ApartTypeSchema.NEW:
            return await self.new_apart_repository.get_apartment_by_id(
                apart_id=apart_id
            )

    async def get_house_address_with_room_count(self, apart_type: str):
        if apart_type == ApartTypeSchema.OLD:
            result = await self.old_apart_repository.get_house_address_with_room_count()
        elif apart_type == ApartTypeSchema.NEW:
            result = await self.new_apart_repository.get_house_address_with_room_count()
        formatted_result = []
        for address, room_counts in result:
            room_details = ", ".join(
                f"{room} к. - {count}" for room, count in room_counts.items()
            )
            formatted_result.append((address, room_details))
        return formatted_result

    async def switch_apartment(self, first_apart_id: int, second_apart_id: int):
        return await self.old_apart_repository.switch_apartment(
            first_apart_id=first_apart_id, second_apart_id=second_apart_id
        )

    async def manual_matching(self, old_apart_id: int, new_apart_ids: List[int]):
        return await self.old_apart_repository.manual_matching(
            old_apart_id=old_apart_id, new_apart_ids=new_apart_ids
        )

    async def get_void_aparts_for_apartment(self, apartmentd_id: int):
        return await self.old_apart_repository.get_void_aparts_for_apartment(
            apart_id=apartmentd_id
        )

    async def cancell_matching_for_apart(self, apart_id: int, apart_type: str):
        if apart_type == ApartTypeSchema.OLD:
            return await self.old_apart_repository.cancell_matching_apart(
                apart_id=apart_id
            )
        elif apart_type == ApartTypeSchema.NEW:
            return await self.new_apart_repository.cancell_matching_apart(
                apart_id=apart_id
            )
        else:
            raise NotFoundException

    async def update_status_for_apart(
        self, apart_id: int, new_apart_id: int, status: str, apart_type: str
    ):
        if apart_type == ApartTypeSchema.OLD:
            return await self.old_apart_repository.update_status_for_apart(
                apart_id=apart_id, new_apart_id=new_apart_id, status=status
            )
        else:
            raise NotFoundException

    async def set_private_for_new_aparts(
        self, new_aparts: List[int], status: bool = True
    ):
        return await self.new_apart_repository.set_private_for_new_aparts(
            new_aparts, status
        )

    async def set_decline_reason(
        self,
        apart_id,
        new_apart_id,
        min_floor,
        max_floor,
        unom,
        entrance,
        apartment_layout,
        notes,
    ):
        return await self.old_apart_repository.set_decline_reason(
            apartment_id=apart_id,
            new_apart_id=new_apart_id,
            min_floor=min_floor,
            max_floor=max_floor,
            unom=unom,
            entrance=entrance,
            apartment_layout=apartment_layout,
            notes=notes,
        )

    async def set_notes_for_many(
        self, apart_ids: list[int], notes: str, apart_type: str
    ):
        if apart_type == ApartTypeSchema.OLD:
            return await self.old_apart_repository.set_notes(apart_ids, notes=notes)
        elif apart_type == ApartTypeSchema.NEW:
            return await self.new_apart_repository.set_notes(
                apart_ids=apart_ids, notes=notes
            )
        else:
            raise NotFoundException

    async def get_decline_reason(self, decline_reason_id):
        return await self.old_apart_repository.get_decline_reason(decline_reason_id)

    async def update_decline_reason(
        self,
        decline_reason_id: int,
        min_floor: Optional[int] = None,
        max_floor: Optional[int] = None,
        unom: Optional[str] = None,
        entrance: Optional[str] = None,
        apartment_layout: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        return await self.old_apart_repository.update_decline_reason(
            decline_reason_id,
            min_floor,
            max_floor,
            unom,
            entrance,
            apartment_layout,
            notes,
        )

    async def get_entrance_ranges(self, address):
        entrance_number = await self.new_apart_repository.get_entrance_ranges(address)
        if not entrance_number:
            raise NotFoundException
        return entrance_number

    async def set_entrance_number_for_many(self, new_apart_ids, entrance_number):
        affected_rows = await self.new_apart_repository.update_entrance_number_for_many(
            new_apart_ids, entrance_number
        )
        return {"affected_rows": affected_rows, "status": "done"}

    async def set_status_for_many(self, apart_ids, status, apart_type):
        """
        Конкретно данный сервис проставляет статус в offer(в jsonb тоже)
        Либо резервирует новые квартиры
        """
        try:
            if apart_type == ApartTypeSchema.OLD:
                affected_rows = await self.old_apart_repository.set_status_for_many(
                    apart_ids, status=status
                )
            elif apart_type == ApartTypeSchema.NEW:
                if status in (
                    Status.RESERVE.value,
                    Status.PRIVATE.value,
                    Status.FREE.value,
                ):
                    affected_rows = await self.new_apart_repository.set_private_or_reserve_status_for_new_aparts(
                        apart_ids, status=status
                    )
                else:
                    raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)
            return {"status": "done", "affected_rows": affected_rows}
        except Exception as e:
            print(e)
            raise

    async def set_special_needs_for_many(self, apart_ids, is_special_needs_marker):
        await self.old_apart_repository.set_special_needs_for_many(
            apart_ids, is_special_needs_marker
        )
