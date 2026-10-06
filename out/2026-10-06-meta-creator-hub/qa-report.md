# QA report: 2026-10-06-meta-creator-hub

Run 2026-10-06 21:30 · **PASS** · 0 fail, 6 warn, 9 pass

| Result | Area | Check |
|---|---|---|
| WARN | copy | contains a line Vish must confirm before posting |
| WARN | design | mascot not used on any slide |
| WARN | links | https://buildwithvish.netlify.app/#read-shortlist-creators-with-ai -> <urlopen error Tunnel connection failed: 403 Forbidden> |
| WARN | links | https://www.emarketer.com/content/meta-s-creator-marketing-hub-gives-brands-central-resource-partnerships -> <urlopen error Tunnel connection failed: 403 Forbidden> |
| WARN | links | https://www.mediapost.com/publications/article/418022/ -> <urlopen error Tunnel connection failed: 403 Forbidden> |
| WARN | links | hash route #read-shortlist-creators-with-ai always returns 200; confirm the page exists in buildwithvish src/long before posting |
| PASS | copy | hook 7 words: "Meta just made creator ads one click." |
| PASS | copy | closes on one open question: "Which part of creator campaigns still eats most of your week?" |
| PASS | copy | caption 1130 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 64 (aim 50+) |
| PASS | facts | source dated 2026-09-15 is 21 days old (tool window 30d) |
| PASS | facts | source dated 2026-09-16 is 20 days old (tool window 30d) |
| PASS | facts | source dated 2026-10-06 is 0 days old (tool window 30d) |
| PASS | design | slide 1: safe area, overflow, contrast, sizes |
| PASS | brand | Aurora Glass (paper) from brand tokens |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
