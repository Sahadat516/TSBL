# Buyer Journey: End-to-End Lifecycle

**Document Version:** 1.0  
**Status:** Final  
**Last Updated:** 2026-07-01  
**Owner:** Product Management  

---

## 1. Journey Overview

The TSBL buyer journey encompasses the complete lifecycle from initial discovery through post-purchase advocacy. This document maps every stage, touchpoint, system interaction, and emotional signal across the funnel.

```
                            BUYER LIFECYCLE MAP
                               
  DISCOVERY ──> EVALUATION ──> PURCHASE ──> DELIVERY ──> POST-PURCHASE
      │             │             │             │              │
      │  Top of     │  Middle of  │  Bottom of  │  Retention   │  Advocacy
      │  Funnel     │  Funnel     │  Funnel     │  Phase       │  Phase
      ▼             ▼             ▼             ▼              ▼
  ┌─────────┐ ┌───────────┐ ┌────────┐ ┌───────────┐ ┌─────────────┐
  │Awareness│ │Comparison │ │Checkout│ │Fulfillment│ │Repeat/Refer │
  └─────────┘ └───────────┘ └────────┘ └───────────┘ └─────────────┘
```

---

## 2. Stage 1: Discovery

### 2.1 Overview
The buyer becomes aware of TSBL and identifies a product or service that addresses their need. This is the widest point of the funnel.

### 2.2 Touchpoints & Channels

| Touchpoint | Channel | Buyer Intent | System Interaction |
|---|---|---|---|
| Organic search (SEO) | Google, Bing | Problem-solving | Search engine indexing, SERP snippet rendering |
| Paid advertisement | Google Ads, Social | Active shopping | Ad campaign tracking, UTM parameter capture |
| Social media post | Facebook, Instagram, LinkedIn | Passive browsing | Social feed integration, share tracking |
| Referral link | Email, messaging apps | Trusted recommendation | Referral program API, affiliate cookie placement |
| Marketplace browse | Direct visit | Exploratory | Category tree rendering, personalised recommendations |
| Email campaign | Email inbox | Re-engagement | CRM segmentation, Mailchimp/SendGrid API |

### 2.3 User Goals

- Identify a solution to an unmet need
- Establish trust in TSBL as a platform
- Locate relevant categories or products
- Assess price range and availability

### 2.4 System Interactions

```
                    DISCOVERY SYSTEM ARCHITECTURE
                                   
  User ──> CDN ──> Load Balancer ──> Web Server
                                      │
                          ┌───────────┴────────────┐
                          │                        │
                     Search Service           Recommendation
                          │                   Engine
                          │                        │
                     Elasticsearch            Redis Cache
                          │                        │
                          └───────────┬────────────┘
                                      │
                               Product Catalog DB
```

### 2.5 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| Irrelevant search results | High bounce rate (>65%) | Semantic search with NLP, synonym mapping |
| Slow page load (>3s) | 53% mobile abandonment | CDN optimisation, lazy loading, image compression |
| No clear navigation | Session abandonment | AI-powered category suggestions, breadcrumbs |
| Zero-results queries | Frustration, exit | "Did you mean?" suggestions, category fallback |

### 2.6 Emotional Journey

```
  Emotional Arc: Discovery
   
  High  ──╮
          │    😊 Curiosity
  Med   ──┤──╮
          │  │  🤔 Confusion (if search fails)
  Low   ──┤──┤───────────────────────
          │  │                      │
          │  │                      😠 Frustration → Exit
        Entry Search Success  Search Fail
```

### 2.7 Key Metrics

| Metric | Target | Measurement |
|---|---|---|
| Bounce rate | <45% | Google Analytics / Heap |
| Session duration | >2:30 min | Session tracking |
| Search-to-browse ratio | >60% | Search analytics |
| New user acquisition cost | <$12 | CRM attribution |

---

## 3. Stage 2: Evaluation

### 3.1 Overview
The buyer compares products, evaluates sellers, and narrows their choices. This is the highest cognitive-load stage.

### 3.2 Touchpoints & Channels

| Touchpoint | Channel | User Goal | System Interaction |
|---|---|---|---|
| Product detail page (PDP) | Website / App | Feature assessment | SKU metadata rendering, gallery CDN |
| Product comparison tool | Website | Side-by-side evaluation | Comparison engine, attribute diff algorithm |
| Seller storefront | Website | Trust verification | Seller profile API, rating aggregation |
| Reviews & ratings tab | Website / App | Social proof validation | Review service, sentiment analysis |
| Q&A section | Website | Clarification | Community Q&A engine, vendor notification |
| Live chat | Widget | Real-time answers | Chat service, agent routing |
| Wishlist | Website / App | Save for later | Wishlist DB, notification triggers |

### 3.3 Evaluation Criteria Matrix

```
                     EVALUATION DECISION MATRIX
                                   
  ┌──────────────────────┬──────┬──────┬──────┬──────┐
  │ Criterion            │ Wt.  │ Prod │ Prod │ Prod │
  │                      │      │  A   │  B   │  C   │
  ├──────────────────────┼──────┼──────┼──────┼──────┤
  │ Price                │ 30%  │  8   │  6   │  9   │
  │ Seller rating        │ 25%  │  7   │  9   │  5   │
  │ Delivery time        │ 20%  │  6   │  8   │  7   │
  │ Feature fit          │ 15%  │  9   │  7   │  6   │
  │ Return policy        │ 10%  │  5   │  8   │  7   │
  ├──────────────────────┼──────┼──────┼──────┼──────┤
  │ Weighted Score       │100%  │ 7.15 │ 7.55 │ 6.90 │
  └──────────────────────┴──────┴──────┴──────┴──────┘
```

### 3.4 Seller Trust Signals

| Signal | Display Location | Weight in Decision |
|---|---|---|
| Verified seller badge | PDP header, search results | High |
| Response rate & time | Storefront, chat widget | Medium |
| Order completion rate | Seller profile | High |
| Review count & recency | PDP tab, storefront | Medium |
| Membership duration | Storefront footer | Low |
| Policy compliance score | Seller profile | Medium |

### 3.5 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| Information asymmetry | Purchase hesitation | Standardised product templates, mandatory fields |
| Review authenticity concerns | Trust erosion | Verified-purchase tagging, review moderation |
| Price inconsistency across sellers | Choice paralysis | Price comparison widget, dynamic filters |
| Missing technical specifications | Abandonment | AI-assisted spec extraction, category schemas |
| No clear shipping estimate | Cart abandonment | Real-time courier rate API, geolocation |

### 3.6 Emotional Arc

```
  Emotional Arc: Evaluation
   
  High  ──╮  😊 Optimism
          │   \
  Med   ──┤────\──😐 Analysis Paralysis──😊 Confident Choice
          │      \                      /
  Low   ──┤───────\────────────────────/
          │        \                  /
          │         😠 Overwhelm → Abandon
        Entry    Comparison      Decision
                 Overload
```

### 3.7 Conversion Drop-off (Expected)

| Evaluation Step | Users Entering | Drop Rate | Users Exiting | Remaining |
|---|---|---|---|---|
| PDP view | 10,000 | -- | -- | 10,000 |
| Review read | 7,500 | 25% | 2,500 | 7,500 |
| Comparison started | 4,500 | 40% | 3,000 | 4,500 |
| Seller evaluation | 3,150 | 30% | 1,350 | 3,150 |
| Add to cart | 2,205 | 30% | 945 | 2,205 |
| **Checkout initiated** | **1,543** | **30%** | **662** | **1,543** |

---

## 4. Stage 3: Purchase

### 4.1 Overview
The buyer commits to a transaction. This stage has the highest stakes and requires frictionless execution.

### 4.2 Sub-stages

#### 4.2.1 Cart Management

| Action | System Process | Error States | Recovery Path |
|---|---|---|---|
| Add item | Cart service → Redis → DB | Stock exceeded | Stock check atomicity, hold timer |
| Update quantity | Cart CRUD → Inventory check | Partial availability | Split cart notification |
| Apply coupon | Coupon engine → validation | Expired/invalid | Error toast, alternative suggestions |
| Save for later | Cart split → wishlist copy | N/A | N/A |
| Remove item | Cart update → DB sync | N/A | Undo action (5s window) |

#### 4.2.2 Coupon & Discount Application

```
                   COUPON VALIDATION FLOW
                                   
  User Inputs Coupon Code
          │
          ▼
  ┌─────────────────┐     NO      ┌──────────────────┐
  │ Coupon Exists?  │──────────>  │ "Invalid Code"   │
  └────────┬────────┘             │ Error Message    │
           │ YES                  └──────────────────┘
           ▼
  ┌─────────────────┐     NO      ┌──────────────────┐
  │ Within Date      │──────────>  │ "Code Expired"   │
  │ Range?           │             │ Warning          │
  └────────┬────────┘             └──────────────────┘
           │ YES
           ▼
  ┌─────────────────┐     NO      ┌──────────────────┐
  │ Min Cart Value  │──────────>  │ Add $X more to   │
  │ Met?            │             │ qualify          │
  └────────┬────────┘             └──────────────────┘
           │ YES
           ▼
  ┌─────────────────┐     NO      ┌──────────────────┐
  │ Usage Limit OK? │──────────>  │ "Already Used"   │
  └────────┬────────┘             └──────────────────┘
           │ YES
           ▼
  ┌────────────────────────────────────────────────┐
  │ Discount Applied → Cart Total Recalculated    │
  │ → Tax & Shipping Recalculated                  │
  └────────────────────────────────────────────────┘
```

#### 4.2.3 Checkout

| Step | Data Captured | Validation | System Touchpoint |
|---|---|---|---|
| Shipping address | Street, city, ZIP, phone | Address verification API (Google/Loqate) | Address service |
| Billing address | Same or different | Tax jurisdiction lookup | Tax engine |
| Shipping method | Standard/Express/Overnight | Courier zone check | Shipping rate API |
| Order summary | Line items, totals, discounts | Price consistency check | Order service |
| Payment selection | Card/Mobile/Wallet/Bank | Payment gateway routing | Payment orchestrator |

#### 4.2.4 Payment Processing

```
                   PAYMENT ORCHESTRATION
                                   
  ┌──────────────┐
  │  User Selects │
  │  Payment Method│
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐     ┌──────────────────────┐
  │  Payment      │────>│  Gateway Tokenisation │
  │  Orchestrator │     └──────────┬───────────┘
  └──────────────┘                │
         │                        ▼
         │              ┌──────────────────────┐
         ├──Card───────>│  Stripe / SSLCommerz │
         ├──Mobile─────>│  bKash / Nagad API   │
         ├──Wallet─────>│  Internal Wallet Srv │
         └──Bank───────>│  Bank Gateway TX     │
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Payment Confirmation │
                         │  → Order Created      │
                         │  → Inventory Held     │
                         │  → Email Triggered    │
                         └──────────────────────┘
```

#### 4.2.5 Order Confirmation

| Element | Content | System Action |
|---|---|---|
| Order number | Auto-generated TSBL-XXXXXX | Order service → DB persist |
| Email receipt | Item list, total, delivery ETA | Transactional email queue |
| SMS notification | Order # + tracking link | SMS gateway API |
| In-app confirmation | Animated success screen | Frontend state update |
| Push notification | "Your order is confirmed" | Push notification service |

### 4.3 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| Forced account creation | 24% abandonment rate | Guest checkout option |
| Hidden fees at last step | Cart abandonment spike | Upfront fee calculator |
| Payment gateway timeout | Order failure, double charge | Idempotency keys, retry logic |
| Card decline without reason | User frustration | Decline reason mapping, alternative suggestion |
| No local payment methods | Market rejection | Multi-gateway integration (bKash, Nagad, etc.) |

### 4.4 Emotional Arc

```
  Emotional Arc: Purchase
   
  High  ──╮
          │       😊 Excitement
  Med   ──┤──────────╮
          │          │   😰 Payment Anxiety
  Low   ──┤──────────┤───────────────╮
          │          │               │
          │          │               │   😊 Relief/Confirmation
        Cart      Checkout       Payment      Order #
        Build     Details        Processing   Received
```

### 4.5 Conversion Funnel & Drop-off

| Stage | Enter | Drop % | Exit | Retained |
|---|---|---|---|---|
| Add to cart | 2,205 | -- | -- | 2,205 |
| View cart | 1,985 | 10% | 220 | 1,985 |
| Proceed to checkout | 1,389 | 30% | 596 | 1,389 |
| Fill shipping | 1,250 | 10% | 139 | 1,250 |
| Fill payment | 1,125 | 10% | 125 | 1,125 |
| Place order | 1,125 | 0% | 0 | 1,125 |
| Payment success | 1,012 | 10% | 113 | 1,012 |
| **Order confirmed** | **1,012** | -- | -- | **1,012** |

---

## 5. Stage 4: Delivery / Fulfillment

### 5.1 Overview
The seller delivers the digital or physical product. For digital goods, this is instantaneous; for physical, it involves logistics tracking.

### 5.2 Fulfillment Types

| Good Type | Delivery Mechanism | System Process | Buyer Expectation |
|---|---|---|---|
| Digital download | S3 signed URL + email link | Asset service → CDN → URL generation | Instant (<30s) |
| Service booking | Calendar slot confirmation | Scheduling engine → calendar API | Confirmation + reminder |
| Physical product | Courier tracking integration | Logistics API → tracking updates | 2–7 day expectation |
| Subscription | Access grant + recurring billing | Subscription engine → license server | Immediate access |

### 5.3 Digital Delivery Flow

```
                   DIGITAL ASSET DELIVERY
                                   
  Order Paid ──> Payment Webhook Received
                    │
                    ▼
  ┌──────────────────────────────┐
  │ Asset Service: Generate       │
  │ Signed S3 URL (TTL: 72h)     │
  └──────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
  ┌──────────────┐    ┌──────────────┐
  │ Email with   │    │ In-App       │
  │ Download Link│    │ Download Page│
  └──────────────┘    └──────────────┘
         │                     │
         ▼                     ▼
  ┌──────────────────────────────────────┐
  │ User clicks → CDN → Asset Streamed   │
  │ Download tracked → Fulfillment       │
  │ marked complete                      │
  └──────────────────────────────────────┘
```

### 5.4 Shipping Tracking Integration

| Event | Buyer Notification | System Trigger |
|---|---|---|
| Label created | "Seller preparing shipment" | Courier API webhook |
| Package picked up | "Shipped — tracking #: XXX" | Status push via WebSocket |
| In transit | Location-based updates | Courier tracking polling |
| Out for delivery | "Arriving today" | Scheduled email |
| Delivered | "Delivered! Rate your experience" | Fulfillment complete event |

### 5.5 Pain Points

| Pain Point | Impact | Mitigation |
|---|---|---|
| No tracking updates for 48h+ | Buyer anxiety escalates to support | Proactive SMS updates, SLA alerts |
| Delayed digital delivery | Trust damage, refund request | Redundancy check: if email fails → SMS + in-app |
| Wrong item received | Return/refund request | Picklist verification at seller side |
| Delivery to wrong address | Chargeback risk | Address confirmation at checkout + OTP |

### 5.6 Emotional Arc

```
  Emotional Arc: Delivery
   
  High  ──╮  😊 Anticipation
          │       \
  Med   ──┤────────\──😐 Waiting Anxiety
          │         \              \
  Low   ──┤──────────\──────────────\──😊 Delivered!
          │            \              \
          │             😠 Delay → Rage → Support
        Order      Shipping      Out for       Received
        Placed     Confirmed     Delivery
```

---

## 6. Stage 5: Post-Purchase

### 6.1 Overview
The post-purchase phase determines long-term buyer lifetime value (LTV). This stage covers review submission, dispute handling, repeat purchases, and advocacy.

### 6.2 Sub-stages

#### 6.2.1 Review Submission

| Element | Detail | System Process |
|---|---|---|
| Rating | 1–5 star scale | Rating service → aggregate calculation |
| Text review | Min 10, Max 1000 chars | Content moderation API (toxicity filter) |
| Image upload | Max 5 images, 10MB each | Image CDN, malware scan, thumbnail generation |
| Verified tag | Auto-attached for verified purchases | Purchase verification DB lookup |
| Seller response | 7-day window to reply | Notification → seller dashboard → public reply |

#### 6.2.2 Dispute Filing

```
                   DISPUTE RESOLUTION FLOW
                                   
  Buyer Files Dispute (72h window)
          │
          ▼
  ┌──────────────────────────────┐
  │ 1. Buyer selects reason:     │
  │    • Item not received       │
  │    • Item not as described   │
  │    • Defective / damaged     │
  │    • Wrong item              │
  └──────────┬───────────────────┘
             ▼
  ┌──────────────────────────────┐
  │ 2. Evidence submission (24h) │
  │    • Photos / video          │
  │    • Text description        │
  └──────────┬───────────────────┘
             ▼
  ┌──────────────────────────────┐
  │ 3. Seller notified (48h      │
  │    response window)          │
  └──────────┬───────────────────┘
             ▼
  ┌──────────────────────────────┐
  │ 4. Resolution options:       │
  │    • Full refund             │
  │    • Partial refund          │
  │    • Replacement             │
  │    • Seller reject → Admin   │
  │      escalation              │
  └──────────┬───────────────────┘
             ▼
  ┌──────────────────────────────┐
  │ 5. Resolution applied →      │
  │    Escrow released /         │
  │    refund initiated          │
  └──────────────────────────────┘
```

#### 6.2.3 Repeat Purchase Triggers

| Trigger | Mechanism | System Action | Expected Lift |
|---|---|---|---|
| Post-delivery follow-up email | Automated D+3 email | CRM campaign trigger | 12% repurchase in 30d |
| Subscription/back-in-stock | Inventory re-stock event | Notification queue → SMS/email | 8% conversion |
| Cart recovery (abandoned) | 1h / 24h / 72h sequences | Email automation workflow | 15% recovery rate |
| Personalised recommendation | AI based on purchase history | Recommendation engine → homepage | 22% CTR |
| Loyalty points expiry notice | 14-day advance notice | Points service → notification | 18% re-engagement |
| Seasonal/event-based | Calendar event trigger | Campaign manager → push | Varies by event |

### 6.3 Buyer Delight Moments

| Moment | Mechanism | Impact on NPS |
|---|---|---|
| Surprise upgrade (free shipping) | System auto-detects eligible cart | +15 points |
| Personalised thank-you note | Seller configured + system template | +8 points |
| Birthday discount voucher | CRM date-of-birth trigger | +12 points |
| Instant digital download | Zero-wait asset delivery | +10 points |
| Proactive delay notification with apology | Courier SLA monitoring | +5 points (damage control) |
| First-purchase welcome gift | Campaign automation | +20 points |

### 6.4 Emotional Arc

```
  Emotional Arc: Post-Purchase
   
  High  ──╮  😊 Delight (surprise gift)
          │         ╱
  Med   ──┤────────╱────────😊 Loyalty
          │       ╱              │
  Low   ──┤──────╱───────────────│──────────────
          │     ╱                │
          │    😐 Neutral         │  😠 If dispute
          │   (no follow-up)     │  mishandled
        Product      D+3         D+30      D+90
        Received  Follow-up    Repurchase  Advocacy
```

### 6.5 Retention Strategies

| Strategy | Execution | KPI | Timeline |
|---|---|---|---|
| Tiered loyalty programme | Points per $1 spent, 5 tiers | Active member % | Q1 rollout |
| Referral rewards | $5 credit per referral (buyer + referrer) | Referral conversion rate | Q2 launch |
| Early access to sales | Platinum/Gold members only | Tier upgrade rate | Q3 |
| Exclusive content | Members-only webinars, guides | Engagement rate | Ongoing |
| Win-back campaigns | 60/90/120-day dormant triggers | Re-activation rate | Quarterly cycle |

---

## 7. Full Funnel Conversion Summary

```
                    CONVERSION FUNNEL — EXPECTED RATES
                                   
   Visitors (100%)
       │
       ▼
   Product Page View (35%)
       │
       ▼
   Add to Cart (22%)
       │
       ▼
   Checkout Start (15%)
       │
       ▼
   Payment Success (10%)
       │
       ▼
   Delivery Complete (9.5%)
       │
       ▼
   Repeat Purchase (2.8%)
       │
       ▼
   Advocate/Refer (0.5%)

  Overall Conversion: 10% (Visitor → Paid Order)
  Expected LTV: $240 avg. (across 3.2 transactions)
```

---

## 8. System Touchpoint Matrix

| Stage | Frontend | API Gateway | Microservice | Data Store |
|---|---|---|---|---|
| Discovery | Homepage, search bar, category nav | `/api/v1/search`, `/api/v1/categories` | Search Service, Recommendation Service | Elasticsearch, PostgreSQL |
| Evaluation | PDP, comparison view, storefront | `/api/v1/products/{id}`, `/api/v1/reviews` | Product Service, Review Service, Seller Service | PostgreSQL, Redis cache |
| Purchase | Cart, checkout, payment form | `/api/v1/cart`, `/api/v1/orders`, `/api/v1/payments` | Cart Service, Order Service, Payment Service | PostgreSQL, Redis (cart session) |
| Delivery | Download page, tracking view | `/api/v1/downloads`, `/api/v1/tracking` | Asset Service, Fulfillment Service, Logistics API | S3/CDN, PostgreSQL |
| Post-purchase | Review form, dispute centre | `/api/v1/reviews`, `/api/v1/disputes` | Review Service, Dispute Service, CRM | PostgreSQL, Segment/Amplitude |

---

## 9. Buyer Decision Points & Exit Risks

| Decision Point | Question Buyer Asks | Exit Risk | Intervention |
|---|---|---|---|
| Landing | "Is this site trustworthy?" | 55% | SSL badge, trust seals, social proof bar |
| Category selection | "Do they have what I need?" | 40% | Smart search, trending categories |
| Product comparison | "Which is the best value?" | 30% | Comparison tool, highlight bestseller badge |
| Seller evaluation | "Can I trust this seller?" | 25% | Verified badge, rating breakdown |
| Add to cart | "Should I buy now?" | 22% | Stock scarcity timer, price drop guarantee |
| Checkout | "Is this safe?" | 30% | SSL padlock, payment icons, guest checkout |
| Payment | "Will my data be safe?" | 10% | 3DSecure, tokenisation, PCI DSS badge |
| Post-delivery | "Was this worth it?" | — | Follow-up email, review incentive |

---

## 10. Buyer Persona Archetypes

| Persona | Behaviour | Preferred Channels | Retention Lever |
|---|---|---|---|
| Value Hunter | Compares extensively, waits for sales | Email, comparison tools | Flash sale alerts, coupon bundles |
| Impulse Buyer | Purchases quickly, price-insensitive | Push, in-app | One-click buy, personalised recommendations |
| Researcher | Reads all reviews, asks Q&A | Web, chat | Expert Q&A, detailed spec sheets |
| Loyalist | Returns to same sellers | Email, direct | Seller subscription, VIP perks |
| First-Timer | Anxious, needs guidance | Email, knowledge base | Welcome series, first-purchase guide |

---

## 11. Key Performance Indicators

| KPI | Calculation | Benchmark | Target |
|---|---|---|---|
| Cart-to-checkout rate | Checkout starts / cart adds | 65% | >75% |
| Checkout completion rate | Paid orders / checkout starts | 72% | >80% |
| Average order value (AOV) | Revenue / orders | $75 | >$95 |
| Buyer lifetime value (LTV) | Avg. order × order frequency × lifespan | $180 | >$240 |
| Net promoter score (NPS) | Promoters - Detractors | +32 | >+45 |
| Repeat purchase rate | 2+ orders / total buyers | 28% | >35% |
| Time to first repeat purchase | Days between order 1 and 2 | 45 days | <35 days |
| Review submission rate | Reviews / delivered orders | 12% | >20% |
| Dispute rate | Disputes / orders | 3% | <1.5% |

---

## 12. Continuous Improvement Cycle

```
                    BUYER JOURNEY OPTIMISATION LOOP
                                   
         ┌─────────────────────────────────────────────┐
         │                1. Measure                     │
         │    (Analytics, session recording, surveys)   │
         └────────────────────┬─────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────┐
         │                2. Analyse                     │
         │    (Funnel analysis, heatmaps, CSAT data)    │
         └────────────────────┬─────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────┐
         │                3. Prioritise                  │
         │    (ICE score: Impact × Confidence × Ease)   │
         └────────────────────┬─────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────┐
         │                4. Experiment                  │
         │    (A/B test, usability test, prototype)     │
         └────────────────────┬─────────────────────────┘
                              │
         ┌────────────────────▼─────────────────────────┐
         │                5. Implement                   │
         │    (Ship feature, update copy, fix UX)       │
         └────────────────────┬─────────────────────────┘
                              │
                              └── Return to 1 ──────────┘
```

---

**End of Document — Buyer Journey v1.0**
