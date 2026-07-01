# Scaling Strategy

## 1. Scaling Philosophy

TRUE STAR BD LIMITED follows a **scale-up (vertical) first, scale-out (horizontal) second** approach. Vertical scaling is preferred for the initial growth phase (0–50K users) due to operational simplicity. Horizontal scaling is adopted when resilience, fault tolerance, and infinite scalability become primary requirements.

### Decision Matrix

| Factor | Vertical Scale-Up | Horizontal Scale-Out | Decision Rule |
|--------|-------------------|---------------------|---------------|
| Application server | Upgrade to 64-core/256GB RAM | Add more instances behind LB | Horizontal after 4 vCPU |
| Database | Upgrade RDS instance class | Read replicas + sharding | Horizontal after 32GB RAM |
| Cache | Upgrade Redis node | Redis Cluster | Horizontal after 64GB RAM |
| Queue | Upgrade worker resources | Auto-scaling worker fleet | Horizontal after 10 concurrent tasks |
| File storage | Increase EBS volume | S3 + CDN | S3 from day one |

---

## 2. Database Scaling

### 2.1 Current Architecture (Tier 1: 0–50K users)

- **Single PostgreSQL instance** (db.r6g.large: 2 vCPU, 16GB RAM).
- **PgBouncer** for connection pooling (transaction mode).
- **Read replicas**: 0 (not yet required).

### 2.2 Tier 2: 50K–500K users

| Component | Configuration | Scaling Trigger |
|-----------|--------------|-----------------|
| Primary DB | db.r6g.xlarge (4 vCPU, 32GB RAM) | CPU > 70% sustained |
| Read replicas | 2 x db.r6g.large | Read replica lag > 100ms |
| PgBouncer | Standalone instance | Connection count > 200 |
| Connection pool size | 100 per app instance | Active connections > 80% |

### 2.3 Tier 3: 500K–1M users

| Component | Configuration | Scaling Trigger |
|-----------|--------------|-----------------|
| Primary DB | db.r6g.2xlarge (8 vCPU, 64GB RAM) | CPU > 60% sustained |
| Read replicas | 4 x db.r6g.xlarge | Read replica lag > 50ms |
| PgBouncer | 2 instances with HA | Pool utilization > 80% |
| Connection pool size | 200 per app instance | Active connections > 80% |

### 2.4 Sharding Readiness

- **Sharding Key**: `vendor_id` (natural high-cardinality key).
- **Middleware**: PostgreSQL FDW or CitusDB extension.
- **Schema**: All tables include `vendor_id` for partition alignment.
- **Plan**: Implement sharding when primary DB exceeds 1TB or write throughput exceeds 5000 TPS.
- **Application Layer**: Repository pattern abstracts shard routing — no raw SQL in views.

---

## 3. Application Scaling

### 3.1 Stateless Design

- **Session Storage**: All sessions in Redis — application instances hold zero state.
- **File Uploads**: Direct to S3 via pre-signed URLs — app server never stores files.
- **Caching**: All cache in Redis — no local memory cache in production.
- **Configuration**: Environment variables + AWS Parameter Store — no local config files.
- **Logging**: stdout + centralized logging — no local log files.

### 3.2 Session Externalization

| Session Data | Storage | TTL | Notes |
|-------------|---------|-----|-------|
| User session | Redis | 24h | Sliding expiry: +15min per request |
| Cart data | Redis | 7d | Persistent across sessions |
| CSRF token | Redis | Session duration | Per-device |
| OAuth state | Redis | 10min | Single-use |

### 3.3 Application Instance Strategy

- **Container Platform**: AWS ECS Fargate (serverless containers).
- **Task Definition**: 2 vCPU / 4GB RAM per instance (optimal price/performance).
- **Min/Max Instances**: 2 / 20 (production).
- **Deployment Strategy**: Blue/Green via CodeDeploy — zero downtime.

---

## 4. Cache Scaling

### 4.1 Redis Cluster Topology

| Tier | Configuration | Nodes | Memory per Node | Total Memory |
|------|--------------|-------|-----------------|--------------|
| Initial | ElastiCache Single | 1 | 13GB (r6g.large) | 13GB |
| Growth | ElastiCache Cluster | 3 | 26GB (r6g.xlarge) | 78GB |
| Scale | ElastiCache Cluster | 6 | 52GB (r6g.2xlarge) | 312GB |

### 4.2 Cluster Configuration

- **Shards**: 3 primary nodes, each with 1 replica.
- **Slot Distribution**: 16,384 hash slots evenly distributed.
- **Key Distribution**: Application-side consistent hashing via `redis-py-cluster`.
- **Auto-Failover**: Replica promoted within 15s of primary failure.
- **Scaling**: Add shards during low-traffic window; rebalancing takes < 5 minutes.

### 4.3 Cluster Monitoring Triggers

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU utilization | > 60% | > 80% | Scale up or add shard |
| Memory usage | > 70% | > 85% | Scale up or evict TTL |
| Connections | > 80% | > 95% | Add node or increase maxconn |
| Hit rate | < 85% | < 70% | Review cache strategy |

---

## 5. Queue Scaling

### 5.1 Celery Worker Architecture

- **Broker**: RabbitMQ (clustered, mirrored queues).
- **Concurrency**: Prefork with 8 workers per instance.
- **Task Type Queues**: Separate queues per priority (critical, high, medium, low).
- **Worker Auto-Scaling**: Celery `autoscale` with min/max concurrency per queue.

### 5.2 Auto-Scaling Policies

| Queue | Min Workers | Max Workers | Scale-Up Trigger | Scale-Down Trigger |
|-------|-------------|-------------|------------------|--------------------|
| `critical` | 2 | 10 | Queue depth > 5 for 30s | Queue depth 0 for 60s |
| `high` | 2 | 8 | Queue depth > 20 for 30s | Queue depth 0 for 120s |
| `medium` | 2 | 6 | Queue depth > 50 for 60s | Queue depth < 10 for 180s |
| `low` | 1 | 4 | Queue depth > 100 for 120s | Queue depth < 20 for 300s |

### 5.3 Worker Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Average task latency | < 5s | > 30s for critical queue |
| Task failure rate | < 1% | > 5% |
| Worker saturation | < 70% | > 85% |
| Queue depth (critical) | < 10 | > 50 |
| Prefetch count | 4 per worker | Misconfiguration |

---

## 6. Search Scaling

### 6.1 Elasticsearch Cluster Topology

| Phase | Nodes | Instance Type | Shards | Replicas | Storage |
|-------|-------|---------------|--------|----------|---------|
| Initial | 3 | m6g.large.search (2 vCPU, 8GB) | 5 primary | 1 | 500GB gp3 |
| Growth | 6 | m6g.xlarge.search (4 vCPU, 16GB) | 10 primary | 1 | 1TB gp3 |
| Scale | 12 | m6g.2xlarge.search (8 vCPU, 32GB) | 20 primary | 2 | 2TB gp3 |

### 6.2 Shard Strategy

- **Shard Size Target**: 10–30 GB per shard (after replication).
- **Primary Shards**: Fixed at index creation — cannot be changed.
- **Replica Shards**: Dynamic — increase for read throughput.
- **Routing**: Custom routing on `vendor_id` for co-located queries.
- **Index Lifecycle**: Hot → Warm → Cold → Delete (30/60/90/365 days).

### 6.3 Scaling Triggers

| Metric | Action |
|--------|--------|
| Index rate > 1000 docs/s | Add nodes or increase shards |
| Query latency (P95) > 200ms | Add replica shards |
| Heap usage > 75% | Scale up node memory |
| Disk usage > 80% | Add nodes with balanced allocation |

---

## 7. File Storage Scaling

### 7.1 Architecture

- **Primary Storage**: AWS S3 Standard.
- **CDN**: CloudFront for global distribution.
- **Transfer Acceleration**: S3 Transfer Acceleration for large uploads (100MB+).
- **Lifecycle Policy**:
  - 0–30 days: S3 Standard.
  - 31–90 days: S3 Infrequent Access.
  - 91–365 days: S3 Glacier Flexible Retrieval.
  - 365+ days: S3 Glacier Deep Archive.

### 7.2 Storage Scaling Dimensions

| Dimension | Strategy | Limit |
|-----------|----------|-------|
| Single-object size | Multipart upload (5MB+ parts) | 5 TB max |
| Total objects | S3 — unlimited | No limit |
| Request rate | S3 auto-scales | 3,500 PUT / 5,500 GET per prefix |
| Cross-region | S3 CRR to secondary region | Automatic |
| Throughput | CloudFront + Origin Shield | Near-unlimited |

### 7.3 CDN Scaling

- **Origin**: CloudFront with S3 origin.
- **Origin Shield**: Enabled to reduce origin request volume by 80%.
- **Price Class**: Price Class 200 (all regions except South America).
- **WAF**: Rate-based rules at edge — 10,000 req/s per IP.

---

## 8. Auto-Scaling Policies

### 8.1 Application Auto-Scaling

| Policy | Metric | Scale-Up | Scale-Down | Cooldown |
|--------|--------|----------|------------|----------|
| CPU-based | Average CPU > 70% for 5min | +2 instances | Average CPU < 30% for 10min | 300s |
| Memory-based | Average memory > 80% for 5min | +2 instances | Average memory < 50% for 10min | 300s |
| Request-based | Requests per target > 1000 for 3min | +1 instance | Requests < 500 for 10min | 300s |
| Scheduled | 8:00 AM daily | +5 instances | 10:00 PM daily | N/A |
| Scheduled | Black Friday | +20 instances fixed | Manual removal | N/A |

### 8.2 Database Auto-Scaling

- **Storage**: Auto-increase of 10% when free space < 20%.
- **Compute**: Manual (RDS doesn't support auto-scaling) — PagerDuty alert triggers manual scale-up.
- **Read Replicas**: Auto-add replica when replica lag > 100ms for 5 minutes.

### 8.3 Cache Auto-Scaling

- **Redis**: Manual scale-up/scale-out. CloudWatch alarm triggers on-call.
- **ElastiCache**: New shards added manually via runbook.

---

## 9. Load Balancing Strategy

### 9.1 Load Balancer Architecture

```
                         ┌─────────────────┐
                         │   Route 53       │
                         │ (Latency-based)  │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  CloudFront      │
                         │  (CDN + WAF)     │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴──────────────┐
             ┌──────▼──────┐             ┌───────▼─────┐
             │  ALB (Prod)  │             │  ALB (Stg)   │
             └──────┬──────┘             └──────┬───────┘
                    │                           │
          ┌─────────┼─────────┐              (staging ASG)
    ┌─────▼────┐ ┌──▼──┐ ┌───▼───┐
    │ ECS Task  │ │ ECS │ │ ECS   │
    │ (app)     │ │ ... │ │ (app)  │
    └───────────┘ └─────┘ └───────┘
```

### 9.2 ALB Configuration

- **Type**: Application Load Balancer (L7).
- **Listeners**: 443 (HTTPS) → target group, 80 → redirect to 443.
- **Target Group**: ECS Fargate tasks — health check path `/health/`.
- **Sticky Sessions**: Disabled (stateless application).
- **Cross-Zone Load Balancing**: Enabled.
- **Deregistration Delay**: 60 seconds.

### 9.3 Routing Rules

| Rule | Path Pattern | Target |
|------|-------------|--------|
| API | `/api/*` | App service |
| Admin | `/admin/*` | App service (admin) |
| Media | `/media/*` | S3 direct (via CloudFront) |
| Static | `/static/*` | S3 direct (via CloudFront) |
| WebSocket | `/ws/*` | App service (WebSocket) |

---

## 10. Future Microservices Decomposition

### 10.1 Bounded Contexts

| Service | Responsibility | Data Store | Decomposition Priority |
|---------|---------------|------------|----------------------|
| **User Service** | Auth, profiles, addresses | PostgreSQL (own DB) | 1 (Q3 2026) |
| **Product Service** | Catalog, inventory, pricing | PostgreSQL (own DB) | 1 (Q3 2026) |
| **Order Service** | Orders, fulfillment, returns | PostgreSQL (own DB) | 2 (Q4 2026) |
| **Payment Service** | Transactions, refunds, reconciliation | PostgreSQL (own DB) | 2 (Q4 2026) |
| **Notification Service** | Email, SMS, push | PostgreSQL (own DB) | 3 (Q1 2027) |
| **Search Service** | Full-text search, autocomplete | Elasticsearch | 3 (Q1 2027) |
| **Analytics Service** | Reporting, dashboards | ClickHouse | 4 (Q2 2027) |
| **Recommendation Service** | Personalization, ML | PostgreSQL + Redis | 4 (Q2 2027) |

### 10.2 Decomposition Principles

1. **Strangler Fig Pattern**: New functionality in new services; old monolith routes to new services via proxy.
2. **Shared Kernel**: Common models (User, Product) shared via internal library — gradual extraction.
3. **Anti-Corruption Layer**: Translation layer between monolith and new services.
4. **Eventual Consistency**: Domain events via RabbitMQ for cross-service data synchronization.
5. **API Gateway**: Kong or Envoy for unified entry point once services exceed 3.

### 10.3 Communication Patterns

| Pattern | Protocol | Use Case |
|---------|----------|----------|
| Synchronous | HTTP/gRPC | Query operations, command results |
| Asynchronous | RabbitMQ | Event notifications, long-running processes |
| Streaming | Kafka (future) | Real-time inventory, high-throughput events |
| CQRS | Separate read/write stores | Reporting, product search |

---

## 11. Cost Optimization in Scaling

### 11.1 Reserved Capacity

| Service | Commitment | Discount | Strategy |
|---------|-----------|----------|----------|
| RDS (DB) | 1-year | ~30% | Baseline 50% of peak capacity |
| ElastiCache | 1-year | ~30% | Baseline shards only |
| ECS Fargate | Not available | N/A | Use spot where possible |
| CloudFront | 1-year | ~30% | Commit based on baseline traffic |

### 11.2 Spot/On-Demand Mix

| Workload | Instance Type | Spot % | Mitigation |
|----------|--------------|--------|------------|
| Staging | All | 100% | Can restart |
| Production ECS | Fargate | N/A | Fargate only |
| Celery workers | EC2 spot | 80% | Fallback to on-demand |
| CI/CD runners | EC2 spot | 100% | Restart if interrupted |

### 11.3 Cost Monitoring

| Metric | Alert | Action |
|--------|-------|--------|
| Monthly spend > 80% budget | Warning | Review scaling policies |
| Monthly spend > 100% budget | Critical | Implement cost controls |
| Unused reserved instances | Warning | Modify or sell |
| EBS snapshot cost | Monthly review | Clean up stale snapshots |

### 11.4 Scaling Cost Projection

| User Tier | Monthly Infrastructure Cost | Annual Cost |
|-----------|---------------------------|-------------|
| 0–10K | ~$500 | ~$6,000 |
| 10K–50K | ~$2,000 | ~$24,000 |
| 50K–200K | ~$8,000 | ~$96,000 |
| 200K–1M | ~$30,000 | ~$360,000 |

---

*Document Owner: Principal Architect*  
*Last Updated: 2026-07-01*  
*Review Cycle: Quarterly*
