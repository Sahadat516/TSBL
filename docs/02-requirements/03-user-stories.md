# TRUE STAR BD LIMITED — Digital Marketplace User Stories

---

**Document Version:** 1.0  
**Date:** 2026-07-01  
**Author:** Principal Software Architect  
**Status:** Draft for Review  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Epic-Level Stories by Module](#2-epic-level-stories-by-module)
3. [User Roles & Personas](#3-user-roles--personas)
4. [Detailed User Stories](#4-detailed-user-stories)
5. [Story Backlog Summary](#5-story-backlog-summary)

---

## 1. Introduction

### 1.1 Purpose

This document defines the complete set of user stories for the TRUE STAR BD LIMITED (TSBL) digital marketplace platform. These stories follow the standard Connextra template and include acceptance criteria, story point estimates, and priority classifications. The document serves as the single source of truth for functional requirements and is intended for product owners, developers, QA engineers, and stakeholders.

### 1.2 Estimation Scale

| Points | Effort | Complexity | Duration (Ideal Days) |
|--------|--------|------------|----------------------|
| 1      | Trivial | Single field/logic change | < 0.5 |
| 2      | Small | Few components, low risk | 0.5–1 |
| 3      | Medium | Multiple components | 1–2 |
| 5      | Large | Cross-module coordination | 2–4 |
| 8      | Extra Large | Multiple systems, high risk | 4–8 |
| 13     | Epic | Major feature, org-wide impact | 8+ |

### 1.3 Priority Definitions

| Priority | Label | Description |
|----------|-------|-------------|
| P1 | Must-have | Release-critical; platform cannot launch without it |
| P2 | Should-have | Important but can launch with workaround |
| P3 | Could-have | Desirable; included if capacity permits |
| P4 | Won't-have | Explicitly deferred to a future release |

---

## 2. Epic-Level Stories by Module

The TSBL platform is organized into **26 modules**. Each module has a single epic-level story that captures its high-level objective.

| # | Module ID | Module Name | Epic Story | Priority |
|---|-----------|-------------|------------|----------|
| 1 | MOD-REG | User Registration & Authentication | As a user, I want to register, log in, and manage my identity securely so that I can access platform features based on my role. | P1 |
| 2 | MOD-PRO | User Profile Management | As a user, I want to create and maintain my profile so that the community knows who I am and I can build trust. | P1 |
| 3 | MOD-LIS | Product Listing & Catalog | As a seller, I want to list products with rich media and attributes so that buyers can discover and evaluate my offers. | P1 |
| 4 | MOD-SRC | Search & Discovery | As a buyer, I want to search, filter, and browse products efficiently so that I can find exactly what I need. | P1 |
| 5 | MOD-CRT | Cart & Wishlist | As a buyer, I want to manage a shopping cart and wishlist so that I can save items for later purchase. | P1 |
| 6 | MOD-CHK | Checkout & Order Management | As a buyer, I want to complete purchases with multiple payment options so that I can acquire products seamlessly. | P1 |
| 7 | MOD-PAY | Payment Processing & Escrow | As a buyer/seller, I want payments held in escrow so that funds are released only when I am satisfied. | P1 |
| 8 | MOD-DLV | Digital Delivery & Fulfillment | As a seller, I want to deliver digital goods through the platform so that buyers receive their purchases instantly. | P1 |
| 9 | MOD-REV | Reviews & Ratings | As a buyer, I want to rate and review products so that I can share my experience and help other buyers. | P2 |
| 10 | MOD-DSP | Dispute Resolution | As a buyer/seller, I want a formal dispute process so that conflicts are resolved fairly by moderators. | P2 |
| 11 | MOD-RFD | Refund & Returns | As a buyer, I want to request refunds for eligible purchases so that I am protected if a product is defective. | P1 |
| 12 | MOD-AFF | Affiliate Marketing | As an affiliate, I want to earn commissions by referring buyers so that I can monetize my audience. | P2 |
| 13 | MOD-CPN | Coupons & Discounts | As a seller, I want to create promotional coupons so that I can drive sales and reward loyal customers. | P2 |
| 14 | MOD-WTH | Withdrawals & Payouts | As a seller, I want to withdraw my earnings so that I can access my revenue from sales. | P1 |
| 15 | MOD-CMS | Content Management | As an administrator, I want to manage static pages, banners, and announcements so that the platform stays current. | P2 |
| 16 | MOD-MOD | Content Moderation | As a moderator, I want to review and approve content so that the platform remains safe and compliant. | P1 |
| 17 | MOD-NTF | Notifications & Alerts | As a user, I want to receive real-time notifications so that I stay informed about orders, messages, and updates. | P2 |
| 18 | MOD-MSG | Messaging & Inquiries | As a buyer, I want to message sellers directly so that I can ask questions before purchasing. | P2 |
| 19 | MOD-DSH | Dashboard & Analytics | As a seller, I want to view sales analytics so that I can make data-driven business decisions. | P2 |
| 20 | MOD-ADM | Administration Panel | As an administrator, I want to manage users, settings, and configurations so that the platform operates smoothly. | P1 |
| 21 | MOD-AUD | Audit & Compliance Logging | As a finance manager, I want an immutable audit trail so that all financial transactions are traceable. | P1 |
| 22 | MOD-FIN | Finance & Commission Engine | As a finance manager, I want to configure commission structures so that the platform generates revenue correctly. | P1 |
| 23 | MOD-SUP | Support Ticket System | As a support agent, I want to manage support tickets so that user issues are resolved promptly. | P2 |
| 24 | MOD-VRF | Seller Verification & KYC | As a moderator, I want to verify seller identities and documents so that only legitimate sellers operate on the platform. | P1 |
| 25 | MOD-API | Public API & Webhook Gateway | As a developer, I want to integrate with the platform via API so that external systems can automate operations. | P3 |
| 26 | MOD-RPT | Reporting & Business Intelligence | As a super administrator, I want to generate custom reports so that I can monitor platform health and growth. | P2 |

---

## 3. User Roles & Personas

| Role ID | Role Name | Description | System Access Level |
|---------|-----------|-------------|-------------------|
| R-GST | Guest | Unauthenticated visitor browsing public content | Public |
| R-BYR | Buyer | Registered user purchasing digital goods | Authenticated |
| R-SLR | Seller | Registered user listing and selling digital goods | Authenticated + Seller |
| R-MOD | Moderator | Staff user reviewing content and disputes | Internal Staff |
| R-SUP | Support Agent | Staff user handling tickets and inquiries | Internal Staff |
| R-FIN | Finance Manager | Staff user managing payouts, commissions, and reconciliation | Internal Staff |
| R-ADM | Administrator | Full system configuration and user management | Internal Admin |
| R-SAD | Super Administrator | Global system access, platform-level settings | Internal Super Admin |

---

## 4. Detailed User Stories

### 4.1 User Registration & Authentication (MOD-REG)

#### US-REG-001: Guest Registration
| Field | Value |
|-------|-------|
| **Story** | As a **guest**, I want to **register for an account with my email and password** so that **I can become a buyer on the platform**. |
| **Acceptance Criteria** | 1. Registration form captures full name, email, password, and phone number. 2. Email verification link is sent upon submission. 3. Account is inactive until email is verified. 4. Password must meet minimum complexity rules (8+ chars, uppercase, lowercase, digit, special char). 5. Duplicate email addresses are rejected with a clear error. 6. Google and Facebook OAuth buttons are visible. 7. CAPTCHA must be solved before submission. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-REG-002: Social Login
| Field | Value |
|-------|-------|
| **Story** | As a **guest**, I want to **sign up or log in using my Google or Facebook account** so that **I can onboard quickly without creating a new password**. |
| **Acceptance Criteria** | 1. OAuth 2.0 flow for Google and Facebook. 2. Profile data (name, email, avatar) is pre-filled from provider. 3. First-time social login creates a new account. 4. Subsequent logins are instant. 5. User can link/unlink social accounts in settings. 6. Email verification is skipped for OAuth accounts. |
| **Estimate** | 3 |
| **Priority** | P1 |

#### US-REG-003: Password Reset
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **reset my password via email** so that **I can regain access if I forget my credentials**. |
| **Acceptance Criteria** | 1. "Forgot Password" link is available on login page. 2. Email with secure reset token (expires in 30 min) is sent. 3. Token is single-use and invalidated after reset. 4. User is logged out of all active sessions after reset. 5. Confirmation email is sent after successful reset. |
| **Estimate** | 2 |
| **Priority** | P1 |

#### US-REG-004: Role-Based Access Control
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **assign and revoke user roles** so that **users have appropriate permissions for their responsibilities**. |
| **Acceptance Criteria** | 1. Role assignment UI in admin panel lists all users. 2. Roles: Guest, Buyer, Seller, Moderator, Support Agent, Finance Manager, Administrator, Super Administrator. 3. Multiple roles can be assigned (e.g., Buyer + Seller). 4. Permission changes take effect immediately without re-login. 5. Audit log records all role changes. 6. Super Admin role can only be assigned by another Super Admin. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-REG-005: Two-Factor Authentication (2FA)
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **enable two-factor authentication** so that **my account is protected against unauthorized access**. |
| **Acceptance Criteria** | 1. 2FA setup via authenticator app (TOTP). 2. Recovery codes (10 codes) are generated during setup. 3. User must enter 2FA code during login if enabled. 4. SMS fallback option is available. 5. Admin can enforce 2FA for seller and staff roles. 6. 2FA can be disabled only after confirming current password. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-REG-006: Session Management
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **view and terminate my active sessions** so that **I can maintain control over my account security**. |
| **Acceptance Criteria** | 1. Security settings page lists all active sessions. 2. Each session shows device, browser, IP, and last active timestamp. 3. User can terminate individual sessions or all sessions. 4. JWT tokens are invalidated on session termination. 5. Concurrent session limit is configurable by admin. |
| **Estimate** | 3 |
| **Priority** | P2 |

### 4.2 User Profile Management (MOD-PRO)

#### US-PRO-001: Buyer Profile
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **edit my profile with a photo, bio, and contact details** so that **sellers can recognize me and communicate effectively**. |
| **Acceptance Criteria** | 1. Profile fields: avatar, display name, bio, phone, country, language preference. 2. Avatar upload supports JPG/PNG, max 2 MB. 3. Display name is publicly visible; real name is private. 4. Email cannot be changed here (requires verification flow). 5. Profile is publicly viewable at `/profile/{username}`. |
| **Estimate** | 2 |
| **Priority** | P1 |

#### US-PRO-002: Seller Profile
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **create a seller profile with store name, logo, description, and policies** so that **buyers can learn about my store before purchasing**. |
| **Acceptance Criteria** | 1. Store name, logo, banner image, tagline, full description, return policy, shipping policy. 2. Store URL is customizable once (`/store/{slug}`). 3. SEO fields: meta title, meta description. 4. Social media links (Facebook, Twitter, Instagram, YouTube). 5. Store status: Active, Suspended, Closed. 6. Verification badge is shown after KYC approval. |
| **Estimate** | 3 |
| **Priority** | P1 |

#### US-PRO-003: Address Book
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **manage multiple saved addresses** so that **I can select a delivery address quickly during checkout**. |
| **Acceptance Criteria** | 1. Add, edit, delete addresses. 2. Fields: label (Home/Office/Other), full address, city, state, postal code, country. 3. Set one address as default. 4. Address validation via geocoding API. 5. Max 10 addresses per account. |
| **Estimate** | 2 |
| **Priority** | P2 |

#### US-PRO-004: Account Deletion
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **delete my account permanently** so that **my personal data is removed from the platform in compliance with privacy regulations**. |
| **Acceptance Criteria** | 1. Account deletion is available in settings. 2. User must confirm password and type "DELETE" to confirm. 3. Pending orders or disputes block deletion. 4. 30-day grace period before permanent deletion. 5. During grace period, account can be restored by logging in. 6. GDPR data export option is offered before deletion. |
| **Estimate** | 5 |
| **Priority** | P2 |

### 4.3 Product Listing & Catalog (MOD-LIS)

#### US-LIS-001: Create Digital Product Listing
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **create a digital product listing with title, description, pricing, and files** so that **buyers can discover and purchase my digital goods**. |
| **Acceptance Criteria** | 1. Product creation form: title (mandatory), description (mandatory), category, tags, price, compare-at price, SKU. 2. File upload: multiple files supported up to 2 GB total. 3. Supported file types configurable by admin. 4. Preview media: up to 5 images + 1 video. 5. Pricing: fixed or variable (buyer chooses amount). 6. Auto-save draft every 30 seconds. 7. Product remains in "Draft" status until submitted for review. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-LIS-002: Product Categories & Attributes
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **assign my product to a category with relevant attributes** so that **buyers can find it through structured browsing**. |
| **Acceptance Criteria** | 1. Hierarchical category tree (max 3 levels deep). 2. Dynamic attribute forms based on selected category. 3. Categories managed by admin. 4. A product can belong to one primary category and multiple secondary categories. 5. Category attributes: text, number, dropdown, multi-select, file. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-LIS-003: Product Variants
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **create product variants with different prices and files** so that **I can offer tiered packages (Basic, Pro, Enterprise)**. |
| **Acceptance Criteria** | 1. Variant options: name, price, stock (digital = unlimited), SKU, files. 2. Variants can have different file attachments. 3. Default variant is selectable. 4. Variant pricing can override base price. 5. Max 100 variants per product. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-LIS-004: Product Approval Workflow
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want to **review submitted products and approve or reject them** so that **only compliant, high-quality products are published**. |
| **Acceptance Criteria** | 1. Moderator queue shows all pending products sorted by submission date. 2. Product preview includes full listing, files, metadata. 3. Approve: product is published immediately. 4. Reject: reason is required; seller receives notification with rejection reason. 5. Rejected products can be edited and resubmitted. 6. SLA: review within 24 hours of submission. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-LIS-005: Bulk Product Upload
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **upload multiple products via CSV/Excel** so that **I can list my entire catalog efficiently**. |
| **Acceptance Criteria** | 1. Template CSV/Excel file download available. 2. File upload with column mapping validation. 3. Validation report with row-level errors. 4. Max 500 products per upload. 5. Products are created in "Draft" status. 6. Progress indicator for large uploads. |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-LIS-006: Product Visibility Controls
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **control whether my product is published, draft, or hidden** so that **I can manage my catalog lifecycle**. |
| **Acceptance Criteria** | 1. Status options: Draft, Pending Review, Published, Hidden, Archived. 2. Hidden products are not searchable but remain accessible via direct link. 3. Archived products preserve data but are removed from search. 4. Seller can un-archive products. 5. Status change history is logged. |
| **Estimate** | 3 |
| **Priority** | P2 |

### 4.4 Search & Discovery (MOD-SRC)

#### US-SRC-001: Full-Text Search
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **search products by keywords with relevant results** so that **I can quickly find what I am looking for**. |
| **Acceptance Criteria** | 1. Search bar is accessible from all pages (header). 2. Full-text search across title, description, tags, and seller name. 3. Results ranked by relevance score. 4. Typo tolerance for up to 2 character errors. 5. Search results load within 500 ms. 6. Empty state with suggestions when no results found. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-SRC-002: Advanced Filters & Sorting
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **filter search results by category, price range, rating, and sort by relevance/price/date** so that **I can narrow down to the perfect product**. |
| **Acceptance Criteria** | 1. Filter panel includes: category, price range (min/max), rating (1-5), file type, seller verification status. 2. Sort options: Relevance (default), Price (low-high), Price (high-low), Newest, Best Rated, Most Sold. 3. Active filters are displayed as removable chips. 4. URL query parameters reflect current filters for shareability. 5. Mobile-friendly collapsible filter panel. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-SRC-003: Category Browsing
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **browse products by category hierarchy** so that **I can explore the marketplace by department**. |
| **Acceptance Criteria** | 1. Main menu displays top-level categories. 2. Clicking a category shows subcategories in a breadcrumb. 3. Category page shows product count. 4. Featured products can be pinned to category pages by admin. 5. Category pages have SEO-friendly URLs. |
| **Estimate** | 3 |
| **Priority** | P1 |

#### US-SRC-004: Search Suggestions & Autocomplete
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **see search suggestions as I type** so that **I can discover popular search terms and save time**. |
| **Acceptance Criteria** | 1. Autocomplete dropdown appears after 2 characters. 2. Suggestions include product names, categories, and trending searches. 3. Max 8 suggestions displayed. 4. Keyboard navigation (arrow keys + Enter). 5. Suggestions update on each keystroke (debounced 300ms). |
| **Estimate** | 3 |
| **Priority** | P2 |

### 4.5 Cart & Wishlist (MOD-CRT)

#### US-CRT-001: Add to Cart
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **add products to a shopping cart** so that **I can review my selections before purchasing**. |
| **Acceptance Criteria** | 1. "Add to Cart" button on product page and search results. 2. Variant selection is required before adding if variants exist. 3. Quantity selector for items (default 1). 4. Cart icon in header shows item count badge. 5. Success toast notification on add. 6. Cart persists across sessions (server-side for logged-in, localStorage for guest). |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-CRT-002: Cart Management
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **view, update quantities, and remove items from my cart** so that **I have full control over my intended purchase**. |
| **Acceptance Criteria** | 1. Cart page lists all items with thumbnail, title, variant, unit price, quantity, subtotal. 2. Inline quantity update with +/- buttons. 3. Remove item with confirmation dialog. 4. Cart subtotal, discounts, and total displayed. 5. "Save for Later" moves item to wishlist. 6. Empty cart shows a friendly message with "Browse Products" CTA. |
| **Estimate** | 3 |
| **Priority** | P1 |

#### US-CRT-003: Wishlist
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **save products to a wishlist** so that **I can bookmark items and purchase them later**. |
| **Acceptance Criteria** | 1. Heart icon on product cards and detail page to toggle wishlist. 2. Wishlist page shows all saved items with thumbnail and current price. 3. "Move to Cart" button for each item. 4. Wishlist is private to the user. 5. Price drop notification can be enabled for wishlist items. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-CRT-004: Guest Cart Merge
| Field | Value |
|-------|-------|
| **Story** | As a **guest**, I want to **retain my cart items after logging in** so that **I do not lose my selections when creating an account**. |
| **Acceptance Criteria** | 1. Guest cart stored in localStorage is merged into server-side cart on login. 2. Duplicate products are updated to the higher quantity. 3. Merge happens silently with a notification. 4. Cart merge works across devices if already logged in. |
| **Estimate** | 3 |
| **Priority** | P1 |

### 4.6 Checkout & Order Management (MOD-CHK)

#### US-CHK-001: Single-Click Purchase
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **purchase a product with a single click** so that **I can complete a sale instantly without going through cart**. |
| **Acceptance Criteria** | 1. "Buy Now" button on product page bypasses cart and goes directly to checkout. 2. Single-item checkout flow is streamlined. 3. Default payment method and address are pre-selected. 4. Order confirmation is shown immediately. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-CHK-002: Multi-Item Checkout
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **check out multiple items from multiple sellers in one transaction** so that **I can consolidate my purchases**. |
| **Acceptance Criteria** | 1. Checkout groups items by seller with per-seller subtotals. 2. Each seller's items are separate line items in the payment. 3. Buyer can remove items per-seller during checkout. 4. Escrow handles split payments per seller. 5. A single receipt shows all items across sellers. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-CHK-003: Order History
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **view my complete order history with status** so that **I can track all purchases in one place**. |
| **Acceptance Criteria** | 1. Order history page shows all orders sorted by date (newest first). 2. Each order shows: order ID, date, items, total, status, payment method. 3. Click order to view full details. 4. Filter by status: Pending, Completed, Refunded, Disputed. 5. Search by order ID or product name. |
| **Estimate** | 3 |
| **Priority** | P1 |

#### US-CHK-004: Order Status Tracking
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **see the real-time status of my order** so that **I know when my digital product is available**. |
| **Acceptance Criteria** | 1. Status flow: Pending → Processing → Completed / Failed. 2. Visual progress indicator. 3. Timestamp for each status transition. 4. Estimated delivery time shown (instant for digital). 5. Status updates via notification and email. |
| **Estimate** | 3 |
| **Priority** | P1 |

### 4.7 Payment Processing & Escrow (MOD-PAY)

#### US-PAY-001: Multiple Payment Gateways
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **pay using credit/debit card, mobile banking, or digital wallet** so that **I can choose the most convenient payment method**. |
| **Acceptance Criteria** | 1. Payment gateways: Stripe, PayPal, bKash, Nagad, Rocket, SSLCommerz. 2. Gateway selection at checkout. 3. Redirect-based payment for external gateways. 4. Inline card form for Stripe. 5. Payment success/failure callbacks handled correctly. 6. Support for multiple currencies (BDT, USD). |
| **Estimate** | 13 |
| **Priority** | P1 |

#### US-PAY-002: Escrow Holding
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want **my payment held in escrow** so that **the seller only receives funds after I confirm delivery satisfaction**. |
| **Acceptance Criteria** | 1. Payment is captured immediately but held in platform escrow account. 2. Escrow period starts on order completion. 3. Funds are released to seller after buyer confirmation or auto-release after escrow period. 4. Escrow period: 14 days by default (configurable). 5. Buyer can raise a dispute during escrow period to hold funds. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-PAY-003: Payment Receipt & Invoice
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **download a payment receipt and invoice** so that **I have records for accounting and tax purposes**. |
| **Acceptance Criteria** | 1. Receipt is generated immediately after successful payment. 2. Receipt includes: order ID, date, items, amounts, tax, total, payment method, transaction ID. 3. Invoice is downloadable as PDF. 4. Receipt is emailed to buyer. 5. VAT/GST breakdown shown if applicable. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-PAY-004: Payment Failure Handling
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **be notified and guided if a payment fails** so that **I can retry with an alternative method**. |
| **Acceptance Criteria** | 1. Clear error message explaining the failure reason. 2. "Retry Payment" button on failure screen. 3. Failed orders are saved as "Payment Pending" for 24 hours. 4. Automatic reminder email to complete payment. 5. Order is cancelled after 24 hours of non-payment. |
| **Estimate** | 3 |
| **Priority** | P1 |

### 4.8 Digital Delivery & Fulfillment (MOD-DLV)

#### US-DLV-001: Digital File Delivery
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **download my purchased digital files immediately after payment** so that **I can access the product without delay**. |
| **Acceptance Criteria** | 1. Download link is available on order confirmation page and in order history. 2. Download link is also sent via email. 3. Files are served via CDN with signed URLs (expire in 24 hours). 4. Large files (>100 MB) show download progress. 5. Max download attempts: 10 per order (configurable). 6. Files are scanned for malware before delivery. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-DLV-002: Download Manager
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **access all my purchased files from a central download manager** so that **I can re-download products I have bought**. |
| **Acceptance Criteria** | 1. "My Downloads" page lists all purchased digital products. 2. Search and filter by product name and date. 3. Each entry shows product name, purchase date, download count, file size. 4. "Download" button with signed URL generation. 5. Lifetime access to purchased digital files. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-DLV-003: Seller File Management
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **upload, version, and update files for my products** so that **I can provide updates and fixes to existing buyers**. |
| **Acceptance Criteria** | 1. Seller can replace files for published products. 2. Version history is maintained (v1.0, v1.1, etc.). 3. Existing buyers receive notification of new version. 4. Version upgrade is optional for buyers (they keep current or download new). 5. File change triggers re-moderation if the product is in Pending status. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-DLV-004: Delivery Confirmation
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **receive delivery confirmation when a buyer downloads my files** so that **I know the transaction is complete**. |
| **Acceptance Criteria** | 1. Seller dashboard shows download events per product. 2. Notification sent to seller when buyer downloads. 3. Download analytics: date, buyer, file, IP (partial). 4. Seller can manually confirm delivery for escrow release. 5. Auto-release trigger after download event. |
| **Estimate** | 3 |
| **Priority** | P2 |

### 4.9 Reviews & Ratings (MOD-REV)

#### US-REV-001: Submit Review
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **submit a star rating and written review for a purchased product** so that **I can share my experience with the community**. |
| **Acceptance Criteria** | 1. Review can only be submitted after purchase and within 30 days. 2. Rating: 1–5 stars (mandatory). 3. Written review: 10–5000 characters (optional but encouraged). 4. Image uploads allowed (max 3, 5 MB each). 5. Single review per product per buyer. 6. Review is published immediately but can be flagged for moderation. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-REV-002: Review Moderation
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want to **review flagged reviews and remove inappropriate content** so that **the platform maintains quality and authenticity**. |
| **Acceptance Criteria** | 1. Moderator has a queue of flagged reviews. 2. Review can be approved, rejected (with reason), or left as-is. 3. Rejected review is hidden but not deleted. 4. Buyer is notified if their review is rejected. 5. Automated filters catch profanity and spam before publishing. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-REV-003: Review Aggregation
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **see the average rating and review count for a product** so that **I can assess product quality at a glance**. |
| **Acceptance Criteria** | 1. Product page shows average rating (stars + numeric), total review count, and rating distribution bar chart. 2. Reviews are sorted by "Most Helpful" default, with options for "Newest" and "Highest/Lowest Rating". 3. Seller cannot delete negative reviews. 4. Verified Purchase badge on reviews from confirmed buyers. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-REV-004: Seller Reply to Reviews
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **reply to buyer reviews publicly** so that **I can address concerns and demonstrate customer engagement**. |
| **Acceptance Criteria** | 1. Seller can post one public reply per review. 2. Reply is displayed directly below the review. 3. Seller can edit their reply within 24 hours. 4. Reply is subject to same moderation rules as reviews. 5. Buyer is notified when seller replies. |
| **Estimate** | 2 |
| **Priority** | P2 |

### 4.10 Dispute Resolution (MOD-DSP)

#### US-DSP-001: Raise Dispute
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **raise a dispute against an order** so that **I can formally report an issue and halt the escroll release**. |
| **Acceptance Criteria** | 1. Dispute button available on order detail page during escrow period. 2. Dispute form: reason category (Item not received, Item defective, Not as described, Other), description (mandatory), file attachments (max 5). 3. Escrow funds are frozen upon dispute creation. 4. Seller is notified immediately. 5. Both parties receive a case ID for reference. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-DSP-002: Dispute Management
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want to **review dispute cases and make binding decisions** so that **conflicts are resolved fairly and quickly**. |
| **Acceptance Criteria** | 1. Moderator dashboard lists all open disputes sorted by oldest first. 2. Each case shows order details, buyer and seller info, dispute reason, evidence. 3. Moderator can request additional evidence from either party. 4. Moderator can grant full refund, partial refund, or release funds to seller. 5. Decision is final and notified to both parties. 6. SLA: initial response within 24 hours, resolution within 5 business days. |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-DSP-003: Escalation to Admin
| Field | Value |
|-------|-------|
| **Story** | As a **buyer/seller**, I want to **appeal a moderator's dispute decision** so that **I can escalate unresolved conflicts to a higher authority**. |
| **Acceptance Criteria** | 1. Appeal option available for 7 days after moderator decision. 2. Appeal requires explanation and new evidence. 3. Appeal is reviewed by a senior moderator or admin. 4. Admin decision is final and cannot be further appealed. 5. Appeal SLA: resolution within 7 business days. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-DSP-004: Automated Dispute Prevention
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want **automated checks to prevent common dispute scenarios** so that **the dispute volume is minimized**. |
| **Acceptance Criteria** | 1. System checks for file integrity before marking order complete. 2. Buyer must click "Download" before order can be auto-completed. 3. Seller cannot cancel an order with active escrow. 4. Multiple disputes from same user trigger a flag for review. 5. High-dispute sellers are flagged for account review. |
| **Estimate** | 5 |
| **Priority** | P3 |

### 4.11 Refund & Returns (MOD-RFD)

#### US-RFD-001: Request Refund
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **request a refund for a digital product** so that **I can get my money back if the product is defective or not as described**. |
| **Acceptance Criteria** | 1. Refund request available within 14 days of purchase. 2. Refund reason categories. 3. Request goes to seller first for 48 hours (seller can accept or escalate). 4. If seller does not respond in 48 hours, auto-escalated to moderator. 5. Buyer cannot request refund if they initiated download more than 5 times (configurable). |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-RFD-002: Refund Processing
| Field | Value |
|-------|-------|
| **Story** | As a **finance manager**, I want to **process approved refunds and reverse escrow funds** so that **buyers receive their money back promptly**. |
| **Acceptance Criteria** | 1. Refund is processed to original payment method when possible. 2. Wallet credit option if original method cannot accept refund. 3. Platform commission is reversed proportionally. 4. Refund appears in buyer's account within 5-10 business days. 5. Refund audit log records who approved, amount, date, and reason. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-RFD-003: Refund Policy Display
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **set my own refund policy for each product** so that **buyers are aware of the terms before purchasing**. |
| **Acceptance Criteria** | 1. Refund policy field on product listing form. 2. Policy is displayed prominently on product page before purchase. 3. Platform enforces a minimum refund policy that sellers cannot override. 4. Custom policies must comply with platform guidelines. 5. Policy is included in the purchase receipt email. |
| **Estimate** | 2 |
| **Priority** | P2 |

### 4.12 Affiliate Marketing (MOD-AFF)

#### US-AFF-001: Affiliate Registration
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **register as an affiliate** so that **I can earn commissions by promoting products**. |
| **Acceptance Criteria** | 1. Affiliate registration form: website/social media URL, promotion methods, audience size. 2. Application is reviewed by admin. 3. Approved affiliates get a unique referral code and dashboard access. 4. Affiliate agreement must be accepted electronically. 5. Payout threshold and commission rate are displayed during signup. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-AFF-002: Referral Link Generation
| Field | Value |
|-------|-------|
| **Story** | As an **affiliate**, I want to **generate referral links for any product or store** so that **I can share them across my channels**. |
| **Acceptance Criteria** | 1. Affiliate dashboard has link generator tool. 2. Links can target specific products or entire stores. 3. Links include unique affiliate ID parameter. 4. Short URL option (e.g., tsbl.bd/r/abc123). 5. Link preview shows destination before sharing. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-AFF-003: Affiliate Commission Tracking
| Field | Value |
|-------|-------|
| **Story** | As an **affiliate**, I want to **track my clicks, conversions, and earnings in real-time** so that **I can optimize my promotion strategy**. |
| **Acceptance Criteria** | 1. Dashboard shows: total clicks, unique clicks, conversions, conversion rate, total earnings, pending earnings, paid earnings. 2. Breakdown by product and date range. 3. Cookie-based tracking with 30-day attribution window. 4. Click-to-conversion funnel visualization. 5. Exportable reports (CSV). |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-AFF-004: Affiliate Payout
| Field | Value |
|-------|-------|
| **Story** | As an **affiliate**, I want to **withdraw my earned commissions** so that **I can receive payment for my marketing efforts**. |
| **Acceptance Criteria** | 1. Minimum payout threshold: $20 (configurable). 2. Payout methods: Bank transfer, bKash, PayPal. 3. Payout requests are processed within 5 business days. 4. Commission is locked for 14 days after sale to allow for refunds. 5. Negative commission balance is carried forward if refunds exceed earnings. |
| **Estimate** | 5 |
| **Priority** | P2 |

### 4.13 Coupons & Discounts (MOD-CPN)

#### US-CPN-001: Create Coupon Campaign
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **create discount coupons with custom rules** so that **I can run promotions and boost sales**. |
| **Acceptance Criteria** | 1. Coupon creation form: code (auto-generate or custom), discount type (percentage or fixed), value, minimum purchase amount, max usage count, expiry date. 2. Coupon can apply to all products or specific products. 3. Start and end date/time for scheduled campaigns. 4. Coupon can be stacked or non-stackable with other offers. 5. Max 50 active coupons per seller. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-CPN-002: Apply Coupon at Checkout
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **enter a coupon code at checkout** so that **I can receive a discount on my purchase**. |
| **Acceptance Criteria** | 1. Coupon code input field on checkout page. 2. "Apply" button validates and applies the coupon. 3. Discount is shown as a line item before totals. 4. Invalid/expired coupon shows clear error message. 5. Applied coupon can be removed. 6. Discount is reflected in payment amount. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-CPN-003: Coupon Analytics
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **view coupon usage analytics** so that **I can measure the effectiveness of my promotions**. |
| **Acceptance Criteria** | 1. Dashboard shows per-coupon metrics: times used, total discount given, revenue generated, conversion rate. 2. Redemption trend over time. 3. Coupon can be disabled mid-campaign. 4. Usage count against max cap is displayed. |
| **Estimate** | 3 |
| **Priority** | P3 |

### 4.14 Withdrawals & Payouts (MOD-WTH)

#### US-WTH-001: Seller Withdrawal Request
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **request a withdrawal of my available balance** so that **I can transfer my earnings to my bank account**. |
| **Acceptance Criteria** | 1. Withdrawal page shows current balance, pending balance, and available balance. 2. Withdrawal amount must be above minimum threshold ($10). 3. Withdrawal methods: Bank transfer, bKash, Nagad, PayPal. 4. Seller must have completed KYC before withdrawal. 5. Daily withdrawal limit: $1,000 (configurable). 6. Withdrawal request is recorded and sent to finance for processing. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-WTH-002: Withdrawal Processing
| Field | Value |
|-------|-------|
| **Story** | As a **finance manager**, I want to **review and process seller withdrawal requests** so that **sellers receive their funds accurately and on time**. |
| **Acceptance Criteria** | 1. Finance dashboard lists all pending withdrawal requests. 2. Each request shows seller info, amount, method, bank details, and KYC status. 3. Finance can approve or reject with reason. 4. Approved withdrawals trigger batch payment via connected gateway. 5. Rejected withdrawals return funds to seller's available balance. 6. SLA: process within 48 hours. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-WTH-003: Withdrawal History
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **view my withdrawal history** so that **I can track all past and pending payouts**. |
| **Acceptance Criteria** | 1. Withdrawal history table shows: date, amount, method, status (Pending, Processing, Completed, Failed, Rejected). 2. Status updates are real-time. 3. Failed withdrawals show reason. 4. Filter by date range and status. 5. Receipt available for completed withdrawals. |
| **Estimate** | 2 |
| **Priority** | P2 |

### 4.15 Content Management (MOD-CMS)

#### US-CMS-001: Page Builder
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **create and edit static pages (About Us, Terms, Privacy, FAQ)** so that **the platform has up-to-date legal and informational content**. |
| **Acceptance Criteria** | 1. WYSIWYG editor with rich text formatting. 2. Media embedding (images, videos). 3. SEO fields: meta title, meta description, slug. 4. Pages can be published, drafted, or archived. 5. Version history with rollback capability. 6. Pages are cached with CDN and purged on update. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-CMS-002: Banner & Slider Management
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **manage homepage banners and promotional sliders** so that **I can feature campaigns and announcements**. |
| **Acceptance Criteria** | 1. Banner creation: image upload, link URL, title, subtitle, CTA text. 2. Sort order for multiple banners. 3. Schedule: start and end date/time. 4. Device-specific images (desktop vs mobile). 5. Click-through rate tracking. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-CMS-004: Announcement System
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **create platform-wide announcements** so that **I can communicate important updates to all users**. |
| **Acceptance Criteria** | 1. Announcement creation with title, body, severity (Info, Warning, Critical). 2. Target audience: All Users, Buyers Only, Sellers Only, Staff. 3. Announcements appear as dismissible banners or modals. 4. Read receipts tracked for critical announcements. 5. Expiry date for auto-hide. |
| **Estimate** | 3 |
| **Priority** | P3 |

### 4.16 Content Moderation (MOD-MOD)

#### US-MOD-001: Moderation Queue
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want to **have a unified queue of all content pending review** so that **I can efficiently process approvals and rejections**. |
| **Acceptance Criteria** | 1. Queue includes: product listings, reviews, seller profiles, file uploads. 2. Sort by submission date (oldest first). 3. Filter by content type and status. 4. Bulk actions: approve selected, reject selected. 5. Queue shows priority items flagged by automated systems. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-MOD-002: Automated Content Filtering
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want **automated content filtering for prohibited items, spam, and plagiarism** so that **obviously violative content never reaches the queue**. |
| **Acceptance Criteria** | 1. Keyword-based blacklist for prohibited items. 2. Image moderation API for NSFW detection. 3. Plagiarism check against existing listings. 4. Auto-reject with 95%+ confidence score. 5. Flag for manual review for 70-94% confidence. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-MOD-003: User Restriction
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want to **restrict or suspend users who violate platform policies** so that **repeat offenders cannot harm the marketplace**. |
| **Acceptance Criteria** | 1. Restriction actions: Warning, Temporary Suspension (1-30 days), Permanent Ban. 2. Reason and evidence required. 3. Affected user receives notification with appeal instructions. 4. Suspended seller's listings are hidden. 5. Suspended buyer cannot place new orders. 6. Restrictions are logged in audit trail. |
| **Estimate** | 5 |
| **Priority** | P1 |

### 4.17 Notifications & Alerts (MOD-NTF)

#### US-NTF-001: In-App Notifications
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **receive in-app notifications for important events** so that **I am always informed about activities concerning my account**. |
| **Acceptance Criteria** | 1. Notification bell icon in header with unread count badge. 2. Notification types: order updates, messages, review replies, dispute updates, withdrawal status, approval/rejection. 3. Clicking a notification navigates to relevant page. 4. Mark as read individually or "Mark All as Read". 5. Notifications are persisted and searchable. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-NTF-002: Email Notifications
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **receive email notifications for critical events** so that **I do not miss important updates when I am offline**. |
| **Acceptance Criteria** | 1. Email triggers: order confirmation, payment receipt, download link, dispute update, password change, KYC status. 2. Transactional emails have high deliverability priority. 3. Users can opt out of marketing emails. 4. Transactional emails cannot be opted out. 5. Email templates are responsive and branded. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-NTF-003: Notification Preferences
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **configure which notifications I receive and through which channel** so that **I am not overwhelmed by unwanted alerts**. |
| **Acceptance Criteria** | 1. Preferences page lists all notification types with toggle switches. 2. Channel options: In-app, Email, SMS (if verified). 3. Digest option for non-critical notifications (daily/weekly summary). 4. Quiet hours configuration. 5. Preferences are saved instantly. |
| **Estimate** | 3 |
| **Priority** | P3 |

### 4.18 Messaging & Inquiries (MOD-MSG)

#### US-MSG-001: Buyer-Seller Messaging
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **send direct messages to sellers** so that **I can ask questions about products before purchasing**. |
| **Acceptance Criteria** | 1. "Contact Seller" button on product page. 2. Message form includes subject and message body. 3. Product link is auto-attached to the message. 4. Conversation history is preserved. 5. Real-time messaging via WebSocket for online users. 6. Seller can block a buyer if necessary (reviewed by moderator). |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-MSG-002: Admin-to-User Messaging
| Field | Value |
|-------|-------|
| **Story** | As a **support agent**, I want to **send official messages to users** so that **I can communicate about account issues, verification, or policy violations**. |
| **Acceptance Criteria** | 1. Support agent can initiate a conversation with any user. 2. Messages are marked as "Official" with distinct styling. 3. Users can reply to official messages. 4. Conversation log is immutable for audit purposes. 5. Templates for common messages (verification, warning, etc.). |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-MSG-003: Message Notifications
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **receive notifications when I get a new message** so that **I can respond promptly**. |
| **Acceptance Criteria** | 1. Real-time notification via WebSocket when new message arrives. 2. Email notification when user is offline. 3. Unread message count in inbox. 4. Push notification for mobile browsers (if supported). |
| **Estimate** | 2 |
| **Priority** | P2 |

### 4.19 Dashboard & Analytics (MOD-DSH)

#### US-DSH-001: Seller Dashboard
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **view a comprehensive dashboard with sales metrics** so that **I can monitor my business performance at a glance**. |
| **Acceptance Criteria** | 1. Dashboard widgets: total revenue (today, this week, this month, all time), total orders, pending orders, average rating. 2. Revenue chart (line/bar) with date range selector. 3. Recent orders list (last 10). 4. Top-selling products. 5. Traffic sources (direct, affiliate, search). 6. Conversion rate. |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-DSH-002: Buyer Dashboard
| Field | Value |
|-------|-------|
| **Story** | As a **buyer**, I want to **view a personalized dashboard** so that **I can quickly access my recent orders, downloads, and wishlist**. |
| **Acceptance Criteria** | 1. Dashboard shows: recent orders (last 5), recent downloads, wishlist count, unread messages, pending reviews. 2. Quick action buttons: "View Cart", "My Downloads", "Wishlist", "Support Tickets". 3. Order status summary widget. 4. Recommended products based on purchase history. |
| **Estimate** | 3 |
| **Priority** | P2 |

#### US-DSH-003: Revenue Reports
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **generate revenue reports for specific periods** so that **I can analyze trends and file taxes**. |
| **Acceptance Criteria** | 1. Report parameters: date range, granularity (daily/weekly/monthly), product filter. 2. Report includes: gross revenue, platform fees, net revenue, refunds, order count. 3. Export as PDF, CSV, Excel. 4. Scheduled report delivery via email. 5. Report data is read-only and time-stamped. |
| **Estimate** | 5 |
| **Priority** | P2 |

### 4.20 Administration Panel (MOD-ADM)

#### US-ADM-001: User Management
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **view, search, edit, and manage all users** so that **I can handle account issues and maintain platform health**. |
| **Acceptance Criteria** | 1. User list with search (email, name, ID) and filters (role, status, registration date). 2. User detail view: profile, orders, listings, messages, dispute history, login history. 3. Actions: edit profile, change role, suspend, ban, verify email. 4. Impersonate user (with audit logging). 5. Export user list as CSV. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-ADM-002: System Configuration
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **configure platform settings** so that **the marketplace operates according to business rules**. |
| **Acceptance Criteria** | 1. Configurable settings: platform name, logo, favicon, currency, timezone, language. 2. Commission rates (global and per-category). 3. Escrow period duration. 4. File size limits and allowed types. 5. Email SMTP configuration. 6. Maintenance mode toggle. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-ADM-003: Category Management
| Field | Value |
|-------|-------|
| **Story** | As an **administrator**, I want to **manage the product category tree** so that **products are organized logically for browsing**. |
| **Acceptance Criteria** | 1. Add, edit, delete, reorder categories. 2. Category hierarchy with parent-child relationships. 3. Category-specific attributes and commission rates. 4. Category image/icon. 5. Merge categories (move all products from one to another). |
| **Estimate** | 5 |
| **Priority** | P1 |

### 4.21 Audit & Compliance Logging (MOD-AUD)

#### US-AUD-001: Financial Audit Trail
| Field | Value |
|-------|-------|
| **Story** | As a **finance manager**, I want **an immutable log of all financial transactions** so that **I can reconcile accounts and pass audits**. |
| **Acceptance Criteria** | 1. Every payment, refund, withdrawal, commission, and fee is logged. 2. Log entries: timestamp, user ID, transaction type, amount, balance before/after, reference ID. 3. Logs are append-only and cannot be modified or deleted. 4. Logs are searchable and filterable. 5. Logs can be exported for external audit. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-AUD-002: Activity Log
| Field | Value |
|-------|-------|
| **Story** | As a **super administrator**, I want **a full activity log of all administrative actions** so that **I can monitor staff activity and detect abuse**. |
| **Acceptance Criteria** | 1. Every admin/moderator action is logged: who, what, when, IP address, user agent. 2. Logs are immutable. 3. Search by admin, action type, date range. 4. Alerts for suspicious patterns (e.g., mass user deletion). 5. Retention period: 2 years minimum. |
| **Estimate** | 5 |
| **Priority** | P1 |

### 4.22 Finance & Commission Engine (MOD-FIN)

#### US-FIN-001: Commission Configuration
| Field | Value |
|-------|-------|
| **Story** | As a **finance manager**, I want to **configure multi-tier commission structures** so that **the platform earns revenue appropriately across categories**. |
| **Acceptance Criteria** | 1. Commission types: flat fee per sale, percentage, tiered (volume-based). 2. Category-specific commission overrides. 3. Seller-specific commission agreements (override global). 4. Commission is calculated at transaction time. 5. Commission reports show earnings breakdown. |
| **Estimate** | 8 |
| **Priority** | P1 |

#### US-FIN-002: Transaction Reconciliation
| Field | Value |
|-------|-------|
| **Story** | As a **finance manager**, I want to **reconcile platform transactions against payment gateway reports** so that **all funds are accounted for**. |
| **Acceptance Criteria** | 1. Upload gateway settlement report (CSV). 2. System matches gateway transactions to platform orders. 3. Unmatched transactions flagged for manual review. 4. Discrepancy report with amount differences. 5. Reconciliation history is preserved. |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-FIN-003: Tax Calculation
| Field | Value |
|-------|-------|
| **Story** | As a **finance manager**, I want to **configure tax rules for different jurisdictions** so that **the platform correctly charges and remits taxes**. |
| **Acceptance Criteria** | 1. Tax configuration per country/region. 2. Tax types: VAT, GST, Sales Tax. 3. Tax rate is percentage or fixed. 4. Tax is calculated at checkout and shown as line item. 5. Tax-exempt buyers (NGOs, government) can upload exemption certificate. |
| **Estimate** | 5 |
| **Priority** | P2 |

### 4.23 Support Ticket System (MOD-SUP)

#### US-SUP-001: Create Support Ticket
| Field | Value |
|-------|-------|
| **Story** | As a **user**, I want to **create a support ticket** so that **I can get help with issues that cannot be resolved through self-service**. |
| **Acceptance Criteria** | 1. "Submit a Ticket" form: subject, category (Account, Payment, Technical, Other), description, file attachments (max 3). 2. Order/product reference can be linked. 3. Ticket receives a unique ID. 4. Confirmation email with ticket ID. 5. Priority is auto-assigned based on category and user history. |
| **Estimate** | 5 |
| **Priority** | P2 |

#### US-SUP-002: Ticket Management
| Field | Value |
|-------|-------|
| **Story** | As a **support agent**, I want to **manage and respond to support tickets** so that **user issues are resolved efficiently**. |
| **Acceptance Criteria** | 1. Agent dashboard lists all open tickets sorted by priority and date. 2. Ticket detail shows full conversation history with timestamps. 3. Agent can change status: Open, In Progress, Waiting on User, Resolved, Closed. 4. Canned responses for common issues. 5. Internal notes visible only to staff. 6. Ticket assignment to specific agents. |
| **Estimate** | 8 |
| **Priority** | P2 |

#### US-SUP-003: Ticket SLA
| Field | Value |
|-------|-------|
| **Story** | As a **support agent**, I want **SLA tracking on tickets** so that **I prioritize urgent issues and meet response time targets**. |
| **Acceptance Criteria** | 1. SLA targets: Critical (1 hour), High (4 hours), Normal (24 hours), Low (72 hours). 2. SLA timer pauses when waiting on user. 3. Color-coded SLA status (green, yellow, red). 4. Escalation to admin if SLA breached. 5. SLA performance report for agents. |
| **Estimate** | 5 |
| **Priority** | P2 |

### 4.24 Seller Verification & KYC (MOD-VRF)

#### US-VRF-001: KYC Document Submission
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **submit my identity and business documents** so that **I can become a verified seller and gain buyer trust**. |
| **Acceptance Criteria** | 1. KYC form collects: full name, date of birth, national ID/passport number, address proof, business registration (if applicable). 2. Document upload: front/back of ID, selfie, utility bill, business license. 3. Supported formats: JPG, PNG, PDF (max 10 MB each). 4. Progress indicator for multi-step form. 5. Application is saved as draft until submitted. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-VRF-002: KYC Review
| Field | Value |
|-------|-------|
| **Story** | As a **moderator**, I want to **review KYC applications and approve or reject them** so that **only verified sellers can transact on the platform**. |
| **Acceptance Criteria** | 1. KYC queue shows all pending applications with submission date. 2. Document viewer with zoom and rotate. 3. Approve: seller gets verified badge and can create listings. 4. Reject: reason required; seller can resubmit. 5. SLA: review within 48 hours. 6. Manual override for complex cases. |
| **Estimate** | 5 |
| **Priority** | P1 |

#### US-VRF-003: KYC Levels
| Field | Value |
|-------|-------|
| **Story** | As a **seller**, I want to **upgrade my KYC level to unlock higher transaction limits** so that **I can scale my business on the platform**. |
| **Acceptance Criteria** | 1. KYC Level 1: Email + Phone verified (max $500/month sales). 2. KYC Level 2: ID verified (max $5,000/month sales). 3. KYC Level 3: Full KYC with business docs (unlimited). 4. Upgrade path is clear with requirements listed. 5. Current limit and next-level limit displayed on dashboard. |
| **Estimate** | 5 |
| **Priority** | P2 |

### 4.25 Public API & Webhook Gateway (MOD-API)

#### US-API-001: RESTful API
| Field | Value |
|-------|-------|
| **Story** | As a **developer**, I want to **access marketplace data via RESTful API** so that **I can build integrations, mobile apps, or third-party tools**. |
| **Acceptance Criteria** | 1. API endpoints for products, orders, users, payments. 2. Authentication via API key or OAuth 2.0. 3. Rate limiting: 100 requests/min per key. 4. Pagination, sorting, and filtering on list endpoints. 5. JSON and XML response formats. 6. API documentation via Swagger/OpenAPI. |
| **Estimate** | 13 |
| **Priority** | P3 |

#### US-API-002: Webhook Events
| Field | Value |
|-------|-------|
| **Story** | As a **developer**, I want to **register webhooks for real-time event notifications** so that **my external system can react to marketplace events**. |
| **Acceptance Criteria** | 1. Webhook events: order.created, payment.completed, dispute.filed, withdrawal.processed. 2. Webhook URL configuration with secret signing key. 3. Payload signed with HMAC-SHA256 for verification. 4. Retry mechanism: 3 retries with exponential backoff. 5. Webhook delivery log with status codes. |
| **Estimate** | 8 |
| **Priority** | P3 |

### 4.26 Reporting & Business Intelligence (MOD-RPT)

#### US-RPT-001: Custom Report Builder
| Field | Value |
|-------|-------|
| **Story** | As a **super administrator**, I want to **create custom reports with drag-and-drop fields and filters** so that **I can analyze platform data without SQL knowledge**. |
| **Acceptance Criteria** | 1. Report builder interface: select data source (orders, users, payments, etc.), choose fields, apply filters, set grouping. 2. Chart types: table, bar, line, pie, area. 3. Date range and period comparison. 4. Save report templates for reuse. 5. Schedule automated report generation and email delivery. |
| **Estimate** | 13 |
| **Priority** | P2 |

#### US-RPT-002: Pre-Built Reports
| Field | Value |
|-------|-------|
| **Story** | As a **super administrator**, I want **pre-built reports for common business metrics** so that **I can monitor KPIs immediately without configuration**. |
| **Acceptance Criteria** | 1. Reports: Daily Sales Summary, Top Sellers, Top Products, User Growth, Revenue by Category, Refund Rate, Dispute Rate. 2. Each report shows current period vs previous period comparison. 3. Export to PDF, CSV, Excel, and PNG (charts). 4. Dashboard snapshots can be scheduled for email. |
| **Estimate** | 8 |
| **Priority** | P2 |

---

## 5. Story Backlog Summary

### 5.1 Count by Priority

| Priority | Count |
|----------|-------|
| P1 — Must-have | 39 |
| P2 — Should-have | 56 |
| P3 — Could-have | 9 |
| P4 — Won't-have | 0 |
| **Total** | **104** |

### 5.2 Count by Role

| Role | Primary Stories |
|------|-----------------|
| Guest (R-GST) | 3 |
| Buyer (R-BYR) | 30 |
| Seller (R-SLR) | 24 |
| Moderator (R-MOD) | 8 |
| Support Agent (R-SUP) | 4 |
| Finance Manager (R-FIN) | 7 |
| Administrator (R-ADM) | 7 |
| Super Administrator (R-SAD) | 2 |
| Developer / Affiliate / Mixed | 19 |
| **Total** | **104** |

### 5.3 Total Story Points

| Priority | Points |
|----------|--------|
| P1 | 201 |
| P2 | 272 |
| P3 | 52 |
| **Total** | **525** |

### 5.4 Estimation Confidence

| Confidence Level | Percentage of Stories |
|------------------|----------------------|
| High (±10%) | 65% |
| Medium (±25%) | 25% |
| Low (±50%) | 10% |

---

*End of Document — TRUE STAR BD LIMITED*

---

**Document Status:** Draft  
**Next Review:** 2026-07-15  
**Change Control:** All changes require approval by the Product Owner and Chief Architect.
