# Hubitat MCP Server

A FastMCP server that connects to your [Hubitat Elevation](https://hubitat.com/) local home automation hub using its Maker API. This allows LLM agents and MCP-compatible applications to inspect and control devices on your Hubitat network.

## Capabilities

The server provides the following tools:

*   **List the Hubitat Devices:** Returns a summary of devices available via the Maker API.
*   **Check Specific Device Details:** Returns the current state, labels, and attributes of a single device.
*   **Check Event History for a Specific Device:** Retrieves recent events for a device (e.g., switches turning on/off, temperature updates).
*   **Get Capabilities for a Specific Device:** Returns exactly what attributes and commands a device supports.
*   **Check Commands for a Specific Device:** Shows commands that can be executed against a device.
*   **Command the Hubitat Devices:** Allows you to trigger actions on devices, e.g., turning a switch on/off, setting a dimmer level, or setting lock codes.

## Requirements

1.  A Hubitat Elevation hub accessible over your local network.
2.  The [Maker API built-in app](https://docs2.hubitat.com/en/apps/maker-api) installed and configured on your Hubitat.
3.  The IP address of your Hubitat hub and the Maker API Access Token.

## Configuration

The server requires two high-level environment variables to communicate with your hub. For ease of development, you can manage these in a `.env` file.

1.  Copy `.env.example` to `.env`.
2.  Fill in your specific details:

*   `HOST`: The base URL pointing to the Maker API app (e.g., `http://192.168.1.50/apps/api/33`).
*   `ACCESS_TOKEN`: Your Maker API access token.
*   `MCP_HOST`: (Optional) Host to bind for HTTP/SSE (default: `0.0.0.0`).
*   `MCP_PORT`: (Optional) Port to bind for HTTP/SSE (default: `8888`).

> **Note:** The `HOST` should only contain the base URL path up to the App ID; do *not* include the `?access_token=...` parameter in this variable.

## Docker Usage

The recommended way to use this server is via Docker.

### Building the Image

Clone the repository and build the container locally:

```bash
docker build -t your-dockerhub-username/hubitat-mcp:latest .
```

*Optionally, push it to your registry:*
```bash
docker push your-dockerhub-username/hubitat-mcp:latest
```

### Running testing locally

You can run the server directly via Docker, streaming over STDIO.
Note: Because it communicates with a local network device (Hubitat), ensure the Docker container has network access to the hub's IP.

```bash
docker.exe run -i --rm \
    -e HOST="http://YOUR_HUBITAT_IP/apps/api/YOUR_APP_ID" \
    -e ACCESS_TOKEN="YOUR_MAKER_API_TOKEN" \
    hubitat-mcp-docker:0.0.1
```

### Using the MCP Inspector (Development)

For development on Windows, it is often easier to use the **SSE (HTTP)** transport to avoid console/TTY issues.

1. Start the server via Docker Compose:
   ```bash
   docker compose up -d
   ```
2. Run the inspector pointing to the local HTTP endpoint:
   ```bash
   npx @modelcontextprotocol/inspector http://localhost:8888/mcp
   ```

## Adding to an MCP Client

Clients like [Agentic IDEs](https://modelcontextprotocol.io/) or chat applications look for an `mcp.json` or comparable configuration to connect to tools.

Use the `command` and `args` to directly execute the Docker container when the client starts.

### Example `mcp.json` (Recommended)

This configuration enables the client to start the container automatically via `stdio` while also exposing port `8888` so you can use the **MCP Inspector** or other tools simultaneously.

> **Note:** On Windows, use `docker.exe` to avoid shell/TTY issues.

```json
{
 "mcpServers": {
    "hubitat": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "HOST=http://192.168.86.28/apps/api/43/",
        "-e",
        "ACCESS_TOKEN=47e363b2-5c89-4efc-9533-d65f805c6088",
        "coatsnmore/hubitat-mcp:0.0.1"
      ],
      "trust": true
    }
  }
}
```

### Alternative: Persistent Server (Docker Compose)

If you prefer to keep the server running in the background and connect via HTTP/SSE:

1. Start the server: `docker compose up -d`
2. Use this `mcp.json` (requires client support for URL transport):
```json
{
  "mcpServers": {
    "hubitat": {
      "url": "http://localhost:8888/mcp"
    }
  }
}
```

### Windows Shell Notes (Git Bash / Mintty)

If you are using **Git Bash** or **Mintty**, the standard `docker` command is often an alias that injects `winpty`. This will corrupt the MCP protocol.

*   **Always use `docker.exe`** in your configuration to bypass shell aliases.
*   **Do NOT use the `-t` or `-it` flags**; MCP requires a raw pipe, not a pseudo-TTY.

## Local Development

Written in Python and packaged using `uv`.

```bash
# Clone the repo
git clone https://github.com/coatsnmore/hubitat-mcp.git
cd hubitat-mcp

# Setup environment variables
cp .env.example .env
# Edit .env to contain your HUBITAT_HOST and HUBITAT_TOKEN

# Run directly via uv
uv run hubitat-mcp
```
