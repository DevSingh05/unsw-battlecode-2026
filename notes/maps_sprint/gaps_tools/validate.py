import sys,pickle,statistics as st; sys.path.insert(0,'notes/tools'); import replay_decode as R
D='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/mapgaps'
data=pickle.load(open(D+'/data.pkl','rb'))
FILES={'Australia':'australia','Islands':'islands','Maze':'maze','Stripes':'stripes','Tower Defense':'tower_defense','Around UNSW':'around_unsw','weakhold':'weakhold'}
def loc(p):
    o=R.load(p); rnd=0;ft=False;sp=[];last=0
    for e in o['events']:
        if e['t']=='roundStart': rnd=e['round'];ft=False;last=rnd
        elif e['t']=='turnStart': ft=True
        elif e['t']=='tileChange' and e['hasPearl'] and not ft: sp.append(rnd)
    return last,sp
for name,fn in FILES.items():
    for s in (1,2):
        last,sp=loc(f'{D}/local/{fn}_{s}.bin')
        # real: spawns in rounds <= last among games lasting >= last; else rate
        full=[sum(1 for r,_ in g['spawns'] if r<=last) for g in data[name] if g['last']>=last]
        rate=[len(g['spawns'])/(g['last']+1) for g in data[name]]
        realR=st.median(full) if full else None
        lr=len(sp)/(last+1)
        print(f"{name:14s} seed{s} local_rounds={last+1} local_spawns={len(sp)} real_median_first{last+1}={realR} (n={len(full)}, range {min(full) if full else '-'}-{max(full) if full else '-'}) ratio={len(sp)/realR if realR else float('nan'):.2f} | rate local {lr:.2f}/rd real median {st.median(rate):.2f}/rd")
