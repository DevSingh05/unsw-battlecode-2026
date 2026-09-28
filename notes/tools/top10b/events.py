"""Dump per-event records (deaths, sprints, splits, eats-by-king) for every (game, team) in analyze.games().
Usage: python3 events.py [jobs] -> events.pkl  {'deaths': [...], 'sprints': [...], 'splits': [...]} each tagged grp/map/gid."""
import os, sys, pickle, collections
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import analyze as A, sim2


def work(args):
    path, tags = args
    g = sim2.simulate(path); m = g['map']
    rounds = dict(g['rounds'])
    out = {'deaths': [], 'sprints': [], 'splits': []}
    # map move by (round,id) for crossing flag on deaths
    mv = {}
    for a in g['moves']:
        if a.get('suicide'): continue
        mvs = a['act'].get('move', [])
        mv[(a['round'], a['id'])] = (mvs, A.crossed_portal(m, a['head'], mvs) if mvs else False, a)
    last_split = {}
    for s in g['splits']:
        last_split.setdefault(s['parent'], []).append(s['round']); last_split.setdefault(s['child'], []).append(s['round'])
    for T, tag in tags.items():
        for d in g['deaths']:
            if d['team'] != T: continue
            x = mv.get((d['round'], d['id']))
            free = sum(1 for v in d['nbrs'].values() if v in ('free', 'pearl'))
            sp = [r for r in last_split.get(d['id'], []) if r <= d['round']]
            s = rounds.get(d['round'])
            kingL = s[T]['max'] if s else None
            rec = dict(tag, round=d['round'], id=d['id'], len=d['len'], reason=d['reason'], age=d['age'], free=free,
                       cross=bool(x and x[1]), move=''.join(x[0]) if x else None, acted=d['actor'] == d['id'],
                       since_split=(d['round'] - sp[-1]) if sp else None, hit=d.get('hit'), king=d.get('king'),
                       enemy_near=d.get('enemy_near'), ally_near=d.get('ally_near'), killer_team=d.get('killer_team'),
                       victim_team=d.get('victim_team'), killer_len=d.get('killer_len'), victim_len=d.get('victim_len'),
                       nbrs=d['nbrs'], teamking=kingL, units=s[T]['n'] if s else None)
            out['deaths'].append(rec)
        for a in g['moves']:
            if a['team'] != T or a.get('suicide'): continue
            mvs = a['act'].get('move', [])
            if len(mvs) >= 2:
                s = rounds.get(a['round'])
                out['sprints'].append(dict(tag, round=a['round'], id=a['id'], L=a['len_before'], steps=len(mvs), ate=a['ate'],
                                           killed=a['killed'], died=a['died'], near=a['near_enemy_head'], enemy_after=a.get('enemy_after'),
                                           is_king=(s and s[T]['king'] == a['id']), cross=A.crossed_portal(m, a['head'], mvs)))
        for s_ in g['splits']:
            if s_['team'] != T: continue
            out['splits'].append(dict(tag, **s_))
    return out


if __name__ == '__main__':
    G = A.games(); by = collections.defaultdict(dict)
    for x in G: by[x['path']][x['T']] = {k: x[k] for k in ('gid', 'map', 'grp', 'name')}
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with Pool(jobs) as P:
        res = P.map(work, sorted(by.items()), chunksize=2)
    ev = {'deaths': [], 'sprints': [], 'splits': []}
    for r in res:
        for k in ev: ev[k] += r[k]
    pickle.dump(ev, open(os.path.join(H, 'events.pkl'), 'wb'))
    print({k: len(v) for k, v in ev.items()})
