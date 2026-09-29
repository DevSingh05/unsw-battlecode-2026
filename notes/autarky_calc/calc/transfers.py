from common import *
import pickle, collections
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
    for p in range(4):
        X = sorted([e for e in E if e['gid'] == gm['gid'] and e['p'] == p], key=lambda e: e['r0'])
        for a, b in zip(X, X[1:]):
            if a['calc'] == b['calc']: continue
            endA = a.get('rdeath', a.get('rout', a['r1']))
            # deaths of prev owner's team within 5 of mouth in (endA-5, b.r0]
            prevT = a['team']
            dd = [d for d in g['deaths'] if endA - 8 <= d['round'] <= b['r0'] and mdist(d['head'], MOUTH[p]) <= 5 and pocket_of(d['head']) is None]
            desc = ' '.join('%s%d L%d %s%s' % ('C' if d['team'] == c else 'u', d['id'], d['len'], d['reason'][:7], (' by ' + ('C' if d.get('killer_team') == c else 'u')) if d.get('killer') is not None else '') for d in dd)
            S = R.get(b['r0'] - 1)
            nprev = sum(1 for j, (h, L, T) in S['heads'].items() if T == prevT and mdist(h, MOUTH[p]) <= 4) if S else -1
            nnew = sum(1 for j, (h, L, T) in S['heads'].items() if T == b['team'] and mdist(h, MOUTH[p]) <= 4) if S else -1
            print('%d p%d %s->%s  prev dive r%d ends r%d, new dive r%d (idle %d)  heads<=4 at takeover prev=%d new=%d | mouth deaths: %s' % (gm['gid'], p, 'calc' if a['calc'] else ('us' if gm['us'] else 'oth'), 'calc' if b['calc'] else ('us' if gm['us'] else 'oth'), a['r0'], endA, b['r0'], b['r0'] - endA, nprev, nnew, desc))
