#!/usr/bin/env bash
# 演示：门禁抓住一个"看起来对"的回归。
# 在临时副本里把 csv 的转义逻辑改坏，然后跑 pytest。
set -uo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
cp -R "$SRC"/. "$TMP"/
cd "$TMP"
export PYTHONPATH="$TMP/src"

python3 - <<'PY'
import pathlib
p = pathlib.Path("src/csvkit/export.py")
s = p.read_text(encoding="utf-8")
# 把标准库 csv.writer 换成手写拼接——"更简单、更少依赖"，一周后炸。
s = s.replace(
    "        writer = csv.writer(fh)\n        writer.writerow(COLUMNS)\n        writer.writerows(rows)",
    "        fh.write(\",\".join(COLUMNS) + \"\\n\")\n"
    "        for r in rows:\n"
    "            fh.write(\",\".join(r) + \"\\n\")",
)
p.write_text(s, encoding="utf-8")
print("已注入回归：改为手工拼接，不再转义逗号")
PY

echo "--- pytest ---"
python3 -m pytest -q 2>&1 | tail -12
echo "--- 退出码：$? （非 0 表示门禁生效）---"
rm -rf "$TMP"
