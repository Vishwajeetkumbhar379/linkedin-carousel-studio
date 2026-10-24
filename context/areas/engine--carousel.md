# engine/carousel

Generate, style, and render LinkedIn carousel decks as PNG/PDF using AI and Playwright.

- `carousel/__init__.py`: Initializes carousel package, sets up module imports.
- `carousel/ai.py`: Generates LinkedIn carousel JSON via Claude using topic, notes, author. (uses templates.py)
- `carousel/aurora.py`: Defines Aurora Glass theme variants and color palettes for carousel rendering. (uses studio.py)
- `carousel/cli.py`: CLI tool for rendering decks to PNG/PDF and drafting decks via Claude. (uses render.py, ai.py, creator-contract-checks.json)
- `carousel/render.py`: Renders carousel deck JSON to PNGs and PDF using Playwright; validates style rules. (uses templates.py)
- `carousel/studio.py`: Defines carousel studio themes, dimensions, fonts, and constants for rendering. (uses templates.py)
- `carousel/templates.py`: Provides slide template rendering functions and CSS for carousel slides.
