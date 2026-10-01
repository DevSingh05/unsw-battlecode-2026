"""Queen (dragon id 0/1) death analysis over local replays. usage: python3 qdeaths.py <replay dir>"""
import sys, os, glob, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'midgame'))
import sim2, replay_decode as R

def deg(m, p):  # non-kelp exits of a tile
    return sum(1 for d in 'NESW' if m.step(p, d) is not None)

def check_ids(path):
    o = R.load(path); m = sim2.Map(o['map'])
    for e in o['events']:
        if e['t'] == 'dragonUpdate' and e['id'] in (0, 1):
            pass
    # first update of id 0 must be adjacent to first DRAGON line head
    firsts = {}
    for e in o['events']:
        if e['t'] == 'dragonUpdate' and e['id'] not in firsts: firsts[e['id']] = e['head']
    ok = all(m.dist(firsts[i], m.dragons[i][1][0]) <= 1 for i in (0, 1) if i in firsts)
    return ok

rows = []
for p in sorted(glob.glob(os.path.join(sys.argv[1], 'v3*_s?.replay'))):
    tag = os.path.basename(p)[:-7]
    g = sim2.simulate(p); m = g['map']
    a, b, mp, s = tag.split('_')[0], tag.split('_')[1], '_'.join(tag.split('_')[2:-1]), tag.split('_')[-1]
    # queen max length and splits made by queen
    qmax = {0: 0, 1: 0}
    for r, snap in g['rounds']:
        for q in (0, 1):
            for T in 'AB':
                if q in snap[T]['ids']: qmax[q] = max(qmax[q], snap[T]['ids'][q])
    qsplits = collections.Counter(sp['parent'] for sp in g['splits'] if sp['parent'] in (0, 1))
    spawn = {i: m.dragons[i][1][0] for i in (0, 1)}
    # start: min dist from queen head to enemy heads
    sd = {i: min(m.dist(spawn[i], m.dragons[j][1][0]) for j in range(len(m.dragons)) if m.dragons[j][0] != m.dragons[i][0]) for i in (0, 1)}
    for d in g['deaths']:
        if d['id'] not in (0, 1): continue
        q = d['id']; bot = (a, b)[q]
        opp = ''
        if d['reason'] == 'HitHeadToHead':
            if 'killer' in d: opp = f"by {d['killer']}{'ally' if d['killer_team']==d['team'] else 'EN'}L{d['killer_len']}"
            elif 'victim' in d: opp = f"mover vs {d['victim']}{'ally' if d['victim_team']==d['team'] else 'EN'}L{d['victim_len']}"
        elif d['reason'] == 'HitOtherBody' and d['hit']:
            h = d['hit']; opp = f"into {'ally' if h['team']==d['team'] else 'EN'}{h['id']} seg{h['seg']}"
        nb = d['nbrs']; free = sum(1 for v in nb.values() if v in ('free', 'pearl'))
        kel = sum(1 for v in nb.values() if v == 'kelp')
        rows.append(dict(tag=tag, map=mp, seed=s, bot=bot, q=q, rnd=d['round'], reason=d['reason'], opp=opp, L=d['len'], qmax=qmax[q],
                         qsplits=qsplits[q], head=d['head'], fromspawn=m.dist(d['head'], spawn[q]), tdeg=deg(m, d['head']),
                         kelpnb=kel, freenb=free, enemy=d.get('enemy_near'), ally=d.get('ally_near'), startd=sd[q], idok=check_ids(p)))
    surv = [q for q in (0, 1) if q not in [d['id'] for d in g['deaths']]]
    for q in surv:
        rows.append(dict(tag=tag, map=mp, seed=s, bot=(a, b)[q], q=q, rnd=None, reason='SURVIVED', opp='', L=len(g['body'][q]), qmax=qmax[q], qsplits=qsplits[q],
                         head=g['body'][q][0], fromspawn=None, tdeg=None, kelpnb=None, freenb=None, enemy=None, ally=None, startd=sd[q], idok=check_ids(p)))
for r in rows:
    print(f"{r['tag']:26} q{r['q']} {r['bot']:4} r{str(r['rnd']):4} {r['reason']:14} {r['opp']:22} L{r['L']:<3} max{r['qmax']:<3} spl{r['qsplits']:<2} "
          f"head{r['head']} dSpawn{r['fromspawn']} tdeg{r['tdeg']} kelpNb{r['kelpnb']} freeNb{r['freenb']} en{r['enemy']} al{r['ally']} startEn{r['startd']} id{r['idok']}")
