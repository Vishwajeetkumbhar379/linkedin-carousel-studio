"""Nobody Tells You, v3 (Vish, 28 Oct): scripts at the level of @alessyleblanc DcCO-pYx7Ue ("I'm 28, I'm unemployed, and this is
how I plan on living..."): who and what's at stake in the first line, exact true details, candid asides, signposts, fast.
The engine is templates/video/series3: the mascot talks (mouth on the voice), blinks, walks, peeks; three.js studio shots
(laptop, phone, globe, card stack) flip in; chapters wipe the colour; a live counter; word-by-word captions.
    python build3.py      -> scripts.json, beats.json      (then ./voices.sh, then canvas_reel.py . eN)
Facts only from brand-profile.md. Every "at" is a phrase from the script ("word#2" = the second time it is said).
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = "video-projects/ntu/assets/"
SERIES = "NOBODY TELLS YOU"
INDIA, GERMANY, LANKA = [21.0, 78.0], [51.0, 10.0], [7.9, 80.7]
PAPER, NIGHT, AMBER = "#F1ECE3", "#14161B", "#E7A15A"


def frames(k):
    """The real frame count of this reel (the counter in EP 1 shows it), from the voice once it exists."""
    f = HERE / f"{k}_words.json"
    return round((json.loads(f.read_text())[-1]["e"] + 1.0) * 30) if f.exists() else 1500


def teaser(at, ep, when, title):
    return {"type": "card", "at": at, "beside": True, "label": f"{when} · EP {ep}", "labelColor": "#D9473A", "title": title, "w": 680}


S, B = {}, {}

# ---------------------------------------------------------------- EP 1 (Fri 30 Oct): nobody edited this reel (EDIT)
S["e1"] = ("[excited] I'm 27, I'm not an editor, and nobody edited this reel. No video AI either. Claude made it, in code, and here's "
           "exactly how. First, the script. I write it the way I'd tell a friend. Second, the voice. That's my voice clone on ElevenLabs, "
           "trained on my own recordings. And yes, I used to be insecure about my voice. That's a story for Sunday. Third, the timing. "
           "Claude listens back and stamps every single word, down to the hundredth of a second. Fourth, the build. Every card, every "
           "camera move, and this guy, are written in code and land on those words. Fifth, the render. Frame by frame. The total cost? "
           "My Claude subscription. [serious] Here's what nobody tells you. The hard part isn't the code. It's saying no until it's right. "
           "And trust me, I said no a lot this week. [warm] Comment EDIT and I'll send you the exact prompts.")
B["e1"] = {"ep": 1, "mood": "upbeat playful tech, bright plucks, bouncy hip hop beat, curious and clever, feel-good",
  "hook": "Nobody edited<br><i>this reel.</i>", "hookEnd": "No video AI", "em": ["claude", "code", "edit", "no", "subscription"],
  "chapters": [["I'm 27", PAPER, "the claim"], ["First, the script", PAPER, "five steps"], ["Here's what nobody", NIGHT, "the truth"], ["Comment EDIT", AMBER, "the prompts"]],
  "ticker": {"label": "STEP", "suffix": " / 5", "keys": [["I'm 27", 0], ["First", 1], ["Second", 2], ["Third", 3], ["Fourth", 4], ["Fifth", 5]]},
  "mascot": [["I'm 27", "walk_r", "walk", {"dur": 1.0, "to": 540}], ["nobody edited", "smile", "face"], ["No video AI", "skeptical", "face"],
             ["Claude made it", "turn_r", "peek", {"x": 880}], ["First, the script", "explain", "bust"], ["Second, the voice", "turn_r", "peek", {"x": 880}],
             ["insecure", "concerned", "face"], ["story for Sunday", "wink", "face"], ["Third, the timing", "think", "bust"], ["Fourth, the build", "point_up", "bust"],
             ["this guy", "wave", "full", {"x": 800}], ["Fifth, the render", "point_left", "bust"], ["total cost", "thumbs", "bust"], ["Here's what nobody", "thought", "face"],
             ["saying no", "arms", "bust"], ["trust me", "laugh", "face"], ["Comment EDIT", "point_up", "bust"], ["exact prompts", "wave", "full"]],
  "react": [["hundredth", "surprised", 1.2]],
  "heroes": [{"kind": "laptop", "at": "Claude made it", "until": "First, the script", "src": A + "claude_code.png", "scroll": [["Claude made it", 0], ["exactly how", 0.025]]},
             {"kind": "phone", "at": "Second, the voice", "until": "And yes", "src": A + "elevenlabs.png", "scroll": [["Second, the voice", 0], ["trained on", 0.03]]}],
  "els": [
    {"type": "card", "at": "nobody edited", "icon": "✂", "label": "Video editor", "title": "Not opened", "w": 640},
    {"type": "card", "at": "No video AI", "beside": True, "icon": "✦", "label": "Video AI", "title": "Not used", "w": 640},
    {"type": "stamp", "at": "either", "text": "NEITHER"},
    {"type": "card", "at": "First, the script", "label": "Step 1 · The script", "title": "“I'm 27, I'm not an editor…”", "sub": "Written the way I'd tell a friend.", "w": 720},
    {"type": "wave", "at": "And yes", "label": "My voice clone", "title": "Reading this script", "until": "Third", "w": 720},
    {"type": "tags", "at": "stamps every single word", "w": 880, "gap": 0.16,
     "items": [f"{w} <b style='color:#E7A15A'>{t}</b>" for w, t in (("I'm", "0.20s"), ("27,", "0.41s"), ("I'm", "0.78s"), ("not", "0.90s"), ("an", "1.05s"), ("editor", "1.13s"))]},
    {"type": "card", "at": "Fourth, the build", "label": "Step 4 · The build", "title": "Every card. Every camera move.", "w": 700, "reveal": "every camera move"},
    {"type": "counter", "at": "Fifth, the render", "label": "Frames rendered", "from": 0, "to": frames("e1"), "until": "The total cost", "w": 640},
    {"type": "card", "at": "The total cost", "icon": "€", "label": "Total cost", "title": "My Claude subscription", "w": 700},
    {"type": "stamp", "at": "subscription", "text": "THAT'S IT", "color": "#2F6B3F"},
    {"type": "quote", "at": "The hard part", "text": "The hard part<br>isn't the <i>code.</i>"},
    {"type": "card", "at": "saying no", "label": "The real job", "title": "Saying no until it's right.", "w": 700},
    {"type": "card", "at": "Comment EDIT", "label": "Comment", "title": "EDIT", "sub": "I'll send you the exact prompts.", "w": 680},
    teaser("exact prompts", 2, "Tomorrow", "One meeting trapped me for six months"),
  ]}

# ---------------------------------------------------------------- EP 2 (Sat 31 Oct): one meeting trapped me for six months
S["e2"] = ("[serious] I'm 27, I worked remotely for four years, and one meeting still trapped me for six months. Here's what happened. "
           "I was working from India, paid in rupees, travelling whenever I could. I'd booked my next two flights. [frustrated] Then an "
           "important meeting came up. So I cancelled the first flight. Then the second one. Then more client work came in, and I was "
           "stuck. In a nine to five. For six months. For someone obsessed with travelling, that was hell. [calm] Here's what nobody tells "
           "you about remote work. It isn't freedom if you're paid in a currency that doesn't stretch. And it isn't freedom if one meeting "
           "can call you back. When I'm not travelling, my life feels like autopilot. When I travel, I count every single day. [determined] "
           "So this time, I'm fixing both. Earn in euros. Build work that can't call me back. The test is December. I've booked Sri Lanka, "
           "for a month. Would you have cancelled those flights?")
B["e2"] = {"ep": 2, "mood": "warm reflective piano and soft pads, light drums enter halfway, hopeful lift at the end",
  "hook": "One meeting trapped me<br><i>for six months.</i>", "hookEnd": "Here's what happened", "em": ["rupees", "hell", "euros", "december", "autopilot", "six"],
  "chapters": [["I'm 27", PAPER, "the setup"], ["Then an", NIGHT, "the meeting"], ["Here's what nobody", PAPER, "the lesson"], ["The test is December", AMBER, "the test"]],
  "ticker": {"label": "FLIGHTS CANCELLED", "keys": [["I'm 27", 0], ["the first flight", 1], ["the second one", 2]]},
  "mascot": [["I'm 27", "walk_r", "walk", {"dur": 1.0, "to": 540}], ["one meeting", "concerned", "face"], ["Here's what happened", "explain", "bust"],
             ["working from India", "turn_l", "peek", {"x": 880}], ["important meeting", "surprised", "peek", {"x": 880}], ["the first flight", "concerned", "peek", {"x": 880}],
             ["more client work", "think", "bust"], ["stuck", "front", "bust"], ["that was hell", "skeptical", "face"], ["Here's what nobody", "explain", "bust"],
             ["paid in a currency", "point_up", "bust"], ["autopilot", "thought", "face"], ["count every single day", "pleased", "face"], ["fixing both", "thumbs", "bust"],
             ["The test is December", "turn_r", "peek", {"x": 880}], ["for a month", "pleased", "face"], ["Would you", "explain", "bust"]],
  "react": [["six months#2", "surprised", 1.2]],
  "heroes": [{"kind": "globe", "at": "working from India", "until": "more client work", "keys": [["working from India", 22, 74, 7.6], ["the second one", 24, 70, 8.4]],
              "pins": [{"lat": INDIA[0], "lon": INDIA[1], "label": "Me, remote", "at": "working from India"}],
              "routes": [{"a": INDIA, "b": [41, 29], "at": "booked my next two flights", "dur": 1.3, "cancel": "the first flight"},
                         {"a": INDIA, "b": [3, 101], "at": "two flights", "dur": 1.3, "cancel": "the second one", "lift": 0.18}]},
             {"kind": "globe", "at": "The test is December", "until": "for a month", "keys": [["The test is December", 45, 25, 8.2], ["I've booked Sri Lanka", 24, 55, 8.8]],
              "pins": [{"lat": GERMANY[0], "lon": GERMANY[1], "label": "Germany", "at": "The test is December"}, {"lat": LANKA[0], "lon": LANKA[1], "label": "Sri Lanka", "at": "booked Sri Lanka"}],
              "routes": [{"a": GERMANY, "b": LANKA, "at": "I've booked Sri Lanka", "dur": 1.5, "color": "#E7A15A"}]}],
  "els": [
    {"type": "counter", "at": "I worked remotely", "label": "Working remotely", "from": 0, "to": 4, "suffix": " years", "w": 640},
    {"type": "tags", "at": "more client work", "w": 880, "gap": 0.2, "items": ["Client work", "Client work", "Client work", "Client work"]},
    {"type": "bar", "at": "I was stuck", "fill": "six months#2", "label": "Office hours, nine to five", "n": 6, "unit": "months", "w": 660},
    {"type": "quote", "at": "that was hell", "text": "That was <i>hell.</i>"},
    {"type": "list", "at": "It isn't freedom", "label": "Remote isn't freedom if", "w": 760,
     "rows": [{"t": "Your currency doesn't stretch", "at": "paid in a currency", "x": True}, {"t": "One meeting can call you back", "at": "one meeting can", "x": True}]},
    {"type": "card", "at": "not travelling", "label": "Not travelling", "title": "Autopilot", "w": 640, "out": "When I travel"},
    {"type": "card", "at": "When I travel", "beside": True, "label": "Travelling", "labelColor": "#2F6B3F", "title": "I count every single day", "w": 640},
    {"type": "list", "at": "fixing both", "label": "So I'm fixing both", "w": 720, "rows": [{"t": "Earn in euros", "at": "Earn in euros"}, {"t": "Work that can't call me back", "at": "Build work"}]},
    {"type": "shot", "at": "for a month", "frame": "photo", "src": A + "sigiriya.jpg", "w": 860, "vh": 560, "fit": "cover", "caption": "Sri Lanka, December", "credit": "Photo: Wikimedia Commons"},
    {"type": "card", "at": "Would you", "label": "Your turn", "title": "Would you have cancelled those flights?", "w": 700},
    teaser("those flights", 3, "Tomorrow", "Bali has a coach problem"),
  ]}

# ---------------------------------------------------------------- EP 3 (Sun 1 Nov): Bali has a coach problem
S["e3"] = ("[mischievously] Hot take. Bali has a coach problem. And I say that as someone whose perfect Tuesday happens in Bali. Up at six. "
           "Ocean swim. Yoga. Coffee, a smoothie bowl, then three hours of work. [serious] But here's what nobody tells you about Bali. Every "
           "next person is a coach. A business coach. A mindset coach. A coach for coaches. I don't have a problem with coaches. I have a "
           "problem with careers that are valid for one year. Everyone moves to the same island, sells the same course to the same people, "
           "who then move to the same island. It's beautiful, and the people are lovely. But it gets repetitive fast, if you're not smart. "
           "[firm] So my rule is simple. Build the skill first. The location second. A skill travels with you. A trend doesn't. That's why "
           "I'm building mine first: brand-side marketing and AI. Agree, or disagree?")
B["e3"] = {"ep": 3, "mood": "playful tropical house, marimba and light percussion, cheeky, sunny",
  "hook": "Bali has a<br><i>coach problem.</i>", "hookEnd": "And I say", "em": ["bali", "coach", "coaches", "skill", "location", "trend"],
  "chapters": [["Hot take", PAPER, "the take"], ["Up at six", AMBER, "the dream"], ["But here's what", PAPER, "the problem"], ["So my rule", NIGHT, "the rule"]],
  "ticker": {"label": "COACHES SPOTTED", "keys": [["Hot take", 0], ["A business coach", 1], ["A mindset coach", 2], ["A coach for coaches", 3]]},
  "mascot": [["Hot take", "walk_r", "walk", {"dur": 0.9, "to": 540}], ["coach problem", "wink", "face"], ["perfect Tuesday", "pleased", "face"], ["Up at six", "explain", "bust"],
             ["But here's what", "skeptical", "face"], ["Every next person", "turn_r", "peek", {"x": 880}], ["coach for coaches", "laugh", "peek", {"x": 880}],
             ["I don't have a problem", "explain", "bust"], ["Everyone moves", "point_up", "bust"], ["same island#2", "wink", "face"], ["It's beautiful", "smile", "face"],
             ["repetitive", "skeptical", "face"], ["So my rule", "arms", "bust"], ["A skill travels", "turn_r", "peek", {"x": 880}], ["That's why", "thumbs", "peek", {"x": 880}],
             ["Agree", "explain", "bust"]],
  "heroes": [{"kind": "cards", "at": "Every next person", "until": "I don't have a problem",
              "faces": [{"label": "Coach no. 1", "title": "Business\ncoach", "size": 100, "at": "A business coach"},
                        {"label": "Coach no. 2", "title": "Mindset\ncoach", "size": 100, "at": "A mindset coach"},
                        {"label": "Coach no. 3", "title": "Coach for\ncoaches", "size": 100, "color": "#D9473A", "at": "A coach for coaches"}]},
             {"kind": "globe", "at": "A skill travels", "until": "Agree", "keys": [["A skill travels", -8, 112, 8.2], ["A trend doesn't", 5, 30, 9.6]],
              "pins": [{"lat": -8.4, "lon": 115.2, "label": "Bali", "at": "A skill travels"}, {"lat": -30.6, "lon": 22.9, "label": "South Africa", "at": "A trend doesn't"},
                       {"lat": -14.2, "lon": -51.9, "label": "South America", "at": "A trend doesn't", "delay": 0.3}, {"lat": 40.4, "lon": -3.7, "label": "Spain", "at": "A trend doesn't", "delay": 0.6}]}],
  "els": [
    {"type": "list", "at": "Up at six", "label": "My perfect Tuesday", "w": 720,
     "rows": [{"t": "Up at six", "at": "Up at six"}, {"t": "Ocean swim", "at": "Ocean swim"}, {"t": "Yoga", "at": "Yoga"}, {"t": "Coffee, smoothie bowl", "at": "Coffee"}, {"t": "Three hours of work", "at": "three hours"}]},
    {"type": "shot", "at": "But here's what", "frame": "photo", "src": A + "ubud.jpg", "w": 860, "vh": 580, "fit": "cover", "caption": "Bali", "credit": "Photo: Wikimedia Commons"},
    {"type": "card", "at": "I don't have a problem", "label": "No problem with", "title": "Coaches", "w": 640},
    {"type": "card", "at": "careers that are", "beside": True, "label": "My problem", "labelColor": "#D9473A", "title": "Careers valid for one year", "w": 640},
    {"type": "list", "at": "Everyone moves", "label": "How it goes", "w": 760,
     "rows": [{"t": "Move to the same island", "at": "Everyone moves"}, {"t": "Sell the same course", "at": "sells the same course"},
              {"t": "To the same people", "at": "to the same people"}, {"t": "Who move to the same island", "at": "who then move"}]},
    {"type": "stamp", "at": "same island#2", "text": "↻ REPEAT"},
    {"type": "quote", "at": "It's beautiful", "text": "It's <i>beautiful.</i>"},
    {"type": "card", "at": "repetitive", "label": "If you're not smart", "title": "It gets repetitive fast", "w": 680},
    {"type": "quote", "at": "Build the skill first", "text": "Skill first.<br><i>Location second.</i>"},
    {"type": "card", "at": "Agree", "label": "Comment", "title": "Agree or disagree?", "w": 660},
    teaser("disagree", 4, "Tomorrow", "Confidence is a character you play"),
  ]}

# ---------------------------------------------------------------- EP 4 (Mon 2 Nov): confidence is a character you play
S["e4"] = ("[softly] For years, I wanted to make content. And every single time, I stopped. Not because I had nothing to say. Because I "
           "didn't feel confident enough to say it. I overthought everything. Even the move to Germany, I doubted that too. [warmly] Here's "
           "what nobody tells you about confidence. You don't find it. You play it. The way you talk to yourself decides how confident you "
           "are. So change what you say. Confidence isn't something you have. It's a character you play. You say it. You repeat it. You act "
           "like him. And one day, you are him. [smiling] This is week three of fifty two, and this guy is the character. Every video I post, "
           "I play him a little more. Follow, and watch him become real.")
B["e4"] = {"ep": 4, "mood": "soft inspiring piano and warm strings, builds slowly to confident and uplifting",
  "hook": "Confidence isn't found.<br><i>It's played.</i>", "hookEnd": "And every single time", "em": ["confident", "confidence", "character", "play", "him", "real"],
  "chapters": [["For years", PAPER, "the stopping"], ["Here's what nobody", NIGHT, "the truth"], ["This is week three", AMBER, "the character"]],
  "ticker": {"label": "CONFIDENCE", "suffix": "%", "keys": [["For years", 12], ["Here's what nobody", 35], ["It's a character", 60], ["And one day", 90], ["become real", 100]]},
  "mascot": [["For years", "thought", "face"], ["every single time", "concerned", "face"], ["Not because", "explain", "bust"], ["I overthought", "think", "bust"],
             ["the move to Germany", "turn_l", "peek", {"x": 880}], ["Here's what nobody", "smile", "face"], ["You don't find it", "point_up", "bust"],
             ["The way you talk", "explain", "bust"], ["So change", "focused", "face"], ["It's a character", "arms", "bust"], ["You say it", "point_up", "bust"],
             ["And one day", "pleased", "face"], ["This is week three", "walk_r", "walk", {"from": -300, "to": 540, "dur": 1.2}], ["this guy", "wave", "full", {"x": 540, "size": 640}],
             ["Every video", "thumbs", "bust"], ["Follow", "point_up", "bust"], ["become real", "wave", "full"]],
  "react": [["doubted", "thought", 1.2]],
  "heroes": [{"kind": "globe", "at": "Even the move", "until": "Here's what nobody", "keys": [["Even the move", 30, 50, 8.6], ["doubted", 42, 30, 8.8]],
              "pins": [{"lat": INDIA[0], "lon": INDIA[1], "label": "India", "at": "Even the move"}, {"lat": GERMANY[0], "lon": GERMANY[1], "label": "Germany", "at": "Germany"}],
              "routes": [{"a": INDIA, "b": GERMANY, "at": "the move to Germany", "dur": 1.4}]}],
  "els": [
    {"type": "card", "at": "I wanted to make content", "icon": "●", "label": "For years", "title": "I wanted to make content", "w": 720},
    {"type": "dlg", "at": "every single time", "title": "Delete draft?", "body": "This video will be deleted.", "btns": ["Keep", "Delete"], "red": 1, "pick": 1, "press": "I stopped"},
    {"type": "list", "at": "Not because", "label": "Why I stopped", "w": 760,
     "rows": [{"t": "Nothing to say", "at": "nothing to say", "x": True}, {"t": "Didn't feel confident", "at": "feel confident"}]},
    {"type": "tags", "at": "I overthought everything", "w": 880, "gap": 0.3, "items": ["Overthinking", "Doubting", "Waiting"]},
    {"type": "card", "at": "The way you talk", "label": "The rule", "title": "How you talk to yourself decides how confident you are.", "w": 760},
    {"type": "doc", "at": "So change what you say", "label": "For example", "w": 760,
     "lines": [{"t": "I'm not ready", "nw": "I'm learning in public", "at": "change what you say"}, {"t": "Who would watch this?", "nw": "Someone needs this", "at": "isn't something"}]},
    {"type": "quote", "at": "It's a character", "text": "It's a <i>character</i><br>you play."},
    {"type": "list", "at": "You say it", "label": "How you play it", "w": 700,
     "rows": [{"t": "Say it", "at": "You say it"}, {"t": "Repeat it", "at": "You repeat it"}, {"t": "Act like him", "at": "You act like him"}]},
    {"type": "card", "at": "And one day", "label": "And one day", "title": "You are him.", "w": 640},
    {"type": "card", "at": "Follow", "label": "Follow", "title": "Watch him become real", "w": 660},
    teaser("become real", 5, "Tomorrow", "A brand made us redo one shortlist 22 times"),
  ]}

# ---------------------------------------------------------------- EP 5 (Tue 3 Nov): the shortlist we redid 22 times (Brand-Side)
S["e5"] = ("[incredulous] I've worked on more than 850 creator deals on the brand side, and this one still bothers me. A brand asked us for "
           "creators with a strong, original personal brand. Nobody copying anybody. Fair. So we built a shortlist. They sent it back. We "
           "built it again. They sent it back again. Twenty two times. We worked through the night, and we found them. Niche, original, "
           "real. [pause] Then the videos came in. [annoyed] And the brand rewrote every single line those creators said. Every one. Here's "
           "what nobody tells you about brand deals. Brands say they want originality. They just don't want to give the freedom that creates "
           "it. [firm] Creators, that's why your brief reads like a script. Brands, here's the rule. If you hire a creator for their voice, "
           "let them use it. Be honest. Have you done this?")
B["e5"] = {"ep": 5, "mood": "tense light pizzicato and a soft synth pulse, investigative, a firm beat at the end",
  "hook": "A brand made us redo<br><i>one shortlist 22 times.</i>", "hookEnd": "A brand asked", "em": ["850", "originality", "freedom", "voice", "twenty", "two"],
  "chapters": [["I've worked on", PAPER, "the brief"], ["Then the videos", NIGHT, "the rewrite"], ["Here's what nobody", PAPER, "the lesson"], ["Creators, that's why", AMBER, "the rule"]],
  "ticker": {"label": "SHORTLIST VERSION", "prefix": "v", "keys": [["I've worked on", 1], ["We built it again", 2], ["They sent it back again", 3], ["Twenty two times", 22]]},
  "mascot": [["I've worked on", "walk_r", "walk", {"dur": 1.0, "to": 540}], ["still bothers me", "concerned", "face"], ["A brand asked", "explain", "bust"], ["Fair", "smile", "face"],
             ["So we built", "turn_r", "peek", {"x": 880}], ["Twenty two times", "surprised", "peek", {"x": 880}], ["We worked through", "think", "bust"], ["Niche", "thumbs", "bust"],
             ["Then the videos", "thought", "face"], ["rewrote", "skeptical", "face"], ["Here's what nobody", "explain", "bust"], ["Creators, that's why", "point_up", "bust"],
             ["If you hire", "arms", "bust"], ["Be honest", "wink", "face"]],
  "heroes": [{"kind": "cards", "at": "So we built a shortlist", "until": "We worked through",
              "faces": [{"label": "Shortlist", "title": "v1", "size": 150, "rows": ["Creator A", "Creator B", "Creator C"]},
                        {"label": "Shortlist", "title": "v1", "size": 150, "rows": ["Creator A", "Creator B", "Creator C"]},
                        {"label": "Shortlist", "title": "v{v}", "size": 150, "rows": ["Creator A", "Creator B", "Creator C"],
                         "counter": {"from": 1, "to": 22, "at": "We built it again", "until": "Twenty two times"}, "stampAt": "They sent it back", "stampText": "SENT BACK"}]}],
  "els": [
    {"type": "counter", "at": "I've worked on", "label": "Creator deals, brand side", "from": 0, "to": 850, "suffix": "+", "w": 640},
    {"type": "card", "at": "A brand asked", "label": "The brief", "title": "Strong, original personal brands", "sub": "Nobody copying anybody.", "w": 720},
    {"type": "card", "at": "We worked through the night", "icon": "☾", "label": "Overnight", "title": "We worked through the night", "w": 700},
    {"type": "tags", "at": "Niche, original", "w": 880, "gap": 0.35, "items": ["Niche", "Original", "Real"]},
    {"type": "doc", "at": "Then the videos came in", "label": "The creator's script", "w": 760,
     "lines": [{"t": "Their own words", "nw": "Brand wording", "at": "rewrote"}, {"t": "Their own story", "nw": "Key message", "at": "every single line"},
               {"t": "Their own joke", "nw": "Mandatory line", "at": "Every one"}]},
    {"type": "quote", "at": "Brands say they want", "text": "They want<br><i>originality.</i>"},
    {"type": "card", "at": "don't want to give", "beside": True, "label": "But not", "labelColor": "#D9473A", "title": "The freedom that creates it", "w": 660},
    {"type": "card", "at": "Creators, that's why", "label": "Creators", "title": "This is why your brief reads like a script", "w": 720},
    {"type": "card", "at": "If you hire", "label": "Brands, the rule", "title": "Hire them for their voice? Let them use it.", "w": 720},
    {"type": "card", "at": "Be honest", "label": "Brands, be honest", "title": "Have you done this?", "w": 660},
    teaser("done this", 6, "Tomorrow", "Germany or India? Pick the country first"),
  ]}

# ---------------------------------------------------------------- EP 6 (Wed 4 Nov): the country before the career
S["e6"] = ("[curious] I moved from India to Germany about a year ago, and here's what nobody tells you before you move abroad. The country "
           "matters more than the career. Germany first. You work extra hours? You get paid for every single one. Meetings start on time. "
           "Things are structured. The nature is beautiful, and the streets are clean. [hesitant] Now, what it gets wrong. It's not lively. "
           "It's not built for remote workers. And people can feel cold. I moved here without knowing anyone, and my German is still a work "
           "in progress, so I felt that one. [warmly] India is the opposite. Chaotic, but warm. Your people are close. Neither is better. "
           "They suit different people. If you want structure and a stable nine to five, Germany works. If you need warmth around you, think "
           "twice. So which are you? Structure, or warmth? Comment it, and I'll tell you where to look.")
B["e6"] = {"ep": 6, "mood": "warm curious acoustic guitar, light percussion, friendly and bright",
  "hook": "The country matters<br><i>more than the career.</i>", "hookEnd": "Germany first", "em": ["germany", "india", "structure", "warmth", "cold", "warm"],
  "chapters": [["I moved", PAPER, "the move"], ["Germany first", PAPER, "what Germany gets right"], ["Now, what it gets wrong", NIGHT, "what it gets wrong"],
               ["India is the opposite", AMBER, "India"], ["So which are you", PAPER, "your pick"]],
  "ticker": {"label": "GERMANY · PROS", "keys": [["I moved", 0], ["You get paid", 1], ["Meetings start", 2], ["Things are structured", 3], ["The nature", 4], ["the streets", 5]]},
  "mascot": [["I moved", "walk_l", "walk", {"from": 1360, "to": 540, "dur": 1.1}], ["The country matters", "explain", "bust"], ["Germany first", "turn_r", "bust"],
             ["You get paid", "thumbs", "bust"], ["what it gets wrong", "think", "bust"], ["feel cold", "concerned", "face"], ["I moved here without", "thought", "face"],
             ["India is the opposite", "pleased", "face"], ["Neither is better", "arms", "bust"], ["If you want", "point_up", "bust"], ["So which are you", "explain", "bust"],
             ["where to look", "wave", "full"]],
  "heroes": [{"kind": "globe", "at": "I moved", "until": "Germany first", "keys": [["I moved", 22, 76, 7.8], ["to Germany", 40, 40, 8.8]],
              "pins": [{"lat": INDIA[0], "lon": INDIA[1], "label": "India", "at": "from India"}, {"lat": GERMANY[0], "lon": GERMANY[1], "label": "Germany", "at": "to Germany"}],
              "routes": [{"a": INDIA, "b": GERMANY, "at": "from India", "dur": 1.5}]}],
  "els": [
    {"type": "shot", "at": "Germany first", "frame": "photo", "src": A + "germany.jpg", "w": 860, "vh": 560, "fit": "cover", "caption": "Germany", "credit": "Photo: Wikimedia Commons"},
    {"type": "list", "at": "You work extra hours", "label": "Germany gets right", "w": 740,
     "rows": [{"t": "Overtime is paid", "at": "You get paid"}, {"t": "Meetings start on time", "at": "Meetings start"}, {"t": "Structure", "at": "Things are structured"},
              {"t": "Nature", "at": "The nature"}, {"t": "Clean streets", "at": "the streets"}]},
    {"type": "list", "at": "what it gets wrong", "label": "Germany gets wrong", "w": 760,
     "rows": [{"t": "Not lively", "at": "not lively", "x": True}, {"t": "Not built for remote work", "at": "built for remote", "x": True}, {"t": "People can feel cold", "at": "feel cold", "x": True}]},
    {"type": "card", "at": "I moved here without", "label": "Me", "title": "New country. Knew no one.", "sub": "German: a work in progress.", "w": 700},
    {"type": "shot", "at": "India is the opposite", "frame": "photo", "src": A + "india.jpg", "w": 860, "vh": 600, "fit": "cover", "caption": "India", "credit": "Photo: Wikimedia Commons"},
    {"type": "tags", "at": "Chaotic", "w": 880, "gap": 0.45, "items": ["Chaotic", "Warm", "Close"]},
    {"type": "quote", "at": "Neither is better", "text": "Neither is<br><i>better.</i>"},
    {"type": "card", "at": "If you want structure", "label": "Want structure, a stable 9 to 5?", "title": "Germany works.", "w": 700},
    {"type": "card", "at": "If you need warmth", "beside": True, "label": "Need warmth around you?", "labelColor": "#D9473A", "title": "Think twice.", "w": 700},
    {"type": "card", "at": "So which are you", "label": "Comment", "title": "Structure or warmth?", "sub": "I'll tell you where to look.", "w": 680},
    teaser("where to look", 7, "Friday", "The biggest hustle is not hustling"),
  ]}

# ---------------------------------------------------------------- EP 7 (Fri 6 Nov): how not to hustle, and the clone reveal
S["e7"] = ("[confident] The biggest hustle right now is figuring out how not to hustle. Here's what nobody tells you about AI and marketing. "
           "Everyone's scared it will replace marketers. It won't. I'm literally writing my master's thesis on this: how AI marketing "
           "automation changes the work of marketers in Germany. Here's what I believe. Marketers who use AI will hand it the heavy lifting. "
           "The repetitive tool work nobody misses. So what's left? The part that was always the job. Psychology. Taste. Creativity. My "
           "daily stack is five tools. Claude Code, which built this video. Claude. ChatGPT. ElevenLabs. And Gemini. [playful] And yes, "
           "here's the twist. Every episode this week was my AI voice clone. On Sunday, I'll tell you why I did it. Hustle less. Think more. "
           "What's one task you'd hand to AI tomorrow?")
B["e7"] = {"ep": 7, "mood": "confident modern lo-fi house beat, warm keys, head-nod groove",
  "hook": "The biggest hustle:<br><i>not hustling.</i>", "hookEnd": "Here's what nobody", "em": ["hustle", "psychology", "taste", "creativity", "clone", "sunday"],
  "chapters": [["The biggest hustle", PAPER, "the take"], ["I'm literally writing", NIGHT, "the thesis"], ["My daily stack", PAPER, "the stack"], ["here's the twist", AMBER, "the twist"]],
  "ticker": {"label": "TOOLS IN MY STACK", "keys": [["The biggest hustle", 0], ["Claude Code", 1], ["Claude#2", 2], ["ChatGPT", 3], ["ElevenLabs", 4], ["Gemini", 5]]},
  "mascot": [["The biggest hustle", "walk_r", "walk", {"dur": 1.0, "to": 540}], ["not to hustle", "wink", "face"], ["Everyone's scared", "think", "bust"], ["It won't", "smile", "face"],
             ["I'm literally writing", "explain", "bust"], ["Here's what I believe", "point_up", "bust"], ["So what's left", "thought", "face"], ["Psychology", "pleased", "face"],
             ["My daily stack", "turn_r", "peek", {"x": 880}], ["ElevenLabs", "point_up", "bust"], ["here's the twist", "laugh", "face"], ["On Sunday", "wink", "face"],
             ["Hustle less", "arms", "bust"], ["What's one task", "point_up", "bust"], ["tomorrow", "wave", "full"]],
  "heroes": [{"kind": "laptop", "at": "My daily stack", "until": "ElevenLabs", "src": A + "claude_code.png", "scroll": [["My daily stack", 0], ["ChatGPT", 0.02]]}],
  "els": [
    {"type": "card", "at": "Everyone's scared", "label": "Everyone's scared", "title": "AI will replace marketers", "w": 700},
    {"type": "stamp", "at": "It won't", "text": "IT WON'T", "color": "#2F6B3F"},
    {"type": "card", "at": "master's thesis", "icon": "✎", "label": "My master's thesis", "title": "AI automation and the work of marketers", "sub": "Germany · finishing it now", "w": 760},
    {"type": "list", "at": "Here's what I believe", "label": "AI takes", "w": 760,
     "rows": [{"t": "The heavy lifting", "at": "heavy lifting"}, {"t": "The repetitive tool work", "at": "repetitive tool work"}]},
    {"type": "quote", "at": "So what's left", "text": "So what's<br><i>left?</i>"},
    {"type": "tags", "at": "Psychology", "w": 880, "gap": 0.5, "items": ["Psychology", "Taste", "Creativity"]},
    {"type": "tags", "at": "ElevenLabs", "w": 900, "gap": 0.15, "items": ["Claude Code", "Claude", "ChatGPT", "ElevenLabs", "Gemini"]},
    {"type": "card", "at": "here's the twist", "label": "Plot twist", "labelColor": "#D9473A", "title": "Every episode this week was my AI voice clone", "w": 760},
    {"type": "wave", "at": "voice clone", "beside": True, "label": "My voice clone", "until": "Sunday", "w": 760},
    {"type": "card", "at": "On Sunday", "label": "Sunday", "title": "Why I cloned my voice", "w": 660},
    {"type": "quote", "at": "Hustle less", "text": "Hustle less.<br><i>Think more.</i>"},
    {"type": "card", "at": "What's one task", "label": "Comment", "title": "One task you'd hand to AI tomorrow?", "w": 720},
    {"type": "card", "at": "tomorrow", "beside": True, "label": "Sunday", "labelColor": "#D9473A", "title": "I was insecure about my voice", "w": 680},
  ]}

for k, b in B.items():
    b.update({"template": "series3", "series": SERIES})
(HERE / "scripts.json").write_text(json.dumps(S, indent=1, ensure_ascii=False))
(HERE / "beats.json").write_text(json.dumps(B, indent=1, ensure_ascii=False))
print({k: len(v.split()) for k, v in S.items()})
