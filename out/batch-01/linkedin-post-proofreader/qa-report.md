# QA report: linkedin-post-proofreader

Run 2026-10-06 22:21 · **PASS** · 0 fail, 4 warn, 5 pass

| Result | Area | Check |
|---|---|---|
| WARN | links | not checked (--no-net): https://news.linkedin.com/2026/how-linkedin-is-tackling-ai-slop |
| WARN | links | not checked (--no-net): https://www.linkedin.com/help/linkedin/answer/a16661057 |
| WARN | links | not checked (--no-net): https://www.socialmediatoday.com/news/linkedin-ditches-post-enhancement-launches-post-proofreader/830851/ |
| WARN | links | not checked (--no-net): https://www.socialmediatoday.com/news/linkedin-says-1m-people-have-reported-ai-slop/828465/ |
| PASS | copy | hook 7 words: "LinkedIn just killed its own AI writer." |
| PASS | copy | closes on one open question: "Do you write first and polish with AI, or the other way round?" |
| PASS | copy | caption 1000 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 74 (aim 50+) |
| PASS | facts | source dated 2026-09-20 is 16 days old (tool window 30d) |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
