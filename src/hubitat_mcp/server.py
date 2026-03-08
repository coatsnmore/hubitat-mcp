import os
import json
import logging
import asyncio
import sys
import threading
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("hubitat-mcp")

load_dotenv()

# Create an MCP server
mcp = FastMCP("Hubitat MCP Server")

HUBITAT_BASE_URL = os.getenv("HOST")
HUBITAT_TOKEN = os.getenv("ACCESS_TOKEN")

@mcp.tool(description="List the Hubitat Devices")
def list_devices():
    """Return a list of devices from Hubitat Maker API and log them nicely."""
    url = f"{HUBITAT_BASE_URL}/devices?access_token={HUBITAT_TOKEN}"
    r = requests.get(url)
    devices = r.json()

    logger.info("Listing Hubitat Devices")
    for d in devices:
        name = d.get("label") or d.get("name", "Unknown")
        device_id = d.get("id", "?")
        device_type = d.get("type", "?")
        logger.debug(f"- {name} (ID: {device_id}, Type: {device_type})")

    return json.dumps(devices)

@mcp.tool(description="Check Specific Device Details")
def device_details(device_id):
    """Return the details for a specific device"""
    url = f"{HUBITAT_BASE_URL}/devices/{device_id}?access_token={HUBITAT_TOKEN}"
    r = requests.get(url)
    device_details = r.json()

    logger.info(f"Fetching details for device '{device_id}'")

    return json.dumps(device_details)

@mcp.tool(description="Check Event History for a Specific Device")
def device_history(device_id):
    """Return the event history for a specific device"""
    url = f"{HUBITAT_BASE_URL}/devices/{device_id}/events?access_token={HUBITAT_TOKEN}"
    r = requests.get(url)
    events = r.json()

    logger.info(f"Fetching history for device '{device_id}'")

    return json.dumps(events)

@mcp.tool(description="Get Capabilities for a Specific Device")
def device_capabilities(device_id):
    """Return a the capabilities for a specific device"""
    url = f"{HUBITAT_BASE_URL}/devices/{device_id}/capabilities?access_token={HUBITAT_TOKEN}"
    r = requests.get(url)
    capabilities = r.json()

    logger.info(f"Fetching capabilities for device '{device_id}'")

    return json.dumps(capabilities)

@mcp.tool(description="Check Commands for a Specific Device")
def device_commands(device_id):
    """Return a the commands for a specific device"""
    url = f"{HUBITAT_BASE_URL}/devices/{device_id}/commands?access_token={HUBITAT_TOKEN}"
    r = requests.get(url)
    commands = r.json()

    logger.info(f"Fetching commands for device '{device_id}'")

    return json.dumps(commands)

@mcp.tool(description="Command the Hubitat Devices")
def control_device(device_id, command):
    """Send a command to a Hubitat device.
    Example: To turn on a light device ID 1

    /devices/1/on

    Example 2: To set the level that light to 50%

    /devices/1/setLevel/50

    Example 3: Sets a lock code for at position 3 with code 4321 and name "Guest":

    /devices/1321/setCode/3,4321,Guest
    """
    url = f"{HUBITAT_BASE_URL}/devices/{device_id}/{command}?access_token={HUBITAT_TOKEN}"
    r = requests.get(url)
    status = "ok" if r.status_code == 200 else "error"
    logger.info(f"Command '{command}' sent to device ID {device_id} - Status: {status}")
    return json.dumps({"status": status}, indent=2)

async def async_main():
    """Async main entry point for the hubitat MCP server."""
    port_env = os.getenv("MCP_PORT")
    port = int(port_env) if port_env else 8888
    tasks = []

    if "--http" in sys.argv or port_env:
        # If explicitly requested or port is defined, we can run HTTP
        host = os.getenv("MCP_HOST", "0.0.0.0")
        logger.info(f"Starting Hubitat MCP HTTP server on {host}:{port}")
        
        # Add HTTP server task
        tasks.append(mcp.run_http_async(transport="streamable-http", host=host, port=port))
        
        if "--http-only" in sys.argv:
            # Only run the HTTP server
            await tasks[0]
            return

    # Always add stdio to the tasks
    logger.info("Starting Hubitat MCP server on stdio")
    tasks.append(mcp.run_stdio_async())

    # Run both concurrently
    await asyncio.gather(*tasks)

def main():
    """Main entry point for the hubitat MCP server."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")

if __name__ == "__main__":
    main()
