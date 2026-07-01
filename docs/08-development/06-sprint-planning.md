# Sprint Planning Guide

## TRUE STAR BD LIMITED — Digital Marketplace Platform

| Document ID | SPRINT-TSBL-001 |
|---|---|
| Version | 1.0 |
| Date | July 1, 2026 |
| Author | Software Architecture Division |
| Status | Approved |
| Classification | Internal — Confidential |

---

## Table of Contents

1. [Sprint Cadence](#1-sprint-cadence)
2. [Sprint Ceremonies](#2-sprint-ceremonies)
3. [Story Point Estimation](#3-story-point-estimation)
4. [Sprint Capacity Planning](#4-sprint-capacity-planning)
5. [Definition of Ready (DoR)](#5-definition-of-ready-dor)
6. [Definition of Done (DoD)](#6-definition-of-done-dod)
7. [Sprint Backlog Management](#7-sprint-backlog-management)
8. [Velocity Tracking](#8-velocity-tracking)
9. [Burndown Chart Expectations](#9-burndown-chart-expectations)
10. [Sample Sprint Plan: First 4 Sprints](#10-sample-sprint-plan-first-4-sprints)
11. [Role Responsibilities](#11-role-responsibilities)

---

## 1. Sprint Cadence

The project operates on a **2-week sprint cycle** with the following schedule:

| Sprint Element | Duration | Schedule |
|---|---|---|
| Sprint Length | 14 calendar days | Monday 10:00 AM to Friday 5:00 PM (Week 2) |
| Planning Day | Sprint Day 1 | Monday, Week 1 |
| Development | Days 2–10 | Tuesday (W1) to Thursday (W2) |
| Review + Retrospective | Sprint Day 13 | Friday, Week 2 (morning) |
| Buffer / Bug Fixing | Sprint Day 14 | Friday, Week 2 (afternoon) |
| Next Sprint Planning | Sprint Day 14 | Friday, Week 2 (after review) |

### 1.1 Sprint Numbering Convention

Sprints are numbered sequentially: `Sprint <number>` (e.g., Sprint 1, Sprint 2). Each sprint ID includes the project prefix and phase:

```
TSBL-S<number>-<phase-code>
Example: TSBL-S04-FND (Sprint 4, Foundation phase)
         TSBL-S08-CORE (Sprint 8, Core Marketplace phase)
```

### 1.2 Calendar Exclusions

| Exclusion | Policy |
|---|---|
| Public Holidays | Sprint paused; days added to sprint end date |
| Team Leave | Planned leave accounted for in capacity; unplanned leave triggers replanning |
| Production Incidents | Sprint frozen at Scrum Master's discretion; resumption after incident resolved |

---

## 2. Sprint Ceremonies

### 2.1 Ceremony Schedule

| Ceremony | Duration | Frequency | Participants |
|---|---|---|---|
| Daily Standup | 15 minutes | Daily | Dev Team, Scrum Master, Product Owner (optional) |
| Sprint Planning | 2–4 hours | Every sprint start | Dev Team, Scrum Master, Product Owner |
| Sprint Review | 1–2 hours | Every sprint end | Dev Team, Scrum Master, Product Owner, Stakeholders |
| Sprint Retrospective | 1–1.5 hours | Every sprint end | Dev Team, Scrum Master |
| Backlog Refinement | 1–2 hours | Weekly (mid-sprint) | Product Owner, Scrum Master, Tech Lead |
| Product Owner Sync | 30 minutes | Daily | Product Owner, Scrum Master |

### 2.2 Daily Standup Protocol

| Element | Detail |
|---|---|
| **Time** | 9:30 AM BDT (UTC+6), every working day |
| **Format** | Three questions: What did I do yesterday? What will I do today? Any blockers? |
| **Location** | Video call (remote team members); physical board room (co-located) |
| **Tool** | Jira board visible; ticket status walk-through encouraged |
| **Blockers** | Escalated to Scrum Master immediately; not left for after standup |
| **Duration** | Strictly 15 minutes; detailed discussions deferred to breakouts |

### 2.3 Sprint Planning Structure

| Segment | Duration | Activities |
|---|---|---|
| Capacity Review | 15 min | Review team availability, velocity trend, leave calendar |
| Sprint Goal Definition | 30 min | Product Owner presents prioritized items; team agrees on sprint goal |
| Story Selection | 60–90 min | Team pulls stories from backlog top; estimates refined if needed |
| Task Breakdown | 45–60 min | Stories decomposed into tasks (hours); initial assignments noted |
| Risk Check | 15 min | Identify potential blockers; agree on mitigation strategies |
| Commitment | 15 min | Team commits to sprint scope; sprint goal finalized |

### 2.4 Sprint Review Structure

| Segment | Duration | Activities |
|---|---|---|
| Sprint Goal Recap | 10 min | Scrum Master restates sprint goal |
| Demo | 45–60 min | Team demonstrates completed stories; stakeholders provide feedback |
| Metrics Review | 15 min | Velocity, burndown, defect rate, test coverage |
| Backlog Update | 15 min | Product Owner adjusts backlog based on feedback |
| Q&A | 15 min | Open floor for stakeholder questions |

### 2.5 Sprint Retrospective Structure

| Segment | Duration | Format |
|---|---|---|
| Data Gathering | 20 min | What went well? What could be improved? What confused us? |
| Insights | 20 min | Group themes; vote on top 3 items to address |
| Action Items | 15 min | Define 1–3 actionable improvements with owners |
| Close | 5 min | Review previous retrospective action items |

---

## 3. Story Point Estimation

### 3.1 Estimation Scale

The team uses the **Fibonacci sequence** for relative estimation:

| Points | Effort | Complexity | Uncertainty | Typical Examples |
|---|---|---|---|---|
| 1 | Trivial | None | None | Bug fix (one-line), CSS tweak, config change |
| 2 | Small | Low | Low | Simple API endpoint, form field addition |
| 3 | Medium | Moderate | Low | CRUD screen, database migration, email template |
| 5 | Large | Moderate | Medium | Multi-step workflow, integration with external API |
| 8 | Very Large | High | Medium | New feature module, payment gateway integration |
| 13 | Extra Large | High | High | Complex cross-cutting feature; requires research |
| 21 | Too Large | — | — | Must be split into smaller stories |

### 3.2 Estimation Guidelines

| Rule | Description |
|---|---|
| Relative not absolute | A 5-point story is larger than a 3-point story; no correlation to hours |
| Team consensus | Estimates are derived via Planning Poker or fist-of-five |
| Include all activities | Points include development, testing, documentation, and deployment |
| Exclude ceremony | Points exclude standups, reviews, retrospectives, and meetings |
| Re-estimate if split | When a story is split, each new story receives its own estimate |
| No partial points | All estimates must be whole Fibonacci numbers |
| Spikes are time-boxed | Research spikes estimated in hours (max 8 hours), not story points |

### 3.3 Planning Poker Protocol

1. Product Owner presents story and acceptance criteria
2. Team discusses requirements (5 minutes max per story)
3. Each member selects a point card privately
4. Cards revealed simultaneously
5. If consensus (same number or adjacent): use the higher number
6. If deviation > 2 steps: high and low estimators justify reasoning
7. Re-vote after discussion (max 2 rounds)
8. If no consensus after 2 rounds: Tech Lead makes final call

---

## 4. Sprint Capacity Planning

### 4.1 Capacity Calculation Formula

```
Team Capacity (hours) = Σ (Individual Available Hours)
Individual Available Hours = (Sprint Working Days × 6.5 productive hours) - (Leave Hours + Ceremony Hours)
```

### 4.2 Default Capacity Parameters

| Parameter | Value |
|---|---|
| Working days per sprint | 10 days (2 weeks) |
| Productive hours per day | 6.5 hours (after subtracting meetings, email, breaks) |
| Ceremony hours per sprint | ~6 hours (standups 2.5h + planning 3h + review 1h + retro 1h) |
| Buffer for unplanned work | 15% of capacity |
| Target utilization | 85% of net capacity |

### 4.3 Sample Capacity Table

| Role | Days | Productive Hours/Day | Ceremony Hours | Leave Hours | Buffer | **Net Hours** |
|---|---|---|---|---|---|---|
| Backend Engineer | 10 | 6.5 | 6 | 0 | 7.5 | **51.5** |
| Frontend Engineer | 10 | 6.5 | 6 | 4 (training) | 7.5 | **47.5** |
| QA Engineer | 10 | 6.5 | 6 | 0 | 7.5 | **51.5** |
| **Team Capacity** | — | — | — | — | — | **~150** |

### 4.4 Points-to-Hours Conversion Reference

| Story Points | Typical Hours Range | Notes |
|---|---|---|
| 1 | 2–4 | Trivial change |
| 2 | 4–8 | Simple change |
| 3 | 8–16 | Moderate effort |
| 5 | 16–32 | Complex feature |
| 8 | 32–50 | Large feature |
| 13 | 50–80 | Very large (should be split) |

**Rule of thumb:** A team with a velocity of 30 points/sprint typically delivers 180–240 hours of work.

---

## 5. Definition of Ready (DoR)

A user story must satisfy **all** the following criteria before it can be pulled into a sprint:

### 5.1 DoR Checklist

| # | Criterion | Owner | Verifiable |
|---|---|---|---|
| 1 | User story follows the standard format: "As a [user], I want [goal] so that [benefit]" | PO | Yes |
| 2 | Acceptance criteria are written in Given-When-Then (Gherkin) format | PO | Yes |
| 3 | Acceptance criteria are clear, testable, and unambiguous | PO + QA | Yes |
| 4 | All non-functional requirements are specified (performance, security, accessibility) | PO | Yes |
| 5 | UI/UX mockups or wireframes are attached and approved | Designer | Yes |
| 6 | API contract or interface specification is defined (if applicable) | Tech Lead | Yes |
| 7 | Dependencies on other stories, systems, or teams are identified | PO + Tech Lead | Yes |
| 8 | Story is estimated in story points (team consensus) | Dev Team | Yes |
| 9 | Story is small enough to be completed within one sprint (≤ 8 points) | Dev Team | Yes |
| 10 | Acceptance criteria are reviewed and understood by at least one QA engineer | QA | Yes |
| 11 | Edge cases and error states are described | PO + QA | Yes |
| 12 | Security implications are considered (if applicable) | Security Eng | Yes |
| 13 | Database schema changes are documented (if applicable) | Tech Lead | Yes |
| 14 | Third-party service integration requirements are known | PO + Tech Lead | Yes |

### 5.2 DoR Violation Protocol

| Violation | Action |
|---|---|
| Missing acceptance criteria | Story returned to Product Owner; not eligible for sprint |
| No mockups for UI stories | Story deferred; designer must complete before next refinement |
| Story > 8 points | Must be split before sprint planning |
| Unknown dependencies | Spike required before inclusion in sprint |

---

## 6. Definition of Done (DoD)

A user story is considered **Done** only when **all** the following criteria are satisfied:

### 6.1 DoD Checklist

| # | Criterion | Verification Method |
|---|---|---|
| **Code Quality** | | |
| 1 | Code compiles without errors | CI pipeline |
| 2 | All linting rules pass (ESLint, PSR-12, etc.) | CI pipeline |
| 3 | Code follows project coding standards | Code review |
| 4 | No hardcoded secrets or credentials | Secret scan |
| 5 | No debug code, commented-out code, or `TODO` placeholders | Code review |
| 6 | Code is reviewed and approved by at least one peer | PR approval |
| **Testing** | | |
| 7 | Unit tests written and passing (coverage > 80%) | CI pipeline |
| 8 | Integration tests written and passing | CI pipeline |
| 9 | All existing tests continue to pass | CI pipeline |
| 10 | Acceptance criteria are verified (manual or automated) | QA sign-off |
| 11 | Edge cases and error states are tested | QA sign-off |
| 12 | Accessibility checks pass (if UI change) | Axe/Lighthouse |
| **Documentation** | | |
| 13 | API documentation is updated (if API change) | OpenAPI spec |
| 14 | README or relevant docs are updated | Code review |
| 15 | Database migration script is included (if applicable) | Code review |
| 16 | Rollback script exists for the migration | Code review |
| **Deployment** | | |
| 17 | Feature is deployed to staging environment | CI/CD pipeline |
| 18 | Smoke tests pass on staging | QA sign-off |
| 19 | Feature flag is configured (if applicable) | Code review |
| 20 | Monitoring and alerting are configured (if new service) | DevOps review |
| **Business** | | |
| 21 | Product Owner accepts the story | Demo sign-off |
| 22 | Release notes are drafted (if included in upcoming release) | PO |

### 6.2 DoD Exceptions

| Exception | Approval Required |
|---|---|
| Documentation deferred (tech debt tracked) | Tech Lead + PO |
| Test coverage below threshold (justified) | Tech Lead + QA Lead |
| Accessibility issue pre-existing | PO accepts known limitation |

---

## 7. Sprint Backlog Management

### 7.1 Backlog Hierarchy

```
Product Backlog
  ├── Epics (large initiatives, multiple sprints)
  │     └── User Stories (sprint-sized work items)
  │           ├── Tasks (developer breakdown, hours)
  │           └── Acceptance Criteria (Given/When/Then)
  ├── Bugs (defects found during testing or production)
  ├── Technical Debt (refactoring, performance improvements)
  └── Spikes (research, prototyping, time-boxed)
```

### 7.2 Backlog Prioritization

The Product Owner maintains backlog priority using the **WSJF** (Weighted Shortest Job First) model:

```
WSJF = Value + Time Criticality + Risk Reduction / Job Size
```

| Factor | Definition | Scale |
|---|---|---|
| Value | Business value delivered to users or stakeholders | 1–5 |
| Time Criticality | Urgency; how quickly value decays | 1–5 |
| Risk Reduction | Reduction in project risk or technical uncertainty | 1–5 |
| Job Size | Relative effort (story points) | 1–13 |

### 7.3 Sprint Backlog Composition Guidelines

| Element | Recommended % | Notes |
|---|---|---|
| New Features | 60–70% | Primary sprint goal |
| Bugs | 10–20% | Prioritized by severity |
| Technical Debt | 10–15% | Allocated every sprint |
| Spikes | 5–10% | As needed for upcoming work |

### 7.4 Sprint Backlog Rules

| Rule | Detail |
|---|---|
| No late additions | Once sprint starts, no new stories added without Scrum Master approval |
| Swapping allowed | Low-priority story may be swapped for high-priority if capacity allows |
| Unfinished work | Returns to product backlog with updated estimate; not carried over automatically |
| Bug priority | P1 (critical) bugs freeze sprint; P2 (high) bugs must be added if discovered |
| Capacity buffer | Reserve 15% for unplanned work; do not over-commit |

### 7.5 Jira Workflow States

```
To Do → In Refinement → Ready for Sprint → In Progress → In Review → Done
                                                              ↓
                                                        In Testing
                                                              ↓
                                                        (merge to Done)
```

| State | Description | Responsible |
|---|---|---|
| To Do | New items awaiting triage | PO |
| In Refinement | Being detailed with acceptance criteria | PO + Tech Lead |
| Ready for Sprint | Fully refined, estimated, meets DoR | PO |
| In Progress | Developer actively working | Dev Team |
| In Review | Code review in progress | Reviewer |
| In Testing | QA validation in progress | QA Engineer |
| Done | Meets DoD, accepted by PO | PO |

---

## 8. Velocity Tracking

### 8.1 Velocity Calculation

```
Sprint Velocity = Sum of story points for completed stories in the sprint
```

### 8.2 Velocity Metrics

| Metric | Calculation | Purpose |
|---|---|---|
| Sprint Velocity | Points completed this sprint | Current period tracking |
| Moving Average | Average of last 3 sprints | Capacity planning |
| Forecast Velocity | Moving average × confidence factor (0.85) | Release planning |
| Velocity Trend | Linear regression of last 6 sprints | Identify improvement/degradation |

### 8.3 Velocity Expectations by Phase

| Phase | Expected Sprint Velocity | Notes |
|---|---|---|
| Phase 0 (Foundation) | 15–25 points/sprint | Setup heavy; low initial velocity |
| Phase 1 (Core Marketplace) | 20–30 points/sprint | Team ramping up |
| Phase 2–3 | 25–35 points/sprint | Stable team, established patterns |
| Phase 4–6 | 30–40 points/sprint | Optimized team velocity |

### 8.4 Velocity Adjustment Rules

| Situation | Action |
|---|---|
| Team member added | Reduce expected velocity for 2 sprints (ramp-up) |
| Team member lost | Reduce capacity proportionally for next sprint |
| New framework/technology | Expect 20% velocity reduction for 1–2 sprints |
| Holiday period | Reduce capacity proportionally |
| Production support duty | Reduce capacity by 10% during support rotation |

---

## 9. Burndown Chart Expectations

### 9.1 Chart Type

The team uses a **Sprint Burndown Chart** showing remaining work (in story points) on the Y-axis versus sprint days on the X-axis.

### 9.2 Ideal Burndown Line

```
Day 0:  Total sprint commitment (e.g., 30 points)
Day 10: 0 points (all stories complete)

Equation: remaining_points = committed_points × (1 - day / sprint_days)
```

### 9.3 Acceptable Variance

| Zone | Variance from Ideal | Action Required |
|---|---|---|
| Green | Within ±10% | No action; team on track |
| Amber | 10–25% above ideal | Scrum Master investigates; pair programming or scope review |
| Red | > 25% above ideal | Sprint replanning triggered; PO involvement required |

### 9.4 Burndown Patterns

| Pattern | Interpretation | Response |
|---|---|---|
| Steady decline | Healthy sprint; good estimation | Maintain course |
| Flat start (days 1–2) | Analysis/design phase; tasks not yet started | Normal; expect drop after day 3 |
| Late drop (days 7–9) | Stories completed late in sprint | Review for blocker patterns |
| Plateau mid-sprint | Blocked story or unclear requirements | Unblock immediately; escalate if needed |
| Upward trend | Scope added mid-sprint | Enforce scope freeze; document new items |
| Never reaches zero | Incomplete stories | Update backlog; discuss in retrospective |

### 9.5 Burndown Update Responsibility

| Update | Frequency | Responsible |
|---|---|---|
| Task status updates | Daily (by standup) | Each team member |
| Story completion | When PR merged + QA signed off | Developer |
| Chart review | Daily during standup | Scrum Master |

---

## 10. Sample Sprint Plan: First 4 Sprints

### 10.1 Sprint 1: Foundation & Scaffolding

| Attribute | Detail |
|---|---|
| **Sprint ID** | TSBL-S01-FND |
| **Phase** | Phase 0 — Foundation |
| **Duration** | W1 Mon – W2 Fri |
| **Velocity Target** | 15 points |
| **Sprint Goal** | Establish project scaffold, CI/CD, and development environment |

| Story ID | Story Title | Points | Assigned To |
|---|---|---|---|
| FND-01 | Scaffold mono-repo with folder structure and build configuration | 3 | TL |
| FND-02 | Set up CI/CD pipeline with build, lint, test, and deploy stages | 5 | DevOps |
| FND-03 | Create Docker Compose development environment | 5 | DevOps |
| FND-04 | Implement API health check and error handling middleware | 2 | BE-1 |
| FND-05 | Set up ESLint, Prettier, and Husky pre-commit hooks | 1 | FE-1 |
| FND-06 | Create contribution guide and pull request template | 1 | TL |
| **Total** | | **17** | — |

### 10.2 Sprint 2: Auth & Data Layer

| Attribute | Detail |
|---|---|
| **Sprint ID** | TSBL-S02-FND |
| **Phase** | Phase 0 — Foundation |
| **Duration** | W3 Mon – W4 Fri |
| **Velocity Target** | 18 points |
| **Sprint Goal** | Implement authentication service and database foundation |

| Story ID | Story Title | Points | Assigned To |
|---|---|---|---|
| FND-07 | Design and implement user schema and migration system | 3 | BE-1 |
| FND-08 | Implement registration endpoint with email verification | 5 | BE-2 |
| FND-09 | Implement login endpoint with JWT token issuance | 3 | BE-2 |
| FND-10 | Create RBAC roles and permissions data model | 3 | BE-1 |
| FND-11 | Build login and registration UI screens | 5 | FE-1 |
| FND-12 | Implement password reset flow (API + UI) | 3 | BE-2, FE-1 |
| **Total** | | **22** | — |

### 10.3 Sprint 3: Core Catalog & Design System

| Attribute | Detail |
|---|---|
| **Sprint ID** | TSBL-S03-CORE |
| **Phase** | Phase 1 — Core Marketplace |
| **Duration** | W7 Mon – W8 Fri |
| **Velocity Target** | 20 points |
| **Sprint Goal** | Deliver product catalog with design system integration |

| Story ID | Story Title | Points | Assigned To |
|---|---|---|---|
| FND-13 | Complete UI component library (buttons, forms, cards, modals) | 5 | FE-1, Designer |
| CORE-01 | Implement category tree CRUD API | 3 | BE-1 |
| CORE-02 | Implement product CRUD API with media support | 5 | BE-2 |
| CORE-03 | Build product listing page with category filter | 5 | FE-2 |
| CORE-04 | Build product detail page with image gallery | 3 | FE-2 |
| CORE-05 | Implement product search endpoint with basic full-text search | 3 | BE-1 |
| **Total** | | **24** | — |

### 10.4 Sprint 4: Cart & Checkout

| Attribute | Detail |
|---|---|
| **Sprint ID** | TSBL-S04-CORE |
| **Phase** | Phase 1 — Core Marketplace |
| **Duration** | W9 Mon – W10 Fri |
| **Velocity Target** | 22 points |
| **Sprint Goal** | Enable buyers to add products to cart and complete checkout |

| Story ID | Story Title | Points | Assigned To |
|---|---|---|---|
| CORE-06 | Implement persistent shopping cart (API + Redis) | 5 | BE-1 |
| CORE-07 | Build cart UI with add/remove/update and badge | 5 | FE-1 |
| CORE-08 | Implement coupon validation and application in cart | 3 | BE-2 |
| CORE-09 | Build multi-step checkout flow UI | 5 | FE-2 |
| CORE-10 | Implement order creation on checkout completion | 5 | BE-2 |
| CORE-11 | Generate confirmation page and email receipt | 3 | FE-2, BE-1 |
| **Total** | | **26** | — |

---

## 11. Role Responsibilities

### 11.1 Product Owner (PO)

| Responsibility | Description | Frequency |
|---|---|---|
| Vision & Strategy | Define and communicate product vision and roadmap | Ongoing |
| Backlog Management | Maintain, prioritize, and refine the product backlog | Daily |
| User Story Creation | Write stories with clear acceptance criteria | Per story |
| Stakeholder Management | Gather requirements, manage expectations, communicate progress | Weekly |
| Acceptance | Accept or reject completed stories at sprint review | Per sprint |
| Release Planning | Define release scope, timeline, and go/no-go criteria | Per release |
| Value Maximization | Ensure team is working on highest-value items | Ongoing |

**Authority:** The Product Owner is the single point of authority for backlog prioritization. No one else may direct the team to work on different items.

### 11.2 Scrum Master (SM)

| Responsibility | Description | Frequency |
|---|---|---|
| Process Facilitation | Facilitate all Scrum ceremonies | Per sprint |
| Impediment Removal | Remove or escalate blockers preventing team progress | Daily |
| Coaching | Coach team on Scrum practices and agile principles | Ongoing |
| Progress Tracking | Track sprint progress, velocity, burndown | Daily |
| Continuous Improvement | Drive retrospective action item implementation | Per sprint |
| Shield Team | Protect team from external interruptions and scope creep | Ongoing |
| Tool Administration | Maintain Jira configuration, boards, dashboards | As needed |

**Authority:** The Scrum Master has no authority over the team's technical decisions but has authority over process adherence.

### 11.3 Development Team (Dev Team)

| Responsibility | Description | Frequency |
|---|---|---|
| Technical Implementation | Design, code, test, and deliver high-quality software | Daily |
| Estimation | Provide effort estimates for user stories | Per sprint |
| Self-Organization | Decide how to accomplish sprint work; assign tasks | Per sprint |
| Quality Ownership | Write tests, perform code reviews, maintain code quality | Daily |
| Technical Decisions | Make implementation decisions within architectural guidelines | Ongoing |
| Continuous Learning | Stay current with technology, share knowledge within team | Ongoing |
| Participation | Attend all ceremonies, contribute to retrospectives | Per sprint |

**Authority:** The Development Team has full authority over how to implement the work within the sprint. No external party may dictate technical implementation details.

### 11.4 Tech Lead (Embedded in Dev Team)

| Responsibility | Description | Frequency |
|---|---|---|
| Architecture Oversight | Ensure technical decisions align with architectural vision | Ongoing |
| Code Quality Standards | Define and enforce coding standards, review practices | Ongoing |
| Technical Spikes | Lead research and prototyping for uncertain technologies | As needed |
| Mentoring | Guide junior developers; facilitate pair programming | Ongoing |
| Cross-Team Coordination | Align with other teams on interfaces and integration points | As needed |
| Tech Debt Management | Identify, track, and prioritize technical debt | Per sprint |

### 11.5 QA Engineer (Embedded in Dev Team)

| Responsibility | Description | Frequency |
|---|---|---|
| Test Strategy | Define test approach for each story | Per sprint |
| Test Execution | Execute manual and automated tests | Daily |
| Bug Reporting | Log defects with clear reproduction steps | As found |
| Acceptance Criteria Validation | Verify stories meet acceptance criteria | Per story |
| Automation | Write and maintain automated test suite | Ongoing |
| Regression Testing | Ensure new changes don't break existing functionality | Per sprint |

---

## Appendix A: Sprint Ceremony Calendar (Template)

| Day | Time | Ceremony | Duration | Participants |
|---|---|---|---|---|
| Monday | 9:30–9:45 | Daily Standup | 15 min | Full Team |
| Monday | 10:00–12:00 | Sprint Planning (W1 only) | 2–4 hrs | Full Team |
| Tuesday–Thursday | 9:30–9:45 | Daily Standup | 15 min | Dev + SM |
| Wednesday | 10:00–11:00 | Backlog Refinement | 1 hr | PO + SM + TL |
| Friday (W2) | 9:30–9:45 | Daily Standup | 15 min | Full Team |
| Friday (W2) | 10:00–11:30 | Sprint Review | 1.5 hrs | Full Team + Stakeholders |
| Friday (W2) | 11:30–12:30 | Sprint Retrospective | 1 hr | Dev + SM |
| Friday (W2) | 14:00–16:00 | Next Sprint Planning | 2 hrs | Full Team |

## Appendix B: Story Point Reference Card

```
Fibonacci Estimation Quick Reference

1  = Simple config change, typo fix
2  = Single endpoint, small UI change
3  = CRUD resource, migration, form
5  = Multi-step flow, 3rd-party integration
8  = Complex feature, cross-cutting concern
13 = Too big - split it!
```

---

*End of Document — SPRINT-TSBL-001*
