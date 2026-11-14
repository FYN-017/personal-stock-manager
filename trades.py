
import sqlite3
import pandas as pd
from datetime import datetime
from database import get_connection


# =========================
# 1. 新增交易紀錄
# =========================

def add_trade(stock_id, trade_date, side,
              quantity, price, fee=0, note=""):

    if side not in ["買進", "賣出"]:
        raise ValueError("交易類型請填買進或賣出")

    datetime.strptime(trade_date, "%Y-%m-%d")

    quantity = float(quantity)
    price = float(price)
    fee = float(fee)

    if quantity <= 0 or price < 0 or fee < 0:
        raise ValueError("數量必須大於 0，價格與手續費不可為負")

    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO trades
            (stock_id, trade_date, side, quantity, price, fee, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            int(stock_id),
            trade_date,
            side,
            quantity,
            price,
            fee,
            note
        ))

        conn.commit()
        print("交易紀錄新增成功")

    finally:
        conn.close()


# =========================
# 2. 查看交易紀錄
# =========================

def show_trades():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            t.id,
            s.market,
            s.symbol,
            s.name,
            t.trade_date,
            t.side,
            t.quantity,
            t.price,
            t.fee,
            t.quantity * t.price AS amount,
            t.note
        FROM trades t
        JOIN stocks s ON t.stock_id = s.id
        ORDER BY t.trade_date DESC, t.id DESC
    """, conn)

    conn.close()

    display(df)

    return df
