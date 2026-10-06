# QA report: frontier-deployed-engineers-carousel

Run 2026-10-06 22:21 · **PASS** · 0 fail, 2 warn, 14 pass

| Result | Area | Check |
|---|---|---|
| WARN | links | not checked (--no-net): https://www.anthropic.com/news/claude-frontier-academy |
| WARN | links | not checked (--no-net): https://www.commbank.com.au/articles/newsroom/2026/10/commbank-engineers-anthropic-claude-frontier-academy.html |
| PASS | copy | hook 8 words: "Anthropic is putting $100M into one job title." |
| PASS | copy | closes on one open question: "What part of AI rollout do you think non-engineers are best placed to " |
| PASS | copy | caption 1121 chars (LinkedIn limit 3000) |
| PASS | copy | reading ease 63 (aim 50+) |
| PASS | facts | source dated 2026-10-02 is 4 days old (news window 14d) |
| PASS | facts | source dated 2026-10-03 is 3 days old (news window 14d) |
| PASS | design | slide 1: safe area, overflow, contrast, sizes |
| PASS | design | slide 2: safe area, overflow, contrast, sizes |
| PASS | design | slide 3: safe area, overflow, contrast, sizes |
| PASS | design | slide 4: safe area, overflow, contrast, sizes |
| PASS | design | slide 5: safe area, overflow, contrast, sizes |
| PASS | design | slide 6: safe area, overflow, contrast, sizes |
| PASS | design | slide 7: safe area, overflow, contrast, sizes |
| PASS | brand | Aurora Glass (paper) from brand tokens |

Manual checks (the reviewer agent signs these off): 3D quality (banding, muddy light), mascot consistency, legal (no third-party logos or characters), tone.
