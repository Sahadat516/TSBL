# TSBL Marketplace

Enterprise multi-vendor digital marketplace platform.

## Architecture Overview

- **Backend**: Python 3.13+, FastAPI, SQLAlchemy 2.x, PostgreSQL, Redis, Celery
- **Frontend**: Next.js 15, React 19, TypeScript, TailwindCSS
- **Infrastructure**: Docker, NGINX, GitHub Actions

## Project Structure

```
tsbl/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/               # API routes (health, readiness, liveness)
│   │   ├── common/            # Shared utilities (base repository, enums)
│   │   ├── core/              # Core framework (config, database, security, logging)
│   │   ├── exceptions/        # Exception hierarchy and handlers
│   │   ├── middleware/        # Request ID, correlation ID, localization
│   │   └── modules/          # Business modules (auth, marketplace, payments, etc.)
│   ├── celery/               # Celery configuration and worker
│   ├── migrations/           # Alembic database migrations
│   └── tests/                # Backend test suite
├── frontend/                  # Next.js application
│   └── src/
│       ├── app/              # App router pages
│       ├── components/       # React components (atomic design)
│       ├── services/         # API service layer
│       ├── stores/           # Zustand state management
│       └── types/            # TypeScript type definitions
├── docker/                    # Docker and NGINX configurations
├── scripts/                   # Development and maintenance scripts
├── tests/                     # Cross-project tests
└── docs/                      # Documentation
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 22+
- Docker (for PostgreSQL, Redis)
- PostgreSQL 16+
- Redis 7+

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Copy environment config
cp .env.dev .env

# Start dependencies
docker compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose (Full Stack)

```bash
docker compose up --build
```

## Modules

| Module | Status | Description |
|--------|--------|-------------|
| Auth | Complete | Registration, login, JWT, password management |
| Marketplace | Planned | Product listing, search, categories |
| Orders | Planned | Order management, status tracking |
| Payments | Planned | Payment processing, gateways |
| Wallet | Planned | Digital wallet, transactions |
| Escrow | Planned | Secure payment holding |
| Reviews | Planned | Product & seller ratings |
| Chat | Planned | Buyer-seller messaging |
| Notifications | Planned | Email, push, in-app |
| Support | Planned | Ticket system |
| Affiliate | Planned | Referral program |
| Analytics | Planned | Dashboard metrics |
| Admin | Planned | Admin panel |

## Environment Variables

Key environment variables (see `.env.dev` for defaults):

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET_KEY` | JWT signing key |
| `ENCRYPTION_KEY` | Encryption key for sensitive data |
| `SENTRY_DSN` | Sentry error tracking DSN |
| `SMTP_*` | Email configuration |

## Testing

```bash
# Backend tests
cd backend && pytest

# With coverage
cd backend && pytest --cov=app --cov-report=html

# Frontend lint
cd frontend && npm run lint

# Type checking
cd frontend && npx tsc --noEmit
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run-backend.ps1` | Start backend dev server |
| `scripts/run-frontend.ps1` | Start frontend dev server |
| `scripts/lint.ps1` | Run all linters |
| `scripts/format.ps1` | Format all code |
| `scripts/test-backend.ps1` | Run backend tests |
| `scripts/migrate.ps1` | Run database migrations |
| `scripts/make-migration.ps1` | Create new migration |
| `scripts/reset-db.ps1` | Reset database (destructive) |
| `scripts/seed.ps1` | Seed database with sample data |

## License

Proprietary - TRUE STAR BD LIMITED
