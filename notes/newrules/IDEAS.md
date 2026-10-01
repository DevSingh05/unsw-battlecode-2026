# New-rule strategy ideas (unswbc 1.2.3), 2026-10-01. Ranked by impact/effort.
Evidence: 11 live losses (battles 828657/829057/829695/829872, replays in scratchpad/nr/L_*.replay) and 2 local v35-v35 games (dilemma s3, schooltime s3).
Scripts: notes/newrules/freeuse.py (multi-step use, pearls/turn, unit curve) and brawl.py (queen fate, kills by mover L/steps).
Key fact, missed by v35 and v36: a head-on kills both dragons whatever their lengths, so a ram's length cost does not matter. Kamikaze reach K(L) = F + (L-2) with F = ceil(L/4).
K is 1 for L2, 2 for L3, 3 for L4, 5 for L5, 8 for L8. The most common live kill is an L3 2-step paid ram (C-- 57/139 on Schooltime 828660, EW 7/13 on Dilemma 829696). v35 assumes reach 1 (MAX_THREAT_REACH); v36 THREAT_FREE assumes F.

1. KREACH threat model (impact HIGH, effort LOW). computeThreats l.2287 and replyEnemyReach l.3191: add a 2nd map, threatK[t] = enemy head reaches t within K(Lvis) steps (BFS with bodies as walls).
   Unseen tail: Lvis >= 3. Queen: hard veto inside K. Others: K tiles cost 1/3 of the full penalty, and only where we can't reply (our own K >= their distance), so they don't turn timid.
   Detection: none needed. Compute: <=61 tiles x <=10 heads, <0.2M. Test: dilemma/trophy/schooltime/default x seeds 1-6 vs v35 (orchestrator batch); count deaths by enemy 2+ step rams with brawl.py.
2. Exact queen kill (impact HIGH, effort LOW-MED). tryRam l.2960: if the enemy queen's head (seg id<=1, team!=ours) is seen at path distance d <= K(myLen) along a body-simulated path
   (tails release 1 per step, an eat holds the tail; each step is checked against the body after the previous step), go now. Skip ramGuard, worth and RAM_MIN_UNITS. Any non-queen unit qualifies.
   Her head doesn't move during our turn, so the kill is certain if the path tiles stay free; enemy bodies that move after us only block. v36 S3 only adds +500 at d<=2.
   Live case: Schooltime 829875 we had 59 units vs their 11 and never killed C--'s L2-3 queen. She lived to r500, and we lost on queen (our longest 36 vs 22). Trophy 829695: the EW queen is still alive.
   Compute: DFS over <=K steps, paths of length <=8 pruned by the BFS distance to her, <1M. Test: count the enemy queen's death round (brawl.py) vs v35 and vs v36 S3.
3. State-phased queen (impact HIGH, effort MED). Fixes v36's elimination deficit (11-29). The queen plays v35 (fights, splits) until the enemy queen is known dead, or until r>=QS_LATE=400.
   After that, QUEEN_SAFE plus a KREACH veto: at that point any living length wins r500. If ours is dead and theirs alive, everyone gets idea 2's bonus with no distance cap (the only way to win r500 short of elimination).
   Detection: a unit that commits idea 2 at d=1 (certain) sets a flag. Allies confirm when the queen's tile shows a corpse or no dragon. Relay it as 1 bit in the existing sonar/beacon word.
   Also infer it when id 1-q isn't seen for 60 rounds while our heads cover her symmetric home. Compute: negligible. Test: an 84-game batch vs v35 (V36 runner), gate win >= .55.
4. Queen self-kill guards (impact MED, LOW). Our queen dies HitSelf at L2 on r7 in a kelp dead end on Dilemma in every game (local s3 and live 829872/829696, both sides). META: 23/42 deaths are self-inflicted.
   Live 829875 r235: our queen was killed head-on by our own L2 (id 131). Split block l.3823: for the queen, k <= myLen-3 (she keeps >=3), no split when her head's dead-end depth >= 1.
   Move loop l.4018: veto tiles with dead-end depth >= her length unless she can reverse. Allies: -300 for ending next to the queen's head (ally K-reach). Test: dilemma/slithery/trauma; check the queen death cause histogram.
5. Cascade opening split (impact MED on brawl maps, effort LOW). EW turns its L12 Dilemma queen into 5 units on r0: SPLIT 9, then the child (it acts the same round) splits 7, then 5, then 3.
   v35 splits 2 per round and needs 6 rounds. 829696: 3 vs 6 units at r10, eliminated at r23. In split block l.3823: if round<=3, myLen>=6 and no enemy within K+2, use k=myLen-2.
   The child's head is the old tail and faces away: check tailHasExit(k). Never on the queen while idea 4 is on. Test: dilemma, trophy, genhold, gen/* (unit count at r10 and r25, plus win rate).
6. Free bonus step for pearls (impact MED, effort LOW; a cheap S5). After the best 1-step (l.3938-4161), if F(myLen)>=2 and a neighbour of the landing tile has a pearl, is outside threatK,
   and leaves >=2 exits, append that step: free +1. Chain up to F. Kings L13+ make 2-4 steps on ~60% of turns for C-- (we do 1) and eat 0.25 vs 0.15/turn (Slithery 829060) and 0.46 vs 0.28 (Portals 828661).
   No gain on Schooltime (0.18 vs 0.19). Fix tryEatSprint's tailFreed overcount first (FREEMOVES section 2; FREE_FIX in v36). Compute <0.1M. Test: pearls/turn by L>=5 (freeuse.py) and longest at r300/r500.
7. Free-step king escape (impact MED, effort MED). tryKingEscape l.3337: try free 2..F step escapes (no cost) before the SPLIT L-2 reverse. That split cost the Maze king ~18 length,
   and on trauma r491 it dropped a queen 33->2. Score: distance to the nearest enemy threatK, plus area >= 3L. Test: maze/trauma/portals, longest at r500 and number of king splits.
8. Single-king feed by r300 (impact MED, effort MED). The live length losses are king losses: 828660 67 vs 32 although our team ate 2502 pearls vs 1088, and 829876 31 vs 26.
   C--'s king turns F=3-4 free steps into reach for corpse feeders. Reuse SYNTHESIS B1: seed by r150-200, merge feed into one king, and use the 6/7 grazing path. Test: longest at r300/400 on schooltime/portals/slithery.
9. REJECTED: an army of medium dragons (L5-8). The head-on trade is 1:1, so an L8 that kills an L2 loses 6 more segments, and every live brawl was won by L2-3 swarms (kill table: L>=5 movers made <2% of kills).
   Use medium size only for kings and foragers (ideas 6-8). Also rejected: hiding the queen inside an ally crowd, because ally heads kill her too (829875).
Order: 1+2 together (one A/B), then 4, 3, 5, 6, 7, 8. Ideas 1-2 and 4-6 are each about 20-60 lines behind new flags in params.hpp (additive).
