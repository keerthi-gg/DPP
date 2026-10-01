import pytest

from app.services.errors import InvalidTransactionError
from app.services.transaction_service import TransactionLedger
from app.storage.transaction_repository import TransactionRepository


def _ledger():
    return TransactionLedger(TransactionRepository())


def test_new_transaction_is_confirmed_and_unlinked():
    ledger = _ledger()
    txn = ledger.create(value=5.0)
    assert txn.status == "confirmed"
    assert txn.linked_event_id is None


def test_validate_and_link_marks_transaction_used():
    ledger = _ledger()
    txn = ledger.create(value=1.0)
    ledger.validate_and_link(txn.transaction_id, "EVT-000001")
    linked = ledger.get(txn.transaction_id)
    assert linked.linked_event_id == "EVT-000001"


def test_unknown_transaction_rejected():
    ledger = _ledger()
    with pytest.raises(InvalidTransactionError):
        ledger.validate_and_link("TXN-000000", "EVT-000001")


def test_reused_transaction_rejected():
    ledger = _ledger()
    txn = ledger.create(value=1.0)
    ledger.validate_and_link(txn.transaction_id, "EVT-000001")
    with pytest.raises(InvalidTransactionError):
        ledger.validate_and_link(txn.transaction_id, "EVT-000002")
