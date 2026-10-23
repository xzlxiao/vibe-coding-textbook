#!/usr/bin/env python3
"""第 11 章配套：四条约束的取证脚本。

每条测试对应规格里的一条约束，输出「通过 / 失败」与关键数字。
这不是单元测试，是「约束是否真的成立」的取证——所以它故意用多线程并发。

运行：
    python verify.py
"""

from __future__ import annotations

import sys
import threading
import time
import traceback

from store import DomainError, Store

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str):
    def deco(fn):
        def run():
            try:
                detail = fn()
                RESULTS.append((name, True, detail))
            except AssertionError as e:
                RESULTS.append((name, False, str(e)))
            except Exception:  # noqa: BLE001
                RESULTS.append((name, False, traceback.format_exc(limit=3)))
        run.__name__ = fn.__name__
        return run
    return deco


@check("C1 幂等：同一 key 并发 20 次，只应有 1 条报名")
def c1_idempotency() -> str:
    s = Store()
    s.create_event("evt", 24)
    key = "k-fixed"
    out, errs = [], []

    def worker():
        try:
            out.append(s.signup("evt", "张三", "13800000000", key))
        except Exception as e:  # noqa: BLE001
            errs.append(e)

    ts = [threading.Thread(target=worker) for _ in range(20)]
    [t.start() for t in ts]
    [t.join() for t in ts]

    assert not errs, f"出现异常：{errs[:2]}"
    ids = {r.registration_id for r in out}
    assert len(ids) == 1, f"产生了 {len(ids)} 条不同报名（应为 1）"
    assert s.confirmed_count("evt") == 1, f"占用名额 {s.confirmed_count('evt')}（应为 1）"
    return f"20 个请求 → 1 条记录，{sum(1 for r in out if r.reused)} 次命中幂等缓存"


@check("C2 并发：容量 1，50 人抢，只应有 1 人 confirmed")
def c2_no_oversell() -> str:
    s = Store()
    s.create_event("evt", 1)
    results, errs = [], []
    barrier = threading.Barrier(50)

    def worker(i: int):
        try:
            barrier.wait()
            results.append(s.signup("evt", f"用户{i}", f"1380000{i:04d}", f"k{i}"))
        except Exception as e:  # noqa: BLE001
            errs.append(e)

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
    [t.start() for t in ts]
    [t.join() for t in ts]

    assert not errs, f"出现异常：{errs[:2]}"
    confirmed = [r for r in results if r.status == "confirmed"]
    waiting = [r for r in results if r.status == "waiting"]
    assert len(confirmed) == 1, f"confirmed={len(confirmed)}（应为 1，即超卖 {len(confirmed) - 1} 个）"
    assert s.confirmed_count("evt") == 1, f"库内占用 {s.confirmed_count('evt')}"
    assert len(waiting) == 49, f"候补 {len(waiting)}（应为 49）"
    return "1 confirmed / 49 waiting，无超卖"


@check("C3 降级：通知服务挂掉时，取消仍成功，通知进待发队列")
def c3_degrade() -> str:
    s = Store(sms_down=True)
    s.create_event("evt", 1)
    a = s.signup("evt", "家长A", "13800000001", "ka")
    b = s.signup("evt", "家长B", "13800000002", "kb")
    assert a.status == "confirmed" and b.status == "waiting", "初始状态不对"

    r = s.cancel(a.registration_id)          # 通知服务是挂的
    assert r["status"] == "cancelled", "取消失败——通知不应阻塞主流程"
    assert s.confirmed_count("evt") == 1, "名额未被候补占用"
    r1 = s.drain_outbox()
    assert r1["sent"] == 0 and r1["failed"] == 1, f"第一次投递结果异常：{r1}"

    s.sms_down = False
    for _ in range(8):                        # 退避后重投
        time.sleep(0.05)
        r2 = s.drain_outbox(now=time.time() + 60)
    assert s.outbox_status().get("sent", 0) == 1, f"最终状态：{s.outbox_status()}"
    return f"取消成功；故障期间 failed={r1['failed']}；恢复后 sent=1，未重复"


@check("C3' 去重：同一取消重复调用，不产生第二条邀请")
def c3_dedupe() -> str:
    s = Store()
    s.create_event("evt", 1)
    a = s.signup("evt", "家长A", "13800000001", "ka")
    s.signup("evt", "家长B", "13800000002", "kb")

    s.cancel(a.registration_id)               # B 获得 offer，产生 1 条通知
    again = s.cancel(a.registration_id)       # 重复取消（重试）
    assert again["reused"] is True, "重复取消未被识别为幂等"
    total = sum(s.outbox_status().values())
    assert total == 1, f"产生 {total} 条通知（应为 1，去重失效）"
    return "重复取消被幂等拦截，通知仍为 1 条"


@check("R6 过期：15 分钟窗口过期后顺延给下一位")
def r6_expire() -> str:
    s = Store()
    s.create_event("evt", 1)
    a = s.signup("evt", "家长A", "13800000001", "ka")
    b = s.signup("evt", "家长B", "13800000002", "kb")
    c = s.signup("evt", "家长C", "13800000003", "kc")

    s.cancel(a.registration_id)               # B 获得 offer
    assert s.waiting_count("evt") == 1, "B 应已离开 waiting"

    expired = s.expire_offers(ttl=0.0, now=time.time() + 1)
    assert len(expired) == 1, f"过期数量 {len(expired)}（应为 1）"
    assert s.confirmed_count("evt") == 1, "名额没有顺延给 C"
    assert s.waiting_count("evt") == 0, "C 应已离开 waiting"

    pending = s.outbox_status().get("pending", 0)
    assert pending == 2, f"应有 2 条通知（B 与 C 各一次），实际 {pending}"
    return "B 过期 → 顺延 C；产生 2 条独立邀请，未重复通知 B"


def main() -> int:
    tests = [c1_idempotency, c2_no_oversell, c3_degrade, c3_dedupe, r6_expire]
    for t in tests:
        t()

    print("=== 约束取证 ===")
    ok = 0
    for name, passed, detail in RESULTS:
        mark = "PASS" if passed else "FAIL"
        print(f"[{mark}] {name}")
        print(f"       {detail}")
        ok += int(passed)
    print(f"\n{ok}/{len(RESULTS)} 通过")
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
