"""Classify sprint moves (steps>=2): kill (killed an enemy), ally-kill, ate, escape (nearest enemy head <=3 before and farther after),
died, other. Also steps and length distributions, and ram initiations split by steps and by rammer length.
Usage: sprints.py GROUPS [maps]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
grps = sys.argv[1].split(','); maps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
G = [x for x in collect.games() if x['grp'] in grps and (not maps or x['map'] in maps)]
M = lambda v: st.mean(v) if v else float('nan')
C = collections.Counter(); steps = collections.Counter(); lens = collections.Counter(); n = 0
ramC = collections.Counter()
bp = collections.defaultdict(list)
for it in G: bp[it['path']].append(it)
for p, its in bp.items():
    g = sim2.simulate(p)
    for it in its:
        n += 1; T = it['T']
        for a in g['moves']:
            if a['team'] != T or a.get('suicide'): continue
            en_kill = [k for k in a['killed'] if k[1] != T]
            if a['steps'] >= 2:
                ne = a['near_enemy_head']
                if en_kill: c = 'kill'
                elif a['died']: c = 'died:' + a['died']
                elif a['killed']: c = 'allykill'
                elif ne and ne[0] <= 4 and a.get('enemy_after') is not None and a['enemy_after'] > ne[0]: c = 'escape'
                elif a['ate']: c = 'ate'
                else: c = 'other'
                C[c] += 1; steps[min(a['steps'], 6)] += 1; lens[min(a['len_before'], 10)] += 1
            if en_kill:
                ramC[('steps>=2' if a['steps'] >= 2 else 'step1', 'L<=3' if a['len_before'] <= 3 else ('L4-7' if a['len_before'] < 8 else 'L8+'))] += 1
                ramC['killedlen_sum'] += sum(k[2] for k in en_kill); ramC['kills'] += len(en_kill)
print('team-games', n)
print('sprints/game by class', {k: round(v / n, 2) for k, v in C.most_common()})
print('steps', sorted(steps.items()), 'len', sorted(lens.items()))
print('kills by mover', {k: round(v / n, 2) for k, v in ramC.items()})
