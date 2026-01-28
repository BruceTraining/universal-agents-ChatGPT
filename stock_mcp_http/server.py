#!/usr/bin/env python3
"""
Stock MCP Server - A Model Context Protocol server that provides stock price information.

Uses the official MCP Python SDK (from mcp.server.fastmcp import FastMCP)
following OpenAI's official examples pattern.

Run with UV:
  uv run stock-mcp-http

Connect ChatGPT Developer Mode to:
  http://localhost:8000/mcp
"""

import os
import sys
import traceback
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from twelvedata import TDClient

from .stock_formatter import format_data


def log(message: str):
    """Log message to stderr to avoid interfering with transport."""
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()


# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("TWELVE_DATA_API_KEY")
if not api_key:
    raise ValueError("TWELVE_DATA_API_KEY environment variable is required")

# Initialize the TwelveData client
twelve_data_client = TDClient(apikey=api_key)

# Port configuration
PORT = int(os.environ.get("PORT", "8000"))

# Create the FastMCP server instance
# stateless_http=True is required for ChatGPT Apps SDK
mcp = FastMCP(
    name="stock-mcp",
    stateless_http=True,
    host="0.0.0.0",
    port=PORT,
)


# ==========================================
# INTERNAL/SHARED FUNCTIONS
# ==========================================


def _fetch_current_stock_price(symbol: str) -> str:
    """
    Internal function to fetch current stock price with change information.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Formatted string with current price and change data
    """
    log(f"Fetching current price for {symbol}")

    try:
        quote_data = twelve_data_client.quote(symbol=symbol.upper()).as_json()
        return format_data(quote_data, symbol.upper())

    except Exception as e:
        error_msg = f"Error fetching stock data for {symbol}: {str(e)}"
        log(error_msg)
        log(traceback.format_exc())
        return f"Error: {error_msg}"


def _fetch_historical_stock_price(symbol: str, date: str) -> str:
    """
    Internal function to fetch historical closing price for a specific date.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        date: Date in YYYY-MM-DD format

    Returns:
        Formatted string with historical closing price data
    """
    log(f"Fetching EOD data for {symbol} on {date}")

    # Validate date format
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        if date_obj.weekday() >= 5:
            return f"Warning: {date} is a weekend. Stock markets are typically closed. Try a weekday date."
    except ValueError:
        return f"Error: Invalid date format '{date}'. Use YYYY-MM-DD"

    try:
        eod_data = twelve_data_client.eod(symbol=symbol.upper(), date=date).as_json()

        if not eod_data:
            return f"Error: No EOD data returned for {symbol} on {date}"

        if "status" in eod_data and eod_data["status"] == "error":
            error_msg = eod_data.get("message", "Unknown API error")
            return f"API Error: {error_msg}"

        if "code" in eod_data and eod_data["code"] == 400:
            error_msg = eod_data.get("message", "No data available for this date")
            return f"No data available: {error_msg}"

        if "close" not in eod_data or eod_data["close"] is None:
            return f"No closing price data available for {symbol} on {date}. Markets may have been closed."

        return format_data(eod_data, symbol.upper(), date)

    except Exception as e:
        error_msg = f"Error fetching EOD data for {symbol} on {date}: {str(e)}"
        log(error_msg)
        log(traceback.format_exc())
        return f"Error: {error_msg}"


# ==========================================
# MCP TOOLS
# ==========================================


@mcp.tool(
    name="get_current_stock_price",
    description="Get current stock price with change information for any stock symbol.",
)
def get_current_stock_price(symbol: str) -> str:
    """
    Get current stock price with change information.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Formatted string with current price, change, and market data
    """
    symbol = symbol.strip()
    log(f"Tool call: get_current_stock_price for {symbol}")
    return _fetch_current_stock_price(symbol)


@mcp.tool(
    name="get_historical_stock_price",
    description="Get historical closing price for a stock on a specific date.",
)
def get_historical_stock_price(symbol: str, date: str) -> str:
    """
    Get historical closing price for a specific date.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        date: Date in YYYY-MM-DD format (e.g., '2024-01-15')

    Returns:
        Formatted string with historical price data (open, close, high, low, volume)
    """
    symbol = symbol.strip()
    log(f"Tool call: get_historical_stock_price for {symbol} on {date}")
    return _fetch_historical_stock_price(symbol, date)


# ==========================================
# MCP RESOURCES
# ==========================================


@mcp.resource(
    uri="stock://{symbol}",
    name="current-stock-price",
    description="Get current stock price for a symbol",
)
def get_stock_price(symbol: str) -> str:
    """Get current stock price with change information."""
    log(f"Resource call: stock://{symbol}")
    return _fetch_current_stock_price(symbol)


@mcp.resource(
    uri="stock://{symbol}/closingdate/{date}",
    name="historical-stock-price",
    description="Get historical closing price for a symbol on a specific date",
)
def get_stock_closing_price(symbol: str, date: str) -> str:
    """Get historical closing price for a specific date."""
    log(f"Resource call: stock://{symbol}/closingdate/{date}")
    return _fetch_historical_stock_price(symbol, date)



# ==========================================
# MCP PROMPTS 
# ==========================================

@mcp.prompt("stock_current_price")
def stock_current_price_prompt(symbol: str) -> str:
    """
    Prompt for getting current stock price information.
    
    This prompt helps MCP clients understand how to request current stock data
    for any publicly traded stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
    
    Returns:
        Instructions for accessing current stock price data
    """
    return f"""
To get current stock price information for {symbol.upper()}:

Use the resource: stock://{symbol.upper()}/
Or use the tool: get_current_stock_price with symbol parameter

This will provide you with:
- Current stock price
- Price change from previous close
- Percentage change
- Day's high and low prices
- Trading volume
- Exchange information

Example usage:
- For Apple stock: stock://AAPL/ or get_current_stock_price(symbol="AAPL")
- For Microsoft stock: stock://MSFT/ or get_current_stock_price(symbol="MSFT")
- For Google stock: stock://GOOGL/ or get_current_stock_price(symbol="GOOGL")

The data is fetched in real-time from the Twelve Data API and includes
comprehensive market information with change indicators.
"""


@mcp.prompt("stock_historical_price")
def stock_historical_price_prompt(symbol: str, date: str) -> str:
    """
    Prompt for getting historical stock price information for a specific date.
    
    This prompt helps MCP clients understand how to request historical End-of-Day
    stock data for any publicly traded stock symbol on a specific date.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
        date: Date in YYYY-MM-DD format
    
    Returns:
        Instructions for accessing historical stock price data
    """
    return f"""
To get historical End-of-Day (EOD) stock price information for {symbol.upper()} on {date}:

Use the resource: stock://{symbol.upper()}/closingdate/{date}
Or use the tool: get_historical_stock_price with symbol and date parameters

This will provide you with:
- Opening price for the day
- Closing price for the day
- Day's high and low prices
- Trading volume
- Actual date of the data

Example usage:
- For Apple stock on Jan 15, 2024: stock://AAPL/closingdate/2024-01-15 or get_historical_stock_price(symbol="AAPL", date="2024-01-15")
- For Microsoft stock on Dec 31, 2023: stock://MSFT/closingdate/2023-12-31 or get_historical_stock_price(symbol="MSFT", date="2023-12-31")

Important notes:
- Date must be in YYYY-MM-DD format
- Weekend dates will return a warning (markets are typically closed)
- Historical data is sourced from Twelve Data's EOD endpoint
- Data may not be available for very recent dates or market holidays
"""




# ==========================================
# SERVER ENTRY POINT
# ==========================================


def main():
    """Main entry point - starts server with Streamable HTTP transport."""
    log(
        f"""
╔══════════════════════════════════════════════════════════════╗
║           Stock MCP Server (HTTP Streaming)                  ║
╠══════════════════════════════════════════════════════════════╣
║  Endpoint: http://localhost:{PORT}/mcp                         ║
║                                                              ║
║  Tools:                                                      ║
║    - get_current_stock_price(symbol)                         ║
║    - get_historical_stock_price(symbol, date)                ║
║                                                              ║
║  Resources:                                                  ║
║    - stock://{{symbol}}                                        ║
║    - stock://{{symbol}}/closingdate/{{date}}                     ║
║                                                              ║
║  Mode: stateless_http (ChatGPT Apps SDK compatible)          ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    try:
        # Run with streamable-http transport for ChatGPT compatibility
        # Host and port are configured in the FastMCP constructor
        mcp.run(transport="streamable-http")

    except KeyboardInterrupt:
        log("\nServer shutdown requested by user")
    except Exception as e:
        log(f"Failed to start Stock MCP Server: {e}")
        log(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
