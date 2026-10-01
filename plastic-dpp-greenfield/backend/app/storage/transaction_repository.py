from app.models.transaction import Transaction
from app.storage.base import Repository


class TransactionRepository(Repository[Transaction]):
    def next_sequence(self) -> int:
        return len(self._items) + 1

    def update(self, item: Transaction) -> Transaction:
        self._items[item.transaction_id] = item
        return item
