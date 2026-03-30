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
def plot_from_json(data_list: List[dict], fruit_name: str) -> Image:
    # 1. 繪圖邏輯 (保持不變，不寫入硬碟)
    df = pd.DataFrame(data_list)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'])
    
    target = fruit_name.strip().capitalize()
    fruit_df = df[df['item'] == target].sort_values('date')
    
    if fruit_df.empty:
        # 如果失敗，回傳一個明確的錯誤 (FastMCP 會處理字串)
        return f"Error: No data for {target}"

    plt.figure(figsize=(10, 5))
    plt.plot(fruit_df['date'], fruit_df['price'], marker='o', color='#2ca02c')
    plt.title(f"{target} Price Trend")
    plt.tight_layout()

    # 2. 將圖片存入記憶體
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # 3. 核心修正：直接回傳 Image 物件，並將二進位資料丟進去
    # 不要自己做 base64.encode，讓 Image 類別幫你做
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