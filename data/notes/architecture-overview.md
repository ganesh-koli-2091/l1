# ShopCo Microservices Architecture Overview

## Service Map

ShopCo's backend is a microservices platform with 10 independent services. Each service owns its own database and communicates via REST APIs synchronously or via events asynchronously.

| Service              | Port  | Database     | Purpose |
|----------------------|-------|--------------|---------|
| Order Service        | 8081  | PostgreSQL   | Order lifecycle |
| Customer Service     | 8082  | PostgreSQL   | Customer accounts |
| Product Service      | 8083  | PostgreSQL + Elasticsearch | Catalog + search |
| Payment Service      | 8084  | PostgreSQL   | Payments and refunds |
| Inventory Service    | 8085  | PostgreSQL   | Stock management |
| Notification Service | 8086  | PostgreSQL   | Email/SMS dispatch |
| Auth Service         | 8087  | PostgreSQL + Redis | JWT and sessions |
| Shipping Service     | 8088  | PostgreSQL   | Shipment and tracking |
| Cart Service         | 8089  | Redis        | Shopping carts |
| Analytics Service    | 8090  | ClickHouse   | Reporting aggregates |

## Happy-Path Order Flow

When a customer places an order, services interact in this sequence:

1. **Cart Service** — customer has items in cart
2. **Inventory Service** — Cart Service calls `POST /inventory/{productId}/reserve` to reserve stock
3. **Cart Service** — calls `POST /cart/{customerId}/checkout`, which calls Order Service
4. **Order Service** — creates order record, calls Payment Service
5. **Payment Service** — charges the payment method
6. **Order Service** — transitions order to `processing`, calls Shipping Service
7. **Shipping Service** — generates shipping label, returns tracking number
8. **Notification Service** — Order Service triggers `order_confirmation` email

## API Gateway

All external traffic enters via an API Gateway at `https://api.shopco.com`. The gateway handles:
- TLS termination
- Rate limiting (see error-handling.md for rate limit headers)
- JWT verification (calls Auth Service `/auth/validate` on every request)
- Request routing to internal services

Internal service-to-service calls bypass the gateway and call services directly on their port.

## Authentication Model

Every request from external clients must include a JWT Bearer token in the `Authorization` header.
Services validate tokens by calling Auth Service's `/auth/validate` endpoint.

The only public endpoints that do not require a token are:
- `POST /api/v1/auth/login`
- `POST /api/v1/customers` (registration)

See authentication-guide.md for the full token flow.

## Asynchronous Events

Some inter-service communication is event-driven via a Kafka broker:
- Order Service publishes `order.created`, `order.cancelled`, `order.delivered` events
- Analytics Service consumes all order events to update its ClickHouse aggregates
- Notification Service subscribes to `order.created` to send confirmation emails

Events are for analytics and notifications only — the order/checkout critical path is synchronous.
