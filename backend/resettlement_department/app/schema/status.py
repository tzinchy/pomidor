from enum import Enum

class Status(str, Enum):
    done = "Согласие"
    refusal = "Отказ"
    court = "Суд"
    compensation_fund = "Фонд компенсация"
    purchase_fund = "Фонд докупка"
    waiting = "Ожидание"
    awaiting_approval = "Ждёт одобрения"