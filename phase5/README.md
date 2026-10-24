**English** | [中文](./README.zh.md)

# 《从能跑到能收钱：AI 产品上线与经营》开源教材（英文骨架）

> 英文骨架：目录树、数量口径与机检说明先行；正文的英文翻译（逐句对应 `README.zh.md`）在阶段 3 补全。

**数量口径**（全书）：58 张图（中英各一套，共 116 个 PNG 文件）。

## 目录结构

```text
phase5/
└── README.md                            # 本文件：全景图谱、分级大纲、学习路线
└── chapters/                            # 十章正文
├── assets/                              # 经质量门禁核验的高清图
│   └── ch01/ ... ch10/
├── code/                                # 可直接运行的配套代码
│   └── _figstyle.py                     # 配图统一样式与绘图助手（被 import）
│   └── make_figures_p5.py               # 全部 20 张配图的生成脚本
│   └── ch02/unit_economics.py           # 单位经济计算器（三档用量 + 敏感性）
│   └── ch03/mvp_matrix.py               # 功能四象限打分
│   └── ch04/rollback_drill.py           # 回滚演练计时与记录模板
│   └── ch05/slo_burn.py                 # 错误预算与燃烧率
│   └── ch06/rto_calc.py                 # RTO/RPO 反推与实测对照
│   └── ch07/budget_guard.py             # 预算熔断参考实现（可嵌入）
│   └── ch08/compliance_matrix.py        # 风险分级与义务清单生成
│   └── ch09/health_dashboard.py         # 健康度看板绘图
│   └── ch10/launch_checklist.py         # 上线日检查单（可打勾、可导出）
└── templates/                           # 可直接抄的交付物模板
```

## 双语维护

- 文件成对：`X.md`（英文，默认）/ `X.zh.md`（中文）；图 `fig-NN-slug.png`（en）/ `fig-NN-slug.zh.png`（zh）。
- 安装机检钩子（每台克隆机一次性）：`git config core.hooksPath .githooks`
- 提交前机检：`python3 tools/check_bilingual.py --min`
