**English** | [中文](./README.zh.md)

# 《把 AI 代码当不可信输入：从"我觉得没问题"到"我敢让它上线"》开源教材（英文骨架）

> 英文骨架：目录树、数量口径与机检说明先行；正文的英文翻译（逐句对应 `README.zh.md`）在阶段 3 补全。

**数量口径**（全书）：58 张图（中英各一套，共 116 个 PNG 文件）。

## 目录结构

```text
phase3/
└── README.md                          # 本文件：全景图谱、模块矩阵、分章大纲
└── chapters/                          # 12 章正文（已完成）
├── assets/                            # 按章分目录的高清图（240 dpi）
│   └── ch01/fig-01-detection-matrix.png
│   └── ch02/fig-01-pass-rate-gap.png
│   └── ch04/fig-01-hallucinated-packages.png
│   └── ch06/fig-01-four-pillars.png
│   └── ch07/fig-01-coverage-vs-mutation.png
│   └── ch08/fig-01-stress-detection.png
│   └── ch09/fig-01-three-readings.png
│   └── ch12/fig-01-gate-cost.png
├── code/                              # 全部可运行
│   └── _figstyle.py                   # 共享绘图样式
│   └── make_figures.py                # 一次生成全部八张图
│   └── pipeline.sh                    # 七道闸的完整流水线
│   └── case_coupon/                   # 贯穿案例：优惠券核销（10 个文件）
│   └── ch03/three_objects.py          # 三种验证对象实验
│   └── ch05/static_sweep.py           # 四类静态检查
│   └── ch06/refactor_probe.py         # 一次无害重构，看谁红
│   └── ch06/test_coupon_mock.py       # mock 型测试样本
│   └── ch08/stress_oversell.py        # 四组压测对照
│   └── ch08/constraint_check.py       # 约束存在性检查
│   └── ch11/eval_harness.py           # judge 位置偏好探针
└── drafts/                            # 草稿区（非交付物）
    └── ch03-untrusted-ai-code-single-chapter.md
```

## 双语维护

- 文件成对：`X.md`（英文，默认）/ `X.zh.md`（中文）；图 `fig-NN-slug.png`（en）/ `fig-NN-slug.zh.png`（zh）。
- 安装机检钩子（每台克隆机一次性）：`git config core.hooksPath .githooks`
- 提交前机检：`python3 tools/check_bilingual.py --min`
