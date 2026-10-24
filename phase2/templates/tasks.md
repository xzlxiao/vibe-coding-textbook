**English** | [中文](./tasks.zh.md)

# Task List: <领域-能力>

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

- Can run in parallel: <任务组 + 理由：不共享文件 / 无隐含契约>
- Must be serial: <任务组 + 理由>

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

<!-- converge 有缺口时只在本区块追加，不修改上面的任务 -->
