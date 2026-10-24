**English** | [中文](./threat-model.zh.md)

# Threat List Template

> How to use: fill in this table as it stands. One threat per row; **a threat with no "testable assertion" does not stay in the table** — move it to "Known uncovered" at the end.
> Suggested size: an amount you can fill in one afternoon (around 8 rows); not completeness — every row must run.

## System

| Item | Fill in |
|---|---|
| System name | |
| Owner | |
| Diagram date | |
| Data flow diagram | (paste the image, or link to the chapter's diagram) |

## Threat list

| # | Component | STRIDE | ASI | Concrete threat | **Testable assertion** | Countermeasure | Residual risk |
|---|---|---|---|---|---|---|---|
| T1 | | | | | | | |
| T2 | | | | | | | |
| T3 | | | | | | | |
| T4 | | | | | | | |
| T5 | | | | | | | |
| T6 | | | | | | | |
| T7 | | | | | | | |
| T8 | | | | | | | |

**What the columns mean**

- **STRIDE**: Spoofing / Tampering / Repudiation / Info Disclosure / DoS / Elevation
- **ASI**: the number from the OWASP Top 10 for Agentic Applications; for threats that are not AI-specific, fill in `—`
- **Testable assertion**: a query or request that can be run; the recommended format is "subject + action + object + expected result", for example:
  `execute select count(*) from notes with the anon role, expect 0`
- **Residual risk**: **what is left** after the countermeasure is done. Writing "none" means it was not thought through

## Known uncovered (anything you cannot write an assertion for goes here)

| Threat | Why no assertion can be written | When to fill it in |
|---|---|---|
| | | |
