#!/usr/bin/env python3
"""Per-phase economy (eats by source, deaths by cause, splits) for us/them, grouped by layout x result.
    python3 notes/forensics/schooltime/phases.py [minElo]"""
import os, pickle, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = pickle.load(open(os.path.join(HERE, 'games.pkl'), 'rb'))
minelo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
def lay(D): return 'A' if D['poolspawns'] > 20 else 'B'
def yard(t): x, y = t; return 22 <= x <= 37 and y >= 24
def cause(d, T):
    r = d['reason']
    if r == 'HitHeadToHead':
        kt = d.get('killer_team') or d.get('victim_team')
        return 'h2h_' + ('ally' if kt == T else 'enemy')
    if r == 'HitOtherBody':
        h = d.get('hit')
        if h: return 'body_' + ('ally' if h['team'] == T else 'enemy')
        return 'body_?' if d['actor'] == d['id'] else 'rammed?'
    return r
PH = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 500)]
grp = collections.defaultdict(list)
for gid, D in G.items():
    if D['oppElo'] < minelo: continue
    grp[(lay(D), 'W' if D['win'] else 'L')].append(D)
for key in sorted(grp):
    Ds = grp[key]; n = len(Ds)
    print('=== layout %s %s  n=%d' % (key[0], key[1], n))
    for side in ('us', 'them'):
        print(' --', side)
        for a, b in PH:
            sp = cp_own = cp_en = yd = 0; dc = collections.Counter(); dl = collections.Counter(); spl = 0; spl2 = 0
            for D in Ds:
                T = D[side]
                for e in D['eats']:
                    if e['team'] != T or not (a <= e['round'] < b): continue
                    if e['corpse'] is None: sp += 1
                    elif e['corpse'][1] == T: cp_own += 1
                    else: cp_en += 1
                    if yard(e['tile']): yd += 1
                for d in D['deaths']:
                    if d['team'] != T or not (a <= d['round'] < b): continue
                    c = cause(d, T); dc[c] += 1; dl[c] += d['len']
                for s in D['splits']:
                    if s['team'] == T and a <= s['round'] < b:
                        spl += 1; spl2 += s['k'] == 2
            tot = sum(dc.values())
            print('  r%3d-%3d eats spawn %5.1f corpseOwn %5.1f corpseEn %5.1f yard %5.1f | splits %5.1f | deaths %5.1f len %5.1f : %s' % (
                a, b, sp / n, cp_own / n, cp_en / n, yd / n, spl / n, tot / n, sum(dl.values()) / n,
                ' '.join('%s %.1f/%.0f' % (k, dc[k] / n, dl[k] / n) for k, _ in dc.most_common(6))))
