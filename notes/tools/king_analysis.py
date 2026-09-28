"""King selection / growth / feeder geometry for roundLimit games. Run after analyze_top.py (uses cache)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_cache import load_all
from collections import Counter, defaultdict
def qq(x):
    x=sorted(x); return [x[int(p*(len(x)-1))] for p in (0.1,.25,.5,.75,.9)] if x else None
gs=load_all()
rel=Counter(); rows=[]; team_feed=defaultdict(list)
for g in gs:
    if g['result']['endReason']!='roundLimit': continue
    m=g['map']; snap=dict(g['rounds'])
    for s in 'AB':
        T=g['names'][s]; fin=snap[g['last_round']][s]; king=fin['king']
        if king is None: continue
        # king rank over time
        def rank(r):
            ids=snap[r][s]['ids']
            if king not in ids: return None
            return 1+sum(1 for j,l in ids.items() if l>ids[king])
        tl={r:snap[r][s]['ids'].get(king) for r in (200,250,300,350,400,450,480,490,499)}
        rk={r:rank(r) for r in (200,300,400,450)}
        # round king became longest for good
        since=None
        for r in range(g['last_round'],-1,-1):
            if r in snap and snap[r][s]['king']!=king: since=r+1; break
        # last growth round
        lg=None; prev=None
        for r in range(0,g['last_round']+1):
            if r not in snap: continue
            l=snap[r][s]['ids'].get(king)
            if prev is not None and l is not None and l>prev: lg=r
            prev=l
        win=g['result']['winner']==s
        rows.append((T,g['id'],m.name,win,king,g['born'][king],since,tl,rk,lg,fin['n']))
        # feeders geometry
        for d in g['deaths']:
            if d['team']!=s or d.get('king') is None or d['king'][0]!=king: continue
            if d['reason'] not in ('HitSelf','HitWall','NoValidAction') and not (d['reason']=='HitOtherBody' and d['hit'] and d['hit']['team']==s): continue
            if d['round']<250 or d['king'][2]>4: continue
            kh,kn=d['king_head2'][0],d['king_head2'][1] if len(d['king_head2'])>1 else None
            # king facing
            fx=None
            for D,(dx,dy) in {'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}.items():
                if kn and m.wrap(kn[0]+dx,kn[1]+dy)==kh: fx=D
            # pearls positions relative to king head in king frame (forward, right)
            def relp(p):
                dx=(p[0]-kh[0]+m.w//2)%m.w-m.w//2; dy=(p[1]-kh[1]+m.h//2)%m.h-m.h//2
                f={'N':(dx,-dy),'S':(-dx,dy),'E':(dy,dx),'W':(-dy,-dx)}.get(fx,(dx,dy))  # (right, forward)
                return f
            pearls=d['body'][::2]
            for p in pearls: rel[relp(p)]+=1
            team_feed[T].append((d['round'],d['len'],d['reason'],d['move'] if 'move' in d else None,relp(d['head']),m.dist(d['head'],kh)))
print('# KING TIMELINES (team, game, map, win, kingId, born, longest-since, len@200..499, rank@200/300/400/450, last growth rnd, final units)')
for r in sorted(rows,key=lambda r:(r[0],r[1])): print(r)
print('\n# FEEDER PEARL POSITIONS relative to king head, (right, forward) in king frame, top 25')
tot=sum(rel.values())
for k,v in rel.most_common(25): print(k, v, f'{100*v/tot:.1f}%')
print('\n# FEEDERS per team (<=4 from king, r>=250)')
for T,f in team_feed.items():
    print(T,'n',len(f),'len q',qq([x[1] for x in f]),'reason',Counter(x[2] for x in f).most_common(),'dist',sorted(Counter(x[5] for x in f).items()),'round q',qq([x[0] for x in f]))
    print('    head rel (right,fwd) top', Counter(x[4] for x in f).most_common(8))
