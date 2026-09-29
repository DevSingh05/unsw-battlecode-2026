#!/usr/bin/env python3
"""Same mechanisms for top-10 games on Devil / Prisoners Dilemma (notes/replays/top10b + permap), per team role
(winner / loser, and top-10 team vs peer where known):
  - trapped-death lengths and the 'split at L4 then die at L3' pump pattern
  - rams initiated while locally outnumbered (Chebyshev 3) and the corpse harvest after each head-on
  - single steps of L<=5 dragons into 1-step / 2-step enemy reach, by local odds
    python3 notes/tools/devdil/top10.py"""
import os, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
from sim2 import simulate, Map
TOP10 = {306, 70, 264, 801, 20, 46, 91, 213, 249, 470}
REF = {'Devil': 'notes/maps/Devil__id13.map', 'Prisoners Dilemma': 'notes/maps/Prisoners_Dilemma__id17.map'}


def games():
    out = {}
    for d in ('top10b', 'permap'):
        f = os.path.join(ROOT, 'notes/replays', d, 'index.json')
        for x in json.load(open(f)):
            if x.get('mapName') in REF and x.get('winner') in ('a', 'b'):
                p = os.path.join(ROOT, 'notes/replays', d, '%d.replay' % x['id'])
                if os.path.exists(p): out[x['id']] = (p, x, d)
    return out


def reach(m, head, L, occ, Rr):
    Rr = min(Rr, max(1, L - 1)); seen = {head: 0}; fr = [head]; out = {}
    while fr:
        nf = []
        for t in fr:
            if seen[t] >= Rr: continue
            for d in 'NESW':
                v = m.step(t, d)
                if v is None or v in seen: continue
                seen[v] = seen[t] + 1; out[v] = seen[v]
                if v not in occ: nf.append(v)
        fr = nf
    return out


def team_letter(o, x, side):
    # replay team 'A' = map team 0; the index a/b are the API's players. Match via result longest/total is not
    # possible without summary; use botA/botB names if present.
    return None


seen_sig = set()
agg = collections.defaultdict(collections.Counter)
for gid, (p, x, src) in sorted(games().items()):
    o = R.load(p)
    sig = (o['result'].get('winner'), str(o['result']), x['mapName'])
    res = o['result']
    win = res.get('winner')  # 'A'/'B'
    if win not in ('A', 'B'): continue
    S = simulate(p); m = S['map']
    key_sig = (x['mapName'], tuple(sorted([x['a']['name'], x['b']['name']])), str(res))
    if key_sig in seen_sig: continue  # deterministic duplicates
    seen_sig.add(key_sig)
    M = x['mapName']
    agg[M]['games'] += 1
    role = lambda T: 'W' if T == win else 'L'
    ref = Map(open(os.path.join(ROOT, REF[M])).read())
    snaps = dict(S['rounds'])
    s100 = snaps.get(min(100, S['last_round']))
    for T in 'AB':
        agg[M][role(T) + '_units100'] += s100[T]['n'] if S['last_round'] >= 100 else 0
    for e in S['eats']:
        if ref.tiles.get(tuple(e['tile']), (0, 0)) == (1, 1) and not e['corpse']: agg[M][role(e['team']) + '_hot'] += 1
    # trapped deaths
    for d in S['deaths']:
        nb = d.get('nbrs', {})
        if d['reason'] in ('HitSelf', 'HitWall', 'HitOtherBody', 'NoValidAction') and not any(v in ('free', 'pearl') for v in nb.values()):
            agg[M][role(d['team']) + '_trapped'] += 1; agg[M][role(d['team']) + '_trappedlen'] += d['len']
            sp = [s for s in S['splits'] if s['parent'] == d['id'] and d['round'] - 6 <= s['round'] <= d['round']]
            ea = [e for e in S['eats'] if e['id'] == d['id'] and sp and e['round'] >= sp[-1]['round']]
            if d['len'] == 3 and sp and sp[-1]['L'] == 4 and len(ea) == 1: agg[M][role(d['team']) + '_L3pat'] += 1
    # head-on trades + harvest
    eaten = collections.defaultdict(collections.Counter)
    for e in S['eats']:
        if e['corpse']: eaten[e['corpse'][0]][e['team']] += 1
    for d in S['deaths']:
        if d['reason'] != 'HitHeadToHead' or 'victim' not in d or d['victim_team'] == d['team']: continue
        T = d['team']; st = simulate(p, stop=(d['round'], d['id']))
        if 'act' not in st: continue
        me = st['body'][d['id']][0]
        oth = sum(1 for j, b in st['body'].items() if j != d['id'] and st['team'][j] == T and m.cheb(b[0], me) <= 3)
        en = sum(1 for j, b in st['body'].items() if st['team'][j] != T and m.cheb(b[0], me) <= 3)
        ok = 'ok' if oth >= en else 'OUT'
        mine = eaten[d['id']][T] + eaten[d['victim']][T]; theirs = eaten[d['id']][d['victim_team']] + eaten[d['victim']][d['victim_team']]
        k = role(T) + '_ram_' + ok
        agg[M][k] += 1; agg[M][k + '_net'] += mine - theirs
    # step risk (single pass)
    body = {}; team = {}; alive = set()
    for i, (t, pts) in enumerate(m.dragons): body[i] = list(pts); team[i] = 'AB'[t]; alive.add(i)
    pending = {}; actor = None
    for e in o['events']:
        t = e['t']
        if t == 'turnStart': actor = e['id']
        elif t == 'dragonAction':
            i = e['id']; a = e['action'] or {}
            if i in pending: agg[M][pending.pop(i)] += 0
            if i not in alive or len(body[i]) > 5 or 'move' not in a or len(a['move']) != 1: continue
            occ = set()
            for j in alive: occ.update(body[j])
            me = body[i][0]; r1 = set(); r2 = set()
            for j in alive:
                if team[j] == team[i] or m.cheb(body[j][0], me) > 6: continue
                for v, dd in reach(m, body[j][0], len(body[j]), occ, 2).items(): (r1 if dd == 1 else r2).add(v)
            r2 -= r1
            al = sum(1 for j in alive if team[j] == team[i] and m.cheb(body[j][0], me) <= 3)
            en = sum(1 for j in alive if team[j] != team[i] and m.cheb(body[j][0], me) <= 3)
            if en == 0: continue
            odds = 'ahead' if al > en else 'notahead'
            dest = m.step(me, a['move'][0])
            zone = 'r1' if dest in r1 else ('r2' if dest in r2 else 'safe')
            k = '%s_step_%s_%s' % (role(team[i]), odds, zone)
            agg[M][k + '_n'] += 1; pending[i] = k
        elif t == 'dragonUpdate':
            i = e['id']; b = body[i]; b.insert(0, e['head'])
            while b and b[-1] != e['tail']: b.pop()
        elif t == 'dragonSplit':
            pp = e['parent']; c = e['child']
            body[pp] = list(e['parentBody']); body[c] = list(e['childBody']); team[c] = e['team']; alive.add(c)
        elif t == 'dragonDeath':
            i = e['id']
            if i in pending:
                k = pending.pop(i)
                if e['reason'] == 'HitHeadToHead' and actor != i and team.get(actor) != team[i]: agg[M][k + '_rammed'] += 1
            alive.discard(i)
for M, c in agg.items():
    n = c['games']
    print('==', M, n, 'unique top-10 games (winner W / loser L), per game')
    for r in 'WL':
        print('  %s units@100 %.1f  hot eats %.1f  trapped deaths %.1f (mean len %.2f, split@4->die@L3 pattern %.1f)' % (
            r, c[r + '_units100'] / n, c[r + '_hot'] / n, c[r + '_trapped'] / n, c[r + '_trappedlen'] / max(1, c[r + '_trapped']), c[r + '_L3pat'] / n))
        print('     rams initiated: locally ok %.1f (net corpse %+.2f/ram), locally outnumbered %.1f (net %+.2f/ram)' % (
            c[r + '_ram_ok'] / n, c[r + '_ram_ok_net'] / max(1, c[r + '_ram_ok']), c[r + '_ram_OUT'] / n, c[r + '_ram_OUT_net'] / max(1, c[r + '_ram_OUT'])))
        for odds in ('ahead', 'notahead'):
            print('     steps with enemy in view, %-8s' % odds + '  '.join('%s %d (rammed %.0f%%)' % (z, c['%s_step_%s_%s_n' % (r, odds, z)], 100 * c['%s_step_%s_%s_rammed' % (r, odds, z)] / max(1, c['%s_step_%s_%s_n' % (r, odds, z)])) for z in ('safe', 'r1', 'r2')))
