import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import context_graph as g  # noqa: E402


def test_scrub_hides_credentials():
    text = 'GROQ_API_KEY="gsk_abcdefghijklmnopqrstuvwx" and api_key: abcdefghijklmnop1234'
    out = g.scrub(text)
    assert "gsk_" not in out and "abcdefghijklmnop1234" not in out


def test_edges_imports_paths_and_wikilinks():
    files = [
        {"id": "e:scripts/weekly.py", "source": "e", "rel": "scripts/weekly.py", "ext": ".py", "text": "import llm\n# see docs/runbook.md"},
        {"id": "e:scripts/llm.py", "source": "e", "rel": "scripts/llm.py", "ext": ".py", "text": ""},
        {"id": "e:docs/runbook.md", "source": "e", "rel": "docs/runbook.md", "ext": ".md", "text": ""},
        {"id": "m:a.md", "source": "m", "rel": "a.md", "ext": ".md", "text": "See [[b]]"},
        {"id": "m:b.md", "source": "m", "rel": "b.md", "ext": ".md", "text": ""},
    ]
    got = {(e["source"], e["target"], e["relation"]) for e in g.edges_for(files)}
    assert ("e:scripts/weekly.py", "e:scripts/llm.py", "imports") in got
    assert ("e:scripts/weekly.py", "e:docs/runbook.md", "references") in got
    assert ("m:a.md", "m:b.md", "links") in got
