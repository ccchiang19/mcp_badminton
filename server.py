import os
import matplotlib.pyplot as plt
from fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("DataAnalyzerGrapher")

# ---------------------------------------------------------
# 1. RESOURCE: How the AI reads your local file
# ---------------------------------------------------------
# 抓取這支 Python 檔案所在的資料夾路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@mcp.resource("file:///{filename}")
def read_local_file(filename: str) -> str:
    # 將資料夾路徑與檔名結合，變成絕對路徑
    file_path = os.path.join(BASE_DIR, filename)
    
    if not os.path.exists(file_path):
        return f"錯誤：找不到檔案！程式嘗試讀取的路徑是：{file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# ---------------------------------------------------------
# 2. TOOL: How the AI takes action (creating the graph)
# ---------------------------------------------------------
@mcp.tool()
def create_and_save_graph(categories: list[str], values: list[float], output_filename: str) -> str:
    """
    Takes analyzed data categories and values, generates a bar chart, 
    and saves it locally as a PNG file.
    """
    plt.figure(figsize=(8, 5))
    plt.bar(categories, values, color='skyblue')
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title('Automated Data Analysis')
    
    # Save the graph to the local hard drive
    plt.savefig(output_filename)
    plt.close()
    
    return f"Success! I have generated the graph and saved it as '{output_filename}' in your folder."

# ---------------------------------------------------------
# 3. PROMPT: How to tell the AI to connect step 1 and step 2
# ---------------------------------------------------------
@mcp.prompt("analyze-and-graph")
def analyze_data_prompt(filename: str) -> str:
    """The workflow instructions for the AI."""
    return (
        f"I need you to act as a data analyst. Please follow these steps:\n"
        f"1. Use the resource 'file://{filename}' to read the raw data.\n"
        f"2. Analyze the text to extract the categories and their corresponding numerical values.\n"
        f"3. Use the 'create_and_save_graph' tool to plot this data. Name the output file 'analyzed_graph.png'.\n"
        f"4. Give me a brief text summary of the trends you see in the data."
    )

if __name__ == "__main__":
    # mcp.run()
    mcp.run_run(transport="http",port=8000)