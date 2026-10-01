# VERIFY: adversarial check of AUDIT / OPPONENTS / IDEAS (1 Oct, code read + rows.pkl + sim2 on 3 replays)
Rule base (RULES_2026-10-01 l.7,21): max steps = ceil(L/4)+(L-2); head-on kills both regardless of length -> K(L) reach is CONFIRMED.

## AUDIT (fatal/high)
1 Queen feeds herself - CONFIRMED. v35 shouldFeed (2092-2108) has no id check; v36 3836 adds `!queenSafe()` (QS_FROM=0, so on from r0): fixed.
2 Queen rams - CONFIRMED. v35 2972 `worth = theirs>=myLen || myLen<=RAM_MAX_OWN_LEN(3)`; ramGuard can block only when outnumbered. v36 3173 returns early for queenSafe: fixed.
3 Trap reverse split strands queen - CONFIRMED. v36 4496 only skips when `queenSafe() && threatAt[myHead]>0`; SPLIT L-2 leaves the head piece (queen id) at L2. Caveat: with bestD<0 she dies anyway, so the real loss is the `bestDepth<4 && best<-100` branch.
4 Queen split to L2 - CONFIRMED. The `queenEarly()` floor (4079) never applies when QS_FROM=0; the normal split gate (4047) and PF split (4024) have no queen check; QUEEN_MINLEN is defined in params but unused in main.cpp.
5 Small-dragon reach 1 - CONFIRMED in code (v35 MAX_THREAT_REACH=1 below L8; SMALL_SPRINT_THREAT=0). v36 queen paid tier `min(F+1, ...)` = 2 for an L4 (K=3): gap confirmed. The causal claim ("explains Dilemma/Trophy elims") is UNCERTAIN: in the 26 elim losses head-on kills were even (we 16.6/game, they 15.2) and the gap was growth.
6 Threat pen 12 - CONFIRMED (SMALL_THREAT_PEN 12.0, myLen<6); v36 QUEEN_THREAT_PEN 300: fixed.
7 No enemy-queen value - CONFIRMED (no id test in v35 tryRam); v36 hunt is inside tryRam, which tries d1 and d1+d2 only (reach <=2).
8 No queen-state mode - CONFIRMED. No enemy-queen tracking in v35 or v36. v36 queenAlive() tracks only our own queen and only under QUEEN_KING=0 (off), so it is weaker than "partial".
9 (med) King cap 4 - CONFIRMED with caveat: v36 caps the full-penalty reach at 4, but its paid tier extends to F+2 at x0.33.
11 (med) tryKingEscape - CONFIRMED. v35 3400: `tailFreed += ... + (k>0?1:0)` charges step 2 as paid; at F>=2 it over-counts release, so step 3 can enter its own body at index myLen-3.

## OPPONENTS (recomputed from scratchpad/nr/rows.pkl, 140 games)
- 63 losses, 37 at round limit, 26 elim (Trophy 10 / Dilemma 6 / Devil 5) - CONFIRMED.
- r500 losses: longest median 39 vs 56, count 15 vs 7, total 126 vs 124, total higher in 24/37, longest at r200 5.3 vs 10.9, r400 26.5 vs 30.9 - CONFIRMED. (In r500 wins it was 7.1 vs 6.9 at r200, so the early-king gap does separate wins from losses.)
- Multi-step rates (C-- 53.5% / 60.5%, us 0.1% / 0.4%) - CONFIRMED. "almost always the full free amount" is REFUTED for C-- at L9+: maxfree in 3237 of 10232 multi turns (32%). It holds at L5-8.
- L5+ head-on victims 179, kdist 1/2/3/4/5+ = 40/60/37/20/22, killer 2+ steps 126; all sizes 1044+196=1240 of 2795 at dist 2-3 - CONFIRMED. Note 385 all-size kills at dist 5+ (portal/wrap/measurement); treat the tail with care.
- Queen median death r15 (us) vs 26 (them), not 28.5: direction CONFIRMED. Our queen HitSelf at L<=3: 92; their queen HitWall: 65; queen head-on kills 16 vs 34 - CONFIRMED.
- Elim losses at r50: 8.1 vs 13.0 units, total 19.7 vs 33.2 - CONFIRMED. Only 20 of 26 games reached r50 (survivorship). Kills "they 16.3, we 15.5" has the sides swapped in my count (we 16.6, they 15.2); "about even" stands.
- Splits "391-500 vs 167-308 per game" - UNCERTAIN: overall medians are 238 vs 137. Direction holds; I could not reproduce the figures.

## IDEAS
- "57 of C--'s 139 kills on Schooltime 828660 are L3 2-step" - REFUTED: we were team B there. The 57 (L3, 2 steps) kills are OURS on C-- (B: 102 kills); C-- (A) made 35. EternalWisdom's 7 of 13 on Dilemma 829696 - CONFIRMED.
- 829875: we had 59 units vs their 12 at r251, longest 36 vs 22, lost on queen; our queen (id1, L4, r235) was killed head-on by our own L2 newborn id131 - CONFIRMED. Their queen was L2-3 until about r370, then grew to L14.
- 829696: 3 vs 6 units at r10, elim r23, our queen HitSelf L2 at r7 - CONFIRMED. 828660: pearls eaten 2502 (us) vs 1088 - CONFIRMED.
- Idea 6 premise: in 828660 C-- L5+ ate 0.11/turn vs our 0.16 despite 64% multi-step, and EternalWisdom (829697 Slithery win) multi-steps 0%. Free-step eating is UNCERTAIN as the cause of the length losses; the single-king policy (idea 8) fits the data better.
