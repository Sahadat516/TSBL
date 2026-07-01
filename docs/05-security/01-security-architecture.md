# Security Architecture

| **Document Owner** | Chief Information Security Officer (CISO) |
|---|---|
| **Classification** | Confidential — Internal Use Only |
| **Version** | 1.0 |
| **Last Updated** | 2026-07-01 |
| **Approved By** | Board of Directors, TRUE STAR BD LIMITED |

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Security Principles](#2-security-principles)
3. [Authentication Architecture](#3-authentication-architecture)
4. [Authorization Architecture (RBAC)](#4-authorization-architecture-rbac)
5. [Password Policies](#5-password-policies)
6. [Session Management](#6-session-management)
7. [API Security](#7-api-security)
8. [Data Encryption](#8-data-encryption)
9. [Database Encryption](#9-database-encryption)
10. [Secrets Management](#10-secrets-management)
11. [OWASP Top 10 Mitigation Strategies](#11-owasp-top-10-mitigation-strategies)
12. [DDoS Protection](#12-ddos-protection)
13. [Web Application Firewall (WAF)](#13-web-application-firewall-waf)
14. [Security Headers](#14-security-headers)
15. [Audit Logging and SIEM Integration](#15-audit-logging-and-siem-integration)
16. [Vulnerability Scanning and Penetration Testing](#16-vulnerability-scanning-and-penetration-testing)
17. [Incident Response Plan](#17-incident-response-plan)
18. [Compliance Considerations](#18-compliance-considerations)
19. [Secure SDLC Practices](#19-secure-sdlc-practices)

---

## 1. Purpose and Scope

This document defines the security architecture for the TRUE STAR BD LIMITED digital marketplace platform. It governs all engineering decisions, operational procedures, and compliance obligations related to information security.

**Scope covers:**

| **Domain** | **Coverage** |
|---|---|
| Application Security | Web, mobile, and API endpoints |
| Infrastructure Security | Cloud hosting, container orchestration, networking |
| Data Security | Customer PII, payment data, transaction records |
| Operational Security | Monitoring, incident response, access control |
| Supply Chain Security | Third-party vendors, open-source dependencies |

---

## 2. Security Principles

### 2.1 Defense in Depth

Security controls are layered across every tier of the stack. Compromise of a single layer does not compromise the system.

| **Layer** | **Controls** |
|---|---|
| Application | Input validation, output encoding, parameterized queries |
| Authentication | MFA, JWT rotation, device fingerprinting |
| Network | WAF, DDoS mitigation, network segmentation |
| Host | Hardened containers, OS-level firewalls, SELinux |
| Data | Encryption at rest (AES-256) and in transit (TLS 1.3) |
| Physical | Cloud provider SOC 2/ISO 27001 certified data centers |

### 2.2 Least Privilege

Every user, service account, and process operates with the minimum permissions necessary to perform its function.

- **Human users:** Role-based access with time-bound just-in-time (JIT) elevation
- **Service accounts:** Scoped API tokens with expiry, no interactive shell access
- **Database:** Application-level credentials have CRUD scope per schema only; migration credentials are separate
- **Network:** Micro-segmentation enforcing east-west traffic rules

### 2.3 Zero Trust — "Never Trust, Always Verify"

No entity is trusted by default, regardless of network location.

| **Zero Trust Pillar** | **Implementation** |
|---|---|
| Identity verification | Every request authenticated (MFA enforced for sensitive actions) |
| Device posture | Device compliance check before granting access |
| Network segmentation | All traffic encrypted; no implicit trust within VPC |
| Policy enforcement | Attribute-based access control (ABAC) on sensitive resources |
| Continuous monitoring | Real-time anomaly detection on every transaction |

---

## 3. Authentication Architecture

### 3.1 Token-Based Authentication (JWT)

The platform uses a **signed JWT** model with short-lived access tokens and long-lived refresh tokens.

```
┌─────────┐  Credentials   ┌──────────────┐  JWT Access Token  ┌──────────┐
│  Client  │ ──────────────>│  Auth Service │ ─────────────────>│  API GW   │
│          │                │               │                   │          │
│          │<───────────────│               │                   │          │
│          │  Refresh Token │               │                   │          │
└─────────┘                └──────────────┘                   └──────────┘
```

| **Component** | **Value** | **Rationale** |
|---|---|---|
| Access token TTL | 15 minutes | Limits exposure window |
| Refresh token TTL | 7 days (sliding) | Balances UX with security |
| Refresh token rotation | Mandatory | Old token invalidated on each refresh |
| Reuse detection | Required | Stolen refresh tokens detected and all family revoked |
| Signing algorithm | RS256 (asymmetric) | Private key signs, public key verifies; no secret sharing |
| Issuer | `auth.tsbl.com` | JWT `iss` claim |
| Audience | `api.tsbl.com` | JWT `aud` claim |

### 3.2 Token Structure

```json
{
  "sub": "usr_2f3a1b4c",
  "iss": "auth.tsbl.com",
  "aud": "api.tsbl.com",
  "iat": 1688119200,
  "exp": 1688120100,
  "roles": ["buyer"],
  "permissions": ["order:read", "order:create"],
  "jti": "tok_9k8m3n2p",
  "type": "access"
}
```

### 3.3 Refresh Token Rotation

| **Step** | **Action** |
|---|---|
| 1 | Client presents valid refresh token |
| 2 | Auth Service validates token signature and expiry |
| 3 | Auth Service issues **new** access + **new** refresh token |
| 4 | Auth Service invalidates old refresh token |
| 5 | If old refresh token reused (stolen), entire token family revoked |

### 3.4 Multi-Factor Authentication (MFA)

| **Factor Type** | **Supported Methods** | **Enforcement** |
|---|---|---|
| Knowledge | Password / PIN | Always required |
| Possession | TOTP (Authenticator app), SMS OTP, WebAuthn (FIDO2) | Admin panel, payment > $500 |
| Inherence | Biometric (device-native, not stored server-side) | Mobile app login |
| Backup Codes | 10 one-time use codes per user | Provisioned at MFA enrollment |

---

## 4. Authorization Architecture (RBAC)

### 4.1 Hierarchical Role Model

```
                        ┌─────────────────────┐
                        │   Super Admin        │
                        │  (system-wide root)  │
                        └───────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
   ┌──────────┴────────┐ ┌─────┴──────┐  ┌────────┴─────────┐
   │  Platform Admin   │ │ Compliance  │  │  Support Manager │
   │  (operations)     │ │ Admin       │  │  (team lead)     │
   └──────────┬────────┘ └────────────┘  └────────┬─────────┘
              │                                     │
   ┌──────────┴────────┐                  ┌────────┴─────────┐
   │  Vendor Manager   │                  │  Support Agent   │
   │  (seller mgmt)    │                  │  (tier 1/2/3)    │
   └──────────┬────────┘                  └──────────────────┘
              │
   ┌──────────┴────────┐
   │  Vendor (seller)  │
   └───────────────────┘
```

### 4.2 Role-Permission Mapping

| **Role** | **Scope** | **Example Permissions** |
|---|---|---|
| `super_admin` | Global | `system:configure`, `user:impersonate`, `audit:export` |
| `platform_admin` | Global | `vendor:approve`, `product:moderate`, `report:generate` |
| `compliance_admin` | Global | `audit:read`, `case:investigate`, `user:suspend` |
| `support_manager` | Global | `ticket:assign`, `ticket:escalate`, `agent:performance` |
| `vendor_manager` | Vendor pool | `vendor:onboard`, `vendor:commission:set` |
| `support_agent` | Assigned tickets | `ticket:read`, `ticket:reply`, `ticket:resolve` |
| `vendor` | Own account only | `product:create`, `order:fulfill`, `report:sales` |
| `buyer` | Own account only | `order:create`, `order:read`, `review:write` |
| `guest` | Public | `product:search`, `product:read` |

### 4.3 Permission Inheritance

Roles inherit permissions hierarchically. A `platform_admin` inherits all permissions of `vendor_manager`, `support_manager`, and below.

---

## 5. Password Policies

### 5.1 Password Requirements

| **Policy** | **Requirement** |
|---|---|
| Minimum length | 12 characters |
| Complexity | No composition rules (NIST SP 800-63B compliant) |
| Maximum length | 128 characters |
| Password history | 10 previous passwords remembered |
| Password expiry | 90 days (privileged users: 60 days) |
| Account lockout | 5 failed attempts → 15-minute lockout |
| Breach detection | Check against Have I Been Pwned (HIBP) API on creation |

### 5.2 Password Hashing

| **Algorithm** | **Purpose** | **Parameters** |
|---|---|---|
| **Argon2id** | Primary hashing algorithm | Memory: 64 MiB, Iterations: 3, Parallelism: 4 |
| **bcrypt** | Fallback (legacy migration) | Cost factor: 12 (2^12 rounds) |
| **PBKDF2-SHA256** | Not used (prevent downgrade) | — |

### 5.3 MFA Enforcement Matrix

| **User Action** | **MFA Required** |
|---|---|
| Login (standard) | Optional |
| Login (new device) | Required |
| Password change | Required |
| PII update (email, phone) | Required |
| Payout configuration | Required |
| Admin panel access | Required |
| API key generation | Required |

---

## 6. Session Management

### 6.1 Session Storage

| **Session Type** | **Storage** | **TTL** |
|---|---|---|
| Web (browser) | Redis cluster (encrypted) | 24 hours inactivity → expiry |
| Mobile (app) | JWT-based (stateless) | Per token TTL |
| API (service) | mTLS certificate | 365 days (rotated quarterly) |

### 6.2 Session Protection

- **Refresh token theft detection:** Reuse detection triggers immediate family revocation and user notification
- **Concurrent session limit:** 5 simultaneous sessions per user (web) / 10 (API)
- **Idle timeout:** 30 minutes (web), 2 hours (mobile)
- **Absolute timeout:** 12 hours (web), 30 days (mobile)
- **Logout everywhere:** Invalidates all refresh token families
- **Device fingerprinting:** Browser/device fingerprint bound to session token

### 6.3 Token Revocation

| **Event** | **Action** |
|---|---|
| Password change | All sessions revoked (except current) |
| MFA disabled | All sessions revoked |
| Account suspended | All sessions revoked, immediate |
| User-initiated logout | Current session invalidated |
| Admin impersonation | Impersonation session logged; original session preserved |

---

## 7. API Security

### 7.1 Rate Limiting

| **Tier** | **Rate** | **Burst** | **Scope** |
|---|---|---|---|
| Public endpoints | 100 req/min | 20 req/sec | Per IP |
| Authenticated users | 1,000 req/min | 100 req/sec | Per user ID |
| Admin endpoints | 500 req/min | 50 req/sec | Per admin ID |
| Payment endpoints | 30 req/min | 5 req/sec | Per user ID |
| Auth endpoints (login) | 10 req/min | 2 req/sec | Per IP |

**Algorithm:** Token bucket (Redis-backed)

### 7.2 Input Validation

| **Layer** | **Method** | **Tools** |
|---|---|---|
| Transport | Schema validation (JSON Schema / OpenAPI) | express-validator, zod |
| Business | Domain-specific validation rules | Custom validators |
| Storage | Parameterized queries / ORM | Prisma, SQLAlchemy |
| Output | Context-aware encoding | DOMPurify (HTML), helmet (headers) |

### 7.3 CORS Policy

```nginx
Access-Control-Allow-Origin: https://*.tsbl.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH
Access-Control-Allow-Headers: Content-Type, Authorization, X-Request-Id
Access-Control-Expose-Headers: X-Request-Id, X-RateLimit-Remaining
Access-Control-Max-Age: 86400
```

- **Pre-flight caching:** 24 hours
- **Credentials:** Included for same-origin only
- **Wildcard origins:** Strictly prohibited in production

### 7.4 CSRF Protection

| **Protection** | **Implementation** |
|---|---|
| Double-submit cookie pattern | Signed random token submitted in header and cookie |
| SameSite cookie attribute | `SameSite=Strict` for session cookies |
| Custom request header | `X-CSRF-Token` validated server-side |
| Idempotency tokens | `POST/PUT/PATCH/DELETE` require idempotency key |
| State-changing methods | No `GET` requests mutate state |

---

## 8. Data Encryption

### 8.1 Encryption in Transit

| **Protocol** | **Details** |
|---|---|
| TLS version | 1.3 (minimum); TLS 1.2 as fallback only |
| Cipher suites | `TLS_AES_256_GCM_SHA384` (preferred), `TLS_CHACHA20_POLY1305_SHA256` |
| Certificate issuer | Let's Encrypt (wildcard: `*.tsbl.com`) |
| Certificate renewal | Automated via cert-manager (90-day rotation) |
| mTLS | Enforced for inter-service communication (service mesh) |
| HSTS | `max-age=31536000; includeSubDomains; preload` |

### 8.2 Encryption at Rest

| **Layer** | **Algorithm** | **Key Management** |
|---|---|---|
| Storage volumes | AES-256-XTS | Cloud KMS (automatic key rotation) |
| Database (full) | AES-256-CBC (TDE) | Automatic 90-day rotation |
| Database (column-level) | AES-256-GCM with envelope encryption | Application-level via Vault |
| Backups | AES-256-CBC | Separate backup encryption key |
| Object storage (S3) | AES-256-SSE | Server-side encryption with KMS |

### 8.3 Key Hierarchy

```
Master Key (Root of Trust)
       │
       ▼
Key Encryption Key (KEK)  ── stored in HSM / Cloud KMS
       │
       ▼
Data Encryption Keys (DEK) ── rotated every 90 days
       │
       ▼
Encrypted Data
```

---

## 9. Database Encryption

### 9.1 Column-Level Encryption (PII)

| **Field** | **Encryption** | **Access Pattern** |
|---|---|---|
| Email address | AES-256-GCM | Deterministic (equality search) |
| Phone number | AES-256-GCM | Deterministic (equality search) |
| Government ID (NID) | AES-256-GCM with associated data (AAD) | Only on authorized admin view |
| Payment card data | AES-256-GCM (PCI-DSS tokenized) | Token stored; raw never persisted |
| Address (full) | AES-256-GCM | Only on order fulfillment |
| Payout bank account | AES-256-GCM (PCI-DSS tokenized) | Token stored; raw never persisted |

### 9.2 Application-Level Encryption Flow

```
1. Application receives PII data
2. Application calls Vault transit engine:
   POST /v1/transit/encrypt/<key_name>
   { "plaintext": "<base64(data)>" }
3. Vault returns ciphertext (base64-encoded)
4. Ciphertext stored in database column
5. On read: Vault /v1/transit/decrypt/<key_name>
```

### 9.3 Database Security Controls

| **Control** | **Implementation** |
|---|---|
| Network isolation | Database in private subnet only; no public endpoint |
| Authentication | `scram-sha-256` / IAM database authentication |
| Connection encryption | TLS 1.3 enforced for all connections |
| Audit logging | All DDL and DML on PII tables logged |
| Backup encryption | AES-256 with separate KMS key |
| Point-in-time recovery | Enabled with 35-day retention |

---

## 10. Secrets Management

### 10.1 Vault Architecture

| **Component** | **Tool** | **Purpose** |
|---|---|---|
| Secret storage | HashiCorp Vault (Enterprise) | Dynamic secrets, encryption keys |
| Vault backend | Integrated storage (Raft) | Clustered, highly available |
| Authentication | Kubernetes auth, JWT auth, LDAP | Service and human identity |
| Key rotation | Vault rotation plugin + scheduled rotation | Automated 90-day rotation |
| Audit | Vault audit log → SIEM | All secret access recorded |

### 10.2 Secret Categories

| **Category** | **Examples** | **Storage Method** |
|---|---|---|
| Database credentials | Username, password | Dynamic secrets (short-lived) |
| API keys | Stripe, Twilio, SendGrid | Static secrets, Vault KV v2 |
| Encryption keys | DEKs, KEKs | Vault Transit Engine |
| TLS certificates | Private keys | Vault PKI Engine |
| Service tokens | JWT signing keys | Vault KV v2, rotated monthly |

### 10.3 Dynamic Database Secrets

```
Application request ──> Vault ──> Database credential issued (TTL: 15 min)
                                     │
                                     ▼
                              Credential auto-expires after TTL
                                     │
                                     ▼
                              Vault revokes from database
```

---

## 11. OWASP Top 10 Mitigation Strategies

| **#** | **Category** | **Mitigation** |
|---|---|---|
| A01 | Broken Access Control | RBAC + ABAC; server-side authorization on every request; deny by default |
| A02 | Cryptographic Failures | TLS 1.3 everywhere; AES-256 for data at rest; Argon2id for passwords; no custom crypto |
| A03 | Injection | Parameterized queries (ORM); input validation (zod, JSON Schema); output encoding |
| A04 | Insecure Design | Threat modeling in design phase; security reviews in PRD; rate limiting on all endpoints |
| A05 | Security Misconfiguration | Infrastructure as Code (Terraform); CIS benchmark scanning; automated config audit |
| A06 | Vulnerable Components | SBOM generation (Syft); dependency scanning (Snyk/Dependabot); weekly CVE scanning |
| A07 | Identification & Auth Failures | MFA enforcement; account lockout; credential breach detection; session rotation |
| A08 | Software & Data Integrity Failures | Sigstore (cosign) for container signing; SLSA Level 3 build pipeline; provenance attestation |
| A09 | Security Logging & Monitoring | Structured JSON logging; centralized SIEM (ELK/Splunk); real-time alerting; no PII in logs |
| A10 | Server-Side Request Forgery | Allow-list of outbound URLs; network segmentation; deny private IP ranges by default |

---

## 12. DDoS Protection

### 12.1 Multi-Layer DDoS Defense

| **Layer** | **Protection** | **Provider** |
|---|---|---|
| Network (L3/L4) | Cloudflare Magic Transit / AWS Shield Advanced | Cloudflare / AWS |
| Application (L7) | Cloudflare WAF + Rate Limiting | Cloudflare |
| Origin shielding | Cloudflare Argo Tunnel / AWS CloudFront | Cloudflare / AWS |
| Edge caching | Cloudflare CDN | Cloudflare |

### 12.2 DDoS Response Playbook

| **Phase** | **Action** | **SLA** |
|---|---|---|
| Detection | Automated traffic anomaly alert → PagerDuty | < 1 minute |
| Triage | On-call engineer confirms DDoS via monitoring dashboards | < 5 minutes |
| Mitigation | Cloudflare auto-mitigation kicks in; manual rule deployment if needed | < 2 minutes |
| Scrubbing | Malicious traffic redirected to Cloudflare scrubber | Immediate |
| Communication | Status page update via status.tsbl.com | < 10 minutes |
| Post-mortem | Root cause analysis documented; rules tuned | Within 48 hours |

---

## 13. Web Application Firewall (WAF)

### 13.1 WAF Stack

| **Tier** | **Technology** | **Deployment** |
|---|---|---|
| Edge (L7) | Cloudflare WAF (Managed Ruleset) | Global edge network |
| Ingress (L7) | ModSecurity (Core Rule Set) | Kubernetes ingress gateway |
| API (L7) | Custom API security gateway | Sidecar proxy in service mesh |

### 13.2 WAF Rule Categories

| **Rule Set** | **Description** | **Action** |
|---|---|---|
| OWASP CRS 3.3 | Generic web application attacks | Block |
| Cloudflare Managed | SQLi, XSS, RFI, LFI, RCE | Block (paranoid mode) |
| Rate limiting | Per-IP, per-user, per-endpoint | Block / Throttle |
| Bot management | Known bots, verified crawlers, ML-based bot detection | Challenge / Block |
| Geo-blocking | Block high-risk countries (non-operational regions) | Block |
| Custom signatures | Application-specific attack patterns | Block |

### 13.3 WAF Bypass Protection

- **WAF runs in blocking mode, not detection-only**
- **Ingress-level WAF** (ModSecurity) prevents traffic from reaching application if edge WAF is bypassed
- **mTLS** ensures only legitimate service mesh traffic reaches pods
- **Integrity check** on all uploads (file type, magic bytes, AV scan)

---

## 14. Security Headers

| **Header** | **Value** | **Source** |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | NGINX / Ingress |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' static.tsbl.com; style-src 'self' static.tsbl.com; img-src 'self' static.tsbl.com cdn.tsbl.com; connect-src 'self' api.tsbl.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'` | NGINX / Ingress |
| `X-Frame-Options` | `DENY` | NGINX / Ingress |
| `X-Content-Type-Options` | `nosniff` | NGINX / Ingress |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | NGINX / Ingress |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(self), display-capture=()` | NGINX / Ingress |
| `Cross-Origin-Embedder-Policy` | `require-corp` | NGINX / Ingress |
| `Cross-Origin-Opener-Policy` | `same-origin` | NGINX / Ingress |
| `Cross-Origin-Resource-Policy` | `same-origin` | NGINX / Ingress |

### CSP Directive Justification

| **Directive** | **Rationale** |
|---|---|
| `default-src 'self'` | Baseline: only load resources from own origin |
| `script-src 'self' static.tsbl.com` | Block inline scripts; allow CDN-hosted JS bundles |
| `connect-src 'self' api.tsbl.com` | Restrict XHR/fetch to own domain and API |
| `frame-ancestors 'none'` | Prevent clickjacking (X-Frame-Options is deprecated but kept) |
| `form-action 'self'` | Forms cannot submit to external domains |

---

## 15. Audit Logging and SIEM Integration

### 15.1 Audit Log Categories

| **Category** | **Events Captured** | **Retention** |
|---|---|---|
| Authentication | Login, logout, MFA, password change, token refresh, account lockout | 1 year |
| Authorization | Role change, permission grant/revoke, access denied | 1 year |
| Data access | PII read/write, export, bulk operations | 2 years (GDPR: 3 years) |
| Payment | Transaction, refund, dispute, payout | 5 years (PCI-DSS) |
| Administration | Config change, user suspend, vendor approval, feature flag toggle | 2 years |
| System | Deployment, scaling event, backup, restore, certificate expiry | 1 year |
| Security | WAF block, rate limit exceeded, breach detection, vulnerability scan | 1 year |

### 15.2 Log Format (Structured JSON)

```json
{
  "timestamp": "2026-07-01T10:30:00.000Z",
  "event_id": "evt_9k8m3n2p",
  "category": "authentication",
  "action": "login_success",
  "user_id": "usr_2f3a1b4c",
  "session_id": "sess_7h6g5f4e",
  "source_ip": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "device_fingerprint": "fp_3d2c1b0a",
  "geo": { "country": "BD", "city": "Dhaka" },
  "risk_score": 0.12,
  "severity": "info",
  "correlation_id": "corr_8j7k6l5m",
  "metadata": { "mfa_method": "totp" }
}
```

### 15.3 SIEM Integration

| **SIEM Platform** | **Elastic Security (ELK Stack)** |
|---|---|
| Log shipping | Filebeat → Logstash → Elasticsearch |
| Correlation rules | Custom Sigma rules + Elastic prebuilt rules |
| Alerting | Watcher / ElastAlert → PagerDuty, Slack |
| Threat intelligence | MITRE ATT&CK mapping; MISP feed integration |
| Retention | 90 days (hot), 1 year (warm), 5 years (cold/Glacier) |
| Compliance export | Automated GDPR data portability / deletion workflows |

### 15.4 Immutable Logging

- Logs written to append-only storage (AWS S3 Object Lock / Azure Blob Storage immutable blob)
- Write-once-read-many (WORM) compliance
- Database triggers on PII columns write to audit table
- No log tampering possible without cloud provider administrative access

---

## 16. Vulnerability Scanning and Penetration Testing

### 16.1 Scan Cadence

| **Scan Type** | **Frequency** | **Tool** | **Trigger** |
|---|---|---|---|
| SAST (Static Analysis) | Every commit | SonarQube (pre-commit hook + CI) | Pull request creation |
| DAST (Dynamic Analysis) | Daily (staging) | OWASP ZAP / Burp Suite Pro | Scheduled pipeline |
| SCA (Dependency Scan) | Every commit + weekly | Snyk / Dependabot / Trivy | CI pipeline + cron |
| Container scan | Every image build | Trivy, Grype, Clair | CI pipeline |
| Infrastructure scan | Weekly | Terraform (tfsec, checkov) + CloudSploit | Scheduled pipeline |
| Secret scanning | Every commit | GitLeaks / truffleHog | Pre-commit hook + CI |
| External perimeter scan | Monthly | HackerOne / Bugcrowd | Recurring engagement |
| Full penetration test | Quarterly | Third-party (CREST/OSCP certified) | Independent assessment |

### 16.2 Vulnerability Severity and SLAs

| **Severity** | **CVSS Range** | **Resolution SLA** | **Example** |
|---|---|---|---|
| Critical | 9.0–10.0 | 24 hours | Remote code execution, SQLi |
| High | 7.0–8.9 | 72 hours | Authentication bypass, XSS with impact |
| Medium | 4.0–6.9 | 14 days | Information disclosure, CSRF |
| Low | 0.1–3.9 | Next release cycle | Missing security header |

---

## 17. Incident Response Plan

### 17.1 Incident Classification

| **Severity** | **Level** | **Response Time** | **Examples** |
|---|---|---|---|
| SEV-1 | Critical | 15 minutes | Data breach, service outage, payment fraud |
| SEV-2 | High | 1 hour | Widespread authentication failure, significant performance degradation |
| SEV-3 | Medium | 4 hours | Isolated user access issues, minor data inconsistency |
| SEV-4 | Low | Next business day | Cosmetic issues, non-critical bug |

### 17.2 Incident Response Phases

```
              ┌─────────────┐
              │  1. Detect  │
              │  & Report   │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  2. Triage  │
              │  & Assess   │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  3. Contain │
              │  & Eradicate│
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  4. Recover │
              │  & Restore  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  5. Post-   │
              │  mortem     │
              └─────────────┘
```

### 17.3 Incident Response Team (IRT)

| **Role** | **Responsibility** | **Backup** |
|---|---|---|
| Incident Commander | Coordinates response; makes go/no-go decisions | CISO |
| Security Lead | Forensics, threat containment, evidence preservation | Security Engineer |
| Engineering Lead | Code/configuration fix, deployment rollback | Senior Engineer |
| Communications Lead | Internal/external communication, regulatory reporting | PR Lead |
| Legal Counsel | Legal liability, breach notification, regulatory compliance | External counsel |

### 17.4 Breach Notification

| **Requirement** | **Timeline** | **Authority** |
|---|---|---|
| Internal notification | Within 1 hour | Incident Commander |
| Regulatory (GDPR DPA) | Within 72 hours | Lead supervisory authority |
| Regulatory (PCI-DSS) | Within 24 hours | Acquiring bank |
| Affected users | Within 72 hours | Direct email communication |
| Public disclosure | As needed (assess with legal) | Press release + status.tsbl.com |

---

## 18. Compliance Considerations

### 18.1 GDPR Compliance

| **Requirement** | **Implementation** |
|---|---|
| Data processing agreement (DPA) | Signed with all sub-processors (cloud providers, payment gateways) |
| Data Protection Officer (DPO) | Appointed DPO@tsbl.com |
| Consent management | Cookie consent banner; granular consent per purpose |
| Right to erasure (Art. 17) | Automated user deletion workflow (30-day soft delete + permanent purge) |
| Data portability (Art. 20) | Self-service export (JSON/CSV) from user settings |
| Breach notification (Art. 33) | 72-hour notification procedure (see Section 17.4) |
| Data retention policy | PII deleted after account closure + 90 days (legal hold excluded) |
| Records of processing (Art. 30) | Automated processing activity register maintained |

### 18.2 PCI-DSS Compliance (If Applicable)

| **Requirement** | **Implementation** |
|---|---|
| Cardholder data storage | Never stored; use PCI-compliant tokenization (Stripe/Adyen) |
| Encryption | AES-256 for any stored payment data |
| Access control | MFA for all payment system access |
| Network segmentation | Cardholder data environment (CDE) isolated from corporate network |
| Logging | All access to CDE logged and monitored |
| Vulnerability scanning | Quarterly ASV scan by approved scanning vendor |
| Penetration testing | Annual PCI-DSS scope penetration test |
| SAQ validation | SAQ D validation annually |

### 18.3 Bangladesh-Specific Regulations

| **Regulation** | **Requirement** | **Status** |
|---|---|---|
| Digital Security Act 2018 | Data localization for citizen data; breach notification | Implemented |
| Bangladesh Bank Guidelines | Payment system security; KYC/AML for merchants | In progress |
| BTRC Regulations | Telecom/internet services licensing | Under review |

---

## 19. Secure SDLC Practices

### 19.1 Security Gates in CI/CD Pipeline

| **Gate** | **Stage** | **Tool** | **Fail Condition** |
|---|---|---|---|
| Secret scanning | Pre-commit + CI | GitLeaks | Any secret detected |
| SAST | CI (after lint) | SonarQube | Any blocker/critical issue |
| SCA | CI (after build) | Snyk / Trivy | Any critical vulnerability in direct dependencies |
| Container scan | CI (after image build) | Trivy | Any high/critical CVE |
| DAST | CI (staging deployment) | OWASP ZAP | Any high severity finding |
| IaC scan | CI (infrastructure) | tfsec / checkov | Any high severity misconfiguration |
| License compliance | CI (after build) | FOSSA / Black Duck | Copyleft license in prohibited dependencies |
| Artifact signing | CI (before deploy) | cosign (Sigstore) | Unsigned artifact |

### 19.2 Threat Modeling

| **Methodology** | **STRIDE per Feature** |
|---|---|
| Frequency | Every new feature or significant change |
| Artifact | Formal threat model document in `docs/threat-models/` |
| Review | Security team reviews threat model before implementation |
| Tools | OWASP Threat Dragon / Microsoft Threat Modeling Tool |

### 19.3 Security Training

| **Audience** | **Frequency** | **Content** |
|---|---|---|
| All employees | Annual | Phishing awareness, password hygiene, data handling |
| Engineering team | Bi-annual | OWASP Top 10, secure coding, threat modeling |
| Incident responders | Quarterly | Tabletop exercises, breach simulation |
| Third-party vendors | Annual | Security questionnaire, SOC 2 review |

---

## 20. Review and Governance

| **Review Cycle** | **Owner** | **Scope** |
|---|---|---|
| Monthly | Security Engineering | Vulnerability metrics, incident trends |
| Quarterly | CISO | Policy review, risk register updates |
| Annually | Board of Directors | Full security program review, audit results |
| Ad-hoc | Incident Commander | Post-incident review and process improvement |

---

*This document is maintained by the TRUE STAR BD LIMITED Security Team. All changes require CISO approval.*
