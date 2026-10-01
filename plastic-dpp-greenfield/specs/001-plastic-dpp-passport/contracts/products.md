# API Contract: Products

**Feature**: [../spec.md](../spec.md) | **Data model**: [../data-model.md](../data-model.md)

All endpoints require `X-Role` and `X-User-Id` headers (see research.md "Note on role-based access"). Lookup endpoints accept any authenticated role; registration is Manufacturer-only.

## POST /products

Register a new plastic product and issue its DPP + QR code (FR-001, FR-002; US1).

**Auth**: `X-Role: manufacturer` required (FR-012). Any other role → `403`.

**Request body**:
```json
{
  "product_type": "PET bottle",
  "material_summary": "PET plastic, food-grade",
  "manufacture_date": "2026-09-30"
}
```

**Responses**:
- `201 Created` — returns the new DPP record (`dpp_id`, `qr_code_ref`, `current_state: "manufactured"`, plus submitted fields).
- `400 Bad Request` — missing/invalid required field (US1 AS2), body indicates which field(s).
- `403 Forbidden` — caller role is not `manufacturer`.

## GET /products/{dpp_id}

Look up a product's identity and current lifecycle status by DPP ID (FR-003, FR-004; US2 AS1).

**Auth**: any authenticated role.

**Responses**:
- `200 OK` — DPP record including `current_state`.
- `404 Not Found` — no product with that `dpp_id` (FR-005, US2 AS2). Read-only; no record is created or altered.

## GET /products/lookup?qr_code={qr_code_ref}

Look up a product's identity and current lifecycle status by QR code value (FR-003, FR-004; US2 AS1).

**Auth**: any authenticated role.

**Responses**:
- `200 OK` — same shape as `GET /products/{dpp_id}`.
- `404 Not Found` — QR code doesn't resolve to a known product (FR-005, US2 AS2/AS3 — the scan itself never changes lifecycle state).

## GET /products

List all registered products (used for general listing and as a building block for the Regulator aggregate report — see `contracts/regulator.md`).

**Auth**: any authenticated role.

**Responses**:
- `200 OK` — `{ "products": [DPP, ...] }`.
