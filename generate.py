#!/usr/bin/env python3
"""Generate the Glass Panel Plasma theme's SVGs.

Everything not generated here falls back to the default Breeze theme. Each
graphic is built from 9-slice rounded frames tinted with the active colour
scheme (ColorScheme-* classes), so the theme follows light/dark schemes.

  * Surfaces (panel, popups, tooltips, widget backgrounds): a dark glass tint
    over KWin's blur, with a thin outline.
  * Controls inside them (text fields, list highlights, taskbar buttons, popup
    headers, frames, tabs, menu bar items): derived from Breeze's own graphics.
    Breeze's frame names and padding hints are copied verbatim, so sizes and
    alignment match Breeze exactly; only the drawing is replaced.

Re-run after editing the values below, then re-apply the theme:
  plasma-apply-desktoptheme default && plasma-apply-desktoptheme zhelly0-glass
"""
import gzip
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BREEZE = "/usr/share/plasma/desktoptheme/default"
MIDDLE = 16          # stretchable middle of each source frame

# ---- the glass recipe ------------------------------------------------------
# KWin 6 has no background-contrast effect any more, so the tint alone has to
# keep light text readable when a bright window is behind the glass.
TINT = 0.50          # colour-scheme background, 0..1
OUTLINE = 0.12       # text colour, 0..1
SURFACE_RADIUS = 12  # panel, popups, tooltips, widget backgrounds
CONTROL_RADIUS = 6   # fields, highlights, buttons inside surfaces


def style(fill=None, line=None, r=CONTROL_RADIUS, sides="tblr"):
    """fill/line: (colour class, opacity) or None. sides: which edges get the line."""
    return {"fill": fill, "line": line, "r": r, "sides": sides}


# Surfaces
GLASS = style(("Background", TINT), ("Text", OUTLINE), SURFACE_RADIUS)
GLASS_SOLID = style(("Background", 0.85), ("Text", OUTLINE), SURFACE_RADIUS)
GLASS_DENSE = style(("Background", 0.94), ("Text", OUTLINE), SURFACE_RADIUS)
# Controls
EMPTY = style(("Text", 0.0))
FIELD = style(("Text", 0.07), ("Text", 0.16))
RING_HOVER = style(None, ("Highlight", 0.6))
RING_FOCUS = style(None, ("Highlight", 1.0))
HOVER = style(("Text", 0.12), ("Text", 0.18))
ACCENT_HOVER = style(("Highlight", 0.18), ("Highlight", 0.45))
ACCENT = style(("Highlight", 0.30), ("Highlight", 0.70))
ACCENT_STRONG = style(("Highlight", 0.38), ("Highlight", 0.85))
ATTENTION = style(("NeutralText", 0.30), ("NeutralText", 0.70))
PROGRESS = style(("PositiveText", 0.30))
TASK_NORMAL = style(("Text", 0.05))
TASK_MINIMIZED = style(("Text", 0.02))
HEADER = style(None, ("Text", 0.12), r=0, sides="b")
FOOTER = style(None, ("Text", 0.12), r=0, sides="t")
FRAME_PLAIN = style(None, ("Text", 0.10))
FRAME_RAISED = style(("Text", 0.10), ("Text", 0.16))
# Buttons: a light glass pill; hover/focus are accent rings drawn over it
BUTTON = style(("Text", 0.10), ("Text", 0.18))
# Thin tracks (slider grooves, scrollbars) use Breeze's 3 px corners
TRACK = style(("Text", 0.16), r=3)
TRACK_FILL = style(("Highlight", 0.90), r=3)
SCROLL_TRACK = style(("Text", 0.05), r=3)
SCROLL_THUMB = style(("Text", 0.35), r=3)
SCROLL_THUMB_HOVER = style(("Highlight", 0.75), r=3)

# Surfaces with explicit padding. (path, style, padding, with blur mask)
SURFACES = [
    # Panel. "solid" is used while a window is maximized (adaptive opacity).
    ("widgets/panel-background",             GLASS,       4, True),
    ("translucent/widgets/panel-background", GLASS,       4, True),
    ("solid/widgets/panel-background",       GLASS_SOLID, 4, True),
    # Popups and hover tooltips. The plain variants are fallbacks without
    # compositing/blur, so they stay dense for readability.
    ("dialogs/background",                   GLASS_DENSE, 6, True),
    ("translucent/dialogs/background",       GLASS,       6, True),
    ("widgets/tooltip",                      GLASS_DENSE, 6, True),
    ("translucent/widgets/tooltip",          GLASS,       6, True),
]

# Controls derived from Breeze: {path: {frame prefix: style}}. Every frame
# prefix Breeze has must be listed, because a replaced file is used on its own
# (missing frames are not taken from Breeze).
TASK_STATES = {"normal": TASK_NORMAL, "minimized": TASK_MINIMIZED, "hover": HOVER,
               "focus": ACCENT, "attention": ATTENTION, "progress": PROGRESS}
DERIVED = {
    "widgets/lineedit": {"base": FIELD, "hover": RING_HOVER, "focus": RING_FOCUS, "focusframe": RING_FOCUS},
    "widgets/viewitem": {"normal": EMPTY, "hover": ACCENT_HOVER, "selected": ACCENT, "selected+hover": ACCENT_STRONG},
    "widgets/tasks": {f"{edge}{state}": s for edge in ("", "north-", "east-", "west-") for state, s in TASK_STATES.items()},
    "widgets/plasmoidheading": {"header": HEADER, "footer": FOOTER},
    "widgets/frame": {"sunken": FIELD, "plain": FRAME_PLAIN, "raised": FRAME_RAISED},
    "widgets/tabbar": {f"{edge}-active-tab": ACCENT_HOVER for edge in ("north", "south", "east", "west")},
    "widgets/menubaritem": {"normal": EMPTY, "hover": HOVER, "pressed": ACCENT},
    "widgets/background": {"": GLASS, "toolbutton-pressed": ACCENT},
    "widgets/button": {"normal": BUTTON, "hover": RING_HOVER, "focus": RING_FOCUS, "pressed": ACCENT,
                       "toolbutton-hover": HOVER, "toolbutton-pressed": ACCENT, "toolbutton-focus": RING_FOCUS},
    "widgets/scrollbar": {"background-horizontal": SCROLL_TRACK, "background-vertical": SCROLL_TRACK,
                          "slider": SCROLL_THUMB, "mouseover-slider": SCROLL_THUMB_HOVER},
    "widgets/slider": {"groove": TRACK, "groove-highlight": TRACK_FILL},
    "widgets/translucentbackground": {"": GLASS},
}

COLOURS = (".ColorScheme-Text { color:#fcfcfc; } .ColorScheme-Background { color:#202326; } "
           ".ColorScheme-Highlight { color:#3daee9; } .ColorScheme-NeutralText { color:#f67400; } "
           ".ColorScheme-PositiveText { color:#27ae60; } .ColorScheme-Shadow { color:#000000; }")


def paint(spec):
    if spec is None:
        return None
    cls, op = spec
    return f'class="ColorScheme-{cls}" fill="currentColor" fill-opacity="{op}"'


# Non-frame elements, drawn at exactly Breeze's sizes (Plasma sizes the
# slider handle from these): {path: {element id: (size, svg body at 0,0)}}.
def circle(size, d, fill=None, line=None, width=1.0):
    """A circle of diameter d centred in a size x size box."""
    c, r = size / 2, d / 2
    body = f'<rect fill="none" x="0" y="0" width="{size}" height="{size}"/>'
    if fill:
        body += f'<circle {paint(fill)} cx="{c}" cy="{c}" r="{r}"/>'
    if line:
        cls, op = line
        body += (f'<circle class="ColorScheme-{cls}" fill="none" stroke="currentColor" stroke-opacity="{op}" '
                 f'stroke-width="{width}" cx="{c}" cy="{c}" r="{r - width / 2}"/>')
    return body


HANDLE = {
    "slider-handle": circle(20, 18, fill=("Text", 0.92), line=("Background", 0.35)),
    "slider-hover":  circle(20, 20, line=("Highlight", 1.0), width=1.5),
    "slider-focus":  circle(24, 24, line=("Highlight", 0.8), width=2),
    "slider-shadow": circle(26, 22, fill=("Shadow", 0.30)),
}
EXTRA = {
    "widgets/slider": {f"{o}-{k}": v for o in ("horizontal", "vertical") for k, v in HANDLE.items()},
}

def frame(prefix, st, mask=False):
    """One 9-slice frame. Corner outlines are filled 1 px rings rather than
    strokes: a stroke pokes half a pixel outside the corner piece, which makes
    it render slightly scaled and leaves visible seams."""
    R = st["r"]
    C = max(R, 2)                     # corner piece size
    M = MIDDLE
    a, b = C + M, 2 * C + M
    if mask:
        f, ln = 'fill="#000000"', None
    else:
        f, ln = paint(st["fill"]), paint(st["line"])
    sides = st["sides"]
    rounded = R > 0 and sides == "tblr"
    r1 = R - 1

    def shape(d):
        return f'<path {f} d="{d}"/>' if f else ""

    def rect(attrs, x, y, w, h):
        return f'<rect {attrs} x="{x}" y="{y}" width="{w}" height="{h}"/>' if attrs else ""

    def line(side, x, y, w, h):
        return rect(ln, x, y, w, h) if ln and side in sides else ""

    def ring(d):
        return f'<path {ln} d="{d}"/>' if ln else ""

    if rounded:
        corners = {
            "topleft":     shape(f"M{R},0 A{R},{R} 0 0 0 0,{R} L{R},{R} Z")
                           + ring(f"M{R},0 A{R},{R} 0 0 0 0,{R} L1,{R} A{r1},{r1} 0 0 1 {R},1 Z"),
            "topright":    shape(f"M{a},0 A{R},{R} 0 0 1 {b},{R} L{a},{R} Z")
                           + ring(f"M{a},0 A{R},{R} 0 0 1 {b},{R} L{b-1},{R} A{r1},{r1} 0 0 0 {a},1 Z"),
            "bottomleft":  shape(f"M0,{a} A{R},{R} 0 0 0 {R},{b} L{R},{a} Z")
                           + ring(f"M0,{a} A{R},{R} 0 0 0 {R},{b} L{R},{b-1} A{r1},{r1} 0 0 1 1,{a} Z"),
            "bottomright": shape(f"M{b},{a} A{R},{R} 0 0 1 {a},{b} L{a},{a} Z")
                           + ring(f"M{b},{a} A{R},{R} 0 0 1 {a},{b} L{a},{b-1} A{r1},{r1} 0 0 0 {b-1},{a} Z"),
        }
    else:
        corners = {
            "topleft":     rect(f, 0, 0, C, C) + line("t", 0, 0, C, 1) + line("l", 0, 0, 1, C),
            "topright":    rect(f, a, 0, C, C) + line("t", a, 0, C, 1) + line("r", b - 1, 0, 1, C),
            "bottomleft":  rect(f, 0, a, C, C) + line("b", 0, b - 1, C, 1) + line("l", 0, a, 1, C),
            "bottomright": rect(f, a, a, C, C) + line("b", a, b - 1, C, 1) + line("r", b - 1, a, 1, C),
        }
    # An invisible rect pins every piece to its exact box, so a piece that is
    # fully transparent (or empty) still has the right size.
    box = lambda x, y, w, h: f'<rect fill="none" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    parts = {
        **corners,
        "top":    rect(f, C, 0, M, C) + line("t", C, 0, M, 1),
        "bottom": rect(f, C, a, M, C) + line("b", C, b - 1, M, 1),
        "left":   rect(f, 0, C, C, M) + line("l", 0, C, 1, M),
        "right":  rect(f, a, C, C, M) + line("r", b - 1, C, 1, M),
        "center": rect(f, C, C, M, M),
    }
    boxes = {"topleft": (0, 0, C, C), "topright": (a, 0, C, C), "bottomleft": (0, a, C, C),
             "bottomright": (a, a, C, C), "top": (C, 0, M, C), "bottom": (C, a, M, C),
             "left": (0, C, C, M), "right": (a, C, C, M), "center": (C, C, M, M)}
    sep = "-" if prefix and not prefix.endswith("-") else ""
    return "\n".join(f'<g id="{prefix}{sep}{k}">{box(*boxes[k])}{v}</g>' for k, v in parts.items())


def document(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">\n'
            f'<style type="text/css" id="current-color-scheme">{COLOURS}</style>\n{body}\n</svg>\n')


def surface_svg(st, pad, with_mask):
    hints = "".join(f'<rect id="hint-{side}-margin" width="{pad}" height="{pad}" fill="none"/>'
                    for side in ("top", "bottom", "left", "right"))
    body = frame("", st) + ("\n" + frame("mask-", st, mask=True) if with_mask else "") + "\n" + hints
    return document(body)


def breeze_hints(path):
    """Copy every hint element (padding/inset/behaviour) from Breeze's file."""
    src = gzip.open(os.path.join(BREEZE, path + ".svgz")).read().decode()
    hints = []
    for m in re.finditer(r'<(?:rect|path)\b[^>]*>', src):
        tag = m.group(0)
        hid = re.search(r'\bid="([^"]*hint[^"]*)"', tag)
        if not hid:
            continue
        w = re.search(r'\bwidth="([^"]+)"', tag)
        h = re.search(r'\bheight="([^"]+)"', tag)
        hints.append(f'<rect id="{hid.group(1)}" width="{w.group(1) if w else 1}" '
                     f'height="{h.group(1) if h else 1}" fill="none"/>')
    return hints


def breeze_frames(path):
    src = gzip.open(os.path.join(BREEZE, path + ".svgz")).read().decode()
    ids = set(re.findall(r'\bid="([^"]+)"', src))
    return {i[:-len("center")].rstrip("-") for i in ids
            if i.endswith("center") and "hint" not in i and "shadow" not in i and not i.startswith("mask")}


def write(path, text):
    out = os.path.join(HERE, path + ".svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(text)
    print("wrote", path)


for path, st, pad, with_mask in SURFACES:
    write(path, surface_svg(st, pad, with_mask))

for path, styles in DERIVED.items():
    missing = breeze_frames(path) - set(styles)
    if missing:
        raise SystemExit(f"{path}: Breeze has frames not covered here: {sorted(missing)}")
    body = "\n".join(frame(prefix, st) for prefix, st in styles.items())
    # Extra elements are placed side by side below the frames so they don't overlap.
    extras = "".join(f'<g id="{eid}" transform="translate({60 + 40 * i},60)">{svgbody}</g>'
                     for i, (eid, svgbody) in enumerate(EXTRA.get(path, {}).items()))
    write(path, document(body + "\n" + extras + "\n" + "\n".join(breeze_hints(path))))
