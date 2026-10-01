# Feature Specification: Plastic DPP Greenfield — Blockchain-Enabled Digital Product Passport

**Feature Branch**: `001-plastic-dpp-passport`

**Created**: 2026-09-30

**Status**: Draft

**Input**: User description: "A blockchain-enabled digital product passport (DPP) system for plastic waste management and circular economy tracking. Each plastic product gets a unique digital identity and QR code. The QR code is used mainly for authentication and lookup. Lifecycle updates, such as ownership transfer, collection, recycling, and closure, should be validated through payment-linked transactions rather than only QR scans. The system should support manufacturers, consumers, recyclers, and regulators."

## Project Vision

Build a trustworthy Digital Product Passport platform for plastic products where every item carries a unique, verifiable digital identity from manufacture through end-of-life. Rather than relying on QR scans alone — which can be spoofed, duplicated, or scanned without any real-world action happening — every meaningful lifecycle change is anchored to a payment-linked transaction, so the recorded history reflects real economic activity (a sale, a collection payout, a recycling settlement). Over time this creates a dataset that manufacturers, consumers, recyclers, and regulators can all trust for circular-economy decision-making, compliance reporting, and eventually blockchain-backed verification.

## Problem Statement

Plastic products today have no persistent, trustworthy digital identity that follows them through their lifecycle. Existing tracking approaches (labels, manual logs, simple QR scans) can be gamed — a scan proves someone had a camera near a code, not that collection, recycling, or a legitimate ownership change actually took place. This makes it hard for regulators to verify compliance, hard for recyclers and consumers to prove their part of the loop was completed, and hard for manufacturers to report credible circular-economy outcomes. The system needs a way to tie each lifecycle claim to independently verifiable evidence — a payment-linked transaction — while still keeping QR-based lookup fast and simple for everyday authentication.

## Goals

- Give every plastic product a unique digital identity (DPP) and a bound QR code at the point of manufacture.
- Make QR codes useful for fast authentication and lookup, without making them a single point of trust for lifecycle changes.
- Require a payment-linked transaction to validate any lifecycle-changing event (ownership transfer, collection, recycling, closure).
- Maintain a complete, tamper-resistant, append-only history of each product's lifecycle events.
- Support four distinct stakeholder roles — manufacturer, consumer, recycler, regulator — each with the right level of access and permissions.
- Provide regulators with reliable, auditable data for compliance and sustainability reporting.
- Lay an architectural foundation that can be extended to real payment rails and/or blockchain settlement without redesigning the core data model.

## User Roles

- **Manufacturer**: Creates plastic products and registers their initial Digital Product Passport (DPP) and QR code. Cannot alter lifecycle history after creation, only view it.
- **Consumer**: Owns or holds a product during its in-use phase. Can look up a product's identity/status via QR/DPP ID, and can initiate a payment-linked lifecycle event when transferring ownership or handing a product off for collection.
- **Recycler**: Collects products from consumers and processes them. Can look up products and confirm payment-linked collection and recycling lifecycle events.
- **Regulator**: An external compliance/oversight stakeholder (e.g., an environmental or waste-management authority) — distinct from a system administrator who manages accounts/infrastructure. Has read-only access to full lifecycle histories and aggregated compliance/reporting data across all products; cannot create, edit, or delete records.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manufacturer registers a product and issues its Digital Product Passport (Priority: P1)

A manufacturer submits details for a new plastic product and the system creates a unique Digital Product Passport (DPP) record along with a bound QR code.

**Why this priority**: Nothing else in the system can function without a product first existing as a DPP — this is the foundational capability every other story depends on.

**Independent Test**: Can be fully tested by having a manufacturer submit product details and confirming a unique DPP ID and QR code are generated and retrievable, independent of any lifecycle or payment logic.

**Acceptance Scenarios**:

1. **Given** a manufacturer is authenticated in the system, **When** they submit valid product details (product type, material composition summary, batch/manufacture date), **Then** the system creates a new DPP record with a unique ID and a bound QR code, and the product's initial lifecycle state is set to "Manufactured".
2. **Given** a manufacturer submits product details with missing required fields, **When** they attempt to register the product, **Then** the system rejects the request and indicates which fields are missing.

---

### User Story 2 - Any stakeholder authenticates and looks up a product via QR code or DPP ID (Priority: P2)

Any stakeholder (manufacturer, consumer, recycler, regulator) scans a product's QR code or enters its DPP ID to confirm the product's authenticity and see its current status.

**Why this priority**: Establishes trust and identity confirmation before any lifecycle action is taken. Every other role-based flow depends on it, but a lookup alone changes nothing, so it ranks just below registration.

**Independent Test**: Can be fully tested by scanning/querying an existing DPP ID and confirming the system returns accurate, read-only product identity and current lifecycle status without altering any data.

**Acceptance Scenarios**:

1. **Given** a product has a valid DPP and QR code, **When** a user scans the QR code or enters the DPP ID, **Then** the system returns the product's identity details and current lifecycle status.
2. **Given** a user enters a DPP ID that does not exist or an invalid QR code, **When** they attempt the lookup, **Then** the system returns a clear "not found / invalid" response and records no lifecycle change.
3. **Given** a user scans a valid QR code, **When** the scan completes, **Then** the system does not change the product's lifecycle state as a result of the scan alone.

---

### User Story 3 - Lifecycle event recorded via payment-linked transaction (Priority: P3)

Consumers and recyclers record lifecycle transitions (ownership transfer, collection, recycling, closure) for a product, and each transition is only accepted when a payment-linked transaction backs it.

**Why this priority**: This is the core trust mechanism requested — depends on Stories 1 and 2 already existing, but delivers the central value proposition of tamper-resistant lifecycle tracking.

**Independent Test**: Can be fully tested by attempting a lifecycle transition with and without a valid payment-linked transaction reference and confirming the system accepts only the backed transition.

**Acceptance Scenarios**:

1. **Given** a product exists in state "Manufactured" and a valid payment-linked transaction reference is provided, **When** a consumer ownership-transfer event is submitted, **Then** the system updates the product's lifecycle state to "Owned" and records the transaction reference, actor, and timestamp.
2. **Given** a product is in state "Owned" and a recycler submits a collection event with a valid payment-linked transaction reference, **When** the event is processed, **Then** the product's lifecycle state updates to "Collected".
3. **Given** a lifecycle transition is submitted without a valid or confirmed payment-linked transaction reference, **When** the system processes the request, **Then** it rejects the transition and the product's lifecycle state remains unchanged.
4. **Given** a product is in state "Closed", **When** any user attempts to submit a further lifecycle transition for it, **Then** the system rejects the request because the state machine does not permit transitions out of a closed state.
5. **Given** a valid lifecycle transition is recorded, **When** an authorized viewer later looks up the product, **Then** the transition, its actor, and its transaction reference appear in the product's immutable event history.

---

### User Story 4 - Regulator reviews lifecycle history and compliance reporting (Priority: P4)

Regulators access read-only lifecycle history and aggregated reporting data across products to verify compliance with recycling and circular-economy requirements.

**Why this priority**: Adds oversight/reporting value on top of the core tracking capability but isn't required for the base product-tracking loop to function, making it the right scope to add last within the MVP.

**Independent Test**: Can be fully tested by seeding several products with recorded lifecycle histories and confirming a regulator account can view full event histories and an aggregated summary without being able to modify any record.

**Acceptance Scenarios**:

1. **Given** a regulator is authenticated, **When** they query a specific product's history, **Then** they see every recorded lifecycle event with actor, timestamp, and transaction reference in order.
2. **Given** multiple products have recorded lifecycle events, **When** a regulator requests an aggregated compliance report, **Then** the system returns counts/summaries of products by lifecycle state (e.g., number recycled, number closed).
3. **Given** a regulator views a product record, **When** they attempt to edit or delete a lifecycle event, **Then** the system denies the action because the regulator role is read-only.

---

### Edge Cases

- What happens when a payment-linked transaction is submitted for a lifecycle event but the transaction later fails, is reversed, or times out after the state change was tentatively recorded?
- How does the system handle a QR/DPP ID lookup for a product that has already reached the "Closed" state — should identity/history still be viewable?
- What happens when two different actors submit competing lifecycle transitions for the same product at nearly the same time (e.g., two recyclers both claim collection)?
- How does the system handle a manufacturer attempting to register a duplicate product identity or reuse an already-issued DPP ID?
- What happens when a QR code is damaged, duplicated, or copied onto a counterfeit product?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow manufacturers to register a new plastic product, capturing product type, material composition summary, batch/manufacture date, and manufacturer identity.
- **FR-002**: System MUST generate a unique Digital Product Passport (DPP) identifier and a bound QR code for every registered product.
- **FR-003**: System MUST allow any authenticated user to look up a product's identity and current lifecycle status by scanning its QR code or submitting its DPP ID.
- **FR-004**: System MUST treat QR code scans and DPP ID lookups as read-only actions that never change a product's lifecycle state on their own.
- **FR-005**: System MUST reject a lookup request for a DPP ID or QR code that does not match a known product, returning a clear "not found" result without creating or altering any record.
- **FR-006**: System MUST record a lifecycle state change (ownership transfer, collection, recycling, closure) only when it is submitted together with a valid, confirmed payment-linked transaction reference.
- **FR-007**: System MUST validate the referenced payment-linked transaction against the transaction ledger before committing any lifecycle state change.
- **FR-008**: System MUST enforce an ordered lifecycle state machine (Manufactured → Owned → Collected → Recycled → Closed) and reject any transition that skips states, reverses order, or acts on an already-closed product.
- **FR-009**: System MUST record, for every accepted lifecycle event, the initiating actor (identity and role), timestamp, prior state, new state, and the linked transaction reference.
- **FR-010**: System MUST keep lifecycle event history append-only; once committed, an event record MUST NOT be edited or deleted by any role.
- **FR-011**: System MUST support four distinct roles — Manufacturer, Consumer, Recycler, Regulator — each with role-appropriate permissions for which actions they may initiate.
- **FR-012**: System MUST restrict product registration actions to the Manufacturer role.
- **FR-013**: System MUST allow Consumer and Recycler roles to initiate the lifecycle transitions relevant to their part of the product journey (consumer-side ownership transfer; recycler-side collection and recycling), each gated by a payment-linked transaction.
- **FR-014**: System MUST give the Regulator role read-only access to the full lifecycle history and an aggregated compliance/reporting view across all products.
- **FR-015**: System MUST reject any lifecycle-changing request from a role that is not authorized to perform that specific transition.
- **FR-016**: System MUST return a clear, actionable error message when a lifecycle update is rejected (e.g., missing/invalid transaction reference, invalid state transition, unauthorized role).

### Non-Functional Requirements

- **NFR-001**: The system MUST keep an immutable, auditable record of every lifecycle event (append-only, no edits or deletes).
- **NFR-002**: Lookup requests (QR scan / DPP ID query) MUST return a response within 5 seconds under normal load.
- **NFR-003**: The system MUST authenticate every user and role before permitting any lifecycle-changing action; unauthenticated users may perform read-only lookups only.
- **NFR-004**: The data model MUST be structured so a future blockchain or distributed-ledger backend can be introduced without redesigning the DPP or lifecycle event schema.
- **NFR-005**: The system MUST support at least 100 concurrently registered products with independent lifecycle histories without cross-contaminating data between products.
- **NFR-006**: The system MUST provide a documented, API-first interface so future consumer apps, recycler apps, and regulator dashboards can integrate without backend changes.
- **NFR-007**: All role-based actions MUST be logged with enough detail (actor, role, timestamp, action) to support later compliance audits.

### Key Entities

- **Digital Product Passport (DPP)**: A single plastic product's unique digital identity. Attributes: DPP ID, product type, material composition summary, manufacture date, manufacturer reference, current lifecycle state, bound QR code reference.
- **QR Code**: A scannable reference bound 1:1 to a DPP, used only for authentication/lookup — never for lifecycle validation on its own.
- **Lifecycle Event**: An append-only record of a state transition. Attributes: event ID, DPP reference, prior state, new state, actor identity/role, timestamp, linked transaction reference.
- **Transaction (payment-linked)**: A reference to a validated payment or ledger-credit action that authorizes a lifecycle event. Attributes: transaction ID, value (if applicable), status (confirmed/failed/pending), linked lifecycle event.
- **User/Role Account**: Represents a stakeholder (Manufacturer, Consumer, Recycler, Regulator) with an identity and an assigned role governing permitted actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A manufacturer can register a new product and receive a working DPP ID and QR code in under 1 minute.
- **SC-002**: 100% of lifecycle state changes recorded in the system have a valid, linked payment transaction reference — zero lifecycle updates are accepted from a QR scan alone.
- **SC-003**: Any stakeholder can look up a product's identity and current status via QR/DPP ID lookup in under 5 seconds.
- **SC-004**: 100% of invalid lifecycle transitions (out-of-order, unauthorized role, missing transaction) are rejected with a clear error rather than silently applied.
- **SC-005**: A regulator can retrieve the complete, ordered lifecycle history for any product and an aggregated compliance summary across all products without needing engineering support to interpret the data.
- **SC-006**: The system supports at least 100 concurrently registered products with independent lifecycle histories without data cross-contamination, validating the MVP's core traceability model.

## MVP Scope

**In scope for MVP**:

- Manufacturer product registration producing a DPP + QR code
- QR code / DPP ID lookup (read-only) available to all roles
- Lifecycle state machine: Manufactured → Owned → Collected → Recycled → Closed
- Payment-linked validation backed by an internal simulated transaction ledger (not a live payment gateway or real blockchain settlement)
- Role-based permissions for Manufacturer, Consumer, Recycler, Regulator
- Append-only lifecycle event history with actor, timestamp, and transaction reference
- Regulator read-only view of full lifecycle history plus a basic aggregated compliance summary

**Out of scope for MVP** (explicitly deferred):

- Real payment gateway or live blockchain/crypto-token settlement
- On-chain storage of DPP or lifecycle event data
- Consumer recycling rewards/incentive programs
- Multi-owner/resale-chain product histories (MVP assumes one linear ownership path)
- Jurisdiction- or category-scoped regulator accounts
- Native mobile apps and QR anti-counterfeiting cryptographic signing
- Integration with external municipal or third-party waste-collection systems

## Assumptions

- For the MVP, a "payment-linked transaction" is backed by an internal simulated transaction/ledger system rather than a live payment gateway or real blockchain/crypto settlement; real payment and blockchain integration are deferred to a future phase (confirmed with the user).
- Regulators are given full read-only access to all products' lifecycle histories and reporting data in the MVP. "Regulator" is treated as an external compliance/oversight stakeholder, distinct from a system administrator who manages accounts/infrastructure; jurisdiction- or category-scoped regulator access is deferred (confirmed with the user).
- The lifecycle state machine for the MVP is: Manufactured → Owned → Collected → Recycled → Closed, matching the events named in the request (ownership transfer, collection, recycling, closure).
- Product identity data is stored off-chain in the MVP (database-backed), architected so a blockchain ledger can be introduced in a later phase without redesigning the DPP data model.
- QR codes are used exclusively for authentication/identity lookup and never as sole authorization for a lifecycle change, per the explicit requirement in the feature description.
- Each product is associated with exactly one manufacturer and progresses through a single linear ownership chain for the MVP (no multi-owner/resale-chain complexity yet).
- Basic role-based access control (Manufacturer, Consumer, Recycler, Regulator) is sufficient for the MVP; more granular permission tiers are a future extension.

## Future Extension Ideas

- Replace the internal simulated transaction ledger with real payment gateway integration and/or blockchain/crypto-token settlement for lifecycle validation.
- Move DPP and lifecycle event storage onto a blockchain or hybrid on-chain/off-chain ledger for tamper-evident, decentralized verification.
- Add jurisdiction- or category-scoped regulator access and support for multiple regulatory bodies.
- Introduce consumer recycling incentives/rewards (e.g., token or discount credits) triggered by verified recycling events.
- Support multi-owner/resale chains (a product changing hands multiple times before recycling) instead of a single linear ownership path.
- Add manufacturer-facing ESG/sustainability dashboards and exportable compliance reports.
- Add QR code tamper-detection/anti-counterfeiting measures (e.g., cryptographic signing of QR payloads).
- Integrate with external municipal or third-party waste-collection systems via APIs.
- Add mobile app/wallet integration for consumers and recyclers to scan and initiate transactions in the field.
- Support batch/bulk product registration for manufacturers with high-volume production lines.
