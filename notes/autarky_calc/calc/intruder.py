"""Intruder analysis: an enemy head comes within 2 of a mouth of a pocket owned (last dove) by team T. What happens within 6 rounds?"""
from common import *
import pickle, collections
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
out = collections.defaultdict(collections.Counter)
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
    owner = {}
    X = sorted([e for e in E if e['gid'] == gm['gid']], key=lambda e: e['r0'])
    dmap = {d['id']: d for d in g['deaths']}
    xi = 0; seen = {}
    for r, S in g['rounds']:
        while xi < len(X) and X[xi]['r0'] <= r:
            owner[X[xi]['p']] = X[xi]['team']; xi += 1
        for p, T in owner.items():
            for j, (h, L, t) in S['heads'].items():
                if t == T or mdist(h, MOUTH[p]) > 2 or pocket_of(h) is not None: continue
                if seen.get((j, p), -99) >= r - 10: seen[(j, p)] = r; continue
                seen[(j, p)] = r
                grpO = 'calc-owned, intruder=' + ('US' if gm['us'] else 'oth') if T == c else ('US-owned, intruder=calc' if gm['us'] else 'oth-owned, intruder=calc')
                ownersNear = sum(1 for k, (hh, LL, tt) in S['heads'].items() if tt == T and mdist(hh, MOUTH[p]) <= 4)
                d = dmap.get(j)
                res = 'intruder survives 6r'
                if d and d['round'] <= r + 6:
                    res = 'intruder dies: ' + d['reason'][:9] + ('(by owner)' if d.get('killer_team') == T else '')
                # did intruder dive?
                dv = [e for e in X if e['id'] == j and r < e['r0'] <= r + 6 and e['p'] == p]
                if dv: res = 'intruder dives in'
                out[grpO][res] += 1
                out[grpO + ' ownersNear>=2' if ownersNear >= 2 else grpO + ' ownersNear<2']['n'] += 1
for k, v in sorted(out.items()):
    print(k, dict(v.most_common()))
