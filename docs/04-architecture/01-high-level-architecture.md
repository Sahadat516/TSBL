# High-Level Architecture — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-HL-001 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Principal Software Architect |
| **Date** | 2026-07-01 |
| **Approver** | CTO / Engineering Lead |

---

## 1. System Context Diagram (C4 — Level 1)

The following text-based diagram illustrates the TSBL digital marketplace as a black-box system interacting with external actors.

```
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                          [End Customer]                                     │
  │                     (Buyer / Shopper / Visitor)                              │
  └──────────────────────────┬──────────────────────────────────────────────────┘
                             │ browses, searches, orders, pays
                             ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                    │
│                    ┌────────────────────────────────────────┐                      │
│                    │         TSBL Digital Marketplace        │                      │
│                    │          (Software System)              │                      │
│                    │                                          │                     │
│                    │  [Web App]    [API Gateway]   [Admin UI] │                     │
│                    │  [Core Engine] [Payment Proc] [Search]   │                     │
│                    │  [Notification] [Analytics] [Auth]      │                     │
│                    └────────────────────────────────────────┘                      │
│                                                                                    │
└──────┬──────────────────────────┬──────────────────────────────┬───────────────────┘
       │                          │                              │
       ▼                          ▼                              ▼
┌──────────────┐       ┌──────────────────┐          ┌──────────────────┐
│ [Vendor]      │       │ [Payment Gateway] │          │ [Third-Party]    │
│ (Seller/      │       │ (SSLCommerz /     │          │ (Email, SMS,     │
│  Merchant)    │       │  bKash / Stripe)  │          │  Logistics API)  │
└──────────────┘       └──────────────────┘          └──────────────────┘
```

### 1.1 External Actors

| Actor | Description |
|---|---|
| **End Customer** | Registers, browses products, places orders, makes payments, tracks shipments |
| **Vendor / Seller** | Manages product listings, processes orders, views analytics |
| **Admin / Staff** | Manages platform configuration, user moderation, dispute resolution |
| **Payment Gateway** | External PSP — SSLCommerz, bKash, Stripe, Nagad |
| **Third-Party Services** | Email (SMTP/SES), SMS (Twilio/GreenWeb), Logistics (SteadFast, RedX, eCourier), OTP providers |

---

## 2. Container Diagram (C4 — Level 2)

```
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                        [Browser]                                                      │
 │                              Next.js SPA (React) + SSR                                                │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                    HTTPS (REST + WebSocket)
                                          │
                                          ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                              [Nginx / Traefik Reverse Proxy]                                          │
 │                              SSL Termination + Rate Limiting + CORS                                    │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                              [FastAPI Application Server]                                             │
 │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
 │  │ Auth     │ │ Catalog  │ │ Cart &   │ │ Order &  │ │ Payment  │ │ Vendor   │ │ Admin    │         │
 │  │ Module   │ │ Module   │ │ Checkout │ │ Fulfill  │ │ Module   │ │ Module   │ │ Module   │         │
 │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
 │                                                                                                      │
 │  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐    │
 │  │  Shared Infrastructure: DI Container | Event Bus | Unit of Work | Middleware Pipeline        │    │
 │  └──────────────────────────────────────────────────────────────────────────────────────────────┘    │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │                │                 │                 │                │                │
        │                │                 │                 │                │                │
        ▼                ▼                 ▼                 ▼                ▼                ▼
 ┌──────────┐   ┌──────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
 │PostgreSQL│   │    Redis     │  │ Elasticsearch   │  │    Celery    │  │    S3    │  │   RabbitMQ    │
 │(Primary) │   │ Cache + WS   │  │ Product Search  │  │  (Worker)    │  │ (MinIO)  │  │ (Event Queue) │
 │          │   │ Session + Q  │  │ + Log Analytics │  │              │  │          │  │              │
 └──────────┘   └──────────────┘  └────────────────┘  └──────────────┘  └──────────┘  └──────────────┘
        │                                                                                  │
        │                          ┌──────────────┐                                       │
        └──────────────────────────│ PostgreSQL   │───────────────────────────────────────┘
                                   │ (Read Replica)│
                                   └──────────────┘
```

---

## 3. Technology Stack Rationale

### 3.1 Frontend — Next.js (React)

| Concern | Decision | Rationale |
|---|---|---|
| Framework | Next.js 14+ (App Router) | SSR for SEO-critical pages (product listings), ISR for catalog pages, SPA for authenticated dashboard. Single codebase for web + API routes (BFF). |
| State Management | Zustand + TanStack Query | Zustand for client-side global state (cart, auth). TanStack Query for server-state caching and synchronisation (automatic refetch, optimistic updates). |
| Styling | Tailwind CSS + shadcn/ui | Utility-first CSS for rapid iteration. Pre-built accessible component library reduces UI development time. |
| Type Safety | TypeScript (strict mode) | End-to-end type safety across frontend and backend via shared `@tsbl/types` package. |
| Real-Time | Socket.IO (client) | Bidirectional communication for order status updates, admin notifications. |

### 3.2 Backend — FastAPI (Python)

| Concern | Decision | Rationale |
|---|---|---|
| Framework | FastAPI (ASGI) | Async-native, auto-generated OpenAPI docs, Pydantic validation, high throughput for I/O-bound marketplace operations. |
| Language | Python 3.12 | Broad ecosystem for ML (recommendations), NLP (search), data analysis. Team velocity優勢. |
| ASGI Server | Uvicorn + Gunicorn | Uvicorn for async workers, Gunicorn as process manager for multi-worker deployments. |
| DI Framework | FastAPI `Depends` + custom container | Built-in dependency injection for request-scoped services; extended with custom `injector` for application-scoped singletons. |
| ORM | SQLAlchemy 2.0 (async) | Mature, well-documented, supports complex queries, raw SQL escape hatch, Alembic migrations. |
| Validation | Pydantic v2 | Integrated with FastAPI, Rust-based core for performance, JSON Schema generation. |

### 3.3 Database — PostgreSQL

| Concern | Decision | Rationale |
|---|---|---|
| RDBMS | PostgreSQL 16 | ACID compliance for financial transactions, rich indexing (GIN, GiST, partial), full-text search, JSONB, partitioning, mature replication. |
| Connection Pool | PgBouncer (transaction mode) | Lightweight connection pooling between FastAPI and PostgreSQL. Reduces connection overhead. |
| Migrations | Alembic | Declarative migration generation, auto-detection of SQLAlchemy model changes, branching support. |

### 3.4 Cache & Sessions — Redis

| Concern | Decision | Rationale |
|---|---|---|
| Cache | Redis 7 | Sub-millisecond reads for product cache, session store, rate limiter counters, distributed lock manager. |
| Pub/Sub | Redis Pub/Sub (or Redis Streams) | Lightweight real-time event relay for WebSocket broadcasting. |
| Message Queue | RabbitMQ (primary) + Redis (lightweight) | RabbitMQ for durable async tasks (order processing, email). Redis for ephemeral job queues (cache invalidation). |

### 3.5 Search — Elasticsearch

| Concern | Decision | Rationale |
|---|---|---|
| Full-Text Search | Elasticsearch 8 | Product search with fuzzy matching, faceted navigation, autocomplete, synonym handling, relevance scoring. |
| Log Aggregation | Elasticsearch + Filebeat | Centralised logging for debugging, audit, and analytics. |

### 3.6 Async Task Processing — Celery

| Concern | Decision | Rationale |
|---|---|---|
| Worker | Celery + RabbitMQ | Reliable task queue for email dispatch, invoice generation, report computation, cache warming. |
| Schedule | Celery Beat | Periodic tasks: order timeout, promotional campaign start/end, database cleanup. |
| Result Store | Redis | Task result storage for polling long-running operations. |

### 3.7 Object Storage — S3 (MinIO / AWS S3)

| Concern | Decision | Rationale |
|---|---|---|
| Storage | S3-compatible (MinIO for dev, AWS S3 for prod) | Product images, vendor documents, invoice PDFs, user avatars. |
| CDN | CloudFront / Cloudflare | Edge caching for static assets, image optimisation (WebP conversion). |

---

## 4. Communication Patterns

### 4.1 Frontend ↔ Backend

```
 ┌─────────────┐          REST (JSON)          ┌─────────────┐
 │             │ ────────────────────────────── │             │
 │  Next.js    │  GET /api/v1/products          │   FastAPI   │
 │  (Browser)  │  POST /api/v1/orders           │   (ASGI)    │
 │             │  PUT /api/v1/profile           │             │
 │             │  DELETE /api/v1/cart/items     │             │
 │             │                                │             │
 │             │ ─ ─ ─ ─ WebSocket (Socket.IO) ─ ─ ─ ─ ─ ─ ─ │
 │             │  order.status_changed           │             │
 │             │  admin.notification             │             │
 │             │  cart.sync                      │             │
 └─────────────┘                                └─────────────┘
```

- **REST**: All CRUD operations, search queries, authentication, file uploads. JSON request/response bodies. Token-based auth via `Authorization: Bearer <JWT>`.
- **WebSocket**: Real-time order status updates, admin alerts, live chat (customer ↔ vendor), dashboard real-time metrics.
- **BFF (Backend for Frontend)**: Next.js API routes act as a thin BFF layer for server-side operations (secure token refresh, server-side API calls).

### 4.2 Backend ↔ Internal Services

```
 ┌─────────────┐     SQLAlchemy (async)     ┌─────────────┐
 │  FastAPI    │ ──────────────────────────► │  PostgreSQL  │
 │  Module A   │                             │  (Primary)   │
 │             │     Redis (aioredis)        ┌─────────────┐
 │             │ ──────────────────────────► │    Redis     │
 │             │                             └─────────────┘
 │             │     Elasticsearch DSL       ┌────────────────┐
 │             │ ──────────────────────────► │ Elasticsearch  │
 │             │                             └────────────────┘
 │             │     Celery apply_async()    ┌────────────────┐
 │             │ ──────────────────────────► │  RabbitMQ      │
 │             │                             └───────┬────────┘
 │             │                                     │
 │             │                             ┌───────▼────────┐
 │             │ ◄──────────────────────────│  Celery Worker  │
 │             │  (AsyncResult / callback)   └────────────────┘
 └─────────────┘
```

All inter-service calls within the backend are **in-process function calls** (modular monolith), not network calls. This avoids the latency, complexity, and failure modes of distributed microservices during the initial build phase. When splitting into microservices, these boundaries become gRPC or async event contracts.

### 4.3 External Integrations

| Integration | Protocol | Library | Purpose |
|---|---|---|---|
| **SSLCommerz** | REST (POST) | `httpx` | Payment initiation, validation, IPN callback |
| **bKash** | REST (JSON) | `httpx` | Payment via bKash Tokenised Checkout |
| **Stripe** | REST + Webhook | `stripe` Python | International payments, Connect for split payments |
| **Twilio** | REST | `twilio` Python | SMS OTP, order notifications |
| **SMTP / SES** | SMTP / AWS SDK | `smtplib` / `boto3` | Transactional emails (invoices, shipping updates) |
| **SteadFast / RedX** | REST | `httpx` | Shipping rate calculation, label generation, tracking |
| **Google Maps** | REST | `httpx` | Address autocomplete, delivery distance calculation |
| **Cloudflare** | DNS / CDN | API | Static asset delivery, DDoS protection |

---

## 5. Architecture Principles and Decisions

### 5.1 Principles (ADRs)

| ID | Principle | Rationale |
|---|---|---|
| **P1** | Modular Monolith first, microservices when proven | Start with a single deployable unit. Extract bounded contexts into microservices only when justified by scaling demands, team autonomy, or deployment frequency. Avoids premature distributed complexity. |
| **P2** | Bounded Contexts via Python packages | Each module (`auth`, `catalog`, `order`, `payment`, `vendor`, `admin`) is a top-level Python package with its own models, services, repos, schemas, routers, and tests. Clear `import` boundaries enforced via linting. |
| **P3** | Event-Driven Coupling | Modules communicate through an internal event bus (in-process) backed by RabbitMQ for durable dispatch. No direct service-to-service calls between modules. This preserves the option to split into services later. |
| **P4** | CQRS for hot paths | Read models (materialised views, Elasticsearch indices) are optimised for query performance. Write models maintain transactional consistency. Synchronised via domain events. |
| **P5** | API-first development | All functionality is exposed through a versioned API. The frontend is a consumer of the API, not tightly coupled to backend internals. |
| **P6** | Defense in Depth | Input validation at API layer (Pydantic), authorisation at service layer, encryption at rest (PostgreSQL `pgcrypto`) and in transit (TLS 1.3), secrets via Vault/Env vars. |
| **P7** | Observability by default | Structured JSON logging, OpenTelemetry tracing, Prometheus metrics on every endpoint, health check endpoints. |
| **P8** | Idempotency for payments | Payment operations are idempotent via idempotency keys. Retries are safe. Dead-letter queues capture failures for manual resolution. |

### 5.2 Key Architectural Decisions

| Decision | Option Chosen | Alternatives Considered |
|---|---|---|
| Deployment Architecture | Docker Compose → Kubernetes | Serverless (Lambda + API Gateway) — rejected due to cold start, stateful WebSocket limitations |
| Monolith vs Microservices | Modular Monolith | Microservices — rejected for initial build due to operational overhead |
| ORM | SQLAlchemy 2.0 (async) | Tortoise ORM (limited ecosystem), raw SQL (too verbose) |
| Task Queue | Celery + RabbitMQ | Arq (redis-only, limited visibility), Dramatiq (smaller community) |
| API Protocol | REST + WebSocket | GraphQL (complexity, caching challenges), gRPC (not browser-native) |
| Search Engine | Elasticsearch | Meilisearch (easier but less control), Typesense (newer, smaller community) |
| Frontend Framework | Next.js | Remix (smaller ecosystem), Vite+React (no SSR built-in) |
| Payment Orchestration | Adapter pattern per gateway | Single gateway (vendor lock-in), Stripe only (BD market constraints) |

---

## 6. Modular Monolith Structure with Bounded Contexts

### 6.1 Top-Level Package Structure

```
src/
├── tsbl/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory
│   ├── config.py                  # Pydantic settings (env-based)
│   │
│   ├── common/                    # Shared kernel
│   │   ├── di.py                  # Dependency injection container
│   │   ├── event_bus.py           # In-process event bus (domain events)
│   │   ├── exceptions.py          # Base exception hierarchy
│   │   ├── middleware/            # Global ASGI middleware
│   │   ├── models/               # SQLAlchemy Base, mixins (TimestampMixin, SoftDeleteMixin)
│   │   ├── repositories/         # Abstract base repository
│   │   ├── unit_of_work.py       # Unit of Work pattern
│   │   └── utils/                # Pagination, serialisers, validators
│   │
│   ├── auth/                      # Bounded Context: Authentication & Authorisation
│   │   ├── domain/               # Entities, Value Objects, Domain Events
│   │   ├── application/          # Use Cases / Services
│   │   ├── infrastructure/       # Repos, JWT provider, OAuth clients
│   │   └── presentation/         # API routers, schemas, WebSocket handlers
│   │
│   ├── catalog/                   # Bounded Context: Product Catalog
│   │   ├── domain/               # Product, Category, Brand, Variant
│   │   ├── application/          # ProductService, SearchService
│   │   ├── infrastructure/       # ProductRepo, ElasticsearchProductRepo
│   │   └── presentation/         # Product routers, search endpoints
│   │
│   ├── cart/                      # Bounded Context: Shopping Cart & Checkout
│   │   ├── domain/               # Cart, CartItem, Checkout
│   │   ├── application/          # CartService, CheckoutService
│   │   ├── infrastructure/       # CartRepo (Redis + PostgreSQL)
│   │   └── presentation/         # Cart API, checkout endpoints
│   │
│   ├── order/                     # Bounded Context: Order Management & Fulfillment
│   │   ├── domain/               # Order, OrderItem, Shipment, Invoice
│   │   ├── application/          # OrderService, FulfillmentService
│   │   ├── infrastructure/       # OrderRepo, Shipment integration
│   │   └── presentation/         # Order API, WebSocket status updates
│   │
│   ├── payment/                   # Bounded Context: Payment Processing
│   │   ├── domain/               # Payment, Transaction, Refund
│   │   ├── application/          # PaymentService, GatewayAdapter
│   │   ├── infrastructure/       │ Gateway implementations (SSLCommerz, bKash, Stripe)
│   │   └── presentation/         # Payment webhook handlers
│   │
│   ├── vendor/                    # Bounded Context: Vendor Management
│   │   ├── domain/               # Vendor, VendorApplication, Payout
│   │   ├── application/          # VendorService, PayoutService
│   │   ├── infrastructure/       # VendorRepo, PayoutProvider
│   │   └── presentation/         # Vendor dashboard API
│   │
│   ├── notification/              # Bounded Context: Notifications
│   │   ├── domain/               # Notification, Template, Channel
│   │   ├── application/          # NotificationService
│   │   ├── infrastructure/       # EmailProvider, SMSProvider, PushProvider
│   │   └── presentation/         # Preference API
│   │
│   ├── admin/                     # Bounded Context: Admin & Moderation
│   │   ├── domain/               # AdminUser, Role, Permission, AuditLog
│   │   ├── application/          # AdminService, ModerationService
│   │   ├── infrastructure/       # AdminRepo, AuditRepo
│   │   └── presentation/         # Admin API, reporting endpoints
│   │
│   └── analytics/                 # Bounded Context: Analytics & Reporting
│       ├── domain/               # Report, Metric, Dashboard
│       ├── application/          # AnalyticsService
│       ├── infrastructure/       # TimescaleDB connector, Event warehouse
│       └── presentation/         # Analytics API, CSV export
```

### 6.2 Bounded Context Boundaries

| Context | Responsibility | Database Schema | Event Ownership |
|---|---|---|---|
| **auth** | Identity, authentication, RBAC, OAuth | `tsbl_auth.*` | `UserRegistered`, `UserLoggedIn`, `RoleAssigned` |
| **catalog** | Products, categories, brands, inventory | `tsbl_catalog.*` | `ProductCreated`, `InventoryChanged`, `CategoryMoved` |
| **cart** | Shopping cart, wishlist, coupon application | `tsbl_cart.*` | `CartAbandoned`, `ItemAdded`, `CouponApplied` |
| **order** | Orders, shipments, returns, invoices | `tsbl_order.*` | `OrderPlaced`, `Shipped`, `Delivered`, `ReturnRequested` |
| **payment** | Transactions, refunds, reconciliation | `tsbl_payment.*` | `PaymentReceived`, `RefundProcessed`, `PaymentFailed` |
| **vendor** | Vendor registration, commissions, payouts | `tsbl_vendor.*` | `VendorApproved`, `PayoutInitiated`, `CommissionUpdated` |
| **notification** | Email, SMS, push, in-app notification | `tsbl_notification.*` | `NotificationSent`, `DeliveryFailed` |
| **admin** | Admin roles, audit log, platform config | `tsbl_admin.*` | `ConfigChanged`, `UserSuspended` |
| **analytics** | Aggregated metrics, reports, dashboards | `tsbl_analytics.*` | (Read-only subscriber to all events) |

---

## 7. Future Microservices Decomposition Boundaries

The modular monolith is structured so that each bounded context can be extracted into an independent microservice with minimal refactoring. The following table describes the extraction plan:

| Phase | Service | Trigger for Extraction | Communication Change |
|---|---|---|---|
| **1** | **Payment Service** | PCI compliance scope reduction, independent scaling during sales events | Event bus → RabbitMQ queue. gRPC for synchronous queries. Webhook endpoints remain public. |
| **2** | **Notification Service** | High volume of transactional emails/SMS. Need independent scaling. | RabbitMQ consumer becomes its own deployment. API for preference management remains. |
| **3** | **Catalog Service** | Read-heavy workload competing with write-heavy order processing. | Elasticsearch index maintained by catalog service. CQRS via materialised cache. gRPC for inventory queries. |
| **4** | **Auth Service** | SSO integration with partner platforms. Security isolation. | OAuth2 / OIDC protocol. Separate user database (read-only replicas for other services). |
| **5** | **Order Service** | Complex state machine requires dedicated team. | Saga pattern for distributed transactions. Choreography-based orchestration. |
| **6** | **Analytics Service** | Heavy ETL workloads impact primary database. | CDC (Debezium) into data lake. Separate OLAP database (ClickHouse). |

### 7.1 Strangler Fig Migration Pattern

Each extraction follows the Strangler Fig pattern:

1. **Isolate data**: Create dedicated database schema / database for the bounded context.
2. **Synchronise**: Run dual-writes (old monolith + new service) in parallel with comparison logging.
3. **Route**: Ingress route traffic for that domain to the new service.
4. **Remove**: Decommission the module from the monolith once traffic is verified.

---

## 8. Non-Functional Requirements Coverage

| NFR | Approach |
|---|---|
| **Scalability** | Horizontal scaling via stateless API containers. Redis cache absorbs read spikes. Celery workers scale independently per queue. |
| **Availability** | Multi-AZ deployment. Health checks on `/health` + `/ready`. Circuit breakers on external integrations. Graceful degradation (serve cached content when downstream fails). |
| **Performance** | p95 API response < 200ms. Search p95 < 300ms. Page load < 2s (LCP). CDN for assets. |
| **Security** | OWASP Top 10 compliance. JWT stored in HttpOnly cookies. CSRF tokens for state-changing requests. Rate limiting per IP + per user. Encryption at rest (AES-256) and in transit (TLS 1.3). |
| **Observability** | OpenTelemetry traces across all services. Prometheus metrics (RED: Rate, Errors, Duration). Loki/Grafana for log aggregation. PagerDuty alerts on SLO breaches. |
| **Disaster Recovery** | RPO < 5 minutes (WAL streaming). RTO < 30 minutes. Automated failover to read replica. Daily backups with 30-day retention. |

---

## 9. Deployment Topology (High-Level)

```
                                  ┌──────────────────────┐
                                  │   Cloudflare DNS/CDN  │
                                  └──────────┬───────────┘
                                             │
                                  ┌──────────▼───────────┐
                                  │   AWS ALB / Nginx     │
                                  │   SSL Termination     │
                                  └──────────┬───────────┘
                                             │
                    ┌────────────────────────┼─────────────────────────┐
                    │                        │                         │
           ┌────────▼────────┐     ┌─────────▼────────┐     ┌────────▼────────┐
           │  Next.js SSR     │     │   FastAPI ASGI    │     │   Admin UI      │
           │  (ECS / Lambda)  │     │   (ECS Fargate)   │     │   (Next.js)     │
           └────────┬────────┘     └─────────┬────────┘     └────────┬────────┘
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │   PgBouncer      │
                                    │   Connection Pool│
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼─────────────────────────┐
                    │                        │                         │
           ┌────────▼────────┐     ┌─────────▼────────┐     ┌────────▼────────┐
           │  PostgreSQL      │     │ PostgreSQL       │     │  Redis           │
           │  Primary         │────►│ Read Replica x2  │     │  (Cache + Queue) │
           └────────┬────────┘     └──────────────────┘     └────────┬────────┘
                    │                                                │
           ┌────────▼────────┐                             ┌─────────▼────────┐
           │  S3 (MinIO)     │                             │  RabbitMQ         │
           │  Object Storage │                             │  + Celery Worker  │
           └─────────────────┘                             └──────────────────┘
```

---

## 10. Glossary

| Term | Definition |
|---|---|
| **Bounded Context** | A logical boundary within which a particular domain model applies (from Domain-Driven Design). |
| **CQRS** | Command Query Responsibility Segregation — separate read and write models. |
| **Event Bus** | In-process pub/sub mechanism for publishing and consuming domain events synchronously or asynchronously. |
| **Modular Monolith** | A single deployment unit with well-defined module boundaries enforced by the codebase structure. |
| **UoW (Unit of Work)** | Pattern that maintains a list of objects affected by a business transaction and coordinates the writing out of changes. |
| **Saga** | A sequence of transactions that maintains data consistency across multiple services without distributed transactions. |
| **Strangler Fig** | A pattern for incrementally migrating a monolithic system to microservices by gradually replacing specific pieces of functionality. |
