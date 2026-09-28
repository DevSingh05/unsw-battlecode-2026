from por_an import *
import sys
p=sys.argv[1]; T=sys.argv[2]; r0=int(sys.argv[3]); r1=int(sys.argv[4])
g=sim(p)
mv=[m for m in g['moves'] if m['team']==T and r0<=m['round']<=r1]
for m in mv:
    print(m['round'],m['id'],m['head'],m['len_before'],m['act'],'ate',m['ate'],'died',m.get('died'))
