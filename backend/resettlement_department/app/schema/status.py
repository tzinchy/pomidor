from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    done = "Согласие"
    refusal = "Отказ"
    court = "Суд"
    compensation_fund = "Фонд компенсация"
    purchase_fund = "Фонд докупка"
    waiting = "Ожидание"
    awaiting_approval = "Ждёт одобрения"

class StatusUpdate(BaseModel):
    new_status: Status
