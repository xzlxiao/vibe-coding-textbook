**English** | [中文](./spec.zh.md)

# Feature Spec: <domain-capability>

> Usage: delete everything in angle brackets before writing. Missing one of the seven sections means this is not a spec you can start work from.
> Discipline: this file must contain no framework names, table names, function names, or directory structures (Chapter 02).

## 1. Goals and Success Metrics

- Which **metric** should this feature move, in **which direction**?
- Measurement: <metric-name> from <current-value> to <target-value>, observation window <duration>

## 2. Out of Scope (Non-goals)

> At least three, and each must be a **decidable absence** (not "not supported for now").

- This round provides no <capability>; no related entry points appear in the UI or the API
- This round does not handle <scenario>; in that scenario the system returns <explicit-result>
- This round does not integrate <external-system>

## 3. User Stories

| Role | Scenario | What they want | Criteria IDs |
|---|---|---|---|
| <who> | <when> | <what> | AC-1, AC-2 |

## 4. Acceptance Criteria (EARS)

> One behavior per criterion. Include trigger conditions and failure paths. Use only "shall / must not" throughout, never "should / may".

- AC-1 [Ubiquitous] The system shall validate <condition> for <object>.
- AC-2 [Event-driven] When <trigger-event> occurs, the system shall <response> within <time-limit>.
- AC-3 [State-driven] While <state> holds, the system shall <behavior>.
- AC-4 [Unwanted] If <exception-condition>, then the system shall <recover/reject-behavior>.
- AC-5 [Optional] When <feature-flag> is enabled, the system shall <behavior>.

## 5. Constraints

> Go through all six types one by one: idempotency / concurrency / timeout & retry / permissions & visibility / performance budget / dependencies & fallback.
> For ones that do not apply, write "not applicable + reason"; do not leave them blank.

| ID | Constraint | Verification |
|---|---|---|
| C1 | All write endpoints must carry `idempotency_key`; duplicate requests return the first result | <script/test-case> |
| C2 | <concurrency-requirement> | <load-test-method> |
| C3 | <retry-and-degradation-requirement> | <fault-injection-method> |
| C4 | Permissions deny by default; list-level and field-level rules | <three-role-test> |
| C5 | p95 / p99 + environment + data volume | <load-test-report> |
| C6 | <dependency-degradation-requirement> | <flag-verification> |

## 6. Data and Interface Contracts

| Field | Type | Nullable | Meaning |
|---|---|---|---|
| <field> | <type> | No | <semantics> |

Error codes:

| code | HTTP | Meaning | What the client should do |
|---|---|---|---|
| <CODE> | 4xx | <meaning> | <prompt/retry/give-up> |

## 7. Failure Semantics

| Failure point | User sees | System leaves behind | Retryable |
|---|---|---|---|
| <dependency-timeout> | <prompt> | <log/queue-state> | Yes / No |

---

<!-- Change log: one line per criterion change -->
<!-- 2026-01-01 first version -->
