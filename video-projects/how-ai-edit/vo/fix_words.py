"""Fix the few words Whisper mishears in the voiceover, so captions and cue() read what Vish says.

    python3 vo/fix_words.py   (after align.py)
"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "src" / "words.json"
w = json.loads(P.read_text())
SAME = {"rewatch": "rewind", "photograph": "photographed", "prompt": "prompts", "Prompt": "prompts"}
out, i = [], 0
while i < len(w):
    t = w[i]["w"].strip(",.?!").lower()
    if t == "come" and i + 2 < len(w) and w[i + 1]["w"].strip(",.").lower() == "and" and w[i + 2]["w"].strip(",.").lower() == "edit":
        out += [{"w": "Comment", "s": w[i]["s"], "e": w[i + 1]["e"]}, {**w[i + 2], "w": "EDIT"}]; i += 3; continue
    if t == "take" and i + 1 < len(w) and w[i + 1]["w"].strip(",.") == "12":
        out.append({**w[i], "w": "took"}); i += 1; continue
    out.append({**w[i], "w": SAME.get(t, w[i]["w"]) if t in SAME else w[i]["w"]}); i += 1
P.write_text(json.dumps(out, indent=0))
print(" ".join(x["w"] for x in out))
