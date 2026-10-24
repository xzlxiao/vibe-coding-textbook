[English](./README.md) | **中文**

# schedule-kit（演示用最小仓库）

一个只做一件事的小工具：把内存里的日程导出成 CSV。

> 这个仓库是第 2 章的实验材料。它的规模刻意做小——因为本章要看的不是
> 代码规模，而是**同一个需求在两种输入方式下的差异**。

## 目录职责

| 路径 | 职责 |
|---|---|
| `src/sched/models.py` | 领域对象：`Event` 与它的不变量 |
| `src/sched/store.py` | 内存存储，唯一的写入入口 |
| `src/sched/export.py` | 导出：CSV 序列化与列顺序 |
| `tests/` | 与上面三项一一对应的单测 |

## 命令

```bash
python -m pytest -q
python -m sched.export --out /tmp/events.csv
```
