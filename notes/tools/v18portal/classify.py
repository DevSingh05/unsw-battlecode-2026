#!/usr/bin/env python3
"""Classify our fatal portal crossings and compare crossing behaviour us vs them.
usage (from project root): python3 notes/tools/v18portal/classify.py [ab_v18_Default] [-v]
"""
import collections
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 'ab_v18_Default'
VERB = '-v' in sys.argv
G = pickle.load(open(HERE / f'{name}.pkl', 'rb'))
NG = len(G)


def pg(x):
    return f'{x / NG:5.1f}'


def fatal(r):
    return r['died'] is not None and r['died_step'] == r['k']


def hitclass(r):
    h = r['hit']
    if h is None:
        return 'unknown:' + str(r['died'])
    j, seg, tm, L = h
    if j == 'self':
        return 'self'
    own = 'ally' if tm == r['team'] else 'enemy'
    if r['died'] == 'HitHeadToHead':
        return own + '_headon'
    return own + ('_neck' if seg == 1 else '_body')


# ---------------- overall crossing stats
print(f'== {name}: {NG} games')
for us in (True, False):
    rs = [r for G_ in G for r in G_['recs'] if r['us'] == us]
    turns = sum(g['turns'].get(g['side'] if us else ('B' if g['side'] == 'A' else 'A'), 0) for g in G)
    f = [r for r in rs if fatal(r)]
    sig = [r for r in rs if r['sighted']]
    print(f"{'us  ' if us else 'them'} crossings/g {pg(len(rs))}  fatal/g {pg(len(f))}  fatal% {100 * len(f) / max(1, len(rs)):4.1f}"
          f"  cross/100 turns {100 * len(rs) / max(1, turns):4.2f}  sighted% {100 * len(sig) / max(1, len(rs)):4.1f}"
          f"  fatal% sighted {100 * sum(fatal(r) for r in sig) / max(1, len(sig)):4.1f} blind {100 * sum(fatal(r) for r in rs if not r['sighted']) / max(1, len(rs) - len(sig)):4.1f}"
          f"  sprint-cross% {100 * sum(len(r['move']) > 1 for r in rs) / max(1, len(rs)):4.1f}")
    c = collections.Counter(hitclass(r) for r in f)
    print('   fatal by what was hit (/g):', ', '.join(f'{k} {v / NG:.1f}' for k, v in c.most_common()))
    # exit occupied at the moment of the move
    occ_now = sum(1 for r in rs if r['exit_occ'] is not None)
    print(f'   exit occupied at decision: {pg(occ_now)}/g ({100 * occ_now / max(1, len(rs)):.1f}% of crossings)')

# ---------------- our fatal crossings: detailed classification
ours = [(g, r) for g in G for r in g['recs'] if r['us'] and fatal(r)]
print(f'\n== our fatal crossings: {len(ours)} ({len(ours) / NG:.1f}/g)')
A = collections.Counter(); B = collections.Counter(); C = collections.Counter(); D = collections.Counter(); E = collections.Counter()
CX = collections.Counter()
rows = []
for g, r in ours:
    hc = hitclass(r)
    A[hc] += 1
    # (b) was the blocker on the exit at the crosser's previous turn?
    h = r['hit']
    pv = r['prev']
    if r['age'] == 0 or pv is None:
        b = 'no_prev_turn(newborn)'
    elif pv['round'] != r['round'] - 1:
        b = 'prev_turn_not_last_round'
    else:
        po = pv['occ']
        if po is None:
            b = 'exit_empty_prev'
        elif h is not None and h[0] != 'self' and po[0] == h[0]:
            b = 'same_blocker_seg%d_prev' % min(po[1], 2)
        elif h is not None and h[0] == 'self' and po[0] == r['id']:
            b = 'self_prev'
        else:
            b = 'other_dragon_prev'
    B[(hc.split('_')[0], b)] += 1
    # (c) warn geometry: pings from the blocker whose origin is the exit tile, in the last 12 rounds
    c = '-'
    if h is not None and h[0] != 'self' and h[2] == r['team']:
        j = h[0]
        ps = [p for p in g['pings'].get(j, []) if p['origin'] == r['exit'] and r['round'] - 12 <= p['round'] <= r['round']]
        # rays that went back through the portal (the warn rays)
        pw = [p for p in ps if p['dir'] == {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[r['dir']]]
        hh = [x for x in g['headhist'].get(j, []) if x[1] == r['exit'] and r['round'] - 12 <= x[0] <= r['round']]
        if not hh:
            c = 'blocker_head_never_on_exit(born/sprint-through)'
        elif not pw:
            c = 'no_warn_sent(' + ('sprint' if all(x[2] > 1 for x in hh) else 'other') + ')'
        else:
            got = [p for p in pw if p['hitId'] == r['id']]
            if got:
                p = got[-1]
                # delivered in time?  lower-id receiver reads next round
                ok = p['round'] < r['round'] or r['id'] > j
                memo = r['round'] < p['round'] + p['len']
                c = 'warn_hit_crosser(' + ('in_time' if ok else 'too_late') + (',memo_live' if memo else ',memo_expired') + ')'
            else:
                p = pw[-1]
                on_path = any(v[0] == r['id'] for v in p['occ_path'].values())
                # was the crosser anywhere on the geometric path at any warn?
                on_any = any(any(v[0] == r['id'] for v in q['occ_path'].values()) for q in pw)
                if on_any:
                    c = 'crosser_on_path_but_ray_stopped_earlier'
                else:
                    c = 'crosser_not_on_ray_line'
    elif h is not None and h[0] != 'self':
        c = 'enemy_blocker'
    else:
        c = 'self/none'
    C[c] += 1
    # (d) forced or chosen
    alts = r['alts']
    safe = [d for d, a in alts.items() if d != r['dir'] and a['st'] == 'free']
    safe_vis = [d for d in safe if not alts[d]['portal']]
    if len(r['move']) > 1:
        dd = 'sprint(%d steps, portal at %d)' % (len(r['move']), r['k'] + 1)
    elif not safe:
        dd = 'forced(0 safe alternatives)'
    elif not safe_vis:
        dd = 'only other portal moves'
    else:
        dd = 'chosen(%d safe alt)' % min(len(safe_vis), 3)
    D[dd] += 1
    chase = 'pearl_on_exit' if r['exit_pearl'] else ('pearl<=3 beyond exit' if r['exit_pearls3'][0] > 0 else 'no pearl near exit')
    altp = max((alts[d]['pearls3'] for d in safe), default=0)
    E[(chase, 'alt_has_pearl<=3' if altp else 'alt_no_pearl')] += 1
    CX[('enemy_head<=3' if r['en_d'] <= 3 else 'no_enemy<=3')] += 1
    rows.append((r['round'], r['L'], hc, b, c, dd, chase))

for title, cnt in (('(a) what we hit', A), ('(b) exit at our previous turn [hitclass-prefix, state]', B), ('(c) warn geometry (ally blockers)', C),
                   ('(d) forced / chosen', D), ('(d2) chasing', E), ('(d3) threat', CX)):
    print(f'\n{title}:')
    for k, v in cnt.most_common():
        print(f'   {str(k):70s} {v / NG:5.1f}/g  {100 * v / len(ours):5.1f}%')

# (e) length and round
print('\n(e) length / round of fatal crossers:')
L = collections.Counter(min(x[1], 10) for x in rows)
print('   L:', ', '.join(f'{k}{"+" if k == 10 else ""}: {v / NG:.1f}' for k, v in sorted(L.items())))
Rn = collections.Counter(min(x[0] // 50, 9) * 50 for x in rows)
print('   round:', ', '.join(f'{k}-: {v / NG:.1f}' for k, v in sorted(Rn.items())))
big = [x for x in rows if x[1] >= 8]
for x in big:
    print('   L>=8:', x)
if VERB:
    for x in rows[:80]:
        print(x)
