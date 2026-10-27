"""Session 1 full scripts (27 Oct 2026): hot takes, reacts, story, psychology, Worth It or Slop. Writes 2026-11-session-1.json.
Marks: / short pause, // full pause, *stress*, (up)/(down), [lens], [point], [count], [smile]. Facts only from brand-profile.md."""
import json
from pathlib import Path

def L(say, see, how=None):
    return {k: v for k, v in (("say", say), ("see", see), ("how", how)) if v}

def S(key, series, fmt, length, card, hook, alts, lines, cta, notes="", broll=None, kw=None):
    return {"week": "Session 1", "key": key, "keyword": kw or "question in the comments", "series": series, "format": fmt, "length": length,
            "title_card": card, "post": "", "cta": cta, "model": "", "hook": hook, "hook_alts": alts, "lines": lines, "notes": notes, "broll": broll or []}

HT = "Hot Take (A split: you below, statement card above)"
X = []
X.append(S("HT-MASTERS", "Hot Take", HT, "20 to 25 s", "HOT TAKE", "A master's degree / is the most expensive way / to stay *unemployed*.",
  ["I paid 40,000 euros / to get rejected 220 times.", "Nobody tells you this before your master's."],
  [L("A master's degree / is the most expensive way / to stay *unemployed*.", "HOT TAKE stamp, the line as a card", "(up) [lens], deadpan"),
   L("I'm saying this / *while* doing one.", "Your face, eyebrow up", "[smile], small shrug"),
   L("40,000 euros of debt. / 220 rejections. //", "Two counters: €40,000 and 220", "[count] on fingers, (down)"),
   L("The degree didn't get me a single interview. / The *work* I post here / gets me messages.", "Inbox: 0 interviews vs DMs arriving", "[point] up at the card"),
   L("So agree, / or tell me I'm wrong.", "AGREE / DISAGREE buttons", "[lens], lean in")],
  "Question: agree or disagree?", "Only say 'gets me messages' if that's true on the day; otherwise say 'is what I'm betting on now'."))
X.append(S("HT-GERMAN", "Hot Take", HT, "20 to 25 s", "HOT TAKE", "Germany says it needs skilled workers. // It means *German-speaking* ones.",
  ["I'm skilled. I don't speak German. Guess what happened.", "Germany doesn't want immigrants. It wants German speakers."],
  [L("Germany says / it needs skilled workers. // It means *German-speaking* ones.", "Headline-style card: 'Germany needs skilled workers' with 'German-speaking' scribbled in", "(up) [lens]"),
   L("Five years in influencer marketing. / 850 plus creator deals. / No German.", "Your CV lines ticking in, the last one red", "[count]"),
   L("Most of my 220 rejections / were automatic. / A filter, / not a person.", "A funnel that drops CVs into a bin", "(down), head shake"),
   L("Is that fair? / Honestly, / I get it. / But then don't call it a shortage.", "The word SHORTAGE with a question mark", "small shrug, [smile]"),
   L("Expats, / tell me I'm wrong.", "Comment bubble", "[lens]")],
  "Question: tell me I'm wrong", "Don't claim the language was the reason for each rejection. It's your opinion."))
X.append(S("HT-APPLY", "Hot Take", HT, "20 s", "HOT TAKE", "Sending 200 applications / is *lazier* than building one project.",
  ["I sent 220 applications. Here's what I should have done.", "Stop applying. Start showing."],
  [L("Sending 200 applications / is *lazier* than building one project.", "Stack of 200 CVs vs one glowing project card", "(up) [lens]"),
   L("I know. / I sent *220*.", "Counter to 220", "[smile], guilty"),
   L("Each one took ten minutes / and said the same thing / as the last.", "Copy, paste, send animation looping", "flat voice"),
   L("This account took more work / than all of them. // And people actually *see* it.", "Your profile grid filling up", "[point] down at the grid"),
   L("Applications or projects? / Comments.", "Two buttons", "[lens]")],
  "Question: applications or projects?"))
X.append(S("HT-AIJOB", "Hot Take", HT, "20 s", "HOT TAKE", "AI won't take your job. // *Refusing* to use it will.",
  ["The scariest person in your office is the one using AI.", "AI isn't coming for your job. Your colleague is."],
  [L("AI won't take your job. // *Refusing* to use it will.", "Card, then a robot hand passing a laptop to a person", "(up) [lens]"),
   L("I'm not an engineer. / I'm a marketer.", "Your job title card: Influencer Marketing", "[point] at yourself"),
   L("And AI now edits my videos, / drafts my posts / and answers my comments.", "Three quick screen shots of your tools", "[count]"),
   L("The marketers I'd worry about / aren't the ones learning this. / It's the ones *waiting*.", "An hourglass", "(down)"),
   L("Are you using it at work yet? / Yes or no.", "YES / NO buttons", "[lens]")],
  "Question: yes or no?"))
X.append(S("HT-BRAND", "Hot Take", HT, "20 s", "HOT TAKE", "Your CV is dead. // Your *profile* is the new one.",
  ["Nobody reads your CV. They read your Instagram.", "Personal branding is the new CV."],
  [L("Your CV is dead. // Your *profile* is the new one.", "A CV going into a shredder, a phone profile rising", "(up) [lens]"),
   L("220 companies saw my CV. / Two pages. / Automatic no.", "CV, then a NO stamp", "[count] 2 on fingers"),
   L("This account / shows what I can actually do, / every week.", "Your reels as a grid", "[point] down"),
   L("Nobody can filter that out / with a keyword.", "A keyword filter that fails, sparks", "[smile]"),
   L("CV or profile: / which gets you hired in 2027? / Comments.", "Two cards", "[lens]")],
  "Question: CV or profile?"))
X.append(S("HT-DEBT", "Hot Take / Real Talk", HT, "25 s", "REAL TALK", "Debt isn't the problem. // Doing *nothing* about it is.",
  ["I'm 40,000 euros in debt. Here's my one rule.", "40k in debt and I'm not panicking. Here's why."],
  [L("Debt isn't the problem. // Doing *nothing* about it is.", "Card, then a debt meter at €40,000", "(down) [lens], calm"),
   L("I'm 27. / I owe 40,000 euros / for my master's and living here.", "The meter, then a cap and a flat icon", "honest, small nod"),
   L("Some nights / that number is all I think about.", "Phone screen at night, the number glowing", "(down), look away then back"),
   L("So I gave it a deadline. / 52 weeks. / 3,000 euros a month. / In public.", "Goal card: €3,000 / month, Week 2 of 52", "(up) [count]"),
   L("If you've got debt too, / what's your plan? / No judgement here.", "Comment bubble", "[lens], warm")],
  "Question: what's your plan?", "Real numbers only. The currency is euros (confirmed 27 Oct)."))
X.append(S("HT-COVER", "Hot Take", HT, "15 to 20 s", "HOT TAKE", "Cover letters are *dead*. // Nobody's reading them.",
  ["I wrote 220 cover letters. Here's who read them.", "Stop writing cover letters."],
  [L("Cover letters are *dead*. // Nobody's reading them.", "A cover letter with a cobweb", "(up) [lens]"),
   L("I wrote them for 220 applications. / Most of the answers came back / automatic.", "Auto-reply emails stacking", "[smile], tired"),
   L("A machine doesn't care / that I'm *passionate*.", "The word 'passionate' crossed out", "eye-roll"),
   L("What should replace it? / Tell me.", "Comment bubble", "[lens]")],
  "Question: what should replace it?"))
X.append(S("HT-BALI", "Hot Take", HT, "20 to 25 s", "HOT TAKE", "'Just move to Bali' / is *terrible* advice. // I'm going to Sri Lanka anyway.",
  ["Remote work from paradise is a lie. Here's the true part.", "Everyone wants the beach laptop life. Nobody shows the bill."],
  [L("'Just move to Bali' / is *terrible* advice.", "A beach laptop photo with a red X", "(up) [lens]"),
   L("I'm flying to Sri Lanka / on December 6th. // So, / yes. / I see it.", "Boarding pass: Dec 6", "[smile], caught"),
   L("The difference? / I'm not going to *escape*. / I'm going to *test* it.", "Two words: ESCAPE crossed, TEST ticked", "[point]"),
   L("Can I earn from a café / with no clients yet? // That's the whole experiment.", "Café table, laptop, a question mark", "(down)"),
   L("Follow along. / If it fails, / you'll see that too.", "Follow button", "[lens]")],
  "Follow + question", "Flight date confirmed by Vish: 6 Dec, for a month."))
X.append(S("HT-START", "Hot Take / Real Talk", HT, "20 s", "REAL TALK", "You don't need confidence to start. // You need *no other option*.",
  ["I wanted to post for years. Here's what finally made me start.", "Confidence is overrated."],
  [L("You don't need confidence to start. // You need *no other option*.", "Card, slow push-in", "(down) [lens]"),
   L("I wanted to make content / for *years*. / I kept stopping.", "Old drafts and deleted videos", "honest"),
   L("Then 220 companies said no. / And suddenly / posting felt less scary / than doing nothing.", "The 220 counter, then a REC dot", "(up)"),
   L("What would make *you* start?", "Comment bubble", "[lens], warm")],
  "Question: what would make you start?"))
X.append(S("HT-FOLLOW", "Hot Take", HT, "15 to 20 s", "HOT TAKE", "Followers are a *vanity* number. // Comments pay the bills.",
  ["After 850 creator deals, I never checked followers first.", "Brands don't care about your followers."],
  [L("Followers are a *vanity* number. // Comments pay the bills.", "Follower count crossed out, comment count glowing", "(up) [lens]"),
   L("I signed 850 plus creator deals / on the brand side.", "850+ badge", "[point] at yourself"),
   L("The first thing I checked / was never followers. / It was whether people *talked back*.", "Comment section scrolling", "lean in"),
   L("So comment something. / Anything. / Prove my point.", "Comment bubble", "[smile] [lens]")],
  "Question: comment anything"))

R = "React (green-screen cut-out over their clip, then you full frame)"
X.append(S("RE-GARY", "Reacts", R, "30 to 40 s", "REACT", "Gary Vee told people / to document, / not create. // I'm doing it with *40k of debt*.",
  ["Gary Vee's best advice, tested by a broke 27-year-old.", "Document, don't create. Here's what that really looks like."],
  [L("[THEIR CLIP, 5 to 8 s: Gary Vee on 'document, don't create']", "Their clip in a frame, credited", "listen, small nod"),
   L("He's right. / And it's easier said / when you're *Gary Vee*.", "Hard cut to you", "[smile] [lens]"),
   L("Here's what documenting looks like for me. / 220 rejections. / 40,000 euros of debt. / Week 2 of 52.", "Three cards stacking", "[count]"),
   L("It's not inspiring. / It's just *true*.", "Quiet frame", "(down)"),
   L("But true is the only thing / I've got that nobody can copy.", "Your grid", "[point] down"),
   L("Would you post your real numbers? / Yes or no.", "YES / NO", "[lens]")],
  "Question: yes or no?", "The edit sources a real 'document, don't create' clip, credited. If none is usable, it uses a quote card."))
X.append(S("RE-HORMOZI", "Reacts", R, "30 s", "REACT", "Hormozi says / volume negates luck. // I sent *220* applications.",
  ["I tested Hormozi's rule. 220 times.", "Volume negates luck? Here's my volume."],
  [L("[THEIR CLIP: Hormozi, 'volume negates luck']", "Their clip, credited", "listen"),
   L("I tried that. / 220 applications.", "Counter to 220", "[smile], raised eyebrow"),
   L("And here's what I learned. // Volume works / when each try teaches you something.", "Two lines: 220 copies vs 220 experiments", "(down) [lens]"),
   L("Mine were the same application, / 220 times.", "Copy-paste loop", "facepalm"),
   L("Now my volume is posts. / Every one is different. / Every one teaches me something.", "Your reels flipping", "(up)"),
   L("Is he right? / Tell me.", "Comment bubble", "[lens]")],
  "Question: is he right?"))
X.append(S("RE-HUANG", "Reacts", R, "30 s", "REACT", "Nvidia's CEO says / you won't lose your job to AI. // You'll lose it to *someone using AI*.",
  ["The richest man in AI just warned marketers.", "This one sentence should scare every marketer."],
  [L("[THEIR CLIP or quote card: Jensen Huang on losing your job to someone who uses AI]", "Their clip or a quote card, credited and dated", "listen"),
   L("I'm the someone. // Kind of.", "Hard cut to you", "[smile] [lens]"),
   L("I'm a marketer, / not an engineer. / And in a few months / I built my own editing system / with Claude.", "Screen: your edit system running", "[point]"),
   L("I didn't learn to code. / I learned to *ask*.", "A chat window, a prompt typing", "(down)"),
   L("Are you the someone, / or the one being replaced?", "Two buttons", "[lens]")],
  "Question: which one are you?", "Verify the quote and its date at edit time; use a quote card if there's no clean clip."))
X.append(S("RE-AMODEI", "Reacts", R, "35 s", "REACT", "The CEO of Anthropic / said AI could wipe out / *half* of entry-level jobs.",
  ["220 rejections, and then I heard this.", "The AI boss warned about entry-level jobs. Here's my take as a job seeker."],
  [L("[QUOTE CARD: Dario Amodei, Anthropic, Axios, May 2025: AI could wipe out half of entry-level white-collar jobs]", "Quote card with source and date", "read, (down)"),
   L("I'm job hunting / *right now*. // So that hit.", "Hard cut to you", "[lens], serious"),
   L("220 rejections. / Most of them / already automatic.", "Auto-reply emails", "[count]"),
   L("But here's my take. // Entry-level *tasks* are going. / The people who run the AI / still get hired.", "Tasks fading out, a person at the controls", "(up) [point]"),
   L("So I'm learning to run it. / In public. / 52 weeks.", "Week 2 of 52", "[smile]"),
   L("Scared or excited? / Comments.", "Two buttons", "[lens]")],
  "Question: scared or excited?", "Quote card only, with its source; check the date and wording at edit time."))
X.append(S("RE-ALTMAN", "Reacts", R, "30 s", "REACT", "Sam Altman thinks / one person / will build a *billion-dollar* company. // I'm one person.",
  ["One-person billion-dollar company? I'll settle for 3,000 euros.", "Sam Altman's prediction, from someone 40k in debt."],
  [L("[QUOTE CARD or CLIP: Sam Altman on the one-person billion-dollar company]", "Quote card, credited and dated", "listen"),
   L("I'm one person. // I'll take *3,000 euros a month*.", "Goal card: €3,000", "[smile] [lens]"),
   L("But he's onto something. / My editor, / my assistant, / my comment replies: / all AI. / Built by me.", "Four tool cards, one by one", "[count]"),
   L("The one-person company / isn't the dream. / It's the *only* option / when nobody hires you.", "A single desk, lamp on", "(down)"),
   L("Would you build alone, / or with a team?", "Two buttons", "[lens]")],
  "Question: alone or team?"))
X.append(S("RE-100JOBS", "Reacts", R, "30 s", "REACT", "'Apply to 100 jobs a day with AI.' // I'm about to *test* that.",
  ["Everyone says use AI to mass apply. I'm testing it for 7 days.", "100 applications a day with AI? Let's see."],
  [L("[THEIR CLIP: any creator selling AI mass-apply tools, credited]", "Their clip, framed", "eyebrow up"),
   L("I've done 220 / by hand. / So let's see if the robots / do better.", "220 counter", "[smile] [lens]"),
   L("For 7 days / AI applies for me. / I count every reply.", "Day 1 to 7 tracker", "[count]"),
   L("If it works, / you get the setup. / If it's slop, / you'll know.", "WORTH IT / SLOP boxes", "(up)"),
   L("Guess now: / how many replies out of 100?", "Comment bubble with a number", "[lens]")],
  "Question: guess the number", "This opens the 'Worth It or Slop?' series (WIS1). Record the check-ins every evening."))
X.append(S("RE-GERMAN", "Reacts", R, "30 s", "REACT", "'Learn German, / or you'll *never* get a job here.' // Let's talk about that.",
  ["Expats keep telling me this. Here's my answer.", "Is German really the only way in?"],
  [L("[THEIR CLIP: an expat creator saying you need German to work in Germany, credited]", "Their clip", "listen, small wince"),
   L("Okay. / That one hurt.", "Hard cut to you", "[smile] [lens]"),
   L("I don't speak German. / And most of my 220 rejections / were automatic.", "Counter + auto-reply", "honest"),
   L("So maybe they're right. // Or maybe / I stop asking German companies / and work for anyone, / from anywhere.", "A map zooming out from Germany", "(up) [point]"),
   L("Learn German, / or go global? / What would you do?", "Two buttons", "[lens]")],
  "Question: German or global?"))
X.append(S("RE-30DAYS", "Reacts", R, "25 s", "REACT", "'Post every day for 30 days / and you'll *blow up*.' // Here's my day count.",
  ["I'm posting daily. Here are my real numbers.", "Daily posting for 30 days: the honest update."],
  [L("[THEIR CLIP: a creator promising growth from 30 days of daily posts]", "Their clip", "arms crossed"),
   L("I'm doing it. / Every day.", "A calendar filling", "[lens]"),
   L("Day [X]: / [FOLLOWERS] followers. / [BEST VIEWS] on my best video.", "Real numbers from your insights", "(down) read them straight"),
   L("Not blown up. / Not quitting.", "Two words", "[smile]"),
   L("Should I keep going? / Comments.", "Comment bubble", "[lens]")],
  "Question: keep going?", "Fill [X] and the numbers on the day you film. Real numbers only."))

ST = "Story (A split, your take full frame, B-roll for each place you name)"
X.append(S("ST-QUIT", "Real Talk", ST, "40 to 50 s", "REAL TALK", "I quit a good salary / to become *40,000 euros* in debt.",
  ["The worst and best decision I made.", "I had a good job. I left it. Here's what happened."],
  [L("I quit a good salary / to become *40,000 euros* in debt.", "Payslip fades, debt meter rises", "(down) [lens]"),
   L("I was an influencer marketing manager. / 850 plus creator deals. / Good money.", "Job card, 850+ badge", "[count]"),
   L("[YOUR WORDS: the day you decided to quit. Where you were, what you told yourself. 2 or 3 sentences.]", "B-roll you film: your old desk photo, or a window", "talk, don't perform"),
   L("I moved to Germany / for a master's. / And then the bills started.", "Boarding pass, then bills raining", "(up)"),
   L("220 rejections later, / do I regret it? //", "Pause on your face", "hold 1 s, [lens]"),
   L("[YOUR WORDS: honest answer. Yes, no, or both, and why.]", "Full frame, no graphics", "(down)"),
   L("Would you have quit? / Tell me.", "Comment bubble", "[lens]")],
  "Question: would you have quit?", "The [YOUR WORDS] lines are yours: say them how you'd say them to a friend. Everything else is fixed facts."))
X.append(S("ST-WEEK1", "Real Talk", ST, "40 s", "REAL TALK", "My first week in Germany: / no friends, / no family, / no *German*.",
  ["Nobody tells you how lonely moving abroad is.", "Moving abroad, the part nobody films."],
  [L("My first week in Germany: / no friends, / no family, / no *German*.", "Three crossed-out cards", "(down) [count]"),
   L("[YOUR WORDS: one scene from that week. The supermarket, the paperwork, the first night. Be specific.]", "B-roll: a supermarket aisle, a German letter", "talk naturally"),
   L("That's when it hit me. / I'd left a good life / for a blank one.", "An empty room, lamp on", "(down)"),
   L("A year later, / I'm still here. / Still figuring it out. / But now / I'm doing it in public.", "Week 2 of 52", "(up) [smile]"),
   L("If you moved abroad, / what was your hardest week?", "Comment bubble", "[lens]")],
  "Question: your hardest week?", "Don't show your city (rule)."))
X.append(S("ST-ROBOT", "Real Talk", ST, "35 s", "REAL TALK", "220 rejections. // Most were sent by a *robot*.",
  ["I got rejected 220 times without a human reading my CV.", "Nobody read my CV. A machine did."],
  [L("220 rejections. // Most were sent by a *robot*.", "Auto-reply emails flood, AUTOMATED stamp", "(down) [lens]"),
   L("Same email. / Different company name. / Sometimes minutes after I applied.", "Timestamps close together", "[count], dry"),
   L("[YOUR WORDS: how that felt the 100th time.]", "Your face, full frame", "honest"),
   L("So I stopped applying / and hired the robots instead.", "Your AI tools lighting up", "(up) [smile]"),
   L("Now AI edits my videos, / drafts my posts / and answers my comments. / I built all of it.", "Three screens", "[point]"),
   L("Week 2 of 52. / What should I sell first? / A or B.", "Vote: A AI content systems / B influencer consulting", "[lens]")],
  "The vote: A or B", "Only say 'minutes after I applied' if it happened to you. Otherwise cut that line."))

PSY = "Psychology Breakdown (talking head + paper card of the study)"
X.append(S("PSY-TAKEN", "Psychology Breakdown", PSY, "40 s", "PSYCHOLOGY", "Brands want you *taken*.",
  ["Why brands want creators other brands already pay.", "The psychology of why brands copy each other."],
  [L("Brands want you *taken*.", "Big serif words", "(up) [lens], half smile"),
   L("After 850 plus creator deals, / I noticed something weird. / The creator *other* brands just paid / suddenly everyone wanted.", "Creator card with three brand stickers landing on it", "[point]"),
   L("So I looked it up. / It's called *mate-choice copying*.", "Paper card: 'Mate-choice copying'", "(down)"),
   L("In a 2007 study, / people rated faces as more attractive / when someone else / was already smiling at them.", "Paper card: Jones et al., 2007, Proceedings of the Royal Society B", "explain calmly"),
   L("Brands do the same. / Social proof / is the strongest thing on your media kit.", "A media kit with 'Worked with' row glowing", "(up) [count]"),
   L("So put your past brand work *first*. / Even small ones.", "Media kit reordered", "[lens]"),
   L("Have you seen this happen? / Tell me.", "Comment bubble", "[lens]")],
  "Question: seen this?", "Check the study wording before posting; keep the claim this simple."))
X.append(S("PSY-PAIN", "Psychology Breakdown", PSY, "35 to 40 s", "PSYCHOLOGY", "Rejection hurts / like *physical pain*. // Literally.",
  ["220 rejections, and science says I'm not being dramatic.", "Why rejection feels like a punch."],
  [L("Rejection hurts / like *physical pain*. // Literally.", "Big serif words, a slow zoom", "(down) [lens]"),
   L("After 220 job rejections, / I wanted to know / why it felt so heavy.", "220 counter", "honest"),
   L("So I looked it up. / In 2003, researchers scanned people's brains / while a game left them out.", "Paper card: Eisenberger, Lieberman and Williams, Science, 2003", "explain"),
   L("Being left out / lit up a brain area / that's also active in *physical* pain.", "A simple brain outline, one area glowing", "[point]"),
   L("So if a no hurts you, / you're not weak. / Your brain is doing its job.", "Text: not weak", "(up), warm"),
   L("What helps you after a rejection? / Comments.", "Comment bubble", "[lens]")],
  "Question: what helps you?"))
X.append(S("PSY-CLIFF", "Psychology Breakdown", PSY, "30 s", "PSYCHOLOGY", "Your brain *hates* unfinished stories. // That's why you're still watching.",
  ["Why you can't stop watching series.", "The trick every Netflix show uses on you."],
  [L("Your brain *hates* unfinished stories. // That's why you're still watching.", "A progress bar stuck at 90%", "[smile] [lens]"),
   L("It's called the *Zeigarnik effect*.", "Paper card: Bluma Zeigarnik, 1927", "(down)"),
   L("In 1927, / a psychologist noticed people remembered / interrupted tasks / better than finished ones.", "Two to-do lists, the unfinished one glowing", "explain"),
   L("Every series cliffhanger / uses it. / So does my 52-week challenge.", "Week 2 of 52, '?' at the end", "[point] at yourself"),
   L("I don't know how it ends either. // Follow to find out.", "Follow button", "[lens], grin")],
  "Follow", "Later studies on this effect are mixed: keep the claim to what she observed."))

X.append(S("WIS-1", "Worth It or Slop?", "B demo: your screen + you in a bubble", "Opener 20 s + 7 check-ins of 15 s + a 40 s verdict", "WORTH IT OR SLOP?",
  "Everyone says / let AI apply to 100 jobs a day. // I'm testing it for *7 days*.",
  ["220 rejections by hand. Now the robots try.", "AI job applications: worth it or slop?"],
  [L("Everyone says / let AI apply to 100 jobs a day. // I'm testing it for *7 days*.", "WORTH IT / SLOP boxes, both empty", "(up) [lens]"),
   L("Rules: / real applications, / roles I'd actually take, / and I count every reply.", "Three rule cards", "[count]"),
   L("CHECK-IN, every evening: 'Day [N]. [X] sent. [Y] replies. [Z] interviews. [One honest line.]'", "Tracker updating", "selfie, tired is fine"),
   L("VERDICT: 'After 7 days: [numbers]. It's... [WORTH IT / SLOP], because [one reason].'", "The verdict box ticks", "hold the pause before the verdict"),
   L("Comment SLOP / and I'll send you the exact setup / so you can test it yourself.", "Comment bubble: SLOP", "[lens]")],
  "Comment SLOP (guide to build after the test)", "Only real numbers. Pick a tool you'd really use; tell me which before you start so I can check it's safe for your accounts.",
  ["Screen recording of the tool applying", "Your inbox every evening (blur names)"], kw="SLOP"))

out = {"title": "Session 1: full scripts", "sheets": X}
Path(__file__).with_name("2026-11-session-1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(X), "sheets")
txt = "\n".join(l["say"] for s in X for l in s["lines"] if not l["say"].startswith("[")) + "\n" + "\n".join(s["hook"] + "\n" + "\n".join(s["hook_alts"]) for s in X)
Path("/tmp/claude-0/-home-user/366652c1-4a9a-5293-b3f6-8b1b78fa3cc9/scratchpad/s1_say.txt").write_text(txt.replace("/", "").replace("*", ""))
