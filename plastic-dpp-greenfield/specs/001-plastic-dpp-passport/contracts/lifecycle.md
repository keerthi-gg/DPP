# API Contract: Transactions & Lifecycle Events

**Feature**: [../spec.md](../spec.md) | **Data model**: [../data-model.md](../data-model.md) | **Research**: [../research.md](../research.md) (R2, R3)

## POST /transactions

Create a payment-linked transaction (simulated settlement for the MVP; FR-006, FR-007; research.md R2).

**Auth**: `consumer` or `recycler` (the roles that initiate lifecycle transitions).

**Request body**:
```json
{ "value": 5.00 }
```
`value` is optional.

**Responses**:
- `201 Created` — `{ "transaction_id": "...", "status": "confirmed", "value": 5.00, "linked_event_id": null }`. MVP marks transactions `confirmed` immediately.

## POST /products/{dpp_id}/lifecycle-events

Submit a lifecycle transition for a product, gated by a payment-linked transaction (FR-006–FR-009, FR-013, FR-015; US3).

**Auth**: role must be authorized for the requested transition (`consumer` for `manufactured → owned`; `recycler` for `owned → collected`, `collected → recycled`, `recycled → closed`).

**Request body**:
```json
{ "target_state": "owned", "transaction_id": "TXN-000045" }
```

**Responses**:
- `201 Created` — returns the new `LifecycleEvent` (`event_id`, `prior_state`, `new_state`, `actor_id`, `actor_role`, `transaction_id`, `timestamp`); the product's `current_state` is updated (US3 AS1/AS2).
- `400 Bad Request` — `transaction_id` missing, unknown, not `confirmed`, or already linked to another event (US3 AS3, research.md R2).
- `403 Forbidden` — caller's role is not authorized to initiate this transition (FR-015).
- `404 Not Found` — unknown `dpp_id`.
- `409 Conflict` — `target_state` is not a valid next state from the product's `current_state` — including any attempt to transition a `closed` product (FR-008, US3 AS4, research.md R3).

## GET /products/{dpp_id}/history

Retrieve the full, ordered lifecycle event history for a product (FR-009, US3 AS5).

**Auth**: any authenticated role (read-only).

**Responses**:
- `200 OK` — `{ "dpp_id": "...", "events": [LifecycleEvent, ...] }` ordered by `timestamp`.
- `404 Not Found` — unknown `dpp_id`.
