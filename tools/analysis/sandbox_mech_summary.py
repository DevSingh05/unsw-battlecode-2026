import json,sys,statistics as st
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r11/mech/'
K=sys.argv[1].split(',') if ',' in sys.argv[1] else ['l4','fe4','t100','t200','t300','max500','n100','n200','box','sb','self','bulk','elim','win']
import os,glob
base={(r['map'],r['seed'],r['side']):r for f in glob.glob(S+'base*.json') for r in json.load(open(f))}
for tag in [a for a in sys.argv[1:] if ',' not in a]:
    rows=json.load(open(S+tag+'.json'))
    P=[(r,base[(r['map'],r['seed'],r['side'])]) for r in rows if (r['map'],r['seed'],r['side']) in base]
    print(f'== {tag} (paired n={len(P)}, cpu max {max(r["cpu"] or 0 for r in rows)}M)  cand / b3')
    print('map            '+' '.join(f'{k:>11s}' for k in K))
    for m in list(dict.fromkeys(r['map'] for r,_ in P))+['ALL']:
        Q=[(a,b) for a,b in P if m=='ALL' or a['map']==m]
        f=lambda k,i: st.mean(x[i][k] for x in Q)
        print(f'{m:14s} '+' '.join(f'{f(k,0):5.1f}/{f(k,1):<5.1f}' for k in K))
