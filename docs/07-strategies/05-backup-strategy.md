# Backup Strategy

## 1. Backup Philosophy

The TRUE STAR BD LIMITED backup strategy follows the **3-2-1 rule**: three copies of data, on two different media types, with one copy off-site. Backups are automated, encrypted, regularly tested, and monitored with alerting on failures. All backups are designed to support point-in-time recovery with a maximum data loss window of 1 hour (RPO).

---

## 2. Backup Scope and Schedule

### 2.1 Overview

| Data Asset | Method | Frequency | Retention | RPO | RTO |
|------------|--------|-----------|-----------|-----|-----|
| PostgreSQL Database | pg_dump + WAL archiving | Full: Daily, WAL: Continuous | 30d daily, 12w weekly, 12m monthly | 1 hour | 4 hours |
| File Storage (S3) | Cross-region replication | Continuous | Same as source | 15 min | 1 hour |
| Application Config | Parameter Store + Git | On change | Git history | 0 | 30 min |
| Redis Cache | RDB snapshots | Every 6 hours | 7 days | 6 hours | 2 hours |
| Search Index (Elasticsearch) | Snapshot to S3 | Daily | 14 days | 24 hours | 4 hours |
| Message Queue (RabbitMQ) | Definitions export | On change | 30 days | N/A | 1 hour |

---

## 3. Database Backup

### 3.1 PostgreSQL Backup Architecture

```
                        ┌─────────────────────┐
                        │  PostgreSQL Primary    │
                        │  (us-east-1a)         │
                        └──────────┬────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                    │
     ┌─────────▼────────┐  ┌──────▼───────┐  ┌─────────▼────────┐
     │  WAL Archiving    │  │  pg_dump     │  │  Read Replica    │
     │  (continuous)     │  │  (daily)      │  │  (HA standby)    │
     │  → S3             │  │  → S3         │  │  (same region)   │
     └──────────────────┘  └──────────────┘  └──────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │          S3 Bucket            │
                    │  /backups/postgresql/         │
                    │    ├── full/                  │
                    │    ├── wal/                   │
                    │    └── logical/               │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    S3 CRR (Cross-Region      │
                    │    Replication) → eu-west-1  │
                    └─────────────────────────────┘
```

### 3.2 Full Backup (Daily)

```bash
# Full database backup script (pg_dump)
pg_dump \
  --host=${DB_HOST} \
  --port=5432 \
  --username=${DB_USER} \
  --dbname=${DB_NAME} \
  --format=directory \
  --jobs=4 \
  --compress=9 \
  --file=/backup/daily/${DB_NAME}_$(date +%Y%m%d_%H%M%S) \
  --no-owner \
  --no-acl \
  --verbose
```

- **Time**: 02:00 UTC daily (lowest traffic window for BD market: 08:00 AM BDT).
- **Method**: `pg_dump` in directory format (parallel, compressible).
- **Validation**: `pg_restore --list` verifies archive integrity immediately after dump.
- **Monitoring**: CloudWatch alarm fires if backup takes > 2 hours or fails.

### 3.3 Incremental Backup (WAL Archiving)

- **Method**: `archive_command` in `postgresql.conf` → `aws s3 cp %p s3://tsbl-backups/postgresql/wal/%f`.
- **Frequency**: Continuous — every WAL segment (16MB) archived immediately.
- **Segment Switch**: `archive_timeout = 300` (forces switch every 5 minutes if idle).
- **Compression**: WAL files compressed via `gzip` before upload (S3 server-side compression not recommended).
- **Monitoring**: `pg_stat_archiver` tracks archiving lag; alert if `last_failed_wal` is not null.

### 3.4 Point-in-Time Recovery (PITR)

```bash
# Restore to specific timestamp
pg_restore \
  --host=${TARGET_HOST} \
  --port=5432 \
  --username=${DB_USER} \
  --dbname=${DB_NAME} \
  --format=directory \
  --jobs=4 \
  --verbose \
  /backup/full/${LATEST_BACKUP}

# Apply WAL up to target time
# In recovery.conf:
restore_command = 'aws s3 cp s3://tsbl-backups/postgresql/wal/%f %p'
recovery_target_time = '2026-07-01 14:30:00 UTC'
recovery_target_action = 'promote'
```

- **RPO**: 1 hour (max loss = one WAL segment interval + archive_timeout).
- **Procedure**: Restore latest full backup → apply WAL files to target time → promote.
- **Testing**: Automated PITR test weekly on staging environment.

---

## 4. File Storage Backup

### 4.1 S3 Cross-Region Replication (CRR)

| Source Bucket | Source Region | Destination Bucket | Destination Region | Replication Scope |
|--------------|---------------|-------------------|--------------------|--------------------|
| `tsbl-production-media` | ap-southeast-1 | `tsbl-backup-media` | eu-west-1 | All objects |
| `tsbl-production-static` | ap-southeast-1 | `tsbl-backup-static` | eu-west-1 | All objects |
| `tsbl-backup-database` | ap-southeast-1 | `tsbl-backup-dr-eu` | eu-west-1 | All objects |

### 4.2 CRR Configuration

```json
{
  "ReplicationConfiguration": {
    "Role": "arn:aws:iam::123456789012:role/s3-crr-role",
    "Rules": [
      {
        "Status": "Enabled",
        "Priority": 1,
        "DeleteMarkerReplication": { "Status": "Disabled" },
        "Filter": {
          "Prefix": ""
        },
        "Destination": {
          "Bucket": "arn:aws:s3:::tsbl-backup-media",
          "StorageClass": "STANDARD_IA",
          "EncryptionConfiguration": {
            "ReplicaKmsKeyID": "arn:aws:kms:eu-west-1:..."
          }
        }
      }
    ]
  }
}
```

### 4.3 Replication Monitoring

| Metric | Target | Alert | Action |
|--------|--------|-------|--------|
| Replication lag | < 15 min | > 30 min | Check CRR status |
| Replication failure count | 0 | > 0 for 10 min | Check S3 replication metrics |
| Bytes pending | < 1 MB | > 100 MB | Investigate bandwidth or throttle |
| Replication time | < 60 min for 1 GB | > 4 hours | Review object size/count |

---

## 5. Application Configuration Backup

### 5.1 Infrastructure-as-Code

- **Terraform state**: Stored in S3 with DynamoDB locking — provides full infrastructure backup.
- **CloudFormation**: State stored in S3.
- **Application secrets**: AWS Secrets Manager / Parameter Store — automatically backed up via backup plan.

### 5.2 Configuration Backup Strategy

| Configuration | Source | Backup Method | Recovery RTO |
|--------------|--------|--------------|--------------|
| Environment variables | Parameter Store | Export to S3 weekly; versioning | 15 min |
| Django settings | Git repository | Always in version control | 5 min |
| Nginx/ALB configs | Terraform | Terraform state in S3 | 30 min |
| Docker Compose/K8s YAML | Git repository | Version control | 10 min |
| CI/CD pipeline config | Git repository | Version control | 10 min |

### 5.3 Parameter Store Export (Weekly)

```bash
# Export all parameters to S3
aws ssm get-parameters-by-path \
  --path "/tsbl/production/" \
  --recursive \
  --with-decryption \
  --region ap-southeast-1 \
  | jq '{Parameters: [.Parameters[] | {Name, Value, Type}]}' \
  | aws s3 cp - "s3://tsbl-backup-configs/ssm-params/$(date +%Y%m%d).json"
```

---

## 6. Backup Retention Policy

### 6.1 PostgreSQL

| Backup Type | Retention | Quantity | Storage Needed |
|-------------|-----------|----------|----------------|
| Daily full | 30 days | 30 backups | ~30 × 5 GB = 150 GB |
| Weekly full | 12 weeks | 12 backups | ~12 × 5 GB = 60 GB |
| Monthly full | 12 months | 12 backups | ~12 × 5 GB = 60 GB |
| WAL files | 7 days | Continuous | ~7 × 15 GB = 105 GB/day |
| Logical dump | 30 days | 30 backups | ~30 × 3 GB = 90 GB |

### 6.2 S3 Lifecycle Policy

```json
{
  "Rules": [
    {
      "Id": "DailyBackupRetention",
      "Status": "Enabled",
      "Filter": { "Prefix": "backups/postgresql/full/" },
      "Expiration": { "Days": 30 }
    },
    {
      "Id": "WeeklyBackupRetention",
      "Status": "Enabled",
      "Filter": { "Prefix": "backups/weekly/" },
      "Expiration": { "Days": 84 }
    },
    {
      "Id": "MonthlyBackupRetention",
      "Status": "Enabled",
      "Filter": { "Prefix": "backups/monthly/" },
      "Expiration": { "Days": 365 }
    },
    {
      "Id": "WALRetention",
      "Status": "Enabled",
      "Filter": { "Prefix": "backups/postgresql/wal/" },
      "Expiration": { "Days": 7 }
    }
  ]
}
```

### 6.3 Long-Term Archive

| Archive Tier | Duration | Storage | Cost/GB/Month |
|-------------|----------|---------|---------------|
| S3 Standard | 0–30 days | SSD | $0.023 |
| S3 Standard-IA | 31–90 days | HDD | $0.0125 |
| S3 Glacier Instant | 91–365 days | Flash-optimized | $0.004 |
| S3 Glacier Deep Archive | 1–7 years | Tape-equivalent | $0.00099 |

---

## 7. Backup Encryption

### 7.1 Encryption at Rest

| Layer | Method | Key Management |
|-------|--------|---------------|
| S3 buckets | AES-256 (SSE-S3 or SSE-KMS) | AWS KMS (managed) |
| pg_dump files | GPG symmetric encryption | Master key in Secrets Manager |
| WAL files | Gzip + GPG | Key rotated every 90 days |
| Redis RDB | Encrypted EBS volume | AWS KMS |
| Elasticsearch snapshots | SSE-S3 | AWS S3 managed |

### 7.2 Encryption in Transit

- **S3 uploads**: TLS 1.2+ (HTTPS) enforced via bucket policy.
- **Cross-region replication**: TLS 1.2+ between regions.
- **Database backup pipeline**: Encrypted tunnel through private network.
- **Certificate validation**: All backup endpoints validated against internal CA.

### 7.3 Key Rotation Policy

| Key Type | Rotation Interval | Automated? |
|----------|------------------|-----------|
| KMS Customer Master Key | Annual | Yes (manual) |
| GPG passphrase | 90 days | Yes (Secrets Manager + rotation Lambda) |
| Database backup user password | 90 days | Yes (via IAM database auth) |
| SSH keys (bastion) | 180 days | Yes (Automation) |

---

## 8. Backup Verification and Restoration Testing

### 8.1 Verification Types

| Type | Frequency | Method | Scope |
|------|-----------|--------|-------|
| Integrity check | Daily (post-backup) | `pg_restore --list` | Full backups |
| Checksum verification | Daily | MD5 checksum of S3 objects | All backup files |
| Restoration drill (staging) | Weekly | Full PITR to staging environment | Database |
| Restoration drill (production) | Monthly | Cross-region restore to DR environment | Database + files |
| DR failover test | Quarterly | Full failover to DR region | Entire system |
| Encryption key test | Monthly | Decrypt with backup key | Verify key usability |

### 8.2 Restoration Test Process (Weekly)

```bash
#!/bin/bash
# Weekly restoration test script
# Run on staging environment

# 1. Download latest daily backup
aws s3 cp s3://tsbl-backups/postgresql/full/latest/ /tmp/restore/ --recursive

# 2. Verify integrity
pg_restore --list /tmp/restore/ > /dev/null
if [ $? -ne 0 ]; then
    echo "Backup integrity check FAILED" | slack-notify --channel "#backup-alerts"
    exit 1
fi

# 3. Restore to staging database
dropdb tsbl_staging
createdb tsbl_staging
pg_restore --dbname=tsbl_staging --jobs=4 /tmp/restore/

# 4. Run data validation queries
psql tsbl_staging -c "
    SELECT COUNT(*) as total_orders FROM orders;
    SELECT COUNT(*) as total_users FROM users;
    SELECT MAX(created_at) as newest_order FROM orders;
"

# 5. Check for data corruption
psql tsbl_staging -c "SELECT count(*) FROM pg_catalog.pg_stat_all_tables WHERE n_live_tup = 0;"

# 6. Report results
echo "Weekly restoration test COMPLETED" | slack-notify --channel "#backup-alerts"
```

### 8.3 Data Integrity Validation

| Check | Query | Expected | Action on Failure |
|-------|-------|----------|-------------------|
| Row count consistency | `COUNT(*)` on critical tables | Match production (within 1%) | Investigate discrepancy |
| Referential integrity | Custom FK check query | Zero orphaned records | Restore from previous day |
| Sequence consistency | `nextval` matches `max(id)+1` | All sequences aligned | Reset sequences |
| Timestamp sanity | `MAX(created_at)` | Within 24 hours | Check WAL archiving |
| Index validation | `pg_integrity_check` | All indexes valid | Reindex |

---

## 9. Automated Backup Scheduling

### 9.1 AWS Backup Plan

| Resource | Backup Plan | Rule Name | Schedule | Lifecycle |
|----------|-------------|-----------|----------|-----------|
| PostgreSQL | `tsbl-db-backup` | daily-full | Cron(0 2 * * ? *) | 30d → S3 IA → 90d → Glacier |
| PostgreSQL | `tsbl-db-backup` | weekly-full | Cron(0 2 * * 0 *) | 84d → S3 IA → 365d → Glacier |
| PostgreSQL | `tsbl-db-backup` | monthly-full | Cron(0 2 1 * ? *) | 365d → Glacier |
| EC2 (bastion) | `tsbl-ec2-backup` | daily-ami | Cron(0 3 * * ? *) | 7d |
| EBS volumes | `tsbl-ebs-backup` | daily-snap | Cron(0 4 * * ? *) | 14d |

### 9.2 Script Automation (Cron)

```bash
# /etc/cron.d/tsbl-backups

# PostgreSQL full backup (daily 02:00 UTC)
0 2 * * * backup_user /usr/local/bin/backup-postgresql-full.sh >> /var/log/backup.log 2>&1

# WAL archive health check (every 15 minutes)
*/15 * * * * backup_user /usr/local/bin/check-wal-archiving.sh >> /var/log/wal-check.log 2>&1

# Backup to S3 Glacier transition (daily 04:00)
0 4 * * * backup_user /usr/local/bin/apply-s3-lifecycle.sh >> /var/log/lifecycle.log 2>&1

# Weekly restoration test (Sunday 06:00 UTC)
0 6 * * 0 backup_user /usr/local/bin/test-restore.sh >> /var/log/restore-test.log 2>&1

# Monthly backup report (1st of month 07:00)
0 7 1 * * backup_user /usr/local/bin/generate-backup-report.sh
```

### 9.3 Failure Notifications

| Event | Channel | Response |
|-------|---------|----------|
| Backup failure | `#backup-alerts` (Slack) + PagerDuty | Investigate within 15 min |
| Restoration test failure | `#backup-alerts` + email | Investigate within 1 hour |
| WAL archiving lag > 30 min | PagerDuty (P2) | Check pg_stat_archiver |
| S3 CRR failure | `#backup-alerts` | Check S3 metrics |
| Encryption key expiry < 30 days | Email to DevOps team | Rotate key |

---

## 10. Off-Site Backup Strategy

### 10.1 Geographic Distribution

| Location | Region | Contents | Purpose |
|----------|--------|----------|---------|
| Primary | ap-southeast-1 (Singapore) | Live production data | Primary operations |
| Warm DR | eu-west-1 (Ireland) | S3 CRR replicas + database backups | Regional disaster |
| Cold Archive | us-east-1 (N. Virginia) | Monthly backups via S3 CRR | Multi-region resilience |

### 10.2 Off-Site Recovery Options

| Scenario | Restore From | Expected RTO | Expected RPO |
|----------|-------------|--------------|--------------|
| Database corruption (logical) | Daily full + WAL in S3 | 4 hours | 1 hour |
| Full region outage | S3 CRR in eu-west-1; spin up new DB | 8 hours | 1 hour |
| Accidental data deletion | S3 versioning (30-day window) | 30 min | 5 min |
| Ransomware attack | Glacier Deep Archive (7-year retention) | 12 hours | 24 hours |

### 10.3 Versioning as Backup

S3 versioning is enabled on all bucket levels:

| Bucket | Versioning Status | Delete Marker | Noncurrent Days | Action |
|--------|-------------------|---------------|-----------------|--------|
| `tsbl-production-media` | Enabled | Keep 30d | 30d → Glacier | Protection against accidental delete |
| `tsbl-backup-database` | Enabled | Keep 7d | 7d → Delete | Prevent backup accumulation |
| `tsbl-backups-eu` | Enabled | Keep 90d | 90d → Deep Archive | Long-term retention |

### 10.4 MFA Delete Protection

- **Enabled on**: `tsbl-backup-database`, `tsbl-backups-eu`, `tsbl-backup-configs`.
- **Effect**: All delete operations require MFA token — prevents accidental or malicious deletion.
- **Exceptions**: Lifecycle policy — does not require MFA.

---

## 11. Backup Cost Management

### 11.1 Estimated Monthly Costs

| Backup Type | Monthly Storage | Monthly Cost |
|-------------|----------------|--------------|
| PostgreSQL full (S3 Standard) | 150 GB | $3.45 |
| PostgreSQL WAL (S3 Standard) | 105 GB | $2.42 |
| PostgreSQL weekly (S3 IA) | 60 GB | $0.75 |
| PostgreSQL monthly (Glacier) | 60 GB | $0.24 |
| S3 CRR (data transfer) | Variable | ~$10 |
| S3 CRR (storage in eu-west-1) | ~300 GB | $6.90 |
| Config backups | 5 GB | $0.12 |
| **Total estimated monthly** | | **~$23.88** |

### 11.2 Cost Optimization

- **Lifecycle policies**: Transition cold data to cheaper storage tiers automatically.
- **Deduplication**: Full backups compressed at level 9, average 70% reduction.
- **Incremental after full**: WAL archiving is inherently incremental — no redundant data.
- **Cleanup**: Stale backups deleted per policy; no orphaned resources.

---

## 12. Implementation Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| Week 1-2 | Foundation | Automated pg_dump + WAL archiving to S3 |
| Week 3-4 | S3 Configuration | CRR setup, lifecycle policies, versioning |
| Week 5-6 | Encryption | GPG key setup, KMS configuration, Secrets Manager |
| Week 7-8 | Automation | Cron jobs, AWS Backup plans, CloudWatch alarms |
| Week 9-10 | Testing | Weekly restoration test automation, validation queries |
| Week 11-12 | Documentation | Runbooks for restore procedures, incident response |

---

*Document Owner: Principal Architect*  
*Last Updated: 2026-07-01*  
*Review Cycle: Quarterly*
