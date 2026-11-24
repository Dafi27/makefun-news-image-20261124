#!/usr/bin/env python3
"""World news of Tuesday 24 November 2026, drawn as one newspaper image.

Pure standard library: the program rasterises its own 5x7 bitmap font and
writes a PNG with zlib, so it runs with no network and no installed packages.
Deterministic: no timestamps, no randomness, no environment input.

Layout (1024x1024): masthead, one lead story, three stories in a row,
two stories in a wide row, footer with sources.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (20, 20, 20)
NAVY = (20, 38, 74)
RED = (176, 30, 36)
GREY = (90, 88, 80)
CARD = (255, 255, 255)
BLUE = (28, 84, 160)
GREEN = (34, 120, 62)
ORANGE = (214, 96, 20)
TEAL = (14, 110, 110)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = ink. Uppercase, digits, punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            i = (y * self.w + max(0, x0)) * 3
            n = min(self.w, x1) - max(0, x0)
            if n > 0:
                self.px[i:i + n * 3] = bytes(c) * n

    def hline(self, x0, x1, y, c, t=1):
        for dy in range(t):
            for x in range(x0, x1):
                self.set(x, y + dy, c)

    def vline(self, x, y0, y1, c, t=1):
        for dx in range(t):
            for y in range(y0, y1):
                self.set(x + dx, y, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(x, y, c)
                else:
                    if abs(d - r * r) <= r * 2:
                        self.set(x, y, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, c)

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c, align="left"):
        if align == "center":
            x -= self.text_w(s, scale) // 2
        elif align == "right":
            x -= self.text_w(s, scale)
        for ch in s:
            g = FONT.get(ch.upper(), FONT['?'])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.rect(x + col * scale, y + r * scale,
                                  x + (col + 1) * scale, y + (r + 1) * scale, c)
            x += 6 * scale

    def wrap(self, s, scale, maxw):
        words = s.split(" ")
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.text_w(t, scale) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
           chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- icons
def icon_chip(cv, cx, cy, s):
    # computer chip: dark body, pins, inner square
    cv.rect(cx - 34 * s // 10, cy - 34 * s // 10,
            cx + 34 * s // 10, cy + 34 * s // 10, NAVY)
    cv.rect(cx - 18 * s // 10, cy - 18 * s // 10,
            cx + 18 * s // 10, cy + 18 * s // 10, (90, 180, 120))
    for k in (-2, -1, 0, 1, 2):
        off = k * 12 * s // 10
        cv.rect(cx + off - 2, cy - 46 * s // 10, cx + off + 2, cy - 34 * s // 10, NAVY)
        cv.rect(cx + off - 2, cy + 34 * s // 10, cx + off + 2, cy + 46 * s // 10, NAVY)
        cv.rect(cx - 46 * s // 10, cy + off - 2, cx - 34 * s // 10, cy + off + 2, NAVY)
        cv.rect(cx + 34 * s // 10, cy + off - 2, cx + 46 * s // 10, cy + off + 2, NAVY)


def icon_ship(cv, cx, cy, s):
    cv.poly([(cx - 44 * s // 10, cy + 12 * s // 10),
             (cx + 44 * s // 10, cy + 12 * s // 10),
             (cx + 30 * s // 10, cy + 30 * s // 10),
             (cx - 30 * s // 10, cy + 30 * s // 10)], NAVY)
    cv.rect(cx - 26 * s // 10, cy - 6 * s // 10,
            cx + 26 * s // 10, cy + 12 * s // 10, (70, 110, 170))
    cv.vline(cx, cy - 44 * s // 10, cy - 6 * s // 10, INK, 3)
    cv.poly([(cx, cy - 44 * s // 10), (cx + 26 * s // 10, cy - 20 * s // 10),
             (cx, cy - 20 * s // 10)], RED)
    for k in range(3):
        cv.line(cx - 48 * s // 10 + k * 4, cy + 40 * s // 10,
                cx + 48 * s // 10 - k * 4, cy + 40 * s // 10, BLUE, 2)


def icon_satellite(cv, cx, cy, s):
    cv.rect(cx - 16 * s // 10, cy - 12 * s // 10,
            cx + 16 * s // 10, cy + 12 * s // 10, NAVY)
    cv.rect(cx - 52 * s // 10, cy - 8 * s // 10,
            cx - 20 * s // 10, cy + 8 * s // 10, BLUE)
    cv.rect(cx + 20 * s // 10, cy - 8 * s // 10,
            cx + 52 * s // 10, cy + 8 * s // 10, BLUE)
    cv.line(cx - 20 * s // 10, cy, cx - 52 * s // 10, cy, CARD, 1)
    cv.line(cx + 20 * s // 10, cy, cx + 52 * s // 10, cy, CARD, 1)
    cv.line(cx, cy + 12 * s // 10, cx + 24 * s // 10, cy + 30 * s // 10, NAVY, 3)
    cv.circle(cx + 28 * s // 10, cy + 32 * s // 10, 8 * s // 10, RED)


def icon_globe(cv, cx, cy, s):
    cv.circle(cx, cy, 36 * s // 10, GREEN)
    cv.circle(cx, cy, 36 * s // 10, INK, fill=False)
    cv.circle(cx, cy, 20 * s // 10, (120, 200, 140))
    cv.line(cx - 36 * s // 10, cy, cx + 36 * s // 10, cy, INK, 2)
    cv.line(cx, cy - 36 * s // 10, cx, cy + 36 * s // 10, INK, 2)


def icon_flame(cv, cx, cy, s):
    cv.poly([(cx, cy - 44 * s // 10),
             (cx + 22 * s // 10, cy - 6 * s // 10),
             (cx + 30 * s // 10, cy + 18 * s // 10),
             (cx + 12 * s // 10, cy + 34 * s // 10),
             (cx - 12 * s // 10, cy + 34 * s // 10),
             (cx - 30 * s // 10, cy + 18 * s // 10),
             (cx - 22 * s // 10, cy - 6 * s // 10)], ORANGE)
    cv.poly([(cx, cy - 8 * s // 10),
             (cx + 12 * s // 10, cy + 10 * s // 10),
             (cx, cy + 28 * s // 10),
             (cx - 12 * s // 10, cy + 10 * s // 10)], (255, 200, 40))


def icon_jet(cv, cx, cy, s):
    cv.poly([(cx - 44 * s // 10, cy + 6 * s // 10),
             (cx + 40 * s // 10, cy - 8 * s // 10),
             (cx + 48 * s // 10, cy),
             (cx + 40 * s // 10, cy + 8 * s // 10)], NAVY)
    cv.poly([(cx - 8 * s // 10, cy - 6 * s // 10),
             (cx + 8 * s // 10, cy - 34 * s // 10),
             (cx + 16 * s // 10, cy - 6 * s // 10)], BLUE)
    cv.poly([(cx - 8 * s // 10, cy + 6 * s // 10),
             (cx + 8 * s // 10, cy + 30 * s // 10),
             (cx + 16 * s // 10, cy + 6 * s // 10)], BLUE)


# ---------------------------------------------------------------- layout
def card(cv, x0, y0, x1, y1):
    cv.rect(x0, y0, x1, y1, CARD)
    cv.rect(x0, y0, x1, y0 + 4, RED)
    for xx in (x0, x1 - 1):
        cv.vline(xx, y0, y1, (200, 196, 184), 1)
    cv.hline(x0, x1, y1 - 1, (200, 196, 184), 1)


def story(cv, x0, y0, x1, y1, kicker, head, deck, icon, accent):
    card(cv, x0, y0, x1, y1)
    pad = 18
    icon(cv, (x0 + x1) // 2, y0 + 58, 10)
    tx = x0 + pad
    tw = x1 - x0 - 2 * pad
    y = y0 + 108
    cv.text(tx, y, kicker, 2, accent)
    y += 30
    for ln in cv.wrap(head, 3, tw):
        cv.text(tx, y, ln, 3, INK)
        y += 30
    y += 4
    for ln in cv.wrap(deck, 2, tw):
        cv.text(tx, y, ln, 2, GREY)
        y += 22


def draw():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 118, NAVY)
    cv.text(W // 2, 22, "THE WORLD TODAY", 9, (255, 255, 255), align="center")
    cv.rect(0, 118, W, 122, RED)
    cv.text(W // 2, 136, "TUESDAY 24 NOVEMBER 2026", 4, INK, align="center")
    cv.text(W // 2, 168, "SIX STORIES FROM AROUND THE WORLD - IN ONE PICTURE",
            2, GREY, align="center")

    # lead story: Nvidia
    x0, y0, x1, y1 = 24, 200, 1000, 396
    card(cv, x0, y0, x1, y1)
    cv.text(x0 + 24, y0 + 16, "TECH  *  TOP STORY", 2, RED)
    cv.text(x0 + 24, y0 + 46, "NVIDIA BRINGS BACK", 6, INK)
    cv.text(x0 + 24, y0 + 92, "JENSEN HUANG", 6, INK)
    cv.text(x0 + 24, y0 + 146, "CEO REINSTATED AFTER SPY SCANDAL - TRUMP SAYS:", 2, GREY)
    cv.text(x0 + 24, y0 + 170, "'I MADE THE DEAL' - SHARES JUMP", 2, GREY)
    icon_chip(cv, 880, y0 + 100, 12)

    # middle row: three stories
    my0, my1 = 412, 688
    gap, cw = 16, 312
    story(cv, 24, my0, 24 + cw, my1, "WAR", "UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA",
          "Sea drones sank the corvette Merkury.",
          icon_ship, NAVY)
    story(cv, 24 + cw + gap, my0, 24 + 2 * cw + gap, my1, "SPACE",
          "NATO VOWS TO DEFEND SPACE",
          "Reports say Russia may launch a nuclear-armed satellite, 'Sputnik-S'.",
          icon_satellite, BLUE)
    story(cv, 24 + 2 * cw + 2 * gap, my0, 1000, my1, "CLIMATE",
          "COP31 ENDS WITH NO DEAL",
          "Climate talks collapse in Antalya over fossil fuels.",
          icon_globe, GREEN)

    # bottom row: two wide stories
    by0, by1 = 704, 956
    bw = 480
    story(cv, 24, by0, 24 + bw, by1, "DISASTER",
          "24 DEAD IN INDONESIA FACTORY FIRE",
          "Candy plant blaze in Banten; about 30 workers still missing.",
          icon_flame, ORANGE)
    story(cv, 24 + bw + gap, by0, 1000, by1, "ASIA",
          "RUSSIAN JETS ENTER S. KOREA AIR ZONE",
          "Seoul: Russian aircraft flew into its air defence zone.",
          icon_jet, TEAL)

    # footer
    cv.text(W // 2, 972, "FIRST REPORTED TUESDAY 24 NOVEMBER 2026 - SOURCES: BBC, AP, REUTERS",
            2, GREY, align="center")
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)  # never delete the directory itself
    cv = draw()
    write_png(cv, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
