#!/usr/bin/env python3
"""Generate the Glass Panel Plasma theme's SVGs.

Only the panel, popup (dialogs/background) and tooltip graphics are replaced;
everything else falls back to the default Breeze theme. Each graphic is a
9-slice rounded frame tinted with the active colour scheme:

  * panel:   a light tint of the text colour, like the SysDash/DeskClock tiles
  * popups / tooltips: the background colour, translucent, so text stays
    readable over windows while KWin blurs what's behind

Re-run after editing the values below, then re-apply the theme:
  plasma-apply-desktoptheme default && plasma-apply-desktoptheme zhelly0-glass
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RADIUS = 12      # corner radius, matches the widgets' 12 px tiles
MIDDLE = 16      # stretchable middle of the source image
HINT = 4         # content padding, same as Breeze

# ---- the glass recipe ------------------------------------------------------
# One look for the panel, popups (start menu, KRunner, calendar, tray) and
# tooltips: a dark tint over KWin's blur. KWin 6 has no background-contrast
# effect any more, so the tint alone has to keep light text readable when a
# bright window is behind the glass.
TINT = 0.50          # colour-scheme background, 0..1
OUTLINE = 0.12       # text colour, 0..1

# (path, colour class, fill opacity, outline opacity, padding)
GRAPHICS = [
    # Panel. "solid" is used while a window is maximized (adaptive opacity).
    ("widgets/panel-background",             "Background", TINT, OUTLINE, HINT),
    ("translucent/widgets/panel-background", "Background", TINT, OUTLINE, HINT),
    ("solid/widgets/panel-background",       "Background", 0.85, OUTLINE, HINT),
    # Popups and hover tooltips. The plain variants are fallbacks without
    # compositing/blur, so they stay dense for readability.
    ("dialogs/background",                   "Background", 0.94, OUTLINE, 6),
    ("translucent/dialogs/background",       "Background", TINT, OUTLINE, 6),
    ("widgets/tooltip",                      "Background", 0.94, OUTLINE, 6),
    ("translucent/widgets/tooltip",          "Background", TINT, OUTLINE, 6),
]


def frame(prefix, cls, fill_op, stroke_op, mask=False):
    R, M = RADIUS, MIDDLE
    W = 2 * R + M
    a, b = R + M, W
    if mask:
        f = 'fill="#000000"'
    else:
        f = f'class="ColorScheme-{cls}" fill="currentColor" fill-opacity="{fill_op}"'
    # Corner outlines are filled 1 px rings, not strokes: a stroke would poke
    # half a pixel outside the corner piece, making it render slightly scaled
    # and leaving visible seams at the piece boundaries.
    r1 = R - 1
    ring = (f'class="ColorScheme-Text" fill="currentColor" fill-opacity="{stroke_op}"')
    arc = lambda d: "" if mask else f'<path {ring} d="{d}"/>'
    line = lambda x, y, w, hh: "" if mask else (
        f'<rect class="ColorScheme-Text" fill="currentColor" fill-opacity="{stroke_op}" '
        f'x="{x}" y="{y}" width="{w}" height="{hh}"/>')
    parts = {
        "topleft":     f'<path {f} d="M{R},0 A{R},{R} 0 0 0 0,{R} L{R},{R} Z"/>'
                       + arc(f"M{R},0 A{R},{R} 0 0 0 0,{R} L1,{R} A{r1},{r1} 0 0 1 {R},1 Z"),
        "topright":    f'<path {f} d="M{a},0 A{R},{R} 0 0 1 {b},{R} L{a},{R} Z"/>'
                       + arc(f"M{a},0 A{R},{R} 0 0 1 {b},{R} L{b-1},{R} A{r1},{r1} 0 0 0 {a},1 Z"),
        "bottomleft":  f'<path {f} d="M0,{a} A{R},{R} 0 0 0 {R},{b} L{R},{a} Z"/>'
                       + arc(f"M0,{a} A{R},{R} 0 0 0 {R},{b} L{R},{b-1} A{r1},{r1} 0 0 1 1,{a} Z"),
        "bottomright": f'<path {f} d="M{b},{a} A{R},{R} 0 0 1 {a},{b} L{a},{a} Z"/>'
                       + arc(f"M{b},{a} A{R},{R} 0 0 1 {a},{b} L{a},{b-1} A{r1},{r1} 0 0 0 {b-1},{a} Z"),
        "top":    f'<rect {f} x="{R}" y="0" width="{M}" height="{R}"/>' + line(R, 0, M, 1),
        "bottom": f'<rect {f} x="{R}" y="{a}" width="{M}" height="{R}"/>' + line(R, b - 1, M, 1),
        "left":   f'<rect {f} x="0" y="{R}" width="{R}" height="{M}"/>' + line(0, R, 1, M),
        "right":  f'<rect {f} x="{a}" y="{R}" width="{R}" height="{M}"/>' + line(b - 1, R, 1, M),
        "center": f'<rect {f} x="{R}" y="{R}" width="{M}" height="{M}"/>',
    }
    return "\n".join(f'<g id="{prefix}{k}">{v}</g>' for k, v in parts.items())


def svg(cls, fill_op, stroke_op, hint):
    W = 2 * RADIUS + MIDDLE
    hints = "".join(
        f'<rect id="hint-{side}-margin" x="{x}" y="{y}" width="{hint}" height="{hint}" fill="none"/>'
        for side, x, y in (("top", RADIUS, 0), ("bottom", RADIUS, W - hint),
                           ("left", 0, RADIUS), ("right", W - hint, RADIUS)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">
<style type="text/css" id="current-color-scheme">.ColorScheme-Text {{ color:#fcfcfc; }} .ColorScheme-Background {{ color:#202326; }}</style>
{frame("", cls, fill_op, stroke_op)}
{frame("mask-", cls, 0, 0, mask=True)}
{hints}
</svg>
'''


for path, cls, fill_op, stroke_op, hint in GRAPHICS:
    out = os.path.join(HERE, path + ".svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(svg(cls, fill_op, stroke_op, hint))
    print("wrote", os.path.relpath(out, HERE))

