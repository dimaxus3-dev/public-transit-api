#!/usr/bin/env python3
"""Render an ingested city's transit network as a standalone SVG map.

    python3 scripts/render_map.py <feed_id> [out.svg] [--clip N]

Draws every route line from data/<feed_id>/lines.geojson in its real GTFS
color on a dark background, with interchange stops as dots. Pure stdlib —
the same artifacts the API serves, so the map is exactly what a client
would draw. Output defaults to docs/maps/<feed_id>.svg.
"""
from __future__ import annotations

import json
import math
import os
import sys

W = 1200                    # canvas width, px; height follows the geo aspect
PAD = 40
BG = "#0d1117"              # GitHub dark-mode canvas — maps blend into the README
MODE_FALLBACK = {           # per-mode color when the feed ships none
    "tram": "#e74c3c", "bus": "#4aa3df", "metro": "#f1c40f",
    "rail": "#9b59b6", "ferry": "#1abc9c", "trolleybus": "#e67e22",
}


def _mercator_y(lat: float) -> float:
    lat = max(-85.0, min(85.0, lat))
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def load(feed_id: str):
    base = os.path.join(os.path.dirname(__file__), "..", "data", feed_id)
    lines = json.load(open(os.path.join(base, "lines.geojson")))["features"]
    try:
        stops = json.load(open(os.path.join(base, "stops.json")))
    except FileNotFoundError:
        stops = []
    return lines, stops


def render(feed_id: str, out_path: str | None = None, clip_pct: int = 2) -> str:
    """clip_pct trims that percentage of outermost stops per side when framing
    (raise it for networks with a long lonely branch, e.g. NYC's SIR)."""
    lines, stops = load(feed_id)

    # Frame the map around the STOPS (where the network's mass is) — shape
    # polylines oversample long lonely branches and would drag the city into
    # a corner. p2/p98 drops lone far-out branches; lines outside just clip.
    if stops:
        xs = sorted(s["lon"] for s in stops if s.get("lon") is not None)
        ys = sorted(s["lat"] for s in stops if s.get("lat") is not None)
    else:
        pts = [(lon, lat) for f in lines for lon, lat in _coords(f)]
        if not pts:
            raise SystemExit(f"no geometry in data/{feed_id}/lines.geojson")
        xs = sorted(p[0] for p in pts)
        ys = sorted(p[1] for p in pts)
    k = max(1, len(xs) * clip_pct // 100)
    lo_x, hi_x = xs[k], xs[-1 - k]
    lo_y, hi_y = ys[k], ys[-1 - k]
    my_lo, my_hi = _mercator_y(lo_y), _mercator_y(hi_y)

    span_x = (hi_x - lo_x) or 1e-9
    span_y = (my_hi - my_lo) or 1e-9
    H = int((W - 2 * PAD) * span_y / span_x) + 2 * PAD
    H = max(400, min(1600, H))

    def xy(lon: float, lat: float) -> tuple[float, float]:
        x = PAD + (lon - lo_x) / span_x * (W - 2 * PAD)
        y = PAD + (my_hi - _mercator_y(lat)) / span_y * (H - 2 * PAD)
        return round(x, 1), round(y, 1)

    # draw longest lines first so short branches stay visible on top
    feats = sorted(lines, key=lambda f: -len(_coords(f)))
    paths = []
    for f in feats:
        p = f["properties"]
        color = (p.get("color") or "").strip() or MODE_FALLBACK.get(p.get("mode", ""), "#8b949e")
        if not color.startswith("#"):
            color = "#" + color
        coords = _coords(f)
        if len(coords) < 2:
            continue
        d = "M" + " L".join(f"{x},{y}" for x, y in (xy(lon, lat) for lon, lat in coords))
        mode = p.get("mode", "bus")
        width = {"metro": 3.2, "rail": 2.8, "tram": 2.4}.get(mode, 1.6)
        opacity = {"metro": 0.95, "rail": 0.9, "tram": 0.9}.get(mode, 0.65)
        paths.append(f'<path d="{d}" stroke="{color}" stroke-width="{width}" '
                     f'fill="none" stroke-opacity="{opacity}" stroke-linecap="round" '
                     f'stroke-linejoin="round"/>')

    # stops: draw only well-connected ones so big networks stay readable
    dots = []
    if stops:
        step = max(1, len(stops) // 700)
        for s in stops[::step]:
            lat, lon = s.get("lat"), s.get("lon")
            if lat is None or lon is None or not (lo_y <= lat <= hi_y and lo_x <= lon <= hi_x):
                continue
            x, y = xy(lon, lat)
            dots.append(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#e6edf3" fill-opacity="0.75"/>')

    n_routes = len({f["properties"].get("route_id") for f in lines})
    modes = sorted({f["properties"].get("mode", "bus") for f in lines})
    title = feed_id.replace("-", " ").title()
    label = f"{title} — {n_routes} routes · {len(stops)} stops · {', '.join(modes)}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>
{chr(10).join(paths)}
{chr(10).join(dots)}
<text x="{PAD}" y="{H - 16}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="15" fill="#8b949e">{label}</text>
<text x="{W - PAD}" y="{H - 16}" text-anchor="end" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="12" fill="#484f58">rendered from GTFS by scripts/render_map.py</text>
</svg>
"""
    out = out_path or os.path.join(os.path.dirname(__file__), "..", "docs", "maps", f"{feed_id}.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(svg)
    print(f"[{feed_id}] {len(paths)} lines, {len(dots)} stop dots -> {os.path.relpath(out)}")
    return out


def _coords(feature) -> list:
    g = feature.get("geometry") or {}
    if g.get("type") == "LineString":
        return g.get("coordinates") or []
    if g.get("type") == "MultiLineString":
        return [pt for part in (g.get("coordinates") or []) for pt in part]
    return []


if __name__ == "__main__":
    args = sys.argv[1:]
    clip = 2
    if "--clip" in args:
        i = args.index("--clip")
        clip = int(args[i + 1])
        del args[i:i + 2]
    if not args:
        raise SystemExit(__doc__)
    render(args[0], args[1] if len(args) > 1 else None, clip_pct=clip)
