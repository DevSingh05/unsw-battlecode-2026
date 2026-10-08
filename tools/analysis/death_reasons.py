import sys,glob,collections
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools'); import replay_sim as S
from multiprocessing import Pool
def one(f):
    sw=int(f.rsplit('_',1)[1].split('.')[0]); us='B' if sw else 'A'; g=S.simulate(f); c=collections.Counter()
    for d in g['deaths']:
        if d['round']<=150: c[('us' if d['team']==us else 'th',d['reason'])]+=1
    return c
if __name__=='__main__':
    for D in sys.argv[1:]:
        fs=glob.glob(D+'/*.replay')
        with Pool(2) as p: R=p.map(one,fs)
        T=sum(R,collections.Counter()); n=len(fs)
        print(D.split('/')[-1], ' '.join(f"{k[0]}:{k[1]}={v/n:.1f}" for k,v in sorted(T.items())))
