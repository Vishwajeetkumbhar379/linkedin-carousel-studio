# Batch 01 writing brief (shared by research agents)

Author: Vishwajeet "Vish" Kumbhar. MBA (IBC, Hochschule Offenburg, Germany), 850+ creator deals in influencer marketing, works at the intersection of AI and marketing, pivoting to AI Ops. Hub: Build with Vish (https://buildwithvish.netlify.app). Today is 2026-10-06.

## Goal
LinkedIn posts that make people stop, learn something useful, comment, and click through to the Build with Vish article. Mostly short videos (30-40 s), some carousels.

## Hard rules (QA will fail the post otherwise)
- No fabricated stats, quotes, testimonials or screenshots. Every number or factual claim must appear in `facts` with a real source URL and a date. News must be dated within the last 14 days (tools/product launches within 30 days), and backed by 2 independent sources or 1 primary source (the company's own announcement or docs).
- Vish's own experience may only use what is given above (850+ creator deals, MBA, AI x marketing work). Do not invent his results, clients or numbers.
- British English. No em dashes or en dashes anywhere (use commas, full stops, colons). Arrows (→) are fine.
- Banned words: delve, game-changer, unlock, unleash, supercharge, seamless, leverage, robust, elevate, harness, empower, revolutionise, cutting-edge, landscape, realm, tapestry, synergy, circle back, "in today's fast-paced world", "let's dive in", buckle up, secret sauce, "it's important to note", "whether you're a".
- Hooks: 12 words or fewer, specific, curiosity or tension, true. Pattern ideas: "X just did Y", "Stop doing X", "The X nobody talks about", a surprising number, a before/after.
- Plain, punchy, human. Short sentences. I statements where honest. Admit limits.
- Never use real company logos in visuals; describe generic objects (chat bubble, feed card, camera, star ring).

## Output: a JSON array of topic objects, written to the file path you are given
Each object:
{
 "slug": "kebab-case-unique",
 "format": "video" | "carousel",
 "pillar": "AI tools that change marketing work" | "Creator economy x AI" | "Real workflows and prompts" | "Career and AI Ops pivot" | "Contrarian takes",
 "score": 0-10 (freshness, usefulness, shareability, comment potential, brand fit averaged),
 "title": "site article title",
 "hook": "the post's first line / cover headline; may contain *one emphasised phrase* in asterisks",
 "subtitle": "one short line under the hook",
 "cover": {"concept": "a 3D scene that literally acts out the headline (one hero group + one context symbol)", "avatar": "surprised|smirk|laugh|full", "label": "short pointer label text"},
 "facts": [{"claim": "...", "source_name": "...", "url": "https://...", "date": "YYYY-MM-DD"}],
 "caption": "LinkedIn caption, 700-1300 characters: hook line, blank line, short paragraphs or → arrow lists, one honest personal angle, one easy closing question, then 'Full breakdown: https://buildwithvish.netlify.app/#read-<slug>'",
 "first_comment": "one line with the source links",
 "article": "the website article in Markdown, 450-750 words, with H2 subheads, a 'What I'd do' section, and a 'Sources' list linking every fact",
 // video only:
 "narration": [["phrase", "phrase"], ["phrase"], ...],   // 5-7 scenes, 12-15 phrases total, 28-40 seconds spoken. Conversational: like telling a friend. Does NOT read the screen word for word.
 "beats": [ one object per phrase, same order ],
 // carousel only:
 "slides": [ 6-8 slide objects ]
}

### Beat objects (video). One per narration phrase. Pick a look and fill its fields:
- {"look":"hook","bg":"ink","kick":"SHORT KICKER","title":"Big headline with *emphasis*"}
- {"look":"text","bg":"violet|ink|ivory|peach|cobalt","title":"short on-screen line with *emphasis*","size":"t1|t2|t3","sub":"optional small line"}
- {"look":"stamp","bg":"cobalt|ink","stamp":"1-2 WORDS","title":"line","sub":"optional"}
- {"look":"chips","bg":"peach|ivory","title":"line","chips":["2-4 short chips"]}
- {"look":"stat","bg":"cobalt|ink","value":"number exactly as sourced e.g. 1.2B or 15.3%","title":"what it measures","src":"Source: X, date","dots":200}
- {"look":"bars","bg":"ivory","title":"line","bars":[{"h":100,"c":"#C9C3E6","label":"A"},{"h":60,"c":"#5B4FE0","label":"B"}],"src":"source line"}   // only for sourced comparisons
- {"look":"versus","bg":"violet","title":"line","left":"label","right":"label"}
- {"look":"chat","bg":"ivory","prompt":"a prompt typed into a generic AI chat"}   // add "ad":true to show a Sponsored card
- {"look":"feed","bg":"peach","title":"line"}   // phone feed scrolling to a Sponsored post
- {"look":"cta","bg":"violet","title":"More *AI x marketing* every week.","button":"Follow Vish"}   // always the last beat
Add "trans": "whip|zoom|click|pop|rise" to every beat except the first. Vary backgrounds so neighbours differ. Use "avatar" on 3-4 beats to say how Vish's avatar reacts there: "surprised" (news, shock), "smirk" (catch, sceptical), "laugh" (fun, CTA), "stressed" (pain point, deadline, mistake), "point" (here's the thing / look at this), "thinking" (question, nuance). Text on screen is short; the voice carries detail.

### Slide objects (carousel)
- {"type":"cover","title":"hook with *emphasis*","subtitle":"...","chip":"pillar short name"}
- {"type":"point","label":"01 · Short label","title":"...","body":"40-45 words max, may use *emphasis*"}
- {"type":"stat","label":"...","value":"sourced number","title":"...","body":"...","source":"Source: X, date"}
- {"type":"list","title":"...","items":["4 short items"]}
- {"type":"compare","title":"...","left":{"label":"...","items":["..."]},"right":{"label":"...","items":["..."]}}
- {"type":"cta","title":"Save this before your next *client call*.","subtitle":"Full breakdown on Build with Vish.","question":"one easy question","button":"Save · Follow for AI x marketing","chip":"Free guide inside"}

### Added 7 Oct 2026: real-screen B-roll looks
- {"look":"clip","bg":"ivory","title":"line","clip":{"url":"https://github.com/owner/repo","scrollPx":1600}}   // the real page, recorded and scrolled
- {"look":"ui","bg":"ivory","title":"line","app":"Claude","screen":"Connectors","steps":[{"click":"Settings"},{"click":"Connectors"},{"click":"Google Drive"},{"result":"connected"}],"button":"Connect","toast":"Google Drive connected"}   // app walkthrough: the cursor clicks each step
- {"look":"ui","app":"Claude","screen":"New chat","steps":[{"type":"the exact prompt"},{"result":"site"}],"siteTitle":"...","siteSub":"..."}   // prompt typed, website with a 3D hero appears; result can also be "reply" with "reply":"..."
Use ui beats for every how-to step inside an AI app; only click names the sources describe.
