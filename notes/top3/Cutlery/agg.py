"""Aggregate metrics.pkl into comparison tables. Usage: python3 notes/top3/Cutlery/agg.py [section ...]
Sections: win tl open eats splits moves deaths rams king end map"""
import os, sys, pickle, statistics as st, collections
H = os.path.dirname(os.path.abspath(__file__))
D = pickle.load(open(os.path.join(H, 'metrics.pkl'), 'rb'))
for x in D:
    if x['grp'] == 'cut': x['grp'] = 'cut-' + x['kind']
GR = ['cut-strong', 'cut-peer', 'cutopp', 'cutvus', 'usC', 'us', 'usopp', 'us31']
G = collections.defaultdict(list)
for x in D: G[x['grp']].append(x)
PHN = ['r0-60', 'r61-200', 'r201-350', 'r351-500']


def mean(v):
    v = [a for a in v if a is not None]
    return st.mean(v) if v else float('nan')


def f(v, p=1): return f'{v:.{p}f}'


def row(name, vals, w=11): print(f'{name:<12}' + ''.join(f'{v:>{w}}' for v in vals))


def phs(x, key, sub, p):
    return x.get(key, {}).get(sub, [0, 0, 0, 0])[p]


secs = sys.argv[1:] or ['win', 'tl', 'open', 'eats', 'splits', 'moves', 'deaths', 'rams', 'king', 'end', 'map']
if 'win' in secs:
    print('== games / winrate / round-limit share')
    for g in GR:
        L = G[g]
        if not L: continue
        print(f'{g:<12} n={len(L):3d} win={mean([x["win"] for x in L]):.2f} roundLimit={mean([x["end"]=="roundLimit" for x in L]):.2f} '
              f'res_long={mean([x["res_long"] for x in L]):.1f} opp_long={mean([x["opp_long"] for x in L]):.1f} maps={len({x["map"] for x in L})}')
if 'tl' in secs:
    print('\n== timeline units / total / longest (eliminated=0)')
    rs = (30, 50, 100, 200, 300, 400, 450, 500)
    row('group', [f'r{r}' for r in rs], 14)
    for g in GR:
        L = G[g]
        if L: row(g, [f"{mean([x[f'n{r}'] for x in L]):.0f}/{mean([x[f'tot{r}'] for x in L]):.0f}/{mean([x[f'max{r}'] for x in L]):.1f}" for r in rs], 14)
    print('-- second longest / small(<=3) units')
    for g in GR:
        L = G[g]
        if L: row(g, [f"{mean([x[f'sec{r}'] for x in L]):.1f}/{mean([x[f'small{r}'] for x in L]):.0f}" for r in rs], 14)
if 'open' in secs:
    print('\n== opening (r0-60)')
    row('group', ['r0split', 'first>0', 'splits60', 'k2%60', 'splitL60', 'nn30', 'nn60', 'cells60', 'visit60', 'tot60'])
    for g in GR:
        L = G[g]
        if not L: continue
        k2 = sum(x['ks60'].get(2, 0) for x in L) / max(1, sum(sum(x['ks60'].values()) for x in L))
        row(g, [f(mean([x['split_r0'] for x in L])), f(mean([x['first_split'] for x in L])), f(mean([phs(x, 'splits', 'all', 0) for x in L])), f(k2, 2),
                f(mean([x['splitL60'] for x in L])), f(mean([x['nn30'] for x in L])), f(mean([x['nn60'] for x in L])), f(mean([x['cells60'] for x in L])),
                f(mean([x['visit60'] for x in L]), 3), f(mean([x['tot60'] for x in L]))])
if 'eats' in secs:
    print('\n== eats per game by phase: spawn / own-corpse / enemy-corpse / pocket-spawn  [spawn per 100 head-rounds]')
    row('group', PHN, 26)
    for g in GR:
        L = G[g]
        if not L: continue
        row(g, [f"{mean([phs(x,'eats','spawn',p) for x in L]):.0f}/{mean([phs(x,'eats','own',p) for x in L]):.0f}/{mean([phs(x,'eats','enemy',p) for x in L]):.0f}/{mean([phs(x,'eats','pocket',p) for x in L]):.0f} [{100*sum(phs(x,'eats','spawn',p) for x in L)/max(1,sum(x['hr'][p] for x in L)):.1f}]" for p in range(4)], 26)
    print('-- total eats per 100 head-rounds (all sources); drops: own pearls dropped / enemy pearls dropped; share of all corpse pearls on board eaten by us')
    for g in GR:
        L = G[g]
        if not L: continue
        tot = [sum(phs(x, 'eats', s, p) for s in ('spawn', 'own', 'enemy') for x in L) for p in range(4)]
        hr = [sum(x['hr'][p] for x in L) for p in range(4)]
        dT = mean([x['drop']['T'] for x in L]); dE = mean([x['drop']['E'] for x in L])
        own = mean([sum(x['eats'].get('own', [0] * 4)) for x in L]); en = mean([sum(x['eats'].get('enemy', [0] * 4)) for x in L])
        print(f'{g:<12}', ' '.join(f'{100*t/max(1,h):5.1f}' for t, h in zip(tot, hr)), f'  drops own {dT:.0f} enemy {dE:.0f}; eaten own {own:.0f} ({own/max(1,dT):.2f}) enemy {en:.0f} ({en/max(1,dE):.2f})')
if 'splits' in secs:
    print('\n== splits per game by phase: all / k2 / tight(<=1 exit) / tip(parent left L2, k>2) / big(L>=10)')
    row('group', PHN, 22)
    for g in GR:
        L = G[g]
        if L: row(g, ['/'.join(f"{mean([phs(x,'splits',s,p) for x in L]):.0f}" for s in ('all', 'k2', 'tight', 'tip', 'big')) for p in range(4)], 22)
if 'moves' in secs:
    print('\n== moves: sprints / sprint-kill / sprint-big(L>=8) / portal crossings / portal deaths / suicides')
    row('group', PHN, 22)
    for g in GR:
        L = G[g]
        if L: row(g, ['/'.join(f"{mean([phs(x,'mv',s,p) for x in L]):.0f}" for s in ('sprint', 'sprint_kill', 'sprint_big', 'portal', 'portal_die', 'suicide')) for p in range(4)], 22)
if 'deaths' in secs:
    print('\n== deaths per game by phase: all / H2H / HitSelf / Wall / NVA / BodyEnemy / BodyAlly ; length lost')
    row('group', PHN, 30)
    for g in GR:
        L = G[g]
        if L: row(g, ['/'.join(f"{mean([phs(x,'deaths',s,p) for x in L]):.0f}" for s in ('all', 'HitHeadToHead', 'HitSelf', 'HitWall', 'NoValidAction', 'BodyEnemy', 'BodyAlly')) + f" L{mean([phs(x,'dlen','all',p) for x in L]):.0f}" for p in range(4)], 30)
    print('-- enemies killed on our bodies (block kills) per phase')
    for g in GR:
        L = G[g]
        if L: row(g, [f"{mean([phs(x,'kills','block',p) for x in L]):.1f}" for p in range(4)])
if 'rams' in secs:
    print('\n== head-on rams (enemy vs enemy only). by=T: we moved into their head')
    print('group        n_init n_recv  initL  vicL(init) init_big_vic(>=8)  own/en heads<=6 at init   at recv   init-sprint%')
    for g in GR:
        L = G[g]
        if not L: continue
        I = [r for x in L for r in x['rams'] if not r['same'] and r['by'] == 'T']
        Rv = [r for x in L for r in x['rams'] if not r['same'] and r['by'] == 'E']
        n = len(L)
        print(f"{g:<12} {len(I)/n:6.1f} {len(Rv)/n:6.1f}  {mean([r['mover_len'] for r in I]):5.1f}  {mean([r['victim_len'] for r in I]):5.1f}  "
              f"{mean([r['victim_len']>=8 for r in I]):6.2f}          {mean([r['own'] for r in I]):.1f}/{mean([r['en'] for r in I]):.1f}   "
              f"{mean([r['own'] for r in Rv]):.1f}/{mean([r['en'] for r in Rv]):.1f}  {mean([(r['steps'] or 1)>=2 for r in I]):.2f}")
    print('-- rams by phase (init/recv), and big-victim rams we suffered (victim=our L>=8)')
    for g in GR:
        L = G[g]
        if not L: continue
        a = [[0, 0] for _ in range(4)]; big = [0] * 4
        for x in L:
            for r in x['rams']:
                if r['same']: continue
                p = [i for i, (lo, hi) in enumerate(((0, 60), (61, 200), (201, 350), (351, 500))) if lo <= r['round'] <= hi][0]
                a[p][0 if r['by'] == 'T' else 1] += 1
                if r['by'] == 'E' and r['victim_len'] >= 8: big[p] += 1
        row(g, [f"{a[p][0]/len(L):.1f}/{a[p][1]/len(L):.1f} b{big[p]/len(L):.1f}" for p in range(4)], 16)
    print('-- same-team head-ons per game')
    for g in GR:
        L = G[g]
        if L: print(f"{g:<12} {mean([sum(1 for r in x['rams'] if r['same']) for x in L]):.1f}")
if 'king' in secs:
    print('\n== king: round first >=10/20/30, longest r300/400/450/500, 2nd at 500, king switches (L>=8), king deaths, king eats own-corpse per phase, feed NVA r351+')
    for g in GR:
        L = G[g]
        if not L: continue
        print(f"{g:<12} k10 {mean([x['king10'] for x in L]):5.0f} k20 {mean([x['king20'] for x in L]):5.0f} k30 {mean([x['king30'] for x in L]):5.0f} "
              f"| {mean([x['max300'] for x in L]):4.1f} {mean([x['max400'] for x in L]):4.1f} {mean([x['max450'] for x in L]):4.1f} {mean([x['max500'] for x in L]):4.1f} sec500 {mean([x['sec500'] for x in L]):4.1f} "
              f"| sw {mean([x['king_switch'] for x in L]):4.1f} kd {mean([x['king_deaths'] for x in L]):.2f} "
              f"| kingown {'/'.join(f'{mean([phs(x,chr(101)+chr(97)+chr(116)+chr(115),chr(107)+chr(105)+chr(110)+chr(103)+chr(111)+chr(119)+chr(110),p) for x in L]):.1f}' for p in range(4))} "
              f"kingall {'/'.join(f'{mean([phs(x,chr(101)+chr(97)+chr(116)+chr(115),chr(107)+chr(105)+chr(110)+chr(103),p) for x in L]):.1f}' for p in range(4))} "
              f"| feedNVA {mean([phs(x,'deaths','feedNVA',3) for x in L]):.1f} susp {mean([phs(x,'mv','suicide',3) for x in L]):.1f}")
    print('-- share of games where king reached 20 before r300 / r400; frac of total in king at r500')
    for g in GR:
        L = G[g]
        if L: print(f"{g:<12} {mean([(x['king20'] or 999)<300 for x in L]):.2f} {mean([(x['king20'] or 999)<400 for x in L]):.2f} {mean([x['max500']/x['tot500'] if x['tot500'] else 0 for x in L]):.2f}")
if 'end' in secs:
    print('\n== endgame r400-499: enemy heads within 6 of our king (mean), own heads within 6 of our king')
    for g in GR:
        L = G[g]
        if L: print(f"{g:<12} {mean([x['end_en_near'] for x in L]):.2f} {mean([x['end_own_near'] for x in L]):.2f}")
if 'map' in secs:
    print('\n== per map: win / r100 n/tot / r200 n/tot / r400 max / r500 max  (cut = all Cutlery games; us = us+usC)')
    maps = sorted({x['map'] for x in D})
    for mp in maps:
        for g, grps in (('cut', ('cut-strong', 'cut-peer')), ('cutopp', ('cutopp',)), ('us', ('us', 'usC', 'us31')), ('usopp', ('usopp', 'cutvus'))):
            L = [x for x in D if x['grp'] in grps and x['map'] == mp]
            if not L: continue
            print(f"{mp[:14]:<15}{g:<7} n={len(L):2d} win {mean([x['win'] for x in L]):.2f}  r100 {mean([x['n100'] for x in L]):3.0f}/{mean([x['tot100'] for x in L]):4.0f}  r200 {mean([x['n200'] for x in L]):3.0f}/{mean([x['tot200'] for x in L]):4.0f}  "
                  f"r300max {mean([x['max300'] for x in L]):4.1f} r400max {mean([x['max400'] for x in L]):4.1f}  r500 {mean([x['max500'] for x in L]):4.1f}/{mean([x['tot500'] for x in L]):4.0f}  k20 {mean([x['king20'] for x in L]):4.0f}")
