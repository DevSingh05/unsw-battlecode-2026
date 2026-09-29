# Conservative static symmetry inference

Archived intact at `archive/symmetry-v13-20260928/` when the next experiment
started from v15. The original source-manifest paths under `codex-battlecode/bot`
refer to that archived copy; hashes are unchanged. Current `bot/` is a separate
food-routing candidate.

Research date: 28 September 2026. Baseline: the frozen `variants/v13` source.
Feature switch: `-DUNSEEN_SYMMETRY=1`; default is 0.

## Why this experiment

Unknown-map code initially treats every unseen edge as open and gives every
unseen tile a 0.01 pearl-rate prior. Each dragon remembers its own observations,
but does not infer static features elsewhere. A false path through an unseen
wall can inflate reachable area and pearl scores; barren areas can attract
foragers through the assumed food prior. These are hypotheses about the planner,
not claims that every such inference improves a match result.

Research sources:

- [Official map rules](https://game.battlecode.au/docs/map-info): maps have one
  of three reflection/rotation symmetries, which bots must discover.
- [Official map-file format](https://game.battlecode.au/docs/map-files): the
  optional SYMMETRY directive couples pearl countdowns. Static geometry alone
  therefore does not justify mirroring a live timer on custom maps.
- [Battlecode 2023, no thoughts head empty](https://battlecode.org/assets/files/postmortem-2023-no-thoughts.pdf),
  p. 2: eliminate symmetry hypotheses from newly observed static features, then
  use symmetry to locate alternative resources. The communication channel in
  that game differs, so this prototype uses per-dragon observations only.
- [The Loong Game](https://over-yonder.tech/games/loong/), local source
  `reference/loong/blog/05-maps-nobody-has-seen.md`: varied generated maps expose
  movement assumptions hidden by the fixed map pool. Website access failed;
  the supplied local article was read instead.
- Engine ground truth: `reference/unswbc/engine/src/config.cc` validates mirrored
  spawn beds when declared; `pearls.cc` shares clocks, not occupancy or pearl
  presence. These files are an older reference; match tests use installed 1.2.2.

Other ideas considered: split-child map handoff, resource-aware splitting, and
portal learning with cautious crossing. Handoff requires a robust message and
selection policy; the latter two overlap active work in the main bot. Symmetry
is independent and requires no coordinates or timing tuned to ranked maps.

## Mechanism and limits

`unseen_symmetry.hpp` stores directly observed edge kinds and whether tiles can
spawn pearls. Reflections use the engine's x/y naming and transform both the
tile and the movement direction. The two views of a physical edge are recorded
together, including torus seams.

All three hypotheses start alive. A pair of directly observed mirrored facts
with different values eliminates that hypothesis. An unseen fact is inferred
only if **every surviving hypothesis** maps it to the same directly observed
fact. No inferred fact is used as evidence. A full overlay rebuild retracts
old inferences after contradictions; zero hypotheses means no inference.

Only unknown maps receive the overlay. Kelp and portal edges are blocked;
ordinary edges are open. Portal destinations remain unknown. Only barren
spawner status is mirrored into the resource model: no pearl presence, gaps,
body occupancy, or live countdowns are copied. `World::sym` stays unchanged.

This version rebuilds unknown-map adjacency and is based on v13's lack of
learned portals. When porting into a portal-learning version, compose the
overlay before learned links or preserve confirmed portal destinations. Do not
paste the rebuild after portal learning, where it would erase learned links.

## Correctness and evaluation

`tests/symmetry_test.cpp` checks torus/odd-dimension reflection involutions,
contradiction rollback, and blocked unknown portals. Against all 40 development
map files, randomized observation order produced 12,158,772 edge comparisons
without a false inference or exclusion of a true symmetry. The holdout map
files are excluded from these development checks.

`tools/evaluate.py` reuses the repository's native builder and Wilson interval,
but places binaries/cache/logs/results inside this folder and retains every
match record. It checks for another pool/arena/evaluation process first and
allows at most six workers. Wins=1, draws=0.5; failed runs are explicit errors.
It raises its own soft file-descriptor limit to 8192 because one local match can
have 128 dragon processes. The initial uncorrected run had 56 harness errors
and is invalid; its files are retained as `results/symmetry-50000.*`.

Native results (40 development maps, two seeds, both sides, v13 opponent):

| Seeds | Score | Rate | Wilson 95% | Harness errors |
|---|---:|---:|---:|---:|
| 50000–50001 | 93/160 | 58.1% | 50.4–65.5% | 0 |
| 51000–51001 | 86/160 | 53.8% | 46.0–61.3% | 0 |
| Combined, descriptive only | 179/320 | 55.9% | 50.5–61.3% | 0 |

No valid-action failure appeared in the 320 valid native-game logs. Native
results do not establish that the judge's CPU budget is met.

**Verdict: promising but inconclusive; keep disabled.** The independent second
seed set does not meet AGENTS.md's acceptance rule. Pooling the two sets does
not repair that failed confirmation. Resampling whole maps instead of treating
all games as independent gives a combined 95% bootstrap interval of
49.7–62.2% (20,000 samples, bootstrap seed 64000), also spanning 50%.

Across both sets, 17 maps score above 50%, 14 tie, and 9 fall below. Maps 07,
13, and 17 are 8/8; map 25 is 1/8. This is a reason to investigate mechanisms,
not add per-map exceptions. The next useful experiment would ablate inferred
terrain versus inferred barren tiles. No parameters or strategy code were
changed after the first batch. `maps/genhold` remains unused: do not consume
that final check while the development confirmation is unresolved.

The process guard initially used macOS `comm`, which truncates executable
paths and could miss Python. It now uses `ucomm`. A main-agent batch observed
at 06:48 started at 06:47:29, after our second batch ended at 06:47:02; there
was no overlap with that batch. Earlier isolation cannot be reconstructed
fully, so these timings are throughput observations, not CPU measurements.

## Known-map regression and judge CPU cost

All ten ranked maps, both sides, seed 52000: **10/20**, zero harness errors.
The flag is gated off whenever the world has a recognized map; every map
scored exactly 1/2. This is a regression smoke check, not a power study.

Official installed toolkit **1.2.2**, four sequential `--sandbox` games, seed
52000, both sides on each of two development maps:

| Map | Candidate mean | v13 mean | Candidate p99 | Candidate max |
|---|---:|---:|---:|---:|
| g2026_14, 36×18, dense | 5.6M | 5.1–5.2M | 6.4M | 7.0M |
| g2026_16, 64×64 | 12.5–12.6M | 10.4M | 14.1M | 16.3M |

The candidate completed **113,775 dragon-turns** across these games, with no
invalid-action deaths, timeouts, or harness errors. Maximum measured CPU use
was 16.3% of the 100M per-turn allowance; this is evidence on these fixtures,
not a worst-case proof for every possible game. The two bots visit different
states, so their mean difference is only an approximate overhead estimate.
The additional vector buffers use 264 KiB per dragon at 64×64, excluding small
vector/allocator overhead. Whole-board rebuilding is O(width × height) each
unknown-map turn; only three symmetry hypotheses are considered.

Native builds, judge source snapshots, and caches are in ignored `build/`.
The local toolkit wrapper redirects error logs and caches and archives its
usual temporary-directory cleanup instead of deleting files. The corrected
process guard was verified to refuse the main agent's running batch, then
allowed the regression and CPU runs after it finished.

Evidence: `results/symmetry-50000-valid.{json,jsonl}`,
`results/symmetry-51000.{json,jsonl}`, `results/combined.json`,
`results/symmetry-ranked.{json,jsonl}`, `results/symmetry-cpu.{json,jsonl}`,
`results/cpu-metrics.json`, and `results/source-manifest.json`.

To repeat CPU tests, copy `bot/` and `variants/v13/` into two new directories
under this sandbox, prepend `#define UNSEEN_SYMMETRY 1` to the candidate's
`main.cpp`, and run `tools/evaluate.py` with those source paths, `--sandbox`,
`--maps gen/g2026_14,gen/g2026_16 --seeds 1 --seed-base 52000 --jobs 1`, and a
new output path. This uses the exact judge compiler and per-turn meter.

## What would establish a useful gain

First repeat a frozen implementation with enough preselected development
seeds to resolve the interval, then use all 40 reserved `genhold` maps exactly
once as a final check. Keep balanced sides and report errors separately.
After team review, real unranked evidence should include several independent
opponents on new maps (or both versions forced into unknown-map mode on the
same maps). Compare win rate, early unit survival, and longest dragon at the
end. No games have been submitted or challenged by this experiment.
