# -*- coding: utf-8 -*-
"""导出样例子集 -> sql/sample_data.sql（电话/手机号脱敏，供 clone 用户跑通测试）。"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pymysql  # noqa: E402

from app.db import get_conn  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sql", "sample_data.sql")

QUERIES = [
    ("prod_order", "`发货单号` IN ('MD000159435','MD000159412','MD000159311')"),
    ("logistics_order", "`订单号` = 'D33692250078306704'"),
    ("delivery_order", "`派送单号` = 'S36692250008301432'"),
    ("code_logistics", "`运输单号` = 'YSS001288574' OR `箱码编码` = '0HKLXR'"),
    ("code_delivery", "`运输单号` = 'YSS001288574'"),
]


def main():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    parts = ["-- 样例子集：1 个完整订单链路（手机号已脱敏）  由 scripts/export_sample.py 生成"]
    for table, where in QUERIES:
        cur.execute(f"SELECT * FROM `{table}` WHERE {where}")
        rows = cur.fetchall()
        if not rows:
            print(f"WARN empty: {table}")
            continue
        cols = ",".join(f"`{c}`" for c in rows[0].keys())
        vals = ["(" + ",".join(cur.connection.escape(v) for v in r.values()) + ")" for r in rows]
        # 注意：不生成 DELETE/TRUNCATE——样例文件只允许导入新建空库，避免误删主库数据
        parts.append(f"INSERT INTO `{table}` ({cols}) VALUES\n" + ",\n".join(vals) + ";")
        print(f"{table}: {len(rows)} rows")
    conn.close()
    sql = "\n\n".join(parts) + "\n"
    sql = re.sub(r"'(1[0-9]{10})'", "'1**********'", sql)  # 手机号脱敏
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(sql)
    print("written:", os.path.normpath(OUT), len(sql), "bytes")


if __name__ == "__main__":
    main()
