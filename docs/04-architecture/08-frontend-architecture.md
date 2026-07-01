# Frontend Architecture — TRUE STAR BD LIMITED

> **Version:** 1.0.0  
> **Last Updated:** 2026-07-02  
> **Status:** Final  

---

## Table of Contents

1. [Frontend Architecture Philosophy](#1-frontend-architecture-philosophy)
2. [Folder Structure](#2-folder-structure)
3. [Route Architecture](#3-route-architecture)
4. [Layout Architecture](#4-layout-architecture)
5. [Component Architecture](#5-component-architecture)
6. [Design System](#6-design-system)
7. [Theme Architecture](#7-theme-architecture)
8. [State Management](#8-state-management)
9. [API Integration Strategy](#9-api-integration-strategy)
10. [Authentication Flow](#10-authentication-flow)
11. [Form Architecture](#11-form-architecture)
12. [Performance Strategy](#12-performance-strategy)
13. [SEO Strategy](#13-seo-strategy)
14. [Accessibility Strategy](#14-accessibility-strategy)
15. [Responsive Design Strategy](#15-responsive-design-strategy)
16. [Internationalization](#16-internationalization)
17. [Dashboard Architecture](#17-dashboard-architecture)
18. [Error Handling](#18-error-handling)
19. [Notification Strategy](#19-notification-strategy)
20. [Frontend Security](#20-frontend-security)
21. [Testing Strategy](#21-testing-strategy)
22. [Coding Standards](#22-coding-standards)
23. [Development Workflow](#23-development-workflow)
24. [Deployment Strategy](#24-deployment-strategy)
25. [Final Frontend Blueprint](#25-final-frontend-blueprint)

---

## 1. Frontend Architecture Philosophy

**Architecture Type:** Feature-based architecture with Component-driven design and Atomic Design principles.

**Feature-based Architecture:** Each domain (auth, marketplace, seller, admin, etc.) is a self-contained feature folder with its own components, hooks, services, and types. Features are independent, reusable, and testable. Clear boundaries prevent cross-feature coupling.

**Component-driven:** UI built from small, reusable components composed into larger ones. Each component has a single responsibility. Components are stateless where possible, with state lifted to hooks/stores.

**Atomic Design:** Components categorized as Atoms (Button, Input), Molecules (SearchBar, FormField), Organisms (ProductCard, OrderTable), Templates (DashboardLayout, ProductDetailLayout), Pages (HomePage, ProductListingPage).

**Domain Separation:** Buyer, Seller, Admin, Affiliate, Support are separate domains with their own layouts, routes, and feature sets. Shared code lives in common/shared folders.

**Scalability Strategy:**
- Code-splitting by route (Next.js App Router auto-splits)
- Lazy loading for heavy components (charts, editors)
- Virtual scrolling for large lists
- Incremental Static Regeneration for product/category pages
- CDN for static assets and images

**Advantages:**
- Teams can work on features independently with minimal conflicts
- Clear ownership: each feature has defined boundaries
- Reusability: shared components reduce duplication
- Testability: features are isolated and mockable
- Scalability: new features added without affecting existing ones

**Trade-offs:**
- Requires discipline to maintain boundaries
- Some duplication unavoidable between domains
- Initial setup overhead for feature scaffolding

---

## 2. Folder Structure

```
src/
├── app/                          # Next.js App Router pages
│   ├── (public)/                 # Public route group (no auth required)
│   │   ├── page.tsx              # Home/Landing page
│   │   ├── products/             # Product listing and detail
│   │   ├── categories/           # Category browsing
│   │   ├── search/               # Search results
│   │   ├── about/                # About, contact, legal pages
│   │   ├── faq/                  # FAQ
│   │   └── blog/                 # Blog
│   ├── (auth)/                   # Auth route group
│   │   ├── login/
│   │   ├── register/
│   │   ├── forgot-password/
│   │   └── reset-password/
│   ├── (dashboard)/              # Dashboard route group
│   │   ├── buyer/
│   │   ├── seller/
│   │   ├── admin/
│   │   ├── affiliate/
│   │   └── support/
│   ├── error.tsx                 # Global error boundary
│   ├── not-found.tsx             # 404 page
│   ├── loading.tsx               # Global loading state
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Global styles
│
├── components/                   # Shared UI components (Atomic Design)
│   ├── ui/                       # Atoms — Base primitives
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   ├── Dropdown.tsx
│   │   ├── Tabs.tsx
│   │   ├── Breadcrumb.tsx
│   │   ├── Pagination.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Spinner.tsx
│   │   ├── Toast.tsx
│   │   ├── Alert.tsx
│   │   └── index.ts              # Barrel export
│   ├── forms/                    # Form components
│   │   ├── FormField.tsx
│   │   ├── FormSelect.tsx
│   │   ├── FormTextarea.tsx
│   │   ├── FormCheckbox.tsx
│   │   ├── FormRadio.tsx
│   │   ├── FormDatePicker.tsx
│   │   ├── FormFileUpload.tsx
│   │   └── FormSubmitButton.tsx
│   ├── layout/                   # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Navbar.tsx
│   │   ├── MobileNav.tsx
│   │   └── BreadcrumbNav.tsx
│   ├── shared/                   # Shared business components
│   │   ├── ProductCard.tsx
│   │   ├── SellerCard.tsx
│   │   ├── OrderCard.tsx
│   │   ├── ReviewCard.tsx
│   │   ├── RatingStars.tsx
│   │   ├── PriceDisplay.tsx
│   │   ├── CurrencySelector.tsx
│   │   ├── LanguageSelector.tsx
│   │   ├── ThemeToggle.tsx
│   │   ├── SearchBar.tsx
│   │   ├── CategoryNav.tsx
│   │   ├── EmptyState.tsx
│   │   ├── ErrorState.tsx
│   │   └── LoadingState.tsx
│   └── charts/                   # Chart components
│       ├── RevenueChart.tsx
│       ├── SalesChart.tsx
│       ├── OrderChart.tsx
│       └── UserChart.tsx
│
├── features/                     # Feature-specific modules
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   └── types/
│   ├── marketplace/
│   │   └── [products, search, categories sub-structure]
│   ├── cart/
│   │   └── [...]
│   ├── checkout/
│   │   └── [...]
│   ├── orders/
│   │   └── [...]
│   ├── wallet/
│   │   └── [...]
│   ├── reviews/
│   │   └── [...]
│   ├── messages/
│   │   └── [...]
│   ├── notifications/
│   │   └── [...]
│   └── affiliate/
│       └── [...]
│
├── hooks/                        # Global shared hooks
│   ├── useAuth.ts
│   ├── useMediaQuery.ts
│   ├── useDebounce.ts
│   ├── useIntersectionObserver.ts
│   ├── useLocalStorage.ts
│   ├── usePagination.ts
│   ├── useInfiniteScroll.ts
│   ├── useCountdown.ts
│   └── useClipboard.ts
│
├── services/                     # API service layer
│   ├── api.ts                    # Axios instance, interceptors
│   ├── auth.service.ts
│   ├── product.service.ts
│   ├── order.service.ts
│   ├── wallet.service.ts
│   ├── review.service.ts
│   ├── chat.service.ts
│   ├── notification.service.ts
│   └── admin.service.ts
│
├── stores/                       # Zustand stores
│   ├── authStore.ts
│   ├── cartStore.ts
│   ├── uiStore.ts
│   ├── themeStore.ts
│   └── notificationStore.ts
│
├── lib/                          # Third-party library configs
│   ├── query-client.ts           # TanStack Query config
│   ├── i18n.ts                   # next-intl config
│   ├── auth.ts                   # Auth utilities
│   ├── api-utils.ts              # API helper functions
│   └── formatters.ts             # Date, currency, number formatters
│
├── utils/                        # General utility functions
│   ├── cn.ts                     # clsx + tailwind-merge
│   ├── validators.ts             # Zod schemas
│   ├── constants.ts
│   ├── helpers.ts
│   └── security.ts               # XSS sanitization, CSP
│
├── providers/                    # React context providers
│   ├── AuthProvider.tsx
│   ├── ThemeProvider.tsx
│   ├── QueryProvider.tsx
│   ├── LocaleProvider.tsx
│   └── ToastProvider.tsx
│
├── middleware.ts                 # Next.js middleware (auth, i18n)
│
├── types/                        # Global TypeScript types
│   ├── api.ts
│   ├── auth.ts
│   ├── product.ts
│   ├── order.ts
│   ├── user.ts
│   ├── common.ts
│   └── index.ts
│
├── config/                       # Application configuration
│   ├── routes.ts                 # Route definitions
│   ├── site.ts                   # Site metadata
│   ├── constants.ts
│   └── seo.ts
│
├── styles/                       # Global styles
│   └── globals.css
│
└── messages/                     # i18n translation files
    ├── en.json
    ├── bn.json
    └── [...other languages]
```

### src/app/
Next.js App Router pages organized by route groups. `(public)` contains all non-authenticated pages: landing, products, categories, search, blog, and static pages. `(auth)` groups login, register, and password reset flows with a shared centered layout. `(dashboard)` contains all protected dashboard routes for buyer, seller, admin, affiliate, and support roles. Each subfolder under these groups corresponds to a URL path segment. The global `error.tsx`, `not-found.tsx`, `loading.tsx`, root `layout.tsx`, and `globals.css` live at the top level. Route groups enable different layouts per context without affecting URL structure.

### src/components/
Shared UI components organized by the Atomic Design hierarchy. `ui/` contains base primitives (Atoms) — Button, Input, Badge, Card, Modal, Table, Dropdown, Tabs, Breadcrumb, Pagination, Skeleton, Spinner, Toast, Alert — each with variants, states, and consistent styling. `forms/` provides form-specific wrappers (FormField, FormSelect, FormTextarea, FormCheckbox, FormRadio, FormDatePicker, FormFileUpload, FormSubmitButton) that integrate with React Hook Form. `layout/` houses structural components (Header, Footer, Sidebar, Navbar, MobileNav, BreadcrumbNav) used across pages. `shared/` contains business-oriented Molecules and Organisms (ProductCard, SellerCard, OrderCard, ReviewCard, RatingStars, PriceDisplay, SearchBar, CategoryNav, EmptyState, ErrorState, LoadingState). `charts/` provides Recharts-based visualization components for dashboards.

### src/features/
Self-contained feature modules. Each feature (auth, marketplace, cart, checkout, orders, wallet, reviews, messages, notifications, affiliate) has its own `components/`, `hooks/`, `services/`, `stores/`, and `types/` subdirectories. Features encapsulate all logic and UI specific to their domain. The marketplace feature includes nested sub-structures for products, search, and categories. Cross-feature communication happens through shared hooks, stores, or service layers. This isolation allows parallel development and independent testing.

### src/hooks/
Global shared hooks used across multiple features. `useAuth` wraps authentication state and actions. `useMediaQuery` provides responsive breakpoint detection. `useDebounce` delays rapid value changes (search input). `useIntersectionObserver` triggers callbacks on element visibility (lazy loading, infinite scroll). `useLocalStorage` persists state with SSR safety. `usePagination` and `useInfiniteScroll` handle list navigation. `useCountdown` manages timer state. `useClipboard` abstracts copy-to-clipboard with fallback.

### src/services/
API service layer with one file per domain. `api.ts` initializes the Axios instance with base URL, request/response interceptors (token attachment, error handling, token refresh). Each service file exports typed async functions for its domain (auth, product, order, wallet, review, chat, notification, admin). Functions accept typed parameters and return typed responses. This layer is the single source of truth for all API communication.

### src/stores/
Zustand stores for global client-side state. `authStore` holds user object, access token, and authentication actions. `cartStore` manages cart items, quantities, and totals. `uiStore` controls sidebar state, modal visibility, mobile menu, and toast queue. `themeStore` persists theme preference. `notificationStore` tracks unread notifications. Stores use Zustand's persist middleware for localStorage persistence where appropriate (theme, cart). Auth state is intentionally kept out of localStorage for security.

### src/lib/
Third-party library configuration and initialization. `query-client.ts` creates and configures the TanStack Query client (stale times, retry policy, default options). `i18n.ts` initializes next-intl with available locales, default locale, and message loading. `auth.ts` provides utility functions for token management and role checking. `api-utils.ts` contains helpers for constructing query strings, error mapping, and response unwrapping. `formatters.ts` exposes locale-aware formatting functions for currency, dates, numbers, and relative time.

### src/utils/
Pure utility functions with no side effects. `cn.ts` combines clsx and tailwind-merge for class name merging. `validators.ts` defines reusable Zod schemas (email, password, URL, file validation). `constants.ts` holds application-wide constants (pagination limits, file size limits, timeout values). `helpers.ts` contains general-purpose functions (slug generation, truncation, deep clone, array grouping). `security.ts` provides XSS sanitization (DOMPurify wrapper) and CSP nonce generation.

### src/providers/
React context providers that wrap the application. `AuthProvider` listens for auth state changes and provides user context. `ThemeProvider` applies the active theme class to the document and manages theme transitions. `QueryProvider` wraps the app with TanStack Query's QueryClientProvider and adds DevTools in development. `LocaleProvider` initializes next-intl and provides locale switching. `ToastProvider` manages a toast notification system with stacking and auto-dismiss.

### src/middleware.ts
Next.js Edge Middleware handling authentication checks and internationalization redirects. On every request, it checks for valid auth tokens (for protected routes), verifies role-based access (buyer, seller, admin, affiliate, support), and redirects unauthenticated users to the login page with a return URL. It also detects the user's preferred locale from cookies/headers and redirects to the appropriate language prefix.

### src/types/
Global TypeScript type definitions shared across the application. `api.ts` defines generic API response types (paginated response, error response, request params). `auth.ts` defines user, token, and permission types. `product.ts` defines product, category, and variant types. `order.ts` defines order, order item, and order status types. `user.ts` defines profile, address, and payment method types. `common.ts` defines shared types (address, pagination, file, review). `index.ts` re-exports all types for convenient imports.

### src/config/
Static application configuration. `routes.ts` defines all route paths as constants (prevents hardcoding, enables type-safe routing). `site.ts` holds site metadata (name, description, logo URL, social links). `constants.ts` defines environment-specific configuration (API URLs, feature flags, supported locales). `seo.ts` configures default SEO metadata and Open Graph defaults.

### src/styles/
Global CSS files. `globals.css` imports Tailwind directives (`@tailwind base`, `@tailwind components`, `@tailwind utilities`), defines CSS custom properties for theming, and includes any necessary global resets or utility classes. Tailwind's CLI processes this file to generate the final stylesheet.

### src/messages/
Internationalization translation files in JSON format. One file per supported locale (`en.json`, `bn.json`, `ar.json`, `hi.json`, `es.json`, `fr.json`). Each file contains nested key-value pairs organized by feature/page section. Messages are loaded lazily by next-intl based on the active locale.

---

## 3. Route Architecture

**Public Routes (no auth):**
- `/` — Home/Landing page
- `/products` — Product listing
- `/products/[slug]` — Product detail
- `/categories` — All categories
- `/categories/[slug]` — Category products
- `/search` — Search results
- `/about` — About us
- `/contact` — Contact us
- `/faq` — FAQ
- `/blog` — Blog listing
- `/blog/[slug]` — Blog article
- `/terms` — Terms of service
- `/privacy` — Privacy policy

**Auth Routes (no auth, redirect if logged in):**
- `/login` — Login page
- `/register` — Registration (buyer/seller selection)
- `/forgot-password` — Password reset request
- `/reset-password/[token]` — Password reset

**Buyer Routes (protected):**
- `/buyer/dashboard` — Buyer dashboard
- `/buyer/orders` — Order history
- `/buyer/orders/[id]` — Order detail
- `/buyer/purchases` — Digital purchases
- `/buyer/downloads` — Download history
- `/buyer/wallet` — Wallet and transactions
- `/buyer/wishlist` — Wishlist
- `/buyer/reviews` — My reviews
- `/buyer/messages` — Conversations
- `/buyer/messages/[id]` — Conversation detail
- `/buyer/profile` — Profile settings
- `/buyer/addresses` — Saved addresses
- `/buyer/payment-methods` — Payment methods
- `/buyer/settings` — Account settings

**Seller Routes (protected):**
- `/seller/dashboard` — Seller dashboard
- `/seller/products` — Product management
- `/seller/products/new` — Add product
- `/seller/products/[id]/edit` — Edit product
- `/seller/orders` — Order management
- `/seller/orders/[id]` — Order detail
- `/seller/earnings` — Earnings and payouts
- `/seller/withdraw` — Withdraw funds
- `/seller/analytics` — Sales analytics
- `/seller/reviews` — Review management
- `/seller/messages` — Conversations
- `/seller/profile` — Store profile
- `/seller/settings` — Store settings

**Admin Routes (protected):**
- `/admin/dashboard` — Admin dashboard
- `/admin/users` — User management
- `/admin/sellers` — Seller management
- `/admin/products` — Product moderation
- `/admin/orders` — All orders
- `/admin/payments` — Payment management
- `/admin/disputes` — Dispute resolution
- `/admin/categories` — Category management
- `/admin/coupons` — Coupon management
- `/admin/affiliates` — Affiliate management
- `/admin/reports` — Reports and analytics
- `/admin/settings` — System settings
- `/admin/cms` — Content management
- `/admin/audit-logs` — Audit logs

**Affiliate Routes (protected):**
- `/affiliate/dashboard` — Affiliate dashboard
- `/affiliate/links` — Affiliate links
- `/affiliate/earnings` — Earnings
- `/affiliate/withdraw` — Withdraw
- `/affiliate/referrals` — Referrals

**Support Routes (protected):**
- `/support/dashboard` — Support dashboard
- `/support/tickets` — Ticket management
- `/support/tickets/[id]` — Ticket detail
- `/support/disputes` — Dispute management

**Dynamic Routes:**
- `/products/[slug]` — Product detail by slug
- `/categories/[slug]` — Category by slug
- `/blog/[slug]` — Blog article by slug
- `/buyer/orders/[id]` — Order by ID
- `/seller/products/[id]/edit` — Product by ID
- `/admin/users/[id]` — User detail
- `/admin/products/[id]` — Product review

**Nested Routes:**
- `/buyer/settings/profile`, `/buyer/settings/security`
- `/seller/settings/store`, `/seller/settings/shipping`

**Route Groups (Next.js App Router):**
- `(public)` — shared public layout
- `(auth)` — centered auth layout
- `(dashboard)` — sidebar dashboard layout

**Error Routes:**
- `/404` — Not Found
- `/401` — Unauthorized (handled by middleware)
- `/403` — Forbidden
- `/500` — Server Error
- `/maintenance` — Maintenance mode

---

## 4. Layout Architecture

**Public Layout:** Header (logo, search, categories, nav, cart, auth buttons), main content area, Footer (links, social, newsletter, copyright). Used for all public pages. The header is sticky with a condensed variant on scroll. The footer is multi-column on desktop, stacked on mobile. Both header and footer support dark mode and are localized.

**Dashboard Layout:** Sidebar (navigation menu, user info, role-specific links), TopBar (search, notifications, user menu), Main content area. Shared across all dashboard routes. Sidebar is collapsible (icon-only mode) and transitions to a slide-in overlay on mobile. On the smallest screens, the sidebar becomes a bottom navigation bar.

**Admin Layout:** Dashboard layout enhanced with admin-specific sidebar (users, products, payments, disputes, settings, audit logs). Super admin has additional menu items (system config, all-logs). The admin top bar includes a site-wide search for users/orders/products and quick-action dropdowns.

**Seller Layout:** Dashboard layout with seller-specific sidebar (products, orders, earnings, analytics, reviews, messages, store settings). Includes a store status indicator (active/paused/suspended) and quick links to add products or view recent orders.

**Authentication Layout:** Centered card layout (logo, form, footer links). Minimal and distraction-free. The card has a max-width of 480px and is centered both horizontally and vertically. Used for login, register, and password reset pages. No header or footer navigation to maintain focus.

**Error Layout:** Minimal layout with error illustration, message, and action button (Go Home, Retry). The 404 page includes a search bar. The 500 page shows a request ID and a retry button. Forbidden (403) includes a contact support link.

**Maintenance Layout:** Full-screen maintenance mode with countdown timer, status message, and estimated return time. Only accessible to admins for preview (via a special cookie or query parameter). Auto-refreshes to check when maintenance ends.

---

## 5. Component Architecture

**Base Components (Atoms):** Button (variants: primary, secondary, outline, ghost, danger; sizes: sm, md, lg; loading state; icon support), Input (text, email, password, search, tel, url; with icon, error state, helper text), Badge (status dot variant, color variants, size variants), Card (with header/body/footer slots, clickable variant), Modal (size variants: sm/md/lg/xl/full; close on overlay/ESC; focus trap), Table (sortable headers, striped rows, responsive scroll), Dropdown (position variants, with dividers, icons, disabled items), Tabs (underline and pill variants, scrollable), Breadcrumb (chevron/slash/arrow separators, max items with truncation), Pagination (page numbers, prev/next, ellipsis, page size selector), Skeleton (rectangle, circle, text variants), Spinner (size variants, with label), Toast (success, error, warning, info; auto-dismiss with configurable duration), Alert (inline, banner, toast variant; dismissible; with icon), Avatar (image fallback to initials, size variants), Tooltip (position variants, delay), ProgressBar (determinate, indeterminate, with label), Divider (horizontal, vertical, with label), Tag/Chip (removable, color variants).

**Shared Components (Molecules):** SearchBar (input + search button + debounced suggestions dropdown with recent searches), ProductCard (image gallery preview, title, price with discount, rating, seller name, add-to-cart button, wishlist toggle), SellerCard (logo, name, rating, product count, join date, verified badge), OrderCard (order number, status badge, item count, total, date, actions dropdown), ReviewCard (user avatar, name, rating, review text, date, helpful button with count), RatingStars (interactive and display-only modes, half-star support, fractional display), PriceDisplay (original price, discounted price, discount percentage, currency-aware), CurrencySelector (currency code, symbol, flag icon, dropdown), LanguageSelector (language name in native script, flag icon, dropdown), ThemeToggle (sun/moon icon, animated transition), CategoryNav (multi-level hierarchical tree with expand/collapse, active state), EmptyState (illustration, title, description, action button), ErrorState (error icon, message, retry button, optional details), LoadingState (skeleton or spinner, configurable rows/columns), NotificationBell (bell icon, unread count badge, dropdown with recent notifications, mark-all-read action).

**Business Components (Organisms):** ProductForm (full product creation/editing: title, description, media upload, pricing, inventory, variants, shipping, SEO fields), CheckoutForm (multi-step: cart review, shipping address, payment method, order confirmation with summary), OrderList (filterable by status, sortable by date/amount, paginated), OrderDetail (order info header, item list, status timeline, payment info, shipping tracking, action buttons), ChatWindow (message list grouped by date, input with emoji/attachment, typing indicator, file preview), WalletCard (balance, held amount, available for withdrawal, mini transaction list, top-up button), DashboardStats (metric cards with trend indicators, mini sparkline charts), DataTable (sortable columns, filter bar, pagination, row selection, bulk actions, export), FileUploader (drag-and-drop zone, file preview for images/documents, upload progress, validation errors), ImageGallery (thumbnail strip, main image viewer, lightbox modal, zoom on hover).

**Feature Components:** Feature-specific components scoped to their feature folder. Examples include SellerProductTable (with bulk status change, export), BuyerOrderTimeline (visual step tracker with dates), AdminUserTable (with impersonation, suspend actions), AffiliateLinkGenerator (with preview, copy, QR code), SupportTicketForm (with priority selection, category, attachment).

**Layout Components:** Header (sticky, condensed on scroll, mega-menu for categories), Footer (multi-column, newsletter signup, social icons, payment methods), Sidebar (collapsible, nested menus, user profile section), Navbar (horizontal links, dropdown menus, responsive hamburger), MobileNav (bottom tab bar with icons, or slide-in drawer), BreadcrumbNav (auto-generated from path segments, with home icon), DashboardShell (sidebar + topbar + content area wrapper).

**Form Components:** FormField (label with required indicator, input wrapper, error message, helper text), FormSelect (native select with styled wrapper, searchable variant), FormTextarea (auto-resize, character count), FormCheckbox (single and group variants, indeterminate state), FormRadio (horizontal and vertical layout, card variant), FormDatePicker (date input, calendar popup, range picker variant), FormFileUpload (drag-drop zone, file list with preview, progress bar, remove button, size/type validation), FormSubmitButton (with loading spinner, disabled state, success feedback).

**Table Components:** DataTable (generic typed table accepting column definitions, data source, sorting/filtering state), renderers for each column type (text, number, date, status badge, actions), header with sort indicators, footer with pagination info.

**Modal Components:** ConfirmModal (destructive action confirmation with description), FormModal (inline form in modal overlay), ImageModal (lightbox with navigation), FullScreenModal (maximized overlay for complex content).

**Chart Components:** RevenueChart (line chart with area fill, monthly/quarterly toggle), SalesChart (bar chart with grouped by product/category), OrderChart (pie/donut chart by status), UserChart (area chart for new users, bar for active users), TrendChart (sparkline mini chart for dashboard metric cards).

**Navigation Components:** SidebarMenu (nested menu items, icons, active indicator, badge counts, collapse animation), TopNav (horizontal links with dropdown submenus, active underline indicator), BreadcrumbNav (auto-generated segments, max items before truncation with ellipsis dropdown), TabNav (horizontal tabs with underline or pill style, scrollable container), StepNav (wizard progress indicator with numbered steps, completed/active/pending states), PaginationNav (page buttons, prev/next, first/last, ellipsis, page size dropdown, total count display).

---

## 6. Design System

**Typography:** Font family: Inter (headings) + system font (body). Scale: xs (12px), sm (14px), base (16px), lg (18px), xl (20px), 2xl (24px), 3xl (30px), 4xl (36px), 5xl (48px). Responsive adjustments at breakpoints. Line height: tight (1.2), normal (1.5), relaxed (1.75). Font weight: normal (400), medium (500), semibold (600), bold (700).

**Spacing:** 4px base unit. Scale: 0, 1 (4px), 2 (8px), 3 (12px), 4 (16px), 5 (20px), 6 (24px), 8 (32px), 10 (40px), 12 (48px), 16 (64px), 20 (80px), 24 (96px). Applied via Tailwind utility classes. Consistent spacing ensures visual rhythm across all components.

**Color Palette:**
- Primary: Blue (#2563EB with dark mode variant)
- Secondary: Slate (#64748B)
- Success: Green (#16A34A)
- Warning: Amber (#D97706)
- Error: Red (#DC2626)
- Info: Cyan (#0891B2)
- Neutral: Gray scale (50-950)
- Surface: White / Gray-900 (dark mode)
- Text: Gray-900 / Gray-100 (dark mode)
- Border: Gray-200 / Gray-700 (dark mode)
- Focus Ring: Primary color at 0.5 opacity

**Grid System:** CSS Grid via Tailwind grid column utilities. Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px). Container max-width: 1280px centered with padding. Product grids: 2 columns (mobile) to 5 columns (wide desktop).

**Component Design Tokens:**
- **Buttons:** variants (primary/secondary/outline/ghost/danger), sizes (sm/md/lg), states (default/hover/active/disabled/loading), rounded (default: md), shadow on primary variant, transition on all.
- **Cards:** padding (p-6), rounded (xl), shadow (sm default, md on hover for interactive cards), border (gray-200), header/body/footer slot regions, clickable overlay variant.
- **Tables:** header (bg-gray-50 dark:bg-gray-800, font-semibold, uppercase tracking-wide), alternating row stripes, hover highlight on rows, responsive horizontal scroll on mobile, sticky header option.
- **Forms:** input height (40px default, 48px for lg), border (gray-300, 1px), focus ring (primary, 2px offset), error state (red border + red text message), label (font-medium, text-sm, mb-1), helper text (text-xs, text-gray-500), required indicator (red asterisk).
- **Badges:** sizes (sm/md/lg), color variants (gray/green/red/amber/blue/purple/indigo), dot variant for live status indicators, pill shape (fully rounded).
- **Alerts:** types (info/success/warning/error), with icon matching type, dismissible (X button), positioned variants (inline, banner full-width, toast floating), border-left accent for inline variant.
- **Modals:** sizes (sm: 400px, md: 500px, lg: 640px, xl: 800px, full: 95vw), backdrop with blur and semi-transparent dark overlay, close button (top-right), header/body/footer slots, ESC key to close, click outside to close, focus trap for accessibility.
- **Dropdowns:** position (bottom-left, bottom-right, top-left, top-right), with divider between groups, disabled items, items with icons, keyboard navigation (up/down arrows, enter to select), click outside to close.
- **Navigation:** vertical sidebar and horizontal topnav variants. Active indicator (left bar for sidebar, underline for topnav). Nested items with indentation and expand/collapse chevrons. Collapse animation via Framer Motion.
- **Breadcrumbs:** separator (chevron/slash/arrow), with home icon, max items before truncation (show last 2 with "..." dropdown for overflow), active page is non-clickable text.
- **Pagination:** page number buttons with active state, prev/next with chevron icons, ellipsis for large page ranges, page size selector dropdown, total result count display.
- **Tabs:** underline (default) and pill variants. Icons on tabs. Horizontal scroll container for overflow tabs. Active tab indicator animation. Content panel transition.
- **Accordion:** chevron icon rotation animation, single or multi-expand modes, with optional icon per item, smooth height transition via Framer Motion.
- **Loading States:** skeleton (rectangle/circle/text lines with shimmer animation), spinner (size variants with Tailwind animate-spin), progress bar (determinate with percentage, indeterminate with stripes), overlay spinner (full-page with backdrop).

---

## 7. Theme Architecture

**Light Mode:** Default theme. White or near-white backgrounds (white, gray-50), dark text (gray-900), subtle shadows (gray-200/300). Primary colors are vibrant and saturated. High contrast between text and background. Border colors are light (gray-200). Surface elevation indicated by shadow depth.

**Dark Mode:** Dark backgrounds (gray-900, gray-950), light text (gray-100, gray-50), reduced shadow emphasis (shadows are lighter and more transparent). Adjusted primary colors to maintain contrast on dark backgrounds. Border colors are dark (gray-700). Surface elevation indicated by lightness rather than shadow.

**System Theme:** Respects `prefers-color-scheme` media query. Defaults to system preference on first visit. User can override the preference via the theme toggle in the UI. The toggle cycles through: system → light → dark → system.

**Theme Persistence:** Theme preference stored in localStorage via Zustand persist middleware. Initialized from `prefers-color-scheme` or saved value. A cookie holds the preference as fallback for SSR. The theme is applied by adding/removing a `dark` class on the `<html>` element. Tailwind's `darkMode: 'class'` configuration handles the rest. Theme transitions are smooth (CSS transition on background and text colors, 200ms ease).

**CSS Variables:** Design tokens exposed as CSS custom properties on `:root` and `.dark`. Colors, spacing scales, font sizes, shadows, border radii defined as variables. Tailwind config references these variables for consistency. Dynamic theme switching works by toggling the class, which changes the variable values. Third-party libraries (charts, editor) also reference these variables.

---

## 8. State Management

**Zustand — Global Client State:**

- **authStore:** Holds current user object, access token (in-memory only), refresh token, isAuthenticated flag, login/logout/refresh actions. On app initialization, attempts silent refresh if a refresh token cookie exists. Clears on logout.
- **cartStore:** Manages cart items array, item quantities, computed total, addToCart/removeFromCart/updateQuantity/clearCart actions. Synced to server on checkout. Persisted to localStorage for session continuity.
- **uiStore:** Controls sidebar open/closed, mobile menu visibility, active modal stack (allows multiple modals), toast queue, global loading overlay. Actions for open/close/toggle.
- **themeStore:** Stores theme preference (light/dark/system). Persisted to localStorage. Applies dark class to HTML element. Listens for system preference changes.
- **notificationStore:** Holds notification list, unread count, markAsRead/markAllRead actions. Updated via WebSocket push and poll fallback. Badge count derived from unread count.
- **filterStore:** Active filters for product search/category pages (price range, category, rating, seller), sort order, search query. Persisted in URL query params for shareability.

**TanStack Query — Server State:**

- **Caching:** All server-fetched data (products, orders, users, messages, reviews, analytics) managed by TanStack Query. Automatic cache deduplication prevents redundant requests.
- **Stale Time:** Varies by data freshness requirements: products list (5 min), product detail (5 min), orders list (1 min), order detail (30 sec), messages (0 — always fresh), wallet balance (30 sec), categories (1 hr), static pages (24 hr).
- **Cache Invalidation:** On successful mutation (create/update/delete), related queries invalidated. On WebSocket event (order status change), specific queries invalidated. On window refocus, stale queries refetched.
- **Pagination:** Infinite queries (`useInfiniteQuery`) for scroll-based lists (product listing, search results). Paginated queries (`useQuery` with page param) for table-based lists (orders, users, transactions).
- **Prefetching:** On hover over a list item, prefetch detail query. On page load, prefetch next page of paginated results. On mouse proximity to scroll end, prefetch next infinite page.
- **Optimistic Updates:** Cart operations, like/wishlist toggle, follow/unfollow. On mutation, immediately update cache, roll back on error.
- **Background Refetch:** On window focus (configurable per query). Interval polling for near-real-time data: messages (15s), notifications (30s), order status (30s).
- **Error Handling:** Global `onError` callback shows toast for unexpected errors. Per-query `onError` handles domain-specific errors (e.g., "product out of stock"). Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s).

**Server State vs Client State:**

- **Server State (TanStack Query):** products, orders, users, reviews, messages — fetched from API, cached, stale-while-revalidate, refetched on invalidation.
- **Client State (Zustand):** UI state (sidebar, modals, toasts), cart (synced to server on checkout), auth tokens (in-memory), theme preference, active filters, notification list.
- **Local State (useState):** Form inputs, dropdown open/closed, accordion expanded state, tab selection, tooltip visibility, animation state.

**Cache Strategy:**
- **Fresh data:** Real-time (messages, notifications) — poll every 15s or push via WebSocket.
- **Semi-fresh:** Order status (30s poll), wallet balance (30s poll).
- **Stale-OK:** Product details (5 min), categories (1 hr), static content (24 hr).
- **Persistent:** Auth tokens (in-memory only), theme (localStorage), cart (localStorage), language preference (localStorage/cookie).

---

## 9. API Integration Strategy

**Axios Client:**

- **Base URL:** Read from `NEXT_PUBLIC_API_URL` environment variable.
- **Request Interceptor:** Attaches Authorization header with Bearer access token from authStore. Adds `Accept-Language` header for i18n. Adds `X-Idempotency-Key` for POST/PUT mutations. Logs non-production requests.
- **Response Interceptor:** Unwraps `response.data`. Handles 401 (token refresh flow). Handles network errors (retry with backoff). Normalizes error responses to standard format `{ code, message, fields, requestId }`.
- **Token Refresh Interceptor:** On 401, checks if refresh is in progress. If not, starts refresh (POST /auth/refresh). Queues concurrent requests during refresh. On success, replays queued requests with new token. On failure, clears auth and redirects to login.
- **Timeout:** 30 seconds default. 60 seconds for file upload endpoints. 10 seconds for health-check endpoints.

**API Layer (`services/`):**

- One service file per domain: `auth.service.ts`, `product.service.ts`, `order.service.ts`, `wallet.service.ts`, `review.service.ts`, `chat.service.ts`, `notification.service.ts`, `admin.service.ts`.
- Each exports typed async functions (not classes): `fetchProducts(params)`, `createProduct(data)`, `updateOrderStatus(id, status)`.
- Functions accept typed parameters, return typed responses using the API types from `types/`.
- Pagination, filtering, sorting passed as query parameters.

**Error Handling:**

- **Global Axios Error Interceptor:** Catches all responses with error status. Logs to console in development, to Sentry in production.
- **Network Errors:** Retry with 3 attempts and exponential backoff (1s, 2s, 4s). Show toast "Connection lost. Retrying...".
- **401 Unauthorized:** Attempt token refresh. If refresh fails, clear auth and redirect to login with return URL.
- **403 Forbidden:** Redirect to `/403` or show inline "Access denied" message. Logged as security event.
- **404 Not Found:** Show "Resource not found" message or redirect to `/404`.
- **422 Validation Error:** Map field-level errors to form fields via React Hook Form's `setError`. Show form-level alert for general errors.
- **429 Rate Limit:** Show countdown toast "Too many requests. Retry in X seconds." Disable submit button during cooldown.
- **500+ Server Error:** Show generic error toast with request ID for support reference. Auto-report to Sentry.

**Retry Strategy:**
- **TanStack Query:** 3 retry attempts with exponential backoff (1s, 2s, 4s) for failed queries. No retry for mutations (handled manually).
- **Axios Interceptor:** Retry for network errors only (not 4xx/5xx). 3 attempts with exponential backoff.
- **Idempotent Requests:** GET, PUT, DELETE can be retried automatically. POST with idempotency key can be retried.

**Token Refresh:**

- Access token expires in 15 minutes. Refresh token expires in 7 days (sliding expiration).
- On 401 response, interceptor attempts refresh via `POST /auth/refresh` with refresh token.
- If refresh succeeds: new access token stored in memory, original request replayed with new token, queued concurrent requests replayed.
- If refresh fails (refresh token expired/invalid): clear auth store, redirect to login.
- Refresh tokens are rotated: old refresh token invalidated, new one issued on each refresh.

**Request Queue:**

- Queue implemented as an array of `{ resolve, reject, config }` objects.
- When 401 is caught, a flag `isRefreshing` is set. All subsequent 401s during refresh push their request config to the queue.
- Once new token is obtained, the queue is drained: each request replayed with the new token.
- If refresh fails, all queued requests are rejected and auth is cleared.

**Pagination:**

- **Cursor-based:** Used for infinite scroll (product listing, search results). Request: `?cursor=abc&limit=20`. Response: `{ data: [...], next_cursor: "xyz", has_more: true }`.
- **Page-based:** Used for tables (orders, users, transactions). Request: `?page=1&per_page=20`. Response: `{ data: [...], total: 150, page: 1, per_page: 20, total_pages: 8 }`.

**Filtering/Sorting:**

- Filters passed as query parameters. Object filters serialized: `?category=games&price_min=10&price_max=100&rating_min=4`.
- Sorting: `?sort=field` (ascending) or `?sort=-field` (descending). Multiple sorts: `?sort=-rating,price`.
- Filters persisted in URL for shareability and browser back/forward support.

**Search:**

- Debounced input (300ms) via `useDebounce` hook.
- Query: `?q=search_term`. Results from Elasticsearch via backend API.
- Combined with filters and sorting: `?q=laptop&category=electronics&price_min=500&sort=-rating`.
- Suggestions endpoint for autocomplete dropdown: `?q=lap&limit=5`.

---

## 10. Authentication Flow

**Login Flow:**

1. User submits email + password on `/login`.
2. Form validated client-side (Zod), then sends `POST /api/v1/auth/login`.
3. Server validates credentials, returns `{ access_token, refresh_token, user }`.
4. Access token stored **in-memory only** (Zustand authStore). Never persisted to localStorage or sessionStorage.
5. Refresh token stored in HTTP-only, Secure, SameSite=Strict cookie (set by server). As a fallback, encrypted in localStorage.
6. User object (id, name, email, role, avatar, permissions) stored in authStore.
7. Redirect to intended page (from `?redirect=` param) or default dashboard based on role.

**Logout Flow:**

1. `POST /api/v1/auth/logout` — invalidates refresh token on server.
2. Clear authStore (user, tokens, isAuthenticated).
3. Clear TanStack Query cache (all queries refetched as anonymous on next visit).
4. Clear any persisted cart/wishlist (optional, configurable).
5. Redirect to `/login` or home page.

**Refresh Token Flow:**

1. Axios response interceptor catches a 401 response.
2. Check `isRefreshing` flag. If already refreshing, queue the request.
3. If not refreshing, set flag, send `POST /api/v1/auth/refresh` with refresh token.
4. On success: update access token in authStore, reset flag, replay all queued requests.
5. On failure: reset flag, clear auth, reject queued requests, redirect to login.

**Session Handling:**

- Session persists across browser tabs via `storage` event listener (syncs logout state).
- On app load: check for existing valid access token. If expired, attempt silent refresh. If refresh fails, user remains anonymous.
- WebSocket connection re-established on token refresh.
- Inactivity timeout: after 30 minutes of inactivity, show a warning modal. After 5 more minutes, auto-logout.
- Session extend: any API call resets the inactivity timer.

**Protected Routes:**

- **Middleware:** Checks for valid access token on route request. No token → redirect to `/login?redirect=<current_url>`.
- **Expired Token:** Middleware allows through (refresh will happen client-side). If refresh fails, client redirects.
- **Role-based Access:** Middleware checks user role against required roles for the route. Buyer routes require `buyer` role. Seller routes require `seller` or `admin`. Admin routes require `admin`.
- **Role Mismatch:** Redirect to user's appropriate dashboard or show 403 page.

**Permission Guard (Client-side):**

- `useAuth()` hook returns `{ user, role, permissions, isAuthenticated, isLoading }`.
- `<PermissionGuard permission="product.create">` — renders children only if user has the `product.create` permission.
- `<RoleGuard roles={['admin', 'seller']}>` — renders children only if user has one of the specified roles.
- Guards are components, not wrappers — they return `null` or children. This enables conditional rendering without extra nesting.

---

## 11. Form Architecture

**React Hook Form:**

- `useForm` with Zod resolver (`@hookform/resolvers/zod`).
- Type-safe forms: inferred TypeScript types from Zod schemas.
- Mode: `onChange` for real-time validation feedback on UX-critical forms (checkout, registration). `onSubmit` for performance on large forms (product creation with many fields).
- `useFormContext` for deeply nested form components to access parent form state.
- Reusable `FormField` wrapper component that connects RHF's `register`/`control` with label, input, error message, and helper text.

**Zod Validation:**

- Zod schemas defined alongside features in `features/*/types/` or `utils/validators.ts`.
- Common validators: `email()`, `password` (min 8, uppercase, lowercase, number, special char), `url()`, `fileSize()`, `fileType()`.
- Cross-field validation via `.refine()`: password match, conditional required fields.
- Async validation via `.refine()` with async function: email uniqueness check on blur.
- i18n error messages via custom error map that looks up translation keys.

**Reusable Inputs:**

- `FormField` — generic wrapper accepting `name`, `label`, `control`, `rules`, `disabled`, `placeholder`, `helperText`. Renders label, input child, error message.
- `FormInput` — text/email/password input with FormField integration.
- `FormSelect` — native or custom select with FormField.
- `FormTextarea` — auto-resizing textarea with FormField.
- `FormCheckbox` — single or group checkboxes with FormField.
- `FormRadio` — horizontal/vertical radio group with FormField.
- `FormDatePicker` — date input with popup calendar.
- `FormFileUpload` — drag-and-drop file upload with preview, progress, validation.
- `FormSubmitButton` — submit button with loading spinner, disabled state, success feedback.

**Error Messages:**

- **Inline:** Per-field error displayed below the input in red text with an error icon. Visible immediately or after submit attempt depending on validation mode.
- **Form-level:** Alert banner at the top of the form showing summary of errors. Used for API-level errors (e.g., "This email is already registered").
- **API Errors:** Server validation errors (422) mapped to form fields via `setError`. Non-field errors shown as form-level alert.
- **Network Errors:** Toast notification "Could not save. Check your connection and try again."

**Async Validation:**

- **On blur:** Check email/username uniqueness via debounced API call. Zod refine + TanStack Query for debounced API check.
- **File upload:** Validate size, type, dimensions before upload begins. Image dimensions checked via `FileReader` + `Image` object.
- **Submit:** Full server-side validation. Server field errors mapped back to form fields. Non-field errors shown as form-level alert.

---

## 12. Performance Strategy

**Lazy Loading:**

- `next/dynamic` for heavy components below the fold: chart components, rich text editors (for product descriptions), image galleries/lightboxes, map components, payment iframes.
- IntersectionObserver for lazy loading images (`loading="lazy"` on `<img>`, and custom hook for content sections).
- Dynamic imports with named exports: `const RevenueChart = dynamic(() => import('@/components/charts/RevenueChart'), { ssr: false })`.

**Dynamic Imports:**

- Chart components (Recharts) — loaded only on dashboard pages.
- CMS content renderers — loaded only on CMS-managed pages.
- Heavy form sections (file uploader, rich text editor) — loaded only when the form section is visible.
- Third-party widgets (maps, payment iframes, social feeds).
- Vendor chunk splitting: `react`, `react-dom`, `next` in framework chunk. Large libraries (Recharts, editor) in their own chunks.

**Code Splitting:**

- Next.js App Router automatically code-splits by route. Each route group shares layout code.
- Route groups (`(public)`, `(auth)`, `(dashboard)`) enable shared layout code without duplication.
- Dynamic imports for conditionally rendered components.
- Libraries split into vendor chunks to leverage browser caching.

**Image Optimization:**

- `next/image` for all images with automatic WebP/AVIF format negotiation.
- Responsive `srcset` generated automatically based on layout sizes.
- Lazy loading by default (`loading="lazy"`) for below-the-fold images.
- Blur placeholder (`placeholder="blur"`, `blurDataURL`) for product images.
- CDN delivery with remote patterns configured in `next.config.js`.
- Quality optimization: 75% default, 85% for product hero images.

**Memoization:**

- `React.memo` for pure components that receive the same props frequently: ProductCard, OrderRow, ReviewCard, ListItem.
- `useMemo` for expensive computed values: filtered/sorted lists, cart totals, formatted prices, grouped data.
- `useCallback` for event handlers passed to child components: onClick, onChange, onSort.
- Selective: memoization applied only where profiling shows benefit (avoid premature optimization).

**Virtual Lists:**

- `@tanstack/react-virtual` for large lists: order history (1000+ orders), message list, transaction log, notification list, user management tables.
- Renders only visible rows + overscan buffer (5 items).
- Fixed or dynamic item height estimation. Dynamic measurement for variable-height items (chat messages).
- Smooth scrolling with native scroll container.

**Prefetching:**

- Link prefetch on hover (Next.js default for `<Link>` components in viewport).
- `router.prefetch()` for predicted next pages (e.g., after adding to cart, prefetch checkout).
- TanStack Query `queryClient.prefetchQuery()` for detail pages on hover over list item.
- Product detail prefetched when user scrolls past the product card in listing.

**Caching:**

- TanStack Query: stale-while-revalidate strategy. Serve cached data immediately, refetch in background.
- Service Worker: Cache static assets (JS, CSS, fonts, icons) via Workbox in next-pwa or custom service worker.
- Browser cache: CDN images with `Cache-Control: public, max-age=31536000, immutable`. Static JS/CSS with content hash in filename for long cache duration.
- API cache headers respected by TanStack Query.

**Streaming:**

- Next.js streaming SSR for slow pages: dashboard overview with multiple chart queries, product listing with filters.
- Suspense boundaries for async components: `<Suspense fallback={<Skeleton />}>` around data-fetching components.
- Progressive rendering: skeleton → content, as each Suspense boundary resolves.
- Partial prerendering (PPR) for hybrid pages: static shell + dynamic content streams in.

---

## 13. SEO Strategy

**Metadata:**

- Next.js Metadata API for all pages. Static metadata for public pages. Dynamic metadata generated in `generateMetadata()` for product, category, and blog pages (fetched from API).
- Template pattern: `"%s | TSBL Marketplace"`. Home page uses just "TSBL Marketplace".
- Each page defines: `title`, `description`, `keywords`, `openGraph`, `twitter`, `robots`, `alternates` (canonical, languages), `other` (custom meta tags).

**Open Graph:**

- Every page includes OG tags: `og:title`, `og:description`, `og:image`, `og:url`, `og:site_name`, `og:type`.
- `og:type` varies by content: `website` for homepage, `article` for blog posts, `product` for product pages.
- OG image: 1200x630px, generated dynamically for product pages (product image + title overlay). Default OG image for other pages.
- `og:locale` reflects current language.

**Twitter Cards:**

- `twitter:card`: `summary_large_image` for most pages, `summary` for profile pages.
- `twitter:title`, `twitter:description`, `twitter:image`, `twitter:site` (`@tsblmarketplace`).

**Structured Data (JSON-LD):**

- **Product:** name, description, image, offers (price, availability, currency), aggregateRating, brand/seller. Injected on product detail pages.
- **Organization:** name, url, logo, contactPoint, sameAs (social links), address. Injected on homepage and contact page.
- **BreadcrumbList:** itemListElement with position, name, url. Injected on all pages with breadcrumbs.
- **Review:** itemReviewed, author, reviewRating, datePublished. Injected alongside user reviews.
- **FAQ:** mainEntity array of Question/Answer. Injected on FAQ page.
- **BlogPosting:** headline, author, datePublished, dateModified, image. Injected on blog pages.
- **LocalBusiness (if applicable):** name, address, geo, openingHours, telephone.

**Canonical URLs:**

- Every page includes a self-referencing canonical link tag.
- Prevents duplicate content issues from query params, pagination, or multiple URL patterns.
- Pagination: `rel="next"` and `rel="prev"` link tags on paginated pages.

**XML Sitemap:**

- Dynamically generated via `app/sitemap.ts`.
- Includes all public routes: homepage, products, categories, blog, static pages.
- Priority and change frequency: products (0.8, weekly), categories (0.6, weekly), blog (0.5, monthly), static (0.3, monthly).
- Updated on content publish (triggered via API revalidation).
- Submitted to Google Search Console.

**Robots.txt:**

- Allow: all public routes (`/`, `/products`, `/categories`, `/blog`, `/about`, `/contact`, `/faq`).
- Disallow: admin routes (`/admin/*`), dashboard routes (`/buyer/*`, `/seller/*`, `/affiliate/*`, `/support/*`), auth routes (`/login`, `/register`, `/forgot-password`, `/reset-password/*`), API routes (`/api/*`).
- Dynamic generation via `app/robots.txt.ts` to include sitemap URL.

**Additional SEO:**

- Semantic HTML5 elements (`<main>`, `<nav>`, `<article>`, `<section>`, `<aside>`, `<header>`, `<footer>`) for proper document outline.
- Single `<h1>` per page, hierarchical heading structure (h1 → h2 → h3).
- Descriptive alt text for all images (product name + "image" format).
- Descriptive link text (no "click here").
- Fast Core Web Vitals targets: LCP < 2.5s, FID < 100ms, CLS < 0.1.
- Mobile-first indexing with fully responsive design.
- Breadcrumb navigation for internal linking and user orientation.

---

## 14. Accessibility Strategy

**WCAG 2.2 AA Compliance:**

- **Perceivable:** All content available to senses. Text alternatives (alt text, captions, transcripts). Adaptable content (reflow, text spacing, orientation). Distinguishable foreground/background (contrast, color not sole differentiator).
- **Operable:** All functionality available via keyboard (no keyboard traps). Enough time (adjustable timeouts, pause moving content). Seizure prevention (no flashing content > 3 Hz). Navigable (skip links, headings, focus order, link purpose).
- **Understandable:** Readable text (locale-appropriate language). Predictable behavior (consistent navigation, no unexpected context changes). Input assistance (labels, errors, suggestions).
- **Robust:** Compatible with current and future assistive technologies. Semantic HTML, proper ARIA, valid code.

**Keyboard Navigation:**

- All interactive elements reachable via Tab in logical order (visual order).
- Visible focus indicator on all interactive elements (3px ring, high contrast).
- Focus trap in modals, dialogs, and slide-in panels. Tab cycles within the component. ESC to close.
- Arrow keys for: tab navigation (left/right), dropdown options (up/down), carousel slides (left/right), accordion items (up/down), tree views (up/down, left/right to expand/collapse).
- Enter/Space to activate buttons, links, toggles.
- Home/End for list navigation. Page Up/Down for scrollable containers.

**ARIA Labels:**

- `aria-label` on icon-only buttons (e.g., "Search", "Close modal", "Menu").
- `aria-describedby` connecting complex inputs to their descriptions.
- `aria-live="polite"` for dynamic content updates (toasts, notifications). `aria-live="assertive"` for critical alerts.
- `aria-expanded` and `aria-controls` on expandable sections (accordion, dropdown, collapsible sidebar).
- `aria-current="page"` on active navigation items. `aria-current="step"` on current wizard step.
- `role="alert"` on error messages and form validation alerts.
- `role="dialog"` and `aria-modal="true"` on modals.
- `role="tablist"`, `role="tab"`, `role="tabpanel"` on tab components.

**Screen Readers:**

- Semantic HTML elements used instead of generic `<div>`s: `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>`, `<article>`, `<section>`.
- Heading hierarchy enforced: one `<h1>` per page, no skipped levels.
- List elements (`<ul>`, `<ol>`, `<li>`) for lists. Description lists (`<dl>`) for key-value pairs (product specs).
- Table headers (`<th>` with `scope`) for data tables.
- All form inputs have associated `<label>` elements (not just placeholders).
- "Skip to content" link as first focusable element on every page.
- Loading and status changes announced via `aria-live` regions.
- PDF and document links indicate file type and size in link text.

**Color Contrast:**

- Minimum 4.5:1 contrast ratio for normal text (below 18px / below 14px bold).
- Minimum 3:1 for large text (above 18px / above 14px bold).
- Dark mode contrasts verified separately.
- Focus indicators: 3px ring with 3:1 minimum contrast against adjacent colors.
- Color not used as the sole indicator of state. Status indicators use icons + color + text (e.g., "Active" badge with green dot + text).
- Error states: red border + error icon + error text message.

**Focus Management:**

- Visible focus ring on all interactive elements: `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`.
- Focus trap in modals: first focusable element on open, cycle within modal, return focus to trigger on close.
- Smart autofocus: first input on forms, close button on modals, search input on search page.
- Focus restoration on close: return focus to the element that triggered the modal/dropdown.
- Manage focus when content updates dynamically (e.g., after adding item to cart, focus moves to cart icon).

---

## 15. Responsive Design Strategy

**Breakpoints (Tailwind):**

- `sm`: 640px — mobile landscape.
- `md`: 768px — tablet portrait.
- `lg`: 1024px — tablet landscape / small laptop.
- `xl`: 1280px — desktop.
- `2xl`: 1536px — wide desktop.

**Navigation:**

- Below `md`: hamburger menu icon opens a full-screen slide-in navigation drawer. Dashboard bottom navigation bar (icons + labels for main sections).
- `md` to `lg`: Collapsible sidebar (icon-only with tooltip labels). Top navigation bar with dropdown menus for secondary navigation.
- `lg` and above: Full sidebar with icon + text labels. Expanded horizontal top navigation.

**Layout Adaptation:**

- **Product Grid:** 2 columns (mobile) → 3 columns (tablet) → 4 columns (desktop) → 5 columns (wide).
- **Sidebar:** Hidden / overlay (mobile) → mini / collapsible (tablet) → full (desktop and above).
- **Tables:** Standard table with horizontal scroll on mobile. On very small screens, table rows transform into card layout.
- **Forms:** Single column (mobile) → two columns (tablet) → three columns (desktop) for large forms. Inline fields stack on mobile.
- **Dashboard Cards:** 1 column (mobile) → 2 columns (tablet) → 3-4 columns (desktop).
- **Hero/Banner:** Full-width on mobile, contained with max-width on desktop. Text overlay on mobile below image.
- **Footer:** Stacked single column (mobile) → 2 columns (tablet) → 4 columns (desktop).

**Adaptive Components:**

- **ProductCard:** Horizontal layout (image left, content right) on mobile. Vertical layout (image top, content below) on tablet and above.
- **DataTable:** Traditional table on desktop. Card list on mobile (each row becomes a card with key-value pairs and actions).
- **Header:** Condensed (compact logo, search icon opens full search, fewer nav items) on mobile. Full layout on desktop.
- **Footer:** Stacked sections (mobile) → multi-column grid (desktop).
- **Modal:** Full-screen on mobile (takeover), centered overlay on desktop.
- **Pagination:** Page numbers hidden on mobile (only prev/next + "Page X of Y").
- **Breadcrumb:** Truncated on mobile (show last 2 items with "...").
- **Charts:** Simplified on mobile (hide legends, fewer data points, smaller sizing).

---

## 16. Internationalization

**Languages:**

- Primary: English (en).
- Secondary: Bengali (bn) — Bangladesh market focus.
- Additional: Arabic (ar), Hindi (hi), Spanish (es), French (fr).
- Additional languages added via JSON files in `src/messages/`.
- Locale detection: URL prefix (`/en/products`, `/bn/products`) via next-intl routing.

**RTL Support:**

- Arabic enabled right-to-left layout.
- Tailwind RTL support via `rtl:` prefix: `rtl:left-auto` `rtl:right-0`.
- Layout flips for RTL: sidebar on right, text alignment reversed, icons mirrored for directional indicators (arrows, chevrons).
- Separate CSS variable adjustments for RTL spacing and margins.
- Form inputs and modals mirror their layout in RTL mode.

**Currency Formatting:**

- `Intl.NumberFormat` for all currency display. Locale and currency code from user profile, browser locale, or URL.
- Format examples: $1,234.56 (en-US), ৳১,২৩৪.৫৬ (bn-BD), €1.234,56 (de-DE).
- Default currency: BDT for Bangladesh market, USD for international.
- Currency selector allows user to override display currency (conversion rates from API).

**Date Formatting:**

- `Intl.DateTimeFormat` with locale-aware formatting.
- Formats: relative ("2 hours ago"), short ("Jan 15, 2026"), long ("January 15, 2026"), full ("Wednesday, January 15, 2026").
- Adaptive: relative for recent (< 7 days), absolute for older.
- Order dates displayed in user's timezone.

**Number Formatting:**

- `Intl.NumberFormat` for decimals, percentages, and compact notation (1.2K, 3.5M).
- Locale-aware grouping separators: 1,234,567.89 (en) vs 12,34,567.89 (hi).
- Decimal and percent formatting per locale conventions.

**Timezone Support:**

- All dates stored in UTC on server, converted to user's local timezone on display.
- Timezone detected via `Intl.DateTimeFormat().resolvedOptions().timeZone`.
- User can override timezone in profile settings (e.g., for sellers managing orders across timezones).
- Timezone displayed next to dates where context matters (order deadlines, support response times).

---

## 17. Dashboard Architecture

**Buyer Dashboard:**

- **Overview:** Welcome message with user name, key metrics (order count this month, total spent, wallet balance, unread messages count).
- **Recent Orders:** Last 5 orders displayed as compact cards with status badge, item count, total, and date. Click navigates to order detail.
- **Quick Actions:** row of action cards: "Browse Products", "View Cart", "Track Orders", "Contact Support".
- **Wishlist Preview:** Recent wishlist items (up to 4) with thumbnail, price, and "Add to Cart" button.
- **Suggested Products:** Personalized product recommendations based on browsing/purchase history.
- **Navigation Sidebar:** Orders, Purchases, Downloads, Wallet, Wishlist, Reviews, Messages, Profile, Settings.

**Seller Dashboard:**

- **Overview:** Revenue chart (last 30 days), order count change, new messages count, product performance summary.
- **Recent Orders:** New and pending orders requiring action. Quick actions: "Mark Shipped", "Contact Buyer".
- **Product Stats:** Total listings, active listings, pending approval, sold this month. With progress indicators.
- **Earnings Summary:** This month earnings, available for withdrawal, pending clearance. With "Withdraw" quick action.
- **Quick Actions:** "Add New Product", "Manage Orders", "View Analytics", "Edit Store Profile".
- **Performance Alerts:** Low stock warnings, pending reviews, policy violations.
- **Navigation Sidebar:** Products (list, add, edit), Orders, Earnings, Withdraw, Analytics, Reviews, Messages, Store Profile, Settings.

**Admin Dashboard:**

- **Overview:** Platform-wide metrics: total users, sellers, products, orders, revenue (all-time + this month).
- **Trend Charts:** Revenue trend (line chart), user growth (area chart), order volume (bar chart).
- **Moderation Queue:** Pending products for approval (count + quick approve/reject), pending disputes, flagged content.
- **Recent Activity Feed:** Chronological list of new user registrations, new sellers, new orders, support ticket escalations.
- **Quick Actions:** Moderate products, manage users, generate reports, system settings.
- **System Health:** Server status, API response times, error rate, queue depths.
- **Navigation Sidebar:** Users, Sellers, Products, Orders, Payments, Disputes, Categories, Coupons, Affiliates, Reports, CMS, Settings, Audit Logs.

**Affiliate Dashboard:**

- **Overview:** Total referrals count, total earnings, conversion rate percentage, pending payouts.
- **Referral Links:** Table of affiliate links with stats (clicks, signups, conversions, earnings). "Copy Link" and "Preview" buttons.
- **Earnings Chart:** Daily/weekly/monthly earnings visualization.
- **Withdraw History:** Recent withdrawal requests with status.
- **Quick Actions:** Generate new link, view top performing links, request withdrawal.
- **Navigation Sidebar:** Links, Earnings, Withdraw, Referrals, Profile.

**Support Dashboard:**

- **Overview:** Open tickets count, pending disputes count, average response time, customer satisfaction rating.
- **Ticket Queue:** Priority-sorted ticket list with status, category, requester, age. Quick reply inline.
- **Dispute Queue:** Open disputes requiring moderation with order ID, disputing parties, amount, status.
- **Quick Actions:** View new tickets, respond to disputes, escalate to admin.
- **Performance Metrics:** Tickets resolved today, average resolution time, response time trend.
- **Navigation Sidebar:** Tickets, Disputes, Knowledge Base, Profile.

---

## 18. Error Handling

**404 (Not Found):**

- Custom `not-found.tsx` page with friendly illustration (empty box or lost shopper graphic).
- Message: "Sorry, we couldn't find what you're looking for."
- Search bar to help users find what they need.
- Links to popular categories and home page.
- Status code logged for analytics.

**401 (Unauthorized):**

- Middleware redirects to `/login?redirect=<current_url>`.
- Client-side Axios interceptor handles expired tokens: attempts silent refresh, redirects to login if refresh fails.
- No custom 401 page (redirect instead).

**403 (Forbidden):**

- Custom page with lock icon and "Access Denied" message.
- Explanation: "You don't have permission to view this page."
- "Contact Support" button opens support form or chat.
- Logged as security event (audit log).

**500 (Server Error):**

- Global `error.tsx` error boundary catches unhandled errors.
- Friendly message: "Something went wrong. Our team has been notified."
- Request ID displayed for support reference.
- "Try Again" button re-renders the page.
- Auto-report to Sentry with error details, component stack, and user context.

**Maintenance:**

- Full-screen maintenance page with TSBL logo.
- Status message: "We're doing some maintenance. We'll be back shortly."
- Estimated duration with countdown timer.
- Auto-refresh to check availability every 30 seconds.
- Admin can bypass via `?maintenance_override=true` (checked against session).

**Offline Mode:**

- `navigator.onLine` detection via `useOnlineStatus` hook.
- Offline banner at top of page: "You're offline. Some features may be unavailable."
- Cached pages (products, blog, static pages) still accessible via Service Worker.
- Failed mutations queued in localStorage, replayed on reconnect.
- Offline indicator on save buttons (disabled with tooltip "You're offline").

**Network Failure:**

- Axios interceptor retries failed requests (3 attempts, exponential backoff).
- Toast notification: "Connection lost. Retrying..." with cancel option.
- Graceful degradation: cached data shown when available instead of error state.
- Mutation failures: saved to local queue, replayed on reconnect with user confirmation.

---

## 19. Notification Strategy

**Toast:**

- Temporary notification, auto-dismiss after 5 seconds (configurable per toast).
- Types: success (green, check icon), error (red, X icon), warning (amber, warning icon), info (blue, info icon).
- Position: top-right on desktop, top-center on mobile.
- Stack multiple toasts (up to 5 visible, older ones pushed up).
- Optional action button: "Undo", "View", "Dismiss".
- Used for: order placed, payment confirmed, message sent, settings saved, action result confirmation.

**Modal:**

- Persistent notification requiring user action.
- Types: confirm (destructive actions with "Are you sure?"), alert (important information with "OK"), form (inline editing).
- Used for: confirm delete product, confirm cancel order, enter verification code, confirm logout.
- Blocking: user must interact before continuing (unless cancel is allowed).

**Banner:**

- Page-level notification at the top of content area, dismissible.
- Types: info (blue), success (green), warning (amber), error (red).
- Used for: account unverified (persistent until verified), payment method required, maintenance warning, cookie consent.

**In-App Notification:**

- Notification bell icon in header with unread count badge.
- Dropdown list of recent notifications with read/unread state.
- Click marks as read and navigates to relevant page (order, message, etc.).
- Types: order update (placed, confirmed, shipped, delivered, disputed), payment received/withdrawn, new message, review received, system announcement.
- Mark all as read action.

**Push Notification:**

- Browser push notifications via Service Worker.
- Permission requested on first relevant action (sending message, placing order), not on page load.
- Types: new message from seller/buyer, order status update, payment received, promotional offer.
- Click on notification opens specific page in the app.
- Notification icon and badge using TSBL branding.

**Real-time Notification:**

- WebSocket connection for instant delivery.
- Connection established on successful authentication.
- Fallback: HTTP polling every 30 seconds.
- Reconnect on disconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s).
- Types: chat messages, order status changes, payment confirmations, support ticket updates.

---

## 20. Frontend Security

**XSS Prevention:**

- React's built-in XSS protection: JSX escapes all values before rendering.
- `dangerouslySetInnerHTML` used **only** with sanitized content via DOMPurify.
- User-generated content (reviews, descriptions, messages) sanitized before display.
- Input sanitization: strip HTML tags from text inputs on form submission.
- CSP headers block inline scripts and eval.

**Content Security Policy (CSP):**

- Strict CSP via meta tag or HTTP header.
- `script-src`: `'self'` + `'nonce-{random}'` for inline scripts.
- `style-src`: `'self'` + `'unsafe-inline'` (required for Tailwind).
- `img-src`: `'self'` + CDN domain + S3/media bucket URLs.
- `connect-src`: `'self'` + API domain + WebSocket URLs.
- `frame-src`: `'none'` (no iframes).
- `object-src`: `'none'`.
- `base-uri`: `'self'`.
- `form-action`: `'self'`.
- `report-uri`: CSP violation reporting endpoint.

**Secure Cookies:**

- Refresh token: HTTP-only (inaccessible to JavaScript), Secure (HTTPS only), SameSite=Strict.
- Session cookie: Secure, SameSite=Lax.
- CSRF token: SameSite=Lax, bound to session.
- No sensitive data in any cookie readable by JavaScript.

**Token Storage:**

- Access token (short-lived, 15 min): **in-memory only** (Zustand store). Never written to localStorage, sessionStorage, or cookies.
- On page reload: access token is gone, refresh endpoint called with HTTP-only cookie to obtain new access token.
- Refresh token (long-lived, 7 days): HTTP-only, Secure, SameSite=Strict cookie set by backend.
- This architecture prevents token theft via XSS (access token not persistent, refresh token not accessible to JS).

**Sensitive Data Handling:**

- Never log sensitive data (passwords, tokens, payment info) client-side.
- Credit card numbers: show only last 4 digits ("**** **** **** 4242").
- Email/phone: obscure in UI where appropriate ("j***@example.com").
- Clear sensitive data on logout: auth store cleared, TanStack Query cache cleared, in-memory tokens discarded.
- No sensitive data in URL params (use POST bodies or URL fragments for non-sensitive state).

---

## 21. Testing Strategy

**Unit Tests (Vitest):**

- **Target:** Pure functions — utils (formatters, validators, helpers), constants, Zod schemas.
- **Approach:** Test input → output mapping. Edge cases, error cases, boundary values.
- **Stores:** Test Zustand store state changes and actions in isolation.
- **Custom Hooks:** Use `renderHook` from `@testing-library/react-hooks`. Mock dependencies (services, stores).
- **Service Functions:** Mock Axios, test request formation and response handling.
- **Coverage Target:** 90%+ lines.

**Component Tests (Vitest + React Testing Library):**

- **Target:** All UI components (atoms, molecules, organisms).
- **Approach:** Render component, assert UI elements exist, simulate user interaction, verify state changes.
- **Test behaviors, not implementation:** Query by role, label, text (user-centric queries). Avoid testing internal state or CSS classes.
- **Mock API calls:** Mock service layer at the module level.
- **Test all states:** Loading (skeleton visible), empty (empty state message), error (error message + retry), populated (data displayed correctly).
- **Coverage Target:** 80%+ lines.

**Integration Tests (Vitest + RTL):**

- **Target:** Feature-level user flows — complete sequences within a feature.
- **Approach:** Multi-step interactions: fill form, submit, verify API call, verify success state, verify navigation.
- **Examples:** Checkout flow (add to cart → fill address → select payment → place order), product creation flow, search and filter flow.
- **Auth flow:** Login → redirect → access protected route → logout.
- **Coverage Target:** 70%+ lines.

**E2E Tests (Playwright):**

- **Target:** Critical user journeys across multiple features.
- **Scenarios:** Buyer purchase flow (search → view → add to cart → checkout → pay), seller product creation (fill form → upload images → set price → publish), admin moderation (review product → approve → verify listing).
- **Cross-browser:** Chromium, Firefox, WebKit.
- **Mobile viewport:** iPhone 12 (390x844), iPad (768x1024).
- **Auth setup:** API login before tests (bypass UI login for speed).
- **Visual regression:** Screenshot comparison for key pages (home, product detail, dashboard).
- **Coverage:** All critical paths.

**Accessibility Tests (axe-core + Playwright):**

- **Automated:** jest-axe for unit/component tests, @axe-core/playwright for E2E.
- **Scope:** Scan all pages and components for WCAG 2.2 AA violations.
- **CI:** Accessibility tests run in CI, blocking PRs with critical violations.
- **Manual:** Periodic manual testing for complex interactions (drag-and-drop, custom widgets).
- **Screen reader:** NVDA (Windows), VoiceOver (macOS) compatibility testing.
- **Color contrast:** Validated in both light and dark modes.

**Performance Tests (Lighthouse CI):**

- **CI Integration:** Lighthouse scores collected on every PR and deploy.
- **Budgets:** Performance > 90, Accessibility > 95, SEO > 95, Best Practices > 90.
- **Core Web Vitals:** LCP < 2.5s, FID < 100ms, CLS < 0.1.
- **Bundle Size:** Monitored via `@next/bundle-analyzer`. Alerts on significant increases.
- **Image Optimization:** Audit for unoptimized images, missing dimensions, incorrect formats.

---

## 22. Coding Standards

**TypeScript Best Practices:**

- Strict mode enabled (`strict: true` in `tsconfig.json`).
- No `any` type — use `unknown` then narrow with type guards, validation, or assertion functions.
- Prefer `interface` for public APIs (extensible, merged declarations). Use `type` for unions, intersections, and utility types.
- `Readonly<T>` for immutable props and state. `ReadonlyArray<T>` for immutable arrays.
- Discriminated unions for complex state (loading, success, error states).
- Generics for reusable components, hooks, and utility functions.
- `as const` for literal types and constant objects.

**Naming Conventions:**

- **Components:** PascalCase (`ProductCard`, `OrderList`, `SearchBar`).
- **Hooks:** `use{Name}` (`useAuth`, `useProductQuery`, `useDebounce`).
- **Functions:** camelCase (`formatCurrency`, `fetchProducts`, `handleSubmit`).
- **Variables:** camelCase (`productId`, `isActive`, `userName`).
- **Constants:** UPPER_SNAKE_CASE (`MAX_ITEMS_PER_PAGE`, `API_TIMEOUT`).
- **Types/Interfaces:** PascalCase (`IProduct`, `IOrder`, `UserRole`). Optional `I` prefix for interfaces (consistent across project).
- **Files:** kebab-case for components (`product-card.tsx`), camelCase for hooks/services (`useAuth.ts`, `productService.ts`).
- **Folders:** kebab-case (`product-list`, `order-detail`).

**Folder Structure Rules:**

- Each feature folder contains: `components/`, `hooks/`, `services/`, `stores/`, `types/` subdirectories.
- Shared components in `components/ui` (atoms) and `components/shared` (molecules/organisms).
- Styles: Tailwind classes in JSX. Minimal global CSS in `styles/globals.css`.
- Tests: co-located with component file (`ProductCard.test.tsx`, `ProductCard.stories.tsx` for Storybook).

**Code Style:**

- ESLint + Prettier enforced via pre-commit hooks and CI.
- Import order: 1) React/Next, 2) external libraries, 3) internal modules (`@/components`, `@/hooks`, `@/utils`), 4) relative imports.
- No default exports for components (named exports only for better refactoring and tree-shaking).
- Barrel files (`index.ts`) for public API of each folder (re-export only what's needed externally).

**Reusable Patterns:**

- **Custom hooks** for data fetching, form handling, and reusable logic.
- **Higher-order components** for layout wrappers and guards (withAuth, withRole).
- **Render props** for flexible, composable components.
- **Compound components** for complex UI patterns (Tabs, Accordion, DropdownMenu) — parent component manages state, children declare content.
- **Composition over inheritance:** compose small components to build complex UI.
- **Custom hooks over HOCs** for sharing stateful logic.

---

## 23. Development Workflow

**Git Branching:**

- `main` — production-ready code. Protected branch, no direct pushes.
- `develop` — integration branch. Feature branches merged here.
- `feature/{ticket-number}-{description}` — new features and enhancements.
- `bugfix/{ticket-number}-{description}` — bug fixes.
- `hotfix/{ticket-number}-{description}` — urgent production fixes (branched from and merged to main + develop).
- `release/v{major}.{minor}.{patch}` — release preparation branch.

**Commit Convention (Conventional Commits):**

- `feat:` — new feature.
- `fix:` — bug fix.
- `refactor:` — code refactoring (no feature/bug change).
- `style:` — formatting, styling changes only.
- `docs:` — documentation changes.
- `test:` — adding or updating tests.
- `chore:` — build, CI, dependencies, tooling.
- `perf:` — performance improvement.
- `BREAKING CHANGE:` — breaking API change (in footer or with `!` after type/scope).
- Format: `type(scope): description (#ticket)` — e.g., `feat(checkout): add COD payment option (#TSBL-1234)`.

**Pull Request Guidelines:**

- PR title follows conventional commit format.
- Description includes: what changed, why it changed, how it was tested, screenshots (for UI changes), notes for reviewers.
- Checklist in PR template: lint passes, tests pass, type checks, no console.log, responsive tested, accessibility considered.
- Minimum 1 reviewer approval required for merge.
- CI must pass (lint, type check, unit tests, build) before merge.
- No merge commits — squash or rebase merge.

**Code Review Standards:**

- **Correctness:** Logic handles edge cases, error paths, and boundary conditions.
- **Performance:** No unnecessary re-renders (missing deps in useMemo/useCallback). Bundle impact considered.
- **Security:** No XSS vectors, no data exposure in client-side logs/storage, proper auth guards.
- **Accessibility:** Keyboard navigable, proper ARIA attributes, color contrast, screen reader tested.
- **Maintainability:** Clear naming, reasonable complexity, testable structure, follows project conventions.
- **Scale:** Solution works for the full data volume, not just test data.

**Release Strategy:**

- **Feature flags:** Gradual rollout of large features via flags (controlled by backend config).
- **Staging deploy:** Every merge to `develop` auto-deploys to staging environment.
- **Production deploy:** Weekly release cycle (Tuesday/Thursday). Release branch created from `develop`.
- **Hotfix:** Expedited review, merged directly to `main`, then backported to `develop`.
- **Versioning:** Semantic Versioning (`major.minor.patch`).
- **Changelog:** Auto-generated from commit history between releases (via `standard-version` or `semantic-release`).

---

## 24. Deployment Strategy

**Docker:**

- **Multi-stage build:**
  - **Builder stage:** `node:20-alpine`, install dependencies (`npm ci`), run build (`npm run build`).
  - **Runner stage:** `nginx:alpine`, copy built assets from builder stage, serve with non-root user.
- **Optimization:** `.dockerignore` excludes `node_modules`, `.next`, `git`, `test`, `coverage`, `docs`.
- **Image tags:** `{branch}-{commit-sha}`, `latest` (for stable releases), `v{major}.{minor}.{patch}`.

**NGINX Configuration:**

- Serve static files from `/usr/share/nginx/html`.
- SPA fallback: `try_files $uri $uri.html $uri/ /index.html`.
- Compression: gzip and brotli for text-based assets.
- Cache headers: static assets with content hash (`immutable`, `max-age=31536000`), HTML (`no-cache`).
- Security headers: `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`.
- HTTP/2 enabled.
- Rate limiting: per-IP, burst allowance.

**CI/CD (GitHub Actions):**

- **CI (on PR to develop/main):**
  1. Install dependencies.
  2. Run lint (ESLint).
  3. Run type check (TypeScript).
  4. Run unit + component tests (Vitest).
  5. Run build.
  6. Build Docker image.
  7. Run E2E tests (Playwright) against preview deployment.

- **CD (merge to main):**
  1. Build + tag Docker image (commit hash, `latest`, version tag).
  2. Push image to container registry (Docker Hub / AWS ECR / GHCR).
  3. Deploy to staging environment.
  4. Run smoke tests + E2E tests against staging.
  5. Run Lighthouse CI audit.
  6. Manual approval gate → deploy to production.
  7. Blue-green deployment (swap traffic).

**Static Assets:**

- All static assets served via CDN (Cloudflare, Fastly, or AWS CloudFront).
- `next/image` configured with remote patterns pointing to CDN domain.
- Asset versioning via content hash in filenames (Next.js automatic).
- Cache headers: `public, max-age=31536000, immutable` for versioned assets.
- CDN cache purged on each deployment (selective purge for changed assets only).

**CDN Strategy:**

- **Images:** CDN with automatic WebP/AVIF transformation and responsive resizing.
- **Static JS/CSS:** CDN edge caching, long TTL.
- **Dynamic content (API):** Bypass CDN or short TTL (60s).
- **Purge strategy:** Purge CDN cache by tag or path on each deploy.
- **Geo-distribution:** Edge nodes in multiple regions for global user base.

**Rollback Strategy:**

- **Immediate:** Revert Docker image tag to previous version, redeploy.
- **Blue-green:** Keep previous environment running, swap traffic back instantly.
- **Feature flags:** Disable problematic feature remotely (no deploy needed).
- **Database:** Backward-compatible migrations (no rollback needed for frontend).
- **CDN:** Revert to previous cached version (purge new version from cache).
- **Monitoring:** Automated rollback on error rate spike (>5% errors, >1% 5xx).

---

## 25. Final Frontend Blueprint

**Architecture Summary:**

TRUE STAR BD LIMITED Frontend is a Production-Ready Enterprise Application built with Next.js 15+, TypeScript, React 19+, TailwindCSS, and a carefully selected ecosystem of libraries.

**Core Design Decisions:**

1. **Feature-based Architecture:** Each domain (auth, marketplace, seller, admin, affiliate, support) is an isolated feature with its own components, hooks, services, stores, and types. Teams work independently on separate features. New features added without touching existing code.

2. **Component-driven with Atomic Design:** UI built from small composable atoms → molecules → organisms → templates → pages. Design system with consistent tokens. Maximum reusability, minimum duplication.

3. **Separation of Concerns:** Components (UI), Hooks (logic), Services (API), Stores (state) — each with clear responsibility. Layers are testable in isolation.

4. **Server and Client State Management:** TanStack Query for all server data (caching, invalidation, pagination, optimistic updates). Zustand for global client state (auth, cart, UI, theme). useState for local component state.

5. **Performance-first:** Next.js App Router auto-splits by route. Dynamic imports for heavy components. Image optimization via next/image. Virtual lists for large datasets. Streaming SSR for slow pages. TanStack Query caching reduces API calls.

6. **Security by Design:** XSS prevention (React sanitization, DOMPurify). CSP headers. Secure cookie storage for refresh tokens. In-memory access tokens. No sensitive data in URLs or localStorage.

7. **Full-spectrum Testing:** Unit (Vitest) → Component (RTL) → Integration → E2E (Playwright) → Accessibility (axe-core) → Performance (Lighthouse). 4-layer test pyramid.

8. **SEO & Accessibility First:** Dynamic metadata, JSON-LD structured data (Product, Review, Breadcrumb, Organization schemas), XML sitemap. WCAG 2.2 AA compliance, keyboard navigation, screen reader support, color contrast.

9. **Internationalization Ready:** next-intl for multi-language. RTL support. Locale-aware currency, date, number formatting. Timezone detection and override.

10. **Scalable Architecture:** Feature-based = horizontally scalable (add features without complexity). Component-driven = vertically scalable (add detail without bloat). The architecture supports 10M+ users, millions of listings, and multiple portals (buyer, seller, admin, affiliate, support) in a single coherent codebase.

**Why Production-Ready:**

- Battle-tested patterns from enterprise marketplaces.
- Security integrated at every layer.
- Performance targets quantified and measurable.
- Comprehensive testing strategy.
- Internationalization and accessibility built-in.
- Clear development workflow and coding standards.
- Containerized deployment with blue-green rollouts.
- Architecture is documented, reviewable, and evolvable.

---

> **Document Author:** Frontend Architecture Team  
> **Reviewers:** Lead Architect, CTO, DevOps Lead  
> **Approved By:** Principal Frontend Architect  
> **Next Review Date:** 2026-10-02
