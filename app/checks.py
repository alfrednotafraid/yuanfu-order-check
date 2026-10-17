# -*- coding: utf-8 -*-
"""四个校核场景的确定性实现（LLM 不参与判断，只做理解与转述）。

规则来源：素材/校验逻辑.docx
  1 生产齐套   ：子单齐套状态聚合 -> 全量完成 / 部分生产 / 未启动生产
  2 发货完整   ：子单发货单号绑定率 -> 全量发货 / 部分发货 / 未发货
                （附带城配仓到货聚合：到齐 / 部分到货 / 未到货，仅干仓配）
  3 运输串少漏 ：运输单号应装箱码 vs 实扫箱码 -> 漏件 / 多件 / 串货 / 未知码
  4 配送齐套   ：派送单应装箱码 vs 实扫箱码 + 归属合法性（分货正确性）
"""
from collections import Counter

# ---------- 单号解析：不同表用不同号段（D3369… 在物流单、MD… 在生产/发货单） ----------

def resolve_ship_codes(cur, order_no):
    """把任意输入单号解析成一组发货单号。返回 (发货单号列表, 解析路径)。"""
    cur.execute(
        "SELECT DISTINCT `发货单号` FROM prod_order WHERE `订单号`=%s OR `发货单号`=%s OR `订单原单号`=%s",
        (order_no, order_no, order_no))
    rows = [r["发货单号"] for r in cur.fetchall() if r["发货单号"]]
    if rows:
        return rows, "prod_order"
    cur.execute(
        "SELECT DISTINCT `发货单号` FROM logistics_order WHERE `订单号`=%s OR `发货单号`=%s OR `订单原单号`=%s",
        (order_no, order_no, order_no))
    rows = [r["发货单号"] for r in cur.fetchall() if r["发货单号"]]
    return (rows, "logistics_order") if rows else ([], "not_found")


# ---------- 场景 1/2：状态聚合 ----------

def production_check(cur, order_no):
    ships, path = resolve_ship_codes(cur, order_no)
    if not ships:
        return {"verdict": "未找到", "message": f"单号 {order_no} 在生产订单中无记录（解析路径 {path}）"}
    ph = ",".join(["%s"] * len(ships))
    cur.execute(
        f"SELECT `交期子单号`,`发货单号`,`齐套状态`,`作废标识` FROM prod_order WHERE `发货单号` IN ({ph})", ships)
    subs = [r for r in cur.fetchall() if r["作废标识"] != "作废"]
    done = sum(1 for s in subs if s["齐套状态"] == "齐套")
    null = sum(1 for s in subs if not s["齐套状态"])
    if done == len(subs):
        v = "全量完成"
    elif null == len(subs):
        v = "未启动生产"
    else:
        v = "部分生产"
    pending = [s["交期子单号"] for s in subs if s["齐套状态"] != "齐套"]
    return {"verdict": v, "detail": {"total_sub": len(subs), "ready_sub": done, "pending_subs": pending},
            "message": f"订单 {order_no} 共 {len(subs)} 个交期子单，齐套 {done} 个 -> {v}"}


def shipment_check(cur, order_no):
    ships, path = resolve_ship_codes(cur, order_no)
    if not ships:
        return {"verdict": "未找到", "message": f"单号 {order_no} 无记录（解析路径 {path}）"}
    ph = ",".join(["%s"] * len(ships))
    cur.execute(
        f"""SELECT `交期子单号`,`发货单号`,`入库状态`,`到货状态`,`作废标识`
            FROM prod_order WHERE `发货单号` IN ({ph})""", ships)
    subs = [r for r in cur.fetchall() if r["作废标识"] != "作废"]
    bound = sum(1 for s in subs if s["发货单号"])
    inbound_ok = sum(1 for s in subs if s["入库状态"] == "已入库")
    unbound = [s["交期子单号"] for s in subs if not s["发货单号"]]
    v = "全量发货" if bound == len(subs) else ("未发货" if bound == 0 else "部分发货")
    iv = "到齐" if inbound_ok == len(subs) else ("未到货" if inbound_ok == 0 else "部分到货")
    return {"verdict": v,
            "detail": {"total_sub": len(subs), "bound": bound, "unbound_subs": unbound,
                       "warehouse": {"inbound_ok": inbound_ok, "verdict": iv}},
            "message": f"订单 {order_no}：{bound}/{len(subs)} 子单已绑定发货单 -> {v}；城配仓入库 {inbound_ok}/{len(subs)} -> {iv}"}


# ---------- 箱码比对核心（场景 3/4 共用） ----------

def _locate(cur, code):
    """查箱码归属：返回 (表, 运输单号, 发货单号) 列表。"""
    found = []
    for t in ("code_logistics", "code_delivery", "code_pickup"):
        cur.execute(f"SELECT `运输单号`,`发货单号` FROM {t} WHERE `箱码编码`=%s", (code,))
        found += [(t, r["运输单号"], r["发货单号"]) for r in cur.fetchall()]
    return found


def diff_boxes(cur, expected_rows, scanned):
    """expected_rows: [{箱码编码,货品名称,品类}]；scanned: 实扫箱码列表。"""
    expected = {r["箱码编码"]: r for r in expected_rows}
    scan_cnt = Counter(scanned)
    missing = [c for c in expected if c not in scan_cnt]
    extra = [c for c in scan_cnt if c not in expected]
    crossed, wrong_split, unknown = [], [], []
    for c in extra:
        locs = _locate(cur, c)
        if not locs:
            unknown.append(c)
        elif any(l[1] in {r.get("运输单号") for r in expected_rows} for l in locs):
            wrong_split.append({"code": c, "belongs": locs})  # 同车不同单 -> 分货错误
        else:
            crossed.append({"code": c, "belongs": locs})       # 别车 -> 串货
    dup = [c for c, n in scan_cnt.items() if n > 1 and c in expected]
    ok = not (missing or extra or dup)
    return {"expected_n": len(expected), "scanned_n": len(scanned),
            "missing": [{"code": c, "name": expected[c].get("货品名称")} for c in missing],
            "extra": extra, "crossed": crossed, "wrong_split": wrong_split,
            "unknown": unknown, "duplicated": dup, "ok": ok}


def transport_check(cur, transport_no, scanned):
    cur.execute("SELECT `箱码编码`,`货品名称`,`品类`,`运输单号` FROM code_logistics WHERE `运输单号`=%s", (transport_no,))
    rows = cur.fetchall()
    if not rows:
        return {"verdict": "未找到", "message": f"运输单 {transport_no} 无应装箱码"}
    d = diff_boxes(cur, rows, scanned)
    v = "交收正常" if d["ok"] else f"异常：漏{len(d['missing'])} 多{len(d['extra'])} 串{len(d['crossed'])} 分错{len(d['wrong_split'])} 未知{len(d['unknown'])}"
    return {"verdict": v, "detail": d,
            "message": f"运输单 {transport_no}：应装 {d['expected_n']} 箱，实扫 {d['scanned_n']} 箱 -> {v}"}


def delivery_check(cur, delivery_no, scanned):
    cur.execute("SELECT DISTINCT `发货单号`,`运输单号` FROM delivery_order WHERE `派送单号`=%s OR `发货单号`=%s",
                (delivery_no, delivery_no))
    links = cur.fetchall()
    if not links:
        return {"verdict": "未找到", "message": f"派送单 {delivery_no} 无记录"}
    ships = {l["发货单号"] for l in links}
    trans = {l["运输单号"] for l in links if l["运输单号"]}
    ph, th = ",".join(["%s"] * len(ships)), ",".join(["%s"] * len(trans or {None}))
    q = f"SELECT `箱码编码`,`货品名称`,`品类`,`运输单号`,`发货单号` FROM code_delivery WHERE `发货单号` IN ({ph})"
    args = list(ships)
    if trans:
        q += f" AND `运输单号` IN ({th})"
        args += list(trans)
    cur.execute(q, args)
    rows = cur.fetchall()
    if not rows:
        return {"verdict": "无货品", "message": f"派送单 {delivery_no} 未找到箱码明细"}
    d = diff_boxes(cur, rows, scanned)
    v = "齐套且分货正确" if d["ok"] else (
        f"异常：缺{len(d['missing'])} 多{len(d['extra'])} 分货错{len(d['wrong_split'])} 串{len(d['crossed'])}")
    return {"verdict": v, "detail": d,
            "message": f"派送单 {delivery_no}：应送 {d['expected_n']} 箱，实扫 {d['scanned_n']} 箱 -> {v}"}
