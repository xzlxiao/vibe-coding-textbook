**English** | [中文](./README.zh.md)

# 《Vibe Coding：把「氛围」装进夹具》（英文骨架）

> 英文骨架：目录树、数量口径与机检说明先行；正文的英文翻译（逐句对应 `README.zh.md`）在阶段 3 补全。

**数量口径**（全书）：58 张图（中英各一套，共 116 个 PNG 文件）。

## 目录结构

```text
phase1/                                # 本册 = 阶段 1，自包含
└── README.md                          # 本文件：阶段导读与知识图谱
└── chapters/
├── assets/                            # 全部配图（240 dpi，可重新生成）
│   └── ch01/  fig-01 感知落差 · fig-02 上下文坍缩 · fig-03 记账口径
│   └── ch02/  fig-01 三层渐进披露
│   └── ch03/  fig-01 夹具两半 · fig-02 门禁左移成本
│   └── ch04/  fig-01 五段记账模板
└── code/
    └── make_figures.py                # 一键重画全部配图
    └── ch01/check_deps.py             # 依赖幻觉扫描器（三层判定）
    └── ch01/sample_ai_output.py       # 一份"看起来能跑"的 AI 产出
    └── ch02/build_context.py          # 三层输入生成器 + token 预算统计
    └── ch02/demo_repo/                # 演示仓库（11 个 py 文件，可跑测试）
    ├── ch03/harness-template/         # ★ 本阶段核心交付物：夹具模板
    │   └── AGENTS.md
    │   └── pyproject.toml             # ruff / mypy / pytest 配置
    │   └── .pre-commit-config.yaml
    │   └── .github/workflows/ci.yml
    │   └── src/csvkit/export.py
    │   └── tests/test_export.py
    │   └── scripts/
    │       └── preview.sh             # 预发布：3 秒起一个可看页面
    │       └── demo_gate_catch.sh     # 演示门禁抓住真实回归
    └── ch04/
        └── ab_log.py                  # 五段记账汇总 + bootstrap 区间
        └── sample_log.csv             # 示例数据（编的，仅为演示格式）
```

## 双语维护

- 文件成对：`X.md`（英文，默认）/ `X.zh.md`（中文）；图 `fig-NN-slug.png`（en）/ `fig-NN-slug.zh.png`（zh）。
- 安装机检钩子（每台克隆机一次性）：`git config core.hooksPath .githooks`
- 提交前机检：`python3 tools/check_bilingual.py --min`
