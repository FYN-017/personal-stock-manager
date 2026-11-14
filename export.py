
import pandas as pd
from database import get_connection


# =========================
# 匯出 CSV
# =========================

def export_csv():

    conn = get_connection()

    try:
        stocks = pd.read_sql_query(
            "SELECT * FROM stocks", conn
        )

        trades = pd.read_sql_query(
            "SELECT * FROM trades", conn
        )

        notes = pd.read_sql_query(
            "SELECT * FROM notes", conn
        )

        stocks.to_csv(
            "/content/stocks.csv",
            index=False,
            encoding="utf-8-sig"
        )

        trades.to_csv(
            "/content/trades.csv",
            index=False,
            encoding="utf-8-sig"
        )

        notes.to_csv(
            "/content/notes.csv",
            index=False,
            encoding="utf-8-sig"
        )

        print("CSV 匯出完成！")

    finally:
        conn.close()
