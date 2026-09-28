#!/usr/bin/env python3
"""Schooltime fatal-crossing classification (notes/20), incl. an exact replay of v22's PORTAL_ECHO_GUARD=2
(bot/main.cpp readMessages(): heads = allyHead+enemyHead echoes over ALL rays of the previous turn,
bodies = ally+enemy echoes, zeroed when more rays than warn rays were sent; the exit is blocked if
heads>0, or bodies>0 and the ray path dies on kelp within PORTAL_ECHO_RANGE+1 steps past the exit;
skipped when the exit is in view).

usage (from project root): python3 notes/tools/schportal/classify.py [ab_v22_Schooltime] [-v]
"""
import collections
import pathlib
import pickle
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import load, fatal, hitclass, guard, NG_of, schD, yard, OPP  # noqa: E402

name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 'ab_v22_Schooltime'
VERB = '-v' in sys.argv
G, m = load(name)
NG = NG_of(G)


def pg(x):
    return f'{x / NG:5.1f}'


print(f'== {name}: {NG} games, layouts {collections.Counter(g["layout"] for g in G)}')
for us in (True, False):
    rs = [r for g in G for r in g['recs'] if r['us'] == us]
    turns = sum(g['turns'].get(g['side'] if us else ('B' if g['side'] == 'A' else 'A'), 0) for g in G)
    f = [r for r in rs if fatal(r)]
    sig = [r for r in rs if r['sighted']]
    print(f"{'us  ' if us else 'them'} crossings/g {pg(len(rs))}  fatal/g {pg(len(f))}  fatal% {100 * len(f) / max(1, len(rs)):4.1f}"
          f"  cross/100 turns {100 * len(rs) / max(1, turns):4.2f}  turns/g {turns / NG:.0f}  exit in view% {100 * len(sig) / max(1, len(rs)):4.1f}"
          f"  sprint-cross% {100 * sum(len(r['move']) > 1 for r in rs) / max(1, len(rs)):4.1f}")
    c = collections.Counter(hitclass(r) for r in f)
    print('   fatal by what was hit (/g):', ', '.join(f'{k} {v / NG:.1f}' for k, v in c.most_common()))
    pc = collections.Counter(); pf = collections.Counter()
    for r in rs:
        k = 'yard0/1' if r['pid'] in (0, 1) else 'maze'
        k += ' in' if yard(r['exit']) else (' out' if yard(r['ent']) else '')
        pc[k] += 1; pf[k] += fatal(r)
    print('   by portal:', ', '.join(f'{k} {pc[k] / NG:.1f}/g fatal {pf[k] / NG:.1f} ({100 * pf[k] / max(1, pc[k]):.0f}%)' for k in sorted(pc)))
    lay = collections.Counter(); layf = collections.Counter(); ng = collections.Counter(g['layout'] for g in G)
    for g in G:
        for r in g['recs']:
            if r['us'] == us:
                lay[g['layout']] += 1; layf[g['layout']] += fatal(r)
    print('   by layout:', ', '.join(f'{k}: {lay[k] / ng[k]:.0f} cross/g, {layf[k] / ng[k]:.1f} fatal/g' for k in sorted(ng)))

ours = [(g, r) for g in G for r in g['recs'] if r['us'] and fatal(r)]
print(f'\n== our fatal crossings: {len(ours)} ({len(ours) / NG:.1f}/g)')
A = collections.Counter(); B = collections.Counter(); C = collections.Counter(); D = collections.Counter()
E = collections.Counter(); GV = collections.Counter(); PR = collections.Counter(); SCH = collections.Counter()
rows = []
for g, r in ours:
    hc = hitclass(r)
    A[hc] += 1
    h = r['hit']; pv = r['prev']
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
    # (c) the blocker's own warn (v18 question), ally blockers only
    c = '-'
    if h is not None and h[0] != 'self' and h[2] == r['team']:
        j = h[0]
        ps = [p for p in g['pings'].get(j, []) if p['origin'] == r['exit'] and r['round'] - 12 <= p['round'] <= r['round']]
        pw = [p for p in ps if p['dir'] == OPP[r['dir']]]
        hh = [x for x in g['headhist'].get(j, []) if x[1] == r['exit'] and r['round'] - 12 <= x[0] <= r['round']]
        if not hh:
            c = 'blocker_head_never_on_exit'
        elif not pw:
            c = 'no_warn_sent'
        else:
            got = [p for p in pw if p['hitId'] == r['id']]
            if got:
                p = got[-1]
                ok = p['round'] < r['round'] or r['id'] > j
                memo = r['round'] < p['round'] + p['len'] + 1
                c = 'warn_hit_crosser(' + ('in_time' if ok else 'too_late') + (',memo_live' if memo else ',memo_expired') + ')'
            else:
                on_any = any(any(v[0] == r['id'] for v in q['occ_path'].values()) for q in pw)
                c = 'crosser_on_path_but_ray_stopped_earlier' if on_any else 'crosser_not_on_ray_line'
    elif h is not None and h[0] != 'self':
        c = 'enemy_blocker'
    else:
        c = 'self/none'
    C[c] += 1
    # (d) forced / chosen
    alts = r['alts']
    safe = [d for d, a in alts.items() if d != r['dir'] and a['st'] == 'free']
    if len(r['move']) > 1:
        dd = 'sprint(%d steps, portal at %d)' % (len(r['move']), r['k'] + 1)
    elif not safe:
        dd = 'forced(0 safe alternatives)'
    else:
        dd = 'chosen(%d safe alt)' % min(len(safe), 3)
    D[dd] += 1
    chase = 'pearl_on_exit' if r['exit_pearl'] else ('pearl<=3 beyond exit' if r['exit_pearls3'][0] > 0 else 'no pearl near exit')
    altp = max((alts[d]['pearls3'] for d in safe), default=0)
    E[(chase, 'alt_has_pearl<=3' if altp else 'alt_no_pearl')] += 1
    # guard replay
    v = guard(m, r)
    GV[v['why']] += 1
    PR[(v['why'].split(':')[0], v.get('ray', '-'))] += 1
    # Schooltime module: rush pull (8/step closer to the pool, r<90, L<=6, layout A)
    dD = schD(r['ent']) - schD(r['exit'])
    rushable = g['layout'] == 'A' and r['round'] < 90 and r['L'] <= 6 and dD > 0
    SCH[('yard portal' if r['pid'] in (0, 1) else 'maze portal',
         'into yard' if yard(r['exit']) else ('out of yard' if yard(r['ent']) else 'maze'),
         'r<90&L<=6&closer(rush-eligible)' if rushable else ('closer to pool' if dD > 0 else 'not closer'))] += 1
    rows.append((g['gid'], r['round'], r['id'], r['L'], hc, b, v['why'], dd, r['pid']))

for title, cnt in (('(a) what we hit', A), ('(b) exit at our previous turn [hitclass-prefix, state]', B),
                   ('(c) blocker warn geometry (ally blockers)', C), ('(d) forced / chosen', D), ('(d2) chasing', E),
                   ('(f) why PORTAL_ECHO_GUARD=2 did not block', GV), ('(f2) guard verdict x crossing-ray echo', PR),
                   ('(g) Schooltime module: portal / direction / rush eligibility', SCH)):
    print(f'\n{title}:')
    for k, v in cnt.most_common():
        print(f'   {str(k):86s} {v / NG:5.1f}/g  {100 * v / len(ours):5.1f}%')

print('\n(e) length / round of fatal crossers:')
L = collections.Counter(min(x[3], 10) for x in rows)
print('   L:', ', '.join(f'{k}{"+" if k == 10 else ""}: {v / NG:.1f}' for k, v in sorted(L.items())))
Rn = collections.Counter(min(x[1] // 50, 9) * 50 for x in rows)
print('   round:', ', '.join(f'{k}-: {v / NG:.1f}' for k, v in sorted(Rn.items())))
for x in rows:
    if x[3] >= 8:
        print('   L>=8:', x)
if VERB:
    for x in rows[:120]:
        print(x)
