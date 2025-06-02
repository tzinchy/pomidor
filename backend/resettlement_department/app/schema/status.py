from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    DONE = 'Согласие'
    REFUSAL = 'Отказ'
    COURT = 'Суд'
    COMPENSATION_FUND = 'МФР Компенсация'
    PURCHASE_FUND = 'МФР Докупка'
    WAITING = 'Ожидание'
    AWAITING_APPROVAL = 'Ждёт одобрения'
    AFTER_REMATCH = 'Подготовить смотровой'
    OUTSIDE_DISTRICT_FUND = 'МФР (вне района)'
    COMPENSATION_OUTSIDE_DISTRICT_FUND = 'МФР Компенсация (вне района)'
    FREE = 'Свободная'
    RESERVE = 'Резерв'
    PRIVATE = 'Блок'

class StatusUpdate(BaseModel):
    new_status: Status
