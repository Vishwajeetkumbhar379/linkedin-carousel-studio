"""The film's soundtrack: Vish's voice on top, the music bed ducked under it, a sound on every visible event.

    python3 video-projects/how-ai-edit/audio/mix.py

Every time comes from src/words.json through the same cue() the acts use, so a new voiceover re-times the
sound with the picture. Writes public/soundtrack.wav (what Film plays), audio/out/{music,sfx}.wav stems
and audio/out/cues.json (the cue sheet).
- Music: audio/music/bed.mp3 (ElevenLabs Music, generated for this film). It enters on the shatter (his
  take before it stays dry), tape-stops on "slow down" and spins back up when the wall run starts, and
  cuts dead for the frozen beat on "Silence". The bed pauses through both, like the picture does.
- Effects: Kenney CC0 packs (week-01-intro/assets/kenney) and synthesised ones (audio/designed.py), all
  labelled in the cue sheet.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designed as D  # noqa: E402
from dsp import SR, curve, db, fade, hp, lp, noise, put, read, reverb, stereo, write  # noqa: E402

PROJ = os.path.dirname(HERE)
KENNEY = os.path.join(PROJ, '..', 'week-01-intro', 'assets', 'kenney')
WORDS = json.load(open(os.path.join(PROJ, 'src', 'words.json')))
RISH_WORDS = len(json.load(open(os.path.join(PROJ, 'src', 'data', 'rish.json')))['words'])
LINES = json.load(open(os.path.join(PROJ, 'vo', 'lines.json')))


# --- the same cue() as src/lib.ts -------------------------------------------------------------------
def _norm(s):
    return ''.join(c for c in s.lower() if c.isalnum() or c == "'")


def cue(phrase, nth=None):
    p = [_norm(x) for x in phrase.split()]
    hits = [WORDS[i]['s'] for i in range(len(WORDS) - len(p) + 1) if all(_norm(WORDS[i + j]['w']) == x for j, x in enumerate(p))]
    if nth is None and len(hits) > 1:
        raise ValueError(f'cue "{phrase}" is said {len(hits)} times; pass nth')
    return hits[nth or 0]


def cue_end(phrase):
    i = next(k for k, w in enumerate(WORDS) if w['s'] == cue(phrase))
    return WORDS[i + len(phrase.split()) - 1]['e']


def sm_inv(a, b, y):
    """Where smoothstep(a, b) reaches y (the acts use sm(); this finds when a count ticks over)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if m * m * (3 - 2 * m) < y else (lo, m)
    return a + (b - a) * (lo + hi) / 2


VO_END = WORDS[-1]['e']
TOTAL = round((VO_END + 1.2) * 30) / 30


# --- sources -------------------------------------------------------------------------------------------
_cache = {}


def kenney(name):
    """A Kenney CC0 sound, e.g. 'interface-sounds/tick_001'."""
    if name not in _cache:
        pack, f = name.split('/')
        _cache[name] = read(os.path.join(KENNEY, pack, 'Audio', f + '.ogg'))
    return _cache[name]


def peak(x, dbfs):
    return x * db(dbfs) / max(1e-9, np.abs(x).max())


def pan(x, p):
    m = x.mean(1)
    return stereo(m, p)


def shutter(seed):
    """A camera shutter: a bright click and the mirror slap 30 ms later."""
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    a = hp(noise(n, seed), 2500) * np.exp(-t / 0.004)
    b = np.zeros(n)
    k = int(0.03 * SR)
    b[k:] = lp(hp(noise(n - k, seed + 1), 900), 6000) * np.exp(-t[: n - k] / 0.008)
    return stereo(fade(a + 0.7 * b, 0.0005, 0.01))


def riffle(dur, count, seed, pan0=-0.4, pan1=0.4):
    """Cards fanning out: short papery flicks that spread out in time and across the stereo field."""
    out = np.zeros((int((dur + 0.1) * SR), 2))
    rng = np.random.default_rng(seed)
    for i in range(count):
        x = i / max(1, count - 1)
        at = dur * (x ** 0.8) + rng.uniform(-0.01, 0.01)
        n = int(0.025 * SR)
        t = np.arange(n) / SR
        flick = lp(hp(noise(n, seed + i), 1800), 7000) * np.exp(-t / 0.006)
        put(out, stereo(flick, pan0 + (pan1 - pan0) * x) * rng.uniform(0.6, 1.0), max(0, at))
    return out


def rumble(dur, seed, clicks=0.0):
    """A cart rolling on the rail: a low rumble and, if clicks > 0, a rail joint every `clicks` seconds."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.35)
    y = lp(noise(n, seed), 180) * 3 + lp(hp(noise(n, seed + 1), 300), 1200) * 0.25
    out = stereo(y * env)
    if clicks:
        k = clicks
        while k < dur - 0.1:
            put(out, peak(kenney('impact-sounds/impactMetal_light_002'), -26), k)
            k += clicks
    return out


# --- the cue sheet: (time, sound, gain dB, what it is, source) -------------------------------------------
CUES = []


def at(t, x, gain, what, src):
    CUES.append((round(t, 3), x, gain, what, src))


def build_cues():
    # l01: the frame freezes on "39", cracks from his mouth and shatters into 39 clips that land in the roll
    freeze = cue('39') - 0.06
    l01_end = cue('No editing app') - 0.08
    dur = l01_end - freeze - 0.05
    at(freeze, D.sub_drop(1.6), -8, 'the freeze lands', 'designed')
    at(freeze, kenney('impact-sounds/impactGlass_heavy_000'), -6, 'the frame cracks', 'kenney')
    at(freeze + 0.03, D.glass_ping('C7', 1.6), -20, 'crack shimmer', 'designed')
    at(freeze + 0.14 * dur, D.whoosh(0.55 * dur, 600, 7000, -0.5, 0.5, seed=8), -10, 'the shards fly', 'designed')
    from_ = freeze + (0.14 + 0.26 * 0.985) * dur
    for i in range(39):  # one tick per shard landing, rising as the roll fills
        tt = from_ + (i / 38) * 0.54 * dur
        at(tt, D.tick(0.9 + 0.8 * i / 38), -24 + 4 * (i / 38), f'shard {i + 1} lands', 'designed')
    # l02: the sealed app rises out of the phone; on "rewind" the playhead runs back to 0:00
    no = cue('No editing app')
    at(no, D.whoosh(1.0, 200, 2600, 0, 0, seed=12), -14, 'the sealed app rises', 'designed')
    at(no + 0.85, kenney('interface-sounds/maximize_004'), -16, 'the app settles', 'kenney')
    rw, see = cue('rewind'), cue('See what touched it')
    at(rw - 0.12, D.dive(1.2), -14, 'the camera drops to the rail', 'designed')
    at(rw, D.scramble(see + 0.6 - rw, reverse=True), -16, 'the playhead runs back', 'designed')
    at(see + 0.6, kenney('interface-sounds/select_002'), -14, 'back at 0:00', 'kenney')
    # l03: the cart rolls to the waveform; every word lands as a stamped glass box
    t0 = cue('First AI listened')
    at(t0, rumble(1.5, 30, clicks=0.32), -12, 'the cart rolls to the audio lane', 'designed + kenney')
    every, end_t = cue('Every word'), cue('end time')
    for i in range(RISH_WORDS):
        s = every + (i / RISH_WORDS) * (end_t - every + 0.3)
        at(s + 0.2, D.thud(140, 0.25), -22, f'word box {i + 1} stamped', 'designed')
        at(s + 0.2, kenney('interface-sounds/tick_002'), -22, f'timestamp {i + 1}', 'kenney')
    # l04: RISH glows red; the fix types itself; one clack turns R into V
    rish, one, fixed = cue('Rish'), cue('One line fixed it'), cue('fixed it')
    at(rish - 0.2, D.alert_low('Bb2', 0.42), -16, 'RISH glows red', 'designed')
    n = 17  # characters in {"Rish,": "Vish,"}
    for i in range(1, n + 1):
        at(sm_inv(one - 0.2, fixed, (i - 0.5) / n), kenney(f'ui-audio/click{1 + i % 5}'), -24, f'key {i}', 'kenney')
    at(fixed + 0.05, kenney('ui-audio/switch7'), -8, 'the flap falls: R to V', 'kenney')
    at(fixed + 0.07, D.thud(90, 0.4), -14, 'flap weight', 'designed')
    # l05: the blade snaps to the gaps between words and the cuts lift out
    t0, not_b, betw = cue('Then it cut everything'), cue('not in between'), cue('between the words')
    at(t0 + 0.15, D.convert(True, 0.3), -16, 'blade snaps to the first gap', 'designed')
    at(t0 + 0.5, D.laser_cut(), -10, 'the 0.05 s sliver cut', 'designed')
    at(not_b + 0.3, D.convert(True, 0.3), -16, 'blade snaps to the second gap', 'designed')
    at(not_b + 0.6, D.laser_cut(0.4, seed=112), -10, 'the tail cut', 'designed')
    at(not_b + 0.62, D.whoosh(betw - not_b - 0.6, 400, 3000, 0.2, 0.6, seed=14), -18, 'the cut lifts out', 'designed')
    # l06: his frames fan out like a deck, square up, swing apart into three panes
    t0, every, so, behind = cue('Then it cut me'), cue('every single frame'), cue('and the caption sits'), cue('behind me')
    at(t0 + 0.2, riffle(every + 0.4 - t0 - 0.2, 26, 40), -12, 'the deck of frames fans out', 'designed')
    at(so - 0.05, D.thud(180, 0.2), -16, 'the deck squares up', 'designed')
    at(so + 0.1, D.whoosh(behind - so + 0.1, 300, 4000, -0.6, 0.6, seed=16), -12, 'three panes swing apart', 'designed')
    # l07: browser chrome grows round the caption; thirty shutter clicks, one second of video
    page, photo = cue('tiny webpage'), cue('photographed')
    sec = cue('30 times a second') + 0.6
    at(page - 0.3, kenney('interface-sounds/open_002'), -12, 'browser chrome appears', 'kenney')
    for i in range(1, 30):
        at(sm_inv(photo, sec + 0.4, i / 30), shutter(200 + i), -16, f'photograph {i}', 'designed')
    at(photo, D.riser(sec + 0.4 - photo, 'F4', 'F5'), -22, 'the stack builds', 'designed')
    at(sec + 0.4, kenney('interface-sounds/confirmation_002'), -14, '30 photographs = 1 second', 'kenney')
    # l08: three ticks at one frame a second, then the run along 1,800 photographs to 30:00
    slow_from = cue('down time') + 0.35
    at(cue("Let's slow down") + 0.3, D.slow_down(1.6), -12, 'time slows', 'designed')
    for k in range(3):
        at(slow_from + k, D.tick(0.55) * 2, -6, f'one frame a second, tick {k + 1}', 'designed')
        at(slow_from + k, D.thud(60, 0.6), -10, f'tick weight {k + 1}', 'designed')
    run0, mins = max(slow_from + 3, cue('At one frame')), cue('30 minutes')
    at(run0, D.whoosh(mins + 0.6 - run0, 200, 3500, -0.4, 0.4, seed=18), -14, 'the run along the wall', 'designed')
    at(run0, D.counter(mins + 0.6 - run0, 6, 40, 0.8, 1.4), -22, 'the clock runs', 'designed')
    at(mins + 0.6, kenney('impact-sounds/impactBell_heavy_001'), -18, 'the clock hits 30:00', 'kenney')
    # l09: the playhead crosses the hole in the music; everything stops for a beat
    t0, sil = cue('And the sound'), cue('Silence')
    at(t0, rumble(sil - t0, 50, clicks=0.4), -14, 'the cart rolls to the hole', 'designed + kenney')
    at(sil + 0.9, D.thud(70, 0.5), -12, 'sound and motion come back', 'designed')
    # l10: past twelve framed drafts, into v12, which becomes his room; the name tag slaps on
    t0, hi = cue("And it didn't take"), cue("Hi I'm Vish")
    vish = cue_end("Hi I'm Vish") - 0.25
    for v in range(1, 10):  # the camera passes drafts 1..9 (see a10.tsx: pos(v), shot A to B)
        s = (2.6 + (v - 1) * 1.7) / 17.7
        at(sm_inv(t0, hi - 0.4, s) - 0.15, D.whoosh(0.4, 500, 3500, (-0.8 if v % 2 else 0.8), 0, seed=60 + v), -22, f'past draft v{v}', 'designed')
    at(hi - 0.6, D.whoosh(0.7, 300, 6000, 0, 0, seed=80), -10, 'into v12', 'designed')
    at(hi - 0.05, D.glass_ping('F6', 1.4), -22, 'v12 opens into his room', 'designed')
    at(vish - 0.05, D.pop(380), -10, 'the name tag slaps on', 'designed')
    at(vish - 0.04, kenney('impact-sounds/impactGeneric_light_002'), -10, 'name tag weight', 'kenney')
    # l11: the progress bar runs out at one dot, "you"; E, D, I, T go down; the prompts fan out
    t0, job, comment, five = cue("And if you're"), cue('did its job'), cue('Comment EDIT'), cue('the prompts')
    at(t0, D.whoosh(job - t0, 200, 2500, -0.3, 0.3, seed=90), -18, 'the bar runs out', 'designed')
    at(job, D.chime('F5', 2.4), -16, 'one dot left: you', 'designed')
    for i in range(4):
        at(comment + 0.12 * i + 0.08, D.thud(150 - 15 * i, 0.22), -10, f'key {"EDIT"[i]} down', 'designed')
        at(comment + 0.12 * i + 0.08, kenney('ui-audio/switch3'), -14, f'key {"EDIT"[i]} click', 'kenney')
    at(five - 0.3, riffle(0.7, 12, 300, -0.5, 0.5), -12, 'the prompts fan out', 'designed')
    at(five + 0.4, D.chime('C6', 2.6), -20, 'the guide', 'designed')


# --- music: bed position as a function of film time (pauses with the picture) -----------------------
def music(vo_env):
    bed = read(os.path.join(HERE, 'music', 'bed.mp3'))
    n = int(TOTAL * SR)
    t = np.arange(n) / SR
    enter = cue('39') - 0.06
    slow0, slow_from = cue('slow'), cue('down time') + 0.35
    slow_to = max(slow_from + 3, cue('At one frame'))
    sil = cue('Silence')
    # speed of the tape: 1, down to 0 through the stop, held, a quick spin-up, then 1; held for the frozen beat
    speed = np.ones(n)
    a, b = int(slow0 * SR), int(slow_from * SR)
    speed[a:b] = np.linspace(1, 0, b - a) ** 1.6
    speed[b:int(slow_to * SR)] = 0
    c, d = int(slow_to * SR), int((slow_to + 0.25) * SR)
    speed[c:d] = np.linspace(0, 1, d - c) ** 0.7
    speed[int(sil * SR):int((sil + 0.9) * SR)] = 0
    pos = np.cumsum(speed) / SR
    # line the bed's own ending (it fades out at ~73.5 s) up with the end of the film
    off = 73.5 - pos[int((TOTAL - 0.3) * SR)]
    pos = pos + off
    pos[t < enter] = -1  # dry before the shatter
    idx = pos * SR
    ok = (idx >= 0) & (idx < len(bed) - 1)
    out = np.zeros((n, 2))
    i0 = np.floor(idx[ok]).astype(int)
    fr = (idx[ok] - i0)[:, None]
    out[ok] = bed[i0] * (1 - fr) + bed[i0 + 1] * fr
    # gain: enter with the shatter, duck under every word, go dead for the frozen beat
    g = np.ones(n)
    g *= curve(t, [(0, 0), (enter - 0.01, 0), (enter + 0.15, 1), (TOTAL, 1)])
    g[speed == 0] = 0
    duck = db(-10) + (1 - db(-10)) * (1 - vo_env)  # -10 dB under speech, open in the gaps
    out *= (g * duck)[:, None]
    # a little low-pass while the tape slows, so it sounds like a stop, not a fade
    k0, k1 = int((slow0 - 0.05) * SR), int(slow_from * SR)
    out[k0:k1] = lp(out[k0:k1], 1400)
    return out, off


def vo_envelope(vo):
    """0..1: how much speech is happening, smoothed (60 ms attack, 350 ms release) to drive the duck."""
    m = np.abs(vo).max(1)
    hop = int(0.01 * SR)
    frames = np.array([m[i:i + hop].max() for i in range(0, len(m), hop)])
    on = (frames > db(-38)).astype(float)
    env = np.zeros_like(on)
    for i in range(1, len(on)):
        k = 0.01 / 0.06 if on[i] > env[i - 1] else 0.01 / 0.35
        env[i] = env[i - 1] + (on[i] - env[i - 1]) * k
    return np.repeat(env, hop)[: len(m)]


if __name__ == '__main__':
    vo = read(os.path.join(PROJ, 'public', 'vo.wav'))
    n = int(TOTAL * SR)
    vo = np.pad(vo, ((0, max(0, n - len(vo))), (0, 0)))[:n]
    env = vo_envelope(vo)
    bed, off = music(env)
    build_cues()
    sfx = np.zeros((n + SR * 4, 2))
    sil0, sil1 = cue('Silence'), cue('Silence') + 0.9
    for tt, x, gain, what, src in CUES:
        if sil0 - 0.02 <= tt < sil1:
            continue  # the frozen beat is silent apart from his voice
        put(sfx, x, tt, db(gain))
    sfx = sfx[:n]
    sfx *= (1 - 0.45 * env)[:, None]  # effects step back a little under words, never over them
    # true silence through the frozen beat (his voice carries on)
    a, b = int((sil0 - 0.01) * SR), int(sil1 * SR)
    sfx[a:b] = 0
    bed_level, sfx_level = db(-7), db(0)  # the bed is mastered hot (-15 LUFS); bring it under the voice
    mix = vo + bed * bed_level + sfx * sfx_level
    pk = np.abs(mix).max()
    if pk > 0.98:
        mix *= 0.98 / pk
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    write(os.path.join(HERE, 'out', 'music.wav'), bed * bed_level)
    write(os.path.join(HERE, 'out', 'sfx.wav'), sfx * sfx_level)
    write(os.path.join(PROJ, 'public', 'soundtrack.wav'), mix)
    sheet = [{'t': tt, 'what': what, 'gain_db': gain, 'source': src} for tt, _, gain, what, src in CUES]
    json.dump({'music_offset_s': round(off, 3), 'cues': sheet}, open(os.path.join(HERE, 'out', 'cues.json'), 'w'), indent=1)
    print(f'soundtrack {TOTAL:.2f} s, {len(CUES)} sound events, bed offset {off:.2f} s, peak {20 * np.log10(pk):.1f} dBFS')
