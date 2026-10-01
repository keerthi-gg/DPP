from typing import Literal, Optional

from pydantic import BaseModel

TransactionStatus = Literal["pending", "confirmed", "failed"]


class TransactionCreate(BaseModel):
    value: Optional[float] = None


class Transaction(BaseModel):
    transaction_id: str
    status: TransactionStatus
    value: Optional[float] = None
    linked_event_id: Optional[str] = None
