
import os
import sys

# 加入專案資料夾路徑
project_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_folder)

# 匯入各個模組
from database import init_database
from stocks import add_stock, show_stocks, delete_stock
from trades import add_trade, show_trades
from notes import add_note, show_notes
from export import export_csv


# =========================
# 主程式
# =========================

def main():

    # 初始化資料庫
    init_database()

    print("================================")
    print("       個人股票管理系統")
    print("================================")

    print("目前已完成各功能模組的整合。")
    print("股票管理、交易管理、筆記管理及 CSV 匯出")
    print("將由主程式統一呼叫。")


if __name__ == "__main__":
    main()
