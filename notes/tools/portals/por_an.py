import sys, os, statistics as st, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from por_load import *
sys.path.insert(0, ROOT+'/tools')
from genmaps import parse
import pathlib
M=parse(pathlib.Path(ROOT+'/maps/portals.map'))
W,H=M['w'],M['h']
def gap(t): i=t[1]*W+t[0]; return (M['gmin'][i],M['gmax'][i])
HOT={(15,1),(15,3),(15,5),(15,7),(16,8),(16,10),(16,12),(16,14)}
def med(a): return st.median(a) if a else float('nan')
CK=[50,100,150,200,250,300,350,400,450,499]
def team_stats(g,T):
    R=dict(g['rounds'])
    s={}
    s['longest']=[R[r][T]['max'] if r in R else None for r in CK]
    s['units']=[R[r][T]['n'] if r in R else None for r in CK]
    s['total']=[R[r][T]['total'] if r in R else None for r in CK]
    fin=g['rounds'][-1][1][T]
    s['final']=fin['max']; s['final2']=fin['lens'][1] if len(fin['lens'])>1 else 0
    e=[x for x in g['eats'] if x['team']==T]
    s['eat_hot']=sum(1 for x in e if x['corpse'] is None and x['tile'] in HOT)
    s['eat_box']=sum(1 for x in e if x['corpse'] is None and x['tile'] not in HOT and gap(x['tile'])[1]>0)
    s['eat_corpse']=sum(1 for x in e if x['corpse'] is not None)
    s['eat_other']=sum(1 for x in e if x['corpse'] is None and gap(x['tile'])[1]==0)
    s['eat_win']=[sum(1 for x in e if x['corpse'] is None and b<=x['round']<b+100) for b in range(0,500,100)]
    s['hot_win']=[sum(1 for x in e if x['corpse'] is None and x['tile'] in HOT and b<=x['round']<b+100) for b in range(0,500,100)]
    d=[x for x in g['deaths'] if x['team']==T]
    s['deaths']=len(d)
    s['death_reason']=collections.Counter(x['reason'] for x in d)
    s['big']=[x for x in d if x['len']>=8]
    s['splits']=[sum(1 for x in g['splits'] if x['team']==T and b<=x['round']<b+100) for b in range(0,500,100)]
    for thr in (10,20,30):
        s[f'r{thr}']=next((r for r,snap in g['rounds'] if snap[T]['max']>=thr),None)
    return s
