from datetime import datetime

from pydantic import BaseModel

from app.models.lifecycle import LifecycleState


class LifecycleEventCreate(BaseModel):
    target_state: LifecycleState
    transaction_id: str


class LifecycleEvent(BaseModel):
    event_id: str
    dpp_id: str
    prior_state: LifecycleState
    new_state: LifecycleState
    actor_id: str
    actor_role: str
    transaction_id: str
    timestamp: datetime
