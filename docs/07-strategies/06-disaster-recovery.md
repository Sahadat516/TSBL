# Disaster Recovery Plan

## 1. Recovery Objectives

### 1.1 Recovery Time Objective (RTO) and Recovery Point Objective (RPO)

| Tier | System | RTO (Max downtime) | RPO (Max data loss) | Business Impact |
|------|--------|-------------------|---------------------|-----------------|
| **Tier 0** | Payment Gateway, Checkout, Order Processing | 1 hour | 5 minutes | Revenue-critical: $10K+/min |
| **Tier 1** | Product Catalog, Search, User Auth | 4 hours | 1 hour | Revenue-adjacent: $5K+/min |
| **Tier 2** | Reviews, Recommendations, Analytics | 8 hours | 4 hours | Supplementary features |
| **Tier 3** | Admin Dashboard, Reporting, Marketing | 24 hours | 24 hours | Internal operations |
| **Tier 4** | Historical Archives, Logs | 48 hours | 7 days | Compliance / forensics |

### 1.2 Accepted Downtime by Scenario

| Scenario | Allowable Downtime | Allowable Data Loss | Priority |
|----------|-------------------|---------------------|----------|
| Single AZ failure | 0 (HA active-passive) | 0 | Automatic failover |
| Single region failure | 4 hours (Tier 0-1) | 1 hour | Highest |
| Database corruption | 4 hours (Tier 0-1) | 1 hour (PITR) | High |
| Application misconfiguration | 30 minutes (rollback) | 0 | Medium |
| Security breach | 1 hour (containment) | Forensic snapshot | Critical |
| Ransomware attack | 24 hours | 24 hours (to clean backup) | High |
| Cloud provider outage | 8 hours (multi-region) | 1 hour | Medium |

---

## 2. Disaster Scenarios and Mitigation

### 2.1 Scenario Classification Matrix

| Scenario ID | Name | Probability | Impact | Tier Class | Mitigation Strategy |
|------------|------|------------|--------|------------|---------------------|
| DR-001 | Single EC2/Container failure | High | Low | T0-T4 | Auto-healing (ECS replaces failed tasks) |
| DR-002 | Single AZ failure | Medium | Medium | T0-T4 | Multi-AZ deployment |
| DR-003 | Database primary failure | Medium | High | T0-T2 | Automatic replica promotion |
| DR-004 | Database data corruption | Low | Critical | T0-T2 | PITR to pre-corruption timestamp |
| DR-005 | Redis cluster failure | Medium | Medium | T0-T2 | Cluster auto-failover |
| DR-006 | Region-wide cloud outage | Low | Critical | T0-T1 | Multi-region DR (warm standby) |
| DR-007 | DNS provider failure | Low | High | T0-T4 | Route53 with multiple NS records |
| DR-008 | CDN failure | Medium | Medium | T0-T2 | Origin direct fallback |
| DR-009 | DDoS attack | Medium | High | T0-T4 | Shield Advanced + WAF + auto-scaling |
| DR-010 | Ransomware / data encryption | Low | Critical | T0-T4 | Immutable backups + MFA delete |
| DR-011 | Accidental data deletion | Medium | Medium | T0-T4 | S3 versioning + point-in-time recovery |
| DR-012 | SSL certificate expiry | Medium | High | T0-T4 | Automated renewal via ACM |
| DR-013 | Dependency service outage (Stripe) | Low | High | T0 | Circuit breaker to alternate gateway |
| DR-014 | Third-party API failure (shipping) | Medium | Medium | T1-T2 | Queue and retry with backoff |

### 2.2 Detailed Response per Scenario

#### DR-003: Database Primary Failure

| Step | Action | Owner | ETA |
|------|--------|-------|-----|
| 1 | Detect primary failure via CloudWatch alarm | Automated | 0 min |
| 2 | Initiate RDS Multi-AZ failover | Automated | 1 min |
| 3 | Verify new primary is accepting writes | On-call DBA | 2 min |
| 4 | Update application connection string (if needed) | On-call engineer | 2 min |
| 5 | Verify application health via /health endpoint | On-call engineer | 3 min |
| 6 | Restart failed read replicas | On-call DBA | 5 min |
| 7 | Trigger postmortem | Incident Commander | After resolution |

#### DR-004: Database Data Corruption

| Step | Action | Owner | ETA |
|------|--------|-------|-----|
| 1 | Detect corruption via integrity checks or application errors | Automated / On-call | 0 min |
| 2 | Stop application writes to prevent further corruption | On-call engineer | 2 min |
| 3 | Identify timestamp of last known good state | On-call DBA | 5 min |
| 4 | Restore latest full backup to new RDS instance | On-call DBA | 30–60 min |
| 5 | Apply WAL files up to pre-corruption timestamp | On-call DBA | 10–30 min |
| 6 | Verify data integrity with validation queries | On-call DBA | 10 min |
| 7 | Redirect traffic to restored database | On-call engineer | 5 min |
| 8 | Resume application writes | On-call engineer | 2 min |
| 9 | Investigate root cause of corruption | Incident team | Post-recovery |

#### DR-006: Region-Wide Cloud Outage

| Step | Action | Owner | ETA |
|------|--------|-------|-----|
| 1 | Confirm region outage via status page + multiple sources | Incident Commander | 5 min |
| 2 | Declare disaster and activate DR plan | Incident Commander | 5 min |
| 3 | Spin up infrastructure in DR region (eu-west-1) via Terraform | DevOps | 30 min |
| 4 | Restore database from S3 CRR in DR region | DBA | 60 min |
| 5 | Configure Route53 failover to DR region | DevOps | 5 min |
| 6 | Verify application health in DR region | QA Engineer | 15 min |
| 7 | Update status page to "Operational" | Incident Commander | 5 min |
| 8 | Continue operations in DR until primary region restored | All | Ongoing |

---

## 3. Multi-Region Deployment Strategy

### 3.1 Regional Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Route 53 (Latency-Based)                       │
│                     Health checks → failover routing                    │
└──────────────────────┬──────────────────────────┬────────────────────┘
                       │                          │
┌──────────────────────▼──────────┐  ┌─────────────▼────────────────────┐
│    Primary Region               │  │    DR Region                      │
│    ap-southeast-1 (Singapore)   │  │    eu-west-1 (Ireland)            │
│                                 │  │                                   │
│  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐    │
│  │  ALB (Active)           │    │  │  │  ALB (Standby, minimal   │    │
│  │  ECS Fargate Cluster    │    │  │  │  ECS cluster)            │    │
│  │  Auto-scaling: 2-20     │    │  │  │  Auto-scaling: 1-2       │    │
│  └─────────────────────────┘    │  │  └──────────────────────────┘    │
│                                 │  │                                   │
│  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐    │
│  │  RDS Primary (Multi-AZ) │    │  │  │  RDS Read Replica        │    │
│  │  + 2 Read Replicas      │    │  │  │  (promotes to primary)   │    │
│  └─────────────────────────┘    │  │  └──────────────────────────┘    │
│                                 │  │                                   │
│  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐    │
│  │  ElastiCache Redis       │    │  │  │  Redis (empty; seeded    │    │
│  │  Cluster (3 nodes)       │    │  │  │  on failover)            │    │
│  └─────────────────────────┘    │  │  └──────────────────────────┘    │
│                                 │  │                                   │
│  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐    │
│  │  S3 (Primary)           │    │  │  │  S3 (CRR Destination)    │    │
│  └─────────────────────────┘    │  │  └──────────────────────────┘    │
│                                 │  │                                   │
│  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐    │
│  │  RabbitMQ (HA cluster)   │    │  │  │  RabbitMQ (empty)        │    │
│  └─────────────────────────┘    │  │  └──────────────────────────┘    │
│                                 │  │                                   │
│  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐    │
│  │  Elasticsearch Cluster   │    │  │  │  Elasticsearch (restore  │    │
│  │  (3 nodes)               │    │  │  │  from S2 snapshot)       │    │
│  └─────────────────────────┘    │  │  └──────────────────────────┘    │
└──────────────────────────────────┘  └──────────────────────────────────┘
```

### 3.2 DR Region Warm Standby

| Resource | Primary (ap-southeast-1) | DR (eu-west-1) | Type |
|----------|------------------------|----------------|------|
| ECS Fargate | 2–20 tasks (auto-scaled) | 1 task (minimal) | Warm |
| RDS PostgreSQL | db.r6g.2xlarge (Multi-AZ) | db.r6g.xlarge (single-AZ) | Warm (replica) |
| Redis | 3 nodes (r6g.xlarge) | — | Cold (seed on failover) |
| RabbitMQ | 3 node cluster | — | Cold (recover from definitions) |
| Elasticsearch | 3 node cluster | — | Cold (restore from snapshot) |
| S3 | Standard | CRR destination | Hot (always replicating) |
| ALB | Active | Deactivated | Cold (enable on failover) |
| Route53 | Primary record | Failover record | Configured (disabled) |

### 3.3 DR Region Activation Sequence

```
Minute 0:  Disaster declared
Minute 5:  Terraform apply — scale up DR resources
Minute 15: Route53 health check fails → auto-failover to DR
Minute 20: RDS replica promoted to primary
Minute 30: Elasticsearch restored from S3 snapshot
Minute 35: Redis warmed from database (cache rebuild)
Minute 45: Application health verified
Minute 60: Full operations in DR region (Tier 0-1)
```

---

## 4. Failover and Failback Procedures

### 4.1 Failover Procedure (Primary → DR)

#### Pre-Failover Checklist

- [ ] Confirm primary region is truly unavailable (not a transient issue).
- [ ] Notify stakeholders via Slack `#dr-activation` channel.
- [ ] Ensure DR region has sufficient capacity (apply Terraform).
- [ ] Verify S3 CRR is current (lag < 15 min).
- [ ] Verify database backup in DR region is accessible.
- [ ] Disable monitoring alerts that will fire during transition.
- [ ] Update status page to "Major Outage — Investigating."

#### Failover Execution

```bash
#!/bin/bash
# DR Failover Script (partial; each step has a detailed runbook)

# Step 1: Promote RDS replica in DR region
aws rds promote-read-replica \
  --db-instance-identifier tsbl-db-dr \
  --region eu-west-1

# Step 2: Update application to point to new primary
aws ssm put-parameter \
  --name "/tsbl/production/DATABASE_URL" \
  --value "postgresql://user:pass@tsbl-db-dr.xxxxx.eu-west-1.rds.amazonaws.com:5432/tsbl" \
  --type SecureString \
  --overwrite \
  --region eu-west-1

# Step 3: Enable ALB in DR region
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:eu-west-1:xxx:listener/app/tsbl-dr/xxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:eu-west-1:xxx:targetgroup/tsbl-app/xxx

# Step 4: Update Route53 to point to DR ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXX \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.tsbl.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "tsbl-dr-alb-xxxxx.eu-west-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        },
        "SetIdentifier": "dr",
        "Failover": "PRIMARY",
        "HealthCheckId": "xxx"
      }
    }]
  }'

# Step 5: Restart ECS services
aws ecs update-service \
  --cluster tsbl-dr \
  --service tsbl-app \
  --desired-count 4 \
  --region eu-west-1

echo "Failover initiated. Monitoring..."
```

#### Post-Failover Checklist

- [ ] All Tier 0-1 services operational in DR region.
- [ ] Database write validation (create test order).
- [ ] Search functional (verify index completeness).
- [ ] Image serving functional (verify S3 CRR objects accessible).
- [ ] Background workers operational (verify Celery + RabbitMQ).
- [ ] Monitoring dashboards updated to DR region.
- [ ] Status page updated to "Degraded Performance — Operating from DR."
- [ ] Incident timeline documented.

### 4.2 Failback Procedure (DR → Primary)

#### Pre-Failback Checklist

- [ ] Primary region confirmed healthy (verified for 24+ hours).
- [ ] No data divergence between DR and primary databases.
- [ ] Primary database synchronized from DR (reverse replication).
- [ ] All infrastructure in primary region rebuilt (Terraform).
- [ ] DR write operations stopped (read-only mode or maintenance page).
- [ ] Communications scheduled to minimize user impact.

#### Failback Steps

```
1. Stop all write operations in DR (maintenance page).
2. Take final backup of DR database.
3. Restore DR database to primary region.
4. Point application to primary database.
5. Route53 failover back to primary ALB.
6. Verify all services in primary region.
7. Scale down DR region.
8. Update status page to "Operational."
```

#### Post-Failback Verification

- [ ] Database: row counts match between DR last backup and primary.
- [ ] Application: /health, /api/v1/products, /api/v1/orders return 200.
- [ ] Search: Elasticsearch index complete.
- [ ] Caching: Redis warming complete (hit ratio > 90%).
- [ ] Queue: no backlog in any queue.
- [ ] Monitoring: metrics flowing from primary region.

---

## 5. Database Point-in-Time Recovery

### 5.1 Recovery Scenarios

| Scenario | Recovery Method | Expected RTO | Expected RPO |
|----------|---------------|--------------|--------------|
| Accidental DELETE (no WHERE) | PITR to 1 minute before statement | 2 hours | < 1 minute |
| Accidental DROP TABLE | PITR to 1 minute before statement | 2 hours | < 1 minute |
| Bad data migration | PITR to pre-migration timestamp | 3 hours | < 15 minutes |
| Ransomware encryption | PITR to last known clean state | 4 hours | < 1 hour |
| Logical corruption | PITR to pre-corruption timestamp | 3 hours | Depends on detection |

### 5.2 PITR Procedure

```bash
#!/bin/bash
# Point-in-Time Recovery procedure

# Parameters
TARGET_TIMESTAMP="${1}"  # e.g., "2026-07-01 14:30:00 UTC"
RESTORE_INSTANCE="tsbl-db-pitr-restore"
SOURCE_BACKUP_BUCKET="s3://tsbl-backups/postgresql"

echo "[1/5] Finding latest full backup before ${TARGET_TIMESTAMP}"
LATEST_FULL=$(aws s3 ls ${SOURCE_BACKUP_BUCKET}/full/ \
  | awk '{print $4}' \
  | sort \
  | grep -B1 "$(date -d "${TARGET_TIMESTAMP}" +%Y%m%d)" \
  | head -1)

echo "[2/5] Creating new RDS instance for restore"
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier tsbl-production \
  --target-db-instance-identifier ${RESTORE_INSTANCE} \
  --restore-time "${TARGET_TIMESTAMP}" \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name tsbl-private \
  --multi-az false

echo "[3/5] Waiting for instance to become available..."
aws rds wait db-instance-available \
  --db-instance-identifier ${RESTORE_INSTANCE}

echo "[4/5] Running integrity checks"
psql -h ${RESTORE_INSTANCE}.xxxxx.ap-southeast-1.rds.amazonaws.com \
  -U tsbl_admin -d tsbl -c "
    SELECT 'Table count OK: ' || COUNT(*)::text 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
    
    SELECT 'Order count: ' || COUNT(*)::text FROM orders;
    SELECT 'User count: ' || COUNT(*)::text FROM users;
"

echo "[5/5] Restore complete. Instance: ${RESTORE_INSTANCE}"
echo "Promote to production following runbook DR-DB-PROMOTION."
```

### 5.3 Validation After PITR

```sql
-- 1. Check row counts match expected baselines
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products;

-- 2. Check referential integrity
SELECT 'orphan_order_items', COUNT(*)
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.id IS NULL;

-- 3. Check no negative values in monetary columns
SELECT 'negative_prices', COUNT(*)
FROM products
WHERE price < 0;

-- 4. Check max timestamp is before target
SELECT 'max_order_date', MAX(created_at)
FROM orders
HAVING MAX(created_at) < '2026-07-01 14:30:00+00';

-- 5. Verify critical aggregates
SELECT 'total_revenue', SUM(total)
FROM orders
WHERE status = 'confirmed'
  AND created_at < '2026-07-01 14:30:00+00';
```

---

## 6. Data Integrity Verification After Recovery

### 6.1 Automated Integrity Checks

| Check | Type | Query/Command | Failure Action |
|-------|------|---------------|----------------|
| Constraint checks | Database | `SET CONSTRAINTS ALL IMMEDIATE;` | Rollback and investigate |
| Sequence alignment | Database | Check `currval == max(id) + 1` | Reset sequences |
| Checksum verification | File | `aws s3api head-object --bucket X --key Y` | Re-restore from alternate source |
| Index validation | Database | `amcheck` extension | Rebuild indexes |
| FK consistency | Database | `LEFT JOIN` orphan checks | Re-insert missing references |
| Business logic check | Application | `Create test order` API call | Investigate application state |

### 6.2 Sample Validation Script

```python
# validation_runner.py — run after any database recovery

VALIDATIONS = [
    {
        "name": "referential_integrity",
        "query": """
            SELECT table_name, COUNT(*) as orphans
            FROM (
                SELECT 'order_items' as table_name, oi.id
                FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.id
                WHERE o.id IS NULL
                UNION ALL
                SELECT 'product_variants', pv.id
                FROM product_variants pv LEFT JOIN products p ON pv.product_id = p.id
                WHERE p.id IS NULL
            ) orphans
            GROUP BY table_name
        """,
        "expected": lambda rows: all(r["orphans"] == 0 for r in rows),
        "severity": "CRITICAL",
    },
    {
        "name": "sequence_alignment",
        "query": """
            SELECT table_name, last_value, max_id
            FROM (
                SELECT 'orders' as table_name,
                       last_value,
                       (SELECT MAX(id) FROM orders) as max_id
                FROM orders_id_seq
                UNION ALL
                SELECT 'users', last_value, (SELECT MAX(id) FROM users)
                FROM users_id_seq
            ) seq
            WHERE last_value < max_id
        """,
        "expected": lambda rows: len(rows) == 0,
        "severity": "HIGH",
    },
    {
        "name": "business_kpis",
        "query": """
            SELECT 'total_orders' as metric, COUNT(*) as value FROM orders
            UNION ALL
            SELECT 'total_revenue', COALESCE(SUM(total), 0) FROM orders WHERE status = 'confirmed'
            UNION ALL
            SELECT 'active_users', COUNT(*) FROM users WHERE is_active = true
        """,
        "expected": lambda rows: all(r["value"] > 0 for r in rows if "orders" in r["metric"]),
        "severity": "MEDIUM",
    },
]
```

---

## 7. Communication Plan During Disasters

### 7.1 Communication Channels

| Audience | Primary Channel | Secondary Channel | Update Frequency |
|----------|----------------|-------------------|-----------------|
| Incident Response Team | Slack `#dr-activation` | Phone / SMS | Continuous (real-time) |
| Engineering Team | Slack `#engineering` | Email | Every 15 min (P0) |
| Product Management | Slack `#product` | Phone | Every 30 min |
| Executive Team | Email + Phone | SMS | Every 60 min (or on escalation) |
| Customer Support | Slack `#support-leads` | Email + Phone | Every 30 min |
| Customers | Status page (status.tsbl.com) | Social media (X/Twitter) | Every change in status |
| Public / Media | Status page | — | As needed |

### 7.2 Communication Templates

#### Incident Declared

```
🔴 [DR ACTIVATED] — {SCENARIO_NAME}

Severity: {P0/P1}
Started: {TIMESTAMP}
Impact: {SERVICES_AFFECTED}
Estimated users affected: ~{NUMBER}

Current status: {TEAM} is investigating.

Next update: {TIMESTAMP + 15min}

Channel: #dr-activation
Commander: @{NAME}
```

#### Customer-Facing Status Update

```
Subject: [Status Update] {INCIDENT_TITLE}

We are currently experiencing {DESCRIPTION} affecting {FEATURES}.
Our team has identified the issue and is working on a fix.

Current status: {INVESTIGATING / IDENTIFIED / MITIGATING / RESOLVED}

Started: {TIMESTAMP}
Estimated resolution: {ETA}

We apologize for the inconvenience and will provide another update
within {FREQUENCY}.

— TRUE STAR BD LIMITED Engineering
```

#### Post-Incident Summary

```
📋 [Post-Incident Summary] — {INCIDENT_ID}

Duration: {START} → {END} ({TOTAL_DURATION})
Root Cause: {SUMMARY}
Impact: {NUMBER} orders affected, {REVENUE_LOSS}
Action Items:
1. {ACTION_ITEM}
2. {ACTION_ITEM}
3. {ACTION_ITEM}

Postmortem: {LINK}
Scheduled: {DATE}
```

### 7.3 Escalation Matrix

| Level | Role | Contact | Response Time |
|-------|------|---------|---------------|
| Level 1 | On-call Engineer | PagerDuty | 5 min |
| Level 2 | Senior Engineer | PagerDuty + SMS | 15 min |
| Level 3 | Engineering Manager | Phone | 30 min |
| Level 4 | CTO | Phone | 60 min |
| Level 5 | CEO | Phone | Upon CTO escalation |

---

## 8. DR Drill Schedule

### 8.1 Drill Types and Frequency

| Drill Type | Frequency | Scope | Participants | Duration |
|------------|-----------|-------|-------------|----------|
| Tabletop exercise | Monthly | Specific scenario walkthrough | On-call team + SRE | 1 hour |
| Database restoration | Weekly | PITR to staging environment | DBA team | 2 hours |
| Component failover | Quarterly | Redis cluster failover, RDS failover | SRE team | 4 hours |
| Full DR failover | Bi-annual (April, October) | Full region failover to eu-west-1 | All engineering | 8 hours |
| Partial DR failover | Quarterly | Application + database (no search/queue) | Platform team | 4 hours |
| Backup restoration | Monthly | Restore from Glacier Deep Archive | DBA team | 4 hours |
| Security incident drill | Quarterly | Ransomware / breach simulation | Security + Engineering | 4 hours |

### 8.2 Bi-Annual Full DR Failover Drill

#### Pre-Drill (Week Before)

- [ ] Schedule drill window (announced 2 weeks in advance).
- [ ] Notify all stakeholders of expected impact.
- [ ] Set up monitoring dashboards for DR region.
- [ ] Verify DR region infrastructure matches production.
- [ ] Confirm all runbooks are up to date.
- [ ] Brief incident response team on drill objectives.

#### Drill Execution (Day Of)

```
09:00 — Drill begins. Incident Commander declares DR scenario.
09:05 — Communications team sends initial status update.
09:10 — Infrastructure team begins DR region activation.
09:30 — Database team promotes replica and validates.
09:45 — Application team verifies services in DR.
10:00 — Traffic routed to DR region via Route53.
10:15 — Full functional testing in DR region.
11:00 — Load test executes against DR region.
12:00 — Drill ends. Begin failback.
13:00 — Failback complete. Systems restored to primary.
13:30 — Post-drill retrospective.
```

#### Post-Drill Report

```markdown
# DR Drill Report — {DATE}

## Drill Details
- **Scenario**: {SCENARIO}
- **Duration**: {X} hours ({START} → {END})
- **Participants**: {COUNT} engineers

## Metrics
- Time to DR activation: {X} minutes
- Time to database ready: {X} minutes
- Time to application ready: {X} minutes
- Time to traffic routed: {X} minutes
- Time to full operations: {X} minutes
- RTO achieved: {X} hours (target: {Y})
- RPO achieved: {X} minutes (target: {Y})

## Issues Found
1. {Issue description} — {Severity} — {Action item}
2. {Issue description} — {Severity} — {Action item}

## Improvements
1. {Improvement}
2. {Improvement}

## Sign-off
- Incident Commander: {NAME}
- SRE Lead: {NAME}
- CTO: {NAME}
```

### 8.3 Drill Success Criteria

| Criterion | Target | Minimum Acceptable |
|-----------|--------|--------------------|
| RTO (Tier 0-1) | 1 hour | 2 hours |
| RPO (Tier 0-1) | 5 minutes | 15 minutes |
| Data integrity | 100% | 99.99% |
| Order processing | 100% | 95% |
| Search results | 100% | 90% |
| All tests passed | 100% | 80% critical tests |

---

## 9. Runbook Index

### 9.1 Runbook Structure

Each runbook follows this template and is stored in Confluence under "DR Runbooks":

```markdown
# Runbook: {RUNBOOK_ID} — {SCENARIO_NAME}

## Overview
- **Severity**: {P0/P1/P2}
- **System**: {SYSTEM_NAME}
- **Trigger**: {ALERT_NAME}

## Pre-Flight Checklist
- [ ] Step 1
- [ ] Step 2

## Procedure
### Step 1: {ACTION}
- Command: `{EXACT_COMMAND}`
- Expected output: `{EXPECTED_OUTPUT}`
- Verification: `{VERIFICATION_STEP}`
- On failure: `{ROLLBACK_STEP}`

### Step 2: {ACTION}
...

## Rollback Steps
- How to undo this procedure.

## Post-Recovery Verification
- [ ] Check 1
- [ ] Check 2

## Contact List
- DB Admin: @name
- Network Engineer: @name
- Application Owner: @name
```

### 9.2 Runbook List

| ID | Name | Linked Scenario | Complexity | Author |
|----|------|----------------|------------|--------|
| RB-001 | RDS Failover (Multi-AZ) | DR-003 | Low | DBA Team |
| RB-002 | Database PITR | DR-004 | Medium | DBA Team |
| RB-003 | Redis Cluster Recovery | DR-005 | Medium | SRE Team |
| RB-004 | Full Region Failover | DR-006 | High | SRE Team |
| RB-005 | Full Region Failback | DR-006 | High | SRE Team |
| RB-006 | Elasticsearch Snapshot Restore | DR-006 | Medium | SRE Team |
| RB-007 | RabbitMQ Recovery from Backup | DR-006 | Medium | SRE Team |
| RB-008 | S3 Accidental Deletion Recovery | DR-011 | Low | DevOps |
| RB-009 | Ransomware Containment & Recovery | DR-010 | High | Security Team |
| RB-010 | SSL Certificate Renewal | DR-012 | Low | DevOps |
| RB-011 | WAF & DDoS Mitigation | DR-009 | Medium | Security Team |
| RB-012 | Application Rollback (Blue/Green) | DR-008 | Low | Platform Team |

---

## 10. Continuous Improvement

### 10.1 Post-Incident Review Process

Every P0/P1 incident and every DR drill follows this process:

1. **Timeline reconstruction** — Gather all events, decisions, and actions.
2. **Root cause analysis** — 5 Whys or fishbone diagram.
3. **Action item generation** — Each item must be:
   - Specific, Measurable, Assignable, Realistic, Time-bound (SMART).
   - Categorized as: Prevention, Detection, Response, Recovery.
4. **Blameless culture** — Focus on system improvements, not individual errors.
5. **Report publication** — Shared with engineering within 48 hours.

### 10.2 Quarterly DR Review

| Agenda Item | Owner | Duration |
|-------------|-------|----------|
| Review last quarter's incidents | SRE Lead | 30 min |
| Review drill results | SRE Lead | 30 min |
| Update runbooks | Team leads | 30 min |
| Capacity planning for DR | Infra Lead | 30 min |
| Risk assessment update | Security Lead | 30 min |
| Action item follow-up | All | 30 min |

---

## Appendix A: Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| Incident Commander (Primary) | {Name} | {Phone} | {Email} |
| Incident Commander (Secondary) | {Name} | {Phone} | {Email} |
| DBA Lead | {Name} | {Phone} | {Email} |
| Security Lead | {Name} | {Phone} | {Email} |
| DevOps Lead | {Name} | {Phone} | {Email} |
| CTO | {Name} | {Phone} | {Email} |
| VP Engineering | {Name} | {Phone} | {Email} |

## Appendix B: Third-Party Support Contacts

| Service | Support Contact | SLA | Escalation |
|---------|----------------|-----|------------|
| AWS | Enterprise Support | 15 min P0 | TAM |
| Stripe | Premium Support | 10 min P0 | Account Manager |
| Cloudflare | Enterprise Support | 30 min P1 | CSM |
| Datadog/NewRelic | Standard Support | 1 hour P1 | — |

---

*Document Owner: Principal Architect*  
*Last Updated: 2026-07-01*  
*Review Cycle: Quarterly*  
*Next DR Drill: 2026-10-15 (Full Region Failover)*
