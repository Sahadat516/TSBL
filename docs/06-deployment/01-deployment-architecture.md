# Deployment Architecture

| **Document Owner** | VP of Platform Engineering |
|---|---|
| **Classification** | Confidential — Internal Use Only |
| **Version** | 1.0 |
| **Last Updated** | 2026-07-01 |
| **Approved By** | CTO, TRUE STAR BD LIMITED |

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Deployment Overview](#2-deployment-overview)
3. [Docker Containerization Strategy](#3-docker-containerization-strategy)
4. [Docker Compose Configuration](#4-docker-compose-configuration)
5. [NGINX Configuration](#5-nginx-configuration)
6. [Service Mesh Architecture](#6-service-mesh-architecture)
7. [Environment-Specific Configurations](#7-environment-specific-configurations)
8. [Database Migration Deployment Strategy](#8-database-migration-deployment-strategy)
9. [Blue-Green Deployment](#9-blue-green-deployment)
10. [Canary Release Strategy](#10-canary-release-strategy)
11. [Zero-Downtime Deployment Process](#11-zero-downtime-deployment-process)
12. [Kubernetes Readiness Assessment](#12-kubernetes-readiness-assessment)
13. [Service Discovery Approach](#13-service-discovery-approach)
14. [Health Check and Readiness Probe Design](#14-health-check-and-readiness-probe-design)
15. [Resource Limits and Requests](#15-resource-limits-and-requests)
16. [Network Policies and Security Groups](#16-network-policies-and-security-groups)
17. [SSL/TLS Certificate Management](#17-ssltls-certificate-management)
18. [CDN Strategy for Static Assets](#18-cdn-strategy-for-static-assets)
19. [Image Optimization Pipeline](#19-image-optimization-pipeline)

---

## 1. Purpose and Scope

This document defines the deployment architecture for the TRUE STAR BD LIMITED digital marketplace platform. It covers the complete software delivery lifecycle from containerization through production deployment, including release strategies, infrastructure patterns, and operational runbooks.

**Scope covers:**

| **Domain** | **Coverage** |
|---|---|
| Container strategy | Docker image building, optimization, registry management |
| Orchestration | Docker Compose (dev/staging), Kubernetes (production target) |
| Networking | Reverse proxy, load balancing, service mesh, CDN |
| Release management | Blue-Green, canary, zero-downtime, rollback |
| Infrastructure | Cloud provisioning, scaling, resource management |
| Operations | Health checks, monitoring, certificate management |

---

## 2. Deployment Overview

### 2.1 High-Level Architecture

```
                         ┌──────────────────────┐
                         │   CDN (Cloudflare)    │
                         │  (static assets, SSL) │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Load Balancer       │
                         │  (Cloudflare / AWS NLB) │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   NGINX Ingress       │
                         │  (reverse proxy, WAF) │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
    ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
    │  Web Frontend     │ │  API Gateway       │ │  Admin Panel      │
    │  (Next.js/React)  │ │  (Kong / Envoy)    │ │  (React)          │
    └───────────────────┘ └─────────┬─────────┘ └───────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
    ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
    │  Auth Service     │ │  Order Service    │ │  Payment Service  │
    │  (Node.js/Go)     │ │  (Node.js)        │ │  (Go)             │
    └───────────────────┘ └───────────────────┘ └───────────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Service Mesh       │
                         │  (Istio / Linkerd)   │
                         └──────────────────────┘
```

### 2.2 Environment Matrix

| **Environment** | **Purpose** | **Infrastructure** | **Data** |
|---|---|---|---|
| `local` | Developer workstation | Docker Compose | Synthetic data |
| `dev` | Integration testing | Single-node Docker / K3s | Anonymized subset |
| `staging` | Pre-production validation | Multi-node K8s (small) | Anonymized production copy |
| `production` | Live user traffic | Multi-node K8s (HA) | Production data |

---

## 3. Docker Containerization Strategy

### 3.1 Multi-Stage Build Pattern

```dockerfile
# ===========================================
# STAGE 1: Build
# ===========================================
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# ===========================================
# STAGE 2: Production
# ===========================================
FROM node:20-alpine AS production

RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=appuser:appgroup package*.json ./

EXPOSE 3000
USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]
```

### 3.2 Image Tagging Strategy

| **Tag Pattern** | **Example** | **Use Case** |
|---|---|---|
| `{branch}-{sha}-{timestamp}` | `main-a1b2c3d-20260701T1200Z` | Immutable build artifact |
| `{semver}` | `v2.1.0` | Tagged release |
| `latest` | `latest` | Development convenience (mutated) |
| `{branch}` | `main`, `feature/payment-v2` | Environment tracking |

### 3.3 Image Optimization

| **Optimization** | **Before** | **After** | **Method** |
|---|---|---|---|
| Base image | `node:20` (350 MB) | `node:20-alpine` (120 MB) | Alpine-based images |
| Build stages | Single stage | Multi-stage | Build artifacts only |
| Layer caching | No caching | Optimized layer ordering | `COPY` order: dependencies first, source last |
| Image scanning | — | Integrated | Trivy scan in CI |
| Distroless images | — | Optional for Go services | `gcr.io/distroless/static` |

### 3.4 Registry and Signing

| **Component** | **Detail** |
|---|---|
| Registry | AWS ECR / Docker Hub private registry |
| Image signing | cosign (Sigstore) — all images signed before deployment |
| Attestation | SLSA Level 3 provenance attestation in OCI manifest |
| Vulnerability gate | Images with high/critical CVEs blocked from deployment |

---

## 4. Docker Compose Configuration

### 4.1 Local Development Environment

```yaml
version: "3.9"

x-common: &common
  restart: unless-stopped
  networks:
    - tsbl-network
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"

services:
  postgres:
    image: postgres:16-alpine
    <<: *common
    environment:
      POSTGRES_USER: tsbl
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpassword}
      POSTGRES_DB: tsbl_marketplace
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./docker/postgres/init:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    <<: *common
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-devpassword}

  minio:
    image: minio/minio:latest
    <<: *common
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY:-minioadmin}
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"

  api-gateway:
    image: tsbl/api-gateway:${IMAGE_TAG:-latest}
    <<: *common
    ports:
      - "8080:8080"
    depends_on:
      - auth-service
      - order-service
    environment:
      NODE_ENV: development

  auth-service:
    image: tsbl/auth-service:${IMAGE_TAG:-latest}
    <<: *common
    ports:
      - "3001:3000"
    depends_on:
      - postgres
      - redis

  order-service:
    image: tsbl/order-service:${IMAGE_TAG:-latest}
    <<: *common
    ports:
      - "3002:3000"
    depends_on:
      - postgres
      - redis

  web-frontend:
    image: tsbl/web-frontend:${IMAGE_TAG:-latest}
    <<: *common
    ports:
      - "3000:3000"
    depends_on:
      - api-gateway

  admin-panel:
    image: tsbl/admin-panel:${IMAGE_TAG:-latest}
    <<: *common
    ports:
      - "3003:3000"
    depends_on:
      - api-gateway

volumes:
  postgres-data:
  redis-data:
  minio-data:

networks:
  tsbl-network:
    driver: bridge
```

### 4.2 Environment Overrides

| **File** | **Purpose** |
|---|---|
| `docker-compose.yml` | Base configuration (shared) |
| `docker-compose.override.yml` | Local development overrides (auto-loaded) |
| `docker-compose.dev.yml` | Dev environment overrides |
| `docker-compose.staging.yml` | Staging environment overrides |
| `.env` | Environment variable injection (not committed) |

### 4.3 Compose Profiles for Service Selection

```bash
# Start only infrastructure
docker compose --profile infra up

# Start specific service + dependencies
docker compose --profile services up

# Start everything
docker compose --profile all up
```

---

## 5. NGINX Configuration

### 5.1 Reverse Proxy Configuration

```nginx
upstream api_backend {
    least_conn;
    server api-gateway:8080 max_fails=3 fail_timeout=30s;
    keepalive 64;
}

upstream frontend {
    least_conn;
    server web-frontend:3000 max_fails=3 fail_timeout=30s;
    keepalive 64;
}

server {
    listen 443 ssl http2;
    server_name tsbl.com *.tsbl.com;

    # SSL (see Section 17 for certificate management)
    ssl_certificate     /etc/letsencrypt/live/tsbl.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tsbl.com/privkey.pem;
    ssl_protocols       TLSv1.3;
    ssl_ciphers         TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 1h;
    ssl_session_tickets off;

    # Security headers (see docs/05-security/01-security-architecture.md)
    include /etc/nginx/conf.d/security-headers.conf;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 256;
    gzip_proxied any;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;

        # Cache static assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;

        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
        limit_req_status 429;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://api_backend/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;  # 24 hours for long-lived WS
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Deny access to sensitive paths
    location ~ (\.env|\.git|composer\.json|package\.json) {
        deny all;
    }
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name tsbl.com *.tsbl.com;
    return 301 https://$host$request_uri;
}
```

### 5.2 Rate Limiting Zones

```nginx
# Rate limiting configuration (/etc/nginx/conf.d/rate-limiting.conf)

# Per IP — general API
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

# Per IP — auth endpoints (strict)
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

# Burst configuration
limit_req_zone $binary_remote_addr zone=burst_limit:10m rate=200r/s;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
limit_conn conn_limit 50;
```

### 5.3 NGINX Hardening

```conf
# /etc/nginx/conf.d/hardening.conf

# Buffer overflow protection
client_body_buffer_size 128k;
client_header_buffer_size 1k;
client_max_body_size 10m;
large_client_header_buffers 4 8k;

# Timeout settings
client_body_timeout 12s;
client_header_timeout 12s;
send_timeout 10s;

# HTTP methods
if ($request_method !~ ^(GET|HEAD|POST|PUT|DELETE|PATCH|OPTIONS)$) {
    return 405;
}

# Disable server tokens
server_tokens off;

# Proxy buffers
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;
```

---

## 6. Service Mesh Architecture

### 6.1 Service Mesh Technology

| **Tier** | **Technology** | **Status** |
|---|---|---|
| Control plane | Istio / Linkerd | Evaluated; Istio selected for production |
| Data plane | Envoy sidecar (Istio) | Per-pod sidecar injection |
| Ingress gateway | Istio Ingress Gateway | Replaces NGINX in mesh-enabled clusters |
| Egress gateway | Istio Egress Gateway | Controlled external traffic |
| mTLS enforcement | Istio PeerAuthentication | `STRICT` mode in production |

### 6.2 Service Mesh Benefits

| **Capability** | **Impact** |
|---|---|
| Traffic splitting | Weighted canary releases across service versions |
| Circuit breaking | Automatic failure isolation; stops cascading failures |
| Retry and timeout | Configurable per-service policies |
| Observability | mTLS-secured metrics, traces, and access logs |
| Fault injection | Chaos engineering: inject delays and errors for testing |
| Authorization | Service-level RBAC via Istio AuthorizationPolicy |
| Rate limiting | Per-service global rate limits |

### 6.3 Istio VirtualService Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
  namespace: production
spec:
  hosts:
    - order-service
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: order-service
            subset: v2
          weight: 100
    - route:
        - destination:
            host: order-service
            subset: v1
          weight: 90
        - destination:
            host: order-service
            subset: v2
          weight: 10
      retries:
        attempts: 3
        perTryTimeout: 2s
      timeout: 10s
```

---

## 7. Environment-Specific Configurations

### 7.1 Configuration Strategy

| **Configuration** | **Source** | **Method** |
|---|---|---|
| Application config | Environment variables | Kubernetes ConfigMap + Secret |
| Database URLs | Vault dynamic secrets | Vault sidecar / CSI provider |
| API keys | Vault static secrets | Vault sidecar injection |
| Feature flags | LaunchDarkly / custom | Remote evaluation service |
| Service topology | Kubernetes DNS | Native service discovery |

### 7.2 Environment Configuration Matrix

| **Setting** | **Dev** | **Staging** | **Production** |
|---|---|---|---|
| **Replicas** | 1 | 2–3 | 5–20 (auto-scaled) |
| **CPU request/limit** | 0.25 / 0.5 | 0.5 / 1.0 | 1.0 / 2.0 |
| **Memory request/limit** | 256Mi / 512Mi | 512Mi / 1Gi | 1Gi / 2Gi |
| **Log level** | `debug` | `info` | `warn` |
| **Rate limiting** | Disabled | Soft (100 req/s) | Hard (10–100 req/s per tier) |
| **TLS enforcement** | Optional | Required | Required + HSTS |
| **Database backup** | None | Daily | Continuous + daily snapshots |
| **Monitoring** | Console logs | Prometheus + Grafana | Full ELK + PagerDuty |
| **MFA enforcement** | Disabled | Optional | Required (admin, payment) |

### 7.3 Kubernetes ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
  namespace: production
data:
  NODE_ENV: "production"
  LOG_LEVEL: "warn"
  DB_HOST: "postgres-rw.prod.svc.cluster.local"
  DB_PORT: "5432"
  DB_NAME: "tsbl_marketplace"
  REDIS_HOST: "redis.prod.svc.cluster.local"
  REDIS_PORT: "6379"
  RATE_LIMIT_REQUESTS: "1000"
  RATE_LIMIT_WINDOW_MS: "60000"
  ENABLE_CIRCUIT_BREAKER: "true"
  CACHE_TTL_SECONDS: "300"
```

---

## 8. Database Migration Deployment Strategy

### 8.1 Migration Principles

| **Principle** | **Detail** |
|---|---|
| **Forward-only migrations** | Never modify a committed migration; create a new one |
| **Idempotent rollbacks** | Every migration has a reversible down script |
| **No locking** | Migrations designed to avoid long table locks |
| **Zero-downtime** | Schema changes are backward-compatible with old code |
| **Automated** | Migration runs as part of CI/CD pipeline, not manual |

### 8.2 Migration Process

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│  Developer │    │    CI/CD   │    │  Staging   │    │ Production │
│  Creates   │───>│  Pipeline  │───>│  Deploy    │───>│  Deploy    │
│  Migration │    │  Validates │    │  Migrate   │    │  Migrate   │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
```

### 8.3 Migration Types

| **Type** | **Example** | **Downtime Risk** | **Strategy** |
|---|---|---|---|
| Add column (nullable) | `ALTER TABLE orders ADD COLUMN coupon_id UUID NULL` | None | Safe; deploy first, then migrate |
| Add column (NOT NULL) | Need default value | Medium | Add nullable first, backfill, then set NOT NULL |
| Rename column | `price_cents → unit_price_cents` | High | Create new column, dual-write, backfill, drop old |
| Add index | `CREATE INDEX CONCURRENTLY` | None | `CONCURRENTLY` avoids table lock |
| Remove column | `ALTER TABLE orders DROP COLUMN legacy_field` | Medium | Stop reading, stop writing, then drop |
| Split table | Extract `order_items` from `orders` | High | Expand, migrate, contract pattern |

### 8.4 Expand-Migrate-Contract Pattern

```
Phase 1: EXPAND
  - Create new table/column
  - Application writes to both old and new
  - Old remains source of truth for reads

Phase 2: MIGRATE
  - Backfill historical data into new structure
  - Verify data consistency between old and new
  - Switch reads to new structure
  - Old is no longer used for reads

Phase 3: CONTRACT
  - Stop writing to old structure
  - Drop old table/column
  - Clean up application code references
```

### 8.5 Migration Rollback Procedure

```bash
# If migration fails or causes issues:
kubectl exec deploy/order-service -- npm run db:rollback:last
# Then revert application code via previous deployment
kubectl rollout undo deploy/order-service
```

---

## 9. Blue-Green Deployment

### 9.1 Concept

```
                              ┌──────────────────┐
                              │   Load Balancer   │
                              │  (routes traffic) │
                              └────────┬─────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
     ┌──────────▼──────────┐  ┌───────▼──────────┐  ┌───────▼──────────┐
     │  BLUE (Live)        │  │  GREEN (Staging)  │  │  BLUE (Live)     │
     │  v1.0.0 — active    │  │  v2.0.0 — idle    │  │  v1.0.0 — idle   │
     │  100% traffic       │  │  0% traffic       │  │  0% traffic      │
     └─────────────────────┘  └───────────────────┘  └──────────────────┘
            Time: T0                    T1                      T2
                                  Deploy v2.0.0           Switch traffic to GREEN
                                  Run smoke tests         BLUE becomes idle (rollback target)
```

### 9.2 Blue-Green Implementation

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tsbl-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
spec:
  rules:
    - host: tsbl.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-frontend-blue    # Active
                port:
                  number: 3000
```

### 9.3 Blue-Green Deployment Steps

| **Step** | **Action** | **Verification** |
|---|---|---|
| 1 | Deploy GREEN environment (full stack) | All pods healthy; readiness checks pass |
| 2 | Run automated smoke tests against GREEN | API endpoint validation, E2E tests |
| 3 | Run manual QA verification (staging mirror) | Regression test suite |
| 4 | Switch load balancer from BLUE to GREEN | DNS propagation / traffic shift |
| 5 | Monitor production traffic on GREEN | Error rates < baseline, latency OK |
| 6 | Hold BLUE as rollback target | 30-minute observation window |
| 7 | Tear down BLUE | Database migration cleanup (if applicable) |

### 9.4 Database Considerations for Blue-Green

| **Scenario** | **Strategy** |
|---|---|
| Backward-compatible schema changes | No issues; both environments share database |
| Breaking schema changes | Schema migration runs before BLUE → GREEN switch |
| Data migration | Run migration in BLUE phase; verify; deploy GREEN |
| Rollback | Migrations must be reversible within rollback window |

---

## 10. Canary Release Strategy

### 10.1 Canary Stages

| **Stage** | **Traffic %** | **Duration** | **Gate** |
|---|---|---|---|
| Baseline | 0% — deploy, validate | 5 minutes | Health checks pass, no errors |
| 1% | 1% user traffic | 10 minutes | Error rate < 0.1%, latency within baseline |
| 5% | 5% user traffic | 15 minutes | Error rate < 0.1%, no P1 alerts |
| 10% | 10% user traffic | 30 minutes | Business metrics stable (conversion rate, revenue) |
| 25% | 25% user traffic | 1 hour | All metrics stable |
| 50% | 50% user traffic | 1 hour | Same as 25% |
| 100% | Full rollout | — | Full release |

### 10.2 Canary Release with Istio

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service-canary
spec:
  hosts:
    - order-service
  http:
    - match:
        - headers:                # 5% canary
            x-canary:
              exact: "true"
      route:
        - destination:
            host: order-service
            subset: canary
          weight: 100
    - route:
        - destination:
            host: order-service
            subset: stable
          weight: 95
        - destination:
            host: order-service
            subset: canary
          weight: 5
```

### 10.3 Canary Automation with Flagger

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: order-service
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  service:
    port: 3000
  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        threshold: 99
        interval: 1m
      - name: request-duration
        threshold: 500
        interval: 1m
    webhooks:
      - name: load-test
        url: http://load-testrunner/
        timeout: 5s
```

### 10.4 Canary Rollback Criteria

| **Metric** | **Threshold** | **Action** |
|---|---|---|
| HTTP 5xx error rate | > 0.1% of requests | Immediate rollback |
| p95 latency increase | > 20% from baseline | Rollback |
| Revenue conversion | > 5% drop from baseline | Rollback |
| Order failure rate | > 1% of transactions | Rollback |
| Active alerts | Any P1/P2 alert | Rollback |

---

## 11. Zero-Downtime Deployment Process

### 11.1 Requirements for Zero Downtime

| **Requirement** | **Implementation** |
|---|---|
| Rolling update strategy | Kubernetes `RollingUpdate` with `maxSurge: 25%` and `maxUnavailable: 0` |
| Graceful shutdown | Application handles `SIGTERM` — drains connections before exit |
| Readiness probes | Pod not receiving traffic until fully initialized |
| Persistent connections | Connection draining via preStop hook |
| Database backward compatibility | Schema changes non-breaking (see Section 8) |
| Session persistence | External session store (Redis); not tied to pod |

### 11.2 Graceful Shutdown Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # Allow 1 extra pod during update
      maxUnavailable: 0    # Ensure all pods remain available
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: order-service
          lifecycle:
            preStop:
              exec:
                command:
                  - /bin/sh
                  - -c
                  - |
                    sleep 10 &&     # Allow load balancer to de-register pod
                    curl -X POST http://localhost:3000/shutdown &&  # Drain connections
                    sleep 5
```

### 11.3 Zero-Downtime Deployment Sequence

```
  Time ───────────────────────────────────────────────────────────────>
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
  Pod-1 ■■■■■■■■■■■■■■■■■■■■■■■■■□□□□□□□□□□□□□□□□□□□□□□□□□□
        │ Running   │ Running   │ Terminating               │ Terminated
        │           │           │ (drain conns)             │
        │           │           │                           │
  Pod-2 □□□□□□□□□□□□■■■■■■■■■■■■■■■■■■□□□□□□□□□□□□□□□□□□□□□□
        │ Pending   │ Running   │ Running    │ Terminating   │ Terminated
        │           │           │            │               │
  Pod-3 □□□□□□□□□□□□□□□□□□□□□■■■■■■■■■■■■■■■■■■■■■■□□□□□□□□
        │ Pending   │ Pending   │ Running    │ Running        │ Terminating
        │           │           │            │                │
  Pod-4 □□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□■■■■■■■■■■■■■■■■■■■■
        │ (new)     │ (new)     │ (new)      │ (new) Running  │ Running
```

### 11.4 Rollback Procedure

```bash
# Immediate rollback to previous revision
kubectl rollout undo deployment/order-service

# Rollback to specific revision
kubectl rollout undo deployment/order-service --to-revision=3

# Verify rollback status
kubectl rollout status deployment/order-service

# If database migration was involved, run down migration
kubectl exec deploy/order-service -- npm run db:rollback:last
```

---

## 12. Kubernetes Readiness Assessment

### 12.1 Readiness Scorecard

| **Capability** | **Status** | **Priority** | **Notes** |
|---|---|---|---|
| Containerized applications | ✅ Complete | P0 | All services containerized |
| Docker Compose orchestration | ✅ Complete | P0 | Local and dev environments |
| NGINX as reverse proxy | ✅ Complete | P0 | With rate limiting and security |
| Blue-Green deployment | ✅ Complete | P0 | Automated via CI/CD |
| Canary releases | ✅ Complete | P0 | Via Flagger + Istio |
| Zero-downtime deployments | ✅ Complete | P0 | Rolling updates, graceful shutdown |
| **Container orchestration** | **🔄 In progress** | **P0** | **K8s cluster provisioning** |
| **Service mesh** | **🔄 In progress** | **P1** | **Istio evaluation** |
| **Persistent storage** | **🔄 In progress** | **P1** | **StatefulSet for databases** |
| **Horizontal auto-scaling** | **🔄 In progress** | **P1** | **HPA based on CPU/memory/custom metrics** |
| **Cluster autoscaling** | **📋 Planned** | **P2** | **Karpenter / Cluster Autoscaler** |
| **Service mesh mTLS** | **📋 Planned** | **P2** | **Istio PeerAuthentication** |
| **Observability stack** | **📋 Planned** | **P2** | **Prometheus + Grafana + Jaeger** |

### 12.2 Migration Path to Kubernetes

| **Phase** | **Timeline** | **Deliverables** |
|---|---|---|
| Phase 1: Foundation | Week 1–2 | K8s cluster (EKS/AKS/GKE), node pools, networking, CI/CD integration |
| Phase 2: Workload migration | Week 3–4 | Migrate stateless services (API gateway, frontend, auth service) |
| Phase 3: Stateful services | Week 5–6 | Database operators (Postgres Operator, Redis Operator), backups |
| Phase 4: Advanced features | Week 7–8 | Istio service mesh, HPA, Vault integration, Flagger |
| Phase 5: Optimization | Week 9–10 | Cost optimization, PDB, pod topology spread constraints |

---

## 13. Service Discovery Approach

### 13.1 Service Discovery Architecture

| **Environment** | **Method** | **Implementation** |
|---|---|---|
| Local (Docker Compose) | Docker DNS | Service name resolves to container IP |
| Dev / Staging (K8s) | Kubernetes DNS | `<service>.<namespace>.svc.cluster.local` |
| Production (K8s) | Kubernetes DNS + Istio | Same + Istio service registry |
| Third-party services | ExternalName service | Kubernetes `ExternalName` service |

### 13.2 DNS Resolution

```
Service: order-service.prod.svc.cluster.local
                              │         │       │
                              │         │       └─── Kubernetes cluster domain
                              │         └─────────── namespace
                              └───────────────────── service name
```

### 13.3 Service Discovery Metadata

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: production
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "3000"
    service.istio.io/canonical-name: order-service
    service.istio.io/canonical-revision: v2
spec:
  selector:
    app: order-service
  ports:
    - name: http
      port: 3000
      targetPort: 3000
    - name: grpc
      port: 9000
      targetPort: 9000
```

---

## 14. Health Check and Readiness Probe Design

### 14.1 Probe Architecture

| **Probe Type** | **Purpose** | **Failure Consequence** |
|---|---|---|
| **Liveness** | Is the application running? (deadlock detection) | Pod restart |
| **Readiness** | Is the application ready to serve traffic? | Removed from Service endpoints |
| **Startup** | Is the application fully initialized? | Delays liveness checks |

### 14.2 Probe Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          startupProbe:               # Initialization check
            httpGet:
              path: /health/startup
              port: 3000
            initialDelaySeconds: 0
            periodSeconds: 5
            failureThreshold: 30      # Up to 150 seconds to start
          livenessProbe:              # Application is alive
            httpGet:
              path: /health/live
              port: 3000
            periodSeconds: 15
            timeoutSeconds: 3
            failureThreshold: 3       # Restart after 45 seconds of failure
          readinessProbe:             # Ready to serve traffic
            httpGet:
              path: /health/ready
              port: 3000
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 2       # Remove from service after 20 seconds
```

### 14.3 Health Check Endpoint Implementation

```javascript
// health.controller.js — simplified example

async function healthCheck(req, res) {
  const health = {
    status: "ok",
    version: process.env.APP_VERSION,
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    dependencies: {
      postgres: await checkDatabase(),
      redis: await checkRedis(),
      vault: await checkVault(),
    },
  };

  const allHealthy = Object.values(health.dependencies).every(
    (dep) => dep.status === "up"
  );

  res.status(allHealthy ? 200 : 503).json(health);
}
```

### 14.4 Health Check Response

```json
{
  "status": "ok",
  "version": "2.1.0",
  "uptime": 3421.5,
  "timestamp": "2026-07-01T10:30:00.000Z",
  "dependencies": {
    "postgres": {
      "status": "up",
      "latency_ms": 2.3
    },
    "redis": {
      "status": "up",
      "latency_ms": 0.8
    },
    "vault": {
      "status": "degraded",
      "latency_ms": 150.0,
      "message": "One of three Vault replicas unreachable"
    }
  }
}
```

---

## 15. Resource Limits and Requests

### 15.1 Resource Allocation Strategy

| **Service** | **CPU Request** | **CPU Limit** | **Memory Request** | **Memory Limit** | **Replicas (prod)** |
|---|---|---|---|---|---|
| Web Frontend | 250m | 500m | 256Mi | 512Mi | 5–15 |
| Admin Panel | 250m | 500m | 256Mi | 512Mi | 2–3 |
| API Gateway | 500m | 1.0 | 512Mi | 1Gi | 5–20 |
| Auth Service | 500m | 1.0 | 512Mi | 1Gi | 3–10 |
| Order Service | 500m | 1.0 | 1Gi | 2Gi | 3–10 |
| Payment Service | 500m | 1.0 | 512Mi | 1Gi | 3–8 |
| Product Service | 500m | 1.0 | 1Gi | 2Gi | 3–10 |
| Notification Service | 250m | 500m | 256Mi | 512Mi | 2–5 |
| Background Workers | 500m | 1.0 | 1Gi | 2Gi | 2–5 |
| Redis | 1.0 | 2.0 | 2Gi | 4Gi | 3 (cluster) |
| PostgreSQL | 2.0 | 4.0 | 4Gi | 8Gi | 2 (primary + replica) |

### 15.2 Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: requests_per_second
        target:
          type: AverageValue
          averageValue: 500
```

### 15.3 Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
spec:
  minAvailable: 2         # At least 2 pods must remain available
  selector:
    matchLabels:
      app: order-service
```

---

## 16. Network Policies and Security Groups

### 16.1 Kubernetes Network Policies

| **Rule** | **Description** | **Implementation** |
|---|---|---|
| Deny all ingress | Default deny — zero-trust baseline | `NetworkPolicy` default-deny |
| Allow frontend → API | Web frontend can reach API gateway | Selector + port-based allow |
| Allow API → services | API gateway can reach all services | Namespace + label selectors |
| Allow monitoring → pods | Prometheus can scrape metrics | Namespace selector `monitoring` |
| Allow CI/CD → API | Deployment pipeline can check health | IP block `172.16.0.0/12` |
| Deny all egress (default) | Pods cannot reach internet by default | Egress policy per service |

### 16.2 Network Policy Examples

```yaml
# Default deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
---
# Allow API gateway → order service
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-order
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: order-service
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - port: 3000
          protocol: TCP
---
# Allow order service → database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-order-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: order-service
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - port: 5432
          protocol: TCP
```

### 16.3 Cloud Security Groups

| **Security Group** | **Purpose** | **Inbound Rules** | **Outbound Rules** |
|---|---|---|---|
| `sg-frontend-lb` | Load balancer → frontend | HTTP(S) from `0.0.0.0/0` | All traffic to frontend K8s nodes |
| `sg-k8s-nodes` | K8s worker nodes | K8s API (6443) from admin IPs; node ports from LBs | All (restricted by egress firewall) |
| `sg-database` | PostgreSQL / Redis | Port 5432, 6379 from K8s node SG only | None (no internet access) |
| `sg-vault` | Vault cluster | Port 8200 from K8s node SG; port 8201 (raft) from self SG | Vault-specific outbound routes |

---

## 17. SSL/TLS Certificate Management

### 17.1 Certificate Strategy

| **Component** | **Certificate Type** | **Issuer** | **Rotation** |
|---|---|---|---|
| Public endpoints (tsbl.com) | Wildcard `*.tsbl.com` | Let's Encrypt | 90 days (auto-renewed) |
| Internal mTLS (service mesh) | Per-service certificates | Istio CA (Istiod) | 24 hours (auto-rotated) |
| Database connections | Client certificates | Vault PKI | 30 days (auto-rotated) |
| Admin subdomain | Wildcard `*.admin.tsbl.com` | Let's Encrypt | 90 days (auto-renewed) |

### 17.2 Let's Encrypt with cert-manager

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: devops@tsbl.com
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
      - dns01:
          cloudflare:
            email: devops@tsbl.com
            apiTokenSecretRef:
              name: cloudflare-api-token
              key: api-token
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: tsbl-wildcard
  namespace: production
spec:
  secretName: tsbl-wildcard-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - "*.tsbl.com"
    - "tsbl.com"
```

### 17.3 Certificate Renewal Monitoring

| **Metric** | **Threshold** | **Alert** |
|---|---|---|
| Days until expiry | < 30 days | Warning |
| Days until expiry | < 14 days | Critical |
| cert-manager renew error | Any failure | Immediate PagerDuty |
| TLS handshake failure | > 0.1% of requests | Immediate PagerDuty |

---

## 18. CDN Strategy for Static Assets

### 18.1 CDN Architecture

```
┌────────────┐    CDN Edge    ┌────────────┐
│  Browser   │◄──────────────►│  Cloudflare │
│  (User)    │                │  CDN        │
└────────────┘                └──────┬─────┘
                                     │ (cache miss)
                            ┌────────▼────────┐
                            │  Origin Server   │
                            │  (NGINX/K8s)     │
                            └─────────────────┘
```

### 18.2 Cache Configuration

| **Asset Type** | **Example** | **Cache TTL** | **Cache-Control** |
|---|---|---|---|
| JavaScript bundles | `app.a1b2c3d.js` | 1 year | `public, immutable, max-age=31536000` |
| CSS bundles | `styles.e5f6g7h.css` | 1 year | `public, immutable, max-age=31536000` |
| Images (user uploads) | `photo_2026-07-01.jpg` | 30 days | `public, max-age=2592000` |
| Product images | `product_1234.webp` | 90 days | `public, max-age=7776000` |
| Fonts | `Inter-Regular.woff2` | 1 year | `public, immutable, max-age=31536000` |
| API responses | `/api/products` | 5 minutes (edge) | `public, s-maxage=300, max-age=0` |
| HTML pages | `/` | No cache | `no-cache, must-revalidate` |

### 18.3 CDN Providers

| **Provider** | **Role** | **Status** |
|---|---|---|
| Cloudflare | Primary CDN, DDoS protection, WAF, SSL termination | Active |
| AWS CloudFront | Secondary CDN (failover), S3 origin for uploads | Active |
| Image CDN | Cloudflare Images / imgix | Evaluated |

### 18.4 Cache Invalidation

| **Event** | **Invalidation Strategy** |
|---|---|
| New deployment | Automatic: content-hashed filenames (no invalidation needed) |
| Product image update | Purge specific URL via Cloudflare API |
| Price change (API) | Short TTL (5 min); instant purge for promotions |
| Manual override | Cloudflare dashboard → Purge Individual Files |

---

## 19. Image Optimization Pipeline

### 19.1 Pipeline Workflow

```
User Upload ──> Image API ──> Process Queue ──> Optimizer ──> CDN
  (original)   (validate)     (resize +      (compress,    (serve
                               format conv)   WebP/AVIF)    optimized)
```

### 19.2 Image Variants

| **Variant** | **Max Width** | **Format** | **Quality** | **Use Case** |
|---|---|---|---|---|
| `thumbnail` | 150px | WebP (AVIF fallback) | 80% | Search results, grid view |
| `small` | 400px | WebP (AVIF fallback) | 85% | Product listing cards |
| `medium` | 800px | WebP (AVIF fallback) | 90% | Product detail page |
| `large` | 1600px | WebP (AVIF fallback) | 95% | Image zoom / lightbox |
| `original` | Full resolution | Source format | 100% | Archive (not served to browser) |

### 19.3 Optimization Tools

| **Tool** | **Function** | **Deployment** |
|---|---|---|
| Sharp (Node.js) | Resize, format conversion, compression | In-process API service |
| libvips | Underlying image processing library | Sharp dependency |
| MozJPEG | JPEG compression (for legacy fallback) | Sharp plugin |
| oxipng | PNG compression (for legacy fallback) | Runtime optimization |
| cwebp | WebP encoding | Sharp built-in |
| AVIF encoder | AVIF encoding | Sharp (libaom) |

### 19.4 Optimization Configuration

```javascript
// image-optimizer.config.js — simplified example

module.exports = {
  allowedFormats: ["jpeg", "png", "webp", "avif", "gif"],
  maxFileSize: 10 * 1024 * 1024, // 10 MB
  variants: {
    thumbnail: { width: 150, fit: "cover", format: "webp", quality: 80 },
    small: { width: 400, fit: "inside", format: "webp", quality: 85 },
    medium: { width: 800, fit: "inside", format: "webp", quality: 90 },
    large: { width: 1600, fit: "inside", format: "webp", quality: 95 },
  },
  storage: {
    provider: "s3",
    bucket: "tsbl-images",
    path: "products/{productId}/{variant}.{format}",
    cdnUrl: "https://cdn.tsbl.com/images",
  },
  webp: {
    effort: 6, // CPU effort for encoding (0-6)
  },
  avif: {
    effort: 4, // CPU effort for encoding (0-9)
  },
};
```

### 19.5 Responsive Images (srcset Generation)

```html
<img
  src="https://cdn.tsbl.com/images/products/1234/medium.webp"
  srcset="
    https://cdn.tsbl.com/images/products/1234/thumbnail.webp 150w,
    https://cdn.tsbl.com/images/products/1234/small.webp      400w,
    https://cdn.tsbl.com/images/products/1234/medium.webp     800w,
    https://cdn.tsbl.com/images/products/1234/large.webp     1600w
  "
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1600px"
  loading="lazy"
  alt="Product Name"
/>
```

### 19.6 Lazy Loading Strategy

| **Technique** | **Implementation** |
|---|---|
| Native lazy loading | `<img loading="lazy">` attribute |
| Intersection Observer | JavaScript fallback for older browsers |
| Blur-up placeholders | Tiny base64-encoded thumbnail as background |
| Progressive JPEG | Enabled for JPEG fallback images |
| Preload critical images | `<link rel="preload">` for above-the-fold images |

---

## 20. CI/CD Pipeline Integration

### 20.1 Deployment Pipeline Stages

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   Build  │ │   Test   │ │   Scan   │ │   Tag    │ │  Deploy  │
│  (code)  │─>(unit +   │─>(SAST,    │─>(semver,  │─>(Blue/   │
│          │ │  integ.) │ │  SCA)    │ │  sign)    │ │  Green)  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 20.2 Deployment Automation

```yaml
# .github/workflows/deploy.yml — simplified example
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build & push image
        run: |
          docker build -t tsbl/order-service:${{ github.sha }} .
          docker push tsbl/order-service:${{ github.sha }}

      - name: Sign image
        run: cosign sign tsbl/order-service:${{ github.sha }}

      - name: Deploy to staging
        run: |
          kubectl set image deployment/order-service \
            order-service=tsbl/order-service:${{ github.sha }} \
            --namespace staging

      - name: Run smoke tests
        run: npm run test:smoke -- --base-url https://staging.tsbl.com

      - name: Deploy to production (Blue-Green)
        run: |
          # Switch production image tag
          kubectl set image deployment/order-service-green \
            order-service=tsbl/order-service:${{ github.sha }} \
            --namespace production

          # Wait for Green readiness
          kubectl rollout status deployment/order-service-green \
            --namespace production --timeout=5m

          # Switch traffic
          kubectl patch service order-service \
            --patch '{"spec":{"selector":{"version":"green"}}}' \
            --namespace production
```

---

## 21. Monitoring and Observability

### 21.1 Deployment Metrics

| **Metric** | **Source** | **Alert Threshold** |
|---|---|---|
| Deployment duration | CI/CD pipeline | > 15 minutes → warning |
| Rollback frequency | CI/CD pipeline | > 5 per week → review |
| Success rate | CI/CD pipeline | < 95% → critical |
| Time to detect failure | APM / monitoring | > 5 minutes → review |
| Time to recover | Incident response | > 30 minutes → SEV-2 |

### 21.2 Deployment Dashboard (Grafana)

Key panels on the deployment observability dashboard:

1. **Current version** per service (annotated with deploy time)
2. **Error rate** before/after deployment (blue/green overlay)
3. **Latency** p50/p95/p99 before/after deployment
4. **Traffic distribution** during canary release
5. **Health check pass/fail** per pod
6. **Rollback events** with timestamps and triggers

---

## 22. Appendices

### A.1 Glossary

| **Term** | **Definition** |
|---|---|
| Blue-Green | Deployment strategy with two identical environments; traffic switches instantly |
| Canary | Gradual traffic shift to new version with rollback automation |
| HPA | Horizontal Pod Autoscaler — automatically scales replicas |
| mTLS | Mutual TLS — both client and server present certificates |
| PDB | Pod Disruption Budget — minimum available pods during voluntary disruptions |
| SBOM | Software Bill of Materials — inventory of all components and dependencies |
| SLSA | Supply-chain Levels for Software Artifacts — security framework |

### A.2 Related Documents

| **Document** | **Location** |
|---|---|
| Security Architecture | `docs/05-security/01-security-architecture.md` |
| API Reference | `docs/03-api/` |
| Infrastructure Terraform | `infra/terraform/` |
| CI/CD Pipeline Config | `.github/workflows/` |
| Kubernetes Manifests | `infra/k8s/` |

### A.3 Revision History

| **Version** | **Date** | **Author** | **Changes** |
|---|---|---|---|
| 1.0 | 2026-07-01 | Platform Engineering | Initial release |

---

*This document is maintained by the TRUE STAR BD LIMITED Platform Engineering Team. All changes require CTO approval.*
