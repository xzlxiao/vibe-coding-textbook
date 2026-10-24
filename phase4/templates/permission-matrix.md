**English** | [中文](./permission-matrix.zh.md)

# Permission Matrix Template

> How to use: one row per tool. The three criteria (impact radius × reversibility × observability) compute the review tier, **then decide whether to narrow the scope or delete the tool**.
> The criteria do not look at "how important is this action" — importance is subjective; radius, reversibility, and observability are checkable.

## System

| Item | Fill in |
|---|---|
| System / agent name | |
| Total tools | |
| Date of this matrix | |
| Who may change tool definitions | |

## Permission matrix

| Tool | Scope | Credential lifetime | Impact radius | Reversibility | Observability | Review tier | kill switch | Max impact per call |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

**How to fill the columns**

- **Scope**: write "what it can touch", with a hard cap wherever possible (e.g. `≤50 yuan per transaction, ≤500 yuan per day`). Writing "read orders" does not qualify.
- **Credential lifetime**: long-lived / short-lived (how long) / exchanged per use. **Long-lived = every single use is a chance to copy the credential.**
- **Impact radius**: 1 object / 1 service (thousands of rows) / whole DB, whole tenant, already external
- **Reversibility**: rollback-capable (backups or idempotent) / needs snapshot restore / irreversible (already happened externally)
- **Observability**: logs + alerts / logs only / invisible. **"Has logs" does not count as observable; "someone gets woken up" does.**
- **Review tier**: auto-allow / auto + post-hoc review / single human in the loop / two-person + rehearsal / default deny
- **kill switch**: the concrete one-press-and-it-stops action (which flag to flip, which key to revoke). **Un-rehearsed = none.**
- **Max impact per call**: the furthest damage one call can do (e.g. `1 row of subscription state`)

## Review tier decision matrix

| | Impact radius: 1 object | 1 service | Whole DB / already external |
|---|---|---|---|
| **Rollback-capable** | Auto-allow | Auto + post-hoc review | Single human in the loop |
| **Needs recovery** | Auto + alert | Single human in the loop | Two-person + rehearsal |
| **Irreversible** | Single human in the loop | Two-person + rehearsal | Default deny |

**Modifier**: when observability is "logs only" or "invisible", **go up one tier** (stay put if already at the top).

## Step-down record (shrink the radius first, then talk about approvals)

| Tool | Original scope | Original tier | What changed | New tier | Date |
|---|---|---|---|---|---|
| | | | | | |

## Should not be implemented (tools landing on "default deny")

| Tool | Why it should not be implemented | Alternative |
|---|---|---|
| | | |

> Landing on "default deny" is not asking you to add a confirmation checkbox; it means this tool's scope is written too wide.
> The right reaction: **delete the tool definition, or narrow the scope until the tier drops.**
