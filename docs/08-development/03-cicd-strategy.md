# CI/CD Strategy

## TRUE STAR BD LIMITED — Digital Marketplace Platform

| Document ID | DEV-TSBL-003 |
|---|---|
| Version | 1.0 |
| Date | July 1, 2026 |
| Author | Software Architecture Division |
| Status | Approved |
| Classification | Internal — Confidential |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Pipeline Architecture Overview](#2-pipeline-architecture-overview)
3. [CI Pipeline Stages](#3-ci-pipeline-stages)
4. [CD Pipeline Stages](#4-cd-pipeline-stages)
5. [GitHub Actions Configuration Approach](#5-github-actions-configuration-approach)
6. [Docker Image Build and Push Pipeline](#6-docker-image-build-and-push-pipeline)
7. [Automated Testing in CI](#7-automated-testing-in-ci)
8. [Security Scanning](#8-security-scanning)
9. [Deployment Approval Gates](#9-deployment-approval-gates)
10. [Environment Promotion Workflow](#10-environment-promotion-workflow)
11. [Rollback Automation](#11-rollback-automation)
12. [Artifact Versioning and Storage](#12-artifact-versioning-and-storage)

---

## 1. Introduction

This document defines the Continuous Integration and Continuous Deployment (CI/CD) strategy for the TRUE STAR BD LIMITED Digital Marketplace Platform. The pipeline is designed to enforce quality gates at every stage, ensure secure and reliable deployments, and enable rapid, auditable delivery of value to production.

### 1.1 Key Principles

| Principle | Description |
|---|---|
| **Fail fast** | The pipeline terminates at the first failing stage. Immediate feedback to the developer. |
| **Immutable artifacts** | Every build produces a versioned, immutable artifact that is promoted across environments without rebuilding. |
| **Security by default** | Security scanning is integrated at every stage, not bolted on at the end. |
| **Auditability** | Every deployment is traceable to a commit, a PR, a build artifact, and an approver. |
| **Idempotent deployments** | Deploying the same artifact twice produces the same result. |

### 1.2 CI/CD Platform

| Component | Tool |
|---|---|
| CI/CD Engine | GitHub Actions (primary) |
| Container Registry | GitHub Container Registry (ghcr.io) |
| Artifact Storage | GitHub Actions Artifacts (short-term) + S3-compatible storage (long-term) |
| Secret Management | GitHub Actions Secrets + HashiCorp Vault |
| Deployment Target | Kubernetes (via kubectl / Helm) |
| IaC | Terraform + Helm charts |

---

## 2. Pipeline Architecture Overview

### 2.1 High-Level Pipeline Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Developer  │───▶│    CI       │───▶│    CD       │───▶│ Production  │
│   Push Code  │    │  Pipeline   │    │  Pipeline   │    │             │
└─────────────┘    └──────┬──────┘    └──────┬──────┘    └─────────────┘
                          │                  │
                          ▼                  ▼
                   ┌──────────────┐  ┌──────────────┐
                   │  Unit Tests  │  │  Deploy to   │
                   │  Lint, Type  │  │  Staging     │
                   │  SAST, Build │  │  E2E Tests   │
                   │  Container   │  │  Approve     │
                   │              │  │  Deploy Prod │
                   └──────────────┘  └──────────────┘
```

### 2.2 Pipeline Triggers

| Trigger | Pipeline | Target Environment |
|---|---|---|
| Push to feature/bugfix/chore branch | CI only | None |
| Push to `main` | CI + CD | Staging (auto) |
| Push to `release/v*` | CI + CD | Staging (auto) |
| Tag push `v*` | CI + CD | Production (auto) |
| PR opened/synchronized | CI only | None (status check) |
| Schedule (nightly) | CI + Security scan | None |
| Manual dispatch | CI + CD (with approval) | Any |

---

## 3. CI Pipeline Stages

### 3.1 Stage Definitions

Every push to any branch triggers the CI pipeline. The pipeline consists of the following sequential stages:

```
┌──────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
│ Lint │─▶│ Type    │─▶│ Unit      │─▶│ Build    │─▶│ Scan │─▶│ Package │─▶│ Report │
│      │  │ Check   │  │ Test      │  │          │  │      │  │ Image   │  │        │
└──────┘  └──────────┘  └──────────┘  └──────────┘  └──────┘  └──────────┘  └────────┘
```

### 3.2 Stage Details

#### 3.2.1 Stage 1: Lint

| Step | Tool | Command |
|---|---|---|
| Python lint | Ruff | `ruff check app/ tests/` |
| Python format | Ruff | `ruff format --check app/ tests/` |
| TypeScript lint | ESLint | `pnpm run lint` |
| TypeScript format | Prettier | `pnpm run format:check` |
| Commit message | commitlint | `commitlint --from HEAD~1 --to HEAD` |
| YAML lint | yamllint | `yamllint .github/` |

**Failure behavior:** Pipeline terminates immediately with a clear error message indicating the file, line, and rule violated.

#### 3.2.2 Stage 2: Type Check

| Step | Tool | Command |
|---|---|---|
| Python types | mypy | `mypy app/ --strict` |
| TypeScript types | tsc | `tsc --noEmit --strict` |
| Pydantic v2 | pydantic | `pydantic anal` (optional validation) |

**Failure behavior:** Pipeline terminates. Type errors are blocking.

#### 3.2.3 Stage 3: Unit Test

| Step | Tool | Command |
|---|---|---|
| Python backend | pytest | `pytest tests/unit/ --cov=app --cov-fail-under=85 -v` |
| TypeScript frontend | Vitest | `vitest run --coverage --threshold=75` |

**Failure behavior:** Pipeline terminates on test failure or coverage below threshold.

#### 3.2.4 Stage 4: Build

| Step | Tool | Command |
|---|---|---|
| Backend Docker image | Docker | `docker build -t backend -f docker/Dockerfile.backend .` |
| Frontend static build | Vite | `pnpm run build` |
| Migration check | Alembic | `alembic check` (detect schema drift) |

**Failure behavior:** Pipeline terminates if build fails or migration check detects drift.

#### 3.2.5 Stage 5: Security Scan

| Step | Tool | Command |
|---|---|---|
| Python SAST | Bandit | `bandit -r app/ --confidence-level=medium` |
| Python dependencies | safety | `safety check` |
| JS/TS dependencies | npm audit | `pnpm audit --audit-level=high` |
| Container scan | Trivy | `trivy image --severity HIGH,CRITICAL backend:latest` |
| IaC scan | Checkov | `checkov -d terraform/` |
| Secret leak | Gitleaks | `gitleaks detect --source .` |

**Failure behavior:** Pipeline terminates on any CRITICAL or HIGH severity finding. MEDIUM findings are warnings only but require a ticket to resolve.

#### 3.2.6 Stage 6: Package Image

| Step | Description |
|---|---|
| Build production image | Multi-stage Docker build with non-root user |
| Tag image | `ghcr.io/tsbl/{service}:{sha}-{timestamp}` |
| Push to registry | Push to GitHub Container Registry |
| Generate SBOM | Syft generates SPDX JSON SBOM attached to image |
| Sign image | Cosign signs the image for supply chain integrity |

**Failure behavior:** Package failure terminates pipeline. Image is not pushed if signing fails.

#### 3.2.7 Stage 7: Report

| Step | Description |
|---|---|
| Test report | Publish JUnit XML report to GitHub Actions Summary |
| Coverage report | Publish HTML coverage report as CI artifact |
| SBOM attachment | Attach SBOM to GitHub release (if tag push) |
| Slack notification | Notify #ci-cd channel on failure |

---

## 4. CD Pipeline Stages

### 4.1 Deploy to Staging (Automatic)

Triggered by: Push to `main` or `release/v*`.

```
┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Deploy to  │─▶│ Integration  │─▶│ Smoke Tests  │─▶│ Health Check │
│ Staging    │  │ Tests       │  │              │  │              │
└────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

| Stage | Description | Tool | Success Criteria |
|---|---|---|---|
| Deploy to staging | Helm upgrade or kubectl apply | Helm | Pods ready in 120s |
| Integration tests | Tests against staging API with test DB | pytest + httpx | All pass |
| Smoke tests | Critical path validation (login, browse, purchase) | Playwright | All pass |
| Health check | Verify `/health`, `/ready`, `/metrics` endpoints | curl + promtool | 200 OK |

### 4.2 Deploy to Production (Manual Approval + Tag)

Triggered by: Tag push `v*` (after CI passes on the tag commit).

```
┌────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Approval Gate  │─▶│ Deploy Canary│─▶│ Deploy Prod  │─▶│ Post-Deploy  │
│ (Manual)       │  │ (10% traff)  │  │ (100% traff) │  │ Verification │
└────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

| Stage | Description | Approval Required |
|---|---|---|
| Approval gate | Deployment approver reviews release notes, checks staging results | Tech Lead + QA Lead |
| Deploy canary | 10% production traffic routed to new version | Automatic after approval |
| Canary observation | Monitor error rates, latency, business metrics (15 min) | Automatic (threshold-based) |
| Deploy full | Gradual rollout to 25% → 50% → 100% | Automatic (if canary healthy) |
| Post-deploy verify | Run production smoke tests, verify metrics | Automatic |

---

## 5. GitHub Actions Configuration Approach

### 5.1 Workflow Structure

The repository uses a modular workflow structure with reusable components:

```
.github/
  workflows/
    ci.yml                    # Main CI workflow (lint → test → build → scan)
    cd-staging.yml            # Deploy to staging
    cd-production.yml         # Deploy to production (tag-triggered)
    security-scan-nightly.yml # Nightly full security scan
    dependency-update.yml     # Dependabot / Renovate automation
  actions/
    setup-python/action.yml   # Reusable Python setup
    setup-node/action.yml     # Reusable Node.js setup
    docker-build/action.yml   # Reusable Docker build + push
    deploy-helm/action.yml    # Reusable Helm deployment
```

### 5.2 CI Workflow (ci.yml)

```yaml
name: CI
on:
  push:
    branches: [main, 'release/v*', 'feature/**', 'bugfix/**', 'hotfix/**']
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python
      - uses: ./.github/actions/setup-node
      - run: ruff check app/ tests/
      - run: ruff format --check app/ tests/
      - run: pnpm run lint
      - run: pnpm run format:check

  type-check:
    needs: lint
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python
      - uses: ./.github/actions/setup-node
      - run: mypy app/ --strict
      - run: tsc --noEmit --strict

  unit-test:
    needs: type-check
    runs-on: ubuntu-22.04
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: tsbl_test
        options: >-
          --health-cmd "pg_isready -U test"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python
      - uses: ./.github/actions/setup-node
      - run: pytest tests/unit/ --cov=app --cov-fail-under=85 -v --junitxml=report.xml
      - run: vitest run --coverage
      - uses: dorny/test-reporter@v1
        if: always()
        with:
          name: pytest-results
          path: report.xml
          reporter: java-junit

  build-and-scan:
    needs: unit-test
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/docker-build
        with:
          image-name: ${{ github.repository }}/backend
          dockerfile: docker/Dockerfile.backend
      - run: trivy image --severity HIGH,CRITICAL --exit-code 1 ${{ github.repository }}/backend:${{ github.sha }}
      - run: bandit -r app/ --confidence-level=medium --format=json --output=bandit.json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json

  package:
    needs: build-and-scan
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/') || startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-22.04
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/docker-build
        with:
          image-name: ghcr.io/tsbl/backend
          push: true
          tag: ${{ github.sha }}
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/tsbl/backend@${{ steps.digest.outputs.digest }}
```

### 5.3 Workflow Optimization

| Optimization | Implementation |
|---|---|
| Dependency caching | `actions/cache` for pip cache, pnpm store, Docker layers |
| Concurrency control | `concurrency.cancel-in-progress: true` — cancels stale runs on same branch |
| Conditional stages | `if:` conditions to skip package/deploy on non-target branches |
| Matrix builds | Matrix strategy for Python 3.12 and Node 20 across services |
| Timeouts | `timeout-minutes: 10` per job to prevent runaway pipelines |

---

## 6. Docker Image Build and Push Pipeline

### 6.1 Dockerfile Standards

All Docker images MUST follow these standards:

- **Multi-stage builds:** Separate build stage and runtime stage.
- **Non-root user:** Run as `USER 10001` (non-root) in production images.
- **Minimal base images:** Python `slim` or `alpine` variants; Node.js `slim`.
- **Layer optimization:** Combine `RUN` commands; order layers by change frequency (least-changed first).
- **Healthcheck:** Define `HEALTHCHECK` instruction.
- **Labels:** Include org.opencontainers.image labels for provenance.

```dockerfile
# docker/Dockerfile.backend
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

COPY app/ app/
RUN poetry build

FROM python:3.12-slim AS runtime

WORKDIR /app
RUN addgroup --system --gid 10001 app && \
    adduser --system --uid 10001 --gid 10001 app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/dist/ ./dist/
RUN pip install dist/*.whl

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Image Tagging Strategy

| Tag Pattern | Applied When | Example |
|---|---|---|
| `{sha}` | Every push to `main` | `abc123def456` |
| `{version}` | Tag push `v*` | `1.4.0` |
| `latest` | Latest `main` build | `latest` |
| `staging` | Latest staging deployment | `staging` |
| `v{major}.{minor}.{patch}-rc.{n}` | Release candidate | `1.4.0-rc.1` |

### 6.3 Image Retention Policy

| Registry | Retention Policy |
|---|---|
| ghcr.io | Keep last 50 tagged versions; keep all version tags (v*); delete untagged images after 30 days |
| Staging | Keep last 10 images |
| Production | Keep all production images indefinitely (audit requirement) |

---

## 7. Automated Testing in CI

### 7.1 Test Execution Matrix

| Test Type | CI Stage | Frequency | Database Required? | External Services? |
|---|---|---|---|---|
| Unit tests | `unit-test` | Every push | No (mocked) | No |
| Integration tests | `cd-staging` | `main` / `release/*` push | Yes (test DB) | Mocked |
| E2E tests | `cd-staging` | `main` / `release/*` push | Yes (test DB) | Sandbox gateways |
| Performance tests | Scheduled (weekly) | Nightly Sunday | Yes (staging DB) | Sandbox |
| Security tests | `build-and-scan` + nightly | Every push + nightly | No | No |

### 7.2 Test Parallelization

- Python tests: `pytest-xdist` with `-n auto` for CPU core utilization.
- TypeScript tests: Vitest worker threads with `pool: 'threads'`.
- E2E tests: Playwright sharding across 4 parallel workers.
- Integration tests: Run sequentially within their module to avoid DB conflicts.

### 7.3 Test Database for CI

```yaml
services:
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: tsbl_test
    ports:
      - 5432:5432
    options: >-
      --health-cmd "pg_isready -U test"
      --health-interval 10s --health-timeout 5s --health-retries 5
```

Migrations are applied at the start of the test job:

```bash
alembic upgrade head
```

Test data is cleaned between test runs using truncation, not DROP/CREATE (for speed).

---

## 8. Security Scanning

### 8.1 Scanning Tools and Schedule

| Scan Type | Tool | Frequency | Runner | Failure Threshold |
|---|---|---|---|---|
| SAST (Python) | Bandit | Every push | CI | No HIGH or CRITICAL |
| SAST (Terraform) | Checkov | Every push | CI | No HIGH or CRITICAL |
| Dependency (Python) | safety | Every push | CI | No known vulnerabilities |
| Dependency (JS) | npm audit | Every push | CI | No HIGH or CRITICAL |
| Container scan | Trivy | Every push | CI | No HIGH or CRITICAL |
| Secret detection | Gitleaks | Every push | CI | Any finding |
| DAST | OWASP ZAP | Nightly (staging) | Scheduled | No HIGH or CRITICAL |
| Dependency (full) | Snyk / Dependabot | Daily | Scheduled | MEDIUM+ patched in 14 days |
| License compliance | FOSSA | Weekly | Scheduled | Copyleft licenses flagged |

### 8.2 Vulnerability Remediation SLA

| CVSS Score | Severity | Remediation SLA |
|---|---|---|
| 9.0 – 10.0 | CRITICAL | 24 hours |
| 7.0 – 8.9 | HIGH | 7 days |
| 4.0 – 6.9 | MEDIUM | 30 days |
| 0.1 – 3.9 | LOW | Next release cycle |

### 8.3 Fail/Pass Logic

```yaml
# Trivy scan with multiple severities
- name: Scan container image
  run: |
    trivy image \
      --severity CRITICAL,HIGH,MEDIUM \
      --exit-code 0 \
      --format sarif \
      --output trivy-results.sarif \
      ghcr.io/tsbl/backend:${{ github.sha }}

    # Fail only on CRITICAL and HIGH
    trivy image \
      --severity CRITICAL,HIGH \
      --exit-code 1 \
      ghcr.io/tsbl/backend:${{ github.sha }}
```

---

## 9. Deployment Approval Gates

### 9.1 Gate Definitions

| Gate | Environment | Approver | Method | Conditions |
|---|---|---|---|---|
| Staging deploy | Staging | Automatic | CI trigger | CI must pass on `main` or `release/v*` |
| Staging E2E pass | Staging | Automatic | CI | All E2E tests pass on staging |
| Staging QA sign-off | Staging | QA Lead | GitHub Environments | Manual check on staging deployment |
| Production approval | Production | Tech Lead + QA Lead | GitHub Environments | Release notes reviewed, staging green |
| Canary observation | Production | Automatic | Metrics-based | Error rate < 0.1%, p95 latency < 500ms |
| Production rollout | Production | Automatic | Progressive | 25% → 50% → 100% at 5-min intervals |

### 9.2 GitHub Environments Configuration

```yaml
# .github/workflows/cd-production.yml
deploy-production:
  runs-on: ubuntu-22.04
  environment:
    name: production
    url: https://app.tsbl.com
  steps:
    - uses: actions/checkout@v4
    - name: Deploy to production
      run: |
        helm upgrade --install tsbl ./helm \
          --namespace production \
          --set image.tag=${{ github.ref_name }} \
          --atomic \
          --timeout 5m
```

### 9.3 Emergency Deploy Bypass

In critical production incidents (P0), the approval gate for hotfixes can be bypassed:

- **Process:** Tech Lead posts in #incidents channel with the hotfix PR link.
- **Approval:** 1 senior engineer (instead of the usual 2).
- **Post-deploy:** A postmortem is filed within 24 hours.
- **Audit:** Bypass is logged in the deployment audit trail.

---

## 10. Environment Promotion Workflow

### 10.1 Environment Definitions

| Environment | Kubernetes Namespace | URL | DB | Redis | External Services |
|---|---|---|---|---|---|
| `development` | `dev` | dev.tsbl.com | Dev snapshot | Dev instance | Sandbox |
| `staging` | `staging` | staging.tsbl.com | Anonymized prod copy | Staging instance | Sandbox |
| `production` | `production` | app.tsbl.com | Production | Production cluster | Live gateways |

### 10.2 Promotion Flow

```
[Feature Branch] ──CI──▶ [Docker Image:sha]
                               │
                               ▼
     ╔══════════════════════════╗
     ║       Staging            ║  ← Automatic: push to main/release/*
     ║  - Integration tests     ║
     ║  - E2E tests             ║
     ║  - QA validation         ║
     ╚══════════════════════════╝
               │
               ▼ (Approval Gate)
     ╔══════════════════════════╗
     ║    Canary (10%)          ║  ← Tag push v*
     ║  - 15 min observation    ║
     ║  - Error budget check    ║
     ╚══════════════════════════╝
               │
               ▼ (Auto-promote)
     ╔══════════════════════════╗
     ║    Production (100%)     ║
     ║  - Gradual rollout       ║
     ║  - Post-deploy smoke     ║
     ╚══════════════════════════╝
```

### 10.3 Promotion Rule

- The **same artifact** is promoted across environments. Never rebuild for different environments.
- Artifact URL: `ghcr.io/tsbl/backend:{sha}` is identical across dev, staging, and production.
- Environment-specific configuration is injected via Helm values, not baked into the image.

---

## 11. Rollback Automation

### 11.1 Rollback Triggers

A rollback is automatically initiated when the following conditions are met during or after deployment:

| Condition | Detection | Action |
|---|---|---|
| Pod startup failure | Kubernetes liveness/readiness probe | Helm rollback --recreate-pods |
| Error rate spike (> 1% 5xx) | Prometheus + Alertmanager | Automatic rollback |
| p95 latency increase > 100% | Prometheus + Alertmanager | Automatic rollback |
| Business metric drop (e.g., orders/min < 50% of baseline) | Custom metric | Automatic rollback |
| Manual rollback command | Engineer runs `rollback.sh` | Helm rollback to previous revision |

### 11.2 Rollback Script

```bash
#!/usr/bin/env bash
# rollback.sh — Rollback to previous Helm revision
set -euo pipefail

NAMESPACE="${1:-production}"
RELEASE="tsbl"

echo "Initiating rollback in namespace: $NAMESPACE"

# Get current and previous revision
CURRENT_REVISION=$(helm history "$RELEASE" -n "$NAMESPACE" -o json | jq '.[-1].revision')
PREVIOUS_REVISION=$((CURRENT_REVISION - 1))

echo "Rolling back from revision $CURRENT_REVISION to revision $PREVIOUS_REVISION"

# Perform rollback
helm rollback "$RELEASE" "$PREVIOUS_REVISION" \
  --namespace "$NAMESPACE" \
  --timeout 5m \
  --wait \
  --recreate-pods

# Verify health
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=3m

echo "Rollback to revision $PREVIOUS_REVISION completed successfully"
```

### 11.3 Rollback Safety

- **Database rollbacks:** Schema migrations are backward-compatible for one release. A rollback does not revert database schema; it reverts application code that works with the existing (or previous) schema.
- **Data integrity:** Rolling back does not revert data changes (orders, payments). Business process correction (refunds, adjustments) is handled outside the deployment pipeline.
- **Feature flags:** Rollback via feature flags (disable the feature) is preferred over code rollback when possible. Use code rollback only when feature flags are insufficient.

### 11.4 Rollback Testing

Rollback procedures are tested:
- Monthly in staging (automated chaos engineering).
- Before every major release (manual drill).
- Documented in the runbook stored at `docs/runbooks/rollback.md`.

---

## 12. Artifact Versioning and Storage

### 12.1 Artifact Types

| Artifact | Format | Retention | Storage Location |
|---|---|---|---|
| Docker image | OCI (tar.gz) | Per retention policy (Section 6.3) | ghcr.io |
| SBOM | SPDX JSON | 1 year | ghcr.io (attached) + S3 glacier |
| Test reports | JUnit XML | 90 days | GitHub Actions Artifacts |
| Coverage reports | HTML | 90 days | GitHub Actions Artifacts |
| Build logs | Plain text | 90 days | GitHub Actions |
| Helm chart | tar.gz | Indefinitely (versioned in repo) | Git repository |
| Terraform plan | JSON | 30 days | S3 (state bucket) |

### 12.2 Versioning Convention

```
{artifact-type}/{service}/{version}-{build-metadata}
```

Examples:
```
docker/tsbl-backend/v1.4.0
sbom/tsbl-backend/v1.4.0.spdx.json
helm/tsbl-backend-1.4.0.tgz
```

### 12.3 Artifact Cleanup Policy

| Artifact | Age | Action |
|---|---|---|
| Stale Docker images (no tag) | > 30 days | Delete |
| Staging Docker images | > 10 deployments | Delete |
| CI artifacts | > 90 days | Delete |
| SBOMs | > 1 year | Archive to S3 Glacier |
| Build logs | > 90 days | Delete (automated by GitHub) |

---

*End of Document — DEV-TSBL-003*
