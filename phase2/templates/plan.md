**English** | [中文](./plan.zh.md)

# Implementation Plan: <domain-capability>

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
<table/collection-name>
  <field>  <type>  <constraint>  <description>
Index: <index-name> on (<field>) where <condition>
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

- Main path: <step 1 → 2 → 3>
- Failure path: <which step fails, which state to fall back to>

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

<Write out the tech debt you know about but are deliberately not doing this round, so it does not become a hidden assumption>
