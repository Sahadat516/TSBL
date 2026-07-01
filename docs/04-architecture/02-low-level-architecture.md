# Low-Level Architecture — TRUE STAR BD LIMITED (TSBL) Digital Marketplace

---

## Document Control

| Attribute | Value |
|---|---|
| **Document ID** | TSBL-ARCH-LL-002 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Principal Software Architect |
| **Date** | 2026-07-01 |

---

## 1. Clean / Hexagonal Architecture Layers Within Each Module

Each bounded context in the TSBL marketplace follows the **Hexagonal Architecture (Ports & Adapters)** pattern with four distinct layers:

```
 ┌───────────────────────────────────────────────────────────────────┐
 │                    PRESENTATION LAYER                              │
 │  (API Routers / WebSocket Handlers / CLI Commands)                │
 │  Depends on: Application Layer                                    │
 │  Purpose: Receive input, delegate to use cases, format response   │
 └──────────────────────────┬────────────────────────────────────────┘
                            │ calls
                            ▼
 ┌───────────────────────────────────────────────────────────────────┐
 │                    APPLICATION LAYER                               │
 │  (Use Cases / Services / DTOs / Event Handlers)                   │
 │  Depends on: Domain Layer                                         │
 │  Purpose: Orchestrate business workflows, coordinate repos/events │
 └──────────────────────────┬────────────────────────────────────────┘
                            │ calls
                            ▼
 ┌───────────────────────────────────────────────────────────────────┐
 │                      DOMAIN LAYER                                  │
 │  (Entities / Value Objects / Domain Events / Aggregate Roots)      │
 │  Depends on: Nothing (framework-agnostic pure Python)              │
 │  Purpose: Encapsulate enterprise business rules and invariants     │
 └──────────────────────────┬────────────────────────────────────────┘
                            │ implements
                            ▼
 ┌───────────────────────────────────────────────────────────────────┐
 │                   INFRASTRUCTURE LAYER                              │
 │  (Repositories / ORM Models / External API Clients / Cache)        │
 │  Depends on: Domain Layer                                          │
 │  Purpose: Implement ports defined in domain layer, I/O concerns    │
 └───────────────────────────────────────────────────────────────────┘
```

### 1.1 Dependency Rule

Dependencies point **inward**. The domain layer never imports from application, infrastructure, or presentation. The application layer depends on domain abstractions (ports). Infrastructure implements domain interfaces. Presentation depends on application interfaces.

```
  Presentation → Application → Domain
       ↓                          ↑
       └────── Infrastructure ───┘
               (implements ports)
```

---

## 2. Dependency Injection Flow

### 2.1 Container Setup

A single application-scoped DI container is initialised at application startup in `main.py`.

```python
# tsbl/main.py — Conceptual (not executable)

def create_app() -> FastAPI:
    container = Container()
    container.config.from_pydantic(Settings())

    # Wire modules
    container.wire(packages=[
        "tsbl.auth", "tsbl.catalog", "tsbl.order",
        "tsbl.payment", "tsbl.vendor", "tsbl.notification",
    ])

    app = FastAPI(title="TSBL Marketplace")
    app.container = container
    return app
```

### 2.2 Dependency Resolution Flow

```
   FastAPI Request
        │
        ▼
   Router function (presentation)
        │  @router.post("/orders")
        │  async def create_order(
        │      schema: CreateOrderSchema,
        │      service: OrderService = Depends(Provide[Container.order_service])
        │  ):
        ▼
   Container resolves OrderService
        │  ┌─ injects OrderRepository (bound to PostgresOrderRepo)
        │  └─ injects EventBus (bound to RabbitMQEventBus)
        ▼
   OrderService.create_order()
        │  ┌─ calls self.repo.save(order)
        │  └─ calls self.event_bus.publish(OrderPlaced(order_id))
        ▼
   Infrastructure implementations execute
```

### 2.3 Dependency Injection Provider Types

| Provider | Scope | Example |
|---|---|---|
| `Singleton` | Application lifetime | `EventBus`, `CacheClient`, `SearchClient` |
| `RequestScoped` | Per HTTP request | `UnitOfWork`, `CurrentUserContext` |
| `Transient` | Every injection | `Repository`, `Service`, `Factory` |

---

## 3. Repository Pattern Implementation

### 3.1 Abstract Repository (Port)

Defined in the domain layer of each module:

```python
# tsbl/catalog/domain/ports/product_repo.py — Conceptual

class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Product | None: ...

    @abstractmethod
    async def save(self, product: Product) -> Product: ...

    @abstractmethod
    async def delete(self, product_id: UUID) -> None: ...

    @abstractmethod
    async def search(
        self, query: str, filters: dict, page: int, size: int
    ) -> tuple[list[Product], int]: ...
```

### 3.2 Concrete Repository (Adapter)

Implemented in the infrastructure layer:

```python
# tsbl/catalog/infrastructure/repositories/product_repo.py — Conceptual

class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        orm_product = await self._session.get(ProductModel, product_id)
        return orm_product.to_domain() if orm_product else None

    async def save(self, product: Product) -> Product:
        orm_product = ProductModel.from_domain(product)
        self._session.add(orm_product)
        await self._session.flush()
        return orm_product.to_domain()
```

### 3.3 Repository Responsibilities by Module

| Module | Repository | Backing Store | Key Methods |
|---|---|---|---|
| **auth** | `UserRepository` | PostgreSQL | `get_by_email`, `get_by_id`, `save`, `get_roles`, `get_permissions` |
| **catalog** | `ProductRepository` | PostgreSQL (writes), ES (reads) | `search`, `get_by_category`, `save`, `delete`, `update_stock` |
| **catalog** | `CategoryRepository` | PostgreSQL | `get_tree`, `move_node`, `save`, `delete` |
| **cart** | `CartRepository` | Redis + PostgreSQL | `get_cart`, `add_item`, `remove_item`, `apply_coupon` |
| **order** | `OrderRepository` | PostgreSQL | `get_by_id`, `get_by_user`, `save`, `update_status` |
| **payment** | `TransactionRepository` | PostgreSQL | `get_by_id`, `get_by_order`, `save`, `update_status` |
| **vendor** | `VendorRepository` | PostgreSQL | `get_by_id`, `get_by_owner`, `save`, `approve` |
| **notification** | `NotificationRepository` | PostgreSQL | `save`, `get_by_user`, `mark_read`, `get_unread_count` |

---

## 4. Service Layer Responsibilities

Each module's application layer contains services (use cases) that coordinate domain logic and infrastructure.

### 4.1 Service Characteristics

| Characteristic | Description |
|---|---|
| **Orchestration** | Services coordinate domain objects, repositories, and external adapters |
| **No business logic** | Business rules belong in domain entities/value objects, not in services |
| **Unit of Work** | Services manage transactions via the UoW pattern |
| **Event publishing** | Services publish domain events after successful command execution |
| **Validation** | Services receive validated DTOs (Pydantic schemas) from presentation layer |

### 4.2 Service Examples

```
auth/
  application/
    services/
      AuthService          # login, logout, refresh_token, verify_email
      RegistrationService  # register, confirm_otp, resend_otp
      RoleService          # assign_role, revoke_role, list_permissions

catalog/
  application/
    services/
      ProductService       # create_product, update_product, delete_product, get_product
      InventoryService     # adjust_stock, reserve_stock, release_stock
      CategoryService      # create_category, move_category, rebuild_tree
      SearchService        # search, autocomplete, facet_search

order/
  application/
    services/
      OrderService         # place_order, cancel_order, get_order_history
      FulfillmentService   # process_shipment, mark_delivered, handle_return
      InvoiceService       # generate_invoice, send_invoice

payment/
  application/
    services/
      PaymentService       # initiate_payment, confirm_payment, process_refund
      ReconciliationService  # reconcile_transactions, report_discrepancy
```

---

## 5. Event-Driven Communication Between Modules

### 5.1 Event Bus Architecture

```
                    ┌──────────────────────────────────────┐
                    │            EventBus                   │
                    │  (In-process dispatcher + RabbitMQ)   │
                    │                                        │
                    │  ┌────────────────────────────────┐   │
                    │  │  Handler Registry               │   │
                    │  │  OrderPlaced → [OrderHandler,   │   │
                    │  │                 PaymentHandler,  │   │
                    │  │                 AnalyticsHandler] │   │
                    │  └────────────────────────────────┘   │
                    └──────────────────────────────────────┘
                              │              ▲
                    publish() │              │ consume()
                              ▼              │
                    ┌──────────────────────────────────────┐
                    │          RabbitMQ Exchange            │
                    │  topic: tsbl.domain.{event_name}     │
                    └──────────────────────────────────────┘
```

### 5.2 Domain Events Catalog

| Event | Publisher | Subscribers | Payload |
|---|---|---|---|
| `UserRegistered` | Auth | Notification (welcome email), Analytics | `{ user_id, email, name }` |
| `ProductCreated` | Catalog | Search (index), Admin (moderation queue), Analytics | `{ product_id, vendor_id, title }` |
| `OrderPlaced` | Order | Payment (initiate), Inventory (reserve), Notification (confirm), Analytics | `{ order_id, user_id, total, items }` |
| `PaymentReceived` | Payment | Order (update status), Notification (receipt), Analytics | `{ transaction_id, order_id, amount }` |
| `Shipped` | Fulfillment | Notification (tracking), Analytics | `{ order_id, tracking_code, carrier }` |
| `VendorApproved` | Admin | Vendor (notify), Notification (welcome) | `{ vendor_id, owner_email }` |
| `InventoryChanged` | Catalog | Search (update index), Cart (notify low stock) | `{ product_id, variant_id, quantity }` |

### 5.3 Event Handler Registration

Handlers are registered at startup via the container:

```python
# tsbl/main.py — Conceptual

container.event_bus().register(OrderPlaced, [
    container.payment_handler().handle_order_placed,
    container.inventory_handler().handle_order_placed,
    container.notification_handler().handle_order_placed,
])
```

---

## 6. CQRS Pattern for Read/Write Separation

### 6.1 When CQRS Is Used

Full CQRS is applied to modules where read and write workloads differ significantly:

| Module | Write Model | Read Model | Reason |
|---|---|---|---|
| **Catalog** | PostgreSQL (normalised) | Elasticsearch (denormalised) | Search requires faceted, full-text queries on denormalised docs |
| **Orders** | PostgreSQL (normalised) | PostgreSQL materialised view + Redis | Dashboard queries aggregated across thousands of orders |
| **Analytics** | PostgreSQL (raw events) | TimescaleDB / ClickHouse (aggregated) | Reporting queries expensive on transactional schema |

### 6.2 CQRS Flow

```
   ┌──────────┐     Command      ┌──────────────┐     Event     ┌──────────┐
   │  Client   │ ──────────────► │  Command      │ ────────────►│  Read    │
   │  (Write)  │                 │  Handler      │              │  Model   │
   └──────────┘                 └──────┬───────┘              └──────────┘
                                       │                              ▲
                                       ▼                              │
                                ┌──────────────┐              ┌──────────┐
                                │  Write DB     │              │  Query   │
                                │  (PostgreSQL) │              │  Handler │
                                └──────────────┘              └──────────┘
                                                                     ▲
   ┌──────────┐     Query       ┌──────────────┐                     │
   │  Client   │ ──────────────► │  Query        │ ──────────────────┘
   │  (Read)   │                │  Handler      │
   └──────────┘                 └──────────────┘
```

### 6.3 Synchronisation

Read models are eventually consistent. Synchronisation occurs via:

- **Domain events**: On `ProductCreated`, the Elasticsearch index is updated.
- **Outbox pattern**: Events are written to an `event_store` table within the same DB transaction. A separate process (`Celery` or `Debezium`) forwards events to the read model.
- **Cache invalidation**: Write operations invalidate or update cached read models in Redis.

---

## 7. State Management Patterns

### 7.1 Frontend State Management (Next.js)

| State Type | Tool | Scope | Example |
|---|---|---|---|
| **Server State** | TanStack Query | Product listings, orders, user profile | `useQuery(['products'], fetchProducts)` |
| **Client State** | Zustand | UI state, cart, auth tokens | `useAuthStore`, `useCartStore` |
| **URL State** | Next.js `useSearchParams` | Filters, pagination, search query | `?page=2&sort=price_asc&category=electronics` |
| **Form State** | React Hook Form + Zod | Checkout forms, registration | `useForm<RegisterSchema>()` |
| **WebSocket State** | Socket.IO + Zustand | Order tracking, notifications | Socket updates → Zustand slice |

### 7.2 Backend State Management

| State Type | Mechanism | Location | Example |
|---|---|---|---|
| **Request State** | Pydantic + Python context vars | Per-request | Current user, request ID, correlation ID |
| **Session State** | Redis (via FastAPI sessions) | External cache | User session, OAuth state |
| **Application State** | Singleton services | In-memory | Configuration, feature flags, cache client |
| **Distributed State** | Redis + PostgreSQL | External | Rate limiter counters, distributed locks, idempotency keys |

---

## 8. Error Handling Framework

### 8.1 Exception Hierarchy

```
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── TSBLBaseException (all application exceptions inherit from this)
    │   ├── DomainException
    │   │   ├── InvalidProductDataError
    │   │   ├── InsufficientStockError
    │   │   ├── OrderStateTransitionError
    │   │   └── PaymentDeclinedError
    │   ├── ApplicationException
    │   │   ├── AuthenticationError
    │   │   ├── AuthorisationError
    │   │   ├── ValidationError
    │   │   ├── NotFoundError
    │   │   ├── ConflictError
    │   │   └── ServiceUnavailableError
    │   └── InfrastructureException
    │       ├── DatabaseConnectionError
    │       ├── ExternalServiceError
    │       ├── CacheError
    │       └── FileStorageError
    └── (Standard Python exceptions)
```

### 8.2 Global Exception Handler

All unhandled exceptions are caught by a FastAPI exception handler that returns RFC 7807 Problem Details responses:

```python
# Mapping — Conceptual
exception_handlers = {
    NotFoundError:          (status.HTTP_404_NOT_FOUND, "not_found"),
    ValidationError:        (status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error"),
    AuthenticationError:    (status.HTTP_401_UNAUTHORIZED, "unauthorized"),
    AuthorisationError:     (status.HTTP_403_FORBIDDEN, "forbidden"),
    ConflictError:          (status.HTTP_409_CONFLICT, "conflict"),
    InsufficientStockError: (status.HTTP_409_CONFLICT, "insufficient_stock"),
    PaymentDeclinedError:   (status.HTTP_402_PAYMENT_REQUIRED, "payment_declined"),
    ExternalServiceError:   (status.HTTP_502_BAD_GATEWAY, "external_service_error"),
    ServiceUnavailableError:(status.HTTP_503_SERVICE_UNAVAILABLE, "service_unavailable"),
}
```

### 8.3 Error Response Format (RFC 7807)

```json
{
    "type": "https://api.tsbl.com/errors/insufficient_stock",
    "title": "Insufficient Stock",
    "status": 409,
    "detail": "Product 'Wireless Headphones' (SKU: WH-001) only has 2 units available. Requested: 5.",
    "instance": "/api/v1/orders",
    "trace_id": "abc-123-def-456",
    "errors": [
        {
            "field": "items[2].quantity",
            "message": "Quantity exceeds available stock"
        }
    ]
}
```

---

## 9. Transaction Management Across Modules

### 9.1 Unit of Work Pattern

The `UnitOfWork` class manages database transactions and coordinates with the event bus.

```
┌──────────────────────────────────────────────────────────────────┐
│                        UnitOfWork                                 │
│                                                                   │
│  1. Enter (async context manager)                                 │
│     ├─ Acquire DB session                                        │
│     └─ Open new transaction                                       │
│                                                                   │
│  2. Execute business logic (register repos, call services)        │
│                                                                   │
│  3. Commit or Rollback                                           │
│     ├─ On commit: flush DB, dispatch collected domain events      │
│     └─ On rollback: discard changes                               │
│                                                                   │
│  4. Exit                                                          │
│     ├─ If committed: publish events to message broker             │
│     └─ If rolled back: discard events                             │
└──────────────────────────────────────────────────────────────────┘
```

### 9.2 Transaction Boundaries

| Scope | Transaction Type | Pattern |
|---|---|---|
| Single repository method | Implicit (SQLAlchemy autoflush) | — |
| Single service method | `async with uow:` | Unit of Work |
| Single module, multiple services | `async with uow:` (shared session) | Unit of Work |
| Cross-module (same DB) | `async with uow:` (shared session, multiple repos) | Unit of Work |
| Cross-module (different DB) | Outbox pattern + saga | Eventual consistency |

### 9.3 Saga Pattern (Cross-Module Consistency)

For flows spanning multiple bounded contexts (e.g., `PlaceOrder` → `ReserveInventory` → `ProcessPayment`), a choreographed saga is implemented:

```
 Order Service                Inventory Service            Payment Service
      │                             │                            │
      │  ── OrderPlaced ──────────► │                            │
      │                             │  ── InventoryReserved ──►  │
      │                             │                            │
      │                             │      ── PaymentReceived ──►│
      │                             │                            │
      │  ◄────────── OrderConfirmed ─                            │
      │                             │                            │
      │                             │                            │
      │  (If Payment Fails)         │                            │
      │  ◄── OrderFailed ◄────────── ◄────── PaymentFailed ──────│
      │       (compensate)          │   (release inventory)      │
```

Each service listens to events and emits compensating events on failure. The saga coordinator (a process manager in the `order` module) tracks state.

---

## 10. Caching Strategy at Each Layer

### 10.1 Caching Layers

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                          CDN Layer (CloudFront)                      │
 │  Cache: Static assets (images, JS bundles, CSS)                     │
 │  TTL: 1 year (versioned URLs). Cache-Control: public, immutable     │
 └─────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─────────────────────────────────────────────────────────────────────┐
 │                     Application Cache Layer (Redis)                 │
 │                                                                     │
 │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐ │
 │  │ Product Cache      │  │ Session Store     │  │ Category Tree   │ │
 │  │ Key: prod:{id}    │  │ Key: session:{sid}│  │ Key: cat:tree   │ │
 │  │ TTL: 5 min        │  │ TTL: 30 min       │  │ TTL: 60 min     │ │
 │  └───────────────────┘  └───────────────────┘  └─────────────────┘ │
 │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐ │
 │  │ Rate Limiter      │  │ Distributed Lock   │  │ IDempotency     │ │
 │  │ Key: ratelimit:ip │  │ Key: lock:{res}    │  │ Key: idemp:{key}│ │
 │  │ TTL: 1 sec window │  │ TTL: 30 sec        │  │ TTL: 24 hours   │ │
 │  └───────────────────┘  └───────────────────┘  └─────────────────┘ │
 └─────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─────────────────────────────────────────────────────────────────────┐
 │                      Database Cache Layer                           │
 │                                                                     │
 │  • PostgreSQL shared buffers (default ~25% of RAM)                 │
 │  • Materialised views for dashboard queries                        │
 │  • Partial indexes for frequent query patterns                     │
 │  • Covering indexes for SELECT-heavy queries                       │
 └─────────────────────────────────────────────────────────────────────┘
```

### 10.2 Cache Invalidation Strategy

| Trigger | Action | Mechanism |
|---|---|---|
| Product updated | Delete `prod:{id}` from Redis | Event handler on `ProductUpdated` |
| Category tree changed | Delete `cat:tree` from Redis | Event handler on `CategoryMoved` |
| User session expired | TTL expiry | Automatic Redis eviction |
| Inventory changed | Delete `prod:{id}` from Redis | Event handler on `InventoryChanged` |
| Write-through on cart | Update `cart:{user_id}` | Direct Redis write (no expire) |
| Admin cache purge | Flush specific prefix | Admin API endpoint (`POST /api/v1/admin/cache/purge`) |

### 10.3 Cache-Aside Pattern (Read Path)

```
   Client
     │
     │ GET /api/v1/products/123
     ▼
   ProductService.get_product(123)
     │
     ├── 1. Check Redis: GET prod:123
     │       ├── Hit → return cached value
     │       └── Miss → continue
     │
     ├── 2. Query PostgreSQL: SELECT * FROM products WHERE id = 123
     │
     ├── 3. Store in Redis: SET prod:123 <result> EX 300
     │
     └── 4. Return result
```

### 10.4 Write-Through Pattern (Inventory)

```
   Client
     │
     │ POST /api/v1/inventory/adjust
     ▼
   InventoryService.adjust_stock(product_id, delta)
     │
     ├── 1. UPDATE products SET stock = stock + delta WHERE id = :pid
     │
     ├── 2. DELETE prod:{pid} from Redis (invalidate)
     │
     ├── 3. Publish InventoryChanged(product_id, new_stock)
     │
     └── 4. Return updated product
```

---

## 11. Detailed Component Responsibilities

### 11.1 Auth Module

| Component | Type | Responsibility |
|---|---|---|
| `User` | Entity (Aggregate Root) | Encapsulates identity, credentials, email verification status, roles |
| `Role` | Value Object | Named set of permissions |
| `Permission` | Value Object | String-based action identifier (`order:read`, `product:write`) |
| `HashedPassword` | Value Object | Encapsulates bcrypt hashing and verification |
| `UserRegistered` | Domain Event | Published when a user completes registration |
| `AuthService` | Application Service | Login with password, OAuth flow, token refresh |
| `RegistrationService` | Application Service | Register, verify email via OTP, resend OTP |
| `RoleService` | Application Service | CRUD roles, assign/revoke, permission checks |
| `UserRepository` | Port | Interface for user persistence |
| `PostgresUserRepository` | Adapter | SQLAlchemy implementation |
| `JWTProvider` | Adapter | Issue and verify JWT access/refresh tokens |
| `OAuthClient` | Adapter | Google, Facebook OAuth2 integration |
| `OTPProvider` | Adapter | Generate and verify one-time passwords |

### 11.2 Catalog Module

| Component | Type | Responsibility |
|---|---|---|
| `Product` | Entity (Aggregate Root) | Product details, variants, pricing, status |
| `Category` | Entity | Nested tree category with `lft`/`rgt` (nested set) |
| `Brand` | Entity | Brand information |
| `Variant` | Entity | SKU-level attributes, stock, price override |
| `ProductSpecification` | Value Object | Dynamic key-value attributes (JSONB) |
| `Money` | Value Object | Currency + amount with precision handling |
| `Stock` | Value Object | Available, reserved, damaged quantities |
| `ProductCreated` | Domain Event | Published on product creation |
| `ProductService` | Application Service | Product CRUD with validation, stock management |
| `CategoryService` | Application Service | Tree management (add, move, delete) |
| `SearchService` | Application Service | Full-text search, faceted navigation, autocomplete |
| `ProductRepository` | Port | Interface for product persistence |
| `PostgresProductRepository` | Adapter | SQLAlchemy implementation |
| `ElasticsearchProductRepository` | Adapter | Elasticsearch read model for search |

### 11.3 Order Module

| Component | Type | Responsibility |
|---|---|---|
| `Order` | Entity (Aggregate Root) | Order header with status machine, totals, shipping info |
| `OrderItem` | Entity | Line item referencing product/variant at purchase price |
| `OrderStatus` | Value Object | Enum-like state machine: `pending → confirmed → processing → shipped → delivered → completed` |
| `Shipment` | Entity | Tracking info, carrier, estimated delivery |
| `Invoice` | Entity | Generated PDF invoice reference |
| `OrderPlaced` | Domain Event | Published on successful order placement |
| `OrderService` | Application Service | Place, cancel, return; state transitions; history |
| `FulfillmentService` | Application Service | Shipment processing, label generation, tracking updates |
| `InvoiceService` | Application Service | PDF generation, email attachment |
| `OrderRepository` | Port | Interface for order persistence |
| `PostgresOrderRepository` | Adapter | SQLAlchemy implementation |
| `ShipmentProvider` | Port | Interface for logistics integration |
| `SteadfastShipmentProvider` | Adapter | SteadFast API integration |

### 11.4 Payment Module

| Component | Type | Responsibility |
|---|---|---|
| `Payment` | Entity (Aggregate Root) | Payment record linked to order |
| `Transaction` | Entity | Individual charge/refund within a payment |
| `PaymentStatus` | Value Object | `pending → processing → succeeded → failed → refunded` |
| `Money` | Value Object | Currency + amount |
| `PaymentReceived` | Domain Event | Published on successful payment |
| `PaymentService` | Application Service | Initiate, confirm, refund, retry |
| `ReconciliationService` | Application Service | Match internal transactions with gateway reports |
| `PaymentGateway` | Port | Interface for payment processing |
| `SSLCommerzGateway` | Adapter | SSLCommerz API integration |
| `BkashGateway` | Adapter | bKash Tokenised Checkout integration |
| `StripeGateway` | Adapter | Stripe API (Connect for split payments) |
| `TransactionRepository` | Port | Interface for transaction persistence |
| `PostgresTransactionRepository` | Adapter | SQLAlchemy implementation |

### 11.5 Vendor Module

| Component | Type | Responsibility |
|---|---|---|
| `Vendor` | Entity (Aggregate Root) | Business info, commission rate, status |
| `VendorApplication` | Entity | Application for new vendor with documents |
| `Payout` | Entity | Periodic payout to vendor |
| `Commission` | Value Object | Percentage or flat fee per category/product |
| `VendorApproved` | Domain Event | Published when vendor application approved |
| `VendorService` | Application Service | Register, approve, suspend, update profile |
| `PayoutService` | Application Service | Calculate, initiate, confirm payout |
| `VendorRepository` | Port | Interface for vendor persistence |
| `PostgresVendorRepository` | Adapter | SQLAlchemy implementation |

### 11.6 Notification Module

| Component | Type | Responsibility |
|---|---|---|
| `Notification` | Entity | Notification record (email, SMS, in-app) |
| `NotificationTemplate` | Value Object | Jinja2 template with variables |
| `NotificationChannel` | Value Object | Email / SMS / Push / In-App |
| `NotificationSent` | Domain Event | Published on delivery (success or failure) |
| `NotificationService` | Application Service | Send notification, manage preferences, track delivery |
| `EmailProvider` | Port | Interface for email sending |
| `SESEmailProvider` | Adapter | AWS SES implementation |
| `SMTPEmailProvider` | Adapter | SMTP fallback |
| `SMSProvider` | Port | Interface for SMS sending |
| `TwilioSMSProvider` | Adapter | Twilio implementation |
| `GreenWebSMSProvider` | Adapter | GreenWeb BD implementation |

### 11.7 Admin Module

| Component | Type | Responsibility |
|---|---|---|
| `AdminUser` | Entity | Admin with elevated permissions |
| `AuditLog` | Entity | Immutable record of administrative actions |
| `PlatformConfig` | Value Object | Key-value configuration store |
| `AdminService` | Application Service | User management, role assignment, platform config |
| `ModerationService` | Application Service | Review products, disputes, reports |
| `AuditRepository` | Port | Interface for audit log persistence |
| `PostgresAuditRepository` | Adapter | SQLAlchemy implementation with append-only policy |

### 11.8 Analytics Module

| Component | Type | Responsibility |
|---|---|---|
| `Metric` | Value Object | Named metric with timestamp and value |
| `Dashboard` | Entity | User-defined dashboard layout |
| `Report` | Entity | Scheduled report configuration |
| `AnalyticsService` | Application Service | Compute metrics, generate reports, manage dashboards |
| `EventStore` | Port | Interface for event analytics storage |
| `PostgresEventStore` | Adapter | PostgreSQL event storage (initial) |
| `ClickHouseEventStore` | Adapter | ClickHouse for production analytics |

---

## 12. Inter-Module Communication Summary

| Source Module | Destination Module | Event / Call | Mechanism |
|---|---|---|---|
| Auth | Notification | `UserRegistered` → Send welcome email | Event Bus |
| Order | Payment | `OrderPlaced` → Initiate payment | Event Bus |
| Payment | Order | `PaymentReceived` → Update order status | Event Bus |
| Payment | Notification | `PaymentReceived` → Send receipt | Event Bus |
| Order | Inventory | `OrderPlaced` → Reserve stock | Event Bus |
| Order | Notification | `Shipped` → Send tracking | Event Bus |
| Admin | Vendor | `VendorApproved` → Notify vendor | Event Bus |
| Catalog | Search | `ProductCreated` → Index product | Event Bus |
| All | Analytics | All domain events → Record metric | Event Bus |
