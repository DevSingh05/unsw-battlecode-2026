import json, os, collections, statistics as S
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/kings')
G = json.load(open(os.path.join(RD, 'kings_metrics.json')))
def med(x):
    x=[v for v in x if v is not None]; return round(S.median(x),1) if x else None
for mp in ['Schooltime','Portals','Slithery Fight','Queen Of Spades']:
    gs=[g for g in G if g['map']==mp]
    print('='*20, mp, len(gs), 'games; ends', collections.Counter(g['end'] for g in gs))
    for g in gs:
        lin=g['lineage']
        print(f"{g['id']} {g['W'][:12]:12s} beat {g['L'][:12]:12s} {g['end'][:5]} r{g['last']}")
        print(f"   maxW {g['curveW']}\n   maxL {g['curveL']}\n   kingW{g['king_len_at']} 2nd {g['secondW']}")
        print(f"   unitsW {g['unitsW']} unitsL {g['unitsL']}  final {g['final_units']} lensW {g['final_lens_W']}")
        print(f"   lineage {lin} lead_from {g['king_lead_from']} bigsplits {g['king_splits'][:8]}")
        print(f"   src {g['king_src']}")
        print(f"   move {{{', '.join(f'{k}:{v}' for k,v in g['king_move'].items())}}}")
        print(f"   bigdeaths {[d for d in g['big_deaths']][:10]}")
        F=g['feeders']
        print(f"   feeders {len(F)} lens {collections.Counter(f['len'] for f in F)} reasons {collections.Counter(f['reason'] for f in F)} rounds med {med([f['round'] for f in F])} min {min([f['round'] for f in F],default=None)}")
        print(f"   sonar {g['sonar']}")
    if not gs: continue
    ww=[g for g in gs if g['end']=='roundLimit']
    print('-- medians over roundLimit games', len(ww))
    for key in ['curveW','curveL','king_len_at','secondW','unitsW','unitsL','totalW','totalL']:
        print(f"  {key:12s}", [med([g[key][i] for g in ww]) for i in range(9)])
