# Overnight runbook (autonomous improvement loop)

Goal: raise our ladder rating before the Sprint (1 Oct 2026, 00:00 UTC) without breaking anything.

## Each iteration
1. Run `date -u`, then append a timestamped entry to `notes/journal.md` (what you did, results, next idea).
2. Pull new ranked + challenge results: `tools/api.py`, `tools/collect.py`. Update the per-map win table in the journal.
3. Pick ONE improvement (highest expected gain from notes/08, notes/09 or journal findings). Implement it in `bot/` behind a param in `bot/params.hpp`.
4. Test with `tools/pool.py "bot:-DFLAG=..." --seeds 6` against the pool (v2..latest). Change only one thing at a time.
5. Accept only if the whole 95% interval is above 0.50, or for a per-map change, that map's interval is above 0.50 over 36+ games. Otherwise revert and log it.
6. When accepted: snapshot `variants/vN`, run a `--sandbox` game (max points must be under 50M), then `unswbc submit bot -n vN -d "..."`.
   Submit whenever a version is better; there's no waiting period. Limits: 12 uploads/hour. Ranked autoscrims come every 2h (UTC even hours).
7. The real bottleneck is games: **60 challenge games per hour** (confirmed: HTTP 429 "used its 60 games for the hour"). Keep the challenge queue full every hour: after a submit, launch unranked challenges (max 60 games/hour, 10 maps per team) against teams ranked about 10–25 places above us. Collect the replays.

## Research is always free
Reading costs nothing: public replays, other teams' battles (/games, /battles), the docs, the engine repo, the web, and the browser via the Chrome extension. Research whenever it helps; only the 60 games/hour challenge budget is scarce.

## Stop time
Keep looping until **06:00 Eastern = 10:00 UTC** (about 4 hours from 01:50 Eastern) (check `date -u` every iteration). Don't stop early.
Context auto-compacts in long sessions; after a compaction, re-read this file and the tail of notes/journal.md.

## CPU etiquette (user request: laptop was heating up at 98% CPU)
- Run at most ONE local test batch at a time. Default `--jobs 6`; `--jobs 8` is the ceiling (measured 27 Sep: 8 jobs on big maps = user ~45%, sys ~34%, ~1600 processes, no thermal throttling). No parallel pool.py runs.
- Wrap batches in `python3 tools/cpuwatch.py -- <cmd>` to log user/sys CPU, load, process count and thermal state.
- Don't leave background servers running (http.server etc.). Check `ps` for stray unswbc/bot processes after tests and stop leftovers with TaskStop (never kill -9 unrelated processes).
- Prefer fewer, larger tests over many parallel small ones.

## Hard rules
- NEVER delete anything (no rm, no git clean, no overwriting snapshots). To get rid of a file, move it into `archive/` in the project folder; the user deletes it later.
- Never create or regenerate API keys, never change team settings, never request RANKED challenges.
- Keep `variants/` snapshots; never delete one.
- If a submission fails to build or the sandbox shows crashes/timeouts, re-activate the previous version on the website only via the user; log it and stop submitting.
- Stop submitting after 2026-09-30 18:00 UTC (freeze for the Sprint) unless a crash fix is needed.
