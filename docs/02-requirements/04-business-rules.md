# Business Rules — TRUE STAR BD LIMITED Multi-Vendor Digital Marketplace

> **Document Version:** 1.0  
> **Owner:** TRUE STAR BD LIMITED  
> **Classification:** Internal — Confidential  
> **Last Updated:** July 2026  

---

## Table of Contents

1. [User Registration & Account Rules (BR-001–BR-020)](#1-user-registration--account-rules-br-001br-020)
2. [Seller Rules (BR-021–BR-040)](#2-seller-rules-br-021br-040)
3. [Product Listing Rules (BR-041–BR-060)](#3-product-listing-rules-br-041br-060)
4. [Order & Transaction Rules (BR-061–BR-080)](#4-order--transaction-rules-br-061br-080)
5. [Payment & Escrow Rules (BR-081–BR-100)](#5-payment--escrow-rules-br-081br-100)
6. [Wallet Rules (BR-101–BR-115)](#6-wallet-rules-br-101br-115)
7. [Review & Rating Rules (BR-116–BR-130)](#7-review--rating-rules-br-116br-130)
8. [Dispute & Resolution Rules (BR-131–BR-145)](#8-dispute--resolution-rules-br-131br-145)
9. [Affiliate & Referral Rules (BR-146–BR-155)](#9-affiliate--referral-rules-br-146br-155)
10. [Content Moderation Rules (BR-156–BR-170)](#10-content-moderation-rules-br-156br-170)
11. [Fraud Prevention Rules (BR-171–BR-185)](#11-fraud-prevention-rules-br-171br-185)
12. [Platform Administrative Rules (BR-186–BR-200)](#12-platform-administrative-rules-br-186br-200)

---

## 1. User Registration & Account Rules (BR-001–BR-020)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-001 | **Email Uniqueness** | Each email address must be unique across all user accounts. Duplicate registration attempts with the same email must be rejected. | MANDATORY |
| BR-002 | **Email Verification** | A verified email address is required before a user can list products or make purchases. Verification is performed via a time-limited link sent to the registered email. | MANDATORY |
| BR-003 | **Phone Uniqueness** | Each phone number must be unique across all user accounts. This rule may be waived only when a phone number is shared by legally dependent individuals (e.g., family plan) and approved by support. | RECOMMENDED |
| BR-004 | **Phone Verification (Optional)** | Phone number verification via SMS OTP is required for withdrawal functionality. Phone is optional for basic account creation. | MANDATORY |
| BR-005 | **Password Complexity** | Passwords must be at least 8 characters long and must contain at least one uppercase letter, one lowercase letter, one digit, and one special character (`!@#$%^&*()_+-=[]{}|;':\",./<>?`). | MANDATORY |
| BR-006 | **Account Lockout — Failed Login** | After 5 consecutive failed login attempts within a rolling 15-minute window, the account is locked for 30 minutes. Lockout duration resets upon successful login after the lockout period. | MANDATORY |
| BR-007 | **Account Activation Window** | A new account must be activated within 24 hours of registration via the emailed activation link. Expired links trigger a re-send workflow requiring a fresh activation email. | MANDATORY |
| BR-008 | **Minimum Age — Sellers** | Seller applicants must be at least 18 years old at the time of application. Age verification is part of the KYC process. | MANDATORY |
| BR-009 | **Minimum Age — Buyers** | Buyer accounts may be created by individuals aged 13 and older. Accounts for users aged 13–18 require parental consent declarations. | MANDATORY |
| BR-010 | **One Person, One Account** | Each natural person may hold only one account on the platform. Duplicate or secondary accounts are grounds for suspension. | MANDATORY |
| BR-011 | **Account Deletion — Grace Period** | Upon a user-initiated deletion request, the account enters a 30-day grace period during which the user may cancel the deletion. After 30 days, the account and its associated data are permanently removed subject to legal retention requirements. | MANDATORY |
| BR-012 | **Inactive Account Deactivation** | Accounts with no login activity for 365 consecutive days are flagged as dormant and deactivated. Reactivation requires re-verification of email and a fresh password reset. | MANDATORY |
| BR-013 | **Username Rules** | Usernames must be 3–20 alphanumeric characters (underscores and hyphens also permitted). Must be unique across the platform. Profanity, slurs, or impersonation of platform staff or public figures is prohibited. | MANDATORY |
| BR-014 | **Session Timeout** | User sessions expire after 30 minutes of inactivity. Users are warned at the 25-minute mark with an option to extend the session. Unsaved work may be lost on timeout. | MANDATORY |
| BR-015 | **Concurrent Session Limit** | A single user may have a maximum of 5 active sessions across all devices. The oldest session is terminated if a sixth session is initiated. | RECOMMENDED |
| BR-016 | **Password Change — Session Invalidation** | When a user changes their password, all existing sessions (except the current one) are immediately invalidated. The user is prompted to re-authenticate on other devices. | MANDATORY |
| BR-017 | **MFA for Withdrawals > $500** | Multi-factor authentication (MFA) is required before any withdrawal request exceeding $500 (or equivalent in local currency) is processed. | MANDATORY |
| BR-018 | **MFA for Admin Access** | All administrator and moderator accounts must have MFA enabled at all times. Access is denied if MFA is not configured. | MANDATORY |
| BR-019 | **Social Login — Email Verification** | Accounts created via social login (Google, Facebook, Apple, etc.) must still verify their email address before they can transact. The email associated with the social provider is used. | MANDATORY |
| BR-020 | **Account Recovery** | Account recovery (password reset, account unlock) is performed exclusively via the verified email address on file. No recovery via phone, SMS, or support chat is permitted. | MANDATORY |

---

## 2. Seller Rules (BR-021–BR-040)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-021 | **KYC Requirement — Listing** | A seller must successfully complete Know Your Customer (KYC) verification before listing any products. KYC includes government-issued ID verification, address proof, and in some cases a video call. | MANDATORY |
| BR-022 | **Seller Agreement** | Sellers must explicitly agree to the Terms of Service and the Marketplace Seller Agreement before activating their store. Agreement is recorded with a timestamp. | MANDATORY |
| BR-023 | **Store Name Rules** | Store names must be 3–50 characters, unique across the platform, and must not contain special characters (only letters, digits, spaces, hyphens, and apostrophes are allowed). | MANDATORY |
| BR-024 | **Store Limit per Seller** | A seller account may operate a maximum of 5 stores by default. Sellers exceeding this limit require explicit platform approval and a multi-store agreement. | MANDATORY |
| BR-025 | **Default Commission Rate** | The default platform commission on each sale is 15% of the transaction value. This rate is deducted at the point of sale before funds enter the seller's available balance. | MANDATORY |
| BR-026 | **Negotiable Commission** | High-volume sellers (exceeding 500 orders/month for 3 consecutive months) may negotiate a reduced commission rate between 5% and 12%, subject to a contractual agreement. | RECOMMENDED |
| BR-027 | **Commission Deduction Timing** | Commission is deducted at the point of sale, not at withdrawal. The seller's wallet reflects the net amount (sale price minus commission) immediately upon order placement. | MANDATORY |
| BR-028 | **Minimum Payout** | The minimum payout amount for sellers is $10 (or equivalent in local currency). If the available balance is below this threshold, payout is deferred until the minimum is reached. | MANDATORY |
| BR-029 | **Payout Frequency** | Sellers can choose between automatic weekly payouts (every Monday) or manual on-demand payouts (subject to minimum payout rules). Automatic payouts are the default. | MANDATORY |
| BR-030 | **New Seller Probation** | New sellers undergo a 30-day probation period during which payouts are held for 7 days after the order completion date. This holding period is lifted after successful probation. | MANDATORY |
| BR-031 | **Minimum Rating — Active Status** | A seller's average rating must remain at or above 3.0 stars to maintain active store status. Sellers falling below 3.0 are given a 14-day warning period to improve. | MANDATORY |
| BR-032 | **Rating Below 2.0 — Suspension** | If a seller's average rating drops below 2.0 stars, the account is immediately flagged for review. The store may be suspended pending a manual review by the moderation team. | MANDATORY |
| BR-033 | **Order Fulfillment SLA — Digital Goods** | Digital goods must be fulfilled (download link delivered, license key provided, or API access granted) within 24 hours of order confirmation. | MANDATORY |
| BR-034 | **Customer Inquiry Response SLA** | Sellers must respond to customer inquiries within 12 hours. Response time is measured from the time the inquiry is sent to the seller's first reply. | MANDATORY |
| BR-035 | **Seller Cancellation — Before Delivery** | A seller may cancel an order before marking it as delivered. A penalty of 5% of the order value (minimum $1) is deducted from the seller's available balance. | MANDATORY |
| BR-036 | **Excessive Cancellations — Warning** | If a seller's cancellation rate exceeds 5% of total orders in a rolling 30-day period, the account receives a warning. Continued excessive cancellations may lead to temporary suspension. | MANDATORY |
| BR-037 | **Vacation Mode** | A seller may temporarily suspend their store (vacation mode) for up to 30 consecutive days. During this period, products are hidden from search but remain in the database. Vacation mode can be activated once every 90 days. | MANDATORY |
| BR-038 | **Product Listing Limit** | New sellers are limited to 100 active product listings. This limit is scaled upward based on sales performance and account age (200 at Silver tier, 500 at Gold, unlimited at Platinum). | MANDATORY |
| BR-039 | **Prohibited Items** | Sellers may not list products that appear on the platform's prohibited items list, which includes but is not limited to: illegal services, stolen data, hacking tools, counterfeit goods, adult content, weapons, and controlled substances. | MANDATORY |
| BR-040 | **Seller Tier System** | Tiers are determined by lifetime completed orders and confer benefits: **Bronze** (<100 orders) — standard commission, standard support; **Silver** (100–1,000) — 12% commission, priority support; **Gold** (1,000–10,000) — 10% commission, dedicated account manager; **Platinum** (10,000+) — 8% commission, waived withdrawal fees, dedicated account manager. | MANDATORY |

---

## 3. Product Listing Rules (BR-041–BR-060)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-041 | **Product Title** | Product titles must be 10–150 characters. ALL CAPS is not permitted (except for standard acronyms like PC, API, SDK). Keyword stuffing (repetition of the same keywords) is prohibited. | MANDATORY |
| BR-042 | **Product Description** | Product descriptions must be at least 50 characters and may not exceed 5,000 characters. Descriptions must accurately represent the product being sold. | MANDATORY |
| BR-043 | **Minimum Images** | Each product listing must include at least 1 image. A maximum of 10 images is allowed per product. | MANDATORY |
| BR-044 | **Image Requirements** | Images must meet the following specifications: minimum resolution 500×500 px, maximum resolution 4000×4000 px, accepted formats JPEG, PNG, and WebP. File size must not exceed 10 MB per image. | MANDATORY |
| BR-045 | **Category Assignment** | Each product must be assigned to both a parent category and a subcategory. Products categorized incorrectly may be rejected during moderation. | MANDATORY |
| BR-046 | **Digital Delivery Method** | Digital products must specify the delivery method in the listing. Acceptable methods: download link (hosted on platform or external), license key delivery, or API access credentials. | MANDATORY |
| BR-047 | **Platform Specification — Software/Gaming** | Software, game keys, and gaming-related products must explicitly state the target platform(s): PC, PlayStation, Xbox, Nintendo Switch, iOS, Android, or other specified platform. | MANDATORY |
| BR-048 | **Product Pricing** | Product base prices must be between $0.50 and $10,000 (or equivalent in local currency). Equivalent values are calculated using daily exchange rates. | MANDATORY |
| BR-049 | **Sale Price Validation** | When a sale price is set, it must be strictly lower than the base price. Sale prices equal to or greater than the base price are rejected. | MANDATORY |
| BR-050 | **Maximum Discount** | The maximum allowable discount from base price is 90%. Any sale price below 10% of the base price is rejected. | MANDATORY |
| BR-051 | **Product Variant SKUs** | Each product variant (e.g., different license tiers, platform versions) must have a unique Stock Keeping Unit (SKU) assigned by the seller. Duplicate SKUs within a seller's catalog are rejected. | MANDATORY |
| BR-052 | **Product Status Workflow** | Products move through the following statuses in order: **Draft** → **Pending Review** → **Approved** / **Rejected** → **Active** → **Paused** → **Archived**. Products may be cancelled/rejected at any pending state. | MANDATORY |
| BR-053 | **Moderation SLA** | Products requiring manual review are moderated within 24 hours of submission. Products eligible for auto-approval are processed instantly. | MANDATORY |
| BR-054 | **Auto-Approval Criteria** | Products are eligible for auto-approval when all three conditions are met: (a) seller rating > 4.0, (b) seller account age > 90 days, (c) zero prior moderation violations on the account. | MANDATORY |
| BR-055 | **Rejection Reason** | Any product rejected during moderation must include a clear rejection reason visible to the seller. Reasons are selected from a predefined list with an optional custom note. | MANDATORY |
| BR-056 | **Rejection Appeal Window** | A seller may appeal a product rejection within 7 days of the rejection notice. Appeals are reviewed by a senior moderator within 48 hours. | MANDATORY |
| BR-057 | **Product SEO Fields** | SEO fields (meta title, meta description, slug override, alt text for images) are recommended but not required. Products without SEO fields use auto-generated values from the title and description. | RECOMMENDED |
| BR-058 | **Auto-Archive — Inactivity** | Products with no status changes and no sales for 180 consecutive days are automatically moved to the Archived status. Archived products can be reactivated by the seller. | MANDATORY |
| BR-059 | **Zero Sales — Visibility Downgrade** | Products with 0 sales in a rolling 90-day period receive a visibility downgrade in search results (pushed beyond the first 10 pages). This does not apply to new products within their first 30 days. | MANDATORY |
| BR-060 | **Featured/Priority Listing** | Featured and priority listing placements are available as paid promotions. Fees are charged per listing per day. Priority listings are clearly labeled as "Sponsored" in search results. | MANDATORY |

---

## 4. Order & Transaction Rules (BR-061–BR-080)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-061 | **Order Minimum** | The minimum order value is $1.00 (or equivalent). Orders below this threshold are rejected at checkout. | MANDATORY |
| BR-062 | **Order Maximum** | The maximum order value is $10,000 (or equivalent). Orders exceeding this threshold require manual approval by a senior moderator or finance team member. | MANDATORY |
| BR-063 | **Order Status Flow** | Orders follow the lifecycle: **Pending** → **Confirmed** → **Processing** → **Delivered** → **Completed**. Cancellation is permitted at any state prior to delivery. Post-delivery cancellation is handled via the dispute system. | MANDATORY |
| BR-064 | **Digital Goods — Immediate Processing** | Orders containing only digital goods are auto-marked as "Processing" immediately upon payment confirmation, bypassing any manual processing step. | MANDATORY |
| BR-065 | **Buyer Cancellation — 15-Minute Window** | A buyer may cancel an order without penalty within 15 minutes of order placement. After 15 minutes, the order is locked and cancellation requires seller approval. | MANDATORY |
| BR-066 | **Seller Approval — Late Cancellation** | Cancellations requested by the buyer after the 15-minute window require seller approval. The seller may accept or reject the cancellation request. If rejected, the order proceeds normally. | MANDATORY |
| BR-067 | **Digital Fulfillment SLA** | Sellers have 24 hours from order confirmation to fulfill digital goods orders (deliver the product or provide access). | MANDATORY |
| BR-068 | **Auto-Cancellation — Non-Fulfillment** | If a digital order is not fulfilled within 24 hours of confirmation, the order is automatically cancelled and a full refund is issued to the buyer. | MANDATORY |
| BR-069 | **Buyer Confirmation Period** | After the seller marks an order as delivered, the buyer has 3 days to confirm receipt and mark the order as completed. | MANDATORY |
| BR-070 | **Auto-Confirm — No Action** | If the buyer takes no action within the 3-day confirmation period, the order is automatically marked as "Completed" and escrow is released to the seller. | MANDATORY |
| BR-071 | **Escrow Release — Order Completion** | Order completion (whether by buyer confirmation or auto-confirm) triggers the release of held escrow funds to the seller's available balance. | MANDATORY |
| BR-072 | **Dispute Filing Window** | A dispute must be opened within 7 days of the delivery date. Disputes filed after this window are automatically rejected unless the buyer can demonstrate extenuating circumstances. | MANDATORY |
| BR-073 | **Dispute Time Limit — Post-Completion** | No dispute may be opened for orders older than 30 days from the completion date. Such orders are considered permanently closed. | MANDATORY |
| BR-074 | **Refund Window** | Buyers may request a refund within 14 days of order completion. Refund requests initiated after 14 days are handled through the dispute system only. | MANDATORY |
| BR-075 | **Partial Refunds** | Partial refunds are permitted only through the dispute resolution process. Sellers and buyers cannot agree to partial refunds outside the dispute system. | MANDATORY |
| BR-076 | **Bulk Discounts — Seller Configurable** | Sellers may configure bulk discount rules: 10% off for 5+ items in the same order, 20% off for 10+ items. These thresholds are seller-configurable within platform-defined limits (min 5%, max 30% per tier). | RECOMMENDED |

---

## 5. Payment & Escrow Rules (BR-081–BR-100)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-081 | **Escrow — All Payments** | All buyer payments are held in the platform escrow account until the order is marked as completed or a dispute decision is rendered. Funds are never released directly from buyer to seller. | MANDATORY |
| BR-082 | **Escrow Release Triggers** | Escrow funds are released under exactly three conditions: (a) buyer confirms order completion, (b) auto-confirm after 3 days of delivery with no buyer action, or (c) a moderator decision in favor of the seller in a dispute. | MANDATORY |
| BR-083 | **Escrow Period Maximum** | The maximum escrow holding period is 30 days from the date of payment. If an order remains unresolved after 30 days, it is auto-escalated to a senior administrator for resolution. | MANDATORY |
| BR-084 | **Payment Methods** | Accepted payment methods are: bKash, Nagad, Rocket, Visa/Mastercard credit and debit cards, PayPal, and cryptocurrency (USDT on Binance Smart Chain and TRC-20). | MANDATORY |
| BR-085 | **Minimum Deposit** | The minimum deposit amount into a buyer wallet is $5 (or equivalent). | MANDATORY |
| BR-086 | **Maximum Deposit Without KYC** | Buyers who have not completed KYC may deposit a maximum of $500 total across all deposits. Once this limit is reached, KYC is required before further deposits. | MANDATORY |
| BR-087 | **Minimum Withdrawal** | The minimum withdrawal amount is $10 (or equivalent). Withdrawal requests below this threshold are rejected. | MANDATORY |
| BR-088 | **Withdrawal Processing Time** | Withdrawals are processed within 1–3 business days. Processing time may be extended during public holidays or if additional verification is required. | MANDATORY |
| BR-089 | **Withdrawal Fee** | A withdrawal fee of 2% applies, subject to a minimum of $0.50 and a maximum of $10 per withdrawal transaction. | MANDATORY |
| BR-090 | **Refund Processing Time** | Refunds are processed within 3–5 business days from the date of approval. Refunds are returned to the original payment method where technically possible. | MANDATORY |
| BR-091 | **Chargeback — Seller Freeze** | When a chargeback is initiated by a buyer through their payment provider, the seller's account is immediately frozen (no withdrawals, no new listings) until the chargeback dispute is resolved. | MANDATORY |
| BR-092 | **Currency Conversion** | Currency conversion rates are locked at the time of transaction for both payment and refund calculations. Rates are sourced from a defined third-party provider and updated daily. | MANDATORY |
| BR-093 | **Platform Fee — Withdrawal Only** | The platform fee is applied to seller withdrawals, not to sales transactions. The commission deducted at sale is separate from the withdrawal fee. | MANDATORY |
| BR-094 | **No Buyer Fees** | Buyers are not charged any platform fees for deposits or payments. All platform fees are borne by sellers. | MANDATORY |
| BR-095 | **Payment Gateway Fee — Seller Liability** | All payment gateway processing fees are passed to the seller and deducted from their payout at withdrawal time. The buyer is not charged gateway fees. | MANDATORY |
| BR-096 | **Failed Payment Retry** | If a payment attempt fails, the system automatically retries up to 3 times over a 24-hour period. After 3 failed attempts, the order is cancelled and the buyer is notified. | MANDATORY |

---

## 6. Wallet Rules (BR-101–BR-115)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-101 | **Non-Negative Balance** | Wallet balances must never go negative. Any transaction that would result in a negative balance is rejected. | MANDATORY |
| BR-102 | **Held Balance — No Withdrawal** | Funds held in escrow (held balance) are not available for withdrawal. Only the available balance can be withdrawn. | MANDATORY |
| BR-103 | **Immutable Transactions** | All wallet transactions are immutable. No transaction may be deleted, edited, or reversed once committed. Corrections require offsetting transactions that are separately recorded. | MANDATORY |
| BR-104 | **Wallet-to-Wallet Transfer** | Users may transfer funds from their available balance to another user's wallet. A 1% transfer fee is applied (minimum $0.10, maximum $10). Transfers are final and cannot be reversed. | MANDATORY |
| BR-105 | **Wallet Statement Export** | Users may download their wallet statement for the last 90 days as a CSV or PDF file. Data older than 90 days is available on request and may take up to 3 business days to generate. | MANDATORY |
| BR-106 | **Dormant Wallet — Fee** | Wallets with no activity (no deposits, withdrawals, or transfers) for 365 consecutive days are marked as dormant. After 2 years of dormancy, a monthly maintenance fee of $1 is deducted from the available balance until the balance reaches zero. | MANDATORY |
| BR-107 | **Maximum Wallet Balance** | The maximum wallet balance is $100,000 (or equivalent). Any incoming transaction that would exceed this limit is rejected, and the excess is auto-withdrawn to the user's linked bank account. | MANDATORY |
| BR-108 | **Seller Wallet — Proceeds Only** | Seller wallets may only be credited from sale proceeds. External deposits into a seller wallet are not permitted. All external funds must go to the buyer wallet first. | MANDATORY |
| BR-109 | **Buyer Wallet — External Top-Up** | Buyer wallets may be topped up from any accepted external payment method (see BR-084). There is no limit on the number of top-up transactions. | MANDATORY |
| BR-110 | **Dispute Hold** | When a dispute is opened, the disputed amount is frozen in both parties' wallets. The hold is released when the dispute is resolved in favor of the respective party. | MANDATORY |
| BR-111 | **Investigation Hold** | The platform may place a hold on a wallet for up to 30 days for investigation purposes (e.g., suspected fraud, suspicious activity). The user is notified within 24 hours of the hold being placed. | MANDATORY |
| BR-112 | **Withdrawal Destination Verification** | Bank accounts added as withdrawal destinations must be verified via micro-deposit (two small deposits totaling less than $1, confirmed by the user within 7 days). | MANDATORY |
| BR-113 | **Bank Account Change — Security Hold** | When a user changes their linked bank account, a 7-day security hold applies before the first withdrawal to the new account. During this period, no withdrawals to the new account are permitted. | MANDATORY |
| BR-114 | **Wallet Statements — Legal Validity** | Wallet statements generated by the platform are legally valid records for tax and accounting purposes. They are admissible as evidence in dispute resolution. | MANDATORY |
| BR-115 | **Multi-Currency Wallet** | Wallet balances are tracked per currency. Users may hold balances in multiple currencies simultaneously. Currency conversion occurs at the time of withdrawal or transaction. | RECOMMENDED |

---

## 7. Review & Rating Rules (BR-116–BR-130)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-116 | **Verified Purchase Only** | Only users who have purchased the product may submit a review. Reviews must be linked to a completed order for that specific product. | MANDATORY |
| BR-117 | **Rating and Text** | Each review must include a star rating (1–5). Text is optional but, if provided, must be between 10 and 1,000 characters. | MANDATORY |
| BR-118 | **Review Moderation — Rating-Based** | Reviews with a rating of 4 or 5 stars are auto-approved. Reviews with a rating of 1 to 3 stars are held for manual review before publication. Manual review is completed within 12 hours. | MANDATORY |
| BR-119 | **No Editing After Submission** | Once a review is submitted, it cannot be edited by the author under any circumstances. | MANDATORY |
| BR-120 | **Review Deletion by Author** | The review author may delete their own review within 24 hours of submission. After 24 hours, deletion is not permitted. | MANDATORY |
| BR-121 | **One Review Per Product** | A buyer may submit only one review per product. Subsequent purchases of the same product do not generate additional review opportunities. | MANDATORY |
| BR-122 | **Review Helpfulness Voting** | Other buyers may upvote or downvote reviews as helpful or unhelpful. A user may vote only once per review. Vote changes are permitted. | RECOMMENDED |
| BR-123 | **Featured Reviews** | Reviews with 10 or more helpful votes (net upvotes minus downvotes) are featured at the top of the reviews section. Up to 3 featured reviews are displayed before the chronological listing. | RECOMMENDED |
| BR-124 | **Inappropriate Review — Flagging** | A review may be flagged as inappropriate by users. After 3 unique flags, the review is automatically hidden from public view and queued for moderator review. | MANDATORY |
| BR-125 | **Seller Response to Review** | A seller may post one response to each review within 7 days of the review's publication date. Responses are publicly visible and cannot be edited once posted. | MANDATORY |
| BR-126 | **Seller Removal of Reviews** | Sellers may not remove buyer reviews, including negative reviews. Review removal requests must go through the moderation process. | MANDATORY |
| BR-127 | **Suspicious Review Detection** | Multiple 5-star reviews for the same product originating from the same IP address, device fingerprint, or user cluster trigger a fraud alert. Suspicious reviews are hidden pending manual review. | MANDATORY |
| BR-128 | **Seller Rating Calculation** | A seller's overall rating is calculated as the arithmetic mean of their last 100 reviews. Sellers with fewer than 5 reviews display "New Seller" instead of a numeric rating. | MANDATORY |
| BR-129 | **Response Time Rating** | A seller's response time rating is calculated from the last 30 days of customer inquiry responses. This rating is displayed separately from the product review rating. | RECOMMENDED |
| BR-130 | **Review Gating Prohibited** | Sellers may not condition the delivery of a product or the provision of support on the submission of a positive review. Violations result in account suspension. | MANDATORY |

---

## 8. Dispute & Resolution Rules (BR-131–BR-145)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-131 | **Dispute Fee** | A non-refundable dispute filing fee of $2 is charged to the party opening the dispute. This fee is refunded to the buyer if the buyer wins the dispute. | MANDATORY |
| BR-132 | **Dispute Timeline** | Disputes follow this lifecycle: **Opened** → **Investigation** (up to 48 hours) → **Evidence Gathering** (up to 72 hours) → **Decision** (rendered within 24 hours after evidence closes). | MANDATORY |
| BR-133 | **Burden of Proof — Delivery** | The seller bears the burden of proving that the product was delivered as described. If the seller cannot provide adequate proof of delivery, the buyer automatically wins. | MANDATORY |
| BR-134 | **Buyer Evidence — Not as Described** | If the buyer claims the product was not as described, the buyer must provide evidence supporting their claim (screenshots, videos, or other documentation). | MANDATORY |
| BR-135 | **Moderator Decision Finality** | The decision of a platform moderator is final within the platform's dispute resolution system. There is no internal appeal process. Users retain any rights available under applicable consumer protection law. | MANDATORY |
| BR-136 | **Dispute Resolution SLA** | Disputes must be resolved within 5 business days of opening. If resolution is not possible within this period, the dispute is escalated to a senior moderator. | MANDATORY |
| BR-137 | **Complex Dispute Escalation** | Complex disputes (involving multiple parties, amounts exceeding $2,000, or ambiguous evidence) are escalated to a senior moderator for resolution. | MANDATORY |
| BR-138 | **Dispute Outcomes** | Accepted dispute outcomes are: (a) **Buyer Wins** — full refund from escrow or seller wallet, (b) **Seller Wins** — no refund, escrow released to seller, (c) **Partial Split** — percentage-based split between buyer and seller as determined by the moderator. | MANDATORY |
| BR-139 | **Compensation Source** | Dispute compensation is taken from escrow funds first. If escrow funds are insufficient, the remaining amount is deducted from the seller's available wallet balance. | MANDATORY |
| BR-140 | **Excessive Buyer Disputes — Flagging** | Buyers who file disputes on more than 20% of their total orders (in a rolling 90-day period) are flagged for review. Flagged buyers may be subject to purchase restrictions. | MANDATORY |
| BR-141 | **Excessive Seller Disputes — Suspension Risk** | Sellers who have disputes opened on more than 10% of their total orders (in a rolling 90-day period) risk account suspension after a manual review. | MANDATORY |
| BR-142 | **Dispute Resolution Costs** | All dispute resolution costs (payment gateway fees, moderator time allocation) are borne by the losing party. Costs are deducted from the wallet of the losing party. | MANDATORY |
| BR-143 | **Chargeback Disputes — Seller Fee** | If a chargeback dispute is determined to be the merchant's (seller's) error, the seller is charged a $15 chargeback fee in addition to the refunded amount. | MANDATORY |
| BR-144 | **Dispute Communication Channel** | All dispute communication must occur through the platform's dispute messaging system. Communication outside the platform (email, phone) is not admissible as evidence. | MANDATORY |
| BR-145 | **Mediation Option** | For disputes exceeding $5,000, parties may opt for third-party mediation as an alternative to the standard dispute process. Mediation costs are shared equally unless otherwise agreed. | RECOMMENDED |

---

## 9. Affiliate & Referral Rules (BR-146–BR-155)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-146 | **Affiliate Commission Rate** | Affiliates earn a 5% commission on the first purchase made by a user they refer. Commission is calculated on the net transaction value (after discounts, before platform fees). | MANDATORY |
| BR-147 | **Referral Cookie Duration** | Referral attribution uses a 30-day cookie. If the referred user makes their first purchase within 30 days of clicking the affiliate link, the commission is awarded. After 30 days, attribution expires. | MANDATORY |
| BR-148 | **Affiliate Payout Minimum** | Affiliate commissions are paid out when the affiliate's unpaid commission balance reaches $20. Balances below this threshold carry over to the next payout cycle. | MANDATORY |
| BR-149 | **No Self-Referral** | Affiliates may not refer themselves (create an account using their own affiliate link). Self-referral detection results in commission forfeiture and account warning. | MANDATORY |
| BR-150 | **No Misleading Advertising** | Affiliates may not use misleading advertising, fake testimonials, impersonation, or false claims to promote the platform. Violations result in immediate affiliate account termination. | MANDATORY |
| BR-151 | **FTC Disclosure Compliance** | Affiliates must clearly and conspicuously disclose their affiliate relationship with TRUE STAR BD LIMITED in all promotional content, in compliance with FTC guidelines. Non-compliance results in affiliate termination. | MANDATORY |
| BR-152 | **Self-Purchase Through Own Link** | If an affiliate purchases through their own affiliate link, the commission is forfeited, the purchase is voided, and the account receives a formal warning. Repeat violations result in affiliate termination. | MANDATORY |
| BR-153 | **New Seller Referral Bonus** | Existing users who refer a new seller who is approved and lists at least 5 products within 30 days receive a $10 referral bonus credited to their wallet. | MANDATORY |
| BR-154 | **Monthly Top Affiliate Bonus** | The top 10 affiliates by total commission earned in a calendar month receive an additional 2% commission on all qualifying sales for the following month. | RECOMMENDED |
| BR-155 | **Affiliate Link Types** | Affiliates may use standard referral links, promotional codes, and banner ads. All affiliate link types are tracked via the same cookie-based attribution system. | MANDATORY |

---

## 10. Content Moderation Rules (BR-156–BR-170)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-156 | **Prohibited Content — General** | The following content types are strictly prohibited across all platform surfaces (listings, reviews, messages, profiles): adult/pornographic material, graphic violence, hate speech, illegal drug references, weapon sales, counterfeit goods, and any content promoting illegal activity. | MANDATORY |
| BR-157 | **Prohibited Digital Goods** | The following digital goods are strictly prohibited: cracked or pirated software, stolen or shared accounts, hacking tools and malware, plagiarism-enabling services, and any digital goods that infringe on intellectual property rights. | MANDATORY |
| BR-158 | **Competitor Names in Listings** | Product titles and descriptions may not include competitor brand names unless the product is demonstrably compatible with or an accessory for that competitor's product (e.g., "iPhone charger" is permitted; "Better than Apple" is not). | MANDATORY |
| BR-159 | **External Links in Reviews** | Reviews must not include external links, email addresses, phone numbers, or any form of contact information. Reviews containing such content are rejected or removed. | MANDATORY |
| BR-160 | **Message Spam Detection** | Messages flagged by the automated spam detection system result in a user warning on the first offense. Repeat offenses result in a temporary ban of escalating duration (24h, 7d, 30d, permanent). | MANDATORY |
| BR-161 | **Profile Image Appropriateness** | Profile images (avatars, cover photos) must not contain nudity, violence, hate symbols, or copyrighted material. Violating images are removed and the user is notified. | MANDATORY |
| BR-162 | **Store Banner Branding** | Store banners and logos may not mimic or resemble the TRUE STAR BD LIMITED platform branding (logo, color scheme, typography) in a way that could cause confusion. | MANDATORY |
| BR-163 | **DMCA Takedown SLA** | Valid DMCA takedown notices are processed within 24 hours of receipt. Upon takedown, the seller is notified and given an opportunity to file a counter-notice. | MANDATORY |
| BR-164 | **Repeat Copyright Infringement — Three Strikes** | Sellers who receive 3 valid DMCA takedown notices (strikes) have their account permanently terminated. Strikes are counted on a rolling 12-month basis. | MANDATORY |
| BR-165 | **Automated Content Scanning** | All user-generated content (product listings, reviews, messages, profile text) is automatically scanned against a keyword blacklist. Matches are flagged for manual review. | MANDATORY |
| BR-166 | **AI-Generated Content Policy** | AI-generated product descriptions and images are permitted but must be clearly labeled as "AI-generated" in the listing. Misleading use of AI-generated content (e.g., fake screenshots) is prohibited. | RECOMMENDED |
| BR-167 | **Moderation Appeal Process** | Users may appeal a content moderation decision within 7 days. Appeals are reviewed by a different moderator than the one who made the original decision. | MANDATORY |
| BR-168 | **Prohibited Keyword Blacklist** | A centrally managed blacklist of prohibited keywords and phrases is maintained and updated weekly. Automated scanners enforce this blacklist in real time. | MANDATORY |
| BR-169 | **Content Reporting — User Flagging** | Any user may flag content they believe violates platform policies. Flags are reviewed within 4 hours during business hours and 12 hours outside business hours. | MANDATORY |
| BR-170 | **False Reporting — Penalty** | Users who repeatedly submit false or frivolous content flags may have their flagging privileges revoked and may face account restrictions. | MANDATORY |

---

## 11. Fraud Prevention Rules (BR-171–BR-185)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-171 | **Duplicate Account Detection** | Multiple accounts originating from the same IP address, device fingerprint, or phone number trigger an automated review. Verified duplicate accounts are merged or the secondary account is suspended. | MANDATORY |
| BR-172 | **Rapid-Fire Order Detection** | Ten or more orders placed by the same buyer within a 5-minute window are flagged for fraud review. Orders are held in "Pending" status until the review is complete. | MANDATORY |
| BR-173 | **New Account — High-Value Order Flag** | Orders exceeding $500 placed by accounts less than 7 days old are flagged for manual review before processing. | MANDATORY |
| BR-174 | **New Device/Location Notification** | A login from a new device or geographic location triggers an email notification to the account holder with device details and location. A link to "Secure My Account" is provided. | MANDATORY |
| BR-175 | **Multiple Failed Payments — Block** | Five or more consecutive failed payment attempts using the same card or account within a 60-minute period result in that payment method being temporarily blocked for 24 hours. | MANDATORY |
| BR-176 | **Price Manipulation Detection** | A price change on a product exceeding 50% of the previous price within a 24-hour period is flagged as potential price manipulation. The listing is temporarily paused pending review. | MANDATORY |
| BR-177 | **Fake Review Pattern Detection** | Reviews identified as potentially fake via pattern analysis (same IP, similar phrasing, burst timing) are flagged. All reviews by the flagged user are subjected to manual review. | MANDATORY |
| BR-178 | **Seller Collusion Detection** | Sellers purchasing their own products (self-purchase) or engaging in reciprocal purchasing schemes with other sellers are detected via transaction pattern analysis. Profits from collusive transactions are forfeited and the account receives a formal warning. | MANDATORY |
| BR-179 | **Synthetic Identity Detection** | Document verification during KYC includes checks for synthetic identity indicators: inconsistent document metadata, document manipulation artifacts, and cross-referencing with external identity databases. | MANDATORY |
| BR-180 | **Device Fingerprinting** | All user sessions are tracked via device fingerprinting (browser attributes, screen resolution, installed fonts, timezone). Fingerprint changes are logged and correlated for fraud analysis. | RECOMMENDED |
| BR-181 | **Transaction Velocity Check** | No more than 10 transactions (orders, deposits, withdrawals) may be initiated by a single user within a 60-minute period. Exceeding this threshold triggers a temporary transaction hold. | MANDATORY |
| BR-182 | **Geographic Inconsistency Check** | Logins from two geographically distant locations (greater than 500 km apart) within less than 2 hours are flagged as potentially fraudulent. The account is temporarily locked and the user is contacted via phone. | MANDATORY |
| BR-183 | **Fraud Blacklist** | The platform maintains a blacklist of known fraudulent email addresses, phone numbers, IP addresses, and wallet addresses. Registration or transactions involving blacklisted entities are automatically blocked. | MANDATORY |
| BR-184 | **Trusted Buyer Whitelist** | Buyers with a verified transaction history (20+ completed orders, no disputes, account age > 6 months) may be added to a trusted whitelist. Whitelisted buyers experience reduced friction (fewer CAPTCHAs, faster payment processing). | RECOMMENDED |
| BR-185 | **Suspicious Activity Reporting** | The platform reports suspicious transactions exceeding $2,000 to the relevant financial intelligence unit as required by applicable anti-money laundering (AML) regulations. | MANDATORY |

---

## 12. Platform Administrative Rules (BR-186–BR-200)

| # | Rule | Description | Enforcement |
|---|------|-------------|-------------|
| BR-186 | **Super Admin Access** | The Super Admin role has unrestricted access to all platform features, data, and administrative functions. Super Admin actions are not bound by role-based access controls. | MANDATORY |
| BR-187 | **Financial Transaction Immutability** | No administrator, including Super Admin, may modify, delete, or reverse financial transactions. Financial corrections require offsetting entries in the general ledger. | MANDATORY |
| BR-188 | **Admin Audit Trail** | All administrative actions (logins, data views, configuration changes, user modifications) are logged to an immutable audit trail. Audit logs are retained for a minimum of 7 years. | MANDATORY |
| BR-189 | **Moderator Conflict of Interest** | A moderator may not handle a dispute case involving a seller or buyer with whom they have a personal, financial, or professional relationship. Cases must be reassigned to another moderator. | MANDATORY |
| BR-190 | **Finance — Segregation of Duties** | Finance team members who process withdrawals may not approve their own withdrawal requests. A different finance team member or a manager must approve withdrawals for finance staff. | MANDATORY |
| BR-191 | **Reporting Team — Read-Only** | The reporting and analytics team has read-only access to all platform data. They may not modify any user, transaction, or configuration data. | MANDATORY |
| BR-192 | **API Rate Limits** | Public (unauthenticated) API access is limited to 1,000 requests per hour per IP address. Authenticated API access is limited to 10,000 requests per hour per API key. Excess requests receive a 429 status code. | MANDATORY |
| BR-193 | **Data Retention — Post-Deletion** | User data is retained for 5 years after account deletion as required by applicable legal and regulatory obligations. After 5 years, data is permanently and irreversibly deleted. | MANDATORY |
| BR-194 | **GDPR Data Export** | Upon a verified data export request from a user, all personal data held by the platform must be delivered in a machine-readable format (JSON) within 30 calendar days. | MANDATORY |
| BR-195 | **Tax Reporting** | An annual transaction report is generated for each seller who has processed 50 or more transactions in the tax year. Reports are made available by January 31 of the following year. | MANDATORY |
| BR-196 | **Scheduled Maintenance Window** | The platform maintenance window is Sunday from 2:00 AM to 4:00 AM (platform local time). Users are notified at least 24 hours in advance of any scheduled maintenance. | MANDATORY |
| BR-197 | **Emergency Maintenance** | Emergency maintenance may be performed outside the scheduled window. Users are notified immediately upon initiation, and the maintenance duration is minimized. A post-mortem is published within 48 hours. | MANDATORY |
| BR-198 | **A/B Testing Protocol** | A/B tests require explicit approval from the Product Director or above. Users participating in A/B tests must be notified via a banner or in-app notification. Test results and durations are logged for audit. | MANDATORY |
| BR-199 | **Feature Flag Rollout** | All new features must be gated behind feature flags with configurable rollout percentages. Flags are controlled via the admin panel. Rollouts exceeding 50% require Product Director approval. | MANDATORY |
| BR-200 | **Policy Change Notice** | All platform policy changes are communicated to users at least 14 days in advance via email and platform notification. Material policy changes require explicit user acknowledgment before continued use. | MANDATORY |

---

## Appendix A — Enforcement Level Definitions

| Level | Meaning |
|-------|---------|
| **MANDATORY** | The rule must be enforced by the platform at all times. Violations result in automated rejection, blocking, or corrective action. System implementation must prevent violation of these rules. |
| **RECOMMENDED** | The rule represents a best practice that should be implemented. Non-compliance does not result in immediate enforcement action, but the platform may choose to make it mandatory at a future date. |

## Appendix B — Rule Version History

| Version | Date | Author | Change Description |
|---------|------|--------|--------------------|
| 1.0 | July 2026 | TRUE STAR BD LIMITED | Initial release — 200 business rules across 12 categories |

---

> **End of Document** — TRUE STAR BD LIMITED Multi-Vendor Digital Marketplace Business Rules  
> *This document is confidential and proprietary. Unauthorized distribution is prohibited.*
