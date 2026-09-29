# COLLAB: tasks and coordination for Codex (from the main agent, 2026-09-29)

You are the second engineer on team "Cache me outside" (UNSW Battlecode 2026). This file **extends
AGENTS.md**. Where the two disagree, this file wins. The user has approved everything below.

## 0. Situation (read this first)
- **Standings.** We are rank ~22 (elo ~1916), up from 35 on 28 Sep. The live bot is **v24**
  (`../variants/v24`, same as `../bot`).
- **Deadline.** Sprint tournament is on 1 Oct, Qualifiers on 10 Oct. Both are **best of 7 on UNSEEN
  maps**. Submission freeze for the Sprint is **2026-09-30 18:00 UTC**. After that, only crash fixes.
- **What happened since your last session** (details in `../notes/journal.md`, notes 15-20). Each change
  is behind a flag in `../bot/params.hpp`:
  - v17 `FRAME_FIX`: the server swaps team starts in about half of games.
  - v18 `NEWBORN_NECK_GUARD`, `PORTAL_WARN_MEMO`.
  - v19 `TRAP_SPLIT_BLIND`, `KING_PORTAL_PENALTY`=100 on all maps except Portals.
  - v20 `PORTAL_ECHO_GUARD`=2. We use our own warn-ray echoes; Default portal deaths went from 69 to 11/game.
  - v21 `LATE_SPLIT_ROUND`=450.
  - v22 `KING_ESCAPE`, `THREAT_TAIL_UNKNOWN`=2. Big dragons sprint or split away when every step is threatened.
  - v23 `PORTAL_ECHO_BODY_PEN`=30, `PORTAL_PROBE_SOLO`.
  - v24 `RAM_GUARD_LOCAL`=1 (Devil, Dilemma).
- **Result.** v24 vs v16 on unseen sets: generated 0.588, lesson 0.646, holdout 0.662.
- **Rejected ideas (don't redo them):** LEARN_PORTALS (also with a blind penalty), UNK_SIZE_PARAMS,
  INFER_SYM, PEARL_DISTRUST, EAT_SPRINT, PORTAL_ALLY_COST, SMALL_SPRINT_THREAT, KING_V2_MERGE_ROUND
  460/1000, PUMP_TIP_SPLIT, FEED_FRESH (neutral).

## 1. Your tasks, in priority order

### Task A: finish your PEARL_ROUTE idea on top of v24 (highest value)
Your route-based food valuation screened at 69.4% vs v15 on generated maps and was never confirmed.
It is general logic, which is exactly what unseen maps need.
1. Refresh your sandbox bot from `../variants/v24`. Archive the current one into `archive/` first; never delete it.
   Port `pearl_route.hpp` and the `PEARL_ROUTE` flag in, default 0.
2. Screen `-DPEARL_ROUTE=1` vs `variants/v24` on the generated maps.
3. If promising, confirm on two fresh seed sets. Then check:
   - the ranked maps (must not regress, both `maps/*` and `maps/swap/*`);
   - the blind set, via `../tools/unseen_eval.py`, which also runs the lesson maps;
   - finally the held-out set `--holdout`, once.
   
   Example, from the project root:
   `python3 tools/unseen_eval.py "codex-battlecode/bot:-DPEARL_ROUTE=1" --base variants/v24 --sets gen,blind,lesson,ladder --seed-base 96000 --jobs 4`
4. Check compute in the judge sandbox on a 64x64 map (`unswbc run MAP a b --sandbox`). Max must stay well
   under 100M points.
5. If it holds up, do a server test (section 2), then write `bot/CANDIDATE.md` with the exact flags.

### Task B: robustness stress test of v24 on extreme unseen-style maps (crash = lost Bo7 game)
- Generate extreme maps with `../tools/mapgen.py` or your own generator, **into `codex-battlecode/maps/`**:
  - tiny (e.g. 8x8), max 64x64, very long thin maps;
  - portal-dense, pearl-poor or no pearls, pearl-rich;
  - 1 start dragon vs many, walls everywhere, open field.
- Run v24 vs v24 and v24 vs v16 in the **judge sandbox** (`--sandbox`) on each. Look for:
  - crashes, invalid actions or "No Valid Action" deaths, timeouts;
  - max CPU points, degenerate behaviour (e.g. all dragons suicide, never eating).
- Report every problem with a reproducing map+seed in `notes/robustness.md`.
- For each crash, propose a minimal fix as a diff (you can't edit `../bot`).
  **Crash fixes are the most valuable thing you can find.**

### Task C: open research: general logic for unseen maps
You have full permission to read and research anything:
- all project notes, replays, the engine source in `../reference/`;
- public game pages via GET, the Loong blog, and write-ups of Battlesnake, Kaggle Hungry Geese,
  Halite, Lux AI and past Battlecode.

Look for map-agnostic logic we lack. For example:
- runtime estimation of map features, adapting king/split timing to them;
- better pearl-timer inference on unknown maps;
- safe portal use when destinations are unknown;
- opponent modelling from what we see.

Prototype behind flags (default 0), test with the protocol in section 3, and write up in `notes/`.

## 2. Server permissions and coordination (important)
The user allows you to **submit a version and play a few test matches** when you believe you have
something substantially better. Rules:
1. **Lock.** Only one of us may have a test version active on the server.
   - Before submitting, check `coord/SERVER_LOCK`. If it exists and is less than 90 minutes old, wait.
   - Otherwise create it with your name, the UTC time and the version name.
   - The main agent creates the same file when it is testing, and checks it before submitting.
   - Delete-equivalent: when done, move the lock to `coord/done/` (don't delete).
2. **Never across an even UTC hour.** Ranked autoscrims happen then (00:00, 02:00, ...). Only have a test
   version active between :10 and :45 of an odd hour, or :10 to :50 of an even hour. If your test runs
   long, restore before the next even hour.
3. **Budget.** At most **20 challenge games per test** and **at most 2 tests per day**. The team shares
   60 games/hour, so check the hour's usage.
   - Use unranked challenges only (`"ranked": false`), never ranked.
   - Use peers from `../replays/ab_v18/template.json` (10 teams, ranks ~17-35).
   - Use the maps where your change should matter (map IDs: Schooltime 9, Portals 20, Slithery 21,
     QoS 7, Default 4, Trophy 11, Dilemma 17, Autarky 19, Devil 13, Trauma 15).
   - Tool: `CH_MAPS=4,19 python3 ../tools/launch_later.py coord/ch.json ../replays/ab_v18/template.json replays/cx1`
     (run from `codex-battlecode/`; start `coord/ch.json` as `[]`).
     It retries on HTTP 429 and collects the replays.
4. **Naming and submitting.**
   - Name test versions `cx1`, `cx2`, ...
   - Submit from the project root: `unswbc submit codex-battlecode/bot -n cx1 -d "..."`.
   - Run a `--sandbox` game first (no crashes, max points well under 100M).
5. **Restore.** When your games are DONE (or if anything looks broken), immediately resubmit the latest
   main version:
   `unswbc submit variants/v24 -n v24r -d "restore after cx test"`, or whatever the highest `variants/vN` is.
   Check with the API that it is `active`, then release the lock.
6. **Compare fairly.** Measure a mechanism metric as well as wins (`../tools/portaldeaths.py DIR` is an
   example of a per-batch metric). Compare with the latest main batch on the same peers and maps:
   `../replays/ab_v2*`, `summary.json`.
7. Never touch team settings, never create or regenerate API keys, never request ranked matches,
   and never print the key in `~/.unswbc/keys.json` (tools/api.py reads it internally).

## 3. Local testing protocol (anti-overfitting)
- **CPU.**
  - Run one batch at a time machine-wide, with `--jobs 4`, since the main agent also runs tests.
  - Before starting, check `ps aux | grep -E "pool.py|arena.py|unseen_eval"`. If a main batch is running,
    wait; a short `sleep 60` loop is fine.
  - Never leave background jobs running when you stop.
- **Which sets.**
  - Tune on `../maps/gen` and `../maps/lesson` (these are allowed in `--maps` as `gen/...`, `lesson/...`).
  - Confirm on fresh seeds, then check the ranked maps with and without map knowledge
    (`unseen_eval.py` "blind" set).
  - Use `--holdout` only once, as the final check.
  - A change is worth shipping only if pooled unseen is clearly above 0.50 and nothing regresses.

## 4. Communication
- Keep your timestamped journal in `notes/journal.md`.
- Put short status updates for the main agent in `coord/STATUS.md`: what you are doing, results, and any
  server test you plan. Append, newest last.
- The main agent will read `coord/STATUS.md` and may reply in `coord/FROM_MAIN.md`.
- If you find a crash in v24, write it at the TOP of `coord/STATUS.md` with the word **URGENT**.
- Git stays **read-only** for you. The team commits your folder.
- **No attribution** anywhere: no Co-Authored-By lines, no "generated by" notes.

## 5. What "done" looks like
- For each idea:
  - a write-up in `notes/` (what, why, evidence with the seed sets, CPU cost);
  - the code behind a flag, default 0;
  - if it's your best candidate, `bot/CANDIDATE.md` listing the flags to turn on.
- We will port winners into the main bot additively, as new flags.
- Work steadily and in small verified steps. **Quality over quantity.**
