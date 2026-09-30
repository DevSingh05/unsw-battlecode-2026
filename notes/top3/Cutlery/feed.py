"""Feeding / king rally analysis. For each (game, team) in round-limit games: own deaths near the king (Manhattan<=3), by 25-round window,
feeder lengths, share of their pearls eaten by the king, start of the rally (first 25-round window with >=4 near-king deaths),
and pre-rally king size. Usage: feed.py GROUPS(comma) [maps comma]"""
import sys, os, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import collect, sim2
grps = sys.argv[1].split(','); maps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
G = [x for x in collect.games() if x['grp'] in grps and (not maps or x['map'] in maps)]
M = lambda v: st.mean(v) if v else float('nan')
agg = collections.defaultdict(list); starts = []; per = []
for it in G:
    g = sim2.simulate(it['path'])
    if g['result'].get('endReason') != 'roundLimit': continue
    T = it['T']; R = dict(g['rounds'])
    eaten = collections.defaultdict(list)
    for e in g['eats']:
        if e['corpse'] is not None: eaten[e['corpse'][0]].append(e)
    win = collections.Counter(); feedL = []; kshare = []; kin = []; fast = []
    for d in g['deaths']:
        if d['team'] != T or d['round'] < 200 or not d.get('king'): continue
        kid, kl, kd, kc = d['king']
        if kd > 3 or kl < d['len']: continue
        w = (d['round'] // 25) * 25; win[w] += 1; feedL.append(d['len'])
        E = eaten.get(d['id'], []); drop = (d['len'] + 1) // 2
        kshare.append(sum(1 for e in E if e['id'] == kid) / drop)
        fast.append(M([e['round'] - d['round'] for e in E if e['id'] == kid]) if any(e['id'] == kid for e in E) else None)
        kin.append(d['reason'])
    st_ = next((w for w in sorted(win) if win[w] >= 4), None)
    starts.append(st_)
    pre = R.get(st_ - 1)[T]['max'] if st_ and R.get(st_ - 1) else None
    n_pre = R.get(st_ - 1)[T]['n'] if st_ and R.get(st_ - 1) else None
    per.append((it['gid'], it['map'][:10], it['grp'], 'W' if g['result']['winner'] == T else 'L', st_, pre, n_pre, sum(win.values()), round(M(feedL), 1),
                round(M(kshare), 2), g['rounds'][-1][1][T]['max'], collections.Counter(kin).most_common(2)))
    agg['nfeed'].append(sum(win.values())); agg['feedL'] += feedL; agg['kshare'] += kshare; agg['fast'] += [x for x in fast if x is not None]
    for w in range(200, 500, 25): agg[f'w{w}'].append(win[w])
for p in sorted(per, key=lambda p: p[1]): print(p)
print('games', len(per), 'feed deaths/game', round(M(agg['nfeed']), 1), 'feeder len', round(M(agg['feedL']), 2), 'len dist', sorted(collections.Counter(min(x, 8) for x in agg['feedL']).items()),
      'king share of feeder pearls', round(M(agg['kshare']), 2), 'rounds to eat', round(M(agg['fast']), 1))
print('rally start windows', collections.Counter(starts))
print('near-king deaths per window', ' '.join(f'{w}:{M(agg[f"w{w}"]):.1f}' for w in range(200, 500, 25)))
