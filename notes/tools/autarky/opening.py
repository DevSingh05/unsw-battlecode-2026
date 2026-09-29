"""Opening of one game: every split / death / action of the L14 starters and their descendants that are >=5 long, r0-R.
    python3 notes/tools/autarky/opening.py GAME [R=40]"""
import os, sys, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '../midgame')); sys.path.insert(0, H)
import sim2, collect
a = sys.argv[1:]; gid = int(a[0]); RR = int(a[1]) if len(a) > 1 else 40
path = [g['path'] for g in collect.games() if g['gid'] == gid][0]
S = sim2.simulate(path); m = S['map']
starters = [i for i, (t, p) in enumerate(m.dragons) if len(p) >= 10]
ev = []
for x in S['moves']:
    if x['round'] <= RR and x['len_before'] >= 5: ev.append((x['round'], x['id'], f"{x['team']} id{x['id']} L{x['len_before']} {''.join(x['act'].get('move', [])) or 'suicide'} {x['head']}->{x.get('head_after')} ate{x['ate']}"))
for s in S['splits']:
    if s['round'] <= RR and s['L'] >= 5: ev.append((s['round'], s['parent'], f"{s['team']} id{s['parent']} SPLIT L{s['L']} k{s['k']} exits{s['exits']} -> child {s['child']}"))
for d in S['deaths']:
    if d['round'] <= RR and d['len'] >= 4: ev.append((d['round'], d['id'], f"{d['team']} id{d['id']} DIES {d['reason']} L{d['len']} at {d['head']}"))
print('starters', starters, [m.dragons[i][0] for i in starters])
for r, i, s in sorted(ev):
    print(f"r{r:3d} {s}")
