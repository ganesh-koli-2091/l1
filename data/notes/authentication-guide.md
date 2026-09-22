# Authentication Guide

## Overview

ShopCo uses JWT (JSON Web Token) Bearer authentication. Every API request (except login and
customer registration) must include a valid access token in the Authorization header.

## Getting a Token

### Step 1 — Login

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "expiresIn": 900,
  "tokenType": "Bearer"
}
```

The `accessToken` is valid for **15 minutes** (900 seconds).
The `refreshToken` is valid for **30 days**.

## Using the Token

Include the access token in every subsequent request:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Refreshing an Expired Token

When an access token expires, you receive HTTP 401 from any service. Do not redirect to login —
call the refresh endpoint first:

```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

This returns a new `accessToken` and `refreshToken`. The old refresh token is invalidated.
If the refresh token has also expired, the user must log in again.

## Logging Out

```
POST /api/v1/auth/logout
Authorization: Bearer <accessToken>
Content-Type: application/json

{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

Response: HTTP 204 No Content.

## Public Endpoints (No Token Required)

Only these two endpoints are accessible without a token:
- `POST /api/v1/auth/login`
- `POST /api/v1/customers` (registration)

All other endpoints return HTTP 401 if the Authorization header is missing or invalid.

## Token Claims

The JWT access token payload contains:
```json
{
  "sub": "customer-uuid",
  "email": "user@example.com",
  "roles": ["CUSTOMER"],
  "iat": 1710000000,
  "exp": 1710000900
}
```

Admin and reporting endpoints require the `ANALYTICS_READ` or `INVENTORY_ADMIN` role in the
`roles` claim. Regular customers have only the `CUSTOMER` role.

## Common Auth Errors

| Status | Meaning | Fix |
|--------|---------|-----|
| 401 Missing token | No Authorization header | Add Bearer token |
| 401 Token expired | Access token past expiry | Call /auth/refresh |
| 401 Invalid token | Tampered or malformed JWT | Re-login |
| 403 Insufficient role | Missing required role | Use admin credentials |
| 403 Account suspended | Customer account locked | Contact support |
