# Database Architecture â€” TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-DB-005 |
| **Version** | 2.0 |
| **Status** | Approved |
| **Author** | Principal Database Architect |
| **Date** | 2026-07-01 |

---

## 1. Database Overview

### 1.1 Database Platform

- **Database Engine**: PostgreSQL 15+ (minimum 15.4, targeting 16.x for production)
- **Hosting**: AWS RDS Custom or self-managed EC2 (production), RDS for staging/DR
- **Character Set**: `UTF8` with `en_US.UTF-8` locale
- **Default Collation**: `en_US.UTF-8`

### 1.2 PostgreSQL Extensions

| Extension | Version | Purpose | Schema |
|---|---|---|---|
| `uuid-ossp` | 1.1 | UUID generation (fallback; prefer `gen_random_uuid()`) | `tsbl_system` |
| `pgcrypto` | 1.3 | Column-level encryption, password hashing, random bytes | `tsbl_system` |
| `pg_stat_statements` | 1.10 | Query performance monitoring, slow query identification | `tsbl_system` |
| `pg_trgm` | 1.6 | Trigram-based fuzzy text search (ILIKE, similarity) | `tsbl_system` |
| `btree_gin` | 1.3 | GIN index support on scalar columns for composite GIN indexes | `tsbl_system` |
| `citext` | 1.6 | Case-insensitive character string type | `tsbl_system` |
| `hstore` | 1.8 | Key-value store within PostgreSQL (legacy; prefer JSONB) | `tsbl_system` |
| `ltree` | 1.2 | Hierarchical tree labels for category paths | `tsbl_system` |
| `pg_partman` | 5.0 | Automated partition management and retention | `tsbl_system` |
| `pgaudit` | 1.7 | Comprehensive session/object auditing for DDL and DML | `tsbl_system` |
| `pg_cron` | 1.6 | Scheduled job execution within PostgreSQL | `tsbl_system` |
| `pg_repack` | 1.5 | Online table bloat removal without locks | `tsbl_system` |
| `postgis` | 3.4 | Geo-spatial queries for location-based features | `tsbl_system` |

### 1.3 Schema Architecture

The database is organized into 13 schemas, each representing a bounded domain context:

| # | Schema Name | Domain | Tables |
|---|---|---|---|
| 1 | `tsbl_auth` | Authentication & Authorization | 6 |
| 2 | `tsbl_user` | User Management | 7 |
| 3 | `tsbl_system` | System Reference Data | 8 |
| 4 | `tsbl_marketplace` | Core Marketplace & Catalog | 16 |
| 5 | `tsbl_order` | Order Management & Fulfillment | 6 |
| 6 | `tsbl_product` | Digital Product Licensing | 1 |
| 7 | `tsbl_payment` | Payments, Wallets, Revenue | 14 |
| 8 | `tsbl_communication` | Messaging & Notifications | 7 |
| 9 | `tsbl_support` | Customer Support & Disputes | 4 |
| 10 | `tsbl_content` | CMS & Content Management | 5 |
| 11 | `tsbl_marketing` | Marketing, Affiliates, Loyalty | 3 |
| 12 | `tsbl_analytics` | Analytics & Reporting | 2 |
| 13 | `tsbl_audit` | Auditing, Logging, Admin | 11 |

**Total: 13 schemas, 90 tables**

### 1.4 Design Principles

| Principle | Implementation |
|---|---|
| **UUID Primary Keys** | All tables use `UUID` as primary key, generated via `gen_random_uuid()`. UUIDs prevent enumeration attacks, enable distributed ID generation, and simplify merging across shards. |
| **Soft Deletes** | Every table includes a `deleted_at TIMESTAMPTZ` column. Records are never physically deleted unless by explicit purge policy. All queries filter `WHERE deleted_at IS NULL` by default. |
| **Optimistic Locking** | Every table includes a `version INTEGER DEFAULT 1` column. Updates increment the version and include `WHERE version = <current>` to prevent lost updates. Application retries on version conflict. |
| **TIMESTAMPTZ** | All timestamp columns use `TIMESTAMPTZ` (TIMESTAMP WITH TIME ZONE). Stored internally as UTC; timezone conversion handled at application display layer. Never use `TIMESTAMP` or `TIMESTAMP WITHOUT TIME ZONE`. |
| **CITEXT** | Case-insensitive text fields (email, username, slug, code) use `CITEXT` to avoid lowercasing functions in queries. CITEXT provides transparent case-insensitive comparison while preserving original casing. |
| **JSONB** | Semi-structured and extensible data stored as `JSONB`. GIN indexes with `jsonb_path_ops` for efficient querying. Avoid `JSON` (no binary format, no indexing). |
| **Decimal for Currency** | All monetary amounts use `DECIMAL(18,4)` or `DECIMAL(18,2)`. Never use `FLOAT` or `DOUBLE PRECISION` for currency values due to rounding errors. |
| **Immutable Audit Columns** | `created_at` and `created_by` are set once on INSERT and never modified. `updated_at` and `updated_by` are updated on every row modification via application logic (not triggers). |

---

## 2. Naming Conventions

### 2.1 General Rules

| Element | Convention | Example |
|---|---|---|
| **Schemas** | `tsbl_{module}` â€” lowercase, snake_case | `tsbl_marketplace`, `tsbl_payment` |
| **Tables** | `snake_case`, **plural** nouns | `users`, `order_items`, `product_variants` |
| **Columns** | `snake_case`, **singular** nouns | `first_name`, `product_id`, `created_at` |
| **Primary Keys** | `id` (UUID `DEFAULT gen_random_uuid()`) | `id UUID NOT NULL DEFAULT gen_random_uuid()` |
| **Foreign Keys** | `{referenced_table_singular}_id` | `user_id`, `product_id`, `order_id` |
| **Indexes** | `idx_{table}_{column}` | `idx_products_status` |
| **Unique Constraints** | `uq_{table}_{columns}` | `uq_users_email` |
| **Check Constraints** | `chk_{table}_{description}` | `chk_orders_status_valid` |
| **Primary Key Constraint** | `pk_{table}` | `pk_users` |
| **Foreign Key Constraint** | `fk_{child_table}_{parent_table}` | `fk_order_items_orders` |

### 2.2 Abbreviation Rules

| Rule | Example |
|---|---|
| Avoid abbreviations in table names | Use `authentication`, not `auth` (schema is `tsbl_auth`) |
| Keep column names readable | Use `product_type_id`, not `prod_typ_id` |
| ISO standard codes keep short names | `iso_code_2`, `iso_code_3` |

### 2.3 Reserved Word Avoidance

Never use PostgreSQL reserved words (e.g., `user`, `order`, `group`, `index`, `primary`, `key`) as unquoted identifiers. If unavoidable, the table name `orders` (plural) is acceptable as it does not conflict with the reserved word `ORDER`.

### 2.4 JSONB Field Naming

JSONB keys inside `metadata` or `attributes` columns follow `snake_case` convention identical to column naming: `{"first_name": "John", "preferred_contact": "email"}`.

---

## 3. Base Column Template

Every table in the TSBL database follows a strict base column template. These columns are defined first in every `CREATE TABLE` statement.

### 3.1 Base Columns

| Column Name | Data Type | Constraints | Default | Description |
|---|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | `gen_random_uuid()` | Globally unique identifier, never exposed as sequential ID |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | Row creation timestamp (immutable after INSERT) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | Last modification timestamp (updated on every change) |
| `deleted_at` | `TIMESTAMPTZ` | â€” | `NULL` | Soft delete timestamp; `NULL` = active record |
| `created_by` | `UUID` | `REFERENCES users(id)` (nullable) | `NULL` | User ID who created the record |
| `updated_by` | `UUID` | `REFERENCES users(id)` (nullable) | `NULL` | User ID who last modified the record |
| `version` | `INTEGER` | `NOT NULL DEFAULT 1` | `1` | Optimistic lock counter; incremented on every update |

### 3.2 Common Patterns

- **`updated_at` management**: Updated by application layer on every UPDATE. Use `updated_at = NOW()` in the SET clause.
- **Soft delete queries**: Every SELECT on active records must include `AND t.deleted_at IS NULL`. Views or application-level query builders should enforce this automatically.
- **Version checking on update**:
  ```sql
  UPDATE products
  SET name = 'New Name', version = version + 1, updated_at = NOW()
  WHERE id = <uuid> AND version = <current_version>;
  -- Returns 0 rows if optimistic lock fails
  ```

### 3.3 Deviations

The only deviation from the base template is allowed for:
- **Lookup/reference tables** (`countries`, `currencies`, `languages`): May omit `created_by`, `updated_by`, and `version` if row-level auditing is not required.
- **Append-only tables** (`audit_logs`, `analytics_events`): `updated_at`, `updated_by`, and `version` are omitted as rows are immutable.
- **Partitioned tables**: `id` + partition key form the composite primary key. `deleted_at` may be omitted for append-only partitioned tables.

---

## 4. Complete Entity List

| # | Module | Schema | Table Name | Description |
|---|---|---|---|---|
| 1 | Auth | `tsbl_auth` | `authentication` | Authentication methods, password hashes, MFA secrets, reset tokens |
| 2 | User | `tsbl_user` | `users` | Core user accounts with login credentials and status |
| 3 | Auth | `tsbl_auth` | `roles` | System roles defining permission groups |
| 4 | Auth | `tsbl_auth` | `permissions` | Granular permissions for resource-action pairs |
| 5 | Auth | `tsbl_auth` | `user_roles` | Many-to-many user-role assignments |
| 6 | Auth | `tsbl_auth` | `sessions` | Active user sessions with token management |
| 7 | Auth | `tsbl_auth` | `login_history` | Login audit trail (PARTITIONED monthly) |
| 8 | User | `tsbl_user` | `devices` | Registered user devices for push notifications and trusted devices |
| 9 | User | `tsbl_user` | `user_profiles` | Extended user profile information and preferences |
| 10 | User | `tsbl_user` | `seller_profiles` | Seller/vendor profile with store details and metrics |
| 11 | User | `tsbl_user` | `buyer_profiles` | Buyer profile with purchase history and preferences |
| 12 | User | `tsbl_user` | `kyc` | Know Your Customer verification documents and status |
| 13 | User | `tsbl_user` | `addresses` | User addresses (shipping, billing, etc.) |
| 14 | System | `tsbl_system` | `countries` | Country reference data with ISO codes |
| 15 | System | `tsbl_system` | `states` | States and provinces within countries |
| 16 | System | `tsbl_system` | `cities` | Cities within states |
| 17 | System | `tsbl_system` | `languages` | Supported languages with locale codes |
| 18 | System | `tsbl_system` | `currencies` | Supported currencies with exchange rates |
| 19 | Marketplace | `tsbl_marketplace` | `categories` | Hierarchical product categories (ltree path) |
| 20 | Marketplace | `tsbl_marketplace` | `sub_categories` | Sub-categories linked to parent categories |
| 21 | Marketplace | `tsbl_marketplace` | `product_types` | Digital product type definitions and delivery methods |
| 22 | Marketplace | `tsbl_marketplace` | `product_attributes` | Product attribute definitions and allowed values |
| 23 | Marketplace | `tsbl_marketplace` | `products` | Core product listings by sellers |
| 24 | Marketplace | `tsbl_marketplace` | `product_images` | Product image gallery |
| 25 | Marketplace | `tsbl_marketplace` | `product_videos` | Product video embeds and URLs |
| 26 | Marketplace | `tsbl_marketplace` | `product_variants` | Product variations (e.g., license type, format) |
| 27 | Marketplace | `tsbl_marketplace` | `product_inventory` | Stock tracking and availability per product/variant |
| 28 | Marketplace | `tsbl_marketplace` | `product_tags` | Product tags for search and discovery |
| 29 | Marketplace | `tsbl_marketplace` | `product_seo` | Product SEO metadata (meta tags, OG data, structured data) |
| 30 | Marketplace | `tsbl_marketplace` | `search_index_metadata` | Elasticsearch sync tracking per entity |
| 31 | Order | `tsbl_order` | `shopping_cart` | Active shopping cart items |
| 32 | Marketplace | `tsbl_marketplace` | `wishlist` | User wishlist items |
| 33 | Order | `tsbl_order` | `orders` | Order records with buyer, seller, payment, and escrow details |
| 34 | Order | `tsbl_order` | `order_items` | Individual line items within an order |
| 35 | Order | `tsbl_order` | `order_status_history` | Order status change audit trail |
| 36 | Order | `tsbl_order` | `digital_deliveries` | Digital product fulfillment records |
| 37 | Product | `tsbl_product` | `license_keys` | Software license keys (encrypted) |
| 38 | Marketplace | `tsbl_marketplace` | `coupons` | Discount coupon codes and rules |
| 39 | Marketplace | `tsbl_marketplace` | `promotions` | Marketing promotions and campaigns |
| 40 | Payment | `tsbl_payment` | `wallets` | User digital wallets for balance management |
| 41 | Payment | `tsbl_payment` | `wallet_transactions` | Wallet transaction history |
| 42 | Payment | `tsbl_payment` | `escrow_accounts` | Escrow accounts per order for payment protection |
| 43 | Payment | `tsbl_payment` | `escrow_transactions` | Escrow fund movement audit trail |
| 44 | Payment | `tsbl_payment` | `payments` | Payment transactions via payment gateways |
| 45 | Payment | `tsbl_payment` | `payment_methods` | Saved user payment methods (tokenized) |
| 46 | Payment | `tsbl_payment` | `withdrawals` | Seller withdrawal/payout requests |
| 47 | Payment | `tsbl_payment` | `bank_accounts` | Seller bank account details (encrypted) |
| 48 | Payment | `tsbl_payment` | `commission_rules` | Platform commission configuration by tier/category |
| 49 | Payment | `tsbl_payment` | `seller_earnings` | Seller earnings per transaction |
| 50 | Payment | `tsbl_payment` | `platform_revenue` | Platform revenue records |
| 51 | Marketplace | `tsbl_marketplace` | `reviews` | Product reviews by buyers |
| 52 | Marketplace | `tsbl_marketplace` | `ratings` | Rating score breakdowns by category |
| 53 | Marketplace | `tsbl_marketplace` | `buyer_feedback` | Buyer feedback on sellers |
| 54 | Marketplace | `tsbl_marketplace` | `seller_reputation` | Seller reputation scores and metrics |
| 55 | Communication | `tsbl_communication` | `conversations` | Conversation threads between users |
| 56 | Communication | `tsbl_communication` | `messages` | Individual messages within conversations (PARTITIONED monthly) |
| 57 | Communication | `tsbl_communication` | `attachments` | File attachments for messages and tickets |
| 58 | Communication | `tsbl_communication` | `notifications` | In-app notification records |
| 59 | Communication | `tsbl_communication` | `email_queue` | Outbound email queue for transactional emails |
| 60 | Communication | `tsbl_communication` | `sms_queue` | Outbound SMS queue for notifications |
| 61 | Communication | `tsbl_communication` | `push_notifications` | Push notification delivery tracking |
| 62 | Support | `tsbl_support` | `support_tickets` | Customer support ticket records |
| 63 | Support | `tsbl_support` | `ticket_messages` | Messages within support tickets |
| 64 | Support | `tsbl_support` | `disputes` | Order dispute and resolution records |
| 65 | Support | `tsbl_support` | `refund_requests` | Refund request processing |
| 66 | Audit | `tsbl_audit` | `admin_notes` | Internal admin notes on entities |
| 67 | Analytics | `tsbl_analytics` | `reports` | Saved reports and their schedules |
| 68 | Analytics | `tsbl_analytics` | `analytics_events` | User behavior and analytics events (PARTITIONED monthly) |
| 69 | Audit | `tsbl_audit` | `audit_logs` | Data change audit trail (PARTITIONED monthly) |
| 70 | Audit | `tsbl_audit` | `activity_logs` | User activity stream (logins, actions, exports) |
| 71 | System | `tsbl_system` | `api_keys` | API key management for integrations |
| 72 | System | `tsbl_system` | `api_rate_limits` | Rate limit tracking per API key |
| 73 | System | `tsbl_system` | `feature_flags` | Feature toggle flags for gradual rollout |
| 74 | Content | `tsbl_content` | `cms_pages` | CMS-managed content pages |
| 75 | Content | `tsbl_content` | `blog` | Blog articles and posts |
| 76 | Content | `tsbl_content` | `faq` | Frequently asked questions |
| 77 | Content | `tsbl_content` | `banners` | Homepage and promotional banners |
| 78 | Content | `tsbl_content` | `announcements` | Platform announcements and alerts |
| 79 | Marketing | `tsbl_marketing` | `affiliate_program` | Affiliate partnership records |
| 80 | Marketing | `tsbl_marketing` | `referral_system` | User referral tracking and rewards |
| 81 | Marketing | `tsbl_marketing` | `loyalty_program` | Loyalty points and tiers |
| 82 | System | `tsbl_system` | `taxes` | Tax rate configuration by jurisdiction |
| 83 | Payment | `tsbl_payment` | `invoices` | Generated invoice records |
| 84 | Payment | `tsbl_payment` | `invoice_items` | Individual line items on invoices |
| 85 | Order | `tsbl_order` | `shipping` | Shipping tracking records |
| 86 | Marketplace | `tsbl_marketplace` | `downloads` | Digital asset download tracking |
| 87 | Audit | `tsbl_audit` | `security_logs` | Security event logs (PARTITIONED monthly) |
| 88 | Audit | `tsbl_audit` | `fraud_detection_logs` | Fraud detection alerts (PARTITIONED monthly) |
| 89 | System | `tsbl_system` | `blacklist` | Blacklisted users, IPs, devices |
| 90 | System | `tsbl_system` | `whitelist` | Whitelisted entities (IPs, emails, domains) |

---


---

## 5. Relationship Diagram (Text-based ASCII)

### 5.1 Core Entity Relationships

```
                                       +------------+
                                       |   ROLES    |
                                       +-----+------+
                                             |
                                    +--------+--------+
                                    |                  |
                            +-------v-------+  +------v-------+
                            |  USER_ROLES   |  | PERMISSIONS  |
                            +-------+-------+  +--------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
  +-------v-------+         +------v-------+         +-------v-------+
  |    USERS      |         | SESSIONS     |         | LOGIN_HISTORY |
  +---+---+---+---+         +--------------+         +---------------+
      |   |   |
      |   |   +----------------------+---------------------------------+
      |   |                          |                                 |
+-----v---+------+     +------------v------------+     +--------------v----+
| USER_PROFILES   |     | SELLER_PROFILES         |     | BUYER_PROFILES    |
+-----------------+     +---------+---------------+     +---------+--------+
                                  |                             |
                                  |                             |
                         +--------v--------+           +-------v--------+
                         |    PRODUCTS     |           |   ADDRESSES   |
                         +---+--+--+---+---+           +----------------+
                             |  |  |   |
                +------------+  |  |   +----------------------------+
                |               |  |                                |
         +------v------+  +-----v--v----+                   +------v------+
         | CATEGORIES   |  | SUB_       |                   | PRODUCT_TAGS|
         +------+-------+  | CATEGORIES |                   +-------------+
                |          +-------------+
        +-------v--------+
        | PRODUCT_TYPES  |
        +----------------+

  +------+------+      +-------------------+      +------------------+
  |   ORDERS    |      |   ORDER_ITEMS     |      | DIGITAL_         |
  +---+--+--+---+      +--------+----------+      | DELIVERIES       |
      |  |  |                    |                 +--------+---------+
      |  |  |            +-------v--------+                 |
      |  |  |            | LICENSE_KEYS   |                 |
      |  |  |            +----------------+                 |
      |  |  |                                                |
+-----v--v--v--------+     +------------------+
|   ORDER_STATUS_    |     |   PAYMENTS       |
|   HISTORY          |     +-----+-----+------+
+--------------------+           |     |
                         +-------v-+ +-v--------+
                         |  ESCROW | | WALLETS  |
                         | ACCOUNTS| +--+-------+
                         +---------+    |
                                       |
                                +------v-------+
                                | WALLET_      |
                                | TRANSACTIONS |
                                +--------------+

  +-----------+---+        +-----------------+
  | REVIEWS   |   |        | RATINGS         |
  +------+----+---+        +-----------------+
         |
  +------v------+          +------------------+
  | BUYER_      |          | SELLER_          |
  | FEEDBACK    |          | REPUTATION       |
  +-------------+          +------------------+

  +----------------+       +-----------------+
  | CONVERSATIONS  |------>| MESSAGES        |
  +--------+-------+       +-----------------+
           |
    +------v------+
    | ATTACHMENTS |
    +-------------+

  +----------------+       +-----------------+
  | NOTIFICATIONS  |       | EMAIL_QUEUE     |
  +----------------+       +-----------------+

  +----------------+       +-----------------+
  | SUPPORT_       |------>| TICKET_         |
  | TICKETS        |       | MESSAGES        |
  +-------+--------+       +-----------------+
          |
  +-------v--------+
  | DISPUTES       |
  +----------------+
```

### 5.2 Foreign Key Reference Summary

```
users.id ----> authentication.user_id
           --> user_profiles.user_id
           --> seller_profiles.user_id
           --> buyer_profiles.user_id
           --> kyc.user_id
           --> addresses.user_id
           --> user_roles.user_id
           --> sessions.user_id
           --> devices.user_id
           --> wallets.user_id
           --> reviews.buyer_id
           --> orders.buyer_id
           --> shopping_cart.user_id
           --> wishlist.user_id

products.id --> product_images.product_id
           --> product_videos.product_id
           --> product_variants.product_id
           --> product_inventory.product_id
           --> product_tags.product_id
           --> product_seo.product_id
           --> order_items.product_id
           --> reviews.product_id
           --> license_keys.product_id
           --> downloads.product_id

orders.id ---> order_items.order_id
          ---> order_status_history.order_id
          ---> payments.order_id
          ---> escrow_accounts.order_id
          ---> disputes.order_id
          ---> refund_requests.order_id
          ---> invoices.order_id

categories.id --> sub_categories.category_id
            --> products.category_id (self-referencing parent_id)

conversations.id --> messages.conversation_id
support_tickets.id --> ticket_messages.ticket_id

wallets.id --> wallet_transactions.wallet_id
escrow_accounts.id --> escrow_transactions.escrow_account_id
```

---

## 6. Table Dependency Graph

### 6.1 Dependency Levels

Tables are assigned to dependency levels based on their foreign key references. Level 0 tables have no non-base foreign keys.

```
Level 0 (Standalone -- no FK dependencies beyond base):
+-------------------------------------------------------------+
| countries   currencies   languages   roles   permissions    |
| product_types   feature_flags   api_keys   product_attributes|
+-------------------------------------------------------------+

Level 1 (Depend on Level 0):
+-------------------------------------------------------------+
| users (depends on: languages, currencies)                   |
| categories (depends on: self-referencing parent_id)         |
| taxes (depends on: countries, states)                       |
| cms_pages (has author_id -> users)                          |
| states (depends on: countries)                              |
| cities (depends on: states)                                 |
+-------------------------------------------------------------+

Level 2 (Depend on Level 0-1):
+-------------------------------------------------------------+
| user_profiles | seller_profiles | buyer_profiles | addresses |
| products | coupons | promotions | blog | sub_categories     |
| authentication | user_roles | sessions | devices | kyc     |
| login_history | product_attributes | wallets              |
| payment_methods | bank_accounts | api_rate_limits          |
+-------------------------------------------------------------+

Level 3 (Depend on Level 0-2):
+-------------------------------------------------------------+
| orders | reviews | conversations | support_tickets          |
| affiliate_program | referral_system | loyalty_program       |
| product_images | product_videos | product_variants          |
| product_inventory | product_tags | product_seo              |
| search_index_metadata | wishlist | shopping_cart            |
| announcements | banners | faq | blacklist | whitelist       |
+-------------------------------------------------------------+

Level 4+ (Depend on Level 3+):
+-------------------------------------------------------------+
| order_items | order_status_history | payments               |
| escrow_accounts | escrow_transactions | digital_deliveries  |
| license_keys | wallet_transactions | withdrawals            |
| seller_earnings | platform_revenue | commission_rules       |
| ratings | buyer_feedback | seller_reputation               |
| messages | attachments | notifications                     |
| email_queue | sms_queue | push_notifications               |
| ticket_messages | disputes | refund_requests               |
| invoices | invoice_items | shipping | downloads             |
| admin_notes | reports | analytics_events                   |
| audit_logs | activity_logs | security_logs                 |
| fraud_detection_logs                                        |
+-------------------------------------------------------------+
```

### 6.2 Migration Order

1. Extensions and schemas
2. Level 0: `countries`, `currencies`, `languages`, `roles`, `permissions`, `product_types`, `feature_flags`, `api_keys`, `product_attributes`
3. Level 1: `users`, `categories`, `taxes`, `cms_pages`, `states`, `cities`
4. Level 2: All level 2 tables
5. Level 3: All level 3 tables
6. Level 4+: All remaining tables

---



## 7. Complete Table Specifications

### 7.1 authentication (tsbl_auth)

- **Description**: Stores authentication credentials, password hashes, MFA secrets, and reset tokens.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `auth_method(CITEXT NOT NULL)`, `password_hash(TEXT)`, `mfa_secret(TEXT)`, `mfa_enabled(BOOLEAN DEFAULT FALSE)`, `mfa_type(CITEXT)`, `password_changed_at(TIMESTAMPTZ)`, `reset_token(TEXT)`, `reset_token_expires_at(TIMESTAMPTZ)`, `last_login_at(TIMESTAMPTZ)`, `failed_attempts(INTEGER DEFAULT 0)`, `locked_until(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_authentication_user_id`, `idx_authentication_user_auth_method` ON `(user_id, auth_method)`, `idx_authentication_reset_token` WHERE `reset_token IS NOT NULL`
- **Unique Constraints**: `uq_authentication_user_method` ON `(user_id, auth_method)` WHERE `deleted_at IS NULL`

### 7.2 users (tsbl_user)

- **Description**: Core user accounts. Every entity that can authenticate is represented here.
- **Columns**: `id(UUID PK)`, `username(CITEXT NOT NULL)`, `email(CITEXT NOT NULL)`, `phone(CITEXT)`, `status(CITEXT DEFAULT 'active')`, `user_type(CITEXT DEFAULT 'buyer')`, `is_verified(BOOLEAN DEFAULT FALSE)`, `email_verified_at(TIMESTAMPTZ)`, `phone_verified_at(TIMESTAMPTZ)`, `profile_photo_url(TEXT)`, `last_active_at(TIMESTAMPTZ)`, `locale(CITEXT DEFAULT 'en')`, `timezone(CITEXT DEFAULT 'UTC')`, plus all base columns.
- **Indexes**: `idx_users_email`, `idx_users_username`, `idx_users_phone`, `idx_users_status`, `idx_users_user_type`, `idx_users_status_type` ON `(status, user_type)`, `idx_users_created_at`
- **Unique Constraints**: `uq_users_email` WHERE `deleted_at IS NULL`, `uq_users_username` WHERE `deleted_at IS NULL`, `uq_users_phone` WHERE `deleted_at IS NULL AND phone IS NOT NULL`

### 7.3 roles (tsbl_auth)

- **Description**: System role definitions grouping permissions for user assignment.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `is_system_role(BOOLEAN DEFAULT FALSE)`, `priority(INTEGER DEFAULT 0)`, plus all base columns.
- **Indexes**: `idx_roles_slug`
- **Unique Constraints**: `uq_roles_slug` WHERE `deleted_at IS NULL`

### 7.4 permissions (tsbl_auth)

- **Description**: Granular permission definitions for resource-action pairs.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `module(CITEXT NOT NULL)`, `resource(CITEXT NOT NULL)`, `action(CITEXT NOT NULL)`, plus all base columns.
- **Indexes**: `idx_permissions_slug`, `idx_permissions_resource_action` ON `(resource, action)`
- **Unique Constraints**: `uq_permissions_slug` WHERE `deleted_at IS NULL`

### 7.5 user_roles (tsbl_auth)

- **Description**: Many-to-many user-role assignments with metadata.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `role_id(UUID NOT NULL FK->roles)`, `assigned_by(UUID FK->users)`, `assigned_at(TIMESTAMPTZ DEFAULT NOW())`, `expires_at(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_user_roles_user_id`, `idx_user_roles_role_id`, `idx_user_roles_user_role` ON `(user_id, role_id)`
- **Unique Constraints**: `uq_user_roles_user_role` ON `(user_id, role_id)` WHERE `deleted_at IS NULL`

### 7.6 sessions (tsbl_auth)

- **Description**: Active user sessions with token hashes and device tracking.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `token_hash(TEXT NOT NULL)`, `refresh_token_hash(TEXT)`, `ip_address(INET)`, `user_agent(TEXT)`, `device_id(UUID FK->devices)`, `expires_at(TIMESTAMPTZ NOT NULL)`, `last_activity_at(TIMESTAMPTZ)`, `is_revoked(BOOLEAN DEFAULT FALSE)`, plus all base columns.
- **Indexes**: `idx_sessions_user_id`, `idx_sessions_token_hash`, `idx_sessions_expires_at`, `idx_sessions_active` ON `user_id` WHERE `is_revoked = FALSE AND expires_at > NOW()`
- **Unique Constraints**: `uq_sessions_token_hash`

### 7.7 login_history (tsbl_auth) -- PARTITIONED

- **Description**: Login audit trail. PARTITIONED BY RANGE(created_at) monthly.
- **Columns**: `id(UUID PK)`, `user_id(UUID FK->users)`, `login_at(TIMESTAMPTZ NOT NULL)`, `ip_address(INET)`, `user_agent(TEXT)`, `device_id(UUID FK->devices)`, `login_method(CITEXT NOT NULL)`, `status(CITEXT NOT NULL)`, `failure_reason(TEXT)`, `location_geo(GEOGRAPHY(POINT))`, plus base columns.
- **Partitioning**: `PARTITION BY RANGE (created_at)` -- monthly
- **Indexes**: `idx_login_history_user_id`, `idx_login_history_status`, `idx_login_history_login_at`

### 7.8 devices (tsbl_user)

- **Description**: Registered user devices for push notifications and session management.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `device_name(CITEXT)`, `device_type(CITEXT)`, `os(CITEXT)`, `browser(CITEXT)`, `push_token(TEXT)`, `is_trusted(BOOLEAN DEFAULT FALSE)`, `last_used_at(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_devices_user_id`, `idx_devices_push_token`
- **Unique Constraints**: `uq_devices_push_token` WHERE `push_token IS NOT NULL`

### 7.9 user_profiles (tsbl_user)

- **Description**: Extended user profile information and preferences.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users 1:1)`, `first_name(CITEXT)`, `last_name(CITEXT)`, `display_name(CITEXT)`, `bio(TEXT)`, `date_of_birth(DATE)`, `gender(CITEXT)`, `nationality(CITEXT)`, `language_id(UUID FK->languages)`, `currency_id(UUID FK->currencies)`, `timezone(CITEXT)`, `social_links(JSONB)`, `preferences(JSONB)`, plus all base columns.
- **Indexes**: `idx_user_profiles_user_id`, `idx_user_profiles_display_name`, `idx_user_profiles_preferences` GIN
- **Unique Constraints**: `uq_user_profiles_user_id`

### 7.10 seller_profiles (tsbl_user)

- **Description**: Seller store profile with metrics, tier, and policy.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users 1:1)`, `store_name(CITEXT NOT NULL)`, `store_slug(CITEXT NOT NULL)`, `store_description(TEXT)`, `store_logo_url(TEXT)`, `store_banner_url(TEXT)`, `store_status(CITEXT DEFAULT 'pending')`, `commission_rate(DECIMAL(5,4))`, `total_sales(DECIMAL(18,2) DEFAULT 0)`, `total_revenue(DECIMAL(18,2) DEFAULT 0)`, `rating_avg(REAL DEFAULT 0)`, `rating_count(INTEGER DEFAULT 0)`, `response_time_avg(INTERVAL)`, `store_tier(CITEXT DEFAULT 'bronze')`, `joined_at(TIMESTAMPTZ DEFAULT NOW())`, `store_policy(JSONB)`, plus all base columns.
- **Indexes**: `idx_seller_profiles_user_id`, `idx_seller_profiles_store_slug`, `idx_seller_profiles_status`, `idx_seller_profiles_tier`
- **Unique Constraints**: `uq_seller_profiles_user_id`, `uq_seller_profiles_store_slug`

### 7.11 buyer_profiles (tsbl_user)

- **Description**: Buyer profile with purchase history and tier.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users 1:1)`, `default_shipping_address_id(UUID FK->addresses)`, `default_billing_address_id(UUID FK->addresses)`, `total_orders(INTEGER DEFAULT 0)`, `total_spent(DECIMAL(18,2) DEFAULT 0)`, `buyer_tier(CITEXT DEFAULT 'regular')`, `preferences(JSONB)`, plus all base columns.
- **Indexes**: `idx_buyer_profiles_user_id`, `idx_buyer_profiles_tier`
- **Unique Constraints**: `uq_buyer_profiles_user_id`

### 7.12 kyc (tsbl_user)

- **Description**: Know Your Customer verification documents and status.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `id_type(CITEXT NOT NULL)`, `id_number(TEXT encrypted)`, `id_front_image(TEXT)`, `id_back_image(TEXT)`, `selfie_image(TEXT)`, `verification_status(CITEXT DEFAULT 'pending')`, `verified_by(UUID FK->users)`, `verified_at(TIMESTAMPTZ)`, `rejection_reason(TEXT)`, `submitted_at(TIMESTAMPTZ DEFAULT NOW())`, `expires_at(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_kyc_user_id`, `idx_kyc_status`, `idx_kyc_user_status` ON `(user_id, verification_status)`
- **Unique Constraints**: `uq_kyc_user_id_type` ON `(user_id, id_type)` WHERE `deleted_at IS NULL`

### 7.13 addresses (tsbl_user)

- **Description**: User addresses for shipping, billing, and other purposes.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `label(CITEXT)`, `address_line1(TEXT NOT NULL)`, `address_line2(TEXT)`, `city_id(UUID FK->cities)`, `state_id(UUID FK->states)`, `country_id(UUID FK->countries)`, `postal_code(CITEXT)`, `latitude(REAL)`, `longitude(REAL)`, `is_default(BOOLEAN DEFAULT FALSE)`, `type(CITEXT DEFAULT 'shipping')`, `phone(CITEXT)`, plus all base columns.
- **Indexes**: `idx_addresses_user_id`, `idx_addresses_country_id`, `idx_addresses_city_id`, `idx_addresses_user_default` ON `(user_id, is_default)` WHERE `deleted_at IS NULL`

### 7.14 countries (tsbl_system)

- **Description**: ISO country reference data.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `iso_code_2(CHAR(2) NOT NULL)`, `iso_code_3(CHAR(3) NOT NULL)`, `dial_code(CITEXT)`, `currency_id(UUID FK->currencies)`, `is_active(BOOLEAN DEFAULT TRUE)`, `sort_order(INTEGER DEFAULT 0)`, plus base subset.
- **Indexes**: `idx_countries_iso2`, `idx_countries_active`
- **Unique Constraints**: `uq_countries_iso_code_2`, `uq_countries_iso_code_3`

### 7.15 states (tsbl_system)

- **Description**: States and provinces within countries.
- **Columns**: `id(UUID PK)`, `country_id(UUID NOT NULL FK->countries)`, `name(CITEXT NOT NULL)`, `state_code(CITEXT)`, `is_active(BOOLEAN DEFAULT TRUE)`, plus base columns.
- **Indexes**: `idx_states_country_id`, `idx_states_code`
- **Unique Constraints**: `uq_states_country_code` ON `(country_id, state_code)` WHERE `state_code IS NOT NULL`

### 7.16 cities (tsbl_system)

- **Description**: Cities within states.
- **Columns**: `id(UUID PK)`, `state_id(UUID NOT NULL FK->states)`, `name(CITEXT NOT NULL)`, `is_active(BOOLEAN DEFAULT TRUE)`, `timezone(CITEXT)`, plus base columns.
- **Indexes**: `idx_cities_state_id`, `idx_cities_name`

### 7.17 languages (tsbl_system)

- **Description**: Supported languages for UI localization.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `code(CITEXT NOT NULL)`, `locale(CITEXT NOT NULL)`, `is_default(BOOLEAN DEFAULT FALSE)`, `is_active(BOOLEAN DEFAULT TRUE)`, `sort_order(INTEGER DEFAULT 0)`, `rtl(BOOLEAN DEFAULT FALSE)`, plus base columns.
- **Indexes**: `idx_languages_code`
- **Unique Constraints**: `uq_languages_code`, `uq_languages_locale`

### 7.18 currencies (tsbl_system)

- **Description**: Supported currencies with exchange rates.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `code(CITEXT NOT NULL)`, `symbol(CITEXT NOT NULL)`, `exchange_rate(DECIMAL(18,8) DEFAULT 1)`, `is_default(BOOLEAN DEFAULT FALSE)`, `is_active(BOOLEAN DEFAULT TRUE)`, `decimal_places(INTEGER DEFAULT 2)`, `sort_order(INTEGER DEFAULT 0)`, plus base columns.
- **Indexes**: `idx_currencies_code`
- **Unique Constraints**: `uq_currencies_code`

### 7.19 categories (tsbl_marketplace)

- **Description**: Hierarchical product categories using ltree.
- **Columns**: `id(UUID PK)`, `parent_id(UUID FK->categories self)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `icon_url(TEXT)`, `image_url(TEXT)`, `is_active(BOOLEAN DEFAULT TRUE)`, `sort_order(INTEGER DEFAULT 0)`, `level(INTEGER DEFAULT 0)`, `path(LTREE)`, `product_count(INTEGER DEFAULT 0)`, plus all base columns.
- **Indexes**: `idx_categories_parent_id`, `idx_categories_slug`, `idx_categories_path` GIST
- **Unique Constraints**: `uq_categories_slug` WHERE `deleted_at IS NULL`

### 7.20 sub_categories (tsbl_marketplace)

- **Description**: Sub-categories linked to parent categories.
- **Columns**: `id(UUID PK)`, `category_id(UUID NOT NULL FK->categories)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `icon_url(TEXT)`, `is_active(BOOLEAN DEFAULT TRUE)`, `sort_order(INTEGER DEFAULT 0)`, `product_count(INTEGER DEFAULT 0)`, plus all base columns.
- **Indexes**: `idx_sub_categories_category_id`, `idx_sub_categories_slug`
- **Unique Constraints**: `uq_sub_categories_slug` WHERE `deleted_at IS NULL`

### 7.21 product_types (tsbl_marketplace)

- **Description**: Digital product type definitions.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `delivery_method(CITEXT NOT NULL)`, `is_active(BOOLEAN DEFAULT TRUE)`, `sort_order(INTEGER DEFAULT 0)`, plus all base columns.
- **Indexes**: `idx_product_types_slug`
- **Unique Constraints**: `uq_product_types_slug`

### 7.22 product_attributes (tsbl_marketplace)

- **Description**: Product attribute definitions and allowed values.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `type(CITEXT NOT NULL)`, `is_required(BOOLEAN DEFAULT FALSE)`, `is_filterable(BOOLEAN DEFAULT FALSE)`, `is_searchable(BOOLEAN DEFAULT FALSE)`, `sort_order(INTEGER DEFAULT 0)`, `options(JSONB)`, `category_id(UUID FK->categories)`, plus all base columns.
- **Indexes**: `idx_product_attributes_slug`, `idx_product_attributes_category`
- **Unique Constraints**: `uq_product_attributes_slug`

### 7.23 products (tsbl_marketplace)

- **Description**: Core product listings by sellers. Central marketplace entity.
- **Columns**: `id(UUID PK)`, `seller_id(UUID NOT NULL FK->users)`, `category_id(UUID FK->categories)`, `sub_category_id(UUID FK->sub_categories)`, `product_type_id(UUID FK->product_types)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `short_description(TEXT)`, `base_price(DECIMAL(18,2) NOT NULL)`, `sale_price(DECIMAL(18,2))`, `currency_id(UUID NOT NULL FK->currencies)`, `status(CITEXT DEFAULT 'draft')`, `is_featured(BOOLEAN DEFAULT FALSE)`, `is_digital(BOOLEAN DEFAULT TRUE)`, `delivery_time(INTERVAL)`, `requirements(TEXT)`, `faq(JSONB)`, `metadata(JSONB)`, `total_sales(INTEGER DEFAULT 0)`, `rating_avg(REAL DEFAULT 0)`, `rating_count(INTEGER DEFAULT 0)`, `approved_by(UUID FK->users)`, `approved_at(TIMESTAMPTZ)`, `rejected_reason(TEXT)`, `published_at(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_products_seller_id`, `idx_products_category_id`, `idx_products_slug`, `idx_products_status`, `idx_products_created_at`, `idx_products_seller_status` ON `(seller_id, status)`, `idx_products_category_status` ON `(category_id, status)`, `idx_products_metadata` GIN
- **Unique Constraints**: `uq_products_slug`

### 7.24 product_images (tsbl_marketplace)

- **Description**: Product image gallery with primary image support.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `variant_id(UUID FK->product_variants)`, `url(TEXT NOT NULL)`, `alt_text(TEXT)`, `sort_order(INTEGER DEFAULT 0)`, `is_primary(BOOLEAN DEFAULT FALSE)`, `width(INTEGER)`, `height(INTEGER)`, `file_size(INTEGER)`, plus all base columns.
- **Indexes**: `idx_product_images_product_id`, `idx_product_images_variant_id`, `idx_product_images_product_primary` ON `(product_id, is_primary)` WHERE `deleted_at IS NULL`

### 7.25 product_videos (tsbl_marketplace)

- **Description**: Product video embeds and URLs.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `url(TEXT NOT NULL)`, `embed_url(TEXT)`, `type(CITEXT NOT NULL)`, `thumbnail_url(TEXT)`, `sort_order(INTEGER DEFAULT 0)`, `is_primary(BOOLEAN DEFAULT FALSE)`, plus all base columns.
- **Indexes**: `idx_product_videos_product_id`

### 7.26 product_variants (tsbl_marketplace)

- **Description**: Product variations for different options.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `name(CITEXT NOT NULL)`, `sku(CITEXT NOT NULL)`, `price(DECIMAL(18,2) NOT NULL)`, `sale_price(DECIMAL(18,2))`, `stock(INTEGER DEFAULT 0)`, `is_available(BOOLEAN DEFAULT TRUE)`, `attributes(JSONB)`, `sort_order(INTEGER DEFAULT 0)`, plus all base columns.
- **Indexes**: `idx_product_variants_product_id`, `idx_product_variants_sku`
- **Unique Constraints**: `uq_product_variants_sku`

### 7.27 product_inventory (tsbl_marketplace)

- **Description**: Inventory tracking with reserved and sold quantities.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `variant_id(UUID FK->product_variants)`, `quantity(INTEGER DEFAULT 0)`, `reserved_quantity(INTEGER DEFAULT 0)`, `sold_quantity(INTEGER DEFAULT 0)`, `low_stock_threshold(INTEGER DEFAULT 10)`, `is_infinite(BOOLEAN DEFAULT FALSE)`, `last_restocked_at(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_product_inventory_product_id`, `idx_product_inventory_variant_id`, `idx_product_inventory_low_stock` WHERE `quantity <= low_stock_threshold AND is_infinite = FALSE`
- **Unique Constraints**: `uq_product_inventory_product_variant` ON `(product_id, variant_id)` WHERE `deleted_at IS NULL`

### 7.28 product_tags (tsbl_marketplace)

- **Description**: Tags associated with products for search.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `tag(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, plus all base columns.
- **Indexes**: `idx_product_tags_product_id`, `idx_product_tags_tag`, `idx_product_tags_slug`
- **Unique Constraints**: `uq_product_tags_product_tag` ON `(product_id, slug)`

### 7.29 product_seo (tsbl_marketplace)

- **Description**: SEO metadata for products.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products 1:1)`, `meta_title(CITEXT)`, `meta_description(TEXT)`, `meta_keywords(TEXT[])`, `canonical_url(TEXT)`, `og_title(CITEXT)`, `og_description(TEXT)`, `og_image(TEXT)`, `structured_data(JSONB)`, plus all base columns.
- **Indexes**: `idx_product_seo_product_id`, `idx_product_seo_meta_keywords` GIN
- **Unique Constraints**: `uq_product_seo_product_id`

### 7.30 search_index_metadata (tsbl_marketplace)

- **Description**: Elasticsearch sync tracking per entity.
- **Columns**: `id(UUID PK)`, `indexable_type(CITEXT NOT NULL)`, `indexable_id(UUID NOT NULL)`, `last_indexed_at(TIMESTAMPTZ)`, `index_version(INTEGER DEFAULT 1)`, `is_synced(BOOLEAN DEFAULT FALSE)`, `sync_attempts(INTEGER DEFAULT 0)`, `last_error(TEXT)`, `priority(INTEGER DEFAULT 0)`, plus base columns.
- **Indexes**: `idx_search_index_metadata_type_id` ON `(indexable_type, indexable_id)`, `idx_search_index_metadata_unsynced` ON `(indexable_type, priority)` WHERE `is_synced = FALSE AND sync_attempts < 5`
- **Unique Constraints**: `uq_search_index_metadata_type_id` ON `(indexable_type, indexable_id)`

### 7.31 shopping_cart (tsbl_order)

- **Description**: Active shopping cart items.
- **Columns**: `id(UUID PK)`, `user_id(UUID FK->users)`, `session_id(CITEXT)`, `product_id(UUID NOT NULL FK->products)`, `variant_id(UUID FK->product_variants)`, `quantity(INTEGER DEFAULT 1)`, `unit_price(DECIMAL(18,2) NOT NULL)`, `total_price(DECIMAL(18,2) NOT NULL)`, `coupon_id(UUID FK->coupons)`, `is_saved_for_later(BOOLEAN DEFAULT FALSE)`, `expires_at(TIMESTAMPTZ)`, plus base columns.
- **Indexes**: `idx_shopping_cart_user_id`, `idx_shopping_cart_session_id`

### 7.32 wishlist (tsbl_marketplace)

- **Description**: User wishlist items.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `product_id(UUID NOT NULL FK->products)`, `variant_id(UUID FK->product_variants)`, `notes(TEXT)`, `is_public(BOOLEAN DEFAULT FALSE)`, `sort_order(INTEGER DEFAULT 0)`, plus all base columns.
- **Indexes**: `idx_wishlist_user_id`, `idx_wishlist_product_id`
- **Unique Constraints**: `uq_wishlist_user_product` ON `(user_id, product_id, variant_id)` WHERE `deleted_at IS NULL`

### 7.33 orders (tsbl_order)

- **Description**: Core order records managing the full order lifecycle.
- **Columns**: `id(UUID PK)`, `order_number(CITEXT NOT NULL)`, `buyer_id(UUID NOT NULL FK->users)`, `seller_id(UUID NOT NULL FK->users)`, `status(CITEXT DEFAULT 'pending')`, `subtotal(DECIMAL(18,2) NOT NULL)`, `discount_amount(DECIMAL(18,2) DEFAULT 0)`, `coupon_id(UUID FK->coupons)`, `tax_amount(DECIMAL(18,2) DEFAULT 0)`, `total_amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID NOT NULL FK->currencies)`, `payment_status(CITEXT DEFAULT 'pending')`, `payment_id(UUID FK->payments)`, `escrow_id(UUID FK->escrow_accounts)`, `shipping_address_id(UUID FK->addresses)`, `billing_address_id(UUID FK->addresses)`, `buyer_note(TEXT)`, `seller_note(TEXT)`, `is_priority(BOOLEAN DEFAULT FALSE)`, `is_disputed(BOOLEAN DEFAULT FALSE)`, `completed_at(TIMESTAMPTZ)`, `cancelled_at(TIMESTAMPTZ)`, `cancelled_by(UUID FK->users)`, `cancellation_reason(TEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_orders_buyer_id`, `idx_orders_seller_id`, `idx_orders_status`, `idx_orders_payment_status`, `idx_orders_created_at`, `idx_orders_order_number`, `idx_orders_buyer_status` ON `(buyer_id, status)`, `idx_orders_seller_status` ON `(seller_id, status)`, `idx_orders_metadata` GIN
- **Unique Constraints**: `uq_orders_order_number`

### 7.34 order_items (tsbl_order)

- **Description**: Individual line items within an order with snapshots.
- **Columns**: `id(UUID PK)`, `order_id(UUID NOT NULL FK->orders)`, `product_id(UUID NOT NULL FK->products)`, `variant_id(UUID FK->product_variants)`, `seller_id(UUID NOT NULL FK->users)`, `product_name(CITEXT NOT NULL)`, `variant_name(CITEXT)`, `quantity(INTEGER DEFAULT 1)`, `unit_price(DECIMAL(18,2) NOT NULL)`, `discount_amount(DECIMAL(18,2) DEFAULT 0)`, `tax_rate(DECIMAL(5,4) DEFAULT 0)`, `tax_amount(DECIMAL(18,2) DEFAULT 0)`, `total_price(DECIMAL(18,2) NOT NULL)`, `delivery_method(CITEXT)`, `delivery_status(CITEXT DEFAULT 'pending')`, `license_key_id(UUID FK->license_keys)`, `is_digital(BOOLEAN DEFAULT TRUE)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_order_items_order_id`, `idx_order_items_product_id`, `idx_order_items_seller_id`, `idx_order_items_delivery_status`

### 7.35 order_status_history (tsbl_order)

- **Description**: Audit of all order status changes.
- **Columns**: `id(UUID PK)`, `order_id(UUID NOT NULL FK->orders)`, `from_status(CITEXT)`, `to_status(CITEXT NOT NULL)`, `changed_by(UUID FK->users)`, `changed_at(TIMESTAMPTZ DEFAULT NOW())`, `reason(TEXT)`, `is_automated(BOOLEAN DEFAULT FALSE)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_order_status_history_order_id`, `idx_order_status_history_changed_at`

### 7.36 digital_deliveries (tsbl_order)

- **Description**: Digital product fulfillment records.
- **Columns**: `id(UUID PK)`, `order_item_id(UUID NOT NULL FK->order_items)`, `product_id(UUID NOT NULL FK->products)`, `delivery_method(CITEXT NOT NULL)`, `delivery_url(TEXT)`, `license_key_id(UUID FK->license_keys)`, `downloaded_at(TIMESTAMPTZ)`, `download_count(INTEGER DEFAULT 0)`, `max_downloads(INTEGER)`, `expires_at(TIMESTAMPTZ)`, `delivery_status(CITEXT DEFAULT 'pending')`, `delivered_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_digital_deliveries_order_item_id`, `idx_digital_deliveries_license_key_id`, `idx_digital_deliveries_status`

### 7.37 license_keys (tsbl_product)

- **Description**: Software license keys (encrypted via pgcrypto).
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `variant_id(UUID FK->product_variants)`, `seller_id(UUID NOT NULL FK->users)`, `key(TEXT NOT NULL encrypted)`, `type(CITEXT NOT NULL)`, `order_item_id(UUID FK->order_items)`, `is_sold(BOOLEAN DEFAULT FALSE)`, `sold_at(TIMESTAMPTZ)`, `buyer_id(UUID FK->users)`, `is_revoked(BOOLEAN DEFAULT FALSE)`, `revoked_at(TIMESTAMPTZ)`, `revoked_by(UUID FK->users)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_license_keys_product_id`, `idx_license_keys_seller_id`, `idx_license_keys_product_available` ON `(product_id, variant_id)` WHERE `is_sold = FALSE AND is_revoked = FALSE`
- **Unique Constraints**: `uq_license_keys_key`

### 7.38 coupons (tsbl_marketplace)

- **Description**: Discount coupon codes with usage rules.
- **Columns**: `id(UUID PK)`, `code(CITEXT NOT NULL)`, `seller_id(UUID FK->users)`, `type(CITEXT NOT NULL)`, `value(DECIMAL(18,2) NOT NULL)`, `min_order_amount(DECIMAL(18,2))`, `max_discount(DECIMAL(18,2))`, `usage_limit(INTEGER)`, `used_count(INTEGER DEFAULT 0)`, `per_user_limit(INTEGER DEFAULT 1)`, `is_active(BOOLEAN DEFAULT TRUE)`, `starts_at(TIMESTAMPTZ NOT NULL)`, `expires_at(TIMESTAMPTZ NOT NULL)`, `applicable_products(UUID[])`, `applicable_categories(UUID[])`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_coupons_code`, `idx_coupons_seller_id`, `idx_coupons_applicable_products` GIN, `idx_coupons_applicable_categories` GIN
- **Unique Constraints**: `uq_coupons_code`

### 7.39 promotions (tsbl_marketplace)

- **Description**: Marketing promotions and campaigns.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `type(CITEXT NOT NULL)`, `discount_type(CITEXT NOT NULL)`, `discount_value(DECIMAL(18,2) NOT NULL)`, `is_active(BOOLEAN DEFAULT TRUE)`, `starts_at(TIMESTAMPTZ NOT NULL)`, `ends_at(TIMESTAMPTZ NOT NULL)`, `usage_limit(INTEGER)`, `used_count(INTEGER DEFAULT 0)`, `seller_id(UUID FK->users)`, `is_featured(BOOLEAN DEFAULT FALSE)`, `banner_url(TEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_promotions_slug`, `idx_promotions_active_dates` ON `(is_active, starts_at, ends_at)`, `idx_promotions_seller_id`
- **Unique Constraints**: `uq_promotions_slug`

### 7.40 wallets (tsbl_payment)

- **Description**: User digital wallets for balance management.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `balance(DECIMAL(18,2) DEFAULT 0)`, `currency_id(UUID NOT NULL FK->currencies)`, `status(CITEXT DEFAULT 'active')`, `held_balance(DECIMAL(18,2) DEFAULT 0)`, `available_balance(DECIMAL(18,2) DEFAULT 0)`, `total_deposited(DECIMAL(18,2) DEFAULT 0)`, `total_withdrawn(DECIMAL(18,2) DEFAULT 0)`, `last_transaction_at(TIMESTAMPTZ)`, plus all base columns.
- **Indexes**: `idx_wallets_user_id`, `idx_wallets_currency_id`
- **Unique Constraints**: `uq_wallets_user_currency` ON `(user_id, currency_id)`
- **Check Constraints**: `chk_wallets_balance_non_negative` CHECK (`balance >= 0`)

### 7.41 wallet_transactions (tsbl_payment)

- **Description**: Audit trail of all wallet movements.
- **Columns**: `id(UUID PK)`, `wallet_id(UUID NOT NULL FK->wallets)`, `transaction_type(CITEXT NOT NULL)`, `amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID NOT NULL FK->currencies)`, `balance_before(DECIMAL(18,2) NOT NULL)`, `balance_after(DECIMAL(18,2) NOT NULL)`, `reference_type(CITEXT)`, `reference_id(UUID)`, `description(TEXT)`, `status(CITEXT DEFAULT 'completed')`, `processed_at(TIMESTAMPTZ DEFAULT NOW())`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_wallet_transactions_wallet_id`, `idx_wallet_transactions_type`, `idx_wallet_transactions_processed_at`, `idx_wallet_transactions_reference` ON `(reference_type, reference_id)`

### 7.42 escrow_accounts (tsbl_payment)

- **Description**: Escrow accounts for secure payment processing.
- **Columns**: `id(UUID PK)`, `order_id(UUID NOT NULL FK->orders)`, `buyer_id(UUID NOT NULL FK->users)`, `seller_id(UUID NOT NULL FK->users)`, `amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID NOT NULL FK->currencies)`, `status(CITEXT DEFAULT 'held')`, `released_amount(DECIMAL(18,2) DEFAULT 0)`, `held_since(TIMESTAMPTZ DEFAULT NOW())`, `released_at(TIMESTAMPTZ)`, `released_by(UUID FK->users)`, `release_condition(CITEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_escrow_accounts_order_id`, `idx_escrow_accounts_buyer_id`, `idx_escrow_accounts_seller_id`, `idx_escrow_accounts_status`
- **Unique Constraints**: `uq_escrow_accounts_order_id`

### 7.43 escrow_transactions (tsbl_payment)

- **Description**: Audit of fund movements within escrow.
- **Columns**: `id(UUID PK)`, `escrow_account_id(UUID NOT NULL FK->escrow_accounts)`, `transaction_type(CITEXT NOT NULL)`, `amount(DECIMAL(18,2) NOT NULL)`, `balance_before(DECIMAL(18,2) NOT NULL)`, `balance_after(DECIMAL(18,2) NOT NULL)`, `initiated_by(UUID FK->users)`, `approved_by(UUID FK->users)`, `reason(TEXT)`, `status(CITEXT)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_escrow_transactions_escrow_account_id`

### 7.44 payments (tsbl_payment)

- **Description**: Payment transactions via gateways.
- **Columns**: `id(UUID PK)`, `order_id(UUID FK->orders)`, `buyer_id(UUID NOT NULL FK->users)`, `payment_method_id(UUID FK->payment_methods)`, `amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID NOT NULL FK->currencies)`, `gateway(CITEXT)`, `gateway_transaction_id(CITEXT)`, `status(CITEXT)`, `fee(DECIMAL(18,2) DEFAULT 0)`, `net_amount(DECIMAL(18,2) NOT NULL)`, `refunded_amount(DECIMAL(18,2) DEFAULT 0)`, `paid_at(TIMESTAMPTZ)`, `failure_reason(TEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_payments_order_id`, `idx_payments_buyer_id`, `idx_payments_gateway_txn`, `idx_payments_status`

### 7.45 payment_methods (tsbl_payment)

- **Description**: Saved user payment methods (tokenized).
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `type(CITEXT NOT NULL)`, `provider(CITEXT)`, `last_four(VARCHAR(4))`, `expiry_month(INTEGER)`, `expiry_year(INTEGER)`, `card_holder_name(TEXT)`, `token(TEXT encrypted)`, `is_default(BOOLEAN DEFAULT FALSE)`, `is_verified(BOOLEAN DEFAULT FALSE)`, `billing_address_id(UUID FK->addresses)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_payment_methods_user_id`

### 7.46 withdrawals (tsbl_payment)

- **Description**: Seller withdrawal requests.
- **Columns**: `id(UUID PK)`, `seller_id(UUID NOT NULL FK->users)`, `amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID NOT NULL FK->currencies)`, `bank_account_id(UUID FK->bank_accounts)`, `status(CITEXT)`, `fee(DECIMAL(18,2) DEFAULT 0)`, `net_amount(DECIMAL(18,2) NOT NULL)`, `requested_at(TIMESTAMPTZ DEFAULT NOW())`, `processed_at(TIMESTAMPTZ)`, `processed_by(UUID FK->users)`, `rejection_reason(TEXT)`, `gateway(CITEXT)`, `gateway_reference(CITEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_withdrawals_seller_id`, `idx_withdrawals_status`, `idx_withdrawals_requested_at`

### 7.47 bank_accounts (tsbl_payment)

- **Description**: Seller bank account details (encrypted).
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `bank_name(CITEXT)`, `branch_name(CITEXT)`, `account_holder_name(TEXT)`, `account_number(TEXT encrypted)`, `routing_number(CITEXT)`, `swift_code(CITEXT)`, `iban(CITEXT)`, `is_verified(BOOLEAN DEFAULT FALSE)`, `is_default(BOOLEAN DEFAULT FALSE)`, `verified_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_bank_accounts_user_id`

### 7.48 commission_rules (tsbl_payment)

- **Description**: Platform commission configuration by tier/category.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `seller_tier(CITEXT)`, `category_id(UUID FK->categories)`, `product_type_id(UUID FK->product_types)`, `commission_type(CITEXT)`, `commission_value(DECIMAL(18,2))`, `min_fee(DECIMAL(18,2))`, `max_fee(DECIMAL(18,2))`, `is_active(BOOLEAN DEFAULT TRUE)`, `effective_from(TIMESTAMPTZ)`, `effective_to(TIMESTAMPTZ)`, `priority(INTEGER DEFAULT 0)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_commission_rules_active` ON `(is_active, effective_from, effective_to)`

### 7.49 seller_earnings (tsbl_payment)

- **Description**: Seller earnings per transaction.
- **Columns**: `id(UUID PK)`, `seller_id(UUID NOT NULL FK->users)`, `order_id(UUID FK->orders)`, `order_item_id(UUID FK->order_items)`, `amount(DECIMAL(18,2) NOT NULL)`, `commission_amount(DECIMAL(18,2) DEFAULT 0)`, `commission_rate(DECIMAL(5,4))`, `net_amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID FK->currencies)`, `status(CITEXT)`, `released_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_seller_earnings_seller_id`, `idx_seller_earnings_order_id`

### 7.50 platform_revenue (tsbl_payment)

- **Description**: Platform revenue records.
- **Columns**: `id(UUID PK)`, `order_id(UUID FK->orders)`, `seller_id(UUID FK->users)`, `amount(DECIMAL(18,2) NOT NULL)`, `commission_rate(DECIMAL(5,4))`, `fee_amount(DECIMAL(18,2) DEFAULT 0)`, `total_revenue(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID FK->currencies)`, `recorded_at(TIMESTAMPTZ DEFAULT NOW())`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_platform_revenue_order_id`, `idx_platform_revenue_recorded_at`


### 7.51 reviews (tsbl_marketplace)

- **Description**: Product reviews by buyers with ratings and moderation.
- **Columns**: `id(UUID PK)`, `product_id(UUID NOT NULL FK->products)`, `order_id(UUID FK->orders)`, `buyer_id(UUID NOT NULL FK->users)`, `rating(SMALLINT NOT NULL)`, `title(CITEXT)`, `content(TEXT)`, `is_verified_purchase(BOOLEAN DEFAULT FALSE)`, `is_approved(BOOLEAN DEFAULT FALSE)`, `status(CITEXT)`, `helpful_count(INTEGER DEFAULT 0)`, `reported_count(INTEGER DEFAULT 0)`, `approved_by(UUID FK->users)`, `approved_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_reviews_product_id`, `idx_reviews_buyer_id`, `idx_reviews_status`, `idx_reviews_product_rating` ON `(product_id, rating)`
- **Check Constraints**: `chk_reviews_rating_range` CHECK (`rating >= 1 AND rating <= 5`)

### 7.52 ratings (tsbl_marketplace)

- **Description**: Rating score breakdowns by category.
- **Columns**: `id(UUID PK)`, `product_id(UUID FK->products)`, `seller_id(UUID FK->users)`, `rating_category(CITEXT)`, `score(REAL DEFAULT 0)`, `count(INTEGER DEFAULT 0)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_ratings_product_id`, `idx_ratings_seller_id`

### 7.53 buyer_feedback (tsbl_marketplace)

- **Description**: Buyer feedback on sellers.
- **Columns**: `id(UUID PK)`, `order_id(UUID FK->orders)`, `buyer_id(UUID NOT NULL FK->users)`, `seller_id(UUID NOT NULL FK->users)`, `communication_rating(SMALLINT)`, `delivery_rating(SMALLINT)`, `quality_rating(SMALLINT)`, `overall_rating(SMALLINT)`, `comment(TEXT)`, `is_anonymous(BOOLEAN DEFAULT FALSE)`, `is_approved(BOOLEAN DEFAULT FALSE)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_buyer_feedback_order_id`, `idx_buyer_feedback_seller_id`

### 7.54 seller_reputation (tsbl_marketplace)

- **Description**: Seller reputation scores and metrics.
- **Columns**: `id(UUID PK)`, `seller_id(UUID NOT NULL FK->users 1:1)`, `overall_score(REAL DEFAULT 0)`, `communication_score(REAL DEFAULT 0)`, `delivery_score(REAL DEFAULT 0)`, `quality_score(REAL DEFAULT 0)`, `total_reviews(INTEGER DEFAULT 0)`, `positive_reviews(INTEGER DEFAULT 0)`, `negative_reviews(INTEGER DEFAULT 0)`, `response_rate(REAL DEFAULT 0)`, `response_time_avg(INTERVAL)`, `last_calculated_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_seller_reputation_seller_id`, `idx_seller_reputation_score`
- **Unique Constraints**: `uq_seller_reputation_seller_id`

### 7.55 conversations (tsbl_communication)

- **Description**: Conversation threads between users for buyer-seller communication.
- **Columns**: `id(UUID PK)`, `subject(TEXT)`, `type(CITEXT NOT NULL)`, `buyer_id(UUID FK->users)`, `seller_id(UUID FK->users)`, `support_ticket_id(UUID FK->support_tickets)`, `last_message_at(TIMESTAMPTZ)`, `last_message_preview(TEXT)`, `message_count(INTEGER DEFAULT 0)`, `status(CITEXT DEFAULT 'active')`, `closed_by(UUID FK->users)`, `closed_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_conversations_buyer_id`, `idx_conversations_seller_id`, `idx_conversations_status`

### 7.56 messages (tsbl_communication) -- PARTITIONED

- **Description**: Individual messages within conversations. PARTITIONED BY RANGE(created_at) monthly.
- **Columns**: `id(UUID PK)`, `conversation_id(UUID NOT NULL FK->conversations)`, `sender_id(UUID NOT NULL FK->users)`, `message_type(CITEXT DEFAULT 'text')`, `content(TEXT)`, `metadata(JSONB)`, `is_read(BOOLEAN DEFAULT FALSE)`, `read_at(TIMESTAMPTZ)`, `is_edited(BOOLEAN DEFAULT FALSE)`, `edited_at(TIMESTAMPTZ)`, `is_deleted_for_sender(BOOLEAN DEFAULT FALSE)`, `is_deleted_for_all(BOOLEAN DEFAULT FALSE)`, plus base columns.
- **Partitioning**: `PARTITION BY RANGE (created_at)` -- monthly
- **Indexes**: `idx_messages_conversation_id`, `idx_messages_sender_id`, `idx_messages_created_at`

### 7.57 attachments (tsbl_communication)

- **Description**: File attachments for messages and tickets.
- **Columns**: `id(UUID PK)`, `message_id(UUID FK->messages)`, `ticket_message_id(UUID FK->ticket_messages)`, `file_name(TEXT NOT NULL)`, `file_path(TEXT NOT NULL)`, `file_type(CITEXT)`, `file_size(INTEGER)`, `url(TEXT)`, `thumbnail_url(TEXT)`, `uploader_id(UUID FK->users)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_attachments_message_id`, `idx_attachments_ticket_message_id`

### 7.58 notifications (tsbl_communication)

- **Description**: In-app notification records.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `type(CITEXT NOT NULL)`, `title(CITEXT NOT NULL)`, `body(TEXT)`, `data(JSONB)`, `is_read(BOOLEAN DEFAULT FALSE)`, `read_at(TIMESTAMPTZ)`, `is_archived(BOOLEAN DEFAULT FALSE)`, `reference_type(CITEXT)`, `reference_id(UUID)`, `priority(CITEXT DEFAULT 'normal')`, `expires_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_notifications_user_id`, `idx_notifications_user_unread` ON `user_id` WHERE `is_read = FALSE AND is_archived = FALSE`, `idx_notifications_type`, `idx_notifications_created_at`

### 7.59 email_queue (tsbl_communication)

- **Description**: Outbound email queue for transactional emails.
- **Columns**: `id(UUID PK)`, `to_email(TEXT NOT NULL)`, `to_user_id(UUID FK->users)`, `from_email(TEXT)`, `subject(TEXT NOT NULL)`, `body_html(TEXT)`, `body_text(TEXT)`, `template_name(CITEXT)`, `template_data(JSONB)`, `status(CITEXT DEFAULT 'pending')`, `priority(INTEGER DEFAULT 0)`, `sent_at(TIMESTAMPTZ)`, `sent_count(INTEGER DEFAULT 0)`, `max_attempts(INTEGER DEFAULT 3)`, `last_error(TEXT)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_email_queue_status`, `idx_email_queue_priority` ON `(status, priority)` WHERE `sent_count < max_attempts`

### 7.60 sms_queue (tsbl_communication)

- **Description**: Outbound SMS queue.
- **Columns**: `id(UUID PK)`, `to_phone(TEXT NOT NULL)`, `to_user_id(UUID FK->users)`, `message(TEXT NOT NULL)`, `template_name(CITEXT)`, `template_data(JSONB)`, `status(CITEXT DEFAULT 'pending')`, `priority(INTEGER DEFAULT 0)`, `sent_at(TIMESTAMPTZ)`, `sent_count(INTEGER DEFAULT 0)`, `max_attempts(INTEGER DEFAULT 3)`, `last_error(TEXT)`, `delivery_report(JSONB)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_sms_queue_status`

### 7.61 push_notifications (tsbl_communication)

- **Description**: Push notification delivery tracking.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users)`, `device_id(UUID FK->devices)`, `title(CITEXT NOT NULL)`, `body(TEXT)`, `data(JSONB)`, `status(CITEXT DEFAULT 'pending')`, `sent_at(TIMESTAMPTZ)`, `read_at(TIMESTAMPTZ)`, `delivered_at(TIMESTAMPTZ)`, `failed_at(TIMESTAMPTZ)`, `failure_reason(TEXT)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_push_notifications_user_id`, `idx_push_notifications_status`

### 7.62 support_tickets (tsbl_support)

- **Description**: Customer support ticket records.
- **Columns**: `id(UUID PK)`, `ticket_number(CITEXT NOT NULL)`, `user_id(UUID NOT NULL FK->users)`, `assigned_to(UUID FK->users)`, `subject(TEXT NOT NULL)`, `description(TEXT)`, `priority(CITEXT DEFAULT 'normal')`, `status(CITEXT DEFAULT 'open')`, `category(CITEXT)`, `source(CITEXT)`, `is_escalated(BOOLEAN DEFAULT FALSE)`, `escalated_to(UUID FK->users)`, `escalated_at(TIMESTAMPTZ)`, `resolved_at(TIMESTAMPTZ)`, `closed_at(TIMESTAMPTZ)`, `closed_by(UUID FK->users)`, `satisfaction_rating(SMALLINT)`, `time_to_first_response(INTERVAL)`, `time_to_resolution(INTERVAL)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_support_tickets_user_id`, `idx_support_tickets_assigned_to`, `idx_support_tickets_status`, `idx_support_tickets_ticket_number`
- **Unique Constraints**: `uq_support_tickets_ticket_number`

### 7.63 ticket_messages (tsbl_support)

- **Description**: Messages within support tickets.
- **Columns**: `id(UUID PK)`, `ticket_id(UUID NOT NULL FK->support_tickets)`, `sender_id(UUID NOT NULL FK->users)`, `message_type(CITEXT DEFAULT 'text')`, `content(TEXT)`, `is_internal(BOOLEAN DEFAULT FALSE)`, `attachments(JSONB)`, `is_read(BOOLEAN DEFAULT FALSE)`, `read_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_ticket_messages_ticket_id`, `idx_ticket_messages_sender_id`

### 7.64 disputes (tsbl_support)

- **Description**: Order dispute and resolution records.
- **Columns**: `id(UUID PK)`, `dispute_number(CITEXT NOT NULL)`, `order_id(UUID NOT NULL FK->orders)`, `raised_by(UUID NOT NULL FK->users)`, `raised_against(UUID NOT NULL FK->users)`, `dispute_type(CITEXT NOT NULL)`, `reason(TEXT)`, `description(TEXT)`, `evidence(JSONB)`, `status(CITEXT DEFAULT 'open')`, `assigned_moderator_id(UUID FK->users)`, `resolution(TEXT)`, `resolved_at(TIMESTAMPTZ)`, `resolved_by(UUID FK->users)`, `metadata(JSONB)`, `outcome(CITEXT)`, `compensation_amount(DECIMAL(18,2))`, `compensation_currency_id(UUID FK->currencies)`, plus all base columns.
- **Indexes**: `idx_disputes_order_id`, `idx_disputes_status`, `idx_disputes_dispute_number`
- **Unique Constraints**: `uq_disputes_dispute_number`

### 7.65 refund_requests (tsbl_support)

- **Description**: Refund request processing.
- **Columns**: `id(UUID PK)`, `order_id(UUID FK->orders)`, `order_item_id(UUID FK->order_items)`, `buyer_id(UUID NOT NULL FK->users)`, `seller_id(UUID NOT NULL FK->users)`, `reason(CITEXT NOT NULL)`, `description(TEXT)`, `requested_amount(DECIMAL(18,2))`, `currency_id(UUID FK->currencies)`, `status(CITEXT DEFAULT 'pending')`, `approved_by(UUID FK->users)`, `approved_at(TIMESTAMPTZ)`, `processed_at(TIMESTAMPTZ)`, `refund_amount(DECIMAL(18,2))`, `refund_method(CITEXT)`, `refund_transaction_id(CITEXT)`, `rejection_reason(TEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_refund_requests_order_id`, `idx_refund_requests_status`

### 7.66 admin_notes (tsbl_audit)

- **Description**: Internal admin notes on entities (polymorphic).
- **Columns**: `id(UUID PK)`, `admin_id(UUID NOT NULL FK->users)`, `reference_type(CITEXT NOT NULL)`, `reference_id(UUID NOT NULL)`, `note(TEXT NOT NULL)`, `is_pinned(BOOLEAN DEFAULT FALSE)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_admin_notes_admin_id`, `idx_admin_notes_reference` ON `(reference_type, reference_id)`

### 7.67 reports (tsbl_analytics)

- **Description**: Saved reports and their schedules.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `type(CITEXT NOT NULL)`, `parameters(JSONB)`, `generated_by(UUID FK->users)`, `generated_at(TIMESTAMPTZ)`, `file_url(TEXT)`, `status(CITEXT)`, `schedule(CITEXT)`, `is_scheduled(BOOLEAN DEFAULT FALSE)`, `last_run_at(TIMESTAMPTZ)`, `next_run_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_reports_generated_by`, `idx_reports_type`

### 7.68 analytics_events (tsbl_analytics) -- PARTITIONED

- **Description**: User behavior analytics events. PARTITIONED BY RANGE(occurred_at) monthly.
- **Columns**: `id(UUID PK)`, `event_type(CITEXT NOT NULL)`, `event_name(CITEXT NOT NULL)`, `user_id(UUID FK->users)`, `session_id(CITEXT)`, `product_id(UUID FK->products)`, `page_url(TEXT)`, `referrer_url(TEXT)`, `device_type(CITEXT)`, `ip_address(INET)`, `location_geo(GEOGRAPHY(POINT))`, `properties(JSONB)`, `occurred_at(TIMESTAMPTZ NOT NULL)`, plus base columns (without updated_at/version).
- **Partitioning**: `PARTITION BY RANGE (occurred_at)` -- monthly
- **Indexes**: `idx_analytics_events_type`, `idx_analytics_events_name`, `idx_analytics_events_user_id`, `idx_analytics_events_occurred_at`

### 7.69 audit_logs (tsbl_audit) -- PARTITIONED

- **Description**: Data change audit trail. PARTITIONED BY RANGE(created_at) monthly.
- **Columns**: `id(UUID PK)`, `actor_id(UUID)`, `actor_type(CITEXT)`, `action(CITEXT NOT NULL)`, `resource_type(CITEXT NOT NULL)`, `resource_id(UUID)`, `changes(JSONB)`, `old_values(JSONB)`, `new_values(JSONB)`, `ip_address(INET)`, `user_agent(TEXT)`, `status(CITEXT)`, `metadata(JSONB)`, plus base columns (without updated_at/version).
- **Partitioning**: `PARTITION BY RANGE (created_at)` -- monthly
- **Indexes**: `idx_audit_logs_actor` ON `(actor_id, actor_type)`, `idx_audit_logs_resource` ON `(resource_type, resource_id)`, `idx_audit_logs_action`, `idx_audit_logs_created_at`

### 7.70 activity_logs (tsbl_audit)

- **Description**: User activity stream.
- **Columns**: `id(UUID PK)`, `user_id(UUID FK->users)`, `activity_type(CITEXT NOT NULL)`, `description(TEXT)`, `reference_type(CITEXT)`, `reference_id(UUID)`, `metadata(JSONB)`, `ip_address(INET)`, `occurred_at(TIMESTAMPTZ DEFAULT NOW())`, plus base columns.
- **Indexes**: `idx_activity_logs_user_id`, `idx_activity_logs_type`, `idx_activity_logs_occurred_at`

### 7.71 api_keys (tsbl_system)

- **Description**: API key management for integrations.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `user_id(UUID FK->users)`, `key_hash(TEXT NOT NULL)`, `key_prefix(CITEXT NOT NULL)`, `scopes(TEXT[])`, `rate_limit(INTEGER)`, `rate_limit_window(INTERVAL)`, `is_active(BOOLEAN DEFAULT TRUE)`, `expires_at(TIMESTAMPTZ)`, `last_used_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_api_keys_key_hash`, `idx_api_keys_user_id`
- **Unique Constraints**: `uq_api_keys_key_hash`

### 7.72 api_rate_limits (tsbl_system)

- **Description**: Rate limit tracking per API key.
- **Columns**: `id(UUID PK)`, `api_key_id(UUID FK->api_keys)`, `endpoint(CITEXT NOT NULL)`, `window_start(TIMESTAMPTZ NOT NULL)`, `request_count(INTEGER DEFAULT 0)`, `max_requests(INTEGER NOT NULL)`, `is_throttled(BOOLEAN DEFAULT FALSE)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_api_rate_limits_key_endpoint` ON `(api_key_id, endpoint)`, `idx_api_rate_limits_window`

### 7.73 feature_flags (tsbl_system)

- **Description**: Feature toggle flags for gradual rollout.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `is_enabled(BOOLEAN DEFAULT FALSE)`, `enabled_for_roles(TEXT[])`, `enabled_for_users(UUID[])`, `percentage_rollout(REAL)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_feature_flags_slug`
- **Unique Constraints**: `uq_feature_flags_slug`

### 7.74 cms_pages (tsbl_content)

- **Description**: CMS-managed content pages.
- **Columns**: `id(UUID PK)`, `title(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `content(JSONB)`, `meta_title(CITEXT)`, `meta_description(TEXT)`, `is_published(BOOLEAN DEFAULT FALSE)`, `published_at(TIMESTAMPTZ)`, `author_id(UUID FK->users)`, `template(CITEXT)`, `sort_order(INTEGER DEFAULT 0)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_cms_pages_slug`, `idx_cms_pages_published` ON `(is_published, published_at)`
- **Unique Constraints**: `uq_cms_pages_slug`

### 7.75 blog (tsbl_content)

- **Description**: Blog articles and posts.
- **Columns**: `id(UUID PK)`, `title(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `excerpt(TEXT)`, `content(JSONB)`, `featured_image(TEXT)`, `author_id(UUID FK->users)`, `category(CITEXT)`, `tags(TEXT[])`, `is_published(BOOLEAN DEFAULT FALSE)`, `published_at(TIMESTAMPTZ)`, `view_count(INTEGER DEFAULT 0)`, `meta_title(CITEXT)`, `meta_description(TEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_blog_slug`, `idx_blog_author_id`, `idx_blog_tags` GIN, `idx_blog_published_at`
- **Unique Constraints**: `uq_blog_slug`

### 7.76 faq (tsbl_content)

- **Description**: Frequently asked questions.
- **Columns**: `id(UUID PK)`, `question(TEXT NOT NULL)`, `answer(TEXT NOT NULL)`, `category(CITEXT)`, `is_published(BOOLEAN DEFAULT FALSE)`, `sort_order(INTEGER DEFAULT 0)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_faq_category`

### 7.77 banners (tsbl_content)

- **Description**: Homepage and promotional banners.
- **Columns**: `id(UUID PK)`, `title(CITEXT NOT NULL)`, `slug(CITEXT NOT NULL)`, `description(TEXT)`, `image_url(TEXT)`, `mobile_image_url(TEXT)`, `link_url(TEXT)`, `link_type(CITEXT)`, `position(CITEXT)`, `is_active(BOOLEAN DEFAULT TRUE)`, `starts_at(TIMESTAMPTZ)`, `expires_at(TIMESTAMPTZ)`, `sort_order(INTEGER DEFAULT 0)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_banners_slug`, `idx_banners_active_position` ON `(is_active, position)`
- **Unique Constraints**: `uq_banners_slug`

### 7.78 announcements (tsbl_content)

- **Description**: Platform announcements and alerts.
- **Columns**: `id(UUID PK)`, `title(CITEXT NOT NULL)`, `content(JSONB)`, `type(CITEXT)`, `is_active(BOOLEAN DEFAULT TRUE)`, `starts_at(TIMESTAMPTZ)`, `expires_at(TIMESTAMPTZ)`, `priority(CITEXT DEFAULT 'normal')`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_announcements_active_dates` ON `(is_active, starts_at, expires_at)`

### 7.79 affiliate_program (tsbl_marketing)

- **Description**: Affiliate partnership records.
- **Columns**: `id(UUID PK)`, `affiliate_id(UUID NOT NULL FK->users)`, `referral_code(CITEXT NOT NULL)`, `parent_affiliate_id(UUID FK->affiliate_program self)`, `commission_rate(DECIMAL(5,4))`, `total_earned(DECIMAL(18,2) DEFAULT 0)`, `total_paid(DECIMAL(18,2) DEFAULT 0)`, `balance(DECIMAL(18,2) DEFAULT 0)`, `status(CITEXT DEFAULT 'active')`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_affiliate_program_affiliate_id`, `idx_affiliate_program_referral_code`
- **Unique Constraints**: `uq_affiliate_program_referral_code`

### 7.80 referral_system (tsbl_marketing)

- **Description**: User referral tracking and rewards.
- **Columns**: `id(UUID PK)`, `referrer_id(UUID NOT NULL FK->users)`, `referred_id(UUID NOT NULL FK->users)`, `referral_code(CITEXT NOT NULL)`, `reward_type(CITEXT)`, `reward_value(DECIMAL(18,2))`, `status(CITEXT DEFAULT 'pending')`, `reward_granted_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_referral_system_referrer_id`, `idx_referral_system_referred_id`
- **Unique Constraints**: `uq_referral_system_referrer_referred` ON `(referrer_id, referred_id)`

### 7.81 loyalty_program (tsbl_marketing)

- **Description**: Loyalty points and tier tracking.
- **Columns**: `id(UUID PK)`, `user_id(UUID NOT NULL FK->users 1:1)`, `points(INTEGER DEFAULT 0)`, `lifetime_points(INTEGER DEFAULT 0)`, `tier(CITEXT DEFAULT 'bronze')`, `points_expire_at(TIMESTAMPTZ)`, `last_earned_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_loyalty_program_user_id`, `idx_loyalty_program_tier`
- **Unique Constraints**: `uq_loyalty_program_user_id`

### 7.82 taxes (tsbl_system)

- **Description**: Tax rate configuration by jurisdiction.
- **Columns**: `id(UUID PK)`, `name(CITEXT NOT NULL)`, `country_id(UUID FK->countries)`, `state_id(UUID FK->states)`, `rate(DECIMAL(5,4) NOT NULL)`, `type(CITEXT NOT NULL)`, `is_active(BOOLEAN DEFAULT TRUE)`, `applies_to(CITEXT)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_taxes_country_id`, `idx_taxes_active`

### 7.83 invoices (tsbl_payment)

- **Description**: Generated invoice records.
- **Columns**: `id(UUID PK)`, `invoice_number(CITEXT NOT NULL)`, `order_id(UUID FK->orders)`, `user_id(UUID NOT NULL FK->users)`, `type(CITEXT)`, `status(CITEXT)`, `subtotal(DECIMAL(18,2) NOT NULL)`, `tax_amount(DECIMAL(18,2) DEFAULT 0)`, `discount_amount(DECIMAL(18,2) DEFAULT 0)`, `total_amount(DECIMAL(18,2) NOT NULL)`, `currency_id(UUID FK->currencies)`, `due_date(TIMESTAMPTZ)`, `paid_at(TIMESTAMPTZ)`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_invoices_order_id`, `idx_invoices_user_id`, `idx_invoices_invoice_number`
- **Unique Constraints**: `uq_invoices_invoice_number`

### 7.84 invoice_items (tsbl_payment)

- **Description**: Individual line items on invoices.
- **Columns**: `id(UUID PK)`, `invoice_id(UUID NOT NULL FK->invoices)`, `description(TEXT NOT NULL)`, `quantity(INTEGER NOT NULL)`, `unit_price(DECIMAL(18,2) NOT NULL)`, `tax_rate(DECIMAL(5,4) DEFAULT 0)`, `tax_amount(DECIMAL(18,2) DEFAULT 0)`, `total_price(DECIMAL(18,2) NOT NULL)`, `reference_type(CITEXT)`, `reference_id(UUID)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_invoice_items_invoice_id`

### 7.85 shipping (tsbl_order)

- **Description**: Shipping tracking records.
- **Columns**: `id(UUID PK)`, `order_id(UUID FK->orders)`, `order_item_id(UUID FK->order_items)`, `carrier(CITEXT)`, `tracking_number(CITEXT)`, `shipping_method(CITEXT)`, `estimated_delivery(TIMESTAMPTZ)`, `delivered_at(TIMESTAMPTZ)`, `status(CITEXT)`, `shipping_address_id(UUID FK->addresses)`, `weight(DECIMAL(10,2))`, `cost(DECIMAL(18,2))`, `metadata(JSONB)`, plus all base columns.
- **Indexes**: `idx_shipping_order_id`, `idx_shipping_tracking_number`

### 7.86 downloads (tsbl_marketplace)

- **Description**: Digital asset download tracking.
- **Columns**: `id(UUID PK)`, `order_item_id(UUID NOT NULL FK->order_items)`, `product_id(UUID NOT NULL FK->products)`, `buyer_id(UUID NOT NULL FK->users)`, `file_url(TEXT)`, `file_name(TEXT)`, `file_size(INTEGER)`, `ip_address(INET)`, `user_agent(TEXT)`, `downloaded_at(TIMESTAMPTZ DEFAULT NOW())`, `download_count(INTEGER DEFAULT 1)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_downloads_order_item_id`, `idx_downloads_product_id`, `idx_downloads_buyer_id`

### 7.87 security_logs (tsbl_audit) -- PARTITIONED

- **Description**: Security event logs. PARTITIONED BY RANGE(occurred_at) monthly.
- **Columns**: `id(UUID PK)`, `event_type(CITEXT NOT NULL)`, `severity(CITEXT NOT NULL)`, `actor_id(UUID)`, `ip_address(INET)`, `user_agent(TEXT)`, `location_geo(GEOGRAPHY(POINT))`, `description(TEXT)`, `metadata(JSONB)`, `occurred_at(TIMESTAMPTZ NOT NULL)`, plus base columns (without updated_at/version).
- **Partitioning**: `PARTITION BY RANGE (occurred_at)` -- monthly
- **Indexes**: `idx_security_logs_event_type`, `idx_security_logs_severity`, `idx_security_logs_actor_id`, `idx_security_logs_occurred_at`

### 7.88 fraud_detection_logs (tsbl_audit) -- PARTITIONED

- **Description**: Fraud detection alerts. PARTITIONED BY RANGE(occurred_at) monthly.
- **Columns**: `id(UUID PK)`, `rule_name(CITEXT NOT NULL)`, `rule_version(CITEXT)`, `trigger_type(CITEXT NOT NULL)`, `trigger_value(TEXT)`, `risk_score(REAL)`, `user_id(UUID FK->users)`, `order_id(UUID FK->orders)`, `payment_id(UUID FK->payments)`, `action_taken(CITEXT)`, `description(TEXT)`, `metadata(JSONB)`, `occurred_at(TIMESTAMPTZ NOT NULL)`, plus base columns (without updated_at/version).
- **Partitioning**: `PARTITION BY RANGE (occurred_at)` -- monthly
- **Indexes**: `idx_fraud_detection_logs_rule_name`, `idx_fraud_detection_logs_risk_score`, `idx_fraud_detection_logs_user_id`, `idx_fraud_detection_logs_occurred_at`

### 7.89 blacklist (tsbl_system)

- **Description**: Blacklisted users, IPs, devices.
- **Columns**: `id(UUID PK)`, `target_type(CITEXT NOT NULL)`, `target_value(TEXT NOT NULL)`, `reason(TEXT)`, `blacklisted_by(UUID FK->users)`, `blacklisted_at(TIMESTAMPTZ DEFAULT NOW())`, `expires_at(TIMESTAMPTZ)`, `is_active(BOOLEAN DEFAULT TRUE)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_blacklist_target` ON `(target_type, target_value)`

### 7.90 whitelist (tsbl_system)

- **Description**: Whitelisted entities for security exceptions.
- **Columns**: `id(UUID PK)`, `target_type(CITEXT NOT NULL)`, `target_value(TEXT NOT NULL)`, `reason(TEXT)`, `whitelisted_by(UUID FK->users)`, `whitelisted_at(TIMESTAMPTZ DEFAULT NOW())`, `expires_at(TIMESTAMPTZ)`, `is_active(BOOLEAN DEFAULT TRUE)`, `metadata(JSONB)`, plus base columns.
- **Indexes**: `idx_whitelist_target` ON `(target_type, target_value)`



## 8. Index Strategy

### 8.1 B-Tree Indexes

B-Tree is the default and primary index type for all equality and range-based query patterns.

**Index by category:**

| Category | Columns | Rationale |
|---|---|---|
| Foreign Keys | All {table}_id FK columns | JOIN lookups, referential integrity checks |
| Status columns | status on orders, products, payments | Filtered list queries |
| Timestamp columns | created_at, updated_at, deleted_at | Range scans, pagination, sorting |
| Unique columns | email, phone, sku, slug, order_number | Unique constraint enforcement |
| Composite keys | (seller_id, status), (user_id, status), (category_id, status) | Multi-filter list queries |

### 8.2 GIN Indexes

| Column Type | Tables | Operator Classes |
|---|---|---|
| JSONB | All tables with JSONB columns (metadata, ttributes, preferences, data) | jsonb_path_ops for @>, ?, ?|, ?& operators |
| Array | product_tags.tag, meta_keywords, pplicable_products, 	ags | Array containment and overlap operators |
| Full-Text Search | Products (tsvector column) | 	svector search ranking |

Use jsonb_path_ops over default jsonb_ops for smaller index size (approximately 50% smaller) and faster @> lookups.

### 8.3 GiST Indexes

| Column Type | Tables | Use Case |
|---|---|---|
| Geo-location | ddresses (lat/long), login_history (location_geo) | Nearest-neighbour queries, bounding-box searches |
| ltree | categories.path (ltree column for hierarchical paths) | Ancestry/subtree queries |
| tsrange/daterange | coupons validity periods, promotion campaigns | Exclusion constraints, overlap detection |

### 8.4 Partial Indexes

Partial indexes reduce index size and write overhead by indexing only relevant rows.

| Index | Condition | Benefit |
|---|---|---|
| ix_products_active_listing | WHERE status = 'published' AND deleted_at IS NULL | 90% of product queries filter active only |
| ix_notifications_unread | WHERE is_read = FALSE | Unread notification badge queries |
| ix_orders_pending | WHERE status IN ('pending', 'confirmed', 'processing') | Order processing queue queries |
| ix_wishlist_user | WHERE deleted_at IS NULL | Active wishlist lookups |
| ix_coupons_valid | WHERE is_active = TRUE AND expires_at > NOW() | Valid coupon queries |

### 8.5 Covering Indexes (INCLUDE)

Covering indexes enable index-only scans by including payload columns in the leaf pages, eliminating heap lookups.

| Use Case | Index Definition |
|---|---|
| Product listing pages | ON products(category_id, status, created_at DESC) INCLUDE (id, name, base_price, slug, rating_avg) WHERE status = 'published' |
| Order history | ON orders(buyer_id, created_at DESC) INCLUDE (id, order_number, status, total_amount, currency_id) WHERE deleted_at IS NULL |
| Seller dashboard | ON products(seller_id, status) INCLUDE (id, name, base_price, total_sales, created_at) |

### 8.6 Composite Index Strategy

Rules for determining column order in composite B-Tree indexes:

1. **Equality columns first**: Place columns with = conditions leftmost (e.g., user_id, seller_id, status)
2. **Range columns second**: Place columns with range conditions (>, <, BETWEEN) after all equality columns
3. **Sort columns third**: Place ORDER BY columns last if they match the index sort order
4. **Cardinality guide**: Higher-selectivity columns first only when all conditions are equality

**Anti-patterns to avoid:**
- Indexing low-cardinality columns alone (e.g., status alone on a table with 6 statuses -- composite with a high-cardinality column)
- Indexing every column permutation -- monitor actual query patterns via pg_stat_user_indexes
- Redundant leading columns (e.g., (a, b) makes (a) redundant unless (a) is a unique constraint)

### 8.7 Index Maintenance

| Operation | Schedule | Method |
|---|---|---|
| Concurrent index creation | As needed | CREATE INDEX CONCURRENTLY -- allows DML during creation, longer build time |
| REINDEX | Monthly low-traffic window or per-partition rolling | REINDEX INDEX CONCURRENTLY (PG12+) -- non-blocking rebuild |
| VACUUM | Continuous (auto-vacuum) | Auto-vacuum tuned per-table (see Section 15) |
| Bloat monitoring | Daily | Check pg_stat_user_indexes vs pg_index, alert on bloat > 20% |

**Critical rule for concurrent operations:**
- Always use CONCURRENTLY for index creation and reindex in production
- Run during low-traffic periods to minimize contention
- Monitor pg_stat_progress_create_index for progress tracking

### 8.8 Unused Index Detection and Cleanup

**Detection query:**
`sql
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
ORDER BY tablename;
`

**Cleanup workflow:**
1. Identify indexes with zero scans over 7 days
2. Mark candidate indexes as unusable (UPDATE pg_index SET indisvalid = false) -- do not drop immediately
3. Monitor for 2 weeks -- if no application errors, drop the index
4. Drop using DROP INDEX CONCURRENTLY to avoid blocking writes

---

## 9. Partition Strategy

### 9.1 Partitioned Tables

| Table | Partition Key | Partition Interval | Est. Annual Rows |
|---|---|---|---|
| nalytics_events | occurred_at | Monthly (RANGE) | ~200M |
| udit_logs | created_at | Monthly (RANGE) | ~20M |
| security_logs | occurred_at | Monthly (RANGE) | ~15M |
| raud_detection_logs | occurred_at | Monthly (RANGE) | ~10M |
| login_history | created_at | Monthly (RANGE) | ~50M |
| messages | created_at | Monthly (RANGE) | ~100M |

### 9.2 Partition Methods

**RANGE partitioning (primary method):**
`sql
CREATE TABLE tsbl_analytics.analytics_events (
    id           UUID NOT NULL DEFAULT gen_random_uuid(),
    event_name   VARCHAR(128) NOT NULL,
    aggregate_id UUID,
    payload      JSONB,
    occurred_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);
`

### 9.3 Partition Management with pg_partman

`sql
CREATE EXTENSION pg_partman;
SELECT partman.create_parent(
    p_parent_table   := 'tsbl_analytics.analytics_events',
    p_control        := 'occurred_at',
    p_type           := 'native',
    p_interval       := '1 month',
    p_premake        := 3,
    p_start_partition := '2026-07-01'
);
`

**Automated maintenance via pg_cron:**
`sql
SELECT cron.schedule('partman-maintenance', '0 */2 * * *',
    SELECT partman.run_maintenance());
`

### 9.4 Partition Naming Convention

| Convention | Example |
|---|---|
| {parent_table}_{yyyy_mm} | nalytics_events_2026_07, udit_logs_2026_08 |

### 9.5 Partition Pruning Expectations

Query planner prunes partitions based on WHERE clauses on the partition key:
`sql
-- Only scans analytics_events_2026_07 and analytics_events_2026_08
EXPLAIN ANALYZE
SELECT * FROM analytics_events
WHERE occurred_at >= '2026-07-15'
  AND occurred_at < '2026-08-20';
`

**Requirements for effective pruning:**
- WHERE clause must reference the partition key with an immutable expression
- NOW() and CURRENT_TIMESTAMP are stable, not immutable -- use explicit ranges in application queries
- Avoid wrapping partition key in functions (DATE(occurred_at)) -- this disables pruning

### 9.6 Zero-Downtime Partition Management

| Operation | Method | Impact |
|---|---|---|
| Create new partition | CREATE TABLE {child} PARTITION OF {parent} | No lock on parent (PG12+) |
| DROP old partition | DROP TABLE {child} | No lock on parent |
| DETACH partition | ALTER TABLE {parent} DETACH PARTITION {child} CONCURRENTLY (PG14+) | Brief lock, then non-blocking |
| ATTACH partition | ALTER TABLE {parent} ATTACH PARTITION {child} with validation | Validated async, no data movement |

**Retention policy:**
- Time-series partitions older than 12 months: DETACH and archive to S3 cold storage
- After successful archive verification: DROP detached partition
- Minimum 3 months of data always retained online

---

## 10. Archiving Strategy

### 10.1 Archiving Criteria

| Data Category | Retention Online | Archive Trigger | Archive Destination |
|---|---|---|---|
| Application/analytics logs | 90 days | created_at < NOW() - INTERVAL '90 days' | S3 Glacier / Deep Archive |
| Security logs | 6 months | occurred_at < NOW() - INTERVAL '6 months' | S3 Glacier / Deep Archive |
| Audit logs | 24 months | created_at < NOW() - INTERVAL '24 months' | S3 Standard-IA |
| Completed orders | 1 year after delivery | status = 'completed' AND completed_at < NOW() - INTERVAL '1 year' | S3 Standard-IA |
| User accounts (inactive) | 3 years after last login | status = 'inactive' AND last_active_at < NOW() - INTERVAL '3 years' | S3 Glacier Deep Archive |

### 10.2 Archiving Methods

**Method 1: Partition Detach (preferred for partitioned tables)**
`sql
ALTER TABLE tsbl_audit.audit_logs
    DETACH PARTITION audit_logs_2025_07 CONCURRENTLY;
-- Export to Parquet and upload to S3
-- Drop detached table after verification
DROP TABLE IF EXISTS audit_logs_2025_07;
`

**Method 2: Selective Export (for non-partitioned tables)**
`sql
-- Export old completed orders
\COPY (
    SELECT * FROM tsbl_order.orders
    WHERE status = 'completed'
      AND completed_at < NOW() - INTERVAL '1 year'
      AND deleted_at IS NULL
    ORDER BY id
) TO 'orders_archive_2025.csv' WITH (FORMAT CSV, HEADER, COMPRESSION gzip);
`

**Method 3: S3 Cold Storage for Blobs**
- Product images older than 2 years to S3 Glacier Instant Retrieval
- Invoice PDFs after 1 year to S3 Standard-IA
- KYC documents after account closure to S3 Glacier Deep Archive

### 10.3 Archive Storage Format

| Data Type | Format | Rationale |
|---|---|---|
| Analytics / Metrics | Apache Parquet (columnar) | Compressed, columnar, queryable via Athena/Presto |
| Log data | Gzip-compressed NDJSON | Schema-less, append-friendly, stream-parseable |
| Order snapshots | Gzip-compressed CSV | Tabular, portable, easy to restore |
| Binary assets | Raw S3 object | Native S3 lifecycle management |

### 10.4 Archive Verification

| Check | Frequency | Method |
|---|---|---|
| Checksum verification | Per archive job | Compare row hash vs S3 ETag |
| Row count reconciliation | Per archive job | COUNT before delete matches archived row count |
| Random sample restoration | Monthly | Restore 0.1% of archived records, verify values |
| Full restore test | Quarterly | Restore 1 full partition to staging, run integrity queries |

### 10.5 Automated Archiving Pipeline via pg_cron

`sql
-- Daily: Archive logs older than 90 days
SELECT cron.schedule('archive-logs', '0 3 * * *',
    CALL tsbl_analytics.archive_old_events());
-- Weekly: Archive completed orders older than 1 year
SELECT cron.schedule('archive-orders', '0 4 * * 0',
    CALL tsbl_order.archive_completed_orders());
-- Monthly: Detach and archive old partitions
SELECT cron.schedule('archive-partitions', '0 5 1 * *',
    CALL tsbl_audit.archive_old_partitions());
`

---

## 11. Backup Strategy

### 11.1 Backup Schedule

| Type | Frequency | Method | Retention |
|---|---|---|---|
| Full (physical) | Daily (02:00 UTC) | pg_basebackup to S3 | 30 days |
| WAL archiving | Continuous (every 5 min) | rchive_command to S3 | 7 days local, 30 days S3 |
| Logical (weekly) | Sunday 03:00 UTC | pg_dump custom format, compressed | 12 weeks |
| Logical (monthly) | 1st of month 03:00 UTC | pg_dump custom format, compressed | 12 months |
| Logical (yearly) | 1st January 03:00 UTC | pg_dump custom format, encrypted | 7 years |

### 11.2 WAL Archiving Configuration

`ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_timeout = 300
archive_command = 'aws s3 cp %p s3://tsbl-db-backups/prod/wal/%f --storage-class STANDARD_IA'
`

**WAL retention on primary:** wal_keep_size = 1024 (1 GB of WAL segments retained locally for replica catch-up). Replication slots to prevent premature WAL removal.

### 11.3 Point-in-Time Recovery (PITR)

**Recovery configuration:**
`ini
restore_command = 'aws s3 cp s3://tsbl-db-backups/prod/wal/%f %p'
recovery_target_time = '2026-07-15 14:23:00+06'
recovery_target_action = promote
`

**PITR workflow:**
1. Identify target timestamp from application logs or error report
2. Restore the latest daily pg_basebackup to a recovery instance
3. Apply WAL segments from S3 up to the target timestamp
4. Verify data integrity after recovery
5. Promote the recovered instance or open as a new replica

### 11.4 Backup Encryption

| Layer | Method | Key Management |
|---|---|---|
| At rest (S3) | Server-side encryption (SSE-S3 or SSE-KMS) | AWS KMS with automatic key rotation |
| Client-side | AES-256-GCM (gpg symmetric encryption) for logical backups | HashiCorp Vault or AWS Secrets Manager |
| In transit | TLS 1.3 for all S3 uploads | TLS certificates managed via ACM |

### 11.5 Cross-Region Replication

| Environment | Primary Region | Replica Region |
|---|---|---|
| Production | ap-southeast-1 (Singapore) | ap-southeast-3 (Jakarta) |
| Staging | ap-southeast-1 (Singapore) | ap-south-1 (Mumbai) |

S3 bucket policy enforces: MFA delete enabled, Object lock in compliance mode (7-day retention), Versioning enabled.

### 11.6 Automated Backup Verification

| Test | Frequency | Scope |
|---|---|---|
| Checksum verification | Daily | Verify each backup manifest checksum matches S3 object ETags |
| Logical restore | Weekly | Restore weekly pg_dump to staging, run schema validation |
| Physical restore | Monthly | Restore pg_basebackup + WAL to staging, run until consistency |
| Full DR drill | Quarterly | Simulate complete primary failure; restore from S3, verify E2E |
| PITR drill | Quarterly | Random timestamp restore, verify row count matches |

### 11.7 Backup Monitoring and Alerting

| Metric | Threshold | Severity |
|---|---|---|
| Backup age | > 26 hours since last successful backup | CRITICAL |
| WAL archive failure | pg_stat_archiver.failed_count > 0 for > 5 min | CRITICAL |
| Backup size delta | > 20% deviation from 7-day rolling average | WARNING |
| S3 replication lag | > 1 hour (cross-region) | WARNING |

---

## 12. Read Replica Strategy

### 12.1 Architecture

`
                        +-----------------------+
                        |  PostgreSQL Primary   |
                        |  (RW, 64 vCPU/256GB)  |
                        +----------+------------+
                                   |
                      Synchronous Replication (1)
                     Asynchronous Replication (2+)
                                   |
             +--------------------+--------------------+
             |                    |                    |
   +---------v--------+  +------v---------+  +------v---------+
   | Replica 1 (Sync) |  | Replica 2 (Async)|  | Replica 3 (Async)|
   | (Critical reads)  |  | (Analytics)      |  | (Reporting)      |
   +------------------+  +------------------+  +------------------+
             |                    |                    |
             +--------------------+--------------------+
                                  |
                       +----------v-----------+
                       |  PgBouncer (RO pool) |
                       |  port 6432            |
                       +----------------------+
                                  |
                       +----------v-----------+
                       |  PgBouncer (RW pool) |
                       |  port 6433            |
                       +----------------------+

   Application --> SQLAlchemy Router --> PgBouncer(RW | RO) --> PostgreSQL(primary | replica)
`

### 12.2 Replication Method

Streaming replication configured for all replicas:
`ini
# Primary configuration
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1024
max_replication_slots = 10
synchronous_standby_names = 'FIRST 1 (replica1_sync)'
`

| Replica | Type | Mode | Use Case |
|---|---|---|---|
| Replica 1 | Physical | Synchronous | Critical reads (payment/idempotency), failover target |
| Replica 2 | Physical | Asynchronous | Analytics queries, reporting, ETL |
| Replica 3 | Physical | Asynchronous | Heavy search queries, admin panel, data exports |

### 12.3 Read Replica Usage Distribution

| Workload | Target Replica | Read Consistency |
|---|---|---|
| Product listing, search, catalog | Replica 2 or 3 | Eventual (up to 5s lag) |
| User dashboard, order history | Replica 1 | Synchronous (zero lag) |
| Analytics ETL, reporting | Replica 2 | Snapshot isolation |
| Admin panel, data export | Replica 3 | Eventual (up to 5s lag) |
| Payment/order status reads | Primary or Replica 1 | Strong consistency |
| Session validation, auth checks | Primary | Strong consistency |

### 12.4 Load Balancing via SQLAlchemy Read/Write Splitting

| Call Pattern | Route | Reason |
|---|---|---|
| db.session.execute(query) | Reads routed to RO pool | SELECT queries |
| db.session.add(obj), db.session.commit() | Forced to RW pool | Write operations |
| Inside db.session.begin_nested() | RW pool | Savepoints require primary |
| After write in same transaction | RW pool | Read-your-writes consistency |

### 12.5 Replica Lag Monitoring

`sql
SELECT pid, application_name, state, sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
    ROUND(EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))) AS lag_seconds
FROM pg_stat_replication;
`

| Metric | Threshold | Severity | Action |
|---|---|---|---|
| Replication lag | > 5 seconds | WARNING | Investigate replica load or network |
| Replication lag | > 30 seconds | CRITICAL | Remove replica from RO pool, page DBA |
| Replica down | Not reachable | CRITICAL | Failover if sync replica, remove from pool |
| WAL generation rate | > 100 MB/s | WARNING | Archive bottleneck, tune archive_command |

### 12.6 Failover Procedure

**For planned failover (maintenance):**
1. Verify replica lag is < 1 second
2. Stop application writes (maintenance mode)
3. Flush remaining WAL: pg_switch_wal() on primary
4. Wait for replica to apply all WAL (lag = 0)
5. Promote replica: SELECT pg_promote()
6. Update PgBouncer configuration to point at new primary
7. Reconfigure old primary as replica of new primary
8. Resume application traffic

**For unplanned failover (primary failure):**
1. Confirm primary is unreachable (quorum check via Patroni/etcd)
2. Promote the synchronous replica with the highest LSN position
3. Repoint PgBouncer RW pool to promoted replica
4. Stand up new replica from the promoted primary
5. Investigate root cause of primary failure

**Patroni settings:** 	tl: 30, loop_wait: 10, 
etry_timeout: 10, maximum_lag_on_failover: 1048576 (max 1 MB lag).

### 12.7 Connection Routing via PgBouncer

`ini
[databases]
tsbl_rw = host=postgres-primary port=5432 dbname=tsbl
tsbl_ro = host=postgres-replica1 port=5432 dbname=tsbl
          host=postgres-replica2 port=5432 dbname=tsbl
          host=postgres-replica3 port=5432 dbname=tsbl

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432   # RO pool
auth_type = scram-sha-256
pool_mode = transaction
default_pool_size = 50
max_client_conn = 500
`

Two PgBouncer instances: Port 6432 (RO -- all replicas), Port 6433 (RW -- primary only).

---

## 13. Scaling Strategy

### 13.1 Vertical Scaling

| Resource | Primary | Replicas |
|---|---|---|
| vCPU | 32-64 | 16-32 |
| RAM | 128-256 GB | 64-128 GB |
| Storage | 2-4 TB NVMe SSD | 2-4 TB NVMe SSD |
| Network | 25 Gbps | 10-25 Gbps |
| IOPS | 40,000+ (provisioned) | 20,000+ (provisioned) |

**Vertical scaling triggers:** CPU > 70% during peak, memory pressure (OOM), I/O wait > 10%, query queue depth > 10.

### 13.2 Horizontal Scaling

| Scale Tier | Replicas | Read Capacity |
|---|---|---|
| Standard | 2 (1 sync + 1 async) | 2x read throughput |
| High Traffic | 4 (1 sync + 3 async) | 4x read throughput |
| Peak Season | 6 (1 sync + 5 async) | 6x read throughput, deployed 2 weeks ahead |

### 13.3 Connection Pooling via PgBouncer

`ini
[pgbouncer]
pool_mode = transaction
default_pool_size = 200
max_client_conn = 500
reserve_pool_size = 20
reserve_pool_timeout = 5.0
max_db_connections = 200
server_idle_timeout = 300
client_idle_timeout = 600
query_timeout = 30
query_wait_timeout = 60
`

**Pool sizing:** Each application worker (uvicorn/gunicorn): pool_size = 10, max_overflow = 5. With 8 workers: 80 connections steady, 120 peak. PgBouncer pool: 200 connections. PostgreSQL max_connections: 300.

### 13.4 Sharding Readiness

**Sharding key: user_id (UUID)** -- natural distribution, most queries scoped to user.

**Application-level sharding readiness:**
`
tsbl_shard_01 (users 00000000-3fffffff)
tsbl_shard_02 (users 40000000-7fffffff)
tsbl_shard_03 (users 80000000-bfffffff)
tsbl_shard_04 (users c0000000-ffffffff)
`

**Prerequisites before sharding:** All cross-shard queries identified and documented. Data access patterns confirmed to be user-scoped (> 90%). Sharding migration plan (downtime or online via FDW). Monitoring for hot shards.

### 13.5 Caching Layer (Redis)

| Cache | Data | Pattern | TTL | Invalidation |
|---|---|---|---|---|
| Query cache | Product listings, category trees | Cache-aside (lazy load) | 5 minutes | On product update (event-driven) |
| Session store | User sessions | Write-through | 24 hours | On logout or expiry |
| Rate limit counters | API rate limits | Sliding window counter | Variable | Automatic expiry |
| Idempotency cache | Payment idempotency keys | Write-through | 24 hours | On completion |
| Hot data | Top-selling products, featured deals | Write-behind | 1 hour | Periodic refresh |

**Cache-aside pattern:**
1. Application checks Redis for cached result
2. Cache hit to return directly
3. Cache miss to query PostgreSQL
4. Store result in Redis with TTL
5. Return to caller

---

## 14. Security Strategy

### 14.1 Encryption at Rest

| Layer | Method | Scope |
|---|---|---|
| Storage | LUKS full-disk encryption on all database hosts | All data at OS level |
| Column-level | pgcrypto with application-managed keys | PII columns (see 14.3) |
| Backup | AES-256-GCM with envelope encryption | All backup files |

**Key management:** AWS KMS for envelope encryption keys. Application-level encryption keys stored in HashiCorp Vault with automatic rotation every 90 days.

### 14.2 Encryption in Transit

| Connection Route | Protocol | Certificate |
|---|---|---|
| Application to PgBouncer | TLS 1.3 | Client certificate + mutual TLS |
| PgBouncer to PostgreSQL | TLS 1.3 | Internal CA certificate |
| Replication (primary to replica) | TLS 1.3 | Internal CA certificate |
| Admin tools (psql, pgAdmin) | TLS 1.3 | User certificate |

`ini
ssl = on
ssl_min_protocol_version = 'TLSv1.3'
ssl_ciphers = 'HIGH:!aNULL:!eNULL:!MD5'
password_encryption = 'scram-sha-256'
`

### 14.3 Column-Level Encryption

| Table | Encrypted Columns | Encryption Method | Access |
|---|---|---|---|
| users | email, phone | pgcrypto pgp_sym_encrypt() | Only user service has decryption key |
| users | password_hash | bcrypt (application-level, not pgcrypto) | Never decrypted |
| ank_accounts | ccount_number, 
outing_number | pgcrypto pgp_sym_encrypt() | Payment service + admin audit |
| payment_methods | 	oken | Application-level AES-256 | Payment service only |
| license_keys | key | pgcrypto pgp_sym_encrypt() | Product service only |

`sql
-- Encrypt on insert
INSERT INTO tsbl_payment.bank_accounts (account_number, ...)
VALUES (pgp_sym_encrypt('1234567890', current_setting('app.bank_encryption_key')), ...);
-- Decrypt on read (restricted to authorized roles)
SELECT pgp_sym_decrypt(account_number, current_setting('app.bank_encryption_key'))
FROM tsbl_payment.bank_accounts WHERE id = '...';
`

### 14.4 Role-Based Access

| Role | Purpose | Schema Access | DDL | DML |
|---|---|---|---|---|
| 	sbl_app | Application runtime | All 	sbl_* schemas (SELECT, INSERT, UPDATE, DELETE) | No | Yes |
| 	sbl_readonly | Analytics, reporting, admin UI | All 	sbl_* schemas (SELECT only) | No | No |
| 	sbl_migration | Alembic migrations | All schemas full access | Yes | Yes |
| 	sbl_dba | Database administration | Superuser equivalent | Yes | Yes |
| 	sbl_replication | Streaming replication | Replication connection only | No | No |

`sql
CREATE ROLE tsbl_app WITH LOGIN NOBYPASSRLS;
CREATE ROLE tsbl_migration WITH LOGIN BYPASSRLS;
CREATE ROLE tsbl_readonly WITH LOGIN NOBYPASSRLS;
CREATE ROLE tsbl_dba WITH LOGIN SUPERUSER;
CREATE ROLE tsbl_replication WITH LOGIN REPLICATION;
`

### 14.5 Row-Level Security (RLS)

RLS enforces multi-tenant isolation at the database level, ensuring sellers can only access their own data.

`sql
ALTER TABLE tsbl_marketplace.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE tsbl_marketplace.products FORCE ROW LEVEL SECURITY;

CREATE POLICY products_seller_isolation ON tsbl_marketplace.products
    FOR ALL
    USING (seller_id = current_setting('app.current_seller_id')::UUID);
`

**RLS policy matrix:**

| Table | Policy | Enforced Column |
|---|---|---|
| products | Seller sees own products only | seller_id |
| orders | Seller sees orders containing own products | Subquery via order_items.seller_id |
| product_variants | Seller sees own variants | Subquery via products.seller_id |
| 
eviews | Seller sees reviews on own products | Subquery via products.seller_id |

### 14.6 Network Security

| Component | Network Zone | Inbound | Outbound |
|---|---|---|---|
| PostgreSQL primary | Private subnet (10.0.1.0/24) | PgBouncer CIDR only | S3, Replicas |
| PostgreSQL replicas | Private subnet (10.0.2.0/24) | PgBouncer CIDR, primary | S3, Primary |
| PgBouncer | Private subnet (10.0.0.0/24) | Application CIDR only | Database CIDR |

**No public IP addresses** on any database or PgBouncer instance. All traffic via internal load balancers or DNS-based service discovery. Security groups restrict all traffic.

### 14.7 Audit Logging with pgaudit

`ini
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'write,ddl,role'
pgaudit.log_level = 'log'
pgaudit.log_catalog = off
pgaudit.log_parameter = on
pgaudit.log_relation = on
pgaudit.log_statement_once = off
`

**What pgaudit captures:** All DDL statements, all DML writes on audited tables, all role/privilege changes, connection events.

**What pgaudit does NOT capture:** SELECT queries (captured via application-level audit logs instead), application context.

### 14.8 Password Policies

| Policy | Value |
|---|---|
| Password encryption | scram-sha-256 (never md5) |
| Minimum length | 24 characters |
| Rotation interval | 90 days |
| Application connection strings | Stored in HashiCorp Vault, injected at pod startup |

### 14.9 Regular Security Patching

| Activity | Frequency | Method |
|---|---|---|
| Minor version patches | Monthly (or upon CVE) | Rolling restart with Patroni |
| Major version upgrades | Annually | Logical replication via pglogical or pg_upgrade |
| Security extension updates | Monthly | ALTER EXTENSION ... UPDATE |
| SSL certificate rotation | Every 90 days | Automated via cert-manager (Kubernetes) or cron |
| Database user password rotation | Every 90 days | Ansible playbook or Vault rotation |

---

## 15. Performance Optimization Strategy

### 15.1 PostgreSQL Configuration Tuning

`ini
# Memory Configuration
shared_buffers = '4GB'               -- 25% of RAM (16GB baseline; scale: 25% of RAM)
effective_cache_size = '12GB'        -- 75% of RAM
work_mem = '8MB'                     -- Per-operation sort/hash memory (4-8MB typical)
maintenance_work_mem = '512MB'       -- For VACUUM, CREATE INDEX (256MB-1GB)
wal_buffers = '16MB'                 -- WAL write buffer (16-64MB)

# Write-Ahead Log
wal_level = replica
max_wal_size = '4GB'                 -- Max WAL size before checkpoint
min_wal_size = '1GB'
checkpoint_completion_target = 0.9   -- Spread checkpoint over 90% of interval
wal_compression = zstd               -- Compress WAL (PG15+ zstd support)

# Query Planner
random_page_cost = 1.1               -- SSD storage (default 4.0 for HDD)
effective_io_concurrency = 200       -- SSD parallelism
default_statistics_target = 500      -- Increased for better plan estimates

# Parallelism
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_tuple_cost = 0.01
parallel_setup_cost = 100

# Autovacuum (aggressive tuning)
autovacuum_max_workers = 6
autovacuum_naptime = 30s
autovacuum_vacuum_scale_factor = 0.01
autovacuum_vacuum_threshold = 1000
autovacuum_analyze_scale_factor = 0.005
autovacuum_analyze_threshold = 500
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_cost_delay = 5ms
`

### 15.2 Per-Table Autovacuum Overrides

`sql
ALTER TABLE tsbl_order.orders SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_threshold = 5000,
    autovacuum_vacuum_cost_limit = 3000
);

ALTER TABLE tsbl_analytics.analytics_events SET (
    autovacuum_vacuum_scale_factor = 0.005,
    autovacuum_vacuum_threshold = 10000,
    autovacuum_vacuum_cost_limit = 4000
);
`

### 15.3 Query Optimization

**Systematic query performance triage:**
1. **Identify slow queries:** pg_stat_statements -- top queries by 	otal_time / calls, lk_read_time, 	emp_bytes
2. **Capture plans:** Enable uto_explain on replicas for queries > 500ms
3. **Analyze:** Check for sequential scans on tables > 10,000 rows, sort operations spilling to disk, nested loop joins where hash join would be better
4. **Fix:** Index addition, query rewrite, configuration change, or materialized view
5. **Verify:** Re-run EXPLAIN (ANALYZE, BUFFERS) and compare before/after metrics

### 15.4 Vacuum Strategy

| Table Category | Auto-vacuum Tuning | Manual Vacuum |
|---|---|---|
| High-write tables (orders, payments, events) | Aggressive (scale_factor 0.005, cost_limit 3000+) | Nightly during low traffic |
| Moderate-write tables (products, vendors) | Default with slightly increased cost_limit | Weekly |
| Read-mostly tables (categories, brands) | Standard defaults | Monthly |
| Partitioned tables | Per-partition tuning via pg_partman | After partition DETACH |

### 15.5 Table Statistics

`sql
-- Increase statistics target for columns used in JOINs and WHERE clauses
ALTER TABLE tsbl_marketplace.products ALTER COLUMN category_id SET STATISTICS 1000;
ALTER TABLE tsbl_marketplace.products ALTER COLUMN seller_id SET STATISTICS 1000;
ALTER TABLE tsbl_marketplace.products ALTER COLUMN status SET STATISTICS 500;
ALTER TABLE tsbl_order.orders ALTER COLUMN buyer_id SET STATISTICS 1000;
ALTER TABLE tsbl_order.orders ALTER COLUMN status SET STATISTICS 500;
`

### 15.6 Materialized Views

| Materialized View | Refresh Schedule | Use Case |
|---|---|---|
| mv_seller_daily_sales | Every 15 minutes | Seller dashboard (revenue, orders) |
| mv_category_sales_rank | Hourly | Category browsing (bestsellers) |
| mv_admin_platform_metrics | Daily | Admin analytics dashboard |
| mv_search_index_snapshot | Nightly | Product search fallback |
| mv_abandoned_carts | Every 5 minutes | Cart recovery campaign queries |

`sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_seller_daily_sales;
`

### 15.7 JSONB Optimization

| Optimization | Guideline |
|---|---|
| Use jsonb_path_ops GIN index | 50% smaller than default jsonb_ops, faster @> operator |
| Avoid large JSONB documents | Break payloads > 50KB into separate normalized tables |
| Extract frequently-queried fields | Use generated columns for commonly filtered JSONB attributes |
| Expression indexes for specific keys | CREATE INDEX ON products((attributes->>'brand')) |

**Example: generated column for frequently filtered attribute:**
`sql
ALTER TABLE tsbl_marketplace.products ADD COLUMN attr_brand TEXT
    GENERATED ALWAYS AS (metadata->>'brand') STORED;
CREATE INDEX ix_products_attr_brand ON tsbl_marketplace.products(attr_brand)
    WHERE metadata ? 'brand';
`

---

## 16. Migration Strategy

### 16.1 Migration Framework

**Tool:** Alembic (SQLAlchemy migration framework)

**Migration naming convention:** {yyyy_mm_dd}_{seq}_{description}.py

| Migration File | Description |
|---|---|
| 2026_07_01_0001_initial_schema.py | Initial schema creation |
| 2026_07_15_0001_add_product_variants.py | Product variants table |
| 2026_07_20_0001_add_order_indexes.py | Performance indexes for orders |
| 2026_08_01_0001_backfill_product_slugs.py | Data migration for slug population |
| 2026_08_05_0001_seed_categories.py | Seed data for category hierarchy |
| 2026_08_10_0001_rename_billing_fields.py | Rename columns (zero-downtime) |

**Directory structure:**
`
migrations/
  alembic.ini
  env.py
  script.py.mako
  versions/
    2026_07_01_0001_initial_schema.py
    2026_07_15_0001_add_product_variants.py
    ...
`

### 16.2 Migration Types

| Type | Description | Example | Rollback Strategy |
|---|---|---|---|
| **Schema change** | DDL operations on tables, columns, constraints | ALTER TABLE ... ADD COLUMN | Reverse DDL |
| **Data migration** | Transform or backfill existing data | UPDATE products SET slug = ... | Reverse UPDATE or snapshot restore |
| **Seed data** | Insert reference/configuration data | INSERT INTO roles ... | DELETE seed data |
| **Index creation** | Performance index adds | CREATE INDEX CONCURRENTLY | DROP INDEX CONCURRENTLY |
| **Extension management** | Enable/update PostgreSQL extensions | CREATE EXTENSION IF NOT EXISTS ... | DROP EXTENSION |

**Separation of concerns:** Data migrations and schema changes must be in separate migration revisions to allow independent rollback.

### 16.3 Zero-Downtime Migration Patterns

| Operation | Pattern | Steps |
|---|---|---|
| **Add column (nullable)** | Direct ALTER (instant in PG11+) | ALTER TABLE ... ADD COLUMN ... DEFAULT NULL; -- no table rewrite |
| **Add column (NOT NULL)** | Multi-step | 1. Add nullable column 2. Backfill data in batches 3. ALTER TABLE ... ALTER COLUMN ... SET NOT NULL |
| **Drop column** | Deprecate first | 1. Mark column as deprecated (stop writing) 2. Remove reads in next release 3. Drop column in third release |
| **Rename column** | Add + dual-write + backfill + drop | 1. Add new column 2. Application writes to both 3. Backfill old values to new 4. Switch reads to new 5. Drop old |
| **Add index** | CONCURRENTLY | CREATE INDEX CONCURRENTLY IF NOT EXISTS ... -- no write lock |
| **Drop index** | CONCURRENTLY | DROP INDEX CONCURRENTLY IF EXISTS ... -- no write lock |
| **Add FK constraint** | NOT VALID + VALIDATE | 1. ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID (no lock) 2. ALTER TABLE ... VALIDATE CONSTRAINT ... (read lock only) |
| **Add CHECK constraint** | NOT VALID + VALIDATE | Same pattern as FK -- avoids long row-level locks |

**FK validation example:**
`sql
ALTER TABLE tsbl_order.order_items
    ADD CONSTRAINT fk_order_items_product_id
    FOREIGN KEY (product_id) REFERENCES tsbl_marketplace.products(id)
    NOT VALID;

ALTER TABLE tsbl_order.order_items
    VALIDATE CONSTRAINT fk_order_items_product_id;
`

### 16.4 Migration Testing

| Test Type | Stage | Scope |
|---|---|---|
| **Upgrade test** | CI (on PR) | Run lembic upgrade head on fresh database, verify schema |
| **Rollback test** | CI (on PR) | Run lembic upgrade head, then lembic downgrade -1, verify schema reversal |
| **Data integrity test** | CI (on PR) | Insert test data, run migration, verify data preserved after upgrade and downgrade |
| **Performance test** | Staging | Run migration on staging with production-scale data volume, measure duration |
| **Concurrent access test** | Staging | Run migration while simulating read/write workload, verify no locking issues |
| **Smoke test** | Post-deploy | Run query sanity checks after production migration |

### 16.5 Migration Deployment Order

1. **Migration runs BEFORE new application code is deployed**
   - Database must be compatible with both old and new application code
   - Old application code continues running during migration
   - New application code deployment follows after successful migration

2. **Rollback order: reverse of deploy order**
   - Roll back application code first (to previous version)
   - Then roll back database migration

**Deployment script:**
`ash
# Phase 1: Database Migration
alembic upgrade head
# Phase 2: Verify migration
python -c "from app.db import check_schema; check_schema()"
# Phase 3: Deploy new application code
kubectl rollout deployment tsbl-api --image=tsbl/api:
# Phase 4: Post-deploy verification
python -c "from app.db import verify_migration; verify_migration()"
`

### 16.6 Data Migration Guidelines

| Guideline | Detail |
|---|---|
| **Batch processing** | Process data in batches of 1,000-10,000 rows per transaction |
| **Progress logging** | Log batch number, elapsed time, estimated completion at each iteration |
| **Resumable** | Each batch must be idempotent -- use FOR UPDATE SKIP LOCKED or processed-flag column |
| **Timeout protection** | Set statement_timeout per batch, catch and retry on timeout |
| **Rollback safety** | Each batch commits independently -- never wrap entire migration in one transaction |
| **Throttling** | Add pg_sleep(batch_duration * 0.1) between batches to avoid replication lag spikes |

**Resumable batch pattern for large data migrations:**
`python
def migrate_slugs(batch_size=1000, max_batches=None):
    processed = 0
    while True:
        with Session() as session:
            products = (
                session.query(Product)
                .filter(Product.slug.is_(None))
                .limit(batch_size)
                .with_for_update(skip_locked=True)
                .all()
            )
            if not products:
                break
            for product in products:
                product.slug = generate_slug(product.title)
            session.commit()
            processed += len(products)
            logger.info(f"Migrated {processed} products...")
`

---

> **Document Version**: 2.0 | **Last Updated**: 2026-07-01 | **Next Review**: 2026-10-01
>
> **Maintainer**: Principal Database Architect | **Approval**: Chief Technology Officer
