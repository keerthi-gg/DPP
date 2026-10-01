from fastapi import APIRouter, Depends

from app.container import get_transaction_ledger
from app.models.account import Role, UserRoleAccount
from app.models.transaction import Transaction, TransactionCreate
from app.routers.dependencies import get_current_account, log_action
from app.services.errors import UnauthorizedRoleError
from app.services.transaction_service import TransactionLedger

router = APIRouter(prefix="/transactions", tags=["transactions"])

_ALLOWED_ROLES = {Role.CONSUMER, Role.RECYCLER}


@router.post(
    "",
    response_model=Transaction,
    status_code=201,
    summary="Create a payment-linked transaction (simulated settlement)",
    description="Consumer/recycler only. Settles immediately as 'confirmed' for the MVP.",
)
def create_transaction(
    payload: TransactionCreate,
    account: UserRoleAccount = Depends(get_current_account),
    ledger: TransactionLedger = Depends(get_transaction_ledger),
) -> Transaction:
    if account.role not in _ALLOWED_ROLES:
        raise UnauthorizedRoleError("Only consumers or recyclers may create transactions")
    txn = ledger.create(value=payload.value)
    log_action(account, "create_transaction", txn.transaction_id)
    return txn
