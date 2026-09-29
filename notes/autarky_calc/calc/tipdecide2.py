from common import *
import collections
PKT = pockets(); m = realmap()
rows = []
for gm in GAMES:
    g = sim(gm['gid']); c = gm['calc']; R = dict(g['rounds'])
    acts = {}
    for mv in g['moves']: acts[(mv['round'], mv['id'])] = ('move', mv)
    for s in g['splits']: acts[(s['round'], s['parent'])] = ('split', s)
    for (r, i), (k, x) in acts.items():
        S = R.get(r - 1)
        if not S or i not in S['bodies']: continue
        bd = S['bodies'][i]; h = bd[0]; p = pocket_of(h)
        if p is None or S['heads'][i][2] != c: continue
        L = len(bd); d = PKT[h]
        deeper = [t for t in S['pearls'] if pocket_of(t) == p and PKT[t] < d]
        units = sum(1 for j, v in S['heads'].items() if v[2] == c)
        # tail tile free neighbours (child head would be old tail) excluding body
        occ = set(); [occ.update(b) for b in S['bodies'].values()]
        tail = bd[-1]
        tfree = sum(1 for dd in 'NESW' if (lambda n: n is not None and n not in occ)(m.step(tail, dd)))
        en = min((mdist(v[0], MOUTH[p]) for j, v in S['heads'].items() if v[2] != c), default=99)
        own = sum(1 for j, v in S['heads'].items() if v[2] == c and j != i and mdist(v[0], MOUTH[p]) <= 3)
        rows.append(dict(gid=gm['gid'], r=r, L=L, d=d, deep=len(deeper), a=('split%d' % x['k'] if k == 'split' else 'move'), units=units, tfree=tfree, en=en, own=own, tail=tail))
def show(filt, lab):
    R_ = [x for x in rows if filt(x)]
    print(lab, len(R_))
    for key in ('units', 'tfree', 'en', 'own'):
        cc = collections.defaultdict(collections.Counter)
        for x in R_:
            v = x[key]
            if key == 'units': v = (v // 16) * 16
            if key == 'en': v = min(v, 8)
            cc[v][x['a']] += 1
        print('  by', key, dict(sorted((k, dict(v)) for k, v in cc.items())))
show(lambda x: x['L'] == 4 and x['d'] == 3 and x['deep'] == 2, 'L4 depth3 deeper2')
show(lambda x: x['L'] == 4 and x['d'] == 2 and x['deep'] == 1, 'L4 depth2 deeper1')
show(lambda x: x['d'] == 1 and x['L'] >= 4, 'at tip L>=4')
show(lambda x: x['L'] == 6 and x['d'] == 1, 'at tip L6')
