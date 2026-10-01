# Qualifier flags: implementation (1 Oct 2026, ~15:10 UTC / 11:10 EDT)
All four flags from DESIGN.md are in bot/params.hpp (appended at the end, all default 0) and bot/main.cpp. With the defaults, behaviour is unchanged. New helper: `unkMap()` = `!w.known && w.candidates.empty()`, the same test UNK_KING uses. Every unknown-map flag is gated on it.
- KING_FEED_STEAL (+KING_FEED_STEAL_LEN 6): in the KING_V2 feed block, just before `if (FEED_QUEUE && dieNow)`. If a small ally head (not me, not the king, segment count <= 6, counted the same way as tryConsFeed) is within dk of my head, dieNow is set to false. With =2 it also blocks a dk>=3 feed while foodWaiting. Applies on all maps, as the design says.
- UNK_CENTER_PULL (UCP_W 0.25, UCP_R 60): in pearlValue(), unknown-tile else-branch, after v is computed. Only for never-seen, non-spawn tiles with round <= UCP_R.
- UNK_LANE_GUARD (ULG_PEN 25, ULG_STEPS 5, ULG_ALLY_R 3): new `laneTrap(t,d)`, called in the direction loop right after the area penalty, for myLen <= 4. The lane test: t has <=2 open edges, both sides perpendicular to d are kelp, and t has been seen. The walk follows tiles with exactly one forward exit and stops at a junction, a dead end, unseen ground, or after 5 steps. blind = the end tile is unseen or has degree <= 1. allyNear = another own head within 3 of t.
- UNK_LATE_PEEL (ULP_ROUND 470, ULP_MINLEN 8): split gate. latePeel = round<470, L>=8, !kingSelf, L<kingLen-6, units<unitLimit-4, !threatened, unkMap().
## Interpretations
1. CENTER_PULL: I read the pseudocode as `v = max(v, UCP_W*prox*fade)`. Taken literally, the fade would also multiply the normal v and push all values toward 0 as r60 approaches.
2. LATE_PEEL: just adding an OR to the round clause would do nothing. With UNK_KING, every L>=8 dragon is `bigLate` after the seed round (250), and that blocks the split gate earlier. So latePeel also bypasses `!bigLate` (`(!bigLate || latePeel)`). When the peel is the only reason the split fires (bigLate or past splitStop), k is forced to 2 and the "parent sealed -> k=myLen-2" flip is skipped, so it really peels a 2-long feeder. The kingSelf, pfIn and holdTile gates and the viability check still apply.
3. FEED_STEAL=2: "require !foodWaiting at dk 3-4" is implemented as `dk>=3 && foodWaiting -> no feed`. It applies on top of the =1 steal check.
4. LANE_GUARD "seen-kelp": nxt is open until an edge is observed, so step()==-1 always means observed kelp (or an unknown portal). I also require lastSeen[t]>=0. Passability ignores bodies; allies count only through allyNear.
## Variants (new dirs, nothing overwritten)
q36 = bot/ with v35's values for the 15 shared macros that differ (the list in the task, all matched). Every define v35 has is now identical in q36. q36a/b/c/d = q36 with KING_FEED_STEAL / UNK_CENTER_PULL / UNK_LANE_GUARD / UNK_LATE_PEEL set to 1. All five compile cleanly with `c++ -std=c++20 -O2` (0 errors; the -Wall warnings are old ones). bot/ also compiles with all flags on (FEED_STEAL=2).
## Identity check (native, seed 5, vs v34; replays in scratchpad q36id/)
q36 vs v35: devil, schooltime, gen/g2026_02 and genhold/g2027_01 differ by exactly 2 bytes each, the bot path in the header (q36 vs v35). The games are IDENTICAL.
Known-map safety: on devil and schooltime, q36b/c/d replays are identical to q36 (compared after the header). q36a differs on schooltime, which is expected.
The flags do fire: q36a differs on schooltime and g2026_16; q36b on g2026_16 and g2026_06; q36c on g2026_00 and g2026_10; q36d on g2026_16.
## Sandbox (wasm, g2026_05 vs v35; 10x8, the games end by elimination in r19-31)
q36 L r26, q36a W r23, q36b W r31, q36c W r19, q36d W r25. Max points/turn 4.4-4.6M, no crash.
Longer check on g2026_13 (40x40, 500 rounds): q36a/c/d max 10.0M, q36b max 11.2M. No crashes. That is well under 100M.
Not done (per instructions): pool/unseen_eval batches, submission.
