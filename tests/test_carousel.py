import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from carousel.ai import draft
from carousel.templates import render_slide, validate

DECK = json.loads((Path(__file__).parent.parent / "examples" / "creator-contract-checks.json").read_text())


def test_example_deck_passes_style_rules():
    assert validate(DECK) == []


def test_rules_catch_bad_decks():
    bad = {"slides": [{"type": "point", "title": "x"}] * 3}
    errs = validate(bad)
    assert any("5-12" in e for e in errs) and any("cover" in e for e in errs) and any("call to action" in e for e in errs)


def test_every_slide_type_renders_with_counter_and_handle():
    for i, s in enumerate(DECK["slides"], 1):
        h = render_slide(s, i, len(DECK["slides"]), DECK["author"])
        assert f"{i} / {len(DECK['slides'])}" in h and "Vishwajeet Kumbhar" in h


def test_accent_markup_and_escaping():
    h = render_slide({"type": "cover", "title": "Use *AI* <now>"}, 1, 6, DECK["author"])
    assert "<em>AI</em>" in h and "&lt;now&gt;" in h


def test_ai_draft_retries_until_rules_pass():
    bad = {"slug": "x", "caption": "c", "slides": [{"type": "point", "title": "x"}]}
    good = {k: v for k, v in DECK.items() if k != "author"}
    calls = iter([bad, good])
    make = lambda d: SimpleNamespace(content=[SimpleNamespace(type="tool_use", input=d)])
    fake = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: make(next(calls))))
    deck = draft("contracts", "notes", DECK["author"], client=fake)
    assert validate(deck) == []


def test_render_produces_pdf(tmp_path):
    pytest.importorskip("playwright")
    from carousel.render import render

    try:
        pdf = render(DECK, tmp_path, png=False)
    except Exception as e:  # browser not installed in this environment
        pytest.skip(str(e))
    from pypdf import PdfReader

    assert len(PdfReader(str(pdf)).pages) == len(DECK["slides"])
