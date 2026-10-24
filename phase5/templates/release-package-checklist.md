**English** | [中文](./release-package-checklist.zh.md)

# Launch Package Checklist

> Launch date: __________　Version: __________　Owner: __________
> Rules: blocking items (marked ★) must all pass before launch; non-blocking items may ship with gaps, but must be written into the first week's to-do list.

## 1. Can Retreat

- [ ] ★ R1 The previous release can be rolled back with one command (verify: run it once in staging and time it)
- [ ] ★ R2 Database migrations are rollback-capable or already forward-compatible (verify: no DROP / type changes in the scripts)
- [ ] ★ R3 The previous image is retained ≥ 7 days (verify: check the retention policy)
- [ ] R4 Feature flags can turn new features off without a release (verify: after turning it off, the old path works)

## 2. Can See

- [ ] ★ O1 The four golden signals are on the dashboard (verify: open the panel, all four charts have data)
- [ ] ★ O2 Error-rate alerts reach you within 5 minutes (verify: induce one 5xx and time it)
- [ ] O3 Per-request cost can be looked up in the logs
- [ ] O4 Upstream timeouts have a dedicated alert
- [ ] O5 There is a daily summary of "how much we spent today"

## 3. Has a Fallback

- [ ] ★ B1 The backup job succeeded in the last 24 hours (verify: a success record in the log and size > 1MB)
- [ ] ★ B2 A recovery drill has been run and the RTO recorded
- [ ] ★ B3 There is a degradation strategy when the model API is unavailable (verify: unplug the upstream and see what users see)
- [ ] B4 Payment failures show a clear message and offer retry

## 4. Can Explain

- [ ] ★ L1 The pricing page states the billing unit and period
- [ ] ★ L2 Auto-renewal is prominently noted 5 days before the charge
- [ ] ★ L3 The cancel-subscription entry is no more than two levels deep
- [ ] ★ L4 There is a refund policy and contact information
- [ ] ★ L5 AI interactions carry a "this is AI" disclosure
- [ ] L6 Generated content carries labels
- [ ] ★ L7 The model name and filing number/launch number are publicly listed

## 5. The First 24 Hours After Launch

- [ ] Make no non-essential changes
- [ ] Check the dashboard once every 2 hours
- [ ] Record day one: request count / error rate / per-request cost / new paying users

## 6. First-Week To-Do (Non-Blocking Items)

| Item | Owner | Target date |
| :--- | :--- | :--- |
|  |  |  |
|  |  |  |

## 7. Conclusion

- Blocking items unpassed: ____ items → launch date adjusted to: __________
- Conclusion: can launch / postpone (pick one; do not write "we'll try")
