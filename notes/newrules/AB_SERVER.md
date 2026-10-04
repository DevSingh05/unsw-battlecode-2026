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
