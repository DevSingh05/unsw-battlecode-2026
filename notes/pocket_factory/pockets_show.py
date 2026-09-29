"""Print leaf-pruned pockets of a map: components, depth from mouth, gaps; and starter dragons' head/tail pocket status.
usage (from project root): python3 notes/pocket_factory/pockets_show.py maps/autarky.map"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'notes/autarky_calc/jam')); sys.path.insert(0, str(ROOT / 'notes/tools/autarky'))
sys.path.insert(0, str(ROOT / 'notes/tools/midgame')); sys.path.insert(0, str(ROOT / 'notes/tools'))
import simj
from collect import pockets
m = simj.Map(open(sys.argv[1]).read()); PK = pockets(m)
# depth from outside
dep = {}; fr = [t for t in PK if any((v := m.step(t, d)) is not None and v not in PK for d in 'NESW')]
for t in fr: dep[t] = 1
q = list(fr)
while q:
    u = q.pop(0)
    for d in 'NESW':
        v = m.step(u, d)
        if v in PK and v not in dep: dep[v] = dep[u] + 1; q.append(v)
seen = set()
for t in sorted(PK, key=lambda t: (t[1], t[0])):
    if t in seen: continue
    comp = []; st = [t]; seen.add(t)
    while st:
        u = st.pop(); comp.append(u)
        for d in 'NESW':
            v = m.step(u, d)
            if v in PK and v not in seen: seen.add(v); st.append(v)
    print(len(comp), 'tiles:', ' '.join(f'{x},{y}:d{dep.get((x,y))}g{m.tiles.get((x,y),(0,0))}' for x, y in sorted(comp, key=lambda p: dep.get(p, 0))))
for team, pts in m.dragons:
    print('starter', team, len(pts), 'head', pts[0], 'inPK', pts[0] in PK, 'tail', pts[-1], 'inPK', pts[-1] in PK)
