"""Per-team median timelines (units / longest / total length) and split/suicide rates by round bucket."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_cache import load_all
from collections import defaultdict, Counter
import statistics as st
gs=load_all()
R=(25,50,100,150,200,250,300,350,400,450,480,499)
tl=defaultdict(lambda: defaultdict(list))
for g in gs:
    snap=dict(g['rounds'])
    for s in 'AB':
        T=g['names'][s]
        for r in R:
            if r in snap: tl[T][r].append((snap[r][s]['n'],snap[r][s]['max'],snap[r][s]['total']))
for T,d in tl.items():
    print('##',T)
    print('  round  : '+' '.join(f'{r:>5}' for r in R))
    for i,lab in enumerate(('units','longest','total')):
        print(f'  {lab:7}: '+' '.join(f'{st.median([x[i] for x in d[r]]) if d[r] else "-":>5}' for r in R))
# split and self-death rates by bucket per team (per game)
print('\n# events per game per 50-round bucket: splits(4->2+2) / other splits / self-deaths / sprints')
B=range(0,500,50)
for T in tl:
    cnt=defaultdict(Counter); ng=0
    for g in gs:
        side=[k for k,v in g['names'].items() if v==T]
        if not side: continue
        s=side[0]; ng+=1
        for x in g['splits']:
            if x['team']==s: cnt[x['round']//50*50]['s42' if (x['L'],x['k'])==(4,2) else 'sx']+=1
        for d in g['deaths']:
            if d['team']==s and d['reason'] in('HitSelf','HitWall','NoValidAction'): cnt[d['round']//50*50]['sd']+=1
        for a in g['moves']:
            if a['team']==s and a['steps']>1: cnt[a['round']//50*50]['sp']+=1
    print(f'{T[:12]:12} (n={ng}) '+' | '.join(f"{b}:{cnt[b]['s42']/ng:.0f}/{cnt[b]['sx']/ng:.0f}/{cnt[b]['sd']/ng:.0f}/{cnt[b]['sp']/ng:.0f}" for b in B))
