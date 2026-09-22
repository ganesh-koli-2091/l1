# Data Provenance Note

## What the data is

**10 OpenAPI 3.0 YAML files** representing a fictional e-commerce microservices platform called
ShopCo. Each file describes one service (Order, Customer, Product, Payment, Inventory,
Notification, Auth, Shipping, Cart, Analytics) with 3–5 endpoints each (~38 total endpoints).

**4 Markdown architecture notes** covering:
- Service map and inter-service communication flows
- Common API patterns (pagination, filtering, timestamps, idempotency)
- JWT authentication guide (login, refresh, logout, error codes)
- Error handling reference (status codes, rate limits, retry guidance)

## Where it came from

All data was **synthetically generated** by the author for this project. No real company data,
no production API specifications, and no personally identifiable information are present.

The domain model (e-commerce microservices) is realistic and was shaped by the author's 4 years
of experience building Spring Boot microservices, ensuring the endpoint shapes, parameter names,
and service interaction patterns reflect real-world usage rather than toy examples.

## What it does and does not represent

**Does represent:**
- Realistic REST API design patterns (pagination, UUID IDs, ISO 8601 dates)
- Realistic microservice boundaries and responsibilities
- Realistic JWT auth flow and token lifecycle
- A corpus large enough to demonstrate retrieval quality differences

**Does not represent:**
- Any real company's actual API specifications
- All possible endpoint patterns (no GraphQL, no WebSocket, no batch endpoints)
- Error cases beyond standard HTTP status codes
- Versioned or deprecated endpoints
- Any API with more than ~100 endpoints (this corpus has 38 endpoints + 4 note files)

## Known limitations

1. **No batch endpoints.** All endpoints operate on single resources. Queries about batch
   operations will fail (documented in failure_analysis.md).

2. **No subscription or webhook endpoints.** Questions about event subscriptions have no
   matching document.

3. **Parameters only at endpoint level.** Rate limits are documented in error-handling.md
   but not in individual endpoint specs, so queries like "what is the rate limit for the
   payment endpoint?" will retrieve the notes doc but not a per-endpoint rate limit.

4. **English only.** All content is English. Queries in other languages will not match well.

5. **38 endpoints is a small corpus.** A real microservices platform might have 200+ endpoints.
   Retrieval performance may degrade as corpus grows and more endpoints share similar terminology.

## Sensitive data handling

None. All data is synthetic. No API keys, credentials, PII, or real infrastructure details
are present in any file. The `.env` file (which contains the Anthropic API key) is excluded
from the data corpus and listed in `.gitignore`.
