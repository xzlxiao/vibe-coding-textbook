**English** | [中文](./requirements-checklist.zh.md)

# Requirements Quality Checklist

> Usage: these are "unit tests written in natural language" (Chapter 08).
> **Ticked by the reviewer; the implementer may only submit for review.** All green yet problems in production means the checklist itself needs one more item.
> Each item answers only "yes / no". A "no" goes back upstream; do not explain here.

## A. Criterion Quality

- [ ] A1 Every criterion has an observable outlet (API field / page element / data state / log)
- [ ] A2 Every criterion has a quantified value or an enumeration, no adjectives
- [ ] A3 Every core criterion is paired with a failure path (IF ... THEN)
- [ ] A4 Only "shall / must not" throughout, never "should / may"
- [ ] A5 One criterion describes only one behavior

## B. Coverage

- [ ] B1 The six ambiguity types (reference / scope / boundary / exception / timing & concurrency / permissions & visibility) are all swept
- [ ] B2 The six constraint types (idempotency / concurrency / timeout & retry / permissions / performance / fallback) all have clauses or "not applicable + reason"
- [ ] B3 Non-goals: at least three, all decidable absences
- [ ] B4 Boundary values are all stated (0, 1, cap, cap + 1, same value, timeout)

## C. Layering and Consistency

- [ ] C1 The spec contains no framework names / table names / function names / directory structures
- [ ] C2 No new requirements appear in the plan
- [ ] C3 Every task has "what counts as passing"
- [ ] C4 Task dependencies have no cycles
- [ ] C5 Every criterion is covered by at least one task (no orphan requirements)
- [ ] C6 No two different definitions of the same concept (e.g. two readings of "full")
- [ ] C7 No "pending" item silently executed by default (if any, recorded in the pending-decision table)

## Sign-off

| Item | Content |
|---|---|
| Ticked by (reviewer) | |
| Date | |
| Failed items and handling | |
