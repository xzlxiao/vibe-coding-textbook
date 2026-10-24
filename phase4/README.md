**English** | [中文](./README.zh.md)

# 《关得住：AI 系统的攻击面与爆炸半径》开源教材（英文骨架）

> 英文骨架：目录树、数量口径与机检说明先行；正文的英文翻译（逐句对应 `README.zh.md`）在阶段 3 补全。

**数量口径**（全书）：58 张图（中英各一套，共 116 个 PNG 文件）。

## 目录结构

```text
phase4/                                      # 一本书 = 一个目录，自包含
└── README.md                                # 本文件：定位、图谱、大纲、映射、进度
└── chapters/
├── assets/
│   └── chNN/                                # 章内编号，每章从 fig-01 起
├── code/
│   └── make_figures.py                      # 全书配图统一入口（可只重绘某章）
│   └── ch01/ … ch10/                        # 每章一份可运行的最小示例
└── templates/                               # 可抄的交付模板
```

## 双语维护

- 文件成对：`X.md`（英文，默认）/ `X.zh.md`（中文）；图 `fig-NN-slug.png`（en）/ `fig-NN-slug.zh.png`（zh）。
- 安装机检钩子（每台克隆机一次性）：`git config core.hooksPath .githooks`
- 提交前机检：`python3 tools/check_bilingual.py --min`
