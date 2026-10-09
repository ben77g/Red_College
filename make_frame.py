#!/usr/bin/env python3
"""Generate the white picture-frame border (carved acanthus leaf molding).

Run from this folder:  python3 make_frame.py
It writes frame.svg and replaces the frame CSS block in index.html (between the
"/* detailed white picture frame" comment and the "body.locked #frame" line).

The frame is a 3x3 grid of cells used as a CSS border-image. Each cell is C units
square; the browser scales it to the --frame width. From the outside in, an edge
cell has these bands:

    0- 5  outer fillet (bright edge)
    5-14  bead-and-reel row (pearls alternating with little reels)
   14-18  fillet
   18-58  acanthus band: a shaded hollow with carved, serrated leaves pointing
          outward, gold darts between them
   58-61  fillet
   61-76  egg-and-dart band
   76-79  gold fillet with a highlight
   79-96  inner lip: a row of small pearls, then a cove that darkens toward the
          picture (the "sight edge")

The corner cell carries the same bands mitered at 45 degrees, with a raised
square corner block on top holding a 16-petal rosette and four acanthus leaves.
"""
import re
import urllib.parse

C = 96  # cell size in SVG units (the SVG is a 3x3 grid of cells)

# palette: warm white "gesso" frame with gold accents
LINE = "#bfb7a8"      # carving lines
LINE_D = "#a79d8c"    # deeper carving lines
SHADOW = "#9d9382"    # cast shadow under relief
GOLD = "#d4b86a"
GOLD_D = "#a3843a"
GOLD_L = "#fff3cf"


def grad(gid, stops, horizontal=False, kind="linear", extra=""):
    """Linear gradient; vertical by default (outer edge at top)."""
    if kind == "radial":
        s = f'<radialGradient id="{gid}" {extra}>'
        tail = "</radialGradient>"
    else:
        coords = 'x1="0" y1="0" x2="1" y2="0"' if horizontal else 'x1="0" y1="0" x2="0" y2="1"'
        if "x1=" in extra:
            coords = ""
        s = f'<linearGradient id="{gid}" {coords} {extra}>'
        tail = "</linearGradient>"
    for off, col in stops:
        s += f'<stop offset="{off}" stop-color="{col}"/>'
    return s + tail


# band fills (V = for horizontal bands, H = rotated copies for the vertical bands in the corner)
BANDS = {
    "fillet": [(0, "#ffffff"), (0.5, "#f7f4ee"), (1, "#e3ded3")],
    "groove": [(0, "#cfc8ba"), (0.35, "#e8e3d9"), (0.7, "#f6f3ed"), (1, "#d9d3c6")],
    "hollow": [(0, "#bcb3a3"), (0.18, "#d1cabc"), (0.55, "#e9e5dc"), (0.85, "#f1eee7"), (1, "#d9d3c6")],
    "egg": [(0, "#f1ede5"), (0.5, "#fdfcf9"), (1, "#d8d2c5")],
    "cove": [(0, "#fbfaf6"), (0.45, "#e9e5db"), (0.8, "#c9c2b3"), (1, "#aaa08e")],
    "goldband": [(0, "#fff0bf"), (0.45, "#e2c87c"), (1, "#b2924a")],
}


def defs():
    out = ["<defs>"]
    for name, stops in BANDS.items():
        out.append(grad(name + "V", stops))
        out.append(grad(name + "H", stops, horizontal=True))
    out.append(grad("leafG", [(0, "#d9d3c6"), (0.35, "#f1eee7"), (0.7, "#ffffff"), (1, "#f8f6f2")],
                    extra='x1="0" y1="1" x2="0" y2="0"'))
    out.append(grad("curl", [(0, "#d7d1c3"), (1, "#f8f6f1")], extra='x1="0" y1="0" x2="0" y2="1"'))
    out.append(grad("goldG", [(0, GOLD_L), (0.45, "#e4c877"), (1, "#a8873c")], extra='x1="0" y1="0" x2="1" y2="1"'))
    out.append(grad("pearl", [(0, "#ffffff"), (0.55, "#f3f0e9"), (1, "#bdb5a5")], kind="radial",
                    extra='cx=".36" cy=".32" r=".75"'))
    out.append(grad("eggG", [(0, "#ffffff"), (0.6, "#f2eee6"), (1, "#c5bdad")], kind="radial",
                    extra='cx=".4" cy=".3" r=".8"'))
    out.append(grad("petal", [(0, "#ffffff"), (0.65, "#f4f1ea"), (1, "#cfc8b9")], kind="radial",
                    extra='cx=".5" cy=".25" r=".9"'))
    out.append(grad("boss", [(0, "#fff8e0"), (0.5, "#e4c877"), (1, "#9c7c33")], kind="radial",
                    extra='cx=".38" cy=".35" r=".8"'))
    out.append(grad("block", [(0, "#ffffff"), (0.5, "#f5f2ec"), (1, "#ddd7ca")], extra='x1="0" y1="0" x2="1" y2="1"'))
    # clip for the lower-left triangle of a corner cell (the vertical half of the miter)
    out.append(f'<clipPath id="miter"><polygon points="0,0 0,{C} {C},{C}"/></clipPath>')
    out.append(f'<clipPath id="miterTop"><polygon points="0,0 {C},0 {C},{C}"/></clipPath>')
    out.append(leaf_symbol())
    out.append("</defs>")
    return "".join(out)


# ---------------------------------------------------------------- acanthus leaf
# The leaf is built from tooth tips: each lobe is a list of (x, y) tips on the right
# half (base at the origin, tip pointing up). Consecutive tips are joined by concave
# scallops, lobes are separated by a deep round "eye", and the left half mirrors it.
LOBES = [
    [(5.5, -1.5), (10.5, -4), (13, -8.5), (11, -12.5)],
    [(11, -15.2), (12.5, -20), (10.5, -24.5)],
    [(9.5, -27), (10.5, -31.5), (8, -35)],
    [(6, -37.2), (3.2, -40), (0, -42)],
]
EYES = [(3.6, -13.8), (3.2, -25.8), (2.8, -36)]  # hollow between lobe i and i+1


def _scallop(a, b, depth, m):
    """Quadratic from a to b bowing toward the midrib (so a pointed tooth sits at each end)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = (dx * dx + dy * dy) ** .5 or 1
    nx, ny = m * dy / L, -m * dx / L   # inward normal for an upward-running edge
    mx, my = (a[0] + b[0]) / 2 + nx * depth, (a[1] + b[1]) / 2 + ny * depth
    return f"Q{mx:.1f} {my:.1f} {b[0]:.1f} {b[1]:.1f} "


def _half(mirror=False):
    m = -1 if mirror else 1
    pts = [[(m * x, y) for x, y in lobe] for lobe in LOBES]
    eyes = [(m * x, y) for x, y in EYES]
    d = ""
    prev = (0, 0)
    for i, lobe in enumerate(pts):
        for j, p in enumerate(lobe):
            if i == 0 and j == 0:
                d += f"C{m * 2} {-0.1} {m * 3.5} {-0.5} {p[0]:.1f} {p[1]:.1f} "
            elif j == 0:
                e = eyes[i - 1]
                d += f"Q{e[0] + m * 1.2:.1f} {p[1] + 0.8:.1f} {p[0]:.1f} {p[1]:.1f} "
            else:
                d += _scallop(prev, p, 2.4 if i < 3 else 1.4, m)
            prev = p
        if i < len(eyes):
            e = eyes[i]
            # dive into the eye: a rounded hollow
            d += f"Q{e[0] + m * (prev[0] - e[0]) * .45:.1f} {prev[1] + .3:.1f} {e[0] + m * 2.3:.1f} {e[1] + 1:.1f} "
            d += f"A2.3 2.3 0 0 {0 if mirror else 1} {e[0] + m * 1.4:.1f} {e[1] - 2:.1f} "
            prev = (e[0] + m * 1.4, e[1] - 2)
    return d


LEAF_RIGHT = "M0 0 " + _half(False) + "L0 -1 Z"
LEAF_LEFT = "M0 0 " + _half(True) + "L0 -1 Z"

LEAF_VEINS = (
    # midrib: a raised rib (shadow on the left, light on the right)
    f'<path d="M-0.7 -1 Q-1.2 -19 -0.5 -35" stroke="{LINE_D}" stroke-width="1.1" fill="none" stroke-linecap="round"/>'
    f'<path d="M0.8 -1.5 Q0.4 -19 0.9 -34.5" stroke="#ffffff" stroke-width=".8" fill="none" opacity=".95"/>'
    # side veins: one per lobe, sweeping up from the midrib to the lobe's leading tooth
    f'<path d="M0 -4 C4 -4.5 8 -5.5 11.5 -9 M0 -16 C4 -16.5 8 -18 10.8 -21.5 M0 -27.5 C3.5 -28 6.5 -29.5 9 -32.5 M0 -36.5 C2 -37 3.5 -38 4.8 -39.5" '
    f'stroke="{LINE_D}" stroke-width=".7" fill="none" stroke-linecap="round" opacity=".9"/>'
    f'<path d="M0 -4 C-4 -4.5 -8 -5.5 -11.5 -9 M0 -16 C-4 -16.5 -8 -18 -10.8 -21.5 M0 -27.5 C-3.5 -28 -6.5 -29.5 -9 -32.5 M0 -36.5 C-2 -37 -3.5 -38 -4.8 -39.5" '
    f'stroke="{LINE_D}" stroke-width=".7" fill="none" stroke-linecap="round" opacity=".9"/>'
    f'<path d="M0.5 -3.3 C4.5 -3.8 8.3 -4.8 11.6 -8.2 M0.5 -15.3 C4.5 -15.8 8.3 -17.3 10.9 -20.7 M0.5 -26.8 C4 -27.3 6.8 -28.8 9.1 -31.7" '
    f'stroke="#ffffff" stroke-width=".5" fill="none" opacity=".55"/>'
    f'<path d="M-0.5 -3.3 C-4.5 -3.8 -8.3 -4.8 -11.6 -8.2 M-0.5 -15.3 C-4.5 -15.8 -8.3 -17.3 -10.9 -20.7 M-0.5 -26.8 C-4 -27.3 -6.8 -28.8 -9.1 -31.7" '
    f'stroke="#ffffff" stroke-width=".5" fill="none" opacity=".55"/>'
    # pipes: the shaded channels that run down from each eye toward the base
    f'<path d="M5.2 -13 C6 -10 6.8 -7 7.8 -3.5 M4.6 -25 C5.3 -22 6.2 -19 7 -16 M3.8 -35.2 C4.3 -33 5 -30.5 5.8 -28" '
    f'stroke="{SHADOW}" stroke-width="1.7" fill="none" stroke-linecap="round" opacity=".5"/>'
    f'<path d="M-5.2 -13 C-6 -10 -6.8 -7 -7.8 -3.5 M-4.6 -25 C-5.3 -22 -6.2 -19 -7 -16 M-3.8 -35.2 C-4.3 -33 -5 -30.5 -5.8 -28" '
    f'stroke="{SHADOW}" stroke-width="1.7" fill="none" stroke-linecap="round" opacity=".5"/>'
)

# overturned tip: the top of an acanthus leaf folds forward over itself
LEAF_CURL = (
    f'<path d="M-5.6 -37.4 C-2.5 -43.5 3.5 -43.5 6 -38 C4 -35 0.6 -34.2 -1.8 -35.2 C-3.6 -35.9 -4.9 -36.5 -5.6 -37.4 Z" '
    f'transform="translate(.9 1.1)" fill="{SHADOW}" opacity=".45"/>'
    f'<path d="M-5.6 -37.4 C-2.5 -43.5 3.5 -43.5 6 -38 C4 -35 0.6 -34.2 -1.8 -35.2 C-3.6 -35.9 -4.9 -36.5 -5.6 -37.4 Z" '
    f'fill="url(#curl)" stroke="{LINE}" stroke-width=".8" stroke-linejoin="round"/>'
    f'<path d="M-4 -37.6 C-1.5 -41.6 2.8 -41.6 4.8 -38.3" stroke="#ffffff" stroke-width=".8" fill="none" stroke-linecap="round"/>'
    f'<path d="M-3.6 -36.4 C-0.8 -34.9 2.2 -35.1 4.6 -37.4" stroke="{LINE_D}" stroke-width=".5" fill="none"/>'
)


def leaf_symbol():
    """The leaf drawn once (in <defs>); leaf() stamps copies of it with <use>."""
    both = LEAF_RIGHT + LEAF_LEFT
    g = '<g id="lf">'
    # relief: cast shadow under the whole leaf
    g += f'<path d="{both}" transform="translate(1.1 1.4)" fill="{SHADOW}" opacity=".45"/>'
    g += f'<path d="{both}" fill="url(#leafG)" stroke="{LINE}" stroke-width=".85" stroke-linejoin="round"/>'
    # the left half sits in shade (light comes from the upper right)
    g += f'<path d="{LEAF_LEFT}" fill="{SHADOW}" opacity=".2"/>'
    g += LEAF_VEINS + LEAF_CURL
    return g + "</g>"


def leaf(x, y, rot=0, scale=1):
    return f'<use href="#lf" transform="translate({x} {y}) rotate({rot}) scale({scale})"/>'


# ----------------------------------------------------------------- ornaments
def dart(x, y0, y1, w=4.2):
    """Gold dart (a pointed spear) between leaves, pointing outward (toward y0)."""
    mid = y0 + (y1 - y0) * 0.6
    d = f"M{x} {y0} Q{x + w} {mid} {x + w * .55} {y1} L{x} {y1 - 3} L{x - w * .55} {y1} Q{x - w} {mid} {x} {y0} Z"
    return (f'<path d="{d}" transform="translate(.8 1)" fill="{SHADOW}" opacity=".4"/>'
            f'<path d="{d}" fill="url(#goldG)" stroke="{GOLD_D}" stroke-width=".7" stroke-linejoin="round"/>'
            f'<path d="M{x} {y0 + 3} L{x} {y1 - 4}" stroke="{GOLD_L}" stroke-width=".8" stroke-linecap="round"/>')


def bead_and_reel(y0, y1):
    """Pearls alternating with pairs of little reels along the cell."""
    cy = (y0 + y1) / 2
    r = (y1 - y0) / 2 - 0.9
    out = []
    period = 16
    for i in range(C // period):
        bx = i * period + 8
        # reel pair on the left of each bead
        for rx in (bx - 5.2, bx - 3.2):
            out.append(f'<ellipse cx="{rx:.1f}" cy="{cy}" rx="0.9" ry="{r * .78:.2f}" fill="url(#pearl)" stroke="{LINE}" stroke-width=".5"/>')
        out.append(f'<circle cx="{bx + .6}" cy="{cy + .7}" r="{r:.2f}" fill="{SHADOW}" opacity=".35"/>')
        out.append(f'<circle cx="{bx}" cy="{cy}" r="{r:.2f}" fill="url(#pearl)" stroke="{LINE}" stroke-width=".6"/>')
        out.append(f'<circle cx="{bx - r * .35:.2f}" cy="{cy - r * .4:.2f}" r="{r * .3:.2f}" fill="#ffffff" opacity=".9"/>')
    return "".join(out)


def egg_and_dart(y0, y1):
    """Eggs in shells with darts between them; the band's inner side is y1."""
    out = []
    period = 24
    cy = (y0 + y1) / 2 + 0.5
    ry = (y1 - y0) / 2 - 2
    rx = ry * 1.05
    for i in range(C // period):
        cx = i * period + period / 2
        # shell: a thicker arc behind the egg, open toward the inner side
        out.append(f'<path d="M{cx - rx - 2.6:.1f} {y1 - 1} A{rx + 2.6:.1f} {ry + 2.4:.1f} 0 0 1 {cx + rx + 2.6:.1f} {y1 - 1} Z" '
                   f'fill="#e9e4da" stroke="{LINE}" stroke-width=".7"/>')
        out.append(f'<path d="M{cx - rx - 1.3:.1f} {y1 - 1} A{rx + 1.3:.1f} {ry + 1.2:.1f} 0 0 1 {cx + rx + 1.3:.1f} {y1 - 1} Z" '
                   f'fill="{SHADOW}" opacity=".35"/>')
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#eggG)" stroke="{LINE}" stroke-width=".7"/>')
        out.append(f'<ellipse cx="{cx - rx * .3:.1f}" cy="{cy - ry * .35:.1f}" rx="{rx * .3:.1f}" ry="{ry * .22:.1f}" fill="#ffffff" opacity=".85"/>')
    for i in range(C // period + 1):
        x = i * period
        # dart pointing inward (toward the picture)
        d = f"M{x} {y0 + 1.5} L{x + 1.6} {y0 + 5} L{x + 1.4} {y1 - 4} L{x} {y1 - 1} L{x - 1.4} {y1 - 4} L{x - 1.6} {y0 + 5} Z"
        out.append(f'<path d="{d}" fill="url(#goldG)" stroke="{GOLD_D}" stroke-width=".55" stroke-linejoin="round"/>')
    return "".join(out)


def pearl_row(y0, y1, period=8):
    cy = (y0 + y1) / 2
    r = (y1 - y0) / 2 - 0.6
    out = []
    for i in range(C // period):
        cx = i * period + period / 2
        out.append(f'<circle cx="{cx + .4}" cy="{cy + .5}" r="{r:.2f}" fill="{SHADOW}" opacity=".35"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="url(#pearl)" stroke="{LINE}" stroke-width=".5"/>')
        out.append(f'<circle cx="{cx - r * .35:.2f}" cy="{cy - r * .4:.2f}" r="{r * .28:.2f}" fill="#ffffff"/>')
    return "".join(out)


# ----------------------------------------------------------------- band layout
# (y0, y1, gradient name) from the outer edge inward
LAYOUT = [
    (0, 5, "fillet"),
    (5, 14, "groove"),
    (14, 18, "fillet"),
    (18, 58, "hollow"),
    (58, 61, "fillet"),
    (61, 76, "egg"),
    (76, 79, "goldband"),
    (79, C, "cove"),
]


def band_rects(orient="V"):
    """Plain band fills. 'V' draws horizontal bands (outer edge at top);
    'H' draws them as vertical bands (outer edge at left)."""
    out = []
    for y0, y1, name in LAYOUT:
        if orient == "V":
            out.append(f'<rect x="0" y="{y0}" width="{C}" height="{y1 - y0}" fill="url(#{name}V)"/>')
        else:
            out.append(f'<rect x="{y0}" y="0" width="{y1 - y0}" height="{C}" fill="url(#{name}H)"/>')
    # carving lines at the band edges and highlight lines on the fillets
    lines = []
    for y0, y1, name in LAYOUT[1:]:
        lines.append((y0, LINE, .8, 1))
    lines += [(1.2, "#ffffff", .9, .9), (15.2, "#ffffff", .8, .9), (59.2, "#ffffff", .8, .9),
              (76.6, GOLD_L, .8, 1), (78.4, GOLD_D, .6, .8), (C - 0.6, "#8f8574", 1.2, 1)]
    for pos, col, w, op in lines:
        if orient == "V":
            out.append(f'<line x1="0" y1="{pos}" x2="{C}" y2="{pos}" stroke="{col}" stroke-width="{w}" opacity="{op}"/>')
        else:
            out.append(f'<line x1="{pos}" y1="0" x2="{pos}" y2="{C}" stroke="{col}" stroke-width="{w}" opacity="{op}"/>')
    return "".join(out)


def ornaments():
    """The carved ornament of one horizontal edge cell (outer edge at top)."""
    g = []
    g.append(bead_and_reel(5, 14))
    # acanthus band: leaves point outward, base on the inner side of the hollow
    for x in (0, 48, 96):
        g.append(dart(x, 24, 55))
    for cx in (24, 72):
        g.append(leaf(cx, 56, 0, 0.98))
    g.append(egg_and_dart(61, 76))
    g.append(pearl_row(80, 87))
    return "".join(g)


def edge_cell():
    return band_rects("V") + ornaments()


def mirror_diag(content):
    """Reflect edge-cell content across the cell's main diagonal, so the outer edge
    moves from the top to the left side (the vertical half of a mitered corner)."""
    return f'<g transform="matrix(0 1 1 0 0 0)">{content}</g>'


def corner_cell():
    g = []
    # mitered bands: horizontal run above the diagonal, vertical run below it
    g.append('<g clip-path="url(#miterTop)"><use href="#edge"/></g>')
    g.append(f'<g clip-path="url(#miter)">{mirror_diag('<use href="#edge"/>')}</g>')
    g.append(f'<line x1="0" y1="0" x2="{C}" y2="{C}" stroke="{LINE_D}" stroke-width=".7" opacity=".7"/>')

    # raised corner block (patera) sitting over the miter
    b0, b1 = 15, 81
    g.append(f'<rect x="{b0 + 1.5}" y="{b0 + 2}" width="{b1 - b0}" height="{b1 - b0}" rx="3" fill="{SHADOW}" opacity=".45"/>')
    g.append(f'<rect x="{b0}" y="{b0}" width="{b1 - b0}" height="{b1 - b0}" rx="2.5" fill="url(#block)" stroke="{LINE}" stroke-width="1"/>')
    g.append(f'<rect x="{b0 + 3.5}" y="{b0 + 3.5}" width="{b1 - b0 - 7}" height="{b1 - b0 - 7}" rx="1.5" fill="none" stroke="{GOLD}" stroke-width="1.1"/>')
    g.append(f'<rect x="{b0 + 3.5}" y="{b0 + 3.5}" width="{b1 - b0 - 7}" height="{b1 - b0 - 7}" rx="1.5" fill="none" stroke="{GOLD_L}" stroke-width=".4" transform="translate(-.4 -.4)"/>')
    g.append(f'<rect x="{b0 + 6}" y="{b0 + 6}" width="{b1 - b0 - 12}" height="{b1 - b0 - 12}" rx="1" fill="none" stroke="{LINE}" stroke-width=".6"/>')

    cx = cy = (b0 + b1) / 2
    # four acanthus leaves pointing to the block's corners, under the rosette
    for a in (-135, -45, 45, 135):
        g.append(leaf(cx, cy, a, 0.8))
    # four small gold darts between the leaves
    for a in (0, 90, 180, 270):
        g.append(f'<g transform="translate({cx} {cy}) rotate({a})">{dart(0, -27, -8, 3.2)}</g>')

    # rosette: 16 pointed outer petals, 8 inner petals, gold boss
    g.append(f'<circle cx="{cx + .8}" cy="{cy + 1}" r="21" fill="{SHADOW}" opacity=".4"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="20.5" fill="#efebe3" stroke="{LINE}" stroke-width=".8"/>')
    petal = "M0 -20 C 4.2 -16 4.6 -8 0 -3 C -4.6 -8 -4.2 -16 0 -20 Z"
    for n in range(16):
        g.append(f'<path d="{petal}" fill="url(#petal)" stroke="{LINE}" stroke-width=".7" transform="translate({cx} {cy}) rotate({n * 22.5})"/>')
        g.append(f'<path d="M0 -17 L0 -5" stroke="{LINE_D}" stroke-width=".5" transform="translate({cx} {cy}) rotate({n * 22.5})"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="9.5" fill="#f6f3ec" stroke="{LINE}" stroke-width=".8"/>')
    petal2 = "M0 -11 C 3 -8.5 3.2 -4 0 -1.5 C -3.2 -4 -3 -8.5 0 -11 Z"
    for n in range(8):
        g.append(f'<path d="{petal2}" fill="#ffffff" stroke="{LINE}" stroke-width=".6" transform="translate({cx} {cy}) rotate({n * 45 + 22.5})"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="4.6" fill="url(#boss)" stroke="{GOLD_D}" stroke-width=".8"/>')
    g.append(f'<circle cx="{cx - 1.4}" cy="{cy - 1.5}" r="1.3" fill="{GOLD_L}"/>')
    return "".join(g)


def place(ref, col, row, rot=0, flip=False):
    t = f"translate({col * C} {row * C})"
    if rot or flip:
        t += f" translate({C / 2} {C / 2})"
        if flip:
            t += " scale(-1 1)"
        if rot:
            t += f" rotate({rot})"
        t += f" translate({-C / 2} {-C / 2})"
    return f'<use href="#{ref}" transform="{t}"/>'


def main():
    parts = [defs(), f'<defs><g id="edge">{edge_cell()}</g><g id="corner">{corner_cell()}</g></defs>',
             f'<rect width="{3 * C}" height="{3 * C}" fill="#f6f4ef"/>',
             place("edge", 1, 0), place("edge", 1, 2, rot=180), place("edge", 0, 1, rot=-90), place("edge", 2, 1, rot=90),
             place("corner", 0, 0), place("corner", 2, 0, flip=True), place("corner", 0, 2, rot=-90), place("corner", 2, 2, rot=180)]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{3 * C}" height="{3 * C}" '
           f'viewBox="0 0 {3 * C} {3 * C}" shape-rendering="geometricPrecision">' + "".join(parts) + "</svg>")
    open("frame.svg", "w").write(svg)
    uri = "data:image/svg+xml," + urllib.parse.quote(svg, safe="/:=' ()-.,")

    css = f'''  /* detailed white picture frame, acanthus leaf molding (SVG border-image, generated by make_frame.py) */
  :root {{ --frame:46px; }}
  @media (max-width:600px) {{ :root {{ --frame:26px; }} }}
  body {{ padding:var(--frame); }}
  #frame {{ position:fixed; inset:0; z-index:900; pointer-events:none; border:var(--frame) solid #f6f4ef;
    border-image-source:url("{uri}"); border-image-slice:{C}; border-image-width:var(--frame); border-image-repeat:round;
    filter:drop-shadow(0 0 9px rgba(90,40,70,.5)) drop-shadow(0 0 1px rgba(90,40,70,.5)); }}
  body.locked #frame {{ display:none; }}'''
    s = open("index.html").read()
    a = s.index("  /* detailed white picture frame")
    end_marker = "  body.locked #frame { display:none; }"
    b = s.index(end_marker) + len(end_marker)
    s = s[:a] + css + s[b:]
    open("index.html", "w").write(s)
    print("frame.svg and index.html updated")


if __name__ == "__main__":
    main()
