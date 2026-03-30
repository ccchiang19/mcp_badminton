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

@mcp.tool()
def plot_from_json(data_list: list, fruit_name: str) -> Image:
    # --- 資料處理 ---
    df = pd.DataFrame(data_list)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'])
    
    target = fruit_name.strip().capitalize()
    fruit_df = df[df['item'] == target].sort_values('date')
    
    if fruit_df.empty:
        # 讓程式直接報錯，FastMCP 會捕捉並回傳錯誤訊息給 AI
        raise ValueError(f"找不到 {target} 的資料")

    # --- 繪圖 ---
    plt.figure(figsize=(10, 5))
    plt.plot(fruit_df['date'], fruit_df['price'], marker='o', color='purple')
    plt.title(f"{target} Price Trend")
    plt.tight_layout()

    # 2. 存入記憶體 (避開 Read-only 錯誤)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

    # 3. 官方終極解法：傳入 bytes 資料與 format
    # FastMCP 會負責把 bytes 轉成 Base64，並正確貼上 mimeType 標籤！
    return Image(data=buf.getvalue(), format="png")



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