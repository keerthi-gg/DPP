# Phase 1 Data Model: Plastic DPP Greenfield

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Research**: [research.md](./research.md)

Entities below map directly to the Key Entities in the spec. Types are described conceptually (implemented as Pydantic models in `backend/app/models/`).

## DigitalProductPassport (DPP)

Represents a single plastic product's unique digital identity (spec FR-001, FR-002).

| Field | Type | Notes |
|---|---|---|
| `dpp_id` | string (unique) | Generated on registration, e.g. `DPP-000123` |
| `product_type` | string | e.g. "PET bottle", required |
| `material_summary` | string | Material composition summary, required |
| `manufacture_date` | date | Required |
| `manufacturer_id` | string | References the registering Manufacturer account |
| `qr_code_ref` | string | 1:1 reference to the bound QR Code (FR-002) |
| `current_state` | `LifecycleState` enum | Starts at `MANUFACTURED` (US1 AS1); see Lifecycle State Model below |
| `created_at` | datetime | Set at registration |

**Validation rules**: `product_type`, `material_summary`, `manufacturer_id` are required and non-empty (US1 AS2). `dpp_id` and `qr_code_ref` are immutable once assigned.

## QRCode

A scannable reference bound 1:1 to a DPP; authentication/lookup only, never lifecycle authorization (FR-004).

| Field | Type | Notes |
|---|---|---|
| `qr_code_ref` | string (unique) | Primary key, embedded in the DPP as `qr_code_ref` |
| `dpp_id` | string | The DPP it resolves to |

**Validation rules**: A lookup by `qr_code_ref` that doesn't resolve to a known `dpp_id` returns "not found" and never creates or mutates any record (FR-005, US2 AS2).

## LifecycleEvent

An append-only record of one state transition (FR-009, FR-010).

| Field | Type | Notes |
|---|---|---|
| `event_id` | string (unique) | Generated per event |
| `dpp_id` | string | Which product this event belongs to |
| `prior_state` | `LifecycleState` | State before this event |
| `new_state` | `LifecycleState` | State after this event |
| `actor_id` | string | Identity of the initiating user |
| `actor_role` | string | One of `manufacturer` \| `consumer` \| `recycler` \| `regulator` |
| `transaction_id` | string | The payment-linked transaction that authorized this event (FR-006) |
| `timestamp` | datetime | Set at commit time |

**Validation rules**: Once created, a `LifecycleEvent` is never edited or deleted (FR-010/NFR-001). Events for a single `dpp_id` are ordered by `timestamp` and must reflect only transitions allowed by the Lifecycle State Model.

## Transaction (payment-linked)

A reference to a validated payment/ledger-credit action that authorizes a lifecycle event (FR-006, FR-007; see research.md R2).

| Field | Type | Notes |
|---|---|---|
| `transaction_id` | string (unique) | Generated on creation |
| `status` | enum: `pending` \| `confirmed` \| `failed` | MVP marks new transactions `confirmed` immediately (simulated settlement) |
| `value` | number (optional) | Simulated payment/credit amount |
| `linked_event_id` | string (optional) | Set once this transaction has backed a lifecycle event; prevents reuse |

**Validation rules**: A transaction may back at most one `LifecycleEvent` (`linked_event_id` must be empty at the time a lifecycle transition references it). A lifecycle transition referencing a `transaction_id` that doesn't exist, isn't `confirmed`, or is already linked is rejected (FR-006/FR-007, US3 AS3).

## UserRoleAccount

Represents a stakeholder with an identity and an assigned role (FR-011).

| Field | Type | Notes |
|---|---|---|
| `user_id` | string (unique) | |
| `role` | enum: `manufacturer` \| `consumer` \| `recycler` \| `regulator` | Governs which actions the account may initiate (FR-012–FR-015) |

**Validation rules**: Every lifecycle-changing request is checked against the caller's `role` before the lifecycle state machine runs (FR-015); lookups are permitted regardless of role (FR-003, NFR-003 read-only for unauthenticated users).

## Lifecycle State Model

```text
MANUFACTURED --> OWNED --> COLLECTED --> RECYCLED --> CLOSED
```

- Allowed transitions (research.md R3): `MANUFACTURED → OWNED`, `OWNED → COLLECTED`, `COLLECTED → RECYCLED`, `RECYCLED → CLOSED`.
- No transitions are allowed out of `CLOSED` (US3 AS4).
- No transition may skip a state or run in reverse (FR-008).
- Role gating: `OWNED` transition initiated by Consumer; `COLLECTED` and `RECYCLED` transitions initiated by Recycler; `CLOSED` may be initiated by Recycler (final confirmation) — exact closing actor is a router/service detail, not a data-model concern, and should be confirmed during `/speckit-tasks` if ambiguous.
