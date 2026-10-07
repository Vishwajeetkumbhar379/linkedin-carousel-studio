import io
import json

import pytest

from freellm import mcp_server, tasks
from freellm.providers import Chain, LLMError, Provider
from freellm.safety import Blocked, check_path, check_url, scrub


class Fake(Provider):
    def __init__(self, name, replies=None, fail=False, max_chars=80_000):
        super().__init__(name, "http://x", "k", "m", max_chars)
        self.replies, self.fail, self.seen = list(replies or []), fail, []

    def chat(self, system, user, max_tokens=2000):
        self.seen.append(user)
        if self.fail:
            raise LLMError(f"{self.name} 429")
        return self.replies.pop(0) if self.replies else "summary"


@pytest.fixture
def allow(tmp_path, monkeypatch):
    monkeypatch.setenv("FREELLM_ALLOW_DIRS", str(tmp_path / "ok"))
    monkeypatch.setenv("FREELLM_LOG", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(tasks, "LOG", tmp_path / "log.jsonl")
    (tmp_path / "ok").mkdir()
    return tmp_path


def test_scrub_removes_common_secrets(monkeypatch):
    monkeypatch.setenv("MY_SERVICE_TOKEN", "super-secret-value-123456")
    text = ("key = 'sk-ant-api03-abcdefghijklmnopqrstuv'\nGROQ=gsk_abcdefghijklmnopqrstuvwxyz\n"
            "password: hunter2hunter2\nurl=postgres://admin:pa55word@db:5432/x\n"
            "Authorization: Bearer abc.def.ghijklmnop\nAKIAABCDEFGHIJKLMNOP\nuses super-secret-value-123456\n"
            "-----BEGIN RSA PRIVATE KEY-----\nMIIE\n-----END RSA PRIVATE KEY-----\nnormal text stays")
    clean, n = scrub(text)
    for leak in ("sk-ant-api03", "gsk_abc", "hunter2", "pa55word", "abc.def.ghij", "AKIAABCD", "super-secret", "MIIE"):
        assert leak not in clean, leak
    assert "normal text stays" in clean and n >= 8


def test_allowlist_is_required_and_enforced(allow, monkeypatch):
    (allow / "ok" / "a.py").write_text("print(1)")
    (allow / "outside.py").write_text("x")
    (allow / "ok" / ".env").write_text("A=1")
    (allow / "ok" / "link").symlink_to(allow / "outside.py")
    assert check_path(allow / "ok" / "a.py")
    for bad in (allow / "outside.py", allow / "ok" / ".env", allow / "ok" / "link", allow / "ok" / ".." / "outside.py"):
        with pytest.raises(Blocked):
            check_path(bad)
    monkeypatch.delenv("FREELLM_ALLOW_DIRS")
    with pytest.raises(Blocked, match="No folders allowed"):
        check_path(allow / "ok" / "a.py")


def test_private_urls_blocked():
    for url in ("http://127.0.0.1:8080/", "http://169.254.169.254/latest/meta-data", "file:///etc/passwd"):
        with pytest.raises(Blocked):
            check_url(url)


def test_gather_skips_secrets_and_scrubs(allow):
    ok = allow / "ok"
    (ok / "app.py").write_text("API_KEY = 'nvapi-abcdefghijklmnopqrstuvwxyz'\ndef main(): pass\n")
    (ok / "secrets.yaml").write_text("db: hunter2")
    (ok / ".git").mkdir()
    (ok / ".git" / "config").write_text("token")
    (ok / "img.bin").write_bytes(b"\0\1\2")
    b = tasks.gather([str(ok), str(allow / "outside.txt")])
    assert "def main" in b.text and "nvapi-" not in b.text and "hunter2" not in b.text and ".git" not in b.text
    assert b.redactions >= 1 and any("secrets" in s for s in b.skipped)


def test_chunks_respect_size():
    text = "\n\n".join(f"===== f{i} =====\n" + "x" * 900 for i in range(20)) + "\n\n" + "y" * 5000
    parts = tasks.chunks(text, 2000)
    assert all(len(p) <= 2000 for p in parts) and sum(p.count("x") for p in parts) == 18000


def test_chain_falls_back_and_map_reduces(allow):
    (allow / "ok" / "big.txt").write_text("\n\n".join("line %d " % i * 20 for i in range(400)))
    broken, good = Fake("groq", fail=True, max_chars=5000), Fake("nvidia", max_chars=5000)
    out = tasks.summarize([str(allow / "ok")], chain=Chain([broken, good]))
    assert out.startswith("summary") and "via nvidia/m" in out and "tokens kept out of Claude" in out
    assert len(good.seen) > 2  # several map calls plus a reduce
    assert "1 calls" in tasks.stats()
    with pytest.raises(LLMError):
        Chain([Fake("a", fail=True)]).chat("s", "u")


def test_mcp_protocol(allow):
    reqs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "free_summarize", "arguments": {"sources": [str(allow / "nope")]}}}]
    out = io.StringIO()
    mcp_server.serve(io.StringIO("\n".join(json.dumps(r) for r in reqs) + "\n"), out)
    replies = [json.loads(l) for l in out.getvalue().splitlines()]
    assert [r["id"] for r in replies] == [1, 2, 3]
    assert replies[0]["result"]["serverInfo"]["name"] == "free-llm-helper"
    assert {t["name"] for t in replies[1]["result"]["tools"]} >= {"free_summarize", "free_ask", "free_find"}
    assert "Nothing could be read" in replies[2]["result"]["content"][0]["text"] or replies[2]["result"].get("isError")
