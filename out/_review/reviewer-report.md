# Reviewer report, 6 Oct 2026

Checked against research/raw and the MediaPost/eMarketer summary. Opened every PNG.

## Verdicts
- **EU watermark (carousel): fix first.** Missing a key hedge and a key limitation. Weak cover art.
- **ChatGPT image ads (video): fix first.** The hook overstates a US-only test. video.mp4 was still rendering and failed ffprobe ("moov atom not found"), so it is **unreviewed**.
- **Meta Creator Hub (image): don't ship yet.** It has a live placeholder, an unsourced claim, and stale "just" framing.

## Issues

| # | Sev | Location | Issue | Fix |
|---|---|---|---|---|
| 1 | blocker | meta/caption.md para 5 | `[VISH: confirm this line...]` is still in the caption. The 850+ claim is unconfirmed. | Vish confirms the line, then delete the bracket. |
| 2 | blocker | chatgpt/video.mp4 | The file is invalid (render in progress). Motion and burned-in text are unchecked. | After the render, run ffprobe and scrub all 30 s against video.json. |
| 3 | should fix | meta/caption.md bullet 5 | "what used to be Instagram-only" isn't in any source. MediaPost only says Facebook creators were onboarded to the Creator Marketplace API. | "Facebook creators now in the Creator Marketplace API". |
| 4 | should fix | meta/caption.md L1 | "Meta **just**..." about news that's 21 days old. sources.md itself says not to frame it as news. | "Meta merged creator discovery and paid ads into one hub." |
| 5 | should fix | meta/sources.md | No Meta primary source. Dates disagree: MediaPost (Tue 15 Sep) vs eMarketer "launched on Wednesday". | Verify on the Meta newsroom, or write "mid-September". |
| 6 | should fix | meta/caption.md, Disclosure line | The "Werbung"/"Anzeige" rule is a legal claim marked "re-verify". | Verify it, link the ad-labels page and add "not legal advice". |
| 7 | should fix | meta/image.png art | The ring cuts through the glass tile and splits the play icon. Horizontal refraction seams. The ring's right end curls open. It looks broken. | Re-render with the ring behind the tile, closed and with no seams, or drop the ring. |
| 8 | should fix | meta/image.png mascot | The "focused" eyes read as angry. | Use the neutral or happy variant. |
| 9 | nit | meta/image.png | The badge "850+ CREATOR DEALS IN" reads as cut off. "One screen" overstates "one platform". About 230px of dead space above the art. | "From 850+ creator deals". "one hub". Move the art up. |
| 10 | should fix | chatgpt scene 1, caption L1, cover poster | "ChatGPT **will show** ads next to the images you generate" implies every user. It's a US-only test with initial advertisers, and ads run on the free and low-cost tiers (TechCrunch). | "ChatGPT is testing ads next to the images you generate." |
| 11 | should fix | chatgpt scene 5 | On screen it drops "**blended** paid-search benchmark" and has no single-brand hedge (that's only in the caption). | Add "blended" and "One brand, early data." |
| 12 | should fix | chatgpt/caption.md CTA | "Test this in Q1?" goes to an EU audience, but the format is US-only. | Add "Not in Europe yet", or ask "if it reached the EU". |
| 13 | should fix | chatgpt s3 frame | The text says "Labelled", but the ad tile has no "Sponsored" tag, and it sits inside the fan, which undercuts "beside, not inside". | Add a "Sponsored" chip and offset the tile clearly to the side. |
| 14 | nit | chatgpt end.png, s5, s3 | Thin vertical line artefact on the purple tile (about x627, y345-420). s5: tile clips the right edge. s3: tile nearly touches the header pill. The same art in all 6 scenes feels static. | Fix the seam. Keep 48px padding. Vary scale and camera per scene. |
| 15 | nit | chatgpt/caption.md | "already plugged in" overstates "now support". | "now supported". |
| 16 | should fix | eu/slide-04, caption | ~80%/~95% is "for content such as psychology". It's "substantially lower" for maths. The caption drops "at 1% false-positive". | "Best case, prose. Much lower for maths." Add the FPR to the caption. |
| 17 | should fix | eu/slide-05 | Missing "**no watermark doesn't prove a human wrote it**" (OpenAI says this explicitly). "Only if long enough" is a condition, not a signal, and it also needs unedited, untranslated text from an eligible model. | Change the right column to a single item. Add a footer: "No watermark ≠ human-written." |
| 18 | should fix | eu/slide-04 + slide-07 #1 + caption | "Heavily edited text is harder to detect" next to "Editing... was always the job" can read as evasion advice. | Add "Edit for quality, not to hide AI use. Disclose anyway." Never cite the synonym-swap stats. |
| 19 | nit | eu/caption.md bullet 4 | Leaves out "and expert organisations". | Add it. |
| 20 | should fix | eu/slide-01 art | Blurry halos and a ghosted left edge on the bubble. Violet fringing on the bars. The magnifier lens shows empty white, so the "reveals hidden mark" idea fails. | Re-render with clean edges and have the lens enlarge the dot grid. |
| 21 | nit | eu/slides 5, 7, 8 | The numbering jumps 03 → 05 (slides 5 and 7 have no label). Widows: "it" (slide 5), "no?" (slide 8). | Add "04 ·" and "06 ·" labels. Balance the line breaks. |
| 22 | nit | eu/slides 2, 4, 6 | Cards float with about 250px of empty space above them. Several slides look like the same template. | Anchor the cards higher. Add a small accent to slide 4. |
| 23 | nit | all source lines | Grey mono text at about 18px becomes about 7px at phone scale. | At least 24px, with higher contrast. |
| 24 | nit | eu + chatgpt captions | Both end "Yes or no?" on the same day. It feels templated and close to vote-bait. | Use an open question on one of them. |
| 25 | should fix | all first-comment.md | Hash routes always return 200, so the linked pages aren't verified. | Confirm each page exists before posting. |

## Passed
- No em or en dashes.
- None of the banned words.
- British spelling.
- Hooks are 10 to 11 words.
- No third-party logos or characters.
- The mascot model is consistent across all three posts.
- All numbers trace to the raw sources.
- "Over the coming weeks", "eligible", the API opt-in/off-by-default point and "partner-reported" are all correctly hedged.
