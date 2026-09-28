# Own deaths per 50-round window r200-499 by reason and splits per window. top|ours
import sys
from common import *
from replay_sim import simulate
from collections import Counter,defaultdict
mode=sys.argv[1]; sel=sys.argv[2:]
agg=defaultdict(Counter); n=Counter()
def add(l,G,T):
    n[l]+=1
    for x in G['deaths']:
        if x['team']==T and x['round']>=200:
            r=x['reason']
            if r=='HitHeadToHead': r='H2H_'+('enemy' if (x.get('killer_team') and x['killer_team']!=T) or (x.get('victim_team') and x['victim_team']!=T) else 'ally')
            agg[l][(x['round']//50*50,r)]+=1
    for s in G['splits']:
        if s['team']==T and s['round']>=200: agg[l][(s['round']//50*50,'SPLIT')]+=1
if mode=='top':
    for p,gid,win,a,b in top_games():
        G=simulate(p); add('winner',G,win)
else:
    for d,gid,opp,win,side in pickle.load(open('notes/tools/slithery/meta.pkl','rb')):
        if sel and d not in sel: continue
        G=simulate('replays/%s/%d.replay'%(d,gid)); add('us',G,side); add('them',G,'B' if side=='A' else 'A')
for l in agg:
    print('==',l,'games',n[l])
    rs=sorted({k[1] for k in agg[l]})
    print('%-8s'%'win'+''.join('%14s'%r[:13] for r in rs))
    for w in range(200,500,50): print('%-8d'%w+''.join('%14.1f'%(agg[l][(w,r)]/n[l]) for r in rs))
