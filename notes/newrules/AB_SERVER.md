# tools/ab_server.py: server A/B analyzer

Compares our submissions on live server games and controls for opponent strength. It is read-only: it never submits or launches anything.

## Usage (run from /Users/devsingh/Developer/UNSW_Battlecode)

```
python3 tools/ab_server.py v44 v55                 # A = v44 (baseline), B = v55
python3 tools/ab_server.py v44 v49 v55             # every later name is compared with the first
python3 tools/ab_server.py v44@15640 v55           # pick one upload of a reused name by submission id
python3 tools/ab_server.py v44 v55 --since v55=2026-10-03T12:00 --until v44=2026-10-02T20:00
  --ref pooled|self|<num>  our rating in the Elo expectation (default pooled, see below)
  --min-map 5              min games per map on each side for the paired test
  --grace 300              seconds skipped after each upload (games queued for the old build)
  --ends                   split elimination vs round-500 tiebreak (1 API call per new game, cached)
  --no-maps                hide the per-map table
  --refresh                ignore the games cache and page everything again
  --json FILE              dump the per-game rows
```

Timing: the first run pages the public games list at 1.2 s/page, 10 games per page (about 3 min per 12 h of history). After that it fetches only new pages, plus a jump-ahead back pass if you ask for an older window. Cache: `replays/ab_server/games.json`; the `--ends` data goes in `replays/ab_server/ends.json`.

## Data and attribution
- `GET /api/v1/submissions` gives the upload times and the per-map server ratings (`byMap`).
- Per-game history comes from the public `/games/__data.json?teams=952&page=N`. Each game stores both teams' Elo at game time, ranked, challenge (true = a /battles challenge, false = an autoscrim) and the map. The v1 `/battles` list stops at 200 battles (about 12 h), so it cannot be used here.
- A game belongs to a submission if it was played in [uploadedAt + grace, next upload's uploadedAt). This assumes every upload was activated when it was uploaded, which has been true so far. If you switch versions with setActive, use --since/--until.
- top-10 means the current leaderboard top 10, not counting us.
- End type (`--ends`) comes from `GET /api/v1/battles/{gameId}` match.scoresA/B. If the loser's score is 0 the game ended by elimination. Otherwise it went to round 500 and was decided by the queen/length tiebreak.

## Formula
For each game g: s = 1 / 0.5 / 0 (win / draw / loss), and E = 1 / (1 + 10^((R_opp,g − R_us)/400)).
PAE (performance above expectation) = Σ(s − E). The tool prints PAE per game in percentage points.
- R_opp,g is the opponent's team Elo stored with that game.
- R_us = `pooled` (the default) is the mean of our stored Elo over every game in the comparison. It is fixed, so a better build is not penalised for the rating it earned. `self` uses our stored Elo per game instead.
- Paired test: on maps where both sides have at least --min-map games, d_m = PAE/g_B − PAE/g_A, weighted by nA·nB/(nA+nB). The 95% CI comes from a 2000-rep bootstrap stratified by map × submission. The tool also runs a sign test over maps.
- Verdict: B is better if the CI is above 0, worse if it is below 0, and inconclusive otherwise.

## Sanity results (2026-10-03)
v44 (2 uploads, 724 games) vs v49 (1029 games):
```
ALL         v44 453-271 -0.5   v49 597-432 -4.2
Stripes     d -20.8   Queen Of Spades -32.7   Devil -17.6   Portals -5.6   Tower Defense -24.9
VERDICT: v49 worse than v44: -4.8 pp/game (95% CI -8.8..-0.7), n=724/1029 games
```
This matches the known result. v49 is worse on Stripes, QoS, Devil and Portals, and its server per-map ratings there are 1635/1888/1805/1895, against 1845–1926/2032–2118/1935–1990/1925–2003 for v44.

v41 (660 games) vs v44:
```
VERDICT: v44 inconclusive vs v41: +0.4 pp/game (95% CI -4.4..+5.0); B>A on 10/17 maps
```

Scale: the CI half-width is about 4 pp/game with roughly 700 games per side. To detect a 3 pp difference you need well over 1000 games per side.

## Adjusted model: `--adjusted` (protocol scoring, added 2026-10-04)

Run from /Users/devsingh/Developer/UNSW_Battlecode:
```
python3 tools/ab_server.py v61 c1 --adjusted                 # baseline first; prints contrast + stage-2 decision
python3 tools/ab_server.py v61 c1 --adjusted --pae           # also the old PAE tables
python3 tools/ab_server.py v61 c1 --adjusted --since v61=2026-10-04T04:31     # baseline = latest v61 block only
python3 tools/ab_server.py v61 c1 --adjusted --window v61=2026-10-05T01:00..2026-10-05T02:00 --window c1=...
```
- Model: logit(win) = build + opponent effect (ridge 0.3, opponents with 12 or more games; the rest share one Elo slope) + map effect (ridge 1.0) + ranked + autoscrim. Draws count 0.5.
- It is fitted on the compared builds plus every other upload in the games cache ("context", each upload its own factor, uploads under 20 games dropped), so the opponent and map effects are well estimated.
- Output: the build contrast in pp (each game of the two arms predicted once as each build), 95% CI, logit and se, P(better), and the stage-2 line: under 250 candidate games no decision; 250: drop if below -1 pp; 500: drop if below +1 pp; 850: adopt if +2.5 pp or more.
- `--window NAME=ISO..ISO` (repeatable) replaces a name's upload-derived windows. Needed once builds are interleaved by re-activating stored submissions, because the submissions list only gives upload times.

Sanity (4 Oct, 17:25 UTC):
```
v69 vs v61 (all 3 v61 blocks, 1157 games): -1.7 pp (95% CI -8.7..+5.0); P(v69 better) = 0.32; n = 1157 / 195
v69 vs v61 (--until v61=2026-10-04T04:00, the two blocks around it): -6.4 pp (CI -15.0..+2.0); P = 0.07; n = 274 / 195
v55 vs v44: +3.6 pp (95% CI -1.7..+8.7); P(v55 better) = 0.91; n = 724 / 485
A/A: v61#16063 (3 Oct evening) vs v61#16388 (4 Oct 04:31-17:13): +8.1 pp (CI +1.2..+14.3), P = 0.99
```
**The pooled v61 baseline drifts.** The same build scored about 8 pp lower in the overnight block than on 3 Oct evening, after opponent and map adjustment (opponents upload stronger bots, so a fixed opponent effect is wrong over 2 days). Compare a candidate with baseline blocks close in time (`--since v61=...` or interleaved `--window` blocks), not with the whole pool.

## tools/ab_mech.py: mechanism stats from server replays (stage 1)

```
python3 tools/ab_mech.py v61 c1 --limit 60        # compare table, baseline first (run from the project root)
  --limit 60 (0 = all)   fixed pseudo-random sample per name, stable between runs
  --maps "Devil,Maze"    --non-top10    --no-download    --json FILE
  --since / --until / --window / --grace   as in ab_server.py
```
- Replays: `replays/ab_mech/<name>/<gameId>.replay` (copied from another `replays/*/` folder if present, else downloaded from the public endpoint, 1.5 s apart, backing off on 429). Per-game stats cache: `replays/ab_mech/<name>/rows.json`. 60 new games take about 3.5 minutes.
- Stats: win rate, our queen alive at r100 and at r500 (r500 games), total length ratio at r100/r300 (geometric mean), eliminated, stillborn children by r100 (count, length, share of splits), r500 loss with our queen dead and theirs alive, lone queen (of those, enemy had 3 or fewer units), enemy queen killed by our king (longest non-queen unit, L >= 8) and by any unit.
- CIs: Wilson for shares, mean +- 1.96 se for means, B - A by normal approximation.

v61 sample (60 games, 4 Oct): queen alive r100 45%, r500 40% (of 30); length ratio r100 1.92, r300 2.31; eliminated 8%; stillborn by r100 9.1 per game (length 18.6, 9% of splits); r500 queen-dead loss 10% (6), lone queen 3 of those; enemy queen kills: 31 by any unit, 0 by the king.

## tools/auto_challenge.py: panel and unranked-only (added 2026-10-04)

- `--unranked-only`: no ranked series.
- `--panel "TeamA,TeamB,..."`: fixed opponents by leaderboard name (case-insensitive exact match), rotated evenly; the pointer is kept in `replays/auto/panel_state.json`. Ranked series unless `--unranked-only`; unranked panel series rotate evenly through all 17 active maps, 5 per series.
- `--ignore-lock`: keep running while `SERVER_LOCK` exists.
- Without these options the loop behaves as before.

Protocol panel at 45/h (run from /Users/devsingh/Developer/UNSW_Battlecode; stop the old loop first, PID from `pgrep -f auto_challenge.py`):
```
nohup python3 tools/auto_challenge.py --per-hour 45 --cycle 300 --unranked-only --panel "Vibing++,forgot to mention,Sponge(Albert and Bob),horse,WeHaveQuizzes,Computers,free trip to sydney pls,bread first search,Settlers of Battlecode,Team SKKU,Sabotage-d" >> replays/auto/loop.log 2>&1 &
```
Drop `--unranked-only` while the build we intend to keep is live (ranked series against the same panel).

## tools/ab_conductor.py: unattended queue runner (written 2026-10-04, NOT tested, NOT started)

It uploads builds by itself, so read its docstring before starting it. Queue and state: `notes/ab_queue.json`; log: `notes/ab_queue_log.md`; stage dirs: `replays/ab_stage/<name>/`; stop file: `replays/ab_stage/STOP`. The dry run has not been executed yet.
