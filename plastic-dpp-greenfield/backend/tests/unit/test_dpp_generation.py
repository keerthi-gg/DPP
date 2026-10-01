from app.services.product_service import ProductService
from app.storage.product_repository import ProductRepository


def _service():
    return ProductService(ProductRepository())


def test_dpp_id_and_qr_ref_are_unique():
    service = _service()
    p1 = service.register_product("PET bottle", "PET", "2026-09-30", "mfg-1")
    p2 = service.register_product("HDPE jug", "HDPE", "2026-09-30", "mfg-1")
    assert p1.dpp_id != p2.dpp_id
    assert p1.qr_code_ref != p2.qr_code_ref


def test_registered_product_is_retrievable_and_stable():
    service = _service()
    created = service.register_product("PET bottle", "PET", "2026-09-30", "mfg-1")
    fetched = service.get_by_dpp_id(created.dpp_id)
    assert fetched is not None
    assert fetched.dpp_id == created.dpp_id
    assert fetched.qr_code_ref == created.qr_code_ref
