"""Inside AI, EP 3 to 9 (YouTube Shorts, @Buildwithvish). EP 1 (hit send) and EP 2 (the T in GPT) passed 1,000 views each on a
new channel (28 Oct), so the formula stays: one everyday AI moment, a hook that turns on "but", short lines, one surprising number,
a loop question at the end. Voice: ElevenLabs George, like EP 1. Engine: templates/video/series3 in faceless mode, dark chapters.
Facts are checked in facts.txt. Writes scripts.json and beats.json, and checks every cue phrase is in its script."""
import json, re
from pathlib import Path

H = Path(__file__).resolve().parent
norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))
D1, D2, D3, GOLD = "#0D0F14", "#10131B", "#15120C", "#E7A15A"
MOOD = "dark cinematic tech, deep pulsing synth bass, curious ticking percussion, clean modern, builds to a lift"

EP = {
 "a3": dict(ep=3, hook="Your message goes<br><i>143,000 km.</i>", hookEnd="flying at", em=["up", "Starlink", "reverse"],
  script="You ask ChatGPT a question on a plane. Your message is about to travel further than your flight. A lot further. "
         "You're flying at 900 kilometres an hour. But your message doesn't go to the ground. It goes up. "
         "36,000 kilometres up, to a satellite parked over the equator. Then all the way back down to a ground station, and into a data centre. "
         "The answer makes the same trip in reverse. That's about 143,000 kilometres. Three and a half times around the Earth. In about half a second. "
         "Unless your airline has Starlink. Then the satellite is only 550 kilometres up. "
         "So next time the wifi feels slow, remember where your message just went. What's the strangest thing you've asked AI on a flight?",
  chapters=[["You ask ChatGPT", D1, "the question"], ["It goes up", D2, "the trip"], ["That's about", D1, "the maths"], ["Unless your airline", D3, "the twist"]],
  ticker={"label": "KM TRAVELLED", "keys": [["You ask ChatGPT", 0], ["satellite parked", 36000], ["back down to", 72000], ["same trip in reverse", 143000]]},
  heroes=[{"kind": "globe", "at": "flying at", "until": "That's about", "keys": [["flying at", 46, 5, 8.6], ["satellite parked", 18, 0, 9.4], ["same trip in reverse", 35, -30, 9.0]],
           "pins": [{"lat": 48.0, "lon": 6.0, "label": "You, 11 km up", "at": "flying at"}, {"lat": 0.0, "lon": 0.0, "label": "Satellite, 36,000 km up", "at": "satellite parked"},
                    {"lat": 40.4, "lon": -3.7, "label": "Ground station", "at": "back down to"}, {"lat": 39.0, "lon": -77.5, "label": "Data centre", "at": "into a data centre"}],
           "routes": [{"a": [48.0, 6.0], "b": [0.0, 0.0], "at": "It goes up", "dur": 1.2, "lift": 0.9, "color": GOLD},
                      {"a": [0.0, 0.0], "b": [40.4, -3.7], "at": "back down to", "dur": 1.1, "lift": 0.9, "color": GOLD},
                      {"a": [40.4, -3.7], "b": [39.0, -77.5], "at": "into a data centre", "dur": 1.2, "lift": 0.2}]}],
  els=[{"type": "dlg", "at": "You ask ChatGPT", "title": "Wi-Fi on board", "body": "Connected · 35,000 ft", "btns": ["Ask ChatGPT"], "pick": 0, "press": "travel further"},
       {"type": "counter", "at": "That's about", "label": "Round trip", "from": 0, "to": 143000, "suffix": " km", "w": 980},
       {"type": "card", "at": "around the Earth", "label": "That's", "title": "3.5× around<br>the Earth", "w": 640},
       {"type": "stamp", "at": "half a second", "text": "0.5 SECONDS"},
       {"type": "card", "at": "Unless your airline", "label": "With Starlink", "title": "550 km up", "w": 600},
       {"type": "quote", "at": "next time the wifi", "text": "Remember where your message <i>just went.</i>"}]),
 "a4": dict(ep=4, hook="AI couldn't count<br><i>to three.</i>", hookEnd="Here's why", em=["tokens", "three", "count"],
  script="Ask an older AI how many R's are in strawberry, and it would say two. It could write you a poem in seconds. But it couldn't count three letters. "
         "Here's why. AI doesn't read letters. It reads tokens. Chunks of text, like str, aw and berry. "
         "To the model, strawberry is three puzzle pieces, not ten letters. So counting the R's is like counting the bricks inside a box you're not allowed to open. "
         "Newer models fixed it by thinking first, spelling the word out letter by letter. Which is exactly what you'd tell a kid to do. "
         "So how many R's are in strawberry? Be honest. Did you just count?",
  chapters=[["Ask an older AI", D1, "the fail"], ["Here's why", D2, "the reason"], ["Newer models", D1, "the fix"], ["So how many", D3, "the test"]],
  ticker={"label": "PIECES IT SEES", "keys": [["Ask an older AI", 10], ["It reads tokens", 3]]},
  heroes=[{"kind": "cards", "at": "Chunks of text", "until": "So counting the", "faces": [
      {"label": "Token 1", "title": "str", "size": 170, "at": "like str"}, {"label": "Token 2", "title": "aw", "size": 170, "at": "aw and"},
      {"label": "Token 3", "title": "berry", "size": 150, "color": "#D9473A", "at": "and berry"}]}],
  els=[{"type": "dlg", "at": "Ask an older AI", "title": "How many R's in strawberry?", "body": "There are 2 R's in strawberry.", "btns": ["Thanks!"], "pick": 0, "press": "write you a poem"},
       {"type": "stamp", "at": "couldn't count", "text": "IT'S THREE"},
       {"type": "tags", "at": "It reads tokens", "w": 900, "gap": 0.05, "items": ["s", "t", "r", "a", "w", "b", "e", "r", "r", "y"]},
       {"type": "card", "at": "three puzzle pieces", "label": "To the model", "title": "3 pieces,<br>not 10 letters", "w": 680},
       {"type": "doc", "at": "Newer models", "label": "Thinking first", "w": 780, "lines": [{"t": "strawberry", "nw": "s t R a w b e R R y", "at": "spelling the word"}, {"t": "How many R's?", "nw": "3", "at": "letter by letter"}]},
       {"type": "quote", "at": "Did you just count", "text": "Be honest. <i>Did you just count?</i>"}]),
 "a5": dict(ep=5, hook="Same question.<br><i>Two answers.</i>", hookEnd="For every next word", em=["dice", "temperature", "underdog"],
  script="Ask ChatGPT the exact same question twice, and you'll get two different answers. That's not a bug. It's on purpose. "
         "For every next word, the model has a list of options, each with a probability. The sky is blue, maybe ninety percent. Clear, six percent. Falling, one percent. "
         "If it always picked the top word, it would sound like a robot reading a manual. So it rolls weighted dice. Usually the favourite wins. Sometimes the underdog does. "
         "Developers even get a dial for it, called temperature. Turn it down, it plays safe. Turn it up, it gets creative. Turn it all the way up, and it stops making sense. "
         "So every answer you've ever had was one roll of the dice. Try it. Ask the same thing twice, and tell me which answer won.",
  chapters=[["Ask ChatGPT the exact", D1, "the mystery"], ["For every next word", D2, "the odds"], ["Developers even get", D1, "the dial"], ["So every answer", D3, "the truth"]],
  ticker={"label": "TEMPERATURE", "keys": [["Ask ChatGPT the exact", 1], ["Turn it down", 0], ["Turn it up", 1], ["all the way up", 2]]},
  heroes=[{"kind": "cards", "at": "exact same question", "until": "For every next word", "faces": [
      {"label": "Ask #1", "title": "“Blue.”", "size": 120, "at": "exact same question"}, {"label": "Ask #2", "title": "“Teal.”", "size": 120, "color": GOLD, "at": "two different answers"}]}],
  els=[{"type": "stamp", "at": "That's not a bug", "text": "ON PURPOSE"},
       {"type": "list", "at": "The sky is", "label": "The sky is… (example odds)", "w": 760, "rows": [{"t": "blue · 90%", "at": "The sky is"}, {"t": "clear · 6%", "at": "Clear six"}, {"t": "falling · 1%", "at": "Falling one", "x": True}]},
       {"type": "card", "at": "rolls weighted dice", "label": "So it", "title": "Rolls weighted<br>dice", "w": 620},
       {"type": "card", "at": "Sometimes the underdog", "label": "Sometimes", "title": "The underdog<br>wins", "w": 620},
       {"type": "bar", "at": "called temperature", "fill": "all the way up", "label": "Temperature", "n": 10, "unit": "", "w": 680},
       {"type": "quote", "at": "one roll of the dice", "text": "Every answer is <i>one roll of the dice.</i>"}]),
 "a6": dict(ep=6, hook="1,700 years<br><i>of reading.</i>", hookEnd="Sounds boring", em=["patterns", "Google", "pre-trained"],
  script="Last time, we found out the T in GPT came from Google. Now, the P. P stands for pre-trained. Sounds boring. It isn't. "
         "Before you ever typed a word, the model had already read a huge chunk of the internet. GPT-3 alone was trained on about 300 billion tokens. "
         "Reading that nonstop, day and night, would take you around 1,700 years. But here's the twist. It didn't memorise it. It learned patterns. "
         "How sentences usually go, and what usually comes next. That's the P. Everything it learned before it met you. "
         "And the G? That's next time. Which letter would you have guessed was the most important?",
  chapters=[["Last time", D1, "G · P · T"], ["Before you ever typed", D2, "the reading"], ["here's the twist", D1, "the twist"], ["And the G", D3, "next time"]],
  ticker={"label": "LETTERS DECODED", "keys": [["Last time", 1], ["That's the P", 2]]},
  heroes=[{"kind": "cards", "at": "Last time", "until": "Sounds boring", "faces": [
      {"label": "Letter 1", "title": "G", "size": 260, "at": "Last time"}, {"label": "Letter 2", "title": "P", "size": 260, "color": GOLD, "at": "Now the P"},
      {"label": "Letter 3", "title": "T", "size": 260, "at": "came from Google"}]}],
  els=[{"type": "card", "at": "P stands for", "label": "P stands for", "title": "Pre-trained", "w": 640},
       {"type": "counter", "at": "alone was trained", "label": "GPT-3 read", "from": 0, "to": 300, "suffix": " billion tokens", "w": 840},
       {"type": "counter", "at": "Reading that nonstop", "label": "You, reading nonstop", "from": 0, "to": 1700, "suffix": " years", "w": 780},
       {"type": "list", "at": "here's the twist", "label": "What it did", "w": 720, "rows": [{"t": "Memorised it", "at": "didn't memorise", "x": True}, {"t": "Learned patterns", "at": "It learned patterns"}]},
       {"type": "quote", "at": "That's the P", "text": "Everything it learned <i>before it met you.</i>"},
       {"type": "stamp", "at": "And the G", "text": "G: NEXT TIME"}]),
 "a7": dict(ep=7, hook="Six court cases.<br><i>None existed.</i>", hookEnd="He even asked", em=["hallucination", "predicts", "yes"],
  script="In 2023, a lawyer in New York handed a judge six court cases. None of them existed. ChatGPT had made them up. The names, the dates, the quotes. All of it. "
         "He even asked it if they were real. It said yes. But it wasn't lying. Lying means you know the truth. "
         "AI doesn't look things up. It predicts what a good answer usually looks like. And a fake case can look exactly like a real one. That's called a hallucination. "
         "The lawyers were fined 5,000 dollars. So use it to draft. Never to check itself. Has AI ever told you something wrong, with total confidence?",
  chapters=[["a lawyer in New York", D1, "the case"], ["But it wasn't lying", D2, "the reason"], ["The lawyers were fined", D1, "the cost"], ["So use it", D3, "the rule"]],
  ticker={"label": "REAL CASES", "keys": [["a lawyer in New York", 6], ["None of them existed", 0]]},
  heroes=[{"kind": "cards", "at": "a lawyer in New York", "until": "He even asked", "faces": [
      {"label": "Case 1 of 6", "title": "Varghese v.\nChina Southern", "size": 70, "at": "a lawyer in New York"},
      {"label": "Case 2 of 6", "title": "Shaboon v.\nEgyptair", "size": 76, "at": "six court cases"},
      {"label": "Case 3 of 6", "title": "Petersen v.\nIran Air", "size": 76, "color": "#D9473A", "at": "None of them existed"}]}],
  els=[{"type": "stamp", "at": "had made them up", "text": "DOESN'T EXIST"},
       {"type": "dlg", "at": "asked it if", "title": "Are these cases real?", "body": "Yes, they are real cases.", "btns": ["OK"], "pick": 0, "press": "It said yes"},
       {"type": "card", "at": "It predicts", "label": "It predicts", "title": "What an answer<br>usually looks like", "w": 720},
       {"type": "card", "at": "called a hallucination", "label": "This is called", "title": "A hallucination", "w": 660},
       {"type": "counter", "at": "were fined", "label": "The fine", "from": 0, "to": 5000, "suffix": " dollars", "w": 640},
       {"type": "list", "at": "use it to draft", "label": "The rule", "w": 740, "rows": [{"t": "Use it to draft", "at": "use it to draft"}, {"t": "Let it check itself", "at": "Never to check", "x": True}]}]),
 "a8": dict(ep=8, hook="“Thinking…”<br><i>is a hidden essay.</i>", hookEnd="Reasoning models", em=["hidden", "volume", "essay"],
  script="When ChatGPT says thinking, it's actually writing. You just can't see it. Reasoning models write a long, private draft before they answer you. "
         "They try an approach, check it, throw it away, and try again. Sometimes thousands of words, for a one line answer. "
         "And here's the part nobody tells you. Developers pay for every one of those hidden words. That's why hard questions take longer, and cost more. "
         "It's not thinking like you do. It's thinking out loud, with the volume off. So next time you see thinking, you'll know. Someone's writing an essay. "
         "What's the longest you've watched it think?",
  chapters=[["When ChatGPT says", D1, "the screen"], ["Reasoning models", D2, "the draft"], ["nobody tells you", D1, "the bill"], ["It's not thinking", D3, "the truth"]],
  ticker={"label": "DRAFTS", "keys": [["When ChatGPT says", 0], ["try an approach", 1], ["try again", 2]]},
  heroes=[{"kind": "cards", "at": "try an approach", "until": "Sometimes thousands", "faces": [
      {"label": "Draft 1", "title": "Approach A", "size": 96, "at": "try an approach"}, {"label": "Check", "title": "Wrong.", "size": 120, "color": "#D9473A", "at": "throw it away"},
      {"label": "Draft 2", "title": "Approach B", "size": 96, "color": GOLD, "at": "try again"}]}],
  els=[{"type": "wave", "at": "says thinking", "label": "ChatGPT", "title": "Thinking…", "until": "Reasoning models", "w": 720},
       {"type": "card", "at": "one line answer", "label": "You see", "title": "One line", "w": 520},
       {"type": "stamp", "at": "Developers pay", "text": "BILLED"},
       {"type": "card", "at": "hard questions", "label": "Hard questions", "title": "Take longer.<br>Cost more.", "w": 640},
       {"type": "quote", "at": "thinking out loud", "text": "Thinking out loud, <i>with the volume off.</i>"}]),
 "a9": dict(ep=9, hook="It re-reads<br><i>your whole chat.</i>", hookEnd="no memory between", em=["fifty", "forgetting", "fresh"],
  script="Every time you send ChatGPT a message, it re-reads your entire chat. From the very first word. The model has no memory between messages. None. "
         "So the app quietly sends the whole conversation again, every single time. Message one, it reads one. Message fifty, it reads all fifty. "
         "That's why really long chats get slower. And at some point, it simply doesn't fit. Every model has a limit, called the context window. "
         "So the oldest parts get trimmed, and it starts forgetting how your chat began. That's why a fresh chat often gives better answers. "
         "How long is your longest chat right now?",
  chapters=[["Every time you send", D1, "the secret"], ["So the app", D2, "the resend"], ["And at some point", D1, "the limit"], ["That's why a fresh", D3, "the fix"]],
  ticker={"label": "MESSAGES RE-READ", "keys": [["Every time you send", 1], ["Message one", 1], ["Message fifty", 50]]},
  heroes=[{"kind": "cards", "at": "quietly sends", "until": "long chats get slower", "faces": [
      {"label": "Send 1", "title": "Reads 1", "size": 110, "at": "Message one"}, {"label": "Send 2", "title": "Reads 2", "size": 110, "at": "it reads one"},
      {"label": "Send 50", "title": "Reads 50", "size": 110, "color": GOLD, "at": "Message fifty"}]}],
  els=[{"type": "stamp", "at": "None", "text": "NO MEMORY"},
       {"type": "counter", "at": "reads all fifty", "label": "Messages it re-reads", "from": 1, "to": 50, "suffix": "", "w": 660},
       {"type": "bar", "at": "called the context window", "fill": "oldest parts", "label": "Context window", "n": 10, "unit": "/ 10 full", "w": 700},
       {"type": "stamp", "at": "starts forgetting", "text": "FORGOTTEN"},
       {"type": "card", "at": "a fresh chat", "label": "The fix", "title": "Start a<br>fresh chat", "w": 600}]),
}

scripts, beats, bad = {}, {}, []
for k, e in EP.items():
    words = [norm(w) for w in e["script"].split()]
    def has(ph):
        q = [norm(x) for x in ph.split("#")[0].split()]
        return any(words[i:i + len(q)] == q for i in range(len(words)))
    def walk(o):
        if isinstance(o, dict):
            for f, v in o.items():
                if f in ("at", "out", "fill", "until", "press") and isinstance(v, str) and not has(v): bad.append((k, v))
                walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(e["els"]); walk(e["heroes"])
    for row in e["chapters"] + e["ticker"]["keys"]:
        if not has(row[0]): bad.append((k, row[0]))
    if not has(e["hookEnd"]): bad.append((k, e["hookEnd"]))
    for h in e["heroes"]: h["dark"] = True  # the 3D shots in the dark studio, like the rest of the series
    scripts[k] = e["script"]
    beats[k] = {"ep": e["ep"], "mood": MOOD, "hook": e["hook"], "hookEnd": e["hookEnd"], "em": e["em"], "chapters": e["chapters"], "ticker": e["ticker"],
                "mascot": [], "react": [], "heroes": e["heroes"], "els": e["els"], "template": "series3", "series": "INSIDE AI", "faceless": True}
if bad: raise SystemExit(f"cue phrases not in the script: {bad}")
(H / "scripts.json").write_text(json.dumps(scripts, indent=1, ensure_ascii=False))
(H / "beats.json").write_text(json.dumps(beats, indent=1, ensure_ascii=False))
print("ok", {k: len(v.split()) for k, v in scripts.items()})
