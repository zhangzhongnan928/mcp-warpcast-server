#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import warpcastApi, { Cast } from "./warpcast-api.js";

// Create an MCP server instance
const server = new McpServer({
  name: "warpcast",
  version: "1.0.0",
});

// Utility function to format a cast as readable text
function formatCast(cast: Cast): string {
  const date = new Date(cast.timestamp).toLocaleString();
  return `
@${cast.author.username} (${cast.author.displayName}) - ${date}
${cast.text}

❤️ ${cast.reactions.likes} · 🔄 ${cast.reactions.recasts} · 💬 ${cast.reactions.replies}
Cast ID: ${cast.hash}
---
`;
}

// Tool: Post a new cast
server.tool(
  "post-cast",
  {
    text: z.string().max(320).describe("The content of your cast (max 320 characters)"),
  },
  async ({ text }) => {
    try {
      const cast = await warpcastApi.postCast(text);
      return {
        content: [
          {
            type: "text",
            text: `✅ Cast posted successfully!\n\n${formatCast(cast)}`,
          },
        ],
      };
    } catch (error) {
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Error posting cast: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  }
);

// Tool: Get casts from a specific user
server.tool(
  "get-user-casts",
  {
    username: z.string().describe("Warpcast username without the @ symbol"),
    limit: z.number().min(1).max(20).default(5).describe("Number of casts to retrieve (max 20)"),
  },
  async ({ username, limit }) => {
    try {
      const casts = await warpcastApi.getUserCasts(username, limit);
      
      if (casts.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `No casts found for user @${username}`,
            },
          ],
        };
      }

      const formattedCasts = casts.map(formatCast).join("\n");
      return {
        content: [
          {
            type: "text",
            text: `Latest casts from @${username}:\n\n${formattedCasts}`,
          },
        ],
      };
    } catch (error) {
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Error fetching casts for @${username}: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  }
);

// Tool: Search for casts
server.tool(
  "search-casts",
  {
    query: z.string().describe("Search query"),
    limit: z.number().min(1).max(20).default(5).describe("Number of results to retrieve (max 20)"),
  },
  async ({ query, limit }) => {
    try {
      const casts = await warpcastApi.searchCasts(query, limit);
      
      if (casts.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `No casts found for query "${query}"`,
            },
          ],
        };
      }

      const formattedCasts = casts.map(formatCast).join("\n");
      return {
        content: [
          {
            type: "text",
            text: `Search results for "${query}":\n\n${formattedCasts}`,
          },
        ],
      };
    } catch (error) {
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Error searching for casts: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  }
);

// Tool: Get trending casts
server.tool(
  "get-trending-casts",
  {
    limit: z.number().min(1).max(20).default(5).describe("Number of trending casts to retrieve (max 20)"),
  },
  async ({ limit }) => {
    try {
      const casts = await warpcastApi.getTrendingCasts(limit);
      
      if (casts.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: "No trending casts found",
            },
          ],
        };
      }

      const formattedCasts = casts.map(formatCast).join("\n");
      return {
        content: [
          {
            type: "text",
            text: `Trending casts on Warpcast:\n\n${formattedCasts}`,
          },
        ],
      };
    } catch (error) {
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Error fetching trending casts: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  }
);

// Start the server with stdio transport
async function main() {
  try {
    // Check for API credentials
    if (!process.env.WARPCAST_API_KEY || !process.env.WARPCAST_API_SECRET) {
      console.error("Error: Missing Warpcast API credentials!");
      console.error("Please set WARPCAST_API_KEY and WARPCAST_API_SECRET environment variables.");
      process.exit(1);
    }

    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Warpcast MCP Server is running...");
  } catch (error) {
    console.error("Error starting MCP server:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});