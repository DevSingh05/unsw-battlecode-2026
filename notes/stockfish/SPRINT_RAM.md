# SPRINT_RAM (30 Sep, ~11:30-12:10 UTC / 07:30-08:10 EDT)
Flag `SPRINT_RAM` (default 0) in bot/params.hpp. Code is `trySprintRam()` in bot/main.cpp, just after `tryRam()`, and it is called from decide() right after tryRam.
- **Trigger.** Our length is SR_MIN_LEN 4 to SR_MAX_LEN 7. An enemy head of visible length >= max(SR_TARGET_MIN 8, ceil(SR_TARGET_MULT 2.0 * myLen)) sits at BFS distance 3..min(SR_MAX_STEPS 5, myLen-1). That bound means the sprint can be paid for even if it eats no pearls.
- **Path.** BFS runs over visible tiles that are empty (occId < 0), so portal-warn tiles and our own body are excluded. The enemy head is a leaf. Nothing else moves during our turn, so the head tile we see is the head-on tile. The target's next tile never needs predicting.
- **Guards.** units >= SR_MIN_UNITS 3; not iAmKing(); not kfOn; not shouldFeed(); not pfInward() (pocket). tryRam still handles distance 1-2.
- **EV.** theirs - SR_COST 1.0 * myLen + SR_PEARL_W 0.5 * share * (corpse pearls of both) - 0.1 * steps. share = (allyHeads - enemyHeads + 1) / (heads in view + 1). A ram fires if EV > SR_MIN_EV 0. The best target wins.
- **Trace.** If the env var SR_TRACE_DIR is set, each ram appends a line to $SR_TRACE_DIR/sr.txt.
## Identity
- bot/ with b34 params and flags off (variants/sr36_off) vs v34, seed 1000 on devil, schooltime and slithery_fight.
- The replays are byte-identical to variants/b34 once the bot-path header is skipped.
- SR_TARGET_MULT was added after that check. It sits inside `#if SPRINT_RAM`, so the off build is unchanged.
## Results
- **variants/sr36** (b34 params + SPRINT_RAM=1) vs v34, 6 maps, 4 seeds, --jobs 2: **24.0/48 = 0.500** [0.36, 0.64]. Every map scored 4/8.
- **Only 2 sprint-rams in 48 games:** r483 L4 into len10 in 3 steps, and r486 L6 into len14 in 5 steps.
  - The mirror opponent rarely brings a big head within 3-5 steps of our 4-7 dragons.
  - This test cannot measure the benefit against Stockfish.
- **Mechanics check:** variants/sr36_loose (TARGET_MIN 6, MULT 1.3, MIN_UNITS 2), 12 games with replays.
  - 2/2 rams were confirmed HitHeadToHead, with both dragons dead in the same round (devil r469 L4 into 6, sch r477 L4 into 6).
## Next
- Check the firing rate against a Stockfish-like opponent, or replay the Stockfish losses to find when our medium dragons had a shot.
- If rams stay rare, loosen MULT to 1.5 or TARGET_MIN to 6, or let 3-length dragons use 2-step sprints (already covered by tryRam).
