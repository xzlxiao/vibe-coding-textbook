**English** | [中文](./README.zh.md)

# Vibe Coding 教材：从能跑到能收钱（英文骨架）

> 英文骨架：目录树、数量口径与机检说明先行；正文的英文翻译（逐句对应 `README.zh.md`）在阶段 3 补全。

**共 48 章、58 张图（中英各一套，共 116 个 PNG 文件）、可运行的取证脚本与交付模板。**

## 目录结构

```text
.
└── README.md            # 本文件：全书索引与读法
└── LICENSE              # 授权条款
├── phase1/ … phase5/    # 五册，每册自包含
│   └── README.md        # 该册的全景图谱、大纲、阅读路径
│   └── chapters/        # 正文（ch01-…，册内编号）
│   └── assets/          # 图（200+ DPI，PNG）
│   └── code/            # 可运行脚本（绘图 / 取证 / 模板数据）
│   └── templates/       # 可直接抄用的交付模板（多数册有）
└── phaseN/_archive/     # 少量历史草稿（保留备查，不构成正文）
```

## 双语维护

- 文件成对：`X.md`（英文，默认）/ `X.zh.md`（中文）；图 `fig-NN-slug.png`（en）/ `fig-NN-slug.zh.png`（zh）。
- 安装机检钩子（每台克隆机一次性）：`git config core.hooksPath .githooks`
- 提交前机检：`python3 tools/check_bilingual.py --min`
