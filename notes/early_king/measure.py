import json, sys, os
from multiprocessing import Pool
ROOT='/Users/devsingh/Developer/UNSW_Battlecode'; SP=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT+'/notes/tools/midgame'); sys.path.insert(0, ROOT+'/notes/tools')
from sim2 import simulate
RS=[200,300,400,450]
def one(r):
    G=simulate(r['path']); us=r['side']; th='B' if us=='A' else 'A'
    snaps=dict(G['rounds']); last=G['last_round']
    out={}
    for R in RS+['F']:
        s=snaps[min(R,last)] if R!='F' else G['rounds'][-1][1]
        if R!='F' and R>last: s=None
        out[R]=None if s is None else (s[us]['max'],s[us]['n'],s[th]['max'],s[th]['n'])
    res=G['result'] if isinstance(G['result'],dict) else eval(G['result'])
    ok=(res['winner']==us)==r['win']
    return dict(r, snap=out, last=last, end=res.get('endReason'), ok=ok)
if __name__=='__main__':
    sel=json.load(open(SP+'/sel.json'))
    for r in sel:
        if r['map']=='Portals' and '2026-09-30T02:14'<=r['at'][:16]<'2026-09-30T02:53': r['ver']='v32'
    with Pool(8) as p: res=p.map(one, sel)
    json.dump(res, open(SP+'/meas.json','w'), ensure_ascii=False)
    print(len(res), sum(not x['ok'] for x in res))
