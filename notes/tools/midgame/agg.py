import pickle, collections, statistics as st, sys
res = pickle.load(open('metrics.pkl', 'rb'))
MAPS = set(sys.argv[1].split(',')) if len(sys.argv) > 1 and sys.argv[1] else {'Default', 'Autarky', 'Devil', 'Trophy', 'Prisoners Dilemma'}
G = collections.defaultdict(list)
for r in res:
    if r['map'] in MAPS: G[r['grp']].append(r)
grps = ['top', 'topopp', 'us', 'usopp']
print({g: len(G[g]) for g in grps}, 'win%', {g: round(sum(r['win'] for r in G[g]) / max(1, len(G[g])), 2) for g in grps})
def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 3) if xs else None
def row(k, f=None):
    print(f'{k:22s}', *[f'{str(med([(f(r) if f else r.get(k)) for r in G[g]])):>9s}' for g in grps])
print(f'{"":22s}', *[f'{g:>9s}' for g in grps])
for r_ in (100, 150, 200, 250, 300, 350):
    for k in ('n', 'tot', 'max', 'med', 'le3_', '4to6_', 'ge7_'):
        row(f'{k}{r_}')
for k in ('splits', 'own_nn_med', 'own_nn_le2', 'own_nn_le4', 'en_nn_med', 'en_nn_le3', 'turns', 'steps', 'eats', 'eats_spawn', 'eats_owncorpse', 'eats_encorpse', 'eats_per_turn', 'steps_per_eat', 'contested', 'contested_spawn', 'eat_share', 'spawn_share',
          'encorpse_drops', 'encorpse_byT', 'encorpse_byE', 'owncorpse_drops', 'owncorpse_byT', 'owncorpse_byE', 'h2h_lost', 'kills', 'en_deaths', 'sprint_frac', 'sprints', 'sprint_ate', 'sprint_kill', 'sprint_died', 'sprint_flee', 'deg1', 'deg2', 'map_deg12', 'nearfast', 'map_nearfast', 'nfast'):
    row(k)
def pool(key, g):
    out = []
    for r in G[g]: out += r[key]
    return out
print('--- split L by phase (pooled): median, hist')
for a in (60, 150, 250):
    for g in grps:
        L = pool(f'splitL_{a}', g); K = pool(f'splitK_{a}', g); En = pool(f'splitEn_{a}', g)
        c = collections.Counter(min(x, 10) for x in L)
        print(a, g, len(L), 'L', dict(sorted(c.items())), 'k', dict(sorted(collections.Counter(min(x, 6) for x in K).items())), 'enemy<=3', round(sum(1 for x in En if x <= 3) / max(1, len(En)), 2))
print('--- corpse delay (own-team eats of enemy corpses), pooled median/p75')
for g in grps:
    d = sorted(pool('encorpse_delayT', g)); dd = sorted(pool('owncorpse_delayT', g))
    print(g, 'enemy corpses eaten', len(d), 'med', med(d), 'p75', d[int(.75 * len(d))] if d else None, '| own corpses eaten', len(dd), 'med', med(dd))
    dr = sum(r['encorpse_drops'] for r in G[g]); bt = sum(r['encorpse_byT'] for r in G[g]); be = sum(r['encorpse_byE'] for r in G[g])
    dr2 = sum(r['owncorpse_drops'] for r in G[g]); bt2 = sum(r['owncorpse_byT'] for r in G[g]); be2 = sum(r['owncorpse_byE'] for r in G[g])
    print('   enemy drops', dr, 'eaten by us', round(bt / max(1, dr), 2), 'by them', round(be / max(1, dr), 2), '| own drops', dr2, 'eaten by us', round(bt2 / max(1, dr2), 2), 'by them', round(be2 / max(1, dr2), 2))
print('--- deaths by reason (sum per game)')
for g in grps:
    c = collections.Counter()
    for r in G[g]: c.update(r['deaths'])
    n = len(G[g]); print(g, {k: round(v / n, 1) for k, v in c.most_common()})
    dl = pool('death_len', g); print('   death len hist', dict(sorted(collections.Counter(min(x, 8) for x in dl).items())))
print('--- small (L<=4) dragon encounters with enemy head <=3 (per game)')
for g in grps:
    c = collections.Counter()
    for r in G[g]: c.update(r['enc'])
    n = len(G[g]); tot = sum(c[k] for k in ('app', 'flee', 'hold', 'ram', 'enemy_gone'))
    print(g, 'tot/game', round(tot / n, 1), {k: round(c[k] / max(1, tot), 3) for k in ('app', 'hold', 'flee', 'ram', 'enemy_gone')},
          'died5|', {k: round(c[k + '_died5'] / max(1, c[k]), 3) for k in ('app', 'hold', 'flee', 'ram')},
          'vs bigger', {k: c['vbig_' + k] for k in ('app', 'hold', 'flee', 'ram')}, 'vs smaller', {k: c['vsm_' + k] for k in ('app', 'hold', 'flee', 'ram')})
print('--- local odds (enemy heads within 4 vs own incl self)')
for g in grps:
    c = collections.Counter()
    for r in G[g]: c.update(r['outn'])
    print(g, {k: (c[k], round(c[k + '_dead5'] / max(1, c[k]), 3), 'away', round(c[k + '_away'] / max(1, c[k]), 2), 'closer', round(c[k + '_closer'] / max(1, c[k]), 2)) for k in ('out', 'even', 'up')})
print('--- sprint length/steps; eat length hist')
for g in grps:
    print(g, 'sprinter len', dict(sorted(collections.Counter(min(x, 8) for x in pool('sprint_len', g)).items())), 'steps', dict(sorted(collections.Counter(pool('sprint_steps', g)).items())))
    c = collections.Counter()
    for r in G[g]: c.update(r['eat_len'])
    print('   eater len', dict(sorted(c.items())))
    c = collections.Counter()
    for r in G[g]: c.update(r['maxlen_hist'])
    print('   max len reached r60-350 per dragon', dict(sorted(c.items())))
