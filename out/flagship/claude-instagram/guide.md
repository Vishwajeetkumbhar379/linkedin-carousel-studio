# Connect Instagram to Claude: the full setup (for everyone who commented INSTA)

Instagram is not in Claude's connector directory. Two third-party connectors fill the gap, both on Meta's official API.

## Route 1: read your Instagram data in Claude (Porter, no code)
1. Create a free Porter account at portermetrics.com. In Porter: Create → pick Claude as the destination → Instagram as the source → sign in with Instagram (Business profile).
2. Open claude.ai, click **+** in the chat box, hover **Connectors**, click **Manage connectors**.
3. Click **+** at the top of the list → **Add custom connector**.
4. Name: `Porter`. Remote MCP server URL: `https://mcp.portermetrics.com/mcp`. Click **Add**, then sign in with the Google account linked to Porter.
5. Ask your first question:
   - "What were my top 10 Instagram posts by engagement rate last month?"
   - "Show me my Reels plays vs Stories reach trend this quarter."
   - "Which post type gets the most saves: images, videos or carousels?"

Porter's tools are read-only. 14-day unlimited free trial, then free for up to 3 pages and 30 days of history, no card. Free Claude plans allow one custom connector.

## Route 2: let Claude publish and handle comments (Composio)
Composio's Instagram toolkit connects Claude Code to an Instagram Business or Creator account. It can publish single-photo, video and carousel posts, fetch comments, pull insights and read DM conversations.
1. In Composio, generate your MCP URL and add it to Claude Code.
2. Run `claude`, then `/mcp`, select Composio, click **Authenticate** and finish the OAuth flow.
Requires Claude Pro or Max (or API billing) and a Composio API key.

## What I'd do first
Start with Route 1 for a week. Let Claude read the numbers and tell you which formats earn saves. Only then give it posting rights.

Sources: portermetrics.com/en/tutorial/claude/chat-instagram · composio.dev/toolkits/instagram/framework/claude-code · support.claude.com (custom connectors). Read 7 Oct 2026.
