import json
from pathlib import Path

import pytest

from carousel.studio import THEMES, render_slide

ROOT = Path(__file__).parent.parent
DECK = json.loads((ROOT / "out" / "2026-10-06-eu-ai-text-watermark" / "deck.json").read_text())


def test_every_theme_renders_locked_chrome():
    for theme in THEMES:
        deck = dict(DECK, theme=theme)
        h = render_slide({"type": "point", "label": "01", "title": "Hi *there*", "body": "x"}, 2, 8, deck, {})
        assert "2 / 8" in h and "Vish Kumbhar" in h and "Build with Vish" in h and "<em>there</em>" in h


def test_single_image_mode_hides_counter_and_swipe():
    deck = dict(DECK, single=True, tag="Creator marketing")
    h = render_slide({"type": "cover", "title": "x"}, 1, 1, deck, {})
    assert "Creator marketing" in h and "1 / 1" not in h and "swipe →" not in h


def test_cta_has_question_and_no_swipe():
    h = render_slide(DECK["slides"][-1] | {"mascot": None}, 8, 8, DECK, {})
    assert "YOUR TURN" in h and "swipe →" not in h


def test_brand_tokens_define_locked_rules():
    t = json.loads((ROOT / "brand" / "tokens.json").read_text())
    assert t["color"]["brand"]["violet"] == "#7F77DD"
    assert t["color"]["tints_locked"] == {"purple": "#F5F4FF", "teal": "#F0FBF6", "coral": "#FEF6F3"}
    assert "delve" in t["voice"]["banned"]


def test_qa_copy_checks_catch_dashes_and_banned_words(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from qa import check_copy, flesch

    (tmp_path / "caption.md").write_text("Let's delve into this — now\n\nWhat do you think?")
    R = []
    check_copy(tmp_path, {"slides": []}, R)
    msgs = " ".join(m for _, _, m in R)
    assert "banned phrase 'delve'" in msgs and "em/en dash" in msgs
    assert flesch("The cat sat. It was warm.") > 80


def test_backlog_only_ships_8_plus():
    b = json.loads((ROOT / "topics" / "backlog.json").read_text())
    for t in b["topics"]:
        assert t["ships"] == (t["score"] >= 8)
        assert all(len(s) == 4 and s[2] for s in t["sources"]), t["id"]
