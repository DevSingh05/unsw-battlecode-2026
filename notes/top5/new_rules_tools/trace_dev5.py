"""Turn-by-turn tracer for one replay in replays/devtest/.
usage: python3 trace_dev5.py GID [--ids 0,5,17] [--team A|B] [--from R] [--to R] [--kills] [--snap N]
  --ids     print every action of these dragon ids (head, len, action, steps, ate, killed, died)
  --team    print every action of that team (long; use with --from/--to)
  --kills   print every head-on kill with the killer's last 6 head positions and the victim's
  --snap N  every N rounds print per-team units/total/longest and the 8 longest units with head positions
Splits and deaths in the window are always printed."""
import sys, collections, math
sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0, '/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD = '/Users/devsingh/Developer/UNSW_Battlecode/replays/devtest/'
a = sys.argv[1:]
gid = a[0]
opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
ids = set(int(x) for x in opt('--ids', '').split(',') if x)
team = opt('--team'); lo = int(opt('--from', 0)); hi = int(opt('--to', 500)); snap = int(opt('--snap', 0))
g = sim2.simulate(RD + f'{gid}.replay'); rd = dict(g['rounds']); m = g['map']
print(m.name, f'{m.w}x{m.h}', 'queens: id0 team', g['team'][0], 'id1 team', g['team'][1], 'result', g['result'])
ev = collections.defaultdict(list)
for x in g['deaths']:
    ev[x['round']].append(f"DEATH {x['team']}{x['id']} L{x['len']} {x['reason']} @{x['head']}" + (f" by {x.get('killer')}(L{x.get('killer_len')})" if 'killer' in x else '') + (f" move={x.get('move')}" if x.get('move') else '') + (f" king d{x['king'][2]}" if x.get('king') else ''))
for x in g['splits']:
    ev[x['round']].append(f"SPLIT {x['team']}{x['parent']}->{x['child']} L{x['L']} k{x['k']} exits{x['exits']} enemy_d{x['enemy_dist']}")
acts = collections.defaultdict(list)
for mv in g['moves']:
    if mv['id'] in ids or (team and mv['team'] == team):
        acts[mv['round']].append(mv)
for r in range(lo, hi + 1):
    for e in ev.get(r, []): print(f'r{r}', e)
    for mv in acts.get(r, []):
        L = mv['len_before']; act = 'SUICIDE' if mv.get('suicide') else ''.join(mv['act'].get('move', []))
        paid = max(0, mv['steps'] - math.ceil(L / 4))
        print(f"r{r} {mv['team']}{mv['id']} L{L}->{mv.get('len_after')} @{mv['head']} {act} steps{mv['steps']} paid{paid} ate{mv['ate']}"
              + (f" KILLED{mv['killed']}" if mv['killed'] else '') + (f" DIED {mv['died']}" if mv['died'] else '') + (f" nearE d{mv['near_enemy_head'][0]} L{mv['near_enemy_head'][2]}" if mv['near_enemy_head'] else ''))
    if snap and r % snap == 0 and r in rd:
        s = rd[r]
        for T in 'AB':
            hs = sorted(((v[1], j, v[0]) for j, v in s['heads'].items() if v[2] == T), reverse=True)
            print(f"  snap r{r} {T} n{s[T]['n']} tot{s[T]['total']} max{s[T]['max']}:", ' '.join(f"{j}{'Q' if j <= 1 else ''}L{L}@{p[0]},{p[1]}" for L, j, p in hs[:8]))
if '--kills' in a:
    for mv in g['moves']:
        ks = [k for k in mv['killed'] if k[1] != mv['team']]
        if not ks or not (lo <= mv['round'] <= hi): continue
        for vid, vt, vl in ks:
            tr = []
            for back in (6, 4, 3, 2, 1):
                s = rd.get(mv['round'] - back)
                if s and mv['id'] in s['heads'] and vid in s['heads']: tr.append(m.dist(s['heads'][mv['id']][0], s['heads'][vid][0]))
                else: tr.append('-')
            print(f"KILL r{mv['round']} {mv['team']}{mv['id']} L{mv['len_before']} {''.join(mv['act']['move'])} ate{mv['ate']} -> {vt}{vid} L{vl}{' QUEEN' if vid <= 1 else ''}  dist r-6,-4,-3,-2,-1: {tr}")
