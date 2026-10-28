"""Nobody Tells You (7 episodes, week of 30 Oct): scripts.json + beats.json for scripts/canvas_reel.py (template "series").
    python build.py                 -> scripts.json, beats.json
    python ../../scripts/canvas_reel.py . e1 --stills 1,6,12   (storyboard frames; stand-in timing until e1_words.json exists)
Facts only from brand-profile.md. Every "at" is a phrase from the script ("word#2" = the second time it is said).
"""
import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = "video-projects/ntu/assets/"
SERIES = "NOBODY TELLS YOU"


def merc(lat, lon, z, x0, y0):
    """Lat/lon to pixel on a stitched OpenStreetMap tile image (zoom z, top-left tile x0, y0)."""
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return [round((x - x0) * 256, 1), round((y - y0) * 256, 1)]


SA = lambda lat, lon: merc(lat, lon, 5, 21, 13)  # noqa: E731  map_south_asia 768 x 768
EU = lambda lat, lon: merc(lat, lon, 4, 8, 5)  # noqa: E731  map_india_europe 1024 x 768
WD = lambda lat, lon: [merc(lat, lon, 2, 0, 0)[0], merc(lat, lon, 2, 0, 0)[1] - 250]  # noqa: E731  map_world_mid 1024 x 600
INDIA, GERMANY, LANKA = (21.0, 78.0), (51.0, 10.0), (7.9, 80.7)


def code_lines():
    """The real code that draws these reels (templates/video/series/series.html), lightly coloured."""
    src = (HERE.parents[1] / "templates/video/series/series.html").read_text().split("<script>")[1].splitlines()
    out = []
    for ln in [l for l in src if l.strip()][4:46]:
        t = html.escape(ln[:58])
        for k in ("const ", "function ", "return ", "if ", "=> "):
            t = t.replace(k, f'<span class="k">{k}</span>')
        out.append(t if not ln.strip().startswith("//") else f'<span class="c">{t}</span>')
    return out


S = {}
B = {}

# ---------------------------------------------------------------- EP 1 (Fri 30 Oct): no editor made this reel (EDIT)
S["e1"] = ("[excited] Nobody tells you this. You don't need an editor anymore. This reel? No editor touched it. No video AI either. "
           "Claude made it. In code. Let me show you. [curious] Step one. I write the script, like I'm talking to a friend. "
           "Step two. My voice clone reads it. That's ElevenLabs, trained on my own recordings. Step three. Claude listens back "
           "and times every single word. Step four. It builds every card, every camera move, and this guy, around those words. "
           "Step five. It renders the video. Frame by frame. The total cost? My Claude subscription. [serious] And here's the part "
           "nobody tells you. I'm a marketer, not an engineer. I don't write the code. I tell Claude what I want, and I say no "
           "until it's right. [warm] Comment EDIT, and I'll send you the prompts.")
B["e1"] = {"ep": 1, "mood": "upbeat playful tech, bright plucks, light hip hop beat, curious and clever",
  "hook": "You don't need<br><i>an editor</i> anymore.", "hookEnd": "This reel",
  "mascot": [["Nobody", "arms"], ["This reel", "point_left"], ["Claude made it", "explain"], ["Step one", "point_up"], ["Step two", "point_left"],
             ["Step three", "think"], ["Step four", "explain"], ["this guy", "wave"], ["Step five", "point_left"], ["total cost", "thumbs"],
             ["part nobody", "think"], ["marketer", "arms"], ["I tell Claude", "explain"], ["Comment EDIT", "point_left"], ["prompts", "wave"]],
  "react": [["No video AI", "wink", 1.2], ["this guy", "laugh", 1.4], ["say no", "skeptical", 1.3]],
  "els": [
    {"type": "card", "at": "No editor", "icon": "✂", "label": "Video editor", "title": "Not opened", "w": 720},
    {"type": "card", "at": "No video AI", "beside": True, "icon": "✦", "label": "Video AI", "title": "Not used", "w": 720},
    {"type": "stamp", "at": "either", "text": "NEITHER"},
    {"type": "code", "at": "Claude made it", "file": "series.html · written by Claude", "lines": code_lines(), "w": 940, "h": 1000,
     "scrollAt": "In code", "scrollDur": 3.2, "hl": [8, 9, 10], "hlAt": "Let me show you"},
    {"type": "chip", "at": "In code", "text": "Real code. This reel."},
    {"type": "card", "at": "Step one", "label": "Step 1 · The script", "title": "“Nobody tells you this.”", "sub": "Written like I'm talking to a friend.", "w": 860},
    {"type": "shot", "at": "Step two", "src": A + "elevenlabs.png", "url": "elevenlabs.io", "w": 940, "vh": 980,
     "scroll": [["Step two", 0], ["trained on", 0.05]], "cursor": [["voice clone", 0.55, 0.62], ["ElevenLabs", 0.5, 0.5, True]]},
    {"type": "wave", "at": "trained on", "beside": True, "label": "My voice clone", "title": "Reading the script", "until": "Step three", "w": 940},
    {"type": "tags", "at": "times every single word", "w": 900, "gap": 0.18,
     "items": ["Nobody <b style='color:#E7A15A'>0.2s</b>", "tells <b style='color:#E7A15A'>0.5s</b>", "you <b style='color:#E7A15A'>0.7s</b>",
               "this <b style='color:#E7A15A'>0.9s</b>", "You <b style='color:#E7A15A'>1.6s</b>", "don't <b style='color:#E7A15A'>1.8s</b>"]},
    {"type": "card", "at": "Step four", "label": "Step 4", "title": "Every card. Every camera move.", "w": 860, "reveal": "every camera move"},
    {"type": "counter", "at": "Step five", "label": "Frames rendered", "from": 0, "to": 1500, "until": "Frame by frame", "w": 760},
    {"type": "card", "at": "The total cost", "icon": "€", "label": "Total cost", "title": "My Claude subscription", "w": 860},
    {"type": "stamp", "at": "subscription", "text": "THAT'S IT", "color": "#2F6B3F"},
    {"type": "quote", "at": "I'm a marketer", "text": "Marketer,<br><i>not engineer.</i>"},
    {"type": "list", "at": "I don't write the code", "label": "How we work", "w": 880,
     "rows": [{"t": "Claude writes the code", "at": "I don't write the code"}, {"t": "I say what I want", "at": "what I want"},
              {"t": "I say no until it's right", "at": "say no"}]},
    {"type": "card", "at": "Comment EDIT", "label": "Comment", "title": "EDIT", "sub": "I'll send you the prompts.", "w": 760},
    {"type": "card", "at": "send you the prompts", "beside": True, "label": "Tomorrow · EP 2", "labelColor": "#D9473A", "title": "One meeting cost me six months", "w": 760},
  ]}

# ---------------------------------------------------------------- EP 2 (Sat 31 Oct): remote work can still trap you
S["e2"] = ("[serious] Nobody tells you this about remote work. It can still trap you. For four years, I worked remotely from India. "
           "And I travelled while I did it. Then I booked my next two flights. [frustrated] And an important meeting came up. "
           "So I cancelled both. Then more client work came in. And I was stuck. In a nine to five. For six months. For someone "
           "obsessed with travelling? That was hell. [calm] Here's what I learned the hard way. Remote isn't freedom when you're paid "
           "in a currency that doesn't stretch. And it isn't freedom when one meeting can call you back. When I'm not travelling, my "
           "life feels like autopilot. When I travel, I count every single day. [determined] So now I'm fixing both. Earn in euros. "
           "Build work that can't call me back. In December, I'm in Sri Lanka for a month. Would you have cancelled the flights?")
IN = SA(*INDIA)
B["e2"] = {"ep": 2, "mood": "reflective warm piano, soft pads, light drums enter halfway, hopeful turn at the end",
  "hook": "Remote work can<br><i>still trap you.</i>", "hookEnd": "For four years",
  "mascot": [["Nobody", "arms"], ["For four years", "point_left"], ["booked", "thumbs"], ["important meeting", "think"], ["stuck", "front"],
             ["That was hell", "arms"], ["learned the hard way", "explain"], ["Remote isn't", "point_left"], ["autopilot", "think"],
             ["fixing both", "thumbs"], ["December", "point_left"], ["Would you", "explain"]],
  "react": [["cancelled both", "concerned", 1.4], ["That was hell", "skeptical", 1.2], ["Sri Lanka", "pleased", 1.4]],
  "els": [
    {"type": "counter", "at": "For four years", "label": "Working remotely from India", "from": 0, "to": 4, "suffix": " years", "w": 780},
    {"type": "map", "at": "travelled", "src": A + "map_south_asia.png", "iw": 768, "ih": 768, "w": 900, "h": 856, "label": "India",
     "pins": [{"x": IN[0], "y": IN[1], "label": "Me, remote", "at": "travelled"}],
     "routes": [{"a": IN, "b": [740, 70], "at": "booked", "dur": 1.0, "cancel": "cancelled both"},
                {"a": IN, "b": [40, 120], "at": "two flights", "dur": 1.0, "curve": -0.3, "cancel": "cancelled both"}]},
    {"type": "card", "at": "important meeting", "beside": True, "label": "● Important meeting", "labelColor": "#D9473A", "title": "Tomorrow, 10:00", "w": 760, "anim": "right"},
    {"type": "stamp", "at": "cancelled both", "text": "BOTH CANCELLED"},
    {"type": "tags", "at": "more client work", "w": 900, "gap": 0.22, "items": ["Client work", "Client work", "Client work", "Client work"]},
    {"type": "bar", "at": "stuck", "fill": "six months", "label": "Office hours, nine to five", "n": 6, "unit": "months", "w": 780},
    {"type": "quote", "at": "That was hell", "text": "That was <i>hell.</i>"},
    {"type": "list", "at": "Remote isn't freedom", "label": "Remote isn't freedom when", "w": 900,
     "rows": [{"t": "Your currency doesn't stretch", "at": "paid in a currency", "x": True}, {"t": "One meeting can call you back", "at": "one meeting can", "x": True}]},
    {"type": "card", "at": "not travelling", "label": "Not travelling", "title": "Autopilot", "w": 760, "out": "When I travel"},
    {"type": "card", "at": "When I travel", "beside": True, "label": "Travelling", "labelColor": "#2F6B3F", "title": "I count every single day", "w": 760},
    {"type": "list", "at": "fixing both", "label": "So I'm fixing both", "w": 860,
     "rows": [{"t": "Earn in euros", "at": "Earn in euros"}, {"t": "Work that can't call me back", "at": "Build work"}]},
    {"type": "map", "at": "In December", "src": A + "map_india_europe.png", "iw": 1024, "ih": 768, "w": 940, "h": 668, "label": "December",
     "pins": [{"x": EU(*GERMANY)[0], "y": EU(*GERMANY)[1], "label": "Germany", "at": "In December"},
              {"x": EU(*LANKA)[0], "y": EU(*LANKA)[1], "label": "Sri Lanka", "at": "Sri Lanka"}],
     "routes": [{"a": EU(*GERMANY), "b": EU(*LANKA), "at": "I'm in Sri Lanka", "dur": 1.6, "color": "#E7A15A", "curve": -0.2}]},
    {"type": "shot", "at": "for a month", "frame": "photo", "src": A + "sigiriya.jpg", "w": 900, "vh": 600, "fit": "cover", "caption": "Sri Lanka, for a month", "credit": "Photo: Wikimedia Commons"},
    {"type": "card", "at": "Would you", "label": "Your turn", "title": "Would you have cancelled the flights?", "w": 820},
    {"type": "card", "at": "cancelled the flights", "beside": True, "label": "Tomorrow · EP 3", "labelColor": "#D9473A", "title": "Bali has a coach problem", "w": 820},
  ]}

# ---------------------------------------------------------------- EP 3 (Sun 1 Nov): Bali has a coach problem
S["e3"] = ("[mischievously] Nobody tells you this about Bali. Every next person is a coach. A business coach. A mindset coach. "
           "A coach for coaches. [serious] And I don't have a problem with coaches. I have a problem with careers that are valid "
           "for one year. Because here's how it goes. Everyone moves to the same island. Everyone sells the same course. To the same "
           "people. Who then move to the same island. [warmly] Don't get me wrong. Bali is beautiful. The people are lovely. My "
           "perfect Tuesday? An ocean swim, yoga, then three hours of work. Ideally, in Bali. [firm] But it gets repetitive fast, "
           "if you're not smart. I want a stable income, and the freedom to experiment. Different skills. Different countries. So "
           "here's my rule. Build the skill first. The location second. A skill travels with you. A trend doesn't. Agree, or disagree?")
B["e3"] = {"ep": 3, "mood": "playful tropical, light marimba and percussion, cheeky, sunny",
  "hook": "Bali has a<br><i>coach problem.</i>", "hookEnd": "Every next person",
  "mascot": [["Nobody", "arms"], ["Every next person", "point_left"], ["I don't have a problem", "explain"], ["Because here's how", "point_up"],
             ["Everyone moves", "point_left"], ["Don't get me wrong", "thumbs"], ["perfect Tuesday", "explain"], ["repetitive", "think"],
             ["stable income", "point_left"], ["my rule", "point_up"], ["A skill travels", "arms"], ["Agree", "explain"]],
  "react": [["coach for coaches", "laugh", 1.3], ["same island#2", "wink", 1.2], ["repetitive", "skeptical", 1.3]],
  "els": [
    {"type": "shot", "at": "Every next person", "frame": "photo", "src": A + "ubud.jpg", "w": 900, "vh": 620, "fit": "cover", "caption": "Bali", "credit": "Photo: Wikimedia Commons"},
    {"type": "tags", "at": "A business coach", "w": 900, "gap": 0.75, "items": ["Business coach", "Mindset coach", "Coach for coaches"]},
    {"type": "card", "at": "I don't have a problem", "label": "No problem with", "title": "Coaches", "w": 760},
    {"type": "card", "at": "careers that are", "beside": True, "label": "My problem", "labelColor": "#D9473A", "title": "Careers valid for one year", "w": 760},
    {"type": "list", "at": "Everyone moves", "label": "How it goes", "w": 900,
     "rows": [{"t": "Move to the same island", "at": "Everyone moves"}, {"t": "Sell the same course", "at": "Everyone sells"},
              {"t": "To the same people", "at": "To the same people"}, {"t": "Who move to the same island", "at": "Who then move"}]},
    {"type": "stamp", "at": "same island#2", "text": "↻ REPEAT"},
    {"type": "quote", "at": "Bali is beautiful", "text": "Bali is <i>beautiful.</i>"},
    {"type": "list", "at": "perfect Tuesday", "label": "My perfect Tuesday", "w": 860,
     "rows": [{"t": "Ocean swim", "at": "ocean swim"}, {"t": "Yoga", "at": "yoga"}, {"t": "Three hours of work", "at": "three hours"}]},
    {"type": "chip", "at": "Ideally", "text": "Ideally, in Bali"},
    {"type": "card", "at": "repetitive", "label": "If you're not smart", "title": "It gets repetitive fast", "w": 820},
    {"type": "list", "at": "I want a stable", "label": "What I want", "w": 860,
     "rows": [{"t": "A stable income", "at": "stable income"}, {"t": "Freedom to experiment", "at": "freedom to experiment"}, {"t": "Different skills", "at": "Different skills"}]},
    {"type": "map", "at": "Different countries", "src": A + "map_world_mid.png", "iw": 1024, "ih": 600, "w": 940, "h": 551, "label": "Different countries",
     "pins": [{"x": WD(-8.4, 115.2)[0], "y": WD(-8.4, 115.2)[1], "label": "Bali", "at": "Different countries"},
              {"x": WD(-30.6, 22.9)[0], "y": WD(-30.6, 22.9)[1], "label": "South Africa", "at": "Different countries", "delay": 0.25},
              {"x": WD(-14.2, -51.9)[0], "y": WD(-14.2, -51.9)[1], "label": "South America", "at": "Different countries", "delay": 0.5},
              {"x": WD(40.4, -3.7)[0], "y": WD(40.4, -3.7)[1], "label": "Spain", "at": "Different countries", "delay": 0.75}]},
    {"type": "quote", "at": "Build the skill first", "text": "Skill first.<br><i>Location second.</i>"},
    {"type": "card", "at": "A skill travels", "label": "The difference", "title": "A skill travels with you.", "sub": "A trend doesn't.", "w": 860},
    {"type": "card", "at": "Agree", "label": "Comment", "title": "Agree or disagree?", "w": 800},
    {"type": "card", "at": "disagree", "beside": True, "label": "Tomorrow · EP 4", "labelColor": "#D9473A", "title": "Confidence is a character you play", "w": 800},
  ]}

# ---------------------------------------------------------------- EP 4 (Mon 2 Nov): confidence is a character you play
S["e4"] = ("[softly] Nobody tells you this about confidence. You don't find it. You play it. For years, I wanted to make content. "
           "And every time, I stopped. Not because I had nothing to say. Because I didn't feel confident enough to say it. I "
           "overthought everything. Even the move to Germany, I doubted. [warmly] Here's what I'd tell my younger self. The way you "
           "talk to yourself decides how confident you are. So change what you say. Confidence isn't something you have. It's a "
           "character you play. You say it. You repeat it. You act like him. And one day, you are him. [smiling] This guy? He's the "
           "character. Every video I post, I play him a little more. Follow, and watch him become real.")
B["e4"] = {"ep": 4, "mood": "soft inspiring piano, gentle strings, builds slowly to warm and confident",
  "hook": "Confidence isn't found.<br><i>It's played.</i>", "hookEnd": "For years",
  "mascot": [["Nobody", "think"], ["For years", "point_left"], ["I overthought", "think"], ["younger self", "explain"], ["So change", "point_up"],
             ["character you play", "arms"], ["You say it", "point_up"], ["This guy", "wave"], ["Every video", "thumbs"], ["Follow", "point_left"]],
  "react": [["every time", "concerned", 1.2], ["doubted", "thought", 1.3], ["This guy", "wink", 1.4]],
  "els": [
    {"type": "card", "at": "For years", "icon": "●", "label": "For years", "title": "I wanted to make content", "w": 860},
    {"type": "dlg", "at": "every time", "title": "Delete draft?", "body": "This video will be deleted.", "btns": ["Keep", "Delete"], "red": 1, "pick": 1, "press": "stopped"},
    {"type": "list", "at": "Not because", "label": "Why I stopped", "w": 880,
     "rows": [{"t": "Nothing to say", "at": "nothing to say", "x": True}, {"t": "Didn't feel confident", "at": "feel confident"}]},
    {"type": "tags", "at": "I overthought everything", "w": 900, "gap": 0.3, "items": ["Overthinking", "Doubting", "Waiting"]},
    {"type": "map", "at": "move to Germany", "src": A + "map_india_europe.png", "iw": 1024, "ih": 768, "w": 940, "h": 668, "label": "The move",
     "pins": [{"x": EU(*INDIA)[0], "y": EU(*INDIA)[1], "label": "India", "at": "move to Germany"},
              {"x": EU(*GERMANY)[0], "y": EU(*GERMANY)[1], "label": "Germany", "at": "Germany"}],
     "routes": [{"a": EU(*INDIA), "b": EU(*GERMANY), "at": "move to Germany", "dur": 1.4, "curve": 0.2}]},
    {"type": "stamp", "at": "doubted", "text": "DOUBTED IT"},
    {"type": "card", "at": "The way you", "label": "Note to my younger self", "title": "The way you talk to yourself decides how confident you are.", "w": 900},
    {"type": "doc", "at": "So change what you say", "label": "For example", "w": 900,
     "lines": [{"t": "I'm not ready", "nw": "I'm learning in public", "at": "change what you say"}, {"t": "Who would watch this?", "nw": "Someone needs this", "at": "isn't something"}]},
    {"type": "quote", "at": "It's a character", "text": "It's a <i>character</i><br>you play."},
    {"type": "list", "at": "You say it", "label": "How you play it", "w": 820,
     "rows": [{"t": "Say it", "at": "You say it"}, {"t": "Repeat it", "at": "You repeat it"}, {"t": "Act like him", "at": "You act like him"}]},
    {"type": "card", "at": "And one day", "label": "And one day", "title": "You are him.", "w": 760},
    {"type": "card", "at": "This guy", "label": "The character", "title": "Confident Vish", "sub": "Played a little more every video.", "w": 800},
    {"type": "card", "at": "Follow", "label": "Follow", "title": "Watch him become real", "w": 800},
    {"type": "card", "at": "become real", "beside": True, "label": "Tomorrow · EP 5", "labelColor": "#D9473A", "title": "A brand made us redo one shortlist 22 times", "w": 800},
  ]}

# ---------------------------------------------------------------- EP 5 (Tue 3 Nov): the 22 shortlist redos (Brand-Side)
S["e5"] = ("[incredulous] Nobody tells you what happens to creators behind the scenes. I've worked on 850 plus creator deals, on the "
           "brand side. This one still bothers me. A brand asked us for creators with a strong, original personal brand. Nobody "
           "copying anybody. So we built a shortlist. They sent it back. We built it again. And again. Twenty two times. We worked "
           "through the night. And we found them. Niche, original, real. [pause] Then the videos came in. [annoyed] And the brand "
           "rewrote every single line those creators said. Every one. They wanted originality. They just didn't want to give the "
           "freedom that creates it. [firm] Creators, this is why your brief reads like a script. Brands, here's the rule. If you "
           "hire a creator for their voice, let them use it. Be honest. Have you done this?")
B["e5"] = {"ep": 5, "mood": "tense light pizzicato and soft synth pulse, investigative, a firm beat at the end",
  "hook": "A brand made us redo<br><i>one shortlist 22 times.</i>", "hookEnd": "I've worked on",
  "mascot": [["Nobody", "arms"], ["I've worked on", "thumbs"], ["This one still", "think"], ["A brand asked", "explain"], ["So we built", "point_left"],
             ["Twenty two times", "front"], ["Niche", "thumbs"], ["Then the videos", "think"], ["They wanted originality", "arms"],
             ["Creators, this", "point_left"], ["If you hire", "point_up"], ["Be honest", "explain"]],
  "react": [["They sent it back", "skeptical", 1.2], ["Twenty two times", "surprised", 1.4], ["rewrote", "concerned", 1.4]],
  "els": [
    {"type": "counter", "at": "850", "label": "Creator deals, brand side", "from": 0, "to": 850, "suffix": "+", "w": 760},
    {"type": "card", "at": "A brand asked", "label": "The brief", "title": "Strong, original personal brands", "sub": "Nobody copying anybody.", "w": 880},
    {"type": "list", "at": "So we built a shortlist", "label": "Shortlist", "w": 820,
     "rows": [{"t": "Creator A", "at": "built a shortlist"}, {"t": "Creator B", "at": "built a shortlist"}, {"t": "Creator C", "at": "built a shortlist"}]},
    {"type": "stamp", "at": "They sent it back", "text": "SENT BACK"},
    {"type": "counter", "at": "We built it again", "label": "Shortlist version", "from": 1, "to": 22, "prefix": "v", "until": "Twenty two times", "w": 720},
    {"type": "stamp", "at": "Twenty two times", "text": "22 TIMES"},
    {"type": "card", "at": "through the night", "icon": "☾", "label": "Overnight", "title": "We worked through the night", "w": 860},
    {"type": "tags", "at": "Niche, original", "w": 900, "gap": 0.35, "items": ["Niche", "Original", "Real"]},
    {"type": "doc", "at": "Then the videos came in", "label": "The creator's script", "w": 900,
     "lines": [{"t": "Their own words", "nw": "Brand wording", "at": "rewrote"}, {"t": "Their own story", "nw": "Key message", "at": "every single line"},
               {"t": "Their own joke", "nw": "Mandatory line", "at": "Every one"}]},
    {"type": "quote", "at": "They wanted originality", "text": "They wanted<br><i>originality.</i>"},
    {"type": "card", "at": "didn't want to give", "beside": True, "label": "But not", "labelColor": "#D9473A", "title": "The freedom that creates it", "w": 800},
    {"type": "card", "at": "Creators, this", "label": "Creators", "title": "This is why your brief reads like a script", "w": 880},
    {"type": "card", "at": "If you hire", "label": "Brands, the rule", "title": "Hire them for their voice? Let them use it.", "w": 880},
    {"type": "card", "at": "Be honest", "label": "Brands, be honest", "title": "Have you done this?", "w": 800},
    {"type": "card", "at": "done this", "beside": True, "label": "Tomorrow · EP 6", "labelColor": "#D9473A", "title": "Germany or India? Pick the country first", "w": 800},
  ]}

# ---------------------------------------------------------------- EP 6 (Wed 4 Nov): the country before the career
S["e6"] = ("[curious] Nobody tells you this before you move abroad. The country matters more than the career. I moved from India to "
           "Germany about a year ago. Here's what Germany gets right. You work extra hours? You get paid for every one. Meetings start "
           "on time. Things are structured. The nature is beautiful. The streets are clean. [hesitant] Here's what it gets wrong. It's "
           "not lively. It's not built for remote workers. And people can feel cold. [warmly] India is the opposite. Chaotic, but warm. "
           "Your people are close. Neither one is better. They suit different people. If you want structure and a stable nine to five, "
           "Germany works. If you need warmth around you, think twice. So which are you? Structure, or warmth? Comment it, and I'll "
           "tell you where to look.")
B["e6"] = {"ep": 6, "mood": "warm curious acoustic guitar, light percussion, gentle and friendly",
  "hook": "The country matters<br><i>more than the career.</i>", "hookEnd": "I moved",
  "mascot": [["Nobody", "arms"], ["I moved", "point_left"], ["gets right", "thumbs"], ["gets wrong", "think"], ["India is the opposite", "explain"],
             ["Neither", "arms"], ["If you want", "point_left"], ["So which", "explain"]],
  "react": [["feel cold", "concerned", 1.2], ["warm", "pleased", 1.2]],
  "els": [
    {"type": "map", "at": "I moved", "src": A + "map_india_europe.png", "iw": 1024, "ih": 768, "w": 940, "h": 668, "label": "About a year ago",
     "pins": [{"x": EU(*INDIA)[0], "y": EU(*INDIA)[1], "label": "India", "at": "from India"},
              {"x": EU(*GERMANY)[0], "y": EU(*GERMANY)[1], "label": "Germany", "at": "Germany"}],
     "routes": [{"a": EU(*INDIA), "b": EU(*GERMANY), "at": "from India", "dur": 1.4, "curve": 0.2}]},
    {"type": "shot", "at": "Here's what Germany", "frame": "photo", "src": A + "germany.jpg", "w": 900, "vh": 600, "fit": "cover", "caption": "Germany", "credit": "Photo: Wikimedia Commons"},
    {"type": "list", "at": "You work extra hours", "label": "Germany gets right", "w": 880,
     "rows": [{"t": "Overtime is paid", "at": "You get paid"}, {"t": "Meetings start on time", "at": "Meetings start"}, {"t": "Structure", "at": "Things are structured"},
              {"t": "Nature", "at": "The nature"}, {"t": "Clean streets", "at": "The streets"}]},
    {"type": "list", "at": "gets wrong", "label": "Germany gets wrong", "w": 880,
     "rows": [{"t": "Not lively", "at": "not lively", "x": True}, {"t": "Not built for remote work", "at": "built for remote", "x": True},
              {"t": "People can feel cold", "at": "feel cold", "x": True}]},
    {"type": "shot", "at": "India is the opposite", "frame": "photo", "src": A + "india.jpg", "w": 900, "vh": 640, "fit": "cover", "caption": "India", "credit": "Photo: Wikimedia Commons"},
    {"type": "tags", "at": "Chaotic", "w": 900, "gap": 0.45, "items": ["Chaotic", "Warm", "Close"]},
    {"type": "quote", "at": "Neither one", "text": "Neither is<br><i>better.</i>"},
    {"type": "card", "at": "If you want structure", "label": "Want structure and a stable 9 to 5?", "title": "Germany works.", "w": 860},
    {"type": "card", "at": "If you need warmth", "beside": True, "label": "Need warmth around you?", "labelColor": "#D9473A", "title": "Think twice.", "w": 860},
    {"type": "card", "at": "So which are you", "label": "Comment", "title": "Structure or warmth?", "sub": "I'll tell you where to look.", "w": 820},
    {"type": "card", "at": "where to look", "beside": True, "label": "Friday · EP 7", "labelColor": "#D9473A", "title": "The biggest hustle is not hustling", "w": 820},
  ]}

# ---------------------------------------------------------------- EP 7 (Fri 6 Nov): how not to hustle, and the clone reveal
S["e7"] = ("[confident] Nobody tells you this about hustle culture. The biggest hustle now is figuring out how not to hustle. "
           "Everyone's scared AI will replace marketers. It won't. I'm finishing my master's thesis on exactly this. AI in marketing. "
           "Marketers who use AI will hand it all the heavy lifting. The repetitive tool work nobody misses. So what's left? The "
           "part that was always the job. Psychology. Taste. Creativity. Here's my daily stack. Claude Code, which built this video. "
           "Claude. ChatGPT. ElevenLabs, which is my voice. And Gemini. [playful] And yes. Every episode this week was my AI voice "
           "clone. On Sunday, I'll tell you why. Hustle less. Think more. What's one task you'd hand to AI tomorrow?")
B["e7"] = {"ep": 7, "mood": "confident modern lo-fi beat, warm keys, head-nod groove",
  "hook": "The biggest hustle:<br><i>not hustling.</i>", "hookEnd": "Everyone's scared",
  "mascot": [["Nobody", "arms"], ["Everyone's scared", "think"], ["master's thesis", "explain"], ["heavy lifting", "thumbs"], ["So what's left", "think"],
             ["Psychology", "point_up"], ["daily stack", "point_left"], ["And yes", "front"], ["On Sunday", "explain"], ["Hustle less", "arms"], ["What's one task", "point_left"]],
  "react": [["It won't", "wink", 1.0], ["And yes", "laugh", 1.5]],
  "els": [
    {"type": "card", "at": "Everyone's scared", "label": "Everyone's scared", "title": "AI will replace marketers", "w": 860},
    {"type": "stamp", "at": "It won't", "text": "IT WON'T", "color": "#2F6B3F"},
    {"type": "card", "at": "master's thesis", "icon": "✎", "label": "My master's thesis", "title": "AI in marketing", "sub": "Finishing it now.", "w": 860},
    {"type": "list", "at": "Marketers who use AI", "label": "AI takes", "w": 880,
     "rows": [{"t": "The heavy lifting", "at": "heavy lifting"}, {"t": "The repetitive tool work", "at": "repetitive tool work"}]},
    {"type": "quote", "at": "So what's left", "text": "So what's<br><i>left?</i>"},
    {"type": "tags", "at": "Psychology", "w": 900, "gap": 0.5, "items": ["Psychology", "Taste", "Creativity"]},
    {"type": "shot", "at": "Claude Code, which", "src": A + "claude_code.png", "url": "anthropic.com/claude-code", "w": 940, "vh": 900,
     "scroll": [["Claude Code, which", 0], ["built this video", 0.025]], "cursor": [["which built", 0.3, 0.5], ["this video", 0.22, 0.36, True]]},
    {"type": "tags", "at": "Claude#2", "w": 900, "gap": 0.42, "items": ["Claude", "ChatGPT", "ElevenLabs", "Gemini"]},
    {"type": "shot", "at": "which is my voice", "src": A + "elevenlabs.png", "url": "elevenlabs.io", "w": 940, "vh": 760,
     "scroll": [["which is my voice", 0.0], ["And yes", 0.04]]},
    {"type": "card", "at": "And yes", "label": "Plot twist", "labelColor": "#D9473A", "title": "Every episode this week was my AI voice clone", "w": 900},
    {"type": "wave", "at": "voice clone", "beside": True, "label": "My voice clone", "until": "Sunday", "w": 900},
    {"type": "card", "at": "On Sunday", "label": "Sunday", "title": "Why I cloned my voice", "w": 800},
    {"type": "quote", "at": "Hustle less", "text": "Hustle less.<br><i>Think more.</i>"},
    {"type": "card", "at": "What's one task", "label": "Comment", "title": "One task you'd hand to AI tomorrow?", "w": 860},
  ]}

for k, b in B.items():
    b.update({"template": "series", "series": SERIES})
    for e in b["els"]:  # narrower cards = a closer camera = bigger words on a phone
        if e["type"] in ("card", "list", "counter", "bar", "doc", "wave") and "w" in e:
            e["w"] = round(e["w"] * 0.8)
(HERE / "scripts.json").write_text(json.dumps(S, indent=1, ensure_ascii=False))
(HERE / "beats.json").write_text(json.dumps(B, indent=1, ensure_ascii=False))
print({k: len(v.split()) for k, v in S.items()})
