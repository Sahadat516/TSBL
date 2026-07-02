# TRUE STAR BD LIMITED — API Architecture & Specification

> **Document Version:** 1.0.0
> **Classification:** Internal — Confidential
> **Author:** Enterprise API Architecture Team
> **Last Updated:** 2026-07-02
> **Status:** Final Draft
> **Applies To:** Multi-Vendor Digital Marketplace Platform

---

## Table of Contents

1. API Philosophy
2. API Naming Convention
3. API Versioning Strategy
4. Authentication APIs
5. User APIs
6. Marketplace APIs
7. Shopping APIs
8. Order APIs
9. Wallet APIs
10. Escrow APIs
11. Payment APIs
12. Messaging APIs
13. Notification APIs
14. Review APIs
15. Affiliate APIs
16. Support APIs
17. Admin APIs
18. Analytics APIs
19. Webhook Architecture
20. WebSocket Events
21. Request Standards
22. Response Standards
23. Error Handling
24. Pagination Standards
25. Filtering Standards
26. Search Standards
27. Sorting Standards
28. File Upload Standards
29. Security Standards
30. Performance Standards
31. API Documentation Standards
32. Testing Strategy
33. API Acceptance Criteria
34. API Checklist
35. Final API Blueprint

---

## 1. API Philosophy

### REST Standards
The TSBL Marketplace API follows the principles of REST (Representational State Transfer) as defined by Roy Fielding. Every resource is identified by a URI, manipulated through standard HTTP verbs, and represented in JSON format. The API adheres to the JSON:API specification (jsonapi.org) for consistency, predictability, and interoperability.

### Consistency
- All endpoints follow uniform naming patterns and conventions.
- Consistent error payloads across all resources.
- Uniform pagination, filtering, sorting, and sparse fieldsets.
- Predictable HTTP status code usage.
- Consistent header requirements across all endpoints.

### Scalability
- Stateless design enables horizontal scaling.
- Caching headers (ETag, Cache-Control) reduce server load.
- Connection pooling with configurable pool sizes.
- Async-first architecture for non-blocking I/O.
- Cursor-based pagination for large dataset traversal.
- Rate limiting distributed via Redis.

### Maintainability
- Feature-based module organization mirrors backend domain modules.
- OpenAPI 3.1 specification as the single source of truth.
- Automated contract testing ensures backward compatibility.
- Deprecation headers in responses for sunset endpoints.
- Correlation IDs across all services for distributed tracing.

### Versioning Strategy
- The API uses URL-based versioning: /api/v1/, /api/v2/, etc.
- Major versions are released annually at most.
- A version is supported for a minimum of 12 months after the next version is released.
- Only two major versions are active at any time (current + previous).

### Backward Compatibility
- Adding new fields to responses is backward compatible.
- Adding new optional request parameters is backward compatible.
- Adding new endpoints is backward compatible.
- The following are BREAKING changes and require a new version:
  - Removing or renaming fields
  - Changing field types
  - Making optional fields required
  - Changing endpoint URLs
  - Changing HTTP verbs
  - Removing endpoints
  - Changing error codes

### Deprecation Policy
- Deprecated endpoints continue to work for 12 months after the deprecation announcement.
- Deprecation is communicated via the Sunset HTTP header.
- The Deprecation header indicates the deprecation date.
- Documentation marks deprecated endpoints prominently.
- Deprecation is announced via changelog, email, and API status page.

---

## 2. API Naming Convention

### Resource Naming
- Resources are named using plural nouns: /users, /products, /orders.
- Hyphens (-) separate multi-word resources: /product-categories, /license-keys.
- Lowercase only throughout the URI.
- No underscores in URI paths.

### Plural Resources
- All collection endpoints use plural nouns: GET /api/v1/users, POST /api/v1/products.
- Singleton resources (e.g., profile) use the resource name: GET /api/v1/profile.

### Nested Resources
- Nested resources follow parent-child relationships: /api/v1/users/{userId}/addresses.
- Maximum nesting depth: 2 levels (e.g., /orders/{orderId}/items/{itemId}).
- Deep nesting indicates a missing resource; create a top-level resource instead.

### Path Naming
Pattern: /api/v1/{resource}[/{resourceId}][/{subresource}[/{subresourceId}]]

Examples:
- GET /api/v1/products — List products
- GET /api/v1/products/{productId} — Get single product
- GET /api/v1/products/{productId}/reviews — List product reviews
- POST /api/v1/products/{productId}/reviews — Create review

### HTTP Verb Usage
| Verb | Purpose | Idempotent | Safe |
|------|---------|------------|------|
| GET | Retrieve resource(s) | Yes | Yes |
| POST | Create resource / action | No | No |
| PUT | Full update / replace | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

Actions that don't map to CRUD use POST with verb in the URL:
- POST /api/v1/auth/login
- POST /api/v1/orders/{orderId}/cancel
- POST /api/v1/payments/{paymentId}/refund

### URI Standards
- Protocol: HTTPS only (TLS 1.3 minimum).
- Base URL: https://api.tsbl.com/{version}
- No file extensions (no .json, no .xml).
- No query parameters for resource identification (use path parameters).
- Query parameters for filtering, sorting, pagination, and sparse fieldsets.

---

## 3. API Versioning Strategy

### URL Versioning
- Version is embedded in the URL path: https://api.tsbl.com/api/v1/...
- Version format: {major} (e.g., 1, 2).
- No minor or patch version in URL (semantic versioning is internal).

### Header Versioning (Future)
- Optional Accept-Version header for clients that prefer header-based versioning.
- Example: Accept-Version: ~1 (any 1.x), Accept-Version: 1.2 (specific).
- URL versioning takes precedence over header versioning.

### Migration Strategy
1. New version is developed on a separate branch with OpenAPI spec.
2. Both versions run concurrently with separate deployments.
3. Clients are given 12 months to migrate.
4. Traffic is gradually shifted: 10% ? 25% ? 50% ? 75% ? 100%.
5. Old version is deprecated after 12 months and eventually retired.

### Breaking Changes Policy
Changes requiring a new major version:
- Removal or rename of a field/property.
- Change in field type or format.
- Making a previously optional field required.
- Removing an endpoint or HTTP verb.
- Changing endpoint URL structure.
- Changing error response structure.
- Changing authentication/authorization mechanism.

Non-breaking changes:
- Adding new endpoints.
- Adding new optional fields to request/response.
- Adding new HTTP headers.
- Extending enum values.
- Changing error messages (not codes).
- Changing rate limits.

---

## 4. Authentication APIs

Base Path: /api/v1/auth

### POST /api/v1/auth/register
Create a new buyer account.

**Request:**
`json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123"
}
`

**Response (201):**
`json
{
  "data": {
    "user": { "id": "uuid", "email": "user@example.com", "username": "johndoe", "role": "buyer", "status": "pending", "is_verified": false, "created_at": "2026-07-02T12:00:00Z" },
    "tokens": { "access_token": "jwt...", "refresh_token": "jwt...", "token_type": "bearer", "expires_in": 1800 }
  }
}
`

**Errors:** 409 (email/username exists), 422 (validation).

### POST /api/v1/auth/login
Authenticate and receive JWT tokens.

**Request:**
`json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
`

**Response (200):** Same as register response.

**Errors:** 401 (invalid credentials), 403 (banned/locked), 423 (temporary locked).

### POST /api/v1/auth/logout
Invalidate the current session.

**Headers:** Authorization: Bearer {accessToken}

**Response (204):** No content.

### POST /api/v1/auth/refresh
Obtain a new access token using a refresh token.

**Request:**
`json
{
  "refresh_token": "jwt..."
}
`

**Response (200):**
`json
{
  "data": {
    "access_token": "jwt...",
    "refresh_token": "jwt...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
`

### POST /api/v1/auth/verify-email
Verify email address using token sent via email.

**Request:**
`json
{
  "token": "verification-token"
}
`

**Response (200):** { "message": "Email verified successfully" }

### POST /api/v1/auth/forgot-password
Request a password reset email.

**Request:**
`json
{
  "email": "user@example.com"
}
`

**Response (204):** Always returns 204 (prevential enumeration).

### POST /api/v1/auth/reset-password
Reset password using token from email.

**Request:**
`json
{
  "token": "reset-token",
  "password": "NewPass123",
  "confirm_password": "NewPass123"
}
`

**Response (204):** No content.

### POST /api/v1/auth/change-password
Change password for authenticated user.

**Headers:** Authorization: Bearer {accessToken}

**Request:**
`json
{
  "current_password": "OldPass123",
  "new_password": "NewPass456"
}
`

**Response (204):** No content.

### POST /api/v1/auth/mfa/enable
Enable two-factor authentication.

**Headers:** Authorization: Bearer {accessToken}

**Request:**
`json
{
  "mfa_type": "totp"
}
`

**Response (200):**
`json
{
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code_url": "otpauth://totp/TSBL:user@example.com?..."
  }
}
`

### POST /api/v1/auth/mfa/disable
Disable two-factor authentication.

**Headers:** Authorization: Bearer {accessToken}

**Request:**
`json
{
  "code": "123456"
}
`

**Response (204):** No content.

### POST /api/v1/auth/mfa/verify
Verify MFA code during login.

**Request:**
`json
{
  "mfa_token": "temp-token-from-login",
  "code": "123456"
}
`

**Response (200):** Returns full auth tokens.

---

## 5. User APIs

Base Path: /api/v1/users

### GET /api/v1/users/{userId}
Get user profile.
- **Roles:** Admin, Super Admin (any user), Seller/Buyer (own profile)
- **Response (200):** User object with profile details.

### PATCH /api/v1/users/{userId}
Update user profile.
- **Roles:** Self or Admin/Super Admin
- **Request:** Partial user fields (name, phone, locale, timezone)

### DELETE /api/v1/users/{userId}
Delete (soft) user account.
- **Roles:** Self or Super Admin
- **Precondition:** No active orders or pending disputes
- **Response (204)**

### GET /api/v1/users/{userId}/profile
Get extended profile (bio, store name, social links).
- **Roles:** Self or public profile for sellers

### PATCH /api/v1/users/{userId}/profile
Update extended profile.

### POST /api/v1/users/{userId}/avatar
Upload or update avatar.
- **Content-Type:** multipart/form-data
- **Max size:** 2 MB
- **Formats:** JPG, PNG, WebP
- **Response (200):** { "avatar_url": "https://cdn.tsbl.com/avatars/uuid.jpg" }

### GET /api/v1/users/{userId}/addresses
List user addresses.

### POST /api/v1/users/{userId}/addresses
Create a new address.
- **Request:** { "label": "Home", "street": "...", "city": "...", "state": "...", "country": "...", "postal_code": "...", "is_default": false }

### PATCH /api/v1/users/{userId}/addresses/{addressId}
Update an address.

### DELETE /api/v1/users/{userId}/addresses/{addressId}
Delete an address.

### GET /api/v1/users/{userId}/settings
Get user settings (notifications, privacy, preferences).

### PATCH /api/v1/users/{userId}/settings
Update user settings.

### POST /api/v1/users/{userId}/kyc
Submit KYC documents.
- **Content-Type:** multipart/form-data
- **Fields:** id_document (front), id_document_back, selfie, ddress_proof
- **Response (202):** Accepted for processing.

### GET /api/v1/users/{userId}/kyc/status
Get KYC verification status.
- **Response (200):** { "level": 1, "status": "pending", "expires_at": "..." }

### Seller-Specific Endpoints

### POST /api/v1/users/{userId}/become-seller
Apply for seller status.
- **Request:** KYC documents + seller agreement acceptance
- **Response (201):** { "application_id": "...", "status": "pending_review" }

### GET /api/v1/users/{userId}/seller/profile
Get seller public profile (store name, rating, response time, joined date).

### PATCH /api/v1/users/{userId}/seller/profile
Update seller store details (store name, description, policies).

### GET /api/v1/users/{userId}/seller/analytics
Get seller analytics dashboard data.
- **Query:** ?period=7d|30d|90d|1y
- **Response:** Summary metrics (sales, revenue, views, conversion).

### Admin-Specific Endpoints

### GET /api/v1/users
List all users (with filters).
- **Roles:** Admin, Super Admin
- **Query:** ?role=buyer|seller|admin&status=active|suspended&search=keyword&page=1&per_page=20

### POST /api/v1/users/{userId}/suspend
Suspend a user account.
- **Request:** { "reason": "...", "duration_days": 30 }
- **Response (200)**

### POST /api/v1/users/{userId}/unsuspend
Reinstate a suspended account.

### POST /api/v1/users/{userId}/verify
Manually verify a seller.
- **Request:** { "verification_level": 2, "notes": "..." }

---

## 6. Marketplace APIs

Base Path: /api/v1

### Categories

### GET /api/v1/categories
List all product categories (tree structure).
- **Response (200):** Nested category tree with { id, name, slug, icon, parent_id, children_count }

### GET /api/v1/categories/{categoryId}
Get category details.
- **Response (200):** { id, name, slug, description, icon, parent_id, children[], product_count }

### POST /api/v1/categories
Create a new category.
- **Roles:** Admin, Super Admin
- **Request:** { "name": "...", "slug": "...", "description": "...", "icon": "...", "parent_id": null }

### PATCH /api/v1/categories/{categoryId}
Update category.

### DELETE /api/v1/categories/{categoryId}
Delete category (soft, only if no products).

### GET /api/v1/categories/{categoryId}/subcategories
List direct subcategories.

### Products

### GET /api/v1/products
List/search products.
- **Query:** ?category_id=&search=&min_price=&max_price=&sort=best_selling&page=1&per_page=20
- **Response (200):** Paginated product list with { id, title, price, rating, sales_count, preview_images[], seller{id, name} }

### POST /api/v1/products
Create a new product listing.
- **Roles:** Seller, Admin
- **Request:** { "title": "...", "description": "...", "price": 29.99, "category_id": "...", "tags": ["..."] }
- **Response (201):** Product object.

### GET /api/v1/products/{productId}
Get product details.
- **Response (200):** Full product details with seller info, rating, reviews summary.

### PATCH /api/v1/products/{productId}
Update product.
- **Roles:** Owner seller or Admin
- **Note:** Price change > 20% triggers re-review.

### DELETE /api/v1/products/{productId}
Soft-delete product (archive).
- **Roles:** Owner seller or Admin
- **Precondition:** No active orders.

### POST /api/v1/products/{productId}/submit-for-review
Submit product for moderation review.
- **Response (200):** { "status": "pending_review" }

### POST /api/v1/products/{productId}/feature
Purchase featured placement.
- **Request:** { "duration_weeks": 1 }
- **Response (200):** { "featured_until": "..." }

### GET /api/v1/products/{productId}/images
List product images.

### POST /api/v1/products/{productId}/images
Upload product image.
- **Content-Type:** multipart/form-data
- **Max:** 5 images per product, 2 MB each.
- **Response (201):** { "id": "...", "url": "...", "is_primary": false }

### DELETE /api/v1/products/{productId}/images/{imageId}
Delete product image.

### PATCH /api/v1/products/{productId}/images/{imageId}
Set image as primary.

### GET /api/v1/products/{productId}/files
List product delivery files.

### POST /api/v1/products/{productId}/files
Upload product delivery file.
- **Max:** 5 GB.
- **Note:** File scanned for malware before delivery to buyers.

### GET /api/v1/products/{productId}/tags
Get tags for a product.

### POST /api/v1/products/{productId}/tags
Add tags to product.
- **Max:** 5 tags per product.

### GET /api/v1/inventory/{productId}
Get inventory status.
- **Response (200):** { "total": 100, "sold": 45, "remaining": 55, "threshold": 10 }

### PATCH /api/v1/inventory/{productId}
Update inventory (add license keys, set count).
- **Roles:** Owner seller, Admin

### POST /api/v1/inventory/{productId}/license-keys
Bulk upload license keys (CSV).
- **Response (202):** Processing accepted.

### Search & Discovery

### GET /api/v1/search
Full-text search across products.
- **Query:** ?q=keyword&category_id=&min_price=&max_price=&sort=relevance&page=1&per_page=20
- **Response (200):** Paginated results with { hits[], total, facets{ categories[], price_range{} } }

### GET /api/v1/search/autocomplete
Autocomplete suggestions.
- **Query:** ?q=partial&limit=10
- **Response (200):** { suggestions: [{ text, type: "product|category", result_count }] }

### GET /api/v1/products/featured
List featured products.
- **Query:** ?category_id=&limit=10
- **Response (200):** Array of featured products.

### GET /api/v1/products/trending
List trending products.
- **Query:** ?category_id=&limit=20
- **Response (200):** Array of trending products with trending score.

### GET /api/v1/recommendations
Get personalized product recommendations.
- **Headers:** Authorization: Bearer {token}
- **Query:** ?limit=10&based_on=history|similar|popular
- **Response (200):** Array of product recommendations.

---

## 7. Shopping APIs

Base Path: /api/v1

### Wishlist

### GET /api/v1/wishlist
List user's wishlist.
- **Headers:** Authorization: Bearer {token}

### POST /api/v1/wishlist
Add product to wishlist.
- **Request:** { "product_id": "uuid" }
- **Response (201)**

### DELETE /api/v1/wishlist/{productId}
Remove product from wishlist.

### Cart

### GET /api/v1/cart
Get current user's cart.
- **Headers:** Authorization: Bearer {token}
- **Response (200):** { items[], subtotal, discount, tax, total }

### POST /api/v1/cart/items
Add item to cart.
- **Request:** { "product_id": "uuid", "quantity": 1 }

### PATCH /api/v1/cart/items/{itemId}
Update cart item quantity.
- **Request:** { "quantity": 2 }

### DELETE /api/v1/cart/items/{itemId}
Remove item from cart.

### POST /api/v1/cart/coupon
Apply coupon to cart.
- **Request:** { "code": "SAVE20" }
- **Response (200):** Updated cart with discount.

### DELETE /api/v1/cart/coupon
Remove applied coupon.

### Checkout

### POST /api/v1/checkout
Initiate checkout process.
- **Headers:** Authorization: Bearer {token}
- **Request:** { "cart_id": "...", "address_id": "...", "payment_method_id": "...", "coupon_code": "optional" }
- **Response (200):** { "order_id": "...", "total": 49.99, "payment_intent": "...", "requires_action": false }

### GET /api/v1/checkout/{checkoutId}
Get checkout status.

### Coupons

### GET /api/v1/coupons
List coupons (admin: all, seller: own).

### POST /api/v1/coupons
Create a coupon.
- **Roles:** Admin, Seller
- **Request:** { "code": "SUMMER", "type": "percentage", "value": 20, "max_redemptions": 100, "per_user_limit": 1, "min_order_value": 10, "starts_at": "...", "ends_at": "...", "product_ids": [] }

### PATCH /api/v1/coupons/{couponId}
Update coupon.

### DELETE /api/v1/coupons/{couponId}
Delete coupon.

### Taxes

### GET /api/v1/tax-rates
List applicable tax rates.
- **Query:** ?country=BD&region=Dhaka

### Invoices

### GET /api/v1/invoices
List user invoices.
- **Roles:** Buyer (own), Seller (received), Admin (all)

### GET /api/v1/invoices/{invoiceId}
Get invoice details.
- **Response (200):** Invoice with line items, tax breakdown, payment info.

### GET /api/v1/invoices/{invoiceId}/download
Download invoice PDF.

---

## 8. Order APIs

Base Path: /api/v1/orders

### POST /api/v1/orders
Create an order from checkout.
- **Headers:** Authorization: Bearer {token}
- **Request:** { "checkout_id": "...", "payment_method_id": "..." }
- **Response (201):** { "id": "...", "status": "pending_payment", "total": 49.99, "items": [] }

### GET /api/v1/orders/{orderId}
Get order details.
- **Roles:** Buyer (own), Seller (involved), Admin, Support
- **Response (200):** Full order with items, status history, delivery info.

### GET /api/v1/orders
List user orders.
- **Query:** ?status=completed|pending&role=buyer|seller&page=1&per_page=20
- **Response (200):** Paginated order list.

### POST /api/v1/orders/{orderId}/cancel
Cancel an order.
- **Precondition:** Only PENDING_PAYMENT or PAID orders.

### POST /api/v1/orders/{orderId}/confirm-delivery
Buyer confirms delivery.
- **Response (200):** Order moves to COMPLETED, escrow released.

### GET /api/v1/orders/{orderId}/status
Get order status timeline.
- **Response (200):** { "current": "delivered", "history": [{ "status": "...", "timestamp": "...", "note": "..." }] }

### Digital Delivery

### GET /api/v1/orders/{orderId}/downloads
List downloadable files for the order.
- **Roles:** Buyer (own)
- **Response (200):** { items: [{ file_id, name, size, url, expires_at, downloads_remaining }] }

### GET /api/v1/orders/{orderId}/license-keys
List license keys for the order.
- **Roles:** Buyer (own)
- **Response (200):** { keys: [{ key, product_name, activated_at }] }

### POST /api/v1/orders/{orderId}/deliver
Seller marks order as delivered.
- **Roles:** Seller (own)
- **Request:** { "file_ids": ["..."] }
- **Response (200):** Order status ? DELIVERED.

### GET /api/v1/orders/{orderId}/invoice
Get invoice for the order.

---

## 9. Wallet APIs

Base Path: /api/v1/wallet

### GET /api/v1/wallet
Get wallet balance and summary.
- **Headers:** Authorization: Bearer {token}
- **Response (200):** { "available_balance": 1250.00, "pending_balance": 350.00, "total_earned": 5200.00, "total_withdrawn": 3600.00, "currency": "USD" }

### GET /api/v1/wallet/transactions
List wallet transactions.
- **Query:** ?type=credit|debit&status=completed|pending&from=&to=&page=1&per_page=50
- **Response (200):** Paginated transaction list with running balance.

### GET /api/v1/wallet/transactions/{transactionId}
Get transaction details.

### POST /api/v1/wallet/deposit
Deposit funds into wallet.
- **Roles:** Buyer, Seller
- **Request:** { "amount": 100.00, "payment_method_id": "..." }
- **Response (201):** { "deposit_id": "...", "amount": 100.00, "status": "pending", "payment_intent": "..." }

### POST /api/v1/wallet/withdraw
Request a withdrawal.
- **Roles:** Seller
- **Request:** { "amount": 500.00, "withdrawal_method_id": "...", "notes": "optional" }
- **Response (201):** { "withdrawal_id": "...", "amount": 500.00, "fee": 1.00, "status": "pending", "estimated_arrival": "2026-07-05" }

### GET /api/v1/wallet/withdrawals
List withdrawal history.
- **Query:** ?status=completed|pending|failed&page=1

### POST /api/v1/wallet/withdrawals/{withdrawalId}/cancel
Cancel a pending withdrawal (within 1 hour).

### GET /api/v1/wallet/withdrawal-methods
List saved withdrawal methods.
- **Response (200):** Array of methods (bank accounts, mobile wallets).

### POST /api/v1/wallet/withdrawal-methods
Add a withdrawal method.
- **Request:** { "type": "bank_account", "details": { "bank_name": "...", "account_number": "...", "routing_number": "...", "account_holder": "..." } }

### DELETE /api/v1/wallet/withdrawal-methods/{methodId}
Remove a withdrawal method.

### POST /api/v1/wallet/withdrawal-methods/{methodId}/verify
Initiate verification (micro-deposit or OTP).

### POST /api/v1/wallet/withdrawal-methods/{methodId}/verify/confirm
Confirm verification.
- **Request:** { "code": "12", "amount1": 0.12, "amount2": 0.45 } (micro-deposit) or { "otp": "123456" } (mobile wallet)

### GET /api/v1/wallet/commission
View commission earned (seller) or paid (buyer).
- **Query:** ?period=30d&page=1

### GET /api/v1/wallet/statement
Generate wallet statement PDF.
- **Query:** ?from=&to=&format=pdf

---

## 10. Escrow APIs

Base Path: /api/v1/escrow

### GET /api/v1/escrow/{orderId}
Get escrow status for an order.
- **Roles:** Buyer (own), Seller (own), Admin, Finance
- **Response (200):** { "order_id": "...", "status": "held|released|refunded", "amount": 49.99, "held_since": "...", "release_date": "...", "commission_deducted": 7.50 }

### POST /api/v1/escrow/{orderId}/release
Manually release escrow funds to seller.
- **Roles:** Admin, Finance (based on dispute resolution)
- **Request:** { "reason": "dispute resolved in seller favor" }
- **Response (200):** Funds released.

### POST /api/v1/escrow/{orderId}/refund
Refund escrow funds to buyer.
- **Roles:** Admin, Finance
- **Request:** { "reason": "dispute resolved in buyer favor", "amount": 49.99, "deduct_commission": false }
- **Response (200):** Funds refunded.

### GET /api/v1/escrow
List escrow records.
- **Roles:** Admin, Finance
- **Query:** ?status=held|released|refunded&page=1&per_page=50

### GET /api/v1/escrow/reconciliation
Get daily reconciliation report.
- **Roles:** Finance, Super Admin
- **Response (200):** { "date": "2026-07-02", "total_held": 125000.00, "total_released": 98000.00, "total_refunded": 5000.00, "discrepancy": 0.00, "balance": 22000.00 }

---

## 11. Payment APIs

Base Path: /api/v1/payments

### GET /api/v1/payments/methods
List saved payment methods for user.
- **Roles:** Buyer

### POST /api/v1/payments/methods
Add a payment method.
- **Request:** { "type": "card", "gateway_token": "pm_123456", "is_default": true }

### DELETE /api/v1/payments/methods/{methodId}
Remove a payment method.

### POST /api/v1/payments/intent
Create a payment intent.
- **Request:** { "order_id": "...", "payment_method_id": "...", "amount": 49.99, "currency": "USD" }
- **Response (201):** { "intent_id": "...", "client_secret": "...", "requires_action": false }

### POST /api/v1/payments/intent/{intentId}/confirm
Confirm a payment intent.
- **Request:** { "payment_method_id": "..." }

### GET /api/v1/payments/{paymentId}
Get payment details.
- **Roles:** Buyer (own), Seller (involved), Admin, Finance

### GET /api/v1/payments
List payment history.
- **Query:** ?status=succeeded|failed|refunded&page=1

### POST /api/v1/payments/{paymentId}/refund
Process a refund.
- **Roles:** Admin, Finance (or auto via dispute resolution)
- **Request:** { "amount": 49.99, "reason": "buyer request" }
- **Response (200):** Refund initiated.

### POST /api/v1/payments/{paymentId}/chargeback
Record a chargeback notification.
- **Roles:** Finance, Super Admin (usually triggered by webhook)
- **Response (200):** { "status": "disputed", "chargeback_id": "..." }

### Webhook Endpoint

### POST /api/v1/payments/webhook
Receive payment gateway webhooks.
- **Public endpoint** (validated by signature)
- **Body:** Raw gateway payload
- **Response (200):** { "received": true }

---

## 12. Messaging APIs

Base Path: /api/v1/messaging

### GET /api/v1/messaging/conversations
List active conversations for the user.
- **Headers:** Authorization: Bearer {token}
- **Query:** ?page=1&per_page=20
- **Response (200):** { data: [{ id, participant, last_message, unread_count, updated_at }], meta: { total, unread_total } }

### POST /api/v1/messaging/conversations
Start a new conversation.
- **Request:** { "participant_id": "...", "order_id": "optional", "initial_message": "Hello" }
- **Response (201):** Conversation object.

### GET /api/v1/messaging/conversations/{conversationId}
Get conversation details with participants.

### DELETE /api/v1/messaging/conversations/{conversationId}
Delete conversation (soft, user's visibility only).

### GET /api/v1/messaging/conversations/{conversationId}/messages
List messages in a conversation.
- **Query:** ?cursor=&limit=50
- **Response (200):** Cursor-paginated messages.

### POST /api/v1/messaging/conversations/{conversationId}/messages
Send a message.
- **Request:** { "content": "Thank you!", "attachment_ids": [] }
- **Response (201):** Message object.

### PATCH /api/v1/messaging/messages/{messageId}
Edit message (within 5 minutes of sending).

### DELETE /api/v1/messaging/messages/{messageId}
Delete message (soft, for self only).

### Attachments

### POST /api/v1/messaging/attachments
Upload a message attachment.
- **Content-Type:** multipart/form-data
- **Max:** 10 MB per file, 3 files per message.
- **Allowed:** images, PDF, ZIP, RAR.
- **Response (201):** { "id": "...", "url": "...", "name": "...", "size": 1048576 }

### Read Status

### POST /api/v1/messaging/conversations/{conversationId}/read
Mark conversation as read.
- **Response (204)**

### GET /api/v1/messaging/conversations/{conversationId}/participants
Get participant info and their last read timestamp.

### Typing Indicator

### POST /api/v1/messaging/conversations/{conversationId}/typing
Send typing indicator (WebSocket or HTTP fallback).
- **Request:** { "is_typing": true }
- **Response (204)**

### Presence

### GET /api/v1/messaging/presence/{userId}
Get user's online status.
- **Response (200):** { "user_id": "...", "status": "online|away|offline", "last_seen": "..." }

---

## 13. Notification APIs

Base Path: /api/v1/notifications

### GET /api/v1/notifications
List user notifications.
- **Query:** ?type=order|message|system|marketing&read=false&page=1&per_page=20
- **Response (200):** { data: [{ id, type, title, body, is_read, created_at, deep_link }], meta: { unread_count } }

### PATCH /api/v1/notifications/{notificationId}/read
Mark a notification as read.
- **Response (204)**

### POST /api/v1/notifications/read-all
Mark all notifications as read.
- **Response (204)**

### DELETE /api/v1/notifications/{notificationId}
Delete a notification.

### GET /api/v1/notifications/preferences
Get notification preferences.
- **Response (200):** { "email": { "orders": true, "marketing": false }, "push": { "messages": true, "system": true }, "in_app": { "all": true }, "dnd": { "enabled": false, "until": null } }

### PATCH /api/v1/notifications/preferences
Update notification preferences.

### POST /api/v1/notifications/test
Send a test notification (for debugging settings).
- **Request:** { "channel": "email|push|sms" }

### GET /api/v1/notifications/devices
List registered push notification devices.

### POST /api/v1/notifications/devices
Register a device for push notifications.
- **Request:** { "token": "fcm-token...", "platform": "ios|android|web", "device_id": "..." }

### DELETE /api/v1/notifications/devices/{deviceId}
Unregister a device.

---

## 14. Review APIs

Base Path: /api/v1

### Reviews

### GET /api/v1/products/{productId}/reviews
List product reviews.
- **Query:** ?sort=recent|highest|lowest&page=1&per_page=10
- **Response (200):** { data: [{ id, rating, content, author, verified_purchase, created_at, seller_response }], meta: { average_rating, distribution: {1:0, 2:0, 3:1, 4:5, 5:20} } }

### POST /api/v1/products/{productId}/reviews
Create a review.
- **Roles:** Buyer (verified purchase)
- **Request:** { "rating": 5, "content": "Excellent product! Highly recommend." }
- **Response (201)**

### PATCH /api/v1/products/{productId}/reviews/{reviewId}
Update own review (within 48 hours).
- **Request:** { "rating": 4, "content": "Updated review text" }

### DELETE /api/v1/products/{productId}/reviews/{reviewId}
Delete own review.

### POST /api/v1/products/{productId}/reviews/{reviewId}/report
Report a review for violation.
- **Request:** { "reason": "offensive|spam|fake" }

### POST /api/v1/products/{productId}/reviews/{reviewId}/respond
Seller responds to a review.
- **Roles:** Seller (product owner)
- **Request:** { "content": "Thank you for your feedback!" }
- **Response (201)**

### GET /api/v1/sellers/{sellerId}/reviews
List reviews for all products by a seller.
- **Query:** ?page=1&per_page=10

### Seller Reputation

### GET /api/v1/sellers/{sellerId}/reputation
Get seller reputation details.
- **Response (200):** { "score": 145, "tier": "excellent", "badges": ["top_rated", "fast_delivery"], "metrics": { "completed_orders": 350, "avg_rating": 4.7, "response_time_hours": 2.5, "completion_rate": 98.5, "dispute_rate": 1.2 } }

### Buyer Reputation

### GET /api/v1/buyers/{buyerId}/reputation
Get buyer reputation (visible to sellers).
- **Roles:** Seller
- **Response (200):** { "tier": "good", "total_orders": 25, "disputes_opened": 1, "refund_requests": 2 }

---

## 15. Affiliate APIs

Base Path: /api/v1/affiliate

### POST /api/v1/affiliate/register
Register as an affiliate.
- **Roles:** Any verified user
- **Response (201):** { "affiliate_id": "...", "referral_code": "john123", "status": "active" }

### GET /api/v1/affiliate/links
List referral links.
- **Response (200):** [{ "id": "...", "url": "https://tsbl.com/?ref=john123&product=uuid", "product": { "id, name" }, "clicks": 45, "conversions": 3, "earnings": 7.50 }]

### POST /api/v1/affiliate/links
Generate a referral link.
- **Request:** { "product_id": "optional-uuid" } (null for general marketplace link)
- **Response (201):** { "id": "...", "url": "https://tsbl.com/?ref=john123", "code": "john123" }

### DELETE /api/v1/affiliate/links/{linkId}
Deactivate a referral link.

### GET /api/v1/affiliate/earnings
Get affiliate earnings summary.
- **Query:** ?period=30d
- **Response (200):** { "total_earned": 450.00, "pending": 120.00, "paid_out": 330.00, "currency": "USD", "commission_rate": "5%" }

### GET /api/v1/affiliate/transactions
List affiliate commission transactions.
- **Query:** ?status=pending|paid&page=1

### GET /api/v1/affiliate/clicks
List referral click analytics.
- **Query:** ?from=&to=&group_by=day|product

### GET /api/v1/affiliate/conversions
List referral conversions (purchases).
- **Query:** ?status=pending|approved|reversed&page=1

### GET /api/v1/affiliate/reports
Generate affiliate performance report.
- **Query:** ?from=&to=&format=json|csv

---

## 16. Support APIs

Base Path: /api/v1/support

### Tickets

### POST /api/v1/support/tickets
Create a support ticket.
- **Roles:** All authenticated users
- **Request:** { "subject": "Cannot download my purchase", "category": "technical", "description": "I bought product X but...", "priority": "medium", "attachments": ["file_ids"] }
- **Response (201):** { "id": "TKT-12345", "status": "open", "priority": "medium", "created_at": "..." }

### GET /api/v1/support/tickets
List user's tickets.
- **Query:** ?status=open|resolved|closed&page=1&per_page=20

### GET /api/v1/support/tickets/{ticketId}
Get ticket details with messages.

### PATCH /api/v1/support/tickets/{ticketId}
Update ticket (user: close; agent: change status, assign, set priority).
- **Request:** { "status": "resolved" }
- **Roles:** User (own), Support Agent, Admin

### POST /api/v1/support/tickets/{ticketId}/replies
Add a reply to a ticket.
- **Request:** { "content": "I have tried reinstalling...", "attachments": [] }

### GET /api/v1/support/tickets/{ticketId}/replies
List replies for a ticket.

### GET /api/v1/support/tickets/{ticketId}/attachments
Ticket file attachments.

### POST /api/v1/support/attachments
Upload a file for a ticket.
- **Content-Type:** multipart/form-data
- **Max:** 20 MB total, 3 files.

### Agent Endpoints

### GET /api/v1/support/tickets/assigned
List tickets assigned to current agent.
- **Roles:** Support Agent, Admin

### PATCH /api/v1/support/tickets/{ticketId}/assign
Assign ticket to agent.
- **Roles:** Support Agent, Admin

### POST /api/v1/support/tickets/{ticketId}/escalate
Escalate ticket to senior agent or admin.
- **Request:** { "reason": "Requires admin??" }

### GET /api/v1/support/metrics
Get support team performance metrics.
- **Roles:** Admin, Super Admin
- **Response (200):** { "avg_response_time": "2.5h", "avg_resolution_time": "18h", "tickets_today": 45, "sla_breach_rate": 3.2, "csat_score": 4.2 }

---

## 17. Admin APIs

Base Path: /api/v1/admin

All endpoints in this section require Admin or Super Admin role and 2FA.

### Dashboard

### GET /api/v1/admin/dashboard
Get admin dashboard summary.
- **Response (200):** { "total_users": 50000, "total_sellers": 2500, "total_products": 150000, "total_orders_today": 1200, "revenue_today": 45000.00, "pending_verifications": 35, "open_disputes": 12, "flagged_users": 8, "system_health": { "uptime": "99.97%", "api_latency_ms": 145, "error_rate": 0.02 } }

### Users

### GET /api/v1/admin/users
List all users with advanced filters.
- **Query:** ?role=seller&status=suspended&kyc_level=1&created_from=&created_to=&search=&sort=created_at&page=1&per_page=50

### GET /api/v1/admin/users/{userId}
Get any user's full profile.

### POST /api/v1/admin/users/{userId}/impersonate
Generate impersonation token (read-only access).
- **Response (200):** { "impersonation_token": "jwt...", "expires_in": 900 }

### Products

### GET /api/v1/admin/products
List all products with filters.
- **Query:** ?status=pending_review|published|suspended&seller_id=&category_id=&search=&page=1

### POST /api/v1/admin/products/{productId}/approve
Approve a pending product.

### POST /api/v1/admin/products/{productId}/reject
Reject a product.
- **Request:** { "reason": "IP infringement detected" }

### POST /api/v1/admin/products/{productId}/suspend
Suspend a product.

### Orders

### GET /api/v1/admin/orders
List all orders with filters.
- **Query:** ?status=disputed|refunded&seller_id=&buyer_id=&date_from=&date_to=&page=1

### POST /api/v1/admin/orders/{orderId}/force-refund
Force refund an order.
- **Request:** { "reason": "...", "deduct_from_seller": true }

### Wallet / Payments / Escrow

### GET /api/v1/admin/wallets
List wallet accounts.
- **Query:** ?balance_min=1000&status=frozen&page=1

### POST /api/v1/admin/wallets/{walletId}/freeze
Freeze a wallet.

### POST /api/v1/admin/wallets/{walletId}/unfreeze
Unfreeze a wallet.

### GET /api/v1/admin/transactions
List all financial transactions.
- **Query:** ?type=withdrawal|deposit|commission|refund&page=1

### GET /api/v1/admin/withdrawals
List all withdrawal requests.
- **Query:** ?status=pending&page=1

### POST /api/v1/admin/withdrawals/{withdrawalId}/approve
Manually approve a withdrawal.

### POST /api/v1/admin/withdrawals/{withdrawalId}/reject
Reject a withdrawal.
- **Request:** { "reason": "Suspicious activity detected" }

### GET /api/v1/admin/escrow
List escrow records.
- **Query:** ?status=held>7d (overdue escrows)

### Analytics

### GET /api/v1/admin/analytics/overview
Platform analytics overview.

### GET /api/v1/admin/analytics/revenue
Revenue analytics.
- **Query:** ?period=this_month|last_month|custom&from=&to=&group_by=day|week|month

### GET /api/v1/admin/analytics/users
User growth analytics.

### GET /api/v1/admin/analytics/products
Product performance analytics.

### GET /api/v1/admin/reports/generate
Generate a custom report.
- **Request:** { "type": "financial", "from": "...", "to": "...", "format": "pdf|csv|xlsx", "columns": ["date", "revenue", "commission", "refunds"] }
- **Response (202):** { "report_id": "...", "status": "processing", "estimated_completion": "..." }

### GET /api/v1/admin/reports/{reportId}/download
Download a generated report.

### CMS

### GET /api/v1/admin/cms/pages
List CMS pages.

### POST /api/v1/admin/cms/pages
Create a CMS page.

### PATCH /api/v1/admin/cms/pages/{pageId}
Update CMS page.
- **Request:** { "title": "...", "slug": "...", "content": "markdown...", "published": true }

### GET /api/v1/admin/cms/banners
List homepage banners.

### POST /api/v1/admin/cms/banners
Create a banner.
- **Request:** { "title": "...", "image_url": "...", "link_url": "...", "position": 1, "active": true, "starts_at": "...", "ends_at": "..." }

### Settings

### GET /api/v1/admin/settings
Get platform settings.

### PATCH /api/v1/admin/settings
Update platform settings.
- **Roles:** Super Admin only
- **Request:** { "commission_rates": { "basic": 15, "pro": 10 }, "maintenance_mode": false, "feature_flags": {} }

### Audit Log

### GET /api/v1/admin/audit-logs
View system audit logs.
- **Query:** ?user_id=&action=&resource=&from=&to=&page=1
- **Response (200):** Paginated audit entries with before/after snapshots.

---

## 18. Analytics APIs

Base Path: /api/v1/analytics

### Dashboard (User-Specific)

### GET /api/v1/analytics/dashboard
Get personalized dashboard data.
- **Roles:** Buyer, Seller, Admin
- **Response varies by role.** Seller: sales, views, conversion. Buyer: order history, spending. Admin: platform metrics.

### GET /api/v1/analytics/sales
Sales analytics.
- **Roles:** Seller, Admin
- **Query:** ?period=7d|30d|90d|1y&group_by=day|week|month
- **Response (200):** { "total_sales": 450, "total_revenue": 12500.00, "avg_order_value": 27.78, "data_points": [{ "date": "2026-07-01", "sales": 15, "revenue": 420.00 }] }

### GET /api/v1/analytics/revenue
Revenue analytics with commission breakdown.
- **Roles:** Seller, Admin, Finance

### GET /api/v1/analytics/traffic
Traffic and page view analytics.
- **Roles:** Seller (own products), Admin (platform)
- **Response (200):** { "total_views": 15000, "unique_visitors": 3200, "top_sources": [{ "source": "google", "visits": 5000 }], "data_points": [] }

### GET /api/v1/analytics/conversion
Conversion rate analytics.
- **Roles:** Seller, Admin
- **Response (200):** { "overall_conversion_rate": 3.2, "by_source": [{ "source": "direct", "views": 5000, "conversions": 200, "rate": 4.0 }] }

### GET /api/v1/analytics/products/top
Top-performing products.
- **Query:** ?period=30d&limit=10&metric=sales|revenue|views

### GET /api/v1/analytics/reports/scheduled
List scheduled report deliveries.

### POST /api/v1/analytics/reports/scheduled
Schedule a recurring report.
- **Request:** { "type": "sales", "frequency": "weekly|monthly", "day": 1, "format": "pdf", "recipients": ["email@example.com"] }

### DELETE /api/v1/analytics/reports/scheduled/{reportId}
Cancel a scheduled report.

### GET /api/v1/analytics/export
Export analytics data.
- **Query:** ?type=sales&from=&to=&format=csv
- **Response (200):** CSV file download.

---

## 19. Webhook Architecture

### Overview
The platform sends webhook events to registered external URLs for real-time integration. Events are sent as HTTP POST requests with JSON payloads.

### Webhook Events

**Payment Events:**
- payment.succeeded — Payment captured successfully
- payment.failed — Payment failed
- payment.refunded — Refund processed
- payment.chargeback.created — Chargeback initiated

**Order Events:**
- order.created — New order placed
- order.paid — Order payment confirmed
- order.delivered — Seller marked as delivered
- order.completed — Buyer confirmed delivery
- order.cancelled — Order cancelled
- order.refunded — Order refunded

**Wallet Events:**
- wallet.deposit.completed — Deposit credited
- wallet.withdrawal.completed — Withdrawal processed
- wallet.withdrawal.failed — Withdrawal failed

**Escrow Events:**
- escrow.held — Funds locked in escrow
- escrow.released — Funds released to seller
- escrow.refunded — Funds returned to buyer

**Notification Events:**
- 
otification.bounced — Email bounced
- 
otification.clicked — Link clicked (if tracking enabled)

### Payload Structure
`json
{
  "event_id": "evt_uuid",
  "event_type": "order.completed",
  "created_at": "2026-07-02T12:00:00Z",
  "data": {
    "order_id": "uuid",
    "status": "completed",
    "total": 49.99
  }
}
`

### Registration

### POST /api/v1/webhooks
Register a webhook endpoint.
**Request:**
`json
{
  "url": "https://example.com/webhooks/tsbl",
  "events": ["order.*", "payment.succeeded"],
  "description": "Order notifications",
  "secret": "your-signing-secret"  // optional, auto-generated if omitted
}
`

### GET /api/v1/webhooks
List registered webhooks.

### PATCH /api/v1/webhooks/{webhookId}
Update webhook (URL, events, active status).

### DELETE /api/v1/webhooks/{webhookId}
Delete webhook.

### GET /api/v1/webhooks/{webhookId}/deliveries
List delivery attempts.
- **Query:** ?status=success|failed&page=1

### POST /api/v1/webhooks/{webhookId}/test
Send a test event.
- **Response (202):** { "delivery_id": "...", "status": "pending" }

### Retry Policy
- Initial attempt: immediate.
- Retry 1: 10 seconds.
- Retry 2: 1 minute.
- Retry 3: 10 minutes.
- Retry 4: 1 hour.
- Retry 5: 6 hours.
- Max attempts: 6. After final failure, event is marked as ailed and stored for 30 days.

### Security & Signature Verification
- Each webhook request includes a X-Webhook-Signature header.
- Signature = HMAC-SHA256(webhook_secret, request_body).
- Recipient must compute and compare signatures.
- Timestamp included in payload to prevent replay attacks (tolerance: 5 minutes).
- IP whitelist: webhooks originate from known IP ranges (published in documentation).
- TLS 1.3 enforced for all webhook deliveries.

---

## 20. WebSocket Events

### Connection
- **Endpoint:** wss://api.tsbl.com/ws
- **Authentication:** Token in query string: wss://api.tsbl.com/ws?token=jwt...
- **Protocol:** WebSocket (RFC 6455)
- **Fallback:** HTTP long-polling for environments without WebSocket support.

### Event Types

**Chat Events (user-to-user):**
- chat.message.new — New message received
- chat.message.read — Message read
- chat.typing — User is typing
- chat.presence — User online/offline status

**Notification Events:**
- 
otification.new — New notification received
- 
otification.updated — Notification read status changed

**Order Events:**
- order.status_changed — Order status updated
- order.delivered — Seller delivered
- order.dispute_opened — Dispute initiated

**Wallet Events:**
- wallet.balance_updated — Balance changed
- wallet.deposit.confirmed — Deposit confirmed
- wallet.withdrawal.status — Withdrawal status change

**Escrow Events:**
- escrow.released — Funds released
- escrow.disputed — Dispute affecting escrow

**Admin Dashboard (admin role only):**
- dmin.metrics.updated — Real-time platform metrics
- dmin.alert.new — New system alert

### Message Format
`json
{
  "event": "notification.new",
  "data": { "id": "...", "title": "...", "body": "..." },
  "sent_at": "2026-07-02T12:00:00Z"
}
`

### Subscription

### POST /api/v1/ws/subscriptions
Subscribe to specific event channels.
- **Request:** { "channels": ["order.*", "notification.new"] }
- **Response (200):** Subscribed.

### DELETE /api/v1/ws/subscriptions
Unsubscribe from channels.

### Rate Limits
- 60 messages per second per connection.
- 10 concurrent connections per user.
- Connections idle > 30 minutes are terminated.

---

## 21. Request Standards

### Base URL
https://api.tsbl.com/api/v1

### Required Headers
| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| Authorization | Bearer {jwt} | For authenticated endpoints | JWT access token |
| Content-Type | pplication/json | For POST/PUT/PATCH | Request body format |
| Accept | pplication/json | Yes | Response format |
| X-Request-Id | UUID | Recommended | Idempotency / tracing |
| X-Correlation-Id | UUID | Recommended | Distributed tracing |
| Accept-Language | en-US, n-BD | Optional | Locale for responses |
| X-Timezone | Asia/Dhaka | Optional | User timezone |
| X-Currency | USD, BDT | Optional | Preferred currency |
| Idempotency-Key | UUID | For payment/order creation | Prevents duplicate processing |

### Idempotency
- Idempotency keys are used for POST requests that create resources or process payments.
- Key is a UUID v4 sent in the Idempotency-Key header.
- Key is stored for 24 hours after the first request.
- Same key within 24 hours returns the original response (cached).
- Different body with same key returns 422 Unprocessable Entity.

### Locale Handling
- Locale is determined by: Accept-Language header > user profile setting > browser default > en-US.
- Dates and times are localized per locale.
- Error messages may be localized (if translations exist).

### Timezone
- All timestamps in API responses are in ISO 8601 format with UTC: 2026-07-02T12:00:00Z.
- The X-Timezone header is used for user-facing time displays only.
- All internal storage is UTC.

### Currency
- All monetary values are in the base currency (USD) unless overridden by X-Currency header.
- Amounts are represented as floats with 2 decimal places (JSON: 
umber).
- The currency field is included in all monetary responses.

---

## 22. Response Standards

### Success Response (Single Resource)
`json
{
  "data": {
    "id": "uuid",
    "type": "product",
    "attributes": { ... },
    "relationships": { ... }
  }
}
`

### Success Response (Collection)
`json
{
  "data": [
    {
      "id": "uuid",
      "type": "product",
      "attributes": { ... }
    }
  ],
  "meta": {
    "current_page": 1,
    "per_page": 20,
    "total": 150,
    "last_page": 8
  },
  "links": {
    "self": "https://api.tsbl.com/api/v1/products?page=1",
    "next": "https://api.tsbl.com/api/v1/products?page=2",
    "prev": null,
    "first": "https://api.tsbl.com/api/v1/products?page=1",
    "last": "https://api.tsbl.com/api/v1/products?page=8"
  }
}
`

### Error Response
`json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request was invalid.",
    "status": 422,
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Must be a valid email address"
      }
    ],
    "request_id": "req_uuid",
    "documentation_url": "https://docs.tsbl.com/api/errors#VALIDATION_ERROR"
  }
}
`

### Pagination Metadata
`json
{
  "meta": {
    "current_page": 1,
    "per_page": 20,
    "total": 150,
    "last_page": 8,
    "from": 1,
    "to": 20
  }
}
`

### Cursor Pagination
`json
{
  "data": [ ... ],
  "meta": {
    "has_more": true,
    "next_cursor": "eyJpZCI6MTUwfQ==",
    "prev_cursor": null
  },
  "links": {
    "next": "https://api.tsbl.com/api/v1/messages?cursor=eyJpZCI6MTUwfQ==",
    "prev": null
  }
}
`

### Links
- self: Current page URL.
- 
ext: Next page URL (null if last page).
- prev: Previous page URL (null if first page).
- irst: First page URL.
- last: Last page URL.

---

## 23. Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH |
| 201 | Created | Successful POST |
| 202 | Accepted | Async processing accepted |
| 204 | No Content | Successful DELETE, some POST |
| 301 | Moved Permanently | Resource relocated |
| 400 | Bad Request | Malformed syntax |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource does not exist |
| 405 | Method Not Allowed | Wrong HTTP verb |
| 409 | Conflict | Duplicate resource, state conflict |
| 410 | Gone | Resource permanently removed |
| 415 | Unsupported Media Type | Wrong Content-Type |
| 422 | Unprocessable Entity | Validation failure |
| 423 | Locked | Resource temporarily locked |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side failure |
| 502 | Bad Gateway | Upstream failure |
| 503 | Service Unavailable | Temporary overload/maintenance |

### Error Categories

**Validation Errors (422):**
`json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "status": 422,
    "details": [{ "field": "email", "code": "REQUIRED", "message": "Email is required" }]
  }
}
`

**Business Errors (409/422):**
`json
{
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Wallet balance is insufficient for this withdrawal",
    "status": 422
  }
}
`

**Authentication Errors (401):**
`json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Access token has expired. Please refresh.",
    "status": 401
  }
}
`

**Authorization Errors (403):**
`json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to perform this action",
    "status": 403
  }
}
`

**Rate Limit Errors (429):**
`json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "status": 429
  },
  "headers": {
    "X-RateLimit-Limit": 60,
    "X-RateLimit-Remaining": 0,
    "X-RateLimit-Reset": 1625126400,
    "Retry-After": 35
  }
}
`

**Internal Errors (500):**
`json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred. Our team has been notified.",
    "status": 500,
    "request_id": "req_uuid"
  }
}
`

---

## 24. Pagination Standards

### Cursor Pagination (Default for Real-Time Data)
Used for: messages, notifications, activity feeds.

**Request:**
GET /api/v1/messages?cursor=eyJpZCI6MTUwfQ==&limit=50

**Response:**
`json
{
  "data": [ ... ],
  "meta": {
    "has_more": true,
    "next_cursor": "base64-encoded-string",
    "prev_cursor": null
  }
}
`

**Rules:**
- Cursor is a base64-encoded opaque string.
- Cursor expires after 1 hour.
- limit defaults to 20, max 100.
- Cursor-based pages cannot be jumped to (no page number).
- Suitable for infinite scroll and real-time feeds.

### Offset Pagination (Default for Admin/Lists)
Used for: users, products, orders, transactions.

**Request:**
GET /api/v1/products?page=1&per_page=20

**Response:**
`json
{
  "data": [ ... ],
  "meta": {
    "current_page": 1,
    "per_page": 20,
    "total": 150,
    "last_page": 8,
    "from": 1,
    "to": 20
  },
  "links": {
    "self": "...",
    "next": "...",
    "prev": null,
    "first": "...",
    "last": "..."
  }
}
`

**Rules:**
- page starts at 1.
- per_page defaults to 20, max 100, min 1.
- 	otal and last_page are included for UI pagination controls.
- Offset pagination is NOT suitable for real-time feeds (new records shift pages).

### Infinite Scroll Pagination (Cursor-Based)
- Use cursor pagination for infinite scroll implementations.
- Load more button or scroll trigger fetches 
ext_cursor.
- No page numbers.

---

## 25. Filtering Standards

### Field Filters
Filter by exact field match. Multiple values use comma separation (OR logic).

**Syntax:** ?filter[field]=value1,value2

**Examples:**
- GET /api/v1/products?filter[status]=published
- GET /api/v1/orders?filter[status]=completed,cancelled
- GET /api/v1/users?filter[role]=seller,admin

### Range Filters
Filter by numeric or monetary ranges.

**Syntax:** ?filter[field][gte]=min&filter[field][lte]=max

**Operators:**
- gte — Greater than or equal (=)
- gt — Greater than (>)
- lte — Less than or equal (=)
- lt — Less than (<)

**Examples:**
- GET /api/v1/products?filter[price][gte]=10&filter[price][lte]=100
- GET /api/v1/products?filter[rating][gte]=4
- GET /api/v1/orders?filter[total][gte]=500

### Date Filters
Filter by date/time ranges.

**Syntax:** ?filter[field][gte]=2026-01-01&filter[field][lte]=2026-12-31

**Formats:**
- Date: YYYY-MM-DD
- Datetime: YYYY-MM-DDTHH:mm:ssZ (ISO 8601 UTC)

**Examples:**
- GET /api/v1/orders?filter[created_at][gte]=2026-06-01&filter[created_at][lte]=2026-06-30
- GET /api/v1/analytics/sales?filter[date][gte]=2026-01-01

### Boolean Filters
Filter by boolean fields.

**Syntax:** ?filter[field]=true|false

**Examples:**
- GET /api/v1/users?filter[is_verified]=true
- GET /api/v1/products?filter[is_featured]=true
- GET /api/v1/orders?filter[has_dispute]=true

### Compound Filters
Filters can be combined.

**Example:**
`
GET /api/v1/products
  ?filter[category_id]=electronics
  &filter[price][gte]=50
  &filter[price][lte]=500
  &filter[rating][gte]=4
  &filter[is_featured]=true
`

---

## 26. Search Standards

### Keyword Search
Simple keyword search across product titles and descriptions.

**Syntax:** ?search=keyword

**Example:** GET /api/v1/products?search=wordpress+theme

**Behavior:**
- Case-insensitive.
- Matches against: title, description, tags.
- Results ranked by relevance (TF-IDF based).
- Min query length: 2 characters.
- Max query length: 200 characters.
- Special characters are sanitized.

### Full-Text Search (Elasticsearch)
The primary search endpoint supports full-text search with advanced features.

**Endpoint:** GET /api/v1/search?q=keyword

**Features:**
- Stemming and lemmatization.
- Synonym expansion.
- Fuzzy matching (typo tolerance: 2 edits).
- Phrase matching (double quotes): "wordpress theme".
- Boolean operators: + (must include), - (must exclude), OR.
- Field-specific search: 	itle:theme, description:responsive.

**Faceting:**
`
GET /api/v1/search?q=theme&facets=categories,price_range,rating
`

**Response includes:**
`json
{
  "data": [...],
  "meta": {
    "total": 250,
    "facets": {
      "categories": [{ "id": "...", "name": "WordPress Themes", "count": 80 }],
      "price_range": { "min": 5, "max": 500 },
      "rating": { "1": 5, "2": 10, "3": 25, "4": 60, "5": 150 }
    }
  }
}
`

### Autocomplete
**Endpoint:** GET /api/v1/search/autocomplete?q=word&limit=10

**Response:**
`json
{
  "suggestions": [
    { "text": "wordpress themes", "type": "product", "count": 150 },
    { "text": "wordpress plugins", "type": "product", "count": 80 },
    { "text": "WordPress", "type": "category", "count": 230 }
  ]
}
`

**Behavior:**
- Returns results within 100ms for smooth UX.
- Results cached for 60 seconds.
- Prioritizes exact prefix matches.

### Suggestions
**Endpoint:** GET /api/v1/search/suggestions?q=wor

**Response:**
`json
{
  "query": "wor",
  "suggestions": ["wordpress", "wordpress theme", "wordpress plugin"],
  "products": [{ "id": "...", "title": "WordPress Theme X", "price": 29.99 }]
}
`

---

## 27. Sorting Standards

### Ascending / Descending
**Syntax:** ?sort=field (ascending) or ?sort=-field (descending)

**Examples:**
- GET /api/v1/products?sort=price — Cheapest first.
- GET /api/v1/products?sort=-price — Most expensive first.
- GET /api/v1/users?sort=-created_at — Newest first.
- GET /api/v1/orders?sort=-total — Highest value first.

### Sort Options by Resource

**Products:** elevance (default for search), price, -price, ating, -rating, sales, -sales, created_at, -created_at, 	itle, -title.

**Orders:** created_at, -created_at, 	otal, -total, status.

**Users:** created_at, -created_at, email, username, ole.

**Reviews:** created_at, -created_at, ating, -rating.

### Multi-Column Sorting
**Syntax:** ?sort=field1,-field2

**Example:** GET /api/v1/products?sort=-rating,price

Sorts by rating descending, then by price ascending within the same rating.

### Default Sort
- Search results: elevance (a computed score based on keyword matching + ranking factors).
- Product listings: -created_at (newest first).
- Orders: -created_at (most recent first).
- Users (admin): -created_at (newest first).

---

## 28. File Upload Standards

### Supported File Types

| Usage | Allowed Types | Max Size | Max Count |
|-------|---------------|----------|-----------|
| Product Images | JPG, PNG, WebP | 2 MB each | 5 per product |
| Product Files | ZIP, RAR, 7z, PDF, any | 5 GB | 10 per product |
| Avatar | JPG, PNG, WebP | 2 MB | 1 |
| KYC Documents | JPG, PNG, PDF | 10 MB | 5 per request |
| License Keys (bulk) | CSV, TXT, XLSX | 5 MB | 1 per upload |
| Attachments (messaging) | JPG, PNG, PDF, ZIP, RAR | 10 MB | 3 per message |
| Attachments (support) | JPG, PNG, PDF, ZIP, RAR, DOC | 20 MB total | 5 per ticket |
| Banner Images | JPG, PNG, WebP | 5 MB | 10 per campaign |

### Upload Flow
1. Client requests a presigned upload URL:
   - POST /api/v1/uploads/presigned
   - Request: { "file_name": "image.jpg", "file_size": 1048576, "mime_type": "image/jpeg", "purpose": "product_image" }
   - Response: { "upload_url": "https://cdn.tsbl.com/presigned/...", "file_id": "uuid", "expires_in": 3600 }
2. Client uploads directly to the CDN/storage using the presigned URL.
3. Client notifies the API: POST /api/v1/uploads/{fileId}/complete
4. Server triggers virus scan (for product files) or image optimization (for images).
5. File is available for use once processed.

### Virus Scan
- All uploaded files are scanned for malware.
- Scan is performed asynchronously for files > 100 MB.
- Files with threats detected are quarantined and flagged.
- Product files must pass scan before delivery to buyers.
- Scan results available via GET /api/v1/uploads/{fileId}/scan-status.

### Image Optimization
- Images are automatically optimized: WebP conversion, compression (85% quality), resizing.
- Thumbnails generated: 150×150, 300×300, 800×800.
- Original is preserved for download.
- EXIF data stripped for privacy.

### CDN
- All uploaded files are served via CDN (https://cdn.tsbl.com/).
- CDN caches public files (images) for 24 hours.
- Private files (delivery files, KYC docs) use signed URLs with expiration.
- CDN purging available via admin API.

---

## 29. Security Standards

### JWT (JSON Web Tokens)
- Algorithm: HS256 (HMAC-SHA256).
- Access token expiry: 30 minutes.
- Refresh token expiry: 7 days.
- Payload includes: sub (user ID), ole, iat, exp, 	ype (access/refresh), jti (unique token ID).
- Tokens are stateless (no server-side session storage).
- Secret key rotated every 90 days.

### Refresh Token Flow
1. Client sends access token + refresh token.
2. When access token expires, client calls POST /api/v1/auth/refresh.
3. Server validates refresh token ? issues new access + refresh token pair.
4. Old refresh token is invalidated (rotation).
5. If refresh token is expired or invalid, client must re-login.

### RBAC (Role-Based Access Control)

| Role | Description |
|------|-------------|
| guest | Unauthenticated, read-only access |
| uyer | Can purchase, review, create tickets |
| seller | Buyer permissions + list products, manage sales |
| moderator | Review products, flag content, assist disputes |
| support_agent | Manage support tickets, assist disputes |
| inance_manager | Access financial data, approve withdrawals |
| dmin | Full access except system settings |
| super_admin | Complete system access |

### Permission Matrix
Permissions are checked at the middleware level before reaching the controller.

| Resource | Guest | Buyer | Seller | Moderator | Support | Finance | Admin | Super Admin |
|----------|-------|-------|--------|-----------|---------|---------|-------|-------------|
| Public products | R | R | R | R | R | R | R | R |
| Own profile | - | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD |
| All users | - | - | - | R | R | R | R | CRUD |
| Products (own) | - | - | CRUD | - | - | - | - | - |
| Products (any) | - | - | - | RUD | R | R | CRUD | CRUD |
| Orders (own) | - | R | R | - | - | - | - | - |
| Orders (any) | - | - | - | R | R | R | CRUD | CRUD |
| Payments | - | - | - | - | - | CRUD | CRUD | CRUD |
| Wallet (own) | - | R | CRUD | - | - | - | - | - |
| Wallet (any) | - | - | - | - | - | CRUD | CRUD | CRUD |
| Escrow | - | - | - | - | - | CRUD | CRUD | CRUD |
| Disputes | - | own | own | CRUD | CRUD | - | CRUD | CRUD |
| Support tickets | - | own | own | - | CRUD | - | CRUD | CRUD |
| Reviews | R | CRUD | R | CRUD | - | - | CRUD | CRUD |
| Analytics (own) | - | R | R | R | R | R | R | R |
| Analytics (all) | - | - | - | - | - | R | R | R |
| CMS | - | - | - | - | - | - | CRUD | CRUD |
| Settings | - | - | - | - | - | - | - | CRUD |
| Audit logs | - | - | - | R | R | R | R | R |

(R = Read, C = Create, U = Update, D = Delete)

### Rate Limiting
- Distributed rate limiting via Redis.
- Per-IP and per-user limits.

| Tier | Public Endpoints | Authenticated | Admin | Payment |
|------|-----------------|---------------|-------|---------|
| Rate | 30 req/min | 60 req/min | 120 req/min | 10 req/min |
| Burst | 60 req/min | 120 req/min | 240 req/min | 20 req/min |

Headers included in responses:
- X-RateLimit-Limit: Max requests per window.
- X-RateLimit-Remaining: Remaining requests.
- X-RateLimit-Reset: Unix timestamp when the window resets.
- Retry-After: Seconds to wait (when limit exceeded).

### IP Whitelist
- Admin console accessible only from whitelisted IP ranges.
- Webhook delivery from known IP ranges.
- Super Admin actions require secondary approval from a second IP.

### API Keys (Future)
- For third-party integrations (OAuth 2.0 client credentials flow).
- API keys scoped to specific permissions.
- Keys can be rotated, revoked, and have expiration dates.

### OAuth Ready (Future)
- OAuth 2.0 authorization server for third-party apps.
- Supported grants: Authorization Code, Client Credentials, Refresh Token.
- PKCE required for public clients.

### Encryption
- All data in transit: TLS 1.3.
- All data at rest: AES-256.
- Secrets in environment variables or secrets manager (HashiCorp Vault / AWS Secrets Manager).
- Database columns with PII encrypted at column level.
- Payment card data: never stored (PCI-DSS tokenization).

---

## 30. Performance Standards

### Caching Strategy

**Application Cache (Redis):**
- Product detail pages: 5 minutes (TTL).
- Category trees: 1 hour.
- User profiles: 2 minutes.
- Search results: 30 seconds.
- Configuration settings: 1 hour.
- Session data: in-memory (JWT stateless).

**HTTP Cache:**
- Cache-Control headers on GET responses.
- Public resources (images, product data): public, max-age=300.
- Private resources (user-specific): private, no-cache.
- ETag headers for conditional requests.
- Last-Modified headers for time-based caching.

**CDN Cache:**
- Static assets: 1 year (fingerprinted URLs).
- Product images: 24 hours.
- Category images: 7 days.
- Cache purging via admin API.

### Compression
- All responses compressed with Brotli (preferred) or gzip.
- Minimum size for compression: 1 KB.
- Content-Encoding header indicates compression method.
- Accept-Encoding: r, gzip, identity.

### Streaming
- Large file downloads use chunked transfer encoding.
- Video streaming: HTTP range requests for partial content.
- Server-Sent Events (SSE) for real-time dashboard updates.
- Response streaming for large report generation.

### Batch Requests (GraphQL Future)
- Combine multiple requests into a single POST.
- Request: { "requests": [{ "method": "GET", "path": "/products" }, { "method": "GET", "path": "/users/me" }] }
- Response: { "responses": [{ "status": 200, "body": {...}, "headers": {...} }] }

### Connection Pooling
- Database: SQLAlchemy connection pool (min 10, max 50).
- Redis: Connection pool (min 5, max 20).
- HTTP client: Keep-alive connections with pooling.
- Pool exhaustion: Queued with configurable timeout.

### Performance SLAs

| Endpoint | P50 | P95 | P99 |
|----------|-----|-----|-----|
| Product listing | 200ms | 500ms | 1s |
| Product detail | 150ms | 400ms | 800ms |
| Search | 300ms | 800ms | 1.5s |
| Checkout | 500ms | 1.5s | 3s |
| Order creation | 300ms | 800ms | 1.5s |
| Auth (login) | 500ms | 1s | 2s |
| Webhook delivery | 1s | 3s | 5s |
| File download | 2s | 5s | 10s |
| Admin report | 3s | 10s | 30s |

---

## 31. API Documentation Standards

### OpenAPI 3.1
- The API is documented using the OpenAPI 3.1 specification.
- Single source of truth: openapi.yaml in the repository root.
- All endpoints, schemas, parameters, and responses are defined.
- Every endpoint includes at least one request and response example.
- Common parameters are defined as reusable components.

### Documentation Structure
- openapi.yaml: Complete API specification.
- docs/api/: Markdown reference for human-readable documentation.
- docs/api/changelog.md: API changelog with breaking/non-breaking changes.
- docs/api/errors.md: Comprehensive error code reference.

### Interactive Documentation
- Swagger UI: https://api.tsbl.com/docs
- ReDoc: https://api.tsbl.com/redoc
- Both are auto-generated from the OpenAPI spec.
- Authentication: "Authorize" button to enter JWT token for testing.

### Schema Naming
- Request schemas: {Resource}{Action}Request (e.g., CreateProductRequest).
- Response schemas: {Resource}Response (e.g., ProductResponse).
- List responses: {Resource}ListResponse.
- Error schema: ApiError.
- All schemas include description and example.

### Documentation Best Practices
- Every endpoint includes a summary (brief) and description (detailed).
- Every parameter includes description, equired, 	ype, and example.
- Every response includes description and content.
- Error responses are documented with status codes and schemas.
- Authentication requirements are specified per endpoint.
- Rate limit information is included in endpoint descriptions.

---

## 32. Testing Strategy

### Unit Testing
- Test individual endpoint logic (request validation, response formatting).
- Mock external dependencies (database, cache, third-party services).
- Coverage target: 90%+ for core business logic.
- Framework: pytest (Python), Jest (TypeScript).
- Run on every commit in CI pipeline.

### Integration Testing
- Test real API calls against a test database.
- Test full request ? response cycle including middleware (auth, rate limit).
- Test database interactions (CRUD, transactions, unique constraints).
- Test external service integrations with test sandboxes (Stripe test mode, etc.).
- Coverage target: 80%+ for API endpoints.
- Run on every PR in CI pipeline.

### Contract Testing
- Provider contract tests (backend): Verify OpenAPI spec matches actual behavior.
- Consumer contract tests (frontend/mobile): Verify client expectations.
- Tool: Pact or Dredd.
- Contract tests run in CI and prevent breaking changes from being merged.

### Load Testing
- Simulate production traffic patterns.
- Tools: k6, Locust, or Artillery.
- Scenarios:
  - Product browsing (300 concurrent users).
  - Search (100 concurrent queries/sec).
  - Checkout flow (50 concurrent purchases/min).
  - Authentication (100 login attempts/sec).
  - Mixed workload (realistic user behavior).
- Targets: P95 response times under SLA, zero errors under 2× expected load.
- Run before every major release.

### Security Testing
- Automated security scanning in CI (SAST, DAST).
- Dependency vulnerability scanning (Snyk, Dependabot).
- API fuzzing (invalid inputs, boundary testing).
- Authentication/authorization testing (token manipulation, privilege escalation).
- Rate limiting bypass attempts.
- SQL injection and XSS testing on search/input endpoints.
- Annual third-party penetration test.

---

## 33. API Acceptance Criteria

### Definition of Done per API Group

**Authentication APIs:**
- [ ] User can register, login, logout, and refresh tokens.
- [ ] Token expiry and refresh cycle works correctly.
- [ ] Password reset flows work end-to-end.
- [ ] MFA enable/disable flows work.
- [ ] Rate limiting on login endpoint (5 attempts/15 min).
- [ ] All error scenarios return correct status codes and messages.

**User APIs:**
- [ ] User CRUD operations work with correct RBAC enforcement.
- [ ] Profile, avatar, address, settings management work.
- [ ] KYC document upload and status check work.
- [ ] Seller application and verification flows work.
- [ ] Admin user management (list, filter, suspend) works.

**Marketplace APIs:**
- [ ] Category tree CRUD works.
- [ ] Product CRUD with image upload works.
- [ ] Product search with full-text, filters, facets works.
- [ ] Autocomplete returns results within 100ms.
- [ ] Featured and trending product lists are correct.
- [ ] Inventory tracking works with license key pool.

**Shopping APIs:**
- [ ] Wishlist add/remove/list works.
- [ ] Cart operations (add, update, remove, coupon) work.
- [ ] Checkout flow creates order correctly.
- [ ] Coupon validation and limits enforced.
- [ ] Invoice generation and download work.

**Order APIs:**
- [ ] Order creation from checkout works.
- [ ] Order status transitions follow lifecycle.
- [ ] Digital delivery files and license keys accessible.
- [ ] Order history with filters and pagination works.
- [ ] Cancel/refund flows work correctly.

**Wallet APIs:**
- [ ] Balance and transaction history work.
- [ ] Deposit flow creates payment intent.
- [ ] Withdrawal request, processing, and limits work.
- [ ] Withdrawal method add/verify/delete works.

**Escrow APIs:**
- [ ] Escrow status tracking works per order.
- [ ] Release and refund flows update balances correctly.
- [ ] Reconciliation report balances correctly.

**Payment APIs:**
- [ ] Payment method add/remove works.
- [ ] Payment intent creation and confirmation work.
- [ ] Webhook handling is idempotent and secure.
- [ ] Refund and chargeback flows work.

**Messaging APIs:**
- [ ] Conversation create, list, delete works.
- [ ] Message send, edit, delete within constraints works.
- [ ] Read status and typing indicator work.
- [ ] Attachment upload and delivery works.

**Notification APIs:**
- [ ] User receives notifications for subscribed events.
- [ ] Preference management works (enable/disable channels).
- [ ] Push device registration works.
- [ ] Read/mark-all/delete operations work.

**Review APIs:**
- [ ] Create, read, update, delete reviews works.
- [ ] Seller response works.
- [ ] Rating calculation is accurate.
- [ ] Report review flow works.

**Affiliate APIs:**
- [ ] Registration and link generation works.
- [ ] Click tracking and conversion attribution works.
- [ ] Commission calculation and payout tracking works.

**Support APIs:**
- [ ] Ticket CRUD works for users and agents.
- [ ] Reply and attachment flows work.
- [ ] Assignment, escalation, and priority work.
- [ ] SLA monitoring works.

**Admin APIs:**
- [ ] Dashboard returns correct summary data.
- [ ] User, product, order management works.
- [ ] Financial operations (freeze wallet, approve withdrawal) work.
- [ ] Analytics and report generation work.
- [ ] CMS page and banner management works.
- [ ] Settings update works (Super Admin only).
- [ ] Audit log query with filters works.

**Analytics APIs:**
- [ ] Dashboard data varies by role correctly.
- [ ] Sales, revenue, traffic, conversion data is accurate.
- [ ] Export (CSV) works correctly.
- [ ] Scheduled report delivery works.

**Webhooks:**
- [ ] Registration, update, delete of webhooks works.
- [ ] Events are delivered with correct payload.
- [ ] Retry policy works (6 attempts with backoff).
- [ ] Signature verification prevents tampering.
- [ ] Delivery log and test functionality work.

---

## 34. API Checklist

### Enterprise API Review Checklist

**Design Review:**
- [ ] Endpoint follows REST naming conventions (plural nouns, consistent verbs).
- [ ] URL hierarchy is logical (max 2 levels deep).
- [ ] HTTP verbs used correctly (GET = safe, POST = create, PATCH = update, DELETE = delete).
- [ ] Query parameters for filtering/sorting/pagination (not path parameters).
- [ ] Request/response schemas follow JSON:API convention.
- [ ] Response includes data, meta, and links wrapper.
- [ ] Error responses follow consistent structure.
- [ ] Pagination implemented (cursor for real-time, offset for lists).

**Security Review:**
- [ ] Authentication required for non-public endpoints.
- [ ] RBAC enforced at endpoint level.
- [ ] Rate limiting implemented and configured.
- [ ] Idempotency support for mutation endpoints.
- [ ] Input validation (length, type, format, range).
- [ ] No sensitive data exposed in responses.
- [ ] CORS configured correctly (specific origins, not wildcard for production).
- [ ] SQL injection prevention (parameterized queries, ORM).
- [ ] XSS prevention (output encoding).
- [ ] HTTPS enforced (TLS 1.3).
- [ ] Webhook signature verification implemented.

**Performance Review:**
- [ ] Caching strategy defined (ETag, Cache-Control).
- [ ] Compression enabled (Brotli/gzip).
- [ ] N+1 query prevention (eager loading, includes).
- [ ] Pagination defaults and maximums configured.
- [ ] Sparse fieldsets supported (optional).
- [ ] Response size optimized (no unnecessary fields).
- [ ] Database queries optimized (indexes confirmed).
- [ ] Load testing results meet SLAs.

**Documentation Review:**
- [ ] OpenAPI spec complete and valid.
- [ ] All endpoints documented with request/response examples.
- [ ] All error codes documented.
- [ ] Authentication flow documented.
- [ ] Rate limit information included.
- [ ] Changelog updated.
- [ ] Deprecation notices added (if applicable).

**Testing Review:**
- [ ] Unit tests covering business logic (90%+ coverage).
- [ ] Integration tests covering endpoint flows.
- [ ] Contract tests matching OpenAPI spec.
- [ ] Load tests confirming SLA adherence.
- [ ] Security tests (penetration, fuzzing, dependency scan).

**Operational Review:**
- [ ] Monitoring and alerting configured.
- [ ] Logging with correlation IDs.
- [ ] Graceful degradation for downstream failures.
- [ ] Timeout and retry configurations set.
- [ ] Rate limit headers returned.
- [ ] Health check endpoint (GET /api/v1/health).
- [ ] Version endpoint (GET /api/v1/version).

---

## 35. Final API Blueprint

### API Overview

`
Base URL: https://api.tsbl.com/api/v1
Protocol: HTTPS (TLS 1.3)
Format: JSON (JSON:API compliant)
Auth: JWT Bearer Token (access + refresh)
Versioning: URL-based (/api/v1, /api/v2)
Rate Limiting: Redis-based, tiered limits
Documentation: Swagger UI / ReDoc
`

### Module Map

`
api/v1/
+-- auth/              # Authentication & Authorization
+-- users/             # User management & profiles
+-- categories/        # Product categories
+-- products/          # Product listings & inventory
+-- search/            # Full-text search & autocomplete
+-- cart/              # Shopping cart
+-- checkout/          # Checkout & payment intent
+-- orders/            # Order management
+-- wishlist/          # Buyer wishlist
+-- coupons/           # Discount coupons
+-- taxes/             # Tax rate lookup
+-- invoices/          # Order invoices
+-- wallet/            # Digital wallet
+-- escrow/            # Escrow management
+-- payments/          # Payment methods & history
+-- messaging/         # Conversations & messages
+-- notifications/     # User notifications & preferences
+-- reviews/           # Product reviews & ratings
+-- affiliate/         # Affiliate program
+-- support/           # Support tickets
+-- admin/             # Admin operations
+-- analytics/         # Analytics & reports
+-- webhooks/          # Webhook management
+-- uploads/           # File upload presigned URLs
+-- health            # Health check
`

### Endpoint Count Summary

| Module | Endpoints |
|--------|-----------|
| Authentication | 10 |
| Users | 18 |
| Marketplace (categories, products, inventory, search) | 25 |
| Shopping (wishlist, cart, checkout, coupons, invoices) | 14 |
| Orders | 10 |
| Wallet | 15 |
| Escrow | 5 |
| Payments | 10 |
| Messaging | 12 |
| Notifications | 8 |
| Reviews | 9 |
| Affiliate | 9 |
| Support | 9 |
| Admin | 30 |
| Analytics | 8 |
| Webhooks | 7 |
| Uploads | 3 |
| Health/Version | 2 |
| **Total** | **~204 endpoints** |

### Request Flow

`
Client ? CDN ? Load Balancer ? API Gateway ? Rate Limiter ? Auth Middleware ? RBAC Check ? Controller ? Service Layer ? Repository ? Database/Cache

                    ?                                   ?
               Cache Layer                        External Services
             (Redis/CDN)                    (Stripe, PayPal, Email, SMS)
`

### Error Code Registry

| Code | HTTP | Description |
|------|------|-------------|
| VALIDATION_ERROR | 422 | Request body failed validation |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| TOKEN_EXPIRED | 401 | Access token has expired |
| TOKEN_INVALID | 401 | Token is malformed or revoked |
| FORBIDDEN | 403 | Insufficient permissions |
| RESOURCE_NOT_FOUND | 404 | Requested resource does not exist |
| CONFLICT | 409 | Resource already exists (duplicate) |
| STATE_CONFLICT | 409 | Resource is in wrong state for action |
| INSUFFICIENT_BALANCE | 422 | Wallet balance too low |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| ACCOUNT_LOCKED | 423 | Account temporarily locked |
| ACCOUNT_SUSPENDED | 403 | Account is suspended |
| INVALID_COUPON | 422 | Coupon code is invalid or expired |
| INSUFFICIENT_INVENTORY | 409 | Product is out of stock |
| PAYMENT_FAILED | 402 | Payment processing failed |
| INTERNAL_ERROR | 500 | Unexpected server error |
| SERVICE_UNAVAILABLE | 503 | Temporary service disruption |

### Response Time SLAs

`
   ____ Authentication: P50 500ms | P95 1s | P99 2s
  |    Product Listing:  P50 200ms | P95 500ms | P99 1s
  |    Search:           P50 300ms | P95 800ms | P99 1.5s
  |    Checkout:         P50 500ms | P95 1.5s | P99 3s
  |    Messaging:        P50 100ms | P95 300ms | P99 500ms
 /     Webhook:          P50 1s    | P95 3s   | P99 5s
`

---

*End of Document — API Architecture & Specification v1.0.0*
