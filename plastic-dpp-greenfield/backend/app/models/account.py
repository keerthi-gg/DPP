from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    MANUFACTURER = "manufacturer"
    CONSUMER = "consumer"
    RECYCLER = "recycler"
    REGULATOR = "regulator"


class UserRoleAccount(BaseModel):
    user_id: str
    role: Role
