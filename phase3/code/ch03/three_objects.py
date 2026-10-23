"""第 03 章实验：同一件事，三种验证对象，三种证伪方式。

场景：给用户生成一句"退款已受理"的通知文案。
  A 版是规则拼出来的（确定性的）
  B 版是模型生成的（这里用本地桩模拟：同一输入，多次调用措辞不同）

三段检查依次上：
  check1  代码形态：类型标注 + 静态形状检查
  check2  行为：精确匹配那一句话（对 A 有效，对 B 必然误报）
  check3  输出：一组性质断言 + 一个最小评测集（对两版都适用）

跑法：python three_objects.py
"""

import random
import re

ORDER = {"order_id": "A1024", "amount": 128.00, "eta_days": 3}


# ---------------------------------------------------------------- 两个实现
def refund_line_rule(order: dict) -> str:
    """规则版：确定性输出。"""
    return (
        f"订单 {order['order_id']} 的退款 {order['amount']:.2f} 元已受理，"
        f"预计 {order['eta_days']} 个工作日原路退回。"
    )


def refund_line_ai(order: dict) -> str:
    """模型版的本地桩：措辞随机，但内容应当一致。

    这里用随机模板模拟"同一输入多次调用措辞不同"这一事实，
    真实模型还会在温度、上下文、版本变化时产生更多差异。
    """
    templates = [
        "您好，订单 {oid} 的退款 {amt:.2f} 元已经受理，预计 {eta} 个工作日内原路退回。",
        "订单 {oid}：退款 {amt:.2f} 元已受理，{eta} 个工作日左右回到您的账户。",
        "您的订单 {oid} 退款已处理，金额 {amt:.2f} 元，将在 {eta} 个工作日内到账。",
    ]
    t = random.choice(templates)
    return t.format(oid=order["order_id"], amt=order["amount"], eta=order["eta_days"])


# ---------------------------------------------------------------- 三段检查
def check1_shape(fn) -> tuple[bool, str]:
    """代码形态：能不能调用、参数类型对不对。"""
    try:
        out = fn(ORDER)
    except Exception as e:  # noqa: BLE001
        return False, f"调用失败：{e!r}"
    return isinstance(out, str) and len(out) > 0, "返回非空字符串"


def check2_exact(fn) -> tuple[bool, str]:
    """行为：精确匹配一句话。这是最经典的写法，也是最脆的写法。"""
    expected = (
        "订单 A1024 的退款 128.00 元已受理，预计 3 个工作日原路退回。"
    )
    got = fn(ORDER)
    return got == expected, "一字不差" if got == expected else f"实际：{got}"


def check3_eval(fn) -> tuple[bool, str]:
    """输出：一组性质断言，构成最小评测集。

    每条断言只约束"必须为真的事实"，不约束措辞。
    """
    cases = []
    for _ in range(20):
        text = fn(ORDER)
        cases.append((
            ORDER["order_id"] in text,                       # 含单号
            "128.00" in text,                                # 含金额，两位小数
            str(ORDER["eta_days"]) in text,                  # 含时长
            bool(re.search(r"受理|处理|提交", text)),        # 表达了"已受理"
            len(text) <= 60,                                 # 长度上限
        ))
    passed = sum(1 for c in cases if all(c))
    return passed == len(cases), f"{passed}/20 次调用全项通过"


# ---------------------------------------------------------------- 主流程
def pad(text: str, width: int) -> str:
    """按显示宽度补空格：中日韩字符占两格。"""
    w = sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)
    return text + " " * max(0, width - w)


def main() -> None:
    impls = [("A 规则版", refund_line_rule), ("B 模型版", refund_line_ai)]
    checks = [("check1 代码形态", check1_shape),
              ("check2 行为·精确匹配", check2_exact),
              ("check3 输出·性质断言", check3_eval)]

    print(pad("", 24) + pad("A 规则版", 30) + "B 模型版")
    print("-" * 86)
    for name, fn in checks:
        row = pad(name, 24)
        for _, impl in impls:
            ok, detail = fn(impl)
            cell = f"{'通过' if ok else '失败'} · {detail}"[:26]
            row += pad(cell, 30)
        print(row)
    print("-" * 86)
    print("读法：check2 在 B 上必然失败——不是因为 B 错了，是因为它测的是措辞。")
    print("      check3 才对两版都成立——因为它测的是事实。")


if __name__ == "__main__":
    main()
