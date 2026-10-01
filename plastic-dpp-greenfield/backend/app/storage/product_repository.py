from app.models.product import DigitalProductPassport, QRCode
from app.storage.base import Repository


class ProductRepository(Repository[DigitalProductPassport]):
    def __init__(self) -> None:
        super().__init__()
        self._qr_index: dict[str, str] = {}

    def add(self, key: str, item: DigitalProductPassport) -> DigitalProductPassport:
        super().add(key, item)
        self._qr_index[item.qr_code_ref] = item.dpp_id
        return item

    def get_by_qr(self, qr_code_ref: str) -> DigitalProductPassport | None:
        dpp_id = self._qr_index.get(qr_code_ref)
        return self.get(dpp_id) if dpp_id else None

    def update(self, item: DigitalProductPassport) -> DigitalProductPassport:
        self._items[item.dpp_id] = item
        return item

    def next_sequence(self) -> int:
        return len(self._items) + 1

    def qr_for(self, dpp_id: str) -> QRCode | None:
        item = self.get(dpp_id)
        return QRCode(qr_code_ref=item.qr_code_ref, dpp_id=dpp_id) if item else None
