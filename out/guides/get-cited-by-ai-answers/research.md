# Research notes: get-cited-by-ai-answers (checked 2026-10-08)

## Google (AI features and your website) https://developers.google.com/search/docs/appearance/ai-features (page "Last updated 2025-12-10 UTC")
- No additional requirements to appear in AI Overviews or AI Mode, no other special optimisations needed. SEO fundamentals still apply.
- Both AI Overviews and AI Mode may use "query fan-out": multiple related searches across subtopics and data sources. Show wider, more diverse set of links.
- AI Mode and AI Overviews may use different models/techniques, so responses and links vary. AI Overviews only shown when additive to classic Search; often don't trigger.
- Eligibility: page must be indexed and eligible to be shown in Google Search with a snippet. No additional technical requirements. Indexing/serving not guaranteed.
- Best practices listed: crawling allowed in robots.txt and by CDN/hosting; internal links; page experience; important content available as text; high quality images/video; structured data matches visible text; Merchant Center/Business Profile info up to date.
- "You don't need to create new machine readable files, AI text files, or markup"; no special schema.org needed.
- Measurement: sites appearing in AI features are included in overall search traffic in Search Console, in Performance report, "Web" search type. (No separate AI filter stated on this page.)
- Controls: robots.txt for Googlebot is the control; nosnippet, data-nosnippet, max-snippet, noindex limit what is shown. Google-Extended for limiting AI training/grounding in some other Google systems.
- Troubleshooting: URL Inspection tool to see HTML Googlebot received; recrawl can take days to months.

## OpenAI crawlers https://platform.openai.com/docs/bots (also developers.openai.com/api/docs/bots), fetched 2026-10-08
- OAI-SearchBot: used to surface websites in search results in ChatGPT's search features. Sites opted out of OAI-SearchBot will not be shown in ChatGPT search answers, though can still appear as navigational links. OpenAI recommends allowing OAI-SearchBot in robots.txt and allowing requests from published IP ranges (openai.com/searchbot.json).
- GPTBot: crawl content that may be used in training generative AI foundation models. Disallowing it indicates content should not be used for training. Independent of OAI-SearchBot.
- ChatGPT-User: certain user actions in ChatGPT and Custom GPTs; may visit a page when a user asks; not automatic crawling; robots.txt rules may not apply; not used to decide Search inclusion.
- It can take ~24 hours from a robots.txt update for search systems to adjust.
- OAI-AdsBot exists for ad landing pages (not relevant).
- ChatGPT search help article (help.openai.com) returned 403 to curl; did not read directly. Launch post: openai.com/index/introducing-chatgpt-search/ (search result only): Sources button / side panel of links. Secondhand: ChatGPT may search automatically or user can force search from tools menu or by typing / and choosing Search (NOT verified first-hand: describe generically).

## Bing Webmaster Tools (official Microsoft blogs, fetched)
- AI Performance report, public preview announced Feb 2026: https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
  - Shows how publisher content appears across Microsoft Copilot, AI-generated summaries in Bing, and select partner integrations.
  - Metrics: Total Citations; Average Cited Pages (unique pages per day); Grounding queries (key phrases AI used when retrieving content; a SAMPLE of overall citation activity); Page-level citation activity; Visibility trends over time.
  - Does not indicate ranking, placement, authority. Bing respects robots.txt. Suggests: clear headings, tables, FAQ sections; support claims with evidence; keep content fresh; IndexNow; Bing Places for local business.
  - Does NOT cover ChatGPT, Perplexity, Gemini or Google (per Microsoft: Copilot, Bing AI summaries, select partners).
- June 16 2026 update: https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/
  - Preview, globally: Intents (grounding queries classed Informational, Commercial, Navigational, Learn and Solve, Research, Creation, Local), Topics (clusters), Citation Share (% of citations for a grounding query attributed to your site out of all sites; observational, does not expose competitor domains), Compare (overlay previous period, e.g. current 30 days vs prior 30).
- Third-party (secondhand, not cited as fact): exports are manual (CSV-style: daily overview, page level, grounding queries); no API at Feb 2026 per Search Engine Land quoting Microsoft's Fabrice Canel. No click data. -> in guide say "check whether export is available in your account"; describe generically "download the data".

## Google Search Console (official help, fetched 2026-10-08)
- Blog 3 Jun 2026: https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports ("Introducing Search Generative AI performance reports in Search Console"). Note on page: as of 31 Aug 2026 rolled out to all websites worldwide. Shows impressions, pages, countries, devices (Search only), dates (hourly/daily/weekly/monthly). Data also stays inside overall performance report.
- Help: Generative AI performance report (Search) https://support.google.com/webmasters/answer/16984139 : shows impressions in AI Overviews and AI Mode; dimensions Pages, Countries, Dates, Devices; filter Search type Web text-based / Web multimodal; export button for chart and table; 1,000 row limit applies; chart aggregated by property (two results from same site = one impression); table by page. "Not seeing the report?" usually not enough impressions, or site excluded. NO clicks, CTR, queries (impressions only; clicks not in it per blog/secondary).
- Help: Search generative AI control https://support.google.com/webmasters/answer/16908024 : Settings > Search generative AI in Search Console. Options: Include (default) / Exclude / Inherit from parent. Exclude = links and content won't show in AI Overviews, AI Mode, Discover gen AI features; takes a few days. Does not affect AI training (Google-Extended for that).
- Performance report: data collected usually available in 2-3 days; dates in Pacific Time; 1,000 row limit in table.
- Secondary (not first-party): AI Overviews/AI Mode clicks and impressions count in Performance report totals under Web search type; you can't filter AI Mode alone in main report. Official ai-features page says "included in overall search traffic... Performance report, Web search type".
- Official Google Search Console connector for Claude: NOT found. Only third-party hosted/community MCP servers (Coupler.io, Porter Metrics, Windsor.ai, Markifact, community open-source). Guide: treat as optional, vet carefully, default to CSV export + upload. Do not name vendors as endorsements.

## Perplexity https://docs.perplexity.ai/docs/resources/perplexity-crawlers (fetched)
- PerplexityBot: surfaces and links websites in Perplexity search results; not used to crawl for AI foundation models; recommends allowing in robots.txt and permitting its published IP ranges (https://www.perplexity.com/perplexitybot.json).
- Perplexity-User: supports user actions; may visit a page to answer and include link; not for crawling or training; since user-requested, generally ignores robots.txt.
- Changes may take up to 24 hours. WAF (e.g. Cloudflare) may need allow rule combining User-Agent + IP.

## Claude (secondhand from search of support.claude.com article 8241126, couldn't open directly)
- Project knowledge: 30MB per file; unlimited number but total must fit context window; chats up to 20 files, 500MB (older copies say 30MB). -> Guide: say "check the upload limits on Anthropic's help page"; say "a few CSV files are fine".
- Connectors: see /home/user/buildwithvish/src/long/guides/connectors-and-mcp.html (internal guide, already verified by repo: Claude: Customize > Connectors; Free can add one custom connector).

## More first-hand (fetched 2026-10-08)
- Claude upload help https://support.claude.com/en/articles/8241126-uploading-files-to-claude : supported CSV, XLSX (needs code execution + file creation enabled), JSON, PDF, DOCX, TXT, HTML. Upload via + > Add files or photos. Chats: 500MB/file, 20 files/chat. Project files: 30MB per file, unlimited count but must fit context window.
- Claude Projects https://support.claude.com/en/articles/9517075-what-are-projects : available to all users incl. free (free: max five projects). Project knowledge + instructions. Paid plans get RAG expansion. A new beta version of projects is rolling out in stages (Claude Code first); existing projects keep working.
- Claude web search https://support.claude.com/en/articles/10684626-enabling-and-using-web-search : + > Web search toggle; with the new Claude experience there is no toggle, Claude searches when it helps; responses include citations.
- Claude connectors https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities : Customize > Connectors; "Google Drive to search your files" is an example; connectors inherit your permissions; tool permissions can be Always allow / Needs approval / Blocked; custom connectors on all plans (Free: one).
- ChatGPT search (via OpenAI help search snippets, article 9237897 returned 403 to curl): inline citations; Sources option lists cited pages; OpenAI says citations can be incomplete/outdated, open the page to check. Describe generically.
- Perplexity help center: numbered citations on every answer (hover/click). Gemini Apps help https://support.google.com/gemini/answer/14143489 : Sources button when links are available; "Double-check response". 
- Bing AI Performance: location "AI Performance" in left menu and CSV download per third-party guides; Microsoft's own post doesn't say. Describe generically.
- OpenAI says opted-out of OAI-SearchBot = not shown in ChatGPT search answers though can appear as navigational links.

## Decisions for the guide
- No official GSC connector for Claude found -> default CSV export + upload; mention third-party connectors only generically, read-only, vet them.
- Claude cannot tell you what ChatGPT says: only manual checks / pasted answers. Don't treat Claude web search as a proxy.
- Don't state exact menu path for the Generative AI report beyond "with the other performance reports"; Settings > Search generative AI is verified.
