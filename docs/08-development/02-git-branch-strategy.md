# Git Branch Strategy

## TRUE STAR BD LIMITED — Digital Marketplace Platform

| Document ID | DEV-TSBL-002 |
|---|---|
| Version | 1.0 |
| Date | July 1, 2026 |
| Author | Software Architecture Division |
| Status | Approved |
| Classification | Internal — Confidential |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Branching Model Selection](#2-branching-model-selection)
3. [Branch Naming Conventions](#3-branch-naming-conventions)
4. [Main Branches](#4-main-branches)
5. [Feature Branch Workflow](#5-feature-branch-workflow)
6. [Release Branch Workflow](#6-release-branch-workflow)
7. [Hotfix Branch Workflow](#7-hotfix-branch-workflow)
8. [Chore and Maintenance Branches](#8-chore-and-maintenance-branches)
9. [Pull Request Template](#9-pull-request-template)
10. [Code Review Requirements Before Merge](#10-code-review-requirements-before-merge)
11. [Merge Strategy](#11-merge-strategy)
12. [Semantic Versioning Approach](#12-semantic-versioning-approach)
13. [Tag Strategy](#13-tag-strategy)

---

## 1. Introduction

This document defines the git branching strategy for the TRUE STAR BD LIMITED Digital Marketplace Platform. A consistent branching model ensures parallel development velocity, release reliability, and incident response speed. Every engineer contributing to the codebase MUST adhere to this strategy.

---

## 2. Branching Model Selection

### 2.1 Recommendation: Modified Trunk-Based Development

After evaluating both GitFlow and Trunk-Based Development against the project's requirements, we recommend a **Modified Trunk-Based Development** model. This decision is based on the following analysis:

| Factor | GitFlow | Trunk-Based | Modified Trunk-Based (Selected) |
|---|---|---|---|
| Release frequency | Low (weekly/monthly) | High (daily/deploy-on-demand) | **High (daily/deploy-on-demand)** |
| Team size | Large (10+) | Any | **Medium (3–8 engineers)** |
| Hotfix velocity | Slow (cherry-pick across branches) | Fast (fix forward) | **Fast (fix forward + release branches)** |
| CI complexity | High (many branch targets) | Low | **Low to moderate** |
| Parallel feature isolation | Strong | Weak (feature flags) | **Strong via short-lived branches + feature flags** |
| Audit trail | Excellent (merge commits) | Moderate (squash commits) | **Excellent (squash with PR references)** |
| Deploy frequency | Weekly+ | Multiple times daily | **Multiple times daily** |

### 2.2 Rationale

1. **Deployment velocity:** The digital marketplace requires rapid iteration on features (payment gateways, promotions, seller tools). Trunk-based development with short-lived feature branches enables multiple deployments per day.
2. **Feature flags as isolation mechanism:** Rather than long-lived branches, we use feature flags (LaunchDarkly / custom toggles) to gate incomplete features in production. This eliminates the need for a separate `develop` branch.
3. **Release branches for auditability:** Unlike pure trunk-based development, we maintain release branches for regulatory compliance and audit requirements. Every production deployment corresponds to a tagged commit on a release branch.
4. **Hotfix simplicity:** Critical security patches or payment bugs are fixed on trunk and cherry-picked to the active release branch — no multi-branch merge hell.

---

## 3. Branch Naming Conventions

All branch names MUST follow the pattern:

```
<type>/<ticket-id>-<short-description>
```

### 3.1 Branch Types

| Type | Purpose | Base Branch | Lifetime | Merges Into |
|---|---|---|---|---|
| `feature/` | New feature development | `main` | Short (1–3 days max) | `main` |
| `bugfix/` | Non-critical defect fix | `main` | Short | `main` |
| `hotfix/` | Critical production defect | `main` | Hours | `main` + active `release/*` |
| `release/` | Release preparation | `main` | Days (frozen) | `main` (tagged) |
| `chore/` | Maintenance, deps, tooling | `main` | Short | `main` |
| `docs/` | Documentation-only changes | `main` | Short | `main` |
| `refactor/` | Code restructuring | `main` | Short | `main` |
| `experiment/` | Spike or proof-of-concept | `main` | Ephemeral | Discarded |

### 3.2 Naming Examples

```
feature/TSBL-427-bkash-payment-integration
bugfix/TSBL-512-fix-escrow-double-release
hotfix/TSBL-601-patch-sql-injection-vulnerability
release/v1.4.0
chore/TSBL-389-upgrade-pydantic-v2
docs/TSBL-201-api-rate-limit-docs
refactor/TSBL-301-extract-payment-gateway-strategy
experiment/spike-websocket-broadcast
```

### 3.3 Rules

- Branch names are lowercase. Use hyphens as word separators.
- The ticket ID (`TSBL-{NNN}`) references the project management system (Jira / Linear).
- Descriptions should be 2–5 words summarizing the change.
- `/` is a directory separator in git, not a visual delimiter. Use only one level of hierarchy: `<type>/`.
- No trailing slashes, no special characters except hyphens.

---

## 4. Main Branches

### 4.1 Branch Definitions

| Branch | Protection | Deployment Target | Description |
|---|---|---|---|
| `main` | **Protected.** Requires PR, passing CI, 1+ approval. No direct pushes. | Production | The single source of truth. Every commit on `main` is deployable. |
| `release/v*` | **Protected.** Created per release cycle. No direct pushes. Pre-PR auto-deploys to staging. | Staging → Production | Freeze branch for release preparation and final validation. |
| `staging` | Not a branch — a deployment of tagged commits or release branches to the staging environment. | N/A | Staging environment target; not a persistent git branch. |

### 4.2 `main` Branch Rules

- `main` MUST always be in a deployable state. Every commit to `main` passes all CI stages (lint, type-check, test, build, security scan).
- `main` is the base branch for all feature, bugfix, and chore branches.
- Direct commits to `main` are **forbidden** by branch protection rules.
- `main` is the only branch deployed to production (via release tags).
- Commit history on `main` consists of squashed merge commits from feature/bugfix/hotfix branches and merge commits from release branches.

### 4.3 `release/v*` Branch Rules

- Created from `main` when a release candidate is ready.
- Only bug fixes, documentation updates, and release preparation commits are allowed on release branches.
- No new features on release branches.
- Release branches deploy to staging automatically.
- When validated, the release branch is merged into `main` and tagged.

---

## 5. Feature Branch Workflow

### 5.1 Lifecycle

```
[main] ──┬── [feature/TSBL-427-bkash-payment] ──┐
         │                                       │
         ├── [feature/TSBL-430-wallet-vault] ────┤
         │                                       │
         └───────────────────────────────────────┘ (squash merge → main)
```

### 5.2 Steps

1. **Create branch from `main`:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/TSBL-427-bkash-payment
   ```

2. **Develop incrementally:**
   - Commit frequently using Conventional Commits.
   - Push at least once daily to enable backup and collaboration.
   - Use feature flags for work-in-progress code that must be merged incrementally.

3. **Keep branch up to date:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```
   - Rebase (not merge) to maintain a linear history.
   - Resolve conflicts locally before pushing.

4. **Open pull request:**
   - PR target: `main`.
   - PR title: Use Conventional Commit format.
   - PR description: Use the PR template (see Section 9).

5. **Pass CI and code review:**
   - All CI checks must pass.
   - Minimum 1 approval (2 for critical paths: payment, wallet, auth, escrow).

6. **Squash merge into `main`:**
   - All commits on the feature branch are squashed into a single commit on `main`.
   - The squash commit message is the PR title (Conventional Commit format).

7. **Delete feature branch:**
   - Branch is deleted after merge (automated via GitHub/GitLab settings).

### 5.3 Branch Age Limit

Feature branches MUST live no longer than 3 calendar days. Branches older than 3 days without activity are flagged by automation and may be closed. Long-lived work must be broken into smaller units or gated behind feature flags.

---

## 6. Release Branch Workflow

### 6.1 When to Create a Release Branch

A release branch is created when:

- A set of features is ready for production deployment.
- A scheduled release date is approaching.
- A staging environment needs a stable target for UAT and QA.

### 6.2 Workflow

```
[main] ──────────────────────────────────────────────────
         \                                           /
          └── [release/v1.4.0] ── [bugfix] ────────┘ (merge to main + tag)
```

1. **Create release branch from `main`:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b release/v1.4.0
   ```

2. **Deploy to staging:** Automatically deploy release branch to staging environment.

3. **Release stabilization:**
   - Only critical bug fixes and release documentation commits allowed on the release branch.
   - All changes to the release branch MUST go through PRs with 2 approvals.
   - Version metadata in `pyproject.toml` / `package.json` is updated.

4. **QA/UAT validation:** QA team validates against staging. Sign-off required.

5. **Merge to `main` and tag:**
   ```bash
   git checkout main
   git merge --no-ff release/v1.4.0 -m "chore(release): v1.4.0"
   git tag -a v1.4.0 -m "Release v1.4.0"
   git push origin main --tags
   ```

6. **Deploy to production:** CI/CD pipeline builds from the tag and deploys to production.

7. **Delete release branch:** Clean up after successful production deployment.

### 6.3 Critical Rule

Any fix applied to a release branch MUST also be applied to `main` (either by the release branch merge or by a separate PR if the fix is needed before the release branch merge).

---

## 7. Hotfix Branch Workflow

### 7.1 When to Use a Hotfix

A hotfix is reserved for:
- **Critical security vulnerabilities** in production (CVSS ≥ 7.0)
- **Production outages** affecting all users or financial transactions
- **Data corruption** or data loss scenarios
- **Payment processing failures** blocking revenue

### 7.2 Workflow

```
[main] ── [hotfix/TSBL-601-patch-sqli] ── (squash merge to main)
         │                                     │
         └── [release/v1.4.0] ──────────────── (cherry-pick to active release)
```

1. **Create hotfix branch from `main`:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/TSBL-601-patch-sqli
   ```

2. **Fix and commit:** Follow the same process as feature branches. The PR is marked as `hotfix`.

3. **Expedited review:**
   - Minimum 1 approval (by a senior engineer).
   - CI must still pass (no exceptions for security-critical fixes).
   - Target merge time: < 1 hour from identification.

4. **Squash merge to `main`.**

5. **Cherry-pick to active release branch (if applicable):**
   ```bash
   git checkout release/v1.4.0
   git cherry-pick <commit-hash-from-main>
   git push origin release/v1.4.0
   ```

6. **Immediate deployment:**
   - CI/CD deploys `main` (or the release branch) to production automatically.
   - A rollback plan MUST be prepared before deployment.

7. **Post-hotfix:**
   - A root cause analysis (RCA) must be filed within 24 hours.
   - A permanent prevention measure must be added to the backlog.

### 7.3 Hotfix vs. Bugfix Decision Matrix

| Criteria | Hotfix | Bugfix |
|---|---|---|
| Severity | Production down, data loss, security breach | Minor functionality, cosmetic, non-critical |
| User impact | All users or all financial transactions | Subset of users, non-blocking |
| Workaround available | No | Yes |
| Time sensitivity | Hours | Days (next release cycle) |
| Approval | Expedited (1 senior engineer) | Standard (1–2 engineers) |

---

## 8. Chore and Maintenance Branches

### 8.1 Use Cases

Chore branches cover non-functional changes:

- Dependency upgrades (minor/patch versions)
- CI/CD pipeline improvements
- Tooling configuration changes
- Refactoring (no behavior change)
- Documentation updates
- Performance optimization

### 8.2 Process

Chore branches follow the same feature branch workflow (branch from `main`, PR to `main`, squash merge). They do NOT require feature flags.

### 8.3 Dependency Upgrade Policy

| Dependency Type | PR Requirement | CI Requirement |
|---|---|---|
| Patch version (1.0.x) | Auto-approval by Dependabot/Renovate | Tests must pass |
| Minor version (1.x.0) | Requires review | Tests + build must pass |
| Major version (x.0.0) | Requires review + manual QA | Full CI suite + staging deploy |
| Security advisory | Expedited (hotfix workflow) | Tests must pass |

---

## 9. Pull Request Template

The following template is enforced by a `.github/PULL_REQUEST_TEMPLATE.md` file:

```markdown
## Description

<!-- Provide a concise description of the changes. Include motivation and context. -->

Closes: TSBL-{NNN}

## Type of Change

<!-- Mark with [x] the applicable type -->

- [ ] feat — New feature (non-breaking)
- [ ] fix — Bug fix (non-breaking)
- [ ] hotfix — Critical production fix
- [ ] chore — Maintenance, dependencies, tooling
- [ ] docs — Documentation only
- [ ] refactor — Code restructuring (no behavior change)
- [ ] perf — Performance improvement
- [ ] test — Test additions/fixes
- [ ] BREAKING CHANGE — Backward-incompatible API change

## Testing

<!-- Describe the testing performed -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed in staging
- [ ] No testing required (explain why)

## Checklist

<!-- Verify the following before requesting review -->

- [ ] Code follows project coding standards (lint + format passed)
- [ ] Type checks pass (mypy / tsc)
- [ ] All tests pass locally and in CI
- [ ] No new security vulnerabilities introduced
- [ ] API documentation updated (if applicable)
- [ ] Database migrations have downgrade path
- [ ] Feature flag added (if feature is incomplete)
- [ ] Commit messages follow Conventional Commits

## Screenshots / Logs

<!-- Attach relevant screenshots, logs, or error messages -->

## Rollback Plan

<!-- Describe how to roll back this change if needed -->

```

---

## 10. Code Review Requirements Before Merge

### 10.1 Mandatory Pre-Merge Gates

| Gate | Tool / Process | Failure Action |
|---|---|---|
| Branch is up-to-date with `main` | Git status check | Block merge (require rebase) |
| Lint passes | Ruff (Python), ESLint (TypeScript) | Block merge |
| Format check passes | Ruff format, Prettier | Block merge |
| Type check passes | mypy (strict), tsc (strict) | Block merge |
| Unit tests pass | pytest, Vitest | Block merge |
| Build succeeds | Docker build, Vite build | Block merge |
| No merge conflicts | Git | Block merge |
| Commit message lint | commitlint | Block merge |
| Security scan passes | Bandit, npm audit, Trivy | Block merge |
| Approved reviews | 1 appoval (2 for critical paths) | Block merge |

### 10.2 Approval Requirements by Path

| Area | Minimum Approvals | Approver Qualification |
|---|---|---|
| Frontend UI components | 1 | Any team member |
| Backend non-critical | 1 | Any team member |
| Backend (auth, payment, wallet, escrow) | 2 | 1 must be senior engineer |
| Database migrations | 2 | 1 must be DBA or senior backend |
| CI/CD configuration | 1 | DevOps/infra engineer |
| Security-sensitive changes | 2 | 1 must be security champion |
| Release branches | 2 | 1 must be tech lead |
| Hotfixes | 1 | Senior engineer |

---

## 11. Merge Strategy

### 11.1 Default: Squash Merge

Feature, bugfix, chore, and hotfix branches use **squash merge** into `main`.

**Rationale:**
- Keeps `main` history linear and readable.
- Every commit on `main` represents a complete, tested, single-purpose change.
- Enables easy cherry-pick for hotfixes.
- Simplifies `git bisect` — each commit on `main` is a deployable unit.

```bash
# GitHub / GitLab setting: "Squash merge"
# Squash commit message = PR title (Conventional Commit format)
# Squash commit description = PR body (ticket reference, key details)
```

### 11.2 Release Branches: Merge Commit

Release branches use **merge commit** (`--no-ff`) into `main`.

**Rationale:**
- Preserves the release boundary as a visible commit in history.
- Makes it clear which commits belong to which release.
- Facilitates audit trail for compliance.

```bash
git checkout main
git merge --no-ff release/v1.4.0 -m "chore(release): v1.4.0"
```

### 11.3 Hotfix Cherry-Pick

Hotfixes applied to release branches use `git cherry-pick` (not merge) to avoid duplicating commits when the release branch merges to `main`.

### 11.4 Prohibited Operations

- **Rebasing `main`:** Never rebase `main`. History rewrite on shared branches is forbidden.
- **Force-pushing to `main` or `release/*`:** Forbidden. Protected branch rules enforce this.
- **Merging `main` into feature branches:** Use rebase instead (`git rebase main`).

---

## 12. Semantic Versioning Approach

### 12.1 Version Format

All releases follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE[+BUILD]]
```

### 12.2 Version Bump Rules

| Version Component | Trigger | Example |
|---|---|---|
| MAJOR | Breaking API change, backward-incompatible database migration, removal of a feature | `1.4.0` → `2.0.0` |
| MINOR | New feature (backward-compatible), new API endpoint, new payment gateway | `1.4.0` → `1.5.0` |
| PATCH | Bug fix, security patch, performance improvement, non-breaking dependency upgrade | `1.4.0` → `1.4.1` |
| PRERELEASE | Release candidate, alpha/beta builds | `1.4.0-rc.1` |
| BUILD | CI build number (optional) | `1.4.0+build.42` |

### 12.3 Version Storage

Version is stored in a single, authoritative source:

- **Backend:** `pyproject.toml` — `version = "1.4.0"`
- **Frontend:** `package.json` — `"version": "1.4.0"`
- **CI/CD:** Inferred from the above; not duplicated.
- **Docker:** Image tag = version (e.g., `tsbl/order-service:1.4.0`).

### 12.4 Automated Version Determination

CI determines the version bump type based on commit messages since the last tag:

```
# CI script logic (simplified)
if any commit contains "BREAKING CHANGE" → MAJOR bump
elif any commit starts with "feat" → MINOR bump
else → PATCH bump
```

Pre-release versions are appended for non-main branches: `1.4.0-rc.1`, `1.5.0-alpha.1`.

---

## 13. Tag Strategy

### 13.1 Tag Format

Tags follow the version number exactly:

```
v{MAJOR}.{MINOR}.{PATCH}
```

Examples:
```
v1.0.0
v1.4.0
v2.0.0
v1.4.1-rc.1
```

### 13.2 Tag Types

| Tag Type | Format | Created By | Pushed To | Description |
|---|---|---|---|---|
| Release | `v1.4.0` | CI/CD or manual on `main` | Origin | Marks a production release |
| Release Candidate | `v1.4.0-rc.1` | CI/CD on release branch | Origin | Pre-release for staging validation |
| Hotfix | `v1.4.1` | CI/CD on `main` | Origin | Marks a hotfix release |

### 13.3 Tagging Rules

1. **Every production deployment MUST be tagged.**
2. Tags are created on `main` (or `release/*` for RCs), never on feature branches.
3. Tags are signed (`git tag -s`) for integrity verification.
4. Tag messages describe the release:
   ```
   v1.4.0
   Release v1.4.0 — bKash payment integration + wallet vault feature
   ```
5. Once pushed, tags are immutable. A tag cannot be overwritten. If a release is rolled back, a new PATCH version is released.
6. Tags are included in `git push --tags` only from CI, not from developer workstations (to prevent accidental mismatches).

### 13.4 Tag-Based Deployment

CI/CD pipelines use tags to trigger production deployments:

```yaml
# GitLab CI example
deploy-production:
  stage: deploy
  only:
    - tags
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - kubectl set image deployment/backend backend=$CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
```

### 13.5 Rollback Tag Strategy

When a rollback is required:

1. Identify the last known-good tag (e.g., `v1.3.9`).
2. Redeploy using that tag: `kubectl set image deployment/backend backend=tsbl/order-service:v1.3.9`.
3. Create a new PATCH tag (`v1.4.1`) with the fix, do not reuse the failed tag.

---

*End of Document — DEV-TSBL-002*
