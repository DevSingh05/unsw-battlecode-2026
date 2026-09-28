#!/usr/bin/env python3
"""Turn a .replay into a self-contained HTML player.

usage: replay_html.py GAME.replay OUT.html [--ours A|B] [--title TEXT]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "notes" / "tools"))
from replay_decode import load  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from genmaps import parse  # noqa: E402


def build(path, ours):
    o = load(path)
    tmp = pathlib.Path(path).with_suffix(".map.txt")
    tmp.write_text(o["map"])
    m = parse(tmp)
    tmp.unlink()
    w, h = m["w"], m["h"]
    T = lambda p: p[1] * w + p[0]  # noqa: E731

    team, bodies = {}, {}
    for i, (tm, pts) in enumerate(m["dragons"]):
        team[i] = "AB"[tm]
        bodies[i] = [T(p) for p in pts]
    pearls = set()
    frames, stats = [], []
    deaths = {"A": 0, "B": 0}
    rnd = -1

    def snap():
        ds = [[0 if team[i] == "A" else 1, i, b] for i, b in bodies.items()]
        frames.append({"d": ds, "p": sorted(pearls)})
        st = {}
        for t in "AB":
            ls = [len(b) for i, b in bodies.items() if team[i] == t]
            st[t] = [len(ls), max(ls) if ls else 0, sum(ls), deaths[t]]
        stats.append(st)

    for e in o["events"]:
        t = e["t"]
        if t == "roundStart":
            snap()  # state before this round is played (frame r = after r rounds)
            rnd = e["round"]
        elif t == "dragonUpdate":
            b = bodies.get(e["id"])
            if b is None:
                continue
            hd, tl = T(e["head"]), T(e["tail"])
            if b[0] != hd:
                b.insert(0, hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif t == "dragonSplit":
            bodies[e["parent"]] = [T(p) for p in e["parentBody"]]
            bodies[e["child"]] = [T(p) for p in e["childBody"]]
            team[e["child"]] = e["team"]
        elif t == "dragonDeath":
            if e["id"] in bodies:
                del bodies[e["id"]]
                deaths[team[e["id"]]] += 1
        elif t == "tileChange":
            if e["hasPearl"]:
                pearls.add(T(e["tile"]))
            else:
                pearls.discard(T(e["tile"]))
    snap()

    walls = []  # [x, y, side] side 0=N 3=W ; kelp
    portals = []
    for y in range(h):
        for x in range(w):
            t = y * w + x
            for side, (dx, dy) in ((0, (0, -1)), (3, (-1, 0))):
                v = m["nxt"][t * 4 + side]
                plain = ((y + dy) % h) * w + (x + dx) % w
                if v == -1:
                    walls.append([x, y, side])
                elif v != plain:
                    portals.append([x, y, side])
            # east/south portals (the far side of an edge we already drew is the same edge)
    hot = [t for t in range(w * h) if m["gmax"][t] > 0 and (m["gmin"][t] + m["gmax"][t]) / 2 <= 10]
    spawn = [t for t in range(w * h) if m["gmax"][t] > 0]
    return {
        "name": m["name"], "w": w, "h": h, "walls": walls, "portals": portals, "hot": hot, "spawn": spawn,
        "frames": frames, "stats": stats, "result": o["result"], "ours": ours,
    }


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#0e1116;--panel:#161b22;--ink:#e6edf3;--mute:#8b949e;--rule:#30363d;--ours:#f0883e;--them:#58a6ff;--pearl:#f2f5f7;--kelp:#3fb950;--portal:#d2a8ff;--floor:#131820;--spawn:#18202b;--hot:#233042}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--mute);margin:0 0 16px}
.wrap{display:grid;grid-template-columns:1fr 290px;gap:16px;align-items:start}@media(max-width:900px){.wrap{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:12px}
canvas{width:100%;height:auto;display:block;border-radius:6px;background:var(--floor)}
.ctrl{display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap}
button{background:#21262d;color:var(--ink);border:1px solid var(--rule);border-radius:6px;padding:6px 12px;font:inherit;cursor:pointer}button:hover{border-color:var(--mute)}
input[type=range]{flex:1;min-width:160px;accent-color:var(--ours)}
.round{font-variant-numeric:tabular-nums;min-width:92px;text-align:right;color:var(--mute)}
.team{display:flex;align-items:center;gap:8px;font-weight:600;margin:4px 0 8px}.sw{width:12px;height:12px;border-radius:3px}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}td{padding:3px 0;border-bottom:1px solid var(--rule)}td:last-child{text-align:right}
.legend{color:var(--mute);font-size:12.5px;line-height:1.7}.legend span{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.chart{margin-top:12px}.note{color:var(--mute);font-size:12.5px;margin-top:10px}
.result{margin-top:10px;padding:8px 10px;border-radius:8px;background:#1f2a1f;border:1px solid #2e4a2e}
</style>
</head>
<body><main>
<h1>__TITLE__</h1>
<p class="sub" id="sub"></p>
<div class="wrap">
 <div class="card">
  <canvas id="c"></canvas>
  <div class="ctrl">
   <button id="play">Play</button><button id="slow">&minus;</button><span id="spd" class="round" style="min-width:40px;text-align:center">4x</span><button id="fast">+</button>
   <input id="seek" type="range" min="0" value="0"><span id="rnd" class="round"></span>
  </div>
 </div>
 <div>
  <div class="card" id="teams"></div>
  <div class="card chart"><div class="legend" style="margin-bottom:6px">Dragons alive per round</div><canvas id="ch" height="120"></canvas></div>
  <div class="card chart legend">
   <div><span style="background:var(--ours)"></span>Our bot (v2)</div>
   <div><span style="background:var(--them)"></span>Opponent (v1, older version)</div>
   <div><span style="background:var(--pearl);border-radius:50%"></span>Pearl</div>
   <div><span style="background:var(--kelp)"></span>Kelp wall</div>
   <div><span style="background:var(--portal)"></span>Portal edge</div>
   <div><span style="background:var(--hot)"></span>Fast pearl spawn tile</div>
   <div>Bright square = dragon head. Ring = each team's longest dragon.</div>
  </div>
 </div>
</div>
</main>
<script>
const G=__DATA__;
const W=G.w,H=G.h,F=G.frames,S=G.stats,ours=G.ours,them=ours==="A"?"B":"A";
const css=getComputedStyle(document.documentElement),col=n=>css.getPropertyValue(n).trim();
const C={ours:col('--ours'),them:col('--them'),pearl:col('--pearl'),kelp:col('--kelp'),portal:col('--portal'),floor:col('--floor'),spawn:col('--spawn'),hot:col('--hot')};
const cv=document.getElementById('c'),cx=cv.getContext('2d');
const CELL=Math.max(8,Math.floor(1100/W));cv.width=W*CELL;cv.height=H*CELL;
document.getElementById('sub').textContent=`${G.name} · ${W}×${H} · ${F.length-1} rounds · local test game, our v2 vs older v1`;
const bg=document.createElement('canvas');bg.width=cv.width;bg.height=cv.height;{
 const b=bg.getContext('2d');b.fillStyle=C.floor;b.fillRect(0,0,bg.width,bg.height);
 b.fillStyle=C.spawn;for(const t of G.spawn)b.fillRect((t%W)*CELL,((t/W)|0)*CELL,CELL,CELL);
 b.fillStyle=C.hot;for(const t of G.hot)b.fillRect((t%W)*CELL,((t/W)|0)*CELL,CELL,CELL);
 const lw=Math.max(2,CELL/5);
 const edge=(x,y,s,c)=>{b.fillStyle=c;if(s===0)b.fillRect(x*CELL-lw/2,y*CELL-lw/2,CELL+lw,lw);else b.fillRect(x*CELL-lw/2,y*CELL-lw/2,lw,CELL+lw);};
 for(const[x,y,s]of G.walls)edge(x,y,s,C.kelp);for(const[x,y,s]of G.portals)edge(x,y,s,C.portal);}
function draw(i){
 const f=F[i];cx.drawImage(bg,0,0);
 cx.fillStyle=C.pearl;const r=CELL*0.22;
 for(const t of f.p){cx.beginPath();cx.arc((t%W+0.5)*CELL,(((t/W)|0)+0.5)*CELL,r,0,7);cx.fill();}
 let best={0:null,1:null};
 for(const d of f.d){const L=d[2].length;if(!best[d[0]]||L>best[d[0]][2].length)best[d[0]]=d;}
 for(const[tm,id,b]of f.d){
  const isOurs=(tm===0?"A":"B")===ours,c=isOurs?C.ours:C.them;
  cx.fillStyle=c;cx.globalAlpha=0.55;
  for(let k=1;k<b.length;k++){const t=b[k];cx.fillRect((t%W)*CELL+1,((t/W)|0)*CELL+1,CELL-2,CELL-2);}
  cx.globalAlpha=1;const h=b[0];cx.fillRect((h%W)*CELL,((h/W)|0)*CELL,CELL,CELL);
 }
 for(const k of[0,1]){const d=best[k];if(!d||d[2].length<6)continue;const h=d[2][0];
  cx.strokeStyle=((k===0?"A":"B")===ours)?C.ours:C.them;cx.lineWidth=2;cx.beginPath();cx.arc((h%W+0.5)*CELL,(((h/W)|0)+0.5)*CELL,CELL*1.4,0,7);cx.stroke();}
 document.getElementById('rnd').textContent=`round ${i} / ${F.length-1}`;seek.value=i;
 const st=S[i],row=(t,label,color)=>`<div class="team"><div class="sw" style="background:${color}"></div>${label}</div><table>
<tr><td>Dragons alive</td><td>${st[t][0]}</td></tr><tr><td>Longest dragon</td><td>${st[t][1]}</td></tr>
<tr><td>Total length</td><td>${st[t][2]}</td></tr><tr><td>Deaths so far</td><td>${st[t][3]}</td></tr></table>`;
 let res='';if(i===F.length-1){const R=G.result,win=R.winner===ours?'Our bot wins':'Opponent wins';
  res=`<div class="result">${win} ${R.endReason==='roundLimit'?'on longest dragon at round 500':'by elimination'}: ${R[ours].longest} vs ${R[them].longest}.</div>`;}
 document.getElementById('teams').innerHTML=row(ours,'Our bot',C.ours)+'<div style="height:10px"></div>'+row(them,'Opponent',C.them)+res;
 drawChart(i);}
const ch=document.getElementById('ch'),chx=ch.getContext('2d');
function drawChart(i){const w=ch.width=ch.clientWidth*devicePixelRatio,h=ch.height=120*devicePixelRatio;chx.clearRect(0,0,w,h);
 const max=Math.max(...S.map(s=>Math.max(s.A[0],s.B[0])),1),n=S.length-1;
 for(const[t,c]of[[them,C.them],[ours,C.ours]]){chx.strokeStyle=c;chx.lineWidth=2*devicePixelRatio;chx.beginPath();
  S.forEach((s,k)=>{const x=k/n*w,y=h-4-(s[t][0]/max)*(h-8);k?chx.lineTo(x,y):chx.moveTo(x,y);});chx.stroke();}
 chx.fillStyle='#8b949e';chx.fillRect(i/n*w,0,1.5*devicePixelRatio,h);}
const seek=document.getElementById('seek');seek.max=F.length-1;
let cur=0,playing=false,speeds=[1,2,4,8,16,32],si=2,acc=0,last=0;
seek.oninput=()=>{cur=+seek.value;draw(cur);};
document.getElementById('play').onclick=e=>{playing=!playing;e.target.textContent=playing?'Pause':'Play';if(cur>=F.length-1)cur=0;};
document.getElementById('fast').onclick=()=>{si=Math.min(si+1,speeds.length-1);spd.textContent=speeds[si]+'x';};
document.getElementById('slow').onclick=()=>{si=Math.max(si-1,0);spd.textContent=speeds[si]+'x';};
const spd=document.getElementById('spd');
function tick(ts){if(playing){acc+=(ts-last)/1000*speeds[si]*2.5;while(acc>=1&&cur<F.length-1){cur++;acc--;}if(cur>=F.length-1){playing=false;document.getElementById('play').textContent='Play';}draw(cur);}last=ts;requestAnimationFrame(tick);}
draw(0);requestAnimationFrame(tick);addEventListener('resize',()=>drawChart(cur));
</script>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("out")
    ap.add_argument("--ours", default="A")
    ap.add_argument("--title", default="Battlecode replay")
    a = ap.parse_args()
    data = build(a.replay, a.ours)
    html = PAGE.replace("__TITLE__", a.title).replace("__DATA__", json.dumps(data, separators=(",", ":")))
    pathlib.Path(a.out).write_text(html)
    print(f"wrote {a.out} ({len(html) // 1024} KB, {len(data['frames'])} frames)")


if __name__ == "__main__":
    main()
