from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class CurrentTableRequest(BaseModel):
    apart_type: str
    apart_ids: List[int]
    with_last_offer: Optional[bool] = None