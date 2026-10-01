# Qualifier design: 4 general changes (from PPP.md, COLLAPSE.md, KING.md)
All flags default 0 in variants/v35/params.hpp (`#ifndef X / #define X 0`). Ranked by EV/effort. None makes big dragons more timid: #1 touches only feeders (L<=6), #2 and #3 only L<=4 foragers before r60 or in lanes, #4 adds units.

## 1. KING_FEED_STEAL (about 20 min). Pearls from feeds: king gets 0.39 vs opponents' 0.52-0.61
Where: main.cpp feed block, KING_V2 branch (~3631), just before `if (FEED_QUEUE && dieNow)`.
```
if (KING_FEED_STEAL && dieNow)
  for (o : segs) if (o.head && o.team==myTeam && o.id!=myId && (o.id&1023)!=(kingId&1023)
                     && wrapDist(o.tile, myHead) <= wrapDist(kingTile, myHead)) {
      n = count segs with id==o.id;   // same length count as tryConsFeed (main.cpp:2250)
      if (n <= KING_FEED_STEAL_LEN /*6*/) { dieNow = false; break; } }
```
When dieNow is false the dragon keeps walking and its normal scoring takes it toward the king's front, so the feed is delayed, not cancelled. Variant 1b: with KING_FEED_STEAL=2, also require !foodWaiting at dk 3-4 (so KING_V2_LOOSE applies only at dk<=2).
Evidence: 27.5 pearls/game dropped near the king. Allies take 0.50 of them (0.53 at dk 3-4), and 10.4 of 14.9 feeds come within 2 rounds of another feed. Raising the share to 0.55 adds about +4.5 king length, which flips about 6 of 37 r500 losses.
Test: unseen_eval gen,lesson,gated then holdout, against v35. This is active on known KING_V2 maps too, so run a ladder sanity check on Schooltime/Slithery/Devil. Pass: >=0.52, and near-king feeds/game don't fall more than 20% (kan*.py). Risk: fewer feeds, and volume matters (wins have 23.7 feeds/game, losses 12.8). Try this before FEED_QUEUE=1, which cuts volume harder.

## 2. UNK_CENTER_PULL (about 40 min). Blind early food: 41 vs 157 spawn pearls, 0.4-1.3 heads in the centre
Where: pearlValue() (main.cpp:1112-1124), unknown-tile else-branch, after v is computed.
```
if (UNK_CENTER_PULL && !w.known && ls<0 && w.spawnAt[t]<0 && round <= UNK_CP_R /*60*/) {
  dc = wrapDist(t, centreTile);  // (W/2,H/2) lies on every symmetry axis
  v = max(v, UNK_CP_V /*0.25*/ * max(0, 1 - dc / (0.25*(W+H)))) * (1 - round/(double)UNK_CP_R); }
```
Evidence: blind Devil gets 5 centre pearls by r50 vs their 39, while known-map wins get 37. PPP on Australia: 193 vs 54 eaten by r100 and 57 vs 28 units. Target: >=3 heads in the centre at r25 on the ab_blind34kr maps.
Test: unseen_eval all 4 sets against v35, plus single games against the pi/cheji-style rushers. Sweep UNK_CP_V in {0.15, 0.25, 0.4}. Risk: a head-on rush into the centre at L2-3 means even trades (102 rammed deaths/9 games). Keep ramGuard=2. The pull fades by r60.

## 3. UNK_LANE_GUARD (about 45 min). 111/281 blind deaths are HitSelf; 102 of those in 1-wide kelp lanes with an ally body ahead
Where: direction scoring loop (main.cpp:3938-3960), after the area penalty.
```
if (UNK_LANE_GUARD && !w.known && myLen<=4) {
  walk from t along degree-2 tiles (passable nbrs != previous), up to 5 steps;
  lane = first tile has <=2 passable nbrs with both sides seen-kelp;
  blind = walk ends on a tile with lastSeen<0 or degree<=1;
  allyNear = some own head (not me) within 3 of t;
  if (lane && blind && allyNear) score -= UNK_LANE_PEN /*25*/; }
```
Target: <7 lane traps per 1000 unit-rounds (now 16.8) on the 10 blind replays. Test: unseen_eval all sets, then known kelp maps (weakhold-like, Tower Defense, Stripes), where we already win. Risk: it gives up food in lanes. Gating it to L<=4 with an ally near limits that.

## 4. UNK_LATE_PEEL (about 30 min, speculative). Units collapse after r300: 17/12 splits vs PPP's 118/157 in r401-500
Where: split gate (main.cpp:3817-3820). Add an OR to the round clause.
```
|| (UNK_LATE_PEEL && !w.known && round < 470 && myLen >= 8 && !kingSelf && myLen < kingLen - 6
    && units < w.unitLimit - 4 && !threatened)   // child k = 2 (peel a feeder)
```
Evidence: PPP keeps about 60 units and its L9-14 dragons peel L2s. Test: unseen_eval against v35 (needs >=0.53, since KING.md shows reserve mass isn't binding). Risk: it starves the second big dragon. Try it last.

Not proposed: an earlier UNK_KING_SEED (SEED200/FEED250 tested neutral at .513), anything that makes big dragons more timid (KING_SAFE_PRE, THREAT_BIG_PER_LEN=10 and BOX_HEAD_GUARD all lost), and MERGE_ROUND changes (no evidence).
