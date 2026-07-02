# Architecture Guide

## System Architecture

TSBL Marketplace follows a **Modular Monolith** architecture designed to evolve into Microservices. The system is organized around business capabilities, each encapsulated in a self-contained module.

## Backend Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────┐
│                   API Layer                      │
│           (Routes, Request/Response)             │
├─────────────────────────────────────────────────┤
│               Application Layer                  │
│         (Services, Use Cases, DTOs)              │
├─────────────────────────────────────────────────┤
│               Domain Layer                       │
│     (Entities, Value Objects, Aggregates)        │
├─────────────────────────────────────────────────┤
│            Infrastructure Layer                  │
│   (Repositories, External Services, Cache)       │
├─────────────────────────────────────────────────┤
│              Persistence Layer                   │
│         (Database, Migrations, Redis)            │
└─────────────────────────────────────────────────┘
```

### Module Structure

Each business module follows the same structure:

```
modules/{module}/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── routes.py
├── application/
│   ├── __init__.py
│   └── {module}_service.py
├── domain/
│   ├── __init__.py
│   ├── entities.py
│   └── events.py
├── infrastructure/
│   ├── __init__.py
│   └── {module}_repository.py
└── schemas/
    ├── __init__.py
    └── {module}_schema.py
```

### Dependency Injection

FastAPI's dependency injection system wires the layers together:

```python
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
```

### Middleware Pipeline

```
Request → RequestIDMiddleware → CorrelationIDMiddleware →
LocalizationMiddleware → GZipMiddleware → CORSMiddleware →
TrustedHostMiddleware → Router → Exception Handlers → Response
```

### Error Handling

Custom exception hierarchy with automatic handler registration:

```
AppException (base)
├── BadRequestError (400)
├── ValidationError (422)
├── AuthenticationError (401)
├── AuthorizationError (403)
├── NotFoundError (404)
├── ConflictError (409)
├── RateLimitError (429)
├── BusinessRuleViolation (422)
├── ExternalServiceError (502)
└── ServiceUnavailableError (503)
```

## Frontend Architecture

### Route Structure

```
app/
├── (auth)/              # Authentication pages (login, register, forgot/reset password)
├── (marketplace)/       # Public marketplace pages
├── dashboard/           # Protected dashboard pages
└── layout.tsx           # Root layout
```

### State Management

- **Zustand**: Client-side state (auth, UI)
- **TanStack Query**: Server state (API data caching, synchronization)

### Component Hierarchy (Atomic Design)

```
Atoms: Button, Input, Badge, Icon, Avatar
├── Molecules: FormField, Card, Modal, Dropdown
│   ├── Organisms: LoginForm, ProductCard, Header, Footer
│   │   ├── Templates: AuthLayout, DashboardLayout
│   │   │   └── Pages: Login, Dashboard, ProductDetail
```

## Data Flow

```
Client → Next.js → API Route / Page → Axios/Fetch →
NGINX → FastAPI → Service → Repository → Database
                                    ↕
                                  Redis Cache
                                    ↕
                              Celery (Async Tasks)
```

## Security Architecture

- JWT access tokens (in-memory, 15-30min expiry)
- Refresh tokens (7 days, rotation on use)
- CORS restricted to known origins
- HTTPS enforced in production
- Rate limiting on API endpoints
- Input validation (Pydantic / Zod)
- SQL injection prevention (SQLAlchemy parameterized queries)
- XSS prevention (React escaping, Content Security Policy)
- CSRF protection (SameSite cookies, stateful tokens)

## Performance

- Connection pooling (PostgreSQL, Redis)
- GZip compression (NGINX + FastAPI)
- Database indexing strategy
- Redis caching layer
- Celery for async/background tasks
- CDN-ready static assets (Next.js output)
