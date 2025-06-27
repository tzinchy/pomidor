import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
from fastapi import status as http_status
from fastapi.concurrency import run_in_threadpool
from handlers.httpexceptions import NotFoundException
from repository.new_apart_repository import NewApartRepository
from repository.old_apart_repository import OldApartRepository
from schema.apartment import ApartType


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
            if apart_type == ApartType.OLD:
                return await self.old_apart_repository.get_districts()
            elif apart_type == ApartType.NEW:
                return await self.new_apart_repository.get_districts()
            else:
                raise NotFoundException
        except Exception as error:
            raise HTTPException(detail=error, status_code=http_status.HTTP_409_CONFLICT)

    async def get_municipal_districts(self, apart_type: str, districts: List[str]):
        try:
            if apart_type == ApartType.OLD:
                return await self.old_apart_repository.get_municipal_district(
                    districts=districts
                )
            elif apart_type == ApartType.NEW:
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
        if apart_type == ApartType.OLD:
            return await self.old_apart_repository.get_house_addresses(
                municipal_districts
            )
        elif apart_type == ApartType.NEW:
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
        statuses : List[str] = None
    ):
        if apart_type == ApartType.OLD:
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
                statuses=statuses
            )
        elif apart_type == ApartType.NEW:
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
                statuses=statuses,
            )
        else:
            raise NotFoundException

    async def get_apartment_by_id(self, apart_id: int, apart_type: str):
        if apart_type == ApartType.OLD:
            return await self.old_apart_repository.get_apartment_by_id(
                apart_id=apart_id
            )
        elif apart_type == ApartType.NEW:
            return await self.new_apart_repository.get_apartment_by_id(
                apart_id=apart_id
            )

    async def get_house_address_with_room_count(self, apart_type: str):
        if apart_type == ApartType.OLD:
            result = await self.old_apart_repository.get_house_address_with_room_count()
        elif apart_type == ApartType.NEW:
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
        if apart_type == ApartType.OLD:
            return await self.old_apart_repository.cancell_matching_apart(
                apart_id=apart_id
            )
        elif apart_type == ApartType.NEW:
            return await self.new_apart_repository.cancell_matching_apart(
                apart_id=apart_id
            )
        else:
            raise NotFoundException

    async def update_status_for_apart(
        self, apart_id: int, new_apart_id: int, status: str, apart_type: str
    ):
        if apart_type == ApartType.OLD:
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
        """
        Проставляет поле notes и rsm_notes.
        Строка разбивается по ";".
        Первый элемент идет в rsm_notes, остальные в notes
        """
        notes_list = notes.split(";")
        rsm_note = notes_list.pop(0)
        notes = ";".join(notes_list)
        if apart_type == ApartType.OLD:
            return await self.old_apart_repository.set_notes(apart_ids, notes=notes, rsm_note=rsm_note)
        elif apart_type == ApartType.NEW:
            return await self.new_apart_repository.set_notes(
                apart_ids=apart_ids, notes=notes, rsm_note=rsm_note
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
            if apart_type == ApartType.OLD:
                affected_rows = await self.old_apart_repository.set_status_for_many_old_apart(
                    apart_ids, status=status
                )
            elif apart_type == ApartType.NEW:
                    affected_rows = await self.new_apart_repository.set_status_for_many_new_apart(
                        apart_ids, status=status
                    )

            return {"status": "done", "affected_rows": affected_rows}
        except Exception as e:
            print(e)
            raise

    async def set_special_needs_for_many(self, apart_ids, is_special_needs_marker):
        await self.old_apart_repository.set_special_needs_for_many(
            apart_ids, is_special_needs_marker
        )

    async def get_excel_old_apart(self):
        try:
            folders = [Path("uploads")]
            for folder in folders:
                folder.mkdir(parents=True, exist_ok=True)

            output_path = os.path.join(os.getcwd(), "././uploads", "old_apart.xlsx")
            rows, cols = await self.old_apart_repository.get_excel_old_apart()
            if rows:
                df = pd.DataFrame(rows, columns=cols)
            else:
                df = pd.DataFrame([], columns=cols)
            df.drop(columns=["created_at", "updated_at"], inplace=True)

            print("DataFrame created:")
            print(df)
            await run_in_threadpool(df.to_excel, output_path, index=False)
            print(f"Data successfully saved to {output_path}")
            return {"filepath": output_path}
        except Exception as e:
            return {"error": str(e)}

    async def get_excel_new_apart(self):
        try:
            folders = [Path("uploads")]
            for folder in folders:
                folder.mkdir(parents=True, exist_ok=True)

            output_path = os.path.join(os.getcwd(), "././uploads", "new_apart.xlsx")
            rows, cols = await self.new_apart_repository.get_excel_new_apart()
            if rows:
                df = pd.DataFrame(rows, columns=cols)
            else:
                df = pd.DataFrame([], columns=cols)
            df.drop(columns=["created_at", "updated_at"], inplace=True)

            print("DataFrame created:")
            print(df)
            await run_in_threadpool(df.to_excel, output_path, index=False)
            print(f"Data successfully saved to {output_path}")
            return {"filepath": output_path}
        except Exception as e:
            return {"error": str(e)}

