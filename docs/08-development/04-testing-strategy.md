# Testing Strategy

## TRUE STAR BD LIMITED — Digital Marketplace Platform

| Document ID | DEV-TSBL-004 |
|---|---|
| Version | 1.0 |
| Date | July 1, 2026 |
| Author | Software Architecture Division |
| Status | Approved |
| Classification | Internal — Confidential |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Test Pyramid](#2-test-pyramid)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [API Testing](#5-api-testing)
6. [Frontend Testing](#6-frontend-testing)
7. [End-to-End Testing](#7-end-to-end-testing)
8. [Load and Performance Testing](#8-load-and-performance-testing)
9. [Security Testing](#9-security-testing)
10. [Test Data Management](#10-test-data-management)
11. [Coverage Thresholds and Targets](#11-coverage-thresholds-and-targets)
12. [CI Integration of Tests](#12-ci-integration-of-tests)
13. [Test Environment Management](#13-test-environment-management)

---

## 1. Introduction

This document defines the comprehensive testing strategy for the TRUE STAR BD LIMITED Digital Marketplace Platform. The strategy is aligned with industry best practices (ISO/IEC 25010, ISTQB) and tailored to the specific risk profile of a financial digital marketplace handling payments, escrow, and user data.

### 1.1 Testing Principles

| Principle | Description |
|---|---|
| **Shift left** | Find defects as early as possible in the development lifecycle. Unit tests run on every keystroke (watch mode). |
| **Risk-based prioritization** | Test effort is proportional to business risk. Payment, escrow, and auth logic receive the highest coverage. |
| **Deterministic tests** | Tests must produce the same result every run. Flaky tests are treated as defects with a 24-hour SLA to fix or quarantine. |
| **Fast feedback** | Unit tests complete in < 30 seconds. Integration tests in < 5 minutes. Full CI suite in < 15 minutes. |
| **Test the behavior, not the implementation** | Tests assert on observable outcomes (return values, state changes, side effects), not internal implementation details. |

### 1.2 Test Tools

| Layer | Python (Backend) | TypeScript (Frontend) |
|---|---|---|
| Test framework | pytest 8+ | Vitest |
| Assertions | pytest built-in + `pytest-check` | Vitest built-in (`expect`) |
| Mocking | `pytest-mock` (unittest.mock) | `vi.fn()`, `vi.mock()` |
| HTTP mocking | `httpx` + `respx` | `msw` (Mock Service Worker) |
| Coverage | `pytest-cov` | `@vitest/coverage-v8` |
| Property-based | `hypothesis` | `fast-check` |
| Fixtures | `pytest-fixtures` | `vitest-fixtures` (optional) |
| Faker | `faker` | `@faker-js/faker` |
| DB testing | `pytest-asyncio` + `SQLAlchemy` | N/A |
| E2E | Playwright (Python) | Playwright (TypeScript) |
| API testing | `httpx.AsyncClient` (with FastAPI `TestClient`) | N/A |

---

## 2. Test Pyramid

### 2.1 Pyramid Structure for This Project

```
              ╱╲
             ╱  ╲               E2E (5–10%)
            ╱    ╲
           ╱──────╲
          ╱        ╲           Integration / API (20–30%)
         ╱          ╲
        ╱────────────╲
       ╱              ╲
      ╱                ╲      Unit (60–70%)
     ╱                  ╲
    ╱────────────────────╲
```

### 2.2 Distribution Targets

| Layer | Percentage | Time Budget | Run Frequency |
|---|---|---|---|
| Unit | 60–70% | < 30 sec | On every save (watch mode) |
| Integration / API | 20–30% | < 5 min | On every push to `main` / PR |
| End-to-End | 5–10% | < 15 min | On staging deploy, pre-release |
| Performance | 1–2% | < 30 min | Weekly / pre-major-release |
| Security | 1–2% | < 20 min | Nightly + pre-release |

### 2.3 What Each Layer Covers

| Layer | Scope | Test Doubles | Environment |
|---|---|---|---|
| Unit | Single function, class, or module | All external dependencies mocked | Isolated |
| Integration | Service + repository + DB | External APIs mocked, real DB | Dedicated test DB |
| API | Route handler → service → DB | External APIs mocked | Dedicated test DB |
| Component | Single React component | Child components mocked, API mocked | JSDOM |
| E2E | Full user journey | Sandbox/simulated external services | Staging environment |

---

## 3. Unit Testing

### 3.1 Python Unit Testing (pytest)

#### 3.1.1 Test Structure and Naming

```python
# tests/unit/services/test_escrow_service.py

from decimal import Decimal
from datetime import datetime, timezone

import pytest
from pytest_mock import MockerFixture

from app.models.order import OrderStatus
from app.models.escrow import EscrowStatus
from app.services.escrow import EscrowService


class TestEscrowService:
    """Tests for the EscrowService domain logic."""

    async def test_release_funds__with_valid_order__releases_successfully(
        self,
        mocker: MockerFixture,
        escrow_repository_mock,
        order_repository_mock,
    ) -> None:
        """Held escrow funds are released when delivery is confirmed."""
        # Arrange
        order_id = 1
        expected_amount = Decimal("150.00")
        escrow_repository_mock.get_by_order.return_value = EscrowFactory(
            status=EscrowStatus.HELD,
            amount=expected_amount,
        )
        escrow_repository_mock.release.return_value = EscrowFactory(
            status=EscrowStatus.RELEASED,
            released_at=datetime.now(timezone.utc),
        )
        service = EscrowService(
            escrow_repo=escrow_repository_mock,
            order_repo=order_repository_mock,
        )

        # Act
        result = await service.release_funds(order_id)

        # Assert
        assert result.status == EscrowStatus.RELEASED
        assert result.amount == expected_amount
        assert result.released_at is not None
        escrow_repository_mock.release.assert_awaited_once_with(order_id)

    async def test_release_funds__with_already_released__raises_error(
        self,
        mocker: MockerFixture,
        escrow_repository_mock,
    ) -> None:
        """Releasing already-released escrow raises a domain error."""
        # Arrange
        order_id = 1
        escrow_repository_mock.get_by_order.return_value = EscrowFactory(
            status=EscrowStatus.RELEASED,
        )
        service = EscrowService(escrow_repo=escrow_repository_mock)

        # Act & Assert
        with pytest.raises(DuplicateReleaseError, match="already released"):
            await service.release_funds(order_id)
```

#### 3.1.2 Python Mocking Standards

| Pattern | When to Use | Example |
|---|---|---|
| `mocker.patch` | External library (payment gateway SDK) | `mocker.patch("app.gateways.bkash.BkashClient.send_payment")` |
| `mocker.patch.object` | Method on an existing object | `mocker.patch.object(redis_client, "get", return_value=None)` |
| Repository mocks | Data access layer | `mocker.create_autospec(EscrowRepository)` |
| AsyncMock | Async function mocking | `mocker.async_patch("app.repositories.escrow.release")` |

#### 3.1.3 Fixtures

```python
# tests/conftest.py

import pytest_asyncio
from pytest_mock import MockerFixture
from faker import Faker

fake = Faker()


@pytest_asyncio.fixture
async def db_session():
    """Provide a test database session with transaction rollback."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with AsyncSession(conn, expire_on_commit=False) as session:
            yield session
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def escrow_repository_mock(mocker: MockerFixture):
    """Standard mock for EscrowRepository with all methods auto-specced."""
    return mocker.create_autospec(EscrowRepository, instance=True)
```

#### 3.1.4 What to Unit Test

- All service layer functions and methods.
- Repository methods with mocked DB session.
- Pydantic schema validation (edge cases for constraints, custom validators).
- Utility functions (currency formatting, date calculations, hashing).
- Exception classes and error handling logic.

#### 3.1.5 What NOT to Unit Test

- Configuration loading (tested by integration).
- Database engine and driver behavior (trusted external dependency).
- FastAPI request/response serialization (covered by API tests).
- Third-party library internals.

### 3.2 TypeScript Unit Testing (Vitest)

#### 3.2.1 Test Structure

```typescript
// src/services/__tests__/escrow.service.test.ts

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EscrowService } from '../escrow.service';
import { EscrowStatus } from '@/types/escrow';
import { ApiError } from '@/lib/errors';

// Mock repository
const mockEscrowRepo = {
  getByOrder: vi.fn(),
  release: vi.fn(),
};

describe('EscrowService', () => {
  let service: EscrowService;

  beforeEach(() => {
    vi.clearAllMocks();
    service = new EscrowService(mockEscrowRepo as any);
  });

  describe('releaseFunds', () => {
    it('releases escrow when funds are held', async () => {
      mockEscrowRepo.getByOrder.mockResolvedValue({
        status: EscrowStatus.Held,
        amount: 150.0,
      });
      mockEscrowRepo.release.mockResolvedValue({
        status: EscrowStatus.Released,
        releasedAt: new Date(),
      });

      const result = await service.releaseFunds(1);

      expect(result.status).toBe(EscrowStatus.Released);
      expect(mockEscrowRepo.release).toHaveBeenCalledWith(1);
    });

    it('throws error when escrow is already released', async () => {
      mockEscrowRepo.getByOrder.mockResolvedValue({
        status: EscrowStatus.Released,
      });

      await expect(service.releaseFunds(1)).rejects.toThrow(ApiError);
      expect(mockEscrowRepo.release).not.toHaveBeenCalled();
    });

    it('handles repository failure gracefully', async () => {
      mockEscrowRepo.getByOrder.mockRejectedValue(new Error('DB connection lost'));

      await expect(service.releaseFunds(1)).rejects.toThrow('DB connection lost');
    });
  });
});
```

#### 3.2.2 What to Unit Test (Frontend)

| Component | What to Test |
|---|---|
| Services | All service methods with mocked HTTP (MSW) |
| Hooks | All custom hooks with mocked services |
| Utils | Pure utility functions (formatting, validation, math) |
| Zustand stores | State transitions, computed values |
| Reducers | State mutations given actions |
| Validation schemas | Zod/joi schema validation edge cases |

---

## 4. Integration Testing

### 4.1 Scope

Integration tests verify that multiple components work together correctly. In this project, the primary integration boundary is the **Service + Repository + Database** triad.

### 4.2 Python Integration Testing

```python
# tests/integration/services/test_escrow_service_integration.py

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.escrow import EscrowService
from app.repositories.escrow import EscrowRepository
from app.repositories.order import OrderRepository
from app.models.order import OrderStatus
from tests.factories import OrderFactory, EscrowFactory


@pytest.mark.asyncio
class TestEscrowServiceIntegration:
    """Integration tests for EscrowService with real DB."""

    async def test_full_escrow_lifecycle(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Verifies the complete escrow hold → release lifecycle."""
        # Arrange
        escrow_repo = EscrowRepository(db_session)
        order_repo = OrderRepository(db_session)
        service = EscrowService(escrow_repo, order_repo)

        order = OrderFactory(status=OrderStatus.DELIVERED)
        db_session.add(order)
        escrow = EscrowFactory(order_id=order.id, amount=Decimal("200.00"), status="held")
        db_session.add(escrow)
        await db_session.commit()

        # Act
        result = await service.release_funds(order.id)

        # Assert
        assert result.status == "released"
        assert result.released_at is not None

        # Verify DB state
        updated_escrow = await escrow_repo.get_by_order(order.id)
        assert updated_escrow.status == "released"
        assert updated_escrow.released_at is not None
```

### 4.3 Test Database Configuration

```python
# tests/conftest.py

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import get_test_settings

TEST_DATABASE_URL = get_test_settings().database_url

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Each test gets a transaction that is rolled back after."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session
    await session.close()
    await transaction.rollback()
    await connection.close()
```

### 4.4 External Service Mocking in Integration Tests

External HTTP-based services (payment gateways, email, SMS) are mocked using **respx** (Python HTTP mock):

```python
@pytest.mark.asyncio
async def test_payment_gateway_call(respx_mock, db_session):
    """Integration test with mocked payment gateway HTTP call."""
    respx_mock.post("https://api.bkash.com/checkout/payment").mock(
        return_value=httpx.Response(200, json={
            "transactionId": "TXN123",
            "status": "COMPLETED",
        })
    )
    # ... rest of test
```

---

## 5. API Testing

### 5.1 FastAPI API Testing (pytest + httpx)

API tests verify the full request/response cycle including route validation, authentication, serialization, and error responses.

```python
# tests/api/v1/test_orders.py

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.core.security import create_access_token

app = create_app()


@pytest.mark.asyncio
class TestOrderAPI:
    """API tests for the orders endpoint."""

    async def test_get_order__with_valid_id__returns_200(self, db_session):
        """A valid order request returns 200 with order data."""
        # Arrange
        order = OrderFactory(id=1, buyer_id=1)
        db_session.add(order)
        await db_session.commit()

        token = create_access_token(subject="1", roles=["buyer"])

        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/v1/orders/1",
                headers={"Authorization": f"Bearer {token}"},
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "amount" in data

    async def test_get_order__without_auth__returns_401(self):
        """Unauthenticated requests are rejected."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/v1/orders/1")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "NOT_AUTHENTICATED"

    async def test_get_order__nonexistent__returns_404(self, db_session):
        """Requests for non-existent orders return 404."""
        token = create_access_token(subject="1", roles=["buyer"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/v1/orders/99999",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "ORDER_NOT_FOUND"
```

### 5.2 API Test Coverage Requirements

| Endpoint Category | Required Test Scenarios |
|---|---|
| Public endpoints | Valid request, missing parameters, invalid types, rate limiting |
| Authenticated endpoints | Valid auth, missing token, expired token, malformed token |
| Authorized endpoints | Correct role, insufficient role, admin override |
| CRUD endpoints | Create, read, update, delete, partial update, non-existent resource |
| Paginated endpoints | Page 1, page N, empty page, invalid page parameter |
| Search endpoints | Empty query, special characters, SQL injection attempt, no results |
| Payment endpoints | Success, declined, insufficient funds, gateway timeout, webhook signature mismatch |
| File upload endpoints | Valid file, wrong type, too large, no file, multiple files |
| WebSocket endpoints | Connect, disconnect, message send, malformed message |

---

## 6. Frontend Testing

### 6.1 Component Testing (React Testing Library)

```typescript
// src/components/orders/__tests__/OrderTimeline.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { OrderTimeline } from '../OrderTimeline';
import { OrderStatus } from '@/types/order';

// Wrapper for react-query
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe('OrderTimeline', () => {
  const mockEvents = [
    { id: 1, status: OrderStatus.Placed, timestamp: '2026-06-30T10:00:00Z' },
    { id: 2, status: OrderStatus.Paid, timestamp: '2026-06-30T10:05:00Z' },
    { id: 3, status: OrderStatus.Delivered, timestamp: '2026-06-30T11:00:00Z' },
  ];

  it('renders all timeline events', () => {
    render(<OrderTimeline events={mockEvents} />, { wrapper: createWrapper() });

    expect(screen.getByText('Placed')).toBeInTheDocument();
    expect(screen.getByText('Paid')).toBeInTheDocument();
    expect(screen.getByText('Delivered')).toBeInTheDocument();
  });

  it('shows timestamp in relative format', () => {
    render(<OrderTimeline events={mockEvents} />, { wrapper: createWrapper() });

    expect(screen.getByText(/ago/)).toBeInTheDocument();
  });

  it('renders empty state when no events', () => {
    render(<OrderTimeline events={[]} />, { wrapper: createWrapper() });

    expect(screen.getByText(/no timeline events/i)).toBeInTheDocument();
  });

  it('expands details on click', async () => {
    const user = userEvent.setup();

    render(<OrderTimeline events={mockEvents} />, { wrapper: createWrapper() });

    await user.click(screen.getByText('Paid'));

    await waitFor(() => {
      expect(screen.getByText(/payment details/i)).toBeVisible();
    });
  });
});
```

### 6.2 Component Testing Standards

| Aspect | Standard |
|---|---|
| Render | Test default render, loading state, empty state, error state |
| User interaction | Test clicks, form input, keyboard navigation using `userEvent` |
| Accessibility | Use `jest-axe` or `@testing-library/jest-dom` for a11y assertions |
| Mocking | Mock child components with `vi.mock()` when testing parent isolation |
| Query client | Wrap in `QueryClientProvider` with `retry: false` for testing |
| Router | Wrap in `MemoryRouter` for components using `useNavigate`, `useParams` |
| Assertions | Use `@testing-library/jest-dom` matchers (`toBeVisible`, `toBeDisabled`, etc.) |

**Do NOT test:**
- Internal component state (implementation detail).
- Style/CSS class names (fragile).
- Third-party library internals (trusted).

### 6.3 Hook Testing

```typescript
// src/hooks/__tests__/useWalletBalance.test.ts

import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import { useWalletBalance } from '../useWalletBalance';

const server = setupServer(
  http.get('/api/v1/wallet/balance', () => {
    return HttpResponse.json({ balance: 1250.50, currency: 'BDT' });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('useWalletBalance', () => {
  it('fetches and returns wallet balance', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useWalletBalance(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.balance).toBe(1250.50);
    expect(result.current.data?.currency).toBe('BDT');
  });
});
```

---

## 7. End-to-End Testing

### 7.1 Framework: Playwright

E2E tests are written in TypeScript using Playwright and run against the staging environment.

### 7.2 Test Structure

```
e2e/
  config/
    playwright.config.ts
  fixtures/
    auth.ts              # Authenticated user fixture
    wallet.ts            # Wallet state fixture
  page-objects/
    login.page.ts
    checkout.page.ts
    wallet.page.ts
    seller-dashboard.page.ts
  specs/
    auth/
      login.spec.ts
      registration.spec.ts
      2fa-setup.spec.ts
    marketplace/
      browse-products.spec.ts
      search.spec.ts
    checkout/
      complete-purchase.spec.ts
      coupon-application.spec.ts
    wallet/
      deposit.spec.ts
      withdrawal.spec.ts
    seller/
      product-listing.spec.ts
      order-fulfillment.spec.ts
```

### 7.3 Example E2E Test

```typescript
// e2e/specs/checkout/complete-purchase.spec.ts

import { test, expect } from '@playwright/test';
import { LoginPage } from '../../page-objects/login.page';
import { ProductPage } from '../../page-objects/product.page';
import { CheckoutPage } from '../../page-objects/checkout.page';

test.describe('Complete purchase flow', () => {
  test('buyer purchases a digital product and receives it', async ({ page }) => {
    // Arrange — login as buyer
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginAs('buyer@test.tsbl.com', 'test-password-123');

    // Act — browse, add to cart, checkout
    const productPage = new ProductPage(page);
    await productPage.gotoProduct('premium-website-template');
    await productPage.addToCart();

    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.proceedToCheckout();
    await checkoutPage.selectPaymentMethod('bkash');
    await checkoutPage.completePayment();

    // Assert — order confirmation
    await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
    await expect(page.locator('[data-testid="order-number"]')).not.toBeEmpty();

    // Assert — product is accessible in library
    await page.goto('/library');
    await expect(page.locator('text=premium-website-template')).toBeVisible();
    await expect(page.locator('[data-testid="download-button"]')).toBeEnabled();
  });
});
```

### 7.4 E2E Test Design Principles

- **Page Object Model:** All page interactions are encapsulated in page object classes.
- **Test data isolation:** Each test creates its own test data (user, product, order) via API calls before the test starts.
- **No shared state:** Tests do not depend on other tests. Run order is irrelevant.
- **Retry flaky tests:** `retries: 2` in Playwright config for CI.
- **Trace on failure:** `trace: 'on-first-retry'` captures video, network, and console logs on failure.
- **Smoke vs. full suite:** Smoke tests (critical paths) run on every staging deploy. Full suite runs before releases.

### 7.5 E2E Critical Paths (Smoke Tests)

| Flow | Priority | Description |
|---|---|---|
| User registration | Critical | Guest → Register → Email verification → Login |
| Product purchase | Critical | Browse → View product → Add to cart → Checkout → Payment → Download |
| Seller listing | High | Login as seller → Create product → Publish → View in marketplace |
| Wallet deposit | Critical | Login → Deposit → Verify balance update |
| Wallet withdrawal | High | Login (seller) → Request withdrawal → Admin approve → Verify payout |
| Escrow release | Critical | Buyer purchases → Seller delivers → Buyer confirms → Escrow released |
| Search | High | Search by keyword → Filter → Paginate → View results |

---

## 8. Load and Performance Testing

### 8.1 Tool: k6

Load testing is performed using **k6** (Grafana) for its JavaScript-based scripting, low overhead, and rich metrics output.

### 8.2 Test Scenarios

```javascript
// load-tests/scenarios/checkout-flow.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const checkoutDuration = new Trend('checkout_duration');

export const options = {
  stages: [
    { duration: '2m', target: 50 },    // Ramp up to 50 virtual users
    { duration: '5m', target: 50 },    // Stay at 50 for 5 minutes
    { duration: '2m', target: 100 },   // Ramp up to 100
    { duration: '5m', target: 100 },   // Stay at 100 for 5 minutes
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95% of requests under 2s
    http_req_failed: ['rate<0.01'],     // Less than 1% failure rate
    checkout_duration: ['p(95)<5000'],  // Checkout-specific: 95% under 5s
    errors: ['rate<0.05'],             // Less than 5% custom errors
  },
};

export default function () {
  const BASE_URL = __ENV.BASE_URL || 'http://staging.tsbl.com';

  // 1. Browse products
  const browseRes = http.get(`${BASE_URL}/api/v1/products?page=1&limit=20`);
  check(browseRes, { 'browse status 200': (r) => r.status === 200 });
  errorRate.add(browseRes.status !== 200);

  // 2. View product detail
  const productRes = http.get(`${BASE_URL}/api/v1/products/1`);
  check(productRes, { 'product detail 200': (r) => r.status === 200 });

  // 3. Simulate checkout (POST)
  const payload = JSON.stringify({
    product_id: 1,
    payment_method: 'bkash',
    coupon_code: '',
  });
  const checkoutRes = http.post(`${BASE_URL}/api/v1/orders`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  check(checkoutRes, {
    'checkout 201': (r) => r.status === 201,
    'order number present': (r) => r.json('order_number') !== undefined,
  });
  checkoutDuration.add(checkoutRes.timings.duration);
  errorRate.add(checkoutRes.status !== 201);

  sleep(1);
}
```

### 8.3 Performance Test Schedule

| Test Type | Frequency | Environment | Duration | Acceptance Criteria |
|---|---|---|---|---|
| Smoke test | Every release | Staging | 1 min | No failures at baseline load |
| Load test | Weekly | Staging | 15 min | p95 < 2s, 0% errors at target load |
| Stress test | Monthly | Staging | 30 min | Graceful degradation, no crash |
| Soak test | Pre-major-release | Staging | 4 hours | No memory leak, stable throughput |
| Spike test | Pre-major-release | Staging | 10 min | Auto-scaling responds within 2 min |

### 8.4 Performance Acceptance Criteria

| Metric | Target | Warning | Critical |
|---|---|---|---|
| API p95 response time | < 500ms | > 1s | > 2s |
| API p99 response time | < 1s | > 2s | > 5s |
| Error rate | < 0.1% | > 0.5% | > 1% |
| Throughput (orders/min) | 500 | < 300 | < 100 |
| CPU usage | < 60% | > 80% | > 90% |
| Memory usage | < 70% | > 85% | > 95% |
| Database connection pool utilization | < 60% | > 75% | > 90% |

---

## 9. Security Testing

### 9.1 Static Application Security Testing (SAST)

| Tool | Language | Run Frequency | Command |
|---|---|---|---|
| Bandit | Python | Every CI push | `bandit -r app/ --confidence-level=medium` |
| ESLint security plugin | TypeScript | Every CI push | `eslint-plugin-security` rules in ESLint config |
| SonarQube | All | Every push to `main` | `sonar-scanner` with security ruleset |
| CodeQL | All | Every push to `main` | GitHub CodeQL analysis |

### 9.2 Dynamic Application Security Testing (DAST)

| Tool | Frequency | Environment | Scope |
|---|---|---|---|
| OWASP ZAP | Nightly | Staging | Full scan: all endpoints, all parameters |
| OWASP ZAP API scan | Every release | Staging | OpenAPI-schema-based scan |

### 9.3 Dependency Scanning

| Tool | Check | Frequency | SLA |
|---|---|---|---|
| `safety` | Python known vulnerabilities | Every push | Block on CRITICAL/HIGH |
| `pnpm audit` | JavaScript known vulnerabilities | Every push | Block on CRITICAL/HIGH |
| Dependabot / Renovate | Automated dependency updates | Daily | PR raised for MEDIUM+ |
| Trivy | Container image vulnerabilities | Every push | Block on CRITICAL/HIGH |

### 9.4 Manual Security Testing

| Test Type | Frequency | Performer |
|---|---|---|
| Penetration test | Quarterly | External security vendor |
| Threat model review | Per major feature | Security champion + architect |
| Authentication review | Per release | Senior backend engineer |
| Authorization matrix audit | Per release | Security champion |

### 9.5 Security Test Cases (Automated)

```python
# tests/security/test_sql_injection.py

@pytest.mark.security
@pytest.mark.parametrize(
    "malicious_input",
    [
        "1; DROP TABLE users",
        "' OR '1'='1",
        "1 UNION SELECT * FROM users",
        "<script>alert('xss')</script>",
        "../../../etc/passwd",
    ],
)
async def test_product_search_sql_injection(client, malicious_input):
    """Search endpoint rejects SQL injection attempts."""
    response = await client.get(
        "/api/v1/products",
        params={"q": malicious_input},
    )
    assert response.status_code in (200, 422)
    # Ensure the injection did not succeed: no 500, no data leak
    if response.status_code == 200:
        data = response.json()
        assert "error" not in data or data["error"]["code"] != "INTERNAL_ERROR"
```

---

## 10. Test Data Management

### 10.1 Factories

Factories are used to generate test data consistently. Python uses `factory_boy`; TypeScript uses custom factory functions.

```python
# tests/factories.py

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from faker import Faker
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.escrow import EscrowTransaction, EscrowStatus

fake = Faker()


class UserFactory(factory.DeclarativeMeta):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.email())
    password_hash = "hashed_password_placeholder"
    role = FuzzyChoice([UserRole.BUYER, UserRole.SELLER])
    is_active = True
    kyc_status = "verified"
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year())


class OrderFactory(factory.DeclarativeMeta):
    class Meta:
        model = Order

    buyer_id = factory.Sequence(lambda n: n)
    seller_id = factory.Sequence(lambda n: n + 100)
    status = FuzzyChoice(list(OrderStatus))
    total_amount = FuzzyDecimal(10.00, 5000.00, precision=2)
    currency = "BDT"
    created_at = factory.LazyFunction(lambda: fake.date_time_this_month())


class EscrowFactory(factory.DeclarativeMeta):
    class Meta:
        model = EscrowTransaction

    order_id = factory.Sequence(lambda n: n)
    amount = FuzzyDecimal(10.00, 5000.00, precision=2)
    status = FuzzyChoice(list(EscrowStatus))
    held_at = factory.LazyFunction(lambda: fake.date_time_this_month())
```

### 10.2 Fixtures

```python
# tests/conftest.py

@pytest.fixture
def buyer_user(db_session):
    user = UserFactory(role=UserRole.BUYER)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def seller_user(db_session):
    user = UserFactory(role=UserRole.SELLER)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def escrowed_order(db_session, buyer_user, seller_user):
    order = OrderFactory(
        buyer_id=buyer_user.id,
        seller_id=seller_user.id,
        status=OrderStatus.DELIVERED,
    )
    escrow = EscrowFactory(
        order_id=order.id,
        amount=order.total_amount,
        status=EscrowStatus.HELD,
    )
    db_session.add_all([order, escrow])
    db_session.commit()
    return order, escrow
```

### 10.3 Test Data Seeding for Integration/E2E

```python
# tests/seed.py

"""Seed script for populating the test database with realistic data."""

async def seed_test_database(db_session: AsyncSession) -> dict:
    """Seed 50 users, 200 products, 500 orders with escrow entries."""
    users = UserFactory.create_batch(50)
    db_session.add_all(users)
    await db_session.commit()

    products = ProductFactory.create_batch(200, seller_id=factory.Sequence(
        lambda n: users[n % 50].id
    ))
    db_session.add_all(products)
    await db_session.commit()

    # ... create orders, escrow, payments, etc.

    return {
        "users": len(users),
        "products": len(products),
    }
```

### 10.4 Data Cleanup Strategy

| Test Type | Cleanup Strategy |
|---|---|
| Unit | No cleanup needed (all mocked) |
| Integration | Transaction rollback per test (fastest) |
| API | Transaction rollback + truncate tables between test classes |
| E2E | API calls to teardown created resources; truncate tables between test suites |
| Load | Dedicated DB re-created from seed before each test run |

---

## 11. Coverage Thresholds and Targets

### 11.1 Coverage Thresholds

| Metric | Backend (Python) | Frontend (TypeScript) |
|---|---|---|
| Line coverage | ≥ 85% | ≥ 75% |
| Branch coverage | ≥ 80% | ≥ 75% |
| Function coverage | ≥ 90% | ≥ 80% |
| New code coverage (diff) | ≥ 90% | ≥ 90% |

### 11.2 Coverage by Module Priority

| Module | Minimum Line Coverage | Risk Level |
|---|---|---|
| `services/escrow.py` | 95% | Critical |
| `services/payment.py` | 95% | Critical |
| `services/wallet.py` | 95% | Critical |
| `services/auth.py` | 95% | Critical |
| `services/order.py` | 90% | High |
| `api/v1/*` | 90% | High |
| `repositories/*` | 85% | High |
| `models/*` | 80% | Medium |
| `schemas/*` | 75% | Medium |
| `background/*` | 70% | Low |
| `core/config.py` | 60% | Low |

### 11.3 Coverage Enforcement

```yaml
# pyproject.toml
[tool.pytest.ini_options]
addopts = """
    --cov=app
    --cov-report=term-missing
    --cov-report=xml:coverage.xml
    --cov-report=html:coverage_html
    --cov-fail-under=85
"""
```

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        statements: 75,
        branches: 75,
        functions: 80,
        lines: 75,
      },
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.*', 'src/vite-env.d.ts'],
    },
  },
});
```

### 11.4 Coverage Gap Management

When coverage falls below threshold:

1. The CI pipeline fails.
2. A coverage report artifact is generated showing uncovered lines.
3. The team adds tests in the next sprint to close the gap.
4. Exemptions are granted only by the Architecture Division for non-testable code (trivial getters/setters, auto-generated code).

---

## 12. CI Integration of Tests

### 12.1 Test Execution in CI Pipeline

Refer to [DEV-TSBL-003 CI/CD Strategy](./03-cicd-strategy.md) for full pipeline details.

| CI Event | Tests Executed | Fail Behaviour |
|---|---|---|
| PR opened/synchronized | Unit tests (all), Lint, Type check | Block merge |
| Push to `main` | Unit tests, integration tests, API tests | Block deploy to staging |
| Push to `release/v*` | Full suite (unit + integration + API + E2E smoke) | Block deploy to staging |
| Tag push `v*` | Full suite (unit + integration + API + full E2E) | Block deploy to production |
| Nightly | Full suite + load tests + security scans | Alert on-call engineer |

### 12.2 Test Selection (Impact Analysis)

To optimize CI time, we implement test selection:

- Changed Python files → run related unit tests + all integration tests.
- Changed TypeScript files → run related component tests + all API mocks.
- Changed database migrations → run all integration tests.
- Changed CI configuration → run full suite.
- All other cases → run full suite (safe default).

```yaml
# GitHub Actions — test selection
- name: Determine test scope
  id: test-scope
  run: |
    CHANGED=$(git diff --name-only origin/main...HEAD)
    if echo "$CHANGED" | grep -q "^app/"; then
      echo "scope=full" >> $GITHUB_OUTPUT
    elif echo "$CHANGED" | grep -q "^src/"; then
      echo "scope=frontend" >> $GITHUB_OUTPUT
    else
      echo "scope=minimal" >> $GITHUB_OUTPUT
    fi
```

### 12.3 Flaky Test Management

| Process | Detail |
|---|---|
| Detection | Tests that fail intermittently in CI are flagged. |
| Quarantine | Flaky tests are moved to a separate `flaky` marker/suite and excluded from blocking CI. |
| SLA | A ticket is created. The flaky test must be fixed or removed within 5 business days. |
| Prevention | Tests must not depend on timing, order, global state, or external services without proper isolation. |

---

## 13. Test Environment Management

### 13.1 Environment Definitions

| Environment | Purpose | Database | External Services | Access |
|---|---|---|---|---|
| `local` | Developer workstation | Local PostgreSQL (Docker) | Mocked | Developer only |
| `ci` | GitHub Actions runner | Ephemeral PostgreSQL service | Mocked/respx | CI only |
| `staging` | Pre-production validation | Staging DB (anonymized prod snapshot) | Sandbox gateways | QA + Engineering |
| `production` | Live | Production DB | Live gateways | N/A (no testing) |

### 13.2 Local Development Environment

```bash
# docker-compose.test.yml — spin up test dependencies
version: "3.9"
services:
  postgres-test:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: tsbl_test
    ports:
      - "5433:5432"  # Different port to avoid conflict with local dev DB
  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"
```

```bash
# Run tests locally
pytest tests/ -v --cov=app
vitest run
```

### 13.3 Staging Environment

- Deployed automatically on push to `main` or `release/*`.
- Uses a dedicated PostgreSQL instance with anonymized production data.
- External services use sandbox/developer API keys.
- Accessible only within the corporate VPN.
- Seeds with baseline test data on each deploy (if migration changed schema).

### 13.4 Test Environment Cleanup

| Environment | Cleanup Frequency | Method |
|---|---|---|
| Local | On demand | `docker-compose down -v` |
| CI | After each job run | Ephemeral — destroyed when job ends |
| Staging | On each deploy | Alembic downgrade + upgrade + reseed |
| Staging (data) | Weekly | Refresh from anonymized production snapshot |

### 13.5 Environment Variables for Testing

```bash
# .env.test — loaded automatically by pytest/vitest
DATABASE_URL=postgresql+asyncpg://test:test@localhost:5433/tsbl_test
REDIS_URL=redis://localhost:6380/1
JWT_SECRET=test-secret-key-not-used-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
LOG_LEVEL=ERROR
ENVIRONMENT=test
BKASH_MERCHANT_ID=test_merchant
BKASH_API_KEY=test_api_key
BKASH_API_SECRET=test_secret
```

---

*End of Document — DEV-TSBL-004*
