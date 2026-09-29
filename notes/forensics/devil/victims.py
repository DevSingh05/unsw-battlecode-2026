#!/usr/bin/env python3
"""Every head-on death where the ENEMY moved into OUR head (we are the victim), Devil games.
For our last decision before the ram: our move, where the killer head was, the killer's reach of our
landing tile (1-step / 2-step), whether a landing tile out of 1- and 2-step reach existed, local heads
(cheb<=3 of our head, excluding us) allies v enemies, and who ate the corpse pearls within 6 rounds.
    python3 notes/forensics/devil/victims.py [W|L] [maxround]   -> victims.pkl
"""
import sys, pickle, collections, os
from common import games, sim, state, HERE, REFMAP

want = sys.argv[1] if len(sys.argv) > 1 else None
maxr = int(sys.argv[2]) if len(sys.argv) > 2 else 500


def reach(m, occ, src, L):
    """tiles an enemy head at src can hit this turn: 1 step, and 2 steps if L>=3 (free intermediate)"""
    r1 = set(); r2 = set()
    for d in 'NESW':
        a = m.step(src, d)
        if a is None: continue
        r1.add(a)
        if L >= 3 and a not in occ:
            for d2 in 'NESW':
                b = m.step(a, d2)
                if b is not None and b != src: r2.add(b)
    return r1, r2 - r1


rows = []
for g in sorted(games(), key=lambda g: g['at']):
    if want and ('W' if g['win'] else 'L') != want: continue
    S = sim(g['game']); us = g['side']
    for d in S['deaths']:
        if d['round'] > maxr: break
        if d['team'] != us or d['reason'] != 'HitHeadToHead' or d['id'] == d['actor']: continue
        k = d.get('killer'); vid = d['id']
        # our last action before the death
        mv = [x for x in S['moves'] if x['id'] == vid and (x['round'] < d['round'] or (x['round'] == d['round'] and vid < k))]
        if not mv: continue
        last = mv[-1]
        st = state(g['game'], last['round'], vid)
        m = st['map']; body = st['body']
        if k not in body: continue
        occ = set(t for b in body.values() for t in b)
        me = body[vid][0]; kh = body[k][0]; kl = len(body[k])
        r1, r2 = reach(m, occ, kh, kl)
        alts = []
        for dd in 'NESW':
            t = m.step(me, dd)
            if t is None or t in occ: continue
            alts.append((dd, t, 1 if t in r1 else (2 if t in r2 else 0)))
        act = ''.join(last['act'].get('move', [])) or 'split'
        land = m.step(me, act[0]) if act != 'split' else me
        if act != 'split' and len(act) > 1:
            for c in act[1:]: land = m.step(land, c)
        lz = 1 if land in r1 else (2 if land in r2 else 0)
        loc_a = sum(1 for j, b in body.items() if j != vid and st['team'][j] == us and m.cheb(b[0], me) <= 3)
        loc_e = sum(1 for j, b in body.items() if st['team'][j] != us and m.cheb(b[0], me) <= 3)
        # corpse eats from this ram within 6 rounds
        ce = collections.Counter(e['team'] == us for e in S['eats'] if e['corpse'] and d['round'] <= e['round'] <= d['round'] + 6 and e['corpse'][0] in (vid, k))
        rows.append(dict(game=g['game'], opp=g['opp'], win=g['win'], round=d['round'], id=vid, L=d['len'], killer=k, klen=kl,
                         lastr=last['round'], act=act, me=me, kh=kh, land=land, zone=lz, alts=alts, safe_alt=any(z == 0 for _, _, z in alts),
                         loc_a=loc_a, loc_e=loc_e, ce_us=ce[True], ce_them=ce[False], later=k > vid))
        r = rows[-1]
        print('%d %-10s %s r%3d us%-3d L%d <- EN%-3d L%d | last r%d %s %s->%s zone%d killer@%s | alts %s | local %d/%d | corpse us/them %d/%d' % (
            r['game'], r['opp'][:10], 'W' if r['win'] else 'L', r['round'], vid, r['L'], k, kl, last['round'], act, me, land, lz, kh,
            ' '.join('%s%d' % (a, z) for a, _, z in alts), loc_a, loc_e, r['ce_us'], r['ce_them']), flush=True)
n = len(rows)
forced = sum(1 for r in rows if not r['safe_alt'])
chose = [r for r in rows if r['safe_alt'] and r['zone'] > 0]
print('victims', n, '| forced (no out-of-reach landing)', forced, '| chose into reach with a safe alt', len(chose),
      '(zone1 %d, zone2 %d)' % (sum(r['zone'] == 1 for r in chose), sum(r['zone'] == 2 for r in chose)),
      '| other (zone0: killer moved/sprinted further or we split)', sum(1 for r in rows if r['safe_alt'] and r['zone'] == 0))
print('corpse pearls eaten within 6 rounds us/them: %d/%d' % (sum(r['ce_us'] for r in rows), sum(r['ce_them'] for r in rows)))
print('local heads (allies/enemies): behind %d even %d ahead %d' % (sum(r['loc_a'] < r['loc_e'] for r in rows), sum(r['loc_a'] == r['loc_e'] for r in rows), sum(r['loc_a'] > r['loc_e'] for r in rows)))
pickle.dump(rows, open(os.path.join(HERE, 'victims_%s.pkl' % (want or 'all')), 'wb'))
