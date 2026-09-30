"""Ram anatomy. For each enemy-vs-enemy head-on (mover = rammer), from the perspective of group T:
rams received: rammer steps, rammer len, victim len, did the victim's own previous move bring it into the rammer's reach
(Manhattan dist before its move > rammer steps-reach, after <= reach), and local head counts; rams initiated: same.
Also: 'net corpse' = pearls from ram corpses eaten by T minus by E within 15 rounds. Usage: rams.py GROUPS [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
grps = sys.argv[1].split(','); maps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
M = lambda v: st.mean(v) if v else float('nan')
C = collections.Counter(); ng = 0; L = collections.defaultdict(list)
bp = collections.defaultdict(list)
for x in collect.games():
    if x['grp'] in grps and (not maps or x['map'] in maps): bp[x['path']].append(x)
for p, its in bp.items():
    g = sim2.simulate(p); m = g['map']
    lastmove = {}
    mv_by = collections.defaultdict(list)
    for a in g['moves']: mv_by[a['id']].append(a)
    ate = collections.defaultdict(collections.Counter)
    for e in g['eats']:
        if e['corpse'] is not None: ate[e['corpse'][0]][e['team']] += 1
    for it in its:
        ng += 1; T = it['T']; E = 'B' if T == 'A' else 'A'
        for d in g['deaths']:
            if d['reason'] != 'HitHeadToHead' or d['id'] != d['actor'] or d.get('victim') is None: continue
            if d.get('victim_team') == d['team']: continue
            side = 'init' if d['team'] == T else 'recv'
            st_ = d.get('steps') or 1
            C[(side, 'steps%d' % min(st_, 3))] += 1; C[(side, 'n')] += 1
            L[(side, 'rammerL')].append(d['len']); L[(side, 'victimL')].append(d['victim_len'])
            # victim previous move
            v = d['victim']; pm = [a for a in mv_by[v] if a['round'] < d['round'] or (a['round'] == d['round'])]
            pm = [a for a in pm if a.get('head_after')]
            if pm:
                a = pm[-1]
                rh = d['body'][0] if d.get('body') else d['head']
                # rammer head before its move is d['head'] (death happened before moving)
                reach = min(d['len'] - 1, 3)
                before = m.dist(a['head'], rh); after = m.dist(a['head_after'], rh)
                if after <= reach and before > reach: C[(side, 'victim_stepped_in')] += 1
                elif after <= reach: C[(side, 'victim_already_in')] += 1
            # corpse race for the victim's pearls and the rammer's
            vt = d['victim_team']
            C[(side, 'victim_pearls_T')] += ate[v][T]; C[(side, 'victim_pearls_E')] += ate[v][E]
            C[(side, 'rammer_pearls_T')] += ate[d['id']][T]; C[(side, 'rammer_pearls_E')] += ate[d['id']][E]
print('team-games', ng)
for k in sorted(C): print(f'{C[k]/ng:7.2f}', k)
for k in sorted(L): print(k, round(M(L[k]), 2))
