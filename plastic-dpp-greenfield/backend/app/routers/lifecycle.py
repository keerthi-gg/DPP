from fastapi import APIRouter, Depends

from app.container import get_lifecycle_service
from app.models.account import UserRoleAccount
from app.models.lifecycle_event import LifecycleEvent, LifecycleEventCreate
from app.routers.dependencies import get_current_account, log_action
from app.services.lifecycle_service import LifecycleService

router = APIRouter(prefix="/products", tags=["lifecycle"])


@router.post(
    "/{dpp_id}/lifecycle-events",
    response_model=LifecycleEvent,
    status_code=201,
    summary="Record a payment-linked lifecycle transition",
    description="Requires a confirmed transaction and an authorized role; enforces the state machine.",
)
def create_lifecycle_event(
    dpp_id: str,
    payload: LifecycleEventCreate,
    account: UserRoleAccount = Depends(get_current_account),
    service: LifecycleService = Depends(get_lifecycle_service),
) -> LifecycleEvent:
    event = service.transition(dpp_id, payload.target_state, payload.transaction_id, account)
    log_action(account, f"lifecycle_transition:{event.new_state.value}", dpp_id)
    return event


@router.get(
    "/{dpp_id}/history",
    response_model=dict,
    summary="Get a product's ordered lifecycle history (read-only)",
)
def get_history(
    dpp_id: str,
    account: UserRoleAccount = Depends(get_current_account),
    service: LifecycleService = Depends(get_lifecycle_service),
) -> dict:
    events = service.history(dpp_id)
    return {"dpp_id": dpp_id, "events": [e.model_dump(mode="json") for e in events]}
