# engine/tests

Validate carousel and studio functionalities, ensuring correct rendering, markup, AI draft retries, and brand compliance.

- `tests/test_carousel.py`: Test suite for carousel: validates deck style, renders slides, checks markup, retries AI draft, renders PDF. (uses ai.py, templates.py, render.py, creator-contract-checks.json)
- `tests/test_studio.py`: Studio tests: render themes, single image mode, CTA rules, brand tokens, QA copy checks, backlog ship logic. (uses studio.py, qa.py, tokens.json, backlog.json)
