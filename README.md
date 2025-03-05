# Warpcast MCP Server

A Model Context Protocol (MCP) server for Warpcast integration.

## Features

- Post casts to your Warpcast account
- Read casts from Warpcast
- Search casts by username or hashtag

## Setup

1. Clone this repository
2. Install dependencies: `npm install`
3. Copy `.env.example` to `.env` and add your Warpcast API credentials
4. Build the server: `npm run build`
5. Configure Claude for Desktop to use this server

## Configuration with Claude for Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "warpcast": {
      "command": "node",
      "args": [
        "path/to/mcp-warpcast-server/build/index.js"
      ],
      "env": {
        "WARPCAST_API_KEY": "your_api_key_here",
        "WARPCAST_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

Replace `path/to/mcp-warpcast-server` with the absolute path to where you cloned this repository.

## Usage

Once configured, you can ask Claude to:

- "Post a cast about [topic]"
- "Read the latest casts from [username]"
- "Search for casts about [topic]"

## License

MIT