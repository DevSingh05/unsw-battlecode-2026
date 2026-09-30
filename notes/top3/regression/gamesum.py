"""Per-game summary (sim2) for our Trophy/Devil games: result, end round, our/their n/total/max at r50/100/200/300/400/end,
deaths by reason and length bucket.  python3 notes/top3/regression/gamesum.py MAP[,MAP] [fam,fam]"""
import json, os, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame'))
from versions import version, FAMILY
import sim2
maps = sys.argv[1].split(','); fams = sys.argv[2].split(',') if len(sys.argv) > 2 else ['v29', 'v30', 'v31']
L = json.load(open(os.path.join(H, 'ledger_all.json')))
rows = []
for r in sorted(L, key=lambda r: r['at']):
    f = FAMILY[version(r['at'])]
    if r['map'] not in maps or f not in fams: continue
    p = os.path.join(ROOT, 'replays/regcheck/%d.replay' % r['game'])
    if not os.path.exists(p): continue
    g = sim2.simulate(p); us = r['side']; th = 'B' if us == 'A' else 'A'
    snap = dict(g['rounds'])
    def at(k):
        s = snap.get(k) or g['rounds'][-1][1]
        return '%d/%d/%d-%d/%d/%d' % (s[us]['n'], s[us]['total'], s[us]['max'], s[th]['n'], s[th]['total'], s[th]['max'])
    D = collections.Counter(); big = []
    for d in g['deaths']:
        if d['team'] != us: continue
        D[d['reason']] += 1
        if d['len'] >= 6: big.append('r%d L%d %s' % (d['round'], d['len'], d['reason'][:9]))
    DT = collections.Counter(d['reason'] for d in g['deaths'] if d['team'] == th)
    eu = sum(1 for e in g['eats'] if e['team'] == us); et = sum(1 for e in g['eats'] if e['team'] == th)
    sp = sum(1 for s in g['splits'] if s['team'] == us)
    row = dict(game=r['game'], map=r['map'], fam=f, ver=version(r['at']), opp=r['opp'], elo=r['oppElo'], ranked=r['ranked'],
               win=r['win'], end=g['last_round'], result=str(g['result'])[:80], eats=(eu, et), splits=sp,
               deaths=dict(D), their_deaths=dict(DT), big_deaths=big,
               snaps={k: at(k) for k in (50, 100, 200, 300, 400)}, final=at(g['last_round']))
    rows.append(row)
    print('%d %-7s %-5s %-6s %-20s %4d %s %s end r%3d eats %3d-%3d splits %3d | r100 %s r200 %s r300 %s end %s' % (
        r['game'], r['map'][:7], f, row['ver'], r['opp'][:20], r['oppElo'], 'R' if r['ranked'] else 'u', 'W' if r['win'] else 'L',
        g['last_round'], eu, et, sp, row['snaps'][100], row['snaps'][200], row['snaps'][300], row['final']))
    print('      our deaths %s | theirs %s | big %s' % (dict(D), dict(DT), big[:8]))
json.dump(rows, open(os.path.join(H, 'gamesum_%s.json' % '_'.join(m.replace(' ', '') for m in maps)), 'w'), indent=1, default=str)
