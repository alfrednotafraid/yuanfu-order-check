# -*- coding: utf-8 -*-
"""MySQL 连接助手：统一从 config.ini 读配置，返回 DictCursor 连接。"""
import configparser
import os

import pymysql

_CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.ini")


def get_conn():
    cp = configparser.ConfigParser()
    cp.read(_CFG, encoding="utf-8")
    m = cp["mysql"]
    return pymysql.connect(
        host=m["host"], port=int(m["port"]), user=m["user"], password=m["password"],
        database=m["database"], charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
    )
