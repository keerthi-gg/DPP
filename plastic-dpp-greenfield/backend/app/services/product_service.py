from datetime import date, datetime, timezone

from app.models.lifecycle import LifecycleState
from app.models.product import DigitalProductPassport
from app.services.errors import NotFoundError
from app.storage.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def register_product(
        self,
        product_type: str,
        material_summary: str,
        manufacture_date: date,
        manufacturer_id: str,
    ) -> DigitalProductPassport:
        seq = self._repository.next_sequence()
        dpp_id = f"DPP-{seq:06d}"
        product = DigitalProductPassport(
            dpp_id=dpp_id,
            product_type=product_type,
            material_summary=material_summary,
            manufacture_date=manufacture_date,
            manufacturer_id=manufacturer_id,
            qr_code_ref=f"qr://{dpp_id.lower()}",
            current_state=LifecycleState.MANUFACTURED,
            created_at=datetime.now(timezone.utc),
        )
        return self._repository.add(dpp_id, product)

    def get_by_dpp_id(self, dpp_id: str) -> DigitalProductPassport | None:
        return self._repository.get(dpp_id)

    def get_by_qr_code(self, qr_code_ref: str) -> DigitalProductPassport | None:
        return self._repository.get_by_qr(qr_code_ref)

    def require(self, dpp_id: str) -> DigitalProductPassport:
        product = self._repository.get(dpp_id)
        if product is None:
            raise NotFoundError(f"Product not found: {dpp_id}")
        return product

    def list_products(self) -> list[DigitalProductPassport]:
        return self._repository.list()
