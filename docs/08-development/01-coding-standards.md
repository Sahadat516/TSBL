# Coding Standards

## TRUE STAR BD LIMITED — Digital Marketplace Platform

| Document ID | DEV-TSBL-001 |
|---|---|
| Version | 1.0 |
| Date | July 1, 2026 |
| Author | Software Architecture Division |
| Status | Approved |
| Classification | Internal — Confidential |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Python (FastAPI) Coding Standards](#2-python-fastapi-coding-standards)
3. [TypeScript/React Coding Standards](#3-typescriptreact-coding-standards)
4. [SQL Coding Standards](#4-sql-coding-standards)
5. [Git Commit Message Conventions](#5-git-commit-message-conventions)
6. [Code Review Standards](#6-code-review-standards)
7. [Error Handling Patterns](#7-error-handling-patterns)
8. [Logging Standards](#8-logging-standards)
9. [Testing Standards](#9-testing-standards)
10. [Documentation Standards](#10-documentation-standards)
11. [Security Coding Guidelines](#11-security-coding-guidelines)

---

## 1. Introduction

This document defines mandatory coding standards for all software engineering activities within the TRUE STAR BD LIMITED Digital Marketplace Platform. Adherence to these standards is a prerequisite for code acceptance. These standards apply to all codebases within the project monorepo, including backend services (Python/FastAPI), frontend applications (TypeScript/React), database migrations and queries (SQL), infrastructure-as-code, and CI/CD pipeline definitions.

---

## 2. Python (FastAPI) Coding Standards

### 2.1 Language Version and Runtime

| Requirement | Standard |
|---|---|
| Python Version | 3.12+ |
| ASGI Server | Uvicorn with Gunicorn workers |
| Package Manager | Poetry (lock file committed) |
| Formatting | Ruff (line length: 100) |
| Type Checker | mypy (strict mode) |

### 2.2 PEP 8 Compliance

All Python code MUST conform to PEP 8, enforced via Ruff. Key conventions:

- **Indentation:** 4 spaces per level. No tabs.
- **Line length:** Maximum 100 characters. Docstrings and comments: 72 characters.
- **Blank lines:** Two blank lines before top-level class/function definitions. One blank line before method definitions inside a class.
- **Imports:** Grouped in the following order, separated by a blank line:
  1. Standard library imports (`os`, `datetime`, `typing`)
  2. Third-party imports (`fastapi`, `sqlalchemy`, `pydantic`)
  3. Local application imports (`app.models`, `app.services`)
- **Trailing whitespace:** Forbidden. Ruff enforces removal.
- **String quotes:** Double quotes for docstrings and user-facing strings. Single quotes for identifiers and internal strings. Consistent within a single module.

### 2.3 Type Hints

All function signatures MUST include type hints. No exceptions.

```python
# Correct
def calculate_escrow_release(
    order_id: int,
    amount: Decimal,
    release_type: EscrowReleaseType,
) -> EscrowTransaction:
    ...

# Incorrect — missing type hints
def calculate_escrow_release(order_id, amount, release_type):
    ...
```

- Use `Optional[T]` over `T | None` for backward compatibility, explicitly prefer `T | None` from Python 3.10+.
- Use `list[T]` over `List[T]`, `dict[K, V]` over `Dict[K, V]` (Python 3.9+).
- Use `Self` return type for class methods returning `self`.
- Use `TypeVar` and `Generic` for reusable generic components.
- Use `Protocol` for structural subtyping (duck typing).
- Never use `Any` unless interfacing with untyped third-party code; annotate with `Any` explicitly and add a `# type: ignore[no-any-explicit]` comment.

### 2.4 Docstrings

Use Google-style docstrings via the `napoleon` Sphinx extension.

```python
def create_user(
    email: str,
    password: str,
    role: UserRole,
) -> User:
    """Register a new user account.

    Creates a user record with hashed credentials and assigns the
    specified role. Sends a welcome email asynchronously.

    Args:
        email: User's verified email address.
        password: Plain-text password (bcrypt-hashed before storage).
        role: Initial role assignment from the UserRole enum.

    Returns:
        The newly created User ORM instance.

    Raises:
        DuplicateEmailError: If a user with this email already exists.
        InvalidRoleError: If the specified role is not assignable.

    Example:
        user = create_user("seller@example.com", "s3cur3P@ss", UserRole.SELLER)
    """
```

- All public modules, classes, methods, and functions MUST have docstrings.
- Private functions (prefixed with `_`) SHOULD have docstrings if logic is non-trivial.
- Module-level docstrings MUST describe the module's purpose.

### 2.5 Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Modules | snake_case | `user_service.py`, `payment_gateway.py` |
| Classes | PascalCase | `EscrowManager`, `WalletService` |
| Functions/Methods | snake_case | `release_escrow()`, `get_wallet_balance()` |
| Variables | snake_case | `order_total`, `release_status` |
| Constants | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS`, `ESCROW_HOLD_DAYS` |
| Private members | `_` prefix | `_validate_payload()`, `_cache_key` |
| Dunder methods | `__` prefix/suffix | `__str__`, `__repr__` |
| Type variables | PascalCase prefixed with T | `TOrder`, `TUser` |
| Enums | PascalCase; members UPPER_SNAKE | `class OrderStatus: PENDING = "pending"` |
| Pydantic models | PascalCase | `OrderCreateRequest`, `UserResponse` |
| FastAPI dependencies | snake_case | `get_current_user`, `get_db_session` |
| Routers | snake_case, `router` suffix | `orders_router`, `wallet_router` |
| SQLAlchemy models | PascalCase | `User`, `OrderItem`, `EscrowTransaction` |

### 2.6 FastAPI-Specific Standards

- Use `Depends()` for dependency injection exclusively. No `global` variables.
- Prefer `Body()`, `Query()`, `Path()`, `Header()` with validation parameters over raw type hints.
- Define Pydantic models in separate `schemas/` directory, not inline in route handlers.
- Route handler functions must be async (`async def`) for I/O-bound operations.
- Use `BackgroundTasks` for non-critical operations (email dispatch, log aggregation).
- Apply `@router.api_route` decorators with explicit HTTP method first; use `@router.get`, `@router.post`, etc.
- Version API endpoints: `router = APIRouter(prefix="/api/v1")`.

```python
# Correct
@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Retrieve order by ID",
)
async def get_order(
    order_id: int = Path(..., ge=1, description="Order primary key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> OrderResponse:
    ...
```

### 2.7 Project Structure

```
app/
  __init__.py
  main.py                    # FastAPI app factory
  core/
    config.py                # Settings via pydantic-settings
    security.py              # JWT, password hashing
    logging.py               # Logging configuration
    exceptions.py            # Custom exception classes
    dependencies.py          # Shared FastAPI dependencies
  models/                    # SQLAlchemy ORM models
    user.py
    order.py
    wallet.py
  schemas/                   # Pydantic request/response schemas
    user.py
    order.py
    wallet.py
  repositories/              # Data access layer
    user_repository.py
    order_repository.py
  services/                  # Business logic layer
    user_service.py
    escrow_service.py
  api/
    v1/
      users.py               # Route handlers
      orders.py
      wallet.py
  background/                # Background/Celery tasks
      email_tasks.py
      cleanup_tasks.py
  tests/
    unit/
    integration/
    e2e/
```

---

## 3. TypeScript/React Coding Standards

### 3.1 Language Version and Tooling

| Requirement | Standard |
|---|---|
| TypeScript Version | 5.4+ |
| Framework | React 18+ with Vite |
| Package Manager | pnpm (lock file committed) |
| Linter | ESLint with `@typescript-eslint` and `eslint-plugin-react` |
| Formatter | Prettier (line length: 100) |
| Type Checking | `tsc --noEmit --strict` |
| Test Framework | Vitest |

### 3.2 ESLint and Prettier Configuration

ESLint must extend the following configurations:

```jsonc
// .eslintrc.cjs
module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/strict-type-checked",
    "plugin:@typescript-eslint/stylistic-type-checked",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "prettier", // MUST be last to disable conflicting rules
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: ["./tsconfig.json", "./tsconfig.node.json"],
    tsconfigRootDir: __dirname,
  },
  rules: {
    "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    "@typescript-eslint/explicit-function-return-type": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "react/prop-types": "off", // We use TypeScript for prop validation
    "react/no-array-index-key": "error",
    "no-console": ["warn", { allow: ["warn", "error"] }],
  },
};
```

Prettier configuration:

```jsonc
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always",
  "bracketSpacing": true,
  "endOfLine": "lf"
}
```

### 3.3 TypeScript Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Interfaces | PascalCase, I-prefix optional | `UserProps`, `OrderResponse` |
| Types | PascalCase | `EscrowStatus`, `UserRole` |
| Enums | PascalCase | `enum OrderStatus { ... }` |
| Enum members | PascalCase | `OrderStatus.PendingPayment` |
| Functions | camelCase | `formatCurrency()`, `useAuth()` |
| Variables | camelCase | `userProfile`, `orderTotal` |
| Constants (module-level) | UPPER_SNAKE_CASE | `MAX_FILE_SIZE`, `API_BASE_URL` |
| React components | PascalCase | `UserProfileCard`, `OrderTable` |
| Hooks | camelCase, `use` prefix | `useAuthentication`, `useWalletBalance` |
| Props type | PascalCase + `Props` suffix | `UserCardProps`, `OrderRowProps` |
| Files (components) | PascalCase | `UserProfileCard.tsx` |
| Files (utilities) | camelCase | `formatCurrency.ts` |
| Test files | `.test.ts` or `.spec.tsx` suffix | `OrderService.test.ts` |
| Directory names | kebab-case | `user-profile/`, `order-management/` |

### 3.4 Component Structure

Components MUST follow a consistent structure:

```tsx
// Imports — grouped: React → third-party → internal → styles
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';

import { useAuth } from '@/hooks/useAuth';
import { OrderService } from '@/services/order.service';
import { type Order } from '@/types/order';
import { Card } from '@/components/ui/card';

import styles from './OrderTimeline.module.css';

// Types defined at top of file
interface OrderTimelineProps {
  orderId: number;
  events: OrderEvent[];
}

// Component definition — function declaration, not arrow
export function OrderTimeline({ orderId, events }: OrderTimelineProps) {
  const { user } = useAuth();
  const [expanded, setExpanded] = useState(false);

  // Effects at top, then event handlers, then render
  useEffect(() => {
    if (events.length === 0) {
      // handle empty state
    }
  }, [events]);

  const handleToggleExpand = () => {
    setExpanded((prev) => !prev);
  };

  if (!events || events.length === 0) {
    return <EmptyState message="No timeline events available" />;
  }

  return (
    <Card className={styles.timeline}>
      {events.map((event) => (
        <TimelineItem key={event.id} event={event} />
      ))}
    </Card>
  );
}

// Private sub-components at bottom of file or in separate files
function EmptyState({ message }: { message: string }) {
  return <div className={styles.empty}>{message}</div>;
}
```

### 3.5 State Management Standards

- **Server state:** Use `@tanstack/react-query` for all server data fetching, caching, and mutations.
- **Client state:** Use React `useState` / `useReducer` for component-local state.
- **Global state:** Use Zustand for shared global state (auth, UI preferences). Avoid Redux unless justified by performance profiling.
- **Form state:** Use React Hook Form with Zod schema validation.
- **URL state:** Use React Router's `useSearchParams` for filter/sort/pagination state.

### 3.6 React Coding Patterns

- Use functional components with hooks exclusively. No class components.
- Use `export function ComponentName()` (named export) not `export default`.
- Destructure props in the function signature.
- Extract reusable logic into custom hooks (`use*` pattern).
- Use React Fragments (`<>...</>`) instead of unnecessary `<div>` wrappers.
- Do NOT use index as key in lists; use stable identifiers.
- Use optional chaining (`?.`) and nullish coalescing (`??`) to handle nullable values.
- Memoize expensive computations with `useMemo` and callback references with `useCallback`.

---

## 4. SQL Coding Standards

### 4.1 Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Tables | snake_case, plural | `users`, `order_items`, `escrow_transactions` |
| Columns | snake_case, singular | `user_id`, `created_at`, `amount` |
| Primary keys | `id` (auto-increment or UUID) | `id` |
| Foreign keys | `{referenced_table}_id` | `order_id`, `product_id` |
| Indexes | `idx_{table}_{column}` | `idx_users_email` |
| Unique constraints | `uq_{table}_{column}` | `uq_users_email` |
| Foreign key constraints | `fk_{child}_{parent}` | `fk_order_items_order` |
| Check constraints | `ck_{table}_{description}` | `ck_orders_amount_positive` |
| Triggers | `trg_{table}_{action}` | `trg_orders_updated_at` |
| Views | `v_{descriptive_name}` | `v_seller_monthly_revenue` |
| Functions/Procedures | snake_case | `calculate_escrow_release()` |

### 4.2 Formatting Rules

- All SQL reserved words: UPPERCASE (`SELECT`, `INSERT`, `WHERE`, `FROM`, `JOIN`).
- All identifiers: lowercase snake_case.
- Use consistent indentation (4 spaces) for sub-clauses.
- Each major clause on its own line.
- Align `AND` / `OR` operators at the start of the line.

```sql
-- Correct
SELECT
    u.id,
    u.email,
    u.created_at,
    COALESCE(w.balance, 0.00) AS wallet_balance
FROM
    users u
    LEFT JOIN wallets w
        ON w.user_id = u.id
        AND w.status = 'active'
WHERE
    u.role = 'seller'
    AND u.kyc_status = 'verified'
    AND u.is_active = TRUE
ORDER BY
    u.created_at DESC
LIMIT 20;

-- Incorrect
select u.id, u.email, w.balance from users u
left join wallets w on u.id = w.user_id
where u.role='seller';
```

### 4.3 Query Patterns

- **SELECT columns explicitly.** Never use `SELECT *` in production code. Only `SELECT *` is allowed in ad-hoc migrations or exploration.
- **Table aliases:** Use meaningful short abbreviations (`u` for `users`, `oi` for `order_items`).
- **Joins:** Use explicit `INNER JOIN`, `LEFT JOIN`; never use implicit joins (comma-separated FROM).
- **WHERE filters:** Place selective filters early. Indexed columns should appear first in multi-column filters.
- **Subqueries:** Prefer CTEs (`WITH` clause) over nested subqueries for readability.
- **Aggregations:** Use `GROUP BY` with explicit column names, never ordinal positions.
- **Pagination:** Use keyset pagination (`WHERE id > ? ORDER BY id LIMIT ?`) over `OFFSET` for large datasets.
- **Transactions:** Begin with `BEGIN;` and ensures `COMMIT;` or `ROLLBACK;` in application code using context managers.

```sql
-- Keyset pagination (preferred)
SELECT id, email, created_at
FROM users
WHERE id > :last_seen_id
ORDER BY id ASC
LIMIT 50;

-- Offset pagination (acceptable only for small/admin datasets)
SELECT id, email, created_at
FROM users
ORDER BY id ASC
LIMIT 50 OFFSET :page * 50;
```

### 4.4 Migration Standards

All database migrations MUST be:

- Written as version-controlled files (Alembic for Python).
- Reversible (have a `downgrade()` function).
- Reviewed for performance impact (index creation, lock analysis).
- Tested against a staging database before production.
- Idempotent — gracefully handle re-runs.

```python
"""Add escrow_transactions table.

Revision ID: 002
Revises: 001
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"

def upgrade() -> None:
    op.create_table(
        "escrow_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("held_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_escrow_transactions")),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_escrow_transactions_order"),
        ),
        sa.CheckConstraint(
            "amount > 0",
            name=op.f("ck_escrow_transactions_amount_positive"),
        ),
    )
    op.create_index(
        op.f("ix_escrow_transactions_status"),
        "escrow_transactions",
        ["status"],
    )

def downgrade() -> None:
    op.drop_table("escrow_transactions")
```

---

## 5. Git Commit Message Conventions

### 5.1 Conventional Commits

Every commit message MUST adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short summary>

<body>

<footer>
```

**Allowed types:**

| Type | Usage |
|---|---|
| `feat` | A new feature (triggers MINOR version bump) |
| `fix` | A bug fix (triggers PATCH version bump) |
| `docs` | Documentation-only changes |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code restructuring (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `chore` | Build, CI, dependency changes |
| `ci` | CI configuration changes |
| `build` | Build system changes |
| `revert` | Reverts a previous commit |

**Scope values:**

| Scope | Area |
|---|---|
| `auth` | Authentication & authorization |
| `user` | User management |
| `seller` | Seller/KYC module |
| `product` | Catalog & listing |
| `order` | Orders & checkout |
| `payment` | Payment processing |
| `wallet` | Wallet & escrow |
| `dispute` | Dispute resolution |
| `msg` | Messaging system |
| `cms` | Content management |
| `api` | API structure/routing |
| `ui` | Frontend components |
| `db` | Database migrations |
| `infra` | Infrastructure |
| `ci` | CI/CD pipelines |
| `deps` | Dependencies |

### 5.2 Commit Message Format

**Subject line:** Maximum 72 characters. Imperative mood. Capitalized. No trailing period.

```
feat(auth): implement TOTP two-factor authentication
fix(wallet): correct balance calculation on concurrent withdrawals
refactor(order): extract escrow logic into dedicated service
```

**Body (optional):** Wrapped at 72 characters. Explains *why* the change was made, not *what*.

```
feat(payment): add bKash mobile payment gateway integration

Integrate the bKash merchant API for mobile banking payments.
This expands payment options for Bangladeshi users who prefer
mobile financial services over card payments.

- Add BkashGateway class implementing PaymentGateway protocol
- Create bkash_webhook handler for payment confirmation callbacks
- Store gateway reference and transaction ID in payment_transactions

Closes TSBL-427
```

**Footer (optional):** References to issues, breaking changes, co-authors.

```
BREAKING CHANGE: The process_payment() function now requires
a gateway_id parameter instead of a payment_method string.

Closes TSBL-512
Co-authored-by: Name <email>
```

### 5.3 Commit Best Practices

- Each commit represents a single logical change. Do not bundle unrelated changes.
- A commit should not contain both refactoring and feature work.
- `git rebase` to clean up commit history before merging into shared branches.
- Do not commit generated files, `.env` files, or credentials.
- Squash fixup commits before merging.

---

## 6. Code Review Standards

### 6.1 Review Process

Every pull request MUST receive at least one approved review from a qualified peer before merging. Critical paths (payment, wallet, escrow, authentication) require two approvals.

### 6.2 Review Checklist

Reviewers MUST verify:

- **Correctness:** Does the code satisfy the acceptance criteria? Are edge cases handled?
- **Security:** Are inputs validated? Are there injection vulnerabilities? Is authentication/authorization enforced?
- **Performance:** Are N+1 queries avoided? Are indexes used? Are expensive operations cached?
- **Error handling:** Are all failure modes handled? Are errors logged appropriately?
- **Observability:** Are relevant metrics, traces, and logs added?
- **Test coverage:** Are unit tests written for new logic? Do existing tests still pass?
- **Standards compliance:** Does code follow PEP 8 / ESLint rules? Type hints complete?
- **Backward compatibility:** Does the change break existing API contracts? Is versioning considered?
- **Documentation:** Are API docs updated? Are migration guides written if needed?
- **No sensitive data:** No passwords, tokens, PII in logs, comments, or commits.

### 6.3 Review Etiquette

- **Author:** Keep PRs small (< 400 lines changed). Provide context in the description. Respond to comments within 24 hours.
- **Reviewer:** Be constructive and specific. Use "blocking" vs "suggestion" labels. Approve only when all blocking comments are resolved.
- **Both:** Assume good faith. Focus on the code, not the author.

### 6.4 Automated Checks Before Review

The following MUST pass before a human review begins:

| Check | Tool |
|---|---|
| Lint | Ruff (Python), ESLint (TypeScript) |
| Format | Ruff format / Prettier |
| Type check | mypy (Python), tsc (TypeScript) |
| Unit tests | pytest / Vitest |
| Build | Docker build / Vite build |
| Security scan | Bandit (Python), npm audit |
| Commit lint | commitlint (Conventional Commits) |

---

## 7. Error Handling Patterns

### 7.1 Python / FastAPI Error Handling

**Define typed exception classes per domain:**

```python
class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str, status_code: int = 500) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: int | str) -> None:
        super().__init__(
            message=f"{entity} with id {entity_id} not found",
            code=f"{entity.upper()}_NOT_FOUND",
            status_code=404,
        )


class InsufficientBalanceError(AppError):
    def __init__(self, available: Decimal, requested: Decimal) -> None:
        super().__init__(
            message=f"Insufficient balance. Available: {available}, Requested: {requested}",
            code="INSUFFICIENT_BALANCE",
            status_code=422,
        )
```

**Global exception handler:**

```python
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.error(
        "Application error",
        extra={
            "code": exc.code,
            "message": exc.message,
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request.state.request_id,
            }
        },
    )
```

### 7.2 TypeScript Error Handling

**Use discriminated union for API errors:**

```typescript
interface ApiError {
  type: 'api_error';
  code: string;
  message: string;
  status: number;
}

interface NetworkError {
  type: 'network_error';
  message: string;
}

interface ValidationError {
  type: 'validation_error';
  fields: Record<string, string[]>;
}

type AppError = ApiError | NetworkError | ValidationError;
```

**Service-level error handling:**

```typescript
class EscrowService {
  async releaseFunds(orderId: number): Promise<Either<AppError, ReleaseResult>> {
    try {
      const response = await api.post(`/api/v1/escrow/${orderId}/release`);
      return right(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response) {
          return left({
            type: 'api_error',
            code: error.response.data.error.code,
            message: error.response.data.error.message,
            status: error.response.status,
          });
        }
        return left({
          type: 'network_error',
          message: 'Unable to reach the server. Please check your connection.',
        });
      }
      throw error; // Unexpected errors propagate
    }
  }
}
```

**React error boundary:**

```typescript
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  fallback: ReactNode;
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    logger.error('React component error', { error, componentStack: info.componentStack });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}
```

### 7.3 General Principles

- Never swallow exceptions silently. If caught, log and re-raise or handle appropriately.
- Fail fast: validate inputs at boundary (API layer), not deep in business logic.
- Use "Either" monad pattern (`@returns` / `@error` in Python Union types) for expected failures.
- Unexpected errors (programming mistakes) should propagate to a top-level handler, not be caught.
- Network and I/O errors at boundaries must have retry logic with exponential backoff.

---

## 8. Logging Standards

### 8.1 Logging Framework

| Platform | Library | Configuration |
|---|---|---|
| Python | `structlog` (structured logging) | JSON output to stdout, file rotation in production |
| TypeScript | `pino` (low-overhead structured) | JSON output, transports in production |

### 8.2 Log Levels and Usage

| Level | Usage | Frequency |
|---|---|---|
| `TRACE` | Detailed debug, request/response bodies | Development only |
| `DEBUG` | Developer diagnostics, state transitions | Conditional (feature-flag gated) |
| `INFO` | Business events (order created, payment received) | Normal operation |
| `WARN` | Unexpected but handled conditions (retry, fallback) | Monitor |
| `ERROR` | Failure requiring investigation (DB connection lost) | Alert |
| `CRITICAL` | System-level failure (service down, data corruption) | Pager |

### 8.3 Standard Fields

Every log entry MUST include:

```json
{
  "timestamp": "2026-07-01T10:30:00.000Z",
  "level": "INFO",
  "logger": "escrow_service",
  "message": "Escrow released successfully",
  "request_id": "req_abc123",
  "trace_id": "trace_xyz789",
  "service": "order-service",
  "environment": "production",
  "version": "1.2.3",
  "module": "app.services.escrow",
  "function": "release_escrow",
  "line": 42
}
```

### 8.4 Logging in Python

```python
import structlog

logger = structlog.get_logger()

async def release_escrow(order_id: int) -> EscrowTransaction:
    logger.info("Releasing escrow", order_id=order_id)
    try:
        transaction = await escrow_repository.release(order_id)
        logger.info(
            "Escrow released successfully",
            order_id=order_id,
            transaction_id=transaction.id,
            amount=str(transaction.amount),
            release_type=transaction.release_type.value,
        )
        return transaction
    except EscrowNotFoundError:
        logger.warn("Escrow not found for release", order_id=order_id)
        raise
    except Exception:
        logger.error("Failed to release escrow", order_id=order_id, exc_info=True)
        raise
```

### 8.5 Logging in TypeScript

```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  transport: process.env.NODE_ENV === 'development'
    ? { target: 'pino-pretty' }
    : undefined,
  redact: {
    paths: ['req.headers.authorization', 'req.body.password', 'req.body.confirmPassword'],
    censor: '[REDACTED]',
  },
});

export { logger };
```

### 8.6 What NOT to Log

- Passwords, password hashes, PINs, or security answers
- JWT tokens, API keys, or session tokens
- Full credit card numbers or CVV codes
- PII (email, phone, address) unless anonymized or legally permitted
- Database connection strings containing credentials
- Private keys or certificate content

---

## 9. Testing Standards

### 9.1 General Requirements

| Metric | Threshold |
|---|---|
| Line coverage (backend) | ≥ 85% |
| Line coverage (frontend) | ≥ 75% |
| Branch coverage | ≥ 80% |
| New code coverage | ≥ 90% |
| Unit test pass rate | 100% (blocking) |

Test type distribution target: 60% unit, 25% integration, 15% E2E.

### 9.2 Naming Conventions

- **Test files:** `{module}_test.py` (Python), `{component}.test.tsx` (TypeScript).
- **Test functions:** `test__{scenario}__{expected_outcome}`.
- **Test classes:** `Test{ServiceName}`.

```python
def test__release_escrow__with_held_funds__releases_successfully():
def test__release_escrow__with_already_released__raises_error():
```

```typescript
describe('EscrowService', () => {
  describe('releaseFunds', () => {
    it('releases escrow when funds are held', async () => { ... });
    it('throws error when escrow is already released', async () => { ... });
  });
});
```

### 9.3 Structure

- **Arrange-Act-Assert (AAA)** pattern mandatory.
- Use factories/fixtures for test data — never share mutable state between tests.
- Mock external services at the boundary, not deep inside business logic.

Refer to [DEV-TSBL-004 Testing Strategy](./04-testing-strategy.md) for detailed testing methodology.

---

## 10. Documentation Standards

### 10.1 Inline Comments

- Comments explain *why*, not *what*. The code itself should express *what*.
- Use comments for: non-obvious business rules, complex algorithm rationale, workaround explanations, and TODO items (with ticket reference).
- Delete commented-out code before merging. Do not leave dead code.

### 10.2 README Standards

Every package/module MUST have a `README.md` containing:

| Section | Required |
|---|---|
| Title and description | Yes |
| Prerequisites and dependencies | Yes |
| Setup and installation instructions | Yes |
| Configuration (environment variables) | Yes |
| Run commands (dev, test, build, lint) | Yes |
| Project structure overview | Recommended |
| API documentation links | If applicable |
| Deployment instructions | If applicable |

### 10.3 API Documentation

- All FastAPI routes MUST be documented via OpenAPI (auto-generated with Pydantic models).
- Each endpoint MUST have `summary`, `description`, and response model.
- Use `responses={...}` to document error codes.
- Generate and publish OpenAPI spec on every release.

### 10.4 Architecture Decision Records (ADRs)

Significant architectural decisions MUST be documented in `docs/adr/` using the following template:

```markdown
# ADR-{NNN}: {Title}

**Status:** [Proposed | Accepted | Deprecated | Superseded]

**Date:** YYYY-MM-DD

## Context
...

## Decision
...

## Consequences
...
```

---

## 11. Security Coding Guidelines

### 11.1 Input Validation

- Validate all input at the API boundary using Pydantic (backend) or Zod (frontend).
- Never trust client-side validation alone; re-validate on the server.
- Use allowlists (positive validation) over denylists where possible.
- Sanitize all user input rendered in HTML to prevent XSS. React auto-escapes, but handle `dangerouslySetInnerHTML` with extreme care.

### 11.2 Authentication and Authorization

- Enforce authorization at the API layer using dependency injection (`Depends(RoleChecker(...))`).
- Never rely on frontend-only authorization hiding; always verify on backend.
- Invalidated tokens MUST be checked against a blocklist on every request requiring elevated privileges.
- Rate-limit authentication endpoints (5 attempts/min per IP, 10 attempts/hr per account).

### 11.3 SQL Injection Prevention

- Use parameterized queries exclusively. No raw string interpolation in SQL.
- ORM queries (SQLAlchemy) must use ORM methods; raw SQL is allowed only in migrations and must use `text()` with bind parameters.

```python
# Correct
result = await db.execute(
    sa.text("SELECT * FROM users WHERE email = :email"),
    {"email": email},
)

# Incorrect — SQL injection vulnerability
result = await db.execute(
    sa.text(f"SELECT * FROM users WHERE email = '{email}'"),
)
```

### 11.4 Secrets Management

- No secrets in code, config files, or Docker images.
- Use environment variables or a vault service (HashiCorp Vault, AWS Secrets Manager).
- `.env` files are for development only and MUST be in `.gitignore`.

### 11.5 Data Protection

- Encrypt PII at rest using AES-256-GCM.
- Hash passwords with bcrypt (cost factor ≥ 12) or argon2id.
- TLS 1.3 for all data in transit.
- Mask sensitive data in logs (credit card last 4 digits, partial email).

### 11.6 Dependencies

- Regularly audit dependencies for known vulnerabilities: `poetry audit`, `npm audit`, `pnpm audit`.
- Pin exact versions in lock files. Review dependency updates in PRs.
- No packages with known critical vulnerabilities may be used.
- Use `safety` (Python) and `Socket` (npm) in CI for supply chain security.

### 11.7 Frontend Security

- Set strict Content-Security-Policy headers.
- Use `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`.
- Implement Subresource Integrity (SRI) for CDN-loaded scripts.
- Sanitize URLs before using in `window.open`, `location.href`, or `<a href>` to prevent `javascript:` protocol injection.

### 11.8 File Upload Security

- Validate file type by magic bytes (MIME not sufficient).
- Scan uploaded files for malware.
- Store uploaded files outside the web root; serve via signed URLs.
- Limit file size (configurable per context, default 10 MB).

---

*End of Document — DEV-TSBL-001*
