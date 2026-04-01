import json
import pandas as pd
import io
from fastmcp import FastMCP

mcp = FastMCP("Advanced Pipeline Server")

# 模擬一個簡單的資料庫/快取
DATA_STORE = {
    "raw_data": None,
    "analysis_result": None
}

# --- Tool A: 負責讀取資料 ---
@mcp.tool()
def load_data_from_file(filename: str) -> str:
    """[Tool A] 讀取本地檔案並存入系統快取。"""
    try:
        df = pd.read_csv(f"./{filename}")
        # 將資料存入全域變數，方便其他工具使用
        DATA_STORE["raw_data"] = df.to_dict(orient="records")
        return f"成功讀取 {len(df)} 筆資料，已載入系統。"
    except Exception as e:
        return f"讀取失敗: {str(e)}"

# --- Tool B: 負責分析資料 ---
@mcp.tool()
def analyze_current_data() -> str:
    """[Tool B] 分析目前載入的資料，並準備 UI 內容。"""
    if DATA_STORE["raw_data"] is None:
        return "錯誤：尚未載入任何資料，請先執行 load_data_from_file。"
    
    df = pd.DataFrame(DATA_STORE["raw_data"])
    # 進行一些簡單分析
    summary = {
        "total_items": len(df),
        "avg_price": df['price'].astype(float).mean(),
        "max_price": df['price'].astype(float).max()
    }
    # 將分析後的結果存起來給 Resource 使用
    DATA_STORE["analysis_result"] = summary
    return "分析完成！你可以查看 ui://dashboard 資源來獲取報表。"

# --- Resource: 負責輸出 UI 內容 ---
@mcp.resource("ui://dashboard")
def get_analysis_dashboard() -> str:
    """[Resource] 輸出最終的分析 UI（Markdown 格式）。"""
    res = DATA_STORE["analysis_result"]
    
    if res is None:
        return "# 儀表板\n目前沒有可顯示的分析數據。請 AI 先執行分析工具。"
    
    # 這裡我們用 Markdown 做出一個漂亮的 UI 效果
    ui_output = f"""
# 🍎 水果數據分析摘要
---
* **總品項數量**: {res['total_items']}
* **平均價格**: ${res['avg_price']:.2f}
* **最高單價**: ${res['max_price']:.2f}

> 提示：此數據由 Tool B 自動生成，僅供參考。
"""
    return ui_output

if __name__ == "__main__":
    # 建議開發時先用 stdio，接入 Claude 較方便；若要用 Inspector 測試 port 也行
    mcp.run()