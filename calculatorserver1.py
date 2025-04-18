import pandas as pd
import math
import re
from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Step 1: Create the MCP server
mcp = FastMCP("CalculatorApp")

# Step 2: Load the Excel file (members_data.xlsx)
try:
    df_members = pd.read_excel("members_data.xlsx")
    print("Excel file loaded successfully.", flush=True)
except Exception as e:
    print("Warning: Excel file not loaded.", flush=True)
    df_members = None

# Step 3: Define the Calculator Tool
@mcp.tool(
    name="calculator",
    description="""
    Enhanced Calculator Tool.

    Supports:
    - Basic arithmetic (+, -, *, /)
    - Scientific calculations (sin, cos, log, sqrt, etc.)
    - Business data queries (example: "Count members over age 60" from Excel data)

    Args:
        expression (str): User input containing a math expression or business query
    """
)
def calculate(expression: str) -> str:
    """
    Evaluates basic math, scientific expressions, or business data queries.
    """
    print(f"calculate() called with expression: {expression}", flush=True)

    try:
        expr = expression.lower().strip()

        # Handle Business Data Queries
        if "members" in expr:
            if df_members is None:
                return "Error: Data file not loaded for business queries."

            if "over age" in expr:
                age_match = re.search(r"over age (\d+)", expr)
                if age_match:
                    age_limit = int(age_match.group(1))
                    count = df_members[df_members["Age"] > age_limit].shape[0]
                    return f"Members over age {age_limit}: {count}"
                else:
                    return "Could not extract age information from your query."

        # Handle Scientific Calculations
        allowed_funcs = ["sin", "cos", "tan", "sqrt", "log", "exp", "pow"]
        for func in allowed_funcs:
            expr = expr.replace(func, f"math.{func}")

        allowed_chars = "0123456789+-*/(). math"

        if any(c not in allowed_chars for c in expr.replace(" ", "")):
            return "Invalid characters found in expression."

        result = eval(expr)
        return f"Result: {result}"

    except Exception as e:
        print("Error:", str(e), flush=True)
        return f"Error: {str(e)}"

# Step 4: Add the lifespan (startup/shutdown) handler
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """
    Manage application lifecycle events: startup and shutdown.
    """
    print("Starting CalculatorApp...", flush=True)
    yield
    print("Shutting down CalculatorApp...", flush=True)

# Step 5: Attach the lifespan to MCP
mcp.lifespan(app_lifespan)

# Step 6: Run the MCP server
if __name__ == "__main__":
    mcp.run()
