# FTM deep dive (8 Oct): queen policy and small-map economy

Status: **paused, about 12:30 EDT on 8 Oct, at the coordinator's request.** No results yet. Nothing was submitted or
challenged, there was no Discord or browser use, bot/ and variants/ were not touched, and no local games were run.
Progress, scripts and the resume steps are in `work/top4b/ftm/PROGRESS.md`.

## Done so far
- Rebuilt the tooling that was lost with the old scratch:
  - `work/top4b/ftm/qtrace.py` traces both queens on every turn: legal options, flood areas with and without
    portals, enemy kamikaze reach, eats, splits and deaths.
  - `work/top4b/ftm/agg.py` holds the FTM-vs-us comparison sections.
- Corpus: 198 FTM-vs-us replays (replays/top4_ftm 137 and replays/ftm_oct5 61). Sides come from
  replays/ab_server/games.json.
- The full trace run was in progress when paused.
- Code read for the comparison. These are working notes:
  - Before r100 our queen is scored like a worker. The pearl and area terms apply, and an L<6 queen pays only
    SMALL_THREAT_PEN=12 for a threatened tile.
  - From r20 (or 4 units), QGUARD's QG_MIN=5 floor keeps her at L5 or more whenever she splits.
  - An L3 or shorter queen cannot die HitSelf, because her tail is never next to her head. An L4+ queen can.
    FTM keeps its queen at L2-4.
  - Whether this explains our 19/106 self-deaths is the first thing to quantify.

## Not done yet
- Policy rules with counts.
- Small-unit traces on Autarky, Trophy, Default and weakhold.
- The difference analysis.
- The neverKnown-gated prototype and its unseen_eval run (seed-base 972000).
