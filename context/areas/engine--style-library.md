# engine/style-library

Define, store, and validate visual style specifications, tokens, and registry metadata for content cards.

- `style-library/01-vox-explainer/DESIGN.md`: Specifies Vox Explainer visual style: paper background, blue accents, stop‑motion, serif typography, hand‑drawn arrows, low‑shutter motion.
- `style-library/01-vox-explainer/style.json`: JSON: $schema, id, name, number, status, inspiration, summary, palette
- `style-library/01-vox-explainer/tokens.css`: css file
- `style-library/02-kallaway/DESIGN.md`: Defines Kallaway style: dark canvas, aurora bloom, glassmorphism, edge-lit elements, color tokens, typography, motion rules.
- `style-library/02-kallaway/style.json`: JSON: $schema, id, name, number, status, inspiration, summary, palette
- `style-library/02-kallaway/tokens.css`: css file
- `style-library/GUIDE.md`: Specifies style-library structure, naming scheme, required files, card contract, and registry generation rules. (uses MOTION_PHILOSOPHY.md, registry.json)
- `style-library/_blueprint/DESIGN.md`: Template for creating a new style: placeholder sections for prompt, colors, typography, motion, card kinds, anti-patterns.
- `style-library/_blueprint/style.json`: JSON: $schema, id, name, number, status, inspiration, summary, palette
- `style-library/_blueprint/tokens.css`: css file
- `style-library/registry.json`: JSON: generated_by, styleCount, cardCount, tiers, styles, warnings
