import sys,glob,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools'); import replay_decode as R
by=collections.defaultdict(list)
for f in sorted(glob.glob(sys.argv[1]+'/v51_*_0.replay')):
    o=R.load(f); P={}; rnd=0; lie={}; ages=[]
    for e in o['events']:
        if e['t']=='roundStart':
            rnd=e['round']
            if rnd in (50,100,150): lie[rnd]=len(P)
            if rnd>150: break
        elif e['t']=='tileChange':
            t=tuple(e['tile'])
            if e['hasPearl']: P[t]=rnd
            elif t in P: ages.append(rnd-P.pop(t))
    mp=f.split('/')[-1].split('_')[1]
    ages.sort(); by[mp].append((lie.get(50),lie.get(100),lie.get(150),ages[len(ages)//2] if ages else -1, sum(a<=2 for a in ages)/max(1,len(ages)), len(ages)))
for k,v in by.items(): print(k,v)
