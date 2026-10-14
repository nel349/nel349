"""Draws assets/c-proof-eater.svg: a snake that eats the profile's contribution graph.

Reads the calendar from GitHub's GraphQL API with the token in GITHUB_TOKEN.
Uses only the standard library, so the workflow needs no install step.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
LOGIN = os.environ.get("PROFILE_LOGIN", "nel349")
OUT = Path(__file__).resolve().parent.parent / "assets" / "c-proof-eater.svg"

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionLevel } }
      }
    }
  }
}"""

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
PANEL, BORDER, GRAY, GREEN, AMBER = "#0d1117", "#30363d", "#8b949e", "#3fb950", "#f0b429"
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
SHADES = ["#161b22", "#2d2257", "#4a35a0", "#7c5cff", "#c4b5ff"]

CELL, GAP, OX, OY, WIDTH = 12, 3, 32, 64, 860
STEP_SECONDS, PAUSE_SECONDS, TAIL = 0.045, 2.5, 4


def fetch_calendar(token):
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request(GRAPHQL_ENDPOINT, data=body, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def scanlines(w, h):
    return ('<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect width="4" height="1" fill="#ffffff" opacity="0.025"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" rx="12" fill="url(#scan)"/>')


def draw(calendar):
    weeks, total = calendar["weeks"], calendar["totalContributions"]
    pitch = CELL + GAP
    h = OY + 7 * pitch + 40
    # Serpentine path: down the even weeks, up the odd ones.
    order = []
    for wi, wk in enumerate(weeks):
        days = list(range(len(wk["contributionDays"])))
        order += [(wi, di) for di in (days if wi % 2 == 0 else reversed(days))]
    period = len(order) * STEP_SECONDS + PAUSE_SECONDS
    css, cells, frames = [f".h{{animation:mv {period:.2f}s linear infinite}}"], [], []
    for idx, (wi, di) in enumerate(order):
        level = LEVELS[weeks[wi]["contributionDays"][di]["contributionLevel"]]
        x, y = OX + wi * pitch, OY + di * pitch
        at = idx * STEP_SECONDS / period * 100
        frames.append(f"{at:.3f}%{{transform:translate({x}px,{y}px)}}")
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{SHADES[0]}"/>')
        if level:
            # Each lit cell stays until the head reaches it, then regrows at the end of the loop.
            css.append(f".e{idx}{{animation:k{idx} {period:.2f}s linear infinite}}"
                       f"@keyframes k{idx}{{0%,{at:.2f}%{{opacity:1}}{at + 0.2:.2f}%,97%{{opacity:0}}100%{{opacity:1}}}}")
            cells.append(f'<rect class="e{idx}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{SHADES[level]}"/>')
    last_x, last_y = OX + order[-1][0] * pitch, OY + order[-1][1] * pitch
    frames.append(f"100%{{transform:translate({last_x}px,{last_y}px)}}")
    css.append("@keyframes mv{" + "".join(frames) + "}")
    snake = "".join(f'<rect class="h" style="animation-delay:-{period - k * STEP_SECONDS:.3f}s" width="{CELL}" '
                    f'height="{CELL}" rx="3" fill="{GREEN}" opacity="{1 - k * 0.22:.2f}"/>' for k in range(TAIL))
    body = (f'<rect width="{WIDTH}" height="{h}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<text x="32" y="36" font-size="16" font-weight="700" fill="{GREEN}">PROOF-EATER</text>'
            f'<text x="170" y="36" font-size="13" fill="{GRAY}">eats commits, leaves proofs</text>'
            f'<text x="{WIDTH - 32}" y="36" text-anchor="end" font-size="12" fill="{GRAY}">HIGH SCORE '
            f'<tspan font-size="16" font-weight="700" fill="{AMBER}">{total:,}</tspan></text>'
            + "".join(cells) + snake + scanlines(WIDTH, h))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" viewBox="0 0 {WIDTH} {h}" '
            f'font-family="{MONO}"><style>{"".join(css)}</style>{body}</svg>\n')


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    calendar = fetch_calendar(token)
    OUT.write_text(draw(calendar), encoding="utf-8")
    print(f"wrote {OUT.name}: {calendar['totalContributions']} contributions, {len(calendar['weeks'])} weeks")


if __name__ == "__main__":
    main()
