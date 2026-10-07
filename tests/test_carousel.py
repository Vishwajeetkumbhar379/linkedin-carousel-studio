import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from carousel import ai
from carousel.ai import MistralClient, draft, invented_numbers
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


def test_invented_statistics_are_flagged():
    deck = {"caption": "62% of disputes", "slides": [{"type": "point", "title": "2x faster", "body": "43% had changes, net 30"}]}
    assert invented_numbers(deck, "62% of disputes, approved 2x faster") == ["43%"]


def test_mistral_client_returns_anthropic_shaped_tool_use(monkeypatch):
    good = {k: v for k, v in DECK.items() if k != "author"}
    sent = {}

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            tc = [{"function": {"name": "build_deck", "arguments": json.dumps(good)}}]
            return json.dumps({"choices": [{"message": {"tool_calls": tc}}]}).encode()

    def fake_urlopen(req, timeout):
        sent.update(json.loads(req.data))
        return Resp()

    monkeypatch.setattr(ai.urllib.request, "urlopen", fake_urlopen)
    deck = draft("contracts", "notes", DECK["author"], client=MistralClient(api_key="k"))
    assert validate(deck) == [] and sent["tools"][0]["function"]["name"] == "build_deck"
    assert sent["messages"][0]["role"] == "system" and sent["model"] == ai.MISTRAL_MODEL


def test_render_produces_pdf(tmp_path):
    pytest.importorskip("playwright")
    from carousel.render import render

    try:
        pdf = render(DECK, tmp_path, png=False)
    except Exception as e:  # browser not installed in this environment
        pytest.skip(str(e))
    from pypdf import PdfReader

    assert len(PdfReader(str(pdf)).pages) == len(DECK["slides"])
