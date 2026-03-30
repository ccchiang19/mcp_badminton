import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Any, Union
import io
import base64
from fastmcp import FastMCP
from fastmcp.utilities.types import Image # 確保匯入 Image
from typing import List, Any # 記得匯入型別

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool
def price_evaluation(score: int) -> str:
    if score < 50:
        return f"Good jobbbbbbbbb"
    return f"BAddddddddd!"

# --- Tool: 只負責收 JSON 並畫圖 ---
@mcp.tool()
def plot_from_json(data_list: List[dict], fruit_name: str) -> Any:
    """
    接收 JSON 列表與水果名稱，畫出走勢圖。
    """
    # 1. 轉換為 DataFrame
    df = pd.DataFrame(data_list)
    
    # 2. 強制轉換型別 (避免 JSON 進來全是字串的問題)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'])
    
    # 3. 篩選資料
    target = fruit_name.strip().capitalize()
    fruit_df = df[df['item'] == target].sort_values('date')
    
    # --- 重要修正：錯誤時不要只回傳字串，或確保型別一致 ---
    if fruit_df.empty:
        # 回傳一個能讓 AI 理解的錯誤訊息物件
        return f"Error: 找不到水果 '{target}' 的相關資料，請檢查輸入名稱是否正確。"

    # 4. 繪圖
    plt.figure(figsize=(10, 5))
    plt.plot(fruit_df['date'], fruit_df['price'], marker='o', linestyle='-', color='orange', label=target)
    plt.title(f"{target} Price Trend (Past 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 5. 轉為二進位流
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # --- 關鍵點：確保回傳的是 FastMCP 的 Image 物件 ---
    return Image(data=buf.read(), format="png")


@mcp.resource("files://{filename}")
def get_fruit_by_filename(filename: str) -> str:
    filepath = f"./{filename}"
    
    fruit_data = {}
    
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # row 會像是 {'item': 'Apples', 'price': '50'}
                # 我們把它存進一個字典方便查詢
                fruit_data[row['item'].strip()] = row['price'].strip()
        
        # 這裡你可以決定要回傳「全部資料」還是「特定邏輯」
        # 如果是回傳整份 JSON：
        return json.dumps(fruit_data, indent=4)
        
    except FileNotFoundError:
        return json.dumps({"error": "File not found"})

@mcp.resource("data://config")
def get_static_fruit_config() -> str:
    filepath = f"./data_new.csv"
    
    fruit_data = {}
    
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # row 會像是 {'item': 'Apples', 'price': '50'}
                # 我們把它存進一個字典方便查詢
                fruit_data[row['item'].strip()] = row['price'].strip()
        
        # 這裡你可以決定要回傳「全部資料」還是「特定邏輯」
        # 如果是回傳整份 JSON：
        return json.dumps(fruit_data, indent=4)
        
    except FileNotFoundError:
        return json.dumps({"error": "File not found"})

@mcp.resource("data://inventory")
def get_fruit_data() -> str:
    filepath = "./fruit_price.csv"
    import csv
    data = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return json.dumps(data)
    except FileNotFoundError:
        return json.dumps([])

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)