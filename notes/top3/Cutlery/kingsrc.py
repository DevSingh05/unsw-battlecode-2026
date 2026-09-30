"""Where does the king's length come from, r300-500 (round-limit games)? Per group: king eats per game by source,
own-corpse eats split by dropper distance to king at death (<=3 'fed', else 'scavenged'), dropper death reason,
king sprints, king in-pocket share, and the lengths of units 2..5 at r300/r400/r500.
Usage: kingsrc.py GROUPS [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
grps = sys.argv[1].split(','); maps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
G = [x for x in collect.games() if x['grp'] in grps and (not maps or x['map'] in maps)]
M = lambda v: st.mean(v) if v else float('nan')
C = collections.Counter(); ng = 0; ranks = collections.defaultdict(list); dist_k = []
for it in G:
    g = sim2.simulate(it['path'])
    if g['result'].get('endReason') != 'roundLimit': continue
    ng += 1; T = it['T']; R = dict(g['rounds']); m = g['map']; PK = collect.pockets(m)
    dd = {d['id']: d for d in g['deaths']}
    for e in g['eats']:
        if e['team'] != T or e['round'] < 300: continue
        s = R.get(e['round'] - 1)
        if not s or s[T]['king'] != e['id']: continue
        ph = 'r300-399' if e['round'] < 400 else 'r400-500'
        c = e['corpse']
        if c is None: src = 'spawn-pocket' if e['tile'] in PK else 'spawn-open'
        elif c[1] != T: src = 'enemy-corpse'
        else:
            d = dd.get(c[0]); kd = d['king'][2] if d and d.get('king') and d['king'][0] == e['id'] else 99
            src = ('own-fed(<=3)' if kd <= 3 else 'own-scav') + ':' + (d['reason'] if d else '?')
        C[(ph, src)] += 1; C[(ph, 'ALL')] += 1
    for a in g['moves']:
        if a['team'] != T or a['round'] < 300: continue
        s = R.get(a['round'] - 1)
        if not s or s[T]['king'] != a['id']: continue
        ph = 'r300-399' if a['round'] < 400 else 'r400-500'
        C[(ph, 'kmoves')] += 1
        if a['steps'] >= 2: C[(ph, 'ksprint')] += 1; C[(ph, 'ksprint_ate')] += a['ate'] > 0
        if a['head'] in PK: C[(ph, 'k_in_pocket')] += 1
        # distance from king head to nearest pocket tile
    for r in (300, 400, 499):
        s = R.get(r)
        if s:
            ls = s[T]['lens'] + [0] * 6
            ranks[r].append(ls[:6])
for k in sorted(C): print(f'{C[k]/ng:7.2f}', k)
print('games', ng)
for r, v in ranks.items(): print('r', r, 'top6 lens', [round(M([x[i] for x in v]), 1) for i in range(6)])
