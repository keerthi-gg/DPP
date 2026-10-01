# Implementation Plan: Plastic DPP Greenfield — Blockchain-Enabled Digital Product Passport

**Branch**: `001-plastic-dpp-passport` | **Date**: 2026-09-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-plastic-dpp-passport/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Deliver an MVP backend that issues a unique Digital Product Passport (DPP) and bound QR code for every plastic product, lets any stakeholder look that product up read-only via QR/DPP ID, and only records lifecycle transitions (Manufactured → Owned → Collected → Recycled → Closed) when they are backed by a validated, payment-linked transaction. The MVP simulates the payment layer with an internal transaction ledger service so the data model and API contracts are ready to swap in a real payment gateway and/or blockchain-backed storage later without redesign. Built on the existing `backend/` FastAPI app, refactored from a single `main.py` into models/services/routers/storage modules.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: FastAPI 0.115, Pydantic v2 (via FastAPI), Uvicorn (ASGI server) — all already in [backend/requirements.txt](../../backend/requirements.txt)

**Storage**: In-memory Python dict-based repositories for the MVP (one per entity: DPPs, Lifecycle Events, Transactions, Accounts), hidden behind a repository interface so SQLite/PostgreSQL can be swapped in later (see [research.md](./research.md) R1)

**Testing**: pytest + FastAPI `TestClient`/httpx, matching the existing [backend/tests/test_main.py](../../backend/tests/test_main.py) pattern

**Target Platform**: Linux-deployable ASGI server (uvicorn), developed and run locally on Windows for the capstone

**Project Type**: Single backend web-service (no frontend in MVP scope)

**Performance Goals**: Lookup requests (QR/DPP ID) respond in under 5 seconds (NFR-002/SC-003); product registration completes in under 1 minute end-to-end (SC-001)

**Constraints**: Lifecycle history is append-only — no edits/deletes once committed (FR-010/NFR-001); no lifecycle change may be accepted without a confirmed payment-linked transaction reference (FR-006, SC-002); no real payment gateway or blockchain dependency in the MVP (simulated ledger only, per spec Assumptions)

**Scale/Scope**: 4 roles (Manufacturer, Consumer, Recycler, Regulator), a 5-state lifecycle machine, ~9 REST endpoints, at least 100 concurrently registered products with independent histories (NFR-005/SC-006)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[.specify/memory/constitution.md](../../.specify/memory/constitution.md) contains only unfilled template placeholders (`[PRINCIPLE_1_NAME]`, etc.) — no principles have been ratified for this project yet. There are no gates to evaluate against, so this check passes trivially. **Re-run this check once the constitution is ratified**, since it may retroactively impose constraints (e.g., test-first discipline, simplicity limits) on this plan.

## Project Structure

### Documentation (this feature)

```text
specs/001-plastic-dpp-passport/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py            # FastAPI app assembly; includes routers
│   ├── models/            # Pydantic models: DPP, QRCode, LifecycleEvent, Transaction, Account
│   ├── services/          # Domain logic: registration, lookup, lifecycle transitions, ledger validation
│   ├── routers/            # API route modules: products, lifecycle, transactions, regulator
│   └── storage/           # In-memory repositories behind a swappable interface
├── tests/
│   ├── unit/               # Service/model-level tests (state machine, ledger validation)
│   ├── contract/           # Request/response contract tests per endpoint
│   └── integration/        # End-to-end flows (register → lookup → transition → history)
└── requirements.txt
```

**Structure Decision**: Single backend web-service project — no frontend exists or is planned for the MVP, so this is Option 1 (single project) adapted to the repository's existing `backend/` root rather than a generic `src/`. The current flat `backend/app/main.py` (product model + two endpoints, see [backend/app/main.py](../../backend/app/main.py)) is refactored into `models/`, `services/`, `routers/`, and `storage/` submodules, and `backend/tests/` is split into `unit/`, `contract/`, and `integration/` to match the testing strategy in [research.md](./research.md).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Not applicable — the Constitution Check above found no ratified principles to violate.
