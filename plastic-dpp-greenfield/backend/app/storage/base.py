from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(Generic[T]):
    """In-memory repository keyed by string id.

    Seam for swapping in SQLite/Postgres or a blockchain-backed store later
    (research.md R1) without changing service logic.
    """

    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, key: str, item: T) -> T:
        self._items[key] = item
        return item

    def get(self, key: str) -> T | None:
        return self._items.get(key)

    def list(self) -> list[T]:
        return list(self._items.values())

    def __len__(self) -> int:
        return len(self._items)
