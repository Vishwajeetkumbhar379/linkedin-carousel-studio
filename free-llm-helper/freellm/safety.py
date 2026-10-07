"""Guards for anything that leaves the machine: a folder allowlist, blocked secret files, and secret scrubbing.

Every byte sent to a free provider passes through `scrub()`, and every local path through `check_path()`.
"""
from __future__ import annotations

import fnmatch
import ipaddress
import os
import re
import socket
import urllib.parse
from pathlib import Path

from .providers import PROVIDERS


class Blocked(PermissionError):
    pass


# Files that are never read, whatever the allowlist says.
SECRET_FILES = [
    ".env", ".env.*", "*.env", ".envrc", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore", "id_rsa*",
    "id_ed25519*", "id_ecdsa*", "*.ppk", ".netrc", ".npmrc", ".pypirc", ".git-credentials", ".htpasswd",
    "credentials", "credentials.*", "*secret*", "*secrets*", "*.tfstate", "*.tfstate.*", "*.kdbx", "service-account*.json",
]
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache",
             "dist", "build", ".next", ".terraform", ".aws", ".ssh", ".gnupg", ".kube", ".docker"}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"\b(?:sk-ant-|sk-or-v1-|sk-proj-|sk-)[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b(?:gsk_|nvapi-|xai-|hf_|glpat-|npm_|pypi-)[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abposr]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),  # JWTs
    re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:[^\s@/]{3,}@", re.I),  # credentials inside URLs
    # key = "value" style assignments for anything named like a secret
    re.compile(r"(?i)((?:api[_-]?key|secret|token|passw(?:or)?d|pwd|auth|bearer|private[_-]?key|access[_-]?key)"
               r"[\"']?\s*[:=]\s*[\"']?)([^\s\"'`,;]{8,})"),
    re.compile(r"(?i)(authorization:\s*(?:bearer|basic)\s+)([A-Za-z0-9._~+/=\-]{8,})"),
]
REDACTED = "[REDACTED]"


def _known_secret_values() -> list[str]:
    """Values of env vars that hold keys (provider keys plus anything named *KEY/*TOKEN/*SECRET/*PASSWORD)."""
    names = {k for p in PROVIDERS.values() for k in p["keys"]}
    names |= {n for n in os.environ if re.search(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD)$", n)}
    vals = {os.environ[n] for n in names if len(os.environ.get(n, "")) >= 12}
    return sorted(vals, key=len, reverse=True)


def scrub(text: str) -> tuple[str, int]:
    """Replace anything that looks like a credential. Returns (clean_text, number_of_redactions)."""
    count = 0
    for v in _known_secret_values():
        if v in text:
            count += text.count(v)
            text = text.replace(v, REDACTED)
    for pat in SECRET_PATTERNS:
        def sub(m):
            nonlocal count
            count += 1
            return (m.group(1) + REDACTED) if m.re.groups >= 2 else REDACTED
        text = pat.sub(sub, text)
    return text, count


def allowed_dirs() -> list[Path]:
    raw = os.environ.get("FREELLM_ALLOW_DIRS", "")
    return [Path(os.path.expanduser(d)).resolve() for d in re.split(r"[,:;]", raw) if d.strip()]


def is_secret_file(path: Path) -> bool:
    name = path.name.lower()
    return any(fnmatch.fnmatch(name, pat) for pat in SECRET_FILES)


def check_path(path: str | Path) -> Path:
    """Resolve symlinks and refuse anything outside FREELLM_ALLOW_DIRS, inside a skipped dir, or a secret file."""
    dirs = allowed_dirs()
    if not dirs:
        raise Blocked("No folders allowed yet. Set FREELLM_ALLOW_DIRS to the folders the free helper may read, "
                      "e.g. FREELLM_ALLOW_DIRS=~/projects/my-app:~/notes")
    real = Path(os.path.expanduser(str(path))).resolve()
    if not any(real == d or d in real.parents for d in dirs):
        raise Blocked(f"{path} is outside FREELLM_ALLOW_DIRS ({', '.join(map(str, dirs))})")
    if any(part in SKIP_DIRS for part in real.parts):
        raise Blocked(f"{path} is inside a folder that is never sent ({', '.join(sorted(SKIP_DIRS & set(real.parts)))})")
    if real.is_file() and is_secret_file(real):
        raise Blocked(f"{path} looks like a secrets file and is never sent")
    return real


def check_url(url: str) -> str:
    """Only public http(s) URLs: no localhost, private ranges or metadata endpoints."""
    u = urllib.parse.urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise Blocked(f"Only http(s) URLs are allowed: {url}")
    try:
        infos = socket.getaddrinfo(u.hostname, None)
    except socket.gaierror:
        return url  # let the fetch report it; behind a proxy DNS may not resolve locally
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise Blocked(f"{url} points at a private address and is never fetched")
    return url
