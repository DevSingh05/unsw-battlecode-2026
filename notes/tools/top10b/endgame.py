"""Endgame (r350-500) king study for round-limit games.
Final king = team's longest dragon at the end; lineage traced back through reverse splits (child longer than parent).
Per (game, team): king length at 350/400/450/500, king eats r350+ by source (spawn / own corpse / enemy corpse),
feeder deaths whose corpse the king ate, king sprints (and what they did), enemy heads within 2 of king (threat rounds),
second-longest at end. Usage: python3 endgame.py [jobs] -> endgame.pkl"""
import os, sys, pickle, collections
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import analyze as A, sim2


def work(args):
    path, tags = args
    g = sim2.simulate(path); m = g['map']
    if g['result'].get('endReason') != 'roundLimit': return []
    rounds = dict(g['rounds']); last = g['last_round']
    out = []
    for T, tag in tags.items():
        fin = rounds[last][T]
        if not fin['ids']: continue
        k = max(fin['ids'], key=lambda j: (fin['ids'][j], -j))
        lineage = {k}; cur = k
        # parent -> child reverse split: the child continues the body; walk back
        while cur in g['parent_of']:
            p = g['parent_of'][cur]
            sp = [s for s in g['splits'] if s['child'] == cur]
            if sp and sp[0]['k'] > sp[0]['L'] - sp[0]['k']: lineage.add(p); cur = p
            else: break
        R = dict(tag, king=k, born=g['born'].get(cur, 0))
        for r in (300, 350, 400, 450, 500):
            s = rounds.get(min(r, last))
            R[f'k{r}'] = max((s[T]['ids'].get(j, 0) for j in lineage), default=0)
            R[f'max{r}'] = s[T]['max']; R[f'n{r}'] = s[T]['n']
            R[f'emax{r}'] = s['B' if T == 'A' else 'A']['max']
        ls = fin['lens']; R['second'] = ls[1] if len(ls) > 1 else 0
        src = collections.Counter(); feeders = set(); feederL = []
        dead = {d['id']: d for d in g['deaths']}
        for e in g['eats']:
            if e['id'] in lineage and e['round'] >= 350:
                if e['corpse']:
                    if e['corpse'][1] == T:
                        src['own'] += 1
                        if e['corpse'][0] not in feeders:
                            feeders.add(e['corpse'][0]); feederL.append(e['corpse'][3])
                    else: src['enemy'] += 1
                else: src['spawn'] += 1
        R.update({f'src_{a}': b for a, b in src.items()}); R['feeders'] = len(feeders)
        R['feederL'] = feederL
        # king sprints and threat exposure
        ks = collections.Counter()
        for a in g['moves']:
            if a['id'] in lineage and a['round'] >= 350 and not a.get('suicide'):
                ks['moves'] += 1
                n = a['near_enemy_head']
                if n and n[0] <= 2: ks['thr2'] += 1
                if n and n[0] <= 4: ks['thr4'] += 1
                if a['steps'] >= 2:
                    ks['sprint'] += 1; ks['sprint_ate'] += a['ate']
                    if n and n[0] <= 3: ks['sprint_threat'] += 1
        R.update({f'k_{a}': b for a, b in ks.items()})
        # king U-turn / splits r350+
        R['k_splits'] = sum(1 for s in g['splits'] if s['parent'] in lineage and s['round'] >= 350)
        # all team sprints r350+ by length / purpose
        ts = collections.Counter()
        for a in g['moves']:
            if a['team'] == T and a['round'] >= 350 and a['steps'] >= 2 and a['id'] not in lineage:
                ts['n'] += 1; ts['ate'] += a['ate'] > 0; ts['kill'] += len(a['killed']) > 0; ts['died'] += a['died'] is not None
                ts['L' + str(min(a['len_before'], 6))] += 1
        R.update({f'ts_{a}': b for a, b in ts.items()})
        out.append(R)
    return out


if __name__ == '__main__':
    G = A.games(); by = collections.defaultdict(dict)
    for x in G: by[x['path']][x['T']] = {k: x[k] for k in ('gid', 'map', 'grp', 'name')} | {'win_': None}
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with Pool(jobs) as P:
        res = P.map(work, sorted(by.items()), chunksize=2)
    rows = [r for x in res for r in x]
    pickle.dump(rows, open(os.path.join(H, 'endgame.pkl'), 'wb'))
    print(len(rows))
