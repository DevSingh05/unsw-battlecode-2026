import pickle,collections
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
out=pickle.load(open(S+'qos.pkl','rb'))
out=[g for g in out if g['src'] in ('v7','ch5','ch6','ch8')]
RS=[25,50,100,150,200,250,300,350,400,450,499]
def snap(G,r):
    best=None
    for rr,s in G['rounds']:
        if rr<=r: best=s
    return best
for g in out:
    G=g['G']; us=g['side']; th='B' if us=='A' else 'A'
    row=[]
    for r in RS:
        s=snap(G,r)
        if s is None or r>G['last_round']+1: row.append('   -   '); continue
        row.append('%2d/%-2d %2d/%-2d'%(s[us]['n'],s[th]['n'],s[us]['max'],s[th]['max']))
    print('%s %d %-14s %s %s r%d'%(g['src'],g['id'],g['opp'][:14],'W' if g['win'] else 'L',G['result']['endReason'][:4],G['last_round']))
    print('   ',' | '.join(row))
