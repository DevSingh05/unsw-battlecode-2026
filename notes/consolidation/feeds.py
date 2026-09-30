"""Feed-death detail: L<=5 own-neck suicides r>=320 per team; who ate the pearls.  python3 notes/consolidation/feeds.py REPLAY"""
import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tools/midgame'))
import sim2
S = sim2.simulate(sys.argv[1])
m = S['map']
eats_by_corpse = collections.defaultdict(list)
for e in S['eats']:
    if e['corpse']: eats_by_corpse[e['corpse'][0]].append(e)
son = collections.Counter((s['team'], s['round'] // 50 * 50) for s in S['sonars'] if s['round'] >= 250)
for T in 'AB':
    print(T, 'sonar pings per 50r from r250:', sorted((r, n) for (t, r), n in son.items() if t == T))
    ds = [d for d in S['deaths'] if d['team'] == T and d['round'] >= 320 and d['len'] <= 5 and d['reason'] == 'HitSelf']
    near = [d for d in ds if d.get('ally_near') and d['ally_near'][2] <= 3]
    hostlen = collections.Counter()
    ate_host = ate_team = drop = ate_en = 0
    for d in near:
        # nearest longer ally within 3
        hl = d['ally_near'][1]
        hostlen['L<6' if hl < 6 else 'L6-9' if hl < 10 else 'L10-19' if hl < 20 else 'L20+'] += 1
        es = eats_by_corpse.get(d['id'], [])
        drop += (d['len'] + 1) // 2
        ate_team += sum(1 for e in es if e['team'] == T)
        ate_en += sum(1 for e in es if e['team'] != T)
        ate_host += sum(1 for e in es if e['id'] == d['ally_near'][0])
    print('  HitSelf L<=5 r320+: %d, with ally head <=3: %d; nearest ally len %s' % (len(ds), len(near), dict(hostlen)))
    print('  pearls dropped %d: eaten by team %d (by that nearest ally %d), by enemy %d' % (drop, ate_team, ate_host, ate_en))
    other = collections.Counter(d['reason'] for d in S['deaths'] if d['team'] == T and d['round'] >= 320)
    print('  all deaths r320+ by reason', dict(other))
