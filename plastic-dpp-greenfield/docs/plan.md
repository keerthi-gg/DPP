# Project Plan

## Goal

Deliver a greenfield MVP for a plastic product traceability and recycling platform.

## Assumptions

- The initial build is API-first and can be extended to blockchain later.
- The MVP focuses on product lifecycle records and payment-linked event validation logic.
- The app will demonstrate the key project concept without requiring a full production blockchain deployment.

## Architecture

- API layer: FastAPI
- Data layer: in-memory store for MVP, ready for database extension
- Validation layer: lifecycle status and event rules
- Future phase: blockchain adapter, QR lookup service, wallet integration

## Milestones

### Phase 1: MVP foundation
- Create product model
- Implement product creation and listing
- Add health endpoint
- Add unit tests

### Phase 2: lifecycle logic
- Add lifecycle status transitions
- Add validation for invalid state jumps
- Add event records for manufacturer, recycler, and consumer flow

### Phase 3: extensibility
- Add persistence with SQLite or Postgres
- Integrate QR service and wallet hooks
- Add reporting and dashboard views

## Recommended technology stack

- Backend: Python + FastAPI
- Validation: Pydantic models
- Testing: pytest
- Future blockchain: Hyperledger Fabric or Ethereum
- Future storage: PostgreSQL / IPFS
