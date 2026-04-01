import json
import csv
import pandas as pd
import io
from fastmcp import FastMCP

mcp = FastMCP("Secure Fruit Server")

# 內部狀態儲存（外部無法直接存取）
_INTERNAL_STORAGE = {
    "raw_data": None,
    "analysis_report": None
}

# --- 1. 改良後的 Tool A: 讀取資料 (取代 Resource) ---
@mcp.tool()
def fetch_inventory_data(filename: str = "fruit_price.csv") -> str:
    """
    [安全讀取] 只有在需要時才從本地檔案載入庫存資料。
    這不會預先顯示在 Resource 列表中。
    """
    data = []
    try:
        with open(f"./{filename}", mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        # 存入內部暫存，不直接噴出所有內容給使用者看
        _INTERNAL_STORAGE["raw_data"] = data
        
        # 只回傳摘要，保護隱私
        return f"成功讀取 {len(data)} 筆資料。資料已載入安全緩衝區，請執行分析工具以查看結果。"
    except FileNotFoundError:
        return "錯誤：找不到指定的資料檔案。"

# --- 2. Tool B: 分析並產生報表 ---
@mcp.tool()
def generate_analysis_report() -> str:
    """
    [分析工具] 針對已載入的資料進行統計。
    """
    raw = _INTERNAL_STORAGE["raw_data"]
    if not raw:
        return "請先執行 fetch_inventory_data 載入資料。"
    
    df = pd.DataFrame(raw)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    avg_p = df['price'].mean()
    
    # 產生分析結果存入狀態
    report = f"### 庫存分析報表\n- 總品項: {len(df)}\n- 平均單價: {avg_p:.2f}"
    _INTERNAL_STORAGE["analysis_report"] = report
    
    return "分析完成！報表已準備好。"

# --- 3. 唯一的 Resource: 最終輸出 UI ---
# 注意：這裡我們只留一個「結果出口」，且沒資料時它什麼都不顯示
@mcp.resource("ui://final-report")
def show_report() -> str:
    """顯示最終經過處理的分析報表。"""
    report = _INTERNAL_STORAGE["analysis_report"]
    if not report:
        return "目前沒有已產生的報表。請先要求 AI 執行分析工具。"
    return report

if __name__ == "__main__":
    mcp.run()