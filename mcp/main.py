from fastmcp import FastMCP
import httpx
import os
import json
import asyncio
from starlette.responses import StreamingResponse

# Initialize FastMCP
mcp = FastMCP("My API MCP Wrapper")

# Configuration - set via environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# HTTP client for calling the existing API
http_client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=API_TIMEOUT)


@mcp.tool()
async def get_latest_weather_report() -> dict:
    """
    Retrieves the latest weather report from the weather API.
    
    Returns:
        The latest weather report data.
    """
    try:
        response = await http_client.get("/weather/latest")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"API error: {e.response.status_code} - {e.response.text}", "status_code": e.response.status_code})
    except httpx.RequestError as e:
        return json.dumps({"error": f"Network error: {e}", "status_code": None})

@mcp.tool()
async def get_weather_report_by_date(date_str: str) -> dict:
    """
    Retrieves a weather report for a specific date from the weather API.
    
    Args:
        date_str: The date in YYYY-MM-DD format, or keywords like "today", "tomorrow", "yesterday".
        
    Returns:
        The weather report data for the specified date.
    """
    try:
        response = await http_client.get(f"/weather/{date_str}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"API error: {e.response.status_code} - {e.response.text}", "status_code": e.response.status_code})
    except httpx.RequestError as e:
        return json.dumps({"error": f"Network error: {e}", "status_code": None})

@mcp.tool()
async def get_attempt_logs() -> list:
    """
    Retrieves a list of all data fetching attempt logs from the weather API.
    
    Returns:
        A list of attempt log entries.
    """
    try:
        response = await http_client.get("/logs")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"API error: {e.response.status_code} - {e.response.text}", "status_code": e.response.status_code})
    except httpx.RequestError as e:
        return json.dumps({"error": f"Network error: {e}", "status_code": None})


async def log_event_generator():
    """
    An asynchronous generator that fetches logs from the API and yields them as SSE-formatted strings.
    """
    while True:
        try:
            logs_json = await get_attempt_logs()
            # Assuming logs_json is a list of dictionaries, convert each to a JSON string
            if isinstance(logs_json, list):
                for log_entry in logs_json:
                    yield f"data: {json.dumps(log_entry)}\n\n"
            else:
                # If get_attempt_logs returns an error string, send it as an SSE message
                yield f"data: {logs_json}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        await asyncio.sleep(5)  # Fetch logs every 5 seconds

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)



