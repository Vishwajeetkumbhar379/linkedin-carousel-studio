# QA report: 2026-10-06-chatgpt-image-ads

Run 2026-10-06 19:34 · **PASS** · 0 fail, 3 warn, 9 pass

| Result | Area | Check |
|---|---|---|
| WARN | links | https://buildwithvish.netlify.app/#read-brief-ai-like-an-agency -> <urlopen error Tunnel connection failed: 403 Forbidden> |
| WARN | links | https://techcrunch.com/2026/10/05/openai-launches-visual-ads-that-appear-alongside-image-generation-results -> <urlopen error Tunnel connection failed: 403 Forbidden> |
| WARN | links | hash route #read-brief-ai-like-an-agency always returns 200; confirm the page exists in buildwithvish src/long before posting |
| PASS | copy | hook 8 words: "ChatGPT is turning image prompts into ad space." |
| PASS | copy | closes on one open question: "It's US-only for now. What would you need to see before you'd move tes" |
| PASS | copy | caption 847 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 58 (aim 50+) |
| PASS | facts | source dated 2026-10-05 is 1 days old (news window 14d) |
| PASS | facts | source dated 2026-10-06 is 0 days old (news window 14d) |
| PASS | facts | number '1.2 billion' traced to sources.md |
| PASS | facts | number '1.2B' traced to sources.md |
| PASS | facts | number '15.3%' traced to sources.md |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
