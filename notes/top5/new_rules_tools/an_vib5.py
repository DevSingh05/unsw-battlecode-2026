"""Oct 5 Vibing++ study: per-game rows via an_vib4.analyse on replays/vib_oct5 (our build label from ours_vs_vib.json)."""
import sys,json,pickle,os
sys.path.insert(0,'/Users/devsingh/Developer/UNSW_Battlecode/notes/top5/new_rules_tools')
import an_vib4 as A
S='/private/tmp/claude-501/-Users-devsingh-Developer-UNSW-Battlecode/4107a3b1-a08f-4826-9eaa-522a1a1ebd84/scratchpad/vib5/'
A.RD='/Users/devsingh/Developer/UNSW_Battlecode/replays/vib_oct5/'
BUILD={r['id']:r['build'] for r in json.load(open(S+'ours_vs_vib.json'))}
CUR=[None]
A.usver=lambda at: BUILD.get(CUR[0],'US')
A.SHORT.update({'dev test 1 :P':'DEV'})
if __name__=='__main__':
    G=json.load(open(A.RD+'sample.json'))
    cache=S+'rows_vib5.pkl'
    rows=pickle.load(open(cache,'rb')) if os.path.exists(cache) else {}
    for gm in G:
        if gm['id'] in rows or not os.path.exists(A.RD+f"{gm['id']}.replay"): continue
        CUR[0]=gm['id']
        try: rows[gm['id']]=A.analyse(gm)
        except Exception as e: print('fail',gm['id'],e); rows[gm['id']]=[]
        pickle.dump(rows,open(cache,'wb'))
    print(len(rows))
