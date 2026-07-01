# Module Breakdown — TRUE STAR BD LIMITED Digital Marketplace

> **Document ID:** SRS-MB-002  
> **Version:** 1.0  
> **Status:** Draft  
> **Author:** Principal Software Architect  
> **Last Updated:** 2026-07-01  

---

## Table of Contents

1. [Modules at a Glance](#1-modules-at-a-glance)
2. [Module Specifications](#2-module-specifications)  
   2.1 [AUTH — Authentication](#21-auth--authentication)  
   2.2 [AUTHZ — Authorization](#22-authz--authorization)  
   2.3 [RBAC — Role-Based Access Control](#23-rbac--role-based-access-control)  
   2.4 [USR — User Management](#24-usr--user-management)  
   2.5 [SEL — Seller Management](#25-sel--seller-management)  
   2.6 [MKT — Marketplace](#26-mkt--marketplace)  
   2.7 [CAT — Product Catalog](#27-cat--product-catalog)  
   2.8 [SRCH — Search Engine](#28-srch--search-engine)  
   2.9 [CART — Shopping Cart](#29-cart--shopping-cart)  
   2.10 [CHK — Checkout](#210-chk--checkout)  
   2.11 [ORD — Orders](#211-ord--orders)  
   2.12 [DEL — Digital Delivery](#212-del--digital-delivery)  
   2.13 [WAL — Wallet](#213-wal--wallet)  
   2.14 [ESC — Escrow](#214-esc--escrow)  
   2.15 [PAY — Payments](#215-pay--payments)  
   2.16 [WDR — Withdrawals](#216-wdr--withdrawals)  
   2.17 [CPN — Coupons](#217-cpn--coupons)  
   2.18 [AFF — Affiliate System](#218-aff--affiliate-system)  
   2.19 [MSG — Messaging](#219-msg--messaging)  
   2.20 [NOT — Notifications](#220-not--notifications)  
   2.21 [REV — Reviews](#221-rev--reviews)  
   2.22 [DSP — Disputes](#222-dsp--disputes)  
   2.23 [SUP — Support Tickets](#223-sup--support-tickets)  
   2.24 [ANL — Analytics](#224-anl--analytics)  
   2.25 [CMS — Content Management System](#225-cms--content-management-system)  
   2.26 [ADM — Admin Panel](#226-adm--admin-panel)  
   2.27 [AUD — Audit Logs](#227-aud--audit-logs)  
   2.28 [SET — Settings](#228-set--settings)  
3. [Dependency Graph Summary](#3-dependency-graph-summary)
4. [Cross-Cutting Concerns](#4-cross-cutting-concerns)

---

## 1. Modules at a Glance

| ID | Module | Layer | Primary DB | Key Dependencies |
|---|---|---|---|---|
| AUTH | Authentication | Infrastructure | PostgreSQL | SET, AUD |
| AUTHZ | Authorization | Domain | — (Policy engine) | AUTH, RBAC |
| RBAC | Role-Based Access Control | Domain | PostgreSQL | AUTH |
| USR | User Management | Domain | PostgreSQL | AUTH, AUTHZ, RBAC |
| SEL | Seller Management | Domain | PostgreSQL | USR, RBAC |
| MKT | Marketplace | Domain | PostgreSQL | CAT, SEL, AUTHZ |
| CAT | Product Catalog | Domain | PostgreSQL | SEL, MKT |
| SRCH | Search Engine | Application | Elasticsearch | CAT |
| CART | Shopping Cart | Application | Redis + PostgreSQL | CAT, CPN |
| CHK | Checkout | Application | PostgreSQL | CART, PAY, WAL, CPN |
| ORD | Orders | Domain | PostgreSQL | CHK, DEL, PAY, ESC |
| DEL | Digital Delivery | Domain | Object Storage + PostgreSQL | ORD |
| WAL | Wallet | Domain | PostgreSQL | USR, PAY |
| ESC | Escrow | Domain | PostgreSQL | ORD, WAL |
| PAY | Payments | Domain | PostgreSQL | USR, WAL |
| WDR | Withdrawals | Domain | PostgreSQL | WAL, AUTHZ |
| CPN | Coupons | Domain | PostgreSQL | CAT, ORD |
| AFF | Affiliate System | Domain | PostgreSQL | USR, ORD, WAL |
| MSG | Messaging | Application | PostgreSQL | USR, AUTHZ |
| NOT | Notifications | Application | — (Queue) | All modules |
| REV | Reviews | Domain | PostgreSQL | ORD, USR |
| DSP | Disputes | Domain | PostgreSQL | ORD, USR, WAL, ESC |
| SUP | Support Tickets | Application | PostgreSQL | USR, ORD, NOT |
| ANL | Analytics | Application | ClickHouse | All modules (read) |
| CMS | Content Management | Domain | PostgreSQL | AUTHZ, USR |
| ADM | Admin Panel | Presentation | — (Views) | AUTH, AUTHZ, all modules |
| AUD | Audit Logs | Infrastructure | PostgreSQL (append-only) | All modules |
| SET | Settings | Domain | PostgreSQL | AUTHZ |

---

## 2. Module Specifications

### 2.1 AUTH — Authentication

| Attribute | Detail |
|---|---|
| **Module ID** | `AUTH` |
| **Layer** | Infrastructure — entry-point security |
| **Responsibility** | Verify identity of users and services through multiple authentication strategies. |

**Core Features & Sub-Modules**
- Email + password authentication (bcrypt hashing, salted)
- OAuth 2.0 / OpenID Connect providers (Google, Facebook, GitHub)
- Magic-link / passwordless email login
- Multi-Factor Authentication (TOTP, SMS, backup codes)
- Session management (JWT access + refresh token rotation)
- API key authentication for service accounts
- Remember-me token management
- Brute-force detection & rate limiting per IP/account

**Dependencies**
- `SET` — authentication policies (token TTL, MFA enforcement)
- `AUD` — login attempt audit trail
- `USR` — user credential store

**Data Entities**
- `auth_credentials` — hashed passwords, salt, hash algorithm version
- `auth_oauth_links` — provider, provider_user_id, access/refresh tokens
- `auth_mfa_methods` — type (totp/sms/backup), secret, verified_at
- `auth_sessions` — JWT ID, user_id, device fingerprint, IP, expires_at
- `auth_refresh_tokens` — token hash, device info, rotation counter, family
- `auth_api_keys` — key prefix, hash, client_id, scopes, expires_at
- `auth_magic_links` — token, email, intent, expires_at, consumed_at
- `auth_brute_force` — identifier, attempt_count, window_start, locked_until

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `AUTH.LOGIN(email, password, device)` | Authenticate with credentials |
| Command | `AUTH.LOGIN_OAUTH(provider, code, device)` | OAuth callback |
| Command | `AUTH.REFRESH(refresh_token)` | Rotate token pair |
| Command | `AUTH.LOGOUT(session_id)` | Invalidate session |
| Command | `AUTH.MFA_VERIFY(challenge, code)` | Verify MFA step-up |
| Command | `AUTH.REQUEST_MAGIC_LINK(email)` | Send passwordless link |
| Event | `auth.user.logged_in` | Published on successful login |
| Event | `auth.user.logged_out` | Published on logout or expiry |
| Event | `auth.user.mfa_enabled` | MFA method registered |
| Event | `auth.login.failed` | Failed attempt for monitoring |
| REST | `POST /api/v1/auth/login` | Standard login |
| REST | `POST /api/v1/auth/oauth/{provider}` | OAuth initiation |
| REST | `POST /api/v1/auth/refresh` | Token refresh |
| REST | `POST /api/v1/auth/logout` | Session invalidation |

**State Machine**

```
IDLE → [LOGIN] → AUTHENTICATED → [MFA_REQUIRED] → MFA_PENDING → [VERIFY] → AUTHENTICATED
                                          ↓ [fail]                    ↓ [fail]
                                       IDLE                         IDLE
AUTHENTICATED → [LOGOUT] → IDLE
AUTHENTICATED → [TOKEN_EXPIRY] → IDLE
```

**Error Handling**
| Error | HTTP | Strategy |
|---|---|---|
| Invalid credentials | 401 | Increment attempt counter; lock account at threshold |
| Account locked | 423 | Return remaining lockout duration |
| MFA required | 401 | Signal `X-MFA-Required: totp` in headers |
| Expired token | 401 | Hint `token_type: refresh` if refresh still valid |
| Brute-force detected | 429 | Exponential backoff, silent delay response |

**Performance**
- Token validation must complete in < 5 ms (use local JWKS caching)
- Password hashing via bcrypt with configurable cost (minimum 12)
- Session lookup via Redis TTL cache before falling back to PostgreSQL
- Rate-limit counters stored in Redis with 1-second precision expiry

**Security**
- All passwords hashed with bcrypt; never stored in plaintext
- Refresh token rotation with family detection (reuse = revoke all)
- JWT signed with RS256; public key served via `/.well-known/jwks.json`
- OAuth state parameter with PKCE enforcement
- MFA backup codes generated with CSPRNG, one-time use, bcrypt-hashed
- Login rate limiter: 5 attempts/minute per IP, 10 attempts/hour per account

**Integration Points**
- Middleware: `AuthenticationMiddleware` extracts JWT, populates request context
- GraphQL directives: `@auth`, `@requireMfa` for resolver-level enforcement
- Webhook consumers may subscribe to `auth.*` events for SIEM integration

---

### 2.2 AUTHZ — Authorization

| Attribute | Detail |
|---|---|
| **Module ID** | `AUTHZ` |
| **Layer** | Domain — policy decision point |
| **Responsibility** | Evaluate whether an authenticated subject is permitted to perform an action on a resource. |

**Core Features & Sub-Modules**
- Attribute-Based Access Control (ABAC) engine
- Policy-as-Code using Open Policy Agent (OPA) / Rego
- Resource-level ownership checks
- Context-aware policies (time, location, device trust)
- Delegated administration scopes
- Deny-by-default evaluation model
- Policy caching with TTL invalidation

**Dependencies**
- `AUTH` — verified subject identity
- `RBAC` — role-to-permission mappings used as policy input
- `USR` — user attributes (department, clearance level)
- `SET` — feature flags, policy override configuration

**Data Entities**
- `authz_policies` — Rego source, version, status (active/draft/archived)
- `authz_policy_versions` — version history with diff tracking
- `authz_resource_types` — registered resource classes
- `authz_decisions_cache` — decision ID, subject, action, resource, result, expires_at

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `AUTHZ.ALLOW(subject, action, resource, context)` | Boolean decision, cached |
| Command | `AUTHZ.ALLOW_BULK(decisions[])` | Batch evaluation |
| Command | `AUTHZ.FILTER(subject, action, resources[])` | Filter accessible resources |
| Event | `authz.policy.updated` | Policy changed; invalidate cache |
| Event | `authz.decision.denied` | High-signal denied attempt |
| gRPC | `AuthzService.Allow(AllowRequest) returns AllowResponse` | Internal service mesh |

**Error Handling**
| Error | Strategy |
|---|---|
| Policy not found | Fall back to RBAC-only; log warning |
| Rego evaluation error | Deny; alert operator with policy ID |
| Cache miss (burst) | Evaluate synchronously; backfill cache |

**Performance**
- Decision latency < 2 ms when cached, < 20 ms when cold
- Policy evaluator pooled to reuse compiled Rego modules
- Cache: Redis with local L1 (Caffeine) for hottest policies
- Bulk filter operations use SQL-level WHERE clause injection

**Security**
- All policies deny by default; explicit allow required
- Policy updates require multi-signature approval (admin console)
- Decision audit log includes full evaluation context (PII masked)
- Rego sandbox prevents infinite loops and resource exhaustion

**Integration Points**
- Decorator: `@require_permission("orders:read")` on service methods
- Middleware: `AuthorizationMiddleware` auto-evaluates before route handler
- GraphQL: Field-level authorization via custom directive `@authorize(permission)`
- SQL: Row-level security via `authz_filter()` injected into WHERE clauses

---

### 2.3 RBAC — Role-Based Access Control

| Attribute | Detail |
|---|---|
| **Module ID** | `RBAC` |
| **Layer** | Domain |
| **Responsibility** | Manage roles, permissions, and role-to-user assignments as the primary authorization source for most CRUD operations. |

**Core Features & Sub-Modules**
- Hierarchical roles (inheritance model: Admin > Manager > Staff > User)
- Fine-grained permissions (CRUD per resource)
- Role assignment with temporal bounds (start/end dates)
- Permission groups (logical bundles of permissions)
- Default roles for unauthenticated (Guest) and authenticated (User)
- Flat role structure (no deep nesting to avoid evaluation complexity)
- Built-in roles: SuperAdmin, Admin, SupportAgent, Seller, Buyer, Guest

**Dependencies**
- `USR` — user identity for role assignments
- `SET` — role naming conventions, default registration role

**Data Entities**
- `rbac_roles` — id, name, slug, description, is_system, hierarchy_level
- `rbac_permissions` — id, resource, action, scope (global/owner)
- `rbac_role_permissions` — join table (role_id, permission_id)
- `rbac_user_roles` — join table with temporal fields (user_id, role_id, assigned_by, valid_from, valid_until)
- `rbac_permission_groups` — named bundles for UI rendering

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `RBAC.ASSIGN_ROLE(user_id, role_id, assigner_id, valid_until)` | Assign role |
| Command | `RBAC.REVOKE_ROLE(user_id, role_id)` | Remove assignment |
| Command | `RBAC.ADD_PERMISSION(role_id, permission_id)` | Grant permission |
| Query | `RBAC.GET_PERMISSIONS(user_id)` | All effective permissions |
| Query | `RBAC.HAS_PERMISSION(user_id, resource, action)` | Check single permission |
| Event | `rbac.role.assigned` | User gained role |
| Event | `rbac.role.revoked` | User lost role |
| Event | `rbac.permission.changed` | Role-permission mapping updated |

**Error Handling**
| Error | Strategy |
|---|---|
| Circular role inheritance | Reject mutation; validate with topological sort |
| Delete system role | Reject with 422; system roles are immutable |
| Assign non-existent permission | Validate via foreign key; return 404 |

**Performance**
- Permission lookups cached in Redis (keyed by user_id, 5-minute TTL)
- Temporal role validation done in SQL (no in-memory filtering)
- Batch permission checks resolve in single query with JOIN
- Role-permission graph loaded into memory at startup (cold start < 200 ms for 10K roles)

**Security**
- System roles (SuperAdmin, Admin) cannot be deleted or renamed
- Role assignment audit-logged with `AUD`
- Only users with `rbac:manage` permission can modify roles
- Temporal roles automatically expire via scheduled job (runs every minute)

**Integration Points**
- Service-level: `AuthorizationService` queries RBAC first, falls back to ABAC
- Admin UI: Role management console with permission matrix grid
- API: `GET /api/v1/roles`, `POST /api/v1/roles/{id}/assign`

---

### 2.4 USR — User Management

| Attribute | Detail |
|---|---|
| **Module ID** | `USR` |
| **Layer** | Domain |
| **Responsibility** | Manage the complete lifecycle of user identities, profiles, preferences, and account state. |

**Core Features & Sub-Modules**
- User registration (self-service, admin-created, invitation-based)
- Profile management (avatar, bio, contact info, social links)
- Account status workflow (active, suspended, deactivated, deleted)
- Email verification and change verification
- Account deletion (soft-delete with 30-day grace period)
- User preference storage (locale, theme, notification settings)
- Merge/duplicate detection
- Bulk user import/export (CSV, JSON)
- Account recovery flow
- Device management (trusted devices, active sessions list)

**Dependencies**
- `AUTH` — credential management, login linkage
- `AUTHZ` / `RBAC` — authorization policies for user operations
- `AUD` — account lifecycle audit trail
- `NOT` — welcome emails, verification emails, account alerts

**Data Entities**
- `users` — core identity (email, username, display_name, avatar_url, status, locale, timezone)
- `user_profiles` — bio, website, social_links (JSON), phone, address
- `user_preferences` — notification_channels, theme, language, privacy_settings (JSONB)
- `user_devices` — device_id, name, last_ip, last_seen_at, is_trusted
- `user_verification_tokens` — type (email/phone/password_reset), token_hash, expires_at
- `user_consent_logs` — consent_type, version, granted_at, ip
- `user_deletion_requests` — requested_at, grace_period_end, status, reason
- `user_merge_audit` — primary_id, merged_id, fields_merged, performed_by

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `USR.REGISTER(email, password, profile)` | Create account |
| Command | `USR.UPDATE_PROFILE(user_id, profile_data)` | Modify profile |
| Command | `USR.SUSPEND(user_id, reason, duration)` | Temporary suspension |
| Command | `USR.DELETE(user_id, reason)` | Initiate deletion |
| Command | `USR.COMPLETE_DELETION(user_id)` | Irreversible purge |
| Command | `USR.MERGE(primary_id, secondary_id)` | Merge duplicate accounts |
| Query | `USR.GET_BY_ID(user_id)` | Full profile (authorized) |
| Query | `USR.SEARCH(filters, page)` | User search for admin |
| Event | `user.created` | Account registered |
| Event | `user.updated` | Profile changed |
| Event | `user.suspended` | Account suspended |
| Event | `user.reactivated` | Suspension lifted |
| Event | `user.deletion_requested` | Deletion initiated |
| Event | `user.deletion_completed` | Account purged |
| Event | `user.email_verified` | Email confirmation |
| REST | `GET /api/v1/users/me` | Current user profile |
| REST | `PUT /api/v1/users/me/profile` | Update own profile |
| REST | `GET /api/v1/users/{id}` | Admin: view user |
| REST | `POST /api/v1/users/{id}/suspend` | Admin: suspend |

**State Machine**

```
REGISTERED → [VERIFY] → ACTIVE → [SUSPEND] → SUSPENDED → [REACTIVATE] → ACTIVE
                                → [DEACTIVATE] → DEACTIVATED → [REACTIVATE] → ACTIVE
                                → [REQUEST_DELETE] → DELETION_PENDING → [COMPLETE] → DELETED
                                                                         ↓ [expire]
                                                                       ACTIVE (restored)
```

**Error Handling**
| Error | Strategy |
|---|---|
| Duplicate email | Return 409; check uniqueness at DB level (unique index) |
| Email already verified | Idempotent; return 200 with current verification state |
| Account not deletable (has active orders) | Return 409 with `active_orders_count` in body |
| Consent version mismatch | Return 428 Precondition Required; prompt re-consent |

**Performance**
- Profile queries cached in Redis (10-minute TTL) for read-heavy workloads
- Soft-delete with indexed `deleted_at` column; no table scans after 90 days
- Bulk import streamed via CSV with 1,000-row batch commit
- Search on email/username backed by trigram index (pg_trgm)

**Security**
- Email changes require verification of both old and new email
- Email and phone masked in audit logs (`j***@domain.com`)
- GDPR/CCPA: export and deletion APIs with full data mapping manifest
- Rate limit registration: 3 per IP per hour
- Admin account suspension cannot target last SuperAdmin

**Integration Points**
- Webhook: `user.created` → CRM, Mailchimp, Slack (new sales lead)
- GraphQL: Mutations nested under `currentUser` for self-service
- Admin UI: User detail view with order/support/dispute history panes
- SSO: User can be created via OAuth first-login flow

---

### 2.5 SEL — Seller Management

| Attribute | Detail |
|---|---|
| **Module ID** | `SEL` |
| **Layer** | Domain |
| **Responsibility** | Manage seller onboarding, verification, store configuration, performance metrics, and tier progression. |

**Core Features & Sub-Modules**
- Seller application and onboarding workflow
- KYC verification (identity, business registration, tax ID)
- Store profile and branding (logo, banner, description, policies)
- Seller tier/program system (Bronze → Silver → Gold → Platinum)
- Performance dashboard (sales, rating, dispute rate)
- Payout configuration (bank account, preferred currency, threshold)
- Seller capabilities (allowed product types, max listing count)
- Vacation mode / store closure scheduling
- Product approval workflow (auto-approve vs manual review per tier)

**Dependencies**
- `USR` — user identity linking
- `RBAC` — seller role assignment
- `MKT` — marketplace membership
- `WAL` — seller wallet creation
- `ORD` — sales data for performance metrics
- `REV` — seller rating aggregation
- `DSP` — dispute rate calculation

**Data Entities**
- `sellers` — user_id, store_name, slug, status, tier, joined_at
- `seller_verifications` — type (identity/business/tax), document_url, status, verified_at, verified_by
- `seller_profiles` — description, policies (JSONB), logo_url, banner_url, social_links
- `seller_tiers` — name, requirements (JSONB), benefits (JSONB)
- `seller_payout_settings` — bank_account (encrypted), preferred_currency, min_payout
- `seller_capabilities` — max_products, product_types_allowed, auto_approve
- `seller_vacation_schedules` — start, end, message, hide_products
- `seller_performance_snapshots` — period, sales_count, revenue, avg_rating, dispute_rate

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `SEL.APPLY(user_id, application_data)` | Submit seller application |
| Command | `SEL.APPROVE(seller_id, admin_id)` | Approve seller |
| Command | `SEL.VERIFY(seller_id, verification_type, document)` | Submit verification doc |
| Command | `SEL.UPDATE_TIER(seller_id, new_tier)` | Tier promotion/demotion |
| Command | `SEL.SET_VACATION(seller_id, schedule)` | Enable vacation mode |
| Command | `SEL.UPDATE_PAYOUT(seller_id, bank_details)` | Change payout info |
| Query | `SEL.GET_PERFORMANCE(seller_id, period)` | Aggregated metrics |
| Event | `seller.created` | New seller onboarded |
| Event | `seller.approved` | Application accepted |
| Event | `seller.verified` | KYC stage completed |
| Event | `seller.tier_changed` | Tier upgrade/downgrade |
| Event | `seller.vacation.started` | Vacation mode on |
| Event | `seller.vacation.ended` | Vacation mode off |

**State Machine**

```
APPLICATION_SUBMITTED → [REVIEW] → UNDER_REVIEW → [APPROVE] → ACTIVE
                        [REJECT] → REJECTED                     → [SUSPEND] → SUSPENDED
                                                                → [VACATION] → ON_VACATION
                                                                → [CLOSE] → CLOSED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Duplicate store name | Return 409; check uniqueness case-insensitively |
| KYC document re-submit | Allow; version documents with sequence counter |
| Tier promotion not met | Return 422 with unmet requirements list |
| Vacation conflicts with active orders | Warn but allow; existing orders fulfilled normally |

**Performance**
- Performance snapshots materialized nightly via batch job
- Seller search indexed on `store_name` trigram + `slug` b-tree
- Tier calculations run on-demand with cached thresholds
- KYC document storage via S3/CDN with pre-signed URLs (60-minute expiry)

**Security**
- Payout bank details encrypted at rest (AES-256-GCM with KMS key rotation)
- KYC documents access-controlled: seller + authorized admin + compliance officer
- Tier changes audit-logged with before/after values
- Vacation mode hides products from search but does not cancel active orders

**Integration Points**
- KYC service: Third-party provider (Jumio, Onfido) via webhook callback
- Payout: Banking integration via Plaid / Stripe Connect
- Admin UI: Seller management console with verification workflow
- Marketplace: Seller list for marketplace assignment

---

### 2.6 MKT — Marketplace

| Attribute | Detail |
|---|---|
| **Module ID** | `MKT` |
| **Layer** | Domain |
| **Responsibility** | Define and manage the marketplace structure: categories, collections, featured placements, and taxonomy hierarchy. |

**Core Features & Sub-Modules**
- Category tree management (unbounded depth, materialized path)
- Collections / curated lists (seasonal, promotional, thematic)
- Featured product slots (homepage, category pages)
- Marketplace-level settings (commission rates, listing fees)
- Tax category management (per region, per product type)
- Region/locale-specific visibility rules
- Product placement and ranking configuration
- Marketplace health dashboard (active listings, conversion rates)

**Dependencies**
- `SEL` — seller participation
- `CAT` — product catalog within marketplace
- `ORD` — transaction data for marketplace metrics
- `ANL` — aggregated marketplace analytics
- `CMS` — landing page content integration

**Data Entities**
- `marketplace_categories` — id, parent_id, name, slug, description, icon, image, position, path (materialized)
- `marketplace_collections` — name, slug, type (manual/auto), query_rules (JSONB), start_at, end_at
- `collection_products` — collection_id, product_id, position, added_by
- `featured_slots` — location (homepage/category/search), resource_type, resource_id, start_at, end_at, priority
- `marketplace_settings` — key, value (JSONB), description
- `tax_categories` — name, rate, region (country + state), product_type_filter
- `category_seller_restrictions` — category_id, seller_tier_min

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `MKT.CREATE_CATEGORY(parent_id, name, metadata)` | Create category |
| Command | `MKT.MOVE_CATEGORY(category_id, new_parent_id)` | Re-parent |
| Command | `MKT.CREATE_COLLECTION(name, rules)` | Create auto collection |
| Command | `MKT.SET_FEATURED(resource, slot, schedule)` | Set placement |
| Command | `MKT.UPDATE_COMMISSION(category_id, rate)` | Change commission |
| Query | `MKT.GET_CATEGORY_TREE(root_id)` | Full subtree |
| Query | `MKT.GET_FEATURED(slot, locale)` | Active placements |
| Event | `marketplace.category.created` | New category |
| Event | `marketplace.category.moved` | Category re-parented |
| Event | `marketplace.collection.activated` | Collection went live |
| Event | `marketplace.featured.updated` | Placement changed |
| Event | `marketplace.commission.changed` | Rate update |

**Error Handling**
| Error | Strategy |
|---|---|
| Category depth exceeded | Reject with max depth message (configurable, default 10) |
| Circular parent reference | Validate with ancestor check before update |
| Collection with auto-rules conflict | Validate rules for mutual exclusivity |
| Featured slot overlap | Allow but assign priority; lower priority hidden |

**Performance**
- Category tree cached in Redis as serialized tree (rebuilt on mutation)
- Materialized path enables single-query subtree retrieval
- Featured slots resolved via Redis sorted sets (score = priority + expiry)
- Collection membership computed via query rules engine (materialized every 5 min)

**Security**
- Category management restricted to `marketplace:manage` permission
- Featured slots audited; require approval workflow for paid placements
- Commission rate changes logged in `AUD` with effective date
- Restricted categories (e.g., adult, regulated) require additional seller verification

**Integration Points**
- Admin UI: Drag-and-drop category tree editor
- Search: Category filter facets driven by `MKT` tree
- CMS: Collection pages rich-text editable via `CMS`
- Product Catalog: Products assigned to leaf categories

---

### 2.7 CAT — Product Catalog

| Attribute | Detail |
|---|---|
| **Module ID** | `CAT` |
| **Layer** | Domain |
| **Responsibility** | Manage the lifecycle of digital product listings including creation, pricing, inventory, variants, media, and publishing workflow. |

**Core Features & Sub-Modules**
- Product CRUD with rich metadata
- Variant management (multiple file types, regions, licenses)
- Digital asset management (file uploads, previews, samples)
- Pricing engine (base, tiered, volume, subscription)
- Inventory tracking (download limits, concurrent seat limits)
- Publishing workflow (draft → review → published → archived)
- Bulk product operations (import/export, price updates)
- Product relationships (upsells, cross-sells, bundles)
- Licensing schema management (single, multi-seat, enterprise, custom)
- Version history for product descriptions and media

**Dependencies**
- `SEL` — seller ownership
- `MKT` — category assignment
- `SRCH` — product indexing
- `CPN` — coupon eligibility
- `AFF` — affiliate product linking
- `REV` — product rating aggregation
- `ORD` — sales data for popularity

**Data Entities**
- `products` — id, seller_id, category_id, type, name, slug, description, short_description, status, visibility, featured_image, tags (JSONB)
- `product_variants` — id, product_id, name, sku, price, compare_at_price, license_type, is_active
- `product_media` — id, variant_id, type (preview/sample/full), url, file_size, mime_type, sort_order
- `product_pricing_tiers` — id, variant_id, min_quantity, max_quantity, unit_price
- `product_inventory` — variant_id, total_units, sold_units, download_limit, concurrent_limit
- `product_relationships` — product_id, related_product_id, type (upsell/cross_sell/bundle)
- `product_versions` — id, product_id, version, changelog, snapshot (JSONB), created_by
- `product_custom_fields` — product_id, field_name, field_type, required, options (JSONB)
- `tags` — id, name, slug, usage_count

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `CAT.CREATE_PRODUCT(seller_id, data)` | New listing |
| Command | `CAT.UPDATE_PRODUCT(product_id, data)` | Edit listing |
| Command | `CAT.PUBLISH(product_id)` | Make visible |
| Command | `CAT.ARCHIVE(product_id)` | Remove from sale |
| Command | `CAT.DUPLICATE(product_id)` | Clone listing |
| Command | `CAT.UPDATE_INVENTORY(variant_id, delta)` | Adjust stock |
| Command | `CAT.BULK_PRICE_UPDATE(product_ids, operation, value)` | Mass update |
| Query | `CAT.GET_BY_SLUG(slug)` | Public product page |
| Query | `CAT.SEARCH_SELLER_PRODUCTS(seller_id, filters)` | Seller's own listings |
| Event | `product.created` | New product |
| Event | `product.updated` | Product modified |
| Event | `product.published` | Went live |
| Event | `product.archived` | Removed from sale |
| Event | `product.inventory.changed` | Stock level change |
| Event | `product.price.changed` | Price modification |

**State Machine**

```
DRAFT → [SUBMIT] → PENDING_REVIEW → [APPROVE] → PUBLISHED → [ARCHIVE] → ARCHIVED
                    ↓ [REJECT]                  ↓ [UNPUBLISH]
                 DRAFT                      DRAFT
PUBLISHED → [SCHEDULE_UNPUBLISH] → UNPUBLISHED_SCHEDULED → [DATE_HIT] → UNPUBLISHED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Slug conflict | Append UUID suffix; notify seller |
| Seller max product limit | Reject with current/max count |
| Published product with 0 variants | Allow but flag in seller dashboard |
| Category mismatch (leaf required) | Reject; return allowed leaf categories |
| File size exceeds limit | Return 413; indicate max size in bytes |

**Performance**
- Product read-model cached in Redis (keyed by product_id, 5-min TTL)
- Product listing queries use materialized `product_search_view` refreshed every 5 min
- Media served via CDN (CloudFront/Cloudflare) with origin shield
- Variant pricing pre-computed at write time; no runtime calculation
- Bulk operations use Celery task with progress tracking via Redis

**Security**
- Product visibility respects `seller_vacation_mode` (auto-hide)
- Draft products accessible only by seller and admin
- File download URLs are pre-signed (1-hour expiry) regardless of storage backend
- Seller may only edit own products (enforced at service layer + DB policy)
- Archived products retain data for 90 days then soft-deleted

**Integration Points**
- Search: Product publish/update triggers re-index to Elasticsearch
- Delivery: File upload triggers virus scan via `DEL` (ClamAV)
- Affiliate: Product metadata exposed to affiliate link generator
- Admin: Product approval queue with diff view between versions

---

### 2.8 SRCH — Search Engine

| Attribute | Detail |
|---|---|
| **Module ID** | `SRCH` |
| **Layer** | Application |
| **Responsibility** | Provide fast, relevant, and scalable full-text search across products, sellers, and marketplace content. |

**Core Features & Sub-Modules**
- Full-text search with tokenization, stemming, and synonym expansion
- Faceted search (category, price range, rating, tags, license type)
- Geospatial search for location-based sellers (future)
- Typo tolerance (fuzzy matching with edit distance)
- Autocomplete / search-as-you-type
- Custom ranking (freshness, sales velocity, seller rating, relevance score)
- Saved searches and alerts
- Search analytics (popular queries, zero-result queries, click tracking)
- Multi-language support (analyzer per locale)
- Boolean operators, phrase search, field weighting

**Dependencies**
- `CAT` — product index source
- `SEL` — seller index source
- `MKT` — category taxonomy
- `ANL` — search analytics consumption

**Data Entities**
- `search_index_config` — index_name, analyzer, field_mappings, synonyms (JSONB)
- `search_saved_queries` — user_id, query_string, filters (JSONB), notify_on_new
- `search_analytics_raw` — query, timestamp, result_count, clicked_product, session_id
- `search_synonyms` — term, synonyms (text[]), locale

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `SRCH.INDEX(resource_type, resource_id)` | Index/re-index single entity |
| Command | `SRCH.BULK_INDEX(resource_type, ids[])` | Batch index |
| Command | `SRCH.REMOVE(resource_type, resource_id)` | De-index |
| Command | `SRCH.CLEAR_INDEX(index_name)` | Full re-index trigger |
| Query | `SRCH.SEARCH(query, filters, sort, page)` | Main search endpoint |
| Query | `SRCH.AUTOCOMPLETE(prefix, locale)` | Suggestion |
| Query | `SRCH.FACETS(query, field)` | Facet counts |
| Event | `search.index.updated` | Index refresh requested |
| Event | `search.index.completed` | Bulk re-index done |

**Error Handling**
| Error | Strategy |
|---|---|
| Elasticsearch cluster unavailable | Fall back to PostgreSQL `tsvector` search with degraded quality |
| Index not found | Auto-create on first write with stored mapping template |
| Query parse error | Sanitize query; fall back to simple match |
| Analyzer mismatch for locale | Default to `standard` analyzer; log warning |

**Performance**
- Target P95 search latency < 100 ms
- Autocomplete responses < 30 ms via edge n-gram completion suggester
- Index refresh interval: 5 seconds for near-real-time balance
- Bulk indexing: 5,000 documents per batch with refresh disabled
- Query result cache (TTL: 60 seconds) for identical queries
- Hot (recent/popular) indices on fast storage; cold indices with replica reduction

**Security**
- Indexed data excludes PII (email, phone, addresses)
- Product visibility filter applied at query time (hide draft/archived/vacation)
- Search endpoint rate-limited: 30 req/min per IP (unauthenticated), 120 req/min (authenticated)
- Field-level restrictions: certain metadata only searchable by admin index

**Integration Points**
- GraphQL: `Query.search` resolver delegates to `SRCH` with facet aggregation
- Product lifecycle: `product.published` → `SRCH.INDEX`
- Admin: Full re-index button with progress bar and ETA
- Analytics: Raw search queries streamed to ClickHouse via Kafka

---

### 2.9 CART — Shopping Cart

| Attribute | Detail |
|---|---|
| **Module ID** | `CART` |
| **Layer** | Application |
| **Responsibility** | Manage temporary product collections for authenticated and anonymous users prior to checkout. |

**Core Features & Sub-Modules**
- Guest cart (device fingerprint + localStorage) → user cart on login (merge)
- Add, remove, update quantity of line items
- Cart-level and item-level notes
- Cart expiry (abandoned cart recovery)
- Saved-for-later / wishlist functionality
- Price and availability validation on read
- Coupon application (shallow validation)
- Multi-currency support with display price conversion
- Cart snapshot for price lock guarantee
- Cart merge strategy on login (keep newer items, respect timestamps)

**Dependencies**
- `CAT` — product data, pricing, inventory availability
- `CPN` — coupon code (preliminary validation)
- `CHK` — checkout consumes cart
- `NOT` — abandoned cart reminder

**Data Entities**
- `carts` — id, user_id (nullable), session_id, status (active/abandoned/converted/expired), currency, created_at, updated_at
- `cart_items` — id, cart_id, variant_id, quantity, unit_price (snapshot), notes, added_at
- `cart_coupons` — cart_id, coupon_id, code, discount_amount, applied_at
- `cart_saved_for_later` — user_id, variant_id, saved_at

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `CART.ADD_ITEM(user/session, variant_id, qty, notes)` | Add to cart |
| Command | `CART.UPDATE_ITEM(cart_id, item_id, qty)` | Change quantity |
| Command | `CART.REMOVE_ITEM(cart_id, item_id)` | Remove line item |
| Command | `CART.APPLY_COUPON(cart_id, code)` | Apply discount |
| Command | `CART.REMOVE_COUPON(cart_id)` | Remove discount |
| Command | `CART.MERGE(guest_cart_id, user_cart_id)` | Merge on login |
| Command | `CART.CLEAR_ABANDONED()` | Scheduled cleanup |
| Query | `CART.GET_ACTIVE(user/session)` | Current cart |
| Query | `CART.GET_SAVED(user_id)` | Wishlist |
| Event | `cart.item.added` | Item added |
| Event | `cart.item.removed` | Item removed |
| Event | `cart.coupon.applied` | Coupon attached |
| Event | `cart.abandoned` | No activity for threshold |
| Event | `cart.converted` | Cart became order |
| REST | `GET /api/v1/cart` | Current cart |
| REST | `POST /api/v1/cart/items` | Add item |
| REST | `POST /api/v1/cart/merge` | Merge guest to user |

**Error Handling**
| Error | Strategy |
|---|---|
| Item out of stock | Return 409; include restock_eta if available |
| Price changed | Return 200 with warning header `X-Price-Changed: true`; show old vs new |
| Coupon expired | Return 410; suggest alternative available coupons |
| Cart locked (in checkout) | Return 423; provide checkout session ID |
| Guest merge conflicts | Timestamp-based: newer item kept, older archived |

**Performance**
- Guest cart persisted in Redis (24-hour TTL); user cart in PostgreSQL
- Price snapshot taken at add-time, re-validated at checkout
- Cart read served from Redis L2 cache with pub/sub invalidation
- Abandoned cart cleanup: batch delete Redis keys + PostgreSQL rows older than 30 days

**Security**
- Cart access restricted to owner or admin
- Guest cart ID is a UUID v4 (unguessable)
- Price snapshot immutable; modifications only through checkout re-validation
- Coupon validation is shallow (full validation happens in `CHK`)

**Integration Points**
- Checkout: `GET /api/v1/checkout` consumes active cart
- Email: Abandoned cart recovery triggered by `cart.abandoned` after 1 hour
- Admin: View any user's cart for support/debugging
- Analytics: Cart abandonment rate funnel

---

### 2.10 CHK — Checkout

| Attribute | Detail |
|---|---|
| **Module ID** | `CHK` |
| **Layer** | Application |
| **Responsibility** | Orchestrate the purchase flow: validate cart, collect buyer information, process payment, and create order. |

**Core Features & Sub-Modules**
- Multi-step checkout form (review → info → payment → confirmation)
- Price lock guarantee (prevents price changes during checkout window)
- Full coupon validation (eligibility, stackability, usage limits)
- Tax calculation (per jurisdiction, product type, buyer location)
- Payment method selection and processing
- Guest checkout (account creation optional post-purchase)
- Address validation and auto-complete
- Order preview with all fees (subtotal, discount, tax, total)
- Checkout abandonment handling
- Split payment support (wallet + gateway)

**Dependencies**
- `CART` — cart data and item snapshot
- `PAY` — payment processing
- `WAL` — wallet balance for split payments
- `CPN` — coupon validation
- `ORD` — order creation
- `CAT` — price re-validation
- `NOT` — confirmation emails (triggered after order)

**Data Entities**
- `checkout_sessions` — id, cart_id, user_id, status (pending/completed/failed/expired), price_lock_until, currency, subtotal, discount, tax, total, metadata (JSONB)
- `checkout_payments` — id, session_id, method, amount, status, gateway, transaction_id
- `checkout_audit_log` — session_id, step, action, data (JSONB), timestamp

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `CHK.INITIATE(cart_id, user_id)` | Create session with price lock |
| Command | `CHK.UPDATE_INFO(session_id, buyer_info)` | Set buyer details |
| Command | `CHK.CALCULATE_TAX(session_id)` | Compute tax |
| Command | `CHK.SELECT_PAYMENT(session_id, method)` | Choose payment |
| Command | `CHK.PLACE_ORDER(session_id)` | Finalize purchase |
| Command | `CHK.CANCEL(session_id, reason)` | Abort checkout |
| Query | `CHK.GET_PREVIEW(session_id)` | Current estimate |
| Event | `checkout.started` | Checkout initiated |
| Event | `checkout.payment.selected` | Payment method chosen |
| Event | `checkout.completed` | Order placed successfully |
| Event | `checkout.failed` | Order failed (payment declined, etc.) |
| Event | `checkout.abandoned` | Session expired |
| Webhook | `POST /webhooks/checkout/updated` | For gateways (async) |

**Error Handling**
| Error | Strategy |
|---|---|
| Price lock expired | Re-validate prices; return 409 with new total; require confirmation |
| Payment declined | Return 402; suggest alternative method; preserve session |
| Cart modified during checkout | Return 409; require re-initiation if items changed |
| Tax calculation timeout | Fall back to flat rate; flag for manual review |
| Inventory insufficient | Release held stock; return 409 with affected items |

**Performance**
| Aspect | Strategy |
|---|---|
| Price lock duration | 15 minutes; extendable once (+15 min) |
| Tax calculation | Cached per location/product for 24 hours |
| Payment idempotency key | Required on `CHK.PLACE_ORDER` to prevent double charge |
| Session expiry | 30 minutes from initiation; cleanup via scheduled task |

**Security**
- Idempotency key enforced at database level (unique constraint)
- Price lock prevents race conditions between cart update and checkout
- Payment instrument data never touches application servers (tokenized via gateway)
- Checkout session ID is UUID v4, bound to single user/session
- Full audit log of every step for dispute resolution

**Integration Points**
- Payments: Delegates to `PAY` for gateway processing
- Orders: `ORD.CREATE` called on successful `CHK.PLACE_ORDER`
- Notifications: `checkout.completed` triggers receipt email
- Analytics: Funnel tracking (initiate → pay → complete)

---

### 2.11 ORD — Orders

| Attribute | Detail |
|---|---|
| **Module ID** | `ORD` |
| **Layer** | Domain |
| **Responsibility** | Manage the complete lifecycle of purchase orders from creation through fulfillment, cancellation, returns, and archival. |

**Core Features & Sub-Modules**
- Order creation from checkout session
- Order item management with line-level status tracking
- Order lifecycle (pending → processing → completed → archived)
- Partial and full cancellation
- Refund processing (partial/full, per line item)
- Invoice generation (PDF, printable HTML)
- Order notes (internal/seller/buyer visible)
- Reorder / clone order functionality
- Bulk order operations (status updates, exports)
- eSIM-specific: ICCID tracking, activation status, profile assignment
- Order splitting (multi-seller scenarios)

**Dependencies**
- `CHK` — checkout session data
- `PAY` — payment transactions
- `WAL` — wallet refunds
- `ESC` — escrow release schedule
- `DEL` — digital delivery trigger
- `REV` — review eligibility
- `DSP` — dispute context
- `NOT` — order confirmation, shipping/fulfillment updates

**Data Entities**
- `orders` — id, user_id, checkout_session_id, status, currency, subtotal, discount, tax, total, paid_at, fulfilled_at, metadata (JSONB)
- `order_items` — id, order_id, variant_id, product_name (snapshot), unit_price, quantity, line_total, status, delivery_status
- `order_notes` — id, order_id, author_id, visibility (public/internal), content, created_at
- `order_status_history` — order_id, from_status, to_status, changed_by, reason, timestamp
- `order_invoices` — order_id, invoice_number, url, generated_at
- `order_cancellations` — order_id, requested_by, reason, refund_amount, refund_status, approved_by
- `order_iccid_assignments` — order_id, item_id, iccid, activation_status, profile_url

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `ORD.CREATE(checkout_session_id)` | Create order from checkout |
| Command | `ORD.UPDATE_STATUS(order_id, status, reason)` | Advance lifecycle |
| Command | `ORD.CANCEL(order_id, reason)` | Request cancellation |
| Command | `ORD.APPROVE_CANCEL(order_id)` | Approve and trigger refund |
| Command | `ORD.REFUND(order_id, items[], amount)` | Partial refund |
| Command | `ORD.GENERATE_INVOICE(order_id)` | Produce PDF |
| Query | `ORD.GET(order_id)` | Full order with items |
| Query | `ORD.LIST(user_id, filters)` | Buyer order history |
| Query | `ORD.LIST_SELLER(seller_id, filters)` | Seller order queue |
| Event | `order.created` | New order placed |
| Event | `order.status.changed` | Status transition |
| Event | `order.cancellation.requested` | Cancel initiated |
| Event | `order.refunded` | Refund processed |
| Event | `order.fulfilled` | All items delivered |
| Event | `order.invoice.generated` | Invoice available |
| REST | `GET /api/v1/orders/{id}` | Order detail |
| REST | `POST /api/v1/orders/{id}/cancel` | Request cancel |
| REST | `POST /api/v1/orders/{id}/refund` | Admin: process refund |

**State Machine**

```
PENDING → [CONFIRM] → CONFIRMED → [PROCESS] → PROCESSING → [DELIVER] → COMPLETED → [ARCHIVE] → ARCHIVED
    ↓ [CANCEL]                  ↓ [CANCEL]                 ↓ [PARTIAL_DELIVER]
  CANCELLED                  CANCELLED                  PARTIALLY_COMPLETED → [FULL_DELIVER] → COMPLETED
COMPLETED → [REFUND] → REFUNDED
COMPLETED → [CANCEL] → CANCELLED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Duplicate order (idempotency) | Return 409; return existing order ID |
| Cancel past grace period | Reject; provide policy reference (24-hour window) |
| Refund exceeds paid amount | Reject with available refundable amount |
| Order not found | Return 404; search by order_id or invoice number |
| Invalid status transition | Return 422; list valid transitions from current state |

**Performance**
| Aspect | Strategy |
|---|---|
| Order read-model | Cached in Redis; invalidated on status change |
| Invoice generation | Async via Celery; PDF stored in S3 |
| Order listing for buyers | Paginated with cursor; indexed on `user_id + created_at` |
| Seller order queue | Partitioned by seller_id; real-time via WebSocket for new orders |
| Order export | Streamed as CSV via Celery task; emailed on completion |

**Security**
- Buyers can only view own orders; sellers view only orders containing their products
- Invoice numbers sequentially generated but non-guessable (obfuscated prefix + check digit)
- Cancellation requests require confirmation via email for high-value orders (> $500)
- Refund approvals require dual authorization above threshold ($1,000+)
- Order data retained per regulatory requirements (7 years), then anonymized

**Integration Points**
- Delivery: `order.fulfilled` triggers digital asset delivery
- Wallet: Cancellation/refund triggers wallet credit
- Analytics: Order events streamed to ClickHouse
- Accounting: Order data exported to ERP (QuickBooks/Xero) via nightly batch
- Admin: Order detail view with timeline, note, and action buttons

---

### 2.12 DEL — Digital Delivery

| Attribute | Detail |
|---|---|
| **Module ID** | `DEL` |
| **Layer** | Domain |
| **Responsibility** | Securely deliver digital products (files, eSIM profiles, license keys, API credentials) to buyers after purchase. |

**Core Features & Sub-Modules**
- File delivery (download links, zip archives, multi-part files)
- eSIM profile delivery and activation
- License key generation and delivery
- API credential provisioning
- Delivery channel management (download, email, SMS, webhook)
- Access expiration and download limit enforcement
- Secure file storage with encryption at rest
- Virus scanning integration
- CDN origin pull for large files
- Preview/sample delivery (watermarked, time-limited)
- Delivery receipt tracking (download_acknowledged)

**Dependencies**
- `ORD` — order fulfillment trigger
- `CAT` — product media, file metadata
- `WAL` — paid status verification
- `AUD` — delivery audit trail
- `NOT` — delivery notification (email with download link)

**Data Entities**
- `delivery_records` — id, order_item_id, variant_id, delivery_type, status, delivered_at, expires_at, max_downloads, download_count
- `delivery_files` — id, delivery_id, file_path (storage key), original_name, mime_type, file_size, checksum (SHA-256), encryption_key_id
- `delivery_file_downloads` — id, file_id, ip_address, user_agent, downloaded_at
- `delivery_esim_profiles` — id, order_item_id, iccid, activation_code, profile_url, status (pending/active/suspended/revoked), activated_at
- `delivery_license_keys` — id, order_item_id, license_key, platform, expires_at, activation_limit, activations_used
- `delivery_email_logs` — id, delivery_id, recipient, status, sent_at, opened_at

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `DEL.DELIVER(order_item_id)` | Initiate delivery for item |
| Command | `DEL.DELIVER_ORDER(order_id)` | Deliver all items |
| Command | `DEL.GENERATE_DOWNLOAD_URL(delivery_id)` | Pre-signed URL |
| Command | `DEL.ACTIVATE_ESIM(delivery_id)` | Activate profile |
| Command | `DEL.REVOKE(delivery_id, reason)` | Revoke access |
| Query | `DEL.GET_DELIVERIES(order_id)` | All deliveries for order |
| Query | `DEL.GET_DOWNLOAD_HISTORY(delivery_id)` | Download log |
| Event | `delivery.created` | Delivery prepared |
| Event | `delivery.completed` | Successfully delivered |
| Event | `delivery.failed` | Delivery error |
| Event | `delivery.downloaded` | File was downloaded |
| Event | `delivery.esim.activated` | eSIM enabled |
| REST | `GET /api/v1/deliveries/{id}/download` | Download redirect |
| REST | `POST /api/v1/deliveries/{id}/re-send` | Re-send email |

**Error Handling**
| Error | Strategy |
|---|---|
| File not found on storage | Retry from backup region; else fail and alert operator |
| Download limit exceeded | Return 429; include limit and reset info |
| Delivery expired | Return 410; offer to re-enable (seller configurable) |
| Virus detected | Block delivery; notify seller, refund buyer |
| eSIM activation failed | Retry with exponential backoff (3 attempts); escalate |

**Performance**
| Aspect | Strategy |
|---|---|
| File upload | Multipart upload to S3 with presigned URLs (direct-to-S3, bypass app server) |
| Download delivery | 302 redirect to CDN URL; app server never buffers file bytes |
| Large files (>1 GB) | Streamed via chunked transfer; CDN edge caching |
| Concurrent downloads | Per-user rate limit: 5 concurrent downloads |
| Zip archive generation | Async via Celery for multi-file bundles |

**Security**
- All files encrypted at rest using server-side encryption (AES-256)
- Download URLs pre-signed with 1-hour expiry, single-use recommended
- Download link rotated on each access (old link invalidated)
- Virus scanning via ClamAV (or cloud equivalent) before delivery release
- eSIM profiles: activation codes delivered separately from profile URL
- Access logs maintained for compliance (retention: 3 years)

**Integration Points**
- Storage: AWS S3 / MinIO with IAM role-based access
- CDN: CloudFront / Cloudflare with origin access identity
- Antivirus: ClamAV REST service; webhook callback for scan results
- eSIM: Carrier API (HTTP) for profile management
- Email: Transactional email (SendGrid/SES) for download links

---

### 2.13 WAL — Wallet

| Attribute | Detail |
|---|---|
| **Module ID** | `WAL` |
| **Layer** | Domain |
| **Responsibility** | Manage digital wallets for buyers and sellers, tracking balances, transactions, and holds. |

**Core Features & Sub-Modules**
- Wallet creation per user (buyer wallet, seller wallet)
- Multi-currency wallet support
- Balance inquiry and transaction history
- Credit/debit operations with double-entry accounting
- Wallet holds (earmarked funds for pending orders/escrow)
- Auto top-up configuration (threshold-based)
- Wallet statements (monthly/yearly PDF)
- Transfer between wallets (internal)
- Wallet freezing/unfreezing (security/compliance)
- Sub-ledger for fee tracking (platform fees, commission deductions)

**Dependencies**
- `USR` — user-wallet linkage
- `PAY` — funding via payment gateway
- `ORD` — order payments, refunds
- `ESC` — escrow holds and releases
- `WDR` — withdrawal source
- `AUD` — all financial transactions audited

**Data Entities**
- `wallets` — id, user_id, type (buyer/seller/commission), currency, balance, hold_balance, status (active/frozen/closed), version (optimistic lock)
- `wallet_transactions` — id, wallet_id, type (credit/debit/hold/release), amount, balance_before, balance_after, reference_type, reference_id, description, metadata (JSONB)
- `wallet_holds` — id, wallet_id, amount, reference_type, reference_id, status (active/released/expired), expires_at
- `wallet_topup_rules` — id, wallet_id, threshold, topup_amount, payment_method_id, is_active
- `wallet_statements` — id, wallet_id, period_start, period_end, generated_at, url

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `WAL.CREATE(user_id, type, currency)` | Open wallet |
| Command | `WAL.CREDIT(wallet_id, amount, reference, description)` | Add funds |
| Command | `WAL.DEBIT(wallet_id, amount, reference, description)` | Deduct funds |
| Command | `WAL.HOLD(wallet_id, amount, reference, expires_at)` | Earmark funds |
| Command | `WAL.RELEASE(wallet_id, hold_id)` | Un-hold funds |
| Command | `WAL.TRANSFER(from_wallet, to_wallet, amount, reference)` | Internal transfer |
| Command | `WAL.FREEZE(wallet_id, reason)` | Suspend operations |
| Command | `WAL.UNFREEZE(wallet_id)` | Resume operations |
| Query | `WAL.GET_BALANCE(wallet_id)` | Current available balance |
| Query | `WAL.GET_TRANSACTIONS(wallet_id, filters, page)` | Paginated history |
| Event | `wallet.created` | New wallet |
| Event | `wallet.credited` | Funds added |
| Event | `wallet.debited` | Funds deducted |
| Event | `wallet.hold.placed` | Hold created |
| Event | `wallet.hold.released` | Hold lifted |
| Event | `wallet.balance.low` | Below threshold |
| Event | `wallet.frozen` | Wallet disabled |
| Event | `wallet.unfrozen` | Wallet re-enabled |

**Error Handling**
| Error | Strategy |
|---|---|
| Insufficient balance | Return 422; provide available + hold amounts |
| Optimistic lock conflict (version mismatch) | Retry transaction (max 3 attempts) |
| Wallet frozen | Return 423; include freeze reason and support contact |
| Currency mismatch on transfer | Return 422; offer conversion if exchange rate service available |
| Hold expired | Auto-release via scheduled job; no error to caller |

**Performance**
| Aspect | Strategy |
|---|---|
| Balance query | Cached in Redis with 30-second TTL; invalidated on write |
| Transaction insert | Batch committed every 100ms via WAL buffer |
| Statement generation | Monthly Celery task; PDF in S3 with 7-year retention |
| Balance consistency | Optimistic locking via `version` column; retry on conflict |

**Security**
- All wallet operations require explicit authorization (buyer/seller scope separation)
- Double-entry accounting: every credit has a corresponding debit in another wallet
- Wallet holds prevent balance from being spent while escrow/pending orders exist
- Top-up rules require MFA confirmation for enablement
- Statement access requires ownership verification
- Anti-fraud: velocity check on debits (>10 transactions/minute alerts)

**Integration Points**
- Payments: `PAY` credits buyer wallet on successful funding
- Orders: `ORD` debits buyer wallet on order placement; credits seller on escrow release
- Escrow: `ESC` uses `WAL.HOLD` / `WAL.RELEASE` for escrow lifecycle
- Withdrawals: `WDR.DEBIT` called on withdrawal completion
- Accounting: All transactions exported via periodic push to ERP system

---

### 2.14 ESC — Escrow

| Attribute | Detail |
|---|---|
| **Module ID** | `ESC` |
| **Layer** | Domain |
| **Responsibility** | Manage the escrow lifecycle: hold funds on order placement, release to seller upon delivery confirmation or timeout, and handle dispute scenarios. |

**Core Features & Sub-Modules**
- Escrow creation on order placement (funds held in platform wallet)
- Automatic release on delivery confirmation + buyer auto-complete window
- Delayed release (seller-configured release schedule)
- Partial release (multi-item orders)
- Escrow hold period and auto-release policy
- Dispute-triggered escrow extension
- Refund-triggered escrow reversal
- Fee deduction at release time (platform commission)
- Escrow notifications (buyer: "funds held"; seller: "funds available")
- Escrow audit trail

**Dependencies**
- `ORD` — order events (placed, delivered, cancelled)
- `WAL` — hold and release operations
- `PAY` — funds origin
- `DSP` — dispute status for hold extension
- `NOT` — escrow status notifications

**Data Entities**
- `escrow_transactions` — id, order_id, amount, currency, status (held/released/refunded/partial), hold_period_end, auto_release_at
- `escrow_releases` — id, escrow_id, amount, type (auto/manual/dispute_resolution), released_to (seller_wallet_id), released_by, released_at, fee_amount, fee_breakdown (JSONB)
- `escrow_hold_extensions` — id, escrow_id, reason, extended_until, approved_by

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `ESC.HOLD(order_id)` | Place funds in escrow |
| Command | `ESC.RELEASE(order_id)` | Release to seller |
| Command | `ESC.PARTIAL_RELEASE(order_id, item_ids[])` | Release per item |
| Command | `ESC.REFUND(order_id)` | Reverse to buyer |
| Command | `ESC.EXTEND(order_id, duration, reason)` | Extend hold |
| Query | `ESC.GET_STATUS(order_id)` | Current escrow state |
| Query | `ESC.GET_PENDING_RELEASES()` | Scheduled auto-releases |
| Event | `escrow.held` | Funds placed |
| Event | `escrow.released` | Funds sent to seller |
| Event | `escrow.refunded` | Funds returned to buyer |
| Event | `escrow.auto_release.scheduled` | Timer set |
| Event | `escrow.dispute.extended` | Hold extended due to dispute |

**State Machine**

```
PENDING → [HOLD] → HELD → [RELEASE] → RELEASED
                        → [REFUND] → REFUNDED
                        → [PARTIAL_RELEASE] → PARTIALLY_RELEASED → [RELEASE_REMAINING] → RELEASED
                                                                   ↓ [DISPUTE]
                                                             DISPUTED → [RESOLVE_SELLER] → RELEASED
                                                                     → [RESOLVE_BUYER] → REFUNDED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Release before delivery confirmation | Reject; require delivery acknowledgement |
| Double release attempt | Idempotency check; return current status |
| Insufficient hold balance | Critical alert; manual reconciliation triggered |
| Auto-release with active dispute | Skip auto-release; log warning; notify admin |
| Commission calculation failure | Release with default commission rate; flag for review |

**Performance**
| Aspect | Strategy |
|---|---|
| Auto-release polling | Scheduled task every 5 minutes for orders past `auto_release_at` |
| Hold creation | Synchronous (must complete before order confirmation response) |
| Release | Synchronous wallet operation + async notification |

**Security**
- Escrow funds held in platform-level segregated wallet (not operational account)
- Auto-release requires buyer inaction for defined period (default: 7 days post-delivery)
- Manual release requires authorized admin action for disputed cases
- Fee deduction transparently computed and logged
- Release amounts are immutable after execution

**Integration Points**
- Orders: `ORD.fulfilled` triggers `ESC.AUTO_RELEASE_SCHEDULE`
- Disputes: `DSP.opened` triggers `ESC.EXTEND` to pause auto-release timer
- Wallet: `WAL.HOLD` on creation, `WAL.CREDIT` (seller) or `WAL.REFUND` (buyer) on completion

---

### 2.15 PAY — Payments

| Attribute | Detail |
|---|---|
| **Module ID** | `PAY` |
| **Layer** | Domain |
| **Responsibility** | Integrate with external payment gateways to process, capture, and reconcile payment transactions. |

**Core Features & Sub-Modules**
- Multiple payment gateway abstraction (Stripe, PayPal, Razorpay, local gateways)
- Payment method tokenization (save cards, wallets for reuse)
- One-time and recurring payment processing
- 3D Secure / Strong Customer Authentication (SCA) flow
- Payment intents with authorization and capture (dual-phase)
- Refund processing (full, partial, multiple)
- Payout settlement (seller payouts, affiliate commissions)
- Payment method management (add, remove, set default)
- Receipt generation
- Payment reconciliation (daily batch matching)
- Currency conversion support

**Dependencies**
- `USR` — customer identification
- `WAL` — wallet credit/debit
- `ORD` — order payment allocation
- `AUD` — financial audit trail
- `SET` — gateway configuration

**Data Entities**
- `payment_methods` — id, user_id, gateway, type (card/wallet/bank), token (encrypted), last_four, expiry, is_default, metadata (JSONB)
- `payment_transactions` — id, gateway_txn_id, order_id, user_id, gateway, amount, currency, status (pending/success/failed/refunded/partial_refund), fee, net_amount, error_code, error_message
- `payment_intents` — id, session_id, amount, currency, status, confirm_method, next_action (JSONB), gateway_intent_id
- `payment_refunds` — id, payment_transaction_id, amount, reason, status, gateway_refund_id
- `payment_gateway_config` — gateway, merchant_id, public_key (encrypted), private_key (encrypted), webhook_secret, is_active, priority
- `payment_reconciliation_records` — date, gateway, total_transactions, total_amount, total_fees, matched, discrepancies

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `PAY.CREATE_INTENT(amount, currency, metadata)` | Initiate payment |
| Command | `PAY.CONFIRM(intent_id, payment_method_id)` | Complete payment |
| Command | `PAY.CAPTURE(intent_id)` | Capture authorized funds |
| Command | `PAY.REFUND(transaction_id, amount, reason)` | Process refund |
| Command | `PAY.ADD_METHOD(user_id, gateway, token, metadata)` | Save payment method |
| Command | `PAY.REMOVE_METHOD(method_id)` | Delete saved method |
| Query | `PAY.GET_METHODS(user_id)` | Saved payment methods |
| Query | `PAY.GET_TRANSACTIONS(user_id, filters)` | Payment history |
| Event | `payment.intent.created` | Intent registered |
| Event | `payment.success` | Payment completed |
| Event | `payment.failed` | Payment declined |
| Event | `payment.refunded` | Refund processed |
| Event | `payment.method.added` | New method saved |
| Event | `payment.method.removed` | Method deleted |
| Webhook | `POST /webhooks/payments/{gateway}` | Gateway callbacks |

**State Machine**

```
INTENT_CREATED → [CONFIRM] → CONFIRMED → [CAPTURE] → CAPTURED → [SETTLE] → SETTLED
                ↓ [FAIL]               ↓ [AUTO_CAPTURE]
              FAILED                CAPTURED
CAPTURED → [REFUND] → REFUNDED
CAPTURED → [PARTIAL_REFUND] → PARTIALLY_REFUNDED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Card declined | Return gateway decline code; recommend alternative method |
| 3DS required | Return `next_action: { type: 'redirect', url: '...' }` |
| Gateway timeout | Retry with idempotency key; max 3 attempts |
| Duplicate webhook | Idempotency via `gateway_event_id` unique constraint |
| Gateway configuration invalid | Alert operator; fall back to next available gateway |

**Performance**
| Aspect | Strategy |
|---|---|
| Payment confirmation | Synchronous; target < 2 seconds (including gateway round-trip) |
| Webhook processing | Queue via Celery; processed within 5 seconds |
| Reconciliation | Scheduled daily at 02:00; processes last 48 hours |
| Gateway failover | Automatic circuit breaker after 5 consecutive failures |

**Security**
- PCI DSS compliance via Stripe Elements / hosted payment fields (no raw card data touches servers)
- All gateway credentials encrypted at rest (AES-256-GCM)
- Webhook signatures verified for every incoming event
- Idempotency keys required on all payment mutations
- Payment method tokens are gateway-specific; no raw PAN stored
- Rate limit: 10 payment attempts per user per minute

**Integration Points**
- Gateway: Stripe, PayPal, Razorpay via adapter pattern
- Orders: `payment.success` → `ORD.UPDATE_STATUS`
- Wallet: `payment.success` → `WAL.CREDIT` buyer's wallet
- Accounting: Daily reconciliation report to finance team

---

### 2.16 WDR — Withdrawals

| Attribute | Detail |
|---|---|
| **Module ID** | `WDR` |
| **Layer** | Domain |
| **Responsibility** | Handle seller and affiliate withdrawal requests from their wallets to external bank accounts or payment processors. |

**Core Features & Sub-Modules**
- Withdrawal request submission
- Minimum and maximum withdrawal limits
- Withdrawal fee calculation (flat fee, percentage, tier-based)
- Approval workflow (auto-approve below threshold, manual review above)
- Batch payout processing
- Payout status tracking (pending → processing → completed → failed)
- Withdrawal method management (bank account, PayPal, mobile money)
- Scheduled/recurring withdrawals
- Payout hold for new sellers (cooling period after first sale)
- Tax withholding calculation

**Dependencies**
- `WAL` — balance verification and debit
- `USR` — seller identity
- `SEL` — seller payout settings
- `PAY` — external payout processing
- `AUD` — financial transaction audit
- `NOT` — payout status notifications

**Data Entities**
- `withdrawal_requests` — id, user_id, wallet_id, amount, fee, net_amount, currency, status, method, metadata (JSONB)
- `withdrawal_methods` — id, user_id, type (bank/bkash/paypal), details (encrypted), is_default, verified_at
- `withdrawal_batch` — id, processor, total_amount, total_count, status, processed_at
- `withdrawal_batch_items` — id, batch_id, withdrawal_request_id, status, gateway_reference
- `withdrawal_limits` — user_tier, min_amount, max_amount, daily_limit, monthly_limit
- `tax_withholdings` — id, withdrawal_id, tax_rate, tax_amount, reporting_period

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `WDR.SUBMIT(user_id, amount, method_id)` | Create request |
| Command | `WDR.APPROVE(request_id, approver_id)` | Authorize payout |
| Command | `WDR.REJECT(request_id, reason)` | Decline request |
| Command | `WDR.PROCESS_BATCH(batch_id)` | Execute payouts |
| Command | `WDR.CANCEL(request_id)` | User cancels |
| Query | `WDR.GET_HISTORY(user_id, filters)` | User withdrawal log |
| Query | `WDR.GET_PENDING_APPROVALS(filters)` | Admin queue |
| Event | `withdrawal.requested` | New request |
| Event | `withdrawal.approved` | Payout approved |
| Event | `withdrawal.completed` | Funds sent |
| Event | `withdrawal.failed` | Payout error |
| Event | `withdrawal.cancelled` | Request cancelled |

**State Machine**

```
PENDING → [APPROVE] → APPROVED → [PROCESS] → PROCESSING → [COMPLETE] → COMPLETED
         ↓ [REJECT]            ↓ [BATCH]                ↓ [FAIL]
       REJECTED             BATCHED               FAILED
PENDING → [CANCEL] → CANCELLED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Insufficient balance | Reject with current available balance |
| Daily limit exceeded | Reject with limit and reset time |
| Invalid bank details | Reject; require method re-verification |
| Gateway payout failure | Retry with different gateway; max 3 attempts |
| New seller cooling period | Reject with remaining days |

**Performance**
| Aspect | Strategy |
|---|---|
| Auto-approval threshold | Instant for requests < $100 (configurable) |
| Manual review queue | SLAs: reviewed within 4 business hours |
| Batch payout processing | Hourly batch via Celery Beat |
| Balance verification | Checked at submission and again at processing (race condition guard) |

**Security**
- Withdrawal methods encrypted at rest (AES-256-GCM)
- Bank account verification via micro-deposit (two amounts)
- New withdrawal methods have 72-hour cooldown before first use
- Approval threshold tier: $100 auto, $1,000 requires secondary approval, $10,000+ requires finance team
- Payout frequency limits: max 1 withdrawal per day per seller
- Anti-fraud: velocity check on new methods; geographic IP mismatch alerts

**Integration Points**
- Payment gateway: Stripe Connect / PayPal Mass Payout for batch execution
- Banking: Plaid for bank account verification and linking
- Tax: 1099-NEC/MISC generation at year-end (US sellers)
- Accounting: Withdrawal data exported to QuickBooks/Xero

---

### 2.17 CPN — Coupons

| Attribute | Detail |
|---|---|
| **Module ID** | `CPN` |
| **Layer** | Domain |
| **Responsibility** | Manage discount coupons, promotional codes, and offers across the marketplace. |

**Core Features & Sub-Modules**
- Coupon creation (flat, percentage, free shipping, BOGO)
- Usage limits (per coupon, per user, per order)
- Validity scheduling (start date, end date, recurring windows)
- Minimum purchase requirements (subtotal, item count)
- Product/category/vendor scope restrictions
- Coupon stackability rules (exclusive, stackable with limits)
- Auto-generated coupon codes and bulk creation
- Coupon analytics (redemption rate, revenue impact)
- First-purchase and loyalty-based coupons
- Coupon validation at cart and checkout

**Dependencies**
- `CAT` — product/category scope
- `CART` — coupon application
- `CHK` — coupon validation
- `ORD` — coupon usage tracking
- `USR` — user eligibility

**Data Entities**
- `coupons` — id, code, type (flat/percentage/free_shipping), value, max_discount, currency, is_active, is_exclusive, max_uses, max_uses_per_user, min_order_amount, min_items, created_by
- `coupon_scope` — id, coupon_id, scope_type (product/category/seller/all), scope_value
- `coupon_schedules` — id, coupon_id, start_at, end_at, recurring (JSONB for weekly/monthly)
- `coupon_redemptions` — id, coupon_id, order_id, user_id, discount_amount, redeemed_at
- `coupon_batch_generations` — id, prefix, quantity, pattern, created_by, status (pending/completed/failed)

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `CPN.CREATE(data)` | Create coupon |
| Command | `CPN.VALIDATE(code, cart_context)` | Full validation |
| Command | `CPN.REDEEM(coupon_id, order_id, user_id)` | Mark redeemed |
| Command | `CPN.DISABLE(coupon_id)` | Deactivate |
| Command | `CPN.BULK_GENERATE(prefix, count, pattern)` | Mass create codes |
| Query | `CPN.LIST(filters, page)` | Admin coupon overview |
| Query | `CPN.GET_STATS(coupon_id)` | Redemption analytics |
| Event | `coupon.created` | New coupon |
| Event | `coupon.redeemed` | Coupon used |
| Event | `coupon.expired` | Validity ended |
| Event | `coupon.limit_reached` | Max uses exhausted |
| REST | `GET /api/v1/coupons/validate?code=XYZ` | Validate endpoint |

**Error Handling**
| Error | Strategy |
|---|---|
| Code already exists | Reject; suggest appending random suffix |
| Usage limit reached | Return 410 Gone; indicate next available coupon if any |
| Minimum order not met | Return 422; show shortfall amount |
| Category scope mismatch | Return 422; show applicable categories |
| Expired coupon | Return 410; do not suggest alternatives |

**Performance**
| Aspect | Strategy |
|---|---|
| Coupon validation | < 10 ms; single query with all scope joins |
| Redemption count | Denormalized on coupon row; updated atomically |
| Bulk generation | Async Celery task; 100,000 codes in < 30 seconds |
| Expired coupon cleanup | Scheduled daily; batch archive |

**Security**
- Coupon codes are case-insensitive but stored case-preserved
- Stackability rules prevent compounding > 2 coupons per order
- Coupon creation requires `coupons:create` permission
- First-purchase coupons tied to email, not just user_id
- Abuse detection: IP-based, device fingerprint for bulk account creation

**Integration Points**
- Cart: `CART.APPLY_COUPON` calls `CPN.VALIDATE` (shallow) and stores
- Checkout: `CHK.PLACE_ORDER` calls `CPN.VALIDATE` (deep, with inventory) + `CPN.REDEEM`
- Marketing: Coupon analytics feed into campaign performance dashboard

---

### 2.18 AFF — Affiliate System

| Attribute | Detail |
|---|---|
| **Module ID** | `AFF` |
| **Layer** | Domain |
| **Responsibility** | Manage the affiliate marketing program: affiliate registration, link generation, commission tracking, and payouts. |

**Core Features & Sub-Modules**
- Affiliate registration and approval workflow
- Affiliate link generation (deep links to products, categories, pages)
- Cookie-based and link-based tracking
- Commission structure (percentage, flat, tiered, lifetime)
- Cookie duration configuration (30/60/90 days)
- Sales attribution (last-click model, multi-touch)
- Affiliate dashboard (clicks, conversions, commissions, payouts)
- Payout threshold and schedule
- Affiliate tiers (Bronze/Silver/Gold with increasing commission)
- Fraud detection (self-referral, click farming, fake conversions)

**Dependencies**
- `USR` — affiliate identity
- `ORD` — order attribution
- `WAL` — commission payouts
- `CAT` — product links
- `ANL` — conversion analytics
- `SET` — commission rate configuration

**Data Entities**
- `affiliates` — id, user_id, status, tier, referral_code, tracking_domain, payment_threshold
- `affiliate_links` — id, affiliate_id, target_type (product/category/search), target_value, slug, parameters (JSONB)
- `affiliate_clicks` — id, link_id, ip, user_agent, referrer, landing_url, visitor_id, created_at
- `affiliate_conversions` — id, click_id, order_id, affiliate_id, commission_amount, commission_rate, status (pending/approved/rejected), paid_at
- `affiliate_commission_structures` — id, tier, product_category_id, rate_type (percentage/flat), rate_value, max_cap
- `affiliate_payouts` — id, affiliate_id, period_start, period_end, total_commission, status, paid_at

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `AFF.REGISTER(user_id)` | Apply to program |
| Command | `AFF.APPROVE(affiliate_id)` | Accept application |
| Command | `AFF.GENERATE_LINK(affiliate_id, target, params)` | Create tracking link |
| Command | `AFF.TRACK_CLICK(link_slug, request_context)` | Record click |
| Command | `AFF.ATTRIBUTE(order_id, visitor_id)` | Assign conversion |
| Command | `AFF.CALCULATE_COMMISSION(conversion_id)` | Compute earnings |
| Command | `AFF.PAYOUT(affiliate_id, period)` | Initiate payout |
| Query | `AFF.GET_STATS(affiliate_id, period)` | Performance metrics |
| Query | `AFF.GET_LINKS(affiliate_id)` | All generated links |
| Event | `affiliate.registered` | New affiliate |
| Event | `affiliate.approved` | Active affiliate |
| Event | `affiliate.conversion.recorded` | Sale attributed |
| Event | `affiliate.conversion.approved` | Commission confirmed |
| Event | `affiliate.payout.sent` | Commission paid |

**Error Handling**
| Error | Strategy |
|---|---|
| Self-referral detected | Flag conversion; auto-reject; send warning |
| Duplicate click (same visitor + same link + 1 hour) | Deduplicate; only count first |
| Invalid tracking link | Return 404; redirect to homepage |
| Commission amount below minimum | Accumulate until threshold met |
| Cookie not present (cross-domain) | Fall back to URL parameter tracking |

**Performance**
| Aspect | Strategy |
|---|---|
| Click recording | Fire-and-forget via queue; target processing < 50 ms |
| Conversion attribution | Near-real-time via order completion event |
| Cookie duration | Set via `__aff_` cookie with configurable expiry (default 30 days) |
| Click deduplication | Redis set with 1-hour TTL per visitor+link combination |

**Security**
- Referral codes are random alphanumeric (8+ characters, unguessable)
- Self-referral detection via IP, cookie, and billing address comparison
- Conversion manual review for amounts > $500
- Affiliate links use `rel="sponsored nofollow noopener"` for SEO compliance
- Fraud detection model flags:
  - Same IP for click and purchase
  - > 10 conversions from same IP in 24 hours
  - New accounts with immediate high-value conversions

**Integration Points**
- Tracking pixel: 1×1 transparent GIF placed on order confirmation page
- Checkout: `affiliate_id` passed through checkout flow and attached to order
- Marketing: Affiliate performance feeds into campaign ROI calculator
- Payout: Uses `WDR` module for commission withdrawal

---

### 2.19 MSG — Messaging

| Attribute | Detail |
|---|---|
| **Module ID** | `MSG` |
| **Layer** | Application |
| **Responsibility** | Facilitate real-time and asynchronous communication between buyers, sellers, and support agents. |

**Core Features & Sub-Modules**
- One-on-one messaging (buyer ↔ seller, user ↔ support)
- Group conversations (order-level multi-party: buyer + seller + support)
- Rich text support (markdown, image attachments, file sharing)
- Read receipts and typing indicators
- Message reactions and replies (threaded replies)
- Conversation archiving and muting
- Message search within conversations
- Chat assignments (support agent assignment)
- Pre-defined message templates (canned responses for support)
- Offline message queuing and delivery
- Blocking and reporting abusive messages
- Auto-moderation (profanity filter, PII scanner)

**Dependencies**
- `USR` — participant identity
- `ORD` — order context linking
- `SUP` — ticket-linked conversations
- `NOT` — push notifications for new messages
- `AUTHZ` — conversation access control

**Data Entities**
- `conversations` — id, type (direct/order/ticket/group), title, context_type, context_id, status (active/archived), created_at
- `conversation_participants` — id, conversation_id, user_id, role (buyer/seller/agent), joined_at, last_read_at, is_muted
- `messages` — id, conversation_id, sender_id, content, message_type (text/image/file/system), metadata (JSONB), created_at, edited_at
- `message_attachments` — id, message_id, file_url, file_type, file_size
- `message_reactions` — id, message_id, user_id, reaction (unicode emoji)
- `message_reports` — id, message_id, reporter_id, reason, status (pending/dismissed/actioned)

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `MSG.CREATE_CONVERSATION(participants, context)` | New conversation |
| Command | `MSG.SEND_MESSAGE(conversation_id, content, attachments)` | Send message |
| Command | `MSG.MARK_READ(conversation_id, user_id, last_message_id)` | Read receipt |
| Command | `MSG.ARCHIVE(conversation_id, user_id)` | Archive for user |
| Command | `MSG.REACT(message_id, user_id, reaction)` | Add reaction |
| Command | `MSG.REPORT(message_id, reporter_id, reason)` | Report abuse |
| Query | `MSG.GET_CONVERSATIONS(user_id, filters)` | Inbox list |
| Query | `MSG.GET_MESSAGES(conversation_id, before, limit)` | Message history |
| Event | `conversation.created` | New chat |
| Event | `message.sent` | New message (real-time relay) |
| Event | `message.edited` | Message modified |
| Event | `conversation.participant.joined` | User added |
| Event | `message.reported` | Abuse report triggered |
| WebSocket | `ws:///api/v1/ws/chat` | Real-time message stream |

**Error Handling**
| Error | Strategy |
|---|---|
| User not in conversation | Return 403; never reveal conversation existence |
| Message too large | Return 413; indicate max length (10K characters) |
| File type not allowed | Return 422; list allowed MIME types |
| Conversation archived | Return 410; allow unarchive via support |
| Rate limit exceeded | Return 429; 20 messages per minute per conversation |

**Performance**
| Aspect | Strategy |
|---|---|
| Real-time delivery | WebSocket with Redis pub/sub (fan-out per conversation) |
| Message persistence | Batch write every 2 seconds; immediate write for priority messages |
| Search | Messages indexed in Elasticsearch (conversation-scoped) |
| File upload | Direct-to-S3 with pre-signed URL; 10 MB per file limit |
| Read receipts | Debounced; written every 5 seconds per user per conversation |

**Security**
- Conversation access strictly enforced; users can only access conversations they are participants in
- Support agents have access only to assigned conversations
- Message content scanned for PII (credit cards, SSN) via regex before persistence
- File uploads virus-scanned; blocked if infected
- Message edit history immutable; edits create new version
- Encryption in transit (TLS) and at rest (AES-256)

**Integration Points**
- WebSocket: Real-time messaging via WebSocket gateway in `frontend/`
- Notifications: `message.sent` → push notification if recipient offline
- Support: Conversations auto-created when `SUP` ticket is opened
- Orders: Order page shows linked conversation for buyer–seller communication

---

### 2.20 NOT — Notifications

| Attribute | Detail |
|---|---|
| **Module ID** | `NOT` |
| **Layer** | Application |
| **Responsibility** | Deliver timely, multi-channel notifications to users across all modules. |

**Core Features & Sub-Modules**
- Multi-channel delivery: in-app, email, SMS, push (mobile/web)
- Notification templates (per type, per channel, with variables)
- User preference management (opt-in/out per channel, per notification type)
- Priority-based delivery (critical < 30 seconds, normal < 5 minutes, bulk < 1 hour)
- Digest notifications (daily/weekly summary)
- Scheduled and delayed notifications
- Read/unread tracking
- Notification grouping and deduplication
- Delivery status tracking and retry logic
- Notification center API (in-app inbox)

**Dependencies**
- `USR` — user contact info and preferences
- All other modules — event sources
- `SET` — notification configuration

**Data Entities**
- `notification_templates` — id, type, channel, subject, body (template with variables), locale
- `notification_preferences` — user_id, channel, notification_type, enabled, digest_frequency
- `notifications` — id, user_id, type, channel, title, body, data (JSONB), priority, status (pending/sent/failed/read), scheduled_at, sent_at, read_at
- `notification_delivery_logs` — id, notification_id, channel, status, error_message, retry_count
- `notification_device_tokens` — user_id, device_id, platform (ios/android/web), token, is_active

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `NOT.SEND(user_id, type, data, channel)` | Send single notification |
| Command | `NOT.SEND_BULK(user_ids[], type, data, channel)` | Mass notification |
| Command | `NOT.SCHEDULE(user_id, type, data, deliver_at)` | Schedule future |
| Command | `NOT.MARK_READ(notification_id[])` | Mark as read |
| Command | `NOT.MARK_ALL_READ(user_id)` | Mark all read |
| Command | `NOT.UPDATE_PREFERENCE(user_id, preferences)` | Update user prefs |
| Command | `NOT.REGISTER_DEVICE(user_id, token, platform)` | Push registration |
| Query | `NOT.GET_NOTIFICATIONS(user_id, filters)` | Notification center |
| Query | `NOT.GET_UNREAD_COUNT(user_id)` | Badge count |
| Event | `notification.sent` (internal) | Delivery acknowledged |
| Event | `notification.failed` (internal) | Retry logic trigger |
| REST | `GET /api/v1/notifications` | User inbox |
| REST | `POST /api/v1/notifications/read` | Mark read |
| WebSocket | `ws:///api/v1/ws/notifications` | Real-time push |

**Error Handling**
| Error | Strategy |
|---|---|
| Email delivery failure | Retry 3 times (5 min, 30 min, 2 hours); then fall back to in-app |
| SMS provider down | Queue and retry; if > 1 hour, escalate to monitoring |
| Push token invalid | Mark token inactive; stop sending to device |
| Template rendering error | Send fallback template in default locale |
| Rate limit from provider | Queue with exponential backoff |

**Performance**
| Aspect | Strategy |
|---|---|
| High-throughput delivery | Bulk notifications processed via Celery with dedicated worker pool |
| In-app delivery | Redis pub/sub → WebSocket for real-time; PostgreSQL for persistence |
| Email sending | AWS SES / SendGrid via SMTP proxy with 10 concurrent connections |
| Push notifications | Firebase Cloud Messaging / Apple APNs with batch API |
| Digest generation | Overnight Celery Beat task; page size limit of 50 notifications |

**Security**
- Notification templates sanitized to prevent XSS in rendered content
- Push notification payloads exclude sensitive data (only type + ID)
- Users cannot disable critical notifications (security alerts, account changes)
- Bulk notifications require `notifications:bulk` permission
- Unsubscribe links included in all marketing emails with one-click unsubscribe

**Integration Points**
- All modules: Subscribe to domain events and translate to notifications
- Email: SendGrid / SES for transactional and marketing emails
- SMS: Twilio for transaction alerts and OTPs
- Push: FCM + APNs via unified service
- In-app: Notification center exposed via `GET /api/v1/notifications`

---

### 2.21 REV — Reviews

| Attribute | Detail |
|---|---|
| **Module ID** | `REV` |
| **Layer** | Domain |
| **Responsibility** | Manage the product review and rating system including submission, moderation, and aggregation. |

**Core Features & Sub-Modules**
- Multi-criteria rating (overall, quality, value, delivery speed)
- Written review with character limits
- Verified purchase badge
- Media attachments (images, videos in reviews)
- Helpful votes (upvote/downvote on reviews)
- Review moderation queue (auto-approve, flag for review)
- Review lifecycle (pending → approved → rejected → hidden)
- Aggregated ratings (average per product, per seller)
- Sort reviews by (most recent, highest rated, most helpful)
- Review responses from sellers
- Incentivized review detection
- Review reporting (abuse, fake review)

**Dependencies**
- `ORD` — purchase verification
- `USR` — reviewer identity
- `CAT` — product association
- `SEL` — seller rating aggregation
- `AUD` — moderation audit trail

**Data Entities**
- `reviews` — id, product_id, user_id, order_id, rating (1-5), title, body, is_verified_purchase, status (pending/approved/rejected/hidden), helpful_count, created_at
- `review_criteria_ratings` — id, review_id, criterion (quality/value/delivery), rating
- `review_media` — id, review_id, type (image/video), url, sort_order
- `review_helpful_votes` — review_id, user_id, vote (up/down), created_at (unique constraint)
- `review_moderation_queue` — id, review_id, reason, flagged_by, status (open/approved/rejected), reviewed_by, reviewed_at
- `review_seller_responses` — id, review_id, seller_id, content, created_at, edited_at
- `product_rating_aggregates` — product_id, average_rating, rating_count, distribution (JSONB: {1: N, 2: N, ...})
- `seller_rating_aggregates` — seller_id, average_rating, rating_count

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `REV.SUBMIT(user_id, product_id, order_id, data)` | Create review |
| Command | `REV.APPROVE(review_id, moderator_id)` | Approve review |
| Command | `REV.REJECT(review_id, reason)` | Reject review |
| Command | `REV.VOTE_HELPFUL(review_id, user_id, vote)` | Mark helpful/unhelpful |
| Command | `REV.ADD_SELLER_RESPONSE(review_id, seller_id, content)` | Seller reply |
| Command | `REV.REPORT(review_id, reporter_id, reason)` | Flag for moderation |
| Query | `REV.GET_PRODUCT_REVIEWS(product_id, sort, page)` | Public reviews |
| Query | `REV.GET_SELLER_RATINGS(seller_id)` | Aggregated seller score |
| Query | `REV.GET_MODERATION_QUEUE(filters)` | Admin pending queue |
| Event | `review.submitted` | New review awaiting moderation |
| Event | `review.approved` | Review published |
| Event | `review.rejected` | Review declined |
| Event | `review.helpful.voted` | Helpfulness vote |
| Event | `review.seller.responded` | Seller replied |
| Event | `product.rating.updated` | Aggregate recalculated |

**Error Handling**
| Error | Strategy |
|---|---|
| Duplicate review (same user + product) | Return 409; allow edit of existing review |
| Review period expired (30 days post-delivery) | Reject with policy explanation |
| Self-review (seller reviewing own product) | Block; silent success to not reveal detection |
| Review contains prohibited content | Flag for moderation; auto-reject if explicit |
| Rating aggregate overflow | Recalculate from scratch (scheduled job if drift detected) |

**Performance**
| Aspect | Strategy |
|---|---|
| Rating aggregates | Denormalized; updated atomically on review approval |
| Review list query | Indexed on `product_id + status + created_at` descending |
| Aggregate staleness | Recalculated via scheduled job every hour (catches deleted/flagged reviews) |
| Media loading | Lazy-loaded below fold; thumbnails via CDN |

**Security**
- Only verified purchase reviews eligible for auto-approve
- Seller responses disallowed within 24 hours of review (cooling-off period)
- Review content sanitized (HTML stripped, XSS prevented)
- IP + user_id rate limit: 1 review per product per 30 days
- Moderation actions immutable; audit-logged

**Integration Points**
- Product catalog: `product.rating.updated` events consumed for search ranking
- Search: Rating facet and sort options powered by aggregates
- Seller dashboard: Rating trends and review management interface
- Analytics: Review sentiment analysis pipeline

---

### 2.22 DSP — Disputes

| Attribute | Detail |
|---|---|
| **Module ID** | `DSP` |
| **Layer** | Domain |
| **Responsibility** | Manage the dispute resolution lifecycle between buyers and sellers, including evidence submission, mediation, and resolution. |

**Core Features & Sub-Modules**
- Dispute initiation by buyer or seller (linked to order)
- Dispute categorization (item not received, wrong item, quality issue, refund request)
- Evidence submission (messages, screenshots, files)
- Timeline with all actions and communications recorded
- Automated resolution rules (defined thresholds and policies)
- Manual mediation by support staff
- Resolution options (full refund, partial refund, replacement, release funds)
- Appeal process (escalate to senior mediator)
- Streak-based moderation (repeat offender flagging)
- SLA tracking and breach escalation

**Dependencies**
- `ORD` — disputed order context
- `WAL` — hold extension and refund execution
- `ESC` — escrow hold during dispute
- `MSG` — dispute conversation evidence
- `USR` — participant profiles (dispute history)
- `AUD` — full dispute audit trail
- `NOT` — status updates to parties

**Data Entities**
- `disputes` — id, order_id, initiator_id, respondent_id, category, reason, status (open/investigating/resolved/appealed/closed), desired_outcome, priority, assigned_to, opened_at, sla_deadline
- `dispute_evidence` — id, dispute_id, submitted_by, type (message/file/screenshot), content, file_url, submitted_at
- `dispute_actions` — id, dispute_id, action_type (note/request_evidence/escalate/resolve), actor_id, description, metadata (JSONB)
- `dispute_resolutions` — id, dispute_id, type (refund/replacement/release/partial_refund), amount, approved_by, resolved_at
- `dispute_escalations` — id, dispute_id, escalated_by, reason, assigned_to, escalated_at, resolved_at
- `dispute_rules` — category, auto_resolve_conditions (JSONB), sla_hours, max_escalations

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `DSP.OPEN(order_id, initiator_id, category, reason)` | File dispute |
| Command | `DSP.SUBMIT_EVIDENCE(dispute_id, user_id, evidence)` | Add evidence |
| Command | `DSP.ASSIGN(dispute_id, agent_id)` | Assign mediator |
| Command | `DSP.RESOLVE(dispute_id, resolution, resolver_id)` | Close dispute |
| Command | `DSP.ESCALATE(dispute_id, escalator_id, reason)` | Escalate |
| Command | `DSP.ADD_NOTE(dispute_id, actor_id, note)` | Internal note |
| Query | `DSP.GET(dispute_id)` | Full case file |
| Query | `DSP.LIST_USER(user_id, filters)` | User's disputes |
| Query | `DSP.LIST_QUEUE(filters)` | Mediator queue |
| Event | `dispute.opened` | Dispute filed |
| Event | `dispute.evidence.submitted` | New evidence |
| Event | `dispute.assigned` | Mediator assigned |
| Event | `dispute.resolved` | Resolution reached |
| Event | `dispute.escalated` | Escalated to senior |
| Event | `dispute.sla.breached` | SLA deadline missed |
| REST | `POST /api/v1/disputes` | File dispute |
| REST | `GET /api/v1/disputes/{id}` | Full dispute detail |

**State Machine**

```
OPEN → [ASSIGN] → INVESTIGATING → [RESOLVE] → RESOLVED → [APPEAL] → APPEALED → [REVIEW] → CLOSED
  ↓ [AUTO_RESOLVE]                                                                  ↓ [UPHOLD]
RESOLVED                                                                        CLOSED
```

**Error Handling**
| Error | Strategy |
|---|---|
| Duplicate dispute (same order, same initiator) | Reject; reference existing dispute ID |
| Dispute outside window (30 days post-delivery) | Reject; log buyer complaint separately |
| Resolution amount > order total | Cap at order total; flag for review |
| Evidence file too large (max 50 MB) | Return 413; recommend compression |
| Both parties rejected resolution | Auto-escalate to senior mediator |

**Performance**
| Aspect | Strategy |
|---|---|
| SLA tracking | Checked every 5 minutes via scheduled task; breach event fires |
| Evidence storage | S3 with pre-signed URLs; 50 MB limit per file |
| Auto-resolution rules | Configurable rule engine; evaluated at dispute creation |
| Mediator assignment | Round-robin across available mediators; weighted by workload |

**Security**
- Evidence visible only to dispute parties and assigned mediator
- Resolution actions require digital signature (audit trail)
- Mediators cannot have prior relationship with either party
- Dispute communications are not admissible in public (separate from MSG module visibility)
- Resolution amounts automatically deducted/credited via `WAL`

**Integration Points**
- Escrow: `DSP.opened` → `ESC.EXTEND` to pause auto-release
- Wallet: Resolution calls `WAL.DEBIT` (seller) / `WAL.CREDIT` (buyer)
- Admin: Dispute queue with SLA indicators, bulk actions, and reporting
- Notifications: Status changes pushed to both parties

---

### 2.23 SUP — Support Tickets

| Attribute | Detail |
|---|---|
| **Module ID** | `SUP` |
| **Layer** | Application |
| **Responsibility** | Manage customer support tickets from creation through triage, resolution, and satisfaction survey. |

**Core Features & Sub-Modules**
- Ticket creation (web form, email-to-ticket, API)
- Ticket categorization and priority assignment
- Queue management with agent assignment (manual, auto, round-robin)
- Status workflow (new → open → pending → resolved → closed)
- Canned responses / macros
- Internal notes (not visible to customer)
- Ticket merge and split
- SLA management with escalation
- Satisfaction survey (CSAT) on ticket closure
- Multi-department routing (billing, technical, general)
- Customer communication history within ticket

**Dependencies**
- `USR` — customer and agent identity
- `ORD` — order context linking
- `MSG` — direct messaging with customer
- `NOT` — ticket update notifications
- `DSP` — dispute escalation path
- `AUD` — ticket audit log
- `SET` — SLA configuration

**Data Entities**
- `support_tickets` — id, user_id, subject, category, priority, status, assigned_to, source (web/email/api), satisfaction_score, created_at, sla_deadline
- `ticket_messages` — id, ticket_id, author_id, author_type (customer/agent), content, visibility (public/internal), attachments (JSONB), created_at
- `ticket_macros` — id, name, category, subject_template, body_template, is_active
- `ticket_slas` — category, priority, first_response_hours, resolution_hours, escalation_hours
- `ticket_escalations` — id, ticket_id, reason, escalated_by, escalated_to, escalated_at
- `ticket_surveys` — id, ticket_id, score (1-5), comment, submitted_at

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `SUP.CREATE(user_id, subject, category, message)` | New ticket |
| Command | `SUP.ASSIGN(ticket_id, agent_id)` | Assign agent |
| Command | `SUP.ADD_MESSAGE(ticket_id, author, content, visibility)` | Add reply/note |
| Command | `SUP.UPDATE_STATUS(ticket_id, status)` | Change status |
| Command | `SUP.MERGE(primary_ticket_id, secondary_ticket_id)` | Merge tickets |
| Command | `SUP.APPLY_MACRO(ticket_id, macro_id)` | Execute canned response |
| Command | `SUP.SUBMIT_SURVEY(ticket_id, score, comment)` | CSAT feedback |
| Query | `SUP.GET(ticket_id)` | Full ticket |
| Query | `SUP.LIST_USER(user_id, filters)` | Customer's tickets |
| Query | `SUP.LIST_QUEUE(filters)` | Agent's queue |
| Event | `ticket.created` | New ticket |
| Event | `ticket.assigned` | Agent assigned |
| Event | `ticket.status.changed` | Status transition |
| Event | `ticket.escalated` | Escalation triggered |
| Event | `ticket.resolved` | Resolution reached |
| Event | `ticket.sla.breached` | SLA missed |
| REST | `POST /api/v1/support/tickets` | Create ticket |
| REST | `POST /api/v1/support/tickets/{id}/messages` | Add message |

**State Machine**

```
NEW → [ASSIGN] → OPEN → [PENDING_CUSTOMER] → PENDING → [RESPOND] → OPEN
                      → [AUTO_CLOSE] → CLOSED          → [RESOLVE] → RESOLVED → [CLOSE] → CLOSED
                      → [ESCALATE] → ESCALATED                                      ↓ [REOPEN]
                                                                                 OPEN
```

**Error Handling**
| Error | Strategy |
|---|---|
| Duplicate ticket detection | Check similar open tickets by same user in last 24 hours; suggest |
| Merge incompatible statuses | Force resolve secondary ticket before merge |
| Unknown email sender | Reject; create account prompt |
| Attachment virus detected | Block attachment; notify user via ticket message |
| SLA config not found for category | Apply default SLA; log configuration gap |

**Performance**
| Aspect | Strategy |
|---|---|
| Ticket list for agents | Real-time via WebSocket push for new tickets |
| Email-to-ticket ingestion | Polling every 60 seconds via IMAP/POP3 or SendGrid inbound parse |
| Full-text search on tickets | Elasticsearch with ticket-scoped permissions |
| Macro execution | Template rendered server-side; < 500 ms |
| Survey aggregation | Daily batch for CSAT reporting |

**Security**
- Agents can only view content of tickets they are assigned to (or in their department)
- Internal notes invisible to customers at API and database level
- Ticket access: customer sees own tickets; agents see assigned; admins see all
- Email-to-ticket verified via SPF, DKIM, DMARC
- PII auto-masked in agent responses (credit cards, SSN)

**Integration Points**
- Email: Inbound parse → `SUP.CREATE`; outbound → SendGrid/SES
- Admin: Full ticket management UI with dashboard, macros, and reporting
- Notifications: Email/WebSocket to customer and agent on status changes
- Disputes: `SUP` ticket optionally convertible to `DSP` dispute
- Knowledge Base: CMS articles suggested during ticket creation

---

### 2.24 ANL — Analytics

| Attribute | Detail |
|---|---|
| **Module ID** | `ANL` |
| **Layer** | Application |
| **Responsibility** | Collect, process, store, and expose business metrics and KPIs for dashboards, reports, and data-driven decisions. |

**Core Features & Sub-Modules**
- Event ingestion pipeline (server-side events, client-side tracking)
- Pre-aggregated metrics (hourly/daily/monthly)
- Real-time dashboards (sales, traffic, conversion rates)
- Cohort analysis (retention, churn)
- Funnel analysis (browse → cart → checkout → purchase)
- Revenue analytics (MRR, ARPU, LTV)
- Product performance analytics (views, sales, refund rate)
- Seller performance analytics
- Affiliate performance analytics
- Custom report builder
- Data export (CSV, JSON, Excel)
- Scheduled report delivery (email, Slack, webhook)

**Dependencies**
- All modules — data sources (read-only access to event streams)
- `ORD` — transaction data
- `USR` — user behavior
- `SRCH` — search query analytics
- `CAT` — product-centric metrics
- `SEL` — seller metrics
- `AFF` — affiliate metrics

**Data Entities**
- `analytics_events_raw` — id, event_type, user_id, session_id, properties (JSONB), timestamp (TTL: 90 days)
- `analytics_aggregates_hourly` — metric, dimensions (JSONB), value, hour
- `analytics_aggregates_daily` — metric, dimensions (JSONB), value, date
- `analytics_dashboards` — id, name, owner_id, widgets (JSONB), is_shared, filters (JSONB)
- `analytics_scheduled_reports` — id, name, query_config (JSONB), schedule (cron), recipients, last_sent_at
- `analytics_funnels` — id, name, steps (JSONB), conversion_rate, period
- `analytics_cohorts` — id, name, criteria (JSONB), size, retention_data (JSONB)

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `ANL.TRACK(event_type, user_id, session, properties)` | Ingest event |
| Command | `ANL.TRACK_BATCH(events[])` | Bulk ingest |
| Command | `ANL.COMPUTE_AGGREGATES(metric, period)` | On-demand aggregation |
| Command | `ANL.CREATE_DASHBOARD(name, widgets)` | New dashboard |
| Command | `ANL.SCHEDULE_REPORT(query, cron, recipients)` | Recurring report |
| Query | `ANL.GET_METRIC(metric, dimensions, from, to)` | Time-series data |
| Query | `ANL.GET_FUNNEL(funnel_id, period)` | Funnel steps |
| Query | `ANL.GET_COHORT(cohort_id)` | Retention table |
| Query | `ANL.GET_REALTIME(metrics[])` | Live indicator values |
| Event | `analytics.report.generated` | Scheduled report ready |
| REST | `POST /api/v1/analytics/track` | Client-side event |
| REST | `GET /api/v1/analytics/metrics/{metric}` | Metric query |

**Error Handling**
| Error | Strategy |
|---|---|
| Invalid event schema | Drop event; log to dead-letter queue |
| ClickHouse query timeout | Return partial data with timeout indicator |
| Dashboard widget configuration error | Render broken widget as error card; alert owner |
| Aggregation backlog (> 1 hour delay) | Alert operations; prioritize catch-up pipeline |

**Performance**
| Aspect | Strategy |
|---|---|
| Event ingestion | Kafka → ClickHouse; target 50,000 events/second per node |
| Aggregate computation | ClickHouse materialized views; minutely refresh |
| Dashboard queries | Target < 2 seconds for 30-day window; pre-aggregated |
| Real-time metrics | Redis sorted sets + hyperloglog for approximate unique counts |
| Historical data | ClickHouse TTL: raw 90 days, hourly aggregates 1 year, daily aggregates 5 years |

**Security**
- Dashboard access controlled by owner and `analytics:view` permission
- Event data excludes PII at ingestion point (server-side scrubbing)
- Report delivery over encrypted channels only (email TLS, Slack webhook HTTPS)
- Custom reports limited to 10 million rows export per query
- Query timeout: 30 seconds for interactive, 5 minutes for scheduled

**Integration Points**
- All modules: Emit structured events consumed by `ANL.TRACK`
- Frontend: Client-side tracking via `POST /api/v1/analytics/track` (GDPR-compliant, opt-in)
- Admin: Dashboard builder UI with drag-and-drop widgets
- Business intelligence: Data export to Metabase / Superset / Tableau via read-only ClickHouse user

---

### 2.25 CMS — Content Management System

| Attribute | Detail |
|---|---|
| **Module ID** | `CMS` |
| **Layer** | Domain |
| **Responsibility** | Manage non-product content: landing pages, blog posts, help articles, policy pages, and localized content. |

**Core Features & Sub-Modules**
- Page builder with WYSIWYG editor (rich text, images, embeds)
- Blog engine with categories and tags
- SEO metadata management (meta title, description, Open Graph)
- Content versioning and draft/publish workflow
- Multi-language content (i18n per content node)
- Content scheduling (future publish, auto-expire)
- Media library (images, videos, documents) with search
- Help center / knowledge base with search
- Legal pages (Terms, Privacy, Cookies) with version tracking and consent prompts
- Content blocks / reusable components (headers, footers, CTAs)
- Form builder (contact forms, lead capture)

**Dependencies**
- `USR` — author identity
- `AUTHZ` — content editing permissions
- `MKT` — content-to-marketplace linking
- `SRCH` — content search indexing
- `ANL` — page view analytics
- `NOT` — content publish notifications

**Data Entities**
- `cms_pages` — id, type (page/blog/help/legal), title, slug, content (JSONB — structured blocks), status, author_id, locale, seo_metadata (JSONB), published_at, expires_at
- `cms_page_versions` — id, page_id, version, content_snapshot, changelog, created_by, created_at
- `cms_categories` — id, type (blog/help), name, slug, description
- `cms_media` — id, filename, mime_type, file_size, url, alt_text, uploaded_by, uploaded_at
- `cms_content_blocks` — id, name, type, content (JSONB), is_global, last_used_at
- `cms_forms` — id, name, fields (JSONB), submissions_count, created_at
- `cms_form_submissions` — id, form_id, data (JSONB), submitted_at
- `cms_legal_versions` — id, type (terms/privacy/cookies), version, content, effective_date, consent_required

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `CMS.CREATE_PAGE(type, title, content, locale)` | New content |
| Command | `CMS.PUBLISH(page_id)` | Make live |
| Command | `CMS.ARCHIVE(page_id)` | Remove from public |
| Command | `CMS.DUPLICATE(page_id, locale)` | Copy for translation |
| Command | `CMS.SUBMIT_FORM(form_id, data)` | Form submission |
| Command | `CMS.GET_LEGAL_VERSION(type, version)` | Retrieve policy |
| Query | `CMS.GET_PAGE(slug, locale)` | Public page |
| Query | `CMS.SEARCH(query, locale)` | Content search |
| Query | `CMS.LIST(type, filters)` | Admin content list |
| Event | `cms.page.published` | Content goes live |
| Event | `cms.page.updated` | Content modified |
| Event | `cms.form.submitted` | Form submission received |
| Event | `cms.legal.updated` | Policy version changed |
| REST | `GET /api/v1/cms/pages/{slug}` | Public page |
| REST | `POST /api/v1/cms/forms/{slug}` | Submit form |

**Error Handling**
| Error | Strategy |
|---|---|
| Slug conflict | Append suffix; suggest alternatives |
| Content block recursion (self-referencing) | Reject with 422; detect circular refs |
| Locale content not found | Fall back to default locale; log missing translation alert |
| Form field validation error | Return 422 with field-level errors |
| Media file type not allowed | Return 422; list allowed types |

**Performance**
| Aspect | Strategy |
|---|---|
| Page rendering | Server-side rendered (SSR) with CDN caching; cache-control max-age 3600 |
| Media delivery | CDN with image optimization (WebP, auto-format, quality) |
| Content versioning | Store only diffs for non-media changes; full snapshots every 10 versions |
| Search | Elasticsearch with separate content index; boosted for help articles |
| Legal versions | Append-only; immutable once published |

**Security**
- Draft pages accessible only by authors and editors via preview token
- Admin content management requires `cms:manage` permission
- Form submissions restricted by rate limit (10 per IP per hour without authentication)
- Media uploads scanned for malware; EXIF data stripped
- Legal content changes require compliance officer sign-off
- XSS prevention: all HTML content sanitized via DOMPurify on both input and render

**Integration Points**
- Frontend: CMS content fetched at build time (SSG) and hydrated at request time (ISR)
- Search: Content indexed for global search results
- Notifications: Legal updates emailed to all users requiring re-consent
- Admin: Media library integrated with rich text editor via image picker

---

### 2.26 ADM — Admin Panel

| Attribute | Detail |
|---|---|
| **Module ID** | `ADM` |
| **Layer** | Presentation |
| **Responsibility** | Provide a centralized administrative interface for platform operators to manage all aspects of the marketplace. |

**Core Features & Sub-Modules**
- Dashboard (KPIs: revenue, users, orders, disputes, growth trends)
- User management (view, search, suspend, verify, merge)
- Seller management (approve, tier change, verification review)
- Product moderation (approve/reject listings, bulk edit)
- Order management (view details, process refunds, cancellations)
- Dispute resolution console
- Support ticket management
- Coupon and promotion creation
- CMS page management
- Analytics dashboards and report scheduling
- System configuration (settings, feature flags)
- Audit log viewer
- Role and permission management
- Payment reconciliation view
- Wallet and withdrawal management
- Commission rule configuration

**Dependencies**
- All modules — admin is the presentation layer over all domain modules
- `AUTH` — admin authentication (SSO, MFA enforced)
- `RBAC` — granular admin permissions
- `AUD` — all admin actions logged

**Data Entities**
- `admin_audit_log` — (see AUD module)
- `admin_saved_views` — id, admin_id, module, filters (JSONB), name, is_default
- `admin_announcements` — id, title, body, priority, target_role, expires_at, created_by
- `admin_dashboard_widgets` — admin_id, widget_type, config (JSONB), position

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `ADM.SAVE_VIEW(admin_id, module, filters, name)` | Save filter preset |
| Command | `ADM.ANNOUNCE(title, body, target, expires)` | Platform announcement |
| Query | `ADM.GET_DASHBOARD(admin_id)` | Personalized dashboard |
| Query | `ADM.GET_SYSTEM_HEALTH()` | Service health status |
| Event | `admin.announcement.created` | New announcement |
| REST | `GET /api/v1/admin/dashboard` | Dashboard data |
| REST | `GET /api/v1/admin/{module}` | Module listing pages |
| GraphQL | `Query.admin.*` | All admin queries |

**Error Handling**
| Error | Strategy |
|---|---|
| Insufficient admin permissions | Return 403 with required permission listed |
| Module access disabled for admin role | Hide module from UI; API returns 403 |
| SuperAdmin-only action attempted | Reject; log attempt |
| Bulk operation exceeds limit (e.g., 10K users) | Reject with max limit; suggest batch size |

**Performance**
| Aspect | Strategy |
|---|---|
| Admin queries | Direct on primary database (no caching for dashboard accuracy) |
| Dashboard KPI refresh | Server-side cache: 5 minutes for real-time-ish view |
| Export operations | Celery task with email delivery for large datasets |
| Search across modules | Elasticsearch with cross-module search |

**Security**
- Admin panel requires MFA (mandatory, not optional)
- Admin sessions shorter TTL (15 minutes idle timeout)
- All admin mutations logged with full request/response dump (excluding secrets)
- IP allowlisting for SuperAdmin access
- Separate admin subdomain (`admin.tsbl.com`) with WAF in front
- Session fixation prevention: new session ID on login
- Admin login triggers notification to all SuperAdmins

**Integration Points**
- All modules: Admin provides the management UI over every domain
- Audit: Every admin action sends a structured log to `AUD`
- Notifications: Announcements pushed to in-app notification center
- SSO: Admin login via corporate identity provider (Okta, Azure AD)

---

### 2.27 AUD — Audit Logs

| Attribute | Detail |
|---|---|
| **Module ID** | `AUD` |
| **Layer** | Infrastructure |
| **Responsibility** | Provide an immutable, tamper-evident record of all security-sensitive and financially-significant events across the platform. |

**Core Features & Sub-Modules**
- Append-only log storage (no deletes, no updates)
- Structured event schema with correlation ID
- Actor identification (user_id, admin_id, system, anonymous)
- Resource and action taxonomy
- Before/after state snapshots for mutations
- Event signatures (HMAC chained hashing for tamper evidence)
- Log retention policies (online: 1 year, cold archive: 7 years)
- Real-time streaming to SIEM systems
- Audit log viewer with filtering and export
- Compliance reporting (GDPR, PCI-DSS, SOX)
- Anomaly detection rules

**Dependencies**
- All modules — event publishers
- `USR` — actor identity resolution

**Data Entities**
- `audit_logs` — id, event_id (UUID), timestamp, actor_type (user/system/admin), actor_id, actor_ip, action, resource_type, resource_id, changes (JSONB — before/after), metadata (JSONB), correlation_id, signature (HMAC), sequence_number
- `audit_retention_policies` — event_type, online_days, archive_days, destroy_after_days
- `audit_archives` — id, period_start, period_end, event_count, storage_location, checksum
- `audit_anomaly_rules` — id, name, condition (JSONB), severity, notification_channel

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `AUD.LOG(event_type, actor, action, resource, changes, metadata)` | Write log entry (internal) |
| Command | `AUD.LOG_BATCH(entries[])` | Bulk write |
| Query | `AUD.SEARCH(filters, page)` | Log query |
| Query | `AUD.GET_EVENT(event_id)` | Single event detail |
| Query | `AUD.EXPORT(filters, format)` | Export for compliance |
| Event | `audit.log.written` | (Internal — SIEM stream) |

**Error Handling**
| Error | Strategy |
|---|---|
| Log write failure | Non-blocking; retry via queue with guaranteed delivery |
| Signature mismatch (integrity check) | Critical alert; mark chain as compromised |
| Query on archived data | Trigger retrieval from cold storage; notify user of delay |
| Retention policy not found | Apply default (7 years online); log configuration gap |

**Performance**
| Aspect | Strategy |
|---|---|
| Write throughput | Batch writes every 500ms or 1000 events (whichever first) |
| Write path | Asynchronous, fire-and-forget; never in critical request path |
| Online query | PostgreSQL partitioned by month; indexes on `actor_id + timestamp`, `resource_type + resource_id` |
| Archive retrieval | S3 Glacier with 3-5 hour retrieval SLA |
| Integrity check | Daily batch verification of HMAC chain |

**Security**
- Append-only: database user used by AUD module has no UPDATE or DELETE privileges
- HMAC chain: each entry `signature = HMAC(prev_signature + event_data, rotation_key)`
- Audit logs cannot be tampered with even by database administrators (separate IAM role)
- Sensitive fields automatically masked (passwords, tokens, PII) before logging
- Logs shipped to separate SIEM (Splunk, ELK) for independent storage
- Access to AUD requires `audit:view` permission; export requires `audit:export`

**Integration Points**
- All modules: Implement `AuditableMixin` that auto-generates AUD events for entity mutations
- SIEM: Stream via Kafka to Splunk / ELK / DataDog for real-time security monitoring
- Compliance: Automated SOC2 / PCI-DSS / GDPR audit report generation
- Admin: Read-only log viewer with filtered search and drill-down

---

### 2.28 SET — Settings

| Attribute | Detail |
|---|---|
| **Module ID** | `SET` |
| **Layer** | Domain |
| **Responsibility** | Provide a centralized, versioned configuration store for all system settings, feature flags, and platform policies. |

**Core Features & Sub-Modules**
- Key-value settings store with JSONB values
- Setting categories and namespacing
- Setting versioning and change history
- Environment-specific overrides (dev/staging/prod)
- Feature flags with percentage rollout and user targeting
- Policy definitions (refund windows, dispute SLAs, commission rates)
- Setting validation rules (type, range, enum)
- Cache invalidation on setting changes
- Bulk export/import of settings
- Setting audit log

**Dependencies**
- `USR` — user targeting for feature flags
- `AUD` — setting change audit trail
- `AUTHZ` — setting access permissions

**Data Entities**
- `settings` — id, key (namespaced), value (JSONB), type (string/number/boolean/json), description, category, is_encrypted, version
- `setting_overrides` — id, setting_id, environment, value, created_by
- `feature_flags` — id, key, description, is_enabled, rollout_percentage, user_segment (JSONB), created_at
- `setting_policies` — id, key, value (JSONB), effective_from, effective_until, version, approved_by
- `setting_changelog` — id, setting_id, previous_value, new_value, changed_by, changed_at
- `setting_schemas` — id, key, schema (JSON Schema), validation_class

**Public Interfaces**

| Type | Signature | Description |
|---|---|---|
| Command | `SET.GET(key, context)` | Resolve setting (with overrides) |
| Command | `SET.SET(key, value, changed_by)` | Update setting |
| Command | `SET.DELETE(key)` | Remove setting (archive) |
| Command | `SET.FLAG_IS_ENABLED(flag_key, user_context)` | Check feature flag |
| Command | `SET.GET_POLICY(policy_key, effective_date)` | Get policy at date |
| Query | `SET.LIST_CATEGORY(category)` | All settings in category |
| Query | `SET.GET_HISTORY(key)` | Change history |
| Event | `setting.updated` | Setting changed |
| Event | `setting.feature_flag.changed` | Feature flag toggled |
| Event | `setting.policy.updated` | Policy version changed |
| REST | `GET /api/v1/settings` | List (admin) |
| REST | `PUT /api/v1/settings/{key}` | Update setting |
| REST | `GET /api/v1/flags/{key}` | Check feature flag |

**Error Handling**
| Error | Strategy |
|---|---|
| Setting key not found | Return 404; include list of available keys in category |
| Validation error (schema mismatch) | Return 422; include validation message from JSON Schema |
| Encrypted setting read without permission | Return 403; never reveal key existence |
| Circular policy dependency | Reject; detect on write via dependency graph |
| Environment override delete | Revert to base value; do not delete key entirely |

**Performance**
| Aspect | Strategy |
|---|---|
| Setting read | In-memory cache (ConcurrentHashMap) loaded at application startup |
| Cache invalidation | Redis pub/sub broadcast to all service instances on `setting.updated` |
| Feature flag evaluation | < 1 microsecond (in-memory, pre-compiled conditions) |
| Policy effective date lookup | B-tree index on `effective_from + effective_until` |

**Security**
- Encrypted settings (API keys, gateway secrets) encrypted at rest with AES-256-GCM
- Setting access controlled by prefix pattern: `payment.*` settings require `settings:payment` permission
- Feature flag evaluation cannot reveal flag existence to unauthorized users
- Setting changes require dual approval for `production.*` namespace
- Encrypted values never appear in logs, even masked

**Integration Points**
- All modules: Import `SettingsService` singleton for configuration access
- Admin: Settings management UI with categories, search, and change history
- Deployment: CI/CD pipeline updates `environment` overrides during deployment
- Monitoring: Flag changes published to Slack/PagerDuty for critical settings

---

## 3. Dependency Graph Summary

```
AUTH ──► USR ──► RBAC ──► AUTHZ
 │                │
 │                ├──► SEL ──► MKT ──► CAT ──► SRCH
 │                │         │         │
 │                │         │         ├──► CART ──► CHK ──► ORD ──► DEL
 │                │         │         │         │         │
 │                │         │         │         │         ├──► ESC ──► WAL
 │                │         │         │         │         │    │
 │                │         │         │         ├──► PAY ─┤    │
 │                │         │         │         │    │    │    │
 │                │         │         ├──► CPN ─┘    │    │    │
 │                │         │         │              │    │    │
 │                │         │         ├──► AFF ──────┼────┘    │
 │                │         │         │              │         │
 │                │         ├──► REV ─┘              │         │
 │                │         │                        │         │
 │                │         ├──► DSP ────────────────┼─────────┘
 │                │         │                        │
 │                │         ├──► MSG ──► SUP ────────┘
 │                │         │
 │                │         ├──► ADM
 │                │         │
 │                └──► ANL ─┤ (read from all modules)
 │                          │
 │                          └──► CMS
 │
 └──► AUD ──► (all modules write)
 │
 └──► NOT ──► (all modules publish to)
 │
 └──► SET ──► (all modules read from)
```

---

## 4. Cross-Cutting Concerns

| Concern | Approach |
|---|---|
| **Idempotency** | Idempotency keys required on all payment and order mutations; stored with unique constraint and expiry |
| **Concurrency** | Optimistic locking via `version` column on all financial entities; pessimistic locks for inventory |
| **Tracing** | Correlation ID propagated through all service calls via HTTP header `X-Correlation-ID` |
| **Validation** | Input validation at API layer (Pydantic), domain validation in services, DB constraints as final guard |
| **Soft Deletes** | All entities use soft-delete with `deleted_at` column; hard delete only via GDPR purge |
| **Timestamps** | `created_at`, `updated_at` on all entities; `deleted_at` where applicable |
| **Pagination** | Cursor-based pagination for public APIs; offset-based for admin panels |
| **Rate Limiting** | Tiered: anonymous (30/min), authenticated (120/min), admin (300/min), per-endpoint customization |
| **Caching Strategy** | L1 (in-memory) + L2 (Redis) + L3 (CDN) for public content; cache-aside pattern with write-through invalidation |
| **Error Response Format** | Consistent `{ error: { code, message, details, request_id }}` envelope across all APIs |
| **Health Checks** | `/health` → liveness; `/health/ready` → readiness (DB, Redis, ES, Kafka connectivity) |

---

*End of Document — Module Breakdown v1.0*
