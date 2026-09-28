from por_an import *
from por_geo import cls, POCKET
import sys
p=sys.argv[1]; T=sys.argv[2]; r0=int(sys.argv[3]); r1=int(sys.argv[4]); only=sys.argv[5] if len(sys.argv)>5 else 'pocket'
g=sim(p)
ev=[]
for m in g['moves']:
    if m['team']==T and r0<=m['round']<=r1: ev.append((m['round'],0,f"move id{m['id']} L{m['len_before']} head{m['head']} {m['act']} ate{m['ate']} died{m.get('died')}"))
for s in g['splits']:
    if s['team']==T and r0<=s['round']<=r1: ev.append((s['round'],1,f"SPLIT parent{s['parent']} child{s['child']} L{s['L']} k{s['k']} exits{s['exits']}"))
for d in g['deaths']:
    if d['team']==T and r0<=d['round']<=r1: ev.append((d['round'],2,f"DEATH id{d['id']} L{d['len']} {d['reason']} head{d['head']} {cls(d['head'])}"))
for e in g['eats']:
    if e['team']==T and r0<=e['round']<=r1: ev.append((e['round'],1.5,f"EAT id{e['id']} {e['tile']} {cls(e['tile'])} corpse={e['corpse'] is not None}"))
ev.sort(key=lambda x:(x[0],x[1]))
ids=None
if len(sys.argv)>6: ids=set(int(i) for i in sys.argv[6].split(','))
for r,_,s in ev:
    if ids is None or any(f'id{i} ' in s or f'parent{i} ' in s or f'child{i} ' in s for i in ids): print(r,s)
