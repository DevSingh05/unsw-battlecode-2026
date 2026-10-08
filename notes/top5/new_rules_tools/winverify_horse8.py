"""For a list of games: our queen id, then verify that dragon flags-off and with -D defs; count mismatches before r100."""
import subprocess,sys,re,json,glob,os
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/top4/horse/'
games=[l.split() for l in open(sys.argv[1]) if l.strip()]   # gid label
defs=sys.argv[2:]
def run(gid,qid,d):
    cmd=['python3','tools/decision_replay.py','verify',gid,'--src',S+'bot','--dragons',qid]
    for x in d: cmd+=['-D',x]
    p=subprocess.run(cmd,capture_output=True,text=True).stdout
    mm=[(int(m.group(1)),m.group(2),m.group(3)) for m in re.finditer(r'mismatch dragon \d+ r(\d+): bot (.+?) vs server (.+?)  ',p)]
    tot=re.search(r'(\d+) turns',p)
    return mm,int(tot.group(1)) if tot else 0
out=[]
for gid,lab in games:
    p=subprocess.run(['python3','tools/decision_replay.py','show',gid,'--src',S+'bot','--dragon','q','--round','1','--to','1'],capture_output=True,text=True).stdout
    m=re.search(r'dragon (\d+) team',p)
    if not m: print(gid,'noq',p[-300:]); continue
    qid=m.group(1)
    base,n=run(gid,qid,[]); new,_=run(gid,qid,defs)
    bset={r for r,_,_ in base}
    ch=[x for x in new if x[0] not in bset]
    early=[x for x in ch if x[0]<100]
    out.append((gid,lab,qid,n,len(base),len(ch),len(early),ch[:3]))
    print(gid,lab,'q',qid,'turns',n,'base_mm',len(base),'changed',len(ch),'changed<r100',len(early),'first',ch[:2],flush=True)
json.dump(out,open(S+'winv_'+os.path.basename(sys.argv[1])+'_'+'_'.join(defs)+'.json','w'))
