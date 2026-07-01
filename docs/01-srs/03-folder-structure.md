# Folder Structure & Architectural Rationale — TRUE STAR BD LIMITED Digital Marketplace

> **Document ID:** SRS-FS-003
> **Version:** 1.0
> **Status:** Draft
> **Author:** Principal Software Architect
> **Last Updated:** 2026-07-01

---

## Table of Contents

1. [Architectural Philosophy](#1-architectural-philosophy)
2. [Complete Folder Tree](#2-complete-folder-tree)
3. [Top-Level Directories](#3-top-level-directories)
4. [Frontend Deep Dive](#4-frontend-deep-dive)
5. [Backend Deep Dive](#5-backend-deep-dive)
6. [Infrastructure & Operations](#6-infrastructure--operations)
7. [Cross-Cutting Structure](#7-cross-cutting-structure)
8. [Clean Architecture Mapping](#8-clean-architecture-mapping)
9. [Design Decisions & Rationale](#9-design-decisions--rationale)
10. [Evolution & Scaling Strategy](#10-evolution--scaling-strategy)

---

## 1. Architectural Philosophy

### 1.1 Modular Monolith

TRUE STAR BD LIMITED adopts a **modular monolith** as its primary architectural style. This is a deliberate decision based on the following evaluation:

| Factor | Monolith | Modular Monolith | Microservices |
|---|---|---|---|
| Time to market | Fastest | Fast | Slow |
| Operational complexity | Low | Low-Medium | High |
| Team autonomy | Low | Medium | High |
| Scaling granularity | Coarse | Medium | Fine |
| Refactoring cost | High | Medium | Low |
| Cognitive load | High | Moderate | High |

**Why modular monolith for TSBL:**
- **Team size**: A lean engineering team (5-12 developers) cannot effectively manage 20+ microservices
- **Stage**: Early-stage marketplace needs rapid iteration; microservices introduce premature complexity
- **Cohesion**: The 28 modules share a unified data domain; decomposing into services would create chatty interservice communication
- **Transactionality**: Financial operations (orders, payments, escrow, wallet) require strong consistency that is costly with distributed transactions
- **Deployment**: Single deployable unit reduces CI/CD pipeline complexity and operational overhead

**When to extract modules into services:**
- When a module requires independent scaling (e.g., SRCH - Search Engine with Elasticsearch)
- When a module has different availability requirements (e.g., PAY - Payments needs 99.99% uptime)
- When a module's data volume justifies independent storage (e.g., ANL - Analytics in ClickHouse)
- When the team grows to 3+ squads and module boundaries stabilize

### 1.2 Clean Architecture Alignment

The folder structure implements a variant of **Clean Architecture** / **Hexagonal Architecture** adapted for Python FastAPI:

```
 +------------------------------------------------------------------+
 |                       adapters/                                  |
 |  (api/, repositories/, events/, tasks/, cms/)                    |
 |  +----------------------------------------------------------+   |
 |  |                   application/                            |   |
 |  |  (services/, use-cases/, dto/)                            |   |
 |  |  +---------------------------------------------------+   |   |
 |  |  |                   domain/                         |   |   |
 |  |  |  (models/, domain-services/,                      |   |   |
 |  |  |   value-objects/, exceptions/)                    |   |   |
 |  |  +---------------------------------------------------+   |   |
 |  +----------------------------------------------------------+   |
 |  +----------------------------------------------------------+   |
 |  |                   infrastructure/                        |   |
 |  |  (db/, cache/, storage/, security/,                      |   |
 |  |   messaging/, monitoring/)                               |   |
 |  +----------------------------------------------------------+   |
 +------------------------------------------------------------------+
```

**Layer mapping:**

| Clean Architecture Layer | TSBL Directory | Responsibility |
|---|---|---|
| **Domain Layer** (innermost) | `backend/app/models/`, `backend/app/services/` (domain services) | Enterprise business rules, entities, value objects, domain events |
| **Application Layer** | `backend/app/services/` (application services), `backend/app/schemas/` | Use case orchestration, DTOs, input/output port interfaces |
| **Interface Adapters** | `backend/app/api/`, `backend/app/events/`, `backend/app/tasks/` | Controllers, presenters, serializers, event subscribers |
| **Infrastructure** | `backend/app/core/`, `backend/app/repositories/` | DB access, cache, file storage, external API clients, security |

### 1.3 Naming Conventions

| Artifact | Convention | Example |
|---|---|---|
| Python files | `snake_case.py` | `product_service.py` |
| TypeScript files | `kebab-case.ts` | `use-auth.ts` |
| React components | `PascalCase.tsx` | `ProductCard.tsx` |
| Directories (modules) | `kebab-case` | `product-catalog/` |
| API versioning | `v{major}` | `/api/v1/` |
| Database tables | `snake_case` (plural) | `order_items` |
| Environment variables | `UPPER_SNAKE_CASE` | `DATABASE_URL` |

---

## 2. Complete Folder Tree

```
TSBL/
|
|-- .github/
|   |-- workflows/
|   |   |-- ci-frontend.yml
|   |   |-- ci-backend.yml
|   |   |-- cd-staging.yml
|   |   |-- cd-production.yml
|   |   |-- security-scan.yml
|   |   |-- dependency-review.yml
|   |   +-- stale-issue-management.yml
|   +-- CODEOWNERS
|
|-- frontend/                          # Next.js 14+ React application
|   |-- app/                           # App Router (pages + layouts)
|   |   |-- (auth)/                    # Route group: authentication
|   |   |   |-- login/
|   |   |   |-- register/
|   |   |   |-- forgot-password/
|   |   |   +-- oauth/
|   |   |       +-- [provider]/
|   |   |-- (marketplace)/             # Route group: public marketplace
|   |   |   |-- page.tsx              # Homepage
|   |   |   |-- search/
|   |   |   |-- categories/
|   |   |   |   +-- [slug]/
|   |   |   |-- products/
|   |   |   |   +-- [slug]/           # Product detail page
|   |   |   |-- cart/                 # Shopping cart
|   |   |   +-- checkout/             # Checkout flow
|   |   |       |-- page.tsx
|   |   |       +-- confirmation/
|   |   |-- (dashboard)/              # Route group: user dashboard
|   |   |   |-- dashboard/
|   |   |   |   |-- page.tsx
|   |   |   |   |-- orders/
|   |   |   |   |-- downloads/
|   |   |   |   |-- reviews/
|   |   |   |   +-- settings/
|   |   |   |-- seller/               # Seller dashboard
|   |   |   |   |-- page.tsx
|   |   |   |   |-- products/
|   |   |   |   |   +-- [id]/
|   |   |   |   |-- orders/
|   |   |   |   |-- analytics/
|   |   |   |   |-- payouts/
|   |   |   |   +-- settings/
|   |   |   |-- affiliate/            # Affiliate dashboard
|   |   |   |   |-- page.tsx
|   |   |   |   |-- links/
|   |   |   |   +-- earnings/
|   |   |   +-- admin/                # Admin panel
|   |   |       |-- page.tsx
|   |   |       |-- users/
|   |   |       |-- sellers/
|   |   |       |-- products/
|   |   |       |-- orders/
|   |   |       |-- disputes/
|   |   |       |-- support/
|   |   |       |-- coupons/
|   |   |       |-- cms/
|   |   |       |-- analytics/
|   |   |       |-- settings/
|   |   |       |-- audit-logs/
|   |   |       +-- roles/
|   |   |-- api/                      # API route handlers (Next.js API, optional proxy)
|   |   |-- layout.tsx                # Root layout
|   |   +-- not-found.tsx             # 404 page
|   |
|   |-- components/                   # Reusable UI components
|   |   |-- ui/                       # Primitives (atoms)
|   |   |   |-- Button.tsx
|   |   |   |-- Input.tsx
|   |   |   |-- Select.tsx
|   |   |   |-- Modal.tsx
|   |   |   |-- Toast.tsx
|   |   |   |-- Badge.tsx
|   |   |   |-- Card.tsx
|   |   |   |-- Skeleton.tsx
|   |   |   |-- Pagination.tsx
|   |   |   |-- Spinner.tsx
|   |   |   |-- Dropdown.tsx
|   |   |   |-- Tabs.tsx
|   |   |   +-- DataTable.tsx
|   |   |-- layout/                   # Layout components (molecules)
|   |   |   |-- Header.tsx
|   |   |   |-- Footer.tsx
|   |   |   |-- Sidebar.tsx
|   |   |   |-- MobileNav.tsx
|   |   |   |-- Breadcrumbs.tsx
|   |   |   +-- Container.tsx
|   |   |-- product/                  # Product domain components
|   |   |   |-- ProductCard.tsx
|   |   |   |-- ProductGrid.tsx
|   |   |   |-- ProductGallery.tsx
|   |   |   |-- ProductInfo.tsx
|   |   |   |-- VariantSelector.tsx
|   |   |   |-- PriceDisplay.tsx
|   |   |   +-- AddToCartButton.tsx
|   |   |-- cart/                     # Cart domain components
|   |   |   |-- CartItem.tsx
|   |   |   |-- CartSummary.tsx
|   |   |   +-- CartDrawer.tsx
|   |   |-- checkout/                 # Checkout domain components
|   |   |   |-- CheckoutForm.tsx
|   |   |   |-- PaymentMethodSelector.tsx
|   |   |   |-- OrderReview.tsx
|   |   |   +-- CheckoutSteps.tsx
|   |   |-- order/                    # Order domain components
|   |   |   |-- OrderCard.tsx
|   |   |   |-- OrderTimeline.tsx
|   |   |   +-- OrderStatusBadge.tsx
|   |   |-- auth/                     # Auth domain components
|   |   |   |-- LoginForm.tsx
|   |   |   |-- RegisterForm.tsx
|   |   |   |-- OAuthButtons.tsx
|   |   |   |-- MfaForm.tsx
|   |   |   +-- ResetPasswordForm.tsx
|   |   |-- seller/                   # Seller domain components
|   |   |   |-- SellerCard.tsx
|   |   |   |-- SellerRating.tsx
|   |   |   |-- ProductForm.tsx
|   |   |   |-- InventoryTable.tsx
|   |   |   +-- PayoutSettings.tsx
|   |   |-- admin/                    # Admin domain components
|   |   |   |-- DataGrid.tsx
|   |   |   |-- FilterBar.tsx
|   |   |   |-- StatusToggle.tsx
|   |   |   +-- AuditLogViewer.tsx
|   |   |-- messaging/                # Messaging components
|   |   |   |-- ConversationList.tsx
|   |   |   |-- ChatWindow.tsx
|   |   |   |-- MessageBubble.tsx
|   |   |   +-- MessageInput.tsx
|   |   |-- review/                   # Review components
|   |   |   |-- ReviewCard.tsx
|   |   |   |-- ReviewForm.tsx
|   |   |   |-- RatingStars.tsx
|   |   |   +-- ReviewSummary.tsx
|   |   |-- notification/             # Notification components
|   |   |   |-- NotificationCenter.tsx
|   |   |   +-- NotificationToast.tsx
|   |   +-- shared/                   # Shared/composite components
|   |       |-- EmptyState.tsx
|   |       |-- ErrorBoundary.tsx
|   |       |-- LoadingScreen.tsx
|   |       |-- ConfirmDialog.tsx
|   |       |-- FileUpload.tsx
|   |       |-- RichTextEditor.tsx
|   |       |-- ImagePicker.tsx
|   |       |-- SearchInput.tsx
|   |       +-- SEOHead.tsx
|   |
|   |-- lib/                          # Utilities, helpers, API client
|   |   |-- api/                      # API client layer
|   |   |   |-- client.ts            # Axios/fetch wrapper with interceptors
|   |   |   |-- auth.ts              # Auth API calls
|   |   |   |-- products.ts          # Product API calls
|   |   |   |-- orders.ts            # Order API calls
|   |   |   |-- cart.ts              # Cart API calls
|   |   |   |-- checkout.ts          # Checkout API calls
|   |   |   |-- wallet.ts            # Wallet API calls
|   |   |   |-- admin.ts             # Admin API calls
|   |   |   |-- messaging.ts         # Messaging API calls
|   |   |   |-- notifications.ts     # Notifications API calls
|   |   |   +-- affiliate.ts         # Affiliate API calls
|   |   |-- utils/                    # Utility functions
|   |   |   |-- cn.ts                # clsx + tailwind-merge utility
|   |   |   |-- format.ts            # Currency, date, number formatting
|   |   |   |-- validators.ts        # Client-side validation helpers
|   |   |   |-- debounce.ts
|   |   |   |-- throttle.ts
|   |   |   |-- url.ts               # URL manipulation helpers
|   |   |   +-- cookies.ts           # Cookie management
|   |   |-- constants/                # Application constants
|   |   |   |-- routes.ts            # Route path constants
|   |   |   |-- api-endpoints.ts     # API endpoint constants
|   |   |   |-- enums.ts             # Frontend enum values
|   |   |   +-- config.ts            # Runtime configuration
|   |   +-- websocket/                # WebSocket client
|   |       |-- client.ts
|   |       |-- useWebSocket.ts
|   |       +-- channels.ts
|   |
|   |-- hooks/                        # Custom React hooks
|   |   |-- useAuth.ts
|   |   |-- useCart.ts
|   |   |-- useDebounce.ts
|   |   |-- useIntersectionObserver.ts
|   |   |-- useMediaQuery.ts
|   |   |-- useOnClickOutside.ts
|   |   |-- usePagination.ts
|   |   |-- useSearchParams.ts
|   |   |-- useInfiniteScroll.ts
|   |   |-- useWebSocket.ts
|   |   |-- useNotifications.ts
|   |   |-- usePermissions.ts
|   |   |-- useProductSearch.ts
|   |   +-- useAsync.ts
|   |
|   |-- store/                        # State management (Zustand)
|   |   |-- authStore.ts
|   |   |-- cartStore.ts
|   |   |-- uiStore.ts               # Theme, sidebar, modals
|   |   |-- notificationStore.ts
|   |   +-- orderStore.ts
|   |
|   |-- types/                        # TypeScript type definitions
|   |   |-- api.ts                   # API response/request types
|   |   |-- auth.ts
|   |   |-- user.ts
|   |   |-- product.ts
|   |   |-- order.ts
|   |   |-- cart.ts
|   |   |-- checkout.ts
|   |   |-- payment.ts
|   |   |-- wallet.ts
|   |   |-- seller.ts
|   |   |-- messaging.ts
|   |   |-- notification.ts
|   |   |-- review.ts
|   |   |-- dispute.ts
|   |   |-- affiliate.ts
|   |   |-- admin.ts
|   |   |-- cms.ts
|   |   +-- analytics.ts
|   |
|   |-- public/                       # Static assets
|   |   |-- images/
|   |   |   |-- logo.svg
|   |   |   |-- favicon.ico
|   |   |   |-- og-image.png
|   |   |   +-- placeholders/
|   |   |-- fonts/
|   |   |-- manifest.json
|   |   +-- robots.txt
|   |
|   |-- styles/                       # Global styles
|   |   |-- globals.css              # Tailwind directives + CSS variables
|   |   +-- fonts.css
|   |
|   +-- __tests__/                    # Frontend tests
|       |-- components/
|       |-- hooks/
|       |-- lib/
|       |-- e2e/
|       +-- setup.ts
|
|-- backend/                          # Python FastAPI backend
|   |-- app/
|   |   |-- __init__.py
|   |   |-- main.py                   # FastAPI application factory
|   |   |
|   |   |-- api/                      # Route handlers (interface adapters)
|   |   |   |-- __init__.py
|   |   |   |-- deps.py               # Dependency injection (FastAPI Depends)
|   |   |   +-- v1/                   # API version 1
|   |   |       |-- __init__.py
|   |   |       |-- router.py         # Aggregated router
|   |   |       |-- auth.py
|   |   |       |-- users.py
|   |   |       |-- sellers.py
|   |   |       |-- products.py
|   |   |       |-- search.py
|   |   |       |-- cart.py
|   |   |       |-- checkout.py
|   |   |       |-- orders.py
|   |   |       |-- delivery.py
|   |   |       |-- wallet.py
|   |   |       |-- escrow.py
|   |   |       |-- payments.py
|   |   |       |-- withdrawals.py
|   |   |       |-- coupons.py
|   |   |       |-- affiliates.py
|   |   |       |-- messaging.py
|   |   |       |-- notifications.py
|   |   |       |-- reviews.py
|   |   |       |-- disputes.py
|   |   |       |-- support.py
|   |   |       |-- analytics.py
|   |   |       |-- cms.py
|   |   |       |-- admin.py
|   |   |       |-- audit.py
|   |   |       +-- settings.py
|   |   |
|   |   |-- core/                     # Core infrastructure
|   |   |   |-- __init__.py
|   |   |   |-- config.py            # Pydantic Settings (env vars)
|   |   |   |-- security.py          # JWT, password hashing, encryption
|   |   |   |-- database.py          # Engine, session factory
|   |   |   |-- cache.py             # Redis client
|   |   |   |-- storage.py           # S3/MinIO client
|   |   |   |-- celery_app.py        # Celery instance
|   |   |   |-- logging.py           # Logger configuration
|   |   |   |-- exceptions.py        # Global exception classes
|   |   |   |-- middleware.py        # Custom ASGI middleware
|   |   |   |-- rate_limiter.py      # Rate limiting logic
|   |   |   |-- event_bus.py         # Internal event dispatcher
|   |   |   +-- dependencies.py      # FastAPI dependency providers
|   |   |
|   |   |-- models/                   # SQLAlchemy ORM models (domain entities)
|   |   |   |-- __init__.py
|   |   |   |-- base.py              # Declarative base, mixins
|   |   |   |-- user.py              # User, UserProfile, UserPreference
|   |   |   |-- auth.py              # AuthCredential, AuthSession, AuthMfaMethod
|   |   |   |-- role.py              # Role, Permission, RolePermission, UserRole
|   |   |   |-- seller.py            # Seller, SellerVerification, SellerProfile
|   |   |   |-- product.py           # Product, ProductVariant, ProductMedia
|   |   |   |-- category.py          # Category, Collection, FeaturedSlot
|   |   |   |-- cart.py              # Cart, CartItem, CartCoupon
|   |   |   |-- checkout.py          # CheckoutSession, CheckoutPayment
|   |   |   |-- order.py             # Order, OrderItem, OrderStatusHistory
|   |   |   |-- delivery.py          # DeliveryRecord, DeliveryFile
|   |   |   |-- wallet.py            # Wallet, WalletTransaction, WalletHold
|   |   |   |-- escrow.py            # EscrowTransaction, EscrowRelease
|   |   |   |-- payment.py           # PaymentTransaction, PaymentIntent
|   |   |   |-- withdrawal.py        # WithdrawalRequest, WithdrawalMethod
|   |   |   |-- coupon.py            # Coupon, CouponRedemption, CouponScope
|   |   |   |-- affiliate.py         # Affiliate, AffiliateLink, AffiliateConversion
|   |   |   |-- messaging.py         # Conversation, Message
|   |   |   |-- notification.py      # Notification, NotificationPreference
|   |   |   |-- review.py            # Review, ReviewHelpfulVote
|   |   |   |-- dispute.py           # Dispute, DisputeEvidence, DisputeResolution
|   |   |   |-- support.py           # SupportTicket, TicketMessage
|   |   |   |-- cms.py               # CmsPage, CmsMedia, CmsContentBlock
|   |   |   |-- analytics.py         # AnalyticsDashboard, ScheduledReport
|   |   |   |-- audit.py             # AuditLog
|   |   |   +-- setting.py           # Setting, FeatureFlag
|   |   |
|   |   |-- schemas/                  # Pydantic request/response schemas
|   |   |   |-- __init__.py
|   |   |   |-- common.py            # Pagination, ErrorResponse, SuccessResponse
|   |   |   |-- auth.py
|   |   |   |-- user.py
|   |   |   |-- seller.py
|   |   |   |-- product.py
|   |   |   |-- cart.py
|   |   |   |-- checkout.py
|   |   |   |-- order.py
|   |   |   |-- delivery.py
|   |   |   |-- wallet.py
|   |   |   |-- escrow.py
|   |   |   |-- payment.py
|   |   |   |-- withdrawal.py
|   |   |   |-- coupon.py
|   |   |   |-- affiliate.py
|   |   |   |-- messaging.py
|   |   |   |-- notification.py
|   |   |   |-- review.py
|   |   |   |-- dispute.py
|   |   |   |-- support.py
|   |   |   |-- analytics.py
|   |   |   |-- cms.py
|   |   |   |-- admin.py
|   |   |   |-- audit.py
|   |   |   +-- setting.py
|   |   |
|   |   |-- services/                 # Business logic layer
|   |   |   |-- __init__.py
|   |   |   |-- auth_service.py
|   |   |   |-- user_service.py
|   |   |   |-- seller_service.py
|   |   |   |-- product_service.py
|   |   |   |-- category_service.py
|   |   |   |-- search_service.py
|   |   |   |-- cart_service.py
|   |   |   |-- checkout_service.py
|   |   |   |-- order_service.py
|   |   |   |-- delivery_service.py
|   |   |   |-- wallet_service.py
|   |   |   |-- escrow_service.py
|   |   |   |-- payment_service.py
|   |   |   |-- withdrawal_service.py
|   |   |   |-- coupon_service.py
|   |   |   |-- affiliate_service.py
|   |   |   |-- messaging_service.py
|   |   |   |-- notification_service.py
|   |   |   |-- review_service.py
|   |   |   |-- dispute_service.py
|   |   |   |-- support_service.py
|   |   |   |-- analytics_service.py
|   |   |   |-- cms_service.py
|   |   |   |-- admin_service.py
|   |   |   |-- audit_service.py
|   |   |   +-- setting_service.py
|   |   |
|   |   |-- repositories/             # Data access layer (repository pattern)
|   |   |   |-- __init__.py
|   |   |   |-- base.py              # Generic SQLAlchemy repository
|   |   |   |-- user_repository.py
|   |   |   |-- auth_repository.py
|   |   |   |-- role_repository.py
|   |   |   |-- seller_repository.py
|   |   |   |-- product_repository.py
|   |   |   |-- category_repository.py
|   |   |   |-- cart_repository.py
|   |   |   |-- checkout_repository.py
|   |   |   |-- order_repository.py
|   |   |   |-- delivery_repository.py
|   |   |   |-- wallet_repository.py
|   |   |   |-- escrow_repository.py
|   |   |   |-- payment_repository.py
|   |   |   |-- withdrawal_repository.py
|   |   |   |-- coupon_repository.py
|   |   |   |-- affiliate_repository.py
|   |   |   |-- messaging_repository.py
|   |   |   |-- notification_repository.py
|   |   |   |-- review_repository.py
|   |   |   |-- dispute_repository.py
|   |   |   |-- support_repository.py
|   |   |   |-- analytics_repository.py
|   |   |   |-- cms_repository.py
|   |   |   |-- audit_repository.py
|   |   |   +-- setting_repository.py
|   |   |
|   |   |-- tasks/                    # Celery async tasks
|   |   |   |-- __init__.py
|   |   |   |-- celery_app.py
|   |   |   |-- email_tasks.py
|   |   |   |-- delivery_tasks.py
|   |   |   |-- notification_tasks.py
|   |   |   |-- report_tasks.py
|   |   |   |-- maintenance_tasks.py
|   |   |   |-- payout_tasks.py
|   |   |   |-- index_tasks.py
|   |   |   |-- escrow_tasks.py
|   |   |   +-- affiliate_tasks.py
|   |   |
|   |   |-- events/                   # Event handlers / subscribers
|   |   |   |-- __init__.py
|   |   |   |-- handler.py            # Base event handler interface
|   |   |   |-- user_events.py
|   |   |   |-- order_events.py
|   |   |   |-- payment_events.py
|   |   |   |-- delivery_events.py
|   |   |   |-- review_events.py
|   |   |   |-- dispute_events.py
|   |   |   |-- notification_events.py
|   |   |   +-- analytics_events.py
|   |   |
|   |   |-- ws/                       # WebSocket handlers
|   |   |   |-- __init__.py
|   |   |   |-- manager.py            # Connection manager
|   |   |   |-- auth.py               # WS authentication
|   |   |   +-- handlers/
|   |   |       |-- chat.py
|   |   |       +-- notifications.py
|   |   |
|   |   +-- __init__.py
|   |
|   |-- migrations/                   # Alembic database migrations
|   |   |-- env.py
|   |   |-- alembic.ini
|   |   +-- versions/
|   |
|   |-- tests/                        # Backend tests
|   |   |-- __init__.py
|   |   |-- conftest.py              # Fixtures, factories
|   |   |-- api/
|   |   |-- services/
|   |   |-- repositories/
|   |   |-- tasks/
|   |   |-- fixtures/
|   |   |-- mocks/
|   |   +-- e2e/
|   |
|   |-- alembic.ini
|   |-- pyproject.toml
|   |-- Dockerfile
|   +-- .env.example
|
|-- docker/                           # Docker configurations
|   |-- docker-compose.yml
|   |-- docker-compose.staging.yml
|   |-- docker-compose.prod.yml
|   |-- docker-compose.monitoring.yml
|   |-- nginx/
|   |   +-- default.conf
|   +-- logrotate/
|       +-- docker-container.conf
|
|-- k8s/                              # Kubernetes manifests
|   |-- base/
|   |   |-- kustomization.yaml
|   |   |-- namespace.yaml
|   |   |-- deployment.yaml
|   |   |-- service.yaml
|   |   |-- ingress.yaml
|   |   |-- configmap.yaml
|   |   |-- secrets.yaml
|   |   +-- hpa.yaml
|   |-- overlays/
|   |   |-- staging/
|   |   |   |-- kustomization.yaml
|   |   |   +-- patches.yaml
|   |   +-- production/
|   |       |-- kustomization.yaml
|   |       +-- patches.yaml
|   +-- helm/
|       +-- tsbl/
|
|-- scripts/                          # Utility scripts
|   |-- setup-dev.sh
|   |-- seed-db.py
|   |-- migrate.sh
|   |-- backup-db.sh
|   |-- restore-db.sh
|   |-- lint.sh
|   |-- test.sh
|   |-- deploy-staging.sh
|   |-- deploy-production.sh
|   +-- healthcheck.sh
|
|-- docs/                             # Project documentation
|   |-- 01-srs/
|   |   |-- 01-introduction.md
|   |   |-- 02-module-breakdown.md
|   |   +-- 03-folder-structure.md
|   |-- 02-requirements/
|   |-- 03-workflows/
|   |   |-- buyer-journey.md
|   |   |-- seller-journey.md
|   |   +-- order-fulfillment.md
|   |-- 04-architecture/
|   |   |-- adr-001-monorepo.md
|   |   |-- adr-002-modular-monolith.md
|   |   |-- adr-003-python-fastapi.md
|   |   |-- adr-004-postgresql.md
|   |   +-- adr-005-event-driven.md
|   |-- 05-security/
|   |   |-- threat-model.md
|   |   |-- data-classification.md
|   |   +-- security-controls.md
|   |-- 06-deployment/
|   |   |-- ci-cd-pipeline.md
|   |   |-- environment-setup.md
|   |   +-- runbook.md
|   |-- 07-strategies/
|   |   |-- scalability-strategy.md
|   |   |-- disaster-recovery.md
|   |   +-- monitoring-strategy.md
|   +-- 08-development/
|       |-- coding-standards.md
|       |-- api-conventions.md
|       |-- database-conventions.md
|       +-- contributor-guide.md
|
|-- .gitignore
|-- .pre-commit-config.yaml
|-- .editorconfig
|-- .env.example
|-- Makefile
|-- README.md
+-- AGENTS.md
```

---

## 3. Top-Level Directories

### 3.1 `.github/` — CI/CD and Repository Automation

**Purpose:** Define all continuous integration, continuous delivery, and repository management automation.

**Architectural decisions:**
- **Separate CI workflows per stack** — Frontend and backend have independent pipelines because their toolchains (Node.js vs Python), test runners (Jest vs Pytest), and build outputs differ
- **Security scanning as a gated step** — `security-scan.yml` runs Snyk/Trivy/Dependabot before deployment; failed scans block the pipeline
- **CODEOWNERS** — Enforces code review requirements per directory (`frontend/` owned by frontend team, `backend/` by backend team)

### 3.2 `frontend/` — Next.js Application

**Purpose:** Server-side rendered React application with App Router, TypeScript, and TailwindCSS.

**Architectural decisions:**
- **Route groups `(auth)`, `(marketplace)`, `(dashboard)`** — Organize routes by domain without affecting URL structure; each group can have its own layout
- **Component categorization by domain** — `components/product/`, `components/cart/` etc. keep domain logic co-located; mirrors backend module structure for cognitive alignment
- **Store directory** — Zustand over Redux for lower boilerplate; stores are module-specific (authStore, cartStore) not monolithic
- **Types directory** — Mirrors backend schemas one-to-one; types auto-generated from OpenAPI spec via `openapi-typescript`
- **API client layer** — Centralized `lib/api/` with interceptors for auth token injection, error handling, and request retry

### 3.3 `backend/` — Python FastAPI Application

**Purpose:** RESTful API server following Clean Architecture principles with SQLAlchemy ORM, Pydantic validation, and Celery async task processing.

**Architectural decisions:**
- **Layered structure** — `api/ -> services/ -> repositories/ -> models/` enforces dependency inversion: inner layers know nothing about outer layers
- **Versioned API (`v1/`)** — Enables backward-compatible evolution; v1 endpoints are stable while v2 can be developed alongside
- **One file per module per layer** — Each module appears in exactly one file per layer (e.g., `api/v1/products.py`, `services/product_service.py`, `repositories/product_repository.py`); this prevents merge conflicts and clarifies ownership
- **Repository pattern** — Abstracts SQLAlchemy behind interfaces; enables unit testing with in-memory repositories and future migration to different storage
- **Event bus** — Internal `event_bus.py` dispatches domain events synchronously within the process; extractable to Kafka/RabbitMQ when moving to microservices

### 3.4 `docker/` — Containerization

**Purpose:** Docker Compose configurations for local development, staging, and production environments.

**Architectural decisions:**
- **Multi-stage Dockerfiles** — `python:3.12-slim` with separate build and runtime stages for minimal image size
- **Compose profiles** — `docker compose --profile monitoring up` for observability stack without cluttering dev environment
- **Nginx reverse proxy** — Handles SSL termination, static file serving, and rate limiting before requests reach the app

### 3.5 `k8s/` — Kubernetes Manifests

**Purpose:** Production orchestration with Kustomize overlays for environment-specific customization.

**Architectural decisions:**
- **Kustomize over Helm** — Simpler for a monorepo with few environments; avoids Chart template complexity
- **Sealed Secrets** — Secrets encrypted and committed to git; only decryptable inside the cluster
- **HPA** — Horizontal Pod Autoscaler based on CPU/memory and custom metrics (request latency, queue depth)
- **Base + overlays** — Single source of truth for deployment specs; overlays add environment-specific patches

### 3.6 `scripts/` — Automation

**Purpose:** Developer productivity and operational scripts that do not belong in CI/CD pipelines.

**Architectural decisions:**
- **Shell scripts for infrastructure** — backup-db.sh, deploy-production.sh are operational; bash is the universal scripting language for ops
- **Python scripts for data tasks** — seed-db.py benefits from Python's ORM access and data libraries
- **Makefile as task runner** — Common commands (`make dev`, `make test`, `make lint`) abstract away the underlying tooling

### 3.7 `docs/` — Documentation

**Purpose:** Living documentation organized by architecture concern, not by authoring tool.

**Architectural decisions:**
- **Numbered directories** — Prefixes enforce rendering order in IDE file explorers; 01 is SRS, 08 is development guides
- **ADR directory** — Architecture Decision Records capture why decisions were made, not just what was decided
- **Separation of concerns** — Security docs in 05-security/ are not mixed with deployment docs in 06-deployment/

---

## 4. Frontend Deep Dive

### 4.1 `app/` — App Router Structure

The Next.js App Router uses a **file-system based routing** paradigm where directories become route segments and special files (page.tsx, layout.tsx, loading.tsx, error.tsx) define the UI.

**Route groups** (parenthesized directories) organize routes without affecting the URL:
- `(auth)/` — Authentication flows (login, register, password reset)
- `(marketplace)/` — Public-facing marketplace pages (home, search, product, cart, checkout)
- `(dashboard)/` — Authenticated user areas (user dashboard, seller panel, affiliate panel, admin panel)

Each route group can have its own layout.tsx, enabling:
- `(auth)/layout.tsx` — Minimal layout (no header/footer) for login/register pages
- `(marketplace)/layout.tsx` — Full public layout with header, footer, search bar
- `(dashboard)/layout.tsx` — Dashboard layout with sidebar navigation

### 4.2 `components/` — Component Architecture

Components follow **Atomic Design** principles adapted for React:

| Level | Directory | Description | Examples |
|---|---|---|---|
| Atoms | `components/ui/` | Generic, reusable primitives | Button, Input, Modal, Badge |
| Molecules | `components/layout/` | Composed atoms for structure | Header, Sidebar, Breadcrumbs |
| Organisms | `components/{domain}/` | Domain-specific composite components | ProductCard, CartSummary, ChatWindow |
| Templates | `components/shared/` | Cross-domain shared composites | DataTable, FileUpload, RichTextEditor |

**Component contract:** Every component accepts a typed Props interface, uses TailwindCSS for styling, and handles loading/error/empty states.

### 4.3 `lib/` — Client-Side Logic

**API client layer** (lib/api/client.ts):
- Axios instance with base URL, interceptors for token injection, 401 handling (auto-refresh), and request retry
- Per-module API files (products.ts, orders.ts) provide typed functions that call the backend
- All API calls go through the client; no raw fetch calls outside lib/api/

**WebSocket client** (lib/websocket/):
- Singleton connection manager with auto-reconnect (exponential backoff)
- Channel-based subscription model: client subscribes to specific channels (e.g., chat:conversation-123, notifications:user-456)
- Fallback to polling when WebSocket connection fails

### 4.4 `hooks/` — Custom Hooks

Hooks encapsulate reusable stateful logic:
- **Authentication**: useAuth() — login, logout, session check, permission check
- **Data fetching**: useProductSearch() — debounced search with pagination
- **UI state**: useMediaQuery(), useIntersectionObserver(), useOnClickOutside()
- **Real-time**: useWebSocket(), useNotifications()

Hooks never access the store directly; they return state and actions that consumers use.

### 4.5 `store/` — State Management

Zustand stores are:
- **Module-scoped** — Each store manages a single domain concern (auth, cart, UI, notifications)
- **Persisted selectively** — authStore persisted to localStorage (tokens), cartStore to IndexedDB, uiStore ephemeral
- **Type-safe** — Full TypeScript inference with no action type constants

**State vs server state:** Zustand manages client state (UI state, temporary selections, optimistic updates). Server state (products, orders) is fetched via React Query (TanStack Query) and cached; not duplicated in Zustand.

### 4.6 `types/` — TypeScript Definitions

Types are **auto-generated** from the backend's OpenAPI schema using openapi-typescript. Generation runs:
- On `npm run dev` (watch mode)
- On `npm run build` (as a pre-build step)
- On pre-commit hook (if schema changed)

Manual override types are stored for form-specific input types, component-only prop types, and utility types (PaginatedResponse, ApiError).

---

## 5. Backend Deep Dive

### 5.1 `api/` — Interface Adapters (Controllers)

**Responsibility:** Handle HTTP requests, validate input, call services, format responses.

**Structure:**
- `api/v1/` — Versioned endpoint handlers
- `api/deps.py` — FastAPI Depends() callables for common injections (current user, DB session, permission checker)

**Pattern per endpoint:**
```
GET /products/{slug} -> service.get_by_slug(slug, user) -> ProductResponse
```

**Why one file per module:**
- Each file contains all routes for a module; route prefix defined at router level
- File length stays manageable (typically 50-150 lines for CRUD + 3-5 custom endpoints)
- Avoids deep nesting like `api/v1/products/read.py`, `api/v1/products/write.py`

### 5.2 `core/` — Infrastructure Core

**Responsibility:** Cross-cutting infrastructure concerns.

| File | Responsibility |
|---|---|
| config.py | Pydantic BaseSettings from environment; validated at startup |
| security.py | JWT creation/verification, password hashing (bcrypt), field encryption (AES-256-GCM) |
| database.py | SQLAlchemy AsyncEngine, AsyncSessionFactory, health check |
| cache.py | Redis client (sync for Celery, async for FastAPI), connection pooling |
| storage.py | S3-compatible storage abstraction (MinIO dev, AWS S3 prod) |
| celery_app.py | Celery app configured from config.py |
| exceptions.py | Application exception hierarchy mapped to HTTP status codes |
| middleware.py | Request ID, correlation ID, request timing, CORS |
| rate_limiter.py | Token bucket algorithm backed by Redis |
| event_bus.py | In-process pub/sub with async handlers |
| dependencies.py | FastAPI dependency providers for all external services |

### 5.3 `models/` — Domain Entities (SQLAlchemy)

**Base mixins** (models/base.py):
- TimestampMixin: created_at, updated_at
- SoftDeleteMixin: deleted_at + is_deleted property
- VersionMixin: version integer for optimistic locking
- UUIDPrimaryKey: UUID primary key with auto-generation

**Naming conventions:**
- Table name: snake_case plural (order_items)
- Primary key: id (UUID)
- Foreign key: {referenced_table_singular}_id (order_id)
- Indexes: named `ix_{table}_{column}`; unique constraints named `uq_{table}_{columns}`

**Relationship patterns:**
- Bidirectional relationships defined explicitly on both sides
- lazy="selectin" for common relationships, lazy="raise" for expensive/rare joins
- Soft-delete applied at query level via `where(deleted_at.is_(None))` filter

### 5.4 `schemas/` — Pydantic Models

**Three categories per module:**
1. **Request schemas** — ProductCreateRequest, ProductUpdateRequest — validated on input
2. **Response schemas** — ProductResponse, ProductListResponse — serialized on output
3. **Internal schemas** — ProductFilterParams — used within services

**Key decisions:**
- Schemas are strict: Extra.forbid prevents unexpected fields
- Response schemas use model_validate not model_dump to ensure type safety
- Sensitive fields (passwords, tokens) use Field(exclude=True) on response schemas
- Pagination uses a generic PaginatedResponse generic schema

### 5.5 `services/` — Business Logic

**Two service layers collapsed into one directory:**

| Service Type | Responsibility | Example |
|---|---|---|
| **Domain Service** | Business rules, calculations, validations | EscrowService.release() checks delivery confirmation, computes commission |
| **Application Service** | Orchestration, transaction management, cross-module coordination | CheckoutService.place_order() calls cart, coupon, payment, wallet, order services |

**Service pattern:**
- Services depend on abstractions (repositories, other services, event bus), not on infrastructure
- Transaction boundary managed via Unit of Work pattern (one session per service call)
- Services raise domain exceptions defined in core/exceptions.py
- Services are stateless; all state passed as parameters

### 5.6 `repositories/` — Data Access

**Base repository** (repositories/base.py) provides: get, list, create, update, delete.

**Key decisions:**
- Repositories return domain entities, not dicts
- Repositories do not commit transactions (Unit of Work handles commit/rollback)
- Complex queries use selectinload for eager loading; never lazy load outside session
- Read-only reporting queries use a separate read replica when available

### 5.7 `tasks/` — Async Task Processing

**Task categories and priority queues:**

| Category | Tasks | Priority Queue |
|---|---|---|
| Real-time (<10s) | Email sending, push notifications | `celery -Q realtime` |
| Normal (<5 min) | File processing, index updates | `celery -Q default` |
| Batch (hourly) | Report generation, payouts | `celery -Q batch` |
| Maintenance (daily) | Cleanup, aggregation, backup | `celery -Q maintenance` |

**Key decisions:**
- Tasks are idempotent (can be retried safely)
- Task result stored in Redis result backend with TTL
- Dead-letter queue for failed tasks after max retries

### 5.8 `events/` — Event Handlers

**Pattern:**
- Handlers are synchronous within the process (same transaction for critical handlers)
- Cross-module handlers call other module's services (not repositories directly)
- Handlers that interact with external systems (email, SMS) enqueue Celery tasks
- Event schema defined as Pydantic models

### 5.9 `ws/` — WebSocket Handlers

**Channels:**
- chat:{conversation_id} — Real-time messaging
- notifications:{user_id} — Real-time push notifications
- order:{order_id} — Order status updates (admin/seller)

**Key decisions:**
- WebSocket authentication via token in connection query parameter
- Redis pub/sub for horizontal scaling (multiple app instances)
- Connection manager tracks active connections per user

---

## 6. Infrastructure & Operations

### 6.1 Database Strategy

| Database | Use Case | Data |
|---|---|---|
| **PostgreSQL 16** | Primary OLTP store | All transactional data (users, orders, products, wallets) |
| **Redis 7** | Cache + Pub/Sub + Task Queue | Session data, rate limits, real-time messaging, Celery broker |
| **Elasticsearch 8** | Full-text search | Product, seller, content search indices |
| **ClickHouse** | Analytics | Event stream, aggregated metrics, reporting data |
| **MinIO / S3** | Object storage | Product files, user avatars, delivery assets, backups |

### 6.2 Celery Task Queue Architecture

App -> Redis (broker) -> realtime/default/batch/maintenance queues -> Workers -> PostgreSQL/S3/SES

### 6.3 Monitoring Stack

| Component | Tool | Purpose |
|---|---|---|
| Metrics | Prometheus + Grafana | System metrics, business KPIs |
| Logging | Loki + Promtail | Centralized log aggregation |
| Tracing | OpenTelemetry + Jaeger | Distributed tracing (future microservices) |
| Alerting | Alertmanager + PagerDuty | Incident notification |
| APM | Sentry | Error tracking and performance monitoring |
| Uptime | UptimeRobot / Pingdom | External availability monitoring |

### 6.4 CI/CD Pipeline

```
Commit -> Lint (ruff, mypy, ESLint, Prettier)
       -> Test (pytest, Jest)
       -> Build (Docker image)
       -> Security Scan (Snyk, Trivy)
       -> Deploy to Staging
       -> Integration Tests (Playwright)
       -> Approval Gate (manual)
       -> Deploy to Production (blue-green)
       -> Smoke Tests
       -> Rollback if failed
```

---

## 7. Cross-Cutting Structure

### 7.1 Configuration Management

| Layer | Source | Precedence |
|---|---|---|
| Defaults | backend/app/core/config.py | Lowest |
| Environment | .env files | Medium |
| Secrets | Vault / AWS Secrets Manager | Highest |
| Runtime | SET module (DB-backed) | Overrides env |

### 7.2 Error Handling Strategy

```
API Layer (FastAPI exception handlers)
  -> Application Layer (services raise typed exceptions)
    -> Domain Layer (models validate invariants)
      -> Infrastructure Layer (DB/network errors wrapped)
```

**Exception hierarchy:**
- AppException (base)
  - NotFoundException -> 404
  - ValidationException -> 422
  - ConflictException -> 409
  - UnauthorizedException -> 401
  - ForbiddenException -> 403
  - RateLimitException -> 429
  - PaymentRequiredException -> 402
  - ServiceUnavailableException -> 503

### 7.3 Logging Strategy

| Level | What | Destination |
|---|---|---|
| ERROR | Unhandled exceptions, payment failures, security events | Sentry + Loki |
| WARNING | Validation failures, rate limit hits, retry attempts | Loki |
| INFO | Business events (order created, user registered) | Loki + ClickHouse |
| DEBUG | Request/response payloads (development only) | Console |

### 7.4 Testing Strategy

| Layer | Tool | Scope | Frequency |
|---|---|---|---|
| Unit | Pytest (backend), Jest (frontend) | Functions, services, hooks | Per commit |
| Integration | Pytest + TestClient | API endpoints with test DB | Per commit |
| Repository | Pytest + test DB | SQL queries, ORM mappings | Per commit |
| E2E | Playwright | Critical user journeys (checkout, registration) | Per PR |
| Load | Locust / k6 | Performance benchmarks | Per release |

---

## 8. Clean Architecture Mapping

### 8.1 Dependency Rule

Dependencies point **inward**: outer layers depend on inner layers, never the reverse.

```
infrastructure/ -> repositories/ -> services/ -> models/
     (outer)                                   (inner)
```

**Enforcement:**
- repositories/ imports from models/ only
- services/ imports from repositories/, models/, and schemas/ only
- api/ imports from services/, schemas/, and core/ only
- core/ is dependency-free (except standard library + third-party SDKs)
- Enforced via import-linter (Python) and ESLint import/no-restricted-paths (TS)

### 8.2 Module Boundaries

Each module is a **bounded context** with:
- api/v1/{module}.py <- Interface Adapter (HTTP)
- services/{module}_service.py <- Application / Domain Service
- repositories/{module}_repository.py <- Data Access
- models/{module}.py <- Domain Entity
- schemas/{module}.py <- DTOs

**Module interaction rules:**
- Modules communicate only through services, never directly through repositories
- Cross-module calls go through the service layer (order_service calls wallet_service)
- Event-driven communication for non-critical path (e.g., order.created -> notification_service)

### 8.3 Dependency Injection

FastAPI's Depends provides automatic dependency injection:
```
api/v1/products.py
  -> Depends(get_product_service)
    -> ProductService(repo=Depends(get_product_repository),
                      event_bus=Depends(get_event_bus))
      -> ProductRepository(session=Depends(get_session))
```

This chain makes unit testing trivial: replace get_session with a test session, get_event_bus with a mock.

---

## 9. Design Decisions & Rationale

### 9.1 Why FastAPI over Django REST Framework?

| Criteria | FastAPI | DRF |
|---|---|---|
| Performance | Async-native, top-tier | Sync, adequate |
| Type safety | Pydantic + mypy | Serializers, less strict |
| OpenAPI docs | Automatic, interactive | Manual configuration |
| WebSocket support | Native | Channels (separate package) |
| Dependency injection | Built-in Depends | Manual |

**Decision:** FastAPI's async-first design aligns with the marketplace's I/O-heavy workload (DB queries, external API calls, file streaming). Automatic OpenAPI generation enables frontend type generation.

### 9.2 Why Next.js App Router over React SPA?

| Criteria | Next.js App Router | React SPA (Vite/CRA) |
|---|---|---|
| SEO | SSR + SSG + ISR | CSR only (poor SEO) |
| Performance | Streaming, partial rendering | Full bundle download |
| Routing | File-system based | Manual react-router |
| Data fetching | Server Components, RSC | Client-side only |
| Marketplace relevance | Product pages need SEO | Inadequate for marketplace |

**Decision:** Product listing pages require search engine indexing. Next.js SSR provides first-contentful-paint in < 1 second vs 3-5 seconds for CSR.

### 9.3 Why PostgreSQL over MongoDB?

The marketplace is **highly relational**: orders have items, items have products, products have sellers, sellers have wallets, wallets have transactions. PostgreSQL's relational model, JSONB for flexible attributes, and ACID compliance make it the right choice.

### 9.4 Why Celery over Redis Queue / SQS?

Celery provides task prioritization, retry with backoff, rate limiting, scheduled tasks (Celery Beat), task result storage, and monitoring (Flower). For the marketplace's heterogeneous task landscape (from <1s email sends to >1h report generation), Celery with multiple queues is appropriate.

### 9.5 Why Zustand over Redux?

Redux introduces boilerplate (actions, reducers, types, selectors, middleware) unnecessary for a team of this size. Zustand provides the same capabilities with zero boilerplate, full TypeScript inference, and a simpler mental model.

### 9.6 Why Modular Monolith over Microservices?

See Section 1.1 for detailed reasoning. Premature microservices would slow development by 2-3x without providing benefits that the current team size and traffic volume require.

---

## 10. Evolution & Scaling Strategy

### 10.1 Phase 1: Modular Monolith (Current)

- Single deployment unit (Docker container)
- All modules in one process
- Shared PostgreSQL database
- Internal event bus for module communication
- **Target throughput:** 10,000 concurrent users, 100 orders/minute

### 10.2 Phase 2: Read Model Extraction

**Trigger:** Analytics queries impact transactional performance.

**Action:** Extract ANL module to a separate service with its own ClickHouse database.

**Change:** Analytics events published to Kafka instead of internal event bus.

### 10.3 Phase 3: Search Extraction

**Trigger:** Search latency SLA requires dedicated resources.

**Action:** Extract SRCH module to separate service with dedicated Elasticsearch cluster.

**Change:** Product lifecycle events published to Kafka consumed by search service.

### 10.4 Phase 4: Payment Extraction

**Trigger:** PCI DSS compliance scope or payment gateway slot requirements.

**Action:** Extract PAY module to separate service with isolated deployment.

**Change:** Payment service communicates via gRPC; PCI DSS scope limited to payment service.

### 10.5 Phase 5: Full Microservices

**Trigger:** Team grows to 3+ squads and module boundaries stabilize.

**Action:** Extract modules into services by bounded context:
- Identity Service (AUTH + USR + RBAC)
- Marketplace Service (CAT + MKT + CART + SRCH)
- Ordering Service (CHK + ORD + DEL + ESC)
- Financial Service (WAL + PAY + WDR)
- Communication Service (MSG + NOT + SUP)
- Analytics Service (ANL)
- Content Service (CMS)
- Admin Gateway (ADM — BFF pattern)

**Infrastructure changes:**
- Internal event bus -> Kafka event stream
- Shared database -> Database per service
- In-process calls -> gRPC for synchronous, Kafka for asynchronous
- API Gateway for external routing
- Distributed tracing (OpenTelemetry)
- Saga pattern for distributed transactions

---

*End of Document — Folder Structure & Architectural Rationale v1.0*
