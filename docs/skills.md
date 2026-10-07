# Skills installed for the content engine (7 Oct 2026, approved by Vish)

Project skills live in `.claude/skills/` and load in every Claude Code session opened in this repo (including the weekly routine).
Each folder keeps its upstream LICENSE where one exists.

| Area | Skills | Source (licence) | Use in the engine |
|---|---|---|---|
| Design taste | taste-skill (design-taste-frontend), soft-skill, minimalist-skill, redesign-skill, image-to-code-skill, output-skill | github.com/Leonxlnx/taste-skill (MIT), tasteskill.dev | Per-post art direction, anti-template audit of slides and video frames |
| Design rules | web-design-guidelines | github.com/vercel-labs/agent-skills | Typography, contrast, spacing audit |
| Design rules | frontend-design | github.com/anthropics/skills | Distinct aesthetic per piece |
| Design systems | docs/design-library/ (74 DESIGN.md files) | github.com/VoltAgent/awesome-design-md (MIT) | Reference styles to vary layout and motion inside Vish's palette and fonts |
| UI components | 21st-ui + 21st Magic MCP (`.mcp.json`, key from env `API_KEY_21ST`, free at 21st.dev/mcp) | github.com/21st-dev/magic-mcp (ISC) | App-style UI cut-outs for B-roll |
| Browser | playwright-cli | github.com/microsoft/playwright-cli (Apache-2.0) | Real screen recordings of live pages |
| Motion video | hyperframes, -core, -animation, -creative, -cli, -keyframes, -audio, -registry, motion-graphics, faceless-explainer, general-video, product-launch-video, embedded-captions, media-use, slideshow | github.com/heygen-com/hyperframes (Apache-2.0) | HTML + GSAP motion graphics rendered to MP4 |
| Animation | gsap-core, gsap-timeline, gsap-plugins, gsap-utils, gsap-performance | github.com/greensock/gsap-skills (MIT); GSAP is free incl. plugins | Choreography, SplitText, morphs |
| Motion principles | motion-design | github.com/LottieFiles/motion-design-skill (MIT) | Timing, easing, choreography |
| Viral writing | hook-generator, niche-research, post-scorer, reels-scripting, content-matrix | github.com/charlie947/social-media-skills (MIT) | Hooks, trend research (post-scorer and reels-scripting need Apify, paid) |
| LinkedIn | linkedin-post-writer, linkedin-hook-extractor, linkedin-humanizer, linkedin-content-planner | github.com/sergebulaev/linkedin-skills (MIT) | 20 hook formulas from 400 viral posts, de-AI pass |

Telemetry is off via `.claude/settings.json` (`HYPERFRAMES_NO_TELEMETRY=1`, `DO_NOT_TRACK=1`).
