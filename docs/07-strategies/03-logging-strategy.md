# Logging Strategy

## 1. Log Levels and Usage Guidelines

### 1.1 Level Definitions

| Level | Value | Color | When to Use |
|-------|-------|-------|-------------|
| **FATAL** | 0 | Red | Application is in a catastrophic state and cannot continue (e.g., database unreachable at startup, out of disk space). Triggers immediate PagerDuty alert. |
| **ERROR** | 1 | Orange | An operation failed that should have succeeded (e.g., payment gateway returned 500, database connection failed mid-request). Triggers alert. |
| **WARN** | 2 | Yellow | Something unexpected happened but the system self-recovered (e.g., retry succeeded on second attempt, degraded cache fallback used). Does not trigger alert but routed to daily review. |
| **INFO** | 3 | Blue | Key business events and lifecycle milestones (e.g., order placed, user registered, payment confirmed, deployment started). Used for operational visibility. |
| **DEBUG** | 4 | Gray | Detailed diagnostic information relevant when troubleshooting a specific component. Disabled in production by default; enabled per-module via dynamic config. |

### 1.2 Level Configuration by Environment

| Environment | Console | File | Remote (Loki) |
|-------------|---------|------|---------------|
| Production | WARN | ERROR | INFO |
| Staging | INFO | DEBUG | DEBUG |
| Development | DEBUG | DEBUG | — |
| QA | INFO | DEBUG | DEBUG |

Dynamic level override via environment variable `LOG_LEVEL_OVERRIDE: {"django.db": "DEBUG"}` — no restart required (watched in 60s intervals).

---

## 2. Structured Logging Format

### 2.1 JSON Schema

All log entries are emitted as newline-delimited JSON (NDJSON). Each entry follows this schema:

```json
{
  "timestamp": "2026-07-01T14:30:00.123Z",
  "level": "INFO",
  "logger": "tsbl.orders",
  "message": "Order created successfully",
  "service": "web",
  "environment": "production",
  "region": "us-east-1",
  "instance": "i-0abcd1234efgh5678",
  "trace_id": "8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d",
  "span_id": "a1b2c3d4e5f6a7b8",
  "correlation_id": "req-7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b",
  "user_id": "usr_8a1b2c3d4e5f",
  "session_id": "sess_a1b2c3d4",
  "duration_ms": 245,
  "extra": {}
}
```

### 2.2 Mandatory Fields

| Field | Type | Source | Required | Description |
|-------|------|--------|----------|-------------|
| `timestamp` | ISO 8601 | System | Yes | UTC timestamp with millisecond precision |
| `level` | string | Application | Yes | Log level (uppercase) |
| `logger` | string | Application | Yes | Module/component name (dot-separated) |
| `message` | string | Application | Yes | Human-readable log message |
| `service` | string | Environment | Yes | Service/application name |
| `environment` | string | Environment | Yes | prod/staging/dev/qa |
| `trace_id` | hex string | OpenTelemetry | Yes | Distributed tracing ID (16 bytes hex) |
| `correlation_id` | UUID | Ingress | Yes | End-to-end request correlation ID |

### 2.3 Python Logging Configuration

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": (
                "%(timestamp)s %(level)s %(name)s %(message)s "
                "%(service)s %(environment)s %(trace_id)s %(span_id)s "
                "%(correlation_id)s %(user_id)s %(duration_ms)s"
            ),
            "rename_fields": {"name": "logger", "asctime": "timestamp"},
        },
        "console": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
```

---

## 3. Centralized Logging Architecture

### 3.1 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Application | Django + Python `logging` | Generate structured JSON logs |
| Collector | Promtail (Grafana Loki) | Ship logs from each node to Loki |
| Storage | Grafana Loki | Horizontally scalable log storage |
| UI | Grafana Dashboards | Log exploration, search, alerting |
| Long-term Archive | S3 (Loki boltdb-shipper) | Cost-effective cold storage |
| Alerting | Grafana Alerts | Log-based alert rules |

### 3.2 Architecture Diagram

```
                        ┌──────────────────────┐
                        │   Application (K8s)    │
                        │  stdout → JSON logs    │
                        └──────────┬────────────┘
                                   │
                        ┌──────────▼────────────┐
                        │      Promtail          │
                        │ (DaemonSet per node)    │
                        │ Labels: service, env    │
                        └──────────┬────────────┘
                                   │
                        ┌──────────▼────────────┐
                        │   Grafana Loki          │
                        │ (3 replicas,           │
                        │  boltdb-shipper to S3)  │
                        └──────────┬────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
     ┌────────▼───────┐  ┌────────▼───────┐  ┌─────────▼────────┐
     │  Grafana UI     │  │  Grafana        │  │  S3 Cold Storage  │
     │  Log Explorer   │  │  Alerts         │  │  (90+ days)       │
     └────────────────┘  └────────────────┘  └──────────────────┘
```

### 3.3 Deployment (Docker Compose / K8s)

- **Promtail**: DaemonSet on each Kubernetes node. Reads container stdout logs.
- **Loki**: StatefulSet with 3 replicas. Uses `boltdb-shipper` to store index + chunks on S3.
- **Retention**: 30 days in Loki (hot), 365 days in S3 (cold).
- **Ingestion**: Target 50 MB/s ingestion rate at peak.

---

## 4. Log Retention Policies

| Tier | Storage | Duration | Cost | Access |
|------|---------|----------|------|--------|
| Hot (Loki) | EBS/SSD | 7 days | High | Instant query |
| Warm (Loki) | S3 Standard | 30 days | Medium | Instant query |
| Cold (S3) | S3 Glacier | 365 days | Low | 5-min retrieval |
| Archive | S3 Glacier Deep Archive | 7 years | Minimal | 12-hour retrieval |

### Retention Rules

- **Audit Logs**: 7 years (regulatory requirement).
- **Security Logs**: 365 days (SOC2/PCI compliance).
- **Application Logs**: 30 days (operational requirement).
- **Debug Logs**: 3 days (only if DEBUG level enabled).
- **Access Logs**: 90 days (analysis + troubleshooting).

---

## 5. Log Ingestion Pipeline

```
Application → stdout → Promtail → Loki → S3
                  ↑                       ↓
             Logstash (legacy        Grafana Alerts
             syslog bridge)          (log-based)
```

### 5.1 Pipeline Specifications

| Stage | Protocol | Format | Buffer |
|-------|----------|--------|--------|
| App → stdout | Write to fd 1 | NDJSON | Kernel buffer |
| stdout → Promtail | Promtail reads container logs | JSON | Promtail positions file |
| Promtail → Loki | gRPC (HTTP fallback) | Protobuf (snappy) | In-memory batch (500KB/5s) |
| Loki → S3 | boltdb-shipper | Chunks | Periodic sync (every 10min) |

### 5.2 Error Handling

| Failure Scenario | Behavior | Recovery |
|-----------------|----------|----------|
| Promtail cannot reach Loki | Buffers up to 10GB on disk | Retry with exponential backoff |
| Loki ingestion throttled | Returns 429; Promtail backoff | Scale Loki ingestion rate |
| S3 write fails | Chunks remain in boltdb | Retry; escalate after 1 hour |

---

## 6. Correlation IDs for Request Tracing

### 6.1 ID Generation and Propagation

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│  CloudFront   │────▶│  Application  │────▶│   Celery Task │────▶│  Database    │
│  X-Amzn-     │     │  correlation  │     │  inherits    │     │  pgaudit    │
│  Trace-Id    │     │  _id header   │     │  correlation │     │  log line   │
└─────────────┘     └──────────────┘     │  _id          │     └─────────────┘
                                         └──────────────┘
```

### 6.2 Implementation

| Layer | Correlation ID Source | Header Mapping |
|-------|---------------------|----------------|
| Ingress | CloudFront generates `X-Amzn-Trace-Id` | Used as `trace_id` |
| Django middleware | UUID generated if missing | Sets `X-Correlation-Id` response header |
| Outgoing HTTP | Propagated in `X-Correlation-Id` header | All internal service calls |
| Celery tasks | Extracted from request headers | Injected into task context |
| Database | Logged via `log_statement = 'mod'` | Include correlation_id via `SET LOCAL` |

### 6.3 Django Middleware

```python
class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.headers.get(
            "X-Correlation-Id",
            str(uuid.uuid4())
        )
        request.correlation_id = correlation_id
        with contextlib.ExitStack() as stack:
            stack.enter_context(
            override_log_context(correlation_id=correlation_id)
        )
        response = self.get_response(request)
        response["X-Correlation-Id"] = correlation_id
        return response
```

---

## 7. Application, Audit, and Security Logging

### 7.1 Comparison

| Aspect | Application Logging | Audit Logging | Security Logging |
|--------|-------------------|---------------|------------------|
| Purpose | Operational debugging | Compliance & accountability | Threat detection |
| Retention | 30 days | 7 years | 1 year |
| Storage | Loki hot/warm | S3 Glacier | Loki + S3 |
| PII | Must be masked | Contains identity (justified) | Must be masked |
| Legal hold | No | Yes (litigation hold) | No |
| Sample events | DB query, API call, cache miss | Order placed, refund issued | Login failed, permission denied |

### 7.2 Audit Log Schema

```json
{
  "timestamp": "2026-07-01T14:30:00.123Z",
  "type": "audit",
  "action": "order.created",
  "actor_id": "usr_8a1b2c3d4e5f",
  "actor_ip": "203.0.113.42",
  "target_type": "order",
  "target_id": "ord_f9e8d7c6b5a4",
  "changes": {
    "before": {"status": "pending", "total": 0},
    "after": {"status": "confirmed", "total": 2999}
  },
  "outcome": "success"
}
```

### 7.3 Security Log Schema

```json
{
  "timestamp": "2026-07-01T14:30:00.123Z",
  "type": "security",
  "event": "login.failed",
  "user_id": "usr_8a1b2c3d4e5f",
  "source_ip": "198.51.100.23",
  "user_agent": "Mozilla/5.0 ...",
  "failure_reason": "invalid_password",
  "attempt_count": 3,
  "geo_location": {"country": "NG", "city": "Lagos"},
  "flagged": false
}
```

---

## 8. Sensitive Data Masking

### 8.1 Fields to Mask

| Category | Fields | Mask Strategy | Example Output |
|----------|--------|--------------|----------------|
| Authentication | passwords, tokens, API keys | `[REDACTED]` | `"password": "[REDACTED]"` |
| Payment | credit card numbers, CVV, PAN | Show last 4 | `"card_number": "****-****-****-1234"` |
| PII | email, phone, address | Partial mask | `"email": "j***@example.com"` |
| Personal | full name, national ID | Full mask | `"name": "[REDACTED]"` |
| Health | medical info | Full mask | `"diagnosis": "[REDACTED]"` |

### 8.2 Implementation

- **Django logging**: Custom `SanitizingFormatter` extends `JsonFormatter` — traverses log record's `extra` dict and masks known PII keys.
- **Database**: Application-level masking — never SELECT unmasked PII into application logs.
- **API Gateway**: WAF ACL filters regex patterns for credit card, SSN, etc. from request/response bodies.
- **Post-processing**: Promtail configured with `pipeline_stages` containing `replace` stages for sensitive patterns.

### 8.3 Schema-Based Masking

```yaml
masking_rules:
  - field_pattern: "password|secret|token|key|authorization"
    strategy: redact
    replacement: "[REDACTED]"

  - field_pattern: "email"
    strategy: partial_left
    visible_chars: 1

  - field_pattern: "phone|mobile|telephone"
    strategy: partial_middle
    visible_start: 3
    visible_end: 2

  - field_pattern: "card_number|pan|cc_number"
    strategy: partial_right
    visible_chars: 4
```

---

## 9. Log Aggregation and Search Strategy

### 9.1 Search Operations

| Use Case | Query Pattern | Dashboard |
|----------|--------------|-----------|
| Error investigation | `{service="web"} |= "ERROR"` | Error Explorer |
| Request tracing | `{environment="prod"} |= "8a1b2c3d"` | Trace View |
| User activity | `{service} |= "user_id=usr_xyz"` | User Activity |
| Performance issues | `{service} \| json \| duration_ms > 1000` | Slow Requests |
| Security audit | `{type="security"} \| json` | Security Dashboard |

### 9.2 Indexing Strategy

- **Labels**: `service`, `environment`, `region`, `level` — high cardinality labels avoided.
- **Structured Metadata**: Parsed on ingestion via Promtail `json` stage → stored as indexed fields.
- **Full-Text Search**: `message` field is parsed and searchable.
- **LogQL**: All queries use Loki's LogQL — no separate Elasticsearch needed.

### 9.3 Search Performance Targets

| Query Type | Target Latency | Max Result Size |
|------------|---------------|-----------------|
| Recent errors (last 1h) | < 1s | 1000 lines |
| User trace (last 7d) | < 5s | 1000 lines |
| Aggregation (last 24h) | < 10s | 5000 lines |
| Cold storage (last 1yr) | < 5min | 10000 lines |

### 9.4 Grafana Dashboard Integration

- **Logs Panel**: Embedded log panels in service dashboards, filtered to the relevant service.
- **Live Tail**: Real-time log streaming for incident response.
- **Alert Rule Integration**:
  - `rate({level="ERROR"}[5m]) > 0.01` → PagerDuty notification.
  - `count by (service) ({level="FATAL"}) > 0` → Critical PagerDuty.
  - `absent({service="web"})` → Missing logs → instance down.

---

## 10. Implementation Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| Foundation | Week 1-2 | Structured JSON logging implementation in Django |
| Pipeline | Week 3-4 | Promtail + Loki deployment (staging first) |
| Dashboards | Week 5-6 | Grafana log dashboards + alert rules |
| Correlation | Week 7-8 | Correlation ID middleware + OpenTelemetry integration |
| Masking | Week 9-10 | PII masking implementation + audit |
| Audit | Week 11-12 | Audit logging infrastructure + retention policies |

---

*Document Owner: Principal Architect*  
*Last Updated: 2026-07-01*  
*Review Cycle: Quarterly*
