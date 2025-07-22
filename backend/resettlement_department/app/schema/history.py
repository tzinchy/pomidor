from typing import List, Optional

from pydantic import BaseModel


class HistoryResponse(BaseModel):
    history_id: int
    old_house_addresses: Optional[List[str]]
    new_house_addresses: Optional[List[str]]
    status_id: Optional[int]
    is_downloaded: Optional[bool]
    is_wave: Optional[bool]
    is_shadow : Optional[bool]

    class Config:
        from_attributes = True

class EnvStatResponse(BaseModel):
    id: int
    name: str
    timestamp: str
    is_active: bool