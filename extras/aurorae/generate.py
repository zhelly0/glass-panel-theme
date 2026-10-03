#!/usr/bin/env python3
"""Generate the Glass Aurorae window decoration (title bars and buttons).

Aurorae themes use fixed colours (they don't follow the colour scheme), so the
values below are taken from Breeze Dark; adjust them for other schemes.

Writes the theme to ~/.local/share/aurorae/themes/zhelly0-glass (and a copy
next to this script). Activate with:
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__zhelly0-glass
  qdbus6 org.kde.KWin /KWin reconfigure
"""
import os
import shutil

NAME = "zhelly0-glass"
OUT = os.path.expanduser(f"~/.local/share/aurorae/themes/{NAME}")
COPY = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME)

# ---- colours (Breeze Dark) and the glass recipe -------------------------------
BG = "#202326"        # window background
FG = "#fcfcfc"        # text
ACCENT = "#3daee9"
CLOSE = "#e5484d"
TINT_ACTIVE = 0.50    # title bar glass, same as the Plasma theme
TINT_INACTIVE = 0.35
OUTLINE = 0.12
RADIUS = 10           # top corners of the title bar
M = 16                # stretchable middle of the frame

# ---- layout --------------------------------------------------------------------
TITLE_HEIGHT = 22
BUTTON = 22           # button box; the round button inside is smaller
DOT = 16


def frame(prefix, tint, outline, mask=False):
    """Decoration frame. The centre fills the title bar area (the window's
    content covers the rest); the 1 px outline sits on the outer edges."""
    R = RADIUS
    a, b = R + M, 2 * R + M
    if mask:
        f = 'fill="#000000"'
        ln = None
    else:
        f = f'fill="{BG}" fill-opacity="{tint}"'
        ln = f'fill="{FG}" fill-opacity="{outline}"'
    r1 = R - 1
    ring = (lambda d: f'<path {ln} d="{d}"/>') if ln else (lambda d: "")
    line = (lambda x, y, w, h: f'<rect {ln} x="{x}" y="{y}" width="{w}" height="{h}"/>') if ln else (lambda *a: "")
    box = lambda x, y, w, h: f'<rect fill="none" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    parts = {
        "topleft": (box(0, 0, R, R) + f'<path {f} d="M{R},0 A{R},{R} 0 0 0 0,{R} L{R},{R} Z"/>'
                    + ring(f"M{R},0 A{R},{R} 0 0 0 0,{R} L1,{R} A{r1},{r1} 0 0 1 {R},1 Z")),
        "topright": (box(a, 0, R, R) + f'<path {f} d="M{a},0 A{R},{R} 0 0 1 {b},{R} L{a},{R} Z"/>'
                     + ring(f"M{a},0 A{R},{R} 0 0 1 {b},{R} L{b-1},{R} A{r1},{r1} 0 0 0 {a},1 Z")),
        # Bottom corners stay square: the window content is square too.
        "bottomleft": box(0, a, R, R) + f'<rect {f} x="0" y="{a}" width="{R}" height="{R}"/>'
                      + line(0, b - 1, R, 1) + line(0, a, 1, R),
        "bottomright": box(a, a, R, R) + f'<rect {f} x="{a}" y="{a}" width="{R}" height="{R}"/>'
                       + line(a, b - 1, R, 1) + line(b - 1, a, 1, R),
        "top": box(R, 0, M, R) + f'<rect {f} x="{R}" y="0" width="{M}" height="{R}"/>' + line(R, 0, M, 1),
        "bottom": box(R, a, M, R) + f'<rect {f} x="{R}" y="{a}" width="{M}" height="{R}"/>' + line(R, b - 1, M, 1),
        "left": box(0, R, R, M) + f'<rect {f} x="0" y="{R}" width="{R}" height="{M}"/>' + line(0, R, 1, M),
        "right": box(a, R, R, M) + f'<rect {f} x="{a}" y="{R}" width="{R}" height="{M}"/>' + line(b - 1, R, 1, M),
        "center": box(R, R, M, M) + f'<rect {f} x="{R}" y="{R}" width="{M}" height="{M}"/>',
    }
    sep = "-" if prefix else ""
    return "\n".join(f'<g id="{prefix}{sep}{k}">{v}</g>' for k, v in parts.items())


def svg(body, size=100):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}">\n{body}\n</svg>\n')


def decoration():
    body = "\n".join([
        frame("decoration", TINT_ACTIVE, OUTLINE),
        frame("decoration-inactive", TINT_INACTIVE, OUTLINE * 0.6),
        # Aurorae's blur mask item uses no prefix: it looks for "mask-*" pieces
        # (plus an unprefixed frame) to tell KWin which area to blur.
        frame("", TINT_ACTIVE, OUTLINE),
        frame("mask", 0, 0, mask=True),
        # Content padding inside the frame (Aurorae mainly uses the rc layout).
        *(f'<rect id="hint-{s}-margin" width="1" height="1" fill="none"/>' for s in ("top", "bottom", "left", "right")),
    ])
    return svg(body)


# ---- buttons ---------------------------------------------------------------------
# Glyphs drawn in a 22x22 box, centred on (11,11), as strokes.
GLYPHS = {
    "close": "M7.5,7.5 L14.5,14.5 M14.5,7.5 L7.5,14.5",
    "maximize": "M7.5,7.5 H14.5 V14.5 H7.5 Z",
    "restore": "M7.5,9.5 H12.5 V14.5 H7.5 Z M9.5,9.5 V7.5 H14.5 V12.5 H12.5",
    "minimize": "M7.5,13.5 H14.5",
    "alldesktops": "M11,7 V15 M7,11 H15",
    "keepabove": "M7.5,13 L11,9 L14.5,13",
    "keepbelow": "M7.5,9 L11,13 L14.5,9",
    "shade": "M7.5,9 H14.5 M7.5,12.5 L11,9.5 L14.5,12.5",
    "help": "M8.8,9.2 A2.3,2.3 0 1 1 11.6,11.3 C11,11.6 11,12 11,12.8 M11,14.6 V14.7",
}

# state -> (circle colour, circle opacity, glyph opacity); the close button uses
# a red circle on hover/press.
STATES = {
    "active":                 (FG, 0.10, 0.90),
    "hover":                  (FG, 0.24, 1.00),
    "pressed":                (ACCENT, 0.55, 1.00),
    "inactive":               (FG, 0.06, 0.45),
    "hover-inactive":         (FG, 0.18, 0.85),
    "pressed-inactive":       (ACCENT, 0.45, 1.00),
    "deactivated":            (FG, 0.04, 0.25),
    "deactivated-inactive":   (FG, 0.03, 0.18),
}


def button(name):
    groups = []
    for state, (colour, cop, gop) in STATES.items():
        if name == "close" and state.startswith(("hover", "pressed")):
            colour, cop = CLOSE, 0.90 if state.startswith("hover") else 1.0
        c = BUTTON / 2
        art = (f'<rect fill="none" x="0" y="0" width="{BUTTON}" height="{BUTTON}"/>'
               f'<circle fill="{colour}" fill-opacity="{cop}" cx="{c}" cy="{c}" r="{DOT / 2}"/>'
               f'<path fill="none" stroke="{FG}" stroke-opacity="{gop}" stroke-width="1.4" '
               f'stroke-linecap="round" stroke-linejoin="round" d="{GLYPHS[name]}"/>')
        # Aurorae draws buttons as frames; only the centre is needed.
        groups.append(f'<g id="{state}-center">{art}</g>')
    return svg("\n".join(groups), size=BUTTON)


RC = f"""[General]
ActiveTextColor=252,252,252
InactiveTextColor=150,152,155
TitleAlignment=Center
TitleVerticalAlignment=Center
UseTextShadow=false
Shadow=false
Animation=150

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom=1
TitleEdgeTop=5
TitleEdgeBottom=5
TitleEdgeLeft=8
TitleEdgeRight=8
TitleEdgeTopMaximized=3
TitleEdgeBottomMaximized=3
TitleEdgeLeftMaximized=6
TitleEdgeRightMaximized=6
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={TITLE_HEIGHT}
ButtonWidth={BUTTON}
ButtonHeight={BUTTON}
ButtonSpacing=4
ButtonMarginTop=0
ExplicitButtonSpacer=10
PaddingTop=0
PaddingBottom=0
PaddingLeft=0
PaddingRight=0
"""

METADATA = f"""[Desktop Entry]
Name=Glass
Comment=Frosted-glass title bars matching the Glass Panel Plasma theme
X-KDE-PluginInfo-Author=zhelly0
X-KDE-PluginInfo-Name={NAME}
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=GPL-3.0
X-KDE-PluginInfo-EnabledByDefault=true
"""


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    files = {"decoration.svg": decoration(), f"{NAME}rc": RC, "metadata.desktop": METADATA}
    files.update({f"{b}.svg": button(b) for b in GLYPHS})
    for fname, text in files.items():
        with open(os.path.join(OUT, fname), "w") as fh:
            fh.write(text)
    shutil.rmtree(COPY, ignore_errors=True)
    shutil.copytree(OUT, COPY)
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
