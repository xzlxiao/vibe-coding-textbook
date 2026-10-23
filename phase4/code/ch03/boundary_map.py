#!/usr/bin/env python3
"""把入口清单变成穿越点清单：数据流图里每一条跨界箭头都要有一行交代。

它不做安全判断，只做一件机械化的事——把「谁带着什么凭据穿过了哪条边界」
摊成一张表，并把「现有控制」里写"待验证"或留空的行标出来。
写不出探测的控制，等于没有控制；这张表就是把这件事逼出来。

用法：
  python3 boundary_map.py                    # 用内置的 LessonVault 案例
  python3 boundary_map.py --json my.json     # 换成你自己的入口清单
  python3 boundary_map.py --json my.json --md   # 只输出 markdown 表

JSON 形状：
  {"flows": [{"id": "F2", "from": "前端", "to": "Postgres",
              "credential": "anon JWT", "actor": "浏览器 / 攻击者",
              "worst": "未登录读全表", "control": "仅 RLS（待验证）"}]}
"""

from __future__ import annotations

import argparse
import json
import sys

DEFAULT = {
    "system": "LessonVault",
    "flows": [
        {"id": "F1", "from": "公网", "to": "前端", "credential": "无",
         "actor": "任何人", "worst": "源码与 anon key 可见", "control": "无（设计如此）"},
        {"id": "F2", "from": "前端", "to": "Postgres", "credential": "anon JWT",
         "actor": "浏览器 / 攻击者", "worst": "未登录读全表", "control": "仅 RLS（待验证）"},
        {"id": "F3", "from": "前端", "to": "Storage", "credential": "签名 URL",
         "actor": "浏览器 / 攻击者", "worst": "遍历他人附件", "control": "桶策略（待验证）"},
        {"id": "F4", "from": "Edge Function", "to": "Postgres", "credential": "service_role",
         "actor": "服务端", "worst": "绕过所有 RLS", "control": "环境变量隔离"},
        {"id": "F5", "from": "智能体", "to": "Edge Function", "credential": "服务令牌",
         "actor": "智能体", "worst": "代任意用户执行", "control": ""},
        {"id": "F6", "from": "任意网页", "to": "智能体上下文", "credential": "无",
         "actor": "攻击者", "worst": "目标劫持", "control": ""},
        {"id": "F7", "from": "API", "to": "Stripe", "credential": "受限 key",
         "actor": "服务端", "worst": "越额退款", "control": "单笔上限（待验证）"},
        {"id": "F8", "from": "API", "to": "邮件网关", "credential": "API key",
         "actor": "服务端", "worst": "以你的域名发信", "control": ""},
    ],
}

PENDING_WORDS = ("待验证", "未验证", "缺口")


def classify(control: str) -> tuple[str, str]:
    if not control.strip():
        return "缺口", "没有任何控制；要么补，要么承认这是已知未覆盖"
    if any(w in control for w in PENDING_WORDS):
        return "待验证", "写了但没测过；必须变成一条能跑的探测"
    return "已落实", "写出了具体控制；仍建议加一条回归测试"


def render(data: dict, md_only: bool) -> tuple[str, int]:
    lines = [
        f"### {data.get('system', '（未命名系统）')} · 信任边界穿越点清单",
        "",
        "| 编号 | 从 → 到 | 携带凭据 | 谁在用 | 最坏情况 | 现有控制 | 判定 |",
        "|---|---|---|---|---|---|---|",
    ]
    open_issues = 0
    for f in data["flows"]:
        verdict, _ = classify(f.get("control", ""))
        if verdict != "已落实":
            open_issues += 1
        lines.append(
            f"| {f['id']} | {f['from']} → {f['to']} | {f['credential']} | {f['actor']} | "
            f"{f['worst']} | {f.get('control') or '（空）'} | **{verdict}** |"
        )

    out = "\n".join(lines)
    if md_only:
        return out, open_issues

    out += f"\n\n共 {len(data['flows'])} 条穿越，其中 {open_issues} 条还没有可执行的控制。"
    if open_issues:
        out += "\n\n下一步只有一句：把「待验证」和「缺口」两栏，逐条变成能跑的探测；"
        out += "\n写不出探测的，就把它写进「已知未覆盖」——别留在表里假装它被管住了。"
    return out, open_issues


def main() -> int:
    ap = argparse.ArgumentParser(description="入口清单 → 信任边界穿越点清单")
    ap.add_argument("--json", help="自定义清单路径；缺省用 LessonVault 案例")
    ap.add_argument("--md", action="store_true", help="只输出 markdown 表")
    args = ap.parse_args()

    if args.json:
        with open(args.json, encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        data = DEFAULT

    text, open_issues = render(data, args.md)
    print(text)
    return 1 if open_issues else 0


if __name__ == "__main__":
    sys.exit(main())
