import sys,glob,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/tools'); import replay_sim as RS
# rams.py tag : every queen H2H death after r300 at L>=15 with the killer (id, len, dist) and who (cand/base)
R6='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/r6'
for rp in sorted(glob.glob(f'{R6}/mech/{sys.argv[1]}/*.replay')):
    g=RS.simulate(rp); side=rp.split('_')[-1][0]
    for d in g['deaths']:
        if d['id'] in (0,1) and d['round']>300 and d['len']>=15 and 'HeadToHead' in d['reason']:
            T=g['team'][d['id']]; who='cand' if T==side else 'base'
            print(os.path.basename(rp), who, 'r',d['round'],'L',d['len'],'killer',d.get('enemy_near'), 'by', d.get('by', d.get('killer')))
