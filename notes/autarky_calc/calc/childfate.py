"""What does a pump child do in the 15 rounds after it's born?"""
from common import *
import pickle, collections, statistics as st
E = pickle.load(open(os.path.join(H, 'episodes.pkl'), 'rb'))
res = collections.defaultdict(collections.Counter); dists = collections.defaultdict(list)
for gm in GAMES:
    g = sim(gm['gid']); R = dict(g['rounds'])
    dives = collections.defaultdict(list)
    for e in E:
        if e['gid'] == gm['gid']: dives[e['id']].append(e)
    splits_by = collections.defaultdict(list)
    for s in g['splits']: splits_by[s['parent']].append(s)
    dmap = {d['id']: d for d in g['deaths']}
    for e in E:
        if e['gid'] != gm['gid'] or e['end'] != 'split': continue
        grp = 'calc' if e['calc'] else ('US' if e['vsus'] else 'oth')
        ch = e['child']; r0 = e['r1']; kL = e['k']
        fate = 'alive/wander'
        nd = [x for x in dives.get(ch, []) if x['r0'] <= r0 + 15]
        sp = [s for s in splits_by.get(ch, []) if s['round'] <= r0 + 15]
        d = dmap.get(ch)
        firsts = []
        if nd: firsts.append((nd[0]['r0'], 'redive_same' if nd[0]['p'] == e['p'] else 'redive_other'))
        if sp and not (nd and sp[0]['round'] >= nd[0]['r0']): firsts.append((sp[0]['round'], 'open_split'))
        if d and d['round'] <= r0 + 15: firsts.append((d['round'], 'died_' + ('H2H' if d['reason'] == 'HitHeadToHead' else d['reason'][:6])))
        if firsts: fate = min(firsts)[1]
        res[(grp, kL)][fate] += 1
        if nd and nd[0]['p'] == e['p']: dists[grp].append(nd[0]['r0'] - r0)
for k in sorted(res):
    v = res[k]; n = sum(v.values())
    print(k, n, {a: '%.0f%%' % (100 * b / n) for a, b in v.most_common()})
for k, v in dists.items(): print(k, 'rounds from birth to re-dive same pocket', sorted(collections.Counter(v).items()))
