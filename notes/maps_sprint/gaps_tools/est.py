import pickle,sys,collections
sys.path.insert(0,'/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/mapgaps')
from stats import data,hdr,mir
def samples(name):
    G=data[name]; W,H,sym=hdr(G[0]['map'])
    key=lambda t: min(t,mir(t,W,H,sym))
    S=collections.defaultdict(list); C=collections.defaultdict(list)  # clean samples, censored lower bounds
    cnt=collections.Counter()
    for g in G:
        end=g['last']
        # per class: timeline of pearl counts per tile
        fir=collections.defaultdict(list)
        for r,t in g['spawns']:
            k=key(t)
            if not fir[k] or fir[k][-1]!=r: fir[k].append(r)
        # pearl state changes per tile in order
        tcs=collections.defaultdict(list)
        for r,t,h,ft in g['tc']: tcs[key(t)].append((r,t,h,ft))
        allk=set(key((x,y)) for x in range(W) for y in range(H))
        for k in allk:
            if k not in fir: C[k].append(end+1)
        for k,fr in fir.items():
            cnt[k]+=len(fr)
            tiles={k,mir(k,W,H,sym)}
            # rounds (start-of-round) where all class tiles hold pearl -> blocked
            state={t:0 for t in tiles}; blocked=set(); ev=tcs[k]; i=0
            for r in range(0,end+2):
                # state at start of round r tick = state after all events of rounds < r
                while i<len(ev) and ev[i][0]<r: state[ev[i][1]]=ev[i][2]; i+=1
                if all(state.values()): blocked.add(r)
            prev=None
            for f in fr:
                if prev is None:
                    if not any(b<f for b in blocked): S[k].append(f+1)
                else:
                    if not any(prev<b<f for b in blocked): S[k].append(f-prev)
                prev=f
            if not any(b>prev for b in blocked): C[k].append(end-prev)
    return W,H,sym,S,C,cnt
if __name__=='__main__':
    W,H,sym,S,C,cnt=samples(sys.argv[1])
    for k in sorted(S, key=lambda k:(k[1],k[0])):
        s=sorted(S[k]); print(k,cnt[k],len(s),s[:3],s[-4:],'cens',max(C[k]) if C[k] else None)
