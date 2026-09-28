#!/usr/bin/env python3
"""Render .map files into one HTML page (kelp, portals, pearl tiles, starting dragons).

usage: maps_html.py OUT.html map1.map map2.map ...
"""
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from genmaps import parse  # noqa: E402

PAIR_COLOURS = ["#d2a8ff", "#ffa657", "#79c0ff", "#ff7b72", "#7ee787", "#f2cc60"]


def svg_for(path):
    m = parse(pathlib.Path(path))
    w, h, nxt = m["w"], m["h"], m["nxt"]
    cell = max(6, min(18, 640 // max(w, h)))
    out = [f'<svg viewBox="0 0 {w * cell} {h * cell}" width="{w * cell}" height="{h * cell}" role="img">',
           f'<rect width="{w * cell}" height="{h * cell}" fill="var(--floor)"/>']
    for t in range(w * h):
        mx = m["gmax"][t]
        if mx <= 0:
            continue
        mean = (m["gmin"][t] + mx) / 2
        fill = "var(--hot)" if mx == 1 else "var(--fast)" if mean <= 20 else "var(--spawn)"
        out.append(f'<rect x="{t % w * cell}" y="{t // w * cell}" width="{cell}" height="{cell}" fill="{fill}"/>')
    # portal id per edge, straight from the map file (both ends of a pair share an id)
    edge_pid = {}
    for line in pathlib.Path(path).read_text().splitlines():
        f = line.split()
        if len(f) == 4 and f[0] == "EDGE" and f[2] == "2":
            idx, pid = int(f[1]), int(f[3])
            col, row = idx % (w + 1), idx // (w + 1)
            if col < w and row < 2 * h:
                edge_pid[("H", col, row // 2) if row % 2 == 0 else ("V", col, (row - 1) // 2)] = pid
    portal_ids = {}
    for t in range(w * h):
        x, y = t % w, t // w
        for d, (dx, dy) in ((0, (0, -1)), (3, (-1, 0))):
            v = nxt[t * 4 + d]
            plain = ((y + dy) % h) * w + (x + dx) % w
            if v == plain:
                continue
            if v == -1:
                colour, width = "var(--kelp)", max(2, cell // 5)
            else:
                key = edge_pid.get(("H", x, y) if d == 0 else ("V", x, y), -1)
                colour = PAIR_COLOURS[portal_ids.setdefault(key, len(portal_ids)) % len(PAIR_COLOURS)]
                width = max(3, cell // 3)
            if d == 0:
                out.append(f'<line x1="{x * cell}" y1="{y * cell}" x2="{(x + 1) * cell}" y2="{y * cell}" stroke="{colour}" stroke-width="{width}"/>')
            else:
                out.append(f'<line x1="{x * cell}" y1="{y * cell}" x2="{x * cell}" y2="{(y + 1) * cell}" stroke="{colour}" stroke-width="{width}"/>')
    for team, pts in m["dragons"]:
        col = "var(--a)" if team == 0 else "var(--b)"
        for i, (x, y) in enumerate(pts):
            pad = 1 if i == 0 else cell // 4
            out.append(f'<rect x="{x * cell + pad}" y="{y * cell + pad}" width="{cell - 2 * pad}" height="{cell - 2 * pad}" fill="{col}" rx="2"/>')
    out.append("</svg>")
    sym = {"x": "mirror top/bottom", "y": "mirror left/right", "xy": "180° rotation", "none": "no pearl sharing"}.get(m["sym"], m["sym"])
    starts = f'{sum(1 for t, _ in m["dragons"] if t == 0)} dragons per team'
    hot = sum(1 for t in range(w * h) if m["gmax"][t] == 1)
    meta = f'{w}×{h} · {sym} · {starts} · {len(portal_ids)} portal pairs · {hot} hot tiles'
    return f'<figure><figcaption><b>{html.escape(pathlib.Path(path).stem)}</b><span>{meta}</span></figcaption>{"".join(out)}</figure>'


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unseen Test Maps</title><style>
:root{--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--mute:#8b949e;--rule:#30363d;--floor:#131820;--spawn:#1c2633;--fast:#2b4a6f;--hot:#e3b341;--kelp:#3fb950;--a:#f0883e;--b:#58a6ff}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--bg:#f6f8fa;--panel:#fff;--ink:#1f2328;--mute:#59636e;--rule:#d0d7de;--floor:#eef1f4;--spawn:#dce6f2;--fast:#9ec5ee;--hot:#d4a72c;--kelp:#1a7f37;--a:#bc4c00;--b:#0969da}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1200px;margin:0 auto;padding:20px 16px 40px}h1{font-size:22px;margin:0 0 4px}p.sub{color:var(--mute);margin:0 0 14px}
.legend{display:flex;flex-wrap:wrap;gap:14px;color:var(--mute);font-size:13px;margin-bottom:16px}.legend span{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:6px;vertical-align:-2px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}
figure{margin:0;background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:10px;overflow:hidden}
figcaption{display:flex;flex-direction:column;gap:2px;margin-bottom:8px}figcaption span{color:var(--mute);font-size:12.5px}
svg{max-width:100%;height:auto;display:block;border-radius:4px}
</style></head><body><main><h1>Unseen test maps</h1>
<p class="sub">__N__ of the 80 generated maps we use to rehearse the Sprint, where every map is new. The bot has never seen any of them.</p>
<div class="legend"><div><span style="background:var(--a)"></span>Team A start (head = full square)</div><div><span style="background:var(--b)"></span>Team B start</div>
<div><span style="background:var(--kelp)"></span>Kelp wall</div><div><span style="background:#d2a8ff"></span>Portal pair (same colour = linked)</div>
<div><span style="background:var(--hot)"></span>Pearl every round</div><div><span style="background:var(--fast)"></span>Fast pearls (≤20 rounds)</div><div><span style="background:var(--spawn)"></span>Slow pearls</div></div>
<div class="grid">__FIGS__</div></main></body></html>"""


def main():
    out = pathlib.Path(sys.argv[1])
    figs = "".join(svg_for(p) for p in sys.argv[2:])
    out.write_text(PAGE.replace("__N__", str(len(sys.argv) - 2)).replace("__FIGS__", figs))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
