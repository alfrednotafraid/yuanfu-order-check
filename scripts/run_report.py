# -*- coding: utf-8 -*-
"""一键跑批校核：命令行 `python scripts/run_report.py`，生成 Markdown 差异报告到 reports/。

内容：全量订单状态校核聚合 + 异常清单 + 3 个运输单的箱码比对演示（正常/漏件/串货）。
"""
import datetime as dt
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app import checks  # noqa: E402
from app.db import get_conn  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "reports")


def main():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT `订单号` FROM logistics_order WHERE `订单号` IS NOT NULL")
    orders = [r["订单号"] for r in cur.fetchall()]

    prod_cnt, ship_cnt, abnormal = Counter(), Counter(), []
    for o in orders:
        p = checks.production_check(cur, o)
        s = checks.shipment_check(cur, o)
        prod_cnt[p["verdict"]] += 1
        ship_cnt[s["verdict"] + "/" + s["detail"]["warehouse"]["verdict"]] += 1
        if p["verdict"] != "全量完成" or s["verdict"] != "全量发货" or s["detail"]["warehouse"]["verdict"] != "到齐":
            abnormal.append((o, p["verdict"], s["message"]))

    cur.execute("SELECT `运输单号`, COUNT(*) n FROM code_logistics GROUP BY 1 ORDER BY n DESC LIMIT 3")
    demos = []
    for row in cur.fetchall():
        t = row["运输单号"]
        cur.execute("SELECT `箱码编码` FROM code_logistics WHERE `运输单号`=%s", (t,))
        exp = [r["箱码编码"] for r in cur.fetchall()]
        cur.execute("SELECT `箱码编码` FROM code_logistics WHERE `运输单号`!=%s LIMIT 1", (t,))
        foreign = cur.fetchone()["箱码编码"]
        ok = checks.transport_check(cur, t, exp)
        miss = checks.transport_check(cur, t, exp[:-1])
        cross = checks.transport_check(cur, t, exp + [foreign])
        demos.append((t, row["n"], ok["verdict"], miss["message"], cross["message"]))

    conn.close()
    now = dt.datetime.now()
    lines = [
        "# 远孚订单交付链校核报告",
        f"\n生成时间：{now:%Y-%m-%d %H:%M}　数据源：MySQL yuanfu_check　范围：{len(orders)} 个订单\n",
        "## 1. 生产齐套聚合",
        "\n".join(f"- {k}：{v}" for k, v in prod_cnt.items()),
        "\n## 2. 发货完整 / 城配仓到货聚合",
        "\n".join(f"- {k}：{v}" for k, v in ship_cnt.items()),
        "\n## 3. 异常订单清单",
        ("\n".join(f"- `{o}`：{p}；{m}" for o, p, m in abnormal) or "- 无（样例数据全部为正常态，异常分支见第 4 节构造演示与 tests/ 断言）"),
        "\n## 4. 运输单箱码比对演示（应扫=实扫 / 构造漏件 / 构造串货）",
        "\n".join(f"- {t}（{n} 箱）：正常 -> {ok}；漏件 -> {m}；串货 -> {c}" for t, n, ok, m, c in demos),
        "\n> 校核判定全部由确定性 SQL/集合运算产出，LLM 不参与判断（设计说明见 docs/design.md）。",
    ]
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"check_report_{now:%Y%m%d_%H%M}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"orders={len(orders)} abnormal={len(abnormal)}  report -> {out}")


if __name__ == "__main__":
    main()
