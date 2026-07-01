# 10. UI/UX Blueprint

> **Document Owner:** Principal UI/UX Architect
> **Status:** Draft v1.0
> **Last Updated:** 2026-07-02
> **Project:** TRUE STAR BD LIMITED — Multi-Vendor Digital Marketplace
> **Tech Stack:** Next.js 15+, TailwindCSS, Framer Motion

---

## 1. Design Principles

### 1.1 Clarity
Every screen must answer three questions for the user: *Where am I? What can I do here? Where do I go next?* Information hierarchy is established through typographic scale, whitespace, and visual weight. Critical actions are visually prominent; secondary actions are de-emphasised. No user should ever need to guess what a button does or where a link leads.

### 1.2 Trust
A digital marketplace lives or dies on trust. Every product listing shows transparent pricing (no hidden fees), the seller's full identity (store name, avatar, rating, response time, member-since date), and verified review counts. Transaction security is signalled through SSL badges, payment method logos, and clear refund/return policies at every checkout step. Seller verification badges (ID-verified, phone-verified) are displayed prominently.

### 1.3 Efficiency
The path from discovery to purchase must be as short as possible. Smart defaults (best shipping method, remembered addresses, saved payment methods) reduce friction. Search auto-suggests results as the user types. Filters persist across sessions. The minimum viable path to purchase is three clicks: Browse → Product Detail → Buy Now.

### 1.4 Consistency
All UI patterns are defined in a central design token system and enforced through shared components. Buttons, inputs, modals, cards, and navigation elements behave identically regardless of where they appear. Colour, spacing, typography, and motion follow a single system. This reduces cognitive load and makes the platform feel cohesive.

### 1.5 Accessibility
The interface meets WCAG 2.2 AA standards as a baseline. This means: all interactive elements are keyboard accessible, text has a minimum contrast ratio of 4.5:1, non-text content has text alternatives, and the interface can be navigated without a mouse. Accessibility is not an afterthought — it is tested from the first component.

### 1.6 Mobile-First
All user flows are designed for mobile screens first and progressively enhanced for larger viewports. Touch targets meet the 44×44px minimum. Content is single-column on mobile with a bottom navigation bar. Desktop layouts are an expansion of the mobile experience, never a separate experience.

---

## 2. User Personas & Their Goals

### 2.1 Guest (Anonymous Visitor)
| Attribute | Detail |
|---|---|
| Goal | Browse products, search for specific items, compare prices, decide whether to register |
| Pain Points | Can't see full product details without logging in; forced registration before browsing |
| Needs | Full browsing access, price transparency, ability to see reviews, clear value proposition for signing up |
| Behaviour | Enters via search engine or social link; spends 30–60 seconds deciding whether to engage |

### 2.2 Buyer (Registered Customer)
| Attribute | Detail |
|---|---|
| Goal | Find and purchase digital products, download purchases, leave reviews, track order history |
| Pain Points | Complicated checkout, slow downloads, unclear refund policies, poor search results |
| Needs | Fast search with relevant results, secure one-click checkout, instant download access, order management dashboard |
| Behaviour | Returns to platform for repeat purchases; expects personalised recommendations |
| Segment Examples | Freelancer buying stock assets, developer purchasing code templates, designer buying fonts/graphics |

### 2.3 Seller (Vendor)
| Attribute | Detail |
|---|---|
| Goal | List products, manage inventory, process orders, track earnings, grow their store |
| Pain Points | Complicated listing process, slow KYC verification, unclear fee structure, poor visibility in search |
| Needs | Intuitive product upload wizard, bulk product management, real-time sales dashboard, transparent payout system, promotional tools |
| Behaviour | Logs in daily to check orders and messages; highly motivated by earnings data |
| Segment Examples | Graphic designer, video editor, music producer, software developer, 3D artist |

### 2.4 Moderator
| Attribute | Detail |
|---|---|
| Goal | Review new product listings, ensure policy compliance, resolve disputes between buyers and sellers |
| Pain Points | High volume of listings to review, unclear policy edge cases, no bulk review tools |
| Needs | Queue-based review system with filtering, quick approval/rejection with templated feedback, dispute resolution workspace |
| Behaviour | Works through moderation queue in batches; needs efficient workflows |

### 2.5 Support Agent
| Attribute | Detail |
|---|---|
| Goal | Answer user tickets, resolve account issues, help with order problems |
| Pain Points | Repetitive questions, no canned responses, difficulty accessing user context |
| Needs | Integrated ticket system with canned responses, user order history visible in ticket view, real-time chat with users |
| Behaviour | Handles 10–30 tickets per shift; needs macros and shortcuts |

### 2.6 Admin (Platform Owner)
| Attribute | Detail |
|---|---|
| Goal | Monitor platform health, manage users and sellers, view analytics, configure platform settings |
| Pain Points | Fragmented data, no real-time overview, unable to quickly drill into issues |
| Needs | Role-based admin panels, real-time metrics dashboard, user management CRUD, system configuration UI, moderation oversight |
| Behaviour | Checks platform metrics multiple times daily; occasional deep-dive investigations |

### 2.7 Affiliate
| Attribute | Detail |
|---|---|
| Goal | Generate referral links, track clicks and conversions, earn commission on referred sales |
| Pain Points | No visibility into which links are performing, delayed commission data, unclear payout schedule |
| Needs | Affiliate dashboard with link generator, click/conversion tracking, commission history, payout management |
| Behaviour | Shares links on social media, blogs, YouTube; checks dashboard weekly |

---

## 3. Information Architecture

### 3.1 Main Navigation (Public Header)

```
[HOME] [CATEGORIES ▼] [SELL] [BLOG] [HELP]               [🔍] [🛒] [LOGIN / REGISTER]
```

- **HOME** — Landing page with hero, featured products, trending sellers
- **CATEGORIES** — Mega menu with all top-level categories, subcategories, and featured items
- **SELL** — Seller registration/application landing page
- **BLOG** — Platform blog with articles, tips, updates
- **HELP** — Help centre with FAQ, guides, contact support

### 3.2 User Menu (Authenticated Header)

```
[User Avatar ▼]
├── Dashboard
├── My Orders
├── Wallet
├── Messages
├── Profile Settings
├── Affiliate Dashboard   (if affiliate)
├── Seller Dashboard      (if seller)
├── Admin Panel           (if admin)
└── Logout
```

### 3.3 Dashboard Sidebar (Role-Specific)

**Buyer Sidebar:**
```
Dashboard
├── Overview
├── My Orders
├── Downloads
├── Reviews
├── Wishlist
├── Wallet / Credits
└── Messages
```

**Seller Sidebar:**
```
Dashboard
├── Overview
├── Products
│   ├── All Products
│   ├── Add New Product
│   └── Categories
├── Orders
│   ├── All Orders
│   └── Refunds
├── Analytics
│   ├── Sales Report
│   └── Product Performance
├── Wallet
│   ├── Balance
│   └── Withdrawals
├── Store Settings
├── Reviews
└── Messages
```

**Admin Sidebar:**
```
Dashboard
├── Overview
├── Users
│   ├── All Users
│   ├── Buyers
│   ├── Sellers
│   └── Affiliates
├── Products
│   ├── All Products
│   ├── Moderation Queue
│   └── Categories
├── Orders
│   ├── All Orders
│   └── Disputes
├── Payouts
├── Affiliates
├── Content
│   ├── Blog
│   └── Pages
├── Reports
├── Support Tickets
└── System Settings
```

### 3.4 Footer

```
[Logo]                    [Quick Links]          [Support]          [Social]
About Us                  Home                   Help Centre        Facebook
Terms of Service          Browse Products        Contact Us         Twitter
Privacy Policy            Categories             Email Support      LinkedIn
Refund Policy             Sell                   24/7 Chat          Instagram
Cookie Policy             Blog                                       YouTube

                                    © TRUE STAR BD LIMITED
```

### 3.5 Sitemap Hierarchy

```
/
├── (public)
│   ├── /                     — Homepage
│   ├── /products             — Product listing (all)
│   ├── /products?category=X  — Product listing (filtered)
│   ├── /product/[slug]       — Product detail
│   ├── /cart                 — Shopping cart
│   ├── /checkout             — Checkout flow
│   ├── /checkout/confirm     — Order confirmation
│   ├── /categories           — All categories
│   ├── /category/[slug]      — Category detail with products
│   ├── /search?q=            — Search results
│   ├── /sell                 — Sell landing page
│   ├── /blog                 — Blog listing
│   ├── /blog/[slug]          — Blog article
│   ├── /help                 — Help centre
│   ├── /help/[article]       — Help article
│   ├── /help/contact         — Contact form
│   ├── /store/[slug]         — Seller store front
│   ├── /about                — About page
│   ├── /terms                — Terms of service
│   ├── /privacy              — Privacy policy
│   ├── /refund               — Refund policy
│   └── /404                  — Not found
│
├── (auth)
│   ├── /auth/login           — Login
│   ├── /auth/register        — Registration
│   ├── /auth/forgot-password — Password reset
│   ├── /auth/verify-email    — Email verification
│   └── /auth/oauth/callback  — OAuth callbacks
│
├── (dashboard — buyer)
│   ├── /dashboard            — Buyer overview
│   ├── /dashboard/orders     — Order history
│   ├── /dashboard/downloads  — Digital downloads
│   ├── /dashboard/reviews    — My reviews
│   ├── /dashboard/wishlist   — Saved items
│   ├── /dashboard/wallet     — Credits / transactions
│   ├── /dashboard/messages   — Conversations
│   └── /dashboard/profile    — Profile settings
│
├── (dashboard — seller)
│   ├── /seller               — Seller dashboard overview
│   ├── /seller/products      — Product management
│   ├── /seller/products/new  — Add product
│   ├── /seller/products/[id] — Edit product
│   ├── /seller/orders        — Order management
│   ├── /seller/analytics     — Sales reports
│   ├── /seller/wallet        — Earnings & withdrawals
│   ├── /seller/settings      — Store settings
│   ├── /seller/reviews       — Product reviews
│   └── /seller/messages      — Conversations
│
├── (dashboard — admin)
│   ├── /admin                — Admin overview
│   ├── /admin/users          — User management
│   ├── /admin/products       — Product management
│   ├── /admin/products/moderation — Moderation queue
│   ├── /admin/orders         — Order management
│   ├── /admin/disputes       — Dispute resolution
│   ├── /admin/payouts        — Payout management
│   ├── /admin/affiliates     — Affiliate management
│   ├── /admin/content        — Content management
│   ├── /admin/reports        — Analytics & reports
│   ├── /admin/support        — Support tickets
│   └── /admin/settings       — Platform configuration
│
└── (affiliate)
    └── /affiliate            — Affiliate dashboard
```

---

## 4. Key User Flows

### 4.1 Buyer Flow (End-to-End)

**Step 1: Homepage Entry**
- **Layout:** Full-bleed hero with gradient background. Central search bar with placeholder text ("Search for digital products..."). Below: category icon grid, featured products horizontal scroll, trending seller carousel.
- **Elements:** Logo (top-left), navigation bar, CTA buttons ("Start Selling", "Browse Products"), trust badges (ratings, users, products sold count).
- **Interactions:** Search bar expands on focus with recent searches. Category cards scale on hover. Product cards have a quick "Add to Wishlist" heart icon.
- **States:** Loading — skeleton placeholders for featured products and categories. Empty — first-time visitor sees a welcome banner.

**Step 2: Browse Categories**
- **Layout:** Full-width category grid (6 columns desktop, 3 tablet, 2 mobile). Each card: icon/illustration + category name + subcategory count.
- **Elements:** Breadcrumb (Home > Categories), page title, category cards.
- **Interactions:** Clicking a card navigates to the filtered product listing page. Hover reveals a subtle shadow elevation.
- **States:** Loading — skeleton squares. Empty — (should never occur if categories are seeded).

**Step 3: Product Listing**
- *(Detailed in Section 4.3 — Search & Browse)*

**Step 4: Product Detail**
- *(Detailed in Section 4.4 — Product Detail)*

**Step 5: Add to Cart**
- **Layout:** On product detail page, right sidebar (desktop) or sticky bottom bar (mobile) contains quantity selector + "Add to Cart" button + "Buy Now" button.
- **Elements:** Quantity input (number stepper), variant selector (if applicable), price summary, stock status.
- **Interactions:** Clicking "Add to Cart" triggers a success toast + cart icon badge increment. "Buy Now" adds to cart then navigates directly to checkout. Quantity stepper has +/- buttons with min/max validation.
- **States:** In stock — green badge, add enabled. Out of stock — red badge, button disabled. Adding — button shows spinner (200ms optimistic). Success — toast slides in from top-right. Error — toast with error message.

**Step 6: Cart**
- *(Detailed in Section 4.5 — Cart)*

**Step 7: Checkout**
- *(Detailed in Section 4.6 — Checkout)*

**Step 8: Payment**
- **Layout:** Payment step within checkout. Card input with branded fields, or payment method selection (bKash, Nagad, Rocket, SSLCommerz, Stripe).
- **Elements:** Payment form with inline validation, saved payment methods (radio list), "Add New Card" form, billing address toggle, secure badge.
- **Interactions:** Selecting a saved method shows masked card details. Entering new card triggers real-time formatting and validation. Processing shows full-page overlay with spinner. Success/failure redirects to confirmation or shows error.
- **States:** Idle — payment form ready. Validating — inline field validation on blur. Processing — overlay spinner with "Please don't close this page". Success — redirect to confirmation. Failed — error message + retry option.

**Step 9: Download**
- **Layout:** Order confirmation page with large download button, product thumbnail, order number, and "View in Dashboard" link.
- **Elements:** Download button (primary CTA), email confirmation notice, order summary table, support contact link.
- **Interactions:** Clicking download initiates the file download. Button shows progress if file is large. Confirmation email is sent. Button to "Go to My Orders" for future access.
- **States:** Pre-download — button pulsing gently. Downloading — progress bar. Downloaded — success checkmark + "Download Again" option.

### 4.2 Seller Flow (End-to-End)

**Step 1: Register**
- **Layout:** Standard registration form (name, email, password). Role selection radio: "I want to buy" / "I want to sell". Bottom: "Already have an account? Log in".
- **Elements:** Input fields with validation icons, role toggle, terms checkbox, submit button.
- **Interactions:** Select "I want to sell" reveals additional store name field. Form validates on blur. Submit shows loading state.
- **States:** Idle, validating, submitting, success (redirect to verify email), error (field-level or summary).

**Step 2: Apply as Seller**
- **Layout:** Application wizard with steps: 1. Personal Info → 2. Store Info → 3. KYC Documents → 4. Submit.
- **Elements:** Stepper indicator (top), form content (center), navigation buttons (back/next/submit).
- **Interactions:** Step indicator is clickable to revisit completed steps. Each step validates before allowing "Next". File upload for KYC documents (NID, trade license, etc.) with drag-drop zone.
- **States:** Current — active step highlighted. Completed — green check. Pending — grey. Error — red with message.

**Step 3: KYC Verification**
- **Layout:** Document upload screen with clear instructions. Two columns on desktop: instructions left, upload zone right.
- **Elements:** Upload zone (drag-drop + click), accepted formats list, file size limits, preview of uploaded documents, status badges.
- **Interactions:** Drag file over zone shows highlight border. Upload shows progress bar. Success shows green check. Rejection shows reason + re-upload option. Documents are verified by moderator (manual or automated).
- **States:** Not submitted, pending review, verified, rejected (with reason). Banner at top shows current status.

**Step 4: Store Setup**
- **Layout:** Single-page settings form with sections: Store Name, Store Description, Store Logo, Cover Image, Social Links, Store Policy, Contact Info.
- **Elements:** Image upload with crop for logo/cover, rich text editor for description, URL inputs for social links, toggle for store active/inactive.
- **Interactions:** Logo upload shows preview with crop modal. Cover image upload with focal point selector. Description editor supports basic formatting (bold, italic, lists).
- **States:** Draft — not visible to public. Active — store live. Needs attention — incomplete required fields highlighted.

**Step 5: Add Product**
- **Layout:** Product upload wizard with tabs or stepper: 1. Basic Info → 2. Media → 3. Variants → 4. Pricing → 5. Delivery → 6. Preview & Publish.
- **Elements:**
  - **Basic Info:** Title, description (rich text), category (cascading dropdown), tags (autocomplete chips)
  - **Media:** Image upload (up to 10, drag-reorderable), video URL (optional), preview thumbnails
  - **Variants:** Table of variant options (name, price, stock), add row button, bulk price editor
  - **Pricing:** Base price, sale price (optional), minimum price, commission preview
  - **Delivery:** File upload for digital product, delivery type (instant/scheduled), file size display
  - **Preview:** Live preview of product detail page as buyers would see it
- **Interactions:** Media reorder via drag-and-drop. Variants table supports inline editing. Commission preview updates in real-time as price changes. Preview tab renders the product detail page in an iframe or simulated view.
- **States:** Draft (saved but not submitted), Pending (awaiting moderation), Approved, Rejected (with reason), Published.

**Step 6: Manage Orders**
- **Layout:** Orders table with columns: Order ID, Product, Buyer, Amount, Date, Status, Actions. Filter tabs: All, Pending, Processing, Completed, Cancelled, Refund.
- **Elements:** Data table with sortable columns, status badges, action dropdown per row, search bar, date range picker.
- **Interactions:** Click order row expands or navigates to order detail. Action menu includes: Mark as Delivered, Contact Buyer, Issue Refund. Bulk actions for selected orders.
- **States:** Empty — "No orders yet" illustration. Loading — skeleton rows. Error — retry button.

**Step 7: Withdraw Earnings**
- **Layout:** Wallet page with balance card (available, pending, total), withdrawal form, withdrawal history table.
- **Elements:** Balance card with large number, "Withdraw" button, method selector (bank, bKash, Nagad), amount input, history table.
- **Interactions:** Clicking "Withdraw" opens a modal or expands the form. Method selector shows relevant fields (account number, bank details). Amount input shows max limit and fee preview. Submission shows confirmation dialog.
- **States:** Balance zero — withdraw disabled with message. Pending withdrawal — badge on withdrawal history. Completed — green check. Failed — red badge with reason.

### 4.3 Search & Browse (Detailed)

**Search Bar (Global)**
- **Layout:** Full-width input with search icon (left) and clear button (right, visible on input). Auto-suggest dropdown below.
- **Elements:** Input field, search icon, clear (X) button, dropdown container.
- **Interactions:**
  - On focus: dropdown appears with recent searches (if any) and trending searches
  - On type (debounced 300ms): dropdown shows suggested products (image + name + price + rating), suggested categories, and "View all results for [query]"
  - On Escape: dropdown closes
  - On Enter: navigates to search results page
  - On click outside: dropdown closes
  - On clear: empties input, keeps focus
- **States:** Idle — placeholder text. Focused — dropdown appears. Typing — suggestions loading (skeleton). Results — populated list. No results — "No suggestions found". Selected — navigates to product or search results.

**Filter Panel (Product Listing Page)**
- **Layout:** Left sidebar on desktop (280px). Bottom sheet drawer on mobile (slides up, 80% height).
- **Elements:**
  - Category filter: checkbox tree or collapsible list
  - Price range: dual slider with min/max inputs
  - Rating: clickable star rows (4★ & up, 3★ & up, etc.)
  - Delivery time: radio buttons (Instant, Within 24h, Within 3 days)
  - File type: checkboxes (PDF, MP3, ZIP, PSD, etc.)
  - Seller type: checkboxes (Verified, Top Rated)
  - Active filters: chip row above results (removable chips)
  - "Clear All Filters" link
  - "Apply Filters" button (mobile only)
- **Interactions:**
  - Price slider: dual handle, values update in real-time on bound inputs
  - Checkboxes: toggle on/off, filters apply immediately on desktop (no Apply button)
  - Mobile: Apply button applies all selected filters and closes drawer
  - Filter chips: click X to remove individual filter, animation on removal
  - Active filter count shown on mobile filter button
- **States:** No filters — all options unchecked. Active filters — chips visible, filter controls reflect selections. No results — empty state. Loading — skeleton filters (grey blocks).

**Sort Options**
- **Layout:** Dropdown positioned above product grid, right-aligned.
- **Options:**
  - Relevance (default)
  - Price: Low to High
  - Price: High to Low
  - Newest First
  - Best Selling
  - Top Rated
- **Interactions:** Selection updates product grid with transition animation. Current selection displayed as dropdown label.
- **States:** Selected option highlighted in dropdown list.

**Product Grid**
- **Layout:** Responsive grid — 4 columns (desktop), 3 (tablet), 2 (small tablet), 1 (mobile). Cards with consistent aspect ratio.
- **Card Elements:** Product thumbnail (16:9 or 4:3), title (2-line truncation), price (current + original strikethrough if on sale), rating (stars + count), seller name, badges (Top Rated, Verified, Best Seller, New).
- **Interactions:** Card hover — subtle elevation increase, "Quick View" button appears (desktop). Card click — navigates to product detail. Heart icon — add/remove from wishlist (optimistic, toggle animation).
- **States:** Loading — skeleton cards (animated grey rectangles). Empty — illustration + message. Loaded — animated entrance (staggered fade-up). Error — retry button.

**Pagination vs Infinite Scroll**
- **Desktop:** Pagination with page numbers, prev/next buttons, "Show per page" selector (24, 48, 72).
- **Mobile:** Infinite scroll — loading spinner at bottom triggers next page load automatically.
- **Edge:** If total results < 24, pagination hidden entirely.

### 4.4 Product Detail (Detailed)

**Layout Structure (Desktop)**
```
┌─────────────────────────────────────────────────────────────┐
│ Breadcrumb: Home > Category > Subcategory > Product Title    │
├──────────────────────────┬──────────────────────────────────┤
│                          │  Product Title                   │
│   Image Gallery          │  ⭐ 4.8 (120 reviews)            │
│                          │  $29.99  <s>$49.99</s>  -40%    │
│   Main Image             │                                  │
│   [viewport]             │  Variant: [Dropdown / Buttons]   │
│                          │  Quantity: [-] 1 [+]             │
│   Thumbnail Strip        │                                  │
│   [1] [2] [3] [4] [5]   │  ———————————————                  │
│                          │  Add to Cart  │  Buy Now         │
│                          │  ———————————————                  │
│                          │  💖 Add to Wishlist  🔗 Share   │
│                          ├──────────────────────────────────┤
│                          │  Seller Info                    │
│                          │  [Avatar] Store Name            │
│                          │  ⭐ 4.9  |  Response < 1hr     │
│                          │  Member since Jan 2024          │
│                          │  [Visit Store]                  │
│                          ├──────────────────────────────────┤
│                          │  Product Summary                │
│                          │  • Instant Download             │
│                          │  • 100 MB ZIP file              │
│                          │  • License: Commercial Use      │
│                          │  • 30-Day Money Back            │
├──────────────────────────┴──────────────────────────────────┤
│  Tabs: Description | Reviews | FAQ                          │
│                                                             │
│  [Tab content panel]                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Image Gallery**
- **Main Image:** Large viewport with zoom on hover (desktop). Click to open lightbox.
- **Thumbnails:** Horizontal strip below main image. Active thumbnail has highlighted border.
- **Lightbox:** Full-screen overlay with navigation arrows, close button, image counter ("3 / 10").
- **Interactions:** Hover on main image — zoom lens follows cursor. Click thumbnail — smooth crossfade to new image. Swipe on mobile — navigate between images. Lightbox — keyboard arrows navigate, Escape closes.
- **States:** Loading — image skeleton/pulsing placeholder. Error — broken image fallback with retry. No image — placeholder illustration.

**Product Information Panel (Right Sidebar)**
- **Title:** Large heading, 2 lines max.
- **Rating:** Stars (SVG) + numeric average + review count link. Click count to scroll to reviews tab.
- **Price:** Current price (large, bold), original price (strikethrough, grey), discount percentage badge (red).
- **Variant Selector:** Dropdown (if many variants) or button group (if 2-5). Selected variant updates price, stock status, and image.
- **Quantity Stepper:** Minus/Plus buttons with numeric input. Min 1, max = available stock.
- **Action Buttons:**
  - "Add to Cart" — Primary, full-width. Adds item, shows success toast, updates cart badge.
  - "Buy Now" — Secondary but prominent. Adds to cart + redirects to checkout.
  - States: Default, Hover (slight darken), Active (press), Loading (spinner overlay), Disabled (out of stock).
- **Wishlist & Share:** Icon buttons. Wishlist toggles heart fill with animation. Share opens native share dialog (mobile) or copy-link tooltip (desktop).

**Tabs Section**
- **Description Tab:** Rich text rendered content. Headings, paragraphs, lists, images. No editing — pure display.
- **Reviews Tab:**
  - Rating breakdown chart (horizontal bars: 5★, 4★, etc. with percentage)
  - Sort dropdown: Most Recent, Highest Rated, Lowest Rated, Most Helpful
  - Review cards: avatar, name, date, rating stars, review text, helpful/unhelpful buttons, "Report" link
  - Pagination for reviews (10 per page)
  - "Write a Review" button (opens modal for buyers who purchased)
- **FAQ Tab:**
  - Expandable accordion items. Click question to expand/collapse answer. Only one open at a time or multiple (accordion pattern).
  - "Ask a Question" link if question isn't answered.

**Seller Card (Sidebar)**
- Avatar (48px), store name (link to store front), rating badge, response time, member since date.
- "Visit Store" button — link to store front page with all seller's products.
- Badges: Verified, Top Rated, Phone Verified, ID Verified.

**Mobile Layout (Product Detail)**
- Single column: Gallery (full-width) → Info → Tabs
- Sticky bottom bar: Price (left) + Quantity Stepper + "Add to Cart" button (right)
- Gallery is swipeable full-width carousel (no zoom on mobile)
- Tabs become collapsible sections (accordion style)
- Seller card is a horizontal row below the tabs

### 4.5 Cart (Detailed)

**Layout Structure**
```
┌──────────────────────────────────────────────────────────────┐
│  Header: Shopping Cart (item count)                          │
├───────────────────────────────────────┬──────────────────────┤
│  [Product Table]                      │  Order Summary       │
│                                       │                      │
│  ┌─────────────────────────────────┐  │  Subtotal: $59.98   │
│  │ [IMG] Product Name              │  │  Discount: -$5.00   │
│  │       Variant: Premium          │  │  Coupon: [input]    │
│  │       Unit Price: $29.99        │  │          [Apply]    │
│  │       Qty: [-] 2 [+]    $59.98  │  │                      │
│  │       [Remove] [Wishlist]       │  │  │                  │
│  └─────────────────────────────────┘  │  Total: $54.98     │
│                                       │                      │
│  ┌─────────────────────────────────┐  │  [Proceed to         │
│  │ [IMG] Another Product           │  │   Checkout]          │
│  │       ...                       │  │                      │
│  └─────────────────────────────────┘  │                      │
│                                       │                      │
│  [Continue Shopping]                  │  [PayPal] [bkash]    │
│                                       │                      │
├───────────────────────────────────────┴──────────────────────┤
│  Footer                                                     │
└──────────────────────────────────────────────────────────────┘
```

**Cart Items**
- **Row Elements:** Thumbnail (80×80px), product name (link to detail), variant label, unit price, quantity stepper, line total, remove button.
- **Quantity Selector:** +/- buttons with min 1, max stock. Updates line total in real-time with animation (number flips).
- **Remove:** Click shows confirmation toast with "Undo" action. Item fades out. If last item removed, show empty cart.
- **Wishlist:** Secondary action — moves item from cart to wishlist with success message.

**Coupon Input**
- **Layout:** Text input + "Apply" button inline.
- **Interactions:** Enter code → click Apply → validation spinner → success (green check, discount updates) or error (red message, shake animation). Applied coupon shown as removable chip below input.
- **States:** Idle, Applying (spinner), Applied (green), Invalid (red), Expired (red with message).

**Order Summary**
- Subtotal line, discount line (if coupon applied), delivery fee (if applicable), total line (bold, larger).
- "Proceed to Checkout" button (primary, full-width). Disabled if cart is empty.
- Payment method icons below button (trust signal).

**Empty Cart State**
- Centered illustration (empty shopping cart graphic)
- Title: "Your cart is empty"
- Subtitle: "Looks like you haven't added anything yet"
- CTA: "Browse Products" button (primary)
- Below: "Trending Products" horizontal scroll (optional, to re-engage)

### 4.6 Checkout (Detailed)

**Multi-Step Checkout Flow**

**Step Indicator (Top)**
```
Step 1: Address  ────  Step 2: Payment  ────  Step 3: Review  ────  ✓ Confirmation
     ●━━━━━━━━━━━━━━━━━○━━━━━━━━━━━━━━━━━○━━━━━━━━━━━━━━━━━○
```

**Step 1: Shipping/Billing Address**
- **Layout:** Form with sections: Shipping Address, Billing Address (toggle: "Same as shipping").
- **Fields:** Full Name, Phone, Street Address, City, State/Division, ZIP Code, Country (dropdown).
- **Saved Addresses:** Radio list of previously saved addresses. Selecting auto-fills the form. "Add New Address" button.
- **Interactions:** "Same as billing" toggle collapses billing section. Country dropdown cascades to state dropdown. Phone number formatted with country code prefix. Zip code validation.
- **States:** Saved addresses shown as selectable cards with green check when selected. Form fields validate on blur.

**Step 2: Payment Method**
- **Layout:** Payment method cards (radio selection). Each card shows method icon, name, and relevant details.
- **Methods:**
  - Credit/Debit Card (Visa, Mastercard, Amex — SSLCommerzy)
  - bKash
  - Nagad
  - Rocket
  - PayPal
- **Card Form:** Card number (auto-format with spaces), expiry (MM/YY), CVC, cardholder name. Saved cards shown as masked options with CVV-only input.
- **Mobile Wallet:** bKash/Nagad — phone number input + OTP flow description.
- **Interactions:** Selecting a method shows the relevant form below. Card fields format automatically. Saved card selection reveals only CVV field. OTP flow opens modal for mobile wallets.

**Step 3: Order Review**
- **Layout:** Two columns — items summary (left) + order summary sidebar (right, sticky).
- **Review Items:**
  - Product list (read-only): image, name, variant, quantity, price
  - Shipping address (read-only with "Edit" link)
  - Payment method (masked, read-only with "Edit" link)
  - Coupon applied (if any)
- **Order Summary:** Subtotal, discount, total. All read-only.
- **Action:** "Place Order" button (primary, prominent). Below: "By placing this order, you agree to our Terms of Service and Refund Policy."
- **Interactions:** Edit links scroll to relevant step and open it for editing without losing progress on other steps. "Place Order" triggers payment processing overlay.

**Step 4: Confirmation**
- **Layout:** Success animation (checkmark grows + confetti on desktop), large "Order Placed!" heading.
- **Elements:**
  - Order number (copyable)
  - "Download Now" button (primary, large) — for digital products
  - Email confirmation notice
  - Order summary (compact)
  - "View My Orders" link
  - "Continue Shopping" link
- **Interactions:** Download button initiates file download. "Copy" button next to order number shows brief "Copied!" tooltip. Page auto-redirects to order detail after 30 seconds of inactivity.

**Mobile Checkout**
- Single column. Summary at top, form below. No sticky sidebar (summary calculated in real-time below each step).
- Step indicator condensed to dots.
- Bottom "Continue to Payment" / "Place Order" sticky bar.

### 4.7 Registration & Onboarding (Detailed)

**Sign Up**
- **Layout:** Centered card (max-width 480px). Logo at top.
- **Fields:** Full Name, Email Address, Password (with strength meter), Confirm Password.
- **Role Selection:** Two large toggle cards — "I want to Buy" (shopping bag icon) / "I want to Sell" (store icon). Visual difference: selected card has accent border + checkmark.
- **Terms:** Checkbox — "I agree to the Terms of Service and Privacy Policy".
- **Social Login:** Google, Facebook, GitHub buttons (optional, platform-dependent).
- **Submit:** "Create Account" button.
- **Interactions:** Password strength meter updates in real-time (weak/medium/strong with color). Role selection is visual toggle, not radio. Social login buttons trigger OAuth flow.
- **States:** Idle, validating, submitting, success (redirect to verify email), error (email already exists, weak password, etc.).

**Email Verification**
- **Layout:** Centered card. Envelope icon with "Check your email" message.
- **Elements:** Email displayed (masked: u***@example.com), "Resend Email" link (with cooldown timer), "Enter Code" manual input option (alternate path).
- **Interactions:** On page load, verification email sent automatically. Resend button disabled for 60 seconds with countdown. Manual code entry: 6 separate digit inputs, auto-advance on type, paste support.
- **States:** Email sent (default), Resending (spinner + disabled), Resent (confirmation), Verified (redirect to profile completion), Expired (resend prompt).

**Profile Completion (Buyer)**
- **Layout:** Single-page form with avatar upload, fields.
- **Fields:** Profile Picture (optional, with crop), Phone Number, Address (optional).
- **Interests:** Tag selector — select categories of interest (for personalised recommendations).
- **Actions:** "Skip for Now" (link) / "Complete Profile" (button).
- **Behaviour:** After completion, redirect to homepage with welcome toast. Returning users skip this step.

**Profile Completion (Seller)**
- Triggered after selecting "I want to sell" during registration.
- Immediately redirects to seller application (see Section 4.2, Step 2-4).
- If KYC is pending, seller dashboard shows banner: "Your application is under review. You'll be notified once approved." Limited access to store setup (can draft but not publish).

---

## 5. Page-by-Page UI Specifications

### 5.1 Homepage

**Hero Section**
- **Layout:** Full-width, full-viewport-height on desktop. Background: gradient (brand primary to secondary) with subtle animated patterns or shapes (Framer Motion floating particles or mesh gradient).
- **Content:**
  - Headline: "Discover Premium Digital Products" (40px, bold, white)
  - Subheadline: "From graphics to code — source everything you need for your next project" (18px, regular, white/80%)
  - Search bar: prominently centred, 600px max-width, rounded-full, large input, search icon, placeholder "Search for digital products..."
  - CTA buttons: "Start Selling" (outline white) | "Browse Products" (white solid)
  - Trust indicators: Below search — "10,000+ Products | 5,000+ Sellers | 50,000+ Happy Customers" (icons + numbers)
- **States:** Loaded — animated entrance (staggered fade-up: headline → subheadline → search → stats). Reduced motion — simple fade-in.

**Category Grid**
- **Layout:** Section with heading "Browse by Category" + "View All" link. 8-12 category cards in a responsive grid (6 cols desktop, 4 tablet, 2 mobile).
- **Card Design:** Icon (48px, brand-specific illustration) + category name + product count. Card is rectangular, subtle shadow, rounded corners.
- **Interactions:** Hover — slight scale (1.03) + shadow elevation. Click — navigate to /products?category=slug.

**Featured Products Section**
- **Layout:** "Featured Products" heading. Horizontal scrollable row with overflow-x: auto, snap-scroll on mobile. Arrow buttons on desktop (prev/next).
- **Card Design:** 280px wide, product image (aspect ratio 4:3), title (truncated), price, rating, seller name, wishlist heart.
- **Interactions:** Scroll via mouse wheel/trackpad (desktop) or swipe (mobile). Arrow buttons scroll by one card width.

**Trending Sellers Section**
- **Layout:** "Top Sellers" heading. Horizontal row of seller cards.
- **Card Design:** Avatar (64px circle), store name, rating (stars + number), badge (Verified, Top Rated), product count.
- **Interactions:** Click navigates to /store/[slug]. Hover shows slight elevation.

**Trust Signals Section**
- **Layout:** Grid of 4-6 trust pillars: Secure Payments, Instant Delivery, Quality Guaranteed, 24/7 Support, Easy Returns. Each with icon + title + short description.
- **Design:** Clean icons (line art, consistent stroke), centred text below.

**Testimonials**
- **Layout:** Carousel or grid of testimonial cards (avatar, name, role, quote, rating stars).
- **Auto-rotation** on desktop (5s interval) with pause on hover. Dots navigation below.

**Call-to-Action Banner**
- **Layout:** Full-width section with background image/gradient. "Ready to sell your digital products?" heading + "Start Selling Today" button.
- **Stats:** "Earn up to 70% commission | No monthly fees | Instant payouts"

**Footer** (as specified in Navigation Architecture)

### 5.2 Product Listing Page (PLP)

**Layout (Desktop)**
```
┌──────────────────────────────────────────────────────────────────┐
│ Breadcrumb: Home > Category                                      │
│ Heading: "Graphics" (with product count: "2,340 products")       │
├──────────┬───────────────────────────────────────────────────────┤
│ Filters  │  Active Filters: [Graphics] [Under $50] [✕ Clear All] │
│          │                                                       │
│ Category │  Sort: [Relevance ▼]           View: [Grid] [List]   │
│ ☐ All    │                                                       │
│ ☐ Logos  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐               │
│ ☐ Icons  │  │Card 1│ │Card 2│ │Card 3│ │Card 4│               │
│ ☐ Fonts  │  └──────┘ └──────┘ └──────┘ └──────┘               │
│          │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐               │
│ Price    │  │Card 5│ │Card 6│ │Card 7│ │Card 8│               │
│ [====●--●====] │  └──────┘ └──────┘ └──────┘ └──────┘               │
│ $10  $100 │                                                       │
│          │  < 1  2  3  4  5 ... 10 >                             │
│ Rating   │                                                       │
│ [★★★★☆] │                                                       │
│ [★★★☆☆] │                                                       │
│          │                                                       │
│ Delivery │                                                       │
│ ○ Instant│                                                       │
│ ○ < 24hr │                                                       │
│          │                                                       │
│ [Apply]  │                                                       │
├──────────┴───────────────────────────────────────────────────────┤
│ Footer                                                          │
└──────────────────────────────────────────────────────────────────┘
```

**Desktop Filter Panel (Left Sidebar)**
- 280px width, starts collapsed. "Filters" toggle button shows/hides sidebar.
- Filter groups separated by light dividers, each with collapsible heading.
- Price range: dual-range slider with numeric min/max inputs. Default range: $0 — highest price in results.
- Rating: clickable star rows with checkbox. "4★ & up", "3★ & up", etc.
- All filters applied immediately on change (desktop). "Clear All" link at bottom.

**Product Count**
- Displayed in heading: "Graphics (2,340 products)"
- Updates in real-time as filters change (with counter animation).

**Active Filter Chips**
- Row between breadcrumbs and product grid. Removable chips for each active filter.
- "Clear All" link at end. Chips animate in/out.

**Sort Dropdown**
- Right-aligned above grid. Options: Relevance (default), Price: Low-High, Price: High-Low, Newest, Best Selling, Top Rated.

**View Toggle**
- Grid (default) / List. Grid shows product cards; list shows horizontal rows with more detail (description preview, larger image).

**Product Card (Grid)**
- Width: flexible (25% — 4 cols). Card: white background, border, rounded corners (12px), shadow-sm.
- Content: Image (16:9 aspect ratio, object-fit: cover), badge overlay (top-left: -40%, New, Top Rated), wishlist heart (top-right).
- Below image: Title (2-line clamp), seller name, rating stars + count, price (current + original strikethrough).

**Mobile Product Listing Page**
- Filters accessible via bottom sheet (slides up, 80vh, drag handle at top).
- "Filter" button in top bar with active filter count badge.
- Product grid: 2 columns on small tablet, 1 column on phone.
- Infinite scroll instead of pagination.
- Sort dropdown persists at top.

### 5.3 Product Detail Page (PDP)

**Breadcrumb**
- Home > Category > Subcategory > Product Title (truncated on mobile).

**Image Gallery**
- **Desktop:** Large main image (600×450px) + thumbnail strip below (5-10 thumbnails, 80×60px each). Active thumbnail highlighted. Zoom on hover: magnifier glass effect. Click opens lightbox (full-screen overlay, arrow navigation, close button).
- **Mobile:** Full-width swipeable carousel. Dot indicators. No hover zoom. Pinch-to-zoom supported.
- **States:** Loading — skeleton rectangle. Error — fallback placeholder with "Image not available".

**Product Information Panel**
- **Title:** H2 (28px desktop, 22px mobile), max 2 lines.
- **Rating:** Star SVG + "4.8 (120 reviews)" — clickable, scrolls to reviews.
- **Price:**
  - Sale price: large (32px), bold, accent colour.
  - Original price: strikethrough (18px), grey, 60% opacity.
  - Discount badge: "40% OFF" — small red pill badge.
- **Short Description:** 2-3 lines, grey text.
- **Variant Selector:** If applicable. Button group (2-5 variants) or dropdown (>5 variants). Selected variant updates price, stock, and main image.
- **Quantity:** Stepper component (- 1 +). Min 1, max stock.
- **Action Buttons:**
  - "Add to Cart" — primary, full-width (or 50% split with Buy Now).
  - "Buy Now" — secondary, full-width (or 50% split). Skips cart, goes to checkout.
  - States: normal, hovering, active, loading (spinner replaces text), disabled (grey + "Out of Stock").
- **Wishlist:** Heart icon with badge text. Toggle animation.
- **Share:** Icon button → native share sheet (mobile) / tooltip with copy link (desktop).

**Seller Card**
- Avatar (48px), store name (link), rating, response time, member since, badge(s).
- "Visit Store" button — goes to store front.
- Additional trust: "Verified Seller" badge, "Phone Verified", "ID Verified".

**Product Summary Box**
- Card with key details: Instant Download, File size, License type, Money-back guarantee.
- Icons for each bullet point.

**Tabs Section**
- **Description:** Full rich text rendering. No limit.
- **Reviews:**
  - Rating breakdown chart (horizontal bars: 5★ 60%, 4★ 25%, etc.)
  - Total review count + average rating
  - Sort: Recent, Highest, Lowest, Helpful
  - Review cards: Avatar, name, date, rating, text, helpful buttons, report
  - Pagination (10/page)
  - "Write a Review" button (opens modal for verified buyers)
- **FAQ:** Accordion. Question header clickable → expand/collapse answer. Icon indicator (chevron rotates).

**Sticky Add to Cart (Mobile)**
- Fixed bottom bar. Left: price (large). Right: quantity stepper + "Add to Cart" button. Appears on scroll past the action button area.

### 5.4 Cart Page

**Layout:** Two-column on desktop (items list 65% + order summary 35%). Single column on mobile.

**Items List:**
- Each item row: Image (80×80px), name, variant, unit price, quantity stepper, total price, remove icon.
- Divider between items.
- "Continue Shopping" link below list.

**Quantity Stepper:**
- Minus button | number display | Plus button.
- Min 1, max = stock. Buttons disabled at limits. Number updates total in real-time.

**Remove Action:**
- Click → item fades out with slide-right animation. Toast: "Item removed" with "Undo" button (5s timeout). If last item, show empty cart after removal.

**Coupon Section:**
- Input + Apply button inline.
- Applied: green border + success message + removable chip.
- Error: red border + error message.

**Order Summary:**
| Item | Amount |
|---|---|
| Subtotal (3 items) | $89.97 |
| Discount (SAVE10) | -$9.00 |
| Total | $80.97 |

- "Proceed to Checkout" button (primary, full-width). Disabled if cart empty.
- Payment icons below.

**Empty Cart:**
- Centred illustration, "Your cart is empty", "Browse Products" CTA. Trending products below.

### 5.5 Checkout Page

**Step Indicator:**
- Desktop: horizontal bar with 4 steps. Active step highlighted. Completed steps have green check. Future steps grey.
- Mobile: condensed dot indicator.

**Address Step:**
- Saved addresses as selectable cards. "Add New Address" expands inline form.
- Fields: Country (dropdown → cascade state/city), Street, Apartment, City, State, ZIP, Phone.
- Billing address toggle: "Same as Shipping" (default on). Toggle off reveals billing form.

**Payment Step:**
- Payment method selection: card-style radio buttons with icons.
- Card form: number (auto-space), expiry (MM/YY auto-slash), CVC, name.
- Mobile wallets: phone number input + instructions.
- Saved payment methods: masked card with CVV-only field.

**Review Step:**
- Read-only summary of items, address, payment.
- Edit links inline for each section (opens that step as modal/in-page).
- "Place Order" button (prominent, full-width).
- Terms acceptance text below button.

**Confirmation:**
- Success animation (checkmark + confetti).
- Order number (copyable).
- Download button.
- Email confirmation notice.
- "View Orders" / "Continue Shopping" links.

### 5.6 Buyer Dashboard

**Header:** "Welcome back, [Name]" + current date.

**Overview Cards (Row of 4):**
- Total Orders (with icon) — click navigates to orders
- Wallet Balance (with icon) — click navigates to wallet
- Unread Messages (with icon, red badge count) — click navigates to messages
- Pending Downloads (with icon) — click navigates to downloads

**Recent Orders Table:**
| Order # | Date | Product | Amount | Status | Action |
|---|---|---|---|---|---|
| #TSBL-1024 | Jul 1, 2026 | Brand Kit Pro | $49.99 | ✅ Completed | [Download] |
| #TSBL-1023 | Jun 28, 2026 | Icon Set Vol.3 | $19.99 | ⏳ Processing | [View] |

- Status badges: Completed (green), Processing (yellow/amber), Cancelled (red), Refunded (blue).
- Action column: Download, View, or Contact Seller.

**Quick Links:**
- Grid of icon links: My Orders, Downloads, Reviews, Wishlist, Wallet, Messages, Profile Settings.

**Notification Panel (Right Sidebar, Desktop):**
- Recent notifications list. "Mark all read" link. Each: icon + message + timestamp.

### 5.7 Seller Dashboard

**Metric Cards (Row of 4-5):**
- Revenue Today / This Week / This Month
- Total Orders
- Total Views (last 30 days)
- Conversion Rate (%)
- Pending Actions (new orders, messages — with count badge)

**Revenue Chart:**
- Line chart (last 30 days). X-axis: dates. Y-axis: revenue. Tooltip on hover shows exact value.
- Toggle: 7 days, 30 days, 90 days, 12 months.

**Recent Orders (Requiring Action):**
- Compact table: Order #, Product, Buyer, Amount, Status, Action buttons.
- Action: "Mark as Delivered", "Contact Buyer", "Issue Refund".
- Tab filters: New Orders, Pending Delivery, Completed, Refunds.

**Product Performance (Top 5):**
- Mini table: Product name, views, sales, revenue, conversion.
- Bar chart visual for each product's performance relative to others.

**Quick Actions:**
- Floating action buttons: "Add New Product", "Manage Store", "Withdraw Earnings", "View Analytics".

### 5.8 Admin Dashboard

**Platform Metrics (Row of 6):**
- Total Users | Total Sellers | Total Products | Total Orders | Total Revenue | Active Now
- Each metric card: Icon, large number, label, percentage change vs previous period (green up / red down arrow).

**Charts:**
- **Revenue Trend:** Area chart, monthly granularity, 12 months. Tooltip with exact revenue and order count.
- **User Growth:** Line chart, cumulative + new users per month. Dual axis.
- **Order Volume:** Bar chart, daily for last 30 days with 7-day moving average overlay.

**Moderation Queue:**
- Summary card: "Pending Products: 23" + "View Queue" button.
- "Pending Disputes: 5" + "Resolve Now" button.

**Recent Activity Feed:**
- Scrollable list of recent platform events: "User John registered as seller", "Product 'Premium Icons' was reported", "Order #1024 was refunded".
- Timestamp for each. Colour-coded by type (user, product, order, dispute).

**Quick Links Section:**
- Grid of admin section links with icons: Manage Users, Manage Products, View Reports, Support Tickets, System Settings.

---

## 6. Navigation Architecture

### 6.1 Top Navigation (Public — Unauthenticated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [Logo]  [Categories ▼]  [Sell]  [Blog]  [Help]     [🔍]  [🛒 (0)]  [Login]│
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Logo:** Left-aligned, links to homepage. SVG format for retina. Width: ~140px.
- **Categories:** Dropdown on hover (desktop) or tap (mobile). Mega menu with columns: Category groups with links. "View All" at bottom.
- **Sell:** Link to /sell — prominently styled (outlined or slightly different colour).
- **Blog, Help:** Standard text links.
- **Search Icon:** Toggles search bar expansion on mobile. On desktop, inline search input.
- **Cart:** Icon with badge count (0 when empty, animates on change). Links to /cart.
- **Login / Register:** Rightmost. Dropdown for login form or link to /auth/login. "Register" as secondary link.

### 6.2 Top Navigation (Authenticated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [Logo]  [Categories ▼]  [Sell]  [Blog]  [Help]     [🔍]  [🛒 (2)]  [👤 ▼] │
└─────────────────────────────────────────────────────────────────────────────┘
```

- Same as public, but "Login" replaced with user avatar + dropdown.
- **User Dropdown:**
  - Avatar (32px circle) + name
  - Dashboard
  - My Orders
  - Wallet
  - Messages
  - Profile Settings
  - — divider —
  - Switch to Seller Mode (if buyer+seller)
  - Admin Panel (if admin)
  - Logout

### 6.3 Dashboard Sidebar (Authenticated)

**Desktop:**
- Fixed width: 260px. Dark or white background (brand consistent).
- User info section at top: Avatar, name, email (truncated).
- Navigation items: Icon + label. Active item highlighted.
- Section headers: "General", "Sales", "Account" (grouping).
- Collapsible: hamburger toggle collapses to icon-only (64px) for more content space.

**Mobile:**
- Sidebar hidden by default. Hamburger icon in top bar toggles slide-in drawer (from left, 80% width).
- Overlay behind drawer. Tapping overlay closes drawer.

### 6.4 Mobile Bottom Tab Bar

```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│   🏠     │   📂     │   🛒     │   💬     │   👤     │
│  Home    │Categories│  Cart    │Messages  │ Profile  │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

- Fixed at bottom, 56px height. Safe area padding on modern phones.
- Active tab highlighted with brand colour.
- Cart tab shows badge count.
- Messages tab shows unread count badge.
- Notification badges (red dot/circle) on Messages tab.

### 6.5 Breadcrumbs

- Present on all inner pages (not on homepage).
- Format: Home > Category > Subcategory > Current Page
- Last item is current page (not hyperlinked, bold).
- Separator: ">" or "/" — consistent across platform.
- Mobile: truncated at 2 levels with "..." if needed.

### 6.6 Search (Global)

- **Desktop:** Inline in header on all pages. Expandable input. On focus: dropdown overlay with suggestions.
- **Mobile:** Tap search icon → full-screen search overlay with large input, suggestions, recent searches.
- **Auto-Suggest:** Debounced (300ms). Shows: product results (image + name + price), category suggestions, "View all results for [query]" at bottom.
- **Search Results Page:** /search?q=[query] — uses the PLP template with search-specific empty state.

---

## 7. Interaction Design

### 7.1 Button States

| State | Visual | Behaviour |
|---|---|---|
| **Default** | Solid fill, brand colour | Ready for interaction |
| **Hover** | Slightly darker fill, cursor pointer | 150ms transition |
| **Active/Press** | Darker fill + slight scale (0.98) | 100ms transition |
| **Loading** | Spinner replaces text, button disabled | Indeterminate spinner animation |
| **Disabled** | 50% opacity, no pointer events | Greyed out, cursor not-allowed |
| **Focus** | Visible ring (2px brand + 2px offset) | Keyboard navigation visible |

### 7.2 Form Feedback

- **Inline Validation:** On blur, field validates and shows icon (green check / red X) + hint text below field. Red border for error, green border for success.
- **Success Messages:** Green toast at top-right (desktop) or top-centre (mobile). Auto-dismiss after 4 seconds. Manual dismiss via X button.
- **Error Messages:** Red toast same position. Persistent until dismissed.
- **Server Validation:** Error summary banner at top of form. Field-level errors highlighted. Focus moves to first error field.

### 7.3 Transitions & Animations (Framer Motion)

- **Page Transitions:** Fade + slight slide-up (300ms, ease-out). Reduced motion: fade only (no slide).
- **Modal/Sheet:** Slide-up from bottom (mobile) / fade + scale (desktop). Overlay fades in (200ms).
- **Dropdown/Menu:** Scale from top with opacity (150ms, spring).
- **Toast:** Slide in from right (desktop) / slide down from top (mobile). Stack from top.
- **Card Hover:** Scale 1.02 + shadow elevation (200ms).
- **Accordion:** Height transition (300ms, ease-in-out).
- **Skeleton:** Shimmer animation (moving gradient, 1.5s loop).

### 7.4 Micro-Interactions

- **Wishlist Heart:** Scale bounce on toggle (scale 1 → 1.3 → 1). Fill colour change.
- **Add to Cart:** Button briefly shows checkmark before returning to text. Cart icon badge increments with bounce.
- **Remove Item:** Item slides right + fades out. Undo toast slides in from bottom.
- **Star Rating:** Stars fill on hover with stagger animation. Click sets with a brief pulse.
- **Like/Helpful Button:** Icon fills with a subtle scale pop.
- **Copy Button:** Brief "Copied!" tooltip appears, then fades.

### 7.5 Loading States

| Component | Loading Treatment |
|---|---|
| Page content | Skeleton screen (blocks matching layout shape) |
| Product grid | Skeleton cards (animated grey rectangles) |
| Product detail | Skeleton layout (image rect + text lines + sidebar rect) |
| Table rows | Skeleton rows (3-5 rows with animated bars) |
| Buttons | Spinner replaces text |
| Images | Placeholder with lazy-load blur-up |
| Charts | Skeleton chart outline + shimmer |

### 7.6 Optimistic UI

Actions that update immediately without waiting for server confirmation:
- **Add to Cart:** Icon badge increments instantly. Toast shows success. Server failure → toast changes to error, badge decrements.
- **Wishlist Toggle:** Heart fills immediately. Server failure → reverts with error toast.
- **Delete Item:** Item removes instantly with undo option. Server failure → item reappears with error message.
- **Status Update:** Badge changes immediately. Server failure → reverts with error toast.

### 7.7 Drag and Drop

| Use Case | Implementation |
|---|---|
| Product image reorder | Drag handle on each image thumbnail. Drop zone highlights on drag over. Reorder animation. |
| File upload | Drag file over zone → blue highlight border + "Drop to upload". Progress bar during upload. |
| Dashboard widgets (future) | Drag to rearrange dashboard card positions. |

---

## 8. Mobile Design

### 8.1 Bottom Navigation Bar
- Fixed at bottom of screen. 56px height. 5 tabs: Home, Categories, Cart, Messages, Profile.
- Active tab has brand accent colour icon/text. Inactive tabs are grey.
- Cart tab displays item count badge. Messages tab displays unread count badge.
- Safe area inset padding on iOS-style devices (home indicator area).

### 8.2 Layout Adaptations

| Component | Desktop | Mobile |
|---|---|---|
| Product grid | 3-4 columns | 1-2 columns |
| Product detail | Two columns (gallery + info sidebar) | Single column, sticky buy bar |
| Cart | Two columns (items + summary sidebar) | Single column, summary at bottom |
| Checkout | Multi-step with sidebar summary | Single column, no sidebar |
| Tables | Standard data tables | Card list layout |
| Filters | Left sidebar, always visible | Bottom sheet drawer |
| Dashboard | Sidebar navigation | Bottom tab bar |
| Breadcrumbs | Full path | Truncated (2 levels + "...") |

### 8.3 Touch Targets
- Minimum touch target: 44×44px (following Apple HIG and Material Design guidelines).
- Adequate spacing between tappable elements (minimum 8px gap).
- Buttons, links, icons, and form controls all meet or exceed 44×44px.
- Quantity stepper +/- buttons: large enough for thumb tap.

### 8.4 Swipe Gestures

| Gesture | Action | Visual Feedback |
|---|---|---|
| Swipe left on cart item | Reveal "Remove" button (red) | Item shifts left, button appears |
| Swipe down on filter drawer | Close drawer | Drawer follows finger, snaps close |
| Swipe on product gallery | Navigate between images | Image follows finger with snap |
| Swipe on review/FAQ accordion | Expand/collapse | Content follows finger height |
| Swipe to go back (edge swipe) | Navigate to previous page | Page follows finger, snaps back or forward |

### 8.5 Simplified Data Display (Mobile)
- Tables become card lists:
  - Order history: each order as a card with key info (order #, date, amount, status badge, icon).
  - Product list: same as grid cards.
  - Messages: conversation preview cards.
- No horizontal scroll on data tables. All data is reflowed vertically.

### 8.6 Sticky Add-to-Cart Bar
- Appears on product detail page when user scrolls past the Buy section.
- Fixed at bottom of viewport (above bottom nav, or replacing it during checkout flow).
- Content: Price (left) + Quantity stepper + "Add to Cart" button (right).
- Slides up from bottom with a smooth transition.

### 8.7 Filter Drawer (Bottom Sheet)
- Triggered by "Filter" button in top bar on PLP.
- Slides up from bottom, covers ~80-90% of viewport height.
- Drag handle at top (horizontal bar).
- Content: all filter groups in scrollable area.
- Fixed bottom: "Apply Filters" button (primary) + "Clear All" link.
- Overlay behind (semi-transparent black), tap to close.

---

## 9. Tables & Data Display

### 9.1 Data Table Component

**Desktop (Standard Table):**
```
┌─────────┬──────────┬───────────┬────────┬──────────┬──────────┐
│ Order # │  Date    │  Product  │ Amount │  Status  │  Action  │
├─────────┼──────────┼───────────┼────────┼──────────┼──────────┤
│ ↑ sort  │ ↓ sort   │   sort    │  sort  │   sort   │          │
├─────────┼──────────┼───────────┼────────┼──────────┼──────────┤
│ #1024   │ Jul 1    │ Brand Kit │ $49.99 │ ✅ Compl.│ [▼]      │
│ #1023   │ Jun 28   │ Icon Set  │ $19.99 │ ⏳ Proc. │ [▼]      │
│ ...     │ ...      │ ...       │ ...    │ ...      │ ...      │
└─────────┴──────────┴───────────┴────────┴──────────┴──────────┘
└─── 10 per page ──── < 1 2 3 4 ... 10 > ─────────────────────────┘
```

**Properties:**
- **Sortable Columns:** Click header to toggle ASC/DESC/None. Arrow icon indicates current sort direction.
- **Filterable:** Chips/dropdowns above table for filtering (Status: All, Completed, Pending, etc.).
- **Search:** Search input above table filters rows by keyword.
- **Row Selection:** Checkbox in first column for bulk actions.
- **Pagination:** Bottom. Page numbers, prev/next. "Show per page" selector (10, 25, 50, 100).
- **Row Actions:** Three-dot menu (⋮) at end of row. Dropdown: View, Edit, Delete (with confirmation), other context-specific actions.

**Mobile (Card List):**
```
┌────────────────────────────────────────┐
│  #TSBL-1024               ✅ Completed │
│  Brand Kit Pro                        │
│  Jul 1, 2026              $49.99      │
│                             [View ▼]   │
├────────────────────────────────────────┤
│  #TSBL-1023               ⏳ Processing│
│  Icon Set Vol.3                       │
│  Jun 28, 2026             $19.99      │
│                             [View ▼]   │
└────────────────────────────────────────┘
```

- Each row becomes a card. Key info on left, status on right.
- Action is always visible (no hover-reveal).
- Pagination or infinite scroll at bottom.

### 9.2 Status Badges

| Status | Colour | Icon | Example |
|---|---|---|---|
| Active / Completed | Green (#22C55E) | ✓ | ✅ Completed |
| Pending / Processing | Amber (#F59E0B) | ◷ | ⏳ Processing |
| Cancelled / Rejected | Red (#EF4444) | ✕ | ❌ Cancelled |
| Refunded | Blue (#3B82F6) | ↩ | ↩ Refunded |
| Draft | Grey (#9CA3AF) | ✎ | ✎ Draft |
| Under Review | Purple (#8B5CF6) | ◉ | ◉ Review |
| Published | Green (#22C55E) | ↑ | ↑ Published |

### 9.3 Empty States

| Context | Illustration | Heading | Subtext | CTA |
|---|---|---|---|---|
| Cart | Empty cart graphic | Your cart is empty | Looks like you haven't added anything yet | Browse Products |
| Orders | Empty box graphic | No orders yet | When you make a purchase, it will appear here | Start Shopping |
| Downloads | Empty download graphic | No downloads yet | Your purchased files will appear here | Browse Products |
| Products (seller) | Empty storefront | No products listed | Start by adding your first product | Add Product |
| Search Results | Empty search graphic | No results found | Try adjusting your search or filters | Clear Filters |
| Messages | Empty chat graphic | No messages | When you message a seller, it will appear here | Browse Products |
| Notifications | Empty bell graphic | No notifications | You're all caught up! | — |

### 9.4 Loading Skeletons

- **Table:** 5 rows, each with animated grey bars matching column proportions.
- **Product Grid:** 8 cards, each with image placeholder + 3 text line placeholders. Shimmer animation.
- **Product Detail:** Full layout skeleton: large rectangle (image) + text lines + sidebar rectangle.
- **Dashboard:** Metric cards (4 grey rectangles) + chart skeleton (area shape).

---

## 10. Form Design

### 10.1 General Form Principles

- **Single Column Layout:** All user-facing forms are single column for readability. Multi-column only in admin panels for space efficiency.
- **Labels Above Inputs:** Labels are placed above input fields, never as placeholder-only. Placeholders can provide additional hints.
- **Required Fields:** Marked with red asterisk (*). Optional fields labelled "(optional)" in the label.
- **Inline Validation:** Validates on blur. Success: green border + checkmark icon + green hint text. Error: red border + X icon + red error message.
- **Submit Button:** Full-width on mobile, aligned left on desktop. Shows loading spinner on submit. Disabled until form is valid (optional — can allow submit with server validation).
- **Success:** Toast notification + redirect or clear form. Inline success message for non-redirecting forms.
- **Server Error:** Error summary banner at top of form with list of field-level errors. Fields highlighted. Focus moves to first error field.

### 10.2 Form Input Types

| Input Type | Component | Details |
|---|---|---|
| Text | `<input type="text">` | Standard single-line text |
| Email | `<input type="email">` | Email validation, keyboard type on mobile |
| Password | `<input type="password">` | Show/hide toggle (eye icon) |
| Number | `<input type="number">` | With stepper buttons for quantity |
| Phone | `<input type="tel">` | Country code dropdown + number |
| Textarea | `<textarea>` | Resizable vertical. Character count optional |
| Select | Custom styled `<select>` | Native dropdown on mobile |
| Multi-select | Chips input | Type to search, add chips, remove chips |
| Checkbox | Custom styled checkbox | Large touch target (44px) |
| Radio | Custom styled radio | Group with clear labels |
| Toggle | Switch component | On/off with smooth transition |
| Date | Date picker | Calendar popup. Past dates disabled if needed |
| File Upload | Drag-drop zone | Click or drag. Preview, progress, remove |
| Rich Text | Editor toolbar | Bold, italic, lists, links, headings |

### 10.3 Form Layout Examples

**Login Form:**
```
┌──────────────────────────────┐
│         [Logo]               │
│                              │
│  Welcome Back                │
│  Sign in to your account     │
│                              │
│  Email *                     │
│  ┌────────────────────────┐  │
│  │ user@example.com       │  │
│  └────────────────────────┘  │
│                              │
│  Password *                  │
│  ┌────────────────────────┐  │
│  │ •••••••••              │  │
│  └────────────────────────┘  │
│                              │
│  ☐ Remember me   Forgot?    │
│                              │
│  ┌────────────────────────┐  │
│  │      Sign In           │  │
│  └────────────────────────┘  │
│                              │
│  Don't have an account?     │
│  Create one                  │
└──────────────────────────────┘
```

**Registration Form:**
```
┌──────────────────────────────┐
│         [Logo]               │
│                              │
│  Create Account              │
│                              │
│  I want to...                │
│  ┌──────────┐ ┌──────────┐  │
│  │ 🛍️ Buy  │ │ 🏪 Sell  │  │
│  └──────────┘ └──────────┘  │
│                              │
│  Full Name *                 │
│  ┌────────────────────────┐  │
│  │ John Doe               │  │
│  └────────────────────────┘  │
│                              │
│  Email *                     │
│  ┌────────────────────────┐  │
│  │ john@example.com       │  │
│  └────────────────────────┘  │
│                              │
│  Password *                  │
│  ┌────────────────────────┐  │
│  │ •••••••••              │  │
│  └────────────────────────┘  │
│  ████████░░░░ Weak           │
│                              │
│  Confirm Password *          │
│  ┌────────────────────────┐  │
│  │ •••••••••              │  │
│  └────────────────────────┘  │
│                              │
│  ☐ I agree to Terms & PP    │
│                              │
│  ┌────────────────────────┐  │
│  │   Create Account       │  │
│  └────────────────────────┘  │
│                              │
│  Or continue with            │
│  [Google] [Facebook] [GitHub]│
│                              │
│  Already have an account?    │
│  Sign In                     │
└──────────────────────────────┘
```

### 10.4 File Upload Zone

- **Drag-Drop Area:** Dashed border rectangle (min 200×150px). Upload icon (cloud arrow up). Text: "Drag files here or click to upload". Supported formats listed below in small text.
- **Hover/Over:** Border becomes solid brand colour. Background lightly shaded. Text changes to "Drop to upload".
- **Uploading:** Progress bar with percentage + file name. Cancel button (X).
- **Success:** Green check + file name + file size. Remove button (X).
- **Error:** Red X + file name + error message. Retry button.
- **Multiple Files:** Thumbnail grid of uploaded files. Drag to reorder. Click to preview. X to remove.

### 10.5 Form Submissions

- **Loading State:** Submit button shows spinner + "Saving..." text (or "Adding..." / "Creating..."). Button disabled.
- **Success:** Toast notification (green, top-right). Form either clears (for new entries) or shows success message (for edits). Redirect if applicable.
- **Error (Client):** Field-level validation messages. First error field focused.
- **Error (Server):** Error summary banner at top. Field-level errors highlighted where applicable. Non-field errors listed in summary.

---

## 11. Empty States & Error States

### 11.1 Empty States

| Screen | Illustration | Heading | Subtext | Primary Action | Secondary Action |
|---|---|---|---|---|---|
| Cart | Empty basket | Your cart is empty | Looks like you haven't added anything yet | Browse Products | — |
| Orders (buyer) | Empty box | No orders yet | When you make a purchase, your orders will appear here | Start Shopping | — |
| Downloads | Empty folder | No downloads yet | Your purchased files will appear here | Browse Products | — |
| Wishlist | Empty heart | Your wishlist is empty | Save your favourite items to buy later | Browse Products | — |
| Reviews (buyer) | Empty speech bubble | No reviews yet | Reviews you write will appear here | Browse Products | — |
| Products (seller) | Empty storefront | No products listed | Start selling by adding your first product | Add Product | Learn How |
| Orders (seller) | Empty clipboard | No orders yet | When customers purchase your products, orders will appear here | Share Your Store | — |
| Messages | Empty chat | No messages | Messages from buyers and support will appear here | Browse Products | — |
| Notifications | Empty bell | No notifications | You're all caught up! | — | — |
| Search results | Empty magnifier | No results found | Try adjusting your search or filters | Clear Filters | Browse All |
| Affiliate dashboard | Empty link | No referrals yet | Generate your affiliate links to start earning | Generate Links | Learn More |

### 11.2 Error States

| Error | Visual | Behaviour |
|---|---|---|
| **404 Not Found** | Illustration (broken path/compass) + "Page not found" + "The page you're looking for doesn't exist" | Search bar + "Go Home" button. Sitemap links below. |
| **500 Server Error** | Illustration (server/gears) + "Something went wrong" + "Our team has been notified" | "Try Again" button + "Go Home" link. Auto-retry after 10s (optional). |
| **403 Forbidden** | Illustration (locked door) + "Access denied" + "You don't have permission to view this page" | "Go Home" button. Contact support link. |
| **Network Error** | Offline indicator bar at top (red/yellow) + "You are offline" | Toast: "Network connection lost". Auto-reconnect detection. Retry buttons on all actions. Offline banner dismisses when connection restored. |
| **Payment Failed** | Error icon + "Payment failed" + reason message | "Try Again" button + "Choose Different Payment Method" + "Contact Support" link. |
| **Upload Failed** | Error icon on file + "Upload failed" + reason | "Retry" button per file. "Cancel" button. |
| **Rate Limited** | "Too many requests" + "Please wait a moment before trying again" | Countdown timer. Retry button after timer. |
| **Session Expired** | Modal overlay + "Your session has expired" | "Sign In Again" button. Redirects to login with return URL. |

### 11.3 Empty State Design Guidelines

- **Illustration:** 160×160px on desktop, 120×120px on mobile. Simple line-art style with brand colours. Consistent illustration family across all empty states.
- **Typography:** Heading (18px, bold, dark grey), Subtext (14px, regular, medium grey).
- **CTA:** Primary button style. Links to relevant action.
- **Layout:** Centred in the content area. Padding: 80px top/bottom.

---

## 12. Accessibility & UX Best Practices

### 12.1 Skip Navigation

- **Visible on Focus:** "Skip to content" link is the first focusable element on every page. Hidden by default, appears on Tab press.
- **Behaviour:** Focus skip link → press Enter → focus moves to `<main>` content area. Skip link then hides again.

### 12.2 Focus Indicators

- **Visible Focus Ring:** 2px solid brand colour + 2px offset. Applied to all interactive elements (links, buttons, inputs, selects, toggles).
- **Never Remove `:focus`:** Outlines are never set to `outline: none` without providing a visible focus alternative.
- **Focus Order:** Logical DOM order follows visual order. Tab order is predictable.

### 12.3 Keyboard Navigation

| Key | Behaviour |
|---|---|
| **Tab** | Move focus to next interactive element. Visible focus indicator. |
| **Shift+Tab** | Move focus to previous interactive element. |
| **Enter / Space** | Activate focused button, link, or toggle. |
| **Escape** | Close modal, dropdown, menu, or overlay. Return focus to trigger element. |
| **Arrow Keys** | Navigate within a component (dropdown options, tab list, slider, accordion). |
| **Arrow Left/Right** | Navigate product gallery images. |
| **Number Keys** | Quick navigation in paginated lists (1, 2, 3...). |
| **Ctrl+K (Cmd+K)** | Focus the search bar (global shortcut). |

### 12.4 ARIA Attributes

- **Icons:** All decorative icons have `aria-hidden="true"`. Informational icons have `aria-label` or hidden descriptive text.
- **Buttons:** Icon-only buttons have `aria-label="Describe action"`.
- **Navigation Menus:** `<nav>` with `aria-label="Main navigation"`. Dropdowns use `aria-expanded` and `aria-controls`.
- **Modals:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to heading, `aria-describedby` for description. Focus trapped inside modal. Escape closes.
- **Alerts/Toasts:** `role="alert"` or `aria-live="polite"` for dynamic content.
- **Tabs:** `role="tablist"`, `role="tab"`, `role="tabpanel"` with `aria-selected`, `aria-controls`, `aria-labelledby`.
- **Accordion:** `role="button"` on headers with `aria-expanded` and `aria-controls`. Content panel has `role="region"` and `aria-labelledby`.
- **Progress:** `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`.
- **Status Badges:** `aria-label="Status: Completed"` with colour-agnostic text.
- **Error Messages:** `role="alert"` on error summary. `aria-describedby` links input to its error message. `aria-invalid="true"` on invalid inputs.

### 12.5 Colour & Visual Cues

- **Colour is never the sole indicator** of state, status, or action. Every colour-coded element also has an icon, text label, or pattern.
  - Example: Status badges have colour + icon + text label.
  - Example: required fields have asterisk + label + visual indicator.
  - Example: success/error states have colour + icon + message text.
- **Links** are identified by colour + underline (on hover) or by colour + bold weight.

### 12.6 Touch & Interaction Targets

- **Minimum touch target:** 44×44 CSS pixels (WCAG 2.5.8).
- **Spacing:** Minimum 8px gap between tappable elements.
- **Hover states** — must also work on touch devices. On mobile, hover acts as first tap, active as second tap (or hover is simply not used on mobile).

### 12.7 Typography

| Element | Minimum Size | Weight | Line Height |
|---|---|---|---|
| Body text | 16px | Regular (400) | 1.5 |
| Small text / captions | 14px | Regular (400) | 1.4 |
| Input labels | 14px | Medium (500) | 1.4 |
| Button text | 16px | Semi-bold (600) | 1.2 |
| H1 (page titles) | 32px | Bold (700) | 1.2 |
| H2 (section headings) | 24px | Bold (700) | 1.3 |
| H3 (card headings) | 18px | Semi-bold (600) | 1.3 |
| H4 | 16px | Semi-bold (600) | 1.4 |

- **Body text minimum:** 16px (WCAG recommendation for readability).
- **Contrast ratio:** Minimum 4.5:1 for normal text, 3:1 for large text (18px+ bold or 24px+ regular).
- **Font stack:** System font stack or platform-consistent font (Inter, Nunito Sans, or similar).

### 12.8 Reduced Motion

- **`prefers-reduced-motion`** media query respected globally.
- Animations either disabled entirely or replaced with simple fade transitions.
- No parallax, no auto-playing carousels, no continuous animations.
- Page transitions: fade only (no slide).
- Skeleton shimmer replaced with static grey blocks.

### 12.9 Additional Best Practices

- **Zoom:** Pages are fully functional at 200% zoom (WCAG 1.4.10, 1.4.4).
- **Screen Readers:** All content is announced in logical order. Dynamic content changes are announced via `aria-live` regions.
- **Headings:** Hierarchical heading structure (h1 → h2 → h3). One h1 per page. No skipped levels.
- **Forms:** All inputs have associated `<label>` elements. Error messages are announced by screen readers. Autocomplete attributes are used (`autocomplete="email"`, `autocomplete="name"`, etc.).
- **Images:** All meaningful images have `alt` text. Decorative images have `alt=""`.
- **Language:** `lang` attribute set on `<html>` element.
- **Print Styles:** Product pages, order confirmations, and receipts have print-friendly styles.

---

*End of UI/UX Blueprint Document — TRUE STAR BD LIMITED*
