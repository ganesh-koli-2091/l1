# Common API Patterns

## Pagination

All list endpoints use cursor-free offset pagination with `page` and `pageSize` query parameters.

| Parameter | Type    | Default | Max   |
|-----------|---------|---------|-------|
| page      | integer | 1       | —     |
| pageSize  | integer | 20      | 100   |

**Response envelope for paginated results:**
```json
{
  "data": [...],
  "total": 142,
  "page": 1,
  "pageSize": 20
}
```

Use `total` to calculate the number of pages: `Math.ceil(total / pageSize)`.

## Filtering

Filtering is done via query parameters. Filters are AND-combined — there is no OR filter support.

Common filter parameters across services:
- Date ranges: `fromDate` and `toDate` (ISO 8601 date, e.g. `2024-01-15`)
- Status: `status` enum parameter (service-specific values)
- Owner: `customerId` to scope results to one customer

## Sorting

Sorting uses a `sortBy` query parameter with a fixed enum of allowed sort keys per endpoint.
There is no dynamic sort-by-any-field support. See each endpoint's spec for available values.

Example: `GET /api/v1/products?sortBy=price_asc`

## Request and Response Format

All request and response bodies are JSON. Always set these headers on requests with a body:
```
Content-Type: application/json
Accept: application/json
```

## IDs

All primary entity IDs are UUIDs (e.g. `3fa85f64-5717-4562-b3fc-2c963f66afa6`).
Do not assume sequential integer IDs — they will not work.

## Timestamps

All timestamps are returned in ISO 8601 UTC format: `2024-03-15T14:30:00Z`.
All input date parameters accept ISO 8601 date format: `2024-03-15`.

## Idempotency

`POST` requests to Order Service and Payment Service support idempotency via the
`Idempotency-Key` header. If you send the same key twice, the second call returns the
original response instead of creating a duplicate. Use a UUID as the idempotency key.

## Empty Results

List endpoints return an empty `data` array (not 404) when no records match.
Cart Service returns an empty cart object (not 404) when a customer has no active cart.

## Versioning

All endpoints are prefixed with `/api/v1`. When a breaking change is made, a `/api/v2`
prefix is introduced. Old versions remain available for 6 months after a new version ships.
