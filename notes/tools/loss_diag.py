#!/usr/bin/env python3
"""Loss diagnosis over the ch1 unranked batch (replays/ch1).

Per game, per team: dragon count / eats / deaths by cause over time, harvest
efficiency (eats per dragon-round), friendly-vs-enemy head-ons, who hit whose
body, king length and feeding, king deaths, idle dragons (long no-eat streaks).

    python3 notes/tools/loss_diag.py            # tables to stdout
    python3 notes/tools/loss_diag.py --game 351215   # one-game timeline
Results are cached in replays/ch1/diag.pkl.
"""
import collections, json, os, pickle, sys

sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DIR = os.path.join(ROOT, 'replays', 'ch1')
BINS = [0, 25, 50, 100, 150, 200, 300, 400, 501]


def binof(r):
    for i in range(len(BINS) - 1):
        if BINS[i] <= r < BINS[i + 1]:
            return i
    return len(BINS) - 2


def analyse(gid, us):
    g = simulate(os.path.join(DIR, f'{gid}.replay'))
    them = 'B' if us == 'A' else 'A'
    side = {us: 'us', them: 'them'}
    m = g['map']
    R = {'id': gid, 'map': m.name, 'last': g['last_round'], 'W': m.w, 'H': m.h}
    # ---- per-round snapshots
    snap = {r: s for r, s in g['rounds']}
    R['count'] = {}; R['maxlen'] = {}; R['total'] = {}; R['avglen'] = {}
    for T in 'AB':
        k = side[T]
        R['count'][k] = {r: snap[r][T]['n'] for r in snap}
        R['maxlen'][k] = {r: snap[r][T]['max'] for r in snap}
        R['total'][k] = {r: snap[r][T]['total'] for r in snap}
    # dragon-rounds per bin
    dr = {k: [0] * (len(BINS) - 1) for k in ('us', 'them')}
    for r, s in snap.items():
        for T in 'AB':
            dr[side[T]][binof(r)] += s[T]['n']
    R['dragon_rounds'] = dr
    # ---- eats per bin
    eats = {k: [0] * (len(BINS) - 1) for k in ('us', 'them')}
    corpse_eats = {k: collections.Counter() for k in ('us', 'them')}  # whose corpse we ate
    for e in g['eats']:
        if e['team'] not in side: continue
        k = side[e['team']]
        eats[k][binof(e['round'])] += 1
        if e['corpse']:
            corpse_eats[k][side[e['corpse'][1]]] += 1
        else:
            corpse_eats[k]['spawn'] += 1
    R['eats'] = eats; R['eat_src'] = corpse_eats
    # ---- deaths
    D = []
    for d in g['deaths']:
        k = side[d['team']]
        cause = d['reason']
        by = None
        if cause == 'HitHeadToHead':
            other_team = d.get('killer_team') or d.get('victim_team')
            by = 'friendly' if other_team == d['team'] else 'enemy'
            role = 'victim' if 'killer' in d else 'mover'
            cause = f'H2H-{by}-{role}'
        elif cause == 'HitOtherBody':
            h = d.get('hit')
            by = ('friendly' if h['team'] == d['team'] else 'enemy') if h else 'unk'
            cause = f'Body-{by}'
        king = d.get('king')
        D.append({'side': k, 'round': d['round'], 'cause': cause, 'len': d['len'], 'id': d['id'],
                  'king_len': king[1] if king else 0, 'king_dist': king[2] if king else 99,
                  'enemy_near': d.get('enemy_near'), 'ally_near': d.get('ally_near'), 'head': d['head'],
                  'move': d.get('move'), 'actor': d['actor']})
    R['deaths'] = D
    # ---- king (longest) tracking: per round the longest id and length; detect king deaths
    kings = {k: [] for k in ('us', 'them')}
    for r in sorted(snap):
        for T in 'AB':
            kings[side[T]].append((r, snap[r][T]['king'], snap[r][T]['max']))
    R['kings'] = kings
    # a "king death" = death of a dragon that was its team's longest (len>=8) at that moment
    kd = []
    lastsnap = {}
    for d in g['deaths']:
        r = d['round']
        prev = snap.get(r - 1)
        if not prev: continue
        T = d['team']
        if prev[T]['king'] == d['id'] or (d['len'] >= prev[T]['max'] and d['len'] >= 8):
            kd.append({'side': side[T], 'round': r, 'len': d['len'], 'reason': d['reason'],
                       'killer_team': side.get(d.get('killer_team') or d.get('victim_team') or ''),
                       'hit': d.get('hit'), 'enemy_near': d.get('enemy_near')})
    R['king_deaths'] = kd
    # ---- idle: per dragon, longest streak of moves without eating; fraction of dragon-turns
    # spent in streaks >= 30 rounds
    streak = collections.defaultdict(int)
    idle_turns = {k: 0 for k in ('us', 'them')}; turns = {k: 0 for k in ('us', 'them')}
    idle_by_len = {k: collections.Counter() for k in ('us', 'them')}
    for mv in g['moves']:
        k = side[mv['team']]
        turns[k] += 1
        if mv.get('ate'):
            if streak[mv['id']] >= 30: idle_turns[k] += streak[mv['id']]
            streak[mv['id']] = 0
        else:
            streak[mv['id']] += 1
    for i, s in streak.items():
        if s >= 30: idle_turns[side[g['team'][i]]] += s
    R['idle'] = {k: (idle_turns[k], turns[k]) for k in turns}
    # sprint usage (multi-step moves) and their cost
    spr = {k: collections.Counter() for k in ('us', 'them')}
    for mv in g['moves']:
        k = side[mv['team']]
        if mv.get('steps', 0) >= 2:
            spr[k]['n'] += 1
            spr[k]['steps'] += mv['steps']
            spr[k]['ate'] += mv['ate']
            if mv.get('killed'): spr[k]['kills'] += len(mv['killed'])
    R['sprints'] = spr
    # splits
    sp = {k: [0] * (len(BINS) - 1) for k in ('us', 'them')}
    splen = {k: collections.Counter() for k in ('us', 'them')}
    for s in g['splits']:
        k = side[s['team']]
        sp[k][binof(s['round'])] += 1
        splen[k][(s['L'], s['k'])] += 1
    R['splits'] = sp; R['split_sizes'] = splen
    # final
    R['result'] = g['result']
    return R


def load_all():
    cache = os.path.join(DIR, 'diag.pkl')
    summ = json.load(open(os.path.join(DIR, 'summary.json')))
    if os.path.exists(cache):
        data = pickle.load(open(cache, 'rb'))
        if len(data) == len(summ):
            return summ, data
    data = {}
    for s in summ:
        data[s['id']] = analyse(s['id'], s['side'])
    pickle.dump(data, open(cache, 'wb'))
    return summ, data


def pct(a, b):
    return f'{100 * a / b:.0f}%' if b else '-'


def main():
    summ, data = load_all()
    if '--game' in sys.argv:
        gid = int(sys.argv[sys.argv.index('--game') + 1])
        one(data[gid]); return
    groups = {'W': [], 'L-elim': [], 'L-round': []}
    for s in summ:
        key = 'W' if s['win'] else ('L-elim' if s['end'] == 'teamEliminated' else 'L-round')
        groups[key].append(s['id'])
    for key, ids in groups.items():
        print(f'\n===== {key}: {len(ids)} games  maps={collections.Counter(data[i]["map"] for i in ids)}')
        # count timeline
        for k in ('us', 'them'):
            row = []
            for r in (10, 25, 50, 75, 100, 150, 200, 300, 400, 499):
                vals = [data[i]['count'][k].get(r, 0) for i in ids]
                row.append(f'{r}:{sum(vals)/len(vals):5.1f}')
            print(f'  count {k:4s}', ' '.join(row))
        for k in ('us', 'them'):
            row = []
            for r in (25, 50, 100, 200, 300, 400, 499):
                vals = [data[i]['maxlen'][k].get(r, 0) for i in ids]
                row.append(f'{r}:{sum(vals)/len(vals):5.1f}')
            print(f'  maxlen {k:4s}', ' '.join(row))
        # eats per dragon-round per bin
        for k in ('us', 'them'):
            row = []
            for b in range(len(BINS) - 1):
                e = sum(data[i]['eats'][k][b] for i in ids); d = sum(data[i]['dragon_rounds'][k][b] for i in ids)
                tot = sum(data[i]['eats'][k][b] for i in ids) / len(ids)
                row.append(f'{BINS[b]}-{BINS[b+1]}: {e/d if d else 0:.3f}/{tot:5.1f}')
            print(f'  eat/dr|eats {k:4s}', ' '.join(row))
        # eat sources
        for k in ('us', 'them'):
            c = collections.Counter()
            for i in ids: c += data[i]['eat_src'][k]
            print(f'  eat src {k}', dict(c))
        # deaths
        for k in ('us', 'them'):
            c = collections.Counter()
            for i in ids:
                for d in data[i]['deaths']:
                    if d['side'] == k: c[d['cause']] += 1
            print(f'  deaths {k} (per game)', {a: round(b / len(ids), 1) for a, b in c.most_common()})
        for k in ('us', 'them'):
            it = sum(data[i]['idle'][k][0] for i in ids); tt = sum(data[i]['idle'][k][1] for i in ids)
            print(f'  idle(>=30-round no-eat streak) {k}: {pct(it, tt)} of turns')
        for k in ('us', 'them'):
            c = collections.Counter()
            for i in ids: c += data[i]['sprints'][k]
            print(f'  sprints {k}', dict(c))
        for k in ('us', 'them'):
            c = collections.Counter()
            for i in ids: c += data[i]['split_sizes'][k]
            print(f'  split sizes {k}', dict(c.most_common(5)))
        kd = [(i, d) for i in ids for d in data[i]['king_deaths']]
        print('  king deaths us  :', [(i, d['round'], d['len'], d['reason'], d['killer_team']) for i, d in kd if d['side'] == 'us'][:40])
        print('  king deaths them:', len([1 for i, d in kd if d['side'] == 'them']))


def one(R):
    print(R['id'], R['map'], R['result'])
    for r in list(range(0, 100, 10)) + list(range(100, 500, 25)) + [R['last']]:
        if r not in R['count']['us']: continue
        print(f"  r{r:3d} us n={R['count']['us'][r]:2d} max={R['maxlen']['us'][r]:2d} tot={R['total']['us'][r]:3d} | "
              f"them n={R['count']['them'][r]:2d} max={R['maxlen']['them'][r]:2d} tot={R['total']['them'][r]:3d}")
    for d in R['deaths']:
        print('   ', d['round'], d['side'], d['cause'], 'len', d['len'], 'king', d['king_len'], d['king_dist'], 'en', d['enemy_near'], 'move', d['move'])


if __name__ == '__main__':
    main()
