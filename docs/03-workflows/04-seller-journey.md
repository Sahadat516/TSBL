# Seller Journey: End-to-End Lifecycle

**Document Version:** 1.0  
**Status:** Final  
**Last Updated:** 2026-07-01  
**Owner:** Seller Operations  

---

## 1. Journey Overview

The TSBL seller journey spans the complete arc from initial registration through growth and tier advancement. This document details every stage, system interaction, KPI requirement, and revenue optimisation opportunity.

```
                     SELLER LIFECYCLE MAP

  REGISTRATION ──> ONBOARDING ──> LISTING ──> SALES ──> GROWTH
       │              │             │          │          │
       │  Apply       │  Verify     │  List    │  Sell    │  Scale
       │  & Qualify   │  & Setup    │  Products│  & Ship  │  & Excel
       ▼              ▼             ▼          ▼          ▼
   ┌────────┐   ┌──────────┐  ┌─────────┐ ┌────────┐ ┌──────────┐
   │Bronze │   │Tier      │  │Product  │ │Order   │ │Tier      │
   │Applic.│   │Approval  │  │Catalog  │ │Mgmt.   │ │Advance   │
   └────────┘   └──────────┘  └─────────┘ └────────┘ └──────────┘
```

---

## 2. Seller Tier Structure

TSBL operates a four-tier seller hierarchy with progressive benefits and commission rates.

| Tier | Criteria Threshold | Commission Rate | Listing Limit | Payout Speed | Badge |
|---|---|---|---|---|---|
| **Bronze** | New registration | 15% | 50 products | T+7 days | Standard |
| **Silver** | 100 orders, ≥4.2 rating, 98% completion | 12% | 200 products | T+5 days | Silver Verified |
| **Gold** | 500 orders, ≥4.5 rating, 99% completion, $50K GMV | 10% | 1,000 products | T+3 days | Gold Trusted |
| **Platinum** | 2,000 orders, ≥4.7 rating, 99.5% completion, $250K GMV | 8% | Unlimited | T+1 day | Platinum Elite |

### Tier Benefits Matrix

| Benefit | Bronze | Silver | Gold | Platinum |
|---|---|---|---|---|
| Priority support | Standard | Standard | Priority | VIP hotline |
| Featured listing slots | — | 5/month | 20/month | 100/month |
| Analytics dashboard | Basic | Advanced | Premium | Enterprise |
| Marketing toolkit | — | Basic | Advanced | Full suite |
| Dedicated account manager | — | — | Shared | Dedicated |
| Early access to features | — | — | Yes | Yes + beta |
| Dispute protection | Standard | Mediation priority | Seller-favoured review | Final-say privilege |

### Tier Progression Path

```
                SELLER TIER PROGRESSION

   BRONZE ──────────────> SILVER ────────────> GOLD ────────────> PLATINUM
      │                      │                     │                   │
      │  100 orders          │  500 orders          │  2,000 orders    │
      │  4.2★ rating         │  4.5★ rating         │  4.7★ rating     │
      │  98% completion      │  99% completion       │  99.5% completion│
      │                      │  $50K GMV             │  $250K GMV       │
      ▼                      ▼                     ▼                   ▼
  ┌──────────┐         ┌──────────┐          ┌──────────┐        ┌──────────┐
  │  15%     │         │  12%     │          │  10%     │        │   8%     │
  │  Comm.   │         │  Comm.   │          │  Comm.   │        │  Comm.   │
  └──────────┘         └──────────┘          └──────────┘        └──────────┘
```

---

## 3. Stage 1: Registration

### 3.1 Overview
The seller applies to join the TSBL marketplace. Identity verification and business validation occur at this stage.

### 3.2 Application Process

| Step | Action | Data Required | System Interaction |
|---|---|---|---|
| 1 | Account creation | Email, phone, password | User service → Identity DB |
| 2 | Seller profile setup | Legal name, business type, address | Seller service → Seller DB |
| 3 | Identity verification | NID/Passport upload; selfie | KYC API (OCR + liveness check) |
| 4 | Business documentation | TIN, trade license, bank letter | Document service → S3 → Validation queue |
| 5 | Payment configuration | Bank account / Mobile wallet details | Payout service → Payment gateway |
| 6 | Agreement acceptance | Terms of service, commission disclosure | Legal service → Audit log |
| 7 | Application submission | Triggered review workflow | Admin queue → Approval workflow |

### 3.3 KYC Verification Flow

```
                   SELLER VERIFICATION PIPELINE

   Seller Submits Docs
          │
          ▼
   ┌──────────────────┐
   │ Automated Checks  │
   │ • OCR extraction  │
   │ • Face match      │
   │ • Document expiry │
   │ • Sanctions list  │
   └────────┬─────────┘
            │
     ┌──────┴──────┐
     │              │
   PASS            FAIL
     │              │
     ▼              ▼
   ┌──────┐   ┌────────────────┐
   │ Tier │   │ Manual Review  │
   │ Assigned│ │ Queue (SLA: 24h)│
   │ Bronze│   └────────┬───────┘
   └──────┘            │
                  ┌────┴────┐
                  │         │
                PASS       FAIL
                  │         │
                  ▼         ▼
              Approved    Rejected
                          + Reason
```

### 3.4 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| Document rejection without reason | Frustration, churn | Detailed rejection reason + resubmission guidance |
| Slow verification (>48h) | Drop-off (40% abandon) | Automated OCR + human-in-loop SLA |
| Complex business classification | Wrong tier assignment | AI-assisted category suggestion |
| Bank account validation fails | Payout blocking | Micro-deposit verification + instant validation |

### 3.5 KPI Targets

| Metric | Target | Measurement |
|---|---|---|
| Registration completion rate | >65% | Funnel analytics |
| Verification turnaround | <24h avg | Workflow tracking |
| Document first-pass approval | >70% | Quality dashboard |
| Seller churn (pre-first listing) | <20% | Retention report |

---

## 4. Stage 2: Onboarding

### 4.1 Overview
The seller sets up their storefront, configures policies, and learns platform tools.

### 4.2 Onboarding Checklist

```
                   SELLER ONBOARDING CHECKLIST
   
   ┌─────────────────────────────────────────────────────────────┐
   │  Storefront Setup                                           │
   │  ☐ Upload store logo (500×500px, PNG)                      │
   │  ☐ Write store description (100–500 chars)                  │
   │  ☐ Set store banner (1200×400px)                            │
   │  ☐ Configure store URL slug                                 │
   │  ☐ Add social media links                                   │
   ├─────────────────────────────────────────────────────────────┤
   │  Policy Configuration                                       │
   │  ☐ Set return policy window (7/14/30 days)                 │
   │  ☐ Define shipping zones and rates                          │
   │  ☐ Configure refund terms                                   │
   │  ☐ Set processing time (1/3/5/7 days)                      │
   ├─────────────────────────────────────────────────────────────┤
   │  Product Readiness                                           │
   │  ☐ Create first product listing                             │
   │  ☐ Upload product images (min 3, max 10)                   │
   │  ☐ Set inventory tracking method                            │
   │  ☐ Configure variants (size/color)                          │
   ├─────────────────────────────────────────────────────────────┤
   │  Platform Familiarisation                                    │
   │  ☐ Complete interactive tutorial                            │
   │  ☐ Review seller handbook                                   │
   │  ☐ Watch commission & payout explainer                     │
   │  ☐ Set notification preferences                             │
   └─────────────────────────────────────────────────────────────┘
```

### 4.3 Seller Dashboard — Initial View

```
              SELLER DASHBOARD (ONBOARDING STATE)
   
   ┌──────────────────────────────────────────────────────────────┐
   │  🎉 Welcome to TSBL, [Seller Name]!                          │
   │  Your store is in onboarding mode. Complete these steps:     │
   │                                                              │
   │  [████████░░░░░░]  64% Complete                              │
   │  ─────────────────────────────────────────────               │
   │  □  1. Store setup ──────────────── Complete ✓              │
   │  □  2. First listing ───────────── In Progress               │
   │  □  3. Payment config ──────────── Pending                   │
   │  □  4. Policy setup ────────────── Not started               │
   │                                                              │
   │  ⚡ Quick actions:                                            │
   │  [Add Product] [Set Policies] [View Tutorial]                │
   └──────────────────────────────────────────────────────────────┘
```

### 4.4 Tools Provided at Each Stage

| Tool | Bronze | Silver | Gold | Platinum |
|---|---|---|---|---|
| Product listing manager | ✓ | ✓ | ✓ | ✓ |
| Basic sales dashboard | ✓ | ✓ | ✓ | ✓ |
| Order management console | ✓ | ✓ | ✓ | ✓ |
| Inventory tracker (manual) | ✓ | ✓ | — | — |
| Inventory tracker (auto) | — | — | ✓ | ✓ |
| Bulk listing (CSV/API) | — | ✓ | ✓ | ✓ |
| Advertising campaign manager | — | ✓ | ✓ | ✓ |
| Advanced analytics (cohort, LTV) | — | — | ✓ | ✓ |
| API integration credentials | — | — | — | ✓ |
| Multi-account management | — | — | — | ✓ |

---

## 5. Stage 3: Listing

### 5.1 Overview
The seller creates and manages their product catalog. Listing quality directly impacts search ranking and conversion.

### 5.2 Product Listing Requirements

| Field | Mandatory? | Validation | Impact on Ranking |
|---|---|---|---|
| Title | Yes | 10–150 chars, no ALL CAPS | High |
| Description | Yes | Min 100 chars, structured format | High |
| Category assignment | Yes | Leaf-node category required | High |
| Price | Yes | Numeric, min $0.50 | Medium |
| Stock quantity | Yes | Integer ≥ 0 | Medium |
| Images (min 3) | Yes | ≥ 800×800px, ≤ 10MB each, JPEG/PNG | High |
| Variants | No | Max 5 variation types (size/color/capacity) | Medium |
| Shipping weight/dimensions | Yes (physical) | Numeric, units specified | Low |
| Digital file upload | Yes (digital) | ≤ 2GB, malware scanned | Critical |
| Tags/keywords | Recommended | Max 10, comma-separated | Medium |
| Meta description | Recommended | Max 160 chars | Low |

### 5.3 Listing Moderation Pipeline

```
                 PRODUCT MODERATION FLOW

   Seller Submits / Edits Listing
          │
          ▼
   ┌──────────────────────────────┐
   │ Automated Checks (<30s)       │
   │ • NSFW image detection        │
   │ • Prohibited keyword scan     │
   │ • Price sanity (vs. category) │
   │ • Duplicate detection         │
   │ • Copyright check (hash)      │
   └──────────┬───────────────────┘
              │
        ┌─────┴──────┐
        │            │
      PASS          FLAG
        │            │
        ▼            ▼
   ┌────────┐  ┌────────────────┐
   │ Live   │  │ Manual Review  │
   │ Listed │  │ Queue (SLA: 4h)│
   └────────┘  └───────┬────────┘
                       │
                 ┌─────┴──────┐
                 │            │
              APPROVED      REJECTED
                 │            │
                 ▼            ▼
             Listed      Rejected +
                          Reason +
                          Appeal Option
```

### 5.4 Listing Optimisation Recommendations

| Strategy | Impact | Implementation |
|---|---|---|
| High-resolution primary image | +27% CTR | Minimum 1200×1200px, white background |
| Keyword-rich title (front-loaded) | +18% search visibility | Primary keyword in first 40 chars |
| Bullet-point feature summary | +15% conversion | Top 5 features in structured list |
| Lifestyle/secondary images | +22% add-to-cart rate | Show product in use, size reference |
| Video inclusion | +35% engagement | 30–60s product walkthrough |
| Competitive pricing (±5% of median) | +12% win rate | Dynamic pricing tool (Silver+) |
| Bundle offers | +18% AOV | "Frequently bought together" configuration |

### 5.5 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| Listing rejected without clear guidance | Seller frustration | Granular rejection codes + fix suggestions |
| Category mismatch → poor visibility | Low impressions | AI category suggestion at listing creation |
| Image dimension errors | Time wasted on reformatting | Auto-crop/compress tool in uploader |
| Duplicate listing flagging | Inventory confusion | Merge suggestion workflow |

### 5.6 KPI Targets

| Metric | Target | Measurement |
|---|---|---|
| Time to first listing | <24h of approval | Onboarding analytics |
| Listing quality score (auto) | >80/100 | Listing health dashboard |
| Listing approval rate (first pass) | >85% | Moderation analytics |
| Products listed per seller (30d) | >10 | Seller activity report |

---

## 6. Stage 4: Sales & Order Management

### 6.1 Overview
The seller receives, processes, and fulfils orders while managing customer communication.

### 6.2 Order Management Lifecycle

```
                   ORDER LIFE CYCLE (SELLER VIEW)

   ┌────────────┐
   │ Order      │  Notification received (email, SMS, dashboard)
   │ Received   │
   └─────┬──────┘
         │
         ▼
   ┌────────────┐
   │ Awaiting   │  Seller confirms within SLA (2–24h)
   │ Processing │
   └─────┬──────┘
         │
   ┌─────┴──────┐        ┌────────────────────┐
   │ Processing │──────> │ • Digital: Upload  │
   │            │        │   asset / grant     │
   └─────┬──────┘        │ • Physical: Pack   │
         │               │   + label           │
         │               │ • Service: Confirm  │
         │               │   date              │
         │               └────────────────────┘
         ▼
   ┌────────────┐
   │ Shipped /  │  Tracking ID submitted → Buyer notified
   │ Completed  │
   └─────┬──────┘
         │
         ▼
   ┌────────────┐
   │ Delivered  │  Buyer confirms / auto-confirms after T+N days
   │ (Buyer     │
   │ Confirmed) │
   └─────┬──────┘
         │
         ▼
   ┌────────────┐
   │ Payout     │  Funds released to seller account
   │ Eligible   │
   └────────────┘
```

### 6.3 Order Processing SLA

| Order Type | Processing SLA | Auto-Cancellation | Escalation Trigger |
|---|---|---|---|
| Digital download | <30 minutes | 2 hours | No action within 1h |
| Physical product | <48 hours | 5 days | No label generated in 48h |
| Service booking | <24 hours | 3 days | No date confirmation |
| Custom/made-to-order | As configured | Per agreement | Breach of agreed timeline |

### 6.4 Seller Fulfilment Dashboard

```
              ORDER MANAGEMENT DASHBOARD

   ┌─────────────────────────────────────────────────────────────┐
   │ 🔔 Pending Actions (4)                                      │
   │ ┌─────┬────────────┬────────────┬──────────┬──────────────┐│
   │ │ #   │ Order ID   │ Buyer      │ Amount   │ Status       ││
   │ ├─────┼────────────┼────────────┼──────────┼──────────────┤│
   │ │ 1   │ TSBL-10234 │ A. Rahman  │ $45.00   │ ⏳ Processing ││
   │ │ 2   │ TSBL-10235 │ S. Khan    │ $120.00  │ 📦 Ship Now  ││
   │ │ 3   │ TSBL-10236 │ F. Hasan   │ $22.50   │ ⏳ Processing ││
   │ │ 4   │ TSBL-10237 │ N. Islam   │ $340.00  │ ❓ Dispute    ││
   │ └─────┴────────────┴────────────┴──────────┴──────────────┘│
   │                                                             │
   │ [Bulk Action] [Print Labels] [Export CSV]                   │
   └─────────────────────────────────────────────────────────────┘
```

### 6.5 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| Buyer makes unreasonable demands | Stress, negative review | Pre-defined response templates + admin escalation |
| Shipping cost miscalculation | Profit erosion | Real-time courier rate integration |
| Tracking number entry errors | Delivery delays | Barcode/QR scanner integration |
| High dispute rate (single buyer) | Rating damage | Buyer verification + order limit per account |
| Inventory overselling | Cancellation penalties | Real-time inventory sync across channels |

### 6.6 Dispute Handling (Seller Perspective)

```
              SELLER-SIDE DISPUTE WORKFLOW

   Dispute Filed by Buyer
          │
          ▼
   ┌──────────────────────────────┐
   │ Seller notified via:          │
   │ • Dashboard alert (real-time) │
   │ • Email notification          │
   │ • SMS (opt-in)                │
   └──────────┬───────────────────┘
              ▼
   ┌──────────────────────────────┐
   │ Seller response (48h window): │
   │ 1. Accept liability → refund  │
   │ 2. Offer replacement          │
   │ 3. Reject + provide evidence  │
   └──────────┬───────────────────┘
              ▼
   ┌──────────────────────────────┐
   │ If rejected:                  │
   │ • Admin reviews evidence      │
   │ • Both sides submit docs      │
   │ • Admin decision (72h SLA)    │
   │ • Appeal window: 7 days       │
   └──────────────────────────────┘

   Seller protections:
   • Seller-favoured policy for Platinum tier
   • Dispute insurance (Gold+): 50% of disputed amount covered
   • Rating immunity for resolved disputes (Silver+)
```

---

## 7. Stage 5: Growth & Analytics

### 7.1 Overview
The seller scales their business using TSBL analytics, marketing tools, and operational insights.

### 7.2 Analytics Dashboard — Tier Comparison

| Metric | Bronze | Silver | Gold | Platinum |
|---|---|---|---|---|
| Total revenue (MTD) | ✓ | ✓ | ✓ | ✓ |
| Order count & trends | ✓ | ✓ | ✓ | ✓ |
| Conversion rate | ✓ | ✓ | ✓ | ✓ |
| Average order value | — | ✓ | ✓ | ✓ |
| Traffic sources breakdown | — | ✓ | ✓ | ✓ |
| Top-performing products | — | ✓ | ✓ | ✓ |
| Search impression share | — | — | ✓ | ✓ |
| Competitor price benchmarks | — | — | ✓ | ✓ |
| Customer acquisition cost | — | — | ✓ | ✓ |
| Cohort retention analysis | — | — | — | ✓ |
| Predictive demand forecasting | — | — | — | ✓ |
| Profitability by SKU | — | — | ✓ | ✓ |

### 7.3 Seller Performance Scorecard

```
           SELLER PERFORMANCE SCORECARD

   ┌────────────────────────────────────────────────────────────┐
   │  Seller: [Name]        Tier: Silver     Score: 84/100     │
   │                                                           │
   │  Metric              Score     Target     Status          │
   │  ───────────────────────────────────────────────────      │
   │  Order completion    95%       98%        ⚠️ Near goal    │
   │  Avg. rating         4.1★      4.2★       ⚠️ Near goal    │
   │  On-time dispatch    92%       95%        ⚠️ Near goal    │
   │  Response rate       98%       95%        ✅ Exceeding    │
   │  Dispute rate        1.2%      <2%        ✅ On track     │
   │  Listing quality     78/100    80/100     ⚠️ Near goal    │
   │  Monthly GMV         $8,200    $10,000    ⚡ 82% of target│
   │                                                           │
   │  🏆 Next Tier: Gold                                       │
   │  Progress: [████████░░░░░░░░░░]  42%                      │
   │  Missing: 418 orders / 0.3★ rating / 1% completion        │
   └────────────────────────────────────────────────────────────┘
```

### 7.4 Revenue Optimisation Recommendations

| Strategy | Expected Lift | Difficulty | Tier Requirement | System Feature |
|---|---|---|---|---|
| Optimise listing images | +15–27% CTR | Low | All | AI image analyser |
| Enable flash sales | +40% revenue (event) | Medium | Silver+ | Campaign manager |
| Use promoted listings | +22% impressions | Low | Silver+ | Ad console |
| Set competitive pricing | +12% win rate | Medium | Silver+ | Dynamic pricing tool |
| Create product bundles | +18% AOV | Medium | Gold+ | Bundle builder |
| Offer subscription/back-order | +30% recurring revenue | High | Gold+ | Subscription engine |
| Expand to new categories | +25% addressable market | High | Platinum | Category explorer |
| International shipping | +35% new customer base | High | Platinum | Cross-border logistics |

### 7.5 Seller Support Touchpoints

| Tier | Available Channels | Response SLA | Operating Hours |
|---|---|---|---|
| Bronze | Email, Help Centre, Chatbot | 24h | 9AM–6PM (weekdays) |
| Silver | Email, Live Chat, Help Centre | 12h | 8AM–10PM (including Sat) |
| Gold | Live Chat, Phone, Dedicated Slack | 4h | 24/7 |
| Platinum | VIP Phone, Dedicated AM, Priority Queue | 1h | 24/7 with escalation |

### 7.6 Marketing Toolkit by Tier

```
              MARKETING TOOLKIT ACCESS

   Bronze:    [Basic] ────  Listing tools only
   Silver:    [Basic + Ad Console + Coupon Engine]
   Gold:      [Basic + Ad Console + Coupon Engine + Email Campaigns + Flash Sale Manager]
   Platinum:  [Full Suite + API Access + Multi-Channel Sync + Brand Store Customisation]
```

### 7.7 Growth-Focused KPIs

| KPI | Bronze Target | Silver Target | Gold Target | Platinum Target |
|---|---|---|---|---|
| Monthly GMV growth | +10% MoM | +15% MoM | +10% MoM | +8% MoM (sustain) |
| Average order value | $25 | $35 | $50 | $75 |
| Customer repeat rate | 15% | 25% | 35% | 45% |
| Product catalog size | 10 | 50 | 200 | 500+ |
| Cross-border % | — | 5% | 15% | 30% |
| Advertising ROI | — | 3× | 4× | 5× |
| Net seller satisfaction | 7.0/10 | 7.5/10 | 8.0/10 | 8.5/10 |

---

## 8. Seller Journey Decision Points

| Decision Point | Question | Risk | Intervention |
|---|---|---|---|
| Registration completion | "Is this platform worth my time?" | Drop-off | Showcase top seller earnings, success stories |
| First listing creation | "Can I list easily?" | Abandonment | Guided product listing wizard |
| First order receipt | "How do I fulfil this?" | Fulfilment error | Step-by-step fulfilment tutorial + checklist |
| First dispute | "Will the platform protect me?" | Churn | Clear dispute FAQ, assurance of fair process |
| Tier advancement threshold | "Is the next tier worth the effort?" | Stagnation | Progress bar, concrete benefits comparison |
| Plateau in sales | "What else can I do?" | Churn to competitor | Personalised growth recommendations (Gold+) |

---

## 9. Seller Persona Archetypes

| Persona | Behaviour | Needs | Retention Strategy |
|---|---|---|---|
| Hobbyist Seller | Sells occasionally, low volume | Simple tools, low fees | Education content, community |
| Part-Time Entrepreneur | Consistent listings, growth-minded | Analytics, automation | Target Silver → Gold progression |
| Full-Time Merchant | High volume, multi-channel | API, bulk tools, support | Platinum tier, account manager |
| Brand/Manufacturer | Official brand store, large catalog | Brand customisation, exclusivity | Dedicated partnership programme |
| Digital Creator | Courses, software, templates | File hosting, licensing tools | Creator-specific features, higher margins |

---

## 10. Commission & Payout Deep Dive

### 10.1 Commission Calculation

| Item | Rate | Notes |
|---|---|---|
| Base commission | Tier-based (8–15%) | Applied to order subtotal |
| Payment processing fee | 2.5% + $0.30 | Flat across all tiers |
| Promoted listing fee | Pay-per-click (variable) | Optional, seller-controlled |
| Dispute fee | $5 (waived if seller wins) | Only if escalated to admin |
| Withdrawal fee | $0.50 (bank) / $0.25 (mobile wallet) | Per payout |

### 10.2 Payout Schedule

```
               PAYOUT FLOW TIMELINE

   Order Delivered
         │
         ▼
   ┌────────────────────┐
   │ Clearance Period    │  ┌──────────────────────────────┐
   │ (T+0 to T+3 days)   │  │ Funds held in escrow        │
   │                      │  │ Buyer confirmation or       │
   └──────────┬───────────┘  │ auto-confirmation window    │
              │              └──────────────────────────────┘
              ▼
   ┌────────────────────┐
   │ Available for       │  Seller can request payout
   │ Withdrawal          │  (manual or auto-schedule)
   └──────────┬──────────┘
              │
              ▼
   ┌────────────────────┐
   │ Processing          │  T+1 to T+7 depending on tier
   │ (Bank/Wallet)       │
   └──────────┬──────────┘
              │
              ▼
   ┌────────────────────┐
   │ Funds Settled       │  Notification sent
   └────────────────────┘
```

### 10.3 Commission Impact Analysis

| Scenario | Price | Tier | Commission | Seller Net | Buyer Pays |
|---|---|---|---|---|---|
| Low-value (Bronze) | $20.00 | 15% | $3.00 | $17.00 | $20.00 |
| Low-value (Platinum) | $20.00 | 8% | $1.60 | $18.40 | $20.00 |
| High-value (Bronze) | $500.00 | 15% | $75.00 | $425.00 | $500.00 |
| High-value (Platinum) | $500.00 | 8% | $40.00 | $460.00 | $500.00 |

**Savings at Platinum vs Bronze:** $35 on a $500 sale (7% margin improvement)

---

## 11. Seller Risk & Compliance

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Fake listings / fraud | Medium | High | Listing moderation, seller bonding |
| IP infringement | Medium | High | DMCA takedown process, content ID |
| Late fulfilment pattern | High | Medium | Automated SLA enforcement, rating penalty |
| Abusive buyer behaviour | Medium | Medium | Buyer blacklist, dispute protection |
| Money laundering via sales | Low | Critical | Transaction monitoring, KYC thresholds |
| Tax non-compliance | Medium | High | Automated tax reporting, 1099-K generation |

---

## 12. Seller Journey Optimisation Loop

```
              CONTINUOUS SELLER EXPERIENCE IMPROVEMENT

   ┌─────────────────────────────────────────────────────────────┐
   │  1. Onboard      2. Enable       3. Empower     4. Excel   │
   │     ┌───┐          ┌───┐           ┌───┐          ┌───┐   │
   │     │Friction│      │Tools │        │Insights│    │Growth │  │
   │     │Removal│      │Access│        │& Data │    │Mktg   │  │
   │     └───┘          └───┘           └───┘          └───┘   │
   │                                                             │
   │  Feedback Loops:                                            │
   │  • Quarterly seller satisfaction survey                      │
   │  • Monthly NPS pulse check                                   │
   │  • Support ticket trend analysis                             │
   │  • Forum / community feedback                                │
   │  • Churn exit interviews                                     │
   └─────────────────────────────────────────────────────────────┘
```

---

## 13. Key Performance Indicators (Aggregate)

| KPI | Current Baseline | 6-Month Target | 12-Month Target |
|---|---|---|---|
| Active sellers (monthly) | 500 | 2,000 | 5,000 |
| Avg. seller GMV/month | $4,200 | $6,000 | $10,000 |
| Seller retention (12-month) | 55% | 70% | 80% |
| Avg. tier progression time | 14 months | 9 months | 6 months |
| Platinum seller count | 5 | 25 | 100 |
| Seller NPS | +18 | +35 | +50 |
| First-listing time | 72h | 24h | 12h |
| Dispute rate (seller-favoured) | 40% | 55% | 65% |

---

**End of Document — Seller Journey v1.0**
