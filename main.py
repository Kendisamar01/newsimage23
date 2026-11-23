import os
import struct
import zlib

W = 1024
H = 1024

BG = (244, 239, 228)
INK = (24, 27, 31)
CREAM = (247, 242, 228)
RED = (177, 39, 34)
DEEP_RED = (112, 27, 26)
GRAY = (91, 97, 105)
NAVY = (27, 43, 65)
GRID = (49, 69, 94)
GOLD = (222, 176, 78)
SEA = (83, 111, 128)
PANEL = (235, 228, 214)
PANEL2 = (229, 222, 206)

FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
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
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "00100"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


class Raster:
    def __init__(self):
        self.px = bytearray(BG * (W * H))

    def put(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x0, y0, x1, y1, color):
        if x1 < x0 or y1 < y0:
            return
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(W - 1, x1)
        y1 = min(H - 1, y1)
        row = bytes(color) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            start = (y * W + x0) * 3
            self.px[start:start + len(row)] = row

    def brush(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.put(cx + dx, cy + dy, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        r = (width - 1) // 2
        while True:
            self.brush(x0, y0, r, color) if r else self.put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            span = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - span, cy + dy, cx + span, cy + dy, color)

    def ring(self, cx, cy, r, width, color):
        steps = max(48, int(2 * 3.14159 * r))
        for i in range(steps + 1):
            a = 2 * 3.14159 * i / steps
            x = int(cx + r * __import__('math').cos(a))
            y = int(cy + r * __import__('math').sin(a))
            self.disc(x, y, width // 2 + (1 if width % 2 else 0), color)

    def poly(self, points, color):
        ys = [p[1] for p in points]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for i in range(len(points)):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % len(points)]
                if y0 == y1:
                    continue
                if min(y0, y1) <= y < max(y0, y1):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]), y, color)

    def text(self, x, y, s, scale, color, gap=1):
        s = s.upper()
        for ch in s:
            glyph = FONT.get(ch, FONT['?'])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(x + gx * scale, y + gy * scale,
                                  x + (gx + 1) * scale - 1,
                                  y + (gy + 1) * scale - 1, color)
            x += (5 + gap) * scale

    def text_width(self, s, scale, gap=1):
        return ((5 + gap) * len(s) - gap) * scale

    def text_center(self, cx, y, s, scale, color, gap=1):
        self.text(cx - self.text_width(s, scale, gap) // 2, y, s, scale, color, gap)


def draw_masthead(r):
    r.rect(0, 0, W - 1, 116, INK)
    r.rect(0, 116, W - 1, 120, RED)
    r.rect(24, 10, 1000, 12, (74, 80, 87))
    r.rect(24, 84, 1000, 86, (74, 80, 87))
    r.text_center(512, 18, "THE WORLD", 9, CREAM)
    r.rect(836, 18, 984, 82, RED)
    r.text_center(910, 24, "NOV", 3, CREAM)
    r.text_center(910, 47, "23", 5, CREAM)
    r.text_center(512, 88, "MONDAY, NOVEMBER 23, 2026", 4, GOLD)
    r.rect(24, 130, 1000, 132, INK)


def draw_lead(r):
    r.text(30, 138, "GLOBAL MARKETS", 4, RED)
    r.text_center(512, 170, "$4T WIPEOUT", 12, INK)
    r.text_center(512, 260, "AI SELLOFF: NASDAQ BEAR MARKET", 4, GRAY)
    r.rect(24, 292, 1000, 295, INK)
    r.rect(24, 302, 1000, 574, NAVY)
    r.rect(28, 306, 996, 570, GRID)
    r.rect(30, 308, 994, 568, NAVY)
    for x in range(100, 980, 88):
        r.line(x, 310, x, 566, GRID, 1)
    for y in range(350, 551, 40):
        r.line(32, y, 992, y, GRID, 1)
    chart = [(80, 414), (180, 432), (260, 410), (350, 458), (440, 446),
             (520, 492), (610, 474), (700, 516), (790, 500), (880, 538), (960, 556)]
    r.poly(chart + [(960, 566), (80, 566)], DEEP_RED)
    for i in range(len(chart) - 1):
        r.line(chart[i][0], chart[i][1], chart[i + 1][0], chart[i + 1][1], RED, 12)
    r.poly([(974, 562), (938, 550), (954, 522)], RED)
    r.text(48, 320, "$4 TRILLION", 7, CREAM)
    r.text(50, 376, "ERASED IN A WEEK", 3, GOLD)
    r.rect(708, 320, 980, 376, INK)
    r.text(720, 334, "NASDAQ -10%", 4, CREAM)
    r.text_center(512, 584, "WORST WEEK SINCE 2020 - S&P DOW IN CORRECTION", 3, INK)


def panel_frames(r):
    r.rect(24, 610, 336, 798, PANEL)
    r.rect(344, 610, 680, 798, PANEL)
    r.rect(688, 610, 1000, 798, PANEL)
    r.rect(24, 610, 336, 798, INK)
    r.rect(344, 610, 680, 798, INK)
    r.rect(688, 610, 1000, 798, INK)
    r.rect(26, 612, 334, 796, PANEL)
    r.rect(346, 612, 678, 796, PANEL)
    r.rect(690, 612, 998, 796, PANEL)
    r.rect(24, 800, 1000, 804, INK)


def draw_climate_panel(r):
    r.text(36, 622, "CLIMATE", 3, RED)
    r.text(36, 650, "NO DEAL", 6, INK)
    r.text(36, 696, "AT COP31", 4, GRAY)
    r.rect(40, 738, 116, 788, CREAM)
    r.rect(40, 738, 116, 788, INK)
    r.line(50, 752, 106, 752, GRAY, 2)
    r.line(50, 762, 96, 762, GRAY, 2)
    r.line(50, 772, 102, 772, GRAY, 2)
    r.line(44, 742, 112, 784, RED, 7)
    r.line(112, 742, 44, 784, RED, 7)
    r.text(136, 740, "EU REJECTS", 3, RED)
    r.text(136, 770, "DRAFT", 3, INK)


def draw_hormuz_panel(r):
    r.text(356, 622, "IRAN SAYS", 3, RED)
    r.text(356, 650, "TANKERS", 5, INK)
    r.text(356, 688, "HIT MINES", 5, INK)
    r.rect(350, 754, 674, 790, SEA)
    for y in (762, 776, 786):
        r.line(356, y, 668, y, (111, 137, 150), 2)
    for x in (372, 400):
        r.rect(x, 744, x + 26, 762, INK)
        r.rect(x + 18, 738, x + 26, 744, INK)
    for x in (532, 560):
        r.rect(x, 744, x + 26, 762, INK)
        r.rect(x + 18, 738, x + 26, 744, INK)
    for cx, cy in ((430, 760), (590, 758)):
        r.disc(cx, cy, 6, INK)
        for angle in range(0, 360, 60):
            import math
            dx = int(14 * math.cos(math.radians(angle)))
            dy = int(14 * math.sin(math.radians(angle)))
            r.line(cx, cy, cx + dx, cy + dy, RED, 4)
    r.text(458, 758, "2", 4, CREAM)


def draw_ukraine_panel(r):
    r.text(700, 622, "WAR", 3, RED)
    r.text(700, 650, "20 REGIONS", 5, INK)
    r.text(700, 688, "UNDER ATTACK", 4, INK)
    r.rect(704, 770, 780, 790, (83, 83, 86))
    r.rect(712, 752, 734, 770, (110, 110, 112))
    r.rect(746, 760, 770, 770, (110, 110, 112))
    r.poly([(712, 752), (722, 742), (734, 752)], (83, 83, 86))
    r.disc(758, 744, 12, (150, 150, 150))
    r.disc(774, 738, 16, (172, 172, 172))
    r.line(806, 766, 866, 748, INK, 4)
    r.rect(820, 760, 854, 772, INK)
    r.line(820, 760, 806, 748, INK, 3)
    r.line(854, 760, 866, 748, INK, 3)
    r.line(826, 756, 812, 742, INK, 3)
    r.line(848, 756, 862, 742, INK, 3)
    r.text(872, 752, "PATRIOT", 3, RED)
    r.text(872, 776, "PLEA", 3, RED)


def draw_bottom_frames(r):
    r.rect(24, 810, 336, 1008, PANEL2)
    r.rect(344, 810, 680, 1008, PANEL2)
    r.rect(688, 810, 1000, 1008, PANEL2)
    r.rect(24, 810, 336, 1008, INK)
    r.rect(344, 810, 680, 1008, INK)
    r.rect(688, 810, 1000, 1008, INK)
    r.rect(26, 812, 334, 1006, PANEL2)
    r.rect(346, 812, 678, 1006, PANEL2)
    r.rect(690, 812, 998, 1006, PANEL2)


def draw_myanmar_panel(r):
    r.text(36, 820, "WORLD COURT", 3, RED)
    r.text(36, 846, "MYANMAR", 5, INK)
    r.text(36, 884, "GUILTY", 5, INK)
    r.text(36, 924, "GENOCIDE RULING", 3, GRAY)
    r.line(94, 950, 94, 1000, INK, 5)
    r.line(56, 954, 134, 954, INK, 4)
    r.line(66, 954, 56, 976, INK, 2)
    r.line(124, 954, 134, 976, INK, 2)
    r.line(64, 976, 126, 976, INK, 4)
    r.line(80, 954, 68, 976, INK, 2)
    r.line(110, 954, 122, 976, INK, 2)
    r.disc(186, 966, 8, INK)
    r.rect(178, 976, 194, 1000, INK)
    r.disc(216, 972, 6, INK)
    r.rect(210, 980, 222, 1000, INK)
    r.disc(242, 966, 7, INK)
    r.rect(234, 976, 250, 1000, INK)


def draw_gaza_panel(r):
    r.text(356, 820, "CEASEFIRE", 3, RED)
    r.text(356, 846, "TANKS", 5, INK)
    r.text(356, 884, "CROSS LINE", 4, INK)
    r.text(356, 924, "FIRST SINCE TRUCE", 3, GRAY)
    for x in range(356, 672, 28):
        r.rect(x, 964, x + 16, 968, GOLD)
    r.rect(492, 948, 564, 968, INK)
    r.poly([(500, 948), (508, 936), (548, 936), (556, 948)], INK)
    r.rect(552, 940, 568, 946, INK)
    for x in (504, 522, 540):
        r.disc(x, 970, 7, (50, 50, 52))
    r.line(578, 980, 646, 980, INK, 3)
    r.poly([(646, 980), (632, 972), (632, 988)], INK)
    r.text(586, 984, "YELLOW", 3, GOLD)


def draw_iran_panel(r):
    r.text(700, 820, "IRAN", 3, RED)
    r.text(700, 846, "MISSILE CITY", 4, INK)
    r.text(700, 884, "TWIN LAUNCH", 4, INK)
    r.text(700, 924, "NEW LAUNCHER", 3, GRAY)
    r.poly([(744, 1004), (744, 966), (760, 950), (944, 950), (960, 966), (960, 1004)], (94, 94, 96))
    r.poly([(756, 1004), (756, 968), (768, 958), (936, 958), (948, 968), (948, 1004)], INK)
    for x in (790, 864):
        r.poly([(x, 982), (x + 6, 962), (x + 12, 982)], CREAM)
        r.line(x + 6, 962, x + 6, 940, CREAM, 4)
        r.poly([(x + 6, 932), (x - 2, 944), (x + 14, 944)], RED)
    r.rect(826, 966, 850, 1000, GRAY)
    r.rect(830, 970, 846, 982, CREAM)


def draw():
    r = Raster()
    draw_masthead(r)
    draw_lead(r)
    panel_frames(r)
    draw_climate_panel(r)
    draw_hormuz_panel(r)
    draw_ukraine_panel(r)
    draw_bottom_frames(r)
    draw_myanmar_panel(r)
    draw_gaza_panel(r)
    draw_iran_panel(r)
    return r.px


def png_bytes(pixels):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])

    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)

    header = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) +
            chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def main():
    out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'entry.png'), 'wb') as f:
        f.write(png_bytes(draw()))


if __name__ == '__main__':
    main()
