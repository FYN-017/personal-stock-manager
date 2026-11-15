
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
from database import get_connection, init_database

# =========================
# 1. 頁面設定
# =========================

st.set_page_config(
    page_title="個人股票管理系統",
    page_icon="📈",
    layout="wide"
)

init_database()

st.title("📈 個人股票管理系統")
st.caption("Personal Stock Management System")

# =========================
# 2. 資料讀取
# =========================

def read_data(sql, params=()):
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    finally:
        conn.close()


def get_stocks():
    return read_data("""
        SELECT id, market, symbol, name, sector
        FROM stocks
        ORDER BY market, symbol
    """)


def get_trades():
    return read_data("""
        SELECT t.id, s.market, s.symbol, s.name,
               t.trade_date, t.side, t.quantity,
               t.price, t.fee,
               t.quantity * t.price AS amount,
               t.note
        FROM trades t
        JOIN stocks s ON t.stock_id = s.id
        ORDER BY t.trade_date DESC, t.id DESC
    """)


def get_notes():
    return read_data("""
        SELECT n.id, n.note_date, s.symbol,
               s.name, n.title, n.content
        FROM notes n
        LEFT JOIN stocks s ON n.stock_id = s.id
        ORDER BY n.note_date DESC, n.id DESC
    """)


# =========================
# 3. 側邊選單
# =========================

menu = st.sidebar.radio(
    "功能選單",
    [
        "首頁總覽",
        "股票管理",
        "交易紀錄",
        "每日筆記",
        "資料匯出"
    ]
)

# =========================
# 4. 首頁總覽
# =========================

if menu == "首頁總覽":

    st.header("系統總覽")

    stocks = get_stocks()
    trades = get_trades()
    notes = get_notes()

    col1, col2, col3 = st.columns(3)

    col1.metric("股票數量", len(stocks))
    col2.metric("交易筆數", len(trades))
    col3.metric("筆記數量", len(notes))

    st.divider()

    st.subheader("我的股票")

    if stocks.empty:
        st.info("目前還沒有股票資料。")
    else:
        st.dataframe(stocks, use_container_width=True)

    st.subheader("最近交易紀錄")

    if trades.empty:
        st.info("目前還沒有交易紀錄。")
    else:
        st.dataframe(
            trades.head(10),
            use_container_width=True
        )

# =========================
# 5. 股票管理
# =========================

elif menu == "股票管理":

    st.header("📊 股票管理")

    tab1, tab2 = st.tabs(["新增股票", "查看及刪除"])

    with tab1:

        with st.form("add_stock_form"):

            market = st.selectbox(
                "市場",
                ["台股", "美股"]
            )

            symbol = st.text_input("股票代號")
            name = st.text_input("股票名稱")
            sector = st.text_input("產業")

            submitted = st.form_submit_button("新增股票")

            if submitted:

                if not symbol.strip() or not name.strip():
                    st.error("股票代號及名稱不可空白。")

                else:
                    conn = get_connection()

                    try:
                        conn.execute("""
                            INSERT INTO stocks
                            (market, symbol, name, sector, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            market,
                            symbol.strip().upper(),
                            name.strip(),
                            sector.strip(),
                            datetime.now().isoformat(timespec="seconds")
                        ))

                        conn.commit()
                        st.success("股票新增成功！")
                        st.rerun()

                    except sqlite3.IntegrityError:
                        st.error("這個市場的股票代號已存在。")

                    finally:
                        conn.close()

    with tab2:

        stocks = get_stocks()

        if stocks.empty:
            st.info("目前沒有股票資料。")

        else:
            st.dataframe(stocks, use_container_width=True)

            stock_options = {
                f"{row['market']}｜{row['symbol']}｜{row['name']}": row["id"]
                for _, row in stocks.iterrows()
            }

            selected = st.selectbox(
                "選擇要刪除的股票",
                list(stock_options.keys())
            )

            if st.button("刪除股票", type="secondary"):

                stock_id = stock_options[selected]
                conn = get_connection()

                try:
                    conn.execute(
                        "DELETE FROM stocks WHERE id = ?",
                        (stock_id,)
                    )

                    conn.commit()
                    st.success("股票已刪除。")
                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error("此股票仍有交易或筆記紀錄，無法刪除。")

                finally:
                    conn.close()

# =========================
# 6. 交易紀錄
# =========================

elif menu == "交易紀錄":

    st.header("💰 交易紀錄")

    tab1, tab2 = st.tabs(["新增交易", "交易明細"])

    stocks = get_stocks()

    with tab1:

        if stocks.empty:
            st.warning("請先新增股票資料。")

        else:

            stock_options = {
                f"{row['market']}｜{row['symbol']}｜{row['name']}": row["id"]
                for _, row in stocks.iterrows()
            }

            with st.form("add_trade_form"):

                selected = st.selectbox(
                    "選擇股票",
                    list(stock_options.keys())
                )

                trade_date = st.date_input(
                    "交易日期",
                    value=date.today()
                )

                side = st.selectbox(
                    "交易類型",
                    ["買進", "賣出"]
                )

                quantity = st.number_input(
                    "交易股數",
                    min_value=1,
                    step=1
                )

                price = st.number_input(
                    "成交價格",
                    min_value=0.01,
                    step=0.5
                )

                fee = st.number_input(
                    "手續費",
                    min_value=0.0,
                    step=1.0
                )

                note = st.text_input("備註")

                submitted = st.form_submit_button("新增交易")

                if submitted:

                    conn = get_connection()

                    try:
                        conn.execute("""
                            INSERT INTO trades
                            (stock_id, trade_date, side,
                             quantity, price, fee, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            stock_options[selected],
                            trade_date.isoformat(),
                            side,
                            quantity,
                            price,
                            fee,
                            note
                        ))

                        conn.commit()
                        st.success("交易紀錄新增成功！")
                        st.rerun()

                    finally:
                        conn.close()

    with tab2:

        trades = get_trades()

        if trades.empty:
            st.info("目前沒有交易紀錄。")
        else:
            st.dataframe(trades, use_container_width=True)

# =========================
# 7. 每日筆記
# =========================

elif menu == "每日筆記":

    st.header("📝 每日筆記")

    tab1, tab2 = st.tabs(["新增筆記", "查看筆記"])

    stocks = get_stocks()

    with tab1:

        stock_options = {
            "不指定股票": None
        }

        for _, row in stocks.iterrows():
            stock_options[
                f"{row['symbol']}｜{row['name']}"
            ] = row["id"]

        with st.form("add_note_form"):

            note_date = st.date_input(
                "筆記日期",
                value=date.today()
            )

            selected = st.selectbox(
                "關聯股票",
                list(stock_options.keys())
            )

            title = st.text_input("筆記標題")
            content = st.text_area("筆記內容")

            submitted = st.form_submit_button("儲存筆記")

            if submitted:

                if not title.strip() or not content.strip():
                    st.error("標題及內容不可空白。")

                else:

                    conn = get_connection()

                    try:
                        conn.execute("""
                            INSERT INTO notes
                            (stock_id, note_date, title, content)
                            VALUES (?, ?, ?, ?)
                        """, (
                            stock_options[selected],
                            note_date.isoformat(),
                            title.strip(),
                            content.strip()
                        ))

                        conn.commit()
                        st.success("筆記新增成功！")
                        st.rerun()

                    finally:
                        conn.close()

    with tab2:

        notes = get_notes()

        if notes.empty:
            st.info("目前沒有筆記。")

        else:

            for _, row in notes.iterrows():

                with st.expander(
                    f"{row['note_date']}｜{row['title']}"
                ):

                    st.write(
                        "關聯股票：",
                        row["symbol"] if pd.notna(row["symbol"]) else "無"
                    )

                    st.write(row["content"])

# =========================
# 8. 資料匯出
# =========================

elif menu == "資料匯出":

    st.header("📥 資料匯出")

    tables = {
        "股票資料": ("stocks", "stocks.csv"),
        "交易紀錄": ("trades", "trades.csv"),
        "每日筆記": ("notes", "notes.csv")
    }

    for label, (table_name, file_name) in tables.items():

        df = read_data(f"SELECT * FROM {table_name}")

        st.subheader(label)

        st.write(f"目前共有 {len(df)} 筆資料")

        st.download_button(
            label=f"下載{label} CSV",
            data=df.to_csv(
                index=False,
                encoding="utf-8-sig"
            ),
            file_name=file_name,
            mime="text/csv"
        )

st.sidebar.divider()
st.sidebar.caption("個人股票管理系統 v1.0")

