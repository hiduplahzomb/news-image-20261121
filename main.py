#!/usr/bin/env python3
"""THE WORLD TODAY — Saturday 21 November 2026 in one image.

A newspaper front page drawn entirely in code (Python standard library
only, no network, no fonts, no third-party packages) for make.fun's
news-image-20261121 bounty. The program renders a 1024x1024 PNG that sums
up the day's world news and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png when set, for local runs).

Stories covered (all reported on 21 November 2026):
  1. Russia's largest strike on Ukraine: 400+ drones, 110 missiles;
     two missiles land in Poland.
  2. AI stock sell-off: US stocks -3.7%, S&P 500 into correction.
  3. ICJ finds Myanmar responsible for genocide against the Rohingya.
  4. Trump, Putin and Xi meet in Shenzhen; a peace declaration.
  5. Pancreatic cancer pill: tumours undetectable in 1 in 12 patients.

Deterministic: the same bytes every run.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)      # newspaper cream
PAPER_DARK = (238, 232, 216)
INK = (18, 18, 18)
GREY = (110, 108, 100)
RED = (196, 30, 30)
RED_DARK = (150, 20, 20)
NAVY = (13, 20, 42)
NAVY2 = (27, 35, 64)
SKY_TOP = (8, 11, 28)
SKY_HOR = (32, 40, 78)
GOLD = (212, 175, 55)
GOLD_LT = (240, 205, 110)
CREAM = (255, 246, 220)
YELLOW = (255, 214, 90)
ORANGE = (255, 140, 40)
WHITE = (255, 255, 255)
BLUE = (40, 90, 180)
GREEN = (46, 140, 80)

# ------------------------------------------------------- 5x7 bitmap font
# '#' = filled, '.' = empty. Uppercase, digits and the punctuation the
# headlines need. Designed for this entry; drawn at integer scales.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "%": (".##.#", ".##.#", "...#.", "..#..", ".#...", "#.##.", "#.##."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".###.", "#...#", "#...#", ".###.", "#.#..", "#..#.", ".##.#"),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))


def gradient(stops, t):
    """Interpolate a multi-stop gradient at t in [0, 1]."""
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(1, len(stops)):
        if t <= stops[i][0]:
            p0, c0 = stops[i - 1]
            p1, c1 = stops[i]
            return lerp_color(c0, c1, (t - p0) / (p1 - p0))
    return stops[-1][1]


def blend(dst, src, a):
    """Blend src RGB over dst RGB with alpha a in [0, 1]."""
    return (int(dst[0] + (src[0] - dst[0]) * a),
            int(dst[1] + (src[1] - dst[1]) * a),
            int(dst[2] + (src[2] - dst[2]) * a))


def hash01(x, y):
    """Deterministic pseudo-random value in [0, 1) for a pixel."""
    n = (x * 374761393 + y * 668265263) ^ ((x * y) * 974634 + 1442695041)
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


# ------------------------------------------------------------------ canvas
def new_canvas(w, h, color):
    return [bytearray(bytes(color) * w) for _ in range(h)]


def set_px(rows, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = x * 3
        rows[y][i:i + 3] = bytes(color)


def get_px(rows, x, y):
    i = x * 3
    return (rows[y][i], rows[y][i + 1], rows[y][i + 2])


def blend_px(rows, x, y, color, a):
    if 0 <= x < W and 0 <= y < H:
        set_px(rows, x, y, blend(get_px(rows, x, y), color, a))


def fill_rect(rows, x0, y0, x1, y1, color):
    """Fill the rectangle [x0, x1) x [y0, y1) with a solid color."""
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    if x0 >= x1 or y0 >= y1:
        return
    span = bytes(color) * (x1 - x0)
    for y in range(y0, y1):
        rows[y][x0 * 3:x1 * 3] = span


def fill_rect_alpha(rows, x0, y0, x1, y1, color, a):
    """Fill a rectangle with a translucent color (per-pixel blend)."""
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            blend_px(rows, x, y, color, a)


def rect_outline(rows, x0, y0, x1, y1, color, t=1):
    fill_rect(rows, x0, y0, x1, y0 + t, color)
    fill_rect(rows, x0, y1 - t, x1, y1, color)
    fill_rect(rows, x0, y0, x0 + t, y1, color)
    fill_rect(rows, x1 - t, y0, x1, y1, color)


def hline(rows, x0, x1, y, color, t=1):
    fill_rect(rows, x0, y, x1, y + t, color)


def vline(rows, x, y0, y1, color, t=1):
    fill_rect(rows, x, y0, x + t, y1, color)


def disc(rows, cx, cy, r, color):
    """Filled circle."""
    for yy in range(cy - r, cy + r + 1):
        dy = yy - cy
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        fill_rect(rows, cx - dx, yy, cx + dx + 1, yy + 1, color)


def disc_alpha(rows, cx, cy, r, color, a):
    """Filled circle blended over what is there."""
    for yy in range(cy - r, cy + r + 1):
        dy = yy - cy
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        for x in range(cx - dx, cx + dx + 1):
            blend_px(rows, x, yy, color, a)


def glow(rows, cx, cy, r, color, peak=0.85):
    """Soft radial glow: alpha falls off quadratically to the edge."""
    for yy in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, yy - cy) / r
            if d < 1.0:
                blend_px(rows, x, yy, color, peak * (1.0 - d) ** 2)


def line(rows, x0, y0, x1, y1, color, t=1):
    """Bresenham line with square brush of size t."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = t // 2
    while True:
        fill_rect(rows, x0 - half, y0 - half, x0 - half + t, y0 - half + t,
                  color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def polyline(rows, pts, color, t=1):
    for a, b in zip(pts, pts[1:]):
        line(rows, a[0], a[1], b[0], b[1], color, t)


def polygon(rows, pts, color):
    """Filled polygon, scanline fill."""
    if len(pts) < 3:
        return
    ymin = min(p[1] for p in pts)
    ymax = max(p[1] for p in pts)
    for y in range(ymin, ymax + 1):
        nodes = []
        j = len(pts) - 1
        for i in range(len(pts)):
            yi, yj = pts[i][1], pts[j][1]
            if (yi < y <= yj) or (yj < y <= yi):
                xi, xj = pts[i][0], pts[j][0]
                nodes.append(xi + (y - yi) * (xj - xi) / (yj - yi))
            j = i
        nodes.sort()
        for a, b in zip(nodes[::2], nodes[1::2]):
            fill_rect(rows, int(a), y, int(b) + 1, y + 1, color)


# --------------------------------------------------------------------- text
def text_width(s, scale):
    """Pixel width of s at the given scale (6 units per char, 1 gap)."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def text_height(scale):
    return 7 * scale


def draw_text(rows, x, y, s, scale, color, align="left", shadow=None):
    """Draw s with the 5x7 font. align left/center/right anchors at x."""
    w = text_width(s, scale)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    if shadow is not None:
        draw_text(rows, x + scale, y + scale, s, scale, shadow)
    cx = x
    for ch in s:
        if ch == " ":
            cx += 6 * scale
            continue
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for gr, line_s in enumerate(glyph):
            for gc, cell in enumerate(line_s):
                if cell == "#":
                    fill_rect(rows,
                              cx + gc * scale, y + gr * scale,
                              cx + (gc + 1) * scale, y + (gr + 1) * scale,
                              color)
        cx += 6 * scale


def draw_text_wrapped(rows, x0, y, x1, s, scale, color, leading=4):
    """Draw s wrapped to fit [x0, x1), left aligned; returns next y."""
    words = s.split(" ")
    line = ""
    for word in words:
        trial = word if not line else line + " " + word
        if text_width(trial, scale) <= x1 - x0 or not line:
            line = trial
        else:
            draw_text(rows, x0, y, line, scale, color)
            y += text_height(scale) + leading
            line = word
    if line:
        draw_text(rows, x0, y, line, scale, color)
        y += text_height(scale) + leading
    return y


# ------------------------------------------------------------------- scenes
def draw_masthead(rows):
    """Nameplate + date line, newspaper style."""
    hline(rows, 20, 1004, 18, INK, 4)
    draw_text(rows, W // 2, 30, "THE WORLD TODAY", 8, INK, align="center")
    draw_text(rows, W // 2, 96, "SATURDAY 21 NOVEMBER 2026", 5, RED,
              align="center")
    hline(rows, 20, 1004, 138, INK, 2)
    hline(rows, 20, 1004, 143, INK, 5)


def draw_lead(rows):
    """Lead story: Russia's overnight strike on Ukraine, missiles in Poland.

    Night scene over a city skyline with golden domes: missile trails arc
    across the sky, explosions bloom over the rooftops, and a small Polish
    flag marks the border where two missiles landed.
    """
    x0, y0, x1, y1 = 20, 152, 1004, 560
    # --- night sky ---
    for y in range(y0, y1):
        c = gradient([(0.0, SKY_TOP), (0.75, SKY_HOR), (1.0, (48, 52, 92))],
                     (y - y0) / (y1 - y0))
        fill_rect(rows, x0, y, x1, y + 1, c)
    # --- stars ---
    for sy in range(y0 + 8, y0 + 190, 7):
        for sx in range(x0 + 10, x1 - 10, 9):
            h = hash01(sx, sy)
            if h < 0.10:
                b = 140 + int(115 * hash01(sy, sx))
                set_px(rows, sx, sy, (b, b, min(255, b + 20)))
                if h < 0.03:
                    set_px(rows, sx + 1, sy, (b, b, min(255, b + 20)))
    # --- moon ---
    glow(rows, 905, 215, 70, (220, 220, 200), 0.25)
    disc(rows, 905, 215, 30, (245, 240, 214))
    disc(rows, 895, 208, 6, (225, 219, 190))
    disc(rows, 914, 224, 4, (225, 219, 190))
    # --- missile trails (arcs rising left to right) ---
    for (sx, sy, ex, ey, lift) in ((120, 470, 560, 250, 90),
                                   (260, 480, 700, 210, 120),
                                   (60, 430, 420, 300, 60)):
        pts = []
        for i in range(0, 41):
            t = i / 40.0
            px = int(sx + (ex - sx) * t)
            py = int(sy + (ey - sy) * t - lift * 4 * t * (1 - t))
            pts.append((px, py))
        # fading tail: draw the arc in segments, dimmer toward the start
        for i in range(len(pts) - 1):
            f = i / (len(pts) - 1)
            col = blend((20, 24, 50), (255, 230, 170), 0.15 + 0.85 * f)
            line(rows, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                 col, 2)
        disc(rows, ex, ey, 4, (255, 244, 200))
        glow(rows, ex, ey, 14, (255, 220, 140), 0.7)
    # --- explosions over the rooftops ---
    for (ex, ey, r) in ((330, 400, 52), (620, 385, 66), (800, 410, 40)):
        glow(rows, ex, ey, r * 2, ORANGE, 0.55)
        glow(rows, ex, ey, r, YELLOW, 0.8)
        disc(rows, ex, ey, int(r * 0.32), (255, 244, 200))
        disc(rows, ex, ey, int(r * 0.15), WHITE)
    # --- city skyline (Kyiv silhouette) ---
    base = 470
    buildings = [
        (20, 120, 60), (150, 90, 110), (250, 130, 70), (330, 100, 130),
        (440, 140, 55), (590, 110, 120), (710, 150, 65), (820, 90, 105),
        (920, 84, 80),
    ]
    for (bx, bw, bh) in buildings:
        fill_rect(rows, bx, base - bh, bx + bw, base, (10, 12, 26))
        # lit windows
        for wy in range(base - bh + 10, base - 8, 14):
            for wx in range(bx + 8, bx + bw - 8, 12):
                if hash01(wx, wy) < 0.35:
                    fill_rect(rows, wx, wy, wx + 4, wy + 5, (255, 200, 90))
    # golden domes (Kyiv's churches) sitting on two rooftops
    for (dx, dy, dr) in ((300, 392, 22), (650, 342, 26)):
        vline(rows, dx - 1, dy - dr - 16, dy - dr + 2, GOLD, 3)
        hline(rows, dx - 7, dx + 8, dy - dr - 10, GOLD, 3)
        disc(rows, dx, dy, dr, GOLD)
        fill_rect(rows, dx - dr, dy, dx + dr + 1, dy + 4, GOLD)
        disc(rows, dx - 6, dy - 6, 5, GOLD_LT)
    # --- Polish flag pin at the border (right edge) ---
    flag_x, flag_y = 880, 330
    vline(rows, flag_x, flag_y, flag_y + 60, (200, 200, 200), 3)
    fill_rect(rows, flag_x + 3, flag_y, flag_x + 43, flag_y + 11, WHITE)
    fill_rect(rows, flag_x + 3, flag_y + 11, flag_x + 43, flag_y + 22, RED)
    draw_text(rows, flag_x + 46, flag_y + 2, "POLAND", 2, CREAM)
    # --- headline band ---
    fill_rect_alpha(rows, x0, 470, x1, y1, (8, 8, 14), 0.82)
    hline(rows, x0, x1, 470, RED, 3)
    draw_text(rows, W // 2, 486, "RUSSIA'S BIGGEST STRIKE ON UKRAINE", 4,
              WHITE, align="center")
    draw_text(rows, W // 2, 524,
              "400+ DRONES \u2022 110 MISSILES \u2022 TWO LAND IN POLAND", 3,
              YELLOW, align="center")
    rect_outline(rows, x0, y0, x1, y1, INK, 2)


def draw_markets(rows):
    """Column 1: the AI stock sell-off."""
    x0, y0, x1, y1 = 20, 580, 340, 920
    fill_rect(rows, x0, y0, x1, y1, WHITE)
    rect_outline(rows, x0, y0, x1, y1, INK, 2)
    draw_text(rows, (x0 + x1) // 2, y0 + 14, "AI SELL-OFF", 4, INK,
              align="center")
    hline(rows, x0 + 16, x1 - 16, y0 + 52, GREY, 1)
    # --- plunging chart ---
    cx0, cy0, cx1, cy1 = x0 + 24, y0 + 72, x1 - 24, y0 + 196
    for gy in range(cy0, cy1 + 1, 31):
        hline(rows, cx0, cx1, gy, (228, 228, 228), 1)
    vline(rows, cx0, cy0, cy1, GREY, 2)
    hline(rows, cx0, cx1, cy1, GREY, 2)
    pts = []
    n = 26
    for i in range(n + 1):
        t = i / n
        px = cx0 + int((cx1 - cx0) * t)
        drop = (t ** 1.6) * (cy1 - cy0 - 18)
        jig = int((hash01(i * 7, 3) - 0.5) * 14 * (1 - t * 0.5))
        pts.append((px, cy0 + 8 + int(drop) + jig))
    polyline(rows, pts, RED, 4)
    # down arrow at the end of the line
    ex, ey = pts[-1]
    polygon(rows, [(ex - 2, ey - 26), (ex + 22, ey - 26), (ex + 10, ey - 2)],
            RED)
    draw_text(rows, (x0 + x1) // 2, y0 + 212, "-3.7%", 7, RED,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 272, "S&P 500 INTO", 3, INK,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 300, "CORRECTION", 3, INK,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 320, "NASDAQ ERASES 2026 GAINS", 2,
              GREY, align="center")


def draw_justice(rows):
    """Column 2: the ICJ genocide ruling against Myanmar."""
    x0, y0, x1, y1 = 352, 580, 672, 920
    fill_rect(rows, x0, y0, x1, y1, NAVY2)
    rect_outline(rows, x0, y0, x1, y1, INK, 2)
    draw_text(rows, (x0 + x1) // 2, y0 + 14, "ICJ RULES", 4, GOLD_LT,
              align="center")
    hline(rows, x0 + 16, x1 - 16, y0 + 52, (90, 100, 140), 1)
    # --- scales of justice, gold ---
    cx, top, bot = (x0 + x1) // 2, y0 + 70, y0 + 200
    vline(rows, cx - 2, top, bot, GOLD, 5)
    disc(rows, cx, top - 4, 6, GOLD)
    hline(rows, cx - 78, cx + 78, top + 8, GOLD, 5)
    for sgn in (-1, 1):
        px = cx + sgn * 78
        disc(rows, px, top + 10, 4, GOLD)
        line(rows, px, top + 12, px - 26, bot - 34, GOLD, 3)
        line(rows, px, top + 12, px + 26, bot - 34, GOLD, 3)
        # pan: shallow arc
        for a in range(0, 31):
            t = a / 30.0
            ang = math.pi * t
            px2 = int(px - 26 + 52 * t)
            py2 = int(bot - 34 + 14 * math.sin(ang))
            fill_rect(rows, px2 - 1, py2 - 1, px2 + 2, py2 + 2, GOLD)
    fill_rect(rows, cx - 40, bot, cx + 41, bot + 6, GOLD)
    fill_rect(rows, cx - 55, bot + 6, cx + 56, bot + 11, GOLD)
    draw_text(rows, (x0 + x1) // 2, y0 + 226, "MYANMAR", 4, WHITE,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 262, "RESPONSIBLE", 3, WHITE,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 290, "FOR GENOCIDE", 3, GOLD_LT,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 318, "AGAINST THE ROHINGYA", 2,
              (170, 180, 210), align="center")


def draw_summit(rows):
    """Column 3: the Trump-Putin-Xi summit in Shenzhen."""
    x0, y0, x1, y1 = 684, 580, 1004, 920
    fill_rect(rows, x0, y0, x1, y1, WHITE)
    rect_outline(rows, x0, y0, x1, y1, INK, 2)
    draw_text(rows, (x0 + x1) // 2, y0 + 14, "SHENZHEN", 4, INK,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 46, "SUMMIT", 4, INK,
              align="center")
    hline(rows, x0 + 16, x1 - 16, y0 + 84, GREY, 1)
    # --- three flags on poles: USA, China, Russia ---
    fy = y0 + 100
    fh = 64
    # USA: stripes + canton
    ux = x0 + 22
    for s in range(7):
        fill_rect(rows, ux, fy + s * 9, ux + 76, fy + s * 9 + 5,
                  RED if s % 2 == 0 else WHITE)
    fill_rect(rows, ux, fy, ux + 32, fy + 36, NAVY)
    for sy in range(4):
        for sx in range(4):
            set_px(rows, ux + 4 + sx * 7, fy + 4 + sy * 8, WHITE)
            set_px(rows, ux + 5 + sx * 7, fy + 4 + sy * 8, WHITE)
    # China: red field, yellow stars
    cx = x0 + 122
    fill_rect(rows, cx, fy, cx + 76, fy + fh, (222, 41, 16))
    disc(rows, cx + 16, fy + 16, 9, YELLOW)
    for (sx, sy) in ((40, 8), (48, 18), (48, 30), (40, 38)):
        disc(rows, cx + sx, fy + sy, 4, YELLOW)
    # Russia: white / blue / red bands
    rx = x0 + 222
    fill_rect(rows, rx, fy, rx + 76, fy + 22, WHITE)
    fill_rect(rows, rx, fy + 22, rx + 76, fy + 43, (0, 57, 166))
    fill_rect(rows, rx, fy + 43, rx + 76, fy + fh, (213, 0, 50))
    for fx in (ux, cx, rx):
        vline(rows, fx - 4, fy - 10, fy + fh + 6, GREY, 3)
        disc(rows, fx - 3, fy - 12, 3, GREY)
    draw_text(rows, (x0 + x1) // 2, y0 + 196, "TRUMP PUTIN XI", 3, INK,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 226, "MEET IN SHENZHEN", 3, INK,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 262, "PEACE DECLARATION", 3, RED,
              align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 296, "UN REFORM • MORE OIL", 2,
              GREY, align="center")
    draw_text(rows, (x0 + x1) // 2, y0 + 318, "NUCLEAR RISK TALKS", 2, GREY,
              align="center")


def draw_footer(rows):
    """Ticker strip: the day's hopeful science story."""
    x0, y0, x1, y1 = 20, 940, 1004, 1006
    fill_rect(rows, x0, y0, x1, y1, NAVY)
    draw_text(rows, W // 2, y0 + 14,
              "ALSO: CANCER PILL \u2022 TUMORS UNDETECTABLE IN 1 IN 12", 3,
              CREAM, align="center")
    draw_text(rows, W // 2, y0 + 40, "DARAXONRASIB TRIAL • PANCREATIC CANCER",
              2, (170, 180, 210), align="center")


# ------------------------------------------------------------------- render
def render():
    """Return the front page as a list of 1024 rows of RGB bytearrays."""
    rows = new_canvas(W, H, PAPER)
    # faint paper grain, deterministic
    for y in range(0, H, 3):
        for x in range(0, W, 5):
            h = hash01(x, y)
            if h < 0.05:
                blend_px(rows, x, y, (210, 200, 175), 0.25)
    draw_masthead(rows)
    draw_lead(rows)
    draw_markets(rows)
    draw_justice(rows)
    draw_summit(rows)
    draw_footer(rows)
    return rows


# -------------------------------------------------------------- PNG encoder
def _filter_score(buf):
    """Sum of absolute values of bytes read as signed (PNG heuristic)."""
    return sum(v if v < 128 else 256 - v for v in buf)


def write_png(path, rows):
    """Encode rows (bytearray RGB) as a PNG with per-row filter choice."""
    raw = bytearray()
    prev = bytearray(W * 3)
    for row in rows:
        cands = []
        # Filter 0: None.
        cands.append((0, bytes(row)))
        # Filter 1: Sub.
        sub = bytearray(W * 3)
        for i in range(W * 3):
            left = row[i - 3] if i >= 3 else 0
            sub[i] = (row[i] - left) & 0xFF
        cands.append((1, bytes(sub)))
        # Filter 2: Up.
        up = bytearray(W * 3)
        for i in range(W * 3):
            up[i] = (row[i] - prev[i]) & 0xFF
        cands.append((2, bytes(up)))
        best = min(cands, key=lambda c: _filter_score(c[1]))
        raw.append(best[0])
        raw.extend(best[1])
        prev = row
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = render()
    n = write_png(OUT, rows)
    print("wrote %s (%d bytes, %dx%d)" % (OUT, n, W, H))


if __name__ == "__main__":
    main()
