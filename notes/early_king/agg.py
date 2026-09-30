import json, os, statistics as st, collections
SP=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(SP+'/meas.json'))
RS=['200','300','400','450','F']
def med(v): v=[x for x in v if x is not None]; return f"{st.median(v):.0f}" if v else '-'
short={'Schooltime':'Sch','Portals':'Por','Slithery Fight':'Sli','Queen Of Spades':'QoS'}
print("map W/L  n | longest us/opp @200 300 400 450 final | units us/opp @300 450 F")
for mp in short:
  for grp,f in (('W',lambda r:r['win']),('L',lambda r:not r['win']),('all',lambda r:True)):
    g=[r for r in M if r['map']==mp and f(r)]
    if not g: continue
    L=' '.join(f"{med([r['snap'][R] and r['snap'][R][0] for r in g])}/{med([r['snap'][R] and r['snap'][R][2] for r in g])}" for R in RS)
    U=' '.join(f"{med([r['snap'][R] and r['snap'][R][1] for r in g])}/{med([r['snap'][R] and r['snap'][R][3] for r in g])}" for R in ('300','450','F'))
    print(f"{short[mp]} {grp:3s} {len(g):3d} | {L} | {U}")
# fraction where opp longest>=17 at r300, and where we are behind at r300
for mp in short:
  g=[r for r in M if r['map']==mp and r['snap']['300']]
  a=sum(r['snap']['300'][2]>=17 for r in g); b=sum(r['snap']['300'][0]>=17 for r in g)
  behind=[r for r in g if r['snap']['300'][0]<r['snap']['300'][2]]; ahead=[r for r in g if r['snap']['300'][0]>=r['snap']['300'][2]]
  wr=lambda x: f"{sum(r['win'] for r in x)}/{len(x)}"
  print(short[mp], f"opp>=17@300 {a}/{len(g)} us>=17@300 {b}/{len(g)} | win when behind@300 {wr(behind)} ahead {wr(ahead)}")
  behind=[r for r in g if r['snap']['400'] and r['snap']['400'][0]<r['snap']['400'][2]]; ahead=[r for r in g if r['snap']['400'] and r['snap']['400'][0]>=r['snap']['400'][2]]
  print('   @400 win behind', wr(behind),'ahead',wr(ahead))
print(collections.Counter((short[r['map']],r['ver'],r['win']) for r in M))
print(collections.Counter(r['end'] for r in M))
# per-opp final
for mp in short:
  print(mp, sorted((r['opp'][:8], 'W' if r['win'] else 'L', r['snap']['300'][0] if r['snap']['300'] else None, r['snap']['300'][2] if r['snap']['300'] else None, r['snap']['F'][0], r['snap']['F'][2]) for r in M if r['map']==mp))
