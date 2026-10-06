# Inspiration log

Every source: URL, licence, what was learned, whether code or assets were used. Rule: patterns only; no code or assets copied unless MIT, Apache-2.0 or CC0, and then attributed.

## GitHub sweep, 6 Oct 2026 (ranked by stars, last push < 90 days)

| Repo | Stars | Last push | Licence | What I learned | Used |
|---|---|---|---|---|---|
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | ~93k | 6 Oct 2026 | MIT | Anti-slop rules: no gradient text, no glow, tinted shadows, colour lock, one accent, no fake-perfect numbers, emphasis via weight not font switch | **Installed** `.claude/skills/taste-skill` (commit ce26fc2) |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | ~77k | 6 Oct 2026 | Apache-2.0 | "The brief wins"; craft floor checks (contrast, depth, spacing, one authored motion moment); bans on eyebrows and section numbers (we keep ours because Vish's brief locks them) | **Installed** `.claude/skills/impeccable` (commit cf3d2fa) with LICENSE + NOTICE |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | ~10k | 6 Oct 2026 | Apache-2.0 | Shot "recipe cards" (hook, reveal, proof, CTA) for Remotion product videos; frame-deterministic rendering | Pattern only (our `templates/video/night.html` uses the same frame(t) idea) |
| [MengTo/threeui](https://github.com/MengTo/threeui) | ~6.5k | 6 Oct 2026 | MIT (+ separate asset/font licences) | Three.js hero sections: soft studio lighting, floating glass objects, slow camera drift | Pattern only. Also library #5 in Vish's Notion list |
| [pmndrs/react-three-fiber](https://github.com/pmndrs/react-three-fiber) / [drei](https://github.com/pmndrs/drei) | 33k / 10k | Oct 2026 | MIT | ContactShadows and Environment presets → our canvas contact shadow + RoomEnvironment | Pattern (we use vanilla Three.js, no React needed for stills) |
| [img2threejs/img2threejs](https://github.com/img2threejs/img2threejs) | ~17.6k | Oct 2026 | see repo | Procedural "code-only" 3D models from a reference image | Candidate for mascot/prop generation after review |
| [DavidHDev/canvas-ui](https://github.com/DavidHDev/canvas-ui) | ~4.8k | Oct 2026 | see repo | WebGL effects over real HTML text, which keeps text crisp | Pattern: our 3D layer sits under HTML text |
| [latent-spaces/brag](https://github.com/latent-spaces/brag) | ~13.8k | Oct 2026 | see repo | One-command launch videos for build-in-public posts | Candidate for "Build with Vish projects" video format |
| [FranciscoMoretti/carousel-generator](https://github.com/FranciscoMoretti/carousel-generator) | 213 | Oct 2026 | see repo | Slide schema + PDF export for LinkedIn | Confirms our JSON deck approach |
| [AgriciDaniel/linkedin-content-creator](https://github.com/AgriciDaniel/linkedin-content-creator) | 97 | Oct 2026 | see repo | Research → calendar → batch flow; posts via LinkedIn OAuth | Flow reference only; we keep a human approval step |
| [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills) | ~3k | Oct 2026 | list | 67 DESIGN.md / SKILL.md design skills | Monthly refresh source |
| [h3nryprod01/design-taste](https://github.com/h3nryprod01/design-taste) | 65 | Oct 2026 | see repo | Merge of taste + impeccable + Emil Kowalski motion rules | Not installed (we have the two originals) |
| remotion-dev templates (tiktok captions, audiogram, code-hike) | 220-283 | Sep-Oct 2026 | Remotion licence | Word-level caption timing (Whisper), audiogram layout | Remotion licence: free for individuals and teams of up to 3. Flagged before any team use |

## Vish's hand-picked sources

| Source | Status | Learned |
|---|---|---|
| Notion: The 5 Inspiration Libraries (curated.design, recent.design, 21st.dev, originkit.dev, threeui.com) | ✅ fetched via Crustdata (notion.site blocked here) | Workflow: screenshot single elements, keep them in an `inspiration/` folder, talk Claude through each. threeui has an MCP (worth connecting) |
| aiwithanushka profile | ✅ fetched (49.1K followers; founder of mcode.ai) | Account positioning: "AI automation" + comment-keyword lead magnets |
| 7 Instagram posts | ⚠️ captions + likes/comments only, **no slide images** (Instagram blocks image fetches) | See `teardowns/instagram-references.md`. Need screenshots from Vish for visual teardown |

## 2026 trend notes (search, 6 Oct)
- Soft clay 3D and frosted "liquid glass" surfaces are the mainstream 2026 look (manypixels.co, getillustrations.com). Risk: it is becoming the new template. Our edge has to be the system (locked cards, mascot, honest data), not the material alone.
