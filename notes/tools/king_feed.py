#!/usr/bin/env python3
"""King growth + feeding efficiency in the ch1 batch.

For each game: longest-dragon length over time (us/them), eats by our end-game king,
feeder deaths (our dragon dies HitSelf, round>=330, within 5 of our longest),
where the feeder pearls went (king / other ally / enemy / uneaten), and deaths of
our longest dragon (len>=8) with cause and whether the other party was friendly.
    python3 notes/tools/king_feed.py
"""
import collections, json, os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate
DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'replays', 'ch1')

def run(gid, us):
    g = simulate(os.path.join(DIR, f'{gid}.replay'))
    them = 'B' if us == 'A' else 'A'
    snap = dict(g['rounds'])
    R = {'map': g['map'].name}
    for k, T in (('us', us), ('them', them)):
        R['max_' + k] = [snap.get(r, snap[max(snap)])[T]['max'] for r in (100, 200, 250, 300, 350, 400, 450, g['last_round'])]
    # feeders
    feeders = {}
    for d in g['deaths']:
        if d['team'] == us and d['reason'] == 'HitSelf' and d['round'] >= 330 and d.get('king') and d['king'][2] <= 5 and d['king'][1] >= d['len'] + 2:
            feeders[d['id']] = (d['round'], d['len'], d['king'][0])
    drop = sum(math.ceil(L / 2) for (_, L, _) in feeders.values())
    dest = collections.Counter()
    for e in g['eats']:
        c = e['corpse']
        if c and c[0] in feeders:
            kid = feeders[c[0]][2]
            if e['id'] == kid: dest['king'] += 1
            elif e['team'] == us: dest['ally'] += 1
            else: dest['enemy'] += 1
    R['feeders'] = len(feeders); R['feed_len'] = sum(L for (_, L, _) in feeders.values()); R['feed_drop'] = drop; R['feed_dest'] = dict(dest)
    # our final king: eats in last 170 rounds by source
    fin = snap[max(snap)]
    kid = fin[us]['king']
    ke = collections.Counter()
    for e in g['eats']:
        if e['id'] == kid and e['round'] >= 330:
            ke['spawn' if not e['corpse'] else ('feed' if e['corpse'][0] in feeders else ('own_corpse' if e['corpse'][1] == us else 'enemy_corpse'))] += 1
    R['king_eats_330'] = dict(ke)
    tk = fin[them]['king']
    te = collections.Counter()
    for e in g['eats']:
        if e['id'] == tk and e['round'] >= 330:
            te['spawn' if not e['corpse'] else ('own_corpse' if e['corpse'][1] == them else 'enemy_corpse')] += 1
    R['their_king_eats_330'] = dict(te)
    # birth round of final kings
    R['king_born'] = (g['born'].get(kid), g['born'].get(tk))
    # our big dragon deaths
    bd = []
    for d in g['deaths']:
        if d['team'] == us and d['len'] >= 8:
            other = d.get('killer_team') or d.get('victim_team') or (d['hit']['team'] if d.get('hit') else None)
            bd.append((d['round'], d['len'], d['reason'], 'friendly' if other == us else ('enemy' if other else '-'),
                       d.get('enemy_near', (0, 0, 99))[2] if d.get('enemy_near') else None))
    R['big_deaths'] = bd
    tb = [(d['round'], d['len'], d['reason']) for d in g['deaths'] if d['team'] == them and d['len'] >= 8]
    R['their_big_deaths'] = tb
    return R

if __name__ == '__main__':
    summ = json.load(open(os.path.join(DIR, 'summary.json')))
    for s in summ:
        if s['win'] and s['end'] != 'roundLimit': continue
        R = run(s['id'], s['side'])
        tag = 'W' if s['win'] else 'L'
        print(f"{s['id']} {tag} {R['map'][:16]:16s} max us {R['max_us']} them {R['max_them']} (r100..end)")
        print(f"    feeders {R['feeders']} (len {R['feed_len']}, drop {R['feed_drop']}) -> {R['feed_dest']}; our king eats r330+ {R['king_eats_330']} theirs {R['their_king_eats_330']} born {R['king_born']}")
        print(f"    our len>=8 deaths {R['big_deaths']}; theirs {len(R['their_big_deaths'])}")
