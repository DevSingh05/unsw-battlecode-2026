# Sprint maps: reconstructed pearl gaps (2026-10-01)

The map text inside server replays has every tile at `TILE x y 0 0`. Server replays also strip the
`pearlCountdown` events (local replays keep them), so the real `minGap/maxGap` values are hidden. These
values were rebuilt statistically from spawn events in 8 Sprint replays per map (56 replays in total).
The originals are in `archive/maps_sprint_nogaps/`, and the first, rougher estimate is in
`archive/maps_sprint_nogaps/est_v1/`.

## Facts verified against local replays (devil.map, known gaps)
- At round 0 every spawn tile draws its countdown c ~ U[min,max] and fires at round c-1. After a firing at
  round r, a reset value g fires again at round r+g. Mirror tiles (by `SYMMETRY`: y -> (W-1-x,y),
  x -> (x,H-1-y), xy -> (W-1-x,H-1-y)) share a single countdown.
- The pearl RNG does not depend on the bots. With the same `--seed` and different bots, the countdown
  streams were identical.
- A natural spawn is a `tileChange hasPearl=1` after `roundStart` and before that round's first
  `turnStart`. Pearls that appear mid-turn are death drops, and they are ignored.
- The maps place no pearls at start. The pearls seen at round 0 are tiles whose first draw was 1. These
  are mostly `1 1` tiles.

## Method (`gaps_tools/`: fetch, extract, est, build4, validate; their paths point at the session scratchpad)
1. Mirror pairs form one class. For each class and game, record the rounds where it visibly fired.
2. Take the samples: the first firing + 1 (the initial draw), and each interval between visible firings.
   Drop any interval during which every tile of the class held a pearl at some round start. Such a firing
   was blocked, so the interval would be a sum of draws. Right-censored values: (end - last firing), and
   (end + 1) for games where the class never fired.
3. Fit a mixture by maximum likelihood: intervals = 1..4-fold sums of U[lo,M] (some invisible firings are
   still body-blocked), plus 1% outliers. Weights come from EM. Censored values use the single-draw
   survival. The grid search covers M up to 5000. lo is either 1 or min(sample), and lo > 1 needs at least
   8 samples plus a BIC-style penalty. The mixture matters: Islands' busiest tiles show intervals of
   1..4 with a tail at 5..8. A max-based estimate gave 1-24, but the true value is clearly 1-4.
4. Classes with fewer than 8 samples are pooled. They are clustered on M (within a factor of 1.3) and
   refitted together, with a test for a late-start subgroup (lo > 1). This is how Tower Defense's
   ~400-500 tiles were found.
5. Tiles that never spawned in any replay keep `0 0`. A class that spawned but produced no usable sample
   gets 1-1000 (none did).

The structure is visible in the results, and it matches official-map style: Australia has a large
40-200 region, Maze and Around UNSW have 10-30 regions, Tower Defense has 1-100 and a late group around
400-500, and every map has a few `1 1` tiles. Large-M values (above 1000) are poorly determined because
those tiles fire about once a game. For tiles with only 1-2 samples, the per-tile values are noisy.

## Validation
Each map loads and runs with `unswbc run maps/sprint/<m>.map variants/v35 variants/v34 --no-replay`,
with no warnings. The table compares natural spawns per game. Local means v35 vs v34 with seeds 1 and 2.
Real means the median and range over the 8 Sprint replays in the same round window.

| map | local spawns (window) | real median [range] | ratio | first 25 rounds local / real |
|---|---|---|---|---|
| Australia | 1238, 1234 (500 rd) | 1426 [1201-1594] | 0.87 | 56,57 / 52 |
| Islands | 1519, 1498 (500) | 1492 [1359-1647] | 1.00-1.02 | 72,70 / 72.5 |
| Maze | 1503, 1327 (500) | 1506 [1426-1650] | 0.88-1.00 | 62,70 / 77.5 |
| Around UNSW | 2033, 2054 (500) | 2044 [1990-2120] | 0.99-1.01 | 100,89 / 107.5 |
| weakhold | 718, 683 (500/499) | 616 / 592 [438-845] | 1.15-1.17 | 48,41 / 36.5 |
| Tower Defense | 293 (340), 181 (200) | 301, 156 | 0.97, 1.16 | 14,22 / 20 |
| Stripes | ~30-50 per game | 34-182 (short games) | n/a | 28,34 / 36.5 |

Every map passes the 25% band except Stripes. On Stripes the gap is caused by the bots, not by the gaps:
our bots eat almost nothing there (0-36 pearls per game, against 43-275 in real games). Uneaten pearls on
the `1 1`/1-3 tiles block respawns. Early-round counts, which are mostly free of this effect, match:
first 10 rounds local 26-28 vs real 28-32, first 25 rounds local 28-34 vs real 34-42. The earlier
max-based estimate (est_v1) undercounted by about 30% on the big maps (ratio 0.68-0.76), which is why
the mixture fit replaced it.
