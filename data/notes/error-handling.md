# Error Handling Guide

## Standard Error Response Format

All services return errors in this format:

```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "requestId": "uuid-for-support-tracing",
  "timestamp": "2024-03-15T14:30:00Z"
}
```

Always log the `requestId` — use it when raising a support ticket.

## HTTP Status Codes

| Code | Meaning | Common cause |
|------|---------|--------------|
| 200  | OK | Successful GET, PUT, PATCH |
| 201  | Created | Successful POST that created a resource |
| 202  | Accepted | Request queued (e.g. email, SMS) — check status later |
| 204  | No Content | Successful DELETE or logout |
| 400  | Bad Request | Missing required field, invalid format |
| 401  | Unauthorised | Missing, expired, or invalid JWT token |
| 402  | Payment Required | Payment declined |
| 403  | Forbidden | Valid token but insufficient role or account suspended |
| 404  | Not Found | Resource does not exist |
| 409  | Conflict | State conflict (e.g. cancelling a shipped order, duplicate email) |
| 422  | Unprocessable | Request parsed but validation failed (e.g. no verified phone) |
| 429  | Too Many Requests | Rate limit exceeded — see rate limit section |
| 500  | Internal Server Error | Unexpected error — log the requestId and retry |

## Rate Limiting

The API Gateway enforces rate limits per customer token:
- **Standard:** 100 requests per 60 seconds
- **Search endpoints:** 20 requests per 60 seconds

When rate limited (429), the response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1710001000   (Unix timestamp when the window resets)
Retry-After: 45                  (seconds to wait before retrying)
```

Wait for `Retry-After` seconds before retrying. Do not immediately retry on 429.

## Retries

Safe to retry with exponential backoff:
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

Do NOT retry without an idempotency key:
- 402 Payment Required (retrying will attempt a second charge)
- 409 Conflict (the conflict will not resolve by retrying)

Do NOT retry:
- 400 Bad Request (fix the request first)
- 401 Unauthorised (refresh the token first)
- 403 Forbidden (the user does not have permission)
- 404 Not Found (the resource does not exist)

## Validation Errors

400 responses may include a `details` array with field-level errors:

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [
    { "field": "email", "message": "must be a valid email address" },
    { "field": "password", "message": "must be at least 8 characters" }
  ]
}
```

## Service-Specific Errors

### Order Service
- `CART_EMPTY` (400) — checkout called with no items in cart
- `ORDER_NOT_CANCELLABLE` (409) — order status does not allow cancellation

### Payment Service
- `PAYMENT_DECLINED` (402) — card declined; `declineCode` field has the reason
- `ALREADY_REFUNDED` (409) — full refund already issued

### Inventory Service
- `INSUFFICIENT_STOCK` (409) — requested quantity exceeds available stock
