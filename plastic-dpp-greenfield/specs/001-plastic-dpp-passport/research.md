# Phase 0 Research: Plastic DPP Greenfield

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This file resolves the open technical decisions for the MVP. Each entry follows Decision / Rationale / Alternatives considered.

## R1: In-memory vs. lightweight persistent store for the MVP

**Decision**: Use in-memory Python dict-based repositories — one per entity (DPPs, Lifecycle Events, Transactions, Accounts) — each hidden behind a small repository interface (e.g. `ProductRepository`, `TransactionRepository` with `get`/`add`/`list` methods). Business logic in `services/` only talks to the interface, never to the dict directly.

**Rationale**:
- Matches the pattern already used in [backend/app/main.py](../../backend/app/main.py) (`products: list[Product]`), so the refactor is incremental rather than a rewrite.
- Fastest path to a working capstone demo; no migrations, no DB driver, no connection config.
- Satisfies NFR-004 ("data model MUST be structured so a future blockchain or distributed-ledger backend can be introduced without redesigning the schema") because the repository interface is the seam where a SQLite/SQLAlchemy or blockchain-backed implementation can be swapped in later without touching `services/` or `routers/`.
- Satisfies NFR-005/SC-006 (100 concurrently registered products) trivially at MVP scale.

**Alternatives considered**:
- **SQLite file-based DB**: Adds schema/migration overhead not justified for a capstone MVP scope; deferred to the "Future Extension Ideas" persistence phase noted in the spec.
- **PostgreSQL**: Too heavy to set up/run locally for a capstone demo; same deferral as SQLite.
- **Direct blockchain ledger**: Explicitly out of scope per the spec's Assumptions and Future Extension Ideas — the MVP only needs to be *ready* for this, not implement it.

## R2: How the internal simulated transaction ledger validates transaction references

**Decision**: A dedicated `TransactionLedger` service (backed by its own in-memory repository, per R1) owns `Transaction` records with `transaction_id`, `status` (`pending` | `confirmed` | `failed`), an optional `value`, and an optional `linked_event_id`. Flow:

1. Before submitting a lifecycle transition, the initiating client creates a transaction via `POST /transactions`, which the MVP immediately marks `confirmed` (simulating payment settlement — no real gateway call).
2. The lifecycle transition request (`POST /products/{dpp_id}/lifecycle-events`) must include that `transaction_id`.
3. `LifecycleService.transition()` calls `TransactionLedger.get(transaction_id)` and only proceeds if the transaction exists, `status == "confirmed"`, and `linked_event_id` is still empty (a transaction can back at most one lifecycle event — prevents replay/reuse).
4. On success, the ledger sets `linked_event_id` to the new lifecycle event's id; on any failure the lifecycle state is left unchanged and a 4xx error is returned.

**Rationale**:
- Directly satisfies FR-006/FR-007 (validate the referenced transaction against the ledger before committing any state change) and FR-009 (every event records its linked transaction reference).
- The one-transaction-per-event rule gives simple, testable replay protection without needing real payment infrastructure.
- Keeping the ledger as its own service (not inline fields on the lifecycle payload) means it can be independently unit-tested and later swapped for a real payment-gateway webhook handler or blockchain settlement check (per spec Future Extension Ideas) without changing the lifecycle state machine.

**Alternatives considered**:
- **Trusting a `transaction_id` string supplied by the client with no backing record**: Rejected — this would make lifecycle validation no stronger than a QR scan, which directly contradicts the feature's core requirement (FR-006).
- **Calling a real external payment API in the MVP**: Rejected — explicitly deferred per the spec's Assumptions ("payment-linked transaction" is backed by an internal simulated ledger for the MVP).

## R3: Modeling and enforcing the lifecycle state machine in code

**Decision**: Represent lifecycle state as a Python `Enum`, `LifecycleState = {MANUFACTURED, OWNED, COLLECTED, RECYCLED, CLOSED}`, and define an explicit transition table (`dict[LifecycleState, set[LifecycleState]]`) that only allows the forward path `MANUFACTURED → OWNED → COLLECTED → RECYCLED → CLOSED`. `LifecycleService.transition(dpp_id, target_state, transaction_id, actor)` looks up the product's current state, checks `target_state` is in the allowed-next set, and raises a domain-specific `InvalidTransitionError` (mapped to HTTP 409) if not — covering skipped states, reversed order, and any transition attempted from `CLOSED`.

**Rationale**:
- Puts every valid/invalid transition rule in one place instead of scattering `if` checks across routers, directly satisfying FR-008 and the spec's edge cases about out-of-order and post-closure transitions.
- An explicit table (rather than free-form string comparisons) is trivial to unit-test exhaustively with pytest (`@pytest.mark.parametrize` over all state pairs).
- No new dependency required — 5 states/4 transitions don't justify a full state-machine library.

**Alternatives considered**:
- **Free-form status string with ad hoc validation per router**: Rejected — error-prone and hard to test exhaustively; risks silently accepting an invalid transition.
- **Third-party state-machine library (e.g. `transitions`)**: Rejected as unnecessary complexity for 5 states in a capstone MVP; can be revisited if the state machine grows more complex in a later phase.

## Note on role-based access for the MVP

Not one of the three items requested for this research pass, but needed to make the contracts in Phase 1 concrete: the MVP uses a lightweight mock-auth scheme — each request carries `X-Role` and `X-User-Id` headers identifying the caller's role (`manufacturer` | `consumer` | `recycler` | `regulator`) and identity, which `services/` check against FR-011–FR-015's per-role permissions. This satisfies NFR-003 (every lifecycle-changing action is authenticated) without building full OAuth/session infrastructure, which is out of scope for the capstone MVP. Real authentication is a future-phase concern, not a lifecycle-model concern, so it does not affect the data model or state machine above.
