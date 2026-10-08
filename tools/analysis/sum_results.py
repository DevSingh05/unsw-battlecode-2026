import json,sys,statistics as st
# sumj.py tag... : per map, us vs opp: rams(>r300,L>=15,H2H) shedRuns shedSegs qAlive500 qLen500 longest500 tot300 wins
def m(x): x=[v for v in x if v is not None]; return round(st.mean(x),1) if x else None
for tag in sys.argv[1:]:
    rows=json.load(open(f'/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r6/mech/{tag}.json'))
    print(f'== {tag}: map who n | rams shedRuns shedSegs | qAlive500 qLen500 longest500 tot300 | wins | cpuMax')
    for mp in dict.fromkeys(r['map'] for r in rows):
        for who in ('us','b1'):
            R=[r for r in rows if r['map']==mp and r['who']==who]
            ram=sum(1 for r in R if r['qdead'] and r['qdead'][0]>300 and r['qdead'][1]>=15 and 'HeadToHead' in r['qdead'][2])
            print(f"{mp:14s} {'cand' if who=='us' else 'base'} {len(R)} | {ram} {sum(r['shedruns'] for r in R)} {sum(r['shedsegs'] for r in R)} | {sum(r['q_end'] for r in R)} {m([r['qlen_end'] for r in R])} {m([r['max_end'] for r in R])} {m([r['tot300'] for r in R])} | {sum(r['win'] for r in R)} | {max(r['cpu'] or 0 for r in R)}")
