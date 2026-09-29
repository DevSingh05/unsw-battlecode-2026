"""Summarise the reconstructed v29 decisions of every member of an episode:  python3 episode.py GAME R0 R1 id,id,...
Per dragon-turn: class (turnclass), chosen candidate pearl value, best pearl value among candidates, penalties on the best-pearl candidate."""
import sys, pickle, collections
from parsedbg import parse
g, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); ids = [int(v) for v in sys.argv[4].split(',')]
L = pickle.load(open('life_%d.pkl' % g, 'rb'))
TC = {(x['id'], x['r']): x['cls'] for x in pickle.load(open('turnclass.pkl', 'rb')) if x['game'] == g}
C = collections.Counter(); pen = collections.Counter(); n = 0; agree = 0
for i in ids:
    for x in L.get(i, []):
        if not (r0 <= x['round'] <= r1): continue
        n += 1; agree += x['real'] == x['bot']
        C[TC.get((i, x['round']), '?')] += 1
        P = parse(x['dbg'])
        for d, c in P['cands'].items():
            for k in ('areaP', 'depthP', 'threatP'):
                if c.get(k): pen[k] += 1
            if c.get('box', 0) <= -60: pen['box-60'] += 1
            elif c.get('box', 0) < 0: pen['box-3'] += 1
            if c.get('pocket'): pen['POCKET ' + c['pocket']] += 1
        if P['branch'] and not P['branch'][0] in 'NESW': pen['branch:' + P['branch'].split()[0]] += 1
print('game %d r%d-%d dragons %d turns %d (bot==real %d)' % (g, r0, r1, len(ids), n, agree))
print(' classes:', C.most_common())
print(' penalty hits on any candidate:', pen.most_common())
