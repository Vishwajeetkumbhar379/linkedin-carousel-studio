# Reference study: the Instagram posts Vish loves (7 Oct 2026)

How this was gathered: Instagram blocks direct fetches, so captions, accounts and engagement come from the public post page and `/embed/captioned/` view (Crustdata web fetch, 7 Oct 2026). I could read captions, likes and comments, not the frames. Hooks and structure below are taken from the captions. Visual notes marked *(inferred)* come from the caption, the comment keyword and the account's format, not from seeing the slides. Engagement is as shown on 7 Oct 2026.

## The ten references

| # | Post | Hook (from caption) | Format | Structure | Visual devices | Why it works |
|---|---|---|---|---|---|---|
| 1 | [adrien.ninet, reel](https://www.instagram.com/reel/DeJi-ZaIqdW/) · 54 likes, 42 comments | "Your vibe-coded app can get sued before it makes a single sale" | Talking reel + prompt giveaway | Fear hook → "fines are per visitor, per email" → "so I paste one prompt into Claude" → 6 fixes it makes → "ship fast without shipping a lawsuit" | Screen of the prompt running *(inferred)*; ⚖️ emoji as the context symbol | Specific fear, then one prompt that removes it. Comment "SUED" gate. |
| 2 | [zerotoui, carousel](https://www.instagram.com/p/DeKeKPqApUT/) · 185 likes in 10 h | "You can spot AI slop in 2 seconds. These 7 steps won't remove all of it." | Step-by-step carousel | Problem → 7 numbered steps (research first, who it's for, style guide, real story, 3 layouts with trade-offs, test in browser, cut) → honest "still some issues" | Numbered step slides, before/after UI shots *(inferred)* | Admits limits. Steps are concrete and in order. Full prompt on their site. |
| 3 | [badarmunir_official, carousel](https://www.instagram.com/p/DeEsVurgHbe/) · 341 likes, 219 comments | No caption; every comment is "Auto" | Automation tutorial carousel *(inferred)* | Comment-keyword lead magnet for an automation workflow *(inferred)* | Tool-stack slides *(inferred)* | Comment count is 64% of likes: the keyword gate drives comments, which drives reach. |
| 4 | [aiwithanushka, carousel](https://www.instagram.com/p/DdsihgtCCKx/) · 253 likes, 584 comments | "Comment 'leads' for access" (Claude for lead gen) | Guide carousel | Cover promise → steps → "comment for the guide" | Clean text-first slides *(inferred)* | Comments beat likes more than 2 to 1. The guide is the product. |
| 5 | [forcceee_, reel](https://www.instagram.com/reel/DdfCKASozT2/) · 3.3K likes, 3.2K comments | "Claude Design launched Open Design, a free platform compatible with any AI" | Big-claim tool reel | Claim → what it makes (sites, decks, motion) → numbers (259 skills, 142 design systems) → "comment design" | Fast screen recordings of the tool *(inferred)* | "Free" + a famous name + concrete numbers. Note: the caption overstates who launched it; Open Design is a community project (github.com/nexu-io/open-design). We keep the energy, not the error. |
| 6 | [the.bohdana, carousel](https://www.instagram.com/p/DdwSDuLkdWO/) · 1,100 likes, 8 comments | "the stack i used to vibe code my portfolio" | Tool-stack carousel | One tool per slide, in build order | Aesthetic product shots, soft palette *(inferred)* | Pure save-bait: a stack you can copy. Low comments, high likes. |
| 7 | [jayantcreates.ai, carousel](https://www.instagram.com/p/Ddvgad1lQuh/) · 689 likes, 1.1K comments | "Instagram isn't in Claude's connector list, but you can still connect it" | Big-claim + numbered capability list | Tension hook → 5 numbered things Claude can then do → trust line ("official API, no scraping") | Phone/app cut-outs *(inferred)* | "X + Claude" mash-up, numbered list, a trust line that answers the obvious objection. |
| 8 | [gregisenberg, reel](https://www.instagram.com/reel/DeHcs-lxbAd/) · 210 likes, 90 comments | Muse business ideas | Talking-head idea reel | New platform → ideas to build on it → "comment MUSE" | Face to camera, captions *(inferred)* | Turns a launch into opportunities for the viewer. |
| 9 | [joshua.esca, reel](https://www.instagram.com/reel/DdsswbupDx8/) · 974 likes, 69 comments | "UI design is getting crazy." | Big-claim tool reel with motion graphics | Claim → the Figma agent going idea → editable design → "less time fighting tools" | Heavy motion graphics; a commenter asked what he edits in | Short, confident, visual proof. "Crazy" framing like "Opus 5.5 is crazy". |
| 10 | [aiwithanushka, carousel](https://www.instagram.com/p/Dd3sgeCCBuv/) · 202 likes, 248 comments | "Comment 'save' to get access to the whole guide" ([claude, ai, llm]) | Guide carousel | Cover → tips → guide gate | Text-first slides *(inferred)* | Save + comment loop. |

Also shown by Vish: two reels on free-token GitHub repos, [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) (README: "7.4 billion tokens per month. 34 free LLM providers") and [OmniRoute](https://github.com/diegosouzapw/OmniRoute) (README: "~1.62B Free Tokens / Month"). Pattern: one big free number, the repo on screen, one command to start.

## 10 patterns to copy

1. **Big claim, then proof on screen.** "Opus 5.5 is crazy" works only because the next beat shows the page. We show the real GitHub or anthropic.com page as a screen recording (`clip`), and every number is sourced.
2. **Name-brand mash-ups.** "Claude + Instagram", "Claude Design, free". Put a tool people know next to an outcome they want. Only when a dated launch supports it.
3. **"Free" plus one huge number.** 7.4B tokens, 34 providers. Quote the README exactly and say it's the maintainer's figure.
4. **One step per slide, in build order.** Script → voice → B-roll → motion → sound. Numbered labels ("01 · Voice").
5. **Copy-paste payloads.** Exact prompts and commands in the body (`pip install kokoro`). Saves follow.
6. **Admit the limit.** zerotoui's "won't remove all of it" earns trust. Add one honest catch per post (free tiers have caps, beta only, paid plans only).
7. **A trust line for the obvious objection.** "Official API, no scraping." For us: licence, cost, who it's for.
8. **Stack posts.** "The stack I used" carousels get saves with little copy. One tool per slide, with what it costs.
9. **Lead magnet without DMs.** The references gate the guide behind a comment keyword. Vish never DMs automatically, so we point to the full guide on Build with Vish and ask one easy question to drive comments.
10. **Calm, confident delivery.** Short claims, unhurried voice, motion graphics that move only when the line changes. One idea per beat.
