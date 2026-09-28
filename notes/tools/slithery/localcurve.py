# Mean units/longest curves for candidate vs opponent in an arena replay dir (candidate = the 'proto' bot).
import sys,glob,os,statistics
from common import *
from replay_sim import simulate
from collections import defaultdict
d=sys.argv[1]; key=sys.argv[2] if len(sys.argv)>2 else 'proto'
C=defaultdict(list); wins=0; n=0; fin=[]
for p in sorted(glob.glob(d+'/*.replay')):
    b=os.path.basename(p); first=b.split('_vs_')[0]
    T='A' if key in first else 'B'; o='B' if T=='A' else 'A'
    G=simulate(p); R=dict(G['rounds']); n+=1; wins+= G['result']['winner']==T
    for r in (250,300,350,400,450,499):
        s=R.get(r) or R[max(R)]
        C[('n',r)].append((s[T]['n'],s[o]['n'])); C[('max',r)].append((s[T]['max'],s[o]['max']))
    fin.append((G['result'][T]['longest'],G['result'][o]['longest']))
print(d.split('/')[-1],'wins',wins,'/',n)
for k in sorted(C): print('  %-4s r%d  cand %.1f  opp %.1f'%(k[0],k[1],statistics.mean(a for a,b in C[k]),statistics.mean(b for a,b in C[k])))
print('  final',fin)
