#!/usr/bin/env python3
"""未登录重放探测：只用标准库，三步走完才知道门是虚掩还是没装。

三步（与第 01 章图 1-3 一一对应）：
  第 1 步  不带任何凭据，直接读一张私有表        —— 期望 401/403 或空集
  第 2 步  用匿名 key（可从浏览器 bundle 里抓到）读全表 —— 期望 空集
  第 3 步  用「用户 A」的令牌去读「用户 B」的行   —— 期望 空集

安全约束（重要）：
  · 只做 GET，且强制带 limit，绝不 DELETE / UPDATE / INSERT
  · 只读，不改；发现「已失守」时的第一动作是吊销密钥，不是继续探
  · --dry-run 只打印将要发出的请求，不发网络包（本仓库的默认自测方式）

用法：
  python3 replay_probe.py --base-url https://xxxx.supabase.co --anon-key <ANON> \
      --table notes --dry-run
  python3 replay_probe.py --base-url ... --anon-key ... --table notes \
      --token-a <A 的 access_token> --victim-id <B 的 uuid>

退出码：0 = 三步全健康；1 = 至少一步可疑；2 = 至少一步已失守（可直接接进 CI）
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 12


def build_url(base: str, table: str, params: dict[str, str]) -> str:
    qs = urllib.parse.urlencode(params, safe="*")
    return f"{base.rstrip('/')}/rest/v1/{table}?{qs}"


def request_json(url: str, headers: dict[str, str]) -> tuple[int, list]:
    """返回 (状态码, 行数)。只接受 JSON 数组；解析失败按 0 行处理。"""
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        return exc.code, []
    except urllib.error.URLError as exc:
        raise SystemExit(f"网络不可达，先确认 base-url 与代理设置：{exc.reason}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return status, []
    return status, payload if isinstance(payload, list) else [payload]


def verdict(status: int, rows: list, expect: str) -> tuple[str, str]:
    """把一次探测翻译成「健康 / 可疑 / 已失守」。"""
    if status in (401, 403):
        return "健康", f"HTTP {status}，被拒绝"
    if status >= 400:
        return "可疑", f"HTTP {status}，错误类型不明确，需人工看一眼响应体"
    if not rows:
        return "健康", "HTTP 200 但空集（RLS 生效的典型表现）"
    if expect == "anon":
        return "已失守", f"匿名读到 {len(rows)} 行非公开数据"
    return "已失守", f"越权读到 {len(rows)} 行他人数据"


def main() -> int:
    ap = argparse.ArgumentParser(description="未登录 / 横向越权的只读重放探测")
    ap.add_argument("--base-url", required=True, help="例如 https://xxxx.supabase.co")
    ap.add_argument("--anon-key", required=True, help="前端 bundle 里那份公开 key")
    ap.add_argument("--table", default="notes", help="要探的私有表名")
    ap.add_argument("--limit", type=int, default=5, help="每次最多取几行（默认 5，够判定即可）")
    ap.add_argument("--token-a", help="用户 A 的 access_token（做第 3 步用）")
    ap.add_argument("--victim-id", help="用户 B 的 uuid（做第 3 步用）")
    ap.add_argument("--dry-run", action="store_true", help="只打印请求，不发网络包")
    args = ap.parse_args()

    anon_headers = {"apikey": args.anon_key, "Accept": "application/json"}
    base_params = {"select": "*", "limit": str(args.limit)}

    steps: list[tuple[str, str, dict[str, str], str]] = [
        ("第 1 步 · 无凭据直读私有表",
         build_url(args.base_url, args.table, base_params),
         {"Accept": "application/json"},
         "anon"),
        ("第 2 步 · 用匿名 key 读全表",
         build_url(args.base_url, args.table, {**base_params, "limit": "1000"}),
         anon_headers,
         "anon"),
    ]
    if args.token_a and args.victim_id:
        steps.append((
            "第 3 步 · 用 A 的令牌读 B 的行",
            build_url(args.base_url, args.table, {**base_params, "owner_id": f"eq.{args.victim_id}"}),
            {**anon_headers, "Authorization": f"Bearer {args.token_a}"},
            "cross",
        ))

    worst = 0
    tier_rank = {"健康": 0, "可疑": 1, "已失守": 2}

    print("=" * 78)
    print("未登录重放探测（只读）")
    print("=" * 78)
    for name, url, headers, expect in steps:
        if args.dry_run:
            print(f"\n[{name}]  (dry-run，未发送)")
            print(f"  GET {url}")
            print(f"  headers: {sorted(headers)}")
            continue

        status, rows = request_json(url, headers)
        level, why = verdict(status, rows, expect)
        worst = max(worst, tier_rank[level])
        print(f"\n[{name}]  → {level}")
        print(f"  {why}")
        print(f"  GET {url}")

    if args.dry_run:
        print("\n(dry-run 结束。去掉 --dry-run 才会真的发包。)")
        return 0

    print("\n" + "-" * 78)
    if worst == 0:
        print("结论：三步全健康。把这条命令接进 CI，作为「门是否还锁着」的回归测试。")
    elif worst == 1:
        print("结论：存在可疑项。先看响应体，再决定是改策略还是改探测口径。")
    else:
        print("结论：已失守。第一动作是吊销 anon key 与相关令牌，其次才是改代码。")
    return worst


if __name__ == "__main__":
    sys.exit(main())
