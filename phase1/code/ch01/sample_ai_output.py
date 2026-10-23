"""sample_ai_output.py —— 一份"看起来完全能跑"的 AI 生成代码。

它没有被运行过。请先读一遍，标出你觉得可疑的 3 行，再跑：

    python code/ch01/check_deps.py code/ch01/sample_ai_output.py --online

注意：这份文件是照真实事故的形状缩写的，不是从任何具体工具抄来的。
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass

from pydantic import BaseModel  # 常见依赖，通常已安装
from pydantic_json_repair import repair  # 幻觉包名：注册表里不存在
from flask_csv_plus import CsvResponse  # 幻觉包名：注册表里不存在
import pandas as pd  # 已安装，但很多项目其实不需要它


class ExportRequest(BaseModel):
    table: str
    limit: int = 1000


@dataclass
class ExportResult:
    path: str
    rows: int


def export_table(req: ExportRequest) -> ExportResult:
    """把一张表导出成 CSV。

    这里藏着三类不同性质的问题，扫描器只能抓到第一类。
    """
    conn = os.environ["DB_URL"]  # ① 缺失安全属性：没有默认值、没有启动期校验
    df = pd.read_sql(f"SELECT * FROM {req.table} LIMIT {req.limit}", conn)  # ② 模式化复制：字符串拼 SQL

    broken = repair(json.dumps(df.to_dict()))  # ③ 幻觉依赖：repair 来自不存在的包
    rows = json.loads(broken)

    out = f"/tmp/{req.table}.csv"
    with open(out, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows([r.values() for r in rows])  # ④ 模式化复制：dict 顺序不保证

    return ExportResult(path=out, rows=len(rows))


def download(req: ExportRequest) -> CsvResponse:  # ⑤ 幻觉依赖：CsvResponse 不存在
    result = export_table(req)
    return CsvResponse(result.path, mimetype="text/csv")
