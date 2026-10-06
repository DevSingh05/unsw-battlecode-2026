"""Queen-death context (Oct 5 VIB study): for each game, the 8 rounds before our queen's death: nearest enemy heads (dist, len), killer track."""
import sys
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/vib_oct5/'
def ctx(gid,T,back=8):
    g=sim2.simulate(RD+f'{gid}.replay'); m=g['map']; rd=dict(g['rounds'])
    qi=0 if g['team'][0]==T else 1
    qd=[x for x in g['deaths'] if x['id']==qi]
    if not qd: return None
    x=qd[0]; R=x['round']; kid=x.get('killer') or (x['hit']['id'] if x.get('hit') else None)
    out=[f"{gid} {m.name} queen dies r{R} L{x['len']} {x['reason']} killer={kid} kL={x.get('killer_len')}"]
    for r in range(max(0,R-back),R+1):
        s=rd.get(r)
        if not s or qi not in s['heads']: continue
        h=s['heads'][qi][0]
        en=sorted((m.dist(h,v[0]),v[1],j) for j,v in s['heads'].items() if v[2]!=T)[:3]
        al=sum(1 for j,v in s['heads'].items() if v[2]==T and j!=qi and m.dist(h,v[0])<=3)
        out.append(f"  r{r} q@{h} L{s[T]['ids'].get(qi)} near-enemy(d,L,id)={en} allies<=3:{al}")
    return '\n'.join(out)
if __name__=='__main__':
    for a in sys.argv[1:]:
        gid,T=a.split(':'); print(ctx(int(gid),T))
