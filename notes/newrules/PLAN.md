# v37 plan (new rules, unswbc 1.2.3), 2026-10-01. Sources: AUDIT.md, OPPONENTS.md, IDEAS.md, VERIFY.md, notes/queen/V36*.md
Base: cp -r variants/v36 variants/v37 (additive; v36 untouched). Notation: F(L)=ceil(L/4), K(L)=F+(L-2) = kamikaze reach (head-on kills both, so paid steps are free for a rammer).
Defaults: FREE_FIX=1 THREAT_FREE=1 only if the running server A/B (v35 vs v35+FF+TF) is >= v35, else 0 (local S2: .48, neutral). QUEEN_HUNT=1 (S3 .52).
QUEEN_SAFE=0 (S1 cost elim W-L 11-29, win .43). QUEEN_LOOK/ENCLOSE/DIST_VETO=0 and QUEEN_KING=0 (no gain, .40). Steps 3-4 re-use queenSafe() through their own gates.
Each step is one new flag in params.hpp, default 0, cumulative only after it passes. All commands are run from /Users/devsingh/Developer/UNSW_Battlecode, one batch at a time, --jobs 8.
  U: python3 tools/unseen_eval.py "variants/v37:-DFLAG=1" --base variants/v35 --sets gen,lesson,gated,sprint --holdout --seeds 1 --jobs 8   (~276 games)
  P: python3 tools/pool.py "variants/v37:-DFLAG=1" --pool variants/v35 --maps dilemma,trophy,slithery_fight,schooltime,portals,devil --seeds 7 --jobs 8   (84 games)
  Gate: P >= .53 with no map below .40, and U pooled >= .50. Log elim W-L, r500 W-L, queen-alive counts (qrun-style regex: tiebreak lines are "(longer queen, ..)").

## 1 QKILL: exact enemy-queen kill (audit 7, idea 2; CONFIRMED: 829875 lost on queen with 59 vs 12 units, theirs L2-3 for 370 rounds)
tryRam() (v36 main.cpp:3172), right after the units<2 guard (never trade our last unit) and before the generic loop, if !amQueen():
  eq = enemy head seg with s.id<=1 && s.team!=myTeam; if none -> skip. K = F(myLen)+(myLen-2).
  DFS paths p of 1..K steps from myHead, pruned by the BFS distance to eq.tile: sim own body (step i<F frees 1 tail tile, paid step frees 2, eating holds 1;
  a paid step needs curLen>=3), every tile before the last must be empty or a tile our own tail freed this turn; the last tile == eq.tile. Shortest path wins.
  Emit MOVE p and return true; skip worth/ramGuard/RAM_MIN_UNITS/QH_MIN_UNITS. Nothing moves in our turn, so a clear path is a certain kill. CPU <1M (check --sandbox).
  Test U+P, plus brawl.py: the enemy queen's median death round falls and our losses at r500 on "longer queen" go to 0. Server: schooltime, portals, trophy, dilemma.

## 2 QGUARD: queen self-kill and split floor (audit 3+4, idea 4; CONFIRMED: 92/140 of our queens died HitSelf at L<=3, dilemma r7 L2 dead end)
amQueen() only, gated by round>=QG_FROM (default 20) || units>=QG_UNITS (default 5), so the r0-20 brawl split stays v35 (V36c: a passive early queen loses elims).
  normal split (4047-4095), pocket/PF split (~4024) and every k=myLen-2 branch: k = min(k, myLen-QG_MIN) with QG_MIN=5 (2 free steps); not viable if k<2.
  trapped reverse split (4496): queen splits only when bestD<0. Move loop: veto a step into a dead end whose depth >= her length unless she can reverse out.
  Allies (non-queen): -300 for ending a step with our queen's head inside their own K (829875 r235: our L2 killed our queen).
  Test U+P + qdeaths.py cause histogram (HitSelf at L<=3 should fall); queen alive at r100/r500. Server: dilemma, trophy, slithery_fight.

## 3 KREACH: kamikaze threat reach (audit 5, idea 1; CONFIRMED: 97/179 head-on deaths of our L5+ started at distance 2-3, killers median L3)
computeThreats (2518-2535) and replyEnemyReach (3409): paidReach = min(F(Lv)+max(0,Lv-2), KR_CAP=4) (unseen tail: Lv>=3).
  Apply only when myLen>=5 or amQueen() (L2-4 trades are 1:1 and v35 wins them; VERIFY: elim kill rates are even). Paid tier x THREAT_PAID_MULT (0.33);
  for the queen it is full strength (no QUEEN_SAFE needed). Test U+P + brawl.py: deaths of our L5+ to 2-3 tile rams per game. Server: schooltime, portals, devil.

## 4 QSTATE: queen-state modes (audit 8; CONFIRMED gap, neither version tracks the enemy queen)
Track: ourQ = queen beacon (v36 qRound/qId path at 1763, un-gated from QUEEN_KING; the queen sends her beacon each turn), dead if silent > QUEEN_ALIVE_MEM.
  theirQ: lastSeen round/tile of enemy id<=1; dead when a unit saw it alive last turn and its head tile is now empty/a pearl, or we executed QKILL at d=1; relay 1 bit in the beacon.
  Modes: ours alive && theirs dead -> queenSafe() on for the queen (r500 is won), and tryRam keeps v35 ramGuard. Ours dead && theirs alive -> QKILL with no K cap:
  units within 12 of theirQ.tile add -QS_HUNT_W(20)*dist to their move score. Both unknown and round>=QS_LATE(400) -> queenSafe() on. Both dead -> v35.
  Test U+P (queen alive at r500, r500 W-L). Server: schooltime, portals, trophy, plus the new safe-spawn maps when they ship.

## 5 ONEKING: stop splitting the leader after r200 (OPPONENTS 1; CONFIRMED: r500 losses longest 39 vs 56, units 15 vs 7; r200 longest 5.3 vs 10.9 in losses, 7.1 vs 6.9 in wins)
Split guard (4047): if round>=OK_FROM(200) && myLen >= kingLen (largest beacon length known) -> no voluntary split (trapped bestD<0 still splits).
  The pocket/king-escape split also needs bestD<0 for it. Test P (schooltime/portals/slithery longest at r300/r500) + U. Server: schooltime, portals, slithery_fight.

## 6 CASCADE: same-round opening split (idea 5; CONFIRMED 829696 3 vs 6 units at r10, elim losses are a growth gap: 8.1 vs 13.0 units at r50)
Split block: if round<=3 && myLen>=6 && no enemy head within K(their L)+2 && tailHasExit(k): k=myLen-2 (queen: myLen-3 under QG). The child acts later this round and repeats.
  Test U (gated/holdout unit count at r10/r25) + P (dilemma, trophy, devil). Server: dilemma, trophy, devil.

## 7 KREACH_KING: big-enemy reach for kings (audit 9+12, medium): lift KING_THREAT_REACH 4 to F(Lv) for Lv>=17; king keep-away (4038) = F(enemy)+1. Test P (portals/schooltime).
Not in v37 yet: FREE_EAT multi-step pearl paths (VERIFY: UNCERTAIN, C-- ate 0.11 vs our 0.16 in 828660) and the free-step king escape (idea 7, unmeasured). Measure both with freeuse.py first.
Server order (after asking): v37 with the passed steps vs v35 on the A/B maps above, 5-game unranked batches, check SERVER_LOCK first.
