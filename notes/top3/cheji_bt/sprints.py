"""Characterise sprints (multi-step moves): steps, len before, pearls eaten, net length, kills, enemy distance, pocket tiles."""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
sys.path.insert(0, H); import importlib.util as _u; _s = _u.spec_from_file_location("chan", os.path.join(H, "analyze.py")); _A = _u.module_from_spec(_s); _s.loader.exec_module(_A); deadend_tiles = _A.deadend_tiles
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
grp = sys.argv[1]
C = collections.Counter(); ng = 0; net = collections.Counter(); eatn = collections.Counter(); enemy = collections.Counter(); Lb = collections.Counter(); ex = []
purpose = collections.Counter()
for r in rows:
    if r['grp'] != grp: continue
    ng += 1
    g = sim2.simulate(r['path']); T = r['T']; m = g['map']
    dead, _ = deadend_tiles(m)
    for a in g['moves']:
        if a['team'] != T or a.get('suicide'): continue
        mv = a['act'].get('move', [])
        if len(mv) < 2: continue
        C[len(mv)] += 1
        dl = a['len_after'] - a['len_before'] if not a['died'] else None
        net[dl if dl is None else max(-3, min(dl, 2))] += 1
        eatn[min(a['ate'], 4)] += 1
        ne = a['near_enemy_head'][0] if a['near_enemy_head'] else 99
        enemy[min(ne, 8)] += 1
        Lb[min(a['len_before'], 10)] += 1
        p = 'kill' if a['killed'] else ('died' if a['died'] else ('eat' if a['ate'] else ('flee' if ne <= 3 else 'other')))
        purpose[p] += 1
        if p == 'other' and len(ex) < 8: ex.append((r['gid'], a['round'], a['id'], a['len_before'], ''.join(mv), 'enemy', ne, a['head'], a['head_after']))
print(grp, ng, 'games; sprints/game %.1f' % (sum(C.values()) / ng))
print(' steps', sorted(C.items()))
print(' purpose', {k: round(v / ng, 1) for k, v in purpose.items()})
print(' pearls eaten', sorted(eatn.items()), ' net length', sorted(net.items(), key=lambda x: (x[0] is None, x[0] if x[0] is not None else 0)))
print(' len before', sorted(Lb.items()), ' enemy head dist', sorted(enemy.items()))
for e in ex: print('  ', e)
