"""Split child fate, r61-350: lifetime, pearls eaten in life, by child k and parent exits; also parent fate within 5 rounds.
Usage: python3 childfate.py SFu,U [MAP]"""
import os, sys, pickle, collections, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '../../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); import sim2
rows = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
want = sys.argv[1].split(','); MAP = sys.argv[2] if len(sys.argv) > 2 else None
bypath = collections.defaultdict(list)
for r in rows:
    if r['grp'] in want and (MAP is None or r['map'] == MAP): bypath[r['path']].append(r)
A = collections.defaultdict(lambda: collections.defaultdict(list)); ng = collections.Counter()
for p, rs in sorted(bypath.items()):
    g = sim2.simulate(p)
    death = {d['id']: d for d in g['deaths']}
    eats = collections.Counter(e['id'] for e in g['eats'])
    for r in rs:
        T = r['T']; ng[r['grp']] += 1
        for s in g['splits']:
            if s['team'] != T or not (61 <= s['round'] <= 350) or s['k'] >= s['L'] - 2 and s['L'] >= 8: continue
            c = s['child']; d = death.get(c)
            life = (d['round'] if d else g['last_round']) - s['round']
            key = ('k2' if s['k'] == 2 else 'k3+')
            A[r['grp']][key].append((life, eats[c], d is not None and life <= 5))
            A[r['grp']]['ex' + str(s['exits'])].append((life, eats[c], d is not None and life <= 5))
            pd = death.get(s['parent'])
            A[r['grp']]['parent'].append((0, 0, pd is not None and pd['round'] - s['round'] <= 5))
for gname in want:
    print('==', gname, ng[gname], 'team-games')
    for key, l in sorted(A[gname].items()):
        print(f'  {key:7s} n/g {len(l)/ng[gname]:6.1f}  died<=5r {sum(x[2] for x in l)/len(l):5.2f}  median life {st.median(x[0] for x in l):5.0f}  mean eats {st.mean(x[1] for x in l):5.2f}')
