"""变异测试（mutation testing）最小实现 —— 只用标准库。

思路：不改测试、改被测代码，故意注入小错误（变异体）。
测试套件如果仍然全绿，说明这个变异体「活下来了」——
它对应的那条 Rule 其实没有被任何断言守住。

同一个变异体，分别在两套测试下跑：
  A. test_coupon_ai.py        —— AI 生成的那套
  B. test_coupon_behavior.py  —— 按规格重写的那套
两列的差值，就是「绿灯」与「可信的绿灯」之间的差。

用法：
    python mutation_demo.py                       # 默认变异 coupon_service.py
    python mutation_demo.py coupon_service_fixed.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / (sys.argv[1] if len(sys.argv) > 1 else "coupon_service.py")

# (编号, 说明, 原文, 变异后)
MUTATIONS = [
    ("M1", "边界翻转：used >= quota 变成 used > quota", "if used >= quota:", "if used > quota:"),
    ("M2", "算术错误：used + 1 变成 used + 0", "used + 1", "used + 0"),
    ("M3", "判定反转：没找到券码却走进 not_found", "if row is None:", "if row is not None:"),
    ("M4", "返回值退化：token 变成 None",
     'return {"ok": True, "token": sign_token(user_id, code)}',
     'return {"ok": True, "token": None}'),
]

SUITES = {
    "A 空断言": ("test_coupon_ai.py", HERE),
    "B mock 型": ("test_coupon_mock.py", HERE.parent / "ch06"),
    "C 规格": ("test_coupon_behavior.py", HERE),
}


def run_suite(source: str, test_file: str, src_dir: Path) -> bool:
    """返回 True 表示测试通过（变异体存活）。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "coupon_service.py").write_text(source, encoding="utf-8")
        shutil.copy(src_dir / test_file, tmp_path / test_file)
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", Path(test_file).stem, "-q"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0


def main() -> int:
    original = SRC.read_text(encoding="utf-8")
    header = f"{'变异体':<4}{'说明':<44}" + "".join(f"{k:<14}" for k in SUITES)
    print(header)
    print("-" * len(header))

    killed = {k: 0 for k in SUITES}
    for mid, desc, old, new in MUTATIONS:
        if old not in original:
            print(f"{mid:<4}{desc:<44}变异点未找到，脚本需更新")
            return 2
        mutant = original.replace(old, new, 1)
        row = f"{mid:<4}{desc:<44}"
        for label, (test_file, src_dir) in SUITES.items():
            survived = run_suite(mutant, test_file, src_dir)
            if not survived:
                killed[label] += 1
            row += f"{'存活（漏）' if survived else '杀死（抓到）':<14}"
        print(row)

    print("-" * len(header))
    total = len(MUTATIONS)
    scores = "".join(f"{killed[k]}/{total} = {killed[k] / total:.0%}".ljust(14) for k in SUITES)
    print(f"{'变异分数':<48}{scores}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
