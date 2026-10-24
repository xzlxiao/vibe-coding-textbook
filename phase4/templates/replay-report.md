**English** | [中文](./replay-report.zh.md)

# Logged-Out Replay Test Report Template

> How to use: run all three steps before filling it in. **Do not merge the conclusions of the three steps** — passing step 2 only shows that strangers cannot get in; step 3 answers "can those who got in see each other".
> The test only reads, never writes; when you get "compromised", revoke the key first, then fill in the form.

## System and environment

| Item | Fill in |
|---|---|
| System name | |
| Test environment | (it must run clean in the demo environment first, then against production) |
| Tester / date | |
| Data API | |
| Key used | (write only the key type, never the key itself) |

## Three-step results

### Step 1 · Read the private table directly with no credentials

| Item | Fill in |
|---|---|
| Request | `GET ...` |
| Expected | 401 / 403 or an empty set |
| Actual status code | |
| Actual row count | |
| **Verdict** | Healthy / Suspicious / Compromised |
| If not healthy, the first action | (it should be "revoke", not "change the code") |

### Step 2 · Request "give me the whole table" with the anonymous key

| Item | Fill in |
|---|---|
| Request | `GET ...` |
| Expected | Empty set (the typical expression of working RLS) |
| Actual status code | |
| Actual row count | |
| **Verdict** | Healthy / Suspicious / Compromised |

### Step 3 · Request B's data in A's identity

| Item | Fill in |
|---|---|
| Request | `GET ...` |
| Expected | Empty set / 403 |
| Actual status code | |
| Actual row count | |
| **Verdict** | Healthy / Suspicious / Compromised |

## Verdicts

| Verdict | Meaning |
|---|---|
| Healthy | 401/403, or 200 with an empty set |
| Suspicious | 200 with data, but it is unclear whether the fields are public; **"suspicious" is not "fine", it is "I have not understood it yet"** |
| Compromised | 200 with non-public data obtained |

## Fix and retest

| Step | What was fixed | Retest result | Retest date |
|---|---|---|---|
| | | | |

## The one command to wire into CI

```bash
python3 code/ch09/replay_probe.py --base-url "$SB_URL" --anon-key "$SB_ANON" --table <表名>
```

Exit codes: 0 = all three steps healthy; 1 = at least one step suspicious; 2 = at least one step compromised.
