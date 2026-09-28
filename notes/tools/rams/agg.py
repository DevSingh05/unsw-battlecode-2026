#!/usr/bin/env python3
"""Aggregate notes/tools/rams/rams.pkl (built by rams.py): why our threat model let each ram happen.
    python3 notes/tools/rams/agg.py [-v]
"""
import collections, os, pickle, sys
D = pickle.load(open(os.path.join(os.path.dirname(__file__), 'rams.pkl'), 'rb'))
rams = D['rams']; V = '-v' in sys.argv


def classify(r):
    ch = next((o for o in r['opts'] if o['d'] == r['chosen']), None)
    alts = [o for o in r['opts'] if o.get('legal') == 'ok' and o['d'] != r['chosen']]
    moves = [o for o in alts if o['d'] in 'NESW']
    r['alt_safe_room_sprint'] = [o['d'] for o in alts if o['d'].startswith('SPR') and o['safe'] and o['room']]
    r['alt_safe_room_split'] = [o['d'] for o in alts if o['d'] in ('SPLIT2', 'RSPLIT') and o['safe'] and o['room']]
    r['alt_safe_room'] = [o['d'] for o in alts if o['safe'] and o['room']]
    r['alt_safe_room_move'] = [o['d'] for o in moves if o['safe'] and o['room']]
    r['alt_safe_any'] = [o['d'] for o in alts if o['safe']]
    r['alt_botsafe_room'] = [o['d'] for o in alts if not o['bot_threat'] and o['room']]
    if not r['killer_exists']:
        return 'newborn_killer'
    if ch is None:
        return 'chosen_unknown(%s)' % r['chosen']
    kthr = [x for x in ch.get('threats', []) if x[0] == r['killer']]
    r['k_need'] = kthr[0][2] if kthr else None
    r['alt_botsafe_room_move'] = [o['d'] for o in moves if not o['bot_threat'] and o['room']]
    r['alt_botsafe_move'] = [o['d'] for o in moves if not o['bot_threat']]
    if ch['bot_threat']:
        if r['alt_botsafe_room_move']: return 'seen:botsafe_move_existed'
        if r['alt_botsafe_move']: return 'seen:botsafe_move_noroom'
        return 'seen:all_moves_threatened'
    if not kthr:
        return 'model_miss'
    if not r.get('k_vis_head'):
        if ch['t'] != None and r.get('our_portal'): return 'unseen_head:we_crossed_portal'
        if r.get('killer_portal'): return 'unseen_head:killer_crossed_portal'
        if r.get('k_vislen', 0) > 0: return 'unseen_head:body_visible'
        return 'unseen_head:out_of_view'
    need = kthr[0][2]
    if need > 4:
        return 'reach_cap'
    if need > max(1, r['k_vislen'] - 1):
        return 'len_underestimate'
    return 'bfs_mismatch'


cats = collections.Counter(); bymap = collections.defaultdict(collections.Counter)
fix = collections.Counter(); rows = collections.defaultdict(list)
for r in rams:
    c = classify(r); r['cat'] = c
    cats[c] += 1; bymap[r['map']][c] += 1; rows[c].append(r)
    fix[(c, 'safe+room alt' if r['alt_safe_room'] else ('safe alt (no room)' if r['alt_safe_any'] else 'no safe alt'))] += 1
n = len(rams); ng = sum(D['ngames'].values())
print('rams of our L>=8 by enemy:', n, 'in', ng, 'games (%.2f/g)' % (n / ng), 'per map', D['ngames'])
for c, k in cats.most_common(): print('  %-20s %3d  %s' % (c, k, {m: v[c] for m, v in bymap.items() if v[c]}))
print('\nwith alternatives:')
for (c, a), k in sorted(fix.items()): print('  %-20s %-20s %3d' % (c, a, k))

# killer stats
kl = collections.Counter(min(r['killer_len'] or 0, 9) for r in rams)
print('\nkiller len', sorted(kl.items()))
print('killer acted before us (lower id):', sum(r['killer_before_us'] for r in rams), '/ same round as our move:', sum(r['same_round'] for r in rams))
print('killer crossed portal on ram:', sum(bool(r.get('killer_portal')) for r in rams))
print('killer steps', collections.Counter(len(r['killer_move'] or '') for r in rams))
print('cheb dist killer head at R0', sorted(collections.Counter(r.get('k_cheb') for r in rams).items(), key=lambda x: (x[0] is None, x[0] or 0)))
print('our len', sorted(collections.Counter(min(r['len'], 20) for r in rams).items()))
print('round', sorted(collections.Counter(r['round'] // 50 * 50 for r in rams).items()))
print('our action kind', collections.Counter(r['our_act_kind'] for r in rams), 'units<=3:', sum(r['units'] <= 3 for r in rams))
print('win/loss', collections.Counter(r['win'] for r in rams))
for c in cats:
    print('\n==', c)
    for r in rows[c][: (99 if V else 6)]:
        ch = next((o for o in r['opts'] if o['d'] == r['chosen']), {})
        print('  %s %d %-9s r%d L%d id%d | k id%s L%s(vis %s) cheb%s mv=%s P%d need=%s | chose %s bot%s | safe+room alts %s botsafe %s units %d' % (
            r['src'], r['game'], r['map'][:9], r['round'], r['len'], r['id'], r['killer'], r['killer_len'], r.get('k_vislen'),
            r.get('k_cheb'), r['killer_move'], bool(r.get('killer_portal')), r.get('k_need'), r['chosen'], ch.get('bot_threat'),
            r['alt_safe_room'], r['alt_botsafe_room'], r['units']))
