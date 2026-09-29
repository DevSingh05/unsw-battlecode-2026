# Robustness findings and handoff

## Confirmed: v28 drops one face of unknown portal metadata

`World::observeEdges` creates one canonical observation per physical portal
edge, then sets only `portalSide[td]`. Its reciprocal face is omitted. On a
fresh process, this normally records north/west entrances while missing
south/east entrances. A later sighting at a viewport boundary can change
that, making behaviour depend on observation history. The underlying `nxt`
correctly blocks both faces; it is the metadata used by probes, lures, exits,
and forced-escape ranking that is incomplete.

Reproducer: **`maps/targeted/unknown_neck.map`, seed 121000**, a valid 31×31
rotationally symmetric map with initial bodies crossing portals. Each head
has a portal into its own neck, another portal to empty space, and two walls.
This extends the initial fixture suite, which deliberately kept starter
bodies off portal edges and therefore could not expose this bug.

The two additive, default-off switches are:

```text
-DUNK_PORTAL_SIDES=1 -DUNK_NECK_ESCAPE_GUARD=1
```

The first records both physical faces, without inferring destinations or
adding portal links to BFS. The second ranks the portal opposite the head's
facing as certain body collision, rather than an escape gamble. Use them
together: a neck guard alone cannot select an escape still misclassified as
kelp.

Official 1.2.2 judge sandbox, both candidate seats:

- Baseline v28 as A: `MOVE N`, **HitSelf at round 0** into its current neck.
- Fixed as A: `MOVE E`, survives all 500 rounds (draw versus baseline B).
- Baseline B takes the safe W entrance, exposing the directional bias.
- Fixed as B wins when baseline A dies. These two targeted games are not a
  win-rate estimate.
- No crashes, invalid actions, or timeouts; maximum **7.0M/100M** CPU points.

`tests/portal_sides_test.cpp` checks all four directions and torus seams.
Exact observation: `results/unknown-neck.input`. Patch:
`notes/portal-safety-v28.diff`. Separate source:
`variants/portal_safety_v28/`. Evidence:
`results/portal-safety-reproducer-121000.{json,jsonl}` and
`results/portal-safety-reproducer-metrics.json`, plus the retained replays.
The gen/blind/lesson/ladder regression is in progress before any integration.

## Confirmed: v24 king escape frees its tail too early

Reproducer: `maps/extreme_v24/king_tail_escape.map`, with the exact initial
dragon-0 input saved in `results/king-tail-escape.input`.

- v24 emits `MOVE WW`. The first W lands on its current own tail at (3,4).
- The engine checks collision before moving the tail, so this is fatal.
- `tryKingEscape` used `myLen-(k+1)` before executing step k. At k=0 that
  incorrectly allowed the tail; it also ignored growth stalls after pearls.
- The proposed fix tracks releases only after completed steps, adding normal
  tail motion only when no pearl was eaten, plus the paid sprint segment on
  steps after the first.
- With `KING_ESCAPE_TAIL_FIX=1`, the same input produces the legal `MOVE NEE`.

This is a deterministic unsafe-action bug, **not a runtime crash or timeout**.
Minimal patch: `notes/king-escape-tail-fix.diff`; isolated source:
`variants/escape_tail_fix/`. It was reported at the top of `coord/STATUS.md`.

The main agent independently verified the input/output and shipped the fix as
**v25**, confirmed in `coord/FROM_MAIN.md` and the main journal. It remains in
v28. Do not reintroduce the old v24 escape code when porting another feature.

## Extreme fixture suite

`tools/extreme_maps.py` writes fourteen deterministic maps into
`maps/extreme_v24/`, with a machine-readable `manifest.json`:

- 7×7 and 8×8 minimum-size/wrap cases;
- 64×7 and 7×64 strips;
- 64×64 empty, pearl-rich/many-start, and 320-segment/unit-limit-1 cases;
- dense portal fields with no pearls or abundant pearls;
- nearly all-kelp corridors and an intentionally forced-death fixture;
- asymmetric one-start-versus-sixteen starts;
- the king-tail escape reproducer.

Starts never overlap, initial body links avoid walls, paired portals keep
orientation, and geometry/food are rotationally symmetric. The asymmetric
start-count fixture intentionally changes only the starting teams' counts.
The 7-cell minimum comes from the engine config parser, rather than the
website's nominal ten-cell limit.

The main journal records a completed **v27 judge-sandbox stress run on these
fourteen maps**: zero crashes, invalid actions, or timeouts, maximum **24.6M**
points. This is team-reported evidence; those raw results were not produced
by this evaluator. It also reports side-biased outcomes, so they must not be
treated as a win-rate comparison.

The original requested v24-versus-v24/v16 matrix was superseded by that run
and the shipped safety fix during the usage interruption. Supplemental runs
should target the current frozen baseline and retain map+seed+side+replay.
`tools/summarize_robustness.py` reads those records, reports per-turn CPU,
NoValidAction/time-limit events, first actions/deaths, pearl consumption, and
final counts. Forced collisions on `walls16_forced` are expected; legal
collision deaths are distinct from process crashes and invalid commands.
