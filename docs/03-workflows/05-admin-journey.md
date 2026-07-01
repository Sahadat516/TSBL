# Admin Journey: Operations & Governance

**Document Version:** 1.0  
**Status:** Final  
**Last Updated:** 2026-07-01  
**Owner:** Platform Operations  

---

## 1. Journey Overview

The TSBL administrator journey covers platform governance, user management, financial oversight, content moderation, and system configuration. This document provides step-by-step procedures, decision criteria, and expected outcomes for all critical admin workflows.

```
                ADMIN RESPONSIBILITY DOMAINS

   ┌─────────────────────────────────────────────────────────────┐
   │                  TSBL ADMINISTRATION                        │
   ├──────────────┬──────────────┬───────────────┬──────────────┤
   │  User Mgmt   │   Content    │   Financial    │  System      │
   │  • Create     │   • Listing  │   • Escrow     │  • Config   │
   │  • Suspend    │     Review   │   • Disputes   │  • RBAC     │
   │  • Ban        │   • Flagging │   • Payouts    │  • Audit    │
   │  • Restore    │   • Appeal   │   • Refunds    │  • Reports  │
   └──────────────┴──────────────┴───────────────┴──────────────┘
```

---

## 2. Administrator Dashboard

### 2.1 Dashboard Layout

```
                ADMIN DASHBOARD — HOME VIEW

   ┌──────────────────────────────────────────────────────────────┐
   │  🔍 Search users, orders, listings...    [Notifications 🔔]  │
   ├──────────────────────────────────────────────────────────────┤
   │  ╔══════════╗ ╔══════════╗ ╔══════════╗ ╔══════════╗       │
   │  ║ Total    ║ ║ Active   ║ ║ Pending  ║ ║ Open     ║       │
   │  ║ Users    ║ ║ Sellers  ║ ║ Disputes ║ ║ Tickets  ║       │
   │  ║ 12,450   ║ ║ 2,180    ║ ║ 47       ║ ║ 23       ║       │
   │  ╚══════════╝ ╚══════════╝ ╚══════════╝ ╚══════════╝       │
   ├──────────────────────────────────────────────────────────────┤
   │  ╔══════════════════════════════════════════════════════════╗│
   │  ║  Revenue (MTD)    $1.2M    ▲ 18% vs last month          ║│
   │  ║  Transactions     18,450   ▲ 12% vs last month          ║│
   │  ║  Avg. Order Value $65.04   ▲ 5% vs last month           ║│
   │  ║  Pending Payouts  $340K    28 sellers awaiting           ║│
   │  ╚══════════════════════════════════════════════════════════╝│
   ├──────────────────────────────────────────────────────────────┤
   │  Recent Activity                                [View All]   │
   │  ┌─────────────────────────────────────────────────────────┐│
   │  │ 🟢 New seller registered:  S. Alam (Silver)     2m ago ││
   │  │ 🔴 Dispute filed:          TSBL-23891           5m ago ││
   │  │ 🟡 Listing flagged:         "Premium Watch"     12m ago││
   │  │ 🟢 Payout completed:       M. Rahman ($1,240)   18m ago││
   │  │ 🟠 Ticket escalated:       #TK-4821             25m ago││
   │  └─────────────────────────────────────────────────────────┘│
   ├──────────────────────────────────────────────────────────────┤
   │  Quick Actions:                                              │
   │  [Manage Users] [Disputes] [Moderation Queue] [Payouts]     │
   │  [Reports] [System Settings] [Audit Log]                    │
   └──────────────────────────────────────────────────────────────┘
```

### 2.2 Navigation Structure

```
   ADMIN NAVIGATION TREE

   Dashboard
   ├── User Management
   │   ├── All Users
   │   ├── Buyers
   │   ├── Sellers
   │   ├── Pending Verification
   │   ├── Suspended/Banned
   │   └── Roles & Permissions (RBAC)
   ├── Content Moderation
   │   ├── Listing Queue
   │   ├── Review Queue
   │   ├── Reported Content
   │   └── Appeal Centre
   ├── Financial Oversight
   │   ├── Transaction Log
   │   ├── Escrow Management
   │   ├── Payout Processing
   │   ├── Dispute Resolution
   │   ├── Refund Log
   │   └── Commission Reports
   ├── System Configuration
   │   ├── General Settings
   │   ├── Commission Tiers
   │   ├── Payment Gateways
   │   ├── Shipping Zones
   │   ├── Feature Flags
   │   └── Email Templates
   ├── Analytics & Reports
   │   ├── Real-Time Dashboard
   │   ├── Custom Reports
   │   ├── Export Center
   │   └── Scheduled Reports
   ├── Support Management
   │   ├── Ticket Queue
   │   ├── FAQ Management
   │   ├── Escalation Matrix
   │   └── CSAT Reports
   └── Audit & Compliance
       ├── Audit Log
       ├── Compliance Reports
       ├── Data Export (GDPR)
       └── Security Events
```

---

## 3. User Management Workflows

### 3.1 User Lifecycle State Machine

```
              USER ACCOUNT STATE DIAGRAM

                    ┌─────────────┐
                    │  Pending    │
                    │  Verification│
                    └──────┬──────┘
                           │ Verified
                           ▼
                    ┌─────────────┐
           ┌──────> │   Active    │ <──────┐
           │        └──────┬──────┘        │
           │               │                │
      Suspended        Suspended         Restored
           │               │                │
           ▼               ▼                │
   ┌─────────────┐  ┌─────────────┐         │
   │  Suspended  │  │   Banned    │─────────┘
   │  (Temporary)│  │ (Permanent) │  (If wrongful ban)
   └──────┬──────┘  └─────────────┘
          │ Restored              │
          ▼                       ▼
     ┌─────────┐           ┌──────────┐
     │ Active  │           │ Archive  │
     └─────────┘           │ (Deleted)│
                           └──────────┘
```

### 3.2 Create User (Admin-Proxied)

| Step | Action | System Process | Validation |
|---|---|---|---|
| 1 | Navigate to Users → Create New | Form renders with role dropdown | Admin auth token validated |
| 2 | Enter user details (name, email, phone, role) | User service → validation layer | Email format, phone regex, uniqueness check |
| 3 | Select initial status (Active/Pending Verification) | Status enum assigned | Must match role requirements |
| 4 | Assign default permissions | RBAC service → role-permission mapping | Role must exist in role registry |
| 5 | Submit | User created with hashed temp password | Confirmation email sent to user |
| 6 | Notify user | Email service → welcome + set-password link | Delivery receipt logged |

**Decision Criteria:**
- Only `super_admin` and `user_manager` roles can create users
- Seller accounts require additional KYC documentation (cannot be bypassed via admin creation)
- Temp passwords expire in 24 hours

**Expected Outcome:** User exists in `users` table with correct role_id, status, and audit trail entry.

### 3.3 Suspend User (Temporary)

| Step | Action | System Process | Validation |
|---|---|---|---|
| 1 | Locate user via search or user list | User service → DB query | User must exist and be Active |
| 2 | Click "Suspend" action | Confirmation dialog appears | N/A |
| 3 | Select reason from predefined list | Enum: Payment/Policy/Spam/Abuse/Other | Required field |
| 4 | Set suspension duration (24h/7d/14d/30d/Custom) | End-date calculation | Max 90 days without super_admin approval |
| 5 | Add internal notes (mandatory) | Audit log entry created | Min 20 chars |
| 6 | Confirm suspension | User service → status = suspended | All active sessions revoked |
| 7 | Notify user | Email: suspension notice + duration + appeal instructions | Delivery receipt |

**Decision Criteria:**
- Payment disputes: suspend after 3 missed payments
- Policy violation: suspension duration proportional to severity
- Automated fraud detection triggers: immediate 24h hold pending manual review
- Seller with pending payouts: escrow held until resolution

**Expected Outcome:** User unable to log in. Active listings hidden (sellers). Pending orders enter admin review. Audit log records all actions.

### 3.4 Ban User (Permanent)

| Step | Action | System Process | Validation |
|---|---|---|---|
| 1 | Verify suspension history (≥2 prior suspensions) | User history report | Required for non-emergency bans |
| 2 | Escalate to super_admin for approval | Approval workflow initiated | Second admin required |
| 3 | Select ban reason + upload evidence | Document service → evidence folder | Files scanned for malware |
| 4 | Execute ban | User service → status = banned | Cascade: cancel pending orders, release escrow to affected parties |
| 5 | Final notification | Email + SMS: permanent ban + data retention notice | Proof of delivery stored |
| 6 | Archive user data | Data service → anonymisation after 90 days | GDPR compliance flag |

**Decision Criteria:**
- Fraud, identity theft, illegal goods: immediate ban without prior suspension
- Repeated IP infringement: ban after 3 verified DMCA violations
- Platform abuse: subject to ban review committee
- Banned users cannot re-register (phone + ID + device fingerprint blacklist)

**Expected Outcome:** User permanently disabled. All active transactions halted. Data queued for archival.

### 3.5 Restore User

| Step | Action | System Process | Validation |
|---|---|---|---|
| 1 | Review appeal or admin decision to restore | Appeal form or manual trigger | Appeal must be within 30 days of action |
| 2 | Verify restoration eligibility | Check suspension/ban reason + time elapsed | Some violations are non-reversible (fraud, illegal) |
| 3 | Approve restoration | User service → status = active | Previously suspended only (not banned without special override) |
| 4 | Reinstate listings/access | Listing service → re-publish | Inventory levels verified |
| 5 | Notify user of restoration | Email + dashboard notification | Include any probation terms |

**Decision Criteria:**
- First-time suspension: automatic restoration at end of term
- Second suspension: restoration requires admin review
- Banned users: only reversible by super_admin + compliance officer joint approval
- Probation period applied to restored users (30–90 days of heightened monitoring)

**Expected Outcome:** User regains platform access with prior data intact. Audit log records restoration event.

---

## 4. Content Moderation Workflows

### 4.1 Moderation Queue Prioritisation

```
           MODERATION QUEUE PRIORITY MATRIX

   ┌──────────────┬──────────────────────────────────────┐
   │ Priority     │ Criteria                             │
   ├──────────────┼──────────────────────────────────────┤
   │ 🔴 Critical  │ • NSFW/illegal content               │
   │  (SLA: 15m)  │ • Hate speech                        │
   │              │ • Counterfeit / IP infringement       │
   │              │ • Dangerous goods                    │
   ├──────────────┼──────────────────────────────────────┤
   │ 🟡 High      │ • Misleading product claims          │
   │  (SLA: 1h)   │ • Prohibited items (alcohol, tobacco)│
   │              │ • Price manipulation                 │
   │              │ • Fake reviews                       │
   ├──────────────┼──────────────────────────────────────┤
   │ 🟢 Medium    │ • Low-quality images                 │
   │  (SLA: 4h)   │ • Incomplete descriptions            │
   │              │ • Wrong category                     │
   │              │ • Duplicate listings                 │
   ├──────────────┼──────────────────────────────────────┤
   │ ⚪ Low       │ • Minor formatting issues            │
   │  (SLA: 24h)  │ • Keyword stuffing                   │
   │              │ • Missing metadata                   │
   └──────────────┴──────────────────────────────────────┘
```

### 4.2 Listing Moderation Workflow

| Step | Action | System Interaction | Decision Point |
|---|---|---|---|
| 1 | Review queued item | Moderation queue → pulls next item | Auto-priority sorted |
| 2 | Examine product details | Title, description, images, price, category | Does it violate TOS? |
| 3 | Check seller history | Seller profile → prior violations, tenure | Pattern of violations? |
| 4 | Run image analysis | AI moderation tool (NSFW, text overlay, watermark) | Auto-flag if >90% confidence |
| 5 | Decision | Approve / Reject / Request Revision | See criteria below |
| 6 | Execute action | Listing status updated | Notification sent to seller |
| 7 | Log decision | Audit entry with admin ID + timestamp | Required for compliance |

**Decision Criteria Matrix:**

| Violation Type | Action | Seller Notification | Escalation |
|---|---|---|---|
| NSFW content | Immediate reject + strike | Strike 1 of 3 warning | 3 strikes → account review |
| Counterfeit | Reject + suspend seller | Account suspended pending investigation | Legal team notified |
| Misleading claims | Request revision | 48h to revise or auto-reject | Seller can appeal |
| Category mismatch | Auto-reassign or request edit | Suggested category shown | N/A |
| Low-quality image | Soft reject (can resubmit) | Image guidelines provided | N/A |

### 4.3 Review Moderation Workflow

| Step | Action | System Process | Decision Point |
|---|---|---|---|
| 1 | Review reported review | Reported content queue → review text + product | Is review fake, abusive, or off-topic? |
| 2 | Verify purchase | Check order DB → confirmed delivery | Unverified reviews have lower weight |
| 3 | Check for pattern | Same buyer reviewing same seller multiple times | Coordinated attack? |
| 4 | Decide | Keep / Remove / Flag for investigation | See criteria |
| 5 | Notify parties | Buyer + seller get result notification | If removed, reason provided |

**Decision Criteria:**
- Remove: hate speech, competitor bashing, personal info, spam
- Keep: negative but honest feedback, constructive criticism
- Flag: borderline content for senior moderator review

### 4.4 Appeal Processing

```
             APPEAL RESOLUTION WORKFLOW

   Seller/Buyer Appeals Moderation Decision
          │
          ▼
   ┌──────────────────────────────────┐
   │ 1. Appeal logged + ticket created│
   │    SLA for first response: 24h   │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ 2. Admin reviews original        │
   │    decision + new evidence       │
   └──────────┬───────────────────────┘
              │
        ┌─────┴──────┐
        │            │
    Uphold         Overturn
        │            │
        ▼            ▼
   ┌─────────┐  ┌────────────────┐
   │ Original │  │ Listing/Review │
   │ Decision │  │ Restored       │
   │ Stands   │  │ + Strike       │
   └─────────┘  │ Removed        │
           │    └────────────────┘
           ▼
   ┌──────────────────────────────────┐
   │ Final notification to appellant  │
   │ • Uphold: reason + finality      │
   │ • Overturn: apology + resolution │
   └──────────────────────────────────┘
```

---

## 5. Financial Oversight

### 5.1 Transaction Monitoring

```
                TRANSACTION MONITORING DASHBOARD

   ┌──────────────────────────────────────────────────────────────┐
   │  Transaction Volume (Last 24h): 842 orders                   │
   │  Total Volume: $54,230        ▲ 8% vs yesterday              │
   ├──────────────────────────────────────────────────────────────┤
   │  ⚠️ Anomalies Detected (4):                                   │
   │  ┌──────┬────────────┬───────────┬────────────┬───────────┐ │
   │  │ #    │ TX ID      │ Amount    │ Anomaly    │ Status    │ │
   │  ├──────┼────────────┼───────────┼────────────┼───────────┤ │
   │  │ 1    │ TX-48291   │ $12,400   │ Amount spike│ 🔍 Review │ │
   │  │ 2    │ TX-48293   │ $0.01×50  │ Pattern    │ ⏳ Pending│ │
   │  │ 3    │ TX-48312   │ $9,800    │ New seller │ 🔍 Review │ │
   │  │ 4    │ TX-48345   │ $5,200    │ Geo-mismatch│ ⏳ Pending│ │
   │  └──────┴────────────┴───────────┴────────────┴───────────┘ │
   └──────────────────────────────────────────────────────────────┘
```

### 5.2 Escrow Management

| Concept | Detail | System Process |
|---|---|---|
| Escrow trigger | Order payment confirmed | Payment service → escrow account |
| Hold duration | T+0 (digital) / T+3 (physical) / T+7 (custom) | Timer service tracking |
| Release trigger | Buyer confirmation OR auto-confirm after hold | Fulfillment service → escrow release |
| Partial release | Multi-item orders: per-item release supported | Item-level fulfillment tracking |
| Dispute hold | Funds frozen until dispute resolved | Dispute service → escrow lock |

### 5.3 Escrow Release Flow

```
                 ESCROW RELEASE DECISION TREE

   Order Delivered
          │
          ▼
   ┌──────────────────┐           ┌──────────────────┐
   │ Buyer Confirms?  │──YES──>  │ Fund Released to  │
   └────────┬─────────┘          │ Seller (T+1/3/7)  │
            │ NO                  └──────────────────┘
            ▼
   ┌──────────────────┐
   │ Auto-Confirm      │
   │ Timer Expired      │
   │ (T+3/7 days)      │
   └────────┬─────────┘
            │
      ┌─────┴──────┐
      │            │
   No Dispute    Dispute Filed
      │            │
      ▼            ▼
   ┌────────┐  ┌──────────────────┐
   │ Release│  │ Hold → Admin     │
   │ to     │  │ Review →         │
   │ Seller │  │ Decision         │
   └────────┘  └──────────────────┘
```

### 5.4 Payout Processing

| Step | Action | System Process | Validation |
|---|---|---|---|
| 1 | Review pending payout queue | Financial dashboard → Payouts tab | Auto-sorted by tier (Platinum first) |
| 2 | Verify payout eligibility | Seller must have completed orders, no holds | Compliance check: AML screening |
| 3 | Batch creation | System creates payout batches by payment method | Bank batch / Mobile wallet batch |
| 4 | Review large payouts (>$5,000) | Manual review flag triggered | Additional KYC check |
| 5 | Approve batch | Payout service → payment gateway API | Idempotency key prevents duplicates |
| 6 | Monitor settlement | Payment gateway callback → status update | Success/Fail per transaction |
| 7 | Handle failures | Automatic retry (×3) → manual intervention | Notify seller + update dashboard |

### 5.5 Dispute Resolution (Admin View)

| Phase | Steps | Admin Actions | SLA |
|---|---|---|---|
| Intake | Dispute filed → admin assigned | Review case details, claim amount, evidence | <1h |
| Evidence gathering | Both parties submit within 48h | Request missing docs, extend if needed | 48h |
| Investigation | Cross-reference order, messages, tracking | Check internal logs, delivery proof, chat history | 24h |
| Decision | Rule in favour of buyer / seller / split | Select outcome, write decision rationale | 48h |
| Execution | Refund/release applied | Trigger payment reversal or escrow release | <1h of decision |
| Appeal | Losing party appeals (7-day window) | Escalate to senior admin for fresh review | 72h |

**Decision Criteria:**

| Scenario | Buyer Evidence | Seller Evidence | Recommended Outcome |
|---|---|---|---|
| Item not received | Tracking shows delivered | Proof of delivery signature | Seller wins |
| Item not as described | Photo evidence differs from listing | Listing screenshots match | Buyer wins |
| Defective item | Video proof of defect | No prior return history | Buyer wins (seller takes return) |
| Buyer's remorse | "Changed mind" | Listing + description accurate | Seller wins (no forced refund) |
| Both share fault | Partial evidence | Partial evidence | Split refund (50/50) |

### 5.6 Refund Processing

| Type | Trigger | Flow | Financial Impact |
|---|---|---|---|
| Full refund | Buyer wins dispute OR seller agrees | Payment gateway reversal → escrow release to buyer | Seller forfeits payment + commission refunded |
| Partial refund | Mutual agreement OR admin split decision | Proportional reversal | Partial commission retained |
| Replacement | Seller offers replacement | New order created at $0 | No financial impact |
| Platform-guaranteed refund | Buyer protection claim | TSBL covers from guarantee fund | Charge against operations |

---

## 6. System Configuration & Settings

### 6.1 Configuration Categories

```
            SYSTEM CONFIGURATION TREE

   General Settings
   ├── Platform name, logo, favicon
   ├── Default language, timezone, currency
   ├── Maintenance mode (on/off + message)
   └── Terms of service version / last updated

   Commission Engine
   ├── Tier definitions (criteria, rates)
   ├── Promotional commission overrides
   ├── Category-specific rates
   └── Minimum commission floor ($0.50)

   Payment Gateways
   ├── Gateway enable/disable
   ├── Credential management (encrypted)
   ├── Fallback routing priority
   └── Test mode / live mode toggle

   Shipping Configuration
   ├── Zone definitions (domestic, SAARC, international)
   ├── Courier partner management
   ├── Rate tables
   └── Tracking provider API keys

   Feature Flags
   ├── Guest checkout enable
   ├── Seller tier auto-promotion
   ├── Multi-language support
   ├── Subscription module
   └── Flash sale engine
```

### 6.2 Commission Tier Configuration

| Field | Type | Validation | Description |
|---|---|---|---|
| Tier name | String (enum) | Must be unique | Bronze/Silver/Gold/Platinum |
| Min. orders | Integer | ≥ 0 | Order count threshold |
| Min. rating | Decimal (2,1) | 1.0–5.0 | Average rating threshold |
| Min. completion rate | Decimal (5,2) | 0.00–100.00 | Order completion % |
| Min. GMV | Decimal (12,2) | ≥ 0 | Gross merchandise value |
| Commission rate | Decimal (5,2) | 0.00–50.00 | Per-transaction fee % |
| Payout delay | Integer (days) | 1–30 | Days post-delivery |
| Listing limit | Integer | 0 = unlimited | Max active listings |

### 6.3 Feature Flag Operations

```
          FEATURE FLAG MANAGEMENT

   ┌─────────────────────────────────────────────┐
   │  Feature              │ Status  │ Rollout % │
   │  ───────────────────────────────────────    │
   │  Guest Checkout        │ 🟢 ON   │ 100%     │
   │  Seller Tier Auto-Up   │ 🟢 ON   │ 100%     │
   │  Multi-Language        │ 🔴 OFF  │ —        │
   │  Subscription Module   │ 🟡 BETA │ 5%       │
   │  Flash Sale Engine     │ 🟢 ON   │ 100%     │
   │  Affiliate Programme   │ 🧪 DEV  │ —        │
   │  AI Recommendations    │ 🟢 ON   │ 75%      │
   └─────────────────────────────────────────────┘

   Actions: [Enable] [Disable] [Set Rollout %] [View Impact]
```

---

## 7. Analytics & Reporting

### 7.1 Standard Reports

| Report | Frequency | Data Sources | Key Metrics |
|---|---|---|---|
| Revenue Summary | Daily / MTD / YTD | Transaction service | GMV, net revenue, commission earned |
| User Growth | Weekly | User service | Registrations, activation rate, churn |
| Seller Performance | Monthly | Seller + order services | GMV/seller, tier distribution, top 100 |
| Buyer Behaviour | Monthly | Analytics pipeline | LTV, repeat rate, category preferences |
| Dispute Analysis | Weekly | Dispute service | Dispute rate, resolution time, outcome ratios |
| Content Moderation | Weekly | Moderation queue | Queue volume, SLA adherence, appeal rate |
| Payment Reconciliation | Daily | Payment gateway + order service | Settled vs pending, failure rate, chargebacks |
| Fraud Detection | Real-time | Fraud engine | Flag rate, false positive rate, blocked amount |

### 7.2 Custom Report Builder

```
                  REPORT BUILDER INTERFACE

   ┌────────────────────────────────────────────────────────────┐
   │  Report Name:  [___________________]                       │
   │                                                             │
   │  Data Source:  [▼ Select source]                            │
   │    • Orders • Users • Listings • Payments • Disputes       │
   │                                                             │
   │  Dimensions:  [▼ Add dimension]                             │
   │    + Date • Category • Tier • Region • Payment Method      │
   │                                                             │
   │  Metrics:     [▼ Add metric]                                │
   │    + GMV • Count • Avg. Value • Rate • Commission          │
   │                                                             │
   │  Filters:     [▼ Add filter]                                │
   │    + Date Range • Min Value • Status                        │
   │                                                             │
   │  [Generate] [Save Template] [Schedule] [Export (CSV/PDF)]  │
   └────────────────────────────────────────────────────────────┘
```

### 7.3 Scheduled Report Distribution

| Schedule | Report | Recipients | Format |
|---|---|---|---|
| Daily (08:00) | Yesterday's Revenue, Top Sellers | Ops team, Finance | Email (PDF) |
| Weekly (Mon 09:00) | User Growth, Moderation Stats | Product, Community | Email (CSV + PDF) |
| Monthly (1st) | Full Business Review | Exec team, Board | Email (PDF + slide deck) |
| Quarterly | Compliance & Audit Report | Compliance, Legal | Encrypted email (PDF) |

---

## 8. Role Management (RBAC)

### 8.1 Role Hierarchy

```
               ADMIN ROLE HIERARCHY

   ┌─────────────────────────────────────────────────────┐
   │                 super_admin                          │
   │            (Full system access)                      │
   └──────────┬────────────────────┬────────────────────┘
              │                    │
   ┌──────────▼──────┐   ┌────────▼────────┐
   │  ops_manager    │   │  compliance_officer │
   │ (Operations)    │   │  (Audit & Legal)    │
   └──────────┬──────┘   └────────┬────────┘
              │                    │
   ┌──────────┼──────────┐        │
   │          │          │        │
   ▼          ▼          ▼        ▼
 ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
 │user  │ │content │ │finance │ │audit_viewer  │
 │mgr   │ │mod     │ │mgr     │ │(Read-only)   │
 └──────┘ └────────┘ └────────┘ └──────────────┘
```

### 8.2 Permission Matrix

| Module | super_admin | ops_manager | compliance | user_mgr | content_mod | finance_mgr | audit_viewer |
|---|---|---|---|---|---|---|---|
| User Create | ✓ | ✓ | — | ✓ | — | — | — |
| User Suspend | ✓ | ✓ | ✓ | ✓ | — | — | — |
| User Ban | ✓ | — | ✓ | — | — | — | — |
| User Restore | ✓ | ✓ | ✓ | ✓ | — | — | — |
| Listing Approve | ✓ | ✓ | — | — | ✓ | — | — |
| Listing Reject | ✓ | ✓ | — | — | ✓ | — | — |
| Review Remove | ✓ | ✓ | ✓ | — | ✓ | — | — |
| Transaction View | ✓ | ✓ | ✓ | — | — | ✓ | ✓ |
| Payout Approve | ✓ | ✓ | — | — | — | ✓ | — |
| Dispute Decide | ✓ | ✓ | ✓ | — | — | — | — |
| Refund Issue | ✓ | ✓ | ✓ | — | — | ✓ | — |
| Config Edit | ✓ | ✓ | — | — | — | — | — |
| Feature Flags | ✓ | ✓ | — | — | — | — | — |
| Report Create | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Audit Log View | ✓ | ✓ | ✓ | — | — | — | ✓ |
| Role Assign | ✓ | — | — | — | — | — | — |

### 8.3 Role Creation / Edit Workflow

| Step | Action | Validation | Outcome |
|---|---|---|---|
| 1 | Navigate to Settings → Roles → Create Role | super_admin only | Form renders |
| 2 | Name the role (e.g., "support_agent_l2") | Unique, alphanumeric + underscores | Role stub created |
| 3 | Select permissions from module checklist | At least 1 permission required | Permission set saved |
| 4 | Assign user scope (all / department) | Must not exceed creator's scope | Scope constraint enforced |
| 5 | Save + confirm | Audit log entry created | Role available for assignment |

---

## 9. Support Ticket Escalation

### 9.1 Escalation Matrix

```
                TICKET ESCALATION PATH

   Tier 1 (Chatbot / AI)
   ├── Resolves: 65% of tickets
   │   • Password reset, order status, tracking info
   │   • FAQ responses, policy lookups
   └── Escalates to Tier 2: 35%

   Tier 2 (Support Agent)
   ├── Resolves: 25% of tickets (71% of T2 intake)
   │   • Refund requests, dispute filing assistance
   │   • Seller onboarding help, basic technical issues
   └── Escalates to Tier 3: 10%

   Tier 3 (Admin / Specialist)
   ├── Resolves: 5% of tickets (50% of T3 intake)
   │   • Account suspensions, payment gateway failures
   │   • Complex disputes, policy exceptions
   └── Escalates to Tier 4: 50%

   Tier 4 (super_admin / Engineering)
   ├── Resolves: 2.5% of tickets
   │   • Data integrity issues, security incidents
   │   • Legal escalations, platform-wide outages
   └── Post-mortem required for all Tier 4 resolutions
```

### 9.2 Escalation Triggers

| Trigger | From | To | Condition |
|---|---|---|---|
| Automated threshold | Tier 1 | Tier 2 | 3 failed AI attempts OR sentiment = angry |
| Agent request | Tier 2 | Tier 3 | Requires permissions agent lacks |
| Timeout | Tier 2 | Tier 3 | Ticket age > 48h without resolution |
| Financial ceiling | Tier 3 | Tier 4 | Refund/dispute > $5,000 |
| Security event | Any | Tier 4 + Engineering | Fraud, breach, data leak report |
| Legal requirement | Tier 3 | Tier 4 | Subpoena, DMCA, law enforcement |

---

## 10. Emergency Response Procedures

### 10.1 Severity Classification

| Severity | Definition | Response SLA | Examples |
|---|---|---|---|
| **SEV-1** | Platform down / payment processing halted | <15 min response, <2h fix | Site crash, payment gateway failure, database outage |
| **SEV-2** | Major feature impairment, significant revenue impact | <30 min response, <4h fix | Search down, cart not working, login failure |
| **SEV-3** | Partial feature impairment, isolated impact | <2h response, <24h fix | Slow search, UI bug, specific gateway issue |
| **SEV-4** | Minor issue, cosmetic, no revenue impact | <24h response, next release | Typo, alignment issue, non-critical error message |

### 10.2 SEV-1 Response Protocol

```
              SEV-1 EMERGENCY RESPONSE

   ┌──────────────────────────────────────────────┐
   │ 1. DETECT                                      │
   │    • Automated monitoring alert               │
   │    • User-reported via social / support       │
   │    • Internal team discovery                  │
   └──────────┬───────────────────────────────────┘
              │ <5 min
              ▼
   ┌──────────────────────────────────────────────┐
   │ 2. DECLARE                                    │
   │    • Declare SEV-1 in incident channel        │
   │    • Notify: super_admin + Engineering Lead   │
   │    • Post platform status: "Investigating"    │
   └──────────┬───────────────────────────────────┘
              │ <10 min
              ▼
   ┌──────────────────────────────────────────────┐
   │ 3. TRIAGE                                     │
   │    • Determine scope (all users / segment)   │
   │    • Identify affected services              │
   │    • Decide: fix vs. rollback vs. mitigation │
   └──────────┬───────────────────────────────────┘
              │ <30 min
              ▼
   ┌──────────────────────────────────────────────┐
   │ 4. RESPOND                                    │
   │    • Execute fix / rollback                   │
   │    • Update status page every 15 min          │
   │    • Communicate ETA to stakeholders          │
   └──────────┬───────────────────────────────────┘
              │ Until resolved
              ▼
   ┌──────────────────────────────────────────────┐
   │ 5. RESOLVE                                    │
   │    • Verify fix in staging → deploy to prod  │
   │    • Monitor for 30 min post-fix              │
   │    • Update status: "Resolved"                │
   └──────────┬───────────────────────────────────┘
              │ <24h post-resolution
              ▼
   ┌──────────────────────────────────────────────┐
   │ 6. POST-MORTEM                                │
   │    • Root cause analysis document             │
   │    • Timeline reconstruction                  │
   │    • Action items with owners + deadlines     │
   │    • Share with all admin team                │
   └──────────────────────────────────────────────┘
```

### 10.3 Emergency Contact Tree

```
              ADMIN EMERGENCY CONTACT TREE

   ┌────────────────────────────────┐
   │  Incident Detected             │
   └──────────────┬─────────────────┘
                  │
                  ▼
   ┌────────────────────────────────┐
   │  Tier 1: On-Call Admin         │
   │  Response SLA: 15 min          │
   │  Can resolve: SEV-3, SEV-4     │
   └──────────────┬─────────────────┘
                  │ If SEV-1/SEV-2 or escalation needed
                  ▼
   ┌────────────────────────────────┐
   │  Tier 2: ops_manager           │
   │  Response SLA: 30 min          │
   │  Can resolve: SEV-2            │
   └──────────────┬─────────────────┘
                  │ If SEV-1 or needs engineering
                  ▼
   ┌────────────────────────────────┐
   │  Tier 3: super_admin + Eng     │
   │  Response SLA: immediate       │
   │  Can resolve: SEV-1            │
   └────────────────────────────────┘
```

---

## 11. Audit Log & Compliance

### 11.1 Audit Log Schema

| Field | Type | Description | Example |
|---|---|---|---|
| `event_id` | UUID | Unique event identifier | `a1b2c3d4-...` |
| `timestamp` | ISO 8601 | Event time with UTC offset | `2026-07-01T14:30:00+06:00` |
| `actor_id` | UUID | Admin user who performed action | `usr_abc123` |
| `actor_role` | String | Role at time of action | `content_mod` |
| `action` | String | Verb describing the action | `USER_SUSPEND` |
| `target_type` | String | Entity type affected | `user`, `listing`, `order` |
| `target_id` | String | ID of affected entity | `usr_xyz789` |
| `details` | JSON | Action-specific payload | `{"reason":"payment_default","duration":"7d"}` |
| `ip_address` | String | Originating IP | `203.76.89.12` |
| `user_agent` | String | Browser/client info | `Mozilla/5.0 ...` |
| `outcome` | String | Success / Failure / Pending | `SUCCESS` |

### 11.2 Mandatory Audit Events

| Event Type | Retention | Compliance Requirement |
|---|---|---|
| User creation / suspension / ban / restore | 7 years | GDPR, regulatory |
| Role creation / modification / deletion | 7 years | SOX, internal |
| Payout approval / rejection | 5 years | Financial audit |
| Dispute decision | 5 years | Legal |
| Listing moderation action | 3 years | Platform policy |
| Review removal | 2 years | Consumer protection |
| Configuration change | 5 years | Change management |
| Refund processing | 5 years | Financial audit |
| Login (admin panel) | 1 year | Security |
| Failed access attempt | 1 year | Security |

### 11.3 Audit Review Workflow

| Step | Action | Frequency | Responsible Role |
|---|---|---|---|
| 1 | Generate audit report for period | Daily / Weekly / Monthly | `audit_viewer` |
| 2 | Sample review: select 5% of events | Weekly | `compliance_officer` |
| 3 | Verify action legitimacy against policy | Per sample | `compliance_officer` |
| 4 | Flag anomalies for investigation | As discovered | `compliance_officer` |
| 5 | Escalate confirmed violations | Within 24h | → `super_admin` |
| 6 | Remediate (undo action if applicable) | Within 48h | `ops_manager` |
| 7 | Document findings | End of review cycle | `compliance_officer` |

**High-Risk Events Requiring Automatic Review:**

- Any user ban lasting >30 days
- Any refund >$1,000
- Any dispute decision overturned on appeal
- Any role permission change for `super_admin`-level access
- Any configuration change to commission rates or payout schedules

### 11.4 Compliance Calendar

| Frequency | Activity | Regulator / Standard |
|---|---|---|
| Daily | Transaction monitoring review | AML |
| Weekly | Suspicious activity report (SAR) check | AML |
| Monthly | Refund & dispute ratio analysis | Internal |
| Quarterly | Data retention audit | GDPR |
| Quarterly | RBAC access review | SOX / SOC2 |
| Bi-Annual | Penetration test | PCI DSS |
| Annual | Security audit | PCI DSS |
| Annual | Privacy impact assessment | GDPR |
| On-demand | Law enforcement data request | Local regulation |

---

## 12. Admin KPI Dashboard

| KPI | Target | Measurement | Review Frequency |
|---|---|---|---|
| Moderation queue SLA adherence | >95% | Timestamps per item | Daily |
| Dispute resolution time (avg) | <72h | Dispute service | Daily |
| Payout processing time (avg) | <24h (Platinum), <7d (Bronze) | Payout service | Daily |
| Ticket first-response time | <1h (Tier 2), <15m (Tier 3) | Support system | Hourly |
| User appeal turnaround | <48h | Appeal queue | Daily |
| Audit review completion | 100% of sampled events | Compliance tracker | Weekly |
| Platform uptime | >99.9% | Monitoring service | Monthly |
| Fraud detection accuracy | >95% precision | Fraud engine | Monthly |
| Admin NPS (internal) | >4.0/5.0 | Internal survey | Quarterly |

---

## 13. Admin Persona Archetypes

| Persona | Primary Domain | Key Tools | Pain Points |
|---|---|---|---|
| Operations Admin | Day-to-day platform mgmt | User mgmt, Moderation, Tickets | High volume of repetitive tasks |
| Financial Controller | Payouts, disputes, reconciliation | Financial dashboard, Escrow | Reconciling cross-gateway discrepancies |
| Compliance Officer | Audit, legal, data privacy | Audit log, GDPR tools, Reports | Keeping up with regulatory changes |
| Content Moderator | Listing & review quality | Moderation queue, Image analysis | Volume spikes during sales events |
| System Administrator | Configuration, feature flags | Settings, RBAC, Feature flags | Change management discipline |
| Executive (super_admin) | Strategic oversight | Dashboard, Reports, Emergency | Balancing access with security |

---

## 14. Admin Journey Optimisation

```
              ADMIN EXPERIENCE IMPROVEMENT CYCLE

   ┌─────────────────────────────────────────────────────────────┐
   │  Efficiency                         Accuracy                │
   │  ┌──────────────────────┐          ┌──────────────────────┐│
   │  │ • Bulk actions       │          │ • Decision checklists ││
   │  │ • Keyboard shortcuts │          │ • AI-assisted review ││
   │  │ • Saved filters      │          │ • Precedent database ││
   │  │ • Quick-action bar   │          │ • Confirmation steps ││
   │  └──────────────────────┘          └──────────────────────┘│
   │                                                             │
   │  Satisfaction                       Compliance              │
   │  ┌──────────────────────┐          ┌──────────────────────┐│
   │  │ • Reduced clicks     │          │ • Auto-logging        ││
   │  │ • Clean UI           │          │ • Mandatory fields    ││
   │  │ • Smart defaults     │          │ • Immutable records   ││
   │  │ • Training resources │          │ • Escalation paths    ││
   │  └──────────────────────┘          └──────────────────────┘│
   └─────────────────────────────────────────────────────────────┘
```

---

**End of Document — Admin Journey v1.0**
