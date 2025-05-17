# Warpcast MCP Server

A Model Context Protocol (MCP) server for Warpcast integration that allows you to use Claude to interact with your Warpcast account.

## Features

- Post casts to your Warpcast account
- Read casts from Warpcast
- Search casts by keyword or hashtag
- Browse and interact with channels
- Follow/unfollow channels
- Get trending casts

Warpcast API 
https://docs.farcaster.xyz/reference/warpcast/api

## Usage

Once configured, you can ask Claude to:

- "Post a cast about [topic]"
- "Read the latest casts from [username]"
- "Search for casts about [topic]"
- "Show me trending casts on Warpcast"
- "Show me popular channels on Warpcast"
- "Get casts from the [channel] channel"
- "Follow the [channel] channel for me"

## Available Tools

This MCP server provides several tools that Claude can use:

1. **post-cast**: Create a new post on Warpcast (max 320 characters)
2. **get-user-casts**: Retrieve recent casts from a specific user
3. **search-casts**: Search for casts by keyword or phrase
4. **get-trending-casts**: Get the currently trending casts on Warpcast
5. **get-all-channels**: List available channels on Warpcast
6. **get-channel**: Get information about a specific channel
7. **get-channel-casts**: Get casts from a specific channel
8. **follow-channel**: Follow a channel
9. **unfollow-channel**: Unfollow a channel


## Setup

1. Create a Python virtual environment (Python 3.11 or newer is recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Obtain a Warpcast API token and export it as an environment variable:
   - Log in to [Warpcast](https://warpcast.com/) and open **Settings \> Developer**.
   - Click **Create API Token** and copy the value.
   - Set `WARPCAST_API_TOKEN` in your shell:
     ```bash
     export WARPCAST_API_TOKEN=YOUR_TOKEN
     ```
   The server validates this variable on startup. If it is missing, a warning
   is logged and authorized requests will respond with **HTTP 500** errors.
   You can either set the `WARPCAST_API_TOKEN` environment variable or supply it
   in the `env` section of Claude's configuration (see below).
   
4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

The server exposes HTTP endpoints matching the tools listed above.

### MCP Endpoint

An additional `/mcp` route implements the [Model Context Protocol](https://modelcontextprotocol.io/). To use it:

1. Start the server as usual:
   ```bash
   uvicorn main:app --reload
   ```
2. Open a Server-Sent Events connection to `http://localhost:8000/mcp`.
3. POST JSON-RPC messages (such as the `initialize` request) to the same path.

After initialization clients can discover the Warpcast tools using the `tools/list` method.

## Using with Claude Desktop

Follow these steps to access the Warpcast tools from Claude's desktop application:

1. Start the server (or let Claude launch it) using the setup instructions above.
2. Open your Claude configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
3. Add the Warpcast server under the `mcpServers` key. Replace the path with the location of this repository:

```json
{
  "mcpServers": {
    "warpcast": {
      "command": "uvicorn",
      "args": [
        "--app-dir",
        "/ABSOLUTE/PATH/TO/mcp-warpcast-server",
        "main:app",
        "--port",
        "8000"
      ],
      "env": {
        "WARPCAST_API_TOKEN": "YOUR_API_TOKEN"
      }
    }
  }
}
```

4. Save the file and restart Claude Desktop. You should now see a hammer icon in the chat input that lets you use the Warpcast tools.

## Running Tests

Unit tests are written with `pytest` and use FastAPI's `TestClient` (installed via `fastapi[testclient]`).
Create a virtual environment, install dependencies and run the suite:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make test        # or simply `pytest`
```

The tests mock the Warpcast API layer so no network connection is required.


## MCP Compatibility

This server is compatible with the [Model Context Protocol](https://modelcontextprotocol.org/).
After opening a Server-Sent Events connection to `/mcp`, send an `initialize`
JSON-RPC message. The response on the event stream includes
`{"protocolVersion": "2024-11-05"}` which confirms compatibility.

### Initialization example

In one terminal start listening for events:

```bash
curl -N http://localhost:8000/mcp
```

In another terminal send the `initialize` message:

```bash
curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize"}'
```

The server responds on the first terminal with the protocol version.

After initialization you can call tool endpoints, for example to post a cast:

```bash
curl -X POST http://localhost:8000/post-cast \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello from curl"}'
```
## License

This project is licensed under the [MIT License](LICENSE).
