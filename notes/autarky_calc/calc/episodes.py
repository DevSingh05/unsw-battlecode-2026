"""Pocket dive episodes per team. An episode starts when a dragon's head enters a pocket tile from outside."""
from common import *
import collections, statistics as st, sys

def episodes(gm):
    g = sim(gm['gid']); c = gm['calc']
    R = dict(g['rounds'])
    ev = collections.defaultdict(list)  # id -> list of (round, kind, data)
    for mv in g['moves']:
        ev[mv['id']].append((mv['round'], 0, 'move', mv))
    for s in g['splits']:
        ev[s['parent']].append((s['round'], 1, 'split', s))
    for d in g['deaths']:
        ev[d['id']].append((d['round'], 2, 'death', d))
    dmap = {d['id']: d for d in g['deaths']}
    eps = []
    for i, L in ev.items():
        L.sort(key=lambda x: (x[0], x[1]))
        cur = None
        for r, _, k, x in L:
            if k == 'move':
                h0, h1 = x['head'], x.get('head_after')
                if cur is None and h1 is not None and pocket_of(h1) is not None and pocket_of(h0) is None:
                    p = pocket_of(h1)
                    S = R.get(r - 1)
                    near_own = near_en = en_in = own_in = 0; en_min = 99
                    if S:
                        for j, (h, LL, T) in S['heads'].items():
                            if j == i: continue
                            dd = mdist(h, MOUTH[p])
                            if T == x['team']:
                                if pocket_of(h) == p: own_in += 1
                                elif dd <= 3: near_own += 1
                            else:
                                en_min = min(en_min, dd)
                                if pocket_of(h) == p: en_in += 1
                                elif dd <= 3: near_en += 1
                        pe = sum(1 for t in S['pearls'] if pocket_of(t) == p)
                    else:
                        pe = -1
                    cur = dict(id=i, team=x['team'], calc=(x['team'] == c), p=p, r0=r, L0=x['len_before'], pearls0=pe,
                               near_own=near_own, near_en=near_en, en_min=en_min, own_in=own_in, en_in=en_in, eats=x['ate'], path=[h1])
                elif cur is not None:
                    cur['eats'] += x['ate']
                    if h1 is not None: cur['path'].append(h1)
                    if h1 is not None and pocket_of(h1) is None:
                        if cur.get('end') != 'split': cur.update(end='walkout', r1=r)
                        cur.update(L1=x['len_after'], rout=r); eps.append(cur); cur = None
            elif k == 'split' and cur is not None:
                cur.setdefault('allsplits', []).append((r - cur['r0'], x['L'], x['k'], pockets().get(cur['path'][-1], 0)))
                if 'Ls' in cur: continue
                cur.update(end='split', r1=r, Ls=x['L'], k=x['k'], tile=cur['path'][-1], child=x['child'], exits=x['exits'])
                # fates
                pd = dmap.get(i); cd = dmap.get(x['child'])
                cur['parent_death'] = (pd['round'] - r, pd['reason'], pd['len']) if pd and pd['round'] - r <= 10 else None
                cur['child_death'] = (cd['round'] - r, cd['reason'], cd['len']) if cd and cd['round'] - r <= 10 else None
            elif k == 'death' and cur is not None:
                if cur.get('end') != 'split': cur.update(end='death', r1=r)
                cur.update(reason=x['reason'], Ld=x['len'], rdeath=r); eps.append(cur); cur = None
    return eps

def summarize(E, label):
    n = len(E)
    if not n: print(label, 'none'); return
    ends = collections.Counter(e['end'] for e in E)
    sp = [e for e in E if e['end'] == 'split']
    print('%s: dives %d  ends %s' % (label, n, dict(ends)))
    print('   entry L %s' % dict(collections.Counter(e['L0'] for e in E)))
    print('   pearls in pocket at entry %s' % dict(sorted(collections.Counter(e['pearls0'] for e in E).items())))
    print('   own heads within 3 of mouth at entry %s ; own already inside %s' % (dict(sorted(collections.Counter(e['near_own'] for e in E).items())), dict(collections.Counter(e['own_in'] for e in E))))
    print('   nearest enemy head to mouth at entry: <=3 %d, 4-6 %d, >=7 %d; enemy inside %d' % (sum(e['en_min'] <= 3 for e in E), sum(4 <= e['en_min'] <= 6 for e in E), sum(e['en_min'] >= 7 for e in E), sum(e['en_in'] > 0 for e in E)))
    if sp:
        print('   split (L,k): %s' % collections.Counter((e['Ls'], e['k']) for e in sp).most_common(8))
        print('   split tile depth: %s' % collections.Counter(pockets()[e['tile']] if e['tile'] in pockets() else 'out' for e in sp).most_common())
        print('   rounds entry->split %s' % collections.Counter(e['r1'] - e['r0'] for e in sp).most_common(6))
        print('   parent dies<=10: %d/%d  %s' % (sum(1 for e in sp if e['parent_death']), len(sp), collections.Counter((e['parent_death'][1], e['parent_death'][2], e['parent_death'][0]) for e in sp if e['parent_death']).most_common(6)))
        print('   child dies<=10: %d/%d  %s' % (sum(1 for e in sp if e['child_death']), len(sp), collections.Counter((e['child_death'][1], e['child_death'][0]) for e in sp if e['child_death']).most_common(6)))
        net = [e['k'] - e['L0'] for e in sp]
        print('   net child-entry per split cycle: mean %.2f' % st.mean(net))
        pat = collections.Counter((e['L0'], tuple((a[1], a[2], a[3]) for a in e['allsplits']), e.get('Ld', e.get('L1'))) for e in sp)
        print('   dive patterns (entryL, [(L,k,depth)...], parent end L): n=%d' % len(sp))
        for kk, v in pat.most_common(10): print('      %4d  %s' % (v, kk))
        mass_out = [sum(a[2] for a in e['allsplits']) - e['L0'] for e in sp]
        print('   mass out via children - entry L: mean %.2f; units out per dive %.2f' % (st.mean(mass_out), st.mean(len(e['allsplits']) for e in sp)))
        rr = [e.get('rdeath', e.get('rout', e['r1'])) - e['r0'] for e in sp]
        print('   rounds the diver lineage occupies pocket: %s' % collections.Counter(rr).most_common(6))
    de = [e for e in E if e['end'] == 'death']
    if de: print('   died inside w/o split: %s' % collections.Counter((e['reason'], e['Ld']) for e in de).most_common(6))
    wo = [e for e in E if e['end'] == 'walkout']
    if wo: print('   walked out: L %s' % collections.Counter((e['L0'], e['L1']) for e in wo).most_common(6))

if __name__ == '__main__':
    import pickle
    ALL = []
    for gm in GAMES:
        E = episodes(gm)
        for e in E: e['gid'] = gm['gid']; e['vsus'] = gm['us'] is not None
        ALL += E
    pickle.dump(ALL, open(os.path.join(H, 'episodes.pkl'), 'wb'))
    summarize([e for e in ALL if e['calc'] and e['vsus']], 'CALC vs US (4 games)')
    summarize([e for e in ALL if not e['calc'] and e['vsus']], 'US vs calc (4 games)')
    summarize([e for e in ALL if e['calc'] and not e['vsus']], 'CALC vs others (9 games)')
    summarize([e for e in ALL if not e['calc'] and not e['vsus']], 'others vs calc (9 games)')
