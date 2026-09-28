import os,sys,json,pickle,pathlib
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/tools')
os.chdir('/Users/devsingh/Developer/UNSW_Battlecode')
from genmaps import parse
M=parse(pathlib.Path('maps/slithery_fight.map')); W,H=M['w'],M['h']
GAP={(t%W,t//W):(M['gmin'][t],M['gmax'][t]) for t in range(W*H)}
def A(p,side): return tuple(p) if side=='A' else (62-p[0],26-p[1])
def zone(p):
    """p in own frame (A-frame for own team)."""
    x,y=p; g=GAP[(x,y)][1]
    if (x,y) in {(57,13),(58,13),(57,14),(58,14)}: return 'boxE'
    if (x,y) in {(4,12),(5,12),(4,13),(5,13)}: return 'boxO'
    if g==1:
        if x==8 and y<=10: return 'hotP1'
        if x==8: return 'hotP2'
        if x==33 and y<=2: return 'hotP3'
        if y==5 and x in(31,32): return 'hotP4'
        if y==7 and x<=18: return 'hotR7W'
        if y==7 and x<=23: return 'hotR7E'
        if (x,y)==(31,13): return 'hotC'
        return 'hotEnemy'
    if g==5:
        if y<=1: return 'comb5O'
        if y>=25: return 'comb5E'
        return 'box5'
    if g==10:
        return 'g10'+('O' if (x<31 or (x==31 and y<13)) else 'E')
    if g==100: return 'g100'+('O' if x<31 else 'E')
    if g>0: return 'rare'
    return 'none'
def top_games():
    out=[]
    for d in ['notes/replays/permap','notes/replays/kings']:
        for g in json.load(open(d+'/index.json')):
            if g['mapName']!='Slithery Fight': continue
            p='%s/%d.replay'%(d,g['id'])
            if os.path.exists(p): out.append((p,g['id'],g['winner'].upper(),g['a']['name'],g['b']['name']))
    return out
