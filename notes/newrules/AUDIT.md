# v35 main.cpp audit vs 1.2.3 rules (queens, ceil(L/4) free steps), 2026-10-01
Format: file:line | v35 assumes | the new rule means | severity | fix | v36 status. Sources: RULES_2026-10-01.md, queen/{FREEMOVES,PLAN,V36,V36b,V36c,DEATHS,META}.md, v35 and v36 source (read only).
Key fact: max steps = F+(L-2), F=ceil(L/4). For L<=4 this equals the old L-1, so a small enemy's kamikaze reach is unchanged. What changed: L>=5 moves 2+ steps for free (L5-8: 2, L9-12: 3, L13+: 4+). In a head-on the rammer dies anyway, so paid steps cost it nothing.

## Fatal (queen dies or throws the r500 tiebreak)
1. main.cpp:2092-2108 shouldFeed + 3606-3651 feed suicide (and 2224-2266 tryConsFeed, inert while CONS_R=0). No id check, so a queen at L2-3 with a king heard >= L+2 after FEED_START=330 walks into her own neck. A dead queen counts as 0. Fix: `if (w.myId<=1) return false;` at the top of shouldFeed and tryConsFeed. v36: fixed (`!queenSafe()`, 3832/3836).
2. main.cpp:2972 tryRam: `worth = theirs>=myLen || myLen<=RAM_MAX_OWN_LEN(3)`. v35 splits the queen down to L2-3, so she rams any head, and a head-on kills both (DEATHS: 18/42 v35 queen deaths were her own move). Fix: the queen never rams, except a last-resort ram on the enemy queen. v36: fixed (3173 queenSafe return).
3. main.cpp:4175-4185 trapped reverse split (and 3430-3441 king-escape split). SPLIT L-2 leaves the head part, which keeps the id (the QUEEN), at L2 inside the trap, and the bulk leaves as a non-queen. Fix: for id<=1, skip unless bestD<0 (certain death anyway). Otherwise take the best-depth move or a multi-step exit (O5). v36: the king-escape split is blocked (3659). The trap split is blocked only when threatAt[myHead]>0 (4496), so a "bestDepth<4, best<-100" pocket still strands her at L2. OPEN.
4. main.cpp:3816-3866 growth split (SPLIT_CHILD=2, SPLIT_LEN=4) plus the PF/tip `k=myLen-2` paths (3739, 3795, 3846, 3858). The queen gets cut to L2 over and over. At L2 she has F=1 and can't pay, so she can never dodge 2 tiles, and she loses "longer queen" against any surviving queen of L3+. Fix: id<=1 keeps >=5 (F=2) once units>=4: k=min(k, L-5), no `k=L-2` branches. v36: not fixed. QUEEN_MINLEN=2, and the >=3 floor (4079) applies only to queenEarly, which is off at QS_FROM=0.

## High
5. main.cpp:2321-2322 computeThreats `reach=min(max(1,visLen-1), myLen>=8?4:1)`. Any dragon below L8 (the queen included) sees only 1-tile threats, but L>=5 enemies ram from 2 for free and L3-4 from 2-3 by paying. This fits the elimination losses (Dilemma x2, Trophy). Fix: reach=F(Lv) at full penalty, plus a paid tier up to F+Lv-2 at about 1/3 penalty. Uncapped for the queen. v36: THREAT_FREE (cap 2 for small dragons, paid tier to F+2). Queen uncapped, but her paid tier stops at F+1, below the true kamikaze reach of L3-4 enemies (2-3).
6. main.cpp:4022 the threat penalty is 12 for myLen<6 (30 outnumbered). A queen at L2-3 shrugs off a ram threat. Fix: 300 for the queen, plus a hard veto when a safe step exists. v36: fixed (QUEEN_THREAT_PEN, veto at 4453).
7. main.cpp:2960-3010 tryRam has no queen value: val=40+3*theirs-2*myLen, and RAM_GUARD/RAM_GUARD_LOCAL (2973-2981) block even trades. Killing the enemy queen is worth more than any length. Fix: target id<=1 => skip the guards, +500. v36: QUEEN_HUNT (3186). Only from distance <=2 (see O3).
8. No queen-state mode anywhere (the win logic is all "longest", 1912-1960). Under 1.2.3: ours alive + theirs dead => r500 is won, so avoid elimination (no feeding suicides, fewer rams). Ours dead + theirs alive => r500 is lost, so go all-in for elimination and hunt the queen. Both dead (45/50 live games) => v35 longest logic is right. Fix: queen beacon (v36 queenAlive, QUEEN_ALIVE_MEM) plus an enemy-queen last-seen tracker that drives the mode. v36: partial (queenAlive only for QUEEN_KING=0).

## Medium
9. main.cpp:2321/3211 KING_THREAT_REACH=4 cap. Enemies of L>=17 (F=5) ram our king for free from 5. Fix: reach=F(Lv) uncapped for kings (cost is tiny). v36: non-queen kings still capped at 4 (2533).
10. main.cpp:2323-2338/3195-3209 THREAT_TAIL_UNKNOWN=2. The 7x7 view clips big bodies, so F is understated (an L20 seen as 7 segments gives F=2, not 5). Fix: Lv=max(visLen, beacon/last-seen length, 9 for a king's view). v36: Lv>=3 (non-queen) / 4 (queen). Still low.
11. main.cpp:3339-3410 tryKingEscape. tailFreed adds +1 on k>0 (3400), but the true +1 is only for k>=F, so n=3 can step onto the still-occupied seg L-3 (HitSelf). It also charges ESC_SPRINT_COST*(n-1) when n<=F is free, caps n at 3 and needs L>=8. Fix: k>=F, cost max(0,n-F), n<=F+1, allow L>=5. v36: FREE_FIX done. n<=3 and the L>=8 gate stay (QUEEN_ESCAPE=0).
12. main.cpp:4038 KING_V2 keep distance 3-4 is fixed. Fix: keep=F(Le)+1 per enemy head (an L13+ enemy needs 5+). v36: not fixed.
13. main.cpp:1224-1330 surviveDepth: one step = one turn, freeOther[v]<=t. That holds for v35's 1-step moves. It goes wrong once we take multi-step moves (bodies "clear" too early). v36: FREE_SURVIVE (ceil(t/F)).

## Low / inert
14. main.cpp:2900/2925/2938 tryEatSprint (EAT_SPRINT=0): net=eaten-(steps-1), and tailFreed overcounts, which is a self-kill if the sprint is enabled. It also needs pearls on every step after step 1. v36: net/tailFreed fixed.
15. main.cpp:3191-3330 REPLY_SEARCH=0 (inert): 1-step enemy replies only, capped at 4. Should be F-step replies if it is ever revived.
16. main.cpp:1932 CROWN_INHERIT=5, 1954 iAmKing, trauma.hpp:213-222 TRA_PENKING (queen 0 = pen king at (4,15): this lines up). A non-queen king is only tiebreak #2. Keep it as the fallback for the both-queens-dead case. v36 QUEEN_KING=1 hurt schooltime 0/6, so leave it off.
17. main.cpp:1309 ESCAPE_SPLIT in surviveDepth: the queen "escapes" by splitting, but she stays the head piece. Gate it on id>1.
18. main.cpp:2365 TAIL_THREAT: a split child moves later the same round with F(k) steps, not 1. Minor.
19. main.cpp:4261 catch fallback, and 1405 emitMove, always 1 step. Correct, but they waste F-1 free steps (O1).

## Missed opportunities (free steps), none in v36 yet
O1. FREE_PATH (PLAN S5): L>=5 enumerates paths of up to F steps (<=484 for F=5). Each free step onto a pearl is +1, so an L13+ king eats up to 4 pearls a turn. This is the main lever for the length losses (Schooltime 32 vs 67, Portals 45 vs 60).
O2. Free dodge: any L>=5 (the queen at L5+ included) that is threatened takes 2 steps to an unthreatened tile at no cost. Today only L>=8 kings, and only when every 1-step move is threatened.
O3. Ram/hunt reach: free from d<=F, and as a kamikaze from d<=F+L-2 (the rammer dies, so payment is moot). An L5 hunter reaches the enemy queen from 3-5 tiles. v35/v36 stop at d2.
O4. Pearl races: we move F tiles per turn toward a contested pearl, while L2-4 enemies move 1. Re-run the pearl BFS race with speed F.
O5. Trapped: before a reverse split, search 2..F+1 step exits (step 1 alone looks lethal, but the path clears the pocket).
O6. Queen at L5-8 (F=2): she dodges every 1-tile threat and outruns L2-4 swarms. That argues for a queen floor of 5 (item 4), not 2.
Priority: 3, 4 (queen open bugs) -> 8 (mode) -> O1/O2 (FREE_PATH plus dodge) -> 9, 10, 12. Items 1, 2, 5, 6, 7, 11, 13, 14 are already in v36.
