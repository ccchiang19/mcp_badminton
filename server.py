from fastmcp import FastMCP
import json
import csv

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool
def price_evaluation(score: int) -> str:
    if score < 50:
        return f"Good jobbbbbbbbb"
    return f"BAddddddddd!"

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


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)