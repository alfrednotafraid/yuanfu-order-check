# -*- coding: utf-8 -*-
"""Excel -> MySQL 导入脚本（远孚齐套校核 demo）
- 7 张表全字段导入，字段名保留原始中文（数据忠实落地，便于溯源）
- 类型自动推断：DATETIME / BIGINT / DECIMAL / VARCHAR(64) / TEXT
- 生成的建表语句另存 sql/schema.sql，供仓库与复现使用
"""
import configparser
import datetime as dt
import os
import openpyxl
import pymysql

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SQL = os.path.join(HERE, "..", "sql", "schema.sql")
_cp = configparser.ConfigParser()
_cp.read(os.path.join(HERE, "..", "config.ini"), encoding="utf-8")
# 素材目录默认取项目同级 ../素材，可在 config.ini [import] src 覆盖
SRC = _cp["import"]["src"] if _cp.has_option("import", "src") else os.path.normpath(os.path.join(HERE, "..", "..", "素材"))
DB = dict(host=_cp["mysql"]["host"], port=int(_cp["mysql"]["port"]),
          user=_cp["mysql"]["user"], password=_cp["mysql"]["password"], charset="utf8mb4")
SCHEMA = _cp["mysql"]["database"]

TABLES = [
    ("prod_order",      "订单数据/生产订单.xlsx"),
    ("logistics_order", "订单数据/物流订单.xlsx"),
    ("delivery_order",  "订单数据/配送订单.xlsx"),
    ("pickup_order",    "订单数据/配送订单（自提单）.xlsx"),
    ("code_logistics",  "货品编码/物流订单-货品编码.xlsx"),
    ("code_delivery",   "货品编码/配送（派送）订单-货品编码.xlsx"),
    ("code_pickup",     "货品编码/配送（自提）订单-货品编码.xlsx"),
]

INDEX_COLS = {"发货单号", "订单号", "运输单号", "交期子单号", "生产单号", "箱码编码", "订单原单号"}


def norm(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v else None
    return v


def infer_type(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return "VARCHAR(64)"
    if all(isinstance(v, (dt.datetime, dt.date)) for v in vals):
        return "DATETIME"
    if all(isinstance(v, bool) or (isinstance(v, (int, float)) and float(v).is_integer()) for v in vals):
        return "BIGINT"
    if all(isinstance(v, (int, float)) for v in vals):
        return "DECIMAL(18,4)"
    maxlen = max(len(str(v)) for v in vals)
    return "VARCHAR(64)" if maxlen <= 64 else "TEXT"


def main():
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {SCHEMA} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
    cur.execute(f"USE {SCHEMA}")
    ddl_out = []
    for table, rel in TABLES:
        wb = openpyxl.load_workbook(os.path.join(SRC, rel), read_only=True)
        ws = wb.worksheets[0]
        rows = ws.iter_rows(values_only=True)
        header = [str(h).strip() for h in next(rows)]
        data = [tuple(norm(v) for v in r[:len(header)]) for r in rows if any(v is not None for v in r[:len(header)])]
        wb.close()

        cols = list(zip(header, (infer_type([r[i] for r in data]) for i in range(len(header)))))
        col_defs = "`row_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY"
        idxs = []
        for name, typ in cols:
            col_defs += f",\n  `{name}` {typ} NULL"
            if name in INDEX_COLS and typ.startswith(("VARCHAR", "BIGINT", "DATETIME")):
                idxs.append(f"ALTER TABLE `{table}` ADD INDEX `idx_{name}` (`{name}`)")
        ddl = f"CREATE TABLE `{table}` (\n{col_defs}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        ddl_out.append(f"-- {rel}  ({len(data)} 行)\n{ddl}\n" + "\n".join(idxs) + "\n")

        cur.execute(f"DROP TABLE IF EXISTS `{table}`")
        cur.execute(ddl)
        ph = ",".join(["%s"] * len(header))
        sql = f"INSERT INTO `{table}` ({','.join('`' + h + '`' for h in header)}) VALUES ({ph})"
        for i in range(0, len(data), 1000):
            cur.executemany(sql, data[i:i + 1000])
        conn.commit()
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        print(f"{table:<16} rows={cur.fetchone()[0]:>6}  cols={len(header)}")

    with open(OUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- 自动生成 by scripts/import_excel.py\n" + "\n".join(ddl_out))
    conn.close()
    print("schema.sql written:", os.path.normpath(OUT_SQL))


if __name__ == "__main__":
    main()
