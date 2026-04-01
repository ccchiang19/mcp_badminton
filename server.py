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
# --- 4. Prompt (把流程包起來) ---
@mcp.prompt("fruit_analysis_report")
def fruit_analysis_report(filename: str = "fruit_price.csv") -> str:
    """
    這是一個自動化分析流程：
    1. 使用 fetch_inventory_data 載入指定的 CSV。
    2. 使用 generate_analysis_report 進行數據處理。
    3. 最後讀取 ui://final-report 並呈現給使用者。
    """
    return (
        f"請按照以下步驟操作：\n"
        f"首先，呼叫 `fetch_inventory_data` 工具，載入檔案：{filename}。\n"
        f"接著，呼叫 `generate_analysis_report` 工具進行數據分析。\n"
        f"最後，讀取 `ui://final-report` 資源，並將其中的報表內容完整呈現給我。"
    )

@mcp.tool()
def clear_internal_data() -> str:
    """
    [清空工具] 徹底清除目前系統暫存區的所有原始資料與分析報表。
    當你想開始一個全新的分析任務時，請執行此工具。
    """
    _INTERNAL_STORAGE["raw_data"] = None
    _INTERNAL_STORAGE["analysis_report"] = None
    return "系統暫存區已清空。現在可以載入新的資料夾或檔案。"

# 如果你也想要一個 "Empty" 的 Prompt (讓 AI 準備好重啟任務)
@mcp.prompt("start-fresh")
def start_fresh_prompt() -> str:
    """
    引導 AI 清空目前狀態並準備接受新任務。
    """
    return "請先呼叫 `clear_internal_data` 工具清空目前狀態，然後詢問使用者想要分析哪一個新的檔案。"


if __name__ == "__main__":
    mcp.run()