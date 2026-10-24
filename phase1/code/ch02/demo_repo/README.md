**English** | [中文](./README.zh.md)

# schedule-kit (minimal demo repository)

A small tool that does exactly one thing: export the events in memory to CSV.

> This repository is the lab material for Chapter 2. Its size is deliberately small — because what this chapter examines is not
> code size, but **the difference the same requirement shows under two input styles**.

## Directory Responsibilities

| Path | Responsibility |
|---|---|
| `src/sched/models.py` | Domain objects: `Event` and its invariants |
| `src/sched/store.py` | In-memory store, the single write entry point |
| `src/sched/export.py` | Export: CSV serialization and column order |
| `tests/` | Unit tests matching the three items above one-to-one |

## Commands

```bash
python -m pytest -q
python -m sched.export --out /tmp/events.csv
```
