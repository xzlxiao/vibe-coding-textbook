"""第 11 章实验：AI-as-a-judge 的位置偏好，以及怎么把它逼出来。

场景：20 条客服回复，每条有 A/B 两版，人工标注了哪一版更好。
裁判是一个模拟的 LLM judge：它有真本事（剩下的概率会选对），
但有一个坏习惯——大部分时候直接选"排在前面的那个"。

三段结论：
  1. 打乱顺序再判一次：一致率与翻转率
  2. 用"两次一致才采信"去偏：覆盖率与准确率怎么变
  3. 剩下那部分不一致的样本，才是真正需要人看的

跑法：python eval_harness.py
"""

import random

random.seed(20261019)
POSITION_BIAS = 0.70  # 70% 的时候直接选排在前面的

CASES = [{"id": i, "best": "AB"[i % 2]} for i in range(1, 21)]


def judge(first: str, second: str, best: str) -> str:
    """返回它选中的那一版的标签。"""
    if random.random() < POSITION_BIAS:
        return first
    return best


def run(swap: bool) -> list[str]:
    out = []
    for c in CASES:
        if swap:
            out.append(judge("B", "A", c["best"]))   # B 排在前面
        else:
            out.append(judge("A", "B", c["best"]))   # A 排在前面
    return out


def main() -> None:
    forward = run(swap=False)
    swapped = run(swap=True)

    agree = sum(1 for v, c in zip(forward, CASES) if v == c["best"])
    flipped = sum(1 for a, b in zip(forward, swapped) if a != b)

    print(f"样本数：{len(CASES)}，位置偏好参数：{POSITION_BIAS:.0%}")
    print(f"单次判定与人工一致：{agree}/{len(CASES)} = {agree / len(CASES):.0%}")
    print(f"交换顺序后结论翻转：{flipped}/{len(CASES)} = {flipped / len(CASES):.0%}")
    print()

    decided = correct = 0
    for a, b, c in zip(forward, swapped, CASES):
        if a == b:
            decided += 1
            correct += (a == c["best"])

    print("去偏后（两次一致才采信）：")
    print(f"  可判定样本：{decided}/{len(CASES)} = {decided / len(CASES):.0%}")
    print(f"  其中判对：{correct}/{decided if decided else 1} = "
          f"{(correct / decided if decided else 0):.0%}")
    print(f"  需要人工复核：{len(CASES) - decided} 条")
    print()
    print("结论：翻转率远超 10%，这个 judge 不能单独当门禁。")
    print("      去偏让它变准了，但代价是大部分样本被弃权——那部分只能回到人。")


if __name__ == "__main__":
    main()
