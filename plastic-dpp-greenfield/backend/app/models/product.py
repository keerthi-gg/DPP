from datetime import date, datetime

from pydantic import BaseModel

from app.models.lifecycle import LifecycleState


class ProductCreate(BaseModel):
    product_type: str
    material_summary: str
    manufacture_date: date


class QRCode(BaseModel):
    qr_code_ref: str
    dpp_id: str


class DigitalProductPassport(BaseModel):
    dpp_id: str
    product_type: str
    material_summary: str
    manufacture_date: date
    manufacturer_id: str
    qr_code_ref: str
    current_state: LifecycleState
    created_at: datetime
