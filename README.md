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
*   `MCP_HOST`: (Optional) Host to bind for HTTP (default: `0.0.0.0`).
*   `MCP_PORT`: (Optional) Port to bind for HTTP (default: `8888`).

> **Note:** The `HOST` should only contain the base URL path up to the App ID; do *not* include the `?access_token=...` parameter in this variable.

## Transport Modes

Hubitat MCP operates in one of two transport modes:

1. **STDIO Mode (Default)**:
   - Active by default when running without `--http-only`.
   - Communicates over standard input and standard output (`stdio`).
   - Ideal for local desktop MCP clients (such as Claude Desktop, Cursor, OpenCode, Antigravity) that manage and run the server process directly.

2. **Streamable HTTP Mode (`--http-only`)**:
   - Activated by passing the `--http-only` command-line argument.
   - Starts an HTTP server on `MCP_HOST:MCP_PORT` (default: `0.0.0.0:8888`) exposing the `/mcp` endpoint using FastMCP's **Streamable HTTP** transport.
   - Ideal for running as a persistent background service (e.g., via Docker Compose) or for inspecting and testing tools with the MCP Inspector.
   - *Note: Legacy SSE is not used; Streamable HTTP is the modern transport protocol.*

## Docker Usage

The recommended way to use this server is via Docker.

### Building the Image

Clone the repository and build the container locally:

```bash
docker build -t coatsnmore/hubitat-mcp:0.0.3 .
```

*Optionally, push it to your registry:*
```bash
docker push coatsnmore/hubitat-mcp:0.0.3
```

### Running in STDIO Mode (Default)

Run the container interactively with `-i` (and **no** `-t` flag):

```bash
docker run -i --rm \
    -e HOST="http://YOUR_HUBITAT_IP/apps/api/YOUR_APP_ID" \
    -e ACCESS_TOKEN="YOUR_MAKER_API_TOKEN" \
    coatsnmore/hubitat-mcp:0.0.3
```
> **Note:** Ensure the Docker container has network access to your Hubitat hub IP. On Windows (Git Bash / Mintty), use `docker.exe` to avoid TTY issues.

### Running in Streamable HTTP Mode (`--http-only`)

To run the server in Streamable HTTP mode in the background, pass `--http-only` and publish the port:

```bash
docker run -d --rm \
    -p 8888:8888 \
    -e HOST="http://YOUR_HUBITAT_IP/apps/api/YOUR_APP_ID" \
    -e ACCESS_TOKEN="YOUR_MAKER_API_TOKEN" \
    coatsnmore/hubitat-mcp:0.0.3 --http-only
```

#### Using Docker Compose

Alternatively, use `docker compose` which is preconfigured to run with `--http-only`:

```bash
docker compose up -d
```

### Using the MCP Inspector (Development)

When running in HTTP mode, you can inspect and debug tools using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector http://localhost:8888/mcp
```
*(Note: If using `docker-compose.yml` with host port mapping `8887:8888`, connect to `http://localhost:8887/mcp` instead).*

## Adding to an MCP Client

Clients like [Agentic IDEs](https://modelcontextprotocol.io/) or chat applications connect via an `mcp.json` or client configuration.

### Option 1: STDIO via Docker (Recommended for Desktop Clients)

This configuration enables the client to start the container on demand via `stdio`:

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
        "HOST=http://YOUR_HUBITAT_IP/apps/api/YOUR_APP_ID",
        "-e",
        "ACCESS_TOKEN=YOUR_MAKER_API_TOKEN",
        "coatsnmore/hubitat-mcp:0.0.3"
      ],
      "trust": true
    }
  }
}
```

> **Note for Windows:** Use `"command": "docker.exe"` in your configuration to bypass Git Bash / Mintty shell aliases that inject a pseudo-TTY.

### Option 2: Streamable HTTP via Persistent Server

If you keep the server running in the background (via `docker compose up -d` or `docker run ... --http-only`):

```json
{
  "mcpServers": {
    "hubitat": {
      "url": "http://localhost:8888/mcp"
    }
  }
}
```
*(Note: Requires client support for remote HTTP/Streamable HTTP MCP endpoints).*

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
# Edit .env to contain your HOST and ACCESS_TOKEN

# Run using STDIO (default):
uv run hubitat-mcp

# Run using Streamable HTTP:
uv run hubitat-mcp --http-only
```
