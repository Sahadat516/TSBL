# TRUE STAR BD LIMITED — Business Workflows

---

**Document Version:** 1.0  
**Date:** 2026-07-01  
**Author:** Principal Software Architect  
**Status:** Draft for Review  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Platform Registration & Onboarding Workflow](#2-platform-registration--onboarding-workflow)
3. [Product Listing & Approval Workflow](#3-product-listing--approval-workflow)
4. [Order Fulfillment Workflow](#4-order-fulfillment-workflow)
5. [Payment & Escrow Settlement Workflow](#5-payment--escrow-settlement-workflow)
6. [Dispute Resolution Workflow](#6-dispute-resolution-workflow)
7. [Withdrawal & Payout Workflow](#7-withdrawal--payout-workflow)
8. [Affiliate Commission Workflow](#8-affiliate-commission-workflow)
9. [Content Moderation Workflow](#9-content-moderation-workflow)

---

## 1. Introduction

### 1.1 Purpose

This document defines the core business workflows for the TRUE STAR BD LIMITED (TSBL) digital marketplace. Each workflow is described in terms of its trigger, numbered steps, decision points, actors, expected outcomes, error handling procedures, and service-level agreement (SLA) targets. These workflows form the blueprint for system architecture, API design, and user experience implementation.

### 1.2 Workflow Notation

Each workflow uses the following structure:

| Element | Description |
|---------|-------------|
| **Trigger** | The event or condition that initiates the workflow |
| **Actors** | Human or system participants involved |
| **Steps** | Numbered sequence of actions |
| **Decision Points** | Conditional branches that alter the workflow path |
| **Expected Outcome** | The successful end state |
| **Error Handling** | Procedures when things go wrong |
| **SLA Target** | Maximum elapsed time for completion |

### 1.3 Conventions

- `[System]` — Automated platform action
- `[User:Role]` — Human actor action
- `[Gateway]` — External third-party integration
- `→` — Transition to next step or sub-workflow

---

## 2. Platform Registration & Onboarding Workflow

### 2.1 Overview

This workflow governs how new users register, verify their identity, and onboard as buyers, sellers, or affiliates. It spans guest registration through to KYC verification for sellers.

### 2.2 Workflow Diagram (Textual)

```
Guest → Registration Form → Email Verification → Basic Profile → 
    │
    ├── Buyer Path → Dashboard (Active)
    │
    └── Seller Path → KYC Submission → Document Review → 
            │
            ├── Approved → Seller Dashboard (Verified)
            │
            └── Rejected → Resubmit or Appeal
```

### 2.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Guest user clicks "Sign Up" or "Become a Seller" on the landing page |
| **Actors** | Guest, System, Moderator (for KYC), Email/SMS Gateway |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | User accesses registration form | Guest | Render registration form with CAPTCHA |
| 2 | User fills in name, email, password, phone | Guest | [System] Validate input format, check email uniqueness, enforce password policy |
| 3 | User submits registration | Guest | [System] Hash password (bcrypt), create user account in `PENDING_VERIFICATION` status, generate email verification token |
| 4 | [Decision] Validation success? | — | If validation fails → return specific field errors to user (back to step 2). If success → proceed to step 5 |
| 5 | Send verification email | [System] | Queue email with 6-digit OTP + verification link (expires 24h) |
| 6 | User verifies email | Guest | User clicks link or enters OTP |
| 7 | [Decision] Token valid? | — | If token expired or invalid → show error, offer resend. If valid → proceed to step 8 |
| 8 | Activate account | [System] | Set status to `ACTIVE`, send welcome email, redirect to dashboard |
| 9 | [Decision] User selected "Seller" during signup? | — | If yes → proceed to KYC workflow (step 10). If no → onboarding complete (Buyer) |
| 10 | Seller KYC initiation | [System] | Present KYC form with document upload |
| 11 | User submits KYC documents | User:Seller | Upload ID, selfie, proof of address, business docs (if applicable) |
| 12 | [System] Initial validation | [System] | Check file formats, sizes, OCR extraction, liveness check |
| 13 | [Decision] Auto-validation passes? | — | If confidence > 95% → auto-approve (step 15). If 70-94% → flag for manual review (step 14). If < 70% → reject with reason (step 17) |
| 14 | Manual KYC review | Moderator | Review documents in queue; approve or reject |
| 15 | [Decision] KYC approved? | — | If approved → proceed to step 16. If rejected → step 17 |
| 16 | Activate seller account | [System] | Set `SELLER_VERIFIED` flag, issue verification badge, unlock seller dashboard, send notification |
| 17 | Reject KYC | [System] | Send rejection email with reason and resubmission instructions; set status to `KYC_REJECTED` |
| 18 | User resubmits KYC (or appeals) | User:Seller | Returns to step 11 with pre-filled form |

### 2.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Validation success | All fields meet rules | Step 5 | Step 2 (with errors) |
| Token valid | Token exists, not expired, not used | Step 8 | Step 6 (with error) |
| Seller path selected | Role flag during signup | Step 10 | Complete |
| Auto-validation passes | ML confidence score | Step 15 | Step 14 or Step 17 |
| KYC approved | Moderator decision | Step 16 | Step 17 |

### 2.5 Expected Outcomes

- **Success:** User is an active Buyer or Verified Seller with full platform access.
- **Partial Success:** User is active as a Buyer but has not completed KYC; seller features are locked.
- **Failure:** Registration abandoned due to validation errors, expired token, or KYC rejection.

### 2.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| Duplicate email | Show inline error; suggest login or password reset |
| Email delivery failure | Retry 3 times with exponential backoff; log alert; inform user to check spam or request resend |
| Token expired | Offer "Resend Verification Email" button; invalidate old token, generate new |
| KYC document unreadable | OCR failure → flag for manual review with annotation |
| KYC document forgery suspicion | Flag for admin review; escalate to security team |
| User abandons during KYC | Save as draft; send reminder email after 24h, 72h, then archive after 30 days |

### 2.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Registration to email sent | < 10 seconds | Email queue lag |
| Email verification to activation | < 1 second | Token validation time |
| KYC auto-decision | < 30 seconds | ML inference time |
| KYC manual review | < 48 hours | Queue wait time (business hours) |
| KYC resubmission review | < 24 hours | Priority queue processing |

---

## 3. Product Listing & Approval Workflow

### 3.1 Overview

This workflow covers the lifecycle of a digital product listing from creation through moderation to publication, including updates and archival.

### 3.2 Workflow Diagram (Textual)

```
Seller → Create Product → Fill Details → Upload Files → 
    Submit for Review → Moderation Queue →
        │
        ├── Approved → Published → Searchable
        │
        └── Rejected → Revision Requested → Edit & Resubmit
                │
                └── Abandon → Draft (Archived after 90 days)
```

### 3.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Seller clicks "Add New Product" from seller dashboard |
| **Actors** | Seller, System, Moderator, File Storage (S3/CDN), Anti-Malware Scanner |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | Seller initiates product creation | Seller | [System] Create product record in `DRAFT` status, generate UUID |
| 2 | Seller fills product details | Seller | Title, description, category, tags, price, refund policy, SEO metadata |
| 3 | Seller uploads product files | Seller | [System] Validate file types, sizes; initiate upload to staging storage; perform antivirus scan |
| 4 | [Decision] Files pass security scan? | — | If malware detected → quarantine file, notify seller. If clean → proceed |
| 5 | Seller uploads preview media | Seller | Images (max 5), video (max 1); auto-generate thumbnails |
| 6 | Seller submits for review | Seller | [System] Change status to `PENDING_REVIEW`, add to moderation queue, notify moderators |
| 7 | [Decision] Auto-moderation rules pass? | [System] | Check for prohibited keywords, NSFW images, pricing anomalies. If confidence > 95% → auto-reject. If clean → proceed to step 8 |
| 8 | Moderator reviews listing | Moderator | Preview full listing, download files if needed, verify compliance |
| 9 | [Decision] Moderator approves? | — | If approve → step 10. If reject → step 11 |
| 10 | Publish product | [System] | Set status to `PUBLISHED`, move files to CDN permanent storage, index for search, notify seller, increment seller's listing count |
| 11 | Reject product | Moderator | Select rejection reason from template (prohibited content, insufficient quality, incomplete info, etc.), provide optional custom note, set status to `REJECTED` |
| 12 | Notify seller of rejection | [System] | Send notification with reason and resubmission instructions |
| 13 | Seller edits and resubmits | Seller | Returns to step 2 with pre-filled form; status resets to `PENDING_REVIEW` |
| 14 | [Optional] Seller archives product | Seller | [System] Set status to `ARCHIVED`, remove from search but retain data |

### 3.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Security scan pass | No malware detected | Step 5 | Quarantine + notify |
| Auto-moderation pass | No policy violations | Step 8 | Auto-reject (step 11) |
| Moderator approval | Meets quality & policy standards | Step 10 | Step 11 |

### 3.5 Expected Outcomes

- **Success:** Product is published, searchable, and available for purchase.
- **Rejection:** Seller receives feedback; product can be resubmitted.
- **Abandonment:** Product remains in Draft until auto-archived after 90 days of inactivity.

### 3.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| File upload interrupted | Resume-capable upload via chunked upload; retry from last successful chunk |
| Antivirus service unavailable | Queue scan; set product to `PENDING_SCAN`; allow provisional publication |
| CDN upload failure | Retry 3 times; fallback to alternative CDN region; alert ops team |
| Image processing failure | Use original image; log error; skip thumbnail generation |

### 3.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| File upload & scan | < 5 minutes for 2 GB | Upload throughput + scan time |
| Auto-moderation decision | < 30 seconds | ML inference time |
| Manual moderation review | < 24 hours | Queue wait time |
| Publication propagation | < 2 minutes | CDN + search index propagation |

---

## 4. Order Fulfillment Workflow

### 4.1 Overview

This workflow handles the lifecycle of a digital product order from checkout through payment capture, file delivery, and order completion.

### 4.2 Workflow Diagram (Textual)

```
Buyer → Checkout → Payment → Escrow Hold → 
    Digital Delivery → Buyer Downloads → 
        │
        ├── Buyer Confirms → Escrow Release → Order Complete
        │
        └── Auto-Release (14 days) → Escrow Release → Order Complete
                │
                └── Dispute Filed → Freeze Escrow → Dispute Workflow
```

### 4.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Buyer clicks "Place Order" on checkout page |
| **Actors** | Buyer, Seller, System, Payment Gateway, CDN, Email Gateway |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | Order creation | Buyer | [System] Validate cart, check product availability, calculate totals (price + tax + fees), reserve inventory (decrement stock if limited) |
| 2 | [Decision] Order validation passes? | — | If cart invalid, price changed, or product removed → show error. If valid → proceed to step 3 |
| 3 | Create order record | [System] | Generate order ID, set status to `PENDING_PAYMENT`, store order snapshot (product details, prices at time of order) |
| 4 | Redirect to payment | [System] | Present payment method selection, collect billing info, redirect to payment gateway or show inline card form |
| 5 | Payment processing | [Gateway] | Process payment via selected gateway (card, mobile banking, wallet) |
| 6 | [Decision] Payment successful? | — | If success → step 7. If failure → step 13 |
| 7 | Capture payment in escrow | [System] | Hold funds in platform escrow account, set order status to `PROCESSING` |
| 8 | Trigger digital delivery | [System] | Generate secure signed download URLs for all product files, attach to order record |
| 9 | Deliver to buyer | [System] | Display download links on order confirmation page, send email with download links |
| 10 | Buyer downloads files | Buyer | Click download link, receive files via CDN |
| 11 | [System] Log download event | [System] | Record download timestamp, IP, file; increment download counter; notify seller |
| 12 | Initiate escrow release timer | [System] | Start 14-day escrow countdown (configurable); send notification to buyer: "Confirm Delivery" |
| 13 | [Decision - Parallel] Buyer confirms or timer expires? | — | If buyer clicks "Confirm Delivery" → immediate release to seller (step 16). If 14-day timer expires → auto-release (step 16). If buyer files dispute → step 14 |
| 14 | Dispute filed | Buyer | → Trigger Dispute Resolution Workflow; escrow frozen |
| 15 | [Decision] Dispute resolved? | — | Depending on outcome: full refund to buyer or release to seller |
| 16 | Release funds to seller | [System] | Calculate platform commission, transfer net amount to seller's available balance, set order status to `COMPLETED` |
| 17 | Send completion notifications | [System] | Email buyer: "Order Complete" with receipt. Email seller: "Earnings Updated" with transaction summary |

### 4.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Order validation | Stock, pricing, product validity | Step 3 | Error to user |
| Payment success | Gateway confirms charge | Step 7 | Step 13 |
| Buyer confirms delivery | Buyer clicks confirm within 14 days | Step 16 | Timer wait or dispute |
| Escrow timer expires | 14 days elapsed | Step 16 | — |
| Dispute filed | Buyer or seller initiates | Step 14 | Continue |

### 4.5 Expected Outcomes

- **Success:** Buyer receives files, seller receives funds (minus commission), order is marked Complete.
- **Auto-Complete:** Buyer never confirms but does not dispute; funds auto-release after 14 days.
- **Refund:** Dispute results in full/partial refund; funds returned to buyer.
- **Failure:** Payment never completed; order cancelled after 24 hours.

### 4.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| Payment gateway timeout | Retry up to 3 times; if still failing, present alternative payment method |
| Payment captured but delivery fails | Retry delivery 3 times; if seller files are corrupt, escalate to support |
| CDN URL generation fails | Fall back to direct server download with rate limiting |
| Email delivery fails (order confirmation) | Queue for retry; buyer can still access via "My Orders" page |
| Escrow release fails (gateway issue) | Queue for retry; alert finance team for manual processing |

### 4.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Order creation | < 2 seconds | API response time |
| Payment processing | < 30 seconds | Gateway round-trip |
| Digital delivery initiation | < 10 seconds post-payment | File URL generation |
| Email delivery | < 1 minute | Email queue processing |
| Escrow auto-release | Exactly at 14 days | Cron job precision (±1 hour) |

---

## 5. Payment & Escrow Settlement Workflow

### 5.1 Overview

This workflow manages the entire financial lifecycle of a transaction from payment capture through escrow holding to eventual settlement, including commission calculation and fee deduction.

### 5.2 Workflow Diagram (Textual)

```
Buyer Pays → Gateway Confirmation → Funds Held in Platform Escrow →
    │
    ├── Successful Delivery → Commission Calculation →
    │       ├── Platform Fee Deducted
    │       ├── Payment Gateway Fee Deducted
    │       └── Net Amount → Seller Balance (Available)
    │
    └── Refund Scenario → Full Amount → Buyer Refund
            ├── Platform Fee Reversed
            └── Gateway Fee (non-recoverable) Absorbed by Platform
```

### 5.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Payment gateway asynchronous callback (webhook) confirming successful charge |
| **Actors** | System, Payment Gateway, Finance Manager (manual oversight) |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | Receive payment webhook | [Gateway] | HTTP POST with payment details, signature, transaction ID |
| 2 | Verify webhook signature | [System] | Validate HMAC signature using gateway's secret key; reject if invalid |
| 3 | Check for duplicate webhook | [System] | Idempotency check by transaction ID; ignore if already processed |
| 4 | Record transaction | [System] | Create `transaction` record: type = `PAYMENT`, amount, currency, gateway, gateway fee, status = `CAPTURED` |
| 5 | Credit escrow balance | [System] | Add full amount to platform escrow ledger; update order `escrow_balance` |
| 6 | Calculate platform commission | [System] | Apply commission rules: global rate × category rate × seller-specific override. Deduct from escrow and credit to platform revenue account |
| 7 | Record commission | [System] | Create commission record: amount, rate applied, basis points |
| 8 | [Decision] Is this a refund scenario? | — | If triggered by refund → step 9. If triggered by settlement → step 12 |
| 9 | Initiate refund | [System] | Calculate refund amount (full or partial per dispute decision) |
| 10 | Reverse commission | [System] | Deduct commission from platform revenue, return to escrow |
| 11 | Process refund via gateway | [System] | Call gateway refund API; update transaction record with refund ID |
| 12 | Settlement to seller | [System] | Move funds from escrow to seller `available_balance` ledger; net of commission and any chargebacks |
| 13 | Create settlement record | [System] | Record: seller ID, amount, commission deducted, gateway fee, timestamp |
| 14 | Notify seller | [System] | Send notification: "BDT X,XXX has been added to your available balance" |
| 15 | Reconciliation batch | [System] | End-of-day batch: match gateway settlement report against platform records; flag discrepancies |

### 5.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Signature valid | HMAC matches | Step 3 | Reject (log security alert) |
| Duplicate webhook | transaction_id exists | Ignore | Step 4 |
| Refund scenario | Refund flag from dispute or seller | Step 9 | Step 12 |

### 5.5 Expected Outcomes

- **Success:** Seller's available balance is credited with net sale amount; platform records commission revenue; escrow is cleared.
- **Refund:** Full amount returned to buyer; commission reversed; gateway fee (if non-refundable) absorbed by platform.
- **Failure:** Webhook processing fails → manual reconciliation required.

### 5.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| Webhook delivery timeout | Gateway retries; platform acknowledges with 200 immediately, processes async |
| Signature verification fails | Log security incident; hold transaction for manual review |
| Gateway refund API fails | Retry 3 times; if still failing, issue platform credit to buyer wallet; initiate chargeback |
| Currency mismatch | Convert at platform rate; log FX gain/loss |
| Reconciliation discrepancy | Flag for finance manager review in daily report |

### 5.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Webhook processing | < 5 seconds | Webhook to transaction recorded |
| Commission calculation | < 1 second | Real-time during settlement |
| Refund processing | < 24 hours | From dispute decision to refund initiated |
| Daily reconciliation | < 2 hours | Batch processing time (EOD) |

---

## 6. Dispute Resolution Workflow

### 6.1 Overview

This workflow governs the formal process for handling conflicts between buyers and sellers regarding orders, payments, or product quality.

### 6.2 Workflow Diagram (Textual)

```
Buyer/Seller → File Dispute → Escrow Frozen →
    Moderator Assignment → Evidence Collection →
        │
        ├── Moderator Review → Decision →
        │       ├── Full Refund to Buyer → Escrow Released to Buyer
        │       ├── Partial Refund → Split Escrow
        │       ├── Release to Seller → Escrow Released to Seller
        │       └── Dismissed → Escrow Released to Seller
        │
        └── Appeal → Admin Review → Final Decision (Binding)
```

### 6.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Buyer or seller clicks "Open Dispute" on order detail page during escrow period |
| **Actors** | Buyer, Seller, Moderator, Administrator, System |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | User initiates dispute | Buyer/Seller | [System] Validate that order is in escrow period; if not, show error |
| 2 | Present dispute form | [System] | Reason categories: Item not received, Defective, Not as described, Other |
| 3 | User submits dispute details | Buyer/Seller | Description (mandatory, min 20 chars), attachments (max 5 files) |
| 4 | Create dispute case | [System] | Generate case ID (format: DSP-{YYYYMMDD}-{XXXXX}), set status to `OPEN`, freeze escrow funds |
| 5 | Notify counter-party | [System] | Email + in-app notification to other party with case ID and details |
| 6 | Counter-party responds | Buyer/Seller | Submit their evidence and response (48-hour window) |
| 7 | [Decision] Response received or timeout? | — | If response within 48h → step 8. If timeout → proceed without response |
| 8 | Auto-assign moderator | [System] | Round-robin assignment to available moderators; escalate if queue > 50 cases |
| 9 | Moderator reviews case | Moderator | Examine order details, evidence from both parties, transaction logs |
| 10 | [Optional] Request additional info | Moderator | Send request to either party; 24-hour response window; can be extended once |
| 11 | Moderator makes decision | Moderator | Select outcome: Full Refund, Partial Refund (specify %), Release to Seller, Dismiss |
| 12 | Provide decision rationale | Moderator | Written explanation (mandatory for all decisions) |
| 13 | Execute decision | [System] | Process financial settlement per decision: refund buyer, release to seller, or split |
| 14 | Notify both parties | [System] | Send decision details, rationale, and next steps |
| 15 | [Decision] Appeal filed within 7 days? | — | If appeal → step 16. If no appeal → case closed (step 19) |
| 16 | Appeal filed | Buyer/Seller | Provide new evidence and reason for appeal |
| 17 | Admin reviews appeal | Administrator | Full case review including moderator's decision and new evidence |
| 18 | Admin renders final decision | Administrator | Decision is binding and cannot be appealed further |
| 19 | Close case | [System] | Set status to `CLOSED`, log final outcome, release remaining escrow funds |
| 20 | Update seller/buyer metrics | [System] | Increment dispute counters; if seller exceeds threshold → flag for account review |

### 6.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Response received | Within 48 hours | Step 8 | Step 8 (proceed) |
| Appeal filed | Within 7 days of decision | Step 16 | Step 19 |
| Seller dispute threshold exceeded | > 5 disputes resolved against seller in 30 days | Flag account | Continue |

### 6.5 Expected Outcomes

- **Full Refund:** Buyer receives full amount; seller gets nothing; platform absorbs gateway fees.
- **Partial Refund:** Escrow split per moderator decision (e.g., 70% seller, 30% buyer).
- **Release to Seller:** Seller receives full escrow amount; dispute deemed invalid.
- **Dismissed:** Seller receives funds; buyer with no valid claim.
- **Appeal Upheld/Rejected:** Admin final decision supersedes moderator decision.

### 6.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| Escrow release technical failure | Manual processing by finance team; audit trail maintained |
| Party unresponsive | Proceed after timeout; decision based on available evidence |
| Moderator unavailable | Auto-reassign to next available moderator after 4 hours |
| Evidence upload fails | Accept text-only evidence; log error for support follow-up |
| Dispute filed after escrow period | Block submission; direct to support ticket |

### 6.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Initial response to dispute | < 24 hours | From filing to moderator assignment |
| Evidence collection | < 72 hours | From assignment to decision ready |
| Moderator decision | < 5 business days | From case opened to decision rendered |
| Appeal resolution | < 7 business days | From appeal to final decision |
| Financial settlement execution | < 2 hours post-decision | Backend batch processing |

---

## 7. Withdrawal & Payout Workflow

### 7.1 Overview

This workflow governs how sellers and affiliates request and receive payouts of their available balances.

### 7.2 Workflow Diagram (Textual)

```
Seller/Affiliate → Request Withdrawal → 
    [System] Validate: Balance, KYC, Limits →
        │
        ├── Validation Failed → Reject with Reason
        │
        └── Validation Passed → Finance Queue →
                │
                ├── Finance Approves → Payment Gateway → 
                │       ├── Success → Balance Deducted → Completed
                │       └── Failed → Retry / Notify
                │
                └── Finance Rejects → Release Hold → Balance Restored
```

### 7.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Seller or affiliate clicks "Withdraw" from their financial dashboard |
| **Actors** | Seller, Affiliate, Finance Manager, System, Payment Gateway |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | User initiates withdrawal | Seller/Affiliate | [System] Display current balance, available balance, pending balance |
| 2 | User enters amount and selects payout method | Seller/Affiliate | Amount (must be ≥ minimum threshold), method (Bank, bKash, Nagad, PayPal) |
| 3 | [System] Validate withdrawal | [System] | Check: sufficient available balance, KYC level meets limit, withdrawal frequency not exceeded, amount within daily limit |
| 4 | [Decision] Validation passes? | — | If no → return specific error to user (step 2). If yes → step 5 |
| 5 | Create withdrawal request | [System] | Set status to `PENDING`, deduct amount from available balance and add to `pending_balance`, add to finance queue |
| 6 | Finance manager reviews queue | Finance Manager | View all pending requests sorted by date; each shows user, amount, method, KYC level, historical withdrawal behavior |
| 7 | [Decision] Finance approves? | — | If approve → step 8. If reject → step 12 |
| 8 | Process payment | [System] | Call payout API of selected payment gateway |
| 9 | [Decision] Payment gateway success? | — | If success → step 10. If failure → step 11 |
| 10 | Mark withdrawal completed | [System] | Set status to `COMPLETED`, deduct from pending balance, update ledger, send confirmation to user |
| 11 | Payment gateway failure | [System] | Retry up to 3 times with 5-minute interval; if all fail → set status to `FAILED`, restore balance, notify finance manager |
| 12 | Reject withdrawal | Finance Manager | Select rejection reason (KYC insufficient, suspicious activity, bank details invalid, etc.) |
| 13 | Release hold on funds | [System] | Return amount from pending_balance to available_balance, set status to `REJECTED`, send notification with reason |

### 7.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Validation passes | Balance, KYC, limits all OK | Step 5 | Step 2 (with errors) |
| Finance approves | Manual review passes | Step 8 | Step 12 |
| Gateway success | Payout API returns success | Step 10 | Step 11 |

### 7.5 Expected Outcomes

- **Success:** Funds transferred to seller's external account; platform ledger updated.
- **Rejected:** Funds returned to available balance; seller can correct issue and retry.
- **Failed (Gateway):** Funds returned to available balance; seller retries or chooses different method.

### 7.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| Payout gateway temporarily unavailable | Retry 3 times; if all fail, mark as FAILED and alert finance |
| Invalid bank account details | Finance flags; seller must update payout details and resubmit |
| Duplicate withdrawal request | Idempotency check by request ID; block duplicate |
| Withdrawal exceeds daily limit | Auto-reject with message showing remaining available amount |
| Currency conversion needed | Apply platform exchange rate; show conversion in request preview |

### 7.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Validation & queue entry | < 5 seconds | Real-time |
| Finance review (auto-approved for trusted sellers) | < 2 hours | For sellers with 10+ successful past withdrawals |
| Finance review (manual) | < 48 hours | Queue wait time |
| Payment gateway processing | < 24 hours | From approval to funds sent |
| Failed withdrawal resolution | < 72 hours | From failure to funds restored |

---

## 8. Affiliate Commission Workflow

### 8.1 Overview

This workflow tracks affiliate referrals, attributes sales, calculates commissions, and manages affiliate payouts.

### 8.2 Workflow Diagram (Textual)

```
Affiliate → Generate Referral Link → Share →
    Buyer Clicks Link → Cookie Stored (30-day attribution) →
    Buyer Purchases → Commission Calculation →
        │
        ├── Refund Period Passes (14 days) → Commission Confirmed
        │
        └── Buyer Refunds → Commission Reversed / Adjusted
```

### 8.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | Affiliate generates a referral link from their dashboard |
| **Actors** | Affiliate, Buyer, System, Cookie Store |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | Affiliate logs into dashboard | Affiliate | [System] Authenticate, load affiliate profile and stats |
| 2 | Affiliate generates referral link | Affiliate | Select target (product, store, or general); [System] generate URL with affiliate ID parameter (`?ref=AFF123`) |
| 3 | Affiliate shares link | Affiliate | Copy link, share on social media, blog, email, etc. |
| 4 | Buyer clicks referral link | Buyer | [System] Parse `ref` parameter, set cookie (name `tsbl_ref`, value = affiliate ID, expiry = 30 days) |
| 5 | [Decision] Cookie set successfully? | — | If cookie already exists with different affiliate → keep original (first-touch attribution). If no existing cookie → set new. |
| 6 | Buyer browses and adds to cart | Buyer | [System] Attach cookie reference to cart session |
| 7 | Buyer completes purchase | Buyer | [System] On order completion, look up cookie, match to affiliate |
| 8 | [Decision] Purchase within attribution window? | — | If purchase within 30 days of cookie set → commission eligible. If outside window → no commission |
| 9 | Calculate commission | [System] | Apply commission rate (configurable: % of sale or flat fee); create `affiliate_commission` record with status `PENDING` |
| 10 | Start refund waiting period | [System] | Commission held in pending status for 14 days (matching escrow period) |
| 11 | [Decision] Refund occurred during period? | — | If refund within 14 days → step 12. If no refund → step 13 |
| 12 | Reverse or adjust commission | [System] | If full refund → void commission; if partial refund → recalculate proportionally; set status to `VOIDED` or `ADJUSTED` |
| 13 | Confirm commission | [System] | Set status to `CONFIRMED`, add to affiliate's available balance |
| 14 | Notify affiliate | [System] | Send notification: "New commission earned — BDT X,XXX from sale of [Product]" |
| 15 | Affiliate views earnings in dashboard | Affiliate | Updated real-time metrics: clicks, conversions, earnings |

### 8.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Cookie attribution | First-touch wins | Set cookie | Keep existing |
| Purchase in attribution window | Within 30 days | Step 9 | No commission |
| Refund during waiting period | Refund processed | Step 12 | Step 13 |

### 8.5 Expected Outcomes

- **Success:** Affiliate receives confirmed commission added to available balance.
- **Voided:** Commission reversed due to refund; affiliate does not earn.
- **No attribution:** Purchase not linked to any affiliate; platform retains full commission.

### 8.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| Cookie blocked by browser | Fallback to URL parameter tracking with session persistence |
| Cookie cleared before purchase | No attribution; inform affiliate that cookie must persist |
| Commission calculation overflow | Cap at maximum commission amount (configurable) |
| Affiliate referred themselves | Detect self-referral pattern; void commission; flag for review |

### 8.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Commission calculation | < 5 seconds post-order | Real-time event processing |
| Commission confirmation | Exactly 14 days after order | Cron job precision |
| Payout to affiliate | Per Withdrawal workflow | — |

---

## 9. Content Moderation Workflow

### 9.1 Overview

This workflow governs how user-generated content (product listings, reviews, messages, seller profiles, files) is reviewed for compliance with platform policies.

### 9.2 Workflow Diagram (Textual)

```
User Submits Content → System Ingestion →
    Automated Scan (Keywords, NSFW, Plagiarism) →
        │
        ├── Confidence > 95% Violation → Auto-Reject → Notify User
        │
        ├── Confidence 70-94% → Flag for Manual Review →
        │       ├── Moderator Approves → Publish
        │       └── Moderator Rejects → Reject + Notify
        │
        └── Confidence < 70% Clean → Auto-Approve → Publish
                │
                └── User Reports → Flag Published Content → Manual Review
```

### 9.3 Workflow Details

| Field | Description |
|-------|-------------|
| **Trigger** | User submits content (product listing, review, file upload, profile update, message) |
| **Actors** | User, System (ML/rules engine), Moderator |

| Step | Description | Actor | System Action |
|------|-------------|-------|---------------|
| 1 | User submits content | User | [System] Accept content, assign content type and ID, initiate moderation pipeline |
| 2 | Keyword scanning | [System] | Match against blacklist of prohibited terms; score 0-100 |
| 3 | Image/Media scanning | [System] | NSFW detection via ML model; text extraction via OCR for embedded text scanning |
| 4 | Plagiarism/duplicate check | [System] | Compare against existing platform content; flag if > 80% match |
| 5 | Metadata validation | [System] | Check category appropriateness, pricing sanity (e.g., BDT 100,000 for a PDF), seller reputation score |
| 6 | Calculate composite confidence score | [System] | Weighted average of all scan results |
| 7 | [Decision] Score > 95% violation? | — | If score ≥ 95 → step 8. If 70-94 → step 9. If < 70 → step 11 |
| 8 | Auto-reject content | [System] | Block content, set status to `REJECTED`, notify user with generic policy citation (not specific ML findings), log for ML training |
| 9 | Flag for manual review | [System] | Add to moderator queue with priority score, highlight specific concerns from scans |
| 10 | Moderator reviews content | Moderator | Review content in moderation interface; see scan results as guidance |
| 11 | [Decision] Moderator action? | — | Approve → step 12. Reject → step 13. Request revision → step 14 |
| 12 | Publish content | [System] | Set status to `PUBLISHED` or `ACTIVE`, make visible to appropriate audience, index for search |
| 13 | Reject content | Moderator | Select rejection reason, provide explanation (optional for user), set status to `REJECTED`, notify user |
| 14 | Request revision | Moderator | Send revision request to user with specific feedback, set status to `REVISION_REQUIRED` |
| 15 | User revises and resubmits | User | → Returns to step 1; previous moderation results are cleared for fresh evaluation |
| 16 | [Post-Publish] User reports content | User | Flagged content enters moderation queue with "Reported" tag for expedited review |
| 17 | [Post-Publish] Moderator removes content | Moderator | Set status to `REMOVED`, notify original author, log reason |

### 9.4 Decision Points Summary

| Decision | Criteria | Yes Path | No Path |
|----------|----------|----------|---------|
| Auto-reject threshold | Score ≥ 95 | Step 8 | Check next threshold |
| Manual review threshold | Score 70-94 | Step 9 | Step 11 (auto-approve) |
| Moderator action | Approve/Reject/Revise | Respective step | — |
| User report filed | Report submitted | Step 16 | Content remains |

### 9.5 Expected Outcomes

- **Auto-Approve:** Content published immediately; no manual touch needed.
- **Auto-Reject:** Content blocked; user notified; no human review capacity wasted.
- **Manual Approve:** Moderator confirms content is compliant.
- **Manual Reject:** Content blocked with feedback.
- **Post-Publish Removal:** Content taken down after community flagging.

### 9.6 Error Handling

| Error Condition | Handling Procedure |
|-----------------|-------------------|
| ML service unavailable | Bypass auto-moderation; send all content to manual queue; alert ops team |
| OCR fails on image | Flag for manual review; skip text-based scanning |
| False positive (auto-reject) | Affected user can appeal via support ticket; appeal restores content pending manual review |
| False negative (bad content published) | Rely on community reporting and periodic re-scanning; expedite removal on report |

### 9.7 SLA Targets

| Milestone | Target | Measurement |
|-----------|--------|-------------|
| Auto-moderation decision | < 10 seconds | From submission to auto-action |
| Manual review (standard) | < 24 hours | Queue wait time |
| Manual review (reported/flagged) | < 4 hours | Priority queue |
| User appeal response | < 48 hours | Support ticket SLA |

---

## Appendix A: Workflow Dependency Matrix

| Workflow | Depends On | Triggers |
|----------|------------|----------|
| Registration & Onboarding | — | Product Listing (seller), Order Fulfillment (buyer) |
| Product Listing & Approval | Registration (seller role) | Content Moderation |
| Order Fulfillment | Registration (buyer), Product Listing | Payment & Escrow, Digital Delivery |
| Payment & Escrow Settlement | Order Fulfillment | Withdrawal & Payout, Dispute Resolution |
| Dispute Resolution | Order Fulfillment | Refund processing |
| Withdrawal & Payout | Payment & Escrow (settled), Affiliate Commission | — |
| Affiliate Commission | Registration (affiliate role), Order Fulfillment | Withdrawal & Payout |
| Content Moderation | All content creation workflows | — |

---

## Appendix B: Global SLA Summary

| Workflow | Critical SLA | Standard SLA |
|----------|-------------|--------------|
| Registration & Onboarding | Email verification: < 10 s | KYC review: < 48 h |
| Product Listing & Approval | Auto-moderation: < 30 s | Manual review: < 24 h |
| Order Fulfillment | Payment: < 30 s | Escrow release: 14 days |
| Payment & Escrow Settlement | Webhook processing: < 5 s | Reconciliation: < 2 h (EOD) |
| Dispute Resolution | Moderator assignment: < 24 h | Resolution: < 5 business days |
| Withdrawal & Payout | Validation: < 5 s | Finance processing: < 48 h |
| Affiliate Commission | Calculation: < 5 s | Confirmation: 14 days |
| Content Moderation | Auto-decision: < 10 s | Manual review: < 24 h |

---

*End of Document — TRUE STAR BD LIMITED*

---

**Document Status:** Draft  
**Next Review:** 2026-07-15  
**Change Control:** All changes require approval by the Product Owner and Chief Architect.
