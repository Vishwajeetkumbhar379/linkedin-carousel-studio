# Vish: brand identity (merged)

Status: **draft**, locks after Vish picks a direction at the test-first gate.
Machine-readable version: [`tokens.json`](tokens.json). If the Build with Vish theme changes, edit `tokens.json` only and re-run `make tokens` (regenerates `brand/tokens.css`).

## How this was built

The two live sites are blocked by this cloud container's network policy, so I read their source on GitHub instead (same code Netlify deploys):

| Source | What I took |
|---|---|
| `buildwithvish` repo, `src/style.css`, `app.js`, `content-more.js`, `tools/longform/STYLE.md`, `emails/` | Colour tokens (day + night), Geist type, logo mark, slide component, 8 existing carousels, voice rules, banned words, link structure |
| `Vishwajeetkumbhar379` repo, `portfolio/index.html` | Portfolio palette (bone, deep teal, signal amber), Syne/Public Sans/IBM Plex Mono, section structure, project list |
| This repo, `carousel/templates.py` | The locked carousel rules (tinted cards, #7F77DD, 0.5px borders, badge, pill counter, handle top-left) |
| `vish-linkedin-content` skill | Positioning line, phrases, CTA patterns, the dark #0A0A0F motion style |

## Positioning

**AI x marketing, from someone who has run 850+ creator deals.** Rare, high-signal posts that a marketer can act on the same day. Not AI news recaps.

- Who: Vishwajeet (Vish) Kumbhar. MBA (IBC) student in Germany, 4+ years in influencer marketing and brand management, moving into AI Ops / Product Ops / Growth.
- Proof he can use: 850+ creator deals, team lead experience, 13 open-source tools on GitHub, Build with Vish (a free learning hub he built), the tools in this repo.
- Do not name past employers or clients in public copy unless Vish confirms it per post (the BwV style guide forbids it; the old skill names some brands).
- Never include phone, address, city or university name in public assets.

## The two identities, and how they merge

| | Build with Vish (learning hub) | Portfolio (hire me) | Merged LinkedIn system |
|---|---|---|---|
| Feel | Calm porcelain by day, cinematic particle night | Editorial, bone paper, deep teal, amber signal | BwV calm + portfolio's editorial confidence |
| Type | Geist + Geist Mono | Syne + Public Sans + IBM Plex Mono | **Geist** for everything; Syne reserved for Direction C |
| Accent | Iris violet (#4A44C4 day / #A99CFF night), brand #7F77DD | Signal amber #D99A1E | **#7F77DD** (locked), aurora teal and coral as tints |
| Signature | Rotated-square-with-dot logo, glass panels, particle 3D | Globe, timeline, "Things I've built" | Logo mark + original mascot + 3D hero objects |

Section names to reuse as series names (they already exist on the site, so a post can point to the same word):
Guides · Projects · Carousels · Build Notes (newsletter) · Start here · Launch checklist · Things I've built.

## Locked carousel system (carried over, not replaced)

- 1080 x 1350, 7 to 10 slides, slide 1 hook under 12 words.
- Handle top-left (VK avatar + "Vish Kumbhar" + "Build with Vish"), pill counter top-right.
- Tinted cards: purple #F5F4FF, teal #F0FBF6, coral #FEF6F3. Accent #7F77DD. 0.5px borders. Badge system.
- `swipe →` cue on every slide but the last. Last slide: save CTA + one open question.
- **New on top:** a 3D hero object per slide 1 and per section break, the mascot in a corner, 2 to 3% grain.

## Voice

Plain, direct, warm, brutally honest. Short lines. "I" for opinions. Arrow lists (→). Stack framing ("the stack I'd use").
British English. **No em or en dashes.** Banned words live in `tokens.json > voice.banned` and are enforced by `scripts/qa`.

Things Vish says: "here's what most people miss", "the honest breakdown", "no fluff", "after 850+ creator deals".
Things Vish never says: synergy, leverage, "in today's fast-paced world", anything that sounds like a press release.

## Design guardrails (from the taste and impeccable skills, adapted)

The brief wins over these where they clash (purple accent, badges and counters are Vish's choice, so they stay). Everything else applies:

- No gradient text, no neon glow halos, no purple-to-blue gradient backgrounds.
- No emoji as icons on slides. Use the 3D objects, the mascot, or a drawn icon set.
- Shadows are soft and tinted toward the background hue, never pure black.
- One authored motion moment per video scene, not effects everywhere.
- No fake numbers. Every number on a slide traces to `sources.md`.
- Contrast: body text 4.5:1 minimum, large text 3:1 (checked by `scripts/qa`).

## Mascot

See [`mascot/`](mascot/). "Dot": a small soft-clay violet character whose antenna carries the dot from the BwV logo. Original, does not resemble Claude, Anthropic or any existing brand character.
