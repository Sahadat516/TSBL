# Enterprise ER Architecture & Data Flow — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-DB-006 |
| **Version** | 2.0 |
| **Status** | Approved |
| **Author** | Principal Database Architect |
| **Date** | 2026-07-02 |

---

## 1. High Level ER Diagram

The following ASCII diagram illustrates the complete entity-relationship landscape of the TSBL Digital Marketplace. All major domain clusters are shown with their interconnections.

```
                                ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
                                │                                                 USERS DOMAIN                                                    │
                                │                                                                                                              │
                                │          ┌───────────────┐         ┌─────────────────┐         ┌──────────────────┐                         │
                        ┌───────┼──────────│  Roles        │◄──M:M──►│  Permissions     │         │  Sessions        │                         │
                        │       │      ┌───│  (role_perms) │         └─────────────────┘         └──────────────────┘                         │
                        │       │      │   └───────┬───────┘                                                                                  │
                        │       │      │           │                                                                                          │
                        │       │      │           │ M:M via user_roles                                                                       │
                        │       │      │           │                                                                                          │
   ┌──────────────────┐ │       │      │           ▼                                                                                          │
   │  Affiliates/      │◄──────┤      │    ┌───────────────┐         ┌──────────────────────┐                                                │
   │  Referrals        │ 1:1   │      └───►│    Users       │──1:M──►│  User_Profiles        │  (1:1 per user)                               │
   └──────────────────┘ │       │           │   (core)      │──1:1──►│  Seller_Profiles       │  (optional, requires KYC)                     │
                        │       │           └───────┬───────┘──1:1──►│  Buyer_Profiles        │  (auto-created for all buyers)                 │
                        │       │                   │               └──────────────────────┘                                                │
   ┌──────────────────┐ │       │                   │                                                                                          │
   │  Loyalty          │◄──────┤                   │ 1:1 (optional)              ┌──────────────────────┐                                    │
   │  Program          │ 1:1   │                   └────────────────────────────►│  KYC_Documents        │  (identity verification)           │
   └──────────────────┘ │       │                                                └──────────────────────┘                                    │
                        │       │                   │ 1:M                                                                                      │
                        │       │                   ├────────────────────────────►┌──────────────────────┐                                    │
                        │       │                   │                             │  Addresses            │  (shipping/billing)                 │
                        │       │                   │                             └──────────────────────┘                                    │
                        │       │                   │ 1:M                                                                                      │
                        │       │                   ├────────────────────────────►┌──────────────────────┐                                    │
                        │       │                   │                             │  Devices              │  (push notification tokens)          │
                        │       │                   │                             └──────────────────────┘                                    │
                        │       │                   │ 1:M                                                                                      │
                        │       │                   ├────────────────────────────►┌──────────────────────┐                                    │
                        │       │                   │                             │  Notifications        │  (in-app/push)                      │
                        │       │                   │                             └──────────────────────┘                                    │
                        │       │                   │ 1:M                                                                                      │
                        │       │                   ├────────────────────────────►┌──────────────────────┐                                    │
                        │       │                   │                             │  Conversations        │────1:M──►┌──────────────┐          │
                        │       │                   │                             └──────────────────────┘         │ Messages    │          │
                        │       │                   │                                                                  └──────────────┘          │
                        │       │                   │ 1:M                                                                                      │
                        │       │                   ├────────────────────────────►┌──────────────────────┐                                    │
                        │       │                   │                             │  Login_History        │  (auth audit trail)                │
                        │       │                   │                             └──────────────────────┘                                    │
                        │       └───────────────────┘                                                                                          │
                        ▼                                                                                                                      │
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                                               SELLER DOMAIN                                                                                │
  │                                                                                                              ┌───────────────────────┐    │
  │  Sellers ──1:M──►┌────────────────────┐   ┌──────────────────┐    ┌────────────────────┐   ┌──────────────┐ │  Variants              │    │
  │                  │  Products           │──►│  Product_Images   │    │  Product_Videos     │   │  Categories  │ │  (1:M)                 │    │
  │                  └─────────┬──────────┘   └──────────────────┘    └────────────────────┘   └──────┬───────┘ │  Inventory              │    │
  │                            │                                                                        │       │  Tags (M:M via junction) │    │
  │                            │  M:1                                                                   │       │  SEO                    │    │
  │                            └────────────────────────────────────────────────────────────────────────┘       │  Attributes             │    │
  │                                                                                                              └───────────────────────┘    │
  │  Sellers ──1:M──►┌────────────────────┐                                                                                                    │
  │                  │  Seller_Earnings    │  (per-transaction commission records)                                                              │
  │                  └────────────────────┘                                                                                                    │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                                               BUYER DOMAIN                                                                                │
  │                                                                                                              ┌───────────────────────┐    │
  │  Buyers ──1:M──►┌────────────────────┐   ┌──────────────────┐   ┌────────────────────┐   ┌──────────────┐ │  Order_Items           │    │
  │                 │  Cart               │   │  Wishlist         │   │  Orders             │──►│  Payments    │ │  (1:M)                 │    │
  │                 └────────────────────┘   └──────────────────┘   └──────────┬─────────┘   └──────┬───────┘ │  Status_History (1:M)  │    │
  │                                                                           │                       │       │  Digital_Deliveries    │    │
  │                                                                           │  1:1                   │       │  License_Keys          │    │
  │                                                                           │                       │       └───────────────────────┘    │
  │                                                                           ▼                       ▼                                      │
  │                                                                   ┌────────────────────┐   ┌────────────────────┐                        │
  │                                                                   │  Escrow_Accounts   │   │  Disputes          │                        │
  │                                                                   └────────────────────┘   └────────────────────┘                        │
  │                                                                                                              ┌───────────────────────┐    │
  │  Buyers ──1:M──►┌────────────────────┐                              ┌────────────────────┐                  │  Reviews               │    │
  │                 │  Refund_Requests    │                              │  Download_Logs      │                  │  Ratings               │    │
  │                 └────────────────────┘                              └────────────────────┘                  └───────────────────────┘    │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                                               ADMIN & SUPPORT DOMAIN                                                                       │
  │                                                                                                                                            │
  │                        ┌────────────────────┐   ┌──────────────────────┐    ┌────────────────────┐    ┌────────────────────┐              │
  │  Admins                │  Support_Tickets    │──►│  Ticket_Messages     │    │  Audit_Logs         │    │  Activity_Logs      │              │
  │  ──1:M──►              └────────────────────┘   └──────────────────────┘    └────────────────────┘    └────────────────────┘              │
  │                                                                                                                                            │
  │                        ┌────────────────────┐   ┌──────────────────────┐    ┌────────────────────┐    ┌────────────────────┐              │
  │                        │  CMS_Pages          │   │  Blog                │    │  FAQ                │    │  Banners            │              │
  │                        └────────────────────┘   └──────────────────────┘    └────────────────────┘    └────────────────────┘              │
  │                                                                                                                                            │
  │                        ┌────────────────────┐   ┌──────────────────────┐                                                                  │
  │                        │  Reports            │   │  Admin_Notes         │                                                                  │
  │                        └────────────────────┘   └──────────────────────┘                                                                  │
  │                                                                                                                                            │
  │                        ┌────────────────────┐   ┌──────────────────────┐    ┌────────────────────┐                                        │
  │                        │  Feature_Flags      │   │  API_Keys            │    │  Security_Logs      │                                        │
  │                        └────────────────────┘   └──────────────────────┘    └────────────────────┘                                        │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                                               EXTERNAL / REFERENCE DATA                                                                     │
  │                                                                                                                                            │
  │  ┌────────────────────┐    ┌────────────────────┐   ┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐             │
  │  │  Countries          │    │  Currencies         │   │  Languages          │    │  Taxes              │    │  Product_Types     │             │
  │  └────────────────────┘    └────────────────────┘   └────────────────────┘    └────────────────────┘    └────────────────────┘             │
  │                                                                                                                                            │
  │  ┌────────────────────┐    ┌────────────────────┐   ┌────────────────────┐    ┌────────────────────┐                                      │
  │  │  Payment_Gateways   │    │  Email_Templates    │   │  SMS_Templates      │    │  Commission_Rules  │                                      │
  │  └────────────────────┘    └────────────────────┘   └────────────────────┘    └────────────────────┘                                      │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
### Relationship Arrow Key

| Symbol | Meaning |
|---|---|
| \---1:1---?\ | One-to-one |
| \---1:M---?\ | One-to-many |
| \---M:M---?\ | Many-to-many (via junction table) |
| \---M:1---?\ | Many-to-one |
| \-----\ | Association |

---

## 2. Core Relationship Diagram

### 2.1 User & Identity Domain

**Users ? Roles (M:M via \user_roles\ junction)**
- A user can have multiple roles (e.g., buyer, seller, admin, moderator).
- A role can be assigned to multiple users.
- Junction table \user_roles\ includes \ssigned_by\, \ssigned_at\, \expires_at\ for time-bound role assignments.
- Role assignment is audited in \udit_logs\.

**Roles ? Permissions (M:M via \ole_permissions\ junction)**
- A role groups multiple granular permissions.
- A permission can belong to multiple roles.
- Junction table \ole_permissions\ allows fine-grained access control with \is_denied\ flag for explicit deny.
- Permissions are defined as string constants (e.g., \order:read\, \product:write\, \dmin:full\).

**Users ? User_Profiles (1:1)**
- Every user has exactly one base profile record.
- Contains shared fields: \display_name\, \vatar_url\, \io\, \preferences\ (JSONB).
- Created atomically with user registration (same transaction).
- \ON DELETE CASCADE\ from users � profile cannot exist without user.

**Users ? Seller_Profiles (1:1, optional)**
- Only users with role \seller\ have a seller profile.
- Contains \store_name\, \store_slug\ (unique), \store_description\, \store_logo\, \store_banner\, \store_tier\, \commission_rate\, \store_status\ (active/suspended/closed).
- FK with \ON DELETE SET NULL\ if user is deleted (store history preserved).
- KYC verification required before store can go active.

**Users ? Buyer_Profiles (1:1, optional)**
- Auto-created for every user on first purchase or explicit buyer registration.
- Contains \preferred_currency_id\, \default_shipping_address_id\, \	otal_orders\, \	otal_spent\, \uyer_tier\.
- FK with \ON DELETE CASCADE\.

**Users ? KYC (1:1, optional)**
- At most one active KYC record per user.
- Contains \document_type\, \document_number\ (encrypted), \document_front_image\, \document_back_image\, \selfie_image\, \erification_status\ (unverified/pending/verified/rejected), \erified_by\, \erified_at\.
- FK with \ON DELETE SET NULL\ � KYC records are retained for compliance even if user is deleted (anonymized).

**Users ? Addresses (1:M)**
- A user can have multiple addresses (shipping, billing).
- One address can be marked as \is_default_shipping\, one as \is_default_billing\.
- Soft-deletable; deleted addresses are hidden from UI but retained for existing orders.
- FK with \ON DELETE RESTRICT\ if address is referenced by any order.

**Users ? Devices (1:M)**
- A user can register multiple devices for push notifications.
- Contains \device_type\ (ios/android/web), \push_token\, \device_name\, \last_seen_at\.
- FK with \ON DELETE CASCADE\ � devices are transient.

**Users ? Sessions (1:M)**
- Multiple concurrent sessions per user (web, mobile, API).
- Contains \	oken_hash\, \ip_address\, \user_agent\, \expires_at\, \is_revoked\.
- FK with \ON DELETE CASCADE\ � sessions are transient and short-lived.

**Users ? Login_History (1:M)**
- Append-only audit of every login attempt (success and failure).
- Contains \ip_address\, \user_agent\, \login_method\ (password/oauth/otp), \is_success\, \ailure_reason\.
- FK with \ON DELETE NO ACTION\ � login history is immutable for security auditing.
- Partitioned monthly; retention 12 months.

### 2.2 Marketplace / Product Domain

**Users ? Products (seller: 1:M)**
- A seller can list multiple products.
- A product belongs to exactly one seller.
- FK with \ON DELETE RESTRICT\ if product has active orders.

**Products ? Categories (M:1)**
- Each product belongs to exactly one category.
- A category can contain multiple products.
- FK with \ON DELETE RESTRICT\ � categories with products cannot be deleted.

**Products ? Product_Types (M:1)**
- Each product has one product type (digital download, license key, service, physical).
- Product type defines delivery behavior, tax rules, commission rules.
- FK with \ON DELETE RESTRICT\.

**Products ? Product_Variants (1:M)**
- A product can have multiple variants (e.g., different license tiers: basic, pro, enterprise).
- Each variant has its own \price\, \sku\, \stock\.
- FK with \ON DELETE CASCADE\ � variants are part of the product.

**Products ? Product_Images (1:M)**
- Multiple images per product, ordered by \sort_order\.
- FK with \ON DELETE CASCADE\ � images are part of the product.

**Products ? Product_Tags (M:M via \product_tags\ junction)**
- Products can have multiple tags; tags can apply to multiple products.
- Used for search filtering, recommendation, and SEO.

**Products ? Reviews (1:M)**
- A product can have many reviews from verified buyers.
- FK with \ON DELETE SET NULL\ (review survives product deletion as anonymous).

### 2.3 Order Domain

**Users ? Orders (buyer: 1:M)**
- A buyer can place many orders.
- FK with \ON DELETE RESTRICT\ � orders are financial records and cannot be deleted.

**Users ? Orders (seller: 1:M)**
- A seller receives many orders (as the seller of products in the order).
- FK with \ON DELETE RESTRICT\.

**Users ? Reviews (author: 1:M)**
- A user can write many reviews.
- FK with \ON DELETE SET NULL\ (review becomes anonymous on user deletion).

**Orders ? Order_Items (1:M)**
- One order contains one or more order items (line items).
- FK with \ON DELETE CASCADE\ � items are part of the order.

**Orders ? Payments (1:1)**
- One order has exactly one payment transaction.
- FK with \ON DELETE RESTRICT\ � payments are immutable financial records.

**Orders ? Escrow_Accounts (1:1)**
- One order has exactly one escrow account.
- FK with \ON DELETE RESTRICT\ � escrow records are immutable.

**Orders ? Disputes (1:M)**
- An order can have zero or more disputes.
- FK with \ON DELETE RESTRICT\.

**Wallets ? Users (1:1)**
- Each user has exactly one wallet.
- FK with \ON DELETE RESTRICT\ � wallets are financial records.

**Wallets ? Wallet_Transactions (1:M)**
- Append-only ledger of all wallet movements.
- FK with \ON DELETE RESTRICT\.

**Escrow ? Escrow_Transactions (1:M)**
- Append-only ledger of all escrow movements.
- FK with \ON DELETE RESTRICT\.

**Conversations ? Messages (1:M)**
- Each conversation contains many messages.
- FK with \ON DELETE CASCADE\ � messages are part of the conversation.

**Conversations ? Users (M:M via \conversation_participants\ junction)**
- A conversation can have multiple participants (buyer + seller for sales chat, or multiple agents for support).
- A user can be in multiple conversations.

**Support_Tickets ? Ticket_Messages (1:M)**
- Each support ticket has many messages in the thread.
- FK with \ON DELETE CASCADE\.

**Affiliate ? Users (1:1)**
- Each affiliate program record links to one user (the affiliate).
- FK with \ON DELETE SET NULL\.

**Referral_System ? Referrer/Referred (1:M)**
- One referrer can refer multiple new users.
- FK with \ON DELETE SET NULL\ on referrer, \ON DELETE CASCADE\ on referred.

---

## 3. Relationship Type Table

| # | Left Entity | Right Entity | Rel Type | Left Card | Right Card | Left Opt | Right Opt | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | \users\ | \user_profiles\ | 1:1 | 1 | 1 | Mandatory | Mandatory | Created simultaneously; CASCADE delete |
| 2 | \users\ | \seller_profiles\ | 1:1 | 1 | 1 | Mandatory | Optional | Only users with seller role |
| 3 | \users\ | \uyer_profiles\ | 1:1 | 1 | 1 | Mandatory | Optional | Auto-created on first purchase |
| 4 | \users\ | \kyc_documents\ | 1:1 | 1 | 1 | Mandatory | Optional | At most one active KYC per user |
| 5 | \users\ | \ddresses\ | 1:M | 1 | N | Mandatory | Optional | Multiple shipping/billing addresses |
| 6 | \users\ | \devices\ | 1:M | 1 | N | Mandatory | Optional | Push notification tokens |
| 7 | \users\ | \sessions\ | 1:M | 1 | N | Mandatory | Mandatory | Concurrent login sessions |
| 8 | \users\ | \login_history\ | 1:M | 1 | N | Mandatory | Mandatory | Append-only auth audit |
| 9 | \users\ | \oles\ | M:M | M | M | Mandatory | Mandatory | Via \user_roles\ junction |
| 10 | \oles\ | \permissions\ | M:M | M | M | Mandatory | Mandatory | Via \ole_permissions\ junction |
| 11 | \users\ | \products\ (seller) | 1:M | 1 | N | Mandatory | Optional | Seller lists products |
| 12 | \users\ | \orders\ (buyer) | 1:M | 1 | N | Mandatory | Optional | Buyer places orders |
| 13 | \users\ | \orders\ (seller) | 1:M | 1 | N | Mandatory | Optional | Seller receives orders |
| 14 | \users\ | \eviews\ (author) | 1:M | 1 | N | Mandatory | Optional | User writes reviews |
| 15 | \users\ | \wallets\ | 1:1 | 1 | 1 | Mandatory | Mandatory | Every user has a wallet |
| 16 | \users\ | \conversations\ | M:M | M | M | Mandatory | Optional | Via participants junction |
| 17 | \users\ | \
otifications\ | 1:M | 1 | N | Mandatory | Optional | In-app and push |
| 18 | \users\ | \support_tickets\ | 1:M | 1 | N | Mandatory | Optional | User opens tickets |
| 19 | \users\ | \ffiliate_program\ | 1:1 | 1 | 1 | Mandatory | Optional | Affiliate enrollment |
| 20 | \users\ | \eferrals\ (referrer) | 1:M | 1 | N | Mandatory | Optional | Referral tracking |
| 21 | \users\ | \eferrals\ (referred) | 1:1 | 1 | 1 | Mandatory | Optional | Referred user link |
| 22 | \products\ | \categories\ | M:1 | N | 1 | Mandatory | Mandatory | Product belongs to category |
| 23 | \products\ | \product_types\ | M:1 | N | 1 | Mandatory | Mandatory | Digital/service/physical |
| 24 | \products\ | \product_variants\ | 1:M | 1 | N | Mandatory | Optional | Variants (e.g., license tiers) |
| 25 | \products\ | \product_images\ | 1:M | 1 | N | Mandatory | Optional | Gallery images |
| 26 | \products\ | \product_videos\ | 1:M | 1 | N | Mandatory | Optional | Product videos |
| 27 | \products\ | \product_inventory\ | 1:1 | 1 | 1 | Mandatory | Optional | Stock tracking |
| 28 | \products\ | \product_seo\ | 1:1 | 1 | 1 | Mandatory | Optional | SEO metadata |
| 29 | \products\ | \product_attributes\ | M:M | M | M | Mandatory | Optional | Via \product_attribute_values\ |
| 30 | \products\ | \	ags\ | M:M | M | M | Mandatory | Optional | Via \product_tags\ junction |
| 31 | \products\ | \eviews\ | 1:M | 1 | N | Mandatory | Optional | Product reviews |
| 32 | \products\ | \atings\ | 1:1 | 1 | 1 | Mandatory | Optional | Aggregated rating |
| 33 | \orders\ | \order_items\ | 1:M | 1 | N | Mandatory | Mandatory | Line items |
| 34 | \orders\ | \order_status_history\ | 1:M | 1 | N | Mandatory | Mandatory | Status change audit |
| 35 | \orders\ | \payments\ | 1:1 | 1 | 1 | Mandatory | Optional | Payment transaction |
| 36 | \orders\ | \escrow_accounts\ | 1:1 | 1 | 1 | Mandatory | Optional | Escrow record |
| 37 | \orders\ | \disputes\ | 1:M | 1 | N | Mandatory | Optional | Dispute records |
| 38 | \orders\ | \invoices\ | 1:1 | 1 | 1 | Mandatory | Optional | Invoice document |
| 39 | \order_items\ | \digital_deliveries\ | 1:M | 1 | N | Mandatory | Optional | Delivery records |
| 40 | \order_items\ | \license_keys\ | 1:M | 1 | N | Mandatory | Optional | License key assignments |
| 41 | \wallets\ | \wallet_transactions\ | 1:M | 1 | N | Mandatory | Mandatory | Immutable ledger |
| 42 | \wallets\ | \withdrawals\ | 1:M | 1 | N | Mandatory | Optional | Withdrawal requests |
| 43 | \escrow_accounts\ | \escrow_transactions\ | 1:M | 1 | N | Mandatory | Mandatory | Immutable ledger |
| 44 | \categories\ | \sub_categories\ | 1:M | 1 | N | Mandatory | Optional | Category hierarchy |
| 45 | \conversations\ | \messages\ | 1:M | 1 | N | Mandatory | Mandatory | Chat messages |
| 46 | \conversations\ | \conversation_participants\ | 1:M | 1 | N | Mandatory | Mandatory | Participant list |
| 47 | \support_tickets\ | \	icket_messages\ | 1:M | 1 | N | Mandatory | Mandatory | Ticket thread |
| 48 | \coupons\ | \products\ | M:M | M | M | Mandatory | Optional | Via \coupon_products\ |
| 49 | \coupons\ | \categories\ | M:M | M | M | Mandatory | Optional | Via \coupon_categories\ |
| 50 | \promotions\ | \products\ | M:M | M | M | Mandatory | Optional | Via \promotion_products\ |
| 51 | \
otifications\ | \users\ | M:M | M | M | Mandatory | Mandatory | Via \
otification_recipients\ |
| 52 | \eports\ | \users\ | M:M | M | M | Mandatory | Optional | Via \eport_subscribers\ |
| 53 | \shopping_cart\ | \coupons\ | M:1 | N | 1 | Mandatory | Optional | Applied coupon |
| 54 | \shopping_cart\ | \products\ | M:1 | N | 1 | Mandatory | Mandatory | Cart product reference |
| 55 | \products\ | \seller_earnings\ | 1:M | 1 | N | Mandatory | Optional | Earnings records |
| 56 | \orders\ | \seller_earnings\ | 1:M | 1 | N | Mandatory | Optional | Per-order earnings |
| 57 | \orders\ | \platform_revenue\ | 1:1 | 1 | 1 | Mandatory | Optional | Platform commission |
| 58 | \payments\ | \efund_requests\ | 1:M | 1 | N | Mandatory | Optional | Refund records |
| 59 | \payments\ | \payment_methods\ | M:1 | N | 1 | Mandatory | Optional | Payment method used |
| 60 | \users\ | \pi_keys\ | 1:M | 1 | N | Mandatory | Optional | API access keys |

---

## 4. Foreign Key Flow

### 4.1 Identity & Auth Domain

**users** (Core User Table)
- **Incoming FKs**: user_profiles.user_id, seller_profiles.user_id, buyer_profiles.user_id, kyc_documents.user_id, addresses.user_id, devices.user_id, sessions.user_id, login_history.user_id, user_roles.user_id, wallets.user_id, products.seller_id, orders.buyer_id, orders.seller_id, reviews.user_id, notifications.user_id, conversation_participants.user_id, support_tickets.user_id, ticket_messages.author_id, affiliate_program.user_id, referrals.referrer_id, referrals.referred_user_id, api_keys.user_id, audit_logs.actor_id
- **Outgoing FKs**: None (root entity)
- **Delete Rule**: RESTRICT (users are financial entities)
- **Update Rule**: CASCADE

**roles** — Incoming: user_roles.role_id, role_permissions.role_id. Outgoing: None. Delete: RESTRICT

**permissions** — Incoming: role_permissions.permission_id. Outgoing: None. Delete: RESTRICT

**user_roles** (Junction) — Outgoing: user_id to users CASCADE, role_id to roles RESTRICT, assigned_by to users SET NULL

**role_permissions** (Junction) — Outgoing: role_id to roles CASCADE, permission_id to permissions CASCADE. Delete: CASCADE both

**user_profiles** — Outgoing: user_id to users CASCADE. Delete: CASCADE

**seller_profiles** — Outgoing: user_id to users SET NULL. Delete: SET NULL (retain seller data for order history)

**buyer_profiles** — Outgoing: user_id to users CASCADE. Delete: CASCADE

**kyc_documents** — Outgoing: user_id to users SET NULL, verified_by to users SET NULL. Delete: SET NULL (compliance retention)

**addresses** — Outgoing: user_id to users CASCADE. Delete: RESTRICT if referenced by orders

**devices** — Outgoing: user_id to users CASCADE. Delete: CASCADE

**sessions** — Outgoing: user_id to users CASCADE. Delete: CASCADE

**login_history** — Outgoing: user_id to users NO ACTION. Delete: NO ACTION (immutable security audit)

### 4.2 Product Domain

**categories** — Incoming: products.category_id, sub_categories.parent_category_id, coupon_categories.category_id. Outgoing: parent_category_id to categories SET NULL (self-referential). Delete: RESTRICT

**sub_categories** — Outgoing: category_id to categories CASCADE, parent_category_id to categories SET NULL. Delete: CASCADE

**product_types** — Incoming: products.product_type_id. Outgoing: None. Delete: RESTRICT

**products** — Incoming: product_variants.product_id, product_images.product_id, product_videos.product_id, product_inventory.product_id, product_seo.product_id, product_tags.product_id, product_attribute_values.product_id, reviews.product_id, ratings.product_id, order_items.product_id, shopping_cart.product_id, wishlist.product_id, coupon_products.product_id, promotion_products.product_id, search_index_metadata.product_id, product_metrics.product_id
- **Outgoing FKs**: seller_id to users RESTRICT, category_id to categories RESTRICT, product_type_id to product_types RESTRICT
- **Delete Rule**: RESTRICT

**product_variants** — Outgoing: product_id to products CASCADE. Delete: CASCADE
**product_images** — Outgoing: product_id to products CASCADE. Delete: CASCADE
**product_videos** — Outgoing: product_id to products CASCADE. Delete: CASCADE
**product_inventory** — Outgoing: product_id to products CASCADE. Delete: CASCADE
**product_seo** — Outgoing: product_id to products CASCADE. Delete: CASCADE
**tags** — Incoming: product_tags.tag_id. Outgoing: None. Delete: RESTRICT
**product_tags** (Junction) — Outgoing: product_id to products CASCADE, tag_id to tags RESTRICT
**reviews** — Outgoing: product_id to products SET NULL, user_id to users SET NULL, buyer_id to users SET NULL, order_id to orders SET NULL. Delete: SET NULL
**ratings** — Outgoing: product_id to products CASCADE. Delete: CASCADE

### 4.3 Order Domain

**orders** — Incoming: order_items.order_id, order_status_history.order_id, payments.order_id, escrow_accounts.order_id, disputes.order_id, invoices.order_id, seller_earnings.order_id, platform_revenue.order_id, reviews.order_id, digital_deliveries.order_id
- **Outgoing FKs**: buyer_id to users RESTRICT, seller_id to users RESTRICT, coupon_id to coupons SET NULL, shipping_address_id to addresses SET NULL, billing_address_id to addresses SET NULL, currency_id to currencies RESTRICT
- **Delete Rule**: RESTRICT

**order_items** — Outgoing: order_id to orders CASCADE, product_id to products RESTRICT, variant_id to product_variants SET NULL
**order_status_history** — Outgoing: order_id to orders CASCADE, changed_by to users SET NULL
**payments** — Outgoing: order_id to orders RESTRICT, buyer_id to users RESTRICT, currency_id to currencies RESTRICT, payment_method_id to payment_methods SET NULL. Delete: RESTRICT
**escrow_accounts** — Outgoing: order_id to orders RESTRICT, buyer_id to users RESTRICT, seller_id to users RESTRICT, released_by to users SET NULL. Delete: RESTRICT
**escrow_transactions** — Outgoing: escrow_account_id to escrow_accounts RESTRICT. Delete: RESTRICT
**disputes** — Outgoing: order_id to orders RESTRICT, opened_by to users RESTRICT, assigned_to to users SET NULL, resolved_by to users SET NULL
**refund_requests** — Outgoing: order_id to orders RESTRICT, payment_id to payments RESTRICT, requested_by to users RESTRICT, approved_by to users SET NULL, processed_by to users SET NULL
**invoices** — Outgoing: order_id to orders RESTRICT, buyer_id to users RESTRICT, seller_id to users RESTRICT
**invoice_items** — Outgoing: invoice_id to invoices CASCADE, order_item_id to order_items SET NULL

### 4.4 Payment & Wallet Domain

**wallets** — Outgoing: user_id to users RESTRICT. Delete: RESTRICT
**wallet_transactions** — Outgoing: wallet_id to wallets RESTRICT. Delete: RESTRICT
**withdrawals** — Outgoing: wallet_id to wallets RESTRICT, user_id to users RESTRICT, bank_account_id to bank_accounts RESTRICT, approved_by to users SET NULL, processed_by to users SET NULL
**bank_accounts** — Outgoing: user_id to users RESTRICT. Delete: RESTRICT
**seller_earnings** — Outgoing: seller_id to users RESTRICT, order_id to orders RESTRICT, product_id to products SET NULL
**platform_revenue** — Outgoing: order_id to orders RESTRICT, seller_id to users RESTRICT. Delete: RESTRICT
**commission_rules** — Outgoing: category_id to categories SET NULL, product_type_id to product_types SET NULL. Delete: RESTRICT
**payment_methods** — Outgoing: user_id to users CASCADE. Delete: CASCADE

### 4.5 Communication Domain

**conversations** — Outgoing: created_by to users SET NULL. Delete: CASCADE on messages
**conversation_participants** (Junction) — Outgoing: conversation_id to conversations CASCADE, user_id to users CASCADE
**messages** — Outgoing: conversation_id to conversations CASCADE, sender_id to users SET NULL
**attachments** — Outgoing: message_id to messages CASCADE
**notifications** — Outgoing: user_id to users CASCADE, created_by to users SET NULL
**notification_recipients** (Junction) — Outgoing: notification_id to notifications CASCADE, user_id to users CASCADE
**email_queue** — Outgoing: user_id to users SET NULL. Delete: SET NULL
**sms_queue** — Outgoing: user_id to users SET NULL. Delete: SET NULL
**push_notifications** — Outgoing: user_id to users CASCADE, device_id to devices SET NULL

### 4.6 Support, Admin, CMS, Audit, Marketing, Reporting

**support_tickets** — Outgoing: user_id to users RESTRICT, assigned_to to users SET NULL, order_id to orders SET NULL
**ticket_messages** — Outgoing: ticket_id to support_tickets CASCADE, author_id to users SET NULL
**cms_pages** — Outgoing: created_by to users SET NULL, updated_by to users SET NULL
**blog_posts** — Outgoing: author_id to users SET NULL, category_id to categories SET NULL
**faq_entries** — Outgoing: created_by to users SET NULL
**banners** — Outgoing: created_by to users SET NULL
**announcements** — Outgoing: created_by to users SET NULL
**audit_logs** — Outgoing: actor_id to users SET NULL (polymorphic resource_id, no FK)
**activity_logs** — Outgoing: user_id to users SET NULL
**security_logs** — Outgoing: user_id to users SET NULL. Delete: NO ACTION
**fraud_detection_logs** — Outgoing: user_id to users SET NULL, order_id to orders SET NULL
**analytics_events** — Outgoing: user_id to users SET NULL
**coupons** — Outgoing: created_by to users SET NULL, seller_id to users SET NULL. Delete: RESTRICT
**promotions** — Outgoing: created_by to users SET NULL. Delete: RESTRICT
**affiliate_program** — Outgoing: user_id to users SET NULL, approved_by to users SET NULL
**referrals** — Outgoing: referrer_id to users SET NULL, referred_user_id to users CASCADE
**loyalty_program** — Outgoing: user_id to users CASCADE. Delete: CASCADE
**reports** — Outgoing: created_by to users SET NULL. Delete: RESTRICT
**report_subscribers** (Junction) — Outgoing: report_id to reports CASCADE, user_id to users CASCADE

## 5. Referential Integrity Rules

### 5.1 Cascade Rules Summary Table (90 rows covering all FK relationships)

| # | Parent Table | Child Table | FK Column | Delete Rule | Update Rule | Rationale |
|---|---|---|---|---|---|---|
| 1 | users | user_profiles | user_id | CASCADE | CASCADE | Profile is part of user |
| 2 | users | buyer_profiles | user_id | CASCADE | CASCADE | Profile is part of user |
| 3 | users | seller_profiles | user_id | SET NULL | CASCADE | Retain seller history |
| 4 | users | kyc_documents | user_id | SET NULL | CASCADE | Compliance retention |
| 5 | users | sessions | user_id | CASCADE | CASCADE | Transient data |
| 6 | users | devices | user_id | CASCADE | CASCADE | Registrations |
| 7 | users | addresses | user_id | RESTRICT | CASCADE | May be in orders |
| 8 | users | login_history | user_id | NO ACTION | CASCADE | Immutable audit |
| 9 | users | wallets | user_id | RESTRICT | CASCADE | Financial record |
| 10 | users | products | seller_id | RESTRICT | CASCADE | Orders exist |
| 11 | users | orders (buyer) | buyer_id | RESTRICT | CASCADE | Financial records |
| 12 | users | orders (seller) | seller_id | RESTRICT | CASCADE | Financial records |
| 13 | users | reviews | user_id | SET NULL | CASCADE | Anonymous review |
| 14 | users | support_tickets | user_id | RESTRICT | CASCADE | Ticket retention |
| 15 | users | notifications | user_id | CASCADE | CASCADE | User notifs |
| 16 | users | conv_participants | user_id | CASCADE | CASCADE | Chat part |
| 17 | users | api_keys | user_id | CASCADE | CASCADE | API access |
| 18 | users | affiliate_program | user_id | SET NULL | CASCADE | History retention |
| 19 | users | referrals (referrer) | referrer_id | SET NULL | CASCADE | History retention |
| 20 | users | referrals (referred) | referred_user_id | CASCADE | CASCADE | Referred data |
| 21 | users | loyalty_program | user_id | CASCADE | CASCADE | Points |
| 22 | users | email_queue | user_id | SET NULL | CASCADE | Queue retention |
| 23 | users | sms_queue | user_id | SET NULL | CASCADE | Queue retention |
| 24 | users | push_notifications | user_id | CASCADE | CASCADE | Push records |
| 25 | users | audit_logs | actor_id | SET NULL | CASCADE | Audit trail |
| 26 | users | activity_logs | user_id | SET NULL | CASCADE | Activity log |
| 27 | users | security_logs | user_id | NO ACTION | CASCADE | Immutable |
| 28 | users | fraud_logs | user_id | SET NULL | CASCADE | Fraud retention |
| 29 | users | bank_accounts | user_id | RESTRICT | CASCADE | Financial |
| 30 | roles | user_roles | role_id | RESTRICT | CASCADE | Prevent orphan |
| 31 | roles | role_permissions | role_id | CASCADE | CASCADE | Map |
| 32 | permissions | role_permissions | permission_id | CASCADE | CASCADE | Map |
| 33 | categories | products | category_id | RESTRICT | CASCADE | Products exist |
| 34 | categories | sub_categories | category_id | CASCADE | CASCADE | Hierarchy |
| 35 | categories | coupon_categories | category_id | CASCADE | CASCADE | Map |
| 36 | categories | commission_rules | category_id | SET NULL | CASCADE | Rules |
| 37 | product_types | products | product_type_id | RESTRICT | CASCADE | Type ref |
| 38 | products | product_variants | product_id | CASCADE | CASCADE | Part of product |
| 39 | products | product_images | product_id | CASCADE | CASCADE | Part of product |
| 40 | products | product_videos | product_id | CASCADE | CASCADE | Part of product |
| 41 | products | product_inventory | product_id | CASCADE | CASCADE | Part of product |
| 42 | products | product_seo | product_id | CASCADE | CASCADE | Part of product |
| 43 | products | product_tags | product_id | CASCADE | CASCADE | Tag map |
| 44 | products | attr_values | product_id | CASCADE | CASCADE | Attr map |
| 45 | products | reviews | product_id | SET NULL | CASCADE | Anonymous |
| 46 | products | ratings | product_id | CASCADE | CASCADE | Aggregate |
| 47 | products | order_items | product_id | RESTRICT | CASCADE | Order ref |
| 48 | products | shopping_cart | product_id | RESTRICT | CASCADE | Cart ref |
| 49 | products | seller_earnings | product_id | SET NULL | CASCADE | Earnings |
| 50 | variants | order_items | variant_id | SET NULL | CASCADE | Item survives |
| 51 | variants | shopping_cart | variant_id | SET NULL | CASCADE | Cart survives |
| 52 | tags | product_tags | tag_id | RESTRICT | CASCADE | Tag ref |
| 53 | orders | order_items | order_id | CASCADE | CASCADE | Part of order |
| 54 | orders | order_status_history | order_id | CASCADE | CASCADE | Part of order |
| 55 | orders | payments | order_id | RESTRICT | CASCADE | Financial |
| 56 | orders | escrow_accounts | order_id | RESTRICT | CASCADE | Financial |
| 57 | orders | disputes | order_id | RESTRICT | CASCADE | Disputes |
| 58 | orders | invoices | order_id | RESTRICT | CASCADE | Invoice |
| 59 | orders | seller_earnings | order_id | RESTRICT | CASCADE | Earnings |
| 60 | orders | platform_revenue | order_id | RESTRICT | CASCADE | Revenue |
| 61 | orders | refund_requests | order_id | RESTRICT | CASCADE | Refund |
| 62 | orders | digital_deliveries | order_id | CASCADE | CASCADE | Delivery |
| 63 | orders | reviews | order_id | SET NULL | CASCADE | Survives |
| 64 | payments | refund_requests | payment_id | RESTRICT | CASCADE | Refund trail |
| 65 | escrow_accounts | escrow_transactions | escrow_account_id | RESTRICT | CASCADE | Ledger |
| 66 | wallets | wallet_transactions | wallet_id | RESTRICT | CASCADE | Ledger |
| 67 | wallets | withdrawals | wallet_id | RESTRICT | CASCADE | Withdrawals |
| 68 | conversations | messages | conversation_id | CASCADE | CASCADE | Msgs part |
| 69 | conversations | participants | conversation_id | CASCADE | CASCADE | Participants |
| 70 | support_tickets | ticket_messages | ticket_id | CASCADE | CASCADE | Ticket msgs |
| 71 | coupons | shopping_cart | coupon_id | SET NULL | CASCADE | Cart survives |
| 72 | coupons | coupon_products | coupon_id | CASCADE | CASCADE | Map |
| 73 | coupons | coupon_categories | coupon_id | CASCADE | CASCADE | Map |
| 74 | promotions | promotion_products | promotion_id | CASCADE | CASCADE | Map |
| 75 | notifications | notif_recipients | notification_id | CASCADE | CASCADE | Map |
| 76 | reports | report_subscribers | report_id | CASCADE | CASCADE | Map |
| 77 | currencies | products | currency_id | RESTRICT | CASCADE | Currency |
| 78 | currencies | orders | currency_id | RESTRICT | CASCADE | Currency |
| 79 | currencies | payments | currency_id | RESTRICT | CASCADE | Currency |
| 80 | currencies | wallets | currency_id | RESTRICT | CASCADE | Currency |
| 81 | countries | addresses | country_id | RESTRICT | CASCADE | Country |
| 82 | payment_methods | payments | payment_method_id | SET NULL | CASCADE | Method |
| 83 | bank_accounts | withdrawals | bank_account_id | RESTRICT | CASCADE | Bank ref |
| 84 | devices | push_notifications | device_id | SET NULL | CASCADE | Push |
| 85 | languages | users | preferred_language_id | SET NULL | CASCADE | Lang pref |

### 5.2 RESTRICT for Financial Records

Wallets, transactions, payments, escrow accounts, withdrawals, seller_earnings, platform_revenue, refund_requests, bank_accounts all use RESTRICT.

### 5.3 CASCADE for Dependent Data

Order_items, product_images, product_variants, messages, ticket_messages, invoice_items, order_status_history, conversation_participants use CASCADE.

### 5.4 SET NULL for Optional Relationships

shopping_cart.coupon_id, order_items.variant_id, reviews.product_id/user_id, seller_profiles.user_id, kyc_documents.user_id, audit_logs.actor_id, order_status_history.changed_by, support_tickets.assigned_to use SET NULL.

### 5.5 Soft Delete Integrity Rules

All tables have deleted_at TIMESTAMPTZ. RESTRICT evaluated against deleted_at IS NULL. Application triggers cascading soft delete. Hard delete prohibited on financial records. Hard delete on transient data.

### 5.6 CHECK Constraints

Wallets: balance >= 0, held_balance >= 0, available_balance >= 0, balance >= held_balance. Products: base_price > 0, sale_price < base_price. Variants: price > 0. Reviews: rating 1-5. Orders: total_amount >= 0. Payments: amount > 0. Escrow: amount > 0. Inventory: quantity >= 0, reserved + sold <= quantity.

### 5.7 NOT NULL vs Nullable FKs

NOT NULL: orders.buyer_id, orders.seller_id, addresses.user_id. Nullable: orders.coupon_id, shipping_address_id, variant_id, reviews.user_id, seller_profiles.user_id, audit_logs.actor_id, disputes.assigned_to, payments.payment_method_id, kyc_documents.verified_by.

---

## 6. Junction Tables

### 6.1 user_roles (Users-Roles)
Columns: id UUID PK, user_id UUID FK users CASCADE, role_id UUID FK roles RESTRICT, assigned_by UUID FK users SET NULL, assigned_at TIMESTAMPTZ, expires_at TIMESTAMPTZ, is_active BOOLEAN, metadata JSONB. Unique: (user_id, role_id). Indexes: idx_user_roles_user_id, idx_user_roles_role_id.

### 6.2 role_permissions (Roles-Permissions)
Columns: id UUID PK, role_id UUID FK roles CASCADE, permission_id UUID FK permissions CASCADE, is_denied BOOLEAN DEFAULT FALSE, conditions JSONB. Unique: (role_id, permission_id).

### 6.3 product_tags (Products-Tags)
Columns: id UUID PK, product_id UUID FK products CASCADE, tag_id UUID FK tags RESTRICT, created_at TIMESTAMPTZ. Unique: (product_id, tag_id). Index: idx_product_tags_tag_id.

### 6.4 conversation_participants (Conversations-Users)
Columns: id UUID PK, conversation_id UUID FK conversations CASCADE, user_id UUID FK users CASCADE, joined_at TIMESTAMPTZ, left_at TIMESTAMPTZ, last_read_at TIMESTAMPTZ, is_muted BOOLEAN, role VARCHAR(20). Unique: (conversation_id, user_id). Read receipts via last_read_at.

### 6.5 product_attribute_values (Products-Attributes)
Columns: id UUID PK, product_id UUID FK products CASCADE, attribute_id UUID FK product_attributes RESTRICT, value TEXT, is_highlight BOOLEAN, sort_order INT. Unique: (product_id, attribute_id).

### 6.6 coupon_products (Coupons-Products)
Columns: id UUID PK, coupon_id UUID FK coupons CASCADE, product_id UUID FK products CASCADE, created_at TIMESTAMPTZ. Unique: (coupon_id, product_id).

### 6.7 coupon_categories (Coupons-Categories)
Columns: id UUID PK, coupon_id UUID FK coupons CASCADE, category_id UUID FK categories CASCADE, created_at TIMESTAMPTZ. Unique: (coupon_id, category_id). Applies recursively.

### 6.8 promotion_products (Promotions-Products)
Columns: id UUID PK, promotion_id UUID FK promotions CASCADE, product_id UUID FK products CASCADE, discount_override DECIMAL(18,2) NULL, created_at TIMESTAMPTZ. Unique: (promotion_id, product_id).

### 6.9 notification_recipients (Notifications-Users)
Columns: id UUID PK, notification_id UUID FK notifications CASCADE, user_id UUID FK users CASCADE, is_read BOOLEAN, read_at TIMESTAMPTZ, is_delivered BOOLEAN. Unique: (notification_id, user_id). Index: (user_id, is_read, created_at).

### 6.10 report_subscribers (Reports-Users)
Columns: id UUID PK, report_id UUID FK reports CASCADE, user_id UUID FK users CASCADE, schedule VARCHAR(20) DEFAULT manual, last_sent_at TIMESTAMPTZ. Unique: (report_id, user_id).

---

## 7. Dependency Graph

Level 0 (Root): countries, currencies, languages, roles, permissions, product_types, feature_flags, payment_gateways, tax_rates, email_templates, sms_templates.

Level 1: users, categories, tags, cms_pages, blog_categories, faq_categories, banners, announcements.

Level 2: user_profiles, seller_profiles, buyer_profiles, kyc_documents, addresses, devices, sessions, login_history, products, sub_categories, product_attributes, coupons, promotions, affiliate_program, loyalty_program, commission_rules, blog_posts, faq_entries, search_index_metadata.

Level 3: product_variants, product_images, product_videos, product_inventory, product_seo, product_tags, product_attribute_values, shopping_cart, wishlist, orders, wallets, reviews, ratings, product_metrics, conversations, support_tickets, api_keys, reports.

Level 4: order_items, order_status_history, digital_deliveries, license_keys, payments, escrow_accounts, wallet_transactions, seller_earnings, platform_revenue, messages, ticket_messages, disputes, refund_requests, email_queue, sms_queue, push_notifications, invoice_items, coupon_products, coupon_categories, promotion_products, notification_recipients.

Level 5: escrow_transactions, payment_webhook_logs, withdrawals, bank_accounts, downloads, analytics_events, audit_logs, activity_logs, security_logs, fraud_detection_logs, admin_notes, attachments, dispute_evidence, report_subscribers, invoice.

Creation Order: Phase 1 (Foundation) -> Phase 2 (Core Identity) -> Phase 3 (Extended Identity) -> Phase 4 (Marketplace) -> Phase 5 (Product Details) -> Phase 6 (Order Pipeline) -> Phase 7 (Payment/Escrow) -> Phase 8 (Delivery) -> Phase 9 (Financial Ledger) -> Phase 10 (Communication) -> Phase 11 (Disputes) -> Phase 12 (Analytics/Audit).

---

## 8. Marketplace Data Flow

This section describes the complete end-to-end data flow from buyer discovery through post-purchase, covering every table interaction, state transition, integrity constraint, and rollback path.

### 8.1 End-to-End Flow Diagram

`
[Buyer]
  → Browses Categories/Products
  → Searches
  → Views Product Details
  → Adds to Cart (shopping_cart)
  → Applies Coupon (coupons)
  → Proceeds to Checkout
  → Order Created (orders — status: pending)
  → Order Items Created (order_items)
  → Payment Initiated (payments)
  → Escrow Account Created (escrow_accounts — held)
  → Payment Confirmed
  → Order Status Updated (order_status_history — confirmed)
  → Seller Notified (notifications)
  → Seller Delivers (digital_deliveries / license_keys)
  → Buyer Downloads (downloads)
  → Buyer Confirms Delivery
  → Escrow Released (escrow_accounts — released)
  → Commission Deducted (platform_revenue)
  → Seller Wallet Credited (seller_earnings → wallets)
  → Buyer Submits Review (reviews)
  → Order Completed (order_status_history — completed)
`

### 8.2 Step-by-Step Data Flow

Each step specifies tables read/written, state transitions, data integrity rules, business rules, and rollback procedures.

**Step 1: Browse**: Tables read: categories, sub_categories, products, product_variants, product_images. No state transitions. Soft-deleted/draft products excluded.

**Step 2: Search**: Tables read: products (via search_vector or Elasticsearch), search_index_metadata, product_tags, product_seo. Only published products. Elasticsearch multi-match fallback to tsvector.

**Step 3: Product Detail**: Tables read: products, product_images, product_videos, product_variants, product_inventory, reviews, ratings, seller_profiles, product_seo, product_tags. View count increment non-transactional. Reviews filtered to approved status.

**Step 4: Add to Cart**: Tables read: products, variants, inventory. Tables written: shopping_cart (INSERT/UPDATE). State: new row or quantity increment. Unique constraint on (user_id, product_id, variant_id). Guest cart via session_id. 30-day expiry.

**Step 5: Apply Coupon**: Tables read: coupons, cart. Tables written: cart (SET coupon_id). Validation: is_active, date range, usage_limit, min_amount, per_user_limit. Re-validated at checkout.

**Step 6: Checkout**: Tables read: cart, products, addresses, coupons. Inventory reservation atomic: UPDATE product_inventory SET reserved_quantity = reserved_quantity + qty WHERE id = :id AND quantity - reserved_quantity - sold_quantity >= qty.

**Step 7: Order Created**: Tables written: orders (status=pending), order_status_history. order_number unique generated. Monetary totals validated: subtotal + tax - discount = total. Buyer cannot order own product.

**Step 8: Order Items**: Tables written: order_items per line item. product_name, unit_price are snapshots (immutable). delivery_status=pending. Inventory reserved.

**Step 9: Payment Initiated**: Tables written: payments (status=pending). amount matches order total. idempotency_key prevents duplicate processing. 1:1 order-payment.

**Step 10: Escrow Created**: Tables written: escrow_accounts (status=held), escrow_transactions (type=hold). wallets.held_balance increased. Mandatory for all marketplace transactions.

**Step 11: Payment Confirmed**: payments UPDATE (status=completed, paid_at=NOW). Invoice generated. gateway_transaction_id unique. net_amount = amount - fee.

**Step 12: Order Status Updated**: orders UPDATE (status=confirmed, payment_status=paid). order_status_history INSERT. Seller notified.

**Step 13: Seller Notified**: notifications, email_queue, push_notifications written. Failed delivery retried (3 attempts). Respects notification_preferences.

**Step 14: Seller Delivers**: digital_deliveries INSERT. license_keys UPDATE (is_sold=TRUE). order_items.delivery_status=delivered. Must deliver within delivery_time window.

**Step 15: Buyer Downloads**: downloads INSERT logging ip_address, user_agent. max_downloads enforced. Signed URLs expire after 1 hour.

**Step 16: Buyer Confirms**: order_items.delivery_status=confirmed_by_buyer. Auto-confirm after 3 days timer. Escrow release triggered when ALL items confirmed.

**Step 17: Escrow Released**: escrow_accounts status=released, released_at=NOW. escrow_transactions type=release. wallets.held_balance decreased. Commission calculated BEFORE seller credit.

**Step 18: Commission Deducted**: commission_rules evaluated (priority order, seller_tier/category/product_type matching). platform_revenue INSERT. seller_earnings INSERT with net_amount.

**Step 19: Seller Credited**: wallets.balance += net_amount. wallet_transactions type=escrow_release. balance_before/after recorded. Funds available immediately.

**Step 20: Review**: reviews INSERT (status=pending_approval). is_verified_purchase auto-set. rating 1-5 CHECK. One review per product per order.

**Step 21: Order Complete**: orders status=completed, completed_at=NOW. Loyalty points, referral commissions, affiliate rewards processed.

### 8.3 Order Status State Machine

`
pending → confirmed → processing → delivered → completed
   |           |              |              |
   |           |              |              |
   +→ cancelled              +→ disputed →+→ refunded
         (any state)              (delivered)  |
                                              +→ resolved → completed
`

Valid transitions: pending→confirmed (payment+escrow), pending→cancelled (payment failed), confirmed→cancelled (admin only), confirmed→processing (seller), processing→delivered, delivered→completed (buyer confirm or auto-confirm), delivered→disputed (buyer opens dispute), disputed→resolved (moderator), disputed→refunded (moderator).

### 8.4 Idempotency and Concurrency

Duplicate payment webhook: idempotency_key unique constraint prevents double-processing. Concurrent cart: optimistic locking (version column). Inventory overselling prevention: atomic UPDATE with WHERE quantity - reserved - sold >= qty. Escrow release race: version COLUMN + WHERE status=held. License key double-sell: atomic UPDATE is_sold WHERE is_sold=FALSE.

### 8.5 Recovery and Reconciliation

Payment gateway timeout: retry with idempotency + reconciliation job (5min cron). Escrow creation failure after payment: compensating transaction (void payment). Seller no-delivery: auto-confirm timer + dispute. Lost webhook: reconciliation job queries gateway. Stuck orders: monitoring alert on non-terminal >24h.

---

## 9. Wallet Flow

### 9.1 Wallet Table Architecture

Tables: wallets (per-user balance/held_balance/available_balance), wallet_transactions (immutable ledger), withdrawals, seller_earnings, platform_revenue, commission_rules, bank_accounts.

Balance model: balance = held_balance + available_balance. Constraints: balance >= 0, held_balance >= 0, available_balance >= 0, balance >= held_balance.

### 9.2 Deposit Flow

1. Wallet transaction INSERT (type=deposit, status=pending). 2. Payment record INSERT (status=pending, idempotency_key). 3. User redirect to gateway. 4. Gateway callback/webhook. 5. Payment UPDATE (status=completed). 6. Wallet transaction UPDATE (status=completed). 7. Wallet UPDATE (balance += X, available_balance += X). 8. Wallet transaction records balance_before/balance_after. 9. Notification INSERT. 10. Email queue INSERT.

Integrity: deposit requires authenticated user. balance_before + amount = balance_after. Gateway must confirm before credit. Duplicate webhooks rejected via idempotency_key. Amount within platform limits.

### 9.3 Withdrawal Flow

1. Withdrawals INSERT (status=pending). 2. Verify available_balance >= amount + fee. 3. Wallet hold: available_balance -= amount, held_balance += amount. 4. Finance review (or auto). 5. Approved/rejected. If rejected: reverse hold. 6. Processing. 7. Gateway response. 8. Completed. 9. Wallet: held_balance -= amount, balance -= amount. 10. Wallet transaction INSERT.

Validation: min/max amount, KYC complete, bank account verified, max 1 withdrawal per 24h, fraud check above threshold.

### 9.4 Commission Flow

1. Evaluate commission_rules (priority order, seller_tier+category+product_type matching). 2. Calculate commission = total_amount × rate (capped at max_fee, floored at min_fee). 3. Platform_revenue INSERT. 4. Seller_earnings INSERT (net = amount - commission). 5. Wallet transactions recorded.

Highest-priority matching rule applied. Default rate from seller_profiles if no rule matches. net + platform_revenue + fees = order.total.

### 9.5 Refund Flow

1. Refund_requests INSERT (status=pending). 2. Review (auto if below threshold). 3. Approved, processing. 4. Gateway API called (void/refund). 5. Gateway confirms. 6. Payments.refunded_amount updated. 7. Escrow refunded (if held) OR seller wallet debited (if released). 8. Buyer wallet credited. 9. Order status=refunded.

Scenarios: refund before delivery (escrow held → refund to buyer, seller not affected), after release (seller debited net_amount), partial (pro-rated), chargeback (seller debited + fee).

### 9.6 Escrow Lock/Release

Payment captured → escrow held (buyer held_balance += amount) → seller delivers → buyer confirms → escrow released → commission deducted → seller credited (balance += net_amount) → buyer held_balance released.

---

## 10. Payment Flow

### 10.1 Payment Gateway Flow

1. Payments INSERT (status=pending, gateway=selected, amount=order.total, idempotency_key=UUID).
2. Redirect to gateway or process saved method.
3. Gateway processes (async, 3D Secure if required).
4. Gateway sends webhook POST /api/v1/payments/webhook/{gateway}.
5. Webhook received: validate signature (HMAC-SHA256).
6. Payments UPDATE (status=processing, gateway_transaction_id set).
7. Gateway confirms (second webhook or redirect callback).
8. Payments UPDATE (status=completed, paid_at=NOW, fee, net_amount).
9. Escrow_accounts INSERT (status=held, held_since=NOW).
10. Orders UPDATE (payment_status=paid, status=confirmed).
11. Invoice generated (invoices + invoice_items INSERT).
12. Notifications sent.

### Payment Status State Machine

pending → processing → completed → refunded (or partially_refunded). pending → failed. processing → failed.

### Webhook Processing Pipeline

Receive → Validate signature (HMAC-SHA256, IP whitelist, payload integrity) → Deduplicate via idempotency_key → Find matching payment → BEGIN transaction: update payment status, create escrow if completed, order status update, generate invoice → COMMIT → Send notifications.

### Webhook Event Mapping

charge.completed/payment.success → completed (fund captured, escrow). charge.pending → processing. charge.failed → failed (order released). charge.refunded → refunded. charge.dispute.created → dispute flag.

### Webhook Security

Signature verification (HMAC-SHA256), IP whitelist, payload integrity check, webhook secret monthly rotation, rate limiting (10/min per gateway). Raw payload stored in payment_webhook_logs for replay. Reconciliation cron hourly.

### Refund Eligibility

Order exists, status is completed/delivered/confirmed (not cancelled/disputed unless resolved), payment completed, refund_amount <= amount - refunded_amount, within 30 days of completion, not already fully refunded.

---

## 11. Escrow Flow

### 11.1 Complete Escrow Lifecycle

**Step 1 — Buyer Pays**: escrow_accounts INSERT (status=held, amount=order.total, held_since=NOW, buyer_id, seller_id, order_id). escrow_transactions INSERT (type=hold, amount=order.total, status=completed).

**Step 2 — Escrow Locked**: buyer_wallet.held_balance += order.total_amount. buyer_wallet.available_balance -= order.total_amount. Seller has NO access.

**Step 3 — Seller Delivers**: digital_deliveries INSERT (delivery_status=delivered). order_items.delivery_status=delivered.

**Step 4 — Buyer Accepts**: Manual confirm OR auto-confirm after 3 days. order_items.delivery_status = confirmed_by_buyer or auto_confirmed. ALL items must confirm before release.

**Step 5 — Release Funds**: escrow_accounts UPDATE (status=released, released_at=NOW, released_by=buyer_UUID). escrow_transactions INSERT (type=release). buyer_wallet.held_balance -= amount.

**Step 6 — Commission**: Evaluate commission_rules (priority match). Calculate commission. platform_revenue INSERT. seller_earnings INSERT (net = amount - commission).

**Step 7 — Seller Credited**: seller_wallet.balance += net_amount. seller_wallet.available_balance += net_amount. wallet_transactions INSERT (type=escrow_release). platform wallet transaction for commission.

**Step 8 — Notifications**: To seller (payment received for order X), to buyer (order X completed).

### 11.2 Tables

escrow_accounts (primary), escrow_transactions (immutable ledger), wallets (buyer held, seller balance), wallet_transactions (audit), orders (reference), order_items (delivery status), order_status_history (audit), digital_deliveries (delivery), commission_rules (calculation), seller_earnings, platform_revenue, notifications.

### 11.3 State Transitions

escrow_accounts.status: held → released/refunded/partially_refunded. digital_deliveries.delivery_status: pending → delivered → confirmed_by_buyer/auto_confirmed/disputed. seller_earnings.status: pending → available → withdrawn/reversed.

### 11.4 Business Rules

Escrow mandatory for all transactions. One escrow per order (unique). Held amount = order total. No partial release for digital products. Only buyer (or system auto-confirm) triggers release. Seller cannot self-release. No release during dispute. All items must be confirmed. Commission deducted before credit. Negative commission prohibited.

### 11.5 Error Handling

Escrow creation fail after payment: compensating transaction (void/cancel payment at gateway). Wallet.held_balance update fail: retry with version check (3 retries → manual). Commission rule evaluation fail: apply default safe rate (5%). Seller credit fail: preserve earnings with pending status, alert finance. Buyer never confirms: auto-confirm timer fires. Escrow held >30d: escalation to finance.

### 11.6 Timeouts

Seller delivery deadline: 24h (configurable). Delivery grace period: 3 days. Buyer confirmation window: 3 days. Dispute resolution: 7 days. Escrow max hold: 30 days. Post-completion refund window: 30 days.

### 11.7 Dispute Resolution

Option A — In favor of buyer: escrow refunded, buyer credited, seller gets nothing, commission waived. Option B — In favor of seller: escrow released normally, commission deducted. Option C — Split: partial refund/release.

### 11.8 Accounting Ledger

Entry 1 — Hold: Buyer Available Balance → Escrow Liability (order.total). Entry 2 — Release: Escrow Liability → Platform Revenue (commission). Entry 3 — Release: Escrow Liability → Seller Available Balance (net_amount). Sum of held escrows = sum of buyer held_balances across all buyers. Released escrows = 0 liability.

---

## 12. Chat Relationship

### 12.1 Table Architecture

conversations: id UUID PK, type VARCHAR(30) (buyer_seller/support/internal), subject VARCHAR(255), order_id UUID FK orders SET NULL, product_id UUID FK products SET NULL, created_by UUID FK users SET NULL, status VARCHAR(20) DEFAULT active, is_read_only BOOLEAN, metadata JSONB, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ, deleted_at TIMESTAMPTZ.

messages: id UUID PK, conversation_id UUID NOT NULL FK conversations CASCADE, sender_id UUID FK users SET NULL, type VARCHAR(20) (text/image/file/system), body TEXT NOT NULL, metadata JSONB, is_edited BOOLEAN, edited_at TIMESTAMPTZ, reply_to_id UUID FK messages SET NULL, sender_ip INET, created_at TIMESTAMPTZ, deleted_at TIMESTAMPTZ, deleted_by UUID FK users SET NULL, delete_type VARCHAR(10) (self/everyone).

attachments: id UUID PK, message_id UUID NOT NULL FK messages CASCADE, file_name VARCHAR(255), file_size INT, mime_type VARCHAR(100), file_path TEXT, file_url TEXT, thumbnail_url TEXT, metadata JSONB, created_at TIMESTAMPTZ.

### 12.2 Key Rules

Auto-conversation created on order. Read receipts via last_read_at. Unread count = messages after last_read_at by others. Soft delete: self (hide) or everyone (body set to deleted). System messages auto-generated. Editing allowed within 30 min. Typing indicators via WebSocket (not persisted). Max 25MB per file.

### 12.3 Indexes

idx_messages_conversation_id (conversation_id, created_at) WHERE deleted_at IS NULL. idx_messages_sender_id (sender_id, created_at). idx_conv_type_status (type, status, updated_at).

---

## 13. Notification Relationship

### 13.1 Four Channels

In-App (notifications table), Email Queue (email_queue), SMS Queue (sms_queue), Push Notifications (push_notifications).

Trigger Matrix: Order confirmed (in-app+email+push), delivery (in-app+email+push), payment received (in-app+email+sms+push), payment failed (in-app+email+push), escrow released (in-app+email+push), wallet deposit (in-app+email+sms+push), withdrawal (in-app+email+sms), dispute opened/resolved (in-app+email+push), refund (in-app+email+sms+push), KYC verified/rejected (in-app+email), new order seller (in-app+email+sms+push), security events (in-app+email+sms+push).

### 13.2 Templates

Stored in email_templates, sms_templates. Jinja2 syntax. Multi-language via translations JSONB.

### 13.3 Rate Limits

In-App: 100/day. Email: 50/day, 5/hr. SMS: 10/day, 2/hr. Push: 200/day, 10/hr.

### 13.4 Schema

notifications: id UUID PK, user_id UUID FK users CASCADE, type VARCHAR(50), title VARCHAR(255), body TEXT, data JSONB, reference_type VARCHAR(30), reference_id UUID, priority VARCHAR(10), is_read BOOLEAN, read_at TIMESTAMPTZ, created_at TIMESTAMPTZ, deleted_at TIMESTAMPTZ. Index: (user_id, is_read, created_at DESC).

email_queue: id UUID PK, user_id UUID FK users SET NULL, to_email CITEXT, template_name VARCHAR(100), context JSONB, subject VARCHAR(255), body_html TEXT, body_text TEXT, status VARCHAR(20), attempts SMALLINT, max_attempts SMALLINT DEFAULT 3, sent_at TIMESTAMPTZ, created_at TIMESTAMPTZ. Index: (status, created_at).

sms_queue: id UUID PK, user_id UUID FK users SET NULL, to_phone VARCHAR(20), message TEXT, status VARCHAR(20), attempts SMALLINT, delivery_report JSONB, created_at TIMESTAMPTZ.

push_notifications: id UUID PK, user_id UUID FK users CASCADE, device_id UUID FK devices SET NULL, title VARCHAR(255), body TEXT, data JSONB, status VARCHAR(20), sent_at TIMESTAMPTZ, clicked_at TIMESTAMPTZ, created_at TIMESTAMPTZ.

---

## 14. Audit Flow

### L1 - Application Audit (audit_logs)
Records CRUD on critical entities. Columns: id UUID PK, actor_id UUID FK users SET NULL, actor_ip INET, action VARCHAR(30) (CREATE/READ/UPDATE/DELETE), resource_type VARCHAR(50), resource_id UUID, changes JSONB (before/after), severity VARCHAR(10), outcome VARCHAR(10), created_at TIMESTAMPTZ. Partitioned monthly. Retention: 24 months online, 7 years archived.

### L2 - Auth Audit (login_history)
Every login attempt. Columns: id UUID PK, user_id UUID FK users NO ACTION, email CITEXT, ip_address INET, login_method VARCHAR(20), is_success BOOLEAN, failure_reason VARCHAR(100), geo_location JSONB, created_at TIMESTAMPTZ. Partitioned monthly. Retention: 12 months.

### L3 - Security Audit (security_logs)
Suspicious events. Columns: id UUID PK, user_id UUID FK users SET NULL, event_type VARCHAR(50), severity VARCHAR(10), ip_address INET, request_path TEXT, action_taken VARCHAR(50), created_at TIMESTAMPTZ. Partitioned monthly. Retention: 12 months.

### L4 - Fraud Detection (fraud_detection_logs)
Rule/ML-based detection. Columns: id UUID PK, user_id UUID FK users SET NULL, order_id UUID FK orders SET NULL, rule_name VARCHAR(100), risk_score DECIMAL(5,2), action VARCHAR(30), resolution VARCHAR(30), created_at TIMESTAMPTZ. Partitioned monthly. Retention: 24 months.

### L5 - Activity Logs (activity_logs)
User-facing activity stream. Columns: id UUID PK, user_id UUID FK users SET NULL, activity_type VARCHAR(50), description TEXT, reference_type VARCHAR(30), reference_id UUID, metadata JSONB, is_public BOOLEAN, created_at TIMESTAMPTZ. Retention: 6 months.

### Data Flow
Event -> Event Bus -> Audit Service -> Classify (L1-L5) -> Enrich (geo IP, user agent) -> Persist -> Alert if severity=critical or risk_score>90.

---

## 15. Soft Delete Strategy

Every table includes deleted_at TIMESTAMPTZ NULL. All queries filter WHERE deleted_at IS NULL. Views encapsulate filtering.

Partial indexes on all tables: CREATE INDEX idx_{table}_active ON {table} (id) WHERE deleted_at IS NULL.

Cascade on soft delete: users -> products soft-deleted, orders NOT deleted (financial), reviews anonymized. Products -> images/variants soft-deleted, reviews SET NULL.

Hard delete exceptions: sessions, login_history partitions (DROP), email_queue (30d), sms_queue (30d), push_notifications (7d), analytics_events (partition DROP).

Recovery: POST /api/v1/admin/restore/{type}/{id}. Sets deleted_at=NULL. Audit log entry created. Parent restored first.

30-day grace: 0-30d admin recovery, 30-90d support ticket, 90d+ cold archive.

Unique constraints with soft delete: CREATE UNIQUE INDEX uq_users_email_active ON users (email) WHERE deleted_at IS NULL. Same for username, phone, store_slug, sku, order_number, coupon_code.

---

## 16. Versioning Strategy

### Optimistic Locking
version INTEGER DEFAULT 1 on wallets, orders, products, variants, inventory, cart, escrow, earnings, profiles, kyc, withdrawals, coupons.

### History Tables
order_status_history for orders, product_versions (JSONB snapshot) for products, payment_webhook_logs for payments.

### Event Sourcing (Financial)
wallet_transactions, escrow_transactions: immutable append-only ledgers with balance_before/after CHECK constraints.

### CMS Snapshot Versioning
cms_page_versions stores full snapshot per update. Admin publishes specific version_id.

### Compliance
GDPR: anonymize PII, keep anonymous records. Financial retention: 7 years. Audit immutability via NO ACTION delete rule.

---

## 17. Index Strategy

### Primary Index
UUID PK B-Tree on all tables.

### Unique Indexes
email, username, phone (active), store_slug, sku, order_number, coupon_code, slug (categories/blog), gateway_transaction_id, idempotency_key, payments.order_id, escrow_accounts.order_id, inventory.product_id.

### Composite Indexes
(seller_id, status, created_at DESC), (buyer_id, created_at DESC), (seller_id, created_at DESC), (status, created_at), (wallet_id, created_at DESC), (user_id, is_read, created_at DESC), (conversation_id, created_at ASC), (product_id, status, created_at DESC), (resource_type, resource_id, created_at DESC), (buyer_id, created_at DESC).

### GIN Indexes
JSONB: audit_logs.changes, products.metadata, user_profiles.preferences, orders.metadata. TEXT[]: products.features.

### Full-Text Search
Generated tsvector on products (name+description), blog (title+content), FAQ (question+answer). GIN indexes. Elasticsearch primary, tsvector fallback.

### Partial Indexes
WHERE deleted_at IS NULL (all active records), WHERE is_read=FALSE (unread notifs), WHERE status IN ('active','pending') (processing queues).

---

## 18. Partition Strategy

### Range Partitions (Monthly)
analytics_events, audit_logs, login_history, messages, security_logs, fraud_detection_logs. Managed by pg_partman.

### Retention
analytics_events: 6mo. login_history: 12mo. security_logs: 12mo. fraud_detection_logs: 24mo. audit_logs: 24mo. messages: 6mo.

### Hash Partitions (Optional)
sessions by user_id if >100M records.

### List Partitions
orders by status (active vs historical). products by status (published vs draft).

---

## 19. Query Optimization Strategy

### Covering Indexes
Product listing INCLUDE (name, base_price, sale_price, image_url). Order history INCLUDE (order_number, total_amount, status). Notifications INCLUDE (title, body, type).

### Materialized Views
Seller dashboard: total_orders, total_earnings, avg_rating. Refresh 5min via pg_cron. Product stats: total_sales, avg_rating, revenue. Admin overview: daily active users, new sellers, total revenue, dispute count.

### Query Rewriting
EXISTS vs COUNT, JOIN vs subqueries, UNION ALL vs UNION, LATERAL JOIN for top-N per group.

### Connection Pooling
PgBouncer transaction pooling. 200 conn primary, 100 per replica.

### Statistics Target
SET STATISTICS 1000 on join/where columns.

### Slow Query Detection
pg_stat_statements + auto_explain (>100ms). pg_cron alerts on regressing queries.

---

## 20. Database Security

### Transport
TLS 1.3 required. SSL certificates for app connections.

### At-Rest
LUKS full-disk encryption. AES-256 encrypted backups.

### Column-Level Encryption (pgcrypto)
email, phone, document_number, account_number, routing_number, holder_name, gateway_customer_id, license_keys encrypted.

### Data Masking
Email: ***@***. Phone: *******1234. Bank: last 4 digits. Admin-only full visibility.

### Secrets Management
HashiCorp Vault. Auto-rotate every 90 days.

### RBAC Roles
tsbl_app_user (CRUD, no DDL), tsbl_readonly (SELECT only), tsbl_admin (full DDL/DML), tsbl_migration (schema owner). REVOKE ALL from PUBLIC.

### Network
Private subnet. No public IP. Security group from app tier only.

### Timeouts
app_user: 30s. readonly: 60s. admin: 300s.

### pgaudit
DDL all schemas. DML on financial tables. PII access logging. SIEM integration.

---

## 21. Scaling Strategy

### Read Replicas
1 primary + 2-3 async replicas. Reports/analytics on replicas. Real-time reads on primary.

### HA (Patroni/etcd)
Auto-failover <30s. Scheduled switchover zero-downtime.

### Sharding Readiness
user_id shard key. All user tables include user_id. CitusDB compatible.

### Connection Pooling
PgBouncer 200 primary, 100 replica. SQLAlchemy pool_size=10, max_overflow=20.

### Redis Cache
Cache-aside: products 300s, categories 600s, profiles 3600s TTL. Rate limiting counters. WebSocket pub/sub.

---

## 22. Disaster Recovery

### Backup
pg_basebackup daily + WAL archiving 5min. AES-256 encrypted. S3 cross-region replication. Retention: daily 30d, weekly 12w, monthly 12m, yearly 7y.

### PITR
RPO < 5min. RTO < 30min.

### Scenarios
1. Primary crash: Patroni promotes replica <30s.
2. Corruption: PITR to pre-corruption point. Extract affected rows. RTO 1-2h.
3. Region failure: Cross-region replica promotion. RTO <1h, RPO <15min.
4. Accidental deletion: Restore backup, export deleted rows. RTO 2-4h.
5. Ransomware: Shut down. Restore clean backup. PITR to pre-attack. RTO 4-8h.

### Testing
Quarterly automated restore test. Verify integrity. Run test suite. Report.

---

## 23. Naming Standards

Tables: snake_case plural. Columns: snake_case singular. PK: id UUID gen_random_uuid(). FK: {singular_table}_id. Indexes: idx_{table}_{cols}. Unique: uq_{table}_{cols}. Checks: chk_{table}_{desc}. Schemas: tsbl_{domain}.

tsbl_user: users, profiles, roles, permissions, kyc, addresses, devices, sessions, login_history, api_keys.
tsbl_marketplace: products, categories, variants, images, videos, inventory, seo, tags, reviews, ratings, coupons, promotions, wishlist, affiliate, referrals, loyalty.
tsbl_order: orders, order_items, status_history, cart, digital_deliveries, license_keys, downloads.
tsbl_payment: wallets, transactions, payments, methods, webhook_logs, escrow, escrow_tx, withdrawals, bank_accounts, earnings, revenue, commission_rules, refunds, invoices, invoice_items.
tsbl_communication: conversations, participants, messages, attachments, notifications, recipients, email_queue, sms_queue, push_notifications, templates.
tsbl_support: support_tickets, ticket_messages, ticket_attachments, disputes, evidence.
tsbl_cms: cms_pages, versions, blog, categories, faq, faq_categories, banners, announcements.
tsbl_analytics: analytics_events, search_logs, product_metrics.
tsbl_reporting: reports, report_subscribers.
tsbl_admin: audit_logs, activity_logs, security_logs, fraud_logs, admin_notes, feature_flags.

---

## 24. Best Practices

### Configuration
shared_buffers: 25% RAM. effective_cache_size: 75% RAM. work_mem: 4-8MB (16-32MB for reports). maintenance_work_mem: 512MB. wal_buffers: 64MB. random_page_cost: 1.1 (SSD). effective_io_concurrency: 200. checkpoint_completion_target: 0.9.

### Autovacuum
vacuum_scale_factor: 0.01 (aggressive). High-churn tables: 0.005. Disable on append-only ledgers.

### Data Types
UUID PK. TIMESTAMPTZ. CITEXT (email, username). DECIMAL(18,2) for money. JSONB for metadata. TEXT for content. INET for IP. SMALLINT for small counters.

### Monitoring
pg_stat_activity (active queries, blocked). pg_stat_statements (slow queries). pg_stat_replication (lag). Grafana dashboards: cache hit >99%, replication lag <10s, dead tuples <20%.

### Zero-Downtime Migration
CREATE INDEX CONCURRENTLY. ADD CONSTRAINT NOT VALID then VALIDATE. Dual-write pattern for column changes. pt-online-schema-change for large tables. Shadow table for ALTER TYPE.

### Connection Management
PgBouncer + SQLAlchemy pool_size=10, max_overflow=20, pool_recycle=3600. Health check every 30s.

---

**Document Version**: 2.0 | **Last Updated**: 2026-07-02 | **Next Review**: 2026-10-02
