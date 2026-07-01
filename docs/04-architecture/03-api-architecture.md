# API Architecture — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-API-003 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Principal Software Architect |
| **Date** | 2026-07-01 |

---

## 1. RESTful API Design Principles

The TSBL API adheres to the following design principles derived from the Richardson Maturity Model (Level 2) and REST best practices:

| Principle | Description |
|---|---|
| **Resource-oriented** | URLs represent nouns (resources), not verbs. Actions are expressed via HTTP methods. |
| **Stateless** | Each request contains all information needed to process it. Server does not maintain client session state. |
| **Idempotent methods** | `GET`, `PUT`, `DELETE`, `PATCH` are idempotent. `POST` is not. |
| **Consistent naming** | Plural nouns, kebab-case, lowercase. No underscores or camelCase in URL paths. |
| **Versioned** | All API endpoints are prefixed with `/api/v{major}`. |
| **Content negotiation** | Clients specify `Accept: application/json`. Server responds with `Content-Type: application/json`. |
| **HATEOAS-ready** | Responses include links to related resources where helpful (e.g., pagination links). |
| **Backward compatible** | Breaking changes require a new major version. Non-breaking additions are allowed within a version. |

---

## 2. URL Naming Conventions

### 2.1 Base URL Pattern

```
/api/v{major}/{module}/{resource}[/{resource_id}][/{sub_resource}]
```

### 2.2 Conventions

| Convention | Rule | Example |
|---|---|---|
| **Version prefix** | `/api/v1/` | `/api/v1/products` |
| **Plural nouns** | Resources are always plural | `/api/v1/users` not `/api/v1/user` |
| **kebab-case** | Multi-word resources use hyphens | `/api/v1/shipping-addresses` |
| **Lowercase** | All URL segments are lowercase | `/api/v1/product-reviews` |
| **No file extensions** | No `.json`, `.xml` in URLs | `/api/v1/products` not `/api/v1/products.json` |
| **Query parameters** | `?key=value` for filtering/sorting/pagination | `/api/v1/products?category=electronics&page=2` |
| **Sub-resources** | Nested under parent resource | `/api/v1/orders/{order_id}/items` |
| **Actions** | Rare; use POST to sub-resource for non-CRUD | `POST /api/v1/orders/{id}/cancel` |

### 2.3 Endpoint Grouping by Module

| Module | Base Path | Example Resources |
|---|---|---|
| **Auth** | `/api/v1/auth` | `register`, `login`, `refresh`, `logout`, `verify-email`, `reset-password`, `oauth/{provider}` |
| **Users** | `/api/v1/users` | `profile`, `addresses`, `preferences` |
| **Catalog** | `/api/v1/catalog` | `products`, `categories`, `brands`, `reviews`, `search` |
| **Cart** | `/api/v1/cart` | `items`, `coupon`, `checkout` |
| **Orders** | `/api/v1/orders` | `items`, `shipments`, `invoices`, `returns` |
| **Payments** | `/api/v1/payments` | `transactions`, `methods`, `refunds` |
| **Vendors** | `/api/v1/vendors` | `applications`, `products`, `payouts`, `commissions` |
| **Admin** | `/api/v1/admin` | `users`, `products` (moderation), `config`, `audit-logs`, `reports` |
| **Notifications** | `/api/v1/notifications` | `preferences`, `templates`, `history` |
| **Analytics** | `/api/v1/analytics` | `dashboard`, `reports`, `exports` |

---

## 3. Request / Response Format Standards

### 3.1 Standard Request Headers

| Header | Required | Example | Description |
|---|---|---|---|
| `Authorization` | For protected endpoints | `Bearer eyJhbGci...` | JWT access token |
| `Content-Type` | For requests with body | `application/json` | Must be `application/json` |
| `Accept` | Optional | `application/json` | Default response format |
| `Accept-Language` | Optional | `bn-BD`, `en-US` | Localisation |
| `X-Idempotency-Key` | For payment/order creation | `uuid-v4` | Ensures safe retry |
| `X-Request-Id` | Optional | `uuid-v4` | Correlation ID for tracing |

### 3.2 Standard Response Envelope (List)

```json
{
    "data": [ ... ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 142,
        "total_pages": 8,
        "links": {
            "first": "/api/v1/products?page=1&per_page=20",
            "prev": null,
            "next": "/api/v1/products?page=2&per_page=20",
            "last": "/api/v1/products?page=8&per_page=20"
        }
    }
}
```

### 3.3 Standard Response Envelope (Single / Detail)

```json
{
    "data": { ... }
}
```

### 3.4 Standard Response Envelope (Create — 201)

```json
{
    "data": { ... },
    "message": "Product created successfully"
}
```

### 3.5 Standard Response Envelope (Empty — 204)

No body. Status `204 No Content` for `DELETE` and operations returning no data.

---

## 4. Pagination, Filtering, Sorting Standards

### 4.1 Pagination

| Parameter | Type | Default | Max | Description |
|---|---|---|---|---|
| `page` | integer | 1 | — | Page number (1-indexed) |
| `per_page` | integer | 20 | 100 | Items per page |

**Request**: `GET /api/v1/products?page=2&per_page=10`

**Response pagination block** (embedded in all list responses):

```json
"pagination": {
    "page": 2,
    "per_page": 10,
    "total": 142,
    "total_pages": 15,
    "links": {
        "first": "/api/v1/products?page=1&per_page=10",
        "prev": "/api/v1/products?page=1&per_page=10",
        "next": "/api/v1/products?page=3&per_page=10",
        "last": "/api/v1/products?page=15&per_page=10"
    }
}
```

### 4.2 Filtering

- Filters use **query parameters** with the format `?field=value`.
- Range filters use `?field_min=X&field_max=Y`.
- Multi-value filters use comma-separated values: `?category=electronics,fashion`.
- Complex filters use the bracket notation: `?filter[price][gte]=100&filter[price][lte]=500`.
- Full-text search uses a dedicated `?q=search_term` parameter.

| Syntax | Example | Description |
|---|---|---|
| Exact match | `?status=active` | `status = 'active'` |
| Multiple values | `?category=electronics,fashion` | `category IN ('electronics', 'fashion')` |
| Range | `?price_min=100&price_max=500` | `price BETWEEN 100 AND 500` |
| Date range | `?created_after=2026-01-01&created_before=2026-06-30` | `created_at BETWEEN dates` |
| Boolean | `?in_stock=true` | `stock > 0` |
| Nested attribute | `?filter[variants][price][gte]=100` | Complex nested filtering |
| Search | `?q=wireless+headphones` | Full-text search via Elasticsearch |

### 4.3 Sorting

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sort` | string | Module-dependent | Field name optionally prefixed with `-` for descending |

**Examples**:

```
GET /api/v1/products?sort=price          # Ascending by price
GET /api/v1/products?sort=-price         # Descending by price
GET /api/v1/products?sort=-rating,price  # Desc rating, then asc price
```

Allowed sort fields are whitelisted per endpoint to prevent DB sorting attacks.

---

## 5. Error Response Format (RFC 7807 Problem Details)

All API errors follow [RFC 7807](https://tools.ietf.org/html/rfc7807) Problem Details for HTTP APIs.

### 5.1 Base Error Schema

```json
{
    "type": "https://api.tsbl.com/errors/{error_code}",
    "title": "Human-readable error title",
    "status": 422,
    "detail": "Detailed explanation of the error",
    "instance": "/api/v1/products",
    "trace_id": "req-abc-123-def-456"
}
```

### 5.2 Validation Error (422)

```json
{
    "type": "https://api.tsbl.com/errors/validation_error",
    "title": "Validation Error",
    "status": 422,
    "detail": "One or more fields failed validation",
    "instance": "/api/v1/products",
    "trace_id": "req-xyz-789",
    "errors": [
        {
            "field": "price",
            "message": "Price must be greater than 0",
            "code": "greater_than"
        },
        {
            "field": "title",
            "message": "Title is required",
            "code": "required"
        }
    ]
}
```

### 5.3 Authentication Error (401)

```json
{
    "type": "https://api.tsbl.com/errors/unauthorized",
    "title": "Unauthorized",
    "status": 401,
    "detail": "Access token is missing, expired, or invalid",
    "instance": "/api/v1/orders",
    "trace_id": "req-abc-123"
}
```

### 5.4 Authorisation Error (403)

```json
{
    "type": "https://api.tsbl.com/errors/forbidden",
    "title": "Forbidden",
    "status": 403,
    "detail": "You do not have permission to access this resource",
    "instance": "/api/v1/admin/users",
    "trace_id": "req-def-456"
}
```

### 5.5 Not Found (404)

```json
{
    "type": "https://api.tsbl.com/errors/not_found",
    "title": "Resource Not Found",
    "status": 404,
    "detail": "Product with ID 'prod-abc-123' was not found",
    "instance": "/api/v1/products/prod-abc-123",
    "trace_id": "req-ghi-789"
}
```

### 5.6 Conflict (409)

```json
{
    "type": "https://api.tsbl.com/errors/conflict",
    "title": "Conflict",
    "status": 409,
    "detail": "Cannot cancel order in 'shipped' status. Only orders in 'pending' or 'confirmed' status can be cancelled.",
    "instance": "/api/v1/orders/ord-456/cancel",
    "trace_id": "req-jkl-012"
}
```

### 5.7 Rate Limit Exceeded (429)

```json
{
    "type": "https://api.tsbl.com/errors/rate_limit_exceeded",
    "title": "Rate Limit Exceeded",
    "status": 429,
    "detail": "Too many requests. Please retry after 30 seconds.",
    "instance": "/api/v1/search",
    "trace_id": "req-mno-345",
    "retry_after_seconds": 30
}
```

### 5.8 Standard HTTP Status Codes Used

| Code | Meaning | When to Use |
|---|---|---|
| `200 OK` | Success | GET, PUT, PATCH, POST (read/update) |
| `201 Created` | Resource created | POST (create) |
| `204 No Content` | Success, no body | DELETE, or operations with no return data |
| `400 Bad Request` | Malformed request | Invalid JSON, bad parameters |
| `401 Unauthorized` | Not authenticated | Missing/invalid JWT |
| `403 Forbidden` | Not authorised | Insufficient permissions |
| `404 Not Found` | Resource not found | Invalid ID or path |
| `409 Conflict` | State conflict | Status transition violation, duplicate |
| `422 Unprocessable Entity` | Validation failure | Pydantic validation errors |
| `429 Too Many Requests` | Rate limited | Client exceeded rate limit |
| `500 Internal Server Error` | Unhandled server error | Unexpected failures (not exposed to client) |
| `502 Bad Gateway` | Upstream failure | External service returned error |
| `503 Service Unavailable` | Temporary unavailability | Database down, maintenance mode |

---

## 6. Authentication Flow (JWT Access + Refresh Tokens)

### 6.1 Token Format

| Token | Type | Lifetime | Storage | Contains |
|---|---|---|---|---|
| **Access Token** | JWT (signed RS256) | 15 minutes | Memory (Zustand store) or HttpOnly cookie | `sub` (user_id), `email`, `roles`, `permissions`, `iat`, `exp` |
| **Refresh Token** | JWT (signed RS256) | 7 days | HttpOnly cookie (secure, sameSite=strict) | `sub` (user_id), `token_family`, `iat`, `exp` |
| **Id Token** (OAuth) | JWT (signed by provider) | Varies | Not stored server-side | Provider-specific claims |

### 6.2 Authentication Flow (Password)

```
  Client                             Server
    │                                  │
    │  POST /api/v1/auth/login         │
    │  { email, password }             │
    │ ────────────────────────────────►│
    │                                  │  Validate credentials (bcrypt verify)
    │                                  │  Generate access_token (15m) + refresh_token (7d)
    │                                  │  Store refresh_token fingerprint hash in DB
    │  { access_token, expires_in,     │
    │    refresh_token (HttpOnly) }    │
    │ ◄────────────────────────────────│
    │                                  │
    │  GET /api/v1/users/profile       │
    │  Authorization: Bearer <access>  │
    │ ────────────────────────────────►│
    │                                  │  Verify JWT signature
    │                                  │  Check expiry
    │                                  │  Return profile
    │ ◄────────────────────────────────│
    │                                  │
    │  POST /api/v1/auth/refresh       │
    │  Cookie: refresh_token=...       │
    │ ────────────────────────────────►│
    │                                  │  Verify refresh token signature
    │                                  │  Check fingerprint hash match
    │                                  │  Rotate: invalidate old, issue new pair
    │  { access_token, expires_in }    │
    │ ◄────────────────────────────────│
```

### 6.3 Token Refresh Rotation

- Each refresh token can be used **once**. After use, it is revoked and a new pair issued.
- If a revoked refresh token is reused, **all refresh tokens for that user** are immediately revoked (indicating possible token theft).
- Refresh tokens are stored as a bcrypt hash in the `refresh_tokens` table to prevent leakage from database compromise.

### 6.4 Authentication Headers

| Method | Access Token Location | Refresh Token Location |
|---|---|---|
| SPA (browser) | `Authorization: Bearer <token>` | HttpOnly cookie `__Host-refresh_token` |
| Mobile app | `Authorization: Bearer <token>` | Secure storage, sent in body for refresh |
| Third-party | `Authorization: Bearer <token>` | Not supported (access tokens only, short-lived) |

### 6.5 Logout Flow

```
  Client                                     Server
    │                                          │
    │  POST /api/v1/auth/logout                │
    │  Authorization: Bearer <access>          │
    │ ────────────────────────────────────────►│
    │                                          │  Add access token to blacklist (Redis, TTL = remaining expiry)
    │                                          │  Revoke refresh token (delete from DB)
    │  200 OK                                  │
    │ ◄────────────────────────────────────────│
    │                                          │
    │  (Client clears tokens from storage)     │
```

---

## 7. Rate Limiting Strategy

### 7.1 Rate Limit Tiers

| Tier | Scope | Limit | Window | Applied To |
|---|---|---|---|---|
| **Global** | IP address | 1,000 req | 1 minute | All unauthenticated requests |
| **Authenticated** | User ID | 5,000 req | 1 minute | All authenticated requests |
| **Auth** | IP address | 10 req | 1 minute | Login, register, password reset |
| **Search** | User / IP | 60 req | 1 minute | Search endpoint |
| **Checkout** | User ID | 10 req | 1 minute | Checkout submission |
| **Admin** | Admin user ID | 10,000 req | 1 minute | Admin endpoints |
| **Webhook** | IP whitelist | No limit | — | Payment gateway callbacks |

### 7.2 Rate Limit Headers

All rate-limited responses include:

```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1688144400
```

When exceeded (429):

```
Retry-After: 30
```

### 7.3 Implementation

- **Backend**: Redis-based sliding window counter per key `ratelimit:{scope}:{key}:{window}`.
- **Edge**: Nginx `limit_req_zone` for global IP-based throttling before requests reach the application.

---

## 8. API Versioning Strategy

### 8.1 URI Path Versioning

```
/api/v1/products
/api/v2/products
```

- The major version is included in the URL path.
- Minor changes (new fields, new endpoints) are additive and do not require a version bump.
- Breaking changes (removed fields, changed response structure, removed endpoints) require a new major version.

### 8.2 Version Lifecycle

| Phase | Support Period | Behaviour |
|---|---|---|
| **Active** | 0–12 months after release | Full support, bug fixes |
| **Maintenance** | 12–18 months after release | Critical security fixes only |
| **Deprecated** | 18–24 months after release | `Sunset` header added. `Warning` header added |
| **EOL** | After 24 months | Returns `410 Gone` |

### 8.3 Version Sunset Headers

```
Sunset: Sat, 01 Jul 2028 00:00:00 GMT
Deprecation: true
Link: </api/v2/orders>; rel="successor-version"
```

### 8.4 Internal Version Compatibility

- **Backward-compatible changes** (new fields, new optional query params): Allowed within a major version.
- **Breaking changes**: New major version. Both versions run in parallel during the overlap period.
- **Router structure**: FastAPI versioned routers via `APIRouter(prefix="/api/v1/orders")`.

---

## 9. WebSocket API Design for Real-Time Features

### 9.1 Connection Endpoint

```
WebSocket: wss://api.tsbl.com/ws/v1?token=<jwt_access_token>
```

### 9.2 WebSocket Protocol

- **Authentication**: JWT passed as query parameter on connection.
- **Protocol**: Socket.IO protocol over WebSocket (supports fallback to HTTP long-polling).
- **Message format**: JSON with `event` and `data` fields.

### 9.3 Event Types

#### Client → Server Events

| Event | Payload | Description |
|---|---|---|
| `subscribe` | `{ channels: ["order:123", "notification"] }` | Subscribe to channels |
| `unsubscribe` | `{ channels: ["order:123"] }` | Unsubscribe from channels |
| `ping` | `{}` | Keepalive heartbeat |
| `chat:send` | `{ order_id, message }` | Send message in order chat |

#### Server → Client Events

| Event | Payload | Description |
|---|---|---|
| `connected` | `{ session_id, user_id }` | Confirmation of connection |
| `order:status` | `{ order_id, old_status, new_status, timestamp }` | Order status change |
| `order:tracking` | `{ order_id, location, status, estimated_time }` | Live tracking update |
| `notification` | `{ id, type, title, body, data }` | Push notification |
| `admin:alert` | `{ type, severity, message }` | Admin alert (new vendor, dispute) |
| `chat:message` | `{ order_id, sender, message, timestamp }` | Chat message received |
| `inventory:alert` | `{ product_id, sku, current_stock }` | Low stock alert (vendor) |
| `error` | `{ code, message }` | Error notification |
| `pong` | `{}` | Heartbeat response |

### 9.4 Channel Architecture

```
  Client connects
       │
       ▼
  Socket.IO Server (FastAPI + python-socketio)
       │
       ├── Room-based channels (order:{order_id}, user:{user_id}, vendor:{vendor_id})
       │
       ├── Redis Pub/Sub (cross-process broadcasting)
       │       │
       │       └── Redis <──> Other API workers
       │
       └── Event Handlers:
               ├── Order events → order:{order_id} room
               ├── Notification events → user:{user_id} room
               └── Admin events → admin room
```

### 9.5 Reconnection Strategy

| Attempt | Delay | Jitter |
|---|---|---|
| 1 | 1s | ±500ms |
| 2 | 2s | ±1s |
| 3 | 5s | ±2s |
| 4+ | 10s (max) | ±5s |

Total timeout: 60 seconds before giving up.

---

## 10. OpenAPI / Swagger Documentation Approach

### 10.1 Generation

- **Tool**: FastAPI auto-generates OpenAPI 3.1 spec from Pydantic models and route decorators.
- **URLs**:
  - JSON spec: `https://api.tsbl.com/openapi.json`
  - Swagger UI: `https://api.tsbl.com/docs`
  - ReDoc: `https://api.tsbl.com/redoc`
- **Metadata**: All endpoints include `summary`, `description`, `tags`, `response_description`, and `deprecated` flags.

### 10.2 Documentation Standards

| Element | Requirement | Enforcement |
|---|---|---|
| **Operation summary** | Required | One-line description of the endpoint |
| **Operation description** | Required | Detailed explanation including business rules |
| **Tags** | Required | Grouped by module: `Auth`, `Catalog`, `Orders`, etc. |
| **Request body** | Required | Pydantic schema with field descriptions and examples |
| **Response models** | Required | Pydantic response schema per status code |
| **Error responses** | Required | Document all non-2xx responses for each endpoint |
| **Authentication** | Required | Document auth requirements per endpoint |
| **Rate limits** | Recommended | Document rate limit tier per endpoint |

### 10.3 Example Endpoint Documentation

```yaml
/api/v1/orders:
  post:
    summary: Place a new order
    description: >
      Creates a new order from the user's current cart.
      Requires an active cart with at least one item.
      Triggers inventory reservation and payment initiation.
    tags: [Orders]
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CreateOrderRequest'
          example:
            shipping_address_id: "addr-abc-123"
            payment_method_id: "pmt-bkash-456"
            coupon_code: "SAVE10"
            notes: "Leave at the gate"
    responses:
      '201':
        description: Order created successfully
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OrderResponse'
      '400':
        $ref: '#/components/responses/BadRequest'
      '401':
        $ref: '#/components/responses/Unauthorized'
      '409':
        description: Cart is empty or inventory insufficient
```

---

## 11. API Security

### 11.1 CORS Configuration

```python
# tsbl/config.py — Conceptual
CORS_ORIGINS = [
    "https://www.tsbl.com",
    "https://admin.tsbl.com",
    "https://vendor.tsbl.com",
]
CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_HEADERS = ["Authorization", "Content-Type", "X-Idempotency-Key", "X-Request-Id"]
CORS_EXPOSE_HEADERS = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
CORS_CREDENTIALS = True
CORS_MAX_AGE = 3600
```

- Only specific origins are allowed (no wildcard `*`).
- Credentials (cookies) require explicit origin, not wildcard.

### 11.2 CSRF Protection

- **For cookie-based auth**: Double Submit Cookie pattern.
- **For SPA with JWT in Authorization header**: CSRF is not needed (browser does not include custom headers cross-origin).
- **State-changing requests**: Require `Content-Type: application/json` (prevents simple CSRF).

### 11.3 Input Validation

| Layer | Validation | Tool |
|---|---|---|
| **Transport** | HTTPS enforced, HTTP → HTTPS redirect | Nginx / ALB |
| **HTTP** | Method whitelist, header validation, body size limit | Nginx (client_max_body_size: 10MB) |
| **API Schema** | Type, format, constraint validation | Pydantic (integrated with FastAPI) |
| **Business Logic** | State machines, domain invariants | Service layer validation |
| **SQL Injection** | Parameterised queries via SQLAlchemy | ORM |
| **XSS** | Input sanitisation, output encoding | HTML escaping on frontend |
| **File Upload** | File type validation (magic bytes), size limit, virus scan | `python-magic`, ClamAV |

### 11.4 Security Headers

All responses include:

| Header | Value | Purpose |
|---|---|---|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Enforce HTTPS |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Content-Security-Policy` | `default-src 'self'; ...` | XSS mitigation |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer header |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(self)` | Restrict API access to features |

---

## 12. Endpoint Grouping by Module

### 12.1 Auth Module — `/api/v1/auth`

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/register` | Register new user | No |
| `POST` | `/login` | Login with email/password | No |
| `POST` | `/refresh` | Refresh access token | Refresh token |
| `POST` | `/logout` | Logout (revoke tokens) | Yes |
| `POST` | `/verify-email` | Verify email via OTP | No |
| `POST` | `/resend-otp` | Resend email verification OTP | No |
| `POST` | `/forgot-password` | Request password reset | No |
| `POST` | `/reset-password` | Reset password with token | No |
| `GET` | `/oauth/{provider}` | Initiate OAuth login (redirect) | No |
| `POST` | `/oauth/{provider}/callback` | OAuth callback | No |

### 12.2 Catalog Module — `/api/v1/catalog`

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/products` | List/search products with filters | No |
| `GET` | `/products/{id}` | Get product detail | No |
| `POST` | `/products` | Create product | Vendor |
| `PUT` | `/products/{id}` | Update product | Vendor |
| `DELETE` | `/products/{id}` | Soft-delete product | Vendor/Admin |
| `GET` | `/products/{id}/reviews` | List product reviews | No |
| `POST` | `/products/{id}/reviews` | Add review | Yes |
| `GET` | `/categories` | List category tree | No |
| `GET` | `/categories/{id}` | Get category with products | No |
| `POST` | `/categories` | Create category | Admin |
| `GET` | `/brands` | List brands | No |
| `GET` | `/search` | Full-text search with facets | No |
| `GET` | `/search/autocomplete` | Search autocomplete | No |

### 12.3 Cart Module — `/api/v1/cart`

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/` | Get current user's cart | Yes |
| `POST` | `/items` | Add item to cart | Yes |
| `PUT` | `/items/{id}` | Update cart item quantity | Yes |
| `DELETE` | `/items/{id}` | Remove item from cart | Yes |
| `POST` | `/coupon` | Apply coupon code | Yes |
| `DELETE` | `/coupon` | Remove coupon | Yes |
| `POST` | `/checkout` | Initiate checkout process | Yes |

### 12.4 Order Module — `/api/v1/orders`

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/` | List user's orders (filterable) | Yes |
| `GET` | `/{id}` | Get order detail with items | Yes |
| `POST` | `/` | Place order (from checkout data) | Yes |
| `POST` | `/{id}/cancel` | Cancel order (if allowed) | Yes |
| `GET` | `/{id}/shipments` | Get shipment tracking | Yes |
| `GET` | `/{id}/invoice` | Download invoice PDF | Yes |
| `POST` | `/{id}/returns` | Request return | Yes |
| `PUT` | `/{id}/status` | Update order status | Admin/Vendor |

### 12.5 Payment Module — `/api/v1/payments`

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/methods` | List saved payment methods | Yes |
| `POST` | `/methods` | Add payment method | Yes |
| `DELETE` | `/methods/{id}` | Remove payment method | Yes |
| `POST` | `/initiate` | Initiate payment for order | Yes |
| `POST` | `/confirm/{transaction_id}` | Confirm payment (gateway callback) | No (IP whitelist) |
| `POST` | `/{id}/refund` | Process refund | Admin |
| `GET` | `/transactions` | List transactions | Yes |

### 12.6 Vendor Module — `/api/v1/vendors`

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/applications` | Submit vendor application | Yes |
| `GET` | `/applications/{id}` | Get application status | Yes |
| `PUT` | `/applications/{id}/review` | Review application | Admin |
| `GET` | `/me` | Get current vendor profile | Vendor |
| `PUT` | `/me` | Update vendor profile | Vendor |
| `GET` | `/me/products` | List vendor's products | Vendor |
| `GET` | `/me/payouts` | List payouts | Vendor |
| `GET` | `/me/analytics` | Vendor dashboard analytics | Vendor |

### 12.7 Admin Module — `/api/v1/admin`

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/users` | List all users | Admin |
| `PUT` | `/users/{id}/status` | Suspend/activate user | Admin |
| `GET` | `/products/pending` | List products pending moderation | Admin |
| `PUT` | `/products/{id}/moderate` | Approve/reject product | Admin |
| `GET` | `/vendors/pending` | List pending vendor applications | Admin |
| `GET` | `/config` | Get platform configuration | Admin |
| `PUT` | `/config` | Update platform configuration | Admin |
| `GET` | `/audit-logs` | Query audit logs | Admin |
| `POST` | `/cache/purge` | Purge application cache | Admin |

### 12.8 Notification Module — `/api/v1/notifications`

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/` | List user's notifications | Yes |
| `GET` | `/unread-count` | Get unread notification count | Yes |
| `PUT` | `/{id}/read` | Mark notification as read | Yes |
| `PUT` | `/read-all` | Mark all as read | Yes |
| `GET` | `/preferences` | Get notification preferences | Yes |
| `PUT` | `/preferences` | Update notification preferences | Yes |

---

## 13. Example Request/Response Patterns

### 13.1 Create Product (POST /api/v1/catalog/products)

**Request**:
```json
{
    "title": "Wireless Bluetooth Headphones",
    "description": "Premium noise-cancelling wireless headphones with 30-hour battery life.",
    "category_id": "cat-audio-001",
    "brand_id": "brd-sony-001",
    "price": 5499.00,
    "currency": "BDT",
    "compare_at_price": 6999.00,
    "sku": "WH-SONY-1001",
    "barcode": "4905524937352",
    "weight_grams": 250,
    "images": [
        "https://cdn.tsbl.com/products/wh-1001-front.jpg",
        "https://cdn.tsbl.com/products/wh-1001-side.jpg"
    ],
    "variants": [
        {
            "name": "Black",
            "sku": "WH-SONY-1001-BLK",
            "price": 5499.00,
            "stock": 50,
            "attributes": {"color": "Black", "color_hex": "#000000"}
        },
        {
            "name": "White",
            "sku": "WH-SONY-1001-WHT",
            "price": 5499.00,
            "stock": 30,
            "attributes": {"color": "White", "color_hex": "#FFFFFF"}
        }
    ],
    "attributes": {
        "connectivity": "Bluetooth 5.3",
        "battery_life": "30 hours",
        "noise_cancellation": true,
        "water_resistant": false
    },
    "seo": {
        "meta_title": "Buy Wireless Bluetooth Headphones in Bangladesh",
        "meta_description": "Premium noise-cancelling wireless headphones at the best price in Bangladesh.",
        "slug": "wireless-bluetooth-headphones"
    },
    "tags": ["headphones", "wireless", "bluetooth", "audio", "sony"]
}
```

**Response (201 Created)**:
```json
{
    "data": {
        "id": "prod-abc-123-def-456",
        "title": "Wireless Bluetooth Headphones",
        "slug": "wireless-bluetooth-headphones",
        "sku": "WH-SONY-1001",
        "price": 5499.00,
        "currency": "BDT",
        "status": "pending",
        "created_at": "2026-07-01T10:30:00+06:00",
        "updated_at": "2026-07-01T10:30:00+06:00",
        "_links": {
            "self": "/api/v1/catalog/products/prod-abc-123-def-456",
            "reviews": "/api/v1/catalog/products/prod-abc-123-def-456/reviews"
        }
    },
    "message": "Product created successfully and sent for moderation"
}
```

### 13.2 Search Products (GET /api/v1/catalog/search)

**Request**:
```
GET /api/v1/catalog/search?q=wireless+headphones&category=electronics&price_min=1000&price_max=10000&sort=-rating&page=1&per_page=20
```

**Response (200 OK)**:
```json
{
    "data": [
        {
            "id": "prod-abc-123",
            "title": "Wireless Bluetooth Headphones",
            "slug": "wireless-bluetooth-headphones",
            "price": 5499.00,
            "compare_at_price": 6999.00,
            "currency": "BDT",
            "rating": 4.5,
            "review_count": 128,
            "thumbnail": "https://cdn.tsbl.com/products/wh-1001-front.jpg?w=200",
            "in_stock": true,
            "vendor": {
                "id": "vnd-xyz-789",
                "name": "SonicTech BD",
                "trust_score": 4.8
            }
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 45,
        "total_pages": 3,
        "links": {
            "first": "/api/v1/catalog/search?q=wireless+headphones&page=1&per_page=20",
            "prev": null,
            "next": "/api/v1/catalog/search?q=wireless+headphones&page=2&per_page=20",
            "last": "/api/v1/catalog/search?q=wireless+headphones&page=3&per_page=20"
        }
    },
    "facets": {
        "categories": [
            {"value": "electronics", "count": 30, "label": "Electronics"},
            {"value": "audio", "count": 15, "label": "Audio"}
        ],
        "brands": [
            {"value": "sony", "count": 12, "label": "Sony"},
            {"value": "samsung", "count": 8, "label": "Samsung"},
            {"value": "xiaomi", "count": 5, "label": "Xiaomi"}
        ],
        "price_ranges": [
            {"min": 0, "max": 2000, "count": 5, "label": "Under Tk 2,000"},
            {"min": 2000, "max": 5000, "count": 18, "label": "Tk 2,000 - Tk 5,000"},
            {"min": 5000, "max": 10000, "count": 22, "label": "Tk 5,000 - Tk 10,000"}
        ],
        "ratings": [
            {"value": 4, "count": 28, "label": "4★ & above"},
            {"value": 3, "count": 40, "label": "3★ & above"}
        ]
    },
    "meta": {
        "query": "wireless headphones",
        "did_you_mean": "wireless headphone",
        "total_results": 45,
        "search_time_ms": 45
    }
}
```

### 13.3 Place Order (POST /api/v1/orders)

**Request**:
```json
{
    "shipping_address_id": "addr-abc-123",
    "billing_address_id": "addr-abc-123",
    "payment_method_id": "pmt-bkash-456",
    "coupon_code": "WELCOME10",
    "notes": "Please call before delivery",
    "items": [
        {
            "product_id": "prod-abc-123",
            "variant_id": "var-001",
            "quantity": 2
        },
        {
            "product_id": "prod-def-456",
            "variant_id": null,
            "quantity": 1
        }
    ]
}
```

**Response (201 Created)**:
```json
{
    "data": {
        "id": "ord-001-xyz-789",
        "status": "pending",
        "subtotal": 16497.00,
        "discount": 1649.70,
        "shipping_fee": 100.00,
        "tax": 0.00,
        "total": 14947.30,
        "currency": "BDT",
        "items": [
            {
                "product_id": "prod-abc-123",
                "product_title": "Wireless Bluetooth Headphones",
                "variant": "Black",
                "quantity": 2,
                "unit_price": 5499.00,
                "total": 10998.00
            },
            {
                "product_id": "prod-def-456",
                "product_title": "USB-C Charging Cable",
                "variant": null,
                "quantity": 1,
                "unit_price": 5499.00,
                "total": 5499.00
            }
        ],
        "shipping_address": {
            "full_name": "John Doe",
            "phone": "+8801712345678",
            "address_line1": "123 Gulshan Avenue",
            "address_line2": "Dhaka 1212",
            "city": "Dhaka",
            "division": "Dhaka",
            "postal_code": "1212"
        },
        "payment": {
            "method": "bKash",
            "status": "pending",
            "redirect_url": "https://api.tsbl.com/payments/bkash/initiate?trx=txn-001"
        },
        "created_at": "2026-07-01T11:00:00+06:00",
        "_links": {
            "self": "/api/v1/orders/ord-001-xyz-789",
            "pay": "/api/v1/payments/initiate",
            "cancel": "/api/v1/orders/ord-001-xyz-789/cancel"
        }
    },
    "message": "Order placed successfully. Redirecting to payment."
}
```

---

## 14. API Changelog and Deprecation

All API changes are tracked in a changelog maintained alongside the codebase:

| Date | Version | Change | Type |
|---|---|---|---|
| 2026-07-01 | v1 | Initial API release | — |
| — | v1.1 | Add `thumbnail` field to product search response | Additive |
| — | v1.1 | Add `PATCH /api/v1/catalog/products/{id}` | Additive |
| — | v2 | Remove deprecated `old_price` field. Use `compare_at_price`. | Breaking |

---

## 15. Glossary

| Term | Definition |
|---|---|
| **BFF** | Backend for Frontend — a thin API layer that serves frontend-specific needs |
| **CORS** | Cross-Origin Resource Sharing — browser security mechanism |
| **CSRF** | Cross-Site Request Forgery — attack that tricks user into executing unwanted actions |
| **HATEOAS** | Hypermedia as the Engine of Application State — REST constraint where responses include links |
| **Idempotency Key** | A unique identifier that ensures a request can be safely retried without duplicate side-effects |
| **JWT** | JSON Web Token — compact, URL-safe token format for authentication claims |
| **RFC 7807** | Problem Details for HTTP APIs — standard format for API error responses |
| **Socket.IO** | A library enabling low-latency, bidirectional, event-based communication |
