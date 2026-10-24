# profile-pipeline/linkedin

Generate LinkedIn carousel PDFs, captions, and assets from JSON content with validation and preview images.

- `linkedin/README.md`: Describes LinkedIn carousel pipeline: how to create PDF and caption, build command, approval steps, and posting rules. (uses build.py, theme.css)
- `linkedin/build.py`: Builds LinkedIn carousel: validates JSON, renders HTML, generates PDF via headless Chromium, creates preview PNGs, writes outputs to out/ folder. (uses theme.css)
- `linkedin/config.json`: JSON: handle
- `linkedin/content/agents-email-your-client.json`: JSON: slug, topic, slides, caption
- `linkedin/content/llm-judge-bias.json`: JSON: slug, topic, slides, caption
- `linkedin/examples/agents-email-your-client/caption.txt`: Caption for agent-client carousel: outlines agent roles, client communication guidelines, and a prompt to decide agent email usage.
- `linkedin/examples/llm-judge-bias/caption.txt`: Caption for LLM judge bias carousel: explains ad ranking pitfalls, fixes, and asks which ad was ignored by audience.
- `linkedin/fonts/Inter-OFL.txt`: Inter font license: SIL Open Font License 1.1 text, copyright, and usage permissions.
- `linkedin/fonts/Newsreader-OFL.txt`: Newsreader font license: SIL Open Font License 1.1 text, copyright, and usage permissions.
- `linkedin/tests/test_build.py`: Unit tests for build.py: verify content validation, secret blocking, placeholder detection, and HTML rendering correctness. (uses build.py, llm-judge-bias.json, theme.css)
- `linkedin/theme.css`: css file
