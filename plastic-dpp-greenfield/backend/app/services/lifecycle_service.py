from datetime import datetime, timezone

from app.models.account import Role, UserRoleAccount
from app.models.lifecycle import LifecycleState, is_valid_transition
from app.models.lifecycle_event import LifecycleEvent
from app.services.errors import (
    InvalidTransitionError,
    UnauthorizedRoleError,
)
from app.services.product_service import ProductService
from app.services.transaction_service import TransactionLedger
from app.storage.lifecycle_repository import LifecycleEventRepository

# Which role may initiate a transition into each target state (data-model.md).
# Recycler owns the collection/recycling half, including final closure.
ROLE_FOR_TARGET: dict[LifecycleState, Role] = {
    LifecycleState.OWNED: Role.CONSUMER,
    LifecycleState.COLLECTED: Role.RECYCLER,
    LifecycleState.RECYCLED: Role.RECYCLER,
    LifecycleState.CLOSED: Role.RECYCLER,
}


class LifecycleService:
    def __init__(
        self,
        product_service: ProductService,
        ledger: TransactionLedger,
        event_repository: LifecycleEventRepository,
    ) -> None:
        self._products = product_service
        self._ledger = ledger
        self._events = event_repository

    def transition(
        self,
        dpp_id: str,
        target_state: LifecycleState,
        transaction_id: str,
        actor: UserRoleAccount,
    ) -> LifecycleEvent:
        product = self._products.require(dpp_id)  # 404 if missing

        required_role = ROLE_FOR_TARGET.get(target_state)
        if required_role is None or actor.role != required_role:
            raise UnauthorizedRoleError(
                f"Role {actor.role.value} may not transition to {target_state.value}"
            )

        if not is_valid_transition(product.current_state, target_state):
            raise InvalidTransitionError(
                f"Cannot transition from {product.current_state.value} to {target_state.value}"
            )

        # Validate + consume the transaction only once all other checks pass.
        event_id = f"EVT-{self._events.next_sequence():06d}"
        self._ledger.validate_and_link(transaction_id, event_id)  # 400 if invalid/reused

        event = LifecycleEvent(
            event_id=event_id,
            dpp_id=dpp_id,
            prior_state=product.current_state,
            new_state=target_state,
            actor_id=actor.user_id,
            actor_role=actor.role.value,
            transaction_id=transaction_id,
            timestamp=datetime.now(timezone.utc),
        )
        self._events.add(event_id, event)

        product.current_state = target_state
        self._products._repository.update(product)
        return event

    def history(self, dpp_id: str) -> list[LifecycleEvent]:
        self._products.require(dpp_id)  # 404 if missing
        return self._events.list_for(dpp_id)
