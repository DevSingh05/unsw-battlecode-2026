# Early-king fixes A/B (KING_DEATHS.md fixes 1-2), 30 Sep ~07:20 UTC (03:20 EDT)
All new flags are in bot/params.hpp and default to 0. Code is in bot/main.cpp.
With the new flags off, bot/ + V33 flags plays games identical to variants/v33: sandbox Sch and Por seed 3 replays differ only in the bot path byte.
V33 = `-DPOCKET_FACTORY=1 -DPF_EARLY=1 -DPF_CHILD_MAX=2 -DUNK_NECK_ESCAPE_GUARD=1 -DKING_CONSENSUS=1 -DESCAPE_DEADEND_FIX=1 -DPM_POR_LATESPLIT=0 -DPM_POR_DIVESTOP=360 -DCROWN_INHERIT=5 -DECHO_EXIT_HOLD=15 -DSONAR_ENCRYPT=1`

## A. KING_SAFE_PRE
Applies to iAmKing(), or to myLen >= KING_MIN_LEN once round >= kingSeedRound.
- computeThreats: an enemy head's reach grows by +1 for each visible pearl within its current reach, up to KSP_PEARL_MAX (2). This is added after the KING_THREAT_REACH cap.
- Move score: if an enemy head is within reach + KSP_EXIT_MARGIN (2) of the target tile, count the tile's exits. An exit is a tile we can enter at step 2 that is not threatened.
  - 1 exit: -(KSP_EXIT1_PEN 40 + KSP_EXIT_PER_LEN 1.5 * len).
  - 0 exits: -(KSP_EXIT0_PEN 90 + 1.5 * len).
- tryKingEscape also fires early, when the chosen tile is within reach + KSP_ESC_MARGIN (1) of an enemy head. In that case:
  - a plain step counts as safe only if it is also outside reach + 1;
  - it sprints only 2 steps (KSP_ESC_MAXN), to a tile outside reach + 1;
  - it never reverse-splits.

## B. KING_FOOD / KF_FEEDLEN
- KING_FOOD: during feedPhase, a non-king dragon values pearls at KF_MULT (0.1) if all of these hold:
  - the king heard/seen within KF_FRESH (6) rounds has kingLen >= myLen + 2;
  - our head is within KF_RADIUS (4) of the king's head;
  - the pearl is within KF_PEARL_R (6) of the king's head.
- No expiry exception: pearls do not expire in this engine. KF_PEARL_R stands in for "only we can use it".
- KF_FEEDLEN=N: a dragon that has fed (shouldFeed was true on some turn) keeps feeding while myLen <= max(KING_V2_FEED_LEN, N) before KING_V2_MERGE_ROUND. From FEED6_ROUND on, the cap is max(6, N).

## Local results vs variants/v33
Setup: 5 maps (Sch, Por, Sli, QoS, Devil), seeds 1000-1003, both sides, 40 games, --jobs 2.
The runner is equivalent to pool.py (same arena.build/play and seeds) but keeps replays: scratchpad kfix/run.py.
King deaths = our longest dragon (len >= 8) dying at r >= 300, summed over the 40 games. L450 is the median of our longest at r450 vs the opponent's.

| cand | score | Sch | Por | Sli | QoS | Dev | king deaths (Sch/Por/Sli) | L450 Sch | L450 Por | L450 Sli |
|---|---|---|---|---|---|---|---|---|---|---|
| base (V33, flags off) | .500 (mirror) | 4/8 | 4/8 | 4/8 | 4/8 | 4/8 | 6 (4/2/0) | 37/37 | 23/23 | 47/47 |
| KING_SAFE_PRE=1 | .425 | 4/8 | 3/8 | 2/8 | 4/8 | 4/8 | 2 (1/1/0) | 44.5/27.5 | 23.5/25.5 | 39/46.5 |
| KING_FOOD=1 | .450 | 3/8 | 3/8 | 5/8 | 3/8 | 4/8 | 8 (6/2/0) | 40.5/39.5 | 27.5/27 | 39.5/42.5 |
| KING_FOOD=1 KF_FEEDLEN=5 | .500 | 5/8 | 4/8 | 4/8 | 3/8 | 4/8 | 11 (6/2/3) | 34.5/38.5 | 25.5/22 | 45.5/44 |

Reading (n=40, 95% CI about ±0.15, so none of the scores differ from 0.5):
- KING_SAFE_PRE does what it is meant to: king deaths 6 -> 2 and a bigger Sch king at r450 (44.5 vs 27.5).
  - Sli got worse: 2/8, L450 39 vs 46.5. The few-exit penalty and early sprints probably cost growth on the open map.
  - Next: try KSP_EXIT_MARGIN=1 / KSP_ESC_MARGIN=0, or turn it on only for Sch/Por.
- KING_FOOD raises our L450 on Sch and Por, but king deaths go up on Sch (6). The same happens with KF_FEEDLEN (11 total, 3 on Sli).
  - Allies kept away from the king's food may leave it less screened. The kd metric also counts suicides of an L>=8 "longest", so check the replays before concluding.
- Suggested next test: KING_SAFE_PRE=1 KING_FOOD=1 together, with more seeds, vs v33 and on the ladder-like pool.
