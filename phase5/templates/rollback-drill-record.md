**English** | [中文](./rollback-drill-record.zh.md)

# Rollback Drill Record

> Drill date: __________　Environment: __________　Executor: __________
> Criterion: all four segment timings meet target, and the "sticking points" have been rewritten into executable checklist items.

## 1. Drill Setup

| Item | Content |
| :--- | :--- |
| Injected defect |  |
| Affected user path |  |
| Involves database writes? | Yes / No |
| Involves irreversible migrations? | Yes / No |

## 2. Five Moments

| Moment | Time | Notes |
| :--- | :--- | :--- |
| T1 release complete |  |  |
| T2 detected |  | Who detected it: alert / user / yourself |
| T3 rollback decided |  | Who decided |
| T4 previous version usable |  |  |
| T5 verification passed |  |  |

## 3. Four Segment Timings and Verdict

| Segment | Calculation | Measured | Target | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| Detect | T2 − T1 |  | 5 min |  |
| Decide | T3 − T2 |  | 5 min |  |
| Execute | T4 − T3 |  | 3 min |  |
| Verify | T5 − T4 |  | 10 min |  |
| Total | T5 − T1 |  | — |  |

## 4. Sticking Points and Fixes

| # | Where it stuck | Root cause | Fix | Which checklist item it lands on |
| :--- | :--- | :--- | :--- | :--- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

## 5. Write Back to the Repository

- [ ] Rollback script updated; the command runs as a single line
- [ ] Image retention ≥ 7 days, and verified
- [ ] Migration scripts confirmed free of DROP / type changes (if any, scheduled separately)
- [ ] Checklist R1–R3 checked

## 6. Next Drill

- Date: __________
- New items to verify: __________
