"""Compact per-turn decision dump from life_<g>.pkl: python3 decisions.py GAME R0 R1 id1,id2,..  (ids optional = all near)"""
import sys, pickle
from parsedbg import parse
g, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
ids = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
L = pickle.load(open('life_%d.pkl' % g, 'rb'))
for i in sorted(L):
    if ids and i not in ids: continue
    for x in L[i]:
        if not (r0 <= x['round'] <= r1): continue
        P = parse(x['dbg'])
        cs = ' | '.join('%s%s s=%.1f pe=%.2f a=%d d=%d%s%s%s%s%s' % (d, c['t'], c['score'], c['pearls'], c['area'], c['depth'],
                        ' aP=%.0f' % c['areaP'] if c.get('areaP') else '', ' dP=%.0f' % c['depthP'] if c.get('depthP') else '',
                        ' th=%.0f' % c['threatP'] if c.get('threatP') else '', ' box=%.0f' % c['box'] if c.get('box') else '',
                        ' POCKET:' + c['pocket'] if c.get('pocket') else '') for d, c in P['cands'].items())
        print('r%d id%d %s L%d real=%s bot=%s %s || %s' % (x['round'], i, x['head'], x['len'], x['real'], x['bot'], ('[' + P['branch'] + ']') if P['branch'] else '', cs))
