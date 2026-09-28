import sys, os, json, pickle, glob
ROOT='/Users/devsingh/Developer/UNSW_Battlecode'
sys.path.insert(0, ROOT+'/notes/tools')
from replay_sim import simulate
SP=os.path.dirname(os.path.abspath(__file__))
CD=SP+'/cache'
def sim(path):
    key=CD+'/'+path.replace('/','_')+'.pkl'
    if os.path.exists(key): return pickle.load(open(key,'rb'))
    g=simulate(path); pickle.dump(g,open(key,'wb')); return g

def final(g):
    return g['rounds'][-1][1]

def ours():
    """list of (label, path, our side, win)"""
    out=[]
    L=json.load(open(ROOT+'/replays/v7/ledger.json'))
    for x in L:
        if x['map']=='Portals':
            out.append(('v7',ROOT+f"/replays/v7/{x['game']}.replay",x['side'],x['win'],x['opp']))
    for d in ['ch1','ch2','ch3','ch5','ch6','ch8']:
        try: S=json.load(open(ROOT+f'/replays/{d}/summary.json'))
        except: continue
        for x in S:
            if x.get('map')!='Portals': continue
            p=ROOT+f"/replays/{d}/{x['id']}.replay"
            if not os.path.exists(p): continue
            g=sim(p); f=final(g)
            side=None
            for T in 'AB':
                if f[T]['max']==x['us']['longest'] and f[T]['n']==x['us']['dragonCount']: side=T
            out.append((d,p,side,x['win'],x['opp']))
    return out

def tops():
    out=[]
    for sub in ['permap','kings']:
        for x in json.load(open(ROOT+f'/notes/replays/{sub}/index.json')):
            if x['mapName']=='Portals':
                p=ROOT+f"/notes/replays/{sub}/{x['id']}.replay"
                if os.path.exists(p): out.append((sub,p,x['winner'].upper(),x['a']['name'],x['b']['name']))
    return out
if __name__=='__main__':
    for o in ours(): print(o)
    for o in tops(): print(o)
