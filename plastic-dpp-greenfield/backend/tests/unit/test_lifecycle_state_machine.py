import pytest

from app.models.lifecycle import LifecycleState, is_valid_transition

VALID = [
    (LifecycleState.MANUFACTURED, LifecycleState.OWNED),
    (LifecycleState.OWNED, LifecycleState.COLLECTED),
    (LifecycleState.COLLECTED, LifecycleState.RECYCLED),
    (LifecycleState.RECYCLED, LifecycleState.CLOSED),
]


@pytest.mark.parametrize("current,target", VALID)
def test_valid_forward_transitions(current, target):
    assert is_valid_transition(current, target) is True


def test_no_transition_out_of_closed():
    for state in LifecycleState:
        assert is_valid_transition(LifecycleState.CLOSED, state) is False


def test_skipping_states_is_invalid():
    assert is_valid_transition(LifecycleState.MANUFACTURED, LifecycleState.COLLECTED) is False
    assert is_valid_transition(LifecycleState.OWNED, LifecycleState.RECYCLED) is False


def test_reverse_transitions_are_invalid():
    assert is_valid_transition(LifecycleState.OWNED, LifecycleState.MANUFACTURED) is False
    assert is_valid_transition(LifecycleState.RECYCLED, LifecycleState.COLLECTED) is False
