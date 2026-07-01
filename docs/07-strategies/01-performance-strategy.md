# Performance Strategy

## 1. Performance Budget

### 1.1 Core Metrics & Targets

| Metric | Target | Critical | Measurement Tool |
|--------|--------|----------|-----------------|
| Time to First Byte (TTFB) | < 200ms | < 500ms | Lighthouse, RUM |
| API Response Time (P95) | < 100ms | < 300ms | APM, Custom Metrics |
| Page Load (LCP) | < 2.0s | < 4.0s | Lighthouse, CrUX |
| First Input Delay (FID) | < 100ms | < 300ms | CrUX, RUM |
| Cumulative Layout Shift (CLS) | < 0.1 | < 0.25 | Lighthouse, CrUX |
| Interaction to Next Paint (INP) | < 200ms | < 500ms | CrUX, RUM |
| API Availability | 99.9% | 99.5% | Uptime Monitoring |

### 1.2 Budget Enforcement

Performance budgets are enforced in CI/CD pipeline using Lighthouse CI. Builds exceeding budgets are flagged and may be blocked during freeze periods.

---

## 2. Database Query Optimization

### 2.1 N+1 Query Prevention

- **Detection**: Use Django Debug Toolbar in development; `nplusone` library raises warnings.
- **Auto-Prevention**: Custom Django model manager base class enforces `select_related` and `prefetch_related` on all `QuerySet` results.
- **Code Review Gate**: All PRs must include `assertNumQueries` tests for endpoints returning lists.
- **Tooling**: `django-silk` profiling runs on staging to identify N+1 patterns.

### 2.2 Eager Loading Strategy

| Scenario | Method | Example |
|----------|--------|---------|
| FK relationships | `select_related('fk_field')` | Product → Category |
| M2M/O2M relationships | `prefetch_related('related_set')` | Product → Variants |
| Nested eager loading | Chained select_related | Order → User → Profile |
| Custom prefetch | `Prefetch()` with queryset filters | Active products only |

### 2.3 Connection Pooling

- **Tool**: PgBouncer (transaction-level pooling mode).
- **Pool Size**: `min_pool_size=10`, `max_pool_size=100` per application instance.
- **Timeout**: `server_idle_timeout=300s`.
- **Monitoring**: Pool utilization, client wait time, server round-robin distribution.

### 2.4 Query Performance Rules

- All queries in hot paths must use covered indexes.
- Avoid `SELECT *` — always specify columns.
- Use `only()` and `defer()` for large column tables.
- Use `values()` or `values_list()` for read-only data fetches.
- Paginate all list endpoints — no unbounded queries.
- Use `EXPLAIN ANALYZE` on all queries before merging to main.

---

## 3. Caching Strategy

### 3.1 Multi-Tier Caching Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Browser Cache                       │
│  (Cache-Control, ETag, Expires headers)              │
├─────────────────────────────────────────────────────┤
│                  CDN Cache                            │
│  (CloudFront: TTL 300s static, 60s dynamic)          │
├─────────────────────────────────────────────────────┤
│              Application Cache                        │
│  (Redis: page fragments, serialized objects)          │
├─────────────────────────────────────────────────────┤
│              Query Cache                              │
│  (Redis: cached query results with TTL)              │
└─────────────────────────────────────────────────────┘
```

### 3.2 Redis Caching Layers

#### Query Cache
- **Key Pattern**: `query:{db}:{table}:{hash_of_params}`
- **TTL**: 60–300 seconds depending on data volatility.
- **Invalidation**: Write-through on model `post_save`/`post_delete` signals.
- **Eviction**: `allkeys-lru` — least-recently-used keys evicted first.

#### Page Cache
- **Key Pattern**: `page:{locale}:{path}:{user_group_hash}`
- **TTL**: 300 seconds for public pages, 60s for authenticated pages.
- **Storage**: Full rendered HTML fragments.
- **Invalidation**: Cache-busting via content version key; whole-page invalidate on CMS publish.

#### Fragment Cache
- **Key Pattern**: `frag:{template_name}:{object_id}:{variant}`
- **TTL**: Template-specific (product card: 300s, cart: 30s).
- **Usage**: `{% cache 300 product_card product.id %}` in Django templates.
- **Granularity**: Per-component caching — sidebar, recommendations, footer.

#### Session Cache
- **Storage**: Django sessions stored entirely in Redis.
- **TTL**: Session expiry + 15-minute sliding window.
- **Fallback**: If Redis is down, fall back to database sessions.

### 3.3 Cache Configuration

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis-cluster:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 100,
                "timeout": 5,
            },
        },
        "KEY_PREFIX": "tsbl",
    }
}
```

---

## 4. CDN Strategy

### 4.1 Static Content

- **Provider**: AWS CloudFront with S3 origin.
- **Cache Behavior**: `/static/*` — TTL 365 days, immutable.
- **Versioning**: Content hash in filename (`app.a1b2c3.js`).
- **Compression**: Brotli for JS/CSS, Gzip fallback.

### 4.2 Dynamic Content

- **Cache Behavior**: `/api/*` — TTL 0s (passthrough).
- **Origin Shield**: Enable CloudFront Origin Shield to reduce origin load.
- **Custom Error Pages**: Serve stale content from edge on 5xx origin errors.
- **Signed URLs**: Protected content (user uploads) served via signed CloudFront URLs with 1-hour expiry.

### 4.3 Geographic Distribution

- **Edge Locations**: Minimum 10 PoPs across NA, EU, APAC.
- **Origin**: Primary in `us-east-1`, failover in `eu-west-1`.
- **DNS**: Route53 latency-based routing to nearest CloudFront edge.

---

## 5. Image Optimization Pipeline

### 5.1 Pipeline Flow

```
Upload → Thumbnail Generation → Format Conversion → CDN Storage
  ├─ Original (full-res, stored for reprocessing)
  ├─ WebP (all sizes, primary delivery format)
  ├─ AVIF (modern browsers, content negotiation)
  └─ JPEG fallback (legacy browsers)
```

### 5.2 Responsive Images

```html
<img
  srcset="
    /media/product/photo-320w.webp 320w,
    /media/product/photo-640w.webp 640w,
    /media/product/photo-1280w.webp 1280w
  "
  sizes="(max-width: 600px) 320px, (max-width: 1200px) 640px, 1280px"
  src="/media/product/photo-640w.jpg"
  loading="lazy"
  alt="Product name"
/>
```

### 5.3 Optimization Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Max resolution | 2048px | Full-width retina display |
| Thumbnail | 150x150px | Grid/list views |
| WebP quality | 80 | 25-35% size reduction over JPEG |
| AVIF quality | 70 | 50% size reduction over JPEG |
| Compression level | Maximum | Server-side, no impact on user |
| Progressive JPEG | Enabled | Perceived load improvement |

### 5.4 Lazy Loading

- Native `loading="lazy"` for all below-fold images.
- Intersection Observer polyfill for older browsers.
- Blur-up placeholder technique: 20px version of image blurred with CSS.
- Preload critical above-fold images via `<link rel="preload">`.

---

## 6. Frontend Performance

### 6.1 Code Splitting

- **Route-level**: Lazy-load each page module with React `lazy()` + `Suspense`.
- **Component-level**: Heavy components (image galleries, maps, WYSIWYG editors) loaded on interaction.
- **Vendor Splitting**: Separate chunk for `react`, `react-dom`, `lodash` (stable rarely updated).
- **Dynamic Imports**: `import('@/components/HeavyChart')` triggers chunk loading.

### 6.2 Tree Shaking

- Build tool: Webpack with `sideEffects: false` in `package.json`.
- ES module imports only (`import { map } from 'lodash-es'` not `import _ from 'lodash'`).
- Dead code elimination enforced via lint rule: `no-unused-modules`.
- Bundle analysis integrated into CI: `webpack-bundle-analyzer` on every build.

### 6.3 Bundle Analysis

| Metric | Current | Target | Action if Exceeded |
|--------|---------|--------|--------------------|
| Total JS bundle | < 300 KB | < 200 KB | Audit dependencies |
| CSS bundle | < 50 KB | < 30 KB | Purge unused CSS |
| First load JS | < 150 KB | < 100 KB | Split further |
| Chunk count | < 20 | < 15 | Merge small chunks |

### 6.4 Rendering Strategy (SSR/ISR)

- **Public Pages** (product listing, homepage): ISR via Next.js with 60s revalidation.
- **SEO Pages** (product detail, category): SSR with Redis cache layer.
- **Authenticated Pages** (dashboard, checkout): Client-side rendering with API calls.
- **Edge SSR**: Critical pages at CloudFront edge via Lambda@Edge for sub-100ms response.

---

## 7. Backend Performance

### 7.1 Async Processing

- **Celery Tasks**: Email sending, report generation, image processing, data exports.
- **Task Priority**:
  - `critical` (order confirmation emails) — immediate delivery.
  - `high` (image processing) — 10s delay tolerance.
  - `medium` (report generation) — 60s delay tolerance.
  - `low` (analytics aggregation) — 5min delay tolerance.
- **Result Backend**: Redis with 1-hour expiry on task results.

### 7.2 Background Tasks

| Task | Queue | Priority | Concurrency | Timeout |
|------|-------|----------|-------------|---------|
| Send email | `email` | 5 | 10 | 30s |
| Process image | `media` | 4 | 4 | 300s |
| Generate report | `reports` | 2 | 2 | 600s |
| Sync inventory | `sync` | 3 | 3 | 120s |
| Aggregate analytics | `analytics` | 1 | 1 | 900s |

### 7.3 WSGI/ASGI Server Configuration

- **Sync Endpoints**: Gunicorn with `gevent` workers, 4 workers per core.
- **Async Endpoints**: Uvicorn with `uvloop`, 8 workers per core.
- **Keep-Alive**: 30 seconds, max 100 requests per connection.
- **Graceful Shutdown**: 30-second timeout for in-flight requests.

---

## 8. API Performance

### 8.1 Pagination

- **Default**: 20 items per page, max 100.
- **Cursor-based pagination** for real-time feeds (orders, notifications).
- **Offset-based pagination** for admin interfaces.
- **Pagination headers**: `X-Total-Count`, `X-Page`, `X-Per-Page`, `Link` (RFC 5988).

### 8.2 Field Selection

- **GraphQL**: Query only requested fields (primary API paradigm).
- **REST**: `?fields=id,name,price` — sparse fieldset support.
- **Expand**: `?expand=category,variants` — embedded related resources on demand only.
- **Default**: Minimal payload — expand must be explicitly requested.

### 8.3 Compression

- **Content-Type**: `application/json` always compressed.
- **Algorithm**: Brotli (`br`) preferred, Gzip (`gzip`) fallback.
- **Minimum Size**: Compress responses over 1 KB.
- **Compression Level**: Brotli level 5 (balance of speed/ratio).

### 8.4 API Response Time Budget

| Endpoint Type | P95 Target | P99 Target | Timeout |
|---------------|------------|------------|---------|
| Product list (cached) | 50ms | 100ms | 1s |
| Product detail (cached) | 50ms | 100ms | 1s |
| Checkout (uncached) | 500ms | 1s | 5s |
| Search | 200ms | 500ms | 3s |
| Admin reports | 2s | 5s | 30s |

---

## 9. Load Testing Approach

### 9.1 Testing Types

| Type | Tool | Frequency | Target |
|------|------|-----------|--------|
| Baseline | k6 (1 VU) | Every PR | Establish baseline metrics |
| Load | k6 (100 VU, 10min) | Weekly | Verify sustained performance |
| Stress | k6 (1000 VU ramp) | Bi-weekly | Identify breaking point |
| Soak | Locust (200 VU, 4hr) | Monthly | Detect memory leaks |
| Spike | k6 (0→500 VU instant) | Monthly | Test auto-scaling response |

### 9.2 Load Testing Targets

| Scenario | Target Throughput | Target Latency (P95) | Acceptable Latency (P99) |
|----------|------------------|----------------------|--------------------------|
| Browse products | 1000 req/s | < 200ms | < 500ms |
| Search products | 500 req/s | < 300ms | < 1s |
| Add to cart | 200 req/s | < 100ms | < 300ms |
| Checkout | 100 req/s | < 500ms | < 2s |
| Admin dashboard | 50 req/s | < 1s | < 3s |

### 9.3 Test Infrastructure

- **Tool**: k6 for API testing, Lighthouse CI for frontend testing.
- **Execution**: GitHub Actions scheduled tests against staging environment.
- **Reporting**: InfluxDB + Grafana dashboards for trend analysis.
- **Thresholds**: k6 thresholds defined in test scripts — build fails if breached.

### 9.4 Performance Regression Process

1. PR triggers load test against dedicated staging instance.
2. Results compared against baseline stored in InfluxDB.
3. Any metric exceeding baseline by 20% flagged in PR.
4. Developers must investigate and optimize before merge.
5. Weekly performance review meeting reviews dashboards.

---

## 10. Implementation Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| Q1 2026 | Month 1-2 | Redis caching tier, CDN setup, image pipeline |
| Q1 2026 | Month 2-3 | Query optimization, N+1 prevention, connection pooling |
| Q2 2026 | Month 4-5 | Frontend code splitting, SSR optimization |
| Q2 2026 | Month 5-6 | Load testing infrastructure, CI integration |
| Q3 2026 | Month 7-8 | Async processing, background task refactor |
| Q3 2026 | Month 8-9 | Performance budget enforcement, monitoring dashboards |

---

*Document Owner: Principal Architect*  
*Last Updated: 2026-07-01*  
*Review Cycle: Quarterly*
