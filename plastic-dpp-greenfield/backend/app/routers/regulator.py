from fastapi import APIRouter, Depends

from app.container import get_reporting_service
from app.models.account import Role, UserRoleAccount
from app.routers.dependencies import get_current_account
from app.services.errors import UnauthorizedRoleError
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/regulator", tags=["regulator"])


@router.get(
    "/report",
    response_model=dict,
    summary="Aggregated compliance report by lifecycle state (regulator-only)",
)
def get_report(
    account: UserRoleAccount = Depends(get_current_account),
    service: ReportingService = Depends(get_reporting_service),
) -> dict:
    if account.role != Role.REGULATOR:
        raise UnauthorizedRoleError("Only regulators may access compliance reports")
    return service.aggregate_by_state()
