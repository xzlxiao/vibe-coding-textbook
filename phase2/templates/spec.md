**English** | [中文](./spec.zh.md)

# Feature Spec: <领域-能力>

> Usage: delete everything in angle brackets before writing. Missing one of the seven sections means this is not a spec you can start work from.
> Discipline: this file must contain no framework names, table names, function names, or directory structures (Chapter 02).

## 1. Goals and Success Metrics

- Which **metric** should this feature move, in **which direction**?
- Measurement: <指标名> from <当前值> to <目标值>, observation window <时长>

## 2. Out of Scope (Non-goals)

> At least three, and each must be a **decidable absence** (not "not supported for now").

- This round provides no <能力>; no related entry points appear in the UI or the API
- This round does not handle <场景>; in that scenario the system returns <明确结果>
- This round does not integrate <外部系统>

## 3. User Stories

| Role | Scenario | What they want | Criteria IDs |
|---|---|---|---|
| <谁> | <什么时候> | <做什么> | AC-1, AC-2 |

## 4. Acceptance Criteria (EARS)

> One behavior per criterion. Include trigger conditions and failure paths. Use only "shall / must not" throughout, never "should / may".

- AC-1 [Ubiquitous] The system shall validate <条件> for <对象>.
- AC-2 [Event-driven] When <触发事件> occurs, the system shall <响应> within <时限>.
- AC-3 [State-driven] While <状态> holds, the system shall <行为>.
- AC-4 [Unwanted] If <异常条件>, then the system shall <恢复/拒绝行为>.
- AC-5 [Optional] When <特性开关> is enabled, the system shall <行为>.

## 5. Constraints

> Go through all six types one by one: idempotency / concurrency / timeout & retry / permissions & visibility / performance budget / dependencies & fallback.
> For ones that do not apply, write "not applicable + reason"; do not leave them blank.

| ID | Constraint | Verification |
|---|---|---|
| C1 | All write endpoints must carry `idempotency_key`; duplicate requests return the first result | <脚本/用例> |
| C2 | <并发要求> | <压测方式> |
| C3 | <重试与降级要求> | <故障注入方式> |
| C4 | Permissions deny by default; list-level and field-level rules | <三角色测试> |
| C5 | p95 / p99 + environment + data volume | <压测报告> |
| C6 | <依赖降级要求> | <开关验证> |

## 6. Data and Interface Contracts

| Field | Type | Nullable | Meaning |
|---|---|---|---|
| <field> | <type> | No | <语义> |

Error codes:

| code | HTTP | Meaning | What the client should do |
|---|---|---|---|
| <CODE> | 4xx | <含义> | <提示/重试/放弃> |

## 7. Failure Semantics

| Failure point | User sees | System leaves behind | Retryable |
|---|---|---|---|
| <依赖超时> | <提示> | <日志/队列状态> | Yes / No |

---

<!-- 变更记录：每次改判据，写一行 -->
<!-- 2026-01-01 初版 -->
