"""Trace pocket episodes of one team in one game: every action of the diver (and its split child) while in/near the pocket.
    python3 notes/tools/autarky/trace.py GAME TEAM(A|B) [r0] [r1] [max_eps]"""
import os, sys, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
a = sys.argv[1:]; gid = int(a[0]); T = a[1]; r0 = int(a[2]) if len(a) > 2 else 60; r1 = int(a[3]) if len(a) > 3 else 200; mx = int(a[4]) if len(a) > 4 else 6
path = [g['path'] for g in collect.games() if g['gid'] == gid][0]
S = sim2.simulate(path); m = S['map']; PK = collect.pockets(m)
acts = collections.defaultdict(list)
for x in S['moves']: acts[x['id']].append(('mv', x['round'], x))
for s in S['splits']: acts[s['parent']].append(('split', s['round'], s))
for d in S['deaths']: acts[d['id']].append(('death', d['round'], d))
for k in acts: acts[k].sort(key=lambda z: (z[1], {'mv': 0, 'split': 1, 'death': 2}[z[0]]))
n = 0
for x in S['moves']:
    if x['team'] != T or not (r0 <= x['round'] <= r1) or x.get('suicide'): continue
    if x['head'] in PK or x.get('head_after') not in PK: continue
    n += 1
    if n > mx: break
    i = x['id']; print(f"--- diver {i} enters r{x['round']} L{x['len_before']} at {x['head_after']}")
    follow = [i]
    for kind, r, z in acts[i]:
        if r < x['round'] or r > x['round'] + 12: continue
        if kind == 'mv': print(f"   r{r} id{i} {''.join(z['act'].get('move', [])) or z['act']} {z['head']}->{z.get('head_after')} L{z['len_before']}->{z.get('len_after')} ate{z['ate']}")
        elif kind == 'split':
            print(f"   r{r} id{i} SPLIT L{z['L']} k{z['k']} exits{z['exits']} child {z['child']}"); follow.append(z['child'])
            for k2, r2, z2 in acts[z['child']][:4]:
                if k2 == 'mv': print(f"      child r{r2} {''.join(z2['act'].get('move', []))} {z2['head']}->{z2.get('head_after')} L{z2['len_before']}->{z2.get('len_after')}")
                elif k2 == 'death': print(f"      child r{r2} DIES {z2['reason']} L{z2['len']}")
                else: print(f"      child r{r2} SPLIT L{z2['L']} k{z2['k']}")
        else:
            print(f"   r{r} id{i} DIES {z['reason']} L{z['len']} at {z['head']} nbrs {z['nbrs']}"); break
