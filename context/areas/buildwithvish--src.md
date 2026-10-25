# buildwithvish/src

Provide source code for building assets, managing content, and rendering interactive WebGL scenes for the Vish website.

- `src/app.js`: App script sets up DOM utilities, constants, and navigation handlers for the site. (uses sound.js)
- `src/build.py`: Python build script compiles assets, generates site files, and handles local build mode. (uses content-more.js, ScrollTrigger.min.js, content-portfolio.js, UnrealBloomPass.js, style.css, RenderPass.js)
- `src/content-extra.js`: Defines 'built' guide type and lists two built tool guides with metadata and body content.
- `src/content-guides.js`: Defines tool categories, guide types, and a list of guide entries with metadata and body content.
- `src/content-launch.js`: Defines AI launch security checklist with 19 items, each having id, title, why, how.
- `src/content-more.js`: Defines project steps for building a website with AI, including steps, tools, and instructions.
- `src/content-portfolio.js`: Defines portfolio data: headline, intro, CV link, site link, stats, disciplines, brands, experience.
- `src/content-posts.js`: Defines LinkedIn batch article posts with slug, type, tools, level, mins, rank, fresh, title, excerpt, body.
- `src/portfolio-scene.js`: Creates DealScene WebGL component rendering 850 deals orbiting 9 brand clusters with interactive controls.
- `src/scene.js`: Creates Journey WebGL component with interactive cinematic scenes, modes, and visual effects using Three.js.
- `src/sound.js`: Creates a WebAudio-based ambient sound engine with depth filtering, reverb, and UI note synthesis.
- `src/style.css`: css file
