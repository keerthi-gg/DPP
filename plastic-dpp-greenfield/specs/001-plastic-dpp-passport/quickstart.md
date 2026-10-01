# Quickstart: Plastic DPP Greenfield MVP

**Feature**: [spec.md](./spec.md) | **Contracts**: [contracts/](./contracts/)

Validates the primary end-to-end flow: **register → lookup → transition → view history**.

## Prerequisites

- Python 3.11
- Repo cloned, working directory at `backend/`

## Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
uvicorn app.main:app --reload
```

API docs available at http://127.0.0.1:8000/docs

## Validate the end-to-end flow

All requests below use mock-auth headers (`X-Role`, `X-User-Id`) per research.md's role-based access note.

1. **Register a product** (Manufacturer) — see [contracts/products.md](./contracts/products.md#post-products):
   ```powershell
   curl.exe -X POST http://127.0.0.1:8000/products `
     -H "X-Role: manufacturer" -H "X-User-Id: mfg-1" -H "Content-Type: application/json" `
     -d "{\"product_type\":\"PET bottle\",\"material_summary\":\"PET, food-grade\",\"manufacture_date\":\"2026-09-30\"}"
   ```
   Expect `201` with a `dpp_id` and `qr_code_ref`, `current_state: "manufactured"`.

2. **Look up the product** (any role) — see [contracts/products.md](./contracts/products.md#get-productsdpp_id):
   ```powershell
   curl.exe http://127.0.0.1:8000/products/{dpp_id} -H "X-Role: consumer" -H "X-User-Id: cons-1"
   ```
   Expect `200` with the same `current_state`, confirming the lookup alone changed nothing (FR-004).

3. **Create a payment-linked transaction** (Consumer) — see [contracts/lifecycle.md](./contracts/lifecycle.md#post-transactions):
   ```powershell
   curl.exe -X POST http://127.0.0.1:8000/transactions `
     -H "X-Role: consumer" -H "X-User-Id: cons-1" -H "Content-Type: application/json" -d "{\"value\":5.00}"
   ```
   Expect `201` with `status: "confirmed"` and a `transaction_id`.

4. **Submit a lifecycle transition** (Consumer, ownership transfer) — see [contracts/lifecycle.md](./contracts/lifecycle.md#post-productsdpp_idlifecycle-events):
   ```powershell
   curl.exe -X POST http://127.0.0.1:8000/products/{dpp_id}/lifecycle-events `
     -H "X-Role: consumer" -H "X-User-Id: cons-1" -H "Content-Type: application/json" `
     -d "{\"target_state\":\"owned\",\"transaction_id\":\"{transaction_id}\"}"
   ```
   Expect `201`; re-running the lookup from step 2 now shows `current_state: "owned"`.

5. **Attempt the same transition again with the same `transaction_id`** — expect `400` (transaction already linked; research.md R2 replay protection).

6. **View lifecycle history** (any role) — see [contracts/lifecycle.md](./contracts/lifecycle.md#get-productsdpp_idhistory):
   ```powershell
   curl.exe http://127.0.0.1:8000/products/{dpp_id}/history -H "X-Role: regulator" -H "X-User-Id: reg-1"
   ```
   Expect `200` with one event: `manufactured → owned`, including the `transaction_id` and `actor_id`.

7. **Regulator aggregate report** — see [contracts/regulator.md](./contracts/regulator.md#get-regulatorreport):
   ```powershell
   curl.exe http://127.0.0.1:8000/regulator/report -H "X-Role: regulator" -H "X-User-Id: reg-1"
   ```
   Expect `200` with `by_state` counts reflecting the registered/transitioned products.

## Run automated tests

```powershell
cd backend
pytest
```

Expect all unit, contract, and integration tests (see plan.md Project Structure) to pass, including state-machine edge cases (out-of-order transition, transition on a `closed` product, missing/invalid `transaction_id`).
