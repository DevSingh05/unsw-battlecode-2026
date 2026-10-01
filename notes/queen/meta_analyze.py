"""Queen-rule meta analysis of public replays. Usage: python3 meta_analyze.py games.json replay_dir id1 id2 ..."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'midgame'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import sim2

def n(x): return x.get('name') if isinstance(x, dict) else x

def analyze(path, meta):
    g = sim2.simulate(path); m = g['map']
    # queen ids: 0 and 1, team from map order
    q = {g['team'][0]: 0, g['team'][1]: 1}
    names = {'A': n(meta['a']), 'B': n(meta['b'])}
    out = {'map': m.name, 'end': g['last_round'], 'reason': g['result'].get('endReason'), 'winner': g['result'].get('winner'), 'res': g['result']}
    spawn = {T: m.dragons[q[T]][1][0] for T in 'AB'}
    for T in 'AB':
        qi = q[T]; E = 'B' if T == 'A' else 'A'
        r = {'name': names[T]}
        d = [x for x in g['deaths'] if x['id'] == qi]
        if d:
            x = d[0]; cause = x['reason']; by = None
            if x['reason'] == 'HitHeadToHead': by = x.get('killer_team') or x.get('victim_team')
            elif x['reason'] == 'HitOtherBody' and x['hit']: by = x['hit']['team']
            r['death'] = (x['round'], cause, 'self' if by == T else ('ENEMY' if by == E else by), x['len'])
        else: r['death'] = None
        lens = {}; dist = {}; endist = []; teamtot = {}
        for rnd, s in g['rounds']:
            if rnd % 100 == 0 or rnd == g['last_round']:
                lens[rnd] = s[T]['ids'].get(qi, 0); teamtot[rnd] = (s[T]['n'], s[T]['max'], s[T]['total'])
            if qi in s['heads']:
                h = s['heads'][qi][0]
                if rnd % 10 == 0:
                    dist.setdefault('spawn', []).append(m.dist(h, spawn[T]))
                    eh = [m.dist(h, v[0]) for j, v in s['heads'].items() if v[2] == E]
                    if eh: endist.append(min(eh))
                    if 1 - qi in s['heads']: dist.setdefault('eq', []).append(m.dist(h, s['heads'][1 - qi][0]))
        r['len'] = lens; r['team'] = teamtot
        r['spawn_d'] = (round(sum(dist.get('spawn', [0])) / max(1, len(dist.get('spawn', []))), 1), max(dist.get('spawn', [0])))
        r['near_en'] = round(sum(endist) / max(1, len(endist)), 1) if endist else None
        r['d_eq'] = round(sum(dist.get('eq', [0])) / max(1, len(dist.get('eq', []))), 1) if dist.get('eq') else None
        sp = [x for x in g['splits'] if x['parent'] == qi]
        r['splits'] = [(x['round'], x['L'], x['k']) for x in sp]
        qe = [e for e in g['eats'] if e['id'] == qi]; te = [e for e in g['eats'] if e['team'] == T]
        r['eats'] = (len(qe), len(te), sum(1 for e in qe if e['corpse'] and e['corpse'][1] == T))
        # own-team non-queen deaths within 2 of queen head (feeding/sacrifice)
        r['ally_die_near_q'] = sum(1 for x in g['deaths'] if x['team'] == T and x['id'] != qi and x.get('king') and x['king'][0] == qi and x['king'][2] <= 2)
        # enemy queen killed by us
        out[T] = r
    return out

if __name__ == '__main__':
    games = {m['id']: m for m in json.load(open(sys.argv[1]))}
    res = []
    for gid in sys.argv[3:]:
        gid = int(gid); o = analyze(os.path.join(sys.argv[2], f'{gid}.replay'), games[gid]); o['id'] = gid; res.append(o)
        print(f"== {gid} {o['map']} end r{o['end']} {o['reason']} winner {o['winner']} {o['res']}")
        for T in 'AB':
            r = o[T]
            print(f"  {T} {r['name'][:14]:14} qdeath={r['death']} qlen={r['len']} splits={r['splits'][:6]}{'..' if len(r['splits'])>6 else ''} eats(q,team,q_own_corpse)={r['eats']} spawnd(avg,max)={r['spawn_d']} near_en={r['near_en']} d_eq={r['d_eq']} allydie_near_q={r['ally_die_near_q']}")
            print(f"     team(n,max,tot) {r['team']}")
    json.dump(res, open(os.path.join(sys.argv[2], 'meta_res.json'), 'w'), default=str)
