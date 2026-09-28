# 2x-resolution render: cell chars at (2x+1,2y+1), walls between. gaps: # [1,1], 5 [1,5], + [1,10], o [1,100], . rare
import sys,pathlib
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools')
from genmaps import parse
m=parse(pathlib.Path('/Users/devsingh/Developer/UNSW_Battlecode/maps/slithery_fight.map'))
W,H,nx=m['w'],m['h'],m['nxt']
G=[[' ']*(2*W+1) for _ in range(2*H+1)]
for y in range(H):
  for x in range(W):
    t=y*W+x; mn,mx=m['gmin'][t],m['gmax'][t]
    c={0:' ',1:'#',5:'5',10:'+',100:'o'}.get(mx,'.')
    G[2*y+1][2*x+1]=c
    if nx[t*4+1]==-1: G[2*y+1][2*x+2]='|'
    elif nx[t*4+1]!=y*W+(x+1)%W: G[2*y+1][2*x+2]='P'
    if nx[t*4+2]==-1: G[2*y+2][2*x+1]='-'
    elif nx[t*4+2]!=((y+1)%H)*W+x: G[2*y+2][2*x+1]='P'
    if nx[t*4+3]==-1: G[2*y+1][2*x]='|'
    if nx[t*4+0]==-1: G[2*y][2*x+1]='-'
print('   '+''.join('%-2d'%(x%100) if x%5==0 else '  ' for x in range(W)))
for r,row in enumerate(G):
  lab='%2d '%((r-1)//2) if r%2 else '   '
  print(lab+''.join(row))
