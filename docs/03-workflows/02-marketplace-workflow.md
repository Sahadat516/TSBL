# TRUE STAR BD LIMITED — Marketplace Workflows

---

**Document Version:** 1.0  
**Date:** 2026-07-01  
**Author:** Principal Software Architect  
**Status:** Draft for Review  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Product Discovery & Search Flow](#2-product-discovery--search-flow)
3. [Add to Cart & Checkout Flow](#3-add-to-cart--checkout-flow)
4. [Digital Delivery & Fulfillment Flow](#4-digital-delivery--fulfillment-flow)
5. [Review & Rating Flow](#5-review--rating-flow)
6. [Refund & Dispute Flow](#6-refund--dispute-flow)
7. [Seller Payout & Commission Flow](#7-seller-payout--commission-flow)
8. [Coupon & Discount Application Flow](#8-coupon--discount-application-flow)
9. [Affiliate Tracking & Payout Flow](#9-affiliate-tracking--payout-flow)

---

## 1. Introduction

### 1.1 Purpose

This document describes the detailed marketplace workflows for the TRUE STAR BD LIMITED (TSBL) digital marketplace. Each workflow includes swimlane descriptions, trigger events, system actions, user actions, API calls, state transitions, success/failure paths, and rollback procedures. These workflows are intended for solution architects, developers, QA engineers, and technical project managers.

### 1.2 Swimlane Notation

Each workflow uses a **text-based swimlane diagram** where lanes represent actors/systems and columns represent sequential steps:

```
Lane Name      | Step 1       | Step 2       | Step 3       |
---------------|--------------|--------------|--------------|
Buyer          | Action A     | —            | Action C     |
System         | —            | Action B     | —            |
```

### 1.3 State Transition Notation

```
[Current State] --(Event)--> [Next State]
```

### 1.4 API Call Notation

```
[Method] /api/v1/{resource}
Headers: {key: value}
Body: { JSON payload }
Response: { HTTP status, JSON body }
```

---

## 2. Product Discovery & Search Flow

### 2.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|
Buyer (UI)        | Enters query    | Sees suggestions  | Submits search   | Applies filters   | Views results    | Clicks product   |
Browser (Client)  | Debounce 300ms  | GET /suggestions  | GET /search      | Updates URL params| Renders results  | Navigate to PDP  |
CDN / Edge        | —               | Cache lookup      | Cache lookup     | Cache bust        | Serve static     | Serve product    |
Search Service    | —               | Return suggestions| Execute query    | Re-rank           | —                | —                |
Index (ES/Solr)   | —               | Prefix search     | Full-text search | Filtered query    | —                | —                |
Database          | —               | —                 | —                | —                 | Log impression   | —                |
```

### 2.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `search.query_submitted` | Buyer typing in search bar | `{ query: string, page: number, filters: object }` |
| `search.filter_changed` | Buyer toggling filter controls | `{ filter_name: string, value: any }` |
| `search.sort_changed` | Buyer selecting sort option | `{ sort_by: string, sort_order: asc|desc }` |
| `search.page_changed` | Buyer navigating pagination | `{ page: number, size: number }` |
| `product.impression` | Product card rendered in viewport | `{ product_id: string, position: number, list_id: string }` |

### 2.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Ingest query | Normalize input (lowercase, trim, remove stop words) |
| SYS-2 | Generate suggestions | Query autocomplete index for prefix matches; return top 8 |
| SYS-3 | Build search query | Construct boolean query from keywords + filters + sort |
| SYS-4 | Execute search | Query search index with pagination (default 20 per page) |
| SYS-5 | Compute facets | Aggregate counts for active filter categories |
| SYS-6 | Apply business rules | Boost verified sellers, penalize high-dispute sellers, filter blocked products |
| SYS-7 | Cache results | Cache for 60 seconds (TTL), invalidate on product updates |
| SYS-8 | Log analytics | Write impression and search event to analytics pipeline |

### 2.4 User Actions

| Step | Action | UI Component |
|------|--------|-------------|
| USR-1 | Enter search query | Search input field (header) |
| USR-2 | Select suggestion | Autocomplete dropdown |
| USR-3 | Click "Search" or press Enter | Submit button / keyboard event |
| USR-4 | Select filter checkboxes/range sliders | Filter panel |
| USR-5 | Change sort order | Sort dropdown |
| USR-6 | Navigate pages | Pagination controls |
| USR-7 | Click product card | Product card → navigate to `/product/{slug}` |

### 2.5 API Calls

```
=== Get Search Suggestions ===
GET /api/v1/search/suggestions?q={query}
Response 200: { suggestions: [{text, type, icon}] }

=== Execute Search ===
GET /api/v1/search?q={query}&category={slug}&min_price={n}&max_price={n}
    &rating={n}&sort={field}.{order}&page={n}&size={n}
Response 200: {
    products: [{id, title, slug, price, rating, seller, thumbnail}],
    pagination: {page, size, total, total_pages},
    facets: {categories: [{slug, name, count}], price_ranges: [{label, count}], ratings: [{star, count}]}
}
Response 400: { error: "Invalid filter parameter", details: [...] }
Response 503: { error: "Search service unavailable" }
```

### 2.6 State Transitions

```
[Idle] --(user types query)--> [Typing]
[Typing] --(debounce timeout)--> [Fetching Suggestions]
[Fetching Suggestions] --(response)--> [Showing Suggestions]
[Showing Suggestions] --(user selects/continues)--> [Idle]
[Idle] --(user submits)--> [Searching]
[Searching] --(response received)--> [Displaying Results]
[Displaying Results] --(user changes filter/sort/page)--> [Searching]
[Displaying Results] --(user clicks product)--> [Navigating to Product]
```

### 2.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Search returns ≥ 1 result; results displayed within 500 ms; user navigates to product |
| **Empty Results** | Search returns 0 results; system shows "No results found" with suggestions, popular categories, and "Search tips" |
| **Partial Success** | Some filters yield no results; system degrades gracefully (disable filter, show count 0) |
| **Failure - Timeout** | Search index unresponsive (> 2s); system returns cached results if available, or shows fallback message |
| **Failure - Error** | Search service exception; system logs error, shows generic error, retry button |

### 2.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| API returns stale data | Clear front-end cache; force refetch on next interaction |
| Filter applied incorrectly | URL state is source of truth; resetting URL params restores previous state |
| Impression logged to wrong product | Analytics pipeline deduplicates by session + position; no rollback needed |

---

## 3. Add to Cart & Checkout Flow

### 3.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           | Step 7           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|------------------|
Buyer (UI)        | Clicks "Add to  | Views cart        | Proceeds to      | Selects address   | Selects payment  | Reviews order    | Places order     |
                  | Cart" / "Buy    |                   | checkout         |                   | method           | summary          |                  |
                  | Now"            |                   |                  |                   |                  |                  |                  |
Browser (Client)  | POST /cart      | GET /cart         | PATCH /cart/     | GET /addresses    | GET /payment-    | GET /order/      | POST /orders     |
                  |                 |                   | checkout         | POST /addresses   | methods          | preview          |                  |
Cart Service      | Add item        | Return cart       | Validate cart    | —                 | —                | Calculate totals | Create order     |
Inventory Service | Validate stock  | Check if in stock | Lock items       | —                 | —                | —                 | Confirm stock    |
Payment Service   | —               | —                 | —                | —                 | List methods     | Calculate fees   | Initiate payment |
Order Service     | —               | —                 | —                | —                 | —                | Preview order    | Save order       |
Database          | Save cart item  | Read cart         | Update status    | CRUD addresses    | Read methods     | —                | Insert order     |
```

### 3.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `cart.item.added` | Buyer clicks "Add to Cart" | `{ product_id, variant_id, quantity }` |
| `cart.item.removed` | Buyer removes item | `{ cart_item_id }` |
| `cart.item.quantity_changed` | Buyer changes quantity | `{ cart_item_id, quantity }` |
| `checkout.started` | Buyer clicks "Proceed to Checkout" | `{ cart_id }` |
| `order.placed` | Buyer clicks "Place Order" | `{ cart_id, address_id, payment_method_id }` |

### 3.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Validate product | Check product is published, not deleted, seller is active |
| SYS-2 | Calculate price | Apply base price, variant price, coupons, taxes |
| SYS-3 | Lock cart items | Mark cart items as "locked for checkout" to prevent modification |
| SYS-4 | Validate address | Check required fields, geocode if physical delivery (N/A for digital) |
| SYS-5 | Calculate totals | Subtotal, discount, tax, platform fee, grand total |
| SYS-6 | Idempotency check | Ensure order is not duplicated (idempotency key) |
| SYS-7 | Create order | Insert order with status `PENDING_PAYMENT` |
| SYS-8 | Clear cart | Remove purchased items from cart |

### 3.4 User Actions

| Step | Action | Constraints |
|------|--------|-------------|
| USR-1 | Click "Add to Cart" | Variant must be selected if exists |
| USR-2 | Open cart dropdown | Cart badge shows count |
| USR-3 | Navigate to cart page | — |
| USR-4 | Update item quantity | Min 1, max 99 |
| USR-5 | Remove item | Confirmation optional |
| USR-6 | Click "Proceed to Checkout" | Requires login (guest → login prompt) |
| USR-7 | Select/add shipping address | Max 10 addresses |
| USR-8 | Select payment method | Based on available gateways |
| USR-9 | Apply coupon code | Validate before apply |
| USR-10 | Review order summary | Final price check |
| USR-11 | Click "Place Order" | Final confirmation |

### 3.5 API Calls

```
=== Add to Cart ===
POST /api/v1/cart/items
Body: { product_id: string, variant_id?: string, quantity: number }
Response 201: { cart_item_id: string, cart: { items: [...], subtotal: number } }
Response 409: { error: "Product out of stock" }

=== Get Cart ===
GET /api/v1/cart
Response 200: { items: [...], subtotal: number, discount: number, total: number }

=== Start Checkout ===
POST /api/v1/checkout/start
Body: { cart_id: string }
Response 200: { checkout_id: string, items: [...], totals: {...} }

=== Get Available Payment Methods ===
GET /api/v1/payment-methods?currency={currency}
Response 200: { methods: [{id, name, icon, fee}] }

=== Place Order ===
POST /api/v1/orders
Body: {
    checkout_id: string,
    address_id?: string,
    payment_method_id: string,
    coupon_code?: string,
    idempotency_key: string
}
Response 201: { order_id: string, status: "PENDING_PAYMENT", payment_url?: string }
Response 422: { error: "Cart contents have changed", changes: [...] }
```

### 3.6 State Transitions

```
Cart Item States:
[ACTIVE] --(quantity=0)--> [REMOVED]
[ACTIVE] --(checkout started)--> [LOCKED]
[LOCKED] --(order placed)--> [PURCHASED]
[LOCKED] --(checkout abandoned)--> [ACTIVE]

Order States:
[PENDING_PAYMENT] --(payment received)--> [PROCESSING]
[PENDING_PAYMENT] --(24h expiry)--> [CANCELLED]
[PROCESSING] --(delivered)--> [COMPLETED]
[PROCESSING] --(dispute filed)--> [DISPUTED]
[COMPLETED] --(refund requested)--> [REFUNDED]
```

### 3.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Order created, payment initiated, buyer redirected to gateway or shown confirmation |
| **Cart Changed** | Product price changed or item removed between cart and checkout; system shows diff to buyer; buyer must re-confirm |
| **Payment Failed** | Order saved as PENDING_PAYMENT; buyer can retry within 24h |
| **Validation Failure** | Missing address, invalid coupon, unsupported currency; clear error shown per field |
| **System Error** | Order creation fails; rollback cart to pre-checkout state; error logged; retry offered |

### 3.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Order creation fails mid-way | Delete partial order record; unlock cart items; return cart to ACTIVE state |
| Payment initiated but order not saved | Idempotency key ensures order is created before payment URL returned; if order missing, payment webhook recreates it |
| Coupon applied, then removed | Recalculate totals; return coupon usage count |
| Address deleted during checkout | Prompt buyer to select/enter new address |

---

## 4. Digital Delivery & Fulfillment Flow

### 4.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|
System (Order)    | Payment         | Fetch product     | Generate signed  | Attach to order   | Send delivery    | Start escrow     |
                  | confirmed       | files             | download URLs    | record            | notification     | timer            |
File Storage (S3) | —               | Get file metadata | Generate         | —                 | —                | —                |
                  |                 |                   | pre-signed URLs  |                   |                  |                  |
CDN               | —               | —                 | —                | Cache files at    | Serve files      | —                |
                  |                 |                   |                  | edge              |                  |                  |
Buyer (Email/UI)  | —               | —                 | —                | —                 | Receives links   | Downloads files  |
Email Service     | —               | —                 | —                | —                 | Send email with  | —                |
                  |                 |                   |                  |                   | download links   |                  |
Seller (Notified) | —               | —                 | —                | —                 | —                | Download event   |
                  |                 |                   |                  |                   |                  | notification     |
```

### 4.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `payment.completed` | Payment webhook handler | `{ order_id, transaction_id, amount }` |
| `order.delivery_initiated` | Fulfillment service | `{ order_id, file_count, total_size }` |
| `file.downloaded` | CDN / file server | `{ order_id, product_id, file_id, buyer_id, ip, user_agent }` |
| `delivery.confirmed` | Buyer clicks confirm / auto-timer | `{ order_id }` |

### 4.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Verify payment | Confirm transaction status = `CAPTURED` |
| SYS-2 | Load product files | Fetch file metadata from database (paths, sizes, checksums) |
| SYS-3 | Check file integrity | Compare SHA-256 checksum against stored value; if mismatch, flag and retry from backup |
| SYS-4 | Generate signed URLs | Create pre-signed S3 URLs with 24-hour expiry; rate-limited to 10 URLs per file |
| SYS-5 | Store delivery record | Insert `delivery` record: order_id, file_id, url, expiry, created_at |
| SYS-6 | Send notification | Push email + in-app notification with download links |
| SYS-7 | Start escrow timer | Set `escrow_expires_at = now + 14 days`; schedule auto-release job |
| SYS-8 | Log delivery event | Record delivery attempt in audit log |

### 4.4 User Actions

| Step | Action | UI Component |
|------|--------|-------------|
| USR-1 | View order confirmation | Order confirmation page |
| USR-2 | Click download link | Direct link or "My Downloads" page |
| USR-3 | Save file | Browser download dialog |
| USR-4 | Confirm delivery (optional) | "I've received my files" button |
| USR-5 | Report download issue | "Having trouble? Contact Support" link |

### 4.5 API Calls

```
=== Get Download URLs ===
GET /api/v1/orders/{order_id}/downloads
Headers: Authorization: Bearer {token}
Response 200: {
    files: [
        {file_id, filename, size, mime_type, url, expires_at, download_count}
    ]
}
Response 403: { error: "Order not completed or escrow frozen" }

=== Confirm Delivery ===
POST /api/v1/orders/{order_id}/confirm-delivery
Response 200: { status: "DELIVERY_CONFIRMED", escrow_released: true }

=== Report Delivery Issue ===
POST /api/v1/orders/{order_id}/delivery-issue
Body: { issue_type: "file_corrupt"|"wrong_file"|"cannot_download", description: string }
Response 201: { ticket_id: string }
```

### 4.6 State Transitions

```
Order Fulfillment States:
[PROCESSING] --(delivery initiated)--> [DELIVERING]
[DELIVERING] --(URLs generated)--> [DELIVERED]
[DELIVERED] --(buyer confirms)--> [COMPLETED]
[DELIVERED] --(14 days elapsed)--> [COMPLETED]
[DELIVERED] --(buyer reports issue)--> [DELIVERY_ISSUE_REPORTED]
[DELIVERY_ISSUE_REPORTED] --(seller re-uploads)--> [DELIVERED]

File URL States:
[ACTIVE] --(expired after 24h)--> [EXPIRED]
[EXPIRED] --(re-requested)--> [ACTIVE] (new URL generated)
[ACTIVE] --(max downloads reached)--> [EXHAUSTED]
```

### 4.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Files delivered, buyer downloads, escrow released, seller paid |
| **File Corrupt** | Checksum mismatch detected; system retrieves from backup; if backup also corrupt, flags for seller re-upload |
| **URL Expired** | Buyer clicks expired link → redirected to order page with fresh URL generation |
| **Download Limit Exceeded** | Show error: "Download limit reached. Contact seller to request additional downloads." |
| **Delivery Issue** | Buyer reports issue → support ticket created → seller must respond within 48h |

### 4.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Payment captured but delivery fails | Hold escrow; notify seller to verify files; if seller unresponsive after 48h, auto-refund buyer |
| Wrong files delivered | Seller uploads correct files; new delivery event generated; old URLs invalidated |
| Buyer reports successful download but system didn't record | Support agent manually confirms delivery; escrow released |
| CDN region failure | Failover to alternate CDN region; DNS-based routing |

---

## 5. Review & Rating Flow

### 5.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|
Buyer (UI)        | Navigates to    | Writes review +   | Submits review   | —                 | Views seller     | —                |
                  | review form     | selects rating    |                  |                   | reply            |                  |
System            | Validate        | —                 | Save review;     | —                 | Notify buyer of  | Recalculate      |
                  | eligibility     |                   | queue for        |                   | reply            | product rating   |
                  | (purchased?)    |                   | moderation       |                   |                  |                  |
Moderation Queue  | —               | —                 | Auto-scan; flag  | —                 | —                | —                |
                  |                 |                   | if needed        |                   |                  |                  |
Seller (UI)       | —               | —                 | —                | Writes public     | —                | —                |
                  |                 |                   |                  | reply to review   |                  |                  |
Database          | Read orders     | —                 | Insert review    | —                 | Insert reply     | Update avg       |
                  |                 |                   |                  |                   |                  | rating           |
```

### 5.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `review.submitted` | Buyer submits review form | `{ product_id, rating, text, images }` |
| `review.moderated` | Moderation service | `{ review_id, action: approve|reject|flag }` |
| `seller.review_reply` | Seller replies to review | `{ review_id, text }` |
| `review.reported` | Any user flags review | `{ review_id, reason }` |

### 5.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Verify eligibility | Check order exists, status = COMPLETED, within 30-day review window, no existing review |
| SYS-2 | Sanitize text | Strip HTML, profanity filter, length check (10-5000 chars) |
| SYS-3 | Scan images | NSFW detection; auto-flag if confidence > 80% |
| SYS-4 | Store review | Insert with status `PUBLISHED` (if clean) or `PENDING_MODERATION` |
| SYS-5 | Recalculate rating | Update product `avg_rating`, `rating_count`, rating distribution |
| SYS-6 | Notify seller | Send in-app + email notification |
| SYS-7 | Handle reply | Validate seller owns product; append reply to review |

### 5.4 User Actions

| Step | Action | Constraints |
|------|--------|-------------|
| USR-1 | Click "Write a Review" | Only on order detail page for completed orders |
| USR-2 | Select star rating | 1–5 stars; hover preview |
| USR-3 | Write review text | 10–5000 characters |
| USR-4 | Upload images | Max 3, JPG/PNG, 5 MB each |
| USR-5 | Submit review | Cannot edit after submission |
| USR-6 | Flag review as inappropriate | Reason dropdown + optional note |
| USR-7 | Reply to review (seller) | One reply per review; editable within 24h |

### 5.5 API Calls

```
=== Submit Review ===
POST /api/v1/reviews
Body: { order_id: string, product_id: string, rating: int, text: string, images: [file] }
Response 201: { review_id: string, status: "PUBLISHED"|"PENDING_MODERATION" }
Response 403: { error: "Not eligible to review this product" }

=== Get Product Reviews ===
GET /api/v1/products/{slug}/reviews?page={n}&sort={field}.{order}
Response 200: {
    reviews: [{id, buyer_name, rating, text, images, created_at, seller_reply, helpful_count}],
    pagination: {...},
    aggregate: {avg_rating, total_count, distribution: {1: n, 2: n, 3: n, 4: n, 5: n}}
}

=== Reply to Review (Seller) ===
POST /api/v1/reviews/{review_id}/reply
Body: { text: string }
Response 200: { reply_id: string }
```

### 5.6 State Transitions

```
Review States:
[PENDING_MODERATION] --(approved)--> [PUBLISHED]
[PENDING_MODERATION] --(rejected)--> [REJECTED]
[PUBLISHED] --(reported & moderated)--> [HIDDEN]
[PUBLISHED] --(edited by admin)--> [PUBLISHED] (with edit flag)
[HIDDEN] --(appeal approved)--> [PUBLISHED]
```

### 5.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Review published; product rating updated; seller notified |
| **Auto-Flagged** | Review contains prohibited content → PENDING_MODERATION; buyer notified |
| **Duplicate Review** | Buyer already reviewed this product → reject with message: "You have already reviewed this product" |
| **Eligibility Failed** | Order not found, not completed, or outside window → 403 error |
| **Image Upload Failed** | Text-only review accepted; images dropped with warning |

### 5.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Review published in error | Moderator hides review; rating recalculated; automatic |
| Seller reply inappropriate | Moderator deletes reply; seller warned |
| Rating manipulation detected | Disable reviews for product; investigate; manual rating override |

---

## 6. Refund & Dispute Flow

### 6.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|
Buyer             | Requests refund | Provides evidence | —                 | May appeal        | —                | Receives refund  |
Seller            | —               | Accepts / denies  | —                 | —                 | —                | —                |
System            | Validate        | Notify seller;    | Escalate after   | Freeze escrow     | Execute decision | Notify both      |
                  | eligibility     | 48h timer         | 48h no-response  |                   |                  |                  |
Moderator         | —               | —                 | Review case      | —                 | —                | —                |
Finance Service   | —               | —                 | —                | —                 | Process refund   | —                |
Payment Gateway   | —               | —                 | —                | —                 | Reverse payment  | —                |
```

### 6.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `refund.requested` | Buyer from order detail page | `{ order_id, reason, evidence }` |
| `refund.seller_accepted` | Seller approves refund | `{ refund_request_id }` |
| `refund.seller_denied` | Seller denies | `{ refund_request_id, reason }` |
| `refund.escalated` | No seller response after 48h | `{ refund_request_id }` |
| `refund.processed` | Finance / gateway callback | `{ refund_request_id, transaction_id }` |

### 6.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Validate refund window | Order must be ≤ 14 days old; download count ≤ 5 |
| SYS-2 | Freeze escrow balance | Mark escrow funds as `ON_HOLD` |
| SYS-3 | Create refund request | Status: `PENDING_SELLER_APPROVAL` |
| SYS-4 | Notify seller | 48-hour countdown starts |
| SYS-5 | Auto-escalate | If seller timeout → move to `PENDING_MODERATION` |
| SYS-6 | Process refund | Call gateway refund API; create wallet credit if gateway refund not possible |
| SYS-7 | Reverse commission | Deduct from platform revenue ledger |
| SYS-8 | Update order | Set status to `REFUNDED` or `PARTIALLY_REFUNDED` |

### 6.4 User Actions

| Step | Action | Constraints |
|------|--------|-------------|
| USR-1 | Select product + reason | Order detail page > "Request Refund" |
| USR-2 | Upload evidence | Max 5 files, 10 MB each |
| USR-3 | Submit request | One refund request per order |
| USR-4 | Accept refund (seller) | Auto-refund; no further action |
| USR-5 | Deny refund (seller) | Reason required; case escalated |
| USR-6 | Appeal (buyer) | Within 7 days of rejection |

### 6.5 API Calls

```
=== Request Refund ===
POST /api/v1/orders/{order_id}/refunds
Body: { reason: string, description: string, evidence: [file] }
Response 201: { refund_request_id, status: "PENDING_SELLER_APPROVAL" }

=== Seller Responds to Refund ===
POST /api/v1/refunds/{refund_request_id}/seller-response
Body: { action: "accept"|"deny", reason?: string }
Response 200: { status: "SELLER_APPROVED"|"ESCALATED" }

=== Process Refund (Internal) ===
POST /api/v1/admin/refunds/{refund_request_id}/process
Body: { decision: "full_refund"|"partial_refund", percentage?: number, notes: string }
Headers: Authorization: Bearer {admin_token}
Response 200: { refund_id, amount, transaction_id, status: "COMPLETED" }
```

### 6.6 State Transitions

```
Refund Request States:
[PENDING_SELLER_APPROVAL] --(seller accepts)--> [SELLER_APPROVED]
[PENDING_SELLER_APPROVAL] --(48h timeout)--> [ESCALATED]
[PENDING_SELLER_APPROVAL] --(seller denies)--> [ESCALATED]
[SELLER_APPROVED] --(finance processes)--> [COMPLETED]
[ESCALATED] --(moderator decides)--> [COMPLETED] or [DENIED]
[COMPLETED] --(appeal filed)--> [APPEALED]
[APPEALED] --(admin decides)--> [COMPLETED] (overridden) or [DENIED] (upheld)
```

### 6.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success - Seller Approved** | Refund processed immediately; buyer notified |
| **Success - Moderator Approved** | Refund processed per moderator decision |
| **Denied - Seller + Moderator** | Escrow released to seller; buyer notified with explanation |
| **Refund Processing Failed** | Gateway refund API error; platform issues wallet credit; finance team investigates |
| **Partial Refund** | Percentage split applied; both parties notified |

### 6.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Refund processed to wrong amount | Finance manager issues corrective transaction; audit trail updated |
| Gateway refund succeeded but platform update failed | Idempotency key prevents double refund; reconciliation job corrects |
| Refund accidentally issued twice | Second refund detected by idempotency; rejected with "Already refunded" |
| Appeal reverses previous decision | If funds already released, reclaim from seller balance or deduct from future earnings |

---

## 7. Seller Payout & Commission Flow

### 7.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|
Seller            | Views balance   | Requests          | —                 | —                 | Receives funds   | —                |
                  |                 | withdrawal        |                  |                   |                  |                  |
System            | Calculate       | Validate (KYC,    | Create payout    | Queue for         | —                | Log transaction  |
                  | balance         | limits, balance)  | request          | processing        |                  |                  |
Finance Manager   | —               | —                 | Review request   | Approve / reject  | —                | Reconcile        |
Payment Gateway   | —               | —                 | —                | —                 | Process payout   | Send callback    |
Database          | Read ledger     | Read KYC/limits   | Insert request   | Update status     | Update ledger    | Insert history   |
```

### 7.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `payout.requested` | Seller clicks withdraw | `{ amount, payout_method_id }` |
| `payout.approved` | Finance approves | `{ payout_request_id }` |
| `payout.rejected` | Finance rejects | `{ payout_request_id, reason }` |
| `payout.processed` | Gateway callback | `{ payout_request_id, gateway_txn_id, status }` |

### 7.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Calculate available balance | `SUM(order.net_amount) - SUM(withdrawal.pending) - SUM(escrow.held)` |
| SYS-2 | Validate minimum threshold | Amount ≥ configurable minimum (default $10) |
| SYS-3 | Validate KYC level | Level 1: $500/mo cap; Level 2: $5,000/mo; Level 3: unlimited |
| SYS-4 | Check daily frequency | Max 1 withdrawal per day (configurable) |
| SYS-5 | Create payout record | Status: `PENDING_REVIEW`; hold balance |
| SYS-6 | Auto-approval logic | If seller has 10+ past successful payouts and amount < $1,000 → auto-approve |
| SYS-7 | Batch processing | Group approved payouts for batch file upload to bank |
| SYS-8 | Reconciliation | Match batch file response to payout records |

### 7.4 User Actions

| Step | Action | Constraints |
|------|--------|-------------|
| USR-1 | View financial dashboard | Real-time balance, pending, history |
| USR-2 | Add payout method | Bank account, bKash, Nagad, PayPal |
| USR-3 | Initiate withdrawal | Amount in available balance |
| USR-4 | Confirm withdrawal | Review details before final confirmation |
| USR-5 | View withdrawal history | Filter by date, status |

### 7.5 API Calls

```
=== Initiate Payout ===
POST /api/v1/payouts
Body: { amount: number, payout_method_id: string, otp: string }
Response 201: { payout_id, status: "PENDING_REVIEW", estimated_processing_time: string }
Response 422: { error: "Insufficient balance"|"KYC limit reached"|"Daily limit exceeded" }

=== Get Payout History ===
GET /api/v1/payouts?status={status}&page={n}
Response 200: {
    payouts: [{id, amount, method, status, created_at, processed_at, receipt_url}],
    pagination: {...}
}

=== Admin: Process Payout ===
POST /api/v1/admin/payouts/{payout_id}/process
Body: { action: "approve"|"reject", notes?: string }
Response 200: { status: "PROCESSING"|"REJECTED" }
```

### 7.6 State Transitions

```
Payout States:
[PENDING_REVIEW] --(auto-approve)--> [PROCESSING]
[PENDING_REVIEW] --(finance approves)--> [PROCESSING]
[PENDING_REVIEW] --(finance rejects)--> [REJECTED]
[PROCESSING] --(gateway success)--> [COMPLETED]
[PROCESSING] --(gateway failure)--> [FAILED]
[FAILED] --(retry)--> [PROCESSING]
[FAILED] --(finance cancels)--> [CANCELLED]
```

### 7.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Funds transferred; seller receives confirmation; ledger updated |
| **Auto-Approved** | Low-risk payout bypasses manual review; processed same-day |
| **Rejected - KYC** | Seller must complete KYC upgrade; funds returned to balance |
| **Rejected - Suspicious** | Flagged for compliance; manual investigation; funds frozen |
| **Failed - Gateway** | Funds returned to balance; seller can retry with different method |

### 7.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Payout approved but gateway rejects | Funds restored to seller balance; status set to FAILED; seller notified |
| Duplicate payout processed | Finance manager creates debit adjustment; seller balance corrected |
| Wrong amount paid | Shortfall → additional payout issued; Overpayment → deducted from future earnings |
| Bank account invalid | Payout fails; seller must update details; funds restored |

---

## 8. Coupon & Discount Application Flow

### 8.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|
Seller (Admin)    | Creates coupon  | Sets rules        | Activates coupon | —                 | Views analytics  |
Buyer (Checkout)  | —               | —                 | —                | Enters code       | Sees discount    |
System            | Validate rules  | Store coupon      | Update status    | Validate + apply  | Recalculate total|
Database          | Insert coupon   | —                 | —                | Read coupon       | Update usage     |
Cart Service      | —               | —                 | —                | Check eligibility | Apply discount   |
```

### 8.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `coupon.created` | Seller saves coupon form | `{ code, type, value, rules }` |
| `coupon.activated` | Seller toggles status | `{ coupon_id, active: true }` |
| `coupon.applied` | Buyer enters code at checkout | `{ code, cart_id }` |
| `coupon.removed` | Buyer removes code | `{ cart_id }` |

### 8.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Validate coupon rules | Check: min purchase, valid products, usage count not exceeded, within date range, not expired |
| SYS-2 | Calculate discount | Percentage → `min(item_price * percentage/100, max_discount)`; Fixed → `min(fixed_amount, item_price)` |
| SYS-3 | Check stacking rules | If `stackable = false`, remove any existing coupon before applying |
| SYS-4 | Apply to cart | Add discount_line_item to cart with coupon reference |
| SYS-5 | Increment usage | Update `current_usage_count` on coupon (prevent race condition via atomic increment) |
| SYS-6 | Persist to order | On order creation, copy coupon details to order snapshot (price at time of order) |

### 8.4 User Actions

| Step | Action | Constraints |
|------|--------|-------------|
| USR-1 | Create coupon (seller) | Code unique per seller; auto-generate option |
| USR-2 | Set discount type | Percentage (1-100%) or Fixed amount (≤ product price) |
| USR-3 | Set conditions | Min purchase, applicable products, max uses, expiry |
| USR-4 | Enter coupon code (buyer) | Case-insensitive; trim whitespace |
| USR-5 | Apply coupon | Button triggers validation |
| USR-6 | Remove coupon | "Remove" link next to applied coupon |

### 8.5 API Calls

```
=== Create Coupon (Seller) ===
POST /api/v1/seller/coupons
Body: {
    code?: string, // auto-generated if omitted
    discount_type: "percentage"|"fixed",
    value: number,
    min_purchase?: number,
    product_ids?: [string],
    max_uses?: number,
    starts_at: datetime,
    expires_at: datetime,
    stackable: boolean
}
Response 201: { coupon_id, code, status: "DRAFT" }

=== Apply Coupon (Checkout) ===
POST /api/v1/checkout/{checkout_id}/coupon
Body: { code: string }
Response 200: {
    coupon: {code, discount_type, value, discount_amount},
    totals: {subtotal, discount, tax, total}
}
Response 404: { error: "Coupon not found" }
Response 410: { error: "Coupon expired or usage limit reached" }
Response 422: { error: "Minimum purchase amount not met (requires BDT X,XXX)" }

=== Remove Coupon ===
DELETE /api/v1/checkout/{checkout_id}/coupon
Response 200: { totals: {subtotal, discount: 0, tax, total} }
```

### 8.6 State Transitions

```
Coupon States:
[DRAFT] --(seller activates)--> [ACTIVE]
[ACTIVE] --(expiry date passed)--> [EXPIRED]
[ACTIVE] --(seller deactivates)--> [DISABLED]
[ACTIVE] --(max_uses reached)--> [EXHAUSTED]
[DISABLED] --(seller reactivates)--> [ACTIVE]
[EXPIRED] --(cannot reactivate)--> [ARCHIVED]

Coupon Application States:
[NOT_APPLIED] --(code entered)--> [VALIDATING]
[VALIDATING] --(valid)--> [APPLIED]
[VALIDATING] --(invalid)--> [NOT_APPLIED] (with error)
[APPLIED] --(coupon removed)--> [NOT_APPLIED]
[APPLIED] --(order placed)--> [REDEEMED]
```

### 8.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Discount applied; totals recalculated; buyer sees reduced price |
| **Expired Coupon** | Show "This coupon has expired" |
| **Usage Limit Reached** | Show "This coupon has reached its maximum number of uses" |
| **Minimum Not Met** | Show "Add BDT X,XXX more to use this coupon" |
| **Product Not Eligible** | Show "This coupon does not apply to items in your cart" |
| **Code Not Found** | Show "Invalid coupon code. Please check and try again." |

### 8.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Coupon applied but buyer abandons checkout | Usage count auto-decremented after 24h (session expiry) |
| Coupon applied, order placed, then refunded | Coupon usage decremented; no restoration needed due to refund |
| Race condition on usage count | Atomic increment in database prevents overshoot; remaining uses accurate |
| Price changes after coupon application | Cart totals recalculated on checkout start; discount re-validated |

---

## 9. Affiliate Tracking & Payout Flow

### 9.1 Swimlane Diagram

```
Actor/Layer       | Step 1          | Step 2            | Step 3           | Step 4            | Step 5           | Step 6           |
------------------|-----------------|-------------------|------------------|-------------------|------------------|------------------|
Affiliate         | Generates link  | Shares link       | Views dashboard  | —                 | Requests payout  | —                |
Buyer             | Clicks link     | —                 | Browses          | Purchases         | —                | —                |
Browser (Cookie)  | Store ref cookie| —                 | —                | Attach cookie to  | —                | —                |
                  | (30-day TTL)    |                   |                  | checkout          |                  |                  |
System            | Create unique   | —                 | Log click        | Match cookie to   | Calculate        | Process payout   |
                  | referral URL    |                   |                  | order             | commission       | (per withdrawal  |
                  |                 |                   |                  |                   | hold 14 days     | workflow)        |
Database          | Save link       | —                 | Insert click     | Update attribution| Insert commission| Update balance   |
                  |                 |                   | event            |                   |                  |                  |
```

### 9.2 Trigger Events

| Trigger | Source | Payload |
|---------|--------|---------|
| `affiliate.link_generated` | Affiliate creates link | `{ affiliate_id, target_type, target_id }` |
| `affiliate.link_clicked` | Buyer clicks referral link | `{ affiliate_id, link_id, ip, user_agent, referrer }` |
| `affiliate.conversion` | Order completed with affiliate attribution | `{ order_id, affiliate_id, commission_amount }` |
| `affiliate.commission_confirmed` | Escrow period ends, no refund | `{ commission_id }` |

### 9.3 System Actions

| Step | Action | Description |
|------|--------|-------------|
| SYS-1 | Generate link | Create short URL with encoded affiliate ID and target |
| SYS-2 | Set cookie | Domain cookie: `tsbl_ref={affiliate_id}`; SameSite=Lax; Secure; 30-day TTL |
| SYS-3 | Log click | Record timestamp, IP, user agent, referrer, geolocation |
| SYS-4 | Attribute order | On order completion, check cookie → if match, create commission record |
| SYS-5 | Calculate commission | Apply rate: `order.net_amount * (commission_rate/100)` |
| SYS-6 | Start holding period | Commission status = `PENDING` for 14 days |
| SYS-7 | Confirm commission | After 14 days with no refund → status = `CONFIRMED`; add to available balance |
| SYS-8 | Fraud detection | Flag patterns: same IP as seller, multiple clicks from same device, self-referral |

### 9.4 User Actions

| Step | Action | Constraints |
|------|--------|-------------|
| USR-1 | Register as affiliate | Requires approval; active seller or content creator |
| USR-2 | Generate referral link | Target: any product, store, or general marketplace |
| USR-3 | Copy link to clipboard | "Copy" button with success toast |
| USR-4 | Share link | Email, social media, blog, website |
| USR-5 | View earnings | Real-time dashboard with charts |
| USR-6 | Request payout | Via Withdrawal workflow; minimum $20 |

### 9.5 API Calls

```
=== Generate Referral Link ===
POST /api/v1/affiliate/links
Body: { target_type: "product"|"store"|"general", target_id?: string }
Response 201: {
    link_id, short_url: "https://tsbl.bd/r/AbC123",
    full_url: "https://tsbl.bd/product/xyz?ref=AFF001",
    clicks: 0, conversions: 0
}

=== Get Affiliate Dashboard ===
GET /api/v1/affiliate/dashboard
Response 200: {
    metrics: {
        total_clicks, unique_clicks, conversion_rate,
        pending_commission, confirmed_commission, paid_commission
    },
    links: [{link_id, short_url, clicks, conversions, earnings}],
    recent_conversions: [{order_id, product, amount, commission, status, date}]
}

=== Get Affiliate Commissions ===
GET /api/v1/affiliate/commissions?status={status}&page={n}
Response 200: {
    commissions: [{id, order_id, product, amount, rate, commission, status, created_at, confirmed_at}],
    pagination: {...}
}
```

### 9.6 State Transitions

```
Affiliate Commission States:
[PENDING] --(14 days no refund)--> [CONFIRMED]
[PENDING] --(refund issued)--> [VOIDED]
[PENDING] --(partial refund)--> [ADJUSTED]
[CONFIRMED] --(added to balance)--> [PAID]
[PAID] --(clawback required)--> [RECOUPED]
[VOIDED] --(cannot be reinstated)--> [ARCHIVED]

Click Attribution States:
[CLICKED] --(session active)--> [ATTRIBUTED]
[ATTRIBUTED] --(purchase complete)--> [CONVERTED]
[ATTRIBUTED] --(session expired, no purchase)--> [EXPIRED]
```

### 9.7 Success / Failure Paths

| Path | Description |
|------|-------------|
| **Success** | Affiliate link → click → purchase → commission confirmed → paid |
| **No Purchase** | Click recorded but no conversion; affiliate sees click in analytics |
| **Refund Before Confirmation** | Commission voided; affiliate earns nothing |
| **Self-Referral Detected** | Commission voided; affiliate account flagged; possible suspension |
| **Cookie Blocked** | No attribution; affiliate encouraged to use direct link with UTM parameters |

### 9.8 Rollback Procedures

| Scenario | Rollback Action |
|----------|----------------|
| Commission confirmed but order later refunded | Recoup commission from affiliate balance; if insufficient, deduct from future earnings |
| Duplicate conversion attributed | Manual correction by finance; reverse one commission |
| Affiliate link compromised (fraudulent clicks) | Block link; audit all conversions; void fraudulent commissions |
| Gateway fee clawback affects commission | Recalculate commission net of chargeback fee; adjust commission if not yet paid |

---

## Appendix A: Cross-Cutting API Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `VALIDATION_ERROR` | Request body fails schema validation |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | Authenticated but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Resource state conflict (e.g., duplicate, already actioned) |
| 410 | `GONE` | Resource expired or exhausted |
| 422 | `UNPROCESSABLE_ENTITY` | Business rule violation (e.g., insufficient balance) |
| 429 | `RATE_LIMITED` | Too many requests; retry after header provided |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Downstream dependency unavailable |

## Appendix B: State Machine Summary

| Workflow | States |
|----------|--------|
| **Search** | Idle → Typing → Fetching Suggestions → Showing Suggestions → Searching → Displaying Results → Navigating to Product |
| **Cart** | Active → Locked → Purchased → Removed |
| **Order** | Pending Payment → Processing → Delivering → Delivered → Completed / Disputed / Refunded / Cancelled |
| **Refund** | Pending Seller Approval → Seller Approved → Escalated → Completed / Denied / Appealed |
| **Payout** | Pending Review → Processing → Completed / Failed / Rejected / Cancelled |
| **Coupon** | Draft → Active → Disabled / Expired / Exhausted → Archived |
| **Commission** | Pending → Confirmed → Paid / Voided / Adjusted / Recouped |
| **Review** | Pending Moderation → Published / Rejected / Hidden |

## Appendix C: Delivery & Rollback Responsibility Matrix

| Component | Primary Owner | Rollback Authority | Notification Required |
|-----------|---------------|-------------------|----------------------|
| Order Service | Order Manager | Auto (system) | Buyer + Seller |
| Payment Service | Finance Manager | Finance Manager + System | Buyer + Seller + Finance |
| File Delivery | System (auto) | System (auto) | Buyer (on retry) |
| Refund Processing | Finance Manager | Finance Manager + Moderator | Buyer + Seller + Finance |
| Review Publication | Moderator | Moderator | Buyer (if removed) |
| Affiliate Commission | Finance Manager | Finance Manager | Affiliate |

---

*End of Document — TRUE STAR BD LIMITED*

---

**Document Status:** Draft  
**Next Review:** 2026-07-15  
**Change Control:** All changes require approval by the Product Owner and Chief Architect.
