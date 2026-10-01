from app.services.lifecycle_service import LifecycleService
from app.services.product_service import ProductService
from app.services.reporting_service import ReportingService
from app.services.transaction_service import TransactionLedger
from app.storage.lifecycle_repository import LifecycleEventRepository
from app.storage.product_repository import ProductRepository
from app.storage.transaction_repository import TransactionRepository

# Singleton in-memory wiring for the MVP (research.md R1).
_product_repository = ProductRepository()
_product_service = ProductService(_product_repository)

_transaction_repository = TransactionRepository()
_transaction_ledger = TransactionLedger(_transaction_repository)

_event_repository = LifecycleEventRepository()
_lifecycle_service = LifecycleService(_product_service, _transaction_ledger, _event_repository)

_reporting_service = ReportingService(_product_service)


def get_product_service() -> ProductService:
    return _product_service


def get_transaction_ledger() -> TransactionLedger:
    return _transaction_ledger


def get_lifecycle_service() -> LifecycleService:
    return _lifecycle_service


def get_reporting_service() -> ReportingService:
    return _reporting_service
