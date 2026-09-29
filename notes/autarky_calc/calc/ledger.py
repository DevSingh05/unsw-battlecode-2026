from common import *
import collections
PH = [(0, 100), (100, 200), (200, 300), (300, 500)]
for gm in GAMES:
    if gm['us'] is None and gm['gid'] not in (607083, 608782): continue
    g = sim(gm['gid']); c = gm['calc']
    print(gm['gid'], gm['opp'])
    for T, lab in ((c, 'calc'), ('B' if c == 'A' else 'A', 'opp ')):
        s = '  %s' % lab
        for a, b in PH:
            E_ = [e for e in g['eats'] if e['team'] == T and a <= e['round'] < b]
            pk = sum(1 for e in E_ if pocket_of(e['tile']) is not None)
            cor = sum(1 for e in E_ if e['corpse'] and pocket_of(e['tile']) is None)
            op = len(E_) - pk - cor
            D = [d for d in g['deaths'] if d['team'] == T and a <= d['round'] < b]
            dc = collections.Counter()
            for d in D:
                k = 'H2H' if d['reason'] == 'HitHeadToHead' else ('pocket' if pocket_of(d['head']) is not None else d['reason'][:6])
                dc[k] += d['len']
            spl = sum(1 for x in g['splits'] if x['team'] == T and a <= x['round'] < b)
            s += ' | r%d-%d eat pk%3d open%3d corpse%3d, died %s, splits %d' % (a, b, pk, op, cor, dict(dc), spl)
        print(s)
