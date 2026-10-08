# usage: board.py gid round [radius] -> ascii around our queen at start of round
import sys,json
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import replay_sim as RS, replay_decode as RD
S=sys.argv[0].rsplit('/',1)[0]
gid=sys.argv[1]; stop=int(sys.argv[2]); rad=int(sys.argv[3]) if len(sys.argv)>3 else 8

orig=RD.load
def load(p):
    o=orig(p); ev=[]
    for e in o['events']:
        if e['t']=='roundStart' and e['round']>=stop: break
        ev.append(e)
    o['events']=ev; return o
RS.R.load=load
g=RS.simulate(gid)
m=g['map']; uq=int(sys.argv[4]); us=g['team'][uq]; row={'map':''}
body=g['body']; alive=g['alive']; team=g['team']
pear=set()
# reconstruct pearls: not returned; approximate via eats? skip
occ={}
for j in alive:
    for si,s in enumerate(body[j]): occ[s]=(j,si)
if uq not in alive: print('queen dead'); sys.exit()
hx,hy=body[uq][0]
print(sorted((len(body[j]),j,body[j][0]) for j in alive if team[j]!=us and abs((body[j][0][0]-hx+m.w//2)%m.w-m.w//2)+abs((body[j][0][1]-hy+m.h//2)%m.h-m.h//2)<=8));print('round',stop,'queen L',len(body[uq]),'head',(hx,hy),'tail',body[uq][-1])
for dy in range(-rad,rad+1):
    line=''
    for dx in range(-rad,rad+1):
        x,y=(hx+dx)%m.w,(hy+dy)%m.h
        c='.'
        if (x,y) in occ:
            j,si=occ[(x,y)]
            if j==uq: c='Q' if si==0 else ('t' if si==len(body[j])-1 else 'q')
            elif team[j]==us: c='A' if si==0 else 'a'
            else: c='E' if si==0 else 'e'
        if m.tiles.get((x,y),(0,0))[0]==-1: pass
        # kelp edges: mark walls to the east / south
        e=m.edges.get(m.side_edge((x,y),'E')); s_=m.edges.get(m.side_edge((x,y),'S'))
        ce='|' if e and e[0]==1 else ('>' if e and e[0]==2 else ' ')
        line+=c+ce
    print(line)
    # south walls line
    sl=''
    for dx in range(-rad,rad+1):
        x,y=(hx+dx)%m.w,(hy+dy)%m.h
        s_=m.edges.get(m.side_edge((x,y),'S'))
        sl+=('-' if s_ and s_[0]==1 else ('v' if s_ and s_[0]==2 else ' '))+' '
    print(sl)
