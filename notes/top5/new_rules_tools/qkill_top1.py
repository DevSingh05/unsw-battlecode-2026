"""How FTM kills our queen: killer move steps, start distance, our queen's length and last action. Plus early pearl halves on small maps."""
import sys,json,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
D=pickle.load(open(S+'rows_top1.pkl','rb'))
K=collections.Counter(); ex=[]; qmv=collections.Counter(); pre=collections.Counter()
for gid,rs in D.items():
    if len(rs)!=2: continue
    u=[r for r in rs if r['team']!='FTM'][0]
    if u['team'] not in ('v44','v49','v43') or not u['qdeath'] or u['qdeath'][1]!='HitHeadToHead' or u['qdeath'][2]!='EN': continue
    g=sim2.simulate(RD+f'{gid}.replay'); m=g['map']
    # our team letter: queen team whose death round matches
    qd=[x for x in g['deaths'] if x['id'] in (0,1) and x['round']==u['qdeath'][0] and x['reason']=='HitHeadToHead' and x['len']==u['qdeath'][3]]
    if not qd: continue
    x=qd[0]; qi=x['id']; T=g['team'][qi]
    if x['actor']==qi:
        # our queen moved into them
        a=[a for a in g['moves'] if a['id']==qi and a['round']==x['round']]
        K[('queen moved into',a[0]['steps'] if a else None)]+=1; continue
    a=[a for a in g['moves'] if a['id']==x['actor'] and a['round']==x['round']]
    if not a: continue
    a=a[0]
    d=m.dist(a['head'],x['head']) if False else None
    # queen head at killer's turn start = x['head'] (she didn't move after); killer start dist:
    d=m.dist(a['head'],x['head'])
    K[(a['len_before'],a['steps'],d)]+=1
    # queen's own last move before death
    qa=[b for b in g['moves'] if b['id']==qi and b['round']<=x['round']]
    if qa:
        b=qa[-1]; qmv[(b['steps'], 'stay' if b['head_after']==b['head'] else 'moved')]+=1
        # distance from killer head to queen head at start of queen's last turn
        nd=b['near_enemy_head']; pre[nd[0] if nd else None]+=1
print('killer (len,steps,startdist):',K.most_common(15))
print('queen last move (steps):',qmv.most_common())
print('queen nearest enemy head dist at her last turn start:',sorted(pre.items(),key=lambda t:(t[0] is None, t[0])))
