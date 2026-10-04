"""Enemy-queen kill opportunities: per game/team, rounds where one of our heads (len>=2) is within Manhattan d of the enemy queen head
at the start of our turn, and whether the queen died to us. Also our queen's death context (portal maps)."""
import sys,json,pickle,collections,statistics as st
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/t5n/'
rows=pickle.load(open(S+'rows_top1.pkl','rb'))
out=collections.defaultdict(lambda:collections.Counter())
for gid,rs in rows.items():
    if not rs: continue
    g=sim2.simulate(RD+f'{gid}.replay'); m=g['map']
    q={g['team'][0]:0,g['team'][1]:1}
    names={}
    # map team letter->name via queen-alive check: rows store team names; recover by qlen_end equality with simulation
    last=g['last_round']; rd=dict(g['rounds'])
    for r in rs:
        for T in 'AB':
            if rd[last][T]['ids'].get(q[T],0)==r['qlen_end'] and rd[last][T]['total']==r['tot_end'] and rd[last][T]['n']==r['units_end']: names[T]=r['team']
    if len(set(names.values()))<2: continue
    for T in 'AB':
        E='B' if T=='A' else 'A'; eq=q[E]; c=out[names[T]]
        c['games']+=1
        # moves of our team with enemy queen nearby
        for a in g['moves']:
            if a['team']!=T or 'move' not in a['act']: continue
            s=rd.get(a['round'])
            if not s or eq not in s['heads']: continue
            d=m.dist(a['head'],s['heads'][eq][0])
            if d<=3:
                L=a['len_before']; reach=-(-L//4)+max(0,L-2)
                c[f'near_d{d}']+=1
                if d<=reach: c['in_reach']+=1
                if any(v==eq for v,_,_ in a['killed']): c['qkill_moves']+=1
        if any(x['id']==eq and x['reason']=='HitHeadToHead' and (x.get('killer_team')==T or x.get('victim_team')==T) for x in g['deaths']): c['eq_h2h']+=1
pickle.dump(dict(out),open(S+'qhunt_top1.pkl','wb'))
for T,c in out.items():
    n=c['games']; print(T,n,{k:round(v/n,2) for k,v in sorted(c.items()) if k!='games'})
