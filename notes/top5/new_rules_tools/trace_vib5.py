"""Trace one replay: argv1 gid, argv2 last round, argv3 step. Prints per-team heads/lengths, eats, deaths, splits."""
import sys,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/vib_oct5/'
gid=sys.argv[1]; L=int(sys.argv[2]); stp=int(sys.argv[3]); lo=int(sys.argv[4]) if len(sys.argv)>4 else 0
g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds'])
print(g['map'].name,'queens: id0 team',g['team'][0],'id1 team',g['team'][1],'result',g['result'])
ev=collections.defaultdict(list)
for x in g['deaths']: ev[x['round']].append(f"D {x['team']}{x['id']} L{x['len']} {x['reason'][:8]} @{x['head']}"+(f" by {x.get('killer')}(L{x.get('killer_len')})" if 'killer' in x else ''))
for x in g['splits']: ev[x['round']].append(f"S {x['team']}{x['parent']}->{x['child']} L{x['L']} k{x['k']} ex{x['exits']}")
E=collections.Counter()
for e in g['eats']: E[(e['round']//stp,e['team'])]+=1
for k in range(lo,L+1):
    if ev[k] and k<=L: print(f"  r{k}:",'; '.join(ev[k]))
    if k%stp==0 and k in rd:
        s=rd[k]
        for T in 'AB':
            hs=sorted(((j,v) for j,v in s['heads'].items() if v[2]==T))
            print(f"r{k} {T} n{s[T]['n']} tot{s[T]['total']} eats{E[(k//stp-1,T)] if k else 0}:",' '.join(f"{j}{'Q' if j<=1 else ''}@{v[0][0]},{v[0][1]}L{v[1]}" for j,v in hs[:14]))
