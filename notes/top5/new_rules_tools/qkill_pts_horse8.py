import pickle,subprocess,sys,re,json
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/top4/horse/'
R=pickle.load(open(S+'prof.pkl','rb'))
defs=sys.argv[1:]  # e.g. QE_KR=1
out=[]
for gid,x in sorted(R.items()):
    if not x: continue
    m=x['meta'];lab=m['lab'];H='A' if lab['A']=='HORSE' else 'B';O='B' if H=='A' else 'A'
    if lab[O] not in ('b4','kf1') or m['at']<'2026-10-06T18:00': continue
    for k in x[H]['kills']:
        if not k['vq'] or k['round']>=100: continue
        r=k['round']
        cmd=['python3','tools/decision_replay.py','show',str(gid),'--src',S+'bot','--dragon','q','--side',O,'--round',str(max(1,r-3)),'--to',str(r)]
        for d in defs: cmd+=['-D',d]
        p=subprocess.run(cmd,capture_output=True,text=True)
        lines=[l.strip() for l in p.stdout.splitlines() if 'server:' in l]
        res='HW' if m['winner']==H else 'HL'
        out.append((gid,m['map'],res,r,k['kl'],k['steps'],lines))
        print(gid,m['map'][:10],res,'r',r,'kl',k['kl'],'st',k['steps'],flush=True)
        for l in lines: print('   ',re.sub(r'\s+',' ',l))
json.dump(out,open(S+'pts_'+('_'.join(defs) or 'off')+'.json','w'))
