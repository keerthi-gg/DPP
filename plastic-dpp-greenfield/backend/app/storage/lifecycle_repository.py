from app.models.lifecycle_event import LifecycleEvent
from app.storage.base import Repository


class LifecycleEventRepository(Repository[LifecycleEvent]):
    def next_sequence(self) -> int:
        return len(self._items) + 1

    def list_for(self, dpp_id: str) -> list[LifecycleEvent]:
        events = [e for e in self._items.values() if e.dpp_id == dpp_id]
        return sorted(events, key=lambda e: e.timestamp)
