from app.models.transaction import Transaction
from app.services.errors import InvalidTransactionError
from app.storage.transaction_repository import TransactionRepository


class TransactionLedger:
    """Simulated payment ledger for the MVP (research.md R2).

    New transactions settle immediately as ``confirmed``. A transaction may back
    at most one lifecycle event, which provides replay protection.
    """

    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def create(self, value: float | None = None) -> Transaction:
        seq = self._repository.next_sequence()
        txn = Transaction(
            transaction_id=f"TXN-{seq:06d}",
            status="confirmed",
            value=value,
            linked_event_id=None,
        )
        return self._repository.add(txn.transaction_id, txn)

    def get(self, transaction_id: str) -> Transaction | None:
        return self._repository.get(transaction_id)

    def validate_and_link(self, transaction_id: str, event_id: str) -> Transaction:
        txn = self._repository.get(transaction_id)
        if txn is None:
            raise InvalidTransactionError(f"Unknown transaction: {transaction_id}")
        if txn.status != "confirmed":
            raise InvalidTransactionError(f"Transaction not confirmed: {transaction_id}")
        if txn.linked_event_id is not None:
            raise InvalidTransactionError(
                f"Transaction already used for event {txn.linked_event_id}"
            )
        txn.linked_event_id = event_id
        return self._repository.update(txn)
