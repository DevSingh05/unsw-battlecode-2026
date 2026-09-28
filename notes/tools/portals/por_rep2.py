from por_an import *
rows=[]
for sub,p,win,a,b in tops():
    g=sim(p)
    for T,name in (('A',a),('B',b)):
        rows.append((name,os.path.basename(p)[:6],T==win,team_stats(g,T),g,T))
print('name game W final hot box corpse deaths r10 r20 r30 eatwin hotwin splits units')
for r in rows:
    s=r[3]
    print(f"{r[0][:12]:12s} {r[1]} {'W' if r[2] else 'L'} {s['final']:3d} {s['eat_hot']:4d} {s['eat_box']:4d} {s['eat_corpse']:4d} {s['deaths']:4d} {s['r10']} {s['r20']} {s['r30']} {s['eat_win']} {s['hot_win']} {s['splits']} {s['units']}")
for lab,sel in (('winners',[r for r in rows if r[2]]),('losers',[r for r in rows if not r[2]]),('all',rows)):
    print('==',lab,len(sel))
    for key in ['longest','units','total']:
        arr=list(zip(*[r[3][key] for r in sel]))
        print(f'{key:8s}',' '.join(f'{med([v for v in a if v is not None]):5.1f}' for a in arr))
    for key in ['final','final2','eat_hot','eat_box','eat_corpse','deaths','r10','r20','r30']:
        a=[r[3][key] for r in sel]; print(f'{key:10s} {med([x for x in a if x is not None]):6.1f} none {sum(x is None for x in a)}')
    for key in ['eat_win','hot_win','splits']:
        print(key,[med(list(x)) for x in zip(*[r[3][key] for r in sel])])
