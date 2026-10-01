from app.models.lifecycle import LifecycleState
from app.services.product_service import ProductService


class ReportingService:
    def __init__(self, product_service: ProductService) -> None:
        self._products = product_service

    def aggregate_by_state(self) -> dict:
        products = self._products.list_products()
        by_state = {state.value: 0 for state in LifecycleState}
        for product in products:
            by_state[product.current_state.value] += 1
        return {"total_products": len(products), "by_state": by_state}
