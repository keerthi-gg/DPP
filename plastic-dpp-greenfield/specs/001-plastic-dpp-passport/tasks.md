# Tasks: Plastic DPP Greenfield — Blockchain-Enabled Digital Product Passport

**Input**: Design documents from `specs/001-plastic-dpp-passport/`

**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Included per user request — contract tests per endpoint, unit tests for the lifecycle state machine and transaction ledger, and integration tests for the end-to-end flow.

**Organization**: Tasks are grouped by user story (US1–US4, per spec.md priorities P1–P4) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US4)
- File paths follow the Project Structure in [plan.md](./plan.md): `backend/app/{models,services,routers,storage}/`, `backend/tests/{unit,contract,integration}/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic module structure, refactoring the existing flat `backend/app/main.py`.

- [X] T001 Create `backend/app/models/`, `backend/app/services/`, `backend/app/routers/`, `backend/app/storage/` packages (each with `__init__.py`) per the Project Structure in [plan.md](./plan.md)
- [X] T002 Create `backend/tests/unit/`, `backend/tests/contract/`, `backend/tests/integration/` packages (each with `__init__.py`)
- [X] T003 [P] Add a shared `TestClient` fixture in `backend/tests/conftest.py` for use by contract and integration tests

**Checkpoint**: Module skeleton exists; no behavior yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Define `Role` enum (`manufacturer`/`consumer`/`recycler`/`regulator`) and `UserRoleAccount` model in `backend/app/models/account.py` (data-model.md: UserRoleAccount)
- [X] T005 [P] Define `LifecycleState` enum and the allowed-transition table (`MANUFACTURED→OWNED→COLLECTED→RECYCLED→CLOSED`, no transitions out of `CLOSED`) in `backend/app/models/lifecycle.py` (research.md R3)
- [X] T006 [P] Define a generic `Repository` base interface (`get`/`add`/`list`) in `backend/app/storage/base.py` (research.md R1)
- [X] T007 Implement a mock-auth dependency that reads `X-Role`/`X-User-Id` headers and resolves a `UserRoleAccount` in `backend/app/routers/dependencies.py` (depends on T004; research.md "Note on role-based access", NFR-003)
- [X] T008 [P] Define domain exceptions (`NotFoundError`, `InvalidTransitionError`, `UnauthorizedRoleError`, `InvalidTransactionError`) in `backend/app/services/errors.py`
- [X] T009 Assemble the FastAPI app skeleton and register exception handlers mapping domain exceptions to HTTP 404/403/409/400 in `backend/app/main.py` (depends on T007, T008)

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Manufacturer registers a product and issues its DPP (Priority: P1) 🎯 MVP

**Goal**: A manufacturer submits product details and receives a unique DPP + bound QR code (FR-001, FR-002).

**Independent Test**: `POST /products` as `manufacturer` → `201` with `dpp_id`/`qr_code_ref`/`current_state: "manufactured"`; missing required field → `400`; non-manufacturer role → `403` (contracts/products.md).

### Tests for User Story 1

- [X] T010 [P] [US1] Contract test for `POST /products` (201 success, 400 missing field, 403 wrong role) in `backend/tests/contract/test_products_register.py`
- [X] T011 [P] [US1] Unit test asserting `dpp_id`/`qr_code_ref` are unique and immutable once assigned in `backend/tests/unit/test_dpp_generation.py`

### Implementation for User Story 1

- [X] T012 [P] [US1] Create `DigitalProductPassport` and `QRCode` Pydantic models in `backend/app/models/product.py` (data-model.md: DPP, QRCode)
- [X] T013 [P] [US1] Implement in-memory `ProductRepository` in `backend/app/storage/product_repository.py` (extends T006; research.md R1)
- [X] T014 [US1] Implement `ProductService.register_product()` — field validation, `dpp_id`/`qr_code_ref` generation, initial state `MANUFACTURED` — in `backend/app/services/product_service.py` (depends on T012, T013)
- [X] T015 [US1] Implement `POST /products` route (manufacturer-only, per T007) in `backend/app/routers/products.py` (depends on T014)
- [X] T016 [US1] Register the products router in `backend/app/main.py` (depends on T015)

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Any stakeholder authenticates and looks up a product (Priority: P2)

**Goal**: Any role can look up a product's identity/status by QR code or DPP ID, read-only (FR-003, FR-004, FR-005).

**Independent Test**: `GET /products/{dpp_id}` and `GET /products/lookup?qr_code=...` return `200` for a known product and `404` for an unknown one; neither call changes `current_state` (contracts/products.md).

### Tests for User Story 2

- [X] T017 [P] [US2] Contract test for `GET /products/{dpp_id}` (200 + 404) in `backend/tests/contract/test_products_lookup.py`
- [X] T018 [P] [US2] Contract test for `GET /products/lookup?qr_code=...` (200 + 404) in `backend/tests/contract/test_products_qr_lookup.py`
- [X] T019 [P] [US2] Contract test for `GET /products` list in `backend/tests/contract/test_products_list.py`
- [X] T020 [P] [US2] Integration test confirming a lookup/scan never changes `current_state` in `backend/tests/integration/test_lookup_is_read_only.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement `ProductService.get_by_dpp_id()` and `get_by_qr_code()` in `backend/app/services/product_service.py` (extends US1's service/repository)
- [X] T022 [US2] Implement `GET /products/{dpp_id}`, `GET /products/lookup`, `GET /products` routes in `backend/app/routers/products.py` (depends on T021)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Lifecycle event recorded via payment-linked transaction (Priority: P3) 🎯 MVP

**Goal**: Consumers/recyclers record lifecycle transitions only when backed by a confirmed payment-linked transaction (FR-006–FR-009, FR-013, FR-015).

**Independent Test**: create a transaction, then `POST /products/{dpp_id}/lifecycle-events` with a valid `transaction_id` → `201` + state updates; missing/invalid/reused `transaction_id` → `400`; wrong role → `403`; out-of-order or post-`closed` transition → `409`; the event then appears in `GET /products/{dpp_id}/history` (contracts/lifecycle.md).

### Tests for User Story 3

- [X] T023 [P] [US3] Contract test for `POST /transactions` in `backend/tests/contract/test_transactions_create.py`
- [X] T024 [P] [US3] Contract test for `POST /products/{dpp_id}/lifecycle-events` (201, 400 bad/reused transaction, 403 wrong role, 404 unknown product, 409 invalid transition) in `backend/tests/contract/test_lifecycle_events.py`
- [X] T025 [P] [US3] Contract test for `GET /products/{dpp_id}/history` in `backend/tests/contract/test_lifecycle_history.py`
- [X] T026 [P] [US3] Unit test for the lifecycle transition table, including rejecting skipped/reversed states and any transition from `CLOSED` in `backend/tests/unit/test_lifecycle_state_machine.py`
- [X] T027 [P] [US3] Unit test for transaction ledger validation and one-transaction-per-event replay protection in `backend/tests/unit/test_transaction_ledger.py`
- [X] T028 [US3] Integration test for the full register → lookup → transaction → transition → history flow in `backend/tests/integration/test_lifecycle_flow.py` (depends on US1/US2 routes)

### Implementation for User Story 3

- [X] T029 [P] [US3] Implement in-memory `TransactionRepository` and `LifecycleEventRepository` in `backend/app/storage/transaction_repository.py` and `backend/app/storage/lifecycle_repository.py` (extends T006)
- [X] T030 [P] [US3] Create `LifecycleEvent` and `Transaction` Pydantic models in `backend/app/models/lifecycle_event.py` and `backend/app/models/transaction.py` (data-model.md)
- [X] T031 [US3] Implement `TransactionLedger` service (create/get, immediate `confirmed` status, `linked_event_id` reuse guard) in `backend/app/services/transaction_service.py` (depends on T029, T030; research.md R2)
- [X] T032 [US3] Implement `LifecycleService.transition()` — enforces the transition table (T005), role gating (T004), and transaction validation (T031) — in `backend/app/services/lifecycle_service.py`
- [X] T033 [US3] Implement `POST /transactions` route in `backend/app/routers/transactions.py` (depends on T031)
- [X] T034 [US3] Implement `POST /products/{dpp_id}/lifecycle-events` and `GET /products/{dpp_id}/history` routes in `backend/app/routers/lifecycle.py` (depends on T032)
- [X] T035 [US3] Register the transactions and lifecycle routers in `backend/app/main.py` (depends on T033, T034)

**Checkpoint**: User Stories 1–3 — the MVP slice — are fully functional and independently testable; the core value proposition (payment-linked lifecycle validation) is proven end-to-end.

---

## Phase 6: User Story 4 - Regulator reviews lifecycle history and compliance reporting (Priority: P4)

**Goal**: Regulators get read-only access to full lifecycle history and an aggregated compliance report (FR-014).

**Independent Test**: `GET /regulator/report` as `regulator` → `200` with per-state counts; as any other role → `403`; a regulator attempting `POST /products` or `POST /products/{dpp_id}/lifecycle-events` → `403` (contracts/regulator.md).

### Tests for User Story 4

- [X] T036 [P] [US4] Contract test for `GET /regulator/report` (200 + 403 for non-regulator) in `backend/tests/contract/test_regulator_report.py`
- [X] T037 [P] [US4] Integration test confirming the regulator role is rejected with `403` on `POST /products` and `POST /products/{dpp_id}/lifecycle-events` in `backend/tests/integration/test_regulator_read_only.py`

### Implementation for User Story 4

- [X] T038 [US4] Implement `ReportingService.aggregate_by_state()` in `backend/app/services/reporting_service.py` (reads from US1's `ProductRepository`)
- [X] T039 [US4] Implement `GET /regulator/report` route (regulator-only, per T007) in `backend/app/routers/regulator.py` (depends on T038)
- [X] T040 [US4] Register the regulator router in `backend/app/main.py` (depends on T039)

**Checkpoint**: All four user stories are independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Clean-up and repo-wide consistency after all user stories are complete.

- [X] T041 [P] Replace `backend/tests/test_main.py` (old flat-model product tests) with a `backend/tests/unit/test_health.py` covering just the `/health` endpoint, since product endpoints are now covered by the contract/integration tests above
- [X] T042 [P] Add structured logging of actor, role, timestamp, and action for every lifecycle-changing request (NFR-007) in `backend/app/routers/dependencies.py`
- [X] T043 [P] Add FastAPI route summaries/descriptions so `/docs` reflects the contracts in [contracts/](./contracts/)
- [X] T044 Cross-check [quickstart.md](./quickstart.md) commands against the implemented routes and update if any path/payload drifted
- [X] T045 Run the full `pytest` suite and confirm all unit, contract, and integration tests pass

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)**: strictly sequential; Foundational blocks all user stories.
- **Phase 3 (US1)**: depends only on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2 and reuses US1's `ProductRepository`/`ProductService` (T013/T014) — implement after US1.
- **Phase 5 (US3)**: depends on Phase 2 and on US1's product repository/service existing (a transition needs a product to act on) — implement after US1; independent of US2.
- **Phase 6 (US4)**: depends on Phase 2 and on US1's `ProductRepository` (for aggregation) and US3's lifecycle event data (for history) — implement last.
- **Phase 7 (Polish)**: after all user stories.

Within each user story, `[P]`-marked tasks touch different files and can run in parallel; non-`[P]` tasks depend on a preceding task in the same phase (noted inline).

## Parallel Execution Examples

- **Foundational**: T004, T005, T006, T008 can all run in parallel (different files); T007 waits on T004, T009 waits on T007+T008.
- **US1**: T010, T011, T012, T013 can run in parallel; T014 waits on T012+T013; T015 waits on T014; T016 waits on T015.
- **US3**: T023–T027 (all test files) can run in parallel; T029, T030 can run in parallel; T031 waits on T029+T030; T032 waits on T031; T033/T034 wait on T032.

## Implementation Strategy

**MVP first**: Complete Phases 1–5 (Setup → Foundational → US1 → US2 → US3) and stop there for the first working demo. This proves the feature's core claim — lifecycle changes require a validated payment-linked transaction, not just a QR scan — end-to-end, matching [quickstart.md](./quickstart.md).

**Incremental delivery**: Add Phase 6 (US4 regulator reporting) once the MVP is validated, then Phase 7 (polish) last. Each phase leaves the system in a fully working, independently testable state per its Checkpoint.
