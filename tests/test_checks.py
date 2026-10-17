# -*- coding: utf-8 -*-
"""串/少/漏/分错 断言测试：从库里取真实应装清单，构造异常实扫列表，校验服务输出。

背景：样例数据 1379 条生产订单全部是"齐套/已发货/已入库"的正常态，
"部分生产/漏件/串货"等分支无法用原始数据触发，故在输入侧构造异常。
运行前提：MySQL 已导入数据 + uvicorn 已在 8000 端口启动。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import requests  # noqa: E402

from app import checks  # noqa: E402
from app.db import get_conn  # noqa: E402

BASE = "http://localhost:8000"
TRANSPORT = "YSS001288574"          # 15 箱，跨 2 个发货单
DELIVERY = "S36692250008301432"     # 派送单 -> MD000159412，应送 7 箱
ORDER = "MD000159435"               # 2 个子单，全齐套
ORDER_D = "D33692250078306704"      # 物流单号段，测跨表解析


def codes_of(sql, arg):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, (arg,))
        out = [r["箱码编码"] for r in cur.fetchall()]
    conn.close()
    return out


def post(path, body):
    return requests.post(f"{BASE}{path}", json=body, timeout=10).json()


def test_unbound_branches():
    """未发货/部分发货分支：样例数据全为已绑定，用事务内虚构子单验证后回滚。"""
    conn = get_conn()
    cur = conn.cursor()
    conn.begin()
    try:
        cur.execute("""INSERT INTO prod_order
            (`订单号`,`订单原单号`,`交期子单号`,`发货单号`,`齐套状态`,`入库状态`,`作废标识`)
            VALUES ('TEST999','TEST999','SUB99A','MDTEST99','齐套','已入库',''),
                   ('TEST999','TEST999','SUB99B',NULL,NULL,NULL,''),
                   ('TEST888','TEST888','SUB88A',NULL,NULL,NULL,''),
                   ('TEST888','TEST888','SUB88B',NULL,NULL,NULL,'')""")
        s9 = checks.shipment_check(cur, "TEST999")
        s8 = checks.shipment_check(cur, "TEST888")
        p9 = checks.production_check(cur, "TEST999")
        results = [
            s9["verdict"] == "部分发货" and s9["detail"]["unbound_subs"] == ["SUB99B"],
            s8["verdict"] == "未发货" and s8["detail"]["bound"] == 0,
            p9["verdict"] == "部分生产",
        ]
    finally:
        conn.rollback()
        conn.close()
    return all(results), results


def main():
    exp = codes_of("SELECT `箱码编码` FROM code_logistics WHERE `运输单号`=%s", TRANSPORT)
    foreign = codes_of("SELECT `箱码编码` FROM code_logistics WHERE `运输单号`!=%s LIMIT 1", TRANSPORT)[0]
    deli_exp = codes_of(
        """SELECT c.`箱码编码` FROM code_delivery c JOIN delivery_order d
           ON c.`发货单号`=d.`发货单号` AND c.`运输单号`=d.`运输单号`
           WHERE d.`派送单号`=%s""", DELIVERY)
    same_truck_other = [c for c in exp if c not in deli_exp][0]  # 同车、非本派送单

    cases = [
        ("生产齐套-全量完成", "/check/production", {"order_no": ORDER},
         lambda r: r["verdict"] == "全量完成" and r["detail"]["total_sub"] == 2),
        ("发货完整-跨表解析+到齐", "/check/shipment", {"order_no": ORDER_D},
         lambda r: r["verdict"] == "全量发货" and r["detail"]["warehouse"]["verdict"] == "到齐"),
        ("单号不存在-明确报未找到", "/check/production", {"order_no": "NOPE999"},
         lambda r: r["verdict"] == "未找到"),
        ("运输-正常交收", "/check/transport", {"no": TRANSPORT, "scanned_codes": exp},
         lambda r: r["detail"]["ok"] is True),
        ("运输-漏件(少1箱)", "/check/transport", {"no": TRANSPORT, "scanned_codes": exp[:-1]},
         lambda r: [m["code"] for m in r["detail"]["missing"]] == [exp[-1]]),
        ("运输-串货(混入他车1箱)", "/check/transport", {"no": TRANSPORT, "scanned_codes": exp + [foreign]},
         lambda r: len(r["detail"]["crossed"]) == 1 and r["detail"]["crossed"][0]["code"] == foreign),
        ("运输-重复扫码", "/check/transport", {"no": TRANSPORT, "scanned_codes": exp + [exp[0]]},
         lambda r: r["detail"]["duplicated"] == [exp[0]]),
        ("配送-分货错误(同车错单)", "/check/delivery", {"no": DELIVERY, "scanned_codes": deli_exp + [same_truck_other]},
         lambda r: len(r["detail"]["wrong_split"]) == 1 and r["detail"]["missing"] == []),
        ("配送-正常齐套", "/check/delivery", {"no": DELIVERY, "scanned_codes": deli_exp},
         lambda r: r["detail"]["ok"] is True),
    ]

    ub_ok, ub_detail = test_unbound_branches()
    cases.append(("发货-未发货/部分发货分支(事务回滚)", None, None, lambda r: ub_ok))
    if not ub_ok:
        print(f"       未发货分支断言明细: {ub_detail}")

    failed = 0
    for name, path, body, check in cases:
        try:
            if path is None:
                ok = check(None)
            else:
                ok = check(post(path, body))
        except Exception as e:  # noqa: BLE001
            ok, name = False, f"{name} ({e})"
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        failed += 0 if ok else 1
    print(f"\n{len(cases) - failed}/{len(cases)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
