from fastapi import APIRouter, Depends

from app.container import get_product_service
from app.models.account import Role, UserRoleAccount
from app.models.product import DigitalProductPassport, ProductCreate
from app.routers.dependencies import get_current_account, log_action
from app.services.errors import NotFoundError, UnauthorizedRoleError
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=DigitalProductPassport,
    status_code=201,
    summary="Register a product and issue its DPP + QR code",
    description="Manufacturer-only. Creates a Digital Product Passport in state 'manufactured'.",
)
def register_product(
    payload: ProductCreate,
    account: UserRoleAccount = Depends(get_current_account),
    service: ProductService = Depends(get_product_service),
) -> DigitalProductPassport:
    if account.role != Role.MANUFACTURER:
        raise UnauthorizedRoleError("Only manufacturers may register products")
    product = service.register_product(
        payload.product_type,
        payload.material_summary,
        payload.manufacture_date,
        account.user_id,
    )
    log_action(account, "register_product", product.dpp_id)
    return product


@router.get(
    "",
    response_model=dict,
    summary="List all products",
)
def list_products(
    account: UserRoleAccount = Depends(get_current_account),
    service: ProductService = Depends(get_product_service),
) -> dict:
    return {"products": [p.model_dump(mode="json") for p in service.list_products()]}


@router.get(
    "/lookup",
    response_model=DigitalProductPassport,
    summary="Look up a product by QR code (read-only)",
)
def lookup_by_qr(
    qr_code: str,
    account: UserRoleAccount = Depends(get_current_account),
    service: ProductService = Depends(get_product_service),
) -> DigitalProductPassport:
    product = service.get_by_qr_code(qr_code)
    if product is None:
        raise NotFoundError(f"No product for QR code: {qr_code}")
    return product


@router.get(
    "/{dpp_id}",
    response_model=DigitalProductPassport,
    summary="Look up a product by DPP ID (read-only)",
)
def get_product(
    dpp_id: str,
    account: UserRoleAccount = Depends(get_current_account),
    service: ProductService = Depends(get_product_service),
) -> DigitalProductPassport:
    return service.require(dpp_id)
