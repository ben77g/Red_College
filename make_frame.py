#!/usr/bin/env python3
"""Generate the white picture-frame border (acanthus leaf molding).

Run from this folder:  python3 make_frame.py
It writes frame.svg and replaces the frame CSS block in index.html (between the
"/* detailed white picture frame" comment and the "body.locked #frame" line).
"""
import re
import urllib.parse

C = 64  # cell size in SVG units; the SVG is a 3x3 grid of cells
LINE = "#c9c3b6"
GOLD = "#d6bf80"

DEFS = '''<defs>
<linearGradient id="gA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#f4f1ea"/><stop offset="1" stop-color="#dcd7cb"/></linearGradient>
<linearGradient id="gB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ece8e0"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<linearGradient id="gC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#faf8f4"/><stop offset="1" stop-color="#cfc9bb"/></linearGradient>
<radialGradient id="pearl" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d3cdbf"/></radialGradient>
<radialGradient id="rose" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d9d3c5"/></radialGradient>
<linearGradient id="leaf" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#d9d3c5"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="#ece8df"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff2c4"/><stop offset="1" stop-color="#c9a74f"/></linearGradient>
</defs>'''


def leaf_path():
    """Acanthus leaf with base at (0,0) pointing up to (0,-31); three serrated lobes each side."""
    right = [
        ("M", 0, 0),
        ("C", 3, -1, 9, -1, 13, -5),    # lobe 1
        ("Q", 9, -7, 5, -7),
        ("C", 9, -9, 14, -12, 13, -16),  # lobe 2
        ("Q", 9, -17, 5, -16),
        ("C", 8, -19, 12, -22, 10, -26),  # lobe 3
        ("Q", 7, -26, 4, -24),
        ("C", 5, -27, 3, -30, 0, -31),    # tip
    ]
    d = ""
    for seg in right:
        cmd, *n = seg
        d += cmd + " ".join(f"{n[i]} {n[i+1]}" for i in range(0, len(n), 2)) + " "
    # mirror: walk back down the left side with negated x
    d2 = ""
    # build the mirrored path explicitly, from the tip back to the base
    d2 += "C -3 -30 -5 -27 -4 -24 "           # tip curl, left
    d2 += "Q -7 -26 -10 -26 "
    d2 += "C -12 -22 -8 -19 -5 -16 "
    d2 += "Q -9 -17 -13 -16 "
    d2 += "C -14 -12 -9 -9 -5 -7 "
    d2 += "Q -9 -7 -13 -5 "
    d2 += "C -9 -1 -3 -1 0 0 Z"
    # the right side ends at the tip (0,-31); the left side starts there
    return d + d2


def leaf(x, y, rot=0, scale=1):
    p = leaf_path()
    veins = (
        f'<path d="M0 -1 L0 -29" stroke="{LINE}" stroke-width=".9" fill="none"/>'
        f'<path d="M0 -4 L9 -5 M0 -10 L10 -14 M0 -18 L8 -23 M0 -4 L-9 -5 M0 -10 L-10 -14 M0 -18 L-8 -23" stroke="{LINE}" stroke-width=".6" fill="none"/>'
    )
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({scale})">'
            f'<path d="{p}" fill="url(#leaf)" stroke="{LINE}" stroke-width="1" stroke-linejoin="round"/>{veins}</g>')


def dart(x, y0, y1):
    mid = (y0 + y1) / 2
    return (f'<path d="M{x} {y0} Q{x+3.5} {mid} {x} {y1} Q{x-3.5} {mid} {x} {y0} Z" '
            f'fill="url(#gold)" stroke="#a88f4a" stroke-width=".7"/>')


def edge_cell():
    g = []
    g.append(f'<rect x="0" y="0" width="{C}" height="4" fill="#ffffff"/>')
    g.append(f'<rect x="0" y="4" width="{C}" height="4" fill="#efece5"/>')
    g.append(f'<rect x="0" y="8" width="{C}" height="30" fill="url(#gA)"/>')       # acanthus band
    g.append(f'<rect x="0" y="38" width="{C}" height="3" fill="#fbfaf7"/>')
    g.append(f'<rect x="0" y="41" width="{C}" height="11" fill="url(#gB)"/>')      # gadroon band
    g.append(f'<rect x="0" y="52" width="{C}" height="2" fill="{GOLD}"/>')
    g.append(f'<rect x="0" y="54" width="{C}" height="10" fill="url(#gC)"/>')      # inner lip
    for y in (4, 8, 38, 41, 52, 54):
        g.append(f'<line x1="0" y1="{y}" x2="{C}" y2="{y}" stroke="{LINE}" stroke-width=".8"/>')
    g.append(f'<line x1="0" y1="52.2" x2="{C}" y2="52.2" stroke="#fff6d8" stroke-width=".6"/>')
    # acanthus leaves (pointing outward, base on the inner side of the band) with darts between
    for cx in (16, 48):
        g.append(leaf(cx, 37, 0, 0.93))
    for x in (0, 32, 64):
        g.append(dart(x, 14, 34))
    # gadroon band under the leaves
    for i in range(4):
        x0 = 16 * i
        g.append(f'<path d="M{x0} 41 A8 11 0 0 0 {x0+16} 41 Z" fill="#ffffff" stroke="{LINE}" stroke-width=".8"/>')
        g.append(f'<path d="M{x0+3.5} 41 A4.5 7 0 0 0 {x0+12.5} 41 Z" fill="#ece8df"/>')
    return "".join(g)


def corner_cell():
    g = []
    g.append(f'<rect width="{C}" height="{C}" fill="url(#gA)"/>')
    g.append(f'<path d="M0 {C} L0 0 L{C} 0" fill="none" stroke="{LINE}" stroke-width="1.6"/>')
    g.append(f'<path d="M4 {C} L4 4 L{C} 4" fill="none" stroke="{LINE}" stroke-width=".8"/>')
    g.append(f'<path d="M{C} 52 L52 52 L52 {C}" fill="none" stroke="{GOLD}" stroke-width="2"/>')
    g.append(f'<line x1="0" y1="0" x2="{C}" y2="{C}" stroke="{LINE}" stroke-width=".8" stroke-dasharray="2 2"/>')
    cx = cy = 32
    # leaves radiating from the rosette: up, left and a larger diagonal one
    g.append(leaf(cx, cy, -45, 1.12))
    g.append(leaf(cx, cy, 0, 0.9))
    g.append(leaf(cx, cy, -90, 0.9))
    k = C / 56
    g.append(f'<g transform="translate({cx} {cy}) scale({k:.3f}) translate(-28 -28)">')
    for n in range(12):
        g.append(f'<ellipse cx="28" cy="15" rx="4.6" ry="8" fill="url(#rose)" stroke="{LINE}" stroke-width=".9" transform="rotate({n*30} 28 28)"/>')
    g.append(f'<circle cx="28" cy="28" r="11" fill="url(#rose)" stroke="{LINE}" stroke-width="1"/>')
    for n in range(8):
        g.append(f'<ellipse cx="28" cy="22" rx="2.4" ry="4.2" fill="#ffffff" stroke="{LINE}" stroke-width=".7" transform="rotate({n*45} 28 28)"/>')
    g.append(f'<circle cx="28" cy="28" r="4.2" fill="url(#gold)" stroke="#a88f4a" stroke-width=".8"/><circle cx="26.8" cy="26.8" r="1.4" fill="#fff6d8"/>')
    g.append('</g>')
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
    e, c = edge_cell(), corner_cell()
    parts = [DEFS, f'<rect width="{3*C}" height="{3*C}" fill="#f6f4ef"/>',
             place(e, 1, 0), place(e, 1, 2, rot=180), place(e, 0, 1, rot=-90), place(e, 2, 1, rot=90),
             place(c, 0, 0), place(c, 2, 0, flip=True), place(c, 0, 2, rot=-90), place(c, 2, 2, rot=180)]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{3*C}" height="{3*C}" '
           f'viewBox="0 0 {3*C} {3*C}">' + "".join(parts) + "</svg>")
    open("frame.svg", "w").write(svg)
    uri = "data:image/svg+xml," + urllib.parse.quote(svg, safe="/:=' ()-.,")

    css = f'''  /* detailed white picture frame, acanthus leaf molding (SVG border-image, generated by make_frame.py) */
  :root {{ --frame:64px; }}
  @media (max-width:600px) {{ :root {{ --frame:36px; }} }}
  body {{ padding:var(--frame); }}
  #frame {{ position:fixed; inset:0; z-index:900; pointer-events:none; border:var(--frame) solid #f6f4ef;
    border-image-source:url("{uri}"); border-image-slice:{C}; border-image-width:var(--frame); border-image-repeat:round;
    filter:drop-shadow(0 0 7px rgba(60,40,50,.45)); }}
  body.locked #frame {{ display:none; }}'''
    s = open("index.html").read()
    a = s.index("  /* detailed white picture-frame border")if "  /* detailed white picture-frame border" in s else s.index("  /* detailed white picture frame")
    end_marker = "  body.locked #frame { display:none; }"
    b = s.index(end_marker) + len(end_marker)
    s = s[:a] + css + s[b:]
    open("index.html", "w").write(s)
    print("frame.svg and index.html updated")


if __name__ == "__main__":
    main()
