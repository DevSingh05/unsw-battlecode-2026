# geometry of Portals: tube tiles, pockets, sock (both teams), via genmaps
import sys, pathlib
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools')
from genmaps import parse
M=parse(pathlib.Path('/Users/devsingh/Developer/UNSW_Battlecode/maps/portals.map'))
W,H,nxt=M['w'],M['h'],M['nxt']
def nbrs(t): return [nxt[t*4+d] for d in range(4) if nxt[t*4+d]>=0]
def xy(t): return (t%W,t//W)
POCKET=set(); TUBE=set(); SOCK=set()
for t in range(W*H):
    if M['gmax'][t]==10:
        (POCKET if len(nbrs(t))==1 else TUBE).add(xy(t))
# socks: A: (15,0..7),(16,7); B: (16,8..15),(15,8)
SOCK={(15,y) for y in range(8)}|{(16,7)}|{(16,y) for y in range(8,16)}|{(15,8)}
def cls(p):
    if p in POCKET: return 'pocket'
    if p in TUBE: return 'tube'
    if p in SOCK: return 'sock'
    return 'main'
