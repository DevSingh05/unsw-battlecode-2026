# for our queen's head-on deaths: killer's position when the queen made her last move: Chebyshev dist (visible <=3), Manhattan dist, killer len before
import sys,glob,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools'); import replay_decode as R, replay_sim as S
c=collections.Counter(); rows=[]
for D in sys.argv[1:]:
  for f in sorted(glob.glob(D+'/*.replay')):
    sw=int(f.rsplit('_',1)[1].split('.')[0]); T='B' if sw else 'A'
    o=R.load(f); m=S.Map(o['map'])
    body={i:list(p) for i,(t,p) in enumerate(m.dragons)}; team={i:'AB'[t] for i,(t,p) in enumerate(m.dragons)}; alive=set(body)
    uq=0 if team[0]==T else 1; snap=None; rnd=0; actor=None
    for e in o['events']:
        t=e['t']
        if t=='roundStart': rnd=e['round']
        elif t=='turnStart': actor=e['id']
        elif t=='dragonAction' and e['id']==uq:
            snap={j:(body[j][0],len(body[j])) for j in alive if team[j]!=T}
        elif t=='dragonUpdate':
            b=body[e['id']]; b.insert(0,e['head'])
            while b and b[-1]!=e['tail']: b.pop()
        elif t=='dragonSplit':
            body[e['parent']]=list(e['parentBody']); body[e['child']]=list(e['childBody']); team[e['child']]=e['team']; alive.add(e['child'])
            if snap is not None and e['team']!=T: snap.setdefault(e['child'],(body[e['child']][0],len(body[e['child']])))
        elif t=='dragonDeath':
            alive.discard(e['id'])
            if e['id']==uq:
                if e['reason']=='HitHeadToHead' and actor!=uq and team.get(actor)!=T and snap and actor in snap:
                    qh=body[uq][0]; kh,kl=snap[actor]
                    ch=max(min(abs(qh[0]-kh[0]),m.w-abs(qh[0]-kh[0])),min(abs(qh[1]-kh[1]),m.h-abs(qh[1]-kh[1])))
                    c[('vis' if ch<=3 else 'unseen', m.dist(qh,kh), kl)]+=1
                break
print(sorted(c.items(), key=lambda x:-x[1]))
