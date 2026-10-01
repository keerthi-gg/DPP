# API Contract: Regulator Reporting

**Feature**: [../spec.md](../spec.md) | **Data model**: [../data-model.md](../data-model.md)

## GET /regulator/report

Aggregated, read-only compliance summary across all products (FR-014; US4 AS2).

**Auth**: `X-Role: regulator` required. Any other role → `403`.

**Responses**:
- `200 OK`:
  ```json
  {
    "total_products": 120,
    "by_state": {
      "manufactured": 10,
      "owned": 40,
      "collected": 25,
      "recycled": 30,
      "closed": 15
    }
  }
  ```

## GET /products/{dpp_id}/history (regulator use)

Regulators use the same read-only history endpoint defined in [lifecycle.md](./lifecycle.md) to inspect a specific product's full event trail (US4 AS1). No separate regulator-only endpoint is needed for this — access control is enforced by role, not by a distinct route.

**Enforcement note**: Any `PUT`/`PATCH`/`DELETE` attempt against a product or lifecycle event by a `regulator` role MUST be rejected with `403 Forbidden` — the regulator role is read-only system-wide (US4 AS3). The MVP has no such mutating endpoints exposed to any role other than the lifecycle-event creation flow in [lifecycle.md](./lifecycle.md), so this is enforced simply by never routing regulator-role tokens to state-changing services.
