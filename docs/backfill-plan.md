# Backfill plan (runs after the go-ahead)

Source: `topics/posted.json` (8 carousels found on Build with Vish). Every one already has a matching site page, so step 1 is upgrading pages, not creating them.

| Carousel | Site page | Page state | Redesign priority | Why |
|---|---|---|---|---|
| Your prompts aren't bad. Your briefs are. | brief-ai-like-an-agency | long-form exists | **1** | Core Vish method, evergreen, ties to 850+ deals |
| Stop picking creators by follower count. | shortlist-creators-with-ai | short card only | **2** | Strongest brand fit; page needs depth (the scoring sheet) |
| "#ad somewhere" isn't a plan in Europe. | ad-labels-in-europe | short card only | **3** | Germany angle; re-verify every country rule first |
| 4 numbers every client meeting comes down to. | creator-campaign-math | short card only | 4 | Good save bait; add a calculator to the page |
| The first AI answer is a draft. | one-line-follow-ups | long-form exists | 5 | |
| I built a website without writing code. | build-website-no-code | project page | 6 | |
| Tired of re-explaining yourself to AI? | ai-about-me-folder | project page | 7 | |
| 5 AI workflows. Zero code. | no-code-ai-workflows | short card only | 8 | Re-check every tool claim (most likely to be stale) |

Order of work per item: re-verify every fact as still true today → upgrade the page (long-form spec in `buildwithvish/tools/longform/STYLE.md`) → Netlify draft preview → redesigned carousel in the chosen direction → QA → review pack.

Needed from Vish: which of these were actually posted on LinkedIn (URLs and dates), plus any posts not on the site (LinkedIn data export, or links).
