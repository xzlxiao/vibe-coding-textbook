**English** | [中文](./README.zh.md)

# 《先写规格，再让 AI 动手：从零基础到规格驱动开发》（英文骨架）

> 英文骨架：目录树、数量口径与机检说明先行；正文的英文翻译（逐句对应 `README.zh.md`）在阶段 3 补全。

**数量口径**（全书）：58 张图（中英各一套，共 116 个 PNG 文件）。

## 目录结构

```text
phase2/                       # 本册（阶段 2）
└── README.md                       # 本文件：全景知识图谱、大纲、阅读路径
└── chapters/
├── assets/
│   └── ch01/  ch07/  ch09/  ch12/    # 有图各章 fig-NN-<slug>.png（en）/ fig-NN-<slug>.zh.png（zh），≥200 DPI
├── code/
│   └── figures/                     # 全部配图的生成脚本（make_figures.py）
│   └── ch09/                       # metrics.csv 模板与统计脚本
│   └── ch11/                       # 候补系统参考实现（含 3 个故意留的规格缺口）
└── templates/
```

## 双语维护

- 文件成对：`X.md`（英文，默认）/ `X.zh.md`（中文）；图 `fig-NN-slug.png`（en）/ `fig-NN-slug.zh.png`（zh）。
- 安装机检钩子（每台克隆机一次性）：`git config core.hooksPath .githooks`
- 提交前机检：`python3 tools/check_bilingual.py --min`
