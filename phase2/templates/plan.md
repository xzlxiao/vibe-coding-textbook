**English** | [中文](./plan.zh.md)

# Implementation Plan: <领域-能力>

> Usage: write How only. Any "the user should be able to..." is a new requirement - send it back to the spec (Chapter 02).
> Reader: the implementer (human or AI). Framework names, table names, and function names may appear here.

## 1. Approach and Choices

| Decision point | Choice | Rationale | Rejected options and why |
|---|---|---|---|
| Storage | | | |
| Concurrency control | | | |
| Async / queue | | | |

## 2. Data Model

```text
<表/集合名>
  <字段>  <类型>  <约束>  <说明>
索引：<索引名> on (<字段>) where <条件>
```

## 3. Interface Contract

```text
POST /<path>
  header: Idempotency-Key (required)
  body:   { ... }
  200:    { ... }
  4xx:    { code, message }
```

## 4. Key Flows

- Main path: <步骤 1 → 2 → 3>
- Failure path: <在哪一步失败，回退到哪个状态>

## 5. Mapping to the Spec

| Criterion | Implemented by | Risk |
|---|---|---|
| AC-1 | | |
| AC-2 | | |

> This column must be filled completely. A criterion you cannot place means the approach is not thought through.

## 6. Risks and Rollback

| Risk | Trigger | Mitigation | Rollback action |
|---|---|---|---|
| | | | |

## 7. Not Solved This Time

<明确写出"知道但这次不做"的技术债，避免它变成隐形假设>
