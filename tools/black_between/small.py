"""The Black Between's smaller art (tools/build_black_between.py puts it on its sheets): the
minions (8x8), the shots (8x8, pointing right), the floor (8x8 tiles), the walls of light the
bosses raise, Vesper's dusk mines, and the Rift of the Between (16x16, four frames turning).

Pixel maps are one character a pixel ('.' clear), light from the upper left, as on the game's
other sprites; the client draws the black outline round characters and shots.
"""
import math
import random

from PIL import Image


def C(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def from_map(rows, pal, alpha=255):
    h, w = len(rows), len(rows[0])
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        assert len(r) == w, (r, len(r), w)
        for x, ch in enumerate(r):
            if ch != ".":
                img.putpixel((x, y), C(pal[ch]) + (alpha,))
    return img


def put(img, x, y, c, a=255):
    x, y = int(x), int(y)
    if 0 <= x < img.size[0] and 0 <= y < img.size[1]:
        img.putpixel((x, y), (C(c) if isinstance(c, str) else tuple(c)) + (a,))


# the son's gold and white, the daughter's dusk
GOLD = {"1": "#7a4c0e", "2": "#c08a1c", "3": "#ecc040", "4": "#fff0a8", "w": "#fffaf0", "p": "#f6f2e6",
        "P": "#c4baa4", "t": "#d09a28", "k": "#3a2410", "c": "#a8401a", "C": "#e07028", "B": "#ffffff",
        "b": "#dce2f0", "d": "#8a92aa", "g": "#a06a12", "G": "#ffd24a", "f": "#f2cca4"}
DUSK = {"1": "#1a0c30", "2": "#3a1d6a", "3": "#5f34a3", "4": "#9064d8", "s": "#f0e4ff", "e": "#ff6ae8"}

# ------------------------------------------------------------------------------------------------
# minions: (stand, attack)

TEMPLAR = ["...Cc...", "..tppt.B", "..pkkP.B", ".tpppPtB", ".PtGtPfG", "..pPpP..", "..p..P..", "..t..t.."]
TEMPLAR_HIT = ["...Cc...", "..tppt..", "..pkkP..", ".tpppPtB", ".PtGtPfB", "..pPpPGB", "..p..P.B", "..t..t.."]
SHADE = ["..3333..", ".344432.", ".31e1e2.", ".311112.", "..2s222.", "..2222..", "...21.2.", "....1..."]
SHADE_HIT = ["..3333..", ".344432.", ".3eeee2.", ".311112.", "..2s222.", ".22222..", "..21.2..", "...1...."]
SENTINEL = ["s...t...", "...t4t..", "..t434t.", ".t3VY3t.", "..t232t.", "s..t2t.s", "....t...", "..s....."]
SENTINEL_HIT = [".s..t..s", "...t4t..", "..t4W4t.", ".t3VY3t.", "..t232t.", "...t2t..", "s...t..s", "........"]
SENTINEL_PAL = {"s": "#f0ecff", "t": "#7a70c0", "4": "#9a8ae0", "3": "#5a48a0", "2": "#251a4a",
                "V": "#c070ff", "Y": "#ffcf40", "W": "#ffffff"}


def minions():
    """name -> (stand, attack), 8x8."""
    return {
        "Dawn Templar": (from_map(TEMPLAR, GOLD), from_map(TEMPLAR_HIT, GOLD)),
        "Dusk Shade": (from_map(SHADE, DUSK), from_map(SHADE_HIT, DUSK)),
        "Starbound Sentinel": (from_map(SENTINEL, SENTINEL_PAL), from_map(SENTINEL_HIT, SENTINEL_PAL)),
    }


# ------------------------------------------------------------------------------------------------
# shots, 8x8, pointing right

def _blank():
    return Image.new("RGBA", (8, 8), (0, 0, 0, 0))


def dusk_bolt():
    """A violet comet."""
    img = _blank()
    for x in range(8):
        for y in range(8):
            d = math.hypot(x - 5.5, y - 3.5)
            if d < 2.1:
                put(img, x, y, "#ffffff" if d < 0.8 else ("#e0b0ff" if d < 1.4 else "#a040f0"))
            elif x < 5 and abs(y - 3.5) < (x + 1) * 0.3:
                put(img, x, y, "#5f34a3" if x < 2 else "#8a4ae0")
    return img


def umbral_orb():
    """A dark orb ringed in violet: Vesper's rings."""
    img = _blank()
    for x in range(8):
        for y in range(8):
            d = math.hypot(x - 3.5, y - 3.5)
            if d < 3.2:
                put(img, x, y, "#1a0c30" if d < 1.4 else ("#7a2ad0" if d < 2.4 else "#c070ff"))
    put(img, 2, 2, "#f0d0ff")
    return img


def crescent():
    """A golden sword-wave."""
    img = _blank()
    for y in range(8):
        for x in range(8):
            d1 = math.hypot(x - 2.0, y - 3.5)
            d2 = math.hypot(x - 0.6, y - 3.5)
            if d1 < 4.2 and d2 > 4.0:
                put(img, x, y, "#ffffff" if d2 < 4.8 else ("#ffd24a" if d2 < 5.8 else "#c08a1c"))
    return img


def sunspark():
    """A four-pointed sun star."""
    img = _blank()
    for (x, y, c) in ((3, 0, 1), (4, 0, 1), (3, 1, 2), (4, 1, 2), (0, 3, 1), (1, 3, 2), (6, 3, 2), (7, 3, 1),
                      (0, 4, 1), (1, 4, 2), (6, 4, 2), (7, 4, 1), (3, 6, 2), (4, 6, 2), (3, 7, 1), (4, 7, 1)):
        put(img, x, y, ["", "#c08a1c", "#ffd24a"][c])
    for x in range(2, 6):
        for y in range(2, 6):
            put(img, x, y, "#ffffff" if 3 <= x <= 4 and 3 <= y <= 4 else "#fff0a8")
    return img


def eclipse_orb():
    """Half dusk, half dawn, a black heart: the father's."""
    img = _blank()
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5)
            if d < 3.8:
                if d < 1.6:
                    put(img, x, y, "#05030a")
                elif d < 2.4:
                    put(img, x, y, "#ffffff")
                else:
                    put(img, x, y, "#a040f0" if x + y < 7 else "#ffcf40")
    return img


def starbound_mote():
    """The Sentinels' pale star."""
    img = _blank()
    for (x, y) in ((3, 1), (4, 1), (1, 3), (6, 3), (1, 4), (6, 4), (3, 6), (4, 6)):
        put(img, x, y, "#7a70c0")
    for x in range(2, 6):
        for y in range(2, 6):
            put(img, x, y, "#ffffff" if 3 <= x <= 4 and 3 <= y <= 4 else "#c8c0ff")
    return img


SHOTS = {
    "Dusk Bolt": dusk_bolt,
    "Umbral Orb": umbral_orb,
    "Dawn Crescent": crescent,
    "Sunspark": sunspark,
    "Eclipse Orb": eclipse_orb,
    "Starbound Mote": starbound_mote,
}


# ------------------------------------------------------------------------------------------------
# things on the floor

def dusk_mine(frame):
    """A dusk mine: a dark star pulsing violet, about to burst."""
    img = _blank()
    glow = ("#7a2ad0", "#c070ff")[frame]
    for (x, y) in ((3, 0), (4, 0), (0, 3), (0, 4), (7, 3), (7, 4), (3, 7), (4, 7)):
        put(img, x, y, glow)
    for x in range(1, 7):
        for y in range(1, 7):
            if abs(x - 3.5) + abs(y - 3.5) < 3.6:
                put(img, x, y, "#1a0c30" if abs(x - 3.5) + abs(y - 3.5) < 1.6 else ("#5f34a3" if (x + y) % 2 else "#3a1d6a"))
    put(img, 3, 3, "#ff6ae8" if frame else "#c040e0")
    return img


def wall_of_light(kind, frame):
    """A wall the bosses raise (16x16, standing): Vesper's violet veil or Aurel's dawnlight, a
    shimmering column of light over a glowing seam in the floor."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    if kind == "veil":
        cols = ["#2a0c4a", "#5f2aa0", "#a060f0", "#e8c8ff"]
    else:
        cols = ["#7a4c0e", "#d09a28", "#ffe070", "#fffbe8"]
    rnd = random.Random(frame * 7 + (kind == "veil"))
    for y in range(16):
        for x in range(2, 14):
            core = 1 - abs(x - 7.5) / 6
            wave = 0.5 + 0.5 * math.sin(y * 0.8 + frame * 1.9 + x * 0.4)
            v = core * 0.75 + wave * 0.35
            k = 3 if v > 0.92 else 2 if v > 0.62 else 1 if v > 0.32 else 0
            a = int(120 + 135 * min(1.0, core + 0.2))
            put(img, x, y, cols[k], a)
    for _ in range(5):
        put(img, rnd.randrange(3, 13), rnd.randrange(0, 16), "#ffffff")
    return img


# ------------------------------------------------------------------------------------------------
# the floor: 8x8 tiles

def _tile(fn, seed):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (8, 8), (0, 0, 0, 255))
    fn(img, rnd)
    return img


def astral_stone(seed):
    """Dark violet-slate floor: soft mottling, a seam here and there (not round every tile, which
    reads as a grid), a fleck of starlight caught in some."""
    def f(img, rnd):
        for y in range(8):
            for x in range(8):
                v = rnd.random()
                put(img, x, y, "#2a2442" if v > 0.22 else ("#262039" if v > 0.08 else "#30294c"))
        if seed % 2:
            for y in range(8):
                if rnd.random() < 0.8:
                    put(img, 0, y, "#211c34")
        else:
            for x in range(rnd.randrange(3, 8)):
                put(img, x, 0, "#211c34")
        if seed % 3 == 0:
            put(img, rnd.randrange(2, 6), rnd.randrange(2, 6), "#7a6ac0")
    return _tile(f, seed)


def astral_inlay(seed):
    """The faint lines inlaid in the floor where the bosses' walls will fall: gold under violet."""
    def f(img, rnd):
        for y in range(8):
            for x in range(8):
                c = "#2a2442" if rnd.random() > 0.15 else "#322a4e"
                put(img, x, y, c)
        for i in range(8):
            put(img, i, 3, "#4a3a78")
            put(img, i, 4, "#6a5226" if (i + seed) % 3 else "#8a6a2a")
    return _tile(f, seed)


def platform_rim(seed):
    """The raised rim of the platform: lighter stone, cut in blocks."""
    def f(img, rnd):
        for y in range(8):
            for x in range(8):
                c = "#4a4070" if y < 2 else ("#3a3258" if y < 6 else "#241e38")
                if x in (0, 4) and y >= 2:
                    c = "#1c1830"
                put(img, x, y, c)
        put(img, rnd.randrange(1, 7), 0, "#6a5ea0")
    return _tile(f, seed)


def veil(seed):
    """Vesper's ward on the floor: a violet weave that burns to stand on."""
    def f(img, rnd):
        for y in range(8):
            for x in range(8):
                k = (x + y + seed) % 4
                c = "#5a1a90" if k == 0 else ("#2c0c4a" if (x - y + seed) % 4 == 0 else "#3a1060")
                put(img, x, y, c)
        put(img, rnd.randrange(8), rnd.randrange(8), "#c070ff")
    return _tile(f, seed)


def black_between(seed):
    """The void come up through the floor: starry black, a violet shimmer at its edge (it burns)."""
    def f(img, rnd):
        for y in range(8):
            for x in range(8):
                put(img, x, y, "#08051a" if rnd.random() > 0.08 else "#1a0f36")
        for _ in range(2):
            put(img, rnd.randrange(8), rnd.randrange(8), "#c8c0ff" if rnd.random() < 0.5 else "#6a5aa8")
    return _tile(f, seed)


def constellation(seed):
    """A star of the Constellation Path: safe footing in the dark."""
    def f(img, rnd):
        for y in range(8):
            for x in range(8):
                put(img, x, y, "#121030" if (x + y) % 2 else "#16133a")
        for i in range(8):
            put(img, i, 3 + (seed % 2), "#3a3478")
        put(img, 3, 3, "#ffffff"); put(img, 4, 4, "#ffffff"); put(img, 3, 4, "#d8d0ff"); put(img, 4, 3, "#d8d0ff")
        put(img, 2, 3, "#8a80d0"); put(img, 5, 4, "#8a80d0"); put(img, 3, 2, "#8a80d0"); put(img, 4, 5, "#8a80d0")
    return _tile(f, seed)


TILES = {
    "Astral Stone": [astral_stone(s) for s in (3, 4, 5, 6)],
    "Astral Inlay": [astral_inlay(s) for s in (1, 2)],
    "Platform Rim": [platform_rim(s) for s in (1, 2)],
    "Veil of Dusk": [veil(s) for s in (0, 1, 2)],
    "Black Between": [black_between(s) for s in (1, 2, 3)],
    "Constellation Path": [constellation(s) for s in (0, 1)],
}


# ------------------------------------------------------------------------------------------------
# the Rift of the Between: a galactic portal ringed in dusk and dawn, 16x16, turning

def rift(frame):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            r = math.hypot(dx, dy)
            if r > 7.6:
                continue
            if r > 6.4:
                ang = math.atan2(dy, dx)
                gold = math.cos(ang - 0.8) > 0
                lit = math.cos(ang + 2.3) * 0.5 + 0.5
                c = ["#7a4c0e", "#c08a1c", "#ffd24a"] if gold else ["#2a1450", "#5f34a3", "#a070f0"]
                put(img, x, y, c[int(lit * 2.99)])
                continue
            ang = math.atan2(dy, dx) + frame * math.pi / 6
            arm = math.sin(ang * 2 - r * 0.9)
            if r < 1.5:
                put(img, x, y, "#ffffff")
            elif arm > 0.55:
                put(img, x, y, "#c8a0ff" if (x + y + frame) % 2 else "#fff0b0")
            elif arm > 0.0:
                put(img, x, y, "#3a1d6a")
            else:
                put(img, x, y, "#0a0718")
    rnd = random.Random(frame)
    for _ in range(4):
        a, r = rnd.random() * 6.28, rnd.random() * 5.5
        put(img, 7.5 + math.cos(a) * r, 7.5 + math.sin(a) * r, "#ffffff")
    return img
