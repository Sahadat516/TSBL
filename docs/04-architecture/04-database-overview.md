# Database Overview — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-DB-004 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Principal Software Architect |
| **Date** | 2026-07-01 |

---

## 1. Entity Relationship Overview (Text-Based)

The TSBL database is organised around nine bounded contexts. The following text-based ER diagram shows the high-level relationships between aggregate roots across contexts.

`
                               ┌─────────────────┐                             ┌───────────────────┐
                               │    Vendor       │                             │    Product        │
  ┌─────────────────┐          │  (vendor)       │                             │  (catalog)       │
  │    User         ├──────────│                 │─────────────────────────────│                  │
  │  (auth)         │          │ PK: id          │   FK: vendor_id             │ PK: id           │
  │                 │          │ FK: owner_id    │                             │ FK: vendor_id    │
  │ PK: id          │          │ status          │                             │ FK: category_id  │
  │ email (unique)  │          │ commission_rate │                             │ FK: brand_id     │
  │ phone (unique)  │          │ balance         │                             │ sku (unique)     │
  │ password_hash   │          │ created_at      │                             │ price            │
  │ status          │          └─────────────────┘                             │ stock            │
  │ created_at      │                                                          │ status           │
  └────────┬────────┘                                                          │ attributes(JSONB)│
           │                                                                   │ delet ed_at      │
           │               ┌──────────────────┐          ┌──────────────────┐  └────────┬──────────┘
           │               │  Cart            │          │  Order           │           │
           ├───────────────│  (cart)          │          │  (order)         │           │
           │               │                  │          │                  │           │
           │               │ PK: id           │          │ PK: id           │           │
           │               │ FK: user_id      │          │ FK: user_id      │  ┌────────▼──────────┐
           │               │ status           │          │ status           │  │  ProductVariant   │
           │               └────────┬─────────┘          │ total            │  │  (catalog)        │
           │                        │                    │ placed_at        │  │                   │
           │               ┌────────▼─────────┐          └────────┬─────────┘  │ PK: id            │
           │               │  CartItem         │                   │           │ FK: product_id    │
           │               │  (cart)           │          ┌────────▼─────────┐ │ sku (unique)      │
           │               │                   │          │  OrderItem       │ │ price             │
           │               │ PK: id            │          │  (order)         │ │ stock             │
           │               │ FK: cart_id       │          │                  │ │ attributes(JSONB) │
           │               │ FK: product_id    │          │ PK: id           │ └───────────────────┘
           │               │ quantity          │          │ FK: order_id     │
           │               │ price_snapshot    │          │ FK: product_id   │
           │               └───────────────────┘          │ quantity         │
           │                                               │ unit_price       │
           │                ┌─────────────────┐            └──────────────────┘
           │                │  Payment        │
           └────────────────│  (payment)      │          ┌──────────────────┐
                            │                 │          │  Shipment        │
                            │ PK: id          │          │  (order)         │
                            │ FK: order_id    │          │                  │
                            │ FK: user_id     │          │ PK: id           │
                            │ amount          │          │ FK: order_id     │
                            │ status          │          │ tracking_code    │
                            │ gateway_txn_id  │          │ carrier          │
                            │ idempotency_key │          │ status           │
                            └─────────────────┘          │ est_delivery     │
                                                          └──────────────────┘
           │
           │                ┌──────────────────┐
           └────────────────│  Notification    │
                            │  (notification)  │
                            │                  │
                            │ PK: id           │
                            │ FK: user_id      │
                            │ type             │
                            │ channel          │
                            │ is_read          │
                            │ created_at       │
                            └──────────────────┘
`

---

## 2. All Major Tables Organised by Bounded Context

### 2.1 Auth Context — Schema \	sbl_auth\

| Table | Description | Key Columns |
|---|---|---|
| \users\ | Registered users (buyers, vendors, admins) | \id\, \email\ (unique), \phone\ (unique), \password_hash\, \ull_name\, \vatar_url\, \email_verified_at\, \phone_verified_at\, \status\, \last_login_at\, \created_at\, \updated_at\ |
| \oles\ | Named roles for RBAC | \id\, \
ame\ (unique), \description\, \is_system\, \created_at\ |
| \permissions\ | Granular permission definitions | \id\, \code\ (unique), \
ame\, \description\, \module\ |
| \ole_permissions\ | M2M: roles to permissions | \ole_id\ (FK), \permission_id\ (FK), \created_at\. PK: (\ole_id\, \permission_id\) |
| \user_roles\ | M2M: users to roles | \user_id\ (FK), \ole_id\ (FK), \ssigned_by\, \ssigned_at\. PK: (\user_id\, \ole_id\) |
| \efresh_tokens\ | Active refresh token hashes | \id\, \user_id\ (FK), \	oken_hash\, \amily\, \expires_at\, \evoked_at\, \created_at\ |
| \email_verification_tokens\ | Email verification OTPs | \id\, \user_id\ (FK), \otp_hash\, \	ype\, \expires_at\, \erified_at\, \created_at\ |
| \oauth_accounts\ | Linked OAuth provider accounts | \id\, \user_id\ (FK), \provider\, \provider_user_id\, \email\, \created_at\ |

### 2.2 Catalog Context — Schema \	sbl_catalog\

| Table | Description | Key Columns |
|---|---|---|
| \categories\ | Hierarchical categories (nested set) | \id\, \parent_id\ (FK self), \
ame\, \slug\ (unique), \description\, \image_url\, \lft\, \gt\, \level\, \sort_order\, \is_active\, \created_at\, \updated_at\ |
| \rands\ | Product brands | \id\, \
ame\ (unique), \slug\ (unique), \logo_url\, \description\, \website_url\, \is_active\, \created_at\, \updated_at\ |
| \products\ | Product listings | \id\, \endor_id\ (FK), \category_id\ (FK), \rand_id\ (FK), \	itle\, \slug\ (unique), \sku\ (unique), \price\, \compare_at_price\, \currency\, \cost_price\, \weight_grams\, \stock\, \stock_reserved\, \status\, \ttributes\ (JSONB), \is_featured\, \verage_rating\, \eview_count\, \deleted_at\, \created_at\, \updated_at\ |
| \product_variants\ | Product SKU variations | \id\, \product_id\ (FK), \sku\ (unique), \price\, \stock\, \image_url\, \ttributes\ (JSONB), \sort_order\, \is_active\, \deleted_at\, \created_at\, \updated_at\ |
| \product_images\ | Product image gallery | \id\, \product_id\ (FK), \ariant_id\ (FK), \url\, \lt_text\, \sort_order\, \is_primary\, \created_at\ |
| \product_tags\ | Product tags | \id\, \product_id\ (FK), \	ag\, \created_at\. Unique: (\product_id\, \	ag\) |
| \eviews\ | Product reviews | \id\, \product_id\ (FK), \user_id\ (FK), \order_id\ (FK), \ating\ (1-5), \	itle\, \ody\, \is_verified_purchase\, \is_approved\, \helpful_count\, \created_at\, \updated_at\ |

### 2.3 Cart Context — Schema \	sbl_cart\

| Table | Description | Key Columns |
|---|---|---|
| \carts\ | Active shopping carts | \id\, \user_id\ (FK, unique), \coupon_id\ (FK), \discount_amount\, \status\, \expires_at\, \created_at\, \updated_at\ |
| \cart_items\ | Items in a cart | \id\, \cart_id\ (FK), \product_id\ (FK), \ariant_id\ (FK), \quantity\, \unit_price\, \created_at\. Unique: (\cart_id\, \product_id\, \ariant_id\) |
| \wishlists\ | User wishlist items | \id\, \user_id\ (FK), \product_id\ (FK), \ariant_id\ (FK), \created_at\. Unique: (\user_id\, \product_id\) |

### 2.4 Order Context — Schema \	sbl_order\

| Table | Description | Key Columns |
|---|---|---|
| \orders\ | Order headers | \id\, \order_number\ (unique), \user_id\ (FK), \status\, \subtotal\, \discount_amount\, \shipping_fee\, \	ax_amount\, \	otal\, \currency\, \coupon_code\, \shipping_address_snapshot\ (JSONB), \illing_address_snapshot\ (JSONB), \placed_at\, \created_at\, \updated_at\ |
| \order_items\ | Order line items | \id\, \order_id\ (FK), \product_id\ (FK), \ariant_id\ (FK), \product_title\, \product_sku\, \quantity\, \unit_price\, \	otal_price\, \created_at\ |
| \order_status_logs\ | Status change audit trail | \id\, \order_id\ (FK), \rom_status\, \	o_status\, \changed_by\ (FK), \eason\, \created_at\ |
| \shipments\ | Order shipment tracking | \id\, \order_id\ (FK), \carrier\, \	racking_code\, \status\, \estimated_delivery_date\, \delivered_at\, \weight_grams\, \shipping_cost\, \created_at\, \updated_at\ |
| \shipment_tracking_events\ | Granular tracking updates | \id\, \shipment_id\ (FK), \status\, \location\, \description\, \	racked_at\, \created_at\ |
| \eturns\ | Product return requests | \id\, \order_id\ (FK), \order_item_id\ (FK), \user_id\ (FK), \eason\, \status\, \efund_amount\, \created_at\, \updated_at\ |
| \invoices\ | Generated invoice records | \id\, \order_id\ (FK), \invoice_number\ (unique), \ile_url\ (S3), \generated_at\, \created_at\ |

### 2.5 Payment Context — Schema \	sbl_payment\

| Table | Description | Key Columns |
|---|---|---|
| \payment_methods\ | Saved user payment methods | \id\, \user_id\ (FK), \	ype\, \provider\, \identifier\ (masked), \is_default\, \expires_at\, \created_at\ |
| \payments\ | Payment attempts | \id\, \order_id\ (FK, unique), \user_id\ (FK), \mount\, \currency\, \status\, \gateway\, \gateway_transaction_id\, \idempotency_key\ (unique), \error_message\, \paid_at\, \created_at\, \updated_at\ |
| \	ransactions\ | Charge/refund records | \id\, \payment_id\ (FK), \	ype\, \mount\, \currency\, \status\, \gateway_transaction_id\, \gateway_response\ (JSONB), \created_at\ |
| \efunds\ | Refund records | \id\, \payment_id\ (FK), \	ransaction_id\ (FK), \mount\, \eason\, \status\, \gateway_refund_id\, \created_at\, \processed_at\ |
| \payment_webhook_logs\ | Incoming gateway webhook payloads | \id\, \gateway\, \event_type\, \aw_payload\ (JSONB), \is_processed\, \processed_at\, \created_at\ |

### 2.6 Vendor Context — Schema \	sbl_vendor\

| Table | Description | Key Columns |
|---|---|---|
| \endors\ | Registered vendor businesses | \id\, \owner_id\ (FK, unique), \usiness_name\, \usiness_email\, \usiness_phone\, \	rade_license_number\ (unique), \	in_number\, \description\, \logo_url\, \commission_rate\, \alance\, \	otal_earned\, \status\, \pproved_by\ (FK), \pproved_at\, \created_at\, \updated_at\ |
| \endor_documents\ | Uploaded verification documents | \id\, \endor_id\ (FK), \	ype\, \ile_url\ (S3), \status\, \ejection_reason\, \erified_by\ (FK), \erified_at\, \created_at\ |
| \endor_addresses\ | Vendor business addresses | \id\, \endor_id\ (FK), \	ype\, \ddress_line1\, \ddress_line2\, \city\, \division\, \postal_code\, \is_default\, \created_at\ |
| \endor_bank_accounts\ | Vendor payout bank accounts | \id\, \endor_id\ (FK), \ank_name\, \ranch_name\, \ccount_holder_name\, \ccount_number\ (encrypted), \outing_number\, \is_default\, \erified_at\, \created_at\ |
| \payouts\ | Vendor payout records | \id\, \endor_id\ (FK), \mount\, \status\, \period_start\, \period_end\, \	ransaction_count\, \commission_deducted\, \gateway_payout_id\, \processed_at\, \created_at\ |
| \commission_rules\ | Override commission rules per category | \id\, \endor_id\ (FK), \category_id\ (FK), \commission_rate\, \is_active\, \created_at\ |

### 2.7 Notification Context — Schema \	sbl_notification\

| Table | Description | Key Columns |
|---|---|---|
| \
otification_templates\ | Reusable notification templates | \id\, \code\ (unique), \channel\, \subject\, \ody\ (Jinja2), \ariables\ (JSONB), \created_at\, \updated_at\ |
| \
otifications\ | Sent notification records | \id\, \user_id\ (FK), \	ype\, \channel\, \	itle\, \ody\, \data\ (JSONB), \eference_type\, \eference_id\, \is_read\, \ead_at\, \sent_at\, \delivery_status\, \created_at\ |
| \user_notification_preferences\ | Per-user notification opt-ins | \id\, \user_id\ (FK, unique), \preferences\ (JSONB), \created_at\, \updated_at\ |

### 2.8 Admin Context — Schema \	sbl_admin\

| Table | Description | Key Columns |
|---|---|---|
| \platform_config\ | Key-value configuration store | \id\, \key\ (unique), \alue\ (JSONB), \description\, \updated_by\ (FK), \updated_at\ |
| \udit_logs\ | Immutable audit trail | \id\, \ctor_id\ (FK), \ction\, \esource_type\, \esource_id\, \old_values\ (JSONB), \
ew_values\ (JSONB), \ip_address\, \user_agent\, \created_at\ |
| \disputes\ | Order dispute records | \id\, \order_id\ (FK), \aised_by\ (FK), \ssigned_to\ (FK), \eason\, \status\, \esolution_notes\, \created_at\, \updated_at\ |
| \dispute_messages\ | Messages within a dispute | \id\, \dispute_id\ (FK), \sender_id\ (FK), \message\, \ttachments\ (JSONB), \created_at\ |
| \maintenance_windows\ | Scheduled maintenance records | \id\, \	itle\, \description\, \start_at\, \end_at\, \status\, \created_at\ |

### 2.9 Analytics Context — Schema \	sbl_analytics\

| Table | Description | Key Columns |
|---|---|---|
| \daily_metrics\ | Aggregated daily platform metrics | \id\, \date\ (unique), \
ew_users\, \ctive_users\, \	otal_orders\, \completed_orders\, \gmv\, \platform_fees\, \
ew_vendors\, \created_at\ |
| \product_metrics\ | Per-product daily metrics | \id\, \product_id\ (FK), \date\, \iews\, \dds_to_cart\, \purchases\, \evenue\, \created_at\. Unique: (\product_id\, \date\) |
| \endor_metrics\ | Per-vendor daily metrics | \id\, \endor_id\ (FK), \date\, \	otal_sales\, \	otal_revenue\, \commission_deducted\, \orders_count\, \created_at\. Unique: (\endor_id\, \date\) |
| \search_logs\ | Anonymised search query logs | \id\, \query\, \esult_count\, \ilters_used\ (JSONB), \user_id\ (hashed), \session_id\, \created_at\ |
| \event_store\ | Raw domain events for analytics | \id\, \event_name\, \ggregate_id\, \ggregate_type\, \payload\ (JSONB), \metadata\ (JSONB), \occurred_at\ |

---

## 3. Table Naming Conventions

| Convention | Rule | Example |
|---|---|---|
| **Schema name** | Lowercase, prefixed with \	sbl_\ + context | \	sbl_auth\, \	sbl_catalog\ |
| **Table name** | Lowercase, plural snake_case | \product_variants\, \order_items\ |
| **Primary key** | Always \id\ (UUID type) | \id UUID PRIMARY KEY DEFAULT gen_random_uuid()\ |
| **Foreign key** | \{referenced_table_singular}_id\ | \user_id\, \product_id\ |
| **Created/Updated** | \created_at\, \updated_at\ (TIMESTAMPTZ) | \created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()\ |
| **Soft delete** | \deleted_at\ (nullable TIMESTAMPTZ) | \deleted_at TIMESTAMPTZ\ |
| **Boolean fields** | \is_\ prefix | \is_active\, \is_default\ |
| **Status fields** | \status\ (VARCHAR) | \status VARCHAR(32) NOT NULL DEFAULT 'pending'\ |
| **Unique constraints** | \uq_{table}_{column}\ | \uq_products_sku\ |
| **Indexes** | \ix_{table}_{column}\ | \ix_orders_user_id\ |

---

## 4. Key Relationships and Foreign Keys

| Parent Table | Child Table | FK Column | Type | Business Rule |
|---|---|---|---|---|
| \users\ | \endors\ | \owner_id\ | 1:1 | A user can own at most one vendor account |
| \users\ | \orders\ | \user_id\ | 1:N | A user can have many orders |
| \users\ | \carts\ | \user_id\ | 1:1 | A user has at most one active cart |
| \users\ | \
otifications\ | \user_id\ | 1:N | A user can have many notifications |
| \endors\ | \products\ | \endor_id\ | 1:N | A vendor can list many products |
| \categories\ | \products\ | \category_id\ | 1:N | A category contains many products |
| \categories\ | \categories\ | \parent_id\ | 1:N (self) | Self-referencing hierarchy (nested set) |
| \products\ | \product_variants\ | \product_id\ | 1:N, CASCADE | A product has many variants |
| \products\ | \eviews\ | \product_id\ | 1:N | A product has many reviews |
| \orders\ | \order_items\ | \order_id\ | 1:N, CASCADE | An order has many items |
| \orders\ | \shipments\ | \order_id\ | 1:N | An order can have multiple shipments |
| \orders\ | \payments\ | \order_id\ | 1:1 | An order has one payment |
| \payments\ | \	ransactions\ | \payment_id\ | 1:N | A payment has many transactions |
| \order_items\ | \eturns\ | \order_item_id\ | 1:1 | An order item can be returned at most once |

---

## 5. Indexing Strategy

### 5.1 B-Tree Indexes (Default)

For equality lookups, range queries, and sort operations.

\\\sql
CREATE INDEX ix_products_vendor_id     ON tsbl_catalog.products(vendor_id);
CREATE INDEX ix_products_category_id   ON tsbl_catalog.products(category_id);
CREATE INDEX ix_products_status        ON tsbl_catalog.products(status);
CREATE INDEX ix_products_created_at    ON tsbl_catalog.products(created_at DESC);
CREATE INDEX ix_orders_user_id         ON tsbl_order.orders(user_id);
CREATE INDEX ix_orders_placed_at       ON tsbl_order.orders(placed_at DESC);
CREATE INDEX ix_orders_status          ON tsbl_order.orders(status);
CREATE INDEX ix_payments_order_id      ON tsbl_payment.payments(order_id);
CREATE INDEX ix_payments_status        ON tsbl_payment.payments(status);
-- Composite indexes
CREATE INDEX ix_products_vendor_status ON tsbl_catalog.products(vendor_id, status);
CREATE INDEX ix_orders_user_status     ON tsbl_order.orders(user_id, status);
\\\

### 5.2 Partial Indexes

For frequently filtered queries on a subset of rows.

\\\sql
CREATE INDEX ix_products_active
    ON tsbl_catalog.products(id, price, average_rating)
    WHERE status = 'approved';

CREATE INDEX ix_notifications_unread
    ON tsbl_notification.notifications(user_id, created_at DESC)
    WHERE NOT is_read;

CREATE INDEX ix_vendors_pending
    ON tsbl_vendor.vendors(created_at)
    WHERE status = 'pending';

CREATE INDEX ix_carts_active
    ON tsbl_cart.carts(user_id)
    WHERE status = 'active';
\\\

### 5.3 GIN Indexes

For JSONB columns and full-text search vectors.

\\\sql
CREATE INDEX ix_products_attributes
    ON tsbl_catalog.products USING GIN (attributes jsonb_path_ops);

CREATE INDEX ix_variants_attributes
    ON tsbl_catalog.product_variants USING GIN (attributes jsonb_path_ops);

CREATE INDEX ix_products_search_vector
    ON tsbl_catalog.products USING GIN (search_vector);

CREATE INDEX ix_notification_preferences
    ON tsbl_notification.user_notification_preferences USING GIN (preferences);
\\\

### 5.4 Covering Indexes (INCLUDE)

For index-only scans on high-throughput queries.

\\\sql
CREATE INDEX ix_products_listing
    ON tsbl_catalog.products(category_id, status, created_at DESC)
    INCLUDE (id, title, price, slug, thumbnail_url, average_rating)
    WHERE status = 'approved';

CREATE INDEX ix_orders_listing
    ON tsbl_order.orders(user_id, placed_at DESC)
    INCLUDE (id, order_number, status, total, currency)
    WHERE status != 'cancelled';
\\\

### 5.5 Unique Indexes

\\\sql
CREATE UNIQUE INDEX uq_users_email      ON tsbl_auth.users(LOWER(email));
CREATE UNIQUE INDEX uq_users_phone      ON tsbl_auth.users(phone);
CREATE UNIQUE INDEX uq_products_sku     ON tsbl_catalog.products(sku) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX uq_variants_sku     ON tsbl_catalog.product_variants(sku) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX uq_carts_user       ON tsbl_cart.carts(user_id) WHERE status = 'active';
CREATE UNIQUE INDEX uq_invoices_number  ON tsbl_order.invoices(invoice_number);
\\\

---

## 6. Partitioning Strategy for Large Tables

### 6.1 Tables Identified for Partitioning

| Table | Est. Annual Growth | Partition Key | Type |
|---|---|---|---|
| \orders\ | ~5M rows | \placed_at\ (monthly) | Range |
| \order_status_logs\ | ~30M rows | \created_at\ (monthly) | Range |
| \payments\ | ~5M rows | \created_at\ (monthly) | Range |
| \	ransactions\ | ~10M rows | \created_at\ (monthly) | Range |
| \udit_logs\ | ~20M rows | \created_at\ (monthly) | Range |
| \search_logs\ | ~100M rows | \created_at\ (daily) | Range |
| \event_store\ | ~200M rows | \occurred_at\ (daily) | Range |
| \product_metrics\ | ~30M rows | \date\ (monthly) | Range |
| \
otifications\ | ~50M rows | \created_at\ (monthly) | Range |

### 6.2 Partitioning Implementation Example

\\\sql
CREATE TABLE tsbl_order.orders (
    id              UUID        NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL,
    order_number    VARCHAR(32) NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'pending',
    subtotal        NUMERIC(12,2) NOT NULL,
    total           NUMERIC(12,2) NOT NULL,
    placed_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, placed_at)
) PARTITION BY RANGE (placed_at);

CREATE TABLE tsbl_order.orders_2026_07
    PARTITION OF tsbl_order.orders
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

CREATE TABLE tsbl_order.orders_2026_08
    PARTITION OF tsbl_order.orders
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
\\\

### 6.3 Partition Management

- **Automated creation**: Celery Beat task creates partitions 3 months in advance.
- **Retention**: Partitions older than 24 months detached and archived to S3 (Parquet format).
- **Query routing**: PostgreSQL automatically routes queries via WHERE clause.

---

## 7. Full-Text Search Setup

### 7.1 PostgreSQL Full-Text (fallback / admin search)

\\\sql
ALTER TABLE tsbl_catalog.products ADD COLUMN search_vector tsvector;

CREATE OR REPLACE FUNCTION tsbl_catalog.products_search_vector_update()
RETURNS trigger AS \$\$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('bengali', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('bengali', COALESCE(NEW.short_description, '')), 'B') ||
        setweight(to_tsvector('bengali', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('simple', COALESCE(NEW.sku, '')), 'A');
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_search_vector
    BEFORE INSERT OR UPDATE ON tsbl_catalog.products
    FOR EACH ROW EXECUTE FUNCTION tsbl_catalog.products_search_vector_update();
\\\

### 7.2 Primary Search (Elasticsearch)

- **Sync**: CDC via domain events. \ProductCreated\ / \ProductUpdated\ triggers indexing.
- **Bulk reindex**: Celery task runs nightly.
- **Language**: Bengali (\n\) and English (\en\) analyzers per field. ICU plugin for Bengali tokenization.
- **Aliases**: Index alias per environment for zero-downtime mapping changes.

---

## 8. JSONB Usage for Flexible Attributes

| Table | JSONB Column | Purpose |
|---|---|---|
| \products\ | \ttributes\ | Dynamic product specifications (connectivity, color, etc.) |
| \product_variants\ | \ttributes\ | Variant-specific attributes (size, material) |
| \orders\ | \shipping_address_snapshot\ | Immutable address snapshot at order time |
| \orders\ | \illing_address_snapshot\ | Immutable billing address snapshot |
| \	ransactions\ | \gateway_response\ | Raw gateway response for audit |
| \payment_webhook_logs\ | \aw_payload\ | Raw webhook payload for debugging/replay |
| \
otification_templates\ | \ariables\ | Template variable definitions |
| \
otifications\ | \data\ | Arbitrary notification payload data |
| \platform_config\ | \alue\ | Flexible configuration values |
| \udit_logs\ | \old_values\, \
ew_values\ | Before/after state snapshots |
| \user_notification_preferences\ | \preferences\ | Per-channel opt-in/opt-out |
| \event_store\ | \payload\, \metadata\ | Domain event data + metadata |

**Indexing**: \jsonb_path_ops\ GIN index for \@>\, \?\, \?|\, \?&\ operators. Expression-based B-tree for frequent key lookups:

\\\sql
CREATE INDEX ix_products_attr_connectivity
    ON tsbl_catalog.products((attributes->>'connectivity'))
    WHERE attributes ? 'connectivity';
\\\

---

## 9. Soft Delete Pattern

### 9.1 Implementation

All primary business entities use soft deletes:

\\\sql
ALTER TABLE tsbl_catalog.products ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE tsbl_catalog.product_variants ADD COLUMN deleted_at TIMESTAMPTZ;
\\\

### 9.2 Query Filtering

- **Application**: All repository \ind()\ methods append \AND deleted_at IS NULL\.
- **Admin**: \with_deleted()\ method returns all records including soft-deleted.
- **Unique constraints**: Partial unique indexes enforce uniqueness only among non-deleted:

\\\sql
CREATE UNIQUE INDEX uq_products_sku ON tsbl_catalog.products(sku) WHERE deleted_at IS NULL;
\\\

### 9.3 Restoration & Purge

- **Restore**: Set \deleted_at = NULL\. Exposed via admin API.
- **Hard purge**: Soft-deleted records older than 90 days are permanently purged by weekly Celery task. Logged in audit trail. Skipped for records referenced by active orders/payments.

---

## 10. Audit Logging

### 10.1 Approach

**Application-level** (not trigger-based):
- Business context captured (semantic meaning like "Order status changed from pending to confirmed")
- No trigger overhead on writes
- Easy to filter and extend
- Works across PostgreSQL, Redis, and external services

### 10.2 Schema

\\\sql
CREATE TABLE tsbl_admin.audit_logs (
    id              UUID        NOT NULL DEFAULT gen_random_uuid(),
    actor_id        UUID        REFERENCES tsbl_auth.users(id),
    action          VARCHAR(64) NOT NULL,
    resource_type   VARCHAR(64) NOT NULL,
    resource_id     VARCHAR(64) NOT NULL,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    user_agent      TEXT,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
\\\

### 10.3 Audit Trigger Points

| Action | Logged In | Data Captured |
|---|---|---|
| User login | AuthService | \ction: "auth.login"\ |
| Role change | RoleService | Before/after roles array |
| Product create/update | ProductService | Full before/after snapshot |
| Order status change | OrderService | Old/new status, changed by |
| Payment status change | PaymentService | Gateway transaction IDs |
| Vendor approval | AdminService | Approval reason |
| User suspension | AdminService | Reason, duration |

### 10.4 Access & Retention

- **API**: \GET /api/v1/admin/audit-logs\ with filters.
- **Retention**: 3 years retained. Archived to cold storage after 1 year.

---

## 11. Migration Strategy with Alembic

### 11.1 Configuration

\\\ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost:5432/tsbl
\\\

### 11.2 Directory Structure

\\\
migrations/
├── alembic.ini
├── env.py                     # Async Alembic environment
├── script.py.mako             # Migration template
└── versions/
    ├── 0001_initial_schema.py
    ├── 0002_add_product_variants.py
    └── ...
\\\

### 11.3 Migration Conventions

| Convention | Rule |
|---|---|
| **Naming** | \{sequence}_{description}.py\ |
| **Down migrations** | Always provided |
| **Data migrations** | Separate from schema in same revision |
| **Large data** | Batch updates with server-side cursors for >100k rows |

### 11.4 Zero-Downtime Migration Patterns

| Migration Type | Strategy |
|---|---|
| Add column (nullable) | \ALTER TABLE ADD COLUMN\ (instant) |
| Add column (NOT NULL) | Add nullable, backfill, then SET NOT NULL |
| Add index | \CREATE INDEX CONCURRENTLY\ |
| Drop index | \DROP INDEX CONCURRENTLY\ |
| Add FK | \NOT VALID\ then \VALIDATE CONSTRAINT\ |
| Rename column | Add new, dual-write, backfill, drop old (multi-deploy) |

---

## 12. Connection Pooling Configuration

### 12.1 PgBouncer

\\\ini
[databases]
tsbl = host=postgres-primary port=5432 dbname=tsbl

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
pool_mode = transaction
max_client_conn = 500
default_pool_size = 50
min_pool_size = 10
reserve_pool_size = 5
server_idle_timeout = 300
client_idle_timeout = 600
query_timeout = 30
\\\

### 12.2 SQLAlchemy Pool

\\\python
DATABASE_URL = "postgresql+asyncpg://user:pass@pgbouncer:6432/tsbl"
POOL_SIZE = 20           # Per uvicorn worker
MAX_OVERFLOW = 10        # Additional connections
POOL_TIMEOUT = 30        # Seconds to wait
POOL_PRE_PING = True
POOL_RECYCLE = 1800      # 30 minutes
\\\

### 12.3 Connection Scaling

| Environment | Workers | Pool/Worker | Max Overflow | PgBouncer Pool | PG Max Conn |
|---|---|---|---|---|---|
| Development | 1 | 5 | 2 | 10 | 50 |
| Staging | 2 | 10 | 5 | 25 | 100 |
| Production | 4-8 | 20 | 10 | 50 | 200 |

---
## 13. Read Replica Strategy

### 13.1 Architecture

```
                    +------------------+
                    |  PostgreSQL      |
                    |  Primary (RW)    |
                    +--------+---------+
                             |
               Streaming Replication (sync)
                             |
                    +------------------+
                    |  PgBouncer (RW)  |--- Write + transactional reads
                    +------------------+
                             |
            +----------------+----------------+
            |                |                 |
   +--------v------+ +------v--------+ +------v--------+
   | Replica 1     | | Replica 2     | | Replica 3     |
   | (Async)       | | (Async)       | | (Async)       |
   +---------------+ +---------------+ +---------------+
            |                |                 |
            +----------------+-----------------+
                             |
                    +------------------+
                    |  PgBouncer (RO)  |--- Read-only queries
                    +------------------+
```

### 13.2 Read/Write Routing

| Route | Pool | Use Case |
|---|---|---|
| Primary (RW) | pgbouncer-rw:6432 | All writes, transactional reads, idempotency checks |
| Replica (RO) | pgbouncer-ro:6432 | Product listings, search, analytics, reporting |

### 13.3 Replication Lag Handling

- **Critical reads** (payment status, order confirmation) route to primary.
- **Tolerable reads** (product search, reviews) use replicas (up to 5s lag tolerance).
- **Monitoring**: pg_stat_replication lag tracked via Prometheus. Alert at >30s lag.

### 13.4 Failover

- **Automatic**: Patroni manages failover. Newest replica promoted.
- **Manual**: Runbook for planned maintenance.
- **Application**: PgBouncer fronted by load balancer. DNS update or HAProxy reconfiguration.

---

## 14. Backup and Point-in-Time Recovery

### 14.1 Backup Schedule

| Backup Type | Frequency | Retention | Method |
|---|---|---|---|
| WAL archiving | Every 60s | 7 days | archive_command to S3 |
| Full (base) | Daily | 30 days | pg_basebackup to S3 |
| Weekly (logical) | Sunday 02:00 | 12 weeks | pg_dump compressed |
| Monthly (logical) | 1st 02:00 | 12 months | pg_dump compressed |

### 14.2 WAL Archiving Configuration

```ini
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://tsbl-db-backups/wal/%f'
archive_timeout = 60
```

### 14.3 Point-in-Time Recovery (PITR)

```
1. Identify target timestamp (e.g., 2026-07-01 14:23:00 BST)
2. Restore latest base backup
3. Configure recovery.conf with restore_command and recovery_target_time
4. Start PostgreSQL in recovery mode
5. Verify recovery completes and promote to primary
```

### 14.4 RPO and RTO Targets

| Metric | Target | Achieved By |
|---|---|---|
| RPO | < 5 minutes | WAL archiving every 60s |
| RTO | < 30 minutes | Automated restore scripts, pre-warmed replica |

### 14.5 Backup Verification

- **Daily**: Automated restore test with checksum verification.
- **Monthly**: Full restore to staging with data integrity checks.
- **Quarterly**: Disaster recovery drill simulating complete primary failure.

### 14.6 Storage

| Environment | Location | Encryption |
|---|---|---|
| Development | Local + MinIO | AES-256 |
| Staging | AWS S3 (single region) | AES-256 + TLS |
| Production | AWS S3 (cross-region) | AES-256 + TLS |

---

## 15. Database Security

| Measure | Implementation |
|---|---|
| **Encryption at rest** | pgcrypto for sensitive columns (bank accounts). Full-disk encryption. |
| **Encryption in transit** | TLS 1.3 between all services and database. Client certificates. |
| **Access control** | Separate DB users: tsbl_app, tsbl_migrator, tsbl_readonly. |
| **RLS** | Row-Level Security for multi-tenant isolation (vendors see own products/orders). |
| **Audit** | log_statement = 'ddl'. All connections logged. |
| **Network** | Private subnet only. Security group restricted to app server CIDR. |

---

## 16. Glossary

| Term | Definition |
|---|---|
| **CDC** | Change Data Capture - capturing changes made to data in a database |
| **GIN** | Generalized Inverted Index - for JSONB, full-text, and arrays |
| **JSONB** | Binary JSON - flexible, indexed JSON storage in PostgreSQL |
| **Nested Set** | Tree model using lft and rgt columns for hierarchical queries |
| **PgBouncer** | Lightweight PostgreSQL connection pooler |
| **PITR** | Point-in-Time Recovery - restoring DB to a specific moment |
| **RLS** | Row-Level Security - per-row access control in PostgreSQL |
| **RPO** | Recovery Point Objective - max acceptable data loss |
| **RTO** | Recovery Time Objective - max acceptable downtime |
| **WAL** | Write-Ahead Log - PostgreSQL transaction log for durability and replication |
| **tsvector** | PostgreSQL data type optimized for full-text search |

---
> **Document Version**: 1.0 | **Last Updated**: 2026-07-01 | **Next Review**: 2026-10-01

