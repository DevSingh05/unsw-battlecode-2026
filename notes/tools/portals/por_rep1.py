from por_an import *
rows=[]
for lab,p,side,win,opp in ours():
    g=sim(p); o='B' if side=='A' else 'A'
    rows.append((lab,os.path.basename(p)[:-7],win,opp,team_stats(g,side),team_stats(g,o)))
def show(rows,title):
    print('=====',title,len(rows))
    for key in ['longest','units','total']:
        for who,i in (('us',4),('them',5)):
            arr=list(zip(*[r[i][key] for r in rows]))
            print(f'{key:8s} {who:5s}',' '.join(f'{med([v for v in a if v is not None]):5.1f}' for a in arr))
    for key in ['final','final2','eat_hot','eat_box','eat_corpse','eat_other','deaths','r10','r20','r30']:
        a=[r[4][key] for r in rows]; b=[r[5][key] for r in rows]
        print(f'{key:10s} us {med([x for x in a if x is not None]):6.1f}  them {med([x for x in b if x is not None]):6.1f}  (us none {sum(x is None for x in a)}, them none {sum(x is None for x in b)})')
    for key in ['eat_win','hot_win','splits']:
        print(key,'us',[med(list(x)) for x in zip(*[r[4][key] for r in rows])],'them',[med(list(x)) for x in zip(*[r[5][key] for r in rows])])
print('per game: label id win final us/them  hot us/them  box us/them corpse us/them deaths us/them r20 us/them')
for r in rows:
    u,t=r[4],r[5]
    print(r[0],r[1],'W' if r[2] else 'L',f"{u['final']:3d}/{t['final']:3d}  hot {u['eat_hot']:3d}/{t['eat_hot']:3d} box {u['eat_box']:3d}/{t['eat_box']:3d} corpse {u['eat_corpse']:3d}/{t['eat_corpse']:3d} deaths {u['deaths']:3d}/{t['deaths']:3d} r20 {u['r20']}/{t['r20']}  opp {r[3][:18]}")
show(rows,'all ours')
show([r for r in rows if r[0] in ('ch5','ch6','ch8')],'recent (ch5/6/8)')
show([r for r in rows if not r[2]],'losses')
