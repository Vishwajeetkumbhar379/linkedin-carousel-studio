# QA report: 2026-10-06-eu-ai-text-watermark

Run 2026-10-06 17:14 · **PASS** · 0 fail, 4 warn, 19 pass

| Result | Area | Check |
|---|---|---|
| WARN | links | not checked (--no-net): https://buildwithvish.netlify.app/#read-eu-ai-text-watermark |
| WARN | links | not checked (--no-net): https://community.openai.com/t/openais-approach-to-eu-text-provenance-rules/1403521 |
| WARN | links | not checked (--no-net): https://openai.com/index/eu-text-provenance/ |
| WARN | links | hash route #read-eu-ai-text-watermark always returns 200; confirm the page exists in buildwithvish src/long before posting |
| PASS | copy | hook 10 words: "ChatGPT text in the EU is getting an invisible watermark." |
| PASS | copy | closes on one open question: "Would you tell a client a draft was AI-assisted? Yes or no?" |
| PASS | copy | caption 992 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 66 (aim 50+) |
| PASS | facts | source dated 2026-10-05 is 1 days old (news window 14d) |
| PASS | facts | source dated 2026-10-06 is 0 days old (news window 14d) |
| PASS | facts | number '1%' traced to sources.md |
| PASS | facts | number '400 tokens' traced to sources.md |
| PASS | facts | number '80%' traced to sources.md |
| PASS | facts | number '95%' traced to sources.md |
| PASS | design | slide 1: safe area, overflow, contrast, sizes |
| PASS | design | slide 2: safe area, overflow, contrast, sizes |
| PASS | design | slide 3: safe area, overflow, contrast, sizes |
| PASS | design | slide 4: safe area, overflow, contrast, sizes |
| PASS | design | slide 5: safe area, overflow, contrast, sizes |
| PASS | design | slide 6: safe area, overflow, contrast, sizes |
| PASS | design | slide 7: safe area, overflow, contrast, sizes |
| PASS | design | slide 8: safe area, overflow, contrast, sizes |
| PASS | brand | theme 'studio' comes from brand tokens |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
