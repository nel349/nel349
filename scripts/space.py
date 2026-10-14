"""Shared look for the arcade images: palette, a scrolling starfield and the pixel starship.

Every image uses the same background and star speeds, so stacked edge to edge
they read as one screen. BG matches GitHub's dark theme, which hides the seams there.
"""
import random

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG, BORDER = "#0d1117", "#30363d"
TEXT, GRAY = "#e6edf3", "#8b949e"
PURPLE, VIOLET, GREEN, CYAN, MAGENTA, AMBER = "#a371f7", "#7c5cff", "#3fb950", "#39d0d8", "#ff4fd8", "#f0b429"

# (count per 10,000 px², width, height, speed in px/s, opacity): far dots to near streaks.
STAR_LAYERS = [(0.9, 1, 1, 6, 0.45), (0.45, 2, 2, 14, 0.7), (0.12, 1, 7, 46, 0.55)]

SHIP = [".....#.....", ".....#.....", "....###....", "....###....", ".#..###..#.", ".#.#####.#.", "###########", "##.##.##.##"]


def svg(w, h, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{MONO}"><style>{style}</style>{body}</svg>\n')


def starfield(w, h, seed):
    """Background plus three star layers falling at fixed speeds; returns (markup, css)."""
    rng = random.Random(seed)
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    css = []
    for i, (density, sw, sh, speed, alpha) in enumerate(STAR_LAYERS):
        count = max(1, round(w * h / 10000 * density))
        stars = []
        for _ in range(count):
            x, y = rng.randint(0, w - sw), rng.randint(0, h)
            # Each star is drawn twice, one screen apart, so the loop has no jump.
            stars.append(f'<rect x="{x}" y="{y}" width="{sw}" height="{sh}" fill="#fff"/>'
                         f'<rect x="{x}" y="{y - h}" width="{sw}" height="{sh}" fill="#fff"/>')
        body.append(f'<g class="sf{i}" opacity="{alpha}">{"".join(stars)}</g>')
        css.append(f".sf{i}{{animation:sf{i} {h / speed:.2f}s linear infinite}}"
                   f"@keyframes sf{i}{{from{{transform:translateY(0)}}to{{transform:translateY({h}px)}}}}")
    return "".join(body), "".join(css)


def scanlines(w, h):
    return ('<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect width="4" height="1" fill="#ffffff" opacity="0.025"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#scan)"/>')


def starship(x, y, travel, scale=4):
    """The pixel ship, patrolling `travel` px to the right of x and firing upward; returns (markup, css)."""
    hull = "".join(f'<rect x="{cx * scale}" y="{cy * scale}" width="{scale}" height="{scale}" fill="{CYAN}"/>'
                   for cy, row in enumerate(SHIP) for cx, ch in enumerate(row) if ch == "#")
    nose = len(SHIP[0]) * scale / 2
    tail = len(SHIP) * scale
    body = (f'<g class="ship" transform="translate({x} {y})"><g class="patrol">'
            f'<rect class="laser" x="{nose - 1}" y="-26" width="2" height="16" fill="{MAGENTA}"/>'
            f'{hull}'
            f'<rect class="flame" x="{nose - scale}" y="{tail}" width="{scale * 2}" height="{scale}" fill="{AMBER}"/>'
            f'</g></g>')
    css = (f".patrol{{animation:patrol 7s ease-in-out infinite alternate}}"
           f"@keyframes patrol{{from{{transform:translateX(0)}}to{{transform:translateX({travel}px)}}}}"
           ".laser{animation:laser 1.4s linear infinite}"
           f"@keyframes laser{{0%{{transform:translateY(0);opacity:1}}60%{{transform:translateY(-{y}px);opacity:1}}61%,100%{{opacity:0}}}}"
           ".flame{animation:flame .18s steps(2) infinite}@keyframes flame{50%{opacity:.35}}")
    return body, css
