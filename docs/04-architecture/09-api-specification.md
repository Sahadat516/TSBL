# API Specification — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-API-009 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Principal API Architect |
| **Date** | 2026-07-02 |

---

## Table of Contents

1. [API Design Principles](#1-api-design-principles)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [User Management API](#3-user-management-api)
4. [Seller Management API](#4-seller-management-api)
5. [Product & Marketplace API](#5-product--marketplace-api)
6. [Cart & Checkout API](#6-cart--checkout-api)
7. [Order API](#7-order-api)
8. [Payment & Wallet API](#8-payment--wallet-api)
9. [Escrow API](#9-escrow-api)
10. [Review API](#10-review-api)
11. [Messaging API](#11-messaging-api)
12. [Notification API](#12-notification-api)
13. [Support & Dispute API](#13-support--dispute-api)
14. [Affiliate API](#14-affiliate-api)
15. [Admin API](#15-admin-api)
16. [CMS & Content API](#16-cms--content-api)
17. [System & Configuration API](#17-system--configuration-api)
18. [WebSocket Events](#18-websocket-events)
19. [API Standards](#19-api-standards)
20. [API Security](#20-api-security)

---

## 1. API Design Principles

### 1.1 RESTful Design

The TSBL API follows the Richardson Maturity Model **Level 2** — resources are identified by URIs, HTTP methods define operations, and response status codes convey results. The API is stateless, cacheable, and leverages a uniform interface.

| Principle | Implementation |
|---|---|
| **Resource-oriented** | URLs represent nouns (resources), not verbs. Actions are expressed via HTTP methods. |
| **Stateless** | Each request contains all information needed to process it. No server-side sessions. |
| **Idempotency** | `GET`, `PUT`, `DELETE`, `PATCH` are idempotent. `POST` is not. |
| **Content negotiation** | Clients send `Accept: application/json`. Server responds with `Content-Type: application/json`. |
| **HATEOAS-ready** | Responses include `_links` for related resources and pagination where applicable. |

### 1.2 Resource-Oriented URLs

```
/api/v{major}/{module}/{resource}[/{resource_id}][/{sub_resource}][/{action}]
```

| Convention | Rule | Example |
|---|---|---|
| **Version prefix** | `/api/v{N}/` | `/api/v1/products` |
| **Plural nouns** | Resources are always plural | `/api/v1/users` |
| **kebab-case** | Multi-word segments use hyphens | `/api/v1/forgot-password` |
| **Lowercase** | All URL segments are lowercase | `/api/v1/shipping-addresses` |
| **No file extensions** | No `.json` or `.xml` suffixes | `/api/v1/products` |
| **Query parameters** | Filtering, sorting, pagination via `?key=value` | `/api/v1/products?category=electronics&page=2` |
| **Sub-resources** | Nested under parent resource | `/api/v1/orders/{id}/items` |
| **Action endpoints** | Rare; POST to a verb-path for non-CRUD | `POST /api/v1/orders/{id}/cancel` |

### 1.3 HTTP Methods Correctly Used

| Method | CRUD Equivalent | Idempotent | Safe | Use Case |
|---|---|---|---|---|
| `GET` | Read | Yes | Yes | Retrieve a resource or collection |
| `POST` | Create | No | No | Create a resource or trigger an action |
| `PATCH` | Partial Update | Yes | No | Update specific fields of a resource |
| `PUT` | Replace | Yes | No | Full resource replacement (rare; prefer PATCH) |
| `DELETE` | Delete | Yes | No | Remove or soft-delete a resource |

### 1.4 Consistent Naming Conventions

| Concern | Convention | Example |
|---|---|---|
| **URL paths** | Plural nouns, kebab-case, lowercase | `/api/v1/shipping-addresses` |
| **Query parameters** | camelCase | `?sortBy=createdAt&sortOrder=desc` |
| **JSON field names** | camelCase | `{ "firstName": "John", "isActive": true }` |
| **Primary keys** | `id` (UUID v4) | `"id": "a1b2c3d4-..."` |
| **Foreign keys** | `{resource}Id` | `"userId"`, `"productId"` |
| **Timestamps** | ISO 8601 UTC | `"2026-07-02T14:30:00Z"` |
| **Enum values** | UPPER_SNAKE_CASE | `"PENDING"`, `"ACTIVE"`, `"COMPLETED"` |

### 1.5 Versioning Strategy

- **Major versions** are part of the URL path: `/api/v1/`, `/api/v2/`
- A new major version is released only when breaking changes are required
- Minor additions (new fields, new endpoints) are backward-compatible within a major version
- Deprecated versions receive a **6-month sunset period** with `Sunset` and `Deprecation` response headers
- Clients are informed of upcoming breaking changes via the `Warning` header and developer newsletter

### 1.6 Response Format Standards

All API responses follow a consistent envelope:

**Success Response:**

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-07-02T14:30:00Z",
    "requestId": "req_a1b2c3d4"
  }
}
```

**Collection Response:**

```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "timestamp": "2026-07-02T14:30:00Z",
    "requestId": "req_a1b2c3d4",
    "pagination": {
      "cursor": "eyJpZCI6IjEyMyJ9",
      "nextCursor": "eyJpZCI6IjEyNSJ9",
      "hasMore": true,
      "limit": 20,
      "total": 1034
    }
  }
}
```

### 1.7 Error Format Standards (RFC 7807)

All errors follow [RFC 7807](https://tools.ietf.org/html/rfc7807) (Problem Details for HTTP APIs):

```json
{
  "type": "https://api.tsbl.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "/api/v1/products",
  "timestamp": "2026-07-02T14:30:00Z",
  "requestId": "req_a1b2c3d4",
  "errors": [
    {
      "field": "price",
      "message": "Price must be greater than 0",
      "code": "INVALID_PRICE"
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `type` | URI | Reference to the error type documentation |
| `title` | String | Short, human-readable error summary |
| `status` | Integer | HTTP status code |
| `detail` | String | Human-readable explanation |
| `instance` | URI | The endpoint that produced the error |
| `timestamp` | String (ISO 8601) | When the error occurred |
| `requestId` | String | Correlation ID for debugging |
| `errors` | Array | Optional list of field-level validation errors |

---

## 2. Authentication & Authorization

Authentication is performed via **JWT Bearer tokens**. Access tokens are short-lived (15 minutes). Refresh tokens are long-lived (7 days) and must be stored securely.

### 2.1 Endpoints

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | No | — | Register a new user account |
| `POST` | `/api/v1/auth/login` | No | — | Authenticate and receive JWT tokens |
| `POST` | `/api/v1/auth/refresh` | No¹ | — | Obtain a new access token |
| `POST` | `/api/v1/auth/logout` | Yes | All | Invalidate the current refresh token |
| `POST` | `/api/v1/auth/forgot-password` | No | — | Request a password reset email |
| `POST` | `/api/v1/auth/reset-password` | No | — | Reset password using a token |
| `POST` | `/api/v1/auth/verify-email` | No | — | Verify email address with a token |
| `POST` | `/api/v1/auth/mfa/enable` | Yes | All | Enable multi-factor authentication |
| `POST` | `/api/v1/auth/mfa/verify` | No² | — | Verify MFA code during login |
| `GET` | `/api/v1/auth/me` | Yes | All | Get the authenticated user's profile |

¹ Uses refresh token (in body) — no Bearer token required.
² Uses temporary MFA session token returned from login.

### 2.2 POST /api/v1/auth/register

| Detail | Value |
|---|---|
| **Auth** | None |
| **Idempotent** | No |

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+8801700000000",
  "acceptedTerms": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | String | Yes | Valid email address (unique) |
| `password` | String | Yes | Min 8 chars, 1 uppercase, 1 number, 1 special |
| `firstName` | String | Yes | 1–50 characters |
| `lastName` | String | Yes | 1–50 characters |
| `phone` | String | No | E.164 format preferred |
| `acceptedTerms` | Boolean | Yes | Must be `true` |

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "BUYER",
    "isEmailVerified": false,
    "createdAt": "2026-07-02T14:30:00Z"
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `EMAIL_EXISTS` | Email already registered |
| 422 | `VALIDATION_ERROR` | Invalid field values |
| 400 | `TERMS_NOT_ACCEPTED` | `acceptedTerms` is `false` or missing |

### 2.3 POST /api/v1/auth/login

| Detail | Value |
|---|---|
| **Auth** | None |
| **Idempotent** | No |

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "mfaCode": "123456"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | String | Yes | Registered email address |
| `password` | String | Yes | Account password |
| `mfaCode` | String | No | MFA code if MFA is enabled |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "dGhpcyBpcyBhIHJlZnJl...",
    "expiresIn": 900,
    "tokenType": "Bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "BUYER"
    }
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 401 | `INVALID_CREDENTIALS` | Email or password is incorrect |
| 401 | `MFA_REQUIRED` | MFA code needed (no `mfaCode` provided but MFA is enabled) |
| 401 | `INVALID_MFA_CODE` | MFA code is incorrect or expired |
| 423 | `ACCOUNT_LOCKED` | Too many failed attempts; account temporarily locked |

### 2.4 POST /api/v1/auth/refresh

| Detail | Value |
|---|---|
| **Auth** | Refresh token (in body) |
| **Idempotent** | No |

**Request Body:**

```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJl..."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `refreshToken` | String | Yes | Valid refresh token |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "bmV3IHJlZnJlc2ggdG9r...",
    "expiresIn": 900,
    "tokenType": "Bearer"
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 401 | `INVALID_REFRESH_TOKEN` | Token is invalid, expired, or revoked |
| 400 | `REFRESH_TOKEN_REQUIRED` | No refresh token provided |

### 2.5 POST /api/v1/auth/logout

| Detail | Value |
|---|---|
| **Auth** | Bearer token |
| **Idempotent** | No |

**Request Body:**

```json
{
  "refreshToken": "dGhpcyBpcyBhIHJlZnJl..."
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": { "message": "Successfully logged out" },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

### 2.6 POST /api/v1/auth/forgot-password

| Detail | Value |
|---|---|
| **Auth** | None |
| **Idempotent** | No |

**Request Body:**

```json
{ "email": "user@example.com" }
```

**Response (200 OK):** Always returns 200 to prevent email enumeration.

```json
{
  "success": true,
  "data": { "message": "If the email exists, a password reset link has been sent." },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 429 | `RATE_LIMITED` | Too many requests within the time window |

### 2.7 POST /api/v1/auth/reset-password

**Request Body:**

```json
{
  "token": "reset_token_from_email",
  "password": "NewSecureP@ss456"
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 400 | `INVALID_RESET_TOKEN` | Token is invalid or expired |
| 422 | `VALIDATION_ERROR` | Password does not meet complexity requirements |

### 2.8 POST /api/v1/auth/verify-email

**Request Body:**

```json
{ "token": "email_verification_token" }
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 400 | `INVALID_VERIFICATION_TOKEN` | Token is invalid or expired |
| 409 | `ALREADY_VERIFIED` | Email is already verified |

### 2.9 POST /api/v1/auth/mfa/enable

**Request Body:**

```json
{
  "method": "TOTP",
  "phone": "+8801700000000"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qrCodeUrl": "otpauth://totp/TSBL:user@example.com?secret=...&issuer=TSBL",
    "backupCodes": ["12345678", "23456789", "34567890", "45678901", "56789012"]
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `MFA_ALREADY_ENABLED` | MFA is already configured |
| 422 | `VALIDATION_ERROR` | Invalid method or phone number |

### 2.10 POST /api/v1/auth/mfa/verify

**Request Body:**

```json
{
  "mfaToken": "temp_mfa_session_token",
  "code": "123456"
}
```

**Response:** Same as login response.

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 401 | `INVALID_MFA_CODE` | Code is incorrect or expired |
| 400 | `INVALID_MFA_TOKEN` | Temporary session token is invalid |

### 2.11 GET /api/v1/auth/me

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+8801700000000",
    "role": "BUYER",
    "isEmailVerified": true,
    "isMfaEnabled": false,
    "avatarUrl": "https://cdn.tsbl.com/avatars/uuid.jpg",
    "createdAt": "2026-07-02T14:30:00Z",
    "updatedAt": "2026-07-02T14:30:00Z"
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

---

## 3. User Management API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/users` | Yes | ADMIN | List all users with filtering and pagination |
| `GET` | `/api/v1/users/{id}` | Yes | ADMIN, USER (own) | Get user details |
| `PATCH` | `/api/v1/users/{id}` | Yes | ADMIN, USER (own) | Update user account fields |
| `DELETE` | `/api/v1/users/{id}` | Yes | ADMIN, USER (own) | Soft-delete (deactivate) user account |
| `GET` | `/api/v1/users/{id}/profile` | Yes | ADMIN, USER (own) | Get user public profile |
| `PATCH` | `/api/v1/users/{id}/profile` | Yes | USER (own) | Update user public profile |
| `GET` | `/api/v1/users/{id}/addresses` | Yes | ADMIN, USER (own) | List saved addresses |
| `POST` | `/api/v1/users/{id}/addresses` | Yes | USER (own) | Create a new address |
| `PATCH` | `/api/v1/addresses/{id}` | Yes | USER (own) | Update an address |
| `DELETE` | `/api/v1/addresses/{id}` | Yes | USER (own) | Delete an address |
| `GET` | `/api/v1/users/{id}/kyc` | Yes | ADMIN, USER (own) | Get KYC verification status |
| `POST` | `/api/v1/kyc` | Yes | USER | Submit KYC documents for verification |
| `GET` | `/api/v1/users/{id}/sessions` | Yes | ADMIN, USER (own) | List active user sessions |
| `DELETE` | `/api/v1/sessions/{id}` | Yes | ADMIN, USER (own) | Revoke a specific session |

### 3.1 GET /api/v1/users

| Detail | Value |
|---|---|
| **Auth** | Bearer token |
| **Roles** | ADMIN |
| **Idempotent** | Yes |

**Query Parameters:** `role`, `status`, `search`, `isVerified`, `sortBy`, `sortOrder`, `cursor`, `limit`.

**Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "BUYER",
      "status": "ACTIVE",
      "isEmailVerified": true,
      "isSeller": false,
      "createdAt": "2026-07-02T14:30:00Z"
    }
  ],
  "meta": {
    "timestamp": "2026-07-02T14:30:00Z",
    "requestId": "req_uuid",
    "pagination": {
      "cursor": "eyJpZCI6IjEyMyJ9",
      "nextCursor": "eyJpZCI6IjEyNSJ9",
      "hasMore": true,
      "limit": 20,
      "total": 1034
    }
  }
}
```

### 3.2 GET /api/v1/users/{id}

**Response (200 OK):** Full user object with preferences.

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 403 | `FORBIDDEN` | Not authorized to view this user |
| 404 | `NOT_FOUND` | User does not exist |

### 3.3 PATCH /api/v1/users/{id}

**Request Body:** `firstName`, `lastName`, `phone`, `avatarUrl` (all optional).

### 3.4 DELETE /api/v1/users/{id}

**Query Parameters:** `reason`.

**Response:** Soft-deletes the user account.

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `HAS_ACTIVE_ORDERS` | User has active orders preventing deletion |

### 3.5 GET /api/v1/users/{id}/profile

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "displayName": "John Doe",
    "bio": "Digital artist and designer.",
    "avatarUrl": "https://cdn.tsbl.com/avatars/uuid.jpg",
    "coverUrl": "https://cdn.tsbl.com/covers/uuid.jpg",
    "socialLinks": {
      "website": "https://johndoe.com",
      "facebook": "https://facebook.com/johndoe",
      "twitter": "https://twitter.com/johndoe",
      "linkedin": "https://linkedin.com/in/johndoe"
    },
    "joinedAt": "2026-01-15T10:00:00Z",
    "isSeller": true,
    "sellerSince": "2026-03-01T08:00:00Z"
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

### 3.6 PATCH /api/v1/users/{id}/profile

**Request Body:** `displayName`, `bio` (max 500 chars), `socialLinks`, `avatarUrl`, `coverUrl`.

### 3.7 GET /api/v1/users/{id}/addresses

**Response (200 OK):** Array of address objects with `label`, `fullName`, `phone`, `street`, `city`, `state`, `zipCode`, `country`, `isDefault`.

### 3.8 POST /api/v1/users/{id}/addresses

**Request Body:** `label`, `fullName`, `phone`, `street`, `city`, `state`, `zipCode`, `country` (ISO 3166-1 alpha-2), `isDefault`.

**Response (201 Created):** Created address object.

### 3.9 PATCH /api/v1/addresses/{id}

**Request Body:** Same fields as create, all optional.

### 3.10 DELETE /api/v1/addresses/{id}

### 3.11 GET /api/v1/users/{id}/kyc

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "status": "PENDING",
    "level": "BASIC",
    "submittedAt": "2026-07-01T10:00:00Z",
    "verifiedAt": null,
    "rejectedAt": null,
    "rejectionReason": null,
    "documents": [
      { "type": "NID", "status": "PENDING", "fileName": "nid_front.jpg", "uploadedAt": "2026-07-01T10:00:00Z" }
    ]
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

### 3.12 POST /api/v1/kyc

**Request Body** (multipart/form-data): `documentType` (`NID`, `PASSPORT`, `DRIVING_LICENSE`, `BIRTH_CERTIFICATE`), `documentNumber`, `frontImage`, `backImage`, `selfieImage`.

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `KYC_ALREADY_SUBMITTED` | KYC is already pending or verified |

### 3.13 GET /api/v1/users/{id}/sessions

**Response (200 OK):** Array of session objects with `deviceName`, `ipAddress`, `location`, `lastActiveAt`, `isCurrent`.

### 3.14 DELETE /api/v1/sessions/{id}

---

## 4. Seller Management API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/seller/apply` | Yes | USER | Submit seller application |
| `GET` | `/api/v1/seller/profile` | Yes | SELLER | Get seller profile and store settings |
| `PATCH` | `/api/v1/seller/profile` | Yes | SELLER | Update seller profile and store info |
| `GET` | `/api/v1/seller/earnings` | Yes | SELLER | Get earnings summary |
| `GET` | `/api/v1/seller/earnings/history` | Yes | SELLER | Paginated earnings history |
| `GET` | `/api/v1/seller/analytics` | Yes | SELLER | Sales and performance analytics |
| `GET` | `/api/v1/seller/reviews` | Yes | SELLER | Reviews received on products |
| `GET` | `/api/v1/seller/orders` | Yes | SELLER | Orders for seller's products |

### 4.1 POST /api/v1/seller/apply

**Request Body:** `storeName`, `storeDescription`, `storeSlug`, `category`, `phone`, `country`, `taxId`, `agreedToTerms`.

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "applicationId": "uuid",
    "status": "PENDING",
    "submittedAt": "2026-07-02T14:30:00Z",
    "message": "Your seller application has been submitted for review."
  },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_uuid" }
}
```

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `ALREADY_APPLIED` | Application already pending |
| 409 | `ALREADY_SELLER` | User is already a seller |
| 409 | `SLUG_TAKEN` | Store slug is already in use |

### 4.2 GET /api/v1/seller/profile

**Response (200 OK):** `storeName`, `storeSlug`, `storeDescription`, `storeLogo`, `storeBanner`, `category`, `status`, `rating`, `totalProducts`, `totalSales`, `memberSince`, `payoutAccount`, `settings`.

### 4.3 PATCH /api/v1/seller/profile

**Request Body:** `storeName`, `storeDescription`, `storeLogo`, `storeBanner`, `settings`.

### 4.4 GET /api/v1/seller/earnings

**Query Parameters:** `period` (`today`, `this_week`, `this_month`, `this_year`, `all`).

**Response:** `totalEarned`, `pendingClearance`, `availableForWithdrawal`, `totalWithdrawn`, `periodBreakdown`, `lastPayout`.

### 4.5 GET /api/v1/seller/earnings/history

**Query Parameters:** `from`, `to`, `cursor`, `limit`.

**Response:** Array of earnings records with `orderId`, `productName`, `amount`, `commission`, `netEarned`, `status`, `paidAt`.

### 4.6 GET /api/v1/seller/analytics

**Query Parameters:** `period` (`7d`, `30d`, `90d`, `1y`).

**Response:** `sales`, `views`, `products` (topSelling), `trafficSources`, `chartData`.

### 4.7 GET /api/v1/seller/reviews

**Query Parameters:** `rating`, `productId`, `sortBy`, `cursor`, `limit`.

**Response:** `averageRating`, `ratingDistribution`, `totalReviews`, array of reviews.

### 4.8 GET /api/v1/seller/orders

**Query Parameters:** `status`, `from`, `to`, `search`, `sortBy`, `sortOrder`, `cursor`, `limit`.

---

## 5. Product & Marketplace API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/categories` | No | — | List categories as a tree |
| `GET` | `/api/v1/categories/{slug}` | No | — | Get category details with subcategories |
| `GET` | `/api/v1/products` | No | — | List products with filters, sorting, pagination |
| `GET` | `/api/v1/products/{slug}` | No | — | Get product details |
| `POST` | `/api/v1/products` | Yes | SELLER, ADMIN | Create a new product |
| `PATCH` | `/api/v1/products/{id}` | Yes | SELLER (own), ADMIN | Update product |
| `DELETE` | `/api/v1/products/{id}` | Yes | SELLER (own), ADMIN | Soft-delete a product |
| `POST` | `/api/v1/products/{id}/images` | Yes | SELLER (own), ADMIN | Upload product images |
| `DELETE` | `/api/v1/products/images/{id}` | Yes | SELLER (own), ADMIN | Delete a product image |
| `PATCH` | `/api/v1/products/{id}/variants` | Yes | SELLER (own), ADMIN | Manage product variants |
| `PATCH` | `/api/v1/products/{id}/inventory` | Yes | SELLER (own), ADMIN | Update inventory/stock |
| `GET` | `/api/v1/products/{id}/reviews` | No | — | List reviews for a product |
| `GET` | `/api/v1/search` | No | — | Full-text search across products |
| `GET` | `/api/v1/products/featured` | No | — | List featured/promoted products |

### 5.1 GET /api/v1/categories

**Response (200 OK):** Nested tree of categories with `id`, `name`, `slug`, `icon`, `imageUrl`, `productCount`, `children[]`.

### 5.2 GET /api/v1/categories/{slug}

**Response:** Category with `parent`, `children`, `metaTitle`, `metaDescription`, SEO fields.

### 5.3 GET /api/v1/products

**Query Parameters:** `category`, `subcategory`, `minPrice`, `maxPrice`, `seller`, `rating`, `productType`, `tags`, `inStock`, `sortBy`, `sortOrder`, `cursor`, `limit`.

**Response:** Array of product summaries with `id`, `name`, `slug`, `price`, `compareAtPrice`, `rating`, `salesCount`, `images`, `seller`, `tags`.

### 5.4 GET /api/v1/products/{slug}

**Response:** Full product detail including `variants`, `attributes`, `licenses`, `seo`, `seller` detail, `videoUrl`, `deliveryType`, `hasLicenseOptions`.

### 5.5 POST /api/v1/products

**Request Body:** `name`, `description`, `shortDescription`, `price`, `compareAtPrice`, `currency`, `productType`, `deliveryType`, `categoryId`, `tags`, `attributes`, `variants`, `licenses`, `hasVariants`, `stock`, `isFeatured`.

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `SLUG_CONFLICT` | Generated slug already exists |

### 5.6 PATCH /api/v1/products/{id}

Same fields as create (all optional).

### 5.7 DELETE /api/v1/products/{id}

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `HAS_ACTIVE_ORDERS` | Product has active orders |

### 5.8 POST /api/v1/products/{id}/images

**Request Body** (multipart/form-data): `images[]` (max 10, max 5 MB each), `isPrimary` (index).

### 5.9 DELETE /api/v1/products/images/{id}

### 5.10 PATCH /api/v1/products/{id}/variants

**Request Body:** Full replacement `{ "variants": [...] }`.

### 5.11 PATCH /api/v1/products/{id}/inventory

**Request Body:** `stock`, `lowStockThreshold`, `isInStock`.

### 5.12 GET /api/v1/products/{id}/reviews

**Query Parameters:** `rating`, `sortBy`, `sortOrder`, `cursor`, `limit`.

**Response:** `averageRating`, `ratingDistribution`, `totalReviews`, array of reviews with `buyer`, `sellerReply`, `isVerifiedPurchase`.

### 5.13 GET /api/v1/search

**Query Parameters:** `q` (min 2 chars), `category`, `minPrice`, `maxPrice`, `productType`, `rating`, `inStock`, `sortBy` (relevance, price, rating, newest), `sortOrder`, `cursor`, `limit`.

**Response:** `results`, `suggestions`, `facets` (categories, priceRanges, ratings).

### 5.14 GET /api/v1/products/featured

**Query Parameters:** `limit`. Returns array of featured product summaries.

---

## 6. Cart & Checkout API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/cart` | Yes | All | Get the current user's cart |
| `POST` | `/api/v1/cart/items` | Yes | All | Add an item to the cart |
| `PATCH` | `/api/v1/cart/items/{id}` | Yes | All | Update cart item quantity or variant |
| `DELETE` | `/api/v1/cart/items/{id}` | Yes | All | Remove an item from the cart |
| `POST` | `/api/v1/cart/apply-coupon` | Yes | All | Apply a coupon code to the cart |
| `DELETE` | `/api/v1/cart/coupon` | Yes | All | Remove the applied coupon |
| `POST` | `/api/v1/checkout` | Yes | All | Convert cart to an order |
| `GET` | `/api/v1/cart/saved` | Yes | All | List saved-for-later items |

### 6.1 GET /api/v1/cart

**Response:** Cart with `items[]` (productId, productName, slug, variant, license, unitPrice, quantity, subtotal), `coupon`, `subtotal`, `discount`, `tax`, `shipping`, `total`, `currency`, `itemCount`, `expiresAt`.

### 6.2 POST /api/v1/cart/items

**Request Body:** `productId`, `variantId`, `licenseType`, `quantity` (default: 1, max: 100).

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `SELLER_CANNOT_BUY_OWN` | Seller cannot add their own product |

### 6.3 PATCH /api/v1/cart/items/{id}

**Request Body:** `quantity`, `variantId`.

### 6.4 DELETE /api/v1/cart/items/{id}

### 6.5 POST /api/v1/cart/apply-coupon

**Request Body:** `{ "code": "SAVE20" }`.

**Error Codes:** `COUPON_NOT_FOUND`, `COUPON_EXPIRED`, `COUPON_MINIMUM_NOT_MET`, `COUPON_EXHAUSTED`, `COUPON_ALREADY_APPLIED`.

### 6.6 DELETE /api/v1/cart/coupon

### 6.7 POST /api/v1/checkout

**Idempotent:** No (use `Idempotency-Key` header).

**Request Body:** `shippingAddressId`, `billingAddressId`, `paymentMethodId`, `notes`, `couponCode`.

**Response (201 Created):** `orderId`, `orderNumber`, `status`, `total`, `paymentUrl`.

**Error Codes:** `EMPTY_CART`, `INVALID_PAYMENT_METHOD`, `PRODUCT_OUT_OF_STOCK`, `PRICE_CHANGED`, `DUPLICATE_REQUEST`.

### 6.8 GET /api/v1/cart/saved

---

## 7. Order API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/orders` | Yes | All | List orders (buyer sees own, seller sees own) |
| `GET` | `/api/v1/orders/{id}` | Yes | BUYER (own), SELLER (own), ADMIN | Get order details |
| `POST` | `/api/v1/orders/{id}/cancel` | Yes | BUYER (own), ADMIN | Cancel an order |
| `POST` | `/api/v1/orders/{id}/confirm-delivery` | Yes | BUYER (own) | Confirm receipt of order |
| `GET` | `/api/v1/orders/{id}/timeline` | Yes | BUYER (own), SELLER (own), ADMIN | Order status timeline |
| `GET` | `/api/v1/orders/{id}/invoice` | Yes | BUYER (own), SELLER (own), ADMIN | Download invoice PDF |

### 7.1 GET /api/v1/orders

**Query Parameters:** `status`, `from`, `to`, `search`, `sortBy`, `sortOrder`, `cursor`, `limit`.

### 7.2 GET /api/v1/orders/{id}

**Response:** Full order with `items[]`, `shippingAddress`, `billingAddress`, `payment`, `coupon`, `timeline[]`, `escrowStatus`, `notes`.

### 7.3 POST /api/v1/orders/{id}/cancel

**Request Body:** `reason`, `items[]` (for partial cancellation).

**Error Codes:** `ORDER_CANNOT_BE_CANCELLED`.

### 7.4 POST /api/v1/orders/{id}/confirm-delivery

**Request Body:** `{ "pin": "1234" }`.

**Error Codes:** `INVALID_PIN`, `ORDER_NOT_SHIPPED`, `ALREADY_DELIVERED`.

### 7.5 GET /api/v1/orders/{id}/timeline

**Response:** `currentStatus`, `timeline[]` (status, label, timestamp, note, actor), `estimatedDelivery`.

### 7.6 GET /api/v1/orders/{id}/invoice

**Headers:** `Content-Type: application/pdf`, `Content-Disposition: attachment`.

---

## 8. Payment & Wallet API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/payments/deposit` | Yes | All | Deposit funds to wallet |
| `GET` | `/api/v1/payments/methods` | Yes | All | List saved payment methods |
| `POST` | `/api/v1/payments/methods` | Yes | All | Add a payment method |
| `DELETE` | `/api/v1/payments/methods/{id}` | Yes | All | Remove a payment method |
| `GET` | `/api/v1/wallet` | Yes | All | Get wallet balance |
| `GET` | `/api/v1/wallet/transactions` | Yes | All | Transaction history |
| `POST` | `/api/v1/withdrawals` | Yes | SELLER | Request a withdrawal |
| `GET` | `/api/v1/withdrawals` | Yes | SELLER | Withdrawal history |
| `GET` | `/api/v1/wallet/statements` | Yes | All | Download wallet statement |

### 8.1 POST /api/v1/payments/deposit

**Request Body:** `amount`, `currency`, `paymentMethodId`, `redirectUrl`.

**Response:** `depositId`, `amount`, `status`, `paymentUrl`, `expiresAt`.

### 8.2 GET /api/v1/payments/methods

**Response:** Array of payment methods with `type` (CARD, BKASH, NAGAD, ROCKET, BANK_ACCOUNT), `brand`, `last4`, `isDefault`.

### 8.3 POST /api/v1/payments/methods

**Request Body (CARD):** `type`, `cardNumber`, `expiryMonth`, `expiryYear`, `cvv`, `cardholderName`, `isDefault`.
**Request Body (Mobile Banking):** `type`, `phone`, `accountHolder`, `isDefault`.

### 8.4 DELETE /api/v1/payments/methods/{id}

### 8.5 GET /api/v1/wallet

**Response:** `balance`, `pendingBalance`, `totalDeposited`, `totalWithdrawn`, `totalSpent`, `status`.

### 8.6 GET /api/v1/wallet/transactions

**Query Parameters:** `type` (DEPOSIT, WITHDRAWAL, PURCHASE, REFUND, COMMISSION, AFFILIATE), `status`, `from`, `to`, `cursor`, `limit`.

### 8.7 POST /api/v1/withdrawals

**Request Body:** `amount`, `paymentMethodId`, `notes`.

**Error Codes:** `INSUFFICIENT_BALANCE`, `WITHDRAWAL_MINIMUM`, `NO_PAYOUT_METHOD`.

### 8.8 GET /api/v1/withdrawals

**Query Parameters:** `status`, `cursor`, `limit`.

### 8.9 GET /api/v1/wallet/statements

**Query Parameters:** `month`, `year`, `format` (pdf, csv). Returns binary download.

---

## 9. Escrow API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/escrow/{orderId}` | Yes | BUYER (own), SELLER (own), ADMIN | Get escrow status |
| `GET` | `/api/v1/escrow/transactions` | Yes | SELLER, ADMIN | List escrow transactions |

### 9.1 GET /api/v1/escrow/{orderId}

**Escrow Statuses:** `PENDING`, `FUNDED`, `HELD`, `RELEASED`, `REFUNDED`, `DISPUTED`, `PARTIALLY_RELEASED`.

### 9.2 GET /api/v1/escrow/transactions

**Query Parameters:** `status`, `from`, `to`, `cursor`, `limit`.

---

## 10. Review API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/reviews` | Yes | BUYER (verified purchase) | Create a product review |
| `GET` | `/api/v1/reviews` | No | — | List reviews with filters |
| `PATCH` | `/api/v1/reviews/{id}` | Yes | BUYER (own) | Update own review (within 24h) |
| `DELETE` | `/api/v1/reviews/{id}` | Yes | BUYER (own), ADMIN | Delete a review |
| `POST` | `/api/v1/reviews/{id}/helpful` | Yes | All | Mark review as helpful/unhelpful |
| `POST` | `/api/v1/reviews/{id}/report` | Yes | All | Report a review |

### 10.1 POST /api/v1/reviews

**Request Body:** `productId`, `orderId`, `rating` (1–5), `title`, `body` (max 5000 chars), `images[]` (max 5).

**Error Codes:** `ALREADY_REVIEWED`, `FORBIDDEN` (not a verified purchase).

### 10.2 GET /api/v1/reviews

**Query Parameters:** `productId`, `sellerId`, `rating`, `sortBy`, `sortOrder`, `cursor`, `limit`.

### 10.3 PATCH /api/v1/reviews/{id}

**Error Codes:** `EDIT_WINDOW_EXPIRED` (more than 24 hours).

### 10.5 POST /api/v1/reviews/{id}/helpful

**Request Body:** `{ "isHelpful": true }`.

### 10.6 POST /api/v1/reviews/{id}/report

**Request Body:** `reason` (SPAM, FAKE, OFFENSIVE, CONFLICT_OF_INTEREST, OTHER), `description`.

---

## 11. Messaging API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/conversations` | Yes | All | List user's conversations |
| `POST` | `/api/v1/conversations` | Yes | All | Start a new conversation |
| `GET` | `/api/v1/conversations/{id}` | Yes | Participant | Get conversation with messages |
| `POST` | `/api/v1/conversations/{id}/messages` | Yes | Participant | Send a message |
| `PATCH` | `/api/v1/conversations/{id}/read` | Yes | Participant | Mark conversation as read |
| `DELETE` | `/api/v1/conversations/{id}` | Yes | Participant | Archive conversation |

### 11.1 GET /api/v1/conversations

**Query Parameters:** `status` (ACTIVE, ARCHIVED), `search`, `unreadOnly`, `cursor`, `limit`.

### 11.2 POST /api/v1/conversations

**Request Body:** `participantId`, `initialMessage`, `productId` (context), `orderId` (context).

### 11.3 GET /api/v1/conversations/{id}

**Query Parameters:** `before` (timestamp), `limit`.

### 11.4 POST /api/v1/conversations/{id}/messages

**Request Body:** `body`, `messageType` (TEXT, IMAGE, FILE), `attachments[]`.

---

## 12. Notification API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/notifications` | Yes | All | List user's notifications |
| `PATCH` | `/api/v1/notifications/{id}/read` | Yes | All | Mark a notification as read |
| `POST` | `/api/v1/notifications/read-all` | Yes | All | Mark all notifications as read |
| `GET` | `/api/v1/notifications/unread-count` | Yes | All | Get unread notification count |
| `PATCH` | `/api/v1/notifications/settings` | Yes | All | Update notification preferences |

### 12.1 GET /api/v1/notifications

**Query Parameters:** `type` (ORDER, PAYMENT, MESSAGE, REVIEW, SYSTEM, PROMOTION), `isRead`, `cursor`, `limit`.

### 12.5 PATCH /api/v1/notifications/settings

**Request Body:** `email`, `sms`, `push` objects with boolean flags for each category.

---

## 13. Support & Dispute API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/support/tickets` | Yes | All | Create a support ticket |
| `GET` | `/api/v1/support/tickets` | Yes | All, ADMIN | List support tickets |
| `GET` | `/api/v1/support/tickets/{id}` | Yes | Owner, ADMIN | Get ticket details |
| `POST` | `/api/v1/support/tickets/{id}/messages` | Yes | Owner, ADMIN | Add a message to a ticket |
| `POST` | `/api/v1/disputes` | Yes | BUYER, SELLER, ADMIN | Open a dispute |
| `GET` | `/api/v1/disputes` | Yes | Participant, ADMIN | List disputes |
| `GET` | `/api/v1/disputes/{id}` | Yes | Participant, ADMIN | Get dispute details |
| `POST` | `/api/v1/disputes/{id}/evidence` | Yes | Participant, ADMIN | Submit evidence |
| `POST` | `/api/v1/refunds` | Yes | BUYER | Request a refund |
| `GET` | `/api/v1/refunds` | Yes | BUYER, SELLER, ADMIN | List refund requests |

### 13.1 POST /api/v1/support/tickets

**Request Body:** `subject` (10–200 chars), `category` (ACCOUNT, PAYMENT, ORDER, PRODUCT, SELLER, TECHNICAL, OTHER), `priority` (LOW, MEDIUM, HIGH, URGENT), `description`, `orderId`, `attachments[]`.

### 13.2 POST /api/v1/disputes

**Request Body:** `orderId`, `reason` (ITEM_NOT_RECEIVED, ITEM_NOT_AS_DESCRIBED, QUALITY_ISSUE, INCORRECT_ITEM, FRAUD, OTHER), `description`, `requestedResolution` (REFUND, PARTIAL_REFUND, REPLACEMENT).

### 13.4 POST /api/v1/disputes/{id}/evidence

**Request Body** (multipart/form-data): `files[]`, `description`.

### 13.5 POST /api/v1/refunds

**Request Body:** `orderId`, `items[]`, `reason`.

**Error Codes:** `ALREADY_REFUNDED`, `REFUND_WINDOW_EXPIRED`.

---

## 14. Affiliate API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/affiliate/dashboard` | Yes | AFFILIATE | Get affiliate dashboard stats |
| `GET` | `/api/v1/affiliate/links` | Yes | AFFILIATE | List affiliate referral links |
| `POST` | `/api/v1/affiliate/links` | Yes | AFFILIATE | Generate a new referral link |
| `GET` | `/api/v1/affiliate/earnings` | Yes | AFFILIATE | Earnings history |
| `POST` | `/api/v1/affiliate/withdraw` | Yes | AFFILIATE | Withdraw affiliate earnings |

### 14.1 GET /api/v1/affiliate/dashboard

**Response:** `totalClicks`, `totalConversions`, `conversionRate`, `totalEarned`, `pendingCommission`, `availableForWithdrawal`, `referralCode`, `referralUrl`, `chartData`.

### 14.2 GET /api/v1/affiliate/links

**Response:** Array of links with `url`, `productName`, `commissionRate`, `clicks`, `conversions`, `earnings`, `status`.

### 14.3 POST /api/v1/affiliate/links

**Request Body:** `productId`, `customSlug`.

### 14.5 POST /api/v1/affiliate/withdraw

**Request Body:** `amount`, `paymentMethodId`.

---

## 15. Admin API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/admin/dashboard` | Yes | ADMIN | Admin dashboard statistics |
| `GET` | `/api/v1/admin/users` | Yes | ADMIN | User management list |
| `PATCH` | `/api/v1/admin/users/{id}/status` | Yes | ADMIN | Update user account status |
| `GET` | `/api/v1/admin/sellers` | Yes | ADMIN | Seller management list |
| `PATCH` | `/api/v1/admin/sellers/{id}/approve` | Yes | ADMIN | Approve or reject seller |
| `GET` | `/api/v1/admin/products` | Yes | ADMIN | Product moderation queue |
| `PATCH` | `/api/v1/admin/products/{id}/approve` | Yes | ADMIN | Approve a product |
| `PATCH` | `/api/v1/admin/products/{id}/reject` | Yes | ADMIN | Reject a product |
| `GET` | `/api/v1/admin/disputes` | Yes | ADMIN | Dispute management list |
| `POST` | `/api/v1/admin/disputes/{id}/resolve` | Yes | ADMIN | Resolve a dispute |
| `GET` | `/api/v1/admin/reports` | Yes | ADMIN | Generate and list reports |
| `GET` | `/api/v1/admin/audit-logs` | Yes | ADMIN | Audit log viewer |

### 15.1 GET /api/v1/admin/dashboard

**Response:** `overview` (totalUsers, totalSellers, totalProducts, totalOrders, totalRevenue, pendingSellers, pendingProducts, openDisputes), `revenueChart[]`, `topCategories[]`.

### 15.2 GET /api/v1/admin/users

Same as `/api/v1/users` but with additional filters: `kycStatus`, `sellerStatus`.

### 15.3 PATCH /api/v1/admin/users/{id}/status

**Request Body:** `status` (ACTIVE, SUSPENDED, BANNED, INACTIVE), `reason`.

### 15.4 GET /api/v1/admin/sellers

**Query Parameters:** `status` (PENDING, ACTIVE, REJECTED, SUSPENDED), `search`, `cursor`, `limit`.

### 15.5 PATCH /api/v1/admin/sellers/{id}/approve

**Request Body:** `action` (APPROVE, REJECT), `note`.

### 15.6 GET /api/v1/admin/products

**Query Parameters:** `status` (PENDING_APPROVAL, APPROVED, REJECTED, FLAGGED), `search`, `cursor`, `limit`.

### 15.7 PATCH /api/v1/admin/products/{id}/approve

**Request Body:** `note`.

### 15.8 PATCH /api/v1/admin/products/{id}/reject

**Request Body:** `reason` (COPYRIGHT_INFRINGEMENT, INAPPROPRIATE_CONTENT, MISLEADING_DESCRIPTION, DUPLICATE, LOW_QUALITY, OTHER), `note`.

### 15.9 GET /api/v1/admin/disputes

**Query Parameters:** `status`, `from`, `to`, `cursor`, `limit`.

### 15.10 POST /api/v1/admin/disputes/{id}/resolve

**Request Body:** `ruling` (IN_FAVOR_OF_BUYER, IN_FAVOR_OF_SELLER, PARTIAL), `resolution` (FULL_REFUND, PARTIAL_REFUND, RELEASE_TO_SELLER, OTHER), `note`, `refundAmount`.

### 15.11 GET /api/v1/admin/reports

**Query Parameters:** `type` (revenue, users, sellers, products, disputes), `period`, `from`, `to`, `format` (json, csv, pdf).

### 15.12 GET /api/v1/admin/audit-logs

**Query Parameters:** `actorId`, `action`, `resource`, `resourceId`, `from`, `to`, `cursor`, `limit`.

**Response:** Array of audit log entries with `actorId`, `actorEmail`, `action`, `resource`, `resourceId`, `details`, `ipAddress`, `createdAt`.

---

## 16. CMS & Content API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/cms/pages` | No | — | List CMS pages |
| `GET` | `/api/v1/cms/pages/{slug}` | No | — | Get a CMS page by slug |
| `POST` | `/api/v1/cms/pages` | Yes | ADMIN | Create a CMS page |
| `PATCH` | `/api/v1/cms/pages/{id}` | Yes | ADMIN | Update a CMS page |
| `GET` | `/api/v1/blog` | No | — | List blog posts |
| `GET` | `/api/v1/blog/{slug}` | No | — | Get a blog post by slug |
| `GET` | `/api/v1/faq` | No | — | List FAQ entries |
| `GET` | `/api/v1/banners` | No | — | List active banners |
| `GET` | `/api/v1/announcements` | No | — | List announcements |

### 16.1 GET /api/v1/cms/pages

**Response:** Array of page summaries with `title`, `slug`, `excerpt`, `isPublished`, `updatedAt`.

### 16.2 GET /api/v1/cms/pages/{slug}

**Response:** Full page with `content` (HTML), `metaTitle`, `metaDescription`, `publishedAt`.

### 16.3 POST /api/v1/cms/pages

**Request Body:** `title`, `slug`, `content`, `metaTitle`, `metaDescription`, `isPublished`.

### 16.5 GET /api/v1/blog

**Query Parameters:** `category`, `tag`, `search`, `cursor`, `limit`.

### 16.6 GET /api/v1/blog/{slug}

**Response:** Full blog post with `content`, `featuredImage`, `author`, `category`, `tags`, `readTimeMinutes`, `publishedAt`.

### 16.7 GET /api/v1/faq

**Response:** Array of FAQ entries with `question`, `answer`, `category`, `order`.

### 16.8 GET /api/v1/banners

**Response:** Array of active banners with `title`, `imageUrl`, `linkUrl`, `position` (HOME_TOP, HOME_MIDDLE, SIDEBAR, CATEGORY_TOP), `startsAt`, `endsAt`.

### 16.9 GET /api/v1/announcements

**Response:** Array of announcements with `title`, `body`, `type` (INFO, WARNING, MAINTENANCE), `isDismissible`, `startsAt`, `endsAt`.

---

## 17. System & Configuration API

| Method | URL | Auth Required | Roles Allowed | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/system/health` | No | — | Health check endpoint |
| `GET` | `/api/v1/system/config` | No | — | Public platform configuration |
| `GET` | `/api/v1/system/currencies` | No | — | List supported currencies |
| `GET` | `/api/v1/system/languages` | No | — | List supported languages |
| `GET` | `/api/v1/system/countries` | No | — | List countries |

### 17.1 GET /api/v1/system/health

**Response:** `status`, `version`, `uptime`, `database`, `cache`, `storage`, `timestamp`.

### 17.2 GET /api/v1/system/config

**Response:** `platformName`, `platformUrl`, `supportEmail`, `currency`, `currencies[]`, `language`, `languages[]`, `timezone`, `pagination`, `features`, `socialLinks`.

### 17.3 GET /api/v1/system/currencies

**Response:** Array of `{ code, name, symbol, decimalPlaces, isDefault }`.

### 17.4 GET /api/v1/system/languages

**Response:** Array of `{ code, name, nativeName, isDefault }`.

### 17.5 GET /api/v1/system/countries

**Response:** Array of `{ code (ISO 3166-1 alpha-2), name, dialCode, flag }`.

---

## 18. WebSocket Events

The TSBL platform uses WebSocket connections for real-time bidirectional communication. Connections are authenticated via JWT token passed as a query parameter.

### 18.1 Connection

```
wss://api.tsbl.com/ws/{namespace}?token={jwt_access_token}
```

### 18.2 Endpoints

| Endpoint | Namespace | Description | Auth Required |
|---|---|---|---|
| `wss://api.tsbl.com/ws/chat/{conversation_id}` | Chat | Real-time messaging within a conversation | Yes (participant) |
| `wss://api.tsbl.com/ws/notifications` | Notifications | Real-time user notifications | Yes |
| `wss://api.tsbl.com/ws/orders/{order_id}` | Orders | Real-time order status updates | Yes (buyer/seller) |

### 18.3 Chat WebSocket (`/ws/chat/{conversation_id}`)

**Client → Server Events:**

| Event | Payload | Description |
|---|---|---|
| `message:send` | `{ "body": "Hello!", "messageType": "TEXT", "attachments": [] }` | Send a message |
| `message:typing` | `{ "isTyping": true }` | Typing indicator |
| `message:read` | `{ "messageId": "uuid" }` | Mark message as read |

**Server → Client Events:**

| Event | Payload | Description |
|---|---|---|
| `message:new` | `{ "id": "uuid", "senderId": "uuid", "body": "...", "createdAt": "..." }` | New message received |
| `message:typing` | `{ "userId": "uuid", "isTyping": true }` | Other participant typing status |
| `message:read` | `{ "messageId": "uuid", "userId": "uuid" }` | Message read receipt |
| `conversation:archived` | `{ "conversationId": "uuid" }` | Conversation archived |

### 18.4 Notifications WebSocket (`/ws/notifications`)

**Server → Client Events:**

| Event | Payload | Description |
|---|---|---|
| `notification:new` | `{ "id": "uuid", "type": "ORDER", "title": "...", "body": "...", "data": {} }` | New notification |
| `notification:unread_count` | `{ "count": 5 }` | Updated unread count |

### 18.5 Orders WebSocket (`/ws/orders/{order_id}`)

**Server → Client Events:**

| Event | Payload | Description |
|---|---|---|
| `order:status_changed` | `{ "orderId": "uuid", "from": "PENDING", "to": "PROCESSING", "timestamp": "..." }` | Order status transition |
| `order:payment_confirmed` | `{ "orderId": "uuid", "transactionId": "TRX123456" }` | Payment confirmed |
| `order:delivery_confirmed` | `{ "orderId": "uuid", "deliveredAt": "..." }` | Delivery confirmed |
| `order:dispute_opened` | `{ "orderId": "uuid", "disputeId": "uuid" }` | Dispute opened on order |
| `order:escrow_released` | `{ "orderId": "uuid", "amount": 1320.00 }` | Escrow funds released |

---

## 19. API Standards

### 19.1 Pagination Format

The TSBL API uses **cursor-based pagination** for all collection endpoints.

**Request:**
```
GET /api/v1/products?cursor=eyJpZCI6IjEyMyJ9&limit=20
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `cursor` | String | No | Opaque base64-encoded cursor for pagination |
| `limit` | Integer | No | Number of results per page (default: 20, max varies by endpoint) |

**Response (in `meta.pagination`):**

| Field | Type | Description |
|---|---|---|
| `cursor` | String | Current cursor value (null for first page) |
| `nextCursor` | String | Cursor for the next page (null if no more pages) |
| `hasMore` | Boolean | Whether there are more results available |
| `limit` | Integer | The limit used for this request |
| `total` | Integer | Estimated total count |

### 19.2 Response Format

**Success (single resource):**
```json
{
  "success": true,
  "data": { ... },
  "meta": { "timestamp": "2026-07-02T14:30:00Z", "requestId": "req_a1b2c3d4" }
}
```

**Success (collection):**
```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "timestamp": "2026-07-02T14:30:00Z",
    "requestId": "req_a1b2c3d4",
    "pagination": { ... }
  }
}
```

**Error (RFC 7807):**
```json
{
  "type": "https://api.tsbl.com/errors/error-type",
  "title": "Error Title",
  "status": 422,
  "detail": "Human-readable description.",
  "instance": "/api/v1/resource",
  "timestamp": "2026-07-02T14:30:00Z",
  "requestId": "req_a1b2c3d4",
  "errors": [
    { "field": "fieldName", "message": "Field error message", "code": "ERROR_CODE" }
  ]
}
```

### 19.3 Error Codes Overview

| HTTP Status | Code | Description |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body validation failed |
| 400 | `BAD_REQUEST` | Malformed request syntax |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 401 | `INVALID_CREDENTIALS` | Wrong email or password |
| 401 | `TOKEN_EXPIRED` | Access token has expired |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Resource already exists or state conflict |
| 409 | `DUPLICATE_REQUEST` | Idempotency key already used |
| 410 | `GONE` | Resource has been permanently removed |
| 413 | `PAYLOAD_TOO_LARGE` | Request body exceeds size limit |
| 422 | `UNPROCESSABLE_ENTITY` | Semantic validation failure |
| 429 | `RATE_LIMITED` | Rate limit exceeded |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 502 | `BAD_GATEWAY` | Upstream service unavailable |
| 503 | `SERVICE_UNAVAILABLE` | Platform in maintenance mode |

### 19.4 Rate Limits

| Tier | Rate Limit | Burst | Scope |
|---|---|---|---|
| **Unauthenticated** | 60 req/min | 100 | IP address |
| **Authenticated** | 300 req/min | 500 | User ID |
| **Seller** | 600 req/min | 1000 | User ID |
| **Admin** | 1200 req/min | 2000 | User ID |
| **Payment endpoints** | 30 req/min | 50 | User ID |

Rate limit headers returned with every response:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1688315400
```

### 19.5 Deprecation Policy

| Phase | Headers Added | Duration | Action Required |
|---|---|---|---|
| **Deprecation notice** | `Deprecation: true`, `Sunset: <date>` | 6 months before removal | Clients should migrate |
| **Soft removal** | `Warning: 299 api.tsbl.com "Endpoint deprecated"` | Last 30 days | Endpoint returns 404 |
| **Removal** | — | After sunset date | Endpoint returns 410 Gone |

### 19.6 Standard Headers

| Header | Description | Example |
|---|---|---|
| `X-Request-Id` | Correlation ID (client can set; server generates if absent) | `req_a1b2c3d4` |
| `Idempotency-Key` | Idempotency key for safe retries (POST /checkout, /payments) | `uuid-v4` |
| `Idempotency-Replay` | Set to `true` when a previous request result is replayed | `true` |
| `X-RateLimit-*` | Rate limit information | See above |
| `Deprecation` | Set to `true` for deprecated endpoints | `true` |
| `Sunset` | ISO 8601 date when the endpoint will be removed | `Sun, 02 Jan 2027 00:00:00 GMT` |

---

## 20. API Security

### 20.1 Authentication Flow

```
Client                     API Gateway                  Auth Service
  |   POST /auth/login         |                            |
  |--------------------------->|                            |
  |                            |  Validate credentials      |
  |                            |--------------------------->|
  |                            |  Return JWT pair           |
  |                            |<---------------------------|
  |<--- accessToken + refresh -|                            |
  |                            |                            |
  |  GET /resource             |                            |
  |  Authorization: Bearer ... |                            |
  |--------------------------->|                            |
  |                            |  Validate token (stateless)|
  |<--- 200 OK + data --------|                            |
```

### 20.2 JWT Token Structure

**Access Token (15 min):**
```json
{
  "sub": "user-uuid",
  "role": "BUYER",
  "permissions": ["read:products", "write:orders"],
  "iat": 1688315400,
  "exp": 1688316300,
  "jti": "unique-token-id"
}
```

**Refresh Token (7 days):** Opaque string stored as bcrypt hash in database. No claims.

### 20.3 Token Security Rules

- Access tokens are **never stored** in the database (stateless)
- Refresh tokens are stored as bcrypt hashes
- Token rotation: each refresh invalidates the previous refresh token
- On logout, the refresh token is deleted from the database
- On password change, all refresh tokens for the user are invalidated
- Tokens are transmitted over HTTPS only

### 20.4 Rate Limiting Details

| Layer | Mechanism | Configuration |
|---|---|---|
| **Edge (CDN)** | IP-based token bucket | 1000 req/s per IP |
| **API Gateway** | User-based sliding window | Configurable per tier |
| **Application** | Endpoint-specific throttling | Login: 5 req/min, Search: 60 req/min |
| **Database** | Connection pool limits | Max 200 concurrent connections |

**Rate Limit Response (429):**
```json
{
  "type": "https://api.tsbl.com/errors/rate-limited",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Please slow down your requests.",
  "instance": "/api/v1/auth/login",
  "retryAfter": 45
}
```

**Headers:**
```
Retry-After: 45
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1688315445
```

### 20.5 CORS Configuration

```
Access-Control-Allow-Origin: https://tsbl.com, https://admin.tsbl.com
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, Idempotency-Key, X-Request-Id
Access-Control-Expose-Headers: X-Request-Id, X-RateLimit-*, Idempotency-Replay
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true
```

### 20.6 Idempotency Keys for Payments

**How it works:**
1. Client generates a UUID v4 `Idempotency-Key` header
2. Server checks if this key has been seen before:
   - **New key**: Process the request, store the result mapped to the key
   - **Existing key**: Return the stored response with `Idempotency-Replay: true` header
3. The key expires after 24 hours

**Endpoints requiring idempotency keys:**
- `POST /api/v1/checkout`
- `POST /api/v1/payments/deposit`

**Error Codes:**

| Status | Code | Condition |
|---|---|---|
| 409 | `DUPLICATE_REQUEST` | Idempotency key already used with a different request body |
| 422 | `MISSING_IDEMPOTENCY_KEY` | Idempotency-Key header is required for this endpoint |

### 20.7 API Key Management (for third-party integrations)

Admin users can generate API keys for programmatic access:

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/admin/api-keys` | GET | List API keys |
| `/api/v1/admin/api-keys` | POST | Generate a new API key |
| `/api/v1/admin/api-keys/{id}` | PATCH | Update API key permissions |
| `/api/v1/admin/api-keys/{id}` | DELETE | Revoke an API key |

**API Key Authentication:** Pass via `X-API-Key` header or `api_key` query parameter.

**Scopes:** `full_access`, `read_only`, `products:read`, `products:write`, `orders:read`, `orders:write`.

---

*Document ID: TSBL-ARCH-API-009 | Version: 1.0 | Status: Draft | © 2026 TRUE STAR BD LIMITED*
