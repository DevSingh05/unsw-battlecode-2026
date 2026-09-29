from common import *
import collections, sys
RAD = 4
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']; o = 'B' if c == 'A' else 'A'
    homes = {}
    for t, pts in g['map'].dragons:
        if len(pts) >= 10: homes['AB'[t]] = [p for p in range(4) if abs(MOUTH[p][0] - pts[0][0]) <= 1]
    print(gm['gid'], gm['opp'][:10], ' heads within %d of a mouth (outside pocket), per mouth avg; calc@calcHome calc@oppHome | opp@oppHome opp@calcHome | units calc/opp' % RAD)
    s = ''
    for w0 in range(0, 500, 50):
        acc = collections.Counter(); n = 0
        for r, S in g['rounds']:
            if not (w0 <= r < w0 + 50): continue
            n += 1
            for j, (h, L, T) in S['heads'].items():
                if pocket_of(h) is not None: continue
                for p in range(4):
                    if mdist(h, MOUTH[p]) <= RAD:
                        acc[(T == c, p in homes[T])] += 1
            acc['uc'] += sum(1 for v in S['heads'].values() if v[2] == c); acc['uo'] += sum(1 for v in S['heads'].values() if v[2] == o)
        if n: s += '  r%d: %.1f %.1f | %.1f %.1f | %d/%d\n' % (w0, acc[(True, True)] / n / 2, acc[(True, False)] / n / 2, acc[(False, True)] / n / 2, acc[(False, False)] / n / 2, acc['uc'] / n, acc['uo'] / n)
    print(s, end='')
