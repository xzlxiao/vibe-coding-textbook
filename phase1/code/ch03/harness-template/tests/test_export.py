"""导出行为契约。改 COLUMNS 必须同步改这里——测试就是文档。"""

from __future__ import annotations

from pathlib import Path

import pytest

from csvkit import COLUMNS, to_csv


def test_columns_are_contract() -> None:
    assert COLUMNS == ("id", "name", "amount", "note")


def test_row_count_matches_input(tmp_path: Path) -> None:
    out = tmp_path / "a.csv"
    assert to_csv([(1, "茶", 12, "")], out) == 1


def test_commas_are_escaped(tmp_path: Path) -> None:
    out = tmp_path / "a.csv"
    to_csv([(1, "周会, 含研发", 0, "")], out)
    assert '"周会, 含研发"' in out.read_text(encoding="utf-8")


def test_wrong_arity_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        to_csv([(1, "茶")], tmp_path / "a.csv")


def test_no_blank_lines_on_write(tmp_path: Path) -> None:
    out = tmp_path / "a.csv"
    to_csv([(1, "a", 1, ""), (2, "b", 2, "")], out)
    assert out.read_text(encoding="utf-8").count("\n\n") == 0
