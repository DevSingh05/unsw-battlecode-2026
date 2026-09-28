"""Per-game metrics for our v7 games on the weak maps (see notes/10). Writes replays/v7/weakmap.pkl."""
import sys, os, json, pickle, collections
ROOT='/Users/devsingh/Developer/UNSW_Battlecode'
sys.path.insert(0, ROOT+'/notes/tools')
from replay_sim import simulate
MAPS=('Schooltime','Queen Of Spades','Trauma','Prisoners Dilemma')
RS=[25,50,100,150,200,250,300,350,400,450,499]
FS={'Schooltime':330,'Queen Of Spades':330,'Trauma':330,'Prisoners Dilemma':330}
def analyse(gid, us, mapname):
    g=simulate(f'{ROOT}/replays/v7/{gid}.replay')
    m=g['map']; them='B' if us=='A' else 'A'; side={us:'us',them:'them'}
    snap={r:s for r,s in g['rounds']}
    last=g['last_round']
    R={'id':gid,'map':mapname,'last':last,'res':g['result'],'W':m.w,'H':m.h}
    def at(r):
        rr=min(r,last);
        while rr not in snap and rr>0: rr-=1
        return snap.get(rr)
    for k,T in (('us',us),('them',them)):
        R[k]={'n':{},'max':{},'total':{},'second':{}}
        for r in RS:
            s=at(r)
            if s is None or r>last: R[k]['n'][r]=R[k]['max'][r]=R[k]['total'][r]=R[k]['second'][r]=None; continue
            R[k]['n'][r]=s[T]['n']; R[k]['max'][r]=s[T]['max']; R[k]['total'][r]=s[T]['total']
            R[k]['second'][r]=s[T]['lens'][1] if len(s[T]['lens'])>1 else 0
        # dragon rounds
        dr=collections.Counter()
        for r,s in snap.items(): dr[0 if r<100 else (1 if r<300 else 2)]+=s[T]['n']
        R[k]['dr']=dr
        R[k]['eats']=collections.Counter(); R[k]['cause']=collections.Counter(); R[k]['feed']=collections.Counter()
    kingAt={r:(s[us]['king'],s[them]['king']) for r,s in snap.items()}
    maxAt={r:(s[us]['max'],s[them]['max']) for r,s in snap.items()}
    # deaths
    feeders={}
    deathlocs=[]; kingdeaths=[]
    born=g['born']
    for d in g['deaths']:
        k=side[d['team']]; C=R[k]['cause']; rs=d['reason']; L=d['len']
        rnd=d['round']
        # current team longest before death?
        prev=snap.get(rnd-1) or snap.get(rnd)
        teamT=d['team']
        wasKing = prev is not None and d['id'] in prev[teamT]['ids'] and prev[teamT]['ids'][d['id']]>=prev[teamT]['max'] and L>=8
        cat=None
        if rs=='HitHeadToHead':
            if 'killer' in d:  # victim
                cat='h2h_friendly' if d['killer_team']==d['team'] else 'rammed_by_enemy'
            elif 'victim' in d:
                cat='h2h_friendly' if d['victim_team']==d['team'] else 'our_ram'
            else: cat='h2h_unknown'
        elif rs=='HitOtherBody':
            h=d.get('hit')
            if h is None: cat='body_unknown'
            else: cat='body_ally' if h['team']==d['team'] else 'body_enemy'
        elif rs=='HitSelf':
            b=d['body']; mv=d.get('move','')
            neck=False
            if len(b)>=2 and mv:
                dest=m.step(b[0], mv[min(d.get('step_failed',1),len(mv))-1])
                neck = dest==b[1]
            kg=d.get('king')
            feeder = neck and rnd>=200 and kg is not None and kg[1]>=8 and kg[2]<=5 and L<kg[1]
            cat='feed' if feeder else ('self_neck' if neck else 'self_trap')
        elif rs=='HitWall': cat='wall'
        else: cat=rs
        kg=d.get('king')
        if cat in ('wall','NoValidAction') and rnd>=200 and kg is not None and kg[1]>=8 and kg[2]<=5 and L<kg[1]: cat='feed'
        if cat!='feed' and born.get(d['id'],0)>0 and rnd-born[d['id']]<=3: C['stub']+=1
        C[cat]+=1
        C['len_lost_'+cat]+=L
        if cat=='feed': feeders[d['id']]=(rnd,d['team'])
        if k=='us' and cat!='feed': deathlocs.append((d['head'],rnd,cat,L))
        if wasKing or (L>=10):
            killer=None
            if 'killer' in d: killer=(d['killer_team']==d['team'] and 'ally' or 'enemy', d['killer_len'])
            if 'victim' in d: killer=('ally' if d['victim_team']==d['team'] else 'enemy', d['victim_len'])
            if d.get('hit'): killer=(('ally' if d['hit']['team']==d['team'] else 'enemy')+'_body', d['hit']['len'])
            kingdeaths.append({'side':k,'round':rnd,'len':L,'cat':cat,'killer':killer,'head':d['head'],'wasKing':wasKing,'nbrs':d['nbrs']})
    R['deathlocs']=deathlocs; R['kingdeaths']=kingdeaths
    # eats
    for e in g['eats']:
        if e['team'] not in side: continue
        k=side[e['team']]; E=R[k]['eats']; E['all']+=1
        rb=0 if e['round']<100 else (1 if e['round']<300 else 2); E['b%d'%rb]+=1
        if e['corpse'] is None:
            E['spawn']+=1
            if e['gap']==(1,1): E['hot']+=1
        else:
            E['corpse_'+('own' if e['corpse'][1]==e['team'] else 'enemy')]+=1
            if e['corpse'][0] in feeders:
                ft=feeders[e['corpse'][0]][1]
                kk=side[ft]
                kid = kingAt.get(e['round'],(None,None))[0 if ft==us else 1]
                R[kk]['feed']['eaten']+=1
                if e['team']!=ft: R[kk]['feed']['enemy']+=1
                elif e['id']==kid: R[kk]['feed']['king']+=1
                else: R[kk]['feed']['ally']+=1
        # king eats
        kid=kingAt.get(e['round'],(None,None))[0 if e['team']==us else 1]
        if e['id']==kid and e['round']>=250: E['king_eats_250']+=1
    for fid,(r,t) in feeders.items(): pass
    # dropped pearls by feeders
    for d in g['deaths']:
        if d['id'] in feeders: R[side[d['team']]]['feed']['n']+=1; R[side[d['team']]]['feed']['dropped']+=(d['len']+1)//2
    # splits
    for s in g['splits']:
        k=side[s['team']]; R[k].setdefault('splits',collections.Counter())
        R[k]['splits']['n']+=1; R[k]['splits']['b%d'%(0 if s['round']<100 else (1 if s['round']<300 else 2))]+=1
        if s['exits']==0: R[k]['splits']['noexit']+=1
    # max-len curve every 10 rounds
    R['curve']={r:maxAt[r] for r in maxAt if r%10==0}
    R['ncurve']={r:(snap[r][us]['n'],snap[r][them]['n']) for r in snap if r%10==0}
    return R
if __name__=='__main__':
    L=json.load(open(ROOT+'/replays/v7/ledger.json'))
    out={}
    cache=ROOT+'/replays/v7/weakmap.pkl'
    for g in L:
        if g['map'] not in MAPS: continue
        R=analyse(g['game'],g['side'],g['map']); R['win']=g['win']; R['opp']=g['opp']; R['oppElo']=g['oppElo']; R['ranked']=g['ranked']
        out[g['game']]=R; print(g['game'],g['map'],g['win'],R['res'].get('endReason'),flush=True)
    pickle.dump(out,open(cache,'wb'))
