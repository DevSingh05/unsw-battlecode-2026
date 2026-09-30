"""Per-game metrics for cheji bt replays (read-only). Usage: python3 cheji_measure.py <replay_dir> <sides.json>"""
import sys, os, json, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools/midgame')); sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import sim2
D = sys.argv[1]; sides = json.load(open(sys.argv[2]))
CK = (50, 100, 200, 300, 400)
out = []
for gid, info in sides.items():
    fn = os.path.join(D, f'{gid}.replay')
    if not os.path.exists(fn): continue
    g = sim2.simulate(fn); m = g['map']; C = info['cheji']; O = 'B' if C == 'A' else 'A'
    snaps = dict(g['rounds'])
    row = {'gid': gid, 'map': m.name, 'opp': info.get('opp', ''), 'last': g['last_round'], 'end': g['result'].get('endReason'),
           'cheji_won': g['result'].get('winner') == C}
    for T, lab in ((C, 'c'), (O, 'o')):
        s = {}
        for r in CK + (g['last_round'],):
            sn = snaps.get(r) or snaps[max(k for k in snaps if k <= r)]
            s[r if r in CK else 'fin'] = (sn[T]['n'], sn[T]['max'], sn[T]['total'])
        sp = [x for x in g['splits'] if x['team'] == T]
        mv = [a for a in g['moves'] if a['team'] == T and not a.get('suicide')]
        spr = [a for a in mv if a['steps'] >= 2]
        portal = sum(1 for a in mv if a.get('head_after') and m.dist(a['head'], a['head_after']) > a['steps'])
        hk = sum(1 for d in g['deaths'] if d['reason'] == 'HitHeadToHead' and d.get('killer_team') == T)
        rams = sum(1 for d in g['deaths'] if d['team'] != T and d.get('actor') is not None and g['team'].get(d['actor']) == T and d['reason'] != 'HitHeadToHead')
        spr_kill = sum(1 for a in spr if a['killed']); spr_eat = sum(1 for a in spr if a['ate'])
        dth = collections.Counter(d['reason'] for d in g['deaths'] if d['team'] == T)
        sp_phase = [sum(1 for x in sp if lo <= x['round'] < hi) for lo, hi in ((0, 100), (100, 300), (300, 350), (350, 999))]
        row[lab] = dict(snap=s, splits=len(sp), sp_phase=sp_phase, sprints=len(spr), spr_eat=spr_eat, spr_kill=spr_kill,
                        headon_kills=hk, body_kills=rams, portal=portal, deaths=dict(dth))
    out.append(row)
json.dump(out, open(os.path.join(D, 'metrics.json'), 'w'), indent=0)
for r in out:
    print(f"{r['gid']} {r['map']:<18} end={r['end']} r{r['last']} cheji_won={r['cheji_won']}")
    for lab in 'co':
        x = r[lab]; sn = ' '.join(f"{k}:{v[0]}/{v[1]}/{v[2]}" for k, v in x['snap'].items())
        print(f"  {lab} {sn} | splits {x['splits']} {x['sp_phase']} spr {x['sprints']} (eat {x['spr_eat']} kill {x['spr_kill']}) h2h {x['headon_kills']} body {x['body_kills']} portal {x['portal']} deaths {x['deaths']}")
