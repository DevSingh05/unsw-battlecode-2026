"""Per-game decisive-moment table for our games vs VIB/DEV (argv1 = VIB|DEV, argv2 = comma list of our versions)."""
import sys,pickle,collections,math,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools/midgame'); sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools')
import sim2
RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/top1_vib/'
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/vib4/'
OPP=sys.argv[1]; VERS=sys.argv[2].split(',')
D=pickle.load(open(S+'rows_vib4.pkl','rb'))
out=[]
for gid,rs in sorted(D.items()):
    if len(rs)!=2: continue
    u=[r for r in rs if r['team'] in VERS]; o=[r for r in rs if r['team']==OPP]
    if not u or not o: continue
    u=u[0]; o=o[0]
    g=sim2.simulate(RD+f'{gid}.replay'); rd=dict(g['rounds']); last=g['last_round']; m=g['map']
    T=[t for t in 'AB' if rd[last][t]['total']==u['tot_end'] and rd[last][t]['n']==u['units_end']]
    if len(T)!=1: continue
    T=T[0]; E='B' if T=='A' else 'A'
    qi=[i for i in (0,1) if g['team'][i]==T][0]; eq=1-qi
    def qd(i):
        x=next((x for x in g['deaths'] if x['id']==i),None)
        if not x: return None
        kl=x.get('killer_len') or x.get('victim_len'); st=None
        if 'killer' in x:
            mv=[a for a in g['moves'] if a['id']==x['killer'] and a['round']==x['round']]; st=mv[0]['steps'] if mv else None
        return f"r{x['round']} {x['reason'][:8]} L{x['len']} by L{kl} s{st} d{m.dist(x['head'],m.dragons[i][1][0])}"
    snap=lambda k: rd.get(k)
    def tot(k,t): s=snap(k); return s[t]['total'] if s else '-'
    def lon(k,t): s=snap(k); return s[t]['max'] if s else '-'
    # biggest single-round loss of length for us (h2h) after r250
    big=[(x['round'],x['len'],x.get('killer_len'),x['id']==qi) for x in g['deaths'] if x['team']==T and x['len']>=10 and x['reason']=='HitHeadToHead']
    # collapse round: first round our total < 0.5 * theirs (with theirs >= 20)
    col=next((k for k,s in g['rounds'] if s[E]['total']>=20 and s[T]['total']<0.5*s[E]['total']),None)
    res='W' if u['win'] else 'L'
    oq=qd(qi); tq=qd(eq)
    if u['reason']!='roundLimit':
        if u['win']: dec=f"eliminated them at r{last}; their queen {tq or 'alive'}; tot100 {tot(100,T)}v{tot(100,E)}"
        else: dec=f"our queen {oq or 'alive'}; we fall below half their mass at r{col}; tot100 {tot(100,T)}v{tot(100,E)}; eliminated r{last}"
    elif u['qlen_end']!=u['eqlen_end']:
        if u['win']: dec=f"queen tiebreak {u['qlen_end']}v{u['eqlen_end']}; their queen {tq or 'alive (shorter)'}"
        elif u['qlen_end']==0: dec=f"queen tiebreak 0v{u['eqlen_end']}: our queen {oq}"
        else: dec=f"both queens alive, ours shorter {u['qlen_end']}v{u['eqlen_end']} (longest r300 {lon(300,T)}v{lon(300,E)}, r400 {lon(400,T)}v{lon(400,E)})"
    else:
        late=[b for b in big if b[0]>=400]
        dec=f"longest {u['king_end']}v{o['king_end']} (both queens {'dead' if u['qlen_end']==0 else 'equal'}); tot300 {tot(300,T)}v{tot(300,E)}; lg300 {lon(300,T)}v{lon(300,E)}"+(f"; our L>=10 rammed after r400: {late}" if late else '')
    if len(sys.argv)>3:
        print(f"| {u['team']} | {gid} | {m.name} | {res} | {dec} |"); continue
    why=u['reason'][:5]
    if u['reason']=='roundLimit':
        why='queen' if u['qlen_end']!=u['eqlen_end'] else 'longest'
    out.append((u['team'],gid,m.name[:12],res,why,f"q {u['qlen_end']}v{u['eqlen_end']} lg {u['king_end']}v{o['king_end']} tot {u['tot_end']}v{o['tot_end']}",
                f"tot100 {tot(100,T)}v{tot(100,E)} tot200 {tot(200,T)}v{tot(200,E)} tot300 {tot(300,T)}v{tot(300,E)} lg300 {lon(300,T)}v{lon(300,E)} lg400 {lon(400,T)}v{lon(400,E)}",
                'ourQ:',qd(qi),'| theirQ:',qd(eq),'| col',col,'| ourbig',big[-3:]))
for x in sorted(out,key=lambda x:(x[0],x[3],x[4])): print(*x)
