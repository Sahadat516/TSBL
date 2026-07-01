# Monitoring Strategy

## 1. Monitoring Philosophy

TRUE STAR BD LIMITED follows a **four-signal** approach to monitoring: Latency, Traffic, Errors, and Saturation (the Google SRE golden signals). Every service must expose metrics for all four signals. Dashboards and alerts are designed for **actionability** — every alert must lead to a clear investigation path.

---

## 2. Infrastructure Monitoring

### 2.1 Metrics Collected

| Resource | Metrics | Collection Interval | Retention |
|----------|---------|-------------------|-----------|
| **CPU** | utilization, iowait, steal, load average | 15s | 45 days |
| **Memory** | used, available, cached, swap, page faults | 15s | 45 days |
| **Disk** | used %, inode %, read/write latency (await), IOPS | 30s | 45 days |
| **Network** | bytes in/out, packet drops, retransmits, connection count | 30s | 45 days |
| **ECS/Fargate** | CPU reservation, memory reservation, task count | 15s | 45 days |
| **ALB** | request count, target response time, 5xx count, healthy hosts | 15s | 45 days |

### 2.2 Tooling

- **Agent**: Amazon CloudWatch Agent (or Prometheus Node Exporter for K8s).
- **Storage**: Amazon Managed Service for Prometheus (AMP) + CloudWatch Metrics.
- **Dashboards**: Grafana (self-hosted or Grafana Cloud).

### 2.3 Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU utilization (avg 5min) | > 75% | > 90% | Scale up or investigate runaway process |
| Memory utilization | > 80% | > 92% | Scale up or investigate memory leak |
| Disk utilization | > 80% | > 90% | Clean up or increase volume |
| Network retransmits | > 0.1% | > 1% | Investigate network issues |
| ECS CPU reservation | > 80% | > 95% | Scale out tasks |

---

## 3. Application Monitoring (APM)

### 3.1 OpenTelemetry Instrumentation

| Component | Instrumentation | Standard |
|-----------|----------------|----------|
| Django views | OpenTelemetry Django middleware | Traces |
| Database queries | OpenTelemetry psycopg2 integration | Traces + Metrics |
| Redis calls | OpenTelemetry redis-py integration | Traces |
| Celery tasks | OpenTelemetry Celery integration | Traces |
| HTTP clients | OpenTelemetry requests/aiohttp | Traces |
| Cache calls | Django cache instrumentation | Traces |

### 3.2 Tracing Configuration

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

resource = Resource.create({
    "service.name": "tsbl-web",
    "environment": "production",
    "service.version": "2.1.0",
})

provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://otel-collector:4317"),
        max_queue_size=2048,
        max_export_batch_size=512,
    )
)
trace.set_tracer_provider(provider)
```

### 3.3 APM Metrics

| Metric | Source | Target | Warning | Critical |
|--------|--------|--------|---------|----------|
| Request throughput (req/s) | Trace count | Baseline | ±50% from baseline | ±80% from baseline |
| Request latency (P50) | Span duration | < 200ms | > 500ms | > 1s |
| Request latency (P95) | Span duration | < 500ms | > 1s | > 2s |
| Request latency (P99) | Span duration | < 1s | > 2s | > 5s |
| Error rate | Span status | < 0.5% | > 1% | > 5% |
| Apdex score | Trace duration | > 0.95 | < 0.90 | < 0.80 |
| Active users | Request context | Baseline | ±50% | ±100% |

### 3.4 Sampling Strategy

| Traffic Level | Head-Based Sampling Rate | Notes |
|--------------|-------------------------|-------|
| < 100 req/s | 100% | Low overhead at this volume |
| 100–1000 req/s | 50% | Priority: high-error routes always sampled |
| > 1000 req/s | 10% | Dynamic: increase for error spans |

Tail-based sampling applied via OpenTelemetry Collector: errors and slow traces always retained regardless of head-based sample rate.

---

## 4. Database Monitoring

### 4.1 PostgreSQL Metrics

| Metric | Source | Target | Warning | Critical |
|--------|--------|--------|---------|----------|
| Active connections | `pg_stat_activity` | < 50 | > 80% of max | > 95% of max |
| Connection wait time | PgBouncer stats | < 5ms | > 50ms | > 200ms |
| Query latency (P95) | `pg_stat_statements` | < 50ms | > 200ms | > 500ms |
| Slow queries (> 500ms) | `pg_stat_statements` | 0 | 5/min | 20/min |
| Replica lag | `pg_stat_replication` | < 50ms | > 500ms | > 5s |
| Cache hit ratio | `pg_statio_user_tables` | > 99% | < 95% | < 90% |
| Dead tuples | `pg_stat_user_tables` | < 5% | > 20% | > 50% |
| Table bloat | `pgstattuple` | < 10% | > 30% | > 50% |
| Transaction ID age | `pg_stat_database` | < 1B | > 1.5B | > 1.8B |

### 4.2 Slow Query Detection

- **Tool**: `pg_stat_statements` with automated collection via CloudWatch agent.
- **Threshold**: Queries exceeding 200ms are recorded with query text.
- **Alert**: Send slow query examples to dedicated Slack channel `#db-slow-queries`.
- **Review**: Weekly DBA review of top-10 slow queries; automated optimization suggestions via `pg_hint_plan`.

### 4.3 Database Health Dashboard

```json
{
  "title": "PostgreSQL Performance",
  "panels": [
    {"title": "Query Throughput", "metric": "pg:queries_per_second", "type": "graph"},
    {"title": "Query Latency (P50/P95/P99)", "metric": "pg:query_latency", "type": "graph"},
    {"title": "Connection Count", "metric": "pg:connections", "type": "gauge"},
    {"title": "Cache Hit Ratio", "metric": "pg:cache_hit_ratio", "type": "stat"},
    {"title": "Replica Lag", "metric": "pg:replica_lag", "type": "graph"},
    {"title": "Top 10 Slow Queries", "metric": "pg:slow_queries", "type": "table"},
    {"title": "Transaction Wraparound Age", "metric": "pg:txn_age", "type": "gauge"}
  ]
}
```

---

## 5. Cache Monitoring

### 5.1 Redis Metrics

| Metric | Source | Target | Warning | Critical |
|--------|--------|--------|---------|----------|
| Hit rate | `INFO stats` | > 95% | < 90% | < 80% |
| Memory usage | `INFO memory` | < 70% | > 80% | > 90% |
| Evictions/s | `INFO stats` | 0 | > 10/s | > 50/s |
| Connected clients | `INFO clients` | < 80% | > 90% | > maxclients |
| CPU | `INFO cpu` | < 50% | > 70% | > 85% |
| Replication lag | `INFO replication` | < 1s | > 5s | > 30s |
| Keyspace hits/miss | `INFO stats` | Ratio > 20 | Ratio < 5 | Ratio < 2 |

### 5.2 Cache Health Dashboard

- **Cache Hit Ratio by Pattern**: Query, page, fragment cache hit ratios.
- **Cache Memory Usage**: Per node memory utilization with eviction rate overlay.
- **Cache Key Distribution**: Top-10 key prefixes by memory consumption and count.
- **Cache Latency**: P50/P95 command latency for GET/SET/DELETE operations.
- **Stale Cache**: Keys expiring per second vs. keys accessed per second.

---

## 6. Queue Monitoring

### 6.1 Celery/RabbitMQ Metrics

| Metric | Source | Target | Warning | Critical |
|--------|--------|--------|---------|----------|
| Queue depth (critical) | RabbitMQ management | < 10 | > 50 | > 200 |
| Queue depth (total) | RabbitMQ management | < 100 | > 500 | > 2000 |
| Message processing rate | Celery stats | Baseline | -50% | -80% |
| Task latency (critical) | Celery stats | < 2s | > 10s | > 60s |
| Task latency (default) | Celery stats | < 10s | > 60s | > 300s |
| Task failure rate | Celery stats | < 1% | > 3% | > 10% |
| Worker saturation | Celery stats | < 70% | > 85% | > 95% |
| Unacknowledged messages | RabbitMQ management | < 10 | > 50 | > 200 |

### 6.2 Queue Dashboard

- **Queue Depth (Time Series)**: Per-queue depth overlay with auto-scaling events.
- **Task Processing Time**: Histogram of task duration by queue and task name.
- **Task Failure Rate**: Errors per task type with stack trace drill-down.
- **Worker Pool Status**: Active, idle, reserved workers per host.
- **Broker Connection Status**: RabbitMQ node health, cluster partition status.

---

## 7. Business Metrics Monitoring

### 7.1 Key Business Metrics

| Metric | Definition | Target | Alert | Dashboard |
|--------|-----------|--------|-------|-----------|
| Orders per minute | Completed orders | 10/min | < 1/min for 5min | Executive |
| Revenue (hourly) | Total confirmed order value | $5K/hr | -50% from baseline | Executive |
| Active users | Unique sessions in last 5min | 500 | < 100 | Product |
| Conversion rate | Checkout completions / cart additions | 15% | < 5% | Product |
| Cart abandonment | Carts created / never purchased | < 70% | > 85% | Product |
| Registration rate | New users per hour | 20/hr | < 5/hr | Growth |
| Average order value | Total revenue / order count | $50 | < $30 | Executive |
| Search success rate | Searches with clicks | > 80% | < 60% | Product |

### 7.2 Implementation

- **Source**: Custom Django signals emit events to a dedicated business metrics pipeline.
- **Storage**: InfluxDB or TimescaleDB for time-series business data.
- **Analytics Mixpanel/Amplitude**: Client-side events for user behavior analytics (complementary).

### 7.3 Executive Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  EXECUTIVE DASHBOARD │  Last 24h │  Refresh: 30s           │
├─────────────────┬─────────────────┬────────────────────────┤
│  Revenue (24h)  │  Orders (24h)   │  Active Users          │
│  $124,500       │  2,490          │  1,234                 │
│  ▲ 12% vs prev  │  ▲ 8% vs prev   │  ▼ 3% vs prev         │
├─────────────────┴─────────────────┴────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Revenue (7-day trend)                              │   │
│  │  ▁▃▅▇▆▇█  ▲ 15% WoW                                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌────────────┬────────────┬────────────┬──────────────┐   │
│  │  Conv Rate │  AOV       │  Cart Aban │  Reg Rate    │   │
│  │  14.2%     │  $50.00    │  68%       │  22/hr       │   │
│  │  ▲ 0.5%    │  ▲ $2.00   │  ▼ 2%      │  ▲ 5/hr      │   │
│  └────────────┴────────────┴────────────┴──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Recent Orders (last 50)  │ Status │ Amount │ Time   │   │
│  │  #ORD-12490               │ ✓ Delivered │ $49.99 │ 2m   │   │
│  │  #ORD-12489               │ ⟳ Processing│ $129.00│ 5m   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Alerting Rules and Thresholds

### 8.1 Alert Severity Levels

| Severity | Level | Response Time | Notification Channel |
|----------|-------|---------------|---------------------|
| **Critical (P0)** | Service down, data loss | 5 minutes | PagerDuty + SMS + Slack |
| **High (P1)** | Severe degradation | 15 minutes | PagerDuty + Slack |
| **Medium (P2)** | Partial degradation | 60 minutes | Slack |
| **Low (P3)** | Minor issue, no user impact | Next business day | Email + Slack |

### 8.2 Alert Rules

| Rule | Expression | Severity | For | Summary |
|------|-----------|----------|-----|---------|
| App 5xx rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05` | P0 | 5m | High 5xx error rate |
| App high latency | `histogram_quantile(0.95, rate(http_request_duration_seconds[5m])) > 2` | P1 | 5m | P95 latency > 2s |
| DB down | `pg_up == 0` | P0 | 1m | Database unreachable |
| DB high connections | `pg_connections > 80` | P1 | 5m | DB connections near max |
| Disk full | `node_filesystem_avail_bytes{mount="/"} / node_filesystem_size_bytes{mount="/"} < 0.1` | P1 | 5m | Less than 10% disk free |
| Redis hit rate low | `rate(redis_keyspace_misses_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) > 0.2` | P2 | 10m | Redis hit rate below 80% |
| Queue depth | `rabbitmq_queue_messages{queue="critical"} > 200` | P1 | 2m | Critical queue backing up |
| Certificate expiry | `(cert_expiry_timestamp - time()) / 86400 < 14` | P2 | 1h | SSL cert expires in < 14 days |
| Business orders | `rate(orders_total[30m]) < 1` | P1 | 30m | Order rate dropped below 1/min |

### 8.3 Alert Fatigue Prevention

- **No alert without runbook**: Every alert must have an associated runbook (Confluence page).
- **Aggregation**: Group similar alerts into a single notification.
- **Silencing**: Pre-approved maintenance windows automatically suppress alerts.
- **Escalation**: If no acknowledgement in 15 minutes, escalate to on-call manager.
- **Postmortem**: Every P0/P1 incident requires a blameless postmortem within 48 hours.

---

## 9. SLA/SLO Monitoring

### 9.1 Service Level Objectives

| Service | SLO | Measurement Window | Exclude |
|---------|-----|--------------------|---------|
| Web application | 99.9% uptime | 30 days rolling | Planned maintenance |
| API | 99.9% uptime, P95 < 500ms | 30 days rolling | Rate-limited requests |
| Checkout | 99.99% uptime, P95 < 2s | 30 days rolling | Payment gateway failures |
| Database | 99.95% uptime | 30 days rolling | Maintenance windows |
| Search | 99.9% uptime, P95 < 1s | 30 days rolling | Reindexing |
| CDN | 99.99% uptime | 30 days rolling | Origin issues |

### 9.2 Error Budget

- **Monthly error budget**: 100% - SLO = allowed downtime.
- 99.9% SLO → 43m 12s downtime per month.
- 99.95% SLO → 21m 36s downtime per month.
- **Consumption tracking**: Dashboard showing YTD error budget consumption.
- **Policy**: If error budget consumption exceeds 50% in a month, feature velocity slows — deploy freeze on Fridays.

### 9.3 SLO Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  SLO BURN RATE │  Rolling 30d │  Updated: Every 5min           │
├───────────────┬──────────────────┬──────────────────┬───────────┤
│ Service       │ Uptime           │ Error Budget     │ Status    │
│ Web App       │ 99.95%           │ 78% remaining    │ ✅ OK    │
│ API           │ 99.88%           │ 22% remaining    │ ⚠️ At Risk │
│ Checkout      │ 99.98%           │ 92% remaining    │ ✅ OK    │
│ Database      │ 99.99%           │ 95% remaining    │ ✅ OK    │
│ Search        │ 99.92%           │ 64% remaining    │ ✅ OK    │
└───────────────┴──────────────────┴──────────────────┴───────────┘
```

---

## 10. Incident Response Playbook

### 10.1 Incident Severity Flow

```
Alert Triggered
       │
       ▼
Acknowledged? ──No──→ Escalate after 5min (P0), 15min (P1)
       │
      Yes
       │
       ▼
Assess Severity & Assign Incident Commander
       │
       ├── P0: War room (Slack huddle + Zoom)
       ├── P1: Dedicated Slack channel #inc-xxxx
       ├── P2: Slack notification #incidents
       └── P3: Jira ticket (next day)
       │
       ▼
Execute Runbook ──→ Document Timeline
       │
       ▼
Mitigate / Resolve
       │
       ▼
Post-Incident Review (within 48h)
```

### 10.2 Incident Communication

| Stakeholder | P0 | P1 | P2/P3 |
|-------------|-----|-----|-------|
| Engineering team | #inc-xxxx channel + war room | #inc-xxxx channel | #incidents |
| Product management | Slack DM + email | Email summary | — |
| Executive team | SMS + email (within 15min) | Email (within 1h) | — |
| Customers | Status page update | Status page (if impacting) | — |
| Support team | Email template sent to CS | Email to CS | — |

### 10.3 Status Page Categories

| Status | Definition | Color | Target Update Frequency |
|--------|-----------|-------|------------------------|
| Operational | All systems healthy | Green | — |
| Degraded Performance | Noticeable slowdown but functional | Yellow | Every 30 min |
| Partial Outage | Some features unavailable | Orange | Every 15 min |
| Major Outage | Core functionality unavailable | Red | Every 5 min |
| Maintenance | Scheduled downtime | Blue | Prior notification |

### 10.4 Incident Timeline Template

```markdown
# Incident Report: INC-XXXX

## Summary
- **Date**: 2026-07-01
- **Duration**: 45 minutes (14:30 - 15:15 UTC)
- **Impact**: 1,234 users unable to checkout (0.5% of traffic)
- **Root Cause**: Database connection pool exhaustion due to unoptimized query

## Timeline
| Time (UTC) | Event |
|------------|-------|
| 14:30:00 | Alert triggered: DB connections > 95% |
| 14:30:15 | PagerDuty acknowledged by [Engineer] |
| 14:31:00 | #inc-1234 channel created |
| 14:33:00 | Identified connection spike from order export cron |
| 14:35:00 | Killed runaway cron job |
| 14:38:00 | Connections returned to normal |
| 14:40:00 | Order export code fix deployed |
| 14:45:00 | Monitoring confirmed recovery |
| 15:15:00 | Postmortem scheduled |

## Root Cause Analysis
- [Detailed analysis...]

## Action Items
- [ ] Add connection pool monitoring alert
- [ ] Implement query timeout for export jobs
- [ ] Add rate limiting to admin export endpoints
```

---

## 11. Dashboard Design for Stakeholders

### 11.1 Engineering Dashboard (Grafana)

- **Service Health**: Uptime, error rate, latency (P50/P95/P99) per service.
- **Infrastructure**: CPU, memory, disk, network per host/service.
- **Database**: Query throughput, slow queries, connections, replication lag.
- **Cache**: Hit ratio, evictions, memory usage.
- **Deployments**: Recent deploy events overlaid on error rate.

### 11.2 Product Dashboard (Grafana)

- **User Activity**: Active users, sessions, pageviews.
- **Conversion Funnel**: Browse → Cart → Checkout → Payment → Confirmation.
- **Performance**: LCP, FID, CLS from RUM data.
- **Feature Adoption**: New feature usage per cohort.

### 11.3 Executive Dashboard (Grafana + Metabase)

- **Revenue**: Daily/weekly/monthly revenue with trends.
- **Orders**: Order volume, average order value, fulfillment status.
- **Growth**: New users, returning users, churn rate.
- **Health**: Overall system status (green/yellow/red), SLO burn rate.

---

## 12. Implementation Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| Q1 2026 | Month 1-2 | Infrastructure monitoring (CloudWatch + Grafana) |
| Q1 2026 | Month 2-3 | APM instrumentation (OpenTelemetry) |
| Q2 2026 | Month 4-5 | Database + cache + queue monitoring |
| Q2 2026 | Month 5-6 | Business metrics pipeline + executive dashboard |
| Q3 2026 | Month 7-8 | Alerting rules, SLO monitoring, error budgets |
| Q3 2026 | Month 8-9 | Incident response playbook + on-call rotation |

---

*Document Owner: Principal Architect*  
*Last Updated: 2026-07-01*  
*Review Cycle: Quarterly*
