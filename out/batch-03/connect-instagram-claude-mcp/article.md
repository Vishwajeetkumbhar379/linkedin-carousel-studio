# Connect Instagram to Claude using MCP: automate captions, scheduling and replies

## Connect Instagram to Claude using MCP

The Model Context Protocol (MCP) lets AI apps like Claude talk directly to external services such as Instagram without handling OAuth or API keys yourself. Two guides published in early October 2026 show how to add an MCP endpoint to Claude and then use natural language to work with your Instagram account.

## How to connect

### Via PorterMetrics
Copy the URL mcp.portermetrics.com/mcp. In Claude.ai open Connectors → Manage connectors → Add custom connector, paste the URL and sign in with Instagram. The setup takes under five minutes.

### Via Composio
Add the Composio MCP to Claude Terminal, generate the MCP URL, start Claude Code bash, open the MCP list, select Composio and click Authenticate. Complete the OAuth flow to finish.

## What you can automate

Once linked, Claude can:
- Draft and publish single-photo, video or carousel posts to your feed.
- Request insights on recent posts, fetch comments and manage conversations.
- Build dashboards, trigger alerts or ship client-ready reports based on your Instagram data.
- Access more than 1,500 other managed integrations (e.g. Google Ads, Sheets) through the same MCP connection.

## What I'd do

I have already used MCP connectors for Google Ads and Sheets, so the workflow feels familiar. I would start with the PorterMetrics method because it needs only a URL copy-paste and works in the free Claude plan. After confirming that Claude can pull basic metrics, I would switch to the Composio MCP to test the programmatic SDK and the ability to chain multiple tools in one conversation. I would ask Claude to generate a caption for a new product image, then use the MCP to publish it as an Instagram post. Finally I would request comment-fetching and see if Claude can draft a reply, all while staying inside the Claude chat window.

## Sources
- Composio: https://composio.dev/toolkits/instagram/framework/claude-code (2026-10-07)
- PorterMetrics: https://portermetrics.com/en/tutorial/claude/chat-instagram/ (2026-10-07)
