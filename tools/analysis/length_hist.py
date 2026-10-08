import sys,glob,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools'); import replay_sim as S
H=collections.Counter(); n=0
for f in sorted(glob.glob(sys.argv[1]+'/*.replay'))[:int(sys.argv[2]) if len(sys.argv)>2 else 999]:
    sw=int(f.rsplit('_',1)[1].split('.')[0]); us='B' if sw else 'A'
    g=S.simulate(f)
    for r,s in g['rounds']:
        if r in (25,50,75,100):
            q=0 if g['team'][0]==us else 1
            for i,L in s[us]['ids'].items():
                if i!=q: H[(r,min(L,8))]+=1
            n+=1
for r in (25,50,75,100): print(r,[H[(r,L)] for L in range(2,9)])
