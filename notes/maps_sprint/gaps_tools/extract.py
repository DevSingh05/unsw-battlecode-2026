import sys,glob,json,pickle; sys.path.insert(0,'notes/tools'); import replay_decode as R
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/mapgaps'
games=json.load(open(S+'/games.json'))
out={}
for name,ids in games.items():
    L=[]
    for i in ids:
        o=R.load(f"{S}/{name.replace(' ','_')}_{i}.bin")
        rnd=0; ft=False; sp=[]; pe=[]; last=0
        for e in o['events']:
            t=e['t']
            if t=='roundStart': rnd=e['round']; ft=False; last=rnd
            elif t=='turnStart': ft=True
            elif t=='tileChange':
                if e['hasPearl'] and not ft: sp.append((rnd,e['tile']))
                pe.append((rnd,e['tile'],e['hasPearl'],ft))
        L.append(dict(id=i,seed=o['seed'],last=last,spawns=sp,tc=pe,map=o['map']))
    out[name]=L
    print(name,[ (g['last'],len(g['spawns'])) for g in L])
pickle.dump(out,open(S+'/data.pkl','wb'))
