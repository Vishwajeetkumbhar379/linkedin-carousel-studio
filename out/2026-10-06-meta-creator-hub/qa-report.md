# QA report: 2026-10-06-meta-creator-hub

Run 2026-10-06 17:17 · **PASS** · 0 fail, 5 warn, 9 pass

| Result | Area | Check |
|---|---|---|
| WARN | copy | contains a line Vish must confirm before posting |
| WARN | links | not checked (--no-net): https://buildwithvish.netlify.app/#read-shortlist-creators-with-ai |
| WARN | links | not checked (--no-net): https://www.emarketer.com/content/meta-s-creator-marketing-hub-gives-brands-central-resource-partnerships |
| WARN | links | not checked (--no-net): https://www.mediapost.com/publications/article/418022/ |
| WARN | links | hash route #read-shortlist-creators-with-ai always returns 200; confirm the page exists in buildwithvish src/long before posting |
| PASS | copy | hook 10 words: "Meta put creator discovery and paid ads in one screen." |
| PASS | copy | closes on one open question: "Which part of creator campaigns still eats most of your week?" |
| PASS | copy | caption 1147 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 63 (aim 50+) |
| PASS | facts | source dated 2026-09-15 is 21 days old (tool window 30d) |
| PASS | facts | source dated 2026-09-16 is 20 days old (tool window 30d) |
| PASS | facts | source dated 2026-10-06 is 0 days old (tool window 30d) |
| PASS | design | slide 1: safe area, overflow, contrast, sizes |
| PASS | brand | theme 'field' comes from brand tokens |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
