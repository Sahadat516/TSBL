# TRUE STAR BD LIMITED — Business Rules Specification

> **Document Version:** 1.0.0
> **Classification:** Internal — Confidential
> **Author:** Enterprise Architecture Team
> **Last Updated:** 2026-07-02
> **Status:** Final Draft
> **Applies To:** Multi-Vendor Digital Marketplace Platform

---

## Table of Contents

1. Marketplace Workflow
2. Buyer Journey
3. Seller Journey
4. Admin Journey
5. Product Lifecycle
6. Order Lifecycle
7. Escrow Workflow
8. Wallet Workflow
9. Payment Workflow
10. Refund Workflow
11. Withdrawal Workflow
12. Coupon Workflow
13. Affiliate Workflow
14. Review Workflow
15. Rating Workflow
16. Messaging Workflow
17. Notification Workflow
18. Dispute Workflow
19. Support Ticket Workflow
20. Seller Verification Workflow
21. KYC Workflow
22. Product Approval Workflow
23. Account Suspension Rules
24. Fraud Detection Rules
25. Marketplace Commission Rules
26. Marketplace Fee Rules
27. Seller Ranking Algorithm
28. Buyer Reputation Rules
29. Seller Reputation Rules
30. Search Ranking Rules
31. Featured Product Rules
32. Trending Product Rules
33. Flash Sale Rules
34. Promotion Rules
35. Inventory Rules
36. Digital Delivery Rules
37. License Key Delivery Rules
38. Digital File Delivery Rules
39. Currency Rules
40. Localization Rules
41. Tax Rules
42. Invoice Rules
43. Notification Priority Rules
44. Permission Matrix
45. Role Matrix
46. Feature Access Matrix
47. Business Validation Rules
48. Edge Cases
49. Abuse Prevention Rules
50. Marketplace Policies

---

## 1. Marketplace Workflow

### Objective
Define the end-to-end operational flow governing how buyers, sellers, and administrators interact within the marketplace to complete transactions.

### Business Rules
- BR-MW-001: Every transaction must progress through states: INITIATED ? PENDING_PAYMENT ? PAID ? DELIVERED ? COMPLETED.
- BR-MW-002: The marketplace must act as an intermediary; funds must never move directly between buyer and seller.
- BR-MW-003: All digital goods must be delivered through the platform's delivery subsystem; off-platform delivery is prohibited.
- BR-MW-004: A seller must have VERIFIED status to list products priced above .
- BR-MW-005: The marketplace must withhold a commission on every completed transaction before releasing funds to the seller.
- BR-MW-006: Any user with two or more accounts linked to the same verified identity must be flagged for review.
- BR-MW-007: Marketplace operating hours are 24/7; no downtime is permitted except for scheduled maintenance (max 4 hours monthly).
- BR-MW-008: The marketplace must support a minimum of 10,000 concurrent active sessions at launch.
- BR-MW-009: All marketplace data exports must comply with GDPR and applicable data protection regulations.
- BR-MW-010: The marketplace must maintain an audit log of all state transitions for a minimum of 7 years.

### Validation Rules
- VR-MW-001: A transaction cannot transition from INITIATED to DELIVERED without passing through PAID.
- VR-MW-002: A seller's product listing count must not exceed their tier's maximum limit (Basic: 50, Pro: 500, Enterprise: unlimited).
- VR-MW-003: Buyer must have a verified email and phone before placing an order exceeding ,000.

### Preconditions
- PC-MW-001: The platform must be fully initialized with at least one payment gateway.
- PC-MW-002: At least one administrator must be active.
- PC-MW-003: Terms of Service must be accepted by all users.

### Postconditions
- PO-MW-001: Every transaction results in a unique order ID recorded in the ledger.
- PO-MW-002: Audit trail is appended for every state change.

### Success Flow
1. Guest browses public listings ? registers ? becomes Buyer.
2. Buyer selects product ? initiates purchase ? payment captured in escrow.
3. Seller receives notification ? delivers digital asset.
4. Buyer confirms receipt ? marketplace releases payment to seller (minus commission).
5. Order marked COMPLETED ? both parties can rate.

### Failure Flow
1. Payment fails ? order stays PENDING_PAYMENT for 24 hours ? auto-cancelled.
2. Seller does not deliver within SLA ? buyer can cancel ? full refund issued.
3. Delivery fails ? order goes to DISPUTED ? support intervenes.

### Exception Cases
- EC-MW-001: Payment gateway timeout ? retry 3 times with exponential backoff ? email buyer to retry.
- EC-MW-002: Seller account suspended mid-order ? order auto-cancelled ? buyer fully refunded.
- EC-MW-003: System detects duplicate transaction ? block immediately ? notify finance team.

### Security Rules
- SR-MW-001: All sensitive data (PII, payment info) must be encrypted at rest (AES-256) and in transit (TLS 1.3).
- SR-MW-002: Payment card data must never be stored on platform servers; use PCI-DSS Level 1 tokenization.
- SR-MW-003: Session tokens expire after 30 minutes of inactivity.

### Performance Rules
- PR-MW-001: Order creation API must respond within 2 seconds at P95 under 1,000 concurrent users.
- PR-MW-002: Marketplace homepage must load within 1.5 seconds on a 4G connection.
- PR-MW-003: Search queries must return results within 500ms at P99.

### Acceptance Criteria
- AC-MW-001: A guest can register, browse, purchase, and receive a digital product within the platform.
- AC-MW-002: A seller can list, manage, deliver products, and withdraw earnings.
- AC-MW-003: Admin can view, moderate, and generate reports on all transactions.

### Definition of Done
- DoD-MW-001: All user roles can execute their primary workflows end-to-end.
- DoD-MW-002: All failure paths are handled with appropriate user-facing error messages.
- DoD-MW-003: Performance benchmarks are met under specified load conditions.

---

## 2. Buyer Journey

### Objective
Define every step, decision point, and interaction a buyer experiences from discovery to post-purchase.

### Business Rules
- BR-BJ-001: A buyer must register and verify their email address before placing an order.
- BR-BJ-002: A buyer may browse all public listings without authentication.
- BR-BJ-003: A buyer can add items to a cart without authentication, but must log in to checkout.
- BR-BJ-004: A buyer's cart expires after 7 days of inactivity.
- BR-BJ-005: A buyer can purchase a maximum of 10 copies of the same digital product per single order.
- BR-BJ-006: A buyer can request a refund within 14 days of purchase for undelivered or defective products.
- BR-BJ-007: A buyer must verify their phone number before their first purchase exceeding .
- BR-BJ-008: A buyer's account is auto-flagged if they open more than 5 disputes in a 30-day rolling window.
- BR-BJ-009: A buyer must provide a reason and evidence for any refund request.
- BR-BJ-010: A buyer can delete their account only if they have no active orders or pending disputes.

### Validation Rules
- VR-BJ-001: Email format must comply with RFC 5322.
- VR-BJ-002: Phone number must include country code and be validated via OTP.
- VR-BJ-003: Buyer must be 18 years or older (verified via date of birth).

### Preconditions
- PC-BJ-001: Buyer has a registered and verified account.
- PC-BJ-002: Product is in PUBLISHED status.
- PC-BJ-003: Seller account is ACTIVE and not SUSPENDED.

### Postconditions
- PO-BJ-001: Buyer receives a digital receipt via email.
- PO-BJ-002: Order is created in PENDING_PAYMENT status.
- PO-BJ-003: Buyer's purchase history is updated.

### Success Flow
1. Guest searches/browses marketplace ? views product page.
2. Guest registers ? email verified ? becomes Buyer.
3. Buyer adds product to cart ? proceeds to checkout.
4. Buyer completes payment ? order created.
5. Buyer receives digital asset ? confirms delivery.
6. Buyer leaves review and rating.

### Failure Flow
1. Payment declined ? buyer notified with reason ? retry offered.
2. Product not delivered within SLA ? buyer opens dispute.
3. Invalid/expired coupon ? error shown ? buyer can continue without coupon.

### Exception Cases
- EC-BJ-001: Buyer's session expires during checkout ? cart preserved ? prompt to re-login.
- EC-BJ-002: Product removed by seller while in buyer's cart ? notification shown on checkout.
- EC-BJ-003: Price changed between add-to-cart and checkout ? buyer must accept new price.

### Security Rules
- SR-BJ-001: Passwords must meet complexity requirements (min 8 chars, upper, lower, digit).
- SR-BJ-002: Failed login attempts > 5 in 15 minutes ? account locked for 30 minutes.
- SR-BJ-003: Payment pages must be PCI-DSS compliant.

### Performance Rules
- PR-BJ-001: Checkout page load time < 2 seconds.
- PR-BJ-002: Product search results returned within 300ms.
- PR-BJ-003: Order confirmation email delivered within 60 seconds of payment success.

### Acceptance Criteria
- AC-BJ-001: Buyer can complete full purchase cycle from browse to delivery confirmation.
- AC-BJ-002: Buyer can view order history and download invoices.
- AC-BJ-003: Buyer can initiate and track refund/dispute requests.

### Definition of Done
- DoD-BJ-001: All buyer-facing pages are responsive across mobile, tablet, and desktop.
- DoD-BJ-002: All validation rules produce clear user-facing error messages.
- DoD-BJ-003: Performance SLAs are verified through automated load testing.

---

## 3. Seller Journey

### Objective
Define the complete lifecycle of a seller from registration through listing, selling, earning, and growth on the platform.

### Business Rules
- BR-SJ-001: A seller must register as a buyer first, then apply for seller status.
- BR-SJ-002: A seller must provide valid government-issued ID, tax ID, and business documentation (if applicable).
- BR-SJ-003: A seller's first 5 product listings are subject to manual review by a Moderator.
- BR-SJ-004: A seller can list a maximum of 50 products in their first 30 days (probationary period).
- BR-SJ-005: A seller must maintain a minimum 4.0 average rating to remain in good standing.
- BR-SJ-006: A seller with rating below 3.5 for 30 consecutive days is auto-suspended.
- BR-SJ-007: A seller must respond to buyer messages within 24 hours.
- BR-SJ-008: A seller must deliver digital products within the SLA defined for their product category.
- BR-SJ-009: A seller's earnings are held in escrow for 7 days after order completion before becoming available for withdrawal.
- BR-SJ-010: A seller can withdraw earnings only to a verified bank account or mobile wallet.
- BR-SJ-011: A seller's account is subject to fee structure based on their tier (Basic: 15%, Pro: 10%, Enterprise: 7%).
- BR-SJ-012: A seller may not list products that violate intellectual property rights of third parties.
- BR-SJ-013: A seller must accept the marketplace's terms and fee structure before activating their seller account.
- BR-SJ-014: A seller can offer custom bundles, but the bundle price must be at least 10% less than the sum of individual items.
- BR-SJ-015: A seller cannot purchase their own products or use alternate accounts to inflate sales.

### Validation Rules
- VR-SJ-001: Tax ID format must match the issuing country's standard format.
- VR-SJ-002: Bank account IBAN (if applicable) must pass checksum validation.
- VR-SJ-003: Product description must be between 100 and 10,000 characters.
- VR-SJ-004: Product price must be between .00 and ,000.00.
- VR-SJ-005: Product file size must not exceed 5 GB.

### Preconditions
- PC-SJ-001: User has an active BUYER account in good standing.
- PC-SJ-002: User has completed KYC verification at the basic level.
- PC-SJ-003: User has accepted the Seller Agreement and Fee Schedule.

### Postconditions
- PO-SJ-001: Seller account is created in PENDING_VERIFICATION status.
- PO-SJ-002: Seller dashboard is accessible with analytics.
- PO-SJ-003: First 5 products are queued for manual moderation.

### Success Flow
1. Buyer applies for seller status ? submits KYC documents.
2. Admin reviews documents ? approves ? seller is ACTIVE.
3. Seller creates product listing ? includes description, price, files.
4. Product is approved (auto or manual) ? goes LIVE.
5. Buyer purchases ? seller delivers ? payment held in escrow.
6. Buyer confirms ? funds released minus commission.
7. Seller withdraws earnings to verified bank account.

### Failure Flow
1. KYC documents rejected ? seller notified with reason ? can resubmit up to 3 times.
2. Product rejected during moderation ? seller notified with reason ? can edit and resubmit.
3. Seller fails to deliver on time ? dispute opened ? possible forced refund.

### Exception Cases
- EC-SJ-001: Seller's bank account verification fails ? earnings held until valid account provided.
- EC-SJ-002: Seller's product flagged for IP infringement ? immediate takedown ? account review.
- EC-SJ-003: Seller closes account with pending orders ? orders auto-completed ? funds held for 180 days.

### Security Rules
- SR-SJ-001: Seller documents must be stored encrypted (AES-256) with access limited to authorized Moderators.
- SR-SJ-002: Seller bank account details must never be exposed via APIs.
- SR-SJ-003: All seller communication with buyers must be logged and retained for 3 years.

### Performance Rules
- PR-SJ-001: Seller dashboard loads within 2 seconds.
- PR-SJ-002: Product creation form submits within 1 second.
- PR-SJ-003: Product search indexing is updated within 60 seconds of listing approval.

### Acceptance Criteria
- AC-SJ-001: Seller can complete application, get verified, list a product, make a sale, and withdraw earnings.
- AC-SJ-002: Seller receives timely notifications for orders, disputes, and policy changes.
- AC-SJ-003: Seller can view real-time analytics (sales, views, earnings).

### Definition of Done
- DoD-SJ-001: Complete seller onboarding flow is tested end-to-end.
- DoD-SJ-002: All revenue-related calculations are verified against test scenarios.
- DoD-SJ-003: Automated alerts for policy violations are operational.

---

## 4. Admin Journey

### Objective
Define the full administrative workflow for managing users, products, orders, finance, disputes, and platform operations.

### Business Rules
- BR-AJ-001: An administrator is appointed only by a Super Administrator.
- BR-AJ-002: All admin actions must be logged with timestamp, admin ID, action type, and before/after state.
- BR-AJ-003: An administrator cannot modify their own account role or permissions.
- BR-AJ-004: Administrators must use hardware-based 2FA (TOTP or security key).
- BR-AJ-005: An administrator's session expires after 15 minutes of inactivity.
- BR-AJ-006: Administrators cannot view full payment card numbers or passwords.
- BR-AJ-007: All bulk operations (mass suspend, mass delete) require secondary admin approval.
- BR-AJ-008: An administrator can impersonate a buyer or seller only in read-only mode; all actions are logged.
- BR-AJ-009: An administrator must document the reason for every manual intervention.
- BR-AJ-010: Daily, weekly, and monthly automated reports must be generated.
- BR-AJ-011: An administrator cannot approve their own product listing or seller application.
- BR-AJ-012: Emergency shutdown of the marketplace requires dual admin authentication.

### Validation Rules
- VR-AJ-001: Admin email domain must be @tsbl.com or a verified corporate domain.
- VR-AJ-002: Admin passwords must be at least 12 characters with complexity requirements.
- VR-AJ-003: Admin 2FA must be verified every 30 days.

### Preconditions
- PC-AJ-001: Admin has been onboarded and assigned a role by Super Administrator.
- PC-AJ-002: Admin has completed security awareness training.
- PC-AJ-003: Admin has configured 2FA.

### Postconditions
- PO-AJ-001: Every admin action is recorded in immutable audit log.
- PO-AJ-002: Platform state is updated according to admin action.
- PO-AJ-003: Relevant notifications are dispatched to affected users.

### Success Flow
1. Admin logs in with credentials + 2FA.
2. Admin accesses dashboard ? reviews pending items.
3. Admin takes action (approve/reject/escalate).
4. System logs action ? dispatches notifications.
5. Admin generates report ? reviews platform KPIs.

### Failure Flow
1. Admin credentials compromised ? immediate forced logout across all sessions.
2. Admin action violates business rule ? system blocks action with explanation.
3. Admin attempts unauthorized operation ? access denied ? logged.

### Exception Cases
- EC-AJ-001: Only one Super Administrator is available ? emergency escalation process.
- EC-AJ-002: Bulk operation initiated by mistake ? reversal requires Super Admin approval.
- EC-AJ-003: Admin account inactive for 90 days ? auto-disabled ? requires Super Admin to reactivate.

### Security Rules
- SR-AJ-001: Admin console accessible only from whitelisted IP ranges.
- SR-AJ-002: All admin API calls require JWT + API key + 2FA session token.
- SR-AJ-003: Admin audit logs are immutable and write-once-read-many (WORM).
- SR-AJ-004: Failed admin login attempts > 3 in 15 minutes ? account locked, Super Admin notified.

### Performance Rules
- PR-AJ-001: Admin dashboard loads within 2 seconds.
- PR-AJ-002: Bulk operations (up to 1,000 users) complete within 30 seconds.
- PR-AJ-003: Report generation completes within 5 minutes for data up to 1 year.

### Acceptance Criteria
- AC-AJ-001: Admin can perform all user, product, order, and finance management operations.
- AC-AJ-002: Admin receives timely alerts for platform anomalies and policy violations.
- AC-AJ-003: All admin actions are auditable with complete before/after snapshots.

### Definition of Done
- DoD-AJ-001: Admin console covers all required workflows.
- DoD-AJ-002: Audit trail is verified for completeness and immutability.
- DoD-AJ-003: 2FA enforcement is verified through penetration testing.

---

## 5. Product Lifecycle

### Objective
Define the complete lifecycle of a digital product listing from draft to retirement.

### Business Rules
- BR-PL-001: A product goes through these states: DRAFT ? PENDING_REVIEW ? PUBLISHED ? SUSPENDED ? ARCHIVED.
- BR-PL-002: A product in DRAFT state is visible only to the seller.
- BR-PL-003: A product in PENDING_REVIEW state cannot be edited by the seller.
- BR-PL-004: Significant changes (price > 20%, category change) trigger a re-review.
- BR-PL-005: A product auto-archives after 180 days of zero sales.
- BR-PL-006: A product must have at least 3 high-resolution preview images.
- BR-PL-007: A product must be assigned to exactly one leaf category.
- BR-PL-008: A product can have a maximum of 5 tags.
- BR-PL-009: Digital products cannot be returned; refunds are at seller/marketplace discretion.
- BR-PL-010: A seller cannot delete a product with active orders; must archive instead.
- BR-PL-011: A product's version history must be maintained for audit purposes.
- BR-PL-012: Products with zero inventory are auto-hidden from search.
- BR-PL-013: A product flagged by 3 or more unique users is auto-suspended pending admin review.
- BR-PL-014: Product pricing must be in the marketplace's base currency.
- BR-PL-015: A seller can duplicate a product only up to 3 times.

### Validation Rules
- VR-PL-001: Product title: 10–200 characters.
- VR-PL-002: Product description: 100–10,000 characters.
- VR-PL-003: Price: .00–,000.00 (inclusive).
- VR-PL-004: Preview images: 2 MB max each, JPG/PNG/WebP only.
- VR-PL-005: Product file: 5 GB max; must pass malware scan.
- VR-PL-006: License keys: must be unique per product per seller.

### Preconditions
- PC-PL-001: Seller account is ACTIVE and not under review.
- PC-PL-002: Seller has remaining listing slots per their tier.
- PC-PL-003: Product category is not restricted for the seller's tier.

### Postconditions
- PO-PL-001: Product is visible/marketable per its state.
- PO-PL-002: Search index is updated.
- PO-PL-003: Seller inventory count is updated.
- PO-PL-004: Audit log entry created for the state transition.

### Success Flow
1. Seller creates product in DRAFT ? fills all required fields.
2. Seller submits for review ? product moves to PENDING_REVIEW.
3. Moderator reviews ? approves ? product moves to PUBLISHED.
4. Product appears in search ? buyers purchase.
5. Seller archives product (or auto-archive after 180 days no sales).
6. Product moves to ARCHIVED ? hidden from search.

### Failure Flow
1. Product rejected ? PENDING_REVIEW ? DRAFT ? seller notified with reason.
2. Product flagged by buyers ? SUSPENDED ? admin reviews.
3. Malware detected ? immediate SUSPENDED ? seller account flagged.

### Exception Cases
- EC-PL-001: Product file corrupted during upload ? seller must re-upload.
- EC-PL-002: Product violates policy retroactively ? immediate SUSPENDED.
- EC-PL-003: Seller deletes account ? all products auto-archived.

### Security Rules
- SR-PL-001: All uploaded product files must pass automated malware scanning.
- SR-PL-002: Product preview images must be sanitized (strip EXIF data).
- SR-PL-003: Product file storage must use encrypted at rest (AES-256).

### Performance Rules
- PR-PL-001: Product page loads within 2 seconds.
- PR-PL-002: Product search indexing within 60 seconds of state change.
- PR-PL-003: File upload supports resumable uploads for files > 100 MB.

### Acceptance Criteria
- AC-PL-001: Seller can create, edit, submit, and archive products.
- AC-PL-002: Moderator can review and approve/reject products.
- AC-PL-003: Product lifecycle states are correctly enforced and transitions are logged.

### Definition of Done
- DoD-PL-001: All state transitions are tested.
- DoD-PL-002: Malware scanning is integrated and verified.
- DoD-PL-003: Auto-archive mechanism is verified.

---

## 6. Order Lifecycle

### Objective
Define the complete lifecycle of an order from initiation to completion or cancellation.

### Business Rules
- BR-OL-001: An order progresses through: PENDING_PAYMENT ? PAID ? PROCESSING ? DELIVERED ? COMPLETED.
- BR-OL-002: An order can also reach: CANCELLED, REFUNDED, DISPUTED, or CHARGEBACK.
- BR-OL-003: An order in PENDING_PAYMENT auto-cancels after 24 hours.
- BR-OL-004: An order enters DISPUTED state if buyer initiates a dispute within 14 days of delivery.
- BR-OL-005: A cancelled order before payment capture incurs no charge.
- BR-OL-006: A cancelled order after payment capture triggers automatic refund.
- BR-OL-007: Each order must reference exactly one seller.
- BR-OL-008: An order cannot contain products from multiple sellers; split into sub-orders.
- BR-OL-009: Order total must match the sum of line items + tax + fees - discounts.
- BR-OL-010: A completed order auto-archives after 365 days.
- BR-OL-011: An order can be re-downloaded by the buyer for up to 365 days after completion.
- BR-OL-012: A seller can mark an order as DELIVERED only after uploading the digital file(s).
- BR-OL-013: The buyer has 7 days to confirm delivery; auto-confirm after 7 days if no dispute.
- BR-OL-014: All order state changes must emit domain events.
- BR-OL-015: Order IDs must be unique, sequential, and non-predictable.

### Validation Rules
- VR-OL-001: Order subtotal = sum(quantity × unit_price) for all line items.
- VR-OL-002: Discount amount = order subtotal.
- VR-OL-003: Tax amount calculated based on buyer's jurisdiction.
- VR-OL-004: Payment amount = subtotal + tax - discount + platform fee.

### Preconditions
- PC-OL-001: Buyer is authenticated and has a valid payment method.
- PC-OL-002: All products in order are in PUBLISHED status.
- PC-OL-003: Product price has not changed significantly (> 10%) since added to cart.
- PC-OL-004: Seller account is ACTIVE.

### Postconditions
- PO-OL-001: Payment is captured in escrow.
- PO-OL-002: Seller is notified of new order.
- PO-OL-003: Buyer's invoice is generated.
- PO-OL-004: Affiliate commission is recorded (if applicable).

### Success Flow
1. Buyer initiates checkout ? order created in PENDING_PAYMENT.
2. Payment processed successfully ? order moves to PAID.
3. Seller starts processing ? order moves to PROCESSING.
4. Seller uploads delivery files ? marks DELIVERED.
5. Buyer confirms receipt ? order moves to COMPLETED.
6. Escrow released to seller (minus commission) ? lifecycle ends.

### Failure Flow
1. Payment fails ? PENDING_PAYMENT ? buyer retries or auto-cancels in 24h.
2. Seller fails to deliver in SLA ? buyer opens dispute.
3. Buyer disputes delivery ? DISPUTED ? support mediates.

### Exception Cases
- EC-OL-001: Payment captured but system crashes ? reconciliation job resolves.
- EC-OL-002: Duplicate order due to network retry ? idempotency key prevents.
- EC-OL-003: Buyer's payment method fails ? notify with alternatives.

### Security Rules
- SR-OL-001: Order details visible only to buyer, seller, and authorized staff.
- SR-OL-002: Payment transaction IDs must be stored encrypted.
- SR-OL-003: Order cancellation requires authentication and rate limiting.

### Performance Rules
- PR-OL-001: Order creation API < 1 second P95.
- PR-OL-002: Order listing API (buyer) < 500ms P95.
- PR-OL-003: Invoice PDF generation < 3 seconds.

### Acceptance Criteria
- AC-OL-001: Buyer can place, track, and receive orders.
- AC-OL-002: Seller can view, process, and deliver orders.
- AC-OL-003: All state transitions are correctly enforced and logged.
- AC-OL-004: Cancellation and refund flows work correctly.

### Definition of Done
- DoD-OL-001: All order states and transitions are implemented and tested.
- DoD-OL-002: Payment reconciliation process is verified.
- DoD-OL-003: Idempotency for order creation is verified.

---

## 7. Escrow Workflow

### Objective
Define the rules governing the holding, management, and release of funds in escrow for marketplace transactions.

### Business Rules
- BR-EW-001: 100% of the payment amount (minus gateway fees) must be held in escrow.
- BR-EW-002: Funds released to seller only after buyer confirms delivery OR 7 days pass without dispute.
- BR-EW-003: In a dispute, funds remain in escrow until resolved.
- BR-EW-004: Dispute resolves in buyer's favor ? funds returned minus non-refundable fees.
- BR-EW-005: Dispute resolves in seller's favor ? funds released minus commission.
- BR-EW-006: Escrow must use a segregated bank account.
- BR-EW-007: Escrow releases occur within 24 hours of the triggering event.
- BR-EW-008: Partial releases not supported; funds released in full or not at all.
- BR-EW-009: Escrow account must be reconciled daily against the order ledger.
- BR-EW-010: Discrepancy > 0.1% triggers alert to Finance Manager.
- BR-EW-011: Escrow release must include marketplace commission deduction.

### Validation Rules
- VR-EW-001: Escrow balance must equal sum of all active order payments.
- VR-EW-002: Release amount = order total minus commission minus fees.
- VR-EW-003: Escrow account identifier unique per order.

### Preconditions
- PC-EW-001: Payment has been successfully captured.
- PC-EW-002: Order is in PAID or later state.
- PC-EW-003: Valid escrow wallet exists.

### Postconditions
- PO-EW-001: Seller's available balance increased.
- PO-EW-002: Buyer's payment is final (or reversed for refund).
- PO-EW-003: Escrow balance reduced.
- PO-EW-004: Transaction recorded in financial ledger.

### Success Flow
1. Buyer pays ? funds held in escrow wallet.
2. Seller delivers ? buyer confirms (or 7 days pass).
3. Commission calculated ? deducted.
4. Net amount released to seller's wallet.
5. Escrow balance updated ? transaction logged.

### Failure Flow
1. Escrow release fails ? retried (max 3) ? manual intervention.
2. Reconciliation mismatch ? frozen ? finance investigates.
3. Gateway fails to capture ? order cancelled ? no escrow.

### Exception Cases
- EC-EW-001: Bank holiday delays release ? next business day.
- EC-EW-002: Regulatory freeze ? held until legal clearance.
- EC-EW-003: Negative escrow balance ? marketplace covers from operational account.

### Security Rules
- SR-EW-001: Escrow system isolated from main application network.
- SR-EW-002: Manual overrides require dual authorization.
- SR-EW-003: Escrow API restricted to internal services.
- SR-EW-004: Transaction logs immutable.

### Performance Rules
- PR-EW-001: Escrow release batch processes 10,000 transactions per minute.
- PR-EW-002: Balance query < 500ms.
- PR-EW-003: Daily reconciliation within 1 hour.

### Acceptance Criteria
- AC-EW-001: Funds held in escrow for every paid order.
- AC-EW-002: Funds released correctly on delivery confirmation or dispute resolution.
- AC-EW-003: Commission correctly deducted before release.

### Definition of Done
- DoD-EW-001: Escrow hold and release flows tested end-to-end.
- DoD-EW-002: Reconciliation process verified.
- DoD-EW-003: Dispute fund handling tested.
---

## 8. Wallet Workflow

### Objective
Define the rules governing user wallets for storing, managing, and transacting marketplace funds.

### Business Rules
- BR-WW-001: Every user (buyer and seller) has exactly one wallet.
- BR-WW-002: A wallet supports two balances: AVAILABLE and PENDING.
- BR-WW-003: PENDING balance includes funds from incomplete orders and escrow holds.
- BR-WW-004: A buyer can pre-load their wallet for faster checkout.
- BR-WW-005: A seller's wallet receives funds after escrow release minus commission.
- BR-WW-006: Minimum withdrawal amount: .00.
- BR-WW-007: Maximum single withdrawal amount: ,000.00.
- BR-WW-008: A wallet cannot have a negative balance.
- BR-WW-009: Wallet transactions are recorded with running balance for audit.
- BR-WW-010: Wallet is automatically created when a user registers.
- BR-WW-011: Wallet can be frozen by admin action during fraud investigation.
- BR-WW-012: Wallet freeze prevents outgoing transactions; incoming accepted.
- BR-WW-013: Wallet statement covering up to 12 months can be generated on request.
- BR-WW-014: Wallets with zero balance and no activity for 365 days are DORMANT.
- BR-WW-015: Wallet-to-wallet transfers between users are not permitted.
- BR-WW-016: All wallet mutations require an associated reference.

### Validation Rules
- VR-WW-001: Withdrawal amount = .00 and = ,000.00.
- VR-WW-002: Withdrawal amount = available balance.
- VR-WW-003: Daily withdrawal limit per seller: ,000.00.
- VR-WW-004: Monthly withdrawal limit per seller: ,000.00.

### Preconditions
- PC-WW-001: User wallet exists and is not frozen.
- PC-WW-002: KYC level meets withdrawal requirements.
- PC-WW-003: No pending disputes against the user.

### Postconditions
- PO-WW-001: Wallet balance is updated.
- PO-WW-002: Transaction record is created.
- PO-WW-003: Ledger is updated.

### Success Flow
1. User earns or deposits funds.
2. Funds credited to wallet ? available balance increases.
3. User initiates withdrawal ? available reduced ? PENDING increased.
4. Withdrawal processed ? PENDING reduced.

### Failure Flow
1. Insufficient balance ? rejected.
2. Wallet frozen ? outgoing blocked ? user notified.
3. Unverified withdrawal method ? blocked.

### Exception Cases
- EC-WW-001: Duplicate withdrawal ? idempotency key blocks.
- EC-WW-002: Bank transfer fails ? funds returned to available.
- EC-WW-003: Balance discrepancy ? frozen pending investigation.

### Security Rules
- SR-WW-001: Wallet API rate limited (max 5 withdrawal requests/hour).
- SR-WW-002: Withdrawals > ,000 require 2FA.
- SR-WW-003: Wallet balance masked client-side.
- SR-WW-004: Wallet mutation must be atomic.

### Performance Rules
- PR-WW-001: Balance query < 200ms.
- PR-WW-002: History query (paginated) < 500ms.
- PR-WW-003: Withdrawal batch handles 5,000/minute.

### Acceptance Criteria
- AC-WW-001: Users can view balance and transaction history.
- AC-WW-002: Sellers can withdraw to verified accounts.
- AC-WW-003: Freeze/unfreeze works correctly.

### Definition of Done
- DoD-WW-001: Wallet creation and withdrawal flows tested.
- DoD-WW-002: All limits verified.

---

## 9. Payment Workflow

### Objective
Define rules for processing, handling, and reconciling payments.

### Business Rules
- BR-PW-001: Payment captured before digital asset delivered.
- BR-PW-002: Supported methods: Card, Mobile Wallet, Bank Transfer, PayPal.
- BR-PW-003: All payments via PCI-DSS Level 1 gateway.
- BR-PW-004: Gateway fees borne by marketplace.
- BR-PW-005: Payment retry: max 3 attempts with exponential backoff.
- BR-PW-006: Amount rounded to 2 decimal places.
- BR-PW-007: Currency conversion rates fixed at payment initiation (valid 15 min).
- BR-PW-008: Each payment requires unique idempotency key.
- BR-PW-009: Refunds processed to original payment method.
- BR-PW-010: Partial refunds supported only if gateway supports.
- BR-PW-011: Payment webhook delivered within 5 seconds.
- BR-PW-012: All failures logged with gateway error code.
- BR-PW-013: Stored payment methods use gateway tokenization.
- BR-PW-014: Payments above ,000 require 3D Secure/OTP.

### Validation Rules
- VR-PW-001: Amount must match order total exactly.
- VR-PW-002: Currency must be supported.
- VR-PW-003: Payment method must be active.
- VR-PW-004: Billing country must match gateway region.

### Preconditions
- PC-PW-001: Order in PENDING_PAYMENT state.
- PC-PW-002: All items valid and in stock.
- PC-PW-003: Gateway operational.

### Postconditions
- PO-PW-001: Payment captured in escrow.
- PO-PW-002: Order transitions to PAID.
- PO-PW-003: Seller notified, receipt generated.

### Success Flow
1. Buyer selects payment method ? system creates payment intent.
2. Gateway processes ? returns webhook.
3. System verifies webhook signature ? order PAID.
4. Escrow records funds.

### Failure Flow
1. Card declined ? buyer notified ? can retry.
2. 3DS fails ? payment aborted.
3. Gateway timeout ? retry ? max attempts ? order cancelled.

### Exception Cases
- EC-PW-001: Webhook delayed ? reconciliation resolves.
- EC-PW-002: Duplicate webhook ? idempotency rejects.
- EC-PW-003: Zombie payment ? auto-refund in 24h.

### Security Rules
- SR-PW-001: Card data never touches app servers.
- SR-PW-002: All API calls over TLS 1.3.
- SR-PW-003: Webhook validation via HMAC-SHA256.

### Performance Rules
- PR-PW-001: Payment initiation < 1s P95.
- PR-PW-002: Webhook processing < 500ms P99.
- PR-PW-003: Reconciliation batch < 5 min.

### Acceptance Criteria
- AC-PW-001: All payment methods work.
- AC-PW-002: Failures handled gracefully.
- AC-PW-003: Webhooks processed idempotently.

### Definition of Done
- DoD-PW-001: All methods integrated and tested.
- DoD-PW-002: Webhook verification tested.

---

## 10. Refund Workflow

### Objective
Define rules for handling refund requests.

### Business Rules
- BR-RF-001: Refund request within 14 days of purchase.
- BR-RF-002: Reason: undelivered, defective, or materially different.
- BR-RF-003: Seller can voluntarily approve before dispute.
- BR-RF-004: No response in 48h ? auto-escalates to dispute.
- BR-RF-005: Refund = order total minus non-refundable gateway fees.
- BR-RF-006: One refund per order.
- BR-RF-007: Orders > 14 days require admin review.
- BR-RF-008: Downloaded digital products non-refundable unless defective.
- BR-RF-009: Activated license keys non-refundable.
- BR-RF-010: Marketplace may issue courtesy refund up to .
- BR-RF-011: >5 refunds in 6 months ? abuse review.
- BR-RF-012: Processing: 5-10 business days.
- BR-RF-013: Partial refunds for multi-item orders only.

### Validation Rules
- VR-RF-001: Valid completed order.
- VR-RF-002: Amount = original total.
- VR-RF-003: Reason = 20 characters.
- VR-RF-004: Within 14-day window.

### Preconditions
- PC-RF-001: Order COMPLETED or DISPUTED.
- PC-RF-002: No prior refund for this order.
- PC-RF-003: Gateway supports refunds.

### Postconditions
- PO-RF-001: Refund processed.
- PO-RF-002: Seller wallet debited if paid out.
- PO-RF-003: Order ? REFUNDED.
- PO-RF-004: Commission reversed.

### Success Flow
1. Buyer requests refund with reason.
2. Seller notified (48h to respond).
3. Seller approves ? system processes refund.
4. Buyer receives funds ? order REFUNDED.

### Failure Flow
1. Seller contests ? escalated to dispute.
2. Gateway fails ? manual processing.
3. Outside window ? auto-rejected.

### Security Rules
- SR-RF-001: Auth + audit required.
- SR-RF-002: Bulk refunds require dual admin.
- SR-RF-003: Rate limited (10/hour per buyer).

### Acceptance Criteria
- AC-RF-001: Buyer can initiate refund.
- AC-RF-002: Seller can approve/contest.
- AC-RF-003: Refund reaches original method.

### Definition of Done
- DoD-RF-001: Full flow tested.
- DoD-RF-002: Abuse detection verified.

---

## 11. Withdrawal Workflow

### Objective
Define rules for sellers to withdraw earned funds.

### Business Rules
- BR-WD-001: Only AVAILABLE balance can be withdrawn.
- BR-WD-002: Minimum: .00. Maximum: ,000.00.
- BR-WD-003: Verified withdrawal method required.
- BR-WD-004: Methods: Bank Transfer, Mobile Wallet, PayPal.
- BR-WD-005: Method verification via micro-deposit or OTP.
- BR-WD-006: Processing: Bank 1-3 days, Wallet 24h, PayPal 24-48h.
- BR-WD-007: Fees: Bank .00, Wallet .50, PayPal 2% (cap ).
- BR-WD-008: Scheduling: daily/weekly/monthly with threshold.
- BR-WD-009: New bank account: 7-day cooling period.
- BR-WD-010: Cancellation within 1 hour of request.
- BR-WD-011: Batch processing at 02:00 UTC daily.
- BR-WD-012: KYC Level 1: /day, Level 2: ,000/day, Level 3: ,000/day.

### Validation Rules
- VR-WD-001: Amount between min and max.
- VR-WD-002: Available = amount + fee.
- VR-WD-003: Method verified.
- VR-WD-004: Daily limit not exceeded.

### Preconditions
- PC-WD-001: KYC Level 1 minimum.
- PC-WD-002: Verified withdrawal method.
- PC-WD-003: Available = .00.
- PC-WD-004: Account ACTIVE.

### Postconditions
- PO-WD-001: Withdrawal created PENDING.
- PO-WD-002: Available reduced.
- PO-WD-003: Record created.

### Success Flow
1. Seller selects method ? enters amount.
2. System validates limits ? confirms.
3. Batch processes ? payment sent.
4. Seller receives funds.

### Failure Flow
1. Insufficient balance ? rejected.
2. Limit exceeded ? rejected.
3. Processor rejects ? funds returned.

### Security Rules
- SR-WD-001: Method changes require 2FA.
- SR-WD-002: New method: 7-day cooling.
- SR-WD-003: 3 requests/hour rate limit.

### Acceptance Criteria
- AC-WD-001: Withdrawal request works.
- AC-WD-002: Limits enforced.
- AC-WD-003: Batch processes correctly.

### Definition of Done
- DoD-WD-001: Full flow tested.
- DoD-WD-002: Failures handled.

---

## 12. Coupon Workflow

### Objective
Define rules for creating, managing, and redeeming coupons.

### Business Rules
- BR-CP-001: Admin (platform) or Seller (product/store) can create.
- BR-CP-002: Types: PERCENTAGE, FIXED_AMOUNT.
- BR-CP-003: Start and end date required.
- BR-CP-004: Max discount: 50% (seller), 80% (platform).
- BR-CP-005: Minimum order value configurable.
- BR-CP-006: Max redemptions (total and per user).
- BR-CP-007: Code must be unique.
- BR-CP-008: Format: alphanumeric, 6-20 chars, case-insensitive.
- BR-CP-009: One coupon per order.
- BR-CP-010: Can restrict to products/categories/segments.
- BR-CP-011: Discounted price = .50.
- BR-CP-012: Discount applied before tax.
- BR-CP-013: Seller bears 100% of seller-coupon cost.
- BR-CP-014: Platform coupon: marketplace 50%, seller 50%.

### Validation Rules
- VR-CP-001: % discount within range.
- VR-CP-002: Fixed amount: -.
- VR-CP-003: Code unique, 6-20 chars.
- VR-CP-004: End > start date.

### Preconditions
- PC-CP-001: Creator has permission.
- PC-CP-002: Date range valid.
- PC-CP-003: Redemption limit not reached.

### Postconditions
- PO-CP-001: Order total reduced.
- PO-CP-002: Redemption count incremented.

### Success Flow
1. Coupon created ? validated ? activated.
2. Buyer applies at checkout.
3. System validates ? discount applied.

### Failure Flow
1. Expired ? error.
2. Limit reached ? error.
3. Below minimum ? error.

### Security Rules
- SR-CP-001: Rate limited (10 checks/min/user).
- SR-CP-002: Brute force detection.

### Acceptance Criteria
- AC-CP-001: All coupon types work.
- AC-CP-002: Limits enforced.
- AC-CP-003: Admin/seller creation works.

### Definition of Done
- DoD-CP-001: CRUD + redemption tested.

---

## 13. Affiliate Workflow

### Objective
Define rules for the affiliate marketing program.

### Business Rules
- BR-AF-001: Any verified user can be affiliate.
- BR-AF-002: Unique referral link per affiliate.
- BR-AF-003: Commission on first purchase within 30 days of click.
- BR-AF-004: Rate: 5% of subtotal (after discounts, before tax).
- BR-AF-005: Commission credited after order completed + refund period.
- BR-AF-006: Self-referral prohibited.
- BR-AF-007: Cookie lasts 30 days.
- BR-AF-008: Last-click attribution.
- BR-AF-009: Min payout: .00.
- BR-AF-010: Fraud detection on clicks.
- BR-AF-011: Inactive after 180 days zero referrals.

### Validation Rules
- VR-AF-001: Valid marketplace URL.
- VR-AF-002: Unique affiliate ID in link.
- VR-AF-003: Non-bot user agent.

### Preconditions
- PC-AF-001: Affiliate ACTIVE.
- PC-AF-002: Referred buyer is new.
- PC-AF-003: Click within 30-day window.

### Postconditions
- PO-AF-001: Commission PENDING.
- PO-AF-002: Analytics updated.

### Success Flow
1. Affiliate shares link ? prospect clicks.
2. Prospect registers + purchases.
3. Order completed ? commission credited.

### Failure Flow
1. Not new user ? no commission.
2. Return ? commission reversed.

### Security Rules
- SR-AF-001: UUID referral IDs.
- SR-AF-002: 2FA for payout changes.
- SR-AF-003: Hourly click fraud detection.

### Acceptance Criteria
- AC-AF-001: Links generated, tracked, paid.
- AC-AF-002: Fraud detection works.

### Definition of Done
- DoD-AF-001: Full flow tested.

---

## 14. Review Workflow

### Objective
Define rules for creating and managing product reviews.

### Business Rules
- BR-RV-001: Only verified purchasers can review.
- BR-RV-002: One review per product per buyer.
- BR-RV-003: Min 50 characters.
- BR-RV-004: Editable within 48h.
- BR-RV-005: Seller can respond once.
- BR-RV-006: Verified Purchase badge.
- BR-RV-007: Profanity auto-filtered.
- BR-RV-008: Admin can remove with reason.
- BR-RV-009: Review removal audit logged.
- BR-RV-010: >5 reviews from same IP in 1h = spam flagged.

### Validation Rules
- VR-RV-001: 50-5000 characters.
- VR-RV-002: Rating 1-5 integer.
- VR-RV-003: Completed order required.
- VR-RV-004: Unique per buyer+product.

### Preconditions
- PC-RV-001: Completed order.
- PC-RV-002: No prior review.

### Postconditions
- PO-RV-001: Average rating recalculated.
- PO-RV-002: Review visible.

### Success Flow
1. Buyer writes review ? profanity filter.
2. Passes ? published with badge.
3. Rating recalculated.

### Failure Flow
1. Profanity detected ? blocked.
2. Duplicate ? error.

### Security Rules
- SR-RV-001: Rate limited (5/hour).
- SR-RV-002: Configurable profanity filter.

### Acceptance Criteria
- AC-RV-001: Create, edit, respond.
- AC-RV-002: Filter blocks abuse.

### Definition of Done
- DoD-RV-001: Full flow tested.

---

## 15. Rating Workflow

### Objective
Define rules for calculating and managing ratings.

### Business Rules
- BR-RT-001: 1-5 star scale (integer).
- BR-RT-002: Product rating = average of verified ratings.
- BR-RT-003: Seller rating = average across all products.
- BR-RT-004: Only COMPLETED orders counted.
- BR-RT-005: Buyers with <3 purchases weighted at 0.5.
- BR-RT-006: Min 3 ratings to display average.
- BR-RT-007: Distribution displayed.
- BR-RT-008: Real-time recalculation.
- BR-RT-009: Admin can override displayed rating.
- BR-RT-010: Outliers beyond 3s excluded.

### Validation Rules
- VR-RT-001: Value 1-5 integer.
- VR-RT-002: Unique per buyer+product.

### Preconditions
- PC-RT-001: Completed order.
- PC-RT-002: Verified purchase.

### Postconditions
- PO-RT-001: Rating recalculated.
- PO-RT-002: Distribution updated.

### Success Flow
1. Buyer submits rating.
2. System validates ? applies weight.
3. Average recalculated.

### Exception Cases
- EC-RT-001: Manipulation detected ? hidden.
- EC-RT-002: Admin override with badge.

### Security Rules
- SR-RT-001: Detection runs every 6h.
- SR-RT-002: 5 submissions/hour/IP.

### Acceptance Criteria
- AC-RT-001: Correct calculation.
- AC-RT-002: Threshold enforced.

### Definition of Done
- DoD-RT-001: Formula verified.

---

## 16. Messaging Workflow

### Objective
Define rules for direct messaging between buyers and sellers.

### Business Rules
- BR-MS-001: Messages only between users with order relationship.
- BR-MS-002: Pre-sale inquiry if seller enables.
- BR-MS-003: All messages stored and auditable.
- BR-MS-004: Off-platform contact flagged.
- BR-MS-005: Profanity auto-filtered.
- BR-MS-006: Seller must respond within 24h.
- BR-MS-007: Messages immutable.
- BR-MS-008: Users can block others.
- BR-MS-009: Attachments max 10 MB (images, PDFs, archives).
- BR-MS-010: Read receipts tracked.
- BR-MS-011: Group messaging for disputes only.
- BR-MS-012: Retention: 3 years.

### Validation Rules
- VR-MS-001: 1-5000 characters.
- VR-MS-002: Attachments =10 MB, allowed types.
- VR-MS-003: 50 messages/hour/user max.

### Preconditions
- PC-MS-001: Both accounts ACTIVE.
- PC-MS-002: Sender not blocked.

### Postconditions
- PO-MS-001: Message stored.
- PO-MS-002: Notification sent.

### Success Flow
1. Buyer sends message.
2. Validated ? delivered.
3. Seller notified ? replies.

### Failure Flow
1. Blocked ? rejected.
2. Rate limit ? error.

### Security Rules
- SR-MS-001: Encrypted at rest.
- SR-MS-002: Malware scan on attachments.

### Acceptance Criteria
- AC-MS-001: Send, receive, read.
- AC-MS-002: Blocking works.

### Definition of Done
- DoD-MS-001: Full flow tested.

---

## 17. Notification Workflow

### Objective
Define rules for delivering notifications.

### Business Rules
- BR-NT-001: Channels: in-app, email, push.
- BR-NT-002: Per-category preferences.
- BR-NT-003: Transactional notifications mandatory.
- BR-NT-004: Marketing requires opt-in.
- BR-NT-005: Email retries 3× (5min, 15min, 1h).
- BR-NT-006: Critical sent immediately.
- BR-NT-007: Batch sent at user's preferred time.
- BR-NT-008: DND mode (1/4/8h).
- BR-NT-009: Max 10 marketing emails/week.
- BR-NT-010: Retention: 90 days in-app, 180 days email.
- BR-NT-011: Deep links included.
- BR-NT-012: System notifications bypass preferences.

### Preconditions
- PC-NT-001: User account active.
- PC-NT-002: Template exists.

### Postconditions
- PO-NT-001: Notification queued.
- PO-NT-002: Delivery tracked.

### Security Rules
- SR-NT-001: No PII in email subjects.
- SR-NT-002: Unsubscribe tokens signed.
- SR-NT-003: SPF, DKIM, DMARC configured.

### Acceptance Criteria
- AC-NT-001: All event types notified.
- AC-NT-002: Preferences respected.

### Definition of Done
- DoD-NT-001: All channels tested.

---

## 18. Dispute Workflow

### Objective
Define rules for handling disputes between buyers and sellers.

### Business Rules
- BR-DS-001: Open within 14 days of completion.
- BR-DS-002: States: OPEN ? UNDER_REVIEW ? RESOLVED/ESCALATED.
- BR-DS-003: Evidence due in 48h.
- BR-DS-004: Agent assigned within 4h.
- BR-DS-005: Resolution proposed within 72h.
- BR-DS-006: Rejection ? ESCALATED to Moderator.
- BR-DS-007: Moderator decision final.
- BR-DS-008: Types: FULL_REFUND, PARTIAL_REFUND, SELLER_WINS, COMPROMISE.
- BR-DS-009: Partial: 25%, 50%, 75%.
- BR-DS-010: Dispute fee  to losing party.
- BR-DS-011: Fee waived if buyer wins.
- BR-DS-012: >5 disputes in 6 months ? abuse flag.

### Validation Rules
- VR-DS-001: Reason 50-2000 chars.
- VR-DS-002: Max 5 files, 50 MB.

### Preconditions
- PC-DS-001: Order COMPLETED or DELIVERED.
- PC-DS-002: Within 14-day window.

### Postconditions
- PO-DS-001: Dispute created.
- PO-DS-002: Agent assigned.
- PO-DS-003: Funds held in escrow.

### Security Rules
- SR-DS-001: Evidence scanned.
- SR-DS-002: Agent conflicts checked.

### Acceptance Criteria
- AC-DS-001: Open, review, resolve, escalate.
- AC-DS-002: Funds handled correctly.

### Definition of Done
- DoD-DS-001: Full flow tested.

---

## 19. Support Ticket Workflow

### Objective
Define rules for support tickets (non-dispute).

### Business Rules
- BR-ST-001: Any user can create.
- BR-ST-002: Categories: ACCOUNT, PAYMENT, TECHNICAL, PRODUCT_REPORT, GENERAL.
- BR-ST-003: Priority: LOW, MEDIUM, HIGH, CRITICAL.
- BR-ST-004: SLA: CRITICAL <1h, HIGH <4h, MEDIUM <24h, LOW <72h.
- BR-ST-005: States: OPEN ? ASSIGNED ? IN_PROGRESS ? RESOLVED ? CLOSED.
- BR-ST-006: Auto-close after 7 days inactivity.
- BR-ST-007: Reopen within 14 days.
- BR-ST-008: Survey sent on closure.

### Preconditions
- PC-ST-001: User authenticated.
- PC-ST-002: Account ACTIVE.

### Postconditions
- PO-ST-001: Ticket created.
- PO-ST-002: Team notified.

### Success Flow
1. User creates ticket.
2. Auto-assigned ? agent responds.
3. Issue resolved ? closed ? survey.

### Security Rules
- SR-ST-001: Identity verification required.
- SR-ST-002: Internal notes encrypted.

### Acceptance Criteria
- AC-ST-001: CRUD tickets.
- AC-ST-002: SLA enforced.

### Definition of Done
- DoD-ST-001: Full lifecycle tested.

---

## 20. Seller Verification Workflow

### Objective
Define rules for verifying sellers.

### Business Rules
- BR-SV-001: Three levels: L1 (Basic), L2 (Standard), L3 (Premium).
- BR-SV-002: L1: government ID, selfie, phone.
- BR-SV-003: L2: L1 + tax ID, business license, bank account.
- BR-SV-004: L3: L2 + in-person/video verification, address, references.
- BR-SV-005: Validity: L1 1yr, L2 2yr, L3 3yr.
- BR-SV-006: Re-verification 30 days before expiry.
- BR-SV-007: Cannot list until L1 complete.
- BR-SV-008: Resubmit 3× max ? 90-day cooldown.
- BR-SV-009: Auto + manual review.
- BR-SV-010: Auto within 24h, manual within 48h.

### Preconditions
- PC-SV-001: BUYER account exists.
- PC-SV-002: Seller Agreement accepted.

### Postconditions
- PO-SV-001: Verification level assigned.
- PO-SV-002: Dashboard activated.

### Success Flow
1. Apply ? submit documents.
2. Auto-checks pass ? manual review.
3. Approved ? seller active.

### Security Rules
- SR-SV-001: Documents encrypted.
- SR-SV-002: Access limited.

### Acceptance Criteria
- AC-SV-001: All levels completable.
- AC-SV-002: Auto-checks validate.

### Definition of Done
- DoD-SV-001: All levels tested.

---

## 21. KYC Workflow

### Objective
Define Know Your Customer rules.

### Business Rules
- BR-KYC-001: Mandatory for sellers; buyers > cumulative.
- BR-KYC-002: Levels: 0 (unverified) through 3 (enhanced due diligence).
- BR-KYC-003: L1: name, DOB, government ID.
- BR-KYC-004: L2: L1 + proof of address.
- BR-KYC-005: L3: L2 + source of funds, PEP check, sanctions.
- BR-KYC-006: Valid 2 years.
- BR-KYC-007: Third-party verification service.
- BR-KYC-008: Failed 3× ? account restricted.
- BR-KYC-009: Sanctions screening (OFAC, UN, EU).
- BR-KYC-010: Expired KYC blocks withdrawals.

### Validation Rules
- VR-KYC-001: Name matches ID.
- VR-KYC-002: Age = 18.
- VR-KYC-003: Address doc = 3 months old.

### Preconditions
- PC-KYC-001: Account exists.
- PC-KYC-002: Consent given.

### Postconditions
- PO-KYC-001: Level updated.
- PO-KYC-002: Expiry set.

### Success Flow
1. Initiate ? upload docs.
2. Third-party verification.
3. Approved ? level active.

### Security Rules
- SR-KYC-001: Docs encrypted.
- SR-KYC-002: TLS 1.3.

### Acceptance Criteria
- AC-KYC-001: All levels work.
- AC-KYC-002: Sanctions screening.

### Definition of Done
- DoD-KYC-001: Full flow tested.

---

## 22. Product Approval Workflow

### Objective
Define rules for approving products before going live.

### Business Rules
- BR-PA-001: First 5 products per seller require manual review.
- BR-PA-002: After 5 approved + rating =4.0 ? auto-approve.
- BR-PA-003: Restricted categories always manual.
- BR-PA-004: Review within 24h (auto-approve if no response).
- BR-PA-005: Rejected can be resubmitted 3×.
- BR-PA-006: Checks: malware, IP, content policy.
- BR-PA-007: Price increase >50% or category change triggers re-review.

### Preconditions
- PC-PA-001: Seller L1+ verified.
- PC-PA-002: Product PENDING_REVIEW.
- PC-PA-003: All fields populated.

### Postconditions
- PO-PA-001: Product PUBLISHED or back to DRAFT.
- PO-PA-002: Search index updated.

### Success Flow
1. Submit ? malware/content checks.
2. Passes ? manual review (if required).
3. Approved ? PUBLISHED.

### Failure Flow
1. Malware ? rejected, account flagged.
2. Content violation ? rejected.

### Security Rules
- SR-PA-001: Up-to-date virus definitions.
- SR-PA-002: Auto-checks non-bypassable.

### Acceptance Criteria
- AC-PA-001: Auto/manual routing correct.
- AC-PA-002: Malware blocked.

### Definition of Done
- DoD-PA-001: Both paths tested.
---

## 23. Account Suspension Rules

### Objective
Define rules for suspending accounts due to violations or suspicious activity.

### Business Rules
- BR-AS-001: Suspension types: TEMPORARY (1-30 days) or PERMANENT.
- BR-AS-002: Temporary: policy violations, SLA breaches, suspicious activity.
- BR-AS-003: Permanent: fraud, IP infringement, illegal content, repeated violations.
- BR-AS-004: User notified with reason, duration, appeal process.
- BR-AS-005: During temporary: can log in, cannot transact.
- BR-AS-006: Permanent: cannot log in; orders cancelled with refunds.
- BR-AS-007: Suspended products hidden from search.
- BR-AS-008: Suspended withdrawals held.
- BR-AS-009: Appeal within 14 days; reviewed in 7 business days.
- BR-AS-010: Auto-suspension at fraud score =90.
- BR-AS-011: 3 temporary in 12 months ? permanent.
- BR-AS-012: Cannot create new accounts while suspended.
- BR-AS-013: Reinstatement after permanent requires Super Admin.

### Validation Rules
- VR-AS-001: Reason = 50 chars.
- VR-AS-002: Duration 1-30 days.

### Preconditions
- PC-AS-001: Evidence documented.
- PC-AS-002: Fraud score =90 for auto-suspension.

### Postconditions
- PO-AS-001: Account SUSPENDED.
- PO-AS-002: Orders on hold, products hidden.

### Success Flow
1. Violation detected ? evidence reviewed.
2. Suspension applied ? user notified.
3. Appeal window opened ? resolved.

### Security Rules
- SR-AS-001: Immutable audit trail.
- SR-AS-002: Only Moderators/Admins can suspend.
- SR-AS-003: Bulk suspension requires Super Admin.

### Acceptance Criteria
- AC-AS-001: Suspend, notify, appeal, reinstate.
- AC-AS-002: Duplicate account detection.

### Definition of Done
- DoD-AS-001: Full flow tested.

---

## 24. Fraud Detection Rules

### Objective
Define automated and manual rules for detecting fraud.

### Business Rules
- BR-FD-001: Scoring 0-100. =60: flag. =80: freeze. =90: suspend.
- BR-FD-002: Indicators: multiple accounts/IP, rapid creation, payment abuse, fake reviews, click fraud, identity mismatch.
- BR-FD-003: Real-time + batch checks.
- BR-FD-004: False positive rate <1%.
- BR-FD-005: ML model retrained monthly.
- BR-FD-006: Device fingerprinting.
- BR-FD-007: Geo-IP mismatch detection.
- BR-FD-008: New accounts <30 days + > ? additional verification.
- BR-FD-009: Same card 3+ accounts in 24h ? all frozen.
- BR-FD-010: Withdrawal fraud + chargeback ? permanent suspension.

### Validation Rules
- VR-FD-001: Valid IP format.
- VR-FD-002: Email not disposable domain.

### Preconditions
- PC-FD-001: System initialized with latest rules.
- PC-FD-002: Blacklists loaded.

### Postconditions
- PO-FD-001: Score calculated.
- PO-FD-002: Actions executed at thresholds.

### Success Flow
1. User action ? real-time check.
2. Score below threshold ? proceeds.
3. Background batch logs event.

### Failure Flow (Fraud)
1. Score exceeds threshold ? action blocked.
2. User can appeal.

### Security Rules
- SR-FD-001: Rules encrypted.
- SR-FD-002: Analysts certified annually.

### Acceptance Criteria
- AC-FD-001: Known fraud patterns blocked.
- AC-FD-002: False positive rate acceptable.

### Definition of Done
- DoD-FD-001: All indicators implemented.

---

## 25. Marketplace Commission Rules

### Objective
Define commission structure charged to sellers.

### Business Rules
- BR-MC-001: % of subtotal (after discounts, before tax).
- BR-MC-002: Tiers: Basic 15%, Pro 10%, Enterprise 7%, Partner 5%.
- BR-MC-003: Rate at time of order completion.
- BR-MC-004: Deducted before escrow release.
- BR-MC-005: Category adjustment: Software +2%, Fonts/Templates +1%.
- BR-MC-006: Promotional: 50% of standard rate.
- BR-MC-007: Commission refunded on buyer refund.
- BR-MC-008: Affiliate commissions paid by marketplace.
- BR-MC-009: Changes announced 30 days in advance.

### Validation Rules
- VR-MC-001: Rate 0-100%.
- VR-MC-002: Amount = subtotal.

### Preconditions
- PC-MC-001: Seller tier active.
- PC-MC-002: Order COMPLETED.

### Postconditions
- PO-MC-001: Commission deducted.
- PO-MC-002: Marketplace revenue credited.

### Success Flow
1. Order completed ? commission = subtotal × rate.
2. Category adjustment applied.
3. Deducted from escrow.

### Security Rules
- SR-MC-001: Rate override requires dual admin.
- SR-MC-002: Changes logged.

### Acceptance Criteria
- AC-MC-001: Correct calculation.
- AC-MC-002: Promotional works.

### Definition of Done
- DoD-MC-001: All tier/category combos tested.

---

## 26. Marketplace Fee Rules

### Objective
Define all additional fees beyond commission.

### Business Rules
- BR-MF-001: Listing fee: .00.
- BR-MF-002: Featured listing: /week.
- BR-MF-003: Withdrawal: Bank , Wallet .50, PayPal 2% (cap ).
- BR-MF-004: Dispute fee:  (losing party).
- BR-MF-005: Chargeback fee:  (seller if at fault).
- BR-MF-006: Currency conversion: 1%.
- BR-MF-007: Late delivery penalty: 1%/day, max 10%.
- BR-MF-008: No account maintenance or inactivity fee.

### Preconditions
- PC-MF-001: Action triggering fee initiated.

### Postconditions
- PO-MF-001: Fee applied.
- PO-MF-002: Ledger recorded.

### Security Rules
- SR-MF-001: Config changes require admin.
- SR-MF-002: Waivers require documented reason.

### Acceptance Criteria
- AC-MF-001: All fees calculated correctly.

### Definition of Done
- DoD-MF-001: All fee types tested.

---

## 27. Seller Ranking Algorithm

### Objective
Define algorithm for seller ranking in search results.

### Business Rules
- BR-SR-001: Score = Order Volume (15%) + Rating (25%) + Response Time (10%) + Completion Rate (20%) + Dispute Rate (15%) + Account Age (5%) + Verification Level (10%).
- BR-SR-002: Range: 0-1000.
- BR-SR-003: Recalculated daily at 00:00 UTC.
- BR-SR-004: Min 10 orders to be ranked.
- BR-SR-005: Suspension penalty: -200/day for past 90 days.
- BR-SR-006: Late delivery: -2 per late order.
- BR-SR-007: New seller boost: +50 for first 30 days.
- BR-SR-008: Top 10% = Top Rated Seller.
- BR-SR-009: Bayesian average for rating.
- BR-SR-010: Level multiplier: L1 1.0×, L2 1.1×, L3 1.2×.

### Validation Rules
- VR-SR-001: Weights sum to 100%.

### Preconditions
- PC-SR-001: Seller ACTIVE.
- PC-SR-002: =1 completed order.

### Postconditions
- PO-SR-001: Score updated.
- PO-SR-002: Badges recalculated.

### Security Rules
- SR-SR-001: Config read-only to non-admin.
- SR-SR-002: Manual overrides logged.

### Acceptance Criteria
- AC-SR-001: Score calculated correctly.

### Definition of Done
- DoD-SR-001: Formula verified.

---

## 28. Buyer Reputation Rules

### Objective
Define rules for buyer reputation tracking.

### Business Rules
- BR-BR-001: Start score: 100 (range 0-200).
- BR-BR-002: +5 per completed order (no dispute).
- BR-BR-003: -10 per dispute opened.
- BR-BR-004: -20 per dispute lost.
- BR-BR-005: -5 per refund request.
- BR-BR-006: Seller can block buyers with score <50.
- BR-BR-007: Score <30 ? abuse review.
- BR-BR-008: Score <20 ? blocked from purchasing.
- BR-BR-009: Recovery: +2 per 30 days positive activity.
- BR-BR-010: Tiers shown to sellers: EXCELLENT (150+), GOOD (100-149), FAIR (50-99), POOR (<50).

### Preconditions
- PC-BR-001: Buyer account exists.

### Postconditions
- PO-BR-001: Score updated.
- PO-BR-002: Tier recalculated.

### Acceptance Criteria
- AC-BR-001: Score calculated correctly.
- AC-BR-002: Restrictions enforced.

### Definition of Done
- DoD-BR-001: Verified with test scenarios.

---

## 29. Seller Reputation Rules

### Objective
Define rules for seller reputation and trust metrics.

### Business Rules
- BR-SR1-001: Start: 100 (range 0-200).
- BR-SR1-002: +2 per completed order.
- BR-SR1-003: -5 per late delivery.
- BR-SR1-004: -15 per dispute lost.
- BR-SR1-005: +5 per 5-star rating.
- BR-SR1-006: -10 per 1-star rating.
- BR-SR1-007: +10 for Top Rated Seller.
- BR-SR1-008: Score <50 ? quality watch.
- BR-SR1-009: Score <30 ? auto-suspended.
- BR-SR1-010: Recovery: +1 per 7 days positive.

### Preconditions
- PC-SR1-001: Seller ACTIVE.
- PC-SR1-002: =1 order.

### Postconditions
- PO-SR1-001: Score updated.
- PO-SR1-002: Quality watch triggered if needed.

### Acceptance Criteria
- AC-SR1-001: Score calculated.
- AC-SR1-002: Suspension works.

### Definition of Done
- DoD-SR1-001: Verified.

---

## 30. Search Ranking Rules

### Objective
Define algorithm for product search ranking.

### Business Rules
- BR-SCH-001: Score = Relevancy (40%) + Seller Rating (20%) + Sales Velocity (15%) + Product Age (10%) + Featured Boost (10%) + Affiliate Score (5%).
- BR-SCH-002: New products first 14 days: +10% boost.
- BR-SCH-003: Featured: +20% boost.
- BR-SCH-004: Zero sales in 30 days: -30%.
- BR-SCH-005: Sort options: relevance (default), price, rating, newest, best-selling.
- BR-SCH-006: Incomplete metadata: -10%.
- BR-SCH-007: Query normalization: case-insensitive, stemming, synonyms.
- BR-SCH-008: Personalized: repeat buyer category boost.

### Validation Rules
- VR-SCH-001: Query sanitized.
- VR-SCH-002: Product PUBLISHED.

### Preconditions
- PC-SCH-001: Index up to date (=60s).
- PC-SCH-002: Search cluster healthy.

### Postconditions
- PO-SCH-001: Results within SLA.
- PO-SCH-002: Analytics logged.

### Success Flow
1. Query normalized ? relevance scored.
2. Ranking factors applied.
3. Results returned.

### Failure Flow
1. Index down ? database fallback.
2. No results ? suggestions.

### Security Rules
- SR-SCH-001: Rate limited (60/min/IP).
- SR-SCH-002: No sensitive data exposed.

### Performance Rules
- PR-SCH-001: Results within 300ms P95.
- PR-SCH-002: Index updated within 60s.

### Acceptance Criteria
- AC-SCH-001: Relevant results returned.
- AC-SCH-002: Filters/sorting work.

### Definition of Done
- DoD-SCH-001: Algorithm verified.

---

## 31. Featured Product Rules

### Objective
Define rules for paid featured product placement.

### Business Rules
- BR-FP-001: Featured at top of search/category (first 3-5).
- BR-FP-002: /week per product.
- BR-FP-003: Max 3 featured products per seller.
- BR-FP-004: Rotates if multiple in same category.
- BR-FP-005: Min seller rating 3.5.
- BR-FP-006: Auto-renew opt-in.
- BR-FP-007: Cancel early ? prorated refund.
- BR-FP-008: Allocation: 60% highest bid, 40% best performing.
- BR-FP-009: Marketplace may use for internal promos.

### Preconditions
- PC-FP-001: Sufficient wallet balance.
- PC-FP-002: Product PUBLISHED.

### Postconditions
- PO-FP-001: Product FEATURED.
- PO-FP-002: Fee deducted.

### Acceptance Criteria
- AC-FP-001: Feature, cancel and refund work.

### Definition of Done
- DoD-FP-001: Full flow tested.

---

## 32. Trending Product Rules

### Objective
Define rules for determining trending products.

### Business Rules
- BR-TP-001: Score = 24h sales (40%) + 7d sales (30%) + 24h views (20%) + 7d reviews (10%).
- BR-TP-002: Recalculated every 6 hours.
- BR-TP-003: Min 10 sales in 7 days to qualify.
- BR-TP-004: Top 20 marketplace-wide, top 10 per category.
- BR-TP-005: Max 14 consecutive days in trending.
- BR-TP-006: New product boost: +20% for first 7 days.

### Preconditions
- PC-TP-001: Sufficient sales data.
- PC-TP-002: Engine operational.

### Postconditions
- PO-TP-001: List updated.
- PO-TP-002: Homepage reflects.

### Acceptance Criteria
- AC-TP-001: Correct identification.
- AC-TP-002: 14-day limit enforced.

### Definition of Done
- DoD-TP-001: Algorithm verified.

---

## 33. Flash Sale Rules

### Objective
Define rules for time-limited flash sales.

### Business Rules
- BR-FS-001: Created by Admin (platform) or Seller (product).
- BR-FS-002: Discount: 20%-70%.
- BR-FS-003: Duration: 1-72 hours.
- BR-FS-004: Max quantity per flash sale.
- BR-FS-005: Cannot combine with coupons.
- BR-FS-006: Max 1 flash sale per product per 30 days.
- BR-FS-007: Countdown timer displayed.
- BR-FS-008: Seller bears discount cost.
- BR-FS-009: Once sold out, discount ends early.

### Preconditions
- PC-FS-001: Seller has sufficient inventory.
- PC-FS-002: Product PUBLISHED.

### Postconditions
- PO-FS-001: Discount applied.
- PO-FS-002: Timer displayed.

### Acceptance Criteria
- AC-FS-001: Flash sale works within defined parameters.
- AC-FS-002: Auto-ends when sold out or time expires.

### Definition of Done
- DoD-FS-001: Full flow tested.

---

## 34. Promotion Rules

### Objective
Define rules for marketplace promotions and campaigns.

### Business Rules
- BR-PR-001: Admin creates promotions (category-wide, seasonal, holiday).
- BR-PR-002: Duration: 1-14 days.
- BR-PR-003: Discount: marketplace-funded (reduced commission) or seller-funded.
- BR-PR-004: Promo banner on homepage and category pages.
- BR-PR-005: Email campaign sent to opted-in users.
- BR-PR-006: Promo code auto-generated.
- BR-PR-007: Analytics tracked (impressions, conversions, revenue).
- BR-PR-008: Max 2 active promotions at any time.

### Preconditions
- PC-PR-001: Admin creates with parameters.
- PC-PR-002: Seller opt-in (if seller-funded).

### Postconditions
- PO-PR-001: Promotion active.
- PO-PR-002: Discounts applied.

### Acceptance Criteria
- AC-PR-001: Promotions creatable and display correctly.
- AC-PR-002: Analytics tracked.

### Definition of Done
- DoD-PR-001: Full flow tested.

---

## 35. Inventory Rules

### Objective
Define rules for managing digital product inventory.

### Business Rules
- BR-IN-001: Inventory tracked per product (digital copies, license keys).
- BR-IN-002: Inventory reduced by 1 per sale.
- BR-IN-003: Product hidden from search when inventory = 0.
- BR-IN-004: Seller can set threshold alert (default: 10 remaining).
- BR-IN-005: Pre-order allowed if seller enables.
- BR-IN-006: Seller can bulk upload license keys.
- BR-IN-007: License keys must be unique per product.
- BR-IN-008: Inventory audit daily against sales.
- BR-IN-009: Flash sale reserves inventory.
- BR-IN-010: Unlimited inventory option for non-license digital goods.

### Validation Rules
- VR-IN-001: Inventory = 0.
- VR-IN-002: License keys unique per seller+product.

### Preconditions
- PC-IN-001: Product PUBLISHED.
- PC-IN-002: License key file valid format.

### Postconditions
- PO-IN-001: Inventory decremented on sale.
- PO-IN-002: Alert sent at threshold.

### Acceptance Criteria
- AC-IN-001: Inventory correctly tracks sales.
- AC-IN-002: Zero inventory hides product.
- AC-IN-003: Threshold alerts work.

### Definition of Done
- DoD-IN-001: Inventory flows tested.
---

## 36. Digital Delivery Rules

### Objective
Define rules for delivering digital products to buyers.

### Business Rules
- BR-DD-001: Delivery methods: direct download, license key display, file access link.
- BR-DD-002: Delivery initiated automatically on payment confirmation.
- BR-DD-003: Download link expires after 7 days (extendable by seller).
- BR-DD-004: Max download attempts: 10 per order.
- BR-DD-005: Delivery SLA per category: standard 24h, express 6h.
- BR-DD-006: Seller must mark as DELIVERED after uploading files.
- BR-DD-007: Buyer notified via email + in-app on delivery.
- BR-DD-008: Download available for 365 days after purchase.
- BR-DD-009: Delivery files scanned for malware before release.
- BR-DD-010: Failed delivery auto-retries 3×, then escalates.

### Preconditions
- PC-DD-001: Order PAID.
- PC-DD-002: Files uploaded by seller.

### Postconditions
- PO-DD-001: Buyer can download.
- PO-DD-002: Order ? DELIVERED.

### Acceptance Criteria
- AC-DD-001: Files delivered successfully.
- AC-DD-002: Download limits enforced.

### Definition of Done
- DoD-DD-001: Delivery flows tested.

---

## 37. License Key Delivery Rules

### Objective
Define rules for license key product delivery.

### Business Rules
- BR-LK-001: License keys assigned automatically on payment confirmation.
- BR-LK-002: Keys displayed on order completion page and emailed.
- BR-LK-003: Keys revealed only after payment captured.
- BR-LK-004: Each key assigned to exactly one order.
- BR-LK-005: Bulk license file (CSV) upload supported.
- BR-LK-006: Key format validated (alphanumeric, pattern per product).
- BR-LK-007: Duplicate key detection across the platform.
- BR-LK-008: Revoked keys (by seller) flagged and not assignable.
- BR-LK-009: Key pool replenishment alert at 10 remaining.

### Validation Rules
- VR-LK-001: Key format matches product pattern.
- VR-LK-002: Key unique per seller+product.
- VR-LK-003: Pool > 0 to sell.

### Preconditions
- PC-LK-001: Product has key pool.
- PC-LK-002: Pool has available keys.

### Postconditions
- PO-LK-001: Key assigned to buyer.
- PO-LK-002: Pool decremented.

### Acceptance Criteria
- AC-LK-001: Keys assigned and delivered.
- AC-LK-002: Duplicate detection works.
- AC-LK-003: Revoked keys blocked.

### Definition of Done
- DoD-LK-001: Key lifecycle tested.

---

## 38. Digital File Delivery Rules

### Objective
Define rules for digital file delivery (non-license products).

### Business Rules
- BR-DF-001: Files uploaded by seller, stored encrypted.
- BR-DF-002: Max file size: 5 GB per product.
- BR-DF-003: File types allowed per category (configurable).
- BR-DF-004: Watermark preview for certain categories.
- BR-DF-005: Files delivered via secure download link (HTTPS).
- BR-DF-006: Download speed throttled to prevent abuse (max 50 MB/s).
- BR-DF-007: Corrupted files reported by buyer ? seller must re-upload.
- BR-DF-008: Version history maintained (buyer can download previous versions).
- BR-DF-009: Files purged 365 days after last download.

### Validation Rules
- VR-DF-001: File passes malware scan.
- VR-DF-002: File = 5 GB.
- VR-DF-003: Type in allowed list.

### Preconditions
- PC-DF-001: Product PUBLISHED.
- PC-DF-002: Seller uploaded file.

### Postconditions
- PO-DF-001: File available for download.
- PO-DF-002: Malware scan logged.

### Acceptance Criteria
- AC-DF-001: Upload, scan, deliver, download working.
- AC-DF-002: Version history accessible.

### Definition of Done
- DoD-DF-001: File lifecycle tested.

---

## 39. Currency Rules

### Objective
Define rules for currency handling on the marketplace.

### Business Rules
- BR-CU-001: Base currency: USD.
- BR-CU-002: Supported currencies: USD, BDT, EUR, GBP, CAD, AUD, INR, SGD, MYR.
- BR-CU-003: Exchange rates updated daily from reliable provider.
- BR-CU-004: Prices displayed in buyer's local currency (converted).
- BR-CU-005: All transactions settled in USD for escrow/release.
- BR-CU-006: Conversion fee: 1% of converted amount.
- BR-CU-007: Rate locked at payment initiation (valid 15 minutes).
- BR-CU-008: Sellers paid in their chosen currency.
- BR-CU-009: Currency selector persists across sessions.
- BR-CU-010: Rounding: 2 decimal places.
- BR-CU-011: Rate source: OpenExchangeRates or equivalent.

### Validation Rules
- VR-CU-001: Currency code ISO 4217.
- VR-CU-002: Rate > 0.

### Preconditions
- PC-CU-001: Rate source available.
- PC-CU-002: Currency enabled.

### Postconditions
- PO-CU-001: Amount converted.
- PO-CU-002: Fee applied.

### Acceptance Criteria
- AC-CU-001: Prices display in local currency.
- AC-CU-002: Conversion accurate.

### Definition of Done
- DoD-CU-001: Multi-currency flows tested.

---

## 40. Localization Rules

### Objective
Define rules for marketplace localization.

### Business Rules
- BR-LC-001: Supported locales: en-US, bn-BD, ar-SA, es-ES, fr-FR, de-DE, pt-BR, hi-IN.
- BR-LC-002: Locale detected from browser, user preference, or geo-IP.
- BR-LC-003: User can override locale in settings.
- BR-LC-004: All user-facing text externalized (i18n).
- BR-LC-005: Dates formatted per locale.
- BR-LC-006: Numbers/currencies formatted per locale.
- BR-LC-007: RTL support for Arabic.
- BR-LC-008: Legal texts (TOS, privacy) in user's locale.
- BR-LC-009: Translation coverage: 100% for core flows, 80% for admin.
- BR-LC-010: Community translations allowed (reviewed by admin).

### Validation Rules
- VR-LC-001: Locale code BCP 47 format.
- VR-LC-002: Translation key exists.

### Preconditions
- PC-LC-001: Locale pack loaded.

### Postconditions
- PO-LC-001: UI rendered in locale.
- PO-LC-002: Preference saved.

### Acceptance Criteria
- AC-LC-001: All supported locales render correctly.
- AC-LC-002: RTL works for Arabic.

### Definition of Done
- DoD-LC-001: All locales validated.

---

## 41. Tax Rules

### Objective
Define rules for tax calculation and remittance.

### Business Rules
- BR-TX-001: Tax calculated based on buyer's billing address jurisdiction.
- BR-TX-002: Supported tax types: VAT, GST, Sales Tax, HST.
- BR-TX-003: Digital goods tax rates per jurisdiction (configurable).
- BR-TX-004: Tax calculated after discounts, before commission.
- BR-TX-005: Marketplace responsible for tax remittance where applicable.
- BR-TX-006: Tax-exempt buyers (registered businesses) can upload VAT ID.
- BR-TX-007: Validated VAT ID exempts from tax.
- BR-TX-008: Tax amount displayed separately on invoice.
- BR-TX-009: Quarterly tax reports generated for finance.
- BR-TX-010: Tax rates updated from tax database.
- BR-TX-011: Zero-rated for digital exports per jurisdiction rules.

### Validation Rules
- VR-TX-001: Tax rate = 0%.
- VR-TX-002: VAT ID validated via VIES (EU).

### Preconditions
- PC-TX-001: Buyer jurisdiction determined.
- PC-TX-002: Tax rate configured.

### Postconditions
- PO-TX-001: Tax applied to order.
- PO-TX-002: Invoice generated with tax breakdown.

### Acceptance Criteria
- AC-TX-001: Correct tax calculated for buyer jurisdiction.
- AC-TX-002: VAT ID validation works.
- AC-TX-003: Tax-exempt flow works.

### Definition of Done
- DoD-TX-001: Tax calculation verified.

---

## 42. Invoice Rules

### Objective
Define rules for invoice generation and management.

### Business Rules
- BR-INV-001: Invoice generated for every completed order.
- BR-INV-002: Invoice includes: order ID, buyer/seller details, line items, subtotal, discount, tax, fees, total.
- BR-INV-003: Invoice format: PDF + HTML.
- BR-INV-004: Invoice stored for 7 years.
- BR-INV-005: Buyer can download invoice from order history.
- BR-INV-006: Seller can download invoice for their sales.
- BR-INV-007: Marketplace tax invoice for commission charged.
- BR-INV-008: Invoice number format: INV-YYYYMMDD-XXXXX (sequential).
- BR-INV-009: Refund generates credit note linked to original invoice.
- BR-INV-010: Company details (TSBL) on invoice: name, address, tax ID, reg number.

### Validation Rules
- VR-INV-001: Invoice total matches payment.
- VR-INV-002: Sequential number unique.

### Preconditions
- PC-INV-001: Order COMPLETED.
- PC-INV-002: Company details configured.

### Postconditions
- PO-INV-001: Invoice generated.
- PO-INV-002: Available for download.

### Acceptance Criteria
- AC-INV-001: Invoice generated with all required fields.
- AC-INV-002: Downloadable from order history.

### Definition of Done
- DoD-INV-001: Invoice generation tested.

---

## 43. Notification Priority Rules

### Objective
Define priority levels for notification delivery.

### Business Rules
- BR-NP-001: Priority levels: CRITICAL, HIGH, MEDIUM, LOW.
- BR-NP-002: CRITICAL: payment failure, account suspension, security alert. Sent immediately all channels.
- BR-NP-003: HIGH: order received, dispute opened, withdrawal processed. Sent within 1 minute.
- BR-NP-004: MEDIUM: product approved, review received, coupon expiring. Sent within 1 hour.
- BR-NP-005: LOW: weekly digest, marketing, policy updates. Sent in next batch.
- BR-NP-006: DND mode suppresses MEDIUM and LOW only.
- BR-NP-007: System notifications always bypass DND.

### Criteria
- AC-NP-001: Priorities correctly assigned.
- AC-NP-002: DND respected.

### Definition of Done
- DoD-NP-001: Priority mapping verified.

---

## 44. Permission Matrix

### Objective
Define permissions for each user role on the platform.

| Action | Guest | Buyer | Seller | Moderator | Support | Finance | Admin | Super Admin |
|--------|-------|-------|--------|-----------|---------|---------|-------|-------------|
| Browse marketplace | ? | ? | ? | ? | ? | ? | ? | ? |
| Register | ? | - | - | - | - | - | - | - |
| Purchase products | - | ? | ? | - | - | - | - | - |
| List products | - | - | ? | - | - | - | ? | ? |
| Manage own products | - | - | ? | - | - | - | - | - |
| Review/rate products | - | ? | ? | - | - | - | - | - |
| Message users | - | ?(buyer) | ?(seller) | ?(all) | ?(all) | - | ?(all) | ?(all) |
| View disputes | - | own | own | all | assigned | - | all | all |
| Resolve disputes | - | - | - | ? | ? | - | ? | ? |
| Verify sellers | - | - | - | ? | - | - | ? | ? |
| Suspend accounts | - | - | - | ? | - | - | ? | ? |
| Manage products (any) | - | - | - | ? | - | - | ? | ? |
| View finance reports | - | own | own | - | - | ? | ? | ? |
| Manage withdrawals | - | - | own | - | - | ? | ? | ? |
| Manage platform settings | - | - | - | - | - | - | - | ? |
| Manage admins | - | - | - | - | - | - | - | ? |
| View audit logs | - | - | - | ? | - | ? | ? | ? |
| API access | limited | full | full | full | full | full | full | full |

### Definition of Done
- DoD-PM-001: All roles have correct permissions assigned.

---

## 45. Role Matrix

### Objective
Define roles and their hierarchical structure.

| Role | Hierarchy | Reports To | Max Count |
|------|-----------|------------|-----------|
| Super Admin | 1 | - | 3 |
| Admin | 2 | Super Admin | 10 |
| Finance Manager | 3 | Admin | 5 |
| Moderator | 4 | Admin | 20 |
| Support Agent | 5 | Admin | 30 |
| Seller | 6 | - | Unlimited |
| Buyer | 7 | - | Unlimited |
| Guest | 8 | - | Unlimited |

### Definition of Done
- DoD-RM-001: Role hierarchy implemented.

---

## 46. Feature Access Matrix

### Objective
Define feature access per user role.

| Feature | Guest | Buyer | Seller | Mod | Support | Finance | Admin | Super Admin |
|---------|-------|-------|--------|-----|---------|---------|-------|-------------|
| Homepage | ? | ? | ? | ? | ? | ? | ? | ? |
| Search | ? | ? | ? | ? | ? | ? | ? | ? |
| Product Detail | ? | ? | ? | ? | ? | ? | ? | ? |
| Cart | ? | ? | ? | ? | ? | ? | ? | ? |
| Checkout | - | ? | ? | - | - | - | - | - |
| Order History | - | ? | ? | ? | ? | ? | ? | ? |
| Wallet | - | ? | ? | ? | ? | ? | ? | ? |
| Seller Dashboard | - | - | ? | - | - | - | ? | ? |
| Admin Console | - | - | - | ? | ? | ? | ? | ? |
| Analytics | - | - | ? | ? | ? | ? | ? | ? |
| Reports | - | - | limited | limited | limited | full | full | full |
| Settings | - | ? | ? | ? | ? | ? | ? | ? |
| Developer API | - | ? | ? | ? | ? | ? | ? | ? |

---

## 47. Business Validation Rules

### Objective
Define cross-cutting validation rules that span multiple modules.

- BR-BV-001: Email must be unique across all users.
- BR-BV-002: Username must be unique; alphanumeric + underscore only.
- BR-BV-003: Phone number must be unique if verified.
- BR-BV-004: A user cannot be both buyer and seller for the same transaction.
- BR-BV-005: Order total must never be negative.
- BR-BV-006: Discount amount must never exceed subtotal.
- BR-BV-007: Tax rate must be between 0% and 50%.
- BR-BV-008: Commission rate must be between 0% and 100%.
- BR-BV-009: Wallet balance must never be negative.
- BR-BV-010: Escrow balance must reconcile with active orders.
- BR-BV-011: Product price must be positive.
- BR-BV-012: Review text must be = 50 characters.
- BR-BV-013: Rating value must be integer 1-5.
- BR-BV-014: Date ranges must have end > start.
- BR-BV-015: File uploads must pass malware scan.
- BR-BV-016: Payment gateway webhooks must have valid HMAC signature.
- BR-BV-017: User session must be valid for protected actions.
- BR-BV-018: Idempotency key must be unique per payment.
- BR-BV-019: Currency amounts must be positive and within range.
- BR-BV-020: All monetary values stored as integer cents (avoid float).

---

## 48. Edge Cases

### Objective
Document edge cases and how the system handles them.

| Edge Case | Handling |
|-----------|----------|
| User registers with same email | Rejected: "Email already registered" |
| User deletes account with active orders | Blocked: "Resolve pending orders first" |
| Payment captured but server crashes before order update | Reconciliation job resolves within 5 min |
| Duplicate webhook from payment gateway | Idempotency key rejects duplicate |
| Seller tries to purchase own product | Blocked: "Cannot purchase own product" |
| Buyer and seller are same person (different accounts) | Flagged: fraud detection |
| Product malware scan takes > 30 min | Async: buyer notified when ready |
| Currency exchange rate changes during checkout | Rate locked for 15 min at initiation |
| Refund processed but payment gateway down | Queued: retry every hour for 24h |
| Withdrawal to deleted bank account | Failed: funds returned to wallet |
| User creates ticket while suspended | Allowed: suspension appeal needs support |
| Coupon code applied but then item removed from cart | Coupon removed: recalculate |
| Multiple tabs open doing concurrent actions | Optimistic locking (version column) |
| Bulk email sending hits rate limit | Queued: sends over 24h |
| Flash sale ends while item in cart | Price reverts: buyer notified |

---

## 49. Abuse Prevention Rules

### Objective
Define rules to prevent abuse of the marketplace.

- BR-AP-001: Rate limiting: 60 requests/min per IP for public APIs.
- BR-AP-002: Account creation rate limit: 3 per hour per IP.
- BR-AP-003: Login rate limit: 5 attempts per 15 min per account.
- BR-AP-004: Review submission: 5 per hour per user.
- BR-AP-005: Message sending: 50 per hour per user.
- BR-AP-006: Coupon attempt: 10 per min per user.
- BR-AP-007: Withdrawal request: 3 per hour per user.
- BR-AP-008: Dispute opening: 3 per day per user.
- BR-AP-009: CAPTCHA required after 3 failed login attempts.
- BR-AP-010: Disposable email domains blocked for registration.
- BR-AP-011: VPN/proxy detection for high-risk actions (payment, withdrawal).
- BR-AP-012: Device fingerprinting to detect multi-account abuse.
- BR-AP-013: IP blacklist updated hourly.
- BR-AP-014: Automated bot detection (behavioral analysis).
- BR-AP-015: Content scraping prevention: rate limit on product list APIs.
- BR-AP-016: Fake review detection: similar text, burst timing, low-rep buyers.
- BR-AP-017: Click fraud detection for affiliate links.
- BR-AP-018: Bulk account creation detection (same IP/device pattern).
- BR-AP-019: Payment card testing prevention (velocity checks).
- BR-AP-020: Chargeback monitoring: account frozen after 2 chargebacks in 90 days.

---

## 50. Marketplace Policies

### Objective
Define the marketplace policies that all users must agree to.

### Prohibited Products
- Illegal goods or services
- Copyright-infringing material
- Malware, viruses, or malicious code
- Stolen data or credentials
- Services that violate any law
- Adult content (unless specifically allowed category)
- Hate speech or discriminatory material

### Prohibited Conduct
- Selling own products under multiple accounts
- Price manipulation (collusion with competitors)
- Fake reviews or review manipulation
- Off-platform transactions to avoid fees
- Harassment or abuse of other users
- Attempting to compromise platform security
- Using bots or automation without API authorization
- Data scraping without permission

### Seller Obligations
- Deliver products within SLA
- Respond to messages within 24 hours
- Maintain accurate product descriptions
- Respect copyright and intellectual property
- Provide valid license keys (where applicable)
- Honor refunds per marketplace policy

### Buyer Obligations
- Provide accurate registration information
- Do not abuse the refund/dispute system
- Do not share purchased digital assets illegally
- Respect seller's intellectual property

### Enforcement
- Violations result in warnings, suspensions, or permanent bans
- Appeals process available for all enforcement actions
- Marketplace may withhold funds pending investigation
- Legal action may be pursued for fraud or IP infringement
- Policy changes communicated 30 days in advance

### Data Protection
- User data handled per Privacy Policy
- GDPR/CCPA compliance maintained
- Data retention per legal requirements
- Users can request data export/erasure
- Security incidents reported within 72 hours

### Disclaimers
- Marketplace acts as intermediary only
- No warranty on third-party products
- Dispute resolution via platform process
- Fees subject to change with notice
- Accounts inactive for 2+ years may be closed
- Marketplace reserves right to refuse service

---

*End of Document — Business Rules Specification v1.0.0*
