# After Context Engineering — Outputs with CLAUDE.md

System prompt is now loaded from CLAUDE.md, which enforces:
- Structured answer format (Answer → How to call → What you get back → Related → Source)
- Mandatory source citations in `[Source: filename, METHOD /path]` format
- Named HTTP method + full path in every answer
- Authentication requirement always stated
- Related endpoints suggested when workflow-shaped

Same 3 questions as before_context_output.md.

---

## Query 1: "Which endpoint do I call to get a customer's order history?"

**LLM Response (with CLAUDE.md):**

> **Answer:** Use `GET /api/v1/orders` from the **Order Service**, filtering by `customerId`.
>
> **How to call it:**
> - `GET /api/v1/orders`
> - `customerId` (query, optional, string/UUID) — filter to a specific customer's orders
> - `status` (query, optional, enum) — further filter by `pending`, `processing`, `shipped`, `delivered`, `cancelled`
> - `fromDate` / `toDate` (query, optional, date) — narrow to a date range
> - `page` (query, optional, integer, default 1) and `pageSize` (default 20, max 100)
> - Auth header: `Authorization: Bearer <token>`
>
> **What you get back:**
> - `data` — array of order objects (orderId, status, totalAmount, items, createdAt)
> - `total` — total matching orders (use with pageSize for pagination)
>
> **Related endpoints:**
> - `GET /api/v1/orders/{orderId}` — once you have an orderId, get full order details
> - `GET /api/v1/shipping/orders/{orderId}` — get tracking for any shipped order
>
> [Source: order-service.yaml, GET /orders]

**Improvement vs before:** HTTP method named ✓ | Path given ✓ | Parameters listed ✓ | Auth stated ✓ | Related endpoints ✓ | Source cited ✓

---

## Query 2: "How do I refresh an expired JWT token?"

**LLM Response (with CLAUDE.md):**

> **Answer:** Call `POST /api/v1/auth/refresh` on the **Auth Service** with your existing refresh token.
>
> **How to call it:**
> - `POST /api/v1/auth/refresh`
> - No Authorization header needed (your access token is what's expired)
> - Request body: `{ "refreshToken": "<your-refresh-token>" }`
>
> **What you get back:**
> - `accessToken` — new JWT access token (valid 15 minutes)
> - `refreshToken` — new refresh token (the old one is now invalid — update your stored copy)
> - `expiresIn` — 900 seconds
>
> **Important:** If the refresh token itself has expired (after 30 days), this returns HTTP 401 and the user must log in again via `POST /api/v1/auth/login`.
>
> **Related endpoints:**
> - `POST /api/v1/auth/login` — full login flow to get a fresh token pair
>
> [Source: auth-service.yaml, POST /auth/refresh]

**Improvement vs before:** Not told to "check the docs" ✓ | Exact path given ✓ | Request body shown ✓ | Edge case (refresh expired) explained ✓ | Source cited ✓

---

## Query 3: "How do I check if a product is in stock?"

**LLM Response (with CLAUDE.md):**

> **Answer:** Use `GET /api/v1/inventory/{productId}` from the **Inventory Service**.
>
> **How to call it:**
> - `GET /api/v1/inventory/{productId}`
> - `productId` (path, required, UUID) — the product to check
> - Auth header: `Authorization: Bearer <token>`
>
> **What you get back:**
> - `availableStock` — the number actually available (total minus reserved). **Use this field**, not `totalStock`.
> - `isLowStock` — boolean flag if stock is below the warehouse's low-stock threshold
> - `totalStock` — gross quantity before reservations
>
> **Related endpoints:**
> - `POST /api/v1/inventory/{productId}/reserve` — reserve stock when a customer starts checkout
> - `GET /api/v1/products/{productId}` — also has an `inStock` boolean if you only need a yes/no
>
> [Source: inventory-service.yaml, GET /inventory/{productId}]

**Improvement vs before:** Correct service chosen (not "inventory or product") ✓ | `availableStock` vs `totalStock` distinction explained ✓ | Auth format given ✓ | Source cited ✓

---

## Comparative Summary

| Criterion | Before (no CLAUDE.md) | After (CLAUDE.md) |
|-----------|----------------------|-------------------|
| HTTP method always stated | 0/3 | 3/3 |
| Full endpoint path given | 0/3 | 3/3 |
| Parameters listed by name | 0/3 | 3/3 |
| Auth requirement stated | 0/3 | 3/3 |
| Source citation present | 0/3 | 3/3 |
| Related endpoints suggested | 0/3 | 3/3 |
| Distinguishes similar fields | 0/3 | 2/3 |

The context artifact (CLAUDE.md) transformed all three answers from vague prose to
actionable, cited developer documentation.
