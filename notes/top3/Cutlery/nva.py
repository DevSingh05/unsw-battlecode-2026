"""What are Cutlery's NoValidAction deaths? (and our HitSelf deaths). Usage: nva.py GROUPS(default cut) N_GAMES"""
import sys, os, json, collections, pickle
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
grp = sys.argv[1] if len(sys.argv) > 1 else 'cut'; NG = int(sys.argv[2]) if len(sys.argv) > 2 else 10
G = [x for x in collect.games() if x['grp'] == grp][:NG]
C = collections.Counter(); ex = []
for it in G:
    g = sim2.simulate(it['path']); T = it['T']; m = g['map']; PK = collect.pockets(m)
    # map corpse drops -> who ate
    eaten = collections.Counter()
    for e in g['eats']:
        if e['corpse'] is not None: eaten[(e['corpse'][0])] += 1
    eat_by = collections.defaultdict(list)
    for e in g['eats']:
        if e['corpse'] is not None: eat_by[e['corpse'][0]].append((e['round'] - e['corpse'][2], e['team'], e['len']))
    for d in g['deaths']:
        if d['team'] != T or d['reason'] in ('HitHeadToHead',): continue
        mv = d.get('move', '')
        steps = d.get('steps', 0); sf = d.get('step_failed')
        inpk = d['head'] in PK
        free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
        kd = d.get('king', (None, 0, 99, 99))
        E = eat_by.get(d['id'], [])
        own = sum(1 for dt, tm, L in E if tm == T); en = sum(1 for dt, tm, L in E if tm != T)
        fast = sum(1 for dt, tm, L in E if tm == T and dt <= 5)
        key = (d['reason'], 'L' + str(min(d['len'], 6)), 'steps%d' % min(steps, 3), 'pk' if inpk else 'open', 'free%d' % free)
        C[key] += 1
        C[('ALL', d['reason'])] += 1
        C[('pearls', d['reason'], 'own')] += own; C[('pearls', d['reason'], 'en')] += en; C[('pearls', d['reason'], 'drop')] += (d['len'] + 1) // 2
        C[('pearls', d['reason'], 'own<=5r')] += fast
        C[('king<=3', d['reason'])] += kd[2] <= 3
        C[('bigking<=3', d['reason'])] += (kd[2] <= 3 and kd[1] >= 10)
        if len(ex) < 12 and d['reason'] == 'NoValidAction': ex.append((it['gid'], d['round'], d['len'], mv, steps, sf, d['nbrs'], inpk, kd[:3], E[:4]))
for k, v in sorted(C.items(), key=lambda kv: -kv[1])[:45]: print(v, k)
for e in ex: print(e)
