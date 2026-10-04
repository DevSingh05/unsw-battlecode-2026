"""Opening fingerprint: for each game and named team, the team's actions in rounds 1..N (moves dirs, splits k) as a string.
Usage: python3 fp_top2.py TEAMNAME N listjson:replaydir [listjson:replaydir ...] -> prints map, at, sig hash, per game"""
import sys,json,os,hashlib,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
name=sys.argv[1]; N=int(sys.argv[2])
res=collections.defaultdict(list)
for spec in sys.argv[3:]:
    lj,rd=spec.split(':')
    for gm in json.load(open(lj)):
        p=os.path.join(rd,f"{gm['id']}.replay")
        if not os.path.exists(p): continue
        names=[gm['a']['name'],gm['b']['name']]
        if name not in names: continue
        try: g=sim2.simulate(p)
        except Exception as e: continue
        rw=g['result']['winner']
        if rw is None: continue
        aw=gm['winner']
        L={'A':names[0],'B':names[1]} if (rw=='A')==(aw=='a') else {'A':names[1],'B':names[0]}
        T=[t for t in 'AB' if L[t]==name][0]
        ev=[]
        for a in g['moves']:
            if a['team']==T and a['round']<=N: ev.append((a['round'],a['id'],'M'+''.join(a['act'].get('move',[])) if 'move' in a['act'] else 'S'))
        for s in g['splits']:
            if s['team']==T and s['round']<=N: ev.append((s['round'],s['parent'],f"P{s['k']}"))
        ev.sort()
        sig=hashlib.md5(repr(ev).encode()).hexdigest()[:6]
        res[(g['map'].name,T)].append((gm['at'][:16],sig,len(ev)))
for k,v in sorted(res.items()):
    v.sort()
    print(k, ' '.join(f"{a[5:]}:{s}" for a,s,n in v))
