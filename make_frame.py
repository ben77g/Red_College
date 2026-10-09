#!/usr/bin/env python3
"""Generate the carved white picture-frame border (acanthus leaf molding).

Run from this folder:  python3 make_frame.py
It writes frame.svg and replaces the frame CSS block in index.html (between the
"/* detailed white picture frame" comment and the "body.locked #frame" line).

The frame is a 3x3 grid of 64-unit cells used as a CSS border-image. Reading an
edge cell from the outside (y=0) to the inside (y=64):

  0-3    outer fillet (bright highlight) and a shadow groove
  3-9    string of pearls (bead-and-reel)
  9-41   acanthus band: serrated leaves pointing outward, gold darts between
  41-44  fillet
  44-54  egg-and-dart band
  54-56  gold fillet
  56-64  bevelled inner lip (sight edge)

Corners are mitred: the horizontal bands are clipped to the triangle above the
diagonal, the vertical bands to the triangle below it, and a carved rosette on a
square plinth sits over the mitre.
"""
import re
import urllib.parse

C = 64  # cell size in SVG units; the SVG is a 3x3 grid of cells

# carved ivory palette
WHITE = "#ffffff"
IVORY = "#f7f4ee"
MID = "#e6e1d6"
SHADE = "#cfc8b9"
DEEP = "#a9a08d"
LINE = "#b6ae9d"
GOLD = "#d8bd74"
GOLD_DK = "#a8893c"
GOLD_LT = "#fff3cf"

DEFS = f'''<defs>
<linearGradient id="bandA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfc8b9"/><stop offset=".25" stop-color="#ebe7de"/><stop offset=".7" stop-color="#f6f3ec"/><stop offset="1" stop-color="#ddd7ca"/></linearGradient>
<linearGradient id="bandB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9d3c5"/><stop offset=".5" stop-color="#f4f1ea"/><stop offset="1" stop-color="#e1dccf"/></linearGradient>
<linearGradient id="lip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbfaf6"/><stop offset=".6" stop-color="#e4dfd3"/><stop offset="1" stop-color="#b9b1a0"/></linearGradient>
<linearGradient id="leaf" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#cfc8b9"/><stop offset=".35" stop-color="#f3f0e9"/><stop offset=".75" stop-color="#ffffff"/><stop offset="1" stop-color="#e9e5db"/></linearGradient>
<linearGradient id="leafL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity=".55"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
<linearGradient id="leafR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8f8673" stop-opacity="0"/><stop offset="1" stop-color="#8f8673" stop-opacity=".28"/></linearGradient>
<radialGradient id="pearl" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#ebe6dc"/><stop offset="1" stop-color="#b3ab9a"/></radialGradient>
<radialGradient id="egg" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#eee9df"/><stop offset="1" stop-color="#bdb5a4"/></radialGradient>
<radialGradient id="petal" cx=".5" cy=".2" r=".9"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#eeeae1"/><stop offset="1" stop-color="#c1b9a8"/></radialGradient>
<radialGradient id="boss" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff6d6"/><stop offset=".5" stop-color="#e2c77f"/><stop offset="1" stop-color="#9c7d30"/></radialGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff3cf"/><stop offset=".5" stop-color="#dcc077"/><stop offset="1" stop-color="#a8893c"/></linearGradient>
<linearGradient id="goldV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a8893c"/><stop offset=".3" stop-color="#fff3cf"/><stop offset=".7" stop-color="#d8bd74"/><stop offset="1" stop-color="#8f7230"/></linearGradient>
<linearGradient id="plinth" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#ece8df"/><stop offset="1" stop-color="#cbc4b4"/></linearGradient>
<clipPath id="cpTop"><path d="M0 0 L{C} 0 L{C} {C} Z"/></clipPath>
<clipPath id="cpLeft"><path d="M0 0 L{C} {C} L0 {C} Z"/></clipPath>
</defs>'''


# ----------------------------------------------------------------- leaves
# Right-hand outline of an acanthus leaf, base at (0,0), tip at (0,-31).
# Each entry is (command, points...). Four lobes, each with two sharp teeth and a
# deep notch back toward the midrib, then a curled tip.
RIGHT = [
    ("C", (2.5, -0.5, 6.5, -1, 9.5, -3)),
    ("L", (13.5, -5.5)),
    ("Q", (11, -6.2, 9.5, -6)),
    ("L", (12.8, -9.2)),
    ("Q", (9, -9.6, 5, -8.6)),
    ("C", (8, -10.2, 11.5, -12, 13.6, -14.2)),
    ("L", (13, -16.8)),
    ("Q", (10.2, -16.6, 9, -16.2)),
    ("L", (11.2, -19.4)),
    ("Q", (7.6, -19.4, 4.6, -17.6)),
    ("C", (7.2, -19.8, 10, -21.6, 11, -24.2)),
    ("L", (9.6, -26.4)),
    ("Q", (7.2, -25.8, 5.6, -25.2)),
    ("L", (6.4, -27.8)),
    ("Q", (4, -27.2, 2.8, -26.6)),
    ("C", (4.2, -28.6, 3.2, -30.6, 0, -31)),
]


def _fmt(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def _seg(cmd, pts):
    return cmd + " ".join(_fmt(v) for v in pts) + " "


def _mirror_reversed(segs, start=(0, 0)):
    """Walk the segments backwards with x negated, so the path continues from the
    tip down the left side back to the base."""
    # absolute end points of each segment
    ends = []
    cur = start
    for cmd, pts in segs:
        cur = (pts[-2], pts[-1])
        ends.append(cur)
    out = ""
    for i in range(len(segs) - 1, -1, -1):
        cmd, pts = segs[i]
        prev = ends[i - 1] if i > 0 else start
        if cmd == "L":
            out += _seg("L", (-prev[0], prev[1]))
        elif cmd == "Q":
            out += _seg("Q", (-pts[0], pts[1], -prev[0], prev[1]))
        elif cmd == "C":
            out += _seg("C", (-pts[2], pts[3], -pts[0], pts[1], -prev[0], prev[1]))
    return out


def leaf_outline():
    d = "M0 0 " + "".join(_seg(c, p) for c, p in RIGHT)
    return d + _mirror_reversed(RIGHT) + "Z"


def leaf_half(right=True):
    """Closed half leaf (outline plus the midrib) for one-sided shading."""
    d = "M0 0 " + "".join(_seg(c, p) for c, p in RIGHT) + "L0 0 Z"
    if right:
        return d
    # mirror x for the left half
    return re.sub(r"(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)",
                  lambda m: f"{_fmt(-float(m.group(1)))} {m.group(2)}", d)


def leaf(x, y, rot=0, scale=1):
    o = leaf_outline()
    veins = (
        f'<path d="M0 -1.5 L0 -29" stroke="{DEEP}" stroke-width="1" fill="none" stroke-linecap="round"/>'
        f'<path d="M-0.7 -1.5 L-0.7 -28" stroke="#ffffff" stroke-width=".6" fill="none" stroke-opacity=".9"/>'
        f'<path d="M0 -4 Q5 -4.5 10.5 -6.5 M0 -11 Q5.5 -12 11 -15.5 M0 -19 Q4.5 -20 8.5 -23.5 M0 -25.5 Q2.5 -26 4.5 -27.5 '
        f'M0 -4 Q-5 -4.5 -10.5 -6.5 M0 -11 Q-5.5 -12 -11 -15.5 M0 -19 Q-4.5 -20 -8.5 -23.5 M0 -25.5 Q-2.5 -26 -4.5 -27.5" '
        f'stroke="{DEEP}" stroke-width=".55" fill="none" stroke-opacity=".8"/>'
    )
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({scale})">'
            # carved shadow under the leaf
            f'<path d="{o}" fill="#8f8673" fill-opacity=".35" transform="translate(1.1 1.3)"/>'
            f'<path d="{o}" fill="url(#leaf)" stroke="{LINE}" stroke-width=".9" stroke-linejoin="round"/>'
            # light from the top-left: left half lit, right half in shade
            f'<path d="{leaf_half(False)}" fill="url(#leafL)"/>'
            f'<path d="{leaf_half(True)}" fill="url(#leafR)"/>'
            f'{veins}</g>')


def dart(x, y0, y1):
    """Gold spear between two leaves (base at y1 on the inner side, point at y0)."""
    mid = (y0 + y1) / 2
    w = 3.2
    return (f'<path d="M{x} {y0} Q{x+w} {mid} {x} {y1} Q{x-w} {mid} {x} {y0} Z" '
            f'fill="#6e5a22" fill-opacity=".45" transform="translate(.8 1)"/>'
            f'<path d="M{x} {y0} Q{x+w} {mid} {x} {y1} Q{x-w} {mid} {x} {y0} Z" '
            f'fill="url(#gold)" stroke="{GOLD_DK}" stroke-width=".6"/>'
            f'<path d="M{x} {y0+2} L{x} {y1-2}" stroke="{GOLD_LT}" stroke-width=".7" stroke-linecap="round"/>'
            f'<path d="M{x-1.4} {mid-4} Q{x-2} {mid} {x-1.4} {mid+4}" stroke="{GOLD_LT}" stroke-width=".5" fill="none" stroke-opacity=".8"/>')


# ----------------------------------------------------------------- bands
def bead_row(y, r=2.0, step=4.0):
    g = []
    g.append(f'<rect x="0" y="{y-r-1}" width="{C}" height="{2*r+2}" fill="#d2cbbc"/>')
    g.append(f'<line x1="0" y1="{y-r-0.9}" x2="{C}" y2="{y-r-0.9}" stroke="{DEEP}" stroke-width=".6"/>')
    n = int(C / step)
    for i in range(n):
        cx = step / 2 + i * step
        g.append(f'<circle cx="{cx+.4}" cy="{y+.5}" r="{r}" fill="#7b7262" fill-opacity=".45"/>')
        g.append(f'<circle cx="{cx}" cy="{y}" r="{r}" fill="url(#pearl)" stroke="{LINE}" stroke-width=".45"/>')
        g.append(f'<circle cx="{cx-.6}" cy="{y-.7}" r=".55" fill="#ffffff"/>')
    return "".join(g)


def egg_and_dart(y0, y1):
    """Classic egg-and-dart: eggs in shells every 16 units with darts between."""
    g = []
    cy = (y0 + y1) / 2
    h = (y1 - y0)
    g.append(f'<rect x="0" y="{y0}" width="{C}" height="{h}" fill="url(#bandB)"/>')
    for i in range(4):
        cx = 8 + 16 * i
        # shell (the hollow around the egg), opening toward the inside of the frame
        g.append(f'<path d="M{cx-7} {y1} A7 {h*0.92} 0 0 1 {cx+7} {y1} Z" fill="#aaa18e"/>')
        g.append(f'<path d="M{cx-6.2} {y1} A6.2 {h*0.82} 0 0 1 {cx+6.2} {y1} Z" fill="#faf8f3" stroke="{DEEP}" stroke-width=".5"/>')
        g.append(f'<path d="M{cx-5.4} {y1} A5.4 {h*0.72} 0 0 1 {cx+5.4} {y1}" fill="none" stroke="#d6cfc0" stroke-width=".5"/>')
        # egg
        g.append(f'<ellipse cx="{cx+.5}" cy="{cy+1}" rx="4.1" ry="{h*0.42}" fill="#7b7262" fill-opacity=".4"/>')
        g.append(f'<ellipse cx="{cx}" cy="{cy+.4}" rx="4.1" ry="{h*0.42}" fill="url(#egg)" stroke="{LINE}" stroke-width=".55"/>')
        g.append(f'<ellipse cx="{cx-1.2}" cy="{cy-1.2}" rx="1.3" ry="1.7" fill="#ffffff" fill-opacity=".85"/>')
        # dart between eggs
        dx = 16 * i
        g.append(f'<path d="M{dx} {y0+1} L{dx+1.7} {cy} L{dx} {y1-.5} L{dx-1.7} {cy} Z" fill="#8c8270"/>')
        g.append(f'<path d="M{dx} {y0+1.6} L{dx+1.1} {cy} L{dx} {y1-1} L{dx-1.1} {cy} Z" fill="url(#goldV)"/>')
    return "".join(g)


def fillet(y, h, top=WHITE, bottom=SHADE):
    return (f'<rect x="0" y="{y}" width="{C}" height="{h}" fill="{MID}"/>'
            f'<line x1="0" y1="{y+.35}" x2="{C}" y2="{y+.35}" stroke="{top}" stroke-width=".7"/>'
            f'<line x1="0" y1="{y+h-.35}" x2="{C}" y2="{y+h-.35}" stroke="{bottom}" stroke-width=".7"/>')


def gold_fillet(y, h):
    return (f'<rect x="0" y="{y}" width="{C}" height="{h}" fill="url(#goldV)"/>'
            f'<line x1="0" y1="{y+.3}" x2="{C}" y2="{y+.3}" stroke="{GOLD_DK}" stroke-width=".5"/>'
            f'<line x1="0" y1="{y+h-.3}" x2="{C}" y2="{y+h-.3}" stroke="#6e5a22" stroke-width=".6"/>')


def edge_cell():
    g = []
    # outer fillet and groove
    g.append(f'<rect x="0" y="0" width="{C}" height="3" fill="{WHITE}"/>')
    g.append(f'<line x1="0" y1="2.6" x2="{C}" y2="2.6" stroke="{DEEP}" stroke-width=".8"/>')
    # pearls
    g.append(bead_row(6.2, r=2.1, step=4))
    # acanthus band background (recessed at the top, lit toward the inside)
    g.append(f'<rect x="0" y="9" width="{C}" height="32" fill="url(#bandA)"/>')
    g.append(f'<line x1="0" y1="9.4" x2="{C}" y2="9.4" stroke="{DEEP}" stroke-width=".7"/>')
    # faint carved background texture: a row of small "water leaf" scallops behind the leaves
    for i in range(8):
        x0 = 8 * i
        g.append(f'<path d="M{x0} 40 A4 5 0 0 1 {x0+8} 40" fill="none" stroke="{SHADE}" stroke-width=".5"/>')
    # darts first (behind the leaves), then leaves
    for x in (0, 32, 64):
        g.append(dart(x, 11.5, 39))
    for cx in (16, 48):
        g.append(leaf(cx, 40, 0, 0.96))
    # fillet
    g.append(fillet(41, 3))
    # egg and dart
    g.append(egg_and_dart(44, 54))
    g.append(f'<line x1="0" y1="44.3" x2="{C}" y2="44.3" stroke="{DEEP}" stroke-width=".6"/>')
    # gold fillet
    g.append(gold_fillet(54, 2.2))
    # inner bevelled lip (sight edge)
    g.append(f'<rect x="0" y="56.2" width="{C}" height="7.8" fill="url(#lip)"/>')
    g.append(f'<line x1="0" y1="56.6" x2="{C}" y2="56.6" stroke="{WHITE}" stroke-width=".8"/>')
    g.append(f'<line x1="0" y1="63.4" x2="{C}" y2="63.4" stroke="#8b8372" stroke-width="1.2"/>')
    return "".join(g)


def rotated(content, deg):
    return f'<g transform="translate({C/2} {C/2}) rotate({deg}) translate({-C/2} {-C/2})">{content}</g>'


def rosette(cx, cy, r):
    g = [f'<g transform="translate({cx} {cy})">']
    # shadow
    g.append(f'<circle cx="1" cy="1.2" r="{r*.98}" fill="#6f6756" fill-opacity=".35"/>')
    # outer ring of 12 petals, each with a shaded underside and a lit top
    for n in range(12):
        a = n * 30
        g.append(f'<g transform="rotate({a})">'
                 f'<path d="M0 -{r*.28} C{r*.3} -{r*.45} {r*.36} -{r*.85} 0 -{r} C-{r*.36} -{r*.85} -{r*.3} -{r*.45} 0 -{r*.28} Z" '
                 f'fill="url(#petal)" stroke="{LINE}" stroke-width=".7" stroke-linejoin="round"/>'
                 f'<path d="M0 -{r*.33} C{r*.12} -{r*.5} {r*.12} -{r*.8} 0 -{r*.93}" fill="none" stroke="{DEEP}" stroke-width=".55" stroke-opacity=".8"/>'
                 f'<path d="M-0.6 -{r*.4} C-{r*.08} -{r*.55} -{r*.08} -{r*.75} -0.6 -{r*.85}" fill="none" stroke="#ffffff" stroke-width=".6"/>'
                 f'</g>')
    # middle ring of 8 rounded petals
    g.append(f'<circle cx="0" cy="0" r="{r*.5}" fill="#c8c1b1" stroke="{LINE}" stroke-width=".6"/>')
    for n in range(8):
        a = n * 45 + 22.5
        g.append(f'<g transform="rotate({a})">'
                 f'<ellipse cx="0" cy="-{r*.36}" rx="{r*.15}" ry="{r*.2}" fill="url(#petal)" stroke="{LINE}" stroke-width=".55"/>'
                 f'<ellipse cx="-0.4" cy="-{r*.4}" rx="{r*.05}" ry="{r*.1}" fill="#ffffff" fill-opacity=".9"/>'
                 f'</g>')
    # gold boss
    g.append(f'<circle cx=".6" cy=".8" r="{r*.22}" fill="#5a4a1c" fill-opacity=".5"/>')
    g.append(f'<circle cx="0" cy="0" r="{r*.22}" fill="url(#boss)" stroke="{GOLD_DK}" stroke-width=".7"/>')
    g.append(f'<circle cx="-{r*.07}" cy="-{r*.08}" r="{r*.07}" fill="#fff8e2"/>')
    g.append('</g>')
    return "".join(g)


def corner_cell():
    e = '<use href="#edge"/>'
    g = []
    g.append(f'<rect width="{C}" height="{C}" fill="{IVORY}"/>')
    # mitred bands: top edge clipped above the diagonal, left edge below it
    g.append(f'<g clip-path="url(#cpTop)">{e}</g>')
    g.append(f'<g clip-path="url(#cpLeft)">{rotated(e, -90)}</g>')
    # the mitre joint line
    g.append(f'<line x1="0" y1="0" x2="{C}" y2="{C}" stroke="#8b8372" stroke-width=".9" stroke-opacity=".8"/>')
    g.append(f'<line x1=".5" y1="-.5" x2="{C+.5}" y2="{C-.5}" stroke="#ffffff" stroke-width=".6" stroke-opacity=".8"/>')
    # corner block: a square plinth with a bevel, sitting over the acanthus band
    s0, s1 = 7.5, 42.5
    g.append(f'<rect x="{s0+1}" y="{s0+1.3}" width="{s1-s0}" height="{s1-s0}" rx="2.5" fill="#6f6756" fill-opacity=".35"/>')
    g.append(f'<rect x="{s0}" y="{s0}" width="{s1-s0}" height="{s1-s0}" rx="2.5" fill="url(#plinth)" stroke="{LINE}" stroke-width=".9"/>')
    g.append(f'<rect x="{s0+2.4}" y="{s0+2.4}" width="{s1-s0-4.8}" height="{s1-s0-4.8}" rx="1.5" fill="none" stroke="{WHITE}" stroke-width=".9"/>')
    g.append(f'<rect x="{s0+3.2}" y="{s0+3.2}" width="{s1-s0-6.4}" height="{s1-s0-6.4}" rx="1.2" fill="none" stroke="{SHADE}" stroke-width=".6"/>')
    # little gold studs in the plinth corners
    for (px, py) in ((s0+4.6, s0+4.6), (s1-4.6, s0+4.6), (s0+4.6, s1-4.6), (s1-4.6, s1-4.6)):
        g.append(f'<circle cx="{px}" cy="{py}" r="1.3" fill="url(#boss)" stroke="{GOLD_DK}" stroke-width=".4"/>')
    # small acanthus leaves tucked behind the rosette toward the inner corner
    cx = cy = (s0 + s1) / 2
    g.append(leaf(cx, cy, 135, 0.62))
    g.append(leaf(cx, cy, 90, 0.5))
    g.append(leaf(cx, cy, 180, 0.5))
    g.append(rosette(cx, cy, 14.2))
    return "".join(g)


def place(content, col, row, rot=0, flip=False):
    t = f"translate({col*C} {row*C})"
    if rot or flip:
        t += f" translate({C/2} {C/2})"
        if flip:
            t += " scale(-1 1)"
        if rot:
            t += f" rotate({rot})"
        t += f" translate({-C/2} {-C/2})"
    return f'<g transform="{t}">{content}</g>'


def main():
    e, c = '<use href="#edge"/>', corner_cell()
    defs = DEFS.replace("</defs>", f'<g id="edge">{edge_cell()}</g></defs>')
    parts = [defs, f'<rect width="{3*C}" height="{3*C}" fill="{IVORY}"/>',
             place(e, 1, 0), place(e, 1, 2, rot=180), place(e, 0, 1, rot=-90), place(e, 2, 1, rot=90),
             place(c, 0, 0), place(c, 2, 0, flip=True), place(c, 0, 2, rot=-90), place(c, 2, 2, rot=180)]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{3*C}" height="{3*C}" '
           f'viewBox="0 0 {3*C} {3*C}">' + "".join(parts) + "</svg>")
    open("frame.svg", "w").write(svg)
    uri = "data:image/svg+xml," + urllib.parse.quote(svg, safe="/:=' ()-.,")

    css = f'''  /* detailed white picture frame, acanthus leaf molding (SVG border-image, generated by make_frame.py) */
  :root {{ --frame:72px; }}
  @media (max-width:900px) {{ :root {{ --frame:56px; }} }}
  @media (max-width:600px) {{ :root {{ --frame:40px; }} }}
  body {{ padding:var(--frame); }}
  #frame {{ position:fixed; inset:0; z-index:900; pointer-events:none; border:var(--frame) solid #f6f4ef;
    border-image-source:url("{uri}"); border-image-slice:{C}; border-image-width:var(--frame); border-image-repeat:round;
    filter:drop-shadow(0 0 10px rgba(74,32,64,.45)) drop-shadow(0 2px 2px rgba(74,32,64,.25)); }}
  body.locked #frame {{ display:none; }}'''
    s = open("index.html").read()
    a = s.index("  /* detailed white picture-frame border")if "  /* detailed white picture-frame border" in s else s.index("  /* detailed white picture frame")
    end_marker = "  body.locked #frame { display:none; }"
    b = s.index(end_marker) + len(end_marker)
    s = s[:a] + css + s[b:]
    open("index.html", "w").write(s)
    print("frame.svg and index.html updated (%d bytes of SVG)" % len(svg))


if __name__ == "__main__":
    main()
