
import sqlite3
import pandas as pd
from datetime import datetime
from database import get_connection


# =========================
# 1. 新增股票
# =========================

def add_stock(market, symbol, name, sector=""):

    if market not in ["台股", "美股"]:
        raise ValueError("市場請填台股或美股")

    symbol = symbol.strip().upper()
    name = name.strip()

    if not symbol or not name:
        raise ValueError("股票代號與名稱不可空白")

    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO stocks
            (market, symbol, name, sector, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            market,
            symbol,
            name,
            sector,
            datetime.now().isoformat(timespec="seconds")
        ))

        conn.commit()
        print(f"新增成功：{symbol} {name}")

    except sqlite3.IntegrityError:
        print("新增失敗：這個市場的股票代號已存在")

    finally:
        conn.close()


# =========================
# 2. 查看股票
# =========================

def show_stocks():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            market,
            symbol,
            name,
            sector
        FROM stocks
        ORDER BY market, symbol
    """, conn)

    conn.close()

    display(df)

    return df


# =========================
# 3. 刪除股票
# =========================

def delete_stock(stock_id):

    conn = get_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM stocks WHERE id = ?",
            (int(stock_id),)
        )

        conn.commit()

        if cursor.rowcount:
            print("股票已刪除")
        else:
            print("找不到這個股票 ID")

    except sqlite3.IntegrityError:
        print("刪除失敗：這支股票仍有交易或筆記紀錄")

    finally:
        conn.close()
