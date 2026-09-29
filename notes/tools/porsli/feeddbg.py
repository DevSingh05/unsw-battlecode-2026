# Probe (no games): bot feed state on sampled feed-eligible dragons. Needs a v28 build with notes/tools/porsli/v28dbg.diff
# applied (debug prints only). Usage: MP=Slithery|Portals NS=80 BIN=path/to/v28dbg python3 notes/tools/porsli/feeddbg.py
import sys,os,collections,random,re
sys.argv=['x',os.environ.get('MP','Slithery'),'0']; __file__=os.path.abspath('notes/tools/porsli/feedbot.py')
exec(open('notes/tools/porsli/feedbot.py').read().split("random.shuffle(cands)")[0])
random.shuffle(cands)
B=os.environ['BIN']
C=collections.Counter(); done=0
simmax={}
for gid in set(c[0] for c in cands[:400]):
    S_=simulate(path_of(gid)); rs_=dict(S_['rounds']); T_=[g for g in gs if g['game']==gid][0]['side']
    for c in cands:
        if c[0]==gid: simmax[(gid,c[2])]=rs_[c[2]-1][T_]['max']
for gid,i,rn,born,k,khead in cands[:400]:
    if done>=int(os.environ.get('NS','40')): break
    m,turns=BV.capture(path_of(gid),i,max(born,rn-40),rn)
    if not turns or turns[-1]['round']!=rn: continue
    outs,dbg=BV.run_bot(B,i,turns); done+=1
    blk=[b for b in dbg.split('\nR') if b.startswith('%d '%rn) or b.startswith('R%d '%rn)]
    f=re.search(r'FEEDDBG (.*)',blk[-1]) if blk else None
    line=f.group(1) if f else 'none'
    d=dict(kv.split('=') for kv in line.split()) if f else {}
    C['feeding=%s'%d.get('feeding')]+=1
    if d.get('feeding')=='0':
        why=[]
        if int(d['kingId'])<0: why.append('noking')
        elif int(d['kingLen'])<int(d['myLen'])+2: why.append('kinglen')
        if d.get('iAmKing')=='1': why.append('iAmKing')
        if int(d['units'])<=4: why.append('units')
        C['why:'+'+'.join(why or ['other'])]+=1
    realmax=simmax[(gid,rn)]
    if d.get('feeding')=='1':
        C['feed_to_real' if int(d['kingLen'])>=realmax-2 else 'feed_to_lesser']+=1
    if d.get('kingSelf')=='1': C['kingSelf_len%s'%('<=5' if int(d['myLen'])<=5 else '>5')]+=1
    if done<=6: print(gid,i,rn,line,'realmax',realmax, outs[-1:])
print(dict(C))
