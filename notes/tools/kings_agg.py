import json, os, collections, statistics as S
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../replays/kings')
G = json.load(open(os.path.join(RD, 'kings_metrics.json')))
def med(x):
    x=[v for v in x if v is not None]; return round(S.median(x),1) if x else None
def pct(x,q):
    x=sorted(v for v in x if v is not None); return x[min(len(x)-1,int(q*len(x)))] if x else None
for mp in ['Schooltime','Portals','Slithery Fight','Queen Of Spades']:
    gs=[g for g in G if g['map']==mp and g['end']=='roundLimit']
    print('='*10, mp, len(gs))
    # lineage
    for g in gs:
        lin=g['lineage']; us=[s for s in g['king_splits'] if s[3]=='rev']; sh=[s for s in g['king_splits'] if s[3]=='shed']
        print(f"  {g['id']} {g['W'][:10]:10s} origin id{lin[0][0]} born r{lin[0][1]}, {len(lin)-1} U-turn re-IDs {[ (s[0],s[1],s[2]) for s in us][:6]}, sheds {[(s[0],s[1],s[2]) for s in sh][:6]} lead_from {g['king_lead_from']} final {g['curveW'][-1]} vs {g['curveL'][-1]} units {g['final_units']} Lpeak {g['L_peak']}")
    # king source by phase (pearls/round)
    agg=collections.defaultdict(lambda: collections.Counter())
    for g in gs:
        for ph,c in g['king_src_phase'].items():
            for k,v in c.items():
                kk='spawn' if k.startswith('spawn') else k
                agg[int(ph)][kk]+=v
                if k.startswith('spawn'): agg[int(ph)]['sp'+k[5:]]+=v
    n=len(gs)
    for ph in sorted(agg):
        c=agg[ph]; tot=sum(v for k,v in c.items() if not k.startswith('sp['))
        print(f"   phase {ph*100}-{ph*100+99}: king pearls/round {tot/n/100:.2f}  " + ', '.join(f"{k} {v/n:.1f}" for k,v in sorted(c.items(), key=lambda x:-x[1])))
    tsrc=collections.Counter()
    for g in gs:
        for k,v in g['king_src'].items(): tsrc['spawn' if k.startswith('spawn') else k]+=v
    T=sum(tsrc.values()); print('   total king eats/game', round(T/n,1), {k: f"{100*v/T:.0f}%" for k,v in tsrc.items()})
    # movement
    for a in ('200','300','400'):
        ms=[g['king_move'][a] for g in gs if a in g['king_move']]
        if not ms: continue
        print(f"   move r{a}+: n{len(ms)} uniq {med([m['uniq'] for m in ms])} revisit {med([m['revisit'] for m in ms])} bbox {med([m['bbox'][0] for m in ms])}x{med([m['bbox'][1] for m in ms])} disp100 {med([m['disp100'] for m in ms])} d_rich {med([m['d_rich_med'] for m in ms])} d_hot {med([m['d_hot_med'] for m in ms])} en_min {med([m['en_min'] for m in ms])} en_p10 {med([m['en_p10'] for m in ms])} en_med {med([m['en_med'] for m in ms])} le3 {med([m['en_le3_frac'] for m in ms])}")
    # feeders
    F=[f for g in gs for f in g['feeders']]
    print(f"   feeders total {len(F)} per game {len(F)/n:.1f}; len {sorted(collections.Counter(f['len'] if f['len']<10 else '10+' if False else min(f['len'],10) for f in F).items())}")
    print(f"   reasons {collections.Counter(f['reason'] for f in F).most_common()}")
    fs=[f for f in F if f['len']<=6]
    print(f"   small(<=6) {len(fs)}: dist {sorted(collections.Counter(min(f.get('dist',99),9) for f in fs).items())}")
    print(f"   rel (fwd,right) top {collections.Counter(tuple(f['rel']) for f in fs if f.get('rel')).most_common(12)}")
    rel=[f['rel'] for f in fs if f.get('rel')]
    if rel:
        ah=sum(1 for r in rel if r[0]>0); be=sum(1 for r in rel if r[0]<0); si=sum(1 for r in rel if r[0]==0)
        print(f"   ahead {ah} side {si} behind {be} (of {len(rel)})")
    print(f"   round hist {sorted(collections.Counter(f['round']//50*50 for f in F).items())}")
    print(f"   lag med {med([f['lag'] for f in fs])} p75 {pct([f['lag'] for f in fs],.75)}; eaten/drop {sum(f['eaten_by_king'] for f in fs)}/{sum(f['drop'] for f in fs)}; age med {med([f['age'] for f in fs])}")
    print(f"   dist before death: d-5 {med([f['d-5'] for f in fs])} d-10 {med([f['d-10'] for f in fs])} d-20 {med([f['d-20'] for f in fs])} d-40 {med([f['d-40'] for f in fs])}; near_rounds(<=6) med {med([f['near_rounds'] for f in fs])} p75 {pct([f['near_rounds'] for f in fs],.75)}")
    print(f"   move strings {collections.Counter(f['move'] for f in fs).most_common(8)}")
    print(f"   sonar10 med {med([f['sonar10'] for f in fs])}; frac with any {sum(1 for f in fs if f['sonar10'])/max(1,len(fs)):.2f}")
    fb=[f for f in F if f['len']>=7]
    print(f"   big feeders(>=7) {len(fb)}: {[ (f['round'],f['len'],f['reason'],f.get('dist'),f['eaten_by_king']) for f in fb][:12]}")
    # units
    for key in ['unitsW','unitsL']:
        print(f"   {key} {[med([g[key][i] for g in gs]) for i in range(9)]}")
    print('   final W lens', [g['final_lens_W'][:5] for g in gs])
    # loser king fates
    for g in gs:
        print(f"   L {g['L'][:10]:10s} peak {g['L_peak']} bigdeaths {g['L_bigdeaths'][:6]} | W big H2H losses {g['W_bigdeaths_enemy']}")
    for g in gs:
        print(f"   sonar {g['W'][:10]:10s} {g['sonar']['total']} distinct {g['sonar']['distinct']} per-turn {g['sonar']['pings_per_sender_turn']} same4 {g['sonar']['same_value_all_dirs']} senders {g['sonar']['senders']} phase {g['sonar']['by_phase']}")
