# -*- coding: utf-8 -*-
import re
from typing import List, Union

from fastapi import FastAPI
from pydantic import BaseModel

from app import checks
from app.db import get_conn

app = FastAPI(title="远孚定制家居订单校核服务", version="0.1.0")


class OrderReq(BaseModel):
    order_no: str


class ScanReq(BaseModel):
    no: str
    scanned_codes: Union[str, List[str]] = ""


def parse_codes(v):
    if isinstance(v, list):
        items = v
    else:
        items = re.split(r"[,\uFF0C;\uFF1B\s]+", v or "")
    return [s.strip() for s in items if s and s.strip()]


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/check/production")
def production(req: OrderReq):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            return checks.production_check(cur, req.order_no)
    finally:
        conn.close()


@app.post("/check/shipment")
def shipment(req: OrderReq):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            return checks.shipment_check(cur, req.order_no)
    finally:
        conn.close()


@app.post("/check/transport")
def transport(req: ScanReq):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            return checks.transport_check(cur, req.no, parse_codes(req.scanned_codes))
    finally:
        conn.close()


@app.post("/check/delivery")
def delivery(req: ScanReq):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            return checks.delivery_check(cur, req.no, parse_codes(req.scanned_codes))
    finally:
        conn.close()
