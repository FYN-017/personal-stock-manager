
import pandas as pd
from datetime import datetime
from database import get_connection


# =========================
# 1. 新增每日筆記
# =========================

def add_note(note_date, title, content, stock_id=None):

    datetime.strptime(note_date, "%Y-%m-%d")

    if not title.strip() or not content.strip():
        raise ValueError("筆記標題與內容不可空白")

    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO notes
            (stock_id, note_date, title, content)
            VALUES (?, ?, ?, ?)
        """, (
            int(stock_id) if stock_id not in (None, "") else None,
            note_date,
            title.strip(),
            content.strip()
        ))

        conn.commit()
        print("筆記新增成功")

    finally:
        conn.close()


# =========================
# 2. 查看每日筆記
# =========================

def show_notes():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            n.id,
            n.note_date,
            s.symbol,
            s.name,
            n.title,
            n.content
        FROM notes n
        LEFT JOIN stocks s ON n.stock_id = s.id
        ORDER BY n.note_date DESC, n.id DESC
    """, conn)

    conn.close()

    display(df)

    return df
