"""Oct 5 VIB profile table: VIB rows vs us (oct5), vs FTM/SSS/DEV (oct5), and Oct 4 VIB vs us (vib4 rows) for contrast."""
import pickle,statistics as st,collections,math
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/'
R5=pickle.load(open(S+'vib5/rows_vib5.pkl','rb'))
try: R4=pickle.load(open(S+'vib4/rows_vib4.pkl','rb'))
except Exception: R4={}
US={'f1','cm1','b3','k2','US'}
def groups(R,tag):
    g=collections.defaultdict(list)
    for gid,rs in R.items():
        for r in rs:
            if r['team']!='VIB': continue
            o=r['opp']
            key='vs us' if (o in US or o in ('v61','v69','c1','m1','m2','b1','q1','amb','old')) else 'vs '+('top' if o in('FTM','SSS','DEV') else 'other')
            if key=='vs other': continue
            g[f'{tag} {key}'].append(r)
    return g
G={}; G.update(groups(R5,'oct5')); G.update(groups(R4,'oct4'))
med=lambda a: round(st.median(a),1) if a else None
def ms(rs,f):
    v=[f(r) for r in rs]; v=[x for x in v if x is not None]; return med(v)
rows=[
 ('n games',lambda rs:len(rs)),
 ('VIB win %',lambda rs:round(100*sum(r['win'] for r in rs)/len(rs))),
 ('queen never split %',lambda rs:round(100*sum(1 for r in rs if not r['qsplits'])/len(rs))),
 ('queen first split (median)',lambda rs:ms(rs,lambda r:r['q_firstsplit'])),
 ('queen alive at end %',lambda rs:round(100*sum(1 for r in rs if r['qdeath'] is None)/len(rs))),
 ('queen death round (median)',lambda rs:ms(rs,lambda r:r['qdeath'][0] if r['qdeath'] else None)),
 ('queen self/NoValid deaths',lambda rs:sum(1 for r in rs if r['qdeath'] and r['qdeath'][1] in('NoValidAction','HitSelf'))),
 ('queen len alive r100/200/300',lambda rs:'/'.join(str(ms(rs,lambda r,k=k:r['qlen'][k] or None)) for k in (100,200,300))),
 ('queen is king at end %',lambda rs:round(100*sum(r['king_is_q'] for r in rs)/len(rs))),
 ('units r50/100/200/300',lambda rs:'/'.join(str(ms(rs,lambda r,k=k:r['units'][k])) for k in (50,100,200,300))),
 ('total r50/100/200/300',lambda rs:'/'.join(str(ms(rs,lambda r,k=k:r['tot'][k])) for k in (50,100,200,300))),
 ('opp total r100/200/300',lambda rs:'/'.join(str(ms(rs,lambda r,k=k:r['etot'][k])) for k in (100,200,300))),
 ('longest r100/200/300/400',lambda rs:'/'.join(str(ms(rs,lambda r,k=k:r['longest'][k])) for k in (100,200,300,400))),
 ('first L10 / L20 round',lambda rs:f"{ms(rs,lambda r:r.get('max10'))}/{ms(rs,lambda r:r.get('max20'))}"),
 ('kills per game',lambda rs:ms(rs,lambda r:r['killcat'].get('n',0))),
 ('kill steps 1/2/3/4+ (mean)',lambda rs:'/'.join(str(round(sum(r['killcat'].get(f's{k}',0) for r in rs)/len(rs),1)) for k in (1,2,3,4))),
 ('paid kills / paid-ate kills (mean)',lambda rs:f"{round(sum(r['killcat'].get('paid',0) for r in rs)/len(rs),1)}/{round(sum(r['killcat'].get('paid_ate',0) for r in rs)/len(rs),1)}"),
 ('queen kills (enemy queen killed by VIB) %',lambda rs:round(100*sum(1 for r in rs if r['eq_killed'])/len(rs))),
 ('VIB heads within 4 of enemy queen (hunt_q)',lambda rs:ms(rs,lambda r:r['hunt_q'])),
 ('... vs other enemy heads (hunt_o)',lambda rs:ms(rs,lambda r:r['hunt_o'])),
 ('feeding NoValidAction per game',lambda rs:ms(rs,lambda r:sum(v for (k,b),v in r['feed'].items() if k=='NoValidAction'))),
 ('feeding HitSelf per game',lambda rs:ms(rs,lambda r:sum(v for (k,b),v in r['feed'].items() if k=='HitSelf'))),
 ('splits per game / stillborn r100',lambda rs:f"{ms(rs,lambda r:r['splits'])}/{ms(rs,lambda r:r['stillborn_r100'])}"),
 ('eat60 in enemy half / all',lambda rs:f"{ms(rs,lambda r:r['eat60_en'])}/{ms(rs,lambda r:r['eat60'])}"),
]
keys=[k for k in ('oct5 vs us','oct5 vs top','oct4 vs us','oct4 vs top') if k in G]
print('| metric | '+' | '.join(keys)+' |'); print('|---'*(len(keys)+1)+'|')
for name,f in rows:
    out=[]
    for k in keys:
        try: out.append(str(f(G[k])))
        except Exception as e: out.append('?')
    print(f'| {name} | '+' | '.join(out)+' |')
# bulk split share r100-300 not in rows; per-map VIB win vs us oct5
c=collections.defaultdict(lambda:[0,0])
for r in G['oct5 vs us']:
    c[r['map']][0]+=r['win']; c[r['map']][1]+=1
print('VIB vs us oct5 by map:',{k:f'{v[0]}/{v[1]}' for k,v in sorted(c.items())})
