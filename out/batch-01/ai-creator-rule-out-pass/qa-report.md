# QA report: ai-creator-rule-out-pass

Run 2026-10-06 22:20 · **PASS** · 0 fail, 4 warn, 4 pass

| Result | Area | Check |
|---|---|---|
| WARN | facts | opinion post: no factual claims, no sources needed |
| WARN | links | not checked (--no-net): https://buildwithvish.netlify.app/#read-creator-outreach-that-gets-replies |
| WARN | links | not checked (--no-net): https://buildwithvish.netlify.app/#read-shortlist-creators-with-ai |
| WARN | links | hash route #read-shortlist-creators-with-ai always returns 200; confirm the page exists in buildwithvish src/long before posting |
| PASS | copy | hook 10 words: "Use AI to rule creators out, not to find them." |
| PASS | copy | closes on one open question: "Do you shortlist on fit first, or on numbers first?" |
| PASS | copy | caption 873 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 82 (aim 50+) |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
