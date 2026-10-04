import sys, pickle, os
sys.path.insert(0,'notes/tools')
import replay_sim as S
from multiprocessing import Pool
D='replays/loss_audit2'; P=sys.argv[1]
def build(gid):
    f=f'{D}/{gid}.replay'; pk=f'{P}/{gid}.pkl'
    if os.path.exists(f) and not os.path.exists(pk):
        try:
            g=S.simulate(f); g['map_text']=None
            pickle.dump(g,open(pk,'wb'))
        except Exception as e: print('fail',gid,e,flush=True)
    return gid
if __name__=='__main__':
    ids=[int(x.split('.')[0]) for x in os.listdir(D) if x.endswith('.replay')]
    with Pool(2) as p: p.map(build,ids)
    print('built',len(ids))
