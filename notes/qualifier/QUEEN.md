# QUEEN_MODE in variants/v36q (unswbc 1.2.3 rules), 2026-10-01

v36q is a copy of variants/v35 with QUEEN_MODE=1 (params.hpp, end of file). bot/ is untouched.

## Changes (variants/v36q/main.cpp)
- l.46, l.144: RP.kingDeclare=1 on every map (default and at the end of applyMapParams).
- l.1952 amQueen() = myId 0/1; freeSteps(L)=ceil(L/4).
- l.1956 updateKingship / l.2003 iAmKing: the queen is always king. Non-queens never crown while queenAlive(),
  i.e. her beacon or body was seen in the last QUEEN_ALIVE_MEM=30 rounds. Otherwise the v35 king logic runs as a fallback.
- readMessages (l.1795 and the end): queen beacons go to q*. While she is alive, kingId/kingTile/kingLen are hers and the relay forwards her beacon.
- emitSonar: the queen broadcasts from QUEEN_BROADCAST_START=0.
- shouldFeed: from QUEEN_ALLFEED_ROUND=430, every non-queen feeds the live queen whatever its length.
- The queen never splits: keepLen peel, PUMP_TIP, POCKET_FACTORY, normal split, trap split and the king-escape reverse split are all off for her, and a map-module SPLIT is discarded. ECHO_EXIT_HOLD (SPLIT 2) is still allowed.
- The queen never rams (tryRam). Map modules can't crown or uncrown anyone while she is alive.
- Threats (computeThreats, replyEnemyReach): the queen always uses KING_THREAT_REACH and THREAT_TAIL_UNKNOWN, with reach >= ceil(L/4) per enemy head.
- Move scoring for the queen: QUEEN_THREAT_PEN=300 on a threatened tile; blind portal crossings always pay RP.kingPortal; QUEEN_PORTAL_EXIT_PEN=80; QUEEN_CORRIDOR_PEN=40; QUEEN_ENCLOSE_PEN=400 (queenOpen(): tiles reachable with her body as a wall, below 3L+20); KING-depth survival plus reply search.
- surviveDepth: QUEEN_GROW_SIM makes the queen plan as if she eats every step, so she gets no tail release.
- Multi-step payability (1.2.3): eat-sprint and king-escape tailFreed count only steps past ceil(L/4) as paid. The old n-1 cost model overestimates cost, so it is safe.

## Results: v36q vs v35, unswbc 1.2.3, seeds 1-3, both sides (36 games)
| map | v36q | v35 |
|---|---|---|
| default | 2 | 4 |
| devil | 1 | 5 |
| gen/g2026_00 | 3 | 3 |
| gen/g2026_03 | 0 | 6 |
| schooltime | 2 | 4 |
| slithery_fight | 3 | 3 |
| total | 11 | 25 |
Both queens die early in almost every game, usually between r40 and r150 and on both sides. Most games are then decided by longest dragon or by elimination.
Only once did a queen survive: default s3, where the v36q queen lived and won "longer queen, 10 to 0".
Slithery: both queens start in a dead-end pocket and die at r2 or r5 whatever they do.
Compute (--sandbox, schooltime): p50 6.6M, max 14.4M points per turn, far below 100M.

## Known risks / next steps
- v36q is WORSE than v35 right now. Don't submit it.
- The no-split queen costs early economy, and she still dies. Main causes: 1-wide kelp corridors and crowded yards, where she is the only exit and gets head-on, and pockets where she coils into herself.
- Ideas: let the queen growth-split early (before about r150) while her length stays >= 4; keep her away from all heads, allies included; plan her route at least 2 steps ahead against blockers.
- The queenAlive() fallback depends on hearing her beacon. Far-away dragons may self-crown and pull feeders.
