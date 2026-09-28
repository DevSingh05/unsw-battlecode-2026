"""Aggregate tactics stats over downloaded top-team replays.
Usage: python3 analyze_top.py ../replays  [> out.txt]
Needs ../replays/index.json from fetch_replays.py (team names per match id)."""
import sys, os, glob, json, pickle, collections, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
from replay_sim import simulate

RD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '../replays')
idx = {m['id']: m for m in json.load(open(os.path.join(RD, 'index.json')))}
C = collections.Counter; DD = collections.defaultdict


def q(xs, ps=(10, 25, 50, 75, 90)):
    xs = sorted(xs)
    if not xs: return '-'
    return '/'.join(str(xs[min(len(xs) - 1, int(p / 100 * len(xs)))]) for p in ps) + f' (n={len(xs)})'


games = []
for f in sorted(glob.glob(os.path.join(RD, '*.replay'))):
    mid = int(os.path.basename(f).split('.')[0])
    pk = f + '.sim.pkl'
    if os.path.exists(pk) and os.path.getmtime(pk) > os.path.getmtime(os.path.join(os.path.dirname(__file__), 'replay_sim.py')):
        g = pickle.load(open(pk, 'rb'))
    else:
        g = simulate(f); pickle.dump(g, open(pk, 'wb'))
    meta = idx[mid]
    g['id'] = mid; g['names'] = {'A': meta['a']['name'], 'B': meta['b']['name']}
    g['cache'] = f
    games.append(g)

out = []
P = lambda *a: out.append(' '.join(str(x) for x in a))

# ---------------- per-map summary
P('# PER-GAME SUMMARY')
P('id map rounds end winner winnerName | A max/total/n | B max/total/n | units@50,100,200,300,400,end (A;B)')
for g in games:
    r = g['result']; w = r['winner']
    snaps = dict(g['rounds'])
    def u(T): return ','.join(str(snaps[x][T]['n']) if x in snaps else '-' for x in (50, 100, 200, 300, 400, g['last_round']))
    P(g['id'], g['map'].name, g['last_round'] + 1, r['endReason'], w, g['names'].get(w, 'draw') if w else 'draw', '|',
      f"{r['A']['longest']}/{r['A']['total']}/{r['A']['dragonCount']}", '|', f"{r['B']['longest']}/{r['B']['total']}/{r['B']['dragonCount']}",
      '|', u('A'), ';', u('B'), '|', g['names']['A'], 'vs', g['names']['B'])

# ---------------- splits
P('\n# SPLITS')
by = DD(list)
for g in games:
    for s in g['splits']:
        by[g['names'][s['team']]].append((g, s))
for name, ss in sorted(by.items(), key=lambda x: -len(x[1])):
    Lk = C((s['L'], s['k']) for g, s in ss)
    kk = C(s['k'] for g, s in ss)
    ratio = C('half' if s['k'] in (s['L'] // 2, (s['L'] + 1) // 2) else ('k=2' if s['k'] == 2 else ('L-2' if s['k'] == s['L'] - 2 else 'other')) for g, s in ss)
    P(f'## {name}: {len(ss)} splits in {len(set(g["id"] for g, s in ss))} games')
    P('  top (L,k):', Lk.most_common(12))
    P('  k dist:', sorted(kk.items())[:15], ' pattern:', dict(ratio))
    P('  parent L quantiles:', q([s['L'] for g, s in ss]), ' round quantiles:', q([s['round'] for g, s in ss]))
    P('  parent age at split:', q([s['parent_age'] for g, s in ss]))
# per game split timeline: first split, round to reach peak units, last split, peak units
P('\n## split timeline per game/team: first split rnd, #splits by r50/r100/r200, last split rnd, peak units(rnd)')
for g in games:
    for T in 'AB':
        ss = [s for s in g['splits'] if s['team'] == T]
        peak = max(((snap[T]['n'], -rn) for rn, snap in g['rounds']), default=(0, 0))
        hit64 = next((rn for rn, snap in g['rounds'] if snap[T]['n'] >= 64), None)
        P(' ', g['id'], g['map'].name[:12].ljust(12), g['names'][T][:12].ljust(12), 'first', ss[0]['round'] if ss else None,
          'n@50/100/200', sum(s['round'] < 50 for s in ss), sum(s['round'] < 100 for s in ss), sum(s['round'] < 200 for s in ss),
          'last', ss[-1]['round'] if ss else None, 'total', len(ss), 'peak', peak[0], '@', -peak[1], 'hit64', hit64)

# ---------------- moves / sprints
P('\n# MOVES / SPRINTS')
mv = DD(list)
for g in games:
    for a in g['moves']:
        if a.get('suicide'): continue
        mv[g['names'][a['team']]].append((g, a))
for name, ms in sorted(mv.items(), key=lambda x: -len(x[1])):
    n = len(ms); sp = [(g, a) for g, a in ms if a['steps'] > 1]
    P(f'## {name}: {n} moves, sprints {len(sp)} ({100*len(sp)/max(1,n):.2f}%) steps dist {sorted(C(a["steps"] for g,a in sp).items())}')
    if not sp: continue
    ne = [a['near_enemy_head'][0] if a['near_enemy_head'] else 99 for g, a in sp]
    P('   sprint: nearest enemy head manhattan quantiles', q(ne))
    P('   sprint outcomes: ate>=1', sum(a['ate'] > 0 for g, a in sp), ' ate>=2', sum(a['ate'] > 1 for g, a in sp),
      ' killed', sum(bool(a['killed']) for g, a in sp), ' died', C(a['died'] for g, a in sp if a['died']))
    P('   sprint len_before quantiles', q([a['len_before'] for g, a in sp]), ' round quantiles', q([a['round'] for g, a in sp]))
    # baseline for single moves
    ss = [a for g, a in ms if a['steps'] == 1]
    P('   single-step nearest enemy head quantiles', q([a['near_enemy_head'][0] if a['near_enemy_head'] else 99 for a in ss]))
    ex = [(g['id'], a['round'], a['len_before'], ''.join(a['act']['move']), a['ate'], a['near_enemy_head'], a['killed'], a['died']) for g, a in sp[:12]]
    for e in ex: P('     ex', e)

# ---------------- deaths
P('\n# DEATHS')
dd = DD(list)
for g in games:
    for d in g['deaths']:
        dd[g['names'][d['team']]].append((g, d))
for name, ds in sorted(dd.items(), key=lambda x: -len(x[1])):
    P(f'## {name}: {len(ds)} deaths, reasons {dict(C(d["reason"] for g,d in ds))}')
    P('   len quantiles', q([d['len'] for g, d in ds]))
    hb = [(g, d) for g, d in ds if d['reason'] == 'HitOtherBody' and d['hit']]
    P('   HitOtherBody into ally', sum(d['hit']['team'] == d['team'] for g, d in hb), 'into enemy', sum(d['hit']['team'] != d['team'] for g, d in hb))
    # h2h where this team was mover
    mover = [(g, d) for g, d in ds if d['reason'] == 'HitHeadToHead' and 'victim' in d]
    P('   H2H as mover:', len(mover), 'vs enemy', sum(d['victim_team'] != d['team'] for g, d in mover),
      ' mover len q', q([d['len'] for g, d in mover if d['victim_team'] != d['team']]),
      ' victim len q', q([d['victim_len'] for g, d in mover if d['victim_team'] != d['team']]))
    P('   H2H mover<victim', sum(d['len'] < d['victim_len'] for g, d in mover if d['victim_team'] != d['team']),
      'mover>victim', sum(d['len'] > d['victim_len'] for g, d in mover if d['victim_team'] != d['team']),
      'equal', sum(d['len'] == d['victim_len'] for g, d in mover if d['victim_team'] != d['team']))
    P('   H2H mover step (steps,failed)', C((d.get('steps'), d.get('step_failed')) for g, d in mover))

# kills by team: enemy deaths caused
P('\n## Kill attribution (enemy deaths): body-block = enemy HitOtherBody into our body; h2h by us moving; enemy walks into us h2h')
kc = DD(C)
for g in games:
    for d in g['deaths']:
        me = g['names'][d['team']]
        if d['reason'] == 'HitOtherBody' and d['hit'] and d['hit']['team'] != d['team']:
            kc[g['names'][d['hit']['team']]]['bodyblock'] += 1
            kc[g['names'][d['hit']['team']]]['bodyblock_victimlen_sum'] += d['len']
        if d['reason'] == 'HitHeadToHead' and 'killer' in d and d.get('killer_team') != d['team']:
            kc[g['names'][d['killer_team']]]['h2h_initiated'] += 1
for k, v in kc.items(): P('  ', k, dict(v))

# ---------------- consolidation / king
P('\n# LATE GAME / KING')
for g in games:
    if g['result']['endReason'] != 'roundLimit': continue
    snaps = dict(g['rounds'])
    for T in 'AB':
        name = g['names'][T]
        final = snaps[g['last_round']][T]
        king = final['king']
        if king is None: continue
        # king length timeline
        tl = {r: len_ for r, len_ in []}
        kl = []
        # reconstruct king growth from eats
        keats = [e for e in g['eats'] if e['id'] == king]
        last_eat = keats[-1]['round'] if keats else None
        corpse_eats = [e for e in keats if e['corpse']]
        own_corpse = [e for e in corpse_eats if e['corpse'][1] == T]
        # self-inflicted deaths of own team near king in last 150 rounds
        sac = []
        for d in g['deaths']:
            if d['team'] != T or d['id'] == king or d['round'] < 300: continue
            enemy_caused = (d['reason'] == 'HitOtherBody' and d['hit'] and d['hit']['team'] != T) or \
                           (d['reason'] == 'HitHeadToHead' and (d.get('killer_team', T) != T or d.get('victim_team', T) != T))
            if enemy_caused: continue
            sac.append(d)
        P(f'{g["id"]} {g["map"].name[:14]:14} {name[:14]:14} {"WIN " if g["result"]["winner"]==T else "LOSS"} king={king} len={final["max"]} '
          f'2nd={final["lens"][1] if len(final["lens"])>1 else 0} n={final["n"]} king_eats={len(keats)} corpse_eats={len(corpse_eats)} own_corpse={len(own_corpse)} '
          f'last_eat_rnd={last_eat} own_nonenemy_deaths_after300={len(sac)} reasons={dict(C(d["reason"] for d in sac))}')
        if own_corpse:
            rs = [e['round'] for e in own_corpse]
            P('     own-corpse eats by king rounds q', q(rs), ' first', min(rs))

# ---------------- hot tiles
P('\n# HOT TILES (gap [1,1])')
for g in games:
    hot = {t for t, gp in g['map'].tiles.items() if gp == (1, 1)}
    if not hot: continue
    c = C(); cr = DD(list)
    for e in g['eats']:
        if e['tile'] in hot and not e['corpse']:
            c[e['team']] += 1; cr[e['team']].append(e['round'])
    tot = C(e['team'] for e in g['eats'] if not e['corpse'])
    P(g['id'], g['map'].name[:14].ljust(14), 'hot tiles', len(hot), '| eats on hot A', c['A'], f"({100*c['A']/max(1,tot['A']):.0f}% of A spawn-eats)", 'B', c['B'],
      f"({100*c['B']/max(1,tot['B']):.0f}%)", '| possible ~', len(hot) * (g['last_round'] + 1), '| A', g['names']['A'][:10], 'B', g['names']['B'][:10], 'winner', g['result']['winner'])

print('\n'.join(out))
