from enum import Enum


class LifecycleState(str, Enum):
    MANUFACTURED = "manufactured"
    OWNED = "owned"
    COLLECTED = "collected"
    RECYCLED = "recycled"
    CLOSED = "closed"


# Allowed forward transitions only; CLOSED is terminal (research.md R3).
ALLOWED_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.MANUFACTURED: {LifecycleState.OWNED},
    LifecycleState.OWNED: {LifecycleState.COLLECTED},
    LifecycleState.COLLECTED: {LifecycleState.RECYCLED},
    LifecycleState.RECYCLED: {LifecycleState.CLOSED},
    LifecycleState.CLOSED: set(),
}


def is_valid_transition(current: LifecycleState, target: LifecycleState) -> bool:
    return target in ALLOWED_TRANSITIONS[current]
