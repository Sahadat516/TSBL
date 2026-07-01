# Backend Architecture — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-BE-007 |
| **Version** | 2.0 |
| **Status** | Approved |
| **Author** | Principal Software Architect |
| **Date** | 2026-07-02 |
| **Stack** | Python 3.13+, FastAPI, PostgreSQL 16, SQLAlchemy 2.x, Alembic, JWT (RS256), Redis 7, Celery, Elasticsearch 8, WebSocket, S3-compatible Storage (MinIO), Docker, NGINX |

---

## Table of Contents

1. [Overall Architecture](#1-overall-architecture)
2. [Architecture Style](#2-architecture-style)
3. [Project Folder Structure](#3-project-folder-structure)
4. [Module Architecture](#4-module-architecture)
5. [Layer Architecture](#5-layer-architecture)
6. [Dependency Injection Strategy](#6-dependency-injection-strategy)
7. [Configuration Management](#7-configuration-management)
8. [Security Architecture](#8-security-architecture)
9. [Middleware Architecture](#9-middleware-architecture)
10. [Exception Handling](#10-exception-handling)
11. [Logging Strategy](#11-logging-strategy)
12. [Caching Strategy](#12-caching-strategy)
13. [Background Jobs (Celery)](#13-background-jobs-celery)
14. [Realtime Architecture (WebSocket)](#14-realtime-architecture-websocket)
15. [External Service Integration](#15-external-service-integration)
16. [API Design Standards](#16-api-design-standards)
17. [Validation Strategy](#17-validation-strategy)
18. [Performance Strategy](#18-performance-strategy)
19. [Scalability Strategy](#19-scalability-strategy)
20. [Monitoring Strategy](#20-monitoring-strategy)
21. [Testing Strategy](#21-testing-strategy)
22. [Coding Standards](#22-coding-standards)
23. [Development Workflow](#23-development-workflow)
24. [Deployment Strategy](#24-deployment-strategy)
25. [Final Architecture Summary](#25-final-architecture-summary)

---

## 1. Overall Architecture

### 1.1 Architectural Philosophy

TRUE STAR BD LIMITED's backend is architected as a **Modular Monolith** designed with the explicit intent to evolve into a **Microservices** architecture as the platform scales. It is deployed as a single unit at present, but every module within it is built with strict bounded contexts, defined interfaces, and isolated concerns that allow extraction into independent services with minimal friction.

The guiding principle is **evolution over revolution**: build a cohesive system today that can be surgically disaggregated tomorrow. Each module communicates through well-defined interfaces (Python abstract base classes and protocols), not through implicit coupling. This ensures that when the time comes to extract a high-traffic module — such as payments or products — into its own service, the interface boundary is already drawn.

### 1.2 Advantages of the Modular Monolith

- **Single deployment unit**: One Docker image, one CI/CD pipeline, one deployment target. No coordination across multiple services for routine releases.
- **Shared ACID transactions**: A single PostgreSQL database allows cross-module transactions (e.g., creating an order while deducting inventory and recording a payment ledger entry) without distributed transaction complexity.
- **Zero network latency between modules**: Service calls are in-process function calls. No serialisation overhead, no network jitter, no circuit-breaker logic needed for internal communication.
- **Simpler CI/CD**: One test suite, one build step, one deployment. Developer onboarding is faster because there is a single repository and a single application to understand.
- **Consistent domain model**: Entities are defined once and shared across module boundaries where appropriate, avoiding the data duplication and synchronisation challenges of distributed systems.
- **Lower operational overhead**: One application to monitor, one set of logs to trace, one process to restart. No service mesh, no API gateway routing for internal traffic, no inter-service authentication overhead.

### 1.3 Disadvantages

- **Single deployment risk**: A bug in any module can take down the entire application. Strict module isolation and comprehensive testing mitigate this, but the blast radius is inherently larger than in a distributed system.
- **Cannot scale modules independently**: The entire application scales as one unit. If the marketplace module is under heavy load but the admin module is idle, both receive the same resources. Horizontal scaling of individual modules is only possible after extraction.
- **Shared database coupling**: All modules share the same PostgreSQL schema. Schema migrations must be backward-compatible to avoid blocking other modules. A long-running migration can affect all modules.
- **Build and deploy velocity**: As the codebase grows, the monolith becomes larger, increasing build times and the surface area of risk per deployment.

### 1.4 Future Scalability Path

The architecture is designed for a phased extraction of modules into standalone microservices when traffic patterns demand it:

| Module | Extraction Signal | Extraction Priority |
|---|---|---|
| Payments | >1,000 transactions/day or PCI scope expansion | 1 — High |
| Orders | >10,000 orders/day or checkout latency targets missed | 2 — High |
| Products/Search | >100,000 product views/day or search latency degradation | 3 — Medium |
| Chat (WebSocket) | >10,000 concurrent connections or dedicated scaling needed | 4 — Medium |
| Notifications | >100,000 notifications/day or delivery latency issues | 5 — Low |

The extraction of each module follows a consistent pattern: (1) extract the interface contract into a shared library, (2) replicate the database into a per-service schema or dedicated database, (3) stand up the new service behind the API gateway, (4) migrate consumers one by one from in-process calls to event-driven or RPC calls, (5) decommission the module from the monolith.

---

## 2. Architecture Style

The backend employs a synthesis of multiple proven architectural patterns, each chosen to address specific concerns of the enterprise marketplace domain.

### 2.1 Clean Architecture

The codebase is organised into concentric layers where dependencies point inward — the **Domain** layer knows nothing about the **Infrastructure** layer, and the **Application** layer depends only on **Domain** abstractions. This ensures that business logic is never coupled to frameworks, database drivers, or external services.

- **Entities** (innermost): Pure business objects with behaviour. A `Product` entity knows how to validate its own pricing, a `Wallet` entity enforces balance invariants. No framework decorators, no ORM imports.
- **Use Cases** (Application layer): Service classes that orchestrate domain entities to achieve a business outcome. A `CreateOrderUseCase` orchestrates `Cart`, `Product`, `Inventory`, and `Payment` entities.
- **Interface Adapters**: Repository implementations, external service adapters, serialisers. These translate between domain concepts and infrastructure concerns.
- **Frameworks & Drivers** (outermost): FastAPI routes, SQLAlchemy models, Redis client, Celery tasks. These are the most volatile components and are kept thin.

### 2.2 Layered Architecture

The system is organised into six horizontal layers that process a request from ingress to persistence:

| Layer | Responsibility | Components |
|---|---|---|
| **Presentation** | HTTP interface, request parsing, response serialisation | FastAPI route handlers, WebSocket event handlers, middleware pipeline |
| **Application** | Use case orchestration, business validation, DTO mapping | Service classes, orchestrators, command/query handlers |
| **Domain** | Business entities, value objects, domain events, business rules | Entities, aggregates, value objects, repository interfaces, domain services |
| **Infrastructure** | Technical implementations, external integrations | SQLAlchemy repositories, payment adapters, email adapters, cache adapters, search index adapters |
| **Persistence** | Data storage and retrieval | ORM models, migrations, connection pool, query builders |
| **External Service** | Third-party provider integration | Payment gateway clients, SMS gateways, email providers, cloud storage, CDN |

### 2.3 Domain-Driven Design (DDD)

**Bounded Contexts:** The marketplace domain is decomposed into 14 bounded contexts, each with its own ubiquitous language, domain model, and ownership boundary. Each context maps to a module under `app/modules/`:

| Bounded Context | Core Language | Module |
|---|---|---|
| Auth | Authentication, identity, session, MFA, OAuth | auth |
| Users | Profile, address, preferences, verification | users |
| Marketplace | Product, category, inventory, variant, listing | marketplace |
| Orders | Cart, checkout, order, shipment, tracking | orders |
| Payments | Transaction, gateway, refund, settlement | payments |
| Wallet | Balance, ledger, withdrawal, deposit | wallet |
| Escrow | Hold, release, milestone, arbitration | escrow |
| Reviews | Rating, review, feedback, moderation | reviews |
| Chat | Conversation, message, attachment | chat |
| Notifications | Email, SMS, push, in-app | notifications |
| Support | Ticket, dispute, escalation, resolution | support |
| Affiliate | Referral, commission, conversion, payout | affiliate |
| Analytics | Event, metric, report, dashboard | analytics |
| Admin | Administration, RBAC, audit, settings | admin |

**Ubiquitous Language:** Every code element — class names, method names, variable names, database column names — uses the language of the domain. A `Product` is listed for sale, a `Buyer` places an `Order`, a `Seller` receives a `Payout`. Technical implementation details are hidden from the domain vocabulary.

**Aggregates:** Consistency boundaries are defined by aggregates. The `Order` aggregate contains `OrderItem` entities and enforces invariants such as "an order cannot exceed the seller's maximum order value" and "order status transitions must follow the state machine." Aggregates are loaded and persisted as a single unit.

**Domain Events:** Significant business occurrences are captured as domain events: `OrderPlaced`, `PaymentConfirmed`, `EscrowReleased`, `DisputeOpened`, `ReviewSubmitted`. These events are published within the originating context synchronously (within the same transaction) and consumed by interested contexts either synchronously or asynchronously via the event bus.

**Value Objects:** Immutable, self-validating value objects model concepts with no identity: `Money(amount, currency)`, `Address(street, city, postal_code, country)`, `Rating(score)`, `EmailAddress(value)`, `PhoneNumber(value, country_code)`. Value objects are compared by structural equality, not by identity.

### 2.4 Hexagonal Architecture (Ports and Adapters)

The core domain depends only on **ports** (Python abstract interfaces), never on concrete **adapters**. This allows the domain to be tested, reasoned about, and evolved without any reference to databases, file systems, or external APIs.

**Ports (interface layer):**

- Repository ports: `IProductRepository`, `IOrderRepository`, `IUserRepository`, `ICategoryRepository`
- Service ports: `IPaymentGateway`, `IEmailService`, `ISMSService`, `IPushNotificationService`, `IStorageService`
- Messaging ports: `IEventBus`, `IMessageQueue`, `ICache`

**Adapters (implementation layer):**

- Database adapters: `SQLAlchemyProductRepository`, `SQLAlchemyOrderRepository`
- External service adapters: `StripePaymentGateway`, `SSLCommerzPaymentGateway`, `SendGridEmailService`, `TwilioSMSService`, `FirebasePushService`, `MinioStorageService`
- Cache adapters: `RedisCacheAdapter`
- Search adapters: `ElasticsearchSearchAdapter`

### 2.5 Repository Pattern

Each aggregate root has a dedicated repository interface in the domain layer and a concrete implementation in the infrastructure layer.

- **Generic Base CRUD**: A `BaseRepository[EntityType]` abstract class provides standard operations: `add()`, `get()`, `get_by_id()`, `list()`, `update()`, `delete()`, `exists()`. All concrete repositories inherit from this base.
- **Custom Queries**: Repositories extend the base with domain-specific query methods: `ProductRepository.search_by_name()`, `OrderRepository.find_by_buyer_and_status()`, `WalletRepository.get_balance_for_user()`.
- **Query Separation**: Write operations accept domain entities and return void or unit. Read operations return entities or collections. This separation prevents side effects from creeping into read paths.

### 2.6 Service Pattern

- **Application Services**: Stateless classes that implement use cases. They receive requests (DTOs), validate business rules, coordinate one or more domain entities, invoke repositories, and return results (DTOs or domain events). Example: `OrderService.place_order(cart_id, buyer_id, payment_method)`.
- **Domain Services**: Stateless classes that encapsulate domain logic that does not naturally belong to a single entity. Example: `PricingService.calculate_commission(product_price, seller_tier)`.
- **Orchestrators**: Higher-level services that coordinate multiple application services across module boundaries. Example: `CheckoutOrchestrator` coordinates `CartService`, `InventoryService`, `PricingService`, `OrderService`, `PaymentService`, and `NotificationService` to complete a checkout flow.

### 2.7 Unit of Work

Transaction management is centralised through the Unit of Work (UoW) pattern, implemented via SQLAlchemy's session.

- Each request creates a single database session (scoped).
- The UoW tracks all loaded entities and changes within the session.
- On successful completion, the UoW commits the transaction. On failure, it rolls back.
- The UoW also tracks domain events collected during the request and publishes them after the commit succeeds (outbox pattern in-process).
- This ensures that events are only published if the transaction that produced them succeeds, preventing inconsistent states.

### 2.8 CQRS (Command Query Responsibility Segregation)

A lightweight CQRS separation is applied where it adds value:

- **Commands**: Mutating operations that go through the domain model. Commands are validated against business rules, processed by the aggregate, and persisted through the repository. Example: `PlaceOrderCommand`, `ProcessPaymentCommand`, `ReleaseEscrowCommand`.
- **Queries**: Read operations that bypass the domain model entirely and use lightweight read models or direct projection queries. Dashboard data, analytics reports, and search results are fetched via queries against materialised views or Elasticsearch indices.
- **Query/Command Separation at the Route Level**: `GET` routes use query handlers. `POST`, `PUT`, `PATCH`, `DELETE` routes use command handlers. This separation is structural, not infrastructural — we do not use separate databases for reads and writes unless scalability demands it.

### 2.9 Dependency Injection

FastAPI's native `Depends()` function is the DI container. All dependencies are wired explicitly at the route handler level:

- **Scoped**: Database session (`get_db`), current user context (`get_current_user`), request ID, Unit of Work.
- **Singleton**: Configuration settings, Redis client, Elasticsearch client, S3 client, Celery app, cache adapters, service instances.
- **Transient**: Stateless utilities, value object factories, DTO mappers.

### 2.10 Event-Driven Design

- **Synchronous Domain Events**: Events that must be handled within the same transaction (e.g., updating inventory when an order is placed) are handled synchronously via the event dispatcher within the UoW lifecycle.
- **Asynchronous Events (Message Queue)**: Events that do not require immediate consistency (e.g., sending a notification email, updating analytics) are published to the message queue (RabbitMQ or Redis Streams) and consumed by Celery tasks.
- **Event Schema**: Each event has a standard envelope: `{ event_id, event_type, aggregate_type, aggregate_id, version, timestamp, data, metadata }`.

### 2.11 State Management

Complex business entities use explicit state machines with defined transitions, guards, and side effects:

- **Order State Machine**: `pending -> confirmed -> processing -> shipped -> delivered -> completed` with transitions for cancellation and refund at appropriate states. Each transition fires domain events.
- **Escrow State Machine**: `held -> (milestone_reached) -> held -> released` or `held -> dispute_opened -> (resolved) -> released | refunded`.
- **Dispute State Machine**: `opened -> under_review -> escalated -> resolved_closed` with `resolved_in_favor_of_buyer` or `resolved_in_favor_of_seller` terminal states.
- **Payment State Machine**: `pending -> processing -> completed | failed | refunded | partially_refunded`.
- **State Transition Maps**: Each state machine is defined as an explicit transition map (dictionary of `current_state -> { event: (next_state, guard_fn, side_effect_fn) }`), making all possible flows visible in a single location and preventing illegal transitions at the code level.

---

## 3. Project Folder Structure

```
backend/
+-- app/
|   +-- main.py                           # FastAPI application factory
|   +-- core/
|   |   +-- __init__.py
|   |   +-- config.py                     # pydantic-settings: env to typed settings
|   |   +-- security.py                   # JWT encode/decode, password hashing, encryption utils
|   |   +-- database.py                   # SQLAlchemy async engine, sessionmaker, session dependency
|   |   +-- redis.py                      # Redis client init, connection pool, health check
|   |   +-- celery.py                     # Celery app instance, queue config, task base classes
|   |   +-- elasticsearch.py             # ES client init, index management helpers
|   |   +-- s3.py                         # S3/MinIO client, bucket management, presigned URL helpers
|   |   +-- dependencies.py               # Global FastAPI dependencies (pagination, filters, locale)
|   |   +-- events.py                     # Domain event dispatcher, event bus interface
|   |   +-- logging.py                    # structlog configuration, log formatters, sensitive redaction
|   |   +-- exceptions.py                 # Base AppException, global exception handlers
|   +-- common/
|   |   +-- __init__.py
|   |   +-- base_model.py                 # SQLAlchemy declarative base, common mixins (Timestamps, SoftDelete)
|   |   +-- base_repository.py            # Generic CRUD repository with pagination
|   |   +-- base_service.py               # Service base class with UoW and event dispatcher
|   |   +-- base_schema.py                # Pydantic base schemas, response envelope
|   |   +-- pagination.py                 # Cursor-based and offset-based pagination logic
|   |   +-- response.py                   # Standard API response builder (success, error, paginated)
|   |   +-- exceptions.py                 # Module-level exception definitions
|   |   +-- enums.py                      # Shared enums (OrderStatus, PaymentStatus, UserRole, etc.)
|   |   +-- constants.py                  # Magic numbers, configurable thresholds, time durations
|   |   +-- utils.py                      # Shared utility functions (slugify, truncate, mask_pii)
|   +-- middleware/
|   |   +-- __init__.py
|   |   +-- logging.py                    # Structured request/response logging
|   |   +-- authentication.py             # JWT extraction, validation, current_user injection
|   |   +-- request_id.py                 # UUID v4 correlation ID generation and propagation
|   |   +-- cors.py                       # CORS policy configuration
|   |   +-- rate_limit.py                 # Redis-backed sliding window rate limiter
|   |   +-- localization.py               # Locale detection and resolution
|   |   +-- performance.py               # Request timing, slow query detection
|   +-- modules/
|   |   +-- auth/
|   |   |   +-- api/                      # Route handlers: register, login, refresh, logout, mfa, oauth
|   |   |   +-- application/             # Services: AuthService, MFAService, OAuthService
|   |   |   +-- domain/                  # Entities: User, Session; Value Objects: EmailAddress, Password
|   |   |   +-- infrastructure/          # Repositories: UserRepository, SessionRepository; Adapters: JWTProvider
|   |   |   +-- schemas/                 # Pydantic: LoginRequest, RegisterRequest, TokenResponse
|   |   +-- users/
|   |   |   +-- api/                      # Profile CRUD, address management, verification
|   |   |   +-- application/             # UserService, ProfileService, VerificationService
|   |   |   +-- domain/                  # Entities: Profile, Address, VerificationToken
|   |   |   +-- infrastructure/          # Repositories: UserRepository, AddressRepository
|   |   |   +-- schemas/                 # UserResponse, AddressSchema, ProfileUpdate
|   |   +-- marketplace/
|   |   |   +-- api/                      # Products CRUD, categories, search, inventory
|   |   |   +-- application/             # ProductService, CategoryService, SearchService, InventoryService
|   |   |   +-- domain/                  # Entities: Product, Category, Inventory, Variant; Value Objects: Money, SKU
|   |   |   +-- infrastructure/          # Repositories: ProductRepository, CategoryRepository; SearchAdapter: ES
|   |   |   +-- schemas/                 # ProductResponse, CategoryTree, SearchQuery, InventoryUpdate
|   |   +-- orders/
|   |   |   +-- api/                      # Cart, checkout, order management, shipping
|   |   |   +-- application/             # CartService, CheckoutService, OrderService, ShipmentService
|   |   |   +-- domain/                  # Entities: Cart, Order, OrderItem, Shipment; Domain Events: OrderPlaced
|   |   |   +-- infrastructure/          # Repositories: OrderRepository, CartRepository
|   |   |   +-- schemas/                 # CartItemSchema, CheckoutRequest, OrderDetailResponse
|   |   +-- payments/
|   |   |   +-- api/                      # Payment intent create, confirm, webhook receiver
|   |   |   +-- application/             # PaymentService, GatewayFactory, RefundService
|   |   |   +-- domain/                  # Entities: PaymentTransaction, PaymentMethod; Value Objects: Money
|   |   |   +-- infrastructure/          # Adapters: StripeGateway, SSLCommerzGateway, PayPalGateway, bKashGateway
|   |   |   +-- schemas/                 # PaymentIntentRequest, PaymentConfirmation, WebhookPayload
|   |   +-- wallet/
|   |   |   +-- api/                      # Balance, transactions, deposit, withdrawal
|   |   |   +-- application/             # WalletService, LedgerService, WithdrawalService
|   |   |   +-- domain/                  # Entities: Wallet, LedgerEntry, WithdrawalRequest
|   |   |   +-- infrastructure/          # Repositories: WalletRepository, LedgerRepository
|   |   |   +-- schemas/                 # BalanceResponse, TransactionHistory, WithdrawalRequest
|   |   +-- escrow/
|   |   |   +-- api/                      # Escrow hold, milestone completion, release
|   |   |   +-- application/             # EscrowService, MilestoneService, ArbitrationService
|   |   |   +-- domain/                  # Entity: EscrowTransaction, Milestone; Events: EscrowReleased
|   |   |   +-- infrastructure/          # Repositories: EscrowRepository
|   |   |   +-- schemas/                 # EscrowStatusResponse, MilestoneCompleteRequest
|   |   +-- reviews/
|   |   |   +-- api/                      # Submit, edit, delete reviews; moderate
|   |   |   +-- application/             # ReviewService, RatingService, ModerationService
|   |   |   +-- domain/                  # Entity: Review; Value Objects: Rating, ReviewContent
|   |   |   +-- infrastructure/          # Repositories: ReviewRepository
|   |   |   +-- schemas/                 # ReviewRequest, ReviewResponse, RatingSummary
|   |   +-- chat/
|   |   |   +-- api/                      # Conversations, messages, upload
|   |   |   +-- application/             # ChatService, ConversationService, TypingIndicatorService
|   |   |   +-- domain/                  # Entities: Conversation, Message, Attachment
|   |   |   +-- infrastructure/          # Repositories: ConversationRepository, MessageRepository
|   |   |   +-- schemas/                 # MessageResponse, ConversationSummary, SendMessageRequest
|   |   +-- notifications/
|   |   |   +-- api/                      # Preferences, history, mark-read
|   |   |   +-- application/             # NotificationService, PushService, EmailService, SMSService
|   |   |   +-- domain/                  # Entity: Notification; Value Objects: NotificationChannel, Template
|   |   |   +-- infrastructure/          # Adapters: FCMAdapter, TwilioAdapter, SendGridAdapter; Templates
|   |   |   +-- schemas/                 # NotificationResponse, PreferencesUpdate, SendTestRequest
|   |   +-- support/
|   |   |   +-- api/                      # Tickets, disputes, escalation
|   |   |   +-- application/             # TicketService, DisputeService, EscalationService
|   |   |   +-- domain/                  # Entities: Ticket, Dispute, Escalation; Events: DisputeOpened
|   |   |   +-- infrastructure/          # Repositories: TicketRepository, DisputeRepository
|   |   |   +-- schemas/                 # TicketResponse, DisputeDetail, EscalationRequest
|   |   +-- affiliate/
|   |   |   +-- api/                      # Referral links, commissions, payouts
|   |   |   +-- application/             # AffiliateService, CommissionService, PayoutService
|   |   |   +-- domain/                  # Entities: AffiliateLink, Referral, Commission
|   |   |   +-- infrastructure/          # Repositories: AffiliateRepository, CommissionRepository
|   |   |   +-- schemas/                 # LinkResponse, CommissionSummary, PayoutHistory
|   |   +-- analytics/
|   |   |   +-- api/                      # Dashboard endpoints, report triggers
|   |   |   +-- application/             # AnalyticsService, EventTracker, ReportGenerator
|   |   |   +-- domain/                  # Entity: AnalyticsEvent; Value Objects: EventType, MetricValue
|   |   |   +-- infrastructure/          # EventRepository, MaterialisedViewService
|   |   |   +-- schemas/                 # DashboardResponse, ReportParams, EventPayload
|   |   +-- admin/
|   |       +-- api/                      # User management, settings, audit log viewer, feature flags
|   |       +-- application/             # AdminService, AuditService, FeatureFlagService
|   |       +-- domain/                  # Entities: AdminAction, FeatureFlag
|   |       +-- infrastructure/          # Repositories: AdminRepository, AuditRepository
|   |       +-- schemas/                 # AdminActionResponse, FeatureFlagToggle, SettingsUpdate
|   +-- tasks/
|   |   +-- __init__.py
|   |   +-- email.py                     # Celery tasks: send_welcome, order_confirmation, password_reset, etc.
|   |   +-- notification.py              # Celery tasks: in_app, push, sms delivery
|   |   +-- analytics.py                 # Celery tasks: track_event, daily_report, refresh_mv
|   |   +-- cleanup.py                   # Celery tasks: expired_sessions, temp_files, archive, purge
|   +-- ws/
|       +-- __init__.py
|       +-- connection_manager.py        # WebSocket connection registry, room/channel subscription
|       +-- handlers/
|       |   +-- chat.py                  # Chat WebSocket event handlers (send, typing, read)
|       |   +-- notifications.py         # Notification WebSocket event handlers (new, read, count)
|       |   +-- order_updates.py         # Order status change push handler
|       |   +-- presence.py             # Online/offline, typing, active indicator
|       +-- auth.py                     # WebSocket JWT authentication middleware
+-- tests/
|   +-- conftest.py                     # pytest fixtures: test client, DB session, auth headers
|   +-- unit/                           # Unit tests (domain logic, services, value objects)
|   |   +-- test_domain/
|   |   +-- test_services/
|   +-- integration/                    # Integration tests (repositories, DB, Redis, adapters)
|   |   +-- test_repositories/
|   |   +-- test_adapters/
|   +-- api/                            # API tests (full request-response cycle with TestClient)
|   |   +-- test_auth.py, test_products.py, test_orders.py
|   +-- e2e/                            # End-to-end tests (multi-step business flows)
|       +-- test_checkout_flow.py, test_dispute_flow.py, test_escrow_flow.py
+-- migrations/                         # Alembic migration scripts
|   +-- alembic.ini, env.py, versions/
+-- docs/, scripts/, docker/
+-- .env.example, pyproject.toml, requirements.txt, requirements-dev.txt
```

### Folder Purpose Details

| Folder | Purpose |
|---|---|
| `app/core/` | Foundational infrastructure: configuration loading from environment, database engine setup, security primitives (JWT, hashing, encryption), third-party client initialisation (Redis, ES, S3, Celery), global DI wiring, event dispatcher, logging configuration, and base exception hierarchy. |
| `app/common/` | Shared abstractions used by all modules: base ORM model with common mixins (created_at, updated_at, soft_delete, version lock), generic CRUD repository, service base class, Pydantic base schemas, pagination utilities, standardised response envelope builder, shared enums (OrderStatus, PaymentStatus, UserRole, etc.), and pure utility functions. |
| `app/middleware/` | ASGI middleware that wraps every request: structured request logging, JWT authentication and user context injection, UUID correlation ID generation, CORS policy, Redis-backed rate limiting, locale detection, request timing with slow-request warnings. |
| `app/modules/` | Each module is a self-contained bounded context with five sub-folders: `api/` (FastAPI routers), `application/` (service classes, orchestrators, DTOs), `domain/` (entities, value objects, repository interfaces, domain events), `infrastructure/` (repository implementations, external adapters), and `schemas/` (Pydantic request/response models). |
| `app/tasks/` | Celery task definitions organised by domain: email delivery, push notification dispatch, analytics event tracking, daily report generation, cache warm-up, and periodic cleanup jobs. |
| `app/ws/` | WebSocket subsystem: connection manager (user-to-socket mapping, room/channel subscriptions), domain-specific event handlers (chat messaging, notification push, order status streaming, presence tracking), and WebSocket authentication. |
| `tests/` | Four-tier test suite: `unit/` for domain logic and services (no I/O, mocked dependencies), `integration/` for repositories and adapter implementations (test database, real Redis/ES via Testcontainers), `api/` for full request-response cycle validation (httpx + TestClient, multiple role scenarios), and `e2e/` for multi-step business flow verification (checkout, dispute, escrow). |
| `migrations/` | Alembic-managed database migrations. Each migration is a single-file transaction with upgrade and downgrade functions. Manual review enforces backward compatibility (no destructive column drops without deprecation window). |
| `scripts/` | Developer and operations utilities: database seeding with realistic test data, database reset and migration automation, load test scenario runner (Locust). |
| `docker/` | Containerisation assets: multi-stage Dockerfile (builder stage with full SDK, runtime-slim with only dependencies), Celery worker variant, Docker Compose configuration for development and production, NGINX reverse proxy configuration with security hardening and WebSocket support. |



---

## 4. Module Architecture

Each of the 14 modules follows the same internal structure but has distinct responsibilities, dependencies, public interfaces, and private components.

### 4.1 Auth Module

**Responsibilities:** User registration, login (password + JWT), token refresh, logout, MFA enrolment and verification (TOTP, SMS OTP), OAuth2 social login (Google, Facebook, GitHub), password reset flow, session management, token blacklist maintenance.

**Dependencies:** Users module (for user record lookup and creation), Redis (token blacklist, rate limit counters, MFA session cache), core security utilities (JWT encode/decode, argon2id hashing, TOTP generation), database for refresh token persistence.

**Public Interface:** AuthService.register(), AuthService.login(), AuthService.refresh(), AuthService.logout(), AuthService.verify_mfa(), AuthService.initiate_password_reset(), AuthService.complete_password_reset(), OAuthService.authenticate().

**Private Components:** JWTProvider (token creation and validation), TokenBlacklist (Redis set operations), MFAService (TOTP secret generation, QR code provisioning URI, SMS OTP generation and verification), OAuthAdapter (provider-specific OAuth2 client configuration).

**Shared Components:** User entity (from users module), Role enum, Permission enum.

### 4.2 Users Module

**Responsibilities:** User profile CRUD, address management (multiple addresses per user: billing, shipping, default), email and phone verification, user preferences (locale, timezone, notification settings), account deletion/anonymisation, user search for admin.

**Dependencies:** Auth module (for identity verification during profile changes), core security (PII encryption for sensitive fields), S3 (avatar storage).

**Public Interface:** UserService.get_profile(), UserService.update_profile(), UserService.add_address(), UserService.update_address(), UserService.delete_address(), VerificationService.send_email_verification(), VerificationService.verify_email(), VerificationService.send_phone_verification(), VerificationService.verify_phone().

**Private Components:** AddressValidator, ProfileImageProcessor (resize, compress, upload to S3), PIIEncryptor (AES-256-GCM for sensitive columns), UserSearchAdapter (Elasticsearch indexing for user search).

**Shared Components:** User entity (core identity model used across all modules), Address value object, PhoneNumber value object, UserRole enum.

### 4.3 Marketplace Module

**Responsibilities:** Product CRUD (including variants, images, specifications), category management (hierarchical tree, CRUD, reorder), inventory tracking (stock levels, low-stock alerts, reservations), product search (Elasticsearch full-text, filtered, faceted), product ratings aggregation, product recommendations, bulk product import/export.

**Dependencies:** Users module (seller association), Reviews module (rating aggregation), core infrastructure (ES for search, Redis for product cache, S3 for product images), Image processing (Celery task for thumbnail generation and WebP conversion).

**Public Interface:** ProductService.create_product(), ProductService.update_product(), ProductService.delete_product(), ProductService.get_by_id(), ProductService.list_by_seller(), ProductService.list_by_category(), ProductService.update_inventory(), ProductService.search(), ProductService.get_suggestions(), CategoryService.create_category(), CategoryService.get_tree(), CategoryService.move_category(), InventoryService.reserve_inventory(), InventoryService.release_inventory().

**Private Components:** ProductSearchIndex (ES index mapping, indexing pipeline, query builder), ProductImageProcessor (Celery task for image optimisation and thumbnail generation), InventoryReservationManager (short-lived Redis-based reservation for cart flows), CategoryTreeBuilder (nested set or materialised path computation), BulkImporter (CSV/JSON import with validation pipeline), SlugGenerator (unique URL slug with conflict resolution).

**Shared Components:** Money value object (price), SKU value object, ProductStatus enum (draft, active, inactive, archived), ImageUrl value object.

### 4.4 Orders Module

**Responsibilities:** Cart management (add/remove/update items, apply coupons, calculate totals), checkout orchestration (validate inventory, calculate pricing, apply discounts, create order, initiate payment), order management (view orders, update status, cancellation, returns), shipment tracking (courier integration, tracking number updates, delivery confirmation), order history and filtering.

**Dependencies:** Marketplace module (product data, inventory), Users module (buyer/seller profiles), Payments module (payment intent creation and confirmation), Wallet module (refund processing), Escrow module (escrow creation on order placement), Notifications module (order confirmation emails, status updates), Reviews module (post-delivery review prompt), core infrastructure (Redis for cart caching, Celery for async order processing).

**Public Interface:** CartService.add_item(), CartService.remove_item(), CartService.update_quantity(), CartService.apply_coupon(), CartService.get_cart(), CheckoutService.checkout(), OrderService.place_order(), OrderService.get_order(), OrderService.list_orders(), OrderService.cancel_order(), OrderService.update_status(), ShipmentService.create_shipment(), ShipmentService.update_tracking(), ShipmentService.confirm_delivery().

**Private Components:** CartExpirationManager (abandoned cart cleanup after 7 days), PricingCalculator (subtotal, shipping, tax, discounts, total), CouponValidator (code validity, usage limits, expiry, minimum order value), OrderStatusMachine (explicit state transition map with guards), ReturnProcessor (return request validation, RMA generation, refund triggering).

**Shared Components:** Order aggregate (with OrderItem entities), OrderStatus enum, ShippingMethod enum, Coupon entity, Cart entity.

### 4.5 Payments Module

**Responsibilities:** Payment intent creation and confirmation, payment gateway abstraction (Stripe, SSLCommerz, PayPal, bKash), webhook handling for asynchronous payment events (success, failure, dispute, refund), refund processing (full and partial), payment method tokenisation and storage, payment reconciliation, transaction history.

**Dependencies:** Orders module (order data for payment context), Users module (buyer identification), Wallet module (crediting funds on payment capture), core infrastructure (Redis for idempotency keys, Celery for webhook processing and reconciliation).

**Public Interface:** PaymentService.create_payment_intent(), PaymentService.confirm_payment(), PaymentService.process_webhook(), PaymentService.refund_payment(), PaymentService.get_payment_history().

**Private Components:** GatewayFactory (maps payment method enum to concrete gateway adapter), StripeGateway, SSLCommerzGateway, PayPalGateway, bKashGateway (each implements IPaymentGateway), WebhookVerifier (signature validation per gateway), IdempotencyManager (Redis-backed, 24-hour TTL), PaymentReconciler (Celery task: matches gateway reports with internal transactions), RefundValidator (checks refund eligibility against order/escrow state).

**Shared Components:** PaymentTransaction entity, PaymentStatus enum, Money value object, IPaymentGateway interface (port).

### 4.6 Wallet Module

**Responsibilities:** Balance management (buyer and seller wallets), transaction recording (all balance changes are journal entries), deposits (funds added to wallet via payment gateway), withdrawals (request, approve, disburse), holds (funds reserved but not yet settled), ledger reconciliation, wallet statements and reporting.

**Dependencies:** Payments module (deposit confirmation), Escrow module (escrow release credits seller wallet, escrow hold debits buyer wallet), core infrastructure (Celery for withdrawal processing).

**Public Interface:** WalletService.get_balance(), WalletService.deposit(), WalletService.withdraw(), WalletService.hold_funds(), WalletService.release_hold(), WalletService.get_transaction_history(), LedgerService.get_statement(), WithdrawalService.request_withdrawal(), WithdrawalService.approve_withdrawal(), WithdrawalService.complete_withdrawal().

**Private Components:** LedgerEntryBuilder (double-entry journal: debit one account, credit another), BalanceCalculator (aggregates holds + available + pending across entries), WithdrawalValidator (minimum/maximum amounts, daily limits, KYC status check), DailyLimitManager (per-user withdrawal caps tracked in Redis), WalletReconciler (Celery task: verifies wallet totals against ledger).

**Shared Components:** Wallet entity, LedgerEntry entity, TransactionType enum, Money value object.

### 4.7 Escrow Module

**Responsibilities:** Escrow creation when an order is placed (funds held from buyer), milestone-based release (partial releases for milestone-based orders), full release on delivery confirmation, dispute handling (freeze escrow during dispute), refund processing (return escrowed funds to buyer), escrow status tracking and reporting.

**Dependencies:** Orders module (order lifecycle events trigger escrow actions), Payments module (payment capture confirmation), Wallet module (hold and release operations), Support module (disputes freeze escrow), core infrastructure (Celery for milestone reminder notifications).

**Public Interface:** EscrowService.create_escrow(), EscrowService.release_escrow(), EscrowService.release_milestone(), EscrowService.hold_on_dispute(), EscrowService.refund_escrow(), EscrowService.get_escrow_status(), EscrowService.get_escrow_history().

**Private Components:** EscrowStateMachine (holds to released/refunded/disputed state transitions), MilestoneManager (milestone definition, completion validation, proportional release calculation), ArbitrationService (dispute resolution outcome determination), EscrowFeeCalculator (platform fee deducted from escrow on release).

**Shared Components:** EscrowTransaction entity, EscrowStatus enum, Milestone value object, Money value object.

### 4.8 Reviews Module

**Responsibilities:** Product review submission (rating + text + images), review moderation (auto-flagging suspicious content, admin review queue), rating aggregation (average rating, rating distribution per product), seller feedback (buyer rates seller on communication, shipping speed, accuracy), review helpfulness voting, review reporting.

**Dependencies:** Marketplace module (product association), Orders module (verified purchase check - only buyers who purchased can review), Users module (buyer/seller profiles).

**Public Interface:** ReviewService.submit_review(), ReviewService.edit_review(), ReviewService.delete_review(), ReviewService.get_product_reviews(), ReviewService.get_seller_feedback(), RatingService.get_product_rating(), RatingService.get_seller_rating(), ModerationService.flag_review(), ModerationService.approve_review(), ModerationService.reject_review(), ReviewService.mark_helpful().

**Private Components:** VerifiedPurchaseValidator (checks order history for valid purchase), ReviewContentFilter (profanity filter, spam detection, link whitelist/blacklist), RatingAggregator (materialised view updater for product rating cache), ReviewModerationQueue (prioritised queue of flagged reviews for admin review), ImageValidator (checks uploaded review images for content policy compliance).

**Shared Components:** Review entity, Rating value object, ReviewStatus enum (pending, approved, rejected, flagged).

### 4.9 Chat Module

**Responsibilities:** Conversation management (create between buyer-seller or buyer-support), real-time messaging via WebSocket, message persistence and history, file/attachment sharing (images, documents), typing indicators, delivery and read receipts, conversation search, block/mute functionality.

**Dependencies:** Users module (participant identification), Support module (for buyer-support conversations), core infrastructure (WebSocket connection manager, S3 for file attachments, ES for message search).

**Public Interface:** ChatService.create_conversation(), ChatService.send_message(), ChatService.get_conversation(), ChatService.list_conversations(), ChatService.get_messages(), ChatService.mark_read(), ChatService.delete_message(), ConversationService.block_user(), ConversationService.mute_conversation().

**Private Components:** ConversationValidator (participant eligibility: can buyer message seller before purchase?), AttachmentProcessor (file type/size validation, virus scanning, S3 upload, thumbnail generation), TypingIndicatorManager (debounced per-conversation typing state), ReadReceiptManager (tracks last read message ID per user per conversation), MessageSearchIndex (ES mapping for full-text message search), OfflineMessageQueue (Celery task to deliver push notification for offline recipients).

**Shared Components:** Conversation entity (aggregate), Message entity, Attachment value object, MessageType enum (text, image, file, system).

### 4.10 Notifications Module

**Responsibilities:** Notification creation (system-generated events - order updates, payment confirmations, dispute updates), notification delivery across multiple channels (in-app via WebSocket, email via SendGrid/SES, SMS via Twilio, push via FCM/APNs), notification preferences per user per channel, notification history and read tracking, email and SMS template management, delivery status tracking (sent, delivered, bounced, failed).

**Dependencies:** All modules (consume domain events to create notifications), Users module (preferences, device tokens), core infrastructure (Celery for async delivery, WebSocket for real-time push, S3 for email template storage).

**Public Interface:** NotificationService.create_notification(), NotificationService.send_notification(), NotificationService.mark_read(), NotificationService.mark_all_read(), NotificationService.get_notifications(), NotificationService.get_unread_count(), NotificationService.update_preferences(), NotificationService.get_preferences().

**Private Components:** NotificationRouter (routes notification to appropriate channels based on user preferences and notification priority), EmailRenderer (Jinja2 template rendering with locale support), SMSTemplateManager (template compilation with SMS length validation), PushDeliveryManager (FCM topic subscription, device token management, notification scheduling), BounceHandler (processes email bounce/webhook to mark user email as invalid), DeliveryTracker (Celery task: reconciliation of delivery statuses).

**Shared Components:** Notification entity, NotificationChannel enum (email, sms, push, in_app), NotificationType enum, DeliveryStatus enum, IEmailService interface, ISMSService interface, IPushService interface.

### 4.11 Support Module

**Responsibilities:** Support ticket creation (buyer or seller initiates), ticket assignment (manual or round-robin to support agents), ticket lifecycle management (open, in-progress, waiting on customer, resolved, closed), dispute filing (buyer disputes an order), dispute investigation and resolution, escalation to senior support or management, canned responses and knowledge base integration.

**Dependencies:** Users module (ticket creator and assignee identification), Orders module (dispute context: order details), Escrow module (dispute freezes escrow), Chat module (support conversation linked to ticket), core infrastructure (Celery for escalation reminders and SLA breach notifications).

**Public Interface:** TicketService.create_ticket(), TicketService.assign_ticket(), TicketService.update_ticket(), TicketService.add_comment(), TicketService.resolve_ticket(), TicketService.close_ticket(), DisputeService.file_dispute(), DisputeService.investigate_dispute(), DisputeService.resolve_dispute(), EscalationService.escalate_ticket().

**Private Components:** TicketRouter (intelligent assignment: round-robin for general tickets, skill-based for technical issues), SLAWatcher (monitors ticket age by priority: critical 4hr, high 8hr, medium 24hr, low 72hr), ResolutionRecommender (suggests canned responses based on ticket category and content similarity), DisputeStateMachine (opened to resolved state transitions), EvidenceManager (collects and stores dispute evidence: chat logs, order snapshots, delivery confirmation).

**Shared Components:** Ticket entity, Dispute entity, TicketStatus enum, DisputeStatus enum, TicketPriority enum (critical, high, medium, low).

### 4.12 Affiliate Module

**Responsibilities:** Affiliate registration and onboarding, referral link generation (unique per affiliate per product or general), referral tracking (click tracking via short link, conversion attribution via cookie/UTM), commission calculation (fixed amount or percentage per product category), commission payout (periodic batch payout to affiliate wallet), affiliate dashboard (clicks, conversions, commissions, payouts), fraud detection (self-referral, click fraud).

**Dependencies:** Users module (affiliate identity), Marketplace module (product and commission rate data), Orders module (conversion attribution: which referral led to which order), Wallet module (commission payout), core infrastructure (Redis for click tracking, Celery for commission calculation and payout batch processing).

**Public Interface:** AffiliateService.register_affiliate(), AffiliateService.generate_link(), AffiliateService.track_click(), AffiliateService.get_dashboard(), CommissionService.calculate_commission(), CommissionService.get_pending_commissions(), PayoutService.request_payout(), PayoutService.process_payouts().

**Private Components:** LinkShortener (generates short, trackable URLs), ClickTracker (Redis-based: IP, user agent, referrer, timestamp per link, deduplication logic), AttributionManager (cookie-based attribution with 30-day window, last-click model for multi-touch), CommissionCalculator (tiered commission: base rate times category multiplier times volume bonus), FraudDetector (flags suspicious patterns: same IP as buyer, rapid clicks, self-referral), BatchPayoutProcessor (Celery task: aggregates commissions, generates payout file, submits to wallet module).

**Shared Components:** AffiliateLink entity, Referral entity, Commission entity, CommissionStatus enum, PayoutStatus enum, Money value object.

### 4.13 Analytics Module

**Responsibilities:** Event tracking (user actions: page views, searches, cart adds, purchases), product-level analytics (views, add-to-cart rate, conversion rate, revenue), seller dashboard metrics (orders, revenue, rating, response time), platform-level dashboards (GMV, active users, new listings, dispute rate), report generation (daily, weekly, monthly, custom date range), data retention and archival, export (CSV, Excel, PDF).

**Dependencies:** All modules (events emitted by every module are consumed here), core infrastructure (ES for event storage and aggregation, Celery for report generation and materialised view refresh, Redis for real-time counters).

**Public Interface:** AnalyticsService.track_event(), AnalyticsService.get_product_analytics(), AnalyticsService.get_seller_dashboard(), AnalyticsService.get_platform_dashboard(), AnalyticsService.generate_report(), AnalyticsService.get_realtime_metrics(), ReportService.schedule_report(), ReportService.export_report().

**Private Components:** EventPipeline (validates, enriches, and indexes events into ES), RealtimeAggregator (Redis counters for active users, orders today, revenue today), DashboardBuilder (aggregates data from multiple sources: ES metrics, materialised views, real-time counters), QueryOptimiser (pre-aggregated rollups by hour/day/week/month), ReportScheduler (periodic report generation and distribution), DataArchiver (Celery task: moves events older than 90 days to cold storage), ExportFormatter (converts report data to CSV, Excel, or PDF).

**Shared Components:** AnalyticsEvent entity, EventType enum (page_view, search, cart_add, purchase, review_submitted, etc.), MetricValue value object, Report entity.

### 4.14 Admin Module

**Responsibilities:** User management (CRUD, role assignment, suspension, termination), system settings management (feature flags, configuration values, platform fees, commission rates), audit log viewer and search, moderation queue (reviews, products, disputes), content management (banners, categories, static pages), performance and health monitoring dashboard, support escalation management, privilege escalation and MFA enforcement for admin actions.

**Dependencies:** All modules (admin provides a unified interface to manage resources across all contexts), Users module (admin user identification), core infrastructure (Redis for feature flags, Celery for audit log archival).

**Public Interface:** AdminService.manage_user(), AdminService.assign_role(), AdminService.suspend_user(), AdminService.update_setting(), AdminService.toggle_feature_flag(), AuditService.search_audit_log(), ModerationService.get_queue(), ModerationService.moderate_content(), AdminService.get_system_health().

**Private Components:** FeatureFlagManager (Redis-backed: toggle names with user/role/percentage targeting), SettingsValidator (validates setting values against schema: type, range, allowed values), AuditQueryBuilder (complex multi-criteria search over audit log entries), AdminActionLogger (immutable record of all admin write operations), HealthChecker (aggregates component health: DB, Redis, ES, Celery, S3, payment gateway connectivity), PermissionGate (elevated permission checks for destructive admin actions with MFA re-verification requirement).

**Shared Components:** FeatureFlag entity, SystemSetting entity, AuditLog entity, AdminAction entity.


## 5. Layer Architecture

### 5.1 Presentation Layer

The presentation layer is the outermost boundary, responsible for HTTP/WebSocket interface concerns. It has zero business logic â€” every route handler is a thin adapter that delegates to the application layer.

**Components:**

- **FastAPI Route Handlers**: Async functions decorated with @router.get(), @router.post(), etc. Each handler extracts path and query parameters, invokes the appropriate service method, and returns a serialised response via the response builder.
- **Pydantic Request Validation**: Every route has a typed request schema that FastAPI validates automatically. Schema errors produce consistent 422 responses with field-level detail.
- **Response Serialisation**: Every route has a typed response schema. The response builder wraps data in the standard envelope { success, data, meta }.
- **WebSocket Event Handlers**: Async functions in app/ws/handlers/ process incoming WebSocket messages by event type, delegate to services, and broadcast responses.
- **Middleware Pipeline**: Eight middleware components (logging, auth, request_id, cors, rate_limit, localization, exception, performance) process every request in order before it reaches the route handler.

**Concerns handled here:** HTTP status codes, content negotiation (JSON), caching headers, compression, authentication header extraction, CSRF token validation, CORS enforcement, request ID propagation.

### 5.2 Application Layer

The application layer implements use cases â€” it is the orchestrator that coordinates domain entities, infrastructure adapters, and external services to fulfil a business operation.

**Components:**

- **Service Classes**: Stateless classes (or classes with injected dependencies) that implement a single use case or a group of related use cases. Methods are focused and named after business operations: place_order(), process_payment(), release_escrow().
- **DTOs (Data Transfer Objects)**: Pydantic models that carry data between layers. Request DTOs carry input data from the presentation layer. Response DTOs carry output data to be serialised. DTOs are distinct from domain entities.
- **Orchestrators**: Complex use cases that span multiple services are implemented as orchestrators. The CheckoutOrchestrator calls into cart, pricing, inventory, order, payment, and notification services in a defined sequence with rollback logic.
- **Business Validation**: Cross-entity validation that does not belong in a single domain entity is performed here.
- **Output Serialisation**: Domain entities are transformed into response DTOs before returning to the presentation layer.

**Concerns handled here:** Use case orchestration, transaction management (via Unit of Work), domain event publishing, cross-entity validation, authorisation checks, logging of business operations.

### 5.3 Domain Layer

The domain layer is the heart of the application â€” it contains the business logic, rules, and models that define the marketplace. This layer has zero dependencies on frameworks, databases, or external services.

**Components:**

- **Entities**: Rich domain objects with identity (typically a UUID primary key) and behaviour. An Order entity not only holds order data but also knows how to transition its status, validate line items, and calculate totals.
- **Aggregates**: Consistency boundaries. The Order aggregate includes the Order entity and its OrderItem value objects/entities. All modifications go through the root Order entity, which enforces invariants.
- **Value Objects**: Immutable objects that describe a concept by its attributes, not by an identifier. Money(amount=1000, currency="BDT") is equal to another Money with the same amount and currency.
- **Domain Events**: Plain Python dataclass instances capturing something meaningful that happened in the domain. Events are collected by the Unit of Work and published after transaction commit.
- **Repository Interfaces**: Abstract base classes or Protocols that define how aggregates are persisted and retrieved.
- **Domain Services**: Stateless services that implement domain logic not naturally fitting in an entity. Example: PricingService.calculate_tax().
- **Enums and Constants**: Business enums (OrderStatus, PaymentStatus, UserRole) and constants (MAX_ORDER_ITEMS, MIN_WITHDRAWAL_AMOUNT).

**Concerns handled here:** All business rules, invariants, calculations, validations fundamental to the marketplace domain. This is the most stable and most tested layer.

### 5.4 Infrastructure Layer

The infrastructure layer provides concrete implementations for the interfaces defined in the domain and application layers. It translates between domain concepts and the technical details of databases, caches, filesystems, and external APIs.

**Components:**

- **Repository Implementations**: Concrete classes that implement IProductRepository using SQLAlchemy. They map domain entities to ORM models and vice versa.
- **External Service Adapters**: Classes implementing port interfaces (IPaymentGateway, IEmailService, ISMSService, IPushService, IStorageService). Each encapsulates API client, auth, error handling, retry, and response parsing.
- **Cache Adapters**: Wrappers around Redis with serialisation, TTL management, and invalidation logic.
- **Message Queue Producers/Consumers**: Adapters for publishing domain events to the message broker and consuming events.
- **Search Index Adapters**: ES clients for mapping definitions, document indexing, query building, and result aggregation.
- **File Storage Adapters**: S3/MinIO clients for file operations with presigned URL generation and CDN integration.

**Concerns handled here:** All technical implementation details â€” database access, API calls, serialisation, error handling, retry, connection pooling, credential management.

### 5.5 Persistence Layer

A sub-layer of infrastructure focused specifically on data storage using SQLAlchemy and PostgreSQL:

- **SQLAlchemy ORM Models**: Declarative models mapped to database tables, distinct from domain entities. Repositories handle the mapping between them.
- **Session Management**: Scoped sessions per request via FastAPI dependency. Lifecycle managed by the Unit of Work.
- **Alembic Migrations**: Version-controlled, reviewed for backward compatibility. No destructive column drops without deprecation window.
- **Connection Pooling**: pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600.
- **Query Optimisation**: selectinload and joinedload for eager loading to prevent N+1 queries.

### 5.6 External Service Layer

Manages interactions with third-party providers via the adapter pattern:

- **Payment Gateway Adapters**: StripeGateway, SSLCommerzGateway, PayPalGateway, bKashGateway implementing IPaymentGateway.
- **Email Service Adapters**: SendGridEmailService, SESEmailService implementing IEmailService.
- **SMS Gateway Adapters**: TwilioSMSService and local BD providers implementing ISMSService.
- **Push Notification Adapters**: FCMService, APNsService implementing IPushService.
- **Cloud Storage Adapters**: MinioStorageService, S3StorageService implementing IStorageService.
- **Exchange Rate API**: Daily fetch, cached in currency_rates table, rate recorded at transaction time.

---

## 6. Dependency Injection Strategy

### 6.1 Service Registration

Dependencies are registered and resolved using FastAPI's Depends() function, which acts as the DI container.

**Module-level DI containers:** Each module exposes a dependencies.py with factory functions: auth/dependencies.py provides get_auth_service(), get_mfa_service(), get_oauth_service(). marketplace/dependencies.py provides get_product_service(), get_category_service(), get_search_service().

**FastAPI dependency override for testing:** app.dependency_overrides replaces production deps with test doubles.

### 6.2 Repository Injection

Services depend on repository interfaces, not concrete implementations. Service constructors accept interface types: OrderService.__init__(self, order_repo: IOrderRepository, product_repo: IProductRepository).

DI wiring creates concrete repos with the current DB session and passes them to the service factory.

### 6.3 Configuration Injection

A single Settings class (pydantic-settings) reads env vars, validates, and provides typed access. Injected into components via constructor injection. Per-environment config via .env.dev, .env.test, .env.staging, .env.production.

### 6.4 Singleton Services

| Singleton | Purpose |
|---|---|
| Settings | Application configuration |
| AsyncEngine | DB engine with connection pool |
| Redis client | Cache, rate limiter, pub/sub |
| ES client | Search indexing |
| S3 client | File storage |
| Celery app | Task queue |
| ConnectionManager | WebSocket registry |
| EventBus | Domain event dispatch |
| structlog logger | Structured logging |

### 6.5 Scoped Services

| Scoped Service | Scope |
|---|---|
| AsyncSession | Per request |
| UnitOfWork | Per request |
| CurrentUser | Per request (set by auth middleware) |
| RequestID | Per request (set by request ID middleware) |

### 6.6 Transient Services

Money, Address, PaginationParams, DTOMapper, EventFactory â€” stateless utilities created fresh per injection.

---

## 7. Configuration Management

### 7.1 Environment Variables

All configuration loaded via pydantic-settings:

| Category | Variables |
|---|---|
| Application | APP_NAME, APP_VERSION, DEBUG, ENVIRONMENT, SECRET_KEY, ALLOWED_HOSTS |
| Database | DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW, DATABASE_POOL_RECYCLE, DATABASE_ECHO, DATABASE_STATEMENT_TIMEOUT |
| Redis | REDIS_URL, REDIS_PASSWORD, REDIS_DB, REDIS_SOCKET_TIMEOUT |
| Elasticsearch | ELASTICSEARCH_URL, ELASTICSEARCH_API_KEY, ELASTICSEARCH_INDEX_PREFIX |
| S3/MinIO | S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_REGION, S3_BUCKET_PUBLIC, S3_BUCKET_PRIVATE, S3_CDN_URL |
| JWT | JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS |
| Celery | CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CELERY_WORKER_CONCURRENCY |
| Encryption | ENCRYPTION_KEY, ENCRYPTION_SALT |
| Payment | STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, SSLCOMMERZ_STORE_ID, SSLCOMMERZ_STORE_PASSWORD, PAYPAL_CLIENT_ID, BKASH_API_KEY |
| Email | EMAIL_PROVIDER, SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, AWS_ACCESS_KEY_ID |
| SMS | SMS_PROVIDER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, SMS_SENDER_ID |
| Monitoring | SENTRY_DSN, SENTRY_ENVIRONMENT, OPEN_TELEMETRY_ENDPOINT, PROMETHEUS_METRICS_PORT |
| Rate Limiting | RATE_LIMIT_ANONYMOUS, RATE_LIMIT_AUTHENTICATED, RATE_LIMIT_VERIFIED, RATE_LIMIT_PARTNER |
| Feature Flags | FEATURE_AFFILIATE_ENABLED, FEATURE_ESCROW_ENABLED, FEATURE_MULTI_CURRENCY |
| CORS | CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_MAX_AGE |

### 7.2 Per-Environment Configuration

| Environment | Profile |
|---|---|
| **Development** | Local Docker DB, DEBUG logging, hot reload, CORS permissive, mock external services, SQLAlchemy echo on, Celery eager |
| **Test** | Separate test DB per session, all services mocked, rate limiting off, Celery eager |
| **Staging** | Cloud PG (small), single-node Redis/ES, sandbox external services, Sentry test mode |
| **Production** | PG with replicas, Redis/ES clusters, S3 prod buckets + CDN, live service keys, Sentry full, Prometheus, OpenTelemetry, WAF |

### 7.3 Secrets Management

- .env files never committed (in .gitignore). .env.example documents required vars.
- Production secrets in HashiCorp Vault or AWS Secrets Manager. Application authenticates at startup.
- CI/CD injects secrets via GitHub Actions secrets. Production secrets never exposed in CI.
- DB credentials rotated every 90 days (dual-credential strategy). JWT keys rotated every 180 days.
- AES-256-GCM encryption keys managed externally (Vault/KMS), never in code or database.


---

## 8. Security Architecture

### 8.1 Authentication

**JWT-Based Authentication with Access and Refresh Tokens:**

The platform employs a dual-token JWT authentication model for secure, stateless API access. Access tokens are short-lived (15-30 minutes) and signed using RS256 (asymmetric) in production. The authentication service holds the private signing key; downstream services verify using the public key from /.well-known/jwks.json.

Refresh tokens are long-lived (7-30 days depending on role) and stored in an HTTP-only, secure, SameSite cookie. On each refresh cycle, the server rotates the refresh token - the old token is invalidated and a new pair is issued. If a used refresh token is replayed, all tokens for that user are revoked (theft detection).

A token blacklist in Redis tracks revoked jti claims until natural expiry. Logout, password change, and admin session invalidation add tokens to the blacklist.

**MFA Support:**

TOTP (RFC 6238) via Google Authenticator/Authy for admin roles (mandatory) and sellers (optional). SMS OTP as alternative second factor. MFA session cached 24 hours on trusted devices.

**OAuth2 Social Login:**

Google, Facebook, GitHub via authorization code flow. Email verification enforced for social accounts.

### 8.2 Authorization

**RBAC:** Hierarchical roles: SuperAdmin > Admin > Moderator > Seller > Buyer > Guest. Permissions assigned via role-permission junction table. Permission checks at route level via FastAPI PermissionDependency.

**Row-Level Security (RLS):** PostgreSQL RLS policies on tenant-scoped tables for multi-tenant data isolation. Defence-in-depth beneath application authorisation.

### 8.3 JWT Strategy

Claims: sub (user UUID), role, permissions[], iat, exp, jti (UUID), iss, aud. RS256 signing in production (private key in auth service only, public key via JWKS endpoint). Validation: signature, expiry, issuer, audience, nbf, blacklist.

### 8.4 Refresh Token

Stored in database with device metadata (name, IP, user agent). Rotation on use. Theft detection via reuse. Invalidation on password change, MFA reset, admin revocation. Per-role expiry: admin 7d, seller 14d, buyer 30d, API partner 90d.

### 8.5 Rate Limiting

**Tiered Limits:** Anonymous (30/min), Authenticated (120/min), Verified Seller (300/min), API Partner (1000/min). Burst up to 2x.

**Endpoint-Specific:** POST /auth/login: 5/min per IP. GET /products/search: 30/min.

**Implementation:** Redis sliding window counter. 429 response with Retry-After header.

### 8.6 CORS

Whitelist of allowed origins (production frontend domains + trusted partners). Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS. Credentials enabled for cookie auth. Preflight cache: 3600s.

### 8.7 CSRF

Double-submit cookie pattern for state-changing requests. X-CSRF-Token header must match HTTP-only cookie. SameSite=Lax (default), SameSite=Strict for sensitive ops. API clients use Authorization header only, bypassing CSRF.

### 8.8 XSS Prevention

HTML stripping at API boundary. CSP headers with strict-dynamic. HTTP-only cookies for tokens. X-Content-Type-Options: nosniff.

### 8.9 SQL Injection Prevention

SQLAlchemy ORM parameterises all queries. Raw SQL via text() prohibited without explicit approval. No string concatenation with user input.

### 8.10 Secure Headers

Strict-Transport-Security (2 year preload), X-Content-Type-Options (nosniff), X-Frame-Options (DENY), X-XSS-Protection (1; mode=block), Referrer-Policy (strict-origin-when-cross-origin), Permissions-Policy (camera=(), microphone=(), geolocation=()).

### 8.11 Password Hashing

argon2id (time_cost=3, mem_cost=65536KB, parallelism=4). bcrypt fallback for legacy migration. Password history (10 hashes) prevents reuse. Password change invalidates all sessions.

### 8.12 Encryption

**At Rest:** AES-256-GCM for PII columns (email, phone, bank account). Keys in Vault, never in code. pgcrypto for additional DB-level encryption. EBS volume encryption in production.

**In Transit:** TLS 1.3 (TLS 1.2 fallback). mTLS for VPC internal service-to-service communication.

### 8.13 Sensitive Data Handling

PII masked in logs: email (s****@gmail.com), phone (+880*****789), account (last 4 digits). Passwords, tokens, card details never logged. PCI-DSS: card data never stored/transmitted through app servers - tokenised at gateway. GDPR erasure: anonymisation with irreversible hashing for financial records.

---

## 9. Middleware Architecture

### 9.1 Logging Middleware

Every request logged as structured JSON: method, path, status, duration_ms, client IP, user_id, request_id. Sensitive data redacted (password, token, secret, card_number replaced with [REDACTED]).

### 9.2 Authentication Middleware

Extracts JWT from Authorization header or HTTP-only cookie. Validates signature, expiry, nbf, blacklist. Sets request.state.current_user (id, role, permissions, tenant_id). Optional sliding session (new access token if within 5min of expiry).

### 9.3 Request ID Middleware

UUID v4 correlation ID per request. Accepts client-provided X-Request-ID. Attached to request.state, all log entries, Sentry events, and downstream calls.

### 9.4 Localization Middleware

Locale detection from Accept-Language header > cookie > profile setting. Set in request.state.locale. Affects translation, date/number/currency formatting. Supports lakh/crore notation.

### 9.5 Rate Limit Middleware

Redis-backed check before handler. Returns 429 with Retry-After if exceeded. Distinguishes anonymous (IP), authenticated (user ID), premium (API partner) tiers. Consistent across horizontal instances.

### 9.6 Exception Middleware

Catch-all for unhandled exceptions. Maps exception type to HTTP status. Returns consistent error format. 5xx errors: stack trace logged, generic message returned with request_id.

### 9.7 Audit Middleware

Captures write operations (POST, PUT, PATCH, DELETE): actor, action, resource type/id, timestamp, before/after state. Asynchronous via non-blocking queue. Configurable endpoint set.

### 9.8 Performance Middleware

Wall-clock timing per request. DB query count and duration monitor. WARN at >500ms. ERROR at >2s. Server-Timing header on response.

---

## 10. Exception Handling

### 10.1 Global Exception Strategy

All exceptions inherit AppException. FastAPI exception_handlers map types to handlers. Consistent JSON error format:

{ "status": 422, "code": "validation_error", "message": "...", "details": [{ "field": "price", "message": "Must be positive" }], "request_id": "...", "timestamp": "..." }

### 10.2 Exception Hierarchy

AppException (500) -> ValidationException (422), AuthenticationException (401), AuthorizationException (403), NotFoundException (404), ConflictException (409), RateLimitException (429), BusinessException (400/422), ServiceUnavailableException (503).

### 10.3 Validation Errors

Pydantic errors -> 422 with field-level detail. Service-layer business validation -> BusinessException with machine-readable code.

### 10.4 Business Errors

Standard codes: insufficient_funds, product_unavailable, order_not_cancellable, escrow_already_released, duplicate_dispute, withdrawal_limit_exceeded.

### 10.5 Database Errors

Connection timeout -> 503 with Retry-After hint. Deadlock -> retry 3x with exponential backoff (100ms, 500ms, 2s). Constraint violation -> 409 with constraint name. OperationalError -> 503 with alert.

### 10.6 External Service Errors

Payment gateway timeout -> 502. Email failure -> logged + queued for retry (API never fails for email). S3 failure -> 503 with retry suggestion.

### 10.7 Security Errors

Invalid token -> 401 invalid_token. Expired -> 401 token_expired. Insufficient permissions -> 403 insufficient_permissions. Suspicious activity -> 403 suspicious_activity + security_logs entry.

---

## 11. Logging Strategy

### 11.1 Application Logs

Structured JSON via structlog. Fields: timestamp (ISO8601), level, logger, message, request_id, user_id, path, method, status, duration_ms. Levels: DEBUG (dev only), INFO (business events), WARN (handled issues), ERROR (unhandled), CRITICAL (system down). Output to stdout (container). Collected by Loki/Elasticsearch/Datadog.

### 11.2 Audit Logs

Immutable database table: actor_id, action, resource_type, resource_id, changes (JSON diff), created_at. 3 years online, 7 years archived. Generated by audit middleware on write ops.

### 11.3 Security Logs

Partitioned monthly: failed logins, permission denied, API abuse, suspicious activity, password changes, MFA events, admin actions. 1 year online, 3 years archived.

### 11.4 Performance Logs

Slow requests (>500ms WARN, >2s ERROR) with breakdown. PostgreSQL auto_explain for queries >100ms. Cache hit ratio every 5min. Connection pool utilisation every 1min. Shipped to APM provider.

### 11.5 Log Retention

| Source | Online | Archive |
|---|---|---|
| stdout | 7 days | â€” |
| Audit DB | 3 years | 7 years |
| Security DB | 1 year | 3 years |
| APM | 30 days | â€” |

---

## 12. Caching Strategy

### 12.1 Redis Cache Layers

| Domain | TTL | Invalidation |
|---|---|---|
| Session | 30 min | Logout/password change |
| Product | 5 min | Product update/delete |
| Category | 1 hour | Category CRUD |
| Search | 2 min | New product publish |
| Permission | 10 min | Role/permission change |
| Config | 5 min | Admin settings update |
| Translation | 24 hours | Translation update |
| Cart | 7 days | Cart modification/order |
| Rate Limit | Per-window | Auto-expiry |

### 12.2 Cache Patterns

**Cache-Aside:** Read -> miss -> DB -> populate cache. **Write-Through:** Update DB + write cache in same request. **Write-Behind:** Update DB, async task refreshes cache (for high-throughput counters). **Invalidation:** Delete key on mutation; next read triggers fresh load.

### 12.3 Invalidation Rules

Product change -> invalidate product + category count + search. Order change -> invalidate order + buyer dashboard + seller dashboard. User change -> invalidate user + permission. Category change -> invalidate tree + product counts. Permission change -> global SCAN delete + pub/sub broadcast for multi-instance.

---

## 13. Background Jobs (Celery)

### 13.1 Celery Configuration

Broker: Redis (RabbitMQ in production for guaranteed delivery). Result backend: Redis (short-lived) / PostgreSQL (persistent). Task serialisation: JSON. Concurrency: 6-8 workers (gevent for I/O-bound). Prefetch multiplier: 1 (fair scheduling).

### 13.2 Task Queue Architecture

| Queue | Priority | Workers |
|---|---|---|
| default | Medium | 4 |
| high_priority | High (payments, orders) | 6 |
| low_priority | Low (analytics, cleanup) | 2 |
| email | Medium | 2 |
| notification | Medium | 2 |

### 13.3 Retry Strategy

Transient errors: max 3 retries (60s, 300s, 900s). Business errors: no retry, fail immediately. Dead letter queue after max retries.

### 13.4 Dead Letter Queue

Dedicated dead_letter queue with no consumers. Alert at >10 tasks. Admin dashboard for inspection, retry, or discard.

### 13.5 Task Definitions

**Email:** send_welcome_email, send_order_confirmation, send_password_reset, send_payment_receipt, send_dispute_update, send_escrow_release.

**Notification:** send_in_app_notification, send_push_notification, send_sms.

**Analytics:** track_event, generate_daily_report, update_seller_dashboard (15min), refresh_materialized_views (30min).

**Cleanup:** cleanup_expired_sessions (daily 02:00), cleanup_temp_files (daily 03:00), archive_old_records (weekly Sun 04:00), purge_soft_deleted (monthly 1st 05:00).

---

## 14. Realtime Architecture (WebSocket)

### 14.1 WebSocket Server

FastAPI native WebSocket on ASGI layer. Authentication via JWT query parameter on handshake (wss://api.tsbl.com/ws?token=<jwt>). Rejected with 4001 if invalid. Ping/pong every 30s with 10s timeout for stale connection detection.

### 14.2 Connection Manager

In-memory map: user_id -> [WebSocket connections]. Room/channel subscription model (orders:{order_id}, chat:{conversation_id}, notifications:{user_id}). New connection closes old one (4003, "replaced"). 5-min grace period on disconnect before marking offline.

### 14.3 Chat

Messages sent via { type: "chat:send", conversation_id, content, attachments }. Persisted, broadcast to participants, acknowledged with chat:delivered. Status chain: sent -> delivered -> read (toggleable). Typing indicators debounced with 2s inactivity timeout. File upload via pre-signed URL with progress/complete events. History via REST.

### 14.4 Presence

presence:online / presence:offline events on connect/disconnect. last_seen updated on full disconnect. Active conversation indicator from channel subscription. Privacy settings to hide last_seen.

### 14.5 Order Updates

Events pushed to orders:{order_id}: order:placed, order:confirmed, order:shipped, order:delivered, order:cancelled, order:refunded, payment:confirmed, payment:failed, escrow:released, dispute:opened, dispute:resolved.

### 14.6 Notification Updates

notifications:update event with content + unread count. Client emits notifications:read on view/click. Service worker converts to browser push notification when tab not focused.


---

## 15. External Service Integration

### 15.1 Payment Gateway

**Adapter Pattern:** All payment gateways implement a common IPaymentGateway interface defined in the payments module's domain layer. Switching between Stripe, SSLCommerz, PayPal, and bKash requires only a configuration change.

**IPaymentGateway Interface Methods:** create_intent(), confirm_intent(), process_webhook(), refund(), get_transaction_status().

**Supported Gateways:**

| Gateway | Region | Use Case |
|---|---|---|
| Stripe | Global | Primary international card payments |
| SSLCommerz | Bangladesh | Primary local payments (cards, mobile banking, AMEX) |
| PayPal | Global | International PayPal account payments |
| bKash | Bangladesh | Mobile wallet payments (Bangladesh market leader) |

**Webhook Endpoint:** Single POST /api/v1/payments/webhook endpoint receives events from all gateways. GatewayFactory identifies the originating gateway. WebhookVerifier validates signatures per gateway.

**Idempotency Keys:** All payment mutation requests require an Idempotency-Key header. IdempotencyManager stores key-to-response mapping in Redis with 24-hour TTL.

**Tokenisation:** Payment method details never stored on TSBL servers. Gateway tokens stored instead. Recurring payments use gateway customer vault.

### 15.2 Email Service

**Adapter Pattern:** IEmailService interface. Supported providers: SendGrid, Amazon SES.

**IEmailService Methods:** send_single(), send_bulk(), send_template(), verify_address().

**Template Management:** Jinja2 templates stored in S3 with locale-specific variants (en, bn). EmailRenderer compiles templates with context.

**Email Queue:** All emails sent asynchronously via Celery dedicated email queue.

**Bounce Handling:** Webhooks from SendGrid/SES processed by BounceHandler. Hard bounces mark email invalid. Soft bounces trigger retry. Complaints trigger unsubscription.

### 15.3 SMS Gateway

**Adapter Pattern:** ISMSService interface. Primary providers: Twilio (international), GreenWeb, BulkSMSBD (Bangladesh domestic).

**ISMSService Methods:** send(), send_bulk(), get_delivery_status().

**Transactional SMS Usage:** OTP for MFA, password reset, order updates (opt-in), dispute notifications, withdrawal confirmation. No marketing SMS.

**Bangladesh Regulatory Compliance:** BTRC requires registered sender ID (6-11 alphanumeric), routing through approved aggregators, dedicated sender IDs for transactional SMS.

### 15.4 Push Notification

**Adapter Pattern:** IPushService interface. FCM (Android/web), APNs (iOS).

**IPushService Methods:** send_to_token(), send_to_topic(), subscribe_to_token(), unsubscribe_from_token().

**Device Token Management:** Tokens stored with platform metadata. Invalid tokens (InvalidRegistration, Unregistered) marked inactive. Cleanup removes tokens inactive >90 days.

**Topic-Based Push:** Users subscribed to topics by role: all_users, buyers, sellers, user_{user_id} (personal). Bulk notifications sent via topics.

### 15.5 Cloud Storage

**Adapter Pattern:** IStorageService interface. MinIO (dev/staging), AWS S3/DigitalOcean Spaces (production).

**IStorageService Methods:** upload_file(), get_file(), delete_file(), get_presigned_url(), list_files().

**Bucket Structure:**

| Bucket | Visibility | Purpose |
|---|---|---|
| tsbl-public | Public read | Product images, category icons, banners |
| tsbl-private | Private (presigned URL) | Chat attachments, dispute evidence, reports |
| tsbl-avatars | Public read | User profile images |
| tsbl-temp | Private (short TTL) | Temporary upload staging |

**Image Processing:** Celery task processes uploaded images: resize to standard dimensions, convert to WebP, extract dominant colour for placeholder, generate responsive srcset variants.

**CDN Integration:** Public bucket content served through CDN (CloudFront/Cloudflare). Cache TTL: product images 7 days, category icons 30 days, static assets 1 year.

### 15.6 Exchange Rate API

ExchangeRateService fetches daily rates from provider (OpenExchangeRates, ExchangeRate-API, Bangladesh Bank). Rates cached in Redis and currency_rates table. Rate at transaction time recorded immutably for audit trail. Supported currencies: BDT (default), USD, EUR, GBP, INR.

---

## 16. API Design Standards

### 16.1 REST Naming Conventions

- **Nouns, not verbs**: Resources named as nouns (/products, /orders, /users), never verbs.
- **Plural forms**: Collection resources use plural: /api/v1/products.
- **HTTP methods indicate action**: GET (retrieve), POST (create), PUT (full replace), PATCH (partial update), DELETE (remove).
- **Nesting for relationships**: /api/v1/products/{product_id}/reviews. Limited to two levels.
- **Versioning in URL path**: /api/v1/.

### 16.2 Versioning

- **Primary**: URL path versioning (/api/v1/). Incremented on breaking changes.
- **Secondary (optional)**: Accept-Version header for negotiated versioning.
- **Deprecation**: Deprecated endpoints function for min 6 months with Deprecation header, then return 410 Gone.

### 16.3 Response Format

**Successful Response:**
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601",
    "version": "1.0"
  }
}

**Paginated Response:**
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "pagination": {
      "cursor": "base64",
      "next_cursor": "base64",
      "has_more": true,
      "limit": 20
    }
  }
}

### 16.4 Error Format (RFC 7807)

{
  "success": false,
  "error": {
    "type": "https://api.tsbl.com/errors/validation_error",
    "title": "Validation Error",
    "status": 422,
    "detail": "Human-readable message.",
    "instance": "/api/v1/products",
    "errors": [
      { "field": "price", "message": "Must be positive", "code": "invalid_value" }
    ],
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}

### 16.5 Pagination

**Cursor-Based (Preferred):** GET /api/v1/products?cursor=base64&limit=20. Response includes next_cursor and has_more. Base64-encoded opaque sort key. Stable with concurrent inserts/deletes.

**Offset-Based (Alternative):** GET /api/v1/products?page=1&size=20. Used for admin interfaces and small datasets. Default limit 20, max 100.

### 16.6 Filtering and Sorting

**Filtering:** Query parameters: ?category=electronics&status=active&min_price=100&max_price=5000. Multiple values: ?status=active,pending (OR). Range: ?created_after=2026-01-01.

**Sorting:** ?sort=created_at (ascending). ?sort=-created_at (descending). ?sort=price,-created_at (multi-field).

### 16.7 Search

**Simple Search:** GET /api/v1/products/search?q=laptop. Full-text across name, description, tags.

**Filtered Search:** Combine q with filter params: ?q=laptop&category=electronics.

**Faceted Search:** ?q=phone&facets=true returns counts per category, brand, price range, rating.

**Implementation:** All search queries hit Elasticsearch. Index synced via event-driven indexing. 2-minute search cache TTL.

### 16.8 Idempotency

Required for all financial mutation endpoints via Idempotency-Key header (client UUID v4). Redis-backed mapping with 24-hour TTL. Replayed successful keys return stored response. Expired keys treated as new.

### 16.9 Correlation IDs

X-Request-ID header (UUID v4). Generated by server if not provided. Propagated to logs, downstream HTTP calls (as header), Celery task context, and error responses.

---

## 17. Validation Strategy

### 17.1 Pydantic Models (Request Validation)

Every endpoint has a typed request schema. FastAPI validates automatically. Custom validators via @field_validator (per-field) and @model_validator (cross-field). Strict mode (model_config = {"strict": True}) rejects unknown fields with 422.

### 17.2 Business Validation (Service Layer)

Business rules enforced in service layer: stock availability checks, order state transition guards, payment eligibility (KYC, daily limits), escrow milestone validation. Failures raise BusinessException with specific error code.

### 17.3 Database Validation (PostgreSQL)

Schema-level constraints: NOT NULL, UNIQUE (partial unique index for soft-delete: WHERE deleted_at IS NULL), CHECK (price >= 0, rating BETWEEN 1 AND 5), FOREIGN KEY with appropriate ON DELETE behavior. Optimistic locking via version column for concurrent modification detection.

### 17.4 Input Sanitisation

HTML stripping via bleach library. Whitelist of safe tags for rich-text fields only. File upload validation: MIME type, extension, size (10MB images, 25MB documents), virus scan (ClamAV via Celery), image dimensions. Filename sanitisation: remove paths, strip non-ASCII, spaces to hyphens, UUID prefix. URL validation with domain blacklist.

### 17.5 Output Serialisation

Response schemas control field exposure. Internal fields never serialised. Conditional inclusion per role (seller email to buying customer only, prices by customer tier). Field transformation: password excluded, timestamps ISO8601, Money serialised as {amount, currency}, file paths to full CDN URLs.

---

## 18. Performance Strategy

### 18.1 Lazy Loading vs Eager Loading

Default: lazy loading (simple queries). Explicit eager loading for known N+1 patterns: selectinload for collections, joinedload for single references. N+1 detection middleware warns in dev/staging. CI asserts zero N+1 queries for critical endpoints.

### 18.2 Pagination

Cursor-based for large lists (products, orders, messages). Default 20, max 100. Offset-based for admin interfaces with total count requirement.

### 18.3 Bulk Operations

SQLAlchemy bulk_insert_mappings and bulk_update_mappings for batch imports. Batch sizing at 1000 records per chunk. Celery tasks for large-scale data operations.

### 18.4 Connection Pooling

PgBouncer for transaction pooling (200-500 connections). SQLAlchemy pool_size=10, max_overflow=20. Statement timeout 30s. pool_pre_ping=True for stale connection detection. Read replicas for reporting queries.

### 18.5 Caching

Redis cache-aside with TTLs: products 5min, categories 1hr, search 2min, permissions 10min, config 5min, translations 24hr. Invalidation on mutation. Write-through for critical data, write-behind for high-throughput counters.

### 18.6 Compression

gzip/brotli compression at NGINX level. Image compression (WebP with PNG fallback) on upload. Minified responses via FastAPI middleware.

### 18.7 Streaming

S3 presigned URLs for file downloads (avoid proxying through app server). Server-Sent Events (SSE) for real-time metric streams. Async generators for large dataset exports.

---

## 19. Scalability Strategy

### 19.1 Horizontal Scaling

Stateless application servers behind NGINX load balancer. Multiple Gunicorn + Uvicorn workers (2-4 per core). Session state externalised to Redis. Distributed rate limiting via Redis.

### 19.2 Vertical Scaling

Server upgrades for PostgreSQL (CPU, RAM, fast SSD). Redis memory scaling for larger cache footprints. ES node scaling for search throughput.

### 19.3 Read Replicas

PostgreSQL primary for writes, replicas for reads. Read/write splitting via SQLAlchemy binds (create_async_engine for primary, create_async_engine for replicas with routing). Lag tolerance: non-critical reads (product listings, analytics) can use replicas with seconds-old data. Critical reads (wallet balance, order status) always hit primary.

### 19.4 Background Workers

Celery auto-scaled by queue depth. Pool sizes: high_priority 6 workers, default 4, low_priority 2, email 2, notification 2. Prefetch multiplier 1 for fair scheduling.

### 19.5 Microservice Migration Plan

**Phase 1 - Modular Monolith (current):** Strict bounded contexts, shared database with schema-level isolation, in-process service calls, event bus for cross-context communication. Single deployment unit.

**Phase 2 - Extraction of Payments:** Extract payments module into standalone service first (highest traffic + PCI scope). Shared library for IPaymentGateway interface. Database migration: extract payment tables to separate schema/service DB. Event-driven communication with monolith (async for notifications, sync + retry for financial operations).

**Phase 3 - Extraction of Orders + Products:** Extract orders and marketplace modules. Each gets own database. API gateway routes external requests. Event bus for inter-service communication. Eventually consistent cross-service transactions with saga pattern (compensating transactions for order/payment failures).

**Phase 4 - Fully Distributed:** Per-service databases, event bus as primary integration pattern, API gateway for external routing, service mesh for inter-service communication. Remaining modules extracted as needed.

---

## 20. Monitoring Strategy

### 20.1 Health Check

GET /api/v1/health returns overall status and per-component results:

| Component | Check |
|---|---|
| Database | SELECT 1, connection pool utilisation |
| Redis | PING, memory usage |
| Elasticsearch | Cluster health, index status |
| Celery | Worker availability, queue depths |
| S3 | Bucket accessibility |
| Payment gateways | API key validity (lightweight ping) |

Liveness probe (simple HTTP 200) and readiness probe (full component check) for Kubernetes/container orchestration.

### 20.2 Metrics (Prometheus)

| Metric Category | Key Metrics |
|---|---|
| HTTP | Request count, duration (p50/p95/p99), status code distribution |
| Database | Active/idle/waiting connections, query execution time, pool utilisation |
| Redis | Cache hit ratio, memory used, connected clients, command rate |
| Celery | Queue depth per queue, task duration (p95), success/failure rate, worker count |
| Elasticsearch | Index size, query latency, indexing rate, cluster health |
| Business | Active users, new registrations, orders placed, GMV, payment success rate, dispute rate |
| System | CPU usage, memory usage, disk I/O, network I/O |

All metrics exposed via /metrics endpoint (prometheus_client or opentelemetry). Scraped by Prometheus every 15 seconds.

### 20.3 Tracing (OpenTelemetry)

Distributed tracing with trace ID propagated via W3C Trace Context. Spans for: HTTP handler (full request lifecycle), service method (business logic time), database query (SQL + params, execution time), external API call (provider, endpoint, duration, status).

Sampling strategy: 100% for error spans, 10% for normal requests (head-based sampling). Traces exported to Jaeger, Zipkin, or Datadog APM.

### 20.4 Alerting

**Critical (PagerDuty/on-call):**
- Service down (health check fails for >30s)
- Error rate >5% of total requests in 5-min window
- Database connection pool exhausted
- Celery queue depth >10,000 for high_priority queue
- Payment gateway timeout >10% of requests

**Warning (Slack channel):**
- Response time p95 >1s for 5 minutes
- Error rate >1% for 10 minutes
- CPU >80% for 15 minutes
- Memory >85% for 15 minutes
- Cache hit ratio <80% for 30 minutes
- Disk usage >80%

### 20.5 Dashboards (Grafana)

Three dashboard tiers:

| Dashboard | Audience | Content |
|---|---|---|
| Operations | SRE/DevOps | System metrics, component health, deployment status, error rates, latency |
| Engineering | Developers | Service metrics, DB query performance, cache efficiency, queue depths, trace explorer |
| Business | Product/Management | Active users, orders, revenue, GMV, seller onboarding, dispute rate, conversion funnel |

---

## 21. Testing Strategy

### 21.1 Unit Tests

**Scope:** Domain entities, value objects, domain services, utility functions, state machines.

**Tools:** pytest, pytest-asyncio, unittest.mock.

**Coverage Target:** 90%+ for domain layer, 80%+ overall.

**Pattern:** Given-When-Then. Mock all database and network dependencies. Test pure business logic in isolation.

### 21.2 Integration Tests

**Scope:** Repository implementations, cache adapters, external service adapters (with wiremock/testcontainers), database queries, migration validation.

**Tools:** pytest, SQLAlchemy async fixtures, Testcontainers (PostgreSQL, Redis, Elasticsearch), Factory Boy for test data generation.

**Approach:** Test database created per session via Docker container. Fixtures seed test data. Queries executed against real database. Redis/ES containers for cache and search tests.

### 21.3 API Tests

**Scope:** Full request-response cycle through FastAPI TestClient (httpx). Authentication flows, CRUD operations, error scenarios, pagination, filtering.

**Tools:** httpx, FastAPI TestClient, pytest.

**Coverage:** All endpoints tested with at least 3 scenarios: success case, validation error case, authorisation error case. Test with multiple roles (guest, buyer, seller, admin).

**Validation:** Response status codes, response body structure (JSON Schema), pagination structure, error format compliance.

### 21.4 Security Tests

**Scope:** OWASP Top 10 coverage:

| Category | Test |
|---|---|
| Injection | SQL injection attempts, NoSQL injection, command injection |
| Broken Auth | Token manipulation, session fixation, MFA bypass |
| XSS | Script injection in all text fields |
| Broken Access Control | Role escalation, horizontal privilege escalation, IDOR |
| Sensitive Data Exposure | PII in logs, error messages, response bodies |
| Rate Limiting | Brute force attempts, DoS simulation |
| CSRF | Missing/wrong token scenarios |

**Tools:** OWASP ZAP (DAST), bandit (SAST), safety/pip-audit (dependency scanning).

### 21.5 Load Tests

**Tools:** k6 (primary) or Locust.

**Scenarios:**

| Scenario | Concurrency | Target |
|---|---|---|
| Browse | 100 concurrent users browsing products | p95 <500ms, error <0.1% |
| Search | 50 concurrent users searching | p95 <800ms, error <0.1% |
| Order Flow | 20 concurrent users completing checkout | p95 <2s (including payment), error <0.1% |
| Dashboard | 10 concurrent admin dashboard views | p95 <3s, error <0.5% |
| Mixed | 200 concurrent users (60% browse, 20% search, 15% order, 5% admin) | All targets met simultaneously |

### 21.6 Stress Tests

| Type | Description | Success Criteria |
|---|---|---|
| Spike | 10x normal load for 1 minute | Graceful degradation, no crash, auto-recovery within 30s of load drop |
| Soak | Sustained 2x normal load for 4 hours | No memory leak, no throughput degradation |
| Breakpoint | Load incrementally increased until failure | Identify maximum capacity, graceful failure (503, not crash) |

---

## 22. Coding Standards

### 22.1 PEP 8 Compliance

Enforced via ruff/flake8. Line length: 88 characters (Black default). Indentation: 4 spaces. Blank lines: 2 around functions, 2 around classes. Imports: isort with Black-compatible profile.

### 22.2 Type Hints

Mandatory for all function signatures and public class attributes. mypy in strict mode. Use: Optional[T], Union[T, U], list[T], dict[K,V], Protocol for structural subtyping, TypeVar for generics. No untyped functions in production code.

### 22.3 Docstrings

Google-style docstrings required for all public functions, classes, and methods:

def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: Description of when this is raised.
    """

### 22.4 Naming Conventions

- PascalCase: Classes, enums, type aliases, dataclasses
- snake_case: Functions, methods, variables, parameters, module names
- UPPER_SNAKE_CASE: Constants, environment variable names, enum members
- _private_prefix: Private methods, attributes, and internal functions
- __name_mangling: Only for framework-required name mangling (SQLAlchemy hybrid properties)
- I prefix: Interface/base class names (IProductRepository)
- Abstract prefix: Abstract base classes (AbstractPaymentGateway)

### 22.5 SOLID Principles

| Principle | Application |
|---|---|
| Single Responsibility | Each class has one reason to change. Services focus on one use case. |
| Open/Closed | Classes open for extension (inheritance, composition), closed for modification. |
| Liskov Substitution | Subtypes must be substitutable for their base types. Repository interfaces guarantee this. |
| Interface Segregation | Many small, focused interfaces (IEmailSender, ISMSProvider) not one monolithic IService. |
| Dependency Inversion | Domain depends on abstractions (interfaces), not concretions. Infrastructure implements abstractions. |

### 22.6 DRY, KISS, YAGNI

- **DRY (Don't Repeat Yourself)**: Shared logic extracted into common utilities, base classes, or mixins. Repository base provides common CRUD. Service base provides UoW and event dispatcher.
- **KISS (Keep It Simple, Stupid)**: Simple solutions preferred over clever ones. If a for loop is clearer than a complex comprehension, use the for loop.
- **YAGNI (You Ain't Gonna Need It)**: Implement only what the current requirement specifies. Avoid speculative generality. Abstract only when there is a proven second implementation.

---

## 23. Development Workflow

### 23.1 Git Branches

| Branch | Purpose | Source | Target |
|---|---|---|---|
| main | Production-ready code | Stable | â€” |
| develop | Integration branch for features | Main | â€” |
| staging | Pre-production verification | develop | â€” |
| feature/{ticket}-{desc} | New feature development | develop | develop |
| bugfix/{ticket}-{desc} | Bug fixes | develop | develop |
| hotfix/{ticket}-{desc} | Critical production fixes | main | main + develop |
| release/v{major}.{minor}.{patch} | Release preparation | develop | main |

### 23.2 Commit Convention (Conventional Commits)

Format: type(scope): description

| Type | Usage |
|---|---|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation changes |
| refactor | Code restructuring (no functional change) |
| test | Test additions/modifications |
| chore | Build, CI, dependency changes |
| perf | Performance improvement |
| breach | BREAKING CHANGE (adds BREAKING CHANGE footer) |

Examples:
- feat(auth): add MFA TOTP enrolment endpoint
- fix(payments): correct webhook signature verification for SSLCommerz
- refactor(orders): extract pricing logic into domain service
- chore(deps): upgrade SQLAlchemy to 2.0.30

### 23.3 Code Review Process

**Minimum Reviewers:** 1 for standard modules, 2 for core modules (payments, orders, auth, marketplace).

**Checklist:**

- Correctness: Does the code implement the requirement correctly? Edge cases handled?
- Security: Input validation, authorisation checks, no hard-coded secrets, SQL injection prevention?
- Performance: N+1 queries avoided? Caching considered? Bulk operations where appropriate?
- Testing: Unit tests for domain logic? Integration tests for repositories? API tests for endpoints?
- Style: Ruff/Black compliance? Type hints present? Docstrings for public APIs?
- Architecture: Dependency direction correct? Module boundaries respected? No circular imports?

**Gate:** CI must pass (lint, type-check, tests, security scan). PR must be approved. No self-approval.

### 23.4 Release Process

1. **Create release branch**: release/v1.2.0 from develop
2. **Regression tests**: Full test suite + manual smoke tests on staging
3. **Version bump**: Update VERSION, changelog, commit
4. **Tag**: git tag v1.2.0
5. **Merge to main**: Release branch merged to main
6. **Deploy staging**: Build + deploy to staging for final verification
7. **Smoke tests**: Automated smoke tests + manual exploratory testing
8. **Deploy production**: Blue-green deployment
9. **Monitor**: Watch dashboards for 30 minutes post-deploy
10. **Merge back**: Release branch merged back to develop

---

## 24. Deployment Strategy

### 24.1 Docker

**Multi-Stage Build:**

- **Builder stage**: Full Python SDK, dependencies installed, code compiled/validated.
- **Runtime stage**: python:3.13-slim base, only runtime dependencies copied. Non-root user (appuser). HEALTHCHECK instruction. Graceful shutdown on SIGTERM.

**Docker Compose (Dev):** api, worker (celery), beat (celery-beat), postgres, redis, elasticsearch, minio, nginx.

**Docker Compose (Prod override):** Resource limits, healthchecks, restart policies, volume mounts for certs, log drivers.

### 24.2 NGINX

**Configuration:**

- **Reverse proxy**: Proxy pass to Gunicorn/Uvicorn upstream.
- **SSL/TLS**: TLS 1.3 only, strong ciphers, HSTS preload, automated cert renewal via Certbot.
- **Rate limiting**: Per-IP burst limits at NGINX level (first line of defence before application rate limiters).
- **Compression**: gzip/brotli for text content (HTML, JSON, CSS, JS).
- **WebSocket support**: Upgrade headers, proxy_read_timeout increased for long-lived connections.
- **Static files**: Direct serve for /static/ (no proxy to app).
- **Health check pass-through**: /health and /metrics bypass proxy to app.

### 24.3 CI/CD (GitHub Actions)

**CI Pipeline (on PR to develop/main):**

1. Lint (ruff check)
2. Type check (mypy strict)
3. Unit tests (pytest unit/)
4. Build Docker image (verify Dockerfile)
5. Security scan (trivy/clair on image)
6. Dependency audit (safety/pip-audit)
7. Integration tests (pytest integration/ with Testcontainers)
8. API tests (pytest api/)
9. E2E tests (pytest e2e/)

**CD Pipeline (on merge to main):**

1. Build + tag Docker image (git SHA + semver)
2. Push to container registry (Docker Hub, ECR, GHCR)
3. Deploy to staging environment
4. Run smoke tests
5. Manual approval gate
6. Blue-green production deployment
7. Post-deploy smoke tests
8. Rollback if smoke tests fail (switch NGINX upstream back to blue)

### 24.4 Blue-Green Deployment

- Two identical environments (blue = current, green = new).
- NGINX upstream points to blue initially.
- Green environment is warmed up (health checks pass, cache preloaded).
- NGINX upstream switches from blue to green.
- Blue retained for 30 minutes (quick rollback by switching upstream back).
- After 30 minutes of monitoring, blue is decommissioned.

### 24.5 Rollback Procedures

| Scenario | Rollback Action | Recovery Time |
|---|---|---|
| Bad deployment | NGINX upstream switch to previous | <1 minute |
| Bad schema migration | Alembic downgrade + feature flag to disable affected path | <5 minutes |
| Service unresponsive | Scale up + restart pods | <2 minutes |
| Data corruption | Restore from point-in-time backup (15-min RPO) | <30 minutes |
| Security incident | Kill switch feature flag + NGINX block | <1 minute |

Runbooks for each scenario documented in ops repository. Automated rollback triggers for health check failures.

---

## 25. Final Architecture Summary

TRUE STAR BD LIMITED's backend is a **Production-Ready Modular Monolith** built on Python 3.13+, FastAPI, PostgreSQL, Redis, Elasticsearch, and Celery. It is designed from day zero to scale to microservices with minimal friction.

### Core Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Module Structure | 14 bounded contexts (DDD) | Clear ownership, independent evolvability |
| Layer Pattern | Clean Architecture + Hexagonal | Domain purity, testability, framework independence |
| Internal Communication | Event-driven (sync + async) | Loose coupling, eventual consistency where appropriate |
| API Design | RESTful with cursors + idempotency | Scalable, resilient, standards-compliant |
| Authentication | JWT (RS256) + OAuth2 + MFA | Stateless, secure, multi-provider |
| Authorisation | RBAC + RLS | Defence in depth, multi-tenant isolation |
| Performance | Redis caching, PgBouncer, eager loading | Sub-500ms p95, 99.9% uptime target |
| Background Jobs | Celery with 5 queues | Priority-based processing, async resilience |
| Real-time | WebSocket with connection manager | Live updates, presence, chat |
| Observability | structlog, OpenTelemetry, Prometheus | Full traceability, proactive alerting |
| Testing | 4-layer pyramid + security + load | Enterprise-grade quality assurance |
| Deployment | Docker + NGINX + Blue-Green | Zero-downtime, immediate rollback |

### Why Production-Ready

1. **Security by Design**: JWT with RS256 asymmetric signing, argon2id password hashing, AES-256-GCM encryption at rest, TLS 1.3 in transit, RBAC with RLS, CSRF double-submit, CSP headers, input sanitisation, OWASP Top 10 coverage.

2. **Performance-Oriented**: Redis cache-aside with explicit invalidation, PgBouncer connection pooling, N+1 query detection, cursor-based pagination, bulk operations, image compression, CDN distribution.

3. **Operationally Observable**: Structured JSON logging, distributed tracing (OpenTelemetry), Prometheus metrics, Grafana dashboards (ops/eng/business), Sentry error tracking, health checks, performance middleware.

4. **Enterprise Testing**: Unit tests (90%+ domain coverage), integration tests with Testcontainers, API tests with role-based scenarios, security scans (SAST/DAST/dependency audit), load tests (k6 with 4 scenarios), stress tests (spike/soak/breakpoint).

5. **Scalable Infrastructure**: Multi-stage Docker builds, NGINX reverse proxy with SSL termination, Blue-Green zero-downtime deployment, horizontal scaling of stateless app servers, read replicas for query offloading, auto-scaled Celery workers.

6. **Resilient by Default**: Circuit breakers for external services, retry with exponential backoff, dead letter queues, graceful degradation, feature flag kill switches, automatic rollback triggers.

### Quantified Performance Targets

| Metric | Target | Method |
|---|---|---|
| API response time (p95) | <500ms | Caching, eager loading, connection pooling |
| API response time (p99) | <1s | Query optimisation, read replicas |
| Search latency (p95) | <800ms | Elasticsearch optimised indices |
| Checkout flow (p95) | <2s | Asynchronous payment processing |
| Uptime | 99.9% | Blue-green, health checks, auto-scaling |
| Error rate | <0.1% | Circuit breakers, retries, monitoring |
| Cache hit ratio | >85% | Appropriate TTLs, write-through |
| Background task delay | <30s for high_priority | Dedicated workers, queue prioritisation |

TRUE STAR BD LIMITED's backend architecture represents a mature, pragmatic approach to building an enterprise marketplace platform. It balances immediate delivery needs (single deployable monolith) with long-term scalability requirements (clean extraction path to microservices), wrapped in production-grade security, observability, and operational excellence.
