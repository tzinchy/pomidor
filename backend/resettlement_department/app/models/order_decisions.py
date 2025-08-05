from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    BigInteger,
    text,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from models.base import Base


class OrderDecisions(Base):
    __tablename__ = "order_decisions"

    affair_id = Column(BigInteger)
    order_id = Column(BigInteger, primary_key=True)
    decision_date = Column(Date)
    decision_number = Column(String)
    order_date = Column(Date)
    is_cancelled = Column(Boolean)
    cancel_date = Column(Date)
    cancel_reason = Column(String)
    order_draft_date = Column(Date)
    legal_cancel_date = Column(Date)
    legal_order_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))
    accounting_article = Column(String)
    legal_reason = Column(String)
    collateral_type = Column(String)
    area_id = Column(JSONB)
    article_code = Column(String(20))
    unom = Column(Integer)
    un_kv = Column(Integer)
    cad_num = Column(String)
