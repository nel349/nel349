"""Draws the arcade images: the title screen, the world banners and the level tiles.

These change only when the projects do, so the workflow does not run this; run it by hand.
"""
import math
from html import escape
from pathlib import Path

from space import AMBER, BG, CYAN, GRAY, GREEN, MAGENTA, PURPLE, TEXT, scanlines, starfield, starship, svg

ASSETS = Path(__file__).resolve().parent.parent / "assets"
WIDTH = 860

WORLDS = [
    dict(key="midnight", label="WORLD 1 · MIDNIGHT", color=CYAN, levels=[
        dict(key="kuira", name="KUIRA SDK", level="1-1", color=CYAN, short=["ZK dApps on mobile.", "Proofs on the phone."]),
        dict(key="cli", name="MIDNIGHT CLI", level="1-2", color=GREEN, short=["Wallet + localnet", "from your terminal."]),
    ]),
    dict(key="agents", label="WORLD 2 · AGENTS WITH MONEY", color=MAGENTA, levels=[
        dict(key="mandate", name="MANDATE", level="2-1", color=PURPLE, short=["Agents spend only", "what you allowed."]),
        dict(key="bench", name="BENCH", level="2-2", color=AMBER, short=["A gym for agents.", "Score includes $."]),
        dict(key="pod", name="POD", level="2-3", color=MAGENTA, short=["Paid only if the", "work re-runs."]),
    ]),
]

ICONS = {
    "kuira": [".######.", "#......#", "#.####.#", "#.#..#.#", "#.####.#", "#.#..#.#", "#.####.#", "#......#", "#..##..#", ".######."],
    "cli": ["##########", "#........#", "#.#......#", "#..#.....#", "#...#....#", "#..#.....#", "#.#..###.#", "#........#", "##########"],
    "bench": ["..........", "##......##", "##......##", "##########", "##########", "##......##", "##......##", ".........."],
    "pod": ["..######..", ".#......#.", "#........#", "#.......##", "#......#.#", "#.#...#..#", "#..#.#...#", "#...#....#", ".#......#.", "..######.."],
}

BLINK = ".bl{animation:bl 1.1s steps(1) infinite}@keyframes bl{50%{opacity:0}}"


def write(name, content):
    (ASSETS / name).write_text(content, encoding="utf-8")


def title_screen():
    h = 300
    stars, star_css = starfield(WIDTH, h, seed=1)
    ship, ship_css = starship(150, 236, travel=520)
    body = (stars +
            f'<text x="{WIDTH / 2}" y="84" text-anchor="middle" font-size="44" font-weight="800" fill="{MAGENTA}" opacity="0.6" transform="translate(3 3)">NEL349</text>'
            f'<text x="{WIDTH / 2}" y="84" text-anchor="middle" font-size="44" font-weight="800" fill="{CYAN}" class="gl">NEL349</text>'
            f'<text x="{WIDTH / 2}" y="118" text-anchor="middle" font-size="14" fill="{AMBER}" letter-spacing="4">SELECT A LEVEL</text>'
            f'<text x="{WIDTH / 2}" y="152" text-anchor="middle" font-size="12" fill="{GRAY}">PLAYER 1 · <tspan fill="{TEXT}">DevX @ MIDNIGHT FOUNDATION</tspan></text>'
            f'<text x="{WIDTH / 2}" y="190" text-anchor="middle" font-size="13" fill="{GREEN}" class="bl" letter-spacing="3">▶ PRESS ANY PROJECT TO START</text>'
            + ship + scanlines(WIDTH, h))
    css = (star_css + ship_css + BLINK +
           ".gl{animation:gl 4s steps(1) infinite}@keyframes gl{0%,92%,100%{transform:none}94%{transform:translate(-3px,1px)}96%{transform:translate(2px,-1px)}}")
    write("c-arcade.svg", svg(WIDTH, h, body, css))


def world_banner(world, seed):
    h, c = 56, world["color"]
    stars, star_css = starfield(WIDTH, h, seed)
    body = (stars +
            f'<line x1="0" y1="28" x2="{WIDTH}" y2="28" stroke="{c}" stroke-dasharray="2 6" opacity="0.6"/>'
            f'<rect x="{WIDTH / 2 - 190}" y="12" width="380" height="32" fill="{BG}" stroke="{c}"/>'
            f'<text x="{WIDTH / 2}" y="33" text-anchor="middle" font-size="14" font-weight="700" fill="{c}" letter-spacing="3">{escape(world["label"])}</text>')
    write(f"c-world-{world['key']}.svg", svg(WIDTH, h, body, star_css))


def ring_icon(color, n=10, lit=0.7):
    cells, c = [], (n - 1) / 2
    for y in range(n):
        for x in range(n):
            if 3.4 <= math.hypot(x - c, y - c) <= 4.7:
                ang = (math.degrees(math.atan2(x - c, -(y - c))) + 360) % 360
                cells.append((x, y, color if ang <= 360 * lit else "#2a2440"))
    return cells, n, n


def bitmap_icon(rows, color):
    cells = [(x, y, color) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "#"]
    return cells, len(rows[0]), len(rows)


def level_tile(lv, width, seed):
    """One level card centred in a slice of starfield `width` wide, so a row of slices fills the screen."""
    h, tw, th, s = 260, 200, 230, 6
    stars, star_css = starfield(width, h, seed)
    cells, gw, gh = ring_icon(lv["color"]) if lv["key"] == "mandate" else bitmap_icon(ICONS[lv["key"]], lv["color"])
    pix = "".join(f'<rect x="{x * s}" y="{y * s}" width="{s}" height="{s}" fill="{c}"/>' for x, y, c in cells)
    fx, fy = (width - tw) / 2, (h - th) / 2
    cx = width / 2
    ix, iy = cx - gw * s / 2, fy + 44 + (66 - gh * s) / 2
    body = (stars +
            f'<rect x="{fx + 2}" y="{fy + 2}" width="{tw - 4}" height="{th - 4}" fill="{BG}" fill-opacity="0.82" stroke="{lv["color"]}" stroke-width="3"/>'
            f'<rect x="{fx + 8}" y="{fy + 8}" width="{tw - 16}" height="{th - 16}" fill="none" stroke="{lv["color"]}" stroke-width="1" opacity="0.35"/>'
            f'<text x="{cx}" y="{fy + 32}" text-anchor="middle" font-size="11" fill="{GRAY}" letter-spacing="2">LEVEL {lv["level"]}</text>'
            f'<g transform="translate({ix} {iy})"><g class="bob">{pix}</g></g>'
            f'<text x="{cx}" y="{fy + 148}" text-anchor="middle" font-size="16" font-weight="800" fill="{TEXT}">{escape(lv["name"])}</text>'
            + "".join(f'<text x="{cx}" y="{fy + 172 + j * 16}" text-anchor="middle" font-size="11" fill="{GRAY}">{escape(t)}</text>'
                      for j, t in enumerate(lv["short"]))
            + f'<text x="{cx}" y="{fy + th - 16}" text-anchor="middle" font-size="12" fill="{lv["color"]}" class="bl" letter-spacing="2">▶ PLAY</text>')
    css = star_css + BLINK + ".bob{animation:bob 1.6s steps(2) infinite}@keyframes bob{50%{transform:translateY(-4px)}}"
    write(f"c-tile-{lv['key']}.svg", svg(width, h, body, css))


def main():
    title_screen()
    seed = 10
    for world in WORLDS:
        world_banner(world, seed)
        width = WIDTH // len(world["levels"])
        for lv in world["levels"]:
            seed += 1
            level_tile(lv, width, seed)
        seed += 1
    print("wrote", ", ".join(sorted(p.name for p in ASSETS.glob("c-*.svg") if p.name != "c-proof-eater.svg")))


if __name__ == "__main__":
    main()
