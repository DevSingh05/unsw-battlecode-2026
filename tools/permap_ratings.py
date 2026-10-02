"""Print each recent submission's server rating per map (from /api/v1/submissions byMap), weakest first.
usage: python3 tools/permap_ratings.py [N submissions, default 3]"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import api
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
subs = api.get("/api/v1/submissions")[:n]
maps = sorted({m for s in subs for m in (s.get("byMap") or {})})
print(f"{'map':18s}" + "".join(f"{s['name']:>14s}" for s in subs))
rows = []
for m in maps:
    vals = [(s.get("byMap") or {}).get(m) for s in subs]
    rows.append((vals[0]["rating"] if vals[0] else 9999, m, vals))
for _, m, vals in sorted(rows):
    print(f"{m:18s}" + "".join(f"{(str(v['rating'])+' '+str(v['wins'])+'-'+str(v['losses'])) if v else '-':>14s}" for v in vals))
print(f"{'OVERALL':18s}" + "".join(f"{str(s.get('rating')):>14s}" for s in subs))
