**English** | [中文](./tasks.zh.md)

# Task List: <domain-capability>

> Usage: every task must state in one sentence "what counts as passing" (Chapter 07).
> One task = one review unit = one revertible commit.

## Task Table

| ID | Task | Acceptance method (what counts as passing) | Dependencies | Blast radius | Batch |
|---|---|---|---|---|---|
| T1 | | | none | | 1 |
| T2 | | | T1 | | 1 |
| T3 | | | T1 | | 2 |

## Dependency Graph

```text
T1 → T2 → T3
        ↘ T4
```

## Parallelism Boundaries

- Can run in parallel: <task group + reason: no shared files / no hidden contracts>
- Must be serial: <task group + reason>

## Batch Plan

| Batch | Contains tasks | What can be demoed at the end |
|---|---|---|
| 1 | | |
| 2 | | |

## Coverage Check

> Every criterion must be covered by at least one task; otherwise it is an orphan requirement.

| Criterion | Covering task |
|---|---|
| AC-1 | T2 |

## Convergence (appended by converge; do not write by hand)

<!-- when converge finds gaps, only append in this block; do not edit the tasks above -->
