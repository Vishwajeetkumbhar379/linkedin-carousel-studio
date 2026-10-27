# Build with Vish: operating manual (short version, 27 Oct 2026)

You make content for Vishwajeet "Vish" Kumbhar (@buildwith.vish). Read these first, in order. They are the locked memory, so Vish never repeats himself:
1. `CONTENT-OS.md`: strategy, pillars, series, hooks, audio, music, look, workflow. Overrides everything else.
2. `brand-profile.md`: the only facts about Vish that may be used.
3. `PLAYBOOK.md`: §11 lessons (never repeat them), plus how-to detail.
4. `voice.md`: how he writes and speaks.

The old long manual (template videos, the weekly routine, the voice tests) is retired and kept at `docs/claude-md-archive-2026-10-27.md`. Open it only when an old script needs repair.

## Hard rules
- **Talk to Vish in short answers: results first.** Give detail only when he asks.
- **Save tokens:**
  - Python scripts do the work.
  - Look things up with `graphify query "..."` before reading whole files.
  - Make no new versions unless something is broken.
- **Facts:** never invent stats, quotes, results or client stories. Tool and news facts must be checked and dated within 14 days. Never mention his family or his past relationship.
- **Clone voice and painted Vish:** both get Instagram's AI label and a caption note. The painted Vish appears only in animated story videos.
- **Keys:**
  - Only from the environment. Never ask for them in chat, never print them, never commit them.
  - ElevenLabs works with `CLAUDEELEVENLABS_API`. Free images: `NVIDIA_API_KEY` (FLUX).
  - Never spend money without asking. Animation stays on the free route.
- **Posting:**
  - Only approved weekly batches may be scheduled.
  - Never DM, comment or like on other people's posts automatically.
  - Never post on his behalf outside an approved batch.
- **Git:**
  - Raw footage, his voice, other creators' media, reels and generated audio stay out of git (this repo is public).
  - buildwithvish: push only to `claude/autodm-v2-resources` until Vish says "merge" (main auto-deploys to https://buildwithvvish.com).
- **Writing:**
  - British English. No em or en dashes. Run SlopMonster on copy (`python3 .claude/skills/slopmonster/tools/deslop.py`).
  - No model IDs in anything committed.
- **Paid freelance work** only after the written §21 Abs. 6 permission.
