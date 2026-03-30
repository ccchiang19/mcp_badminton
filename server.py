from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool
def score_evaluation(score: int) -> str:
    if score > 60:
        return f"Good jobbbbbbbbb"
    return f"BAddddddddd!"

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)