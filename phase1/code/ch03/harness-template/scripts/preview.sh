#!/usr/bin/env bash
# 预发布环境的最小实现：起一个静态服务，把生成的 CSV 渲染成表格页面。
# 比"部署到 Vercel"土，但 3 秒可跑、零成本、不依赖账号。
set -euo pipefail
OUT="${1:-/tmp/preview.csv}"
PORT="${2:-8787}"
mkdir -p /tmp/csvkit-preview
python3 - "$OUT" <<'PY'
import csv, html, sys, pathlib
src = pathlib.Path(sys.argv[1])
dst = pathlib.Path("/tmp/csvkit-preview/index.html")
rows = list(csv.reader(src.open(encoding="utf-8")))
body = "\n".join(
    "<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r) + "</tr>" for r in rows[1:]
)
head = "".join(f"<th>{html.escape(c)}</th>" for c in rows[0])
dst.write_text(
    "<meta charset='utf-8'><style>body{font:14px/1.6 system-ui;padding:32px}"
    "table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:6px 12px}"
    "th{background:#f6f8fa;text-align:left}</style>"
    f"<table><tr>{head}</tr>{body}</table>",
    encoding="utf-8",
)
PY
echo "preview → http://127.0.0.1:${PORT}/"
cd /tmp/csvkit-preview && python3 -m http.server "$PORT" --bind 127.0.0.1
