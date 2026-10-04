# REAL_SWEEP: parked unknown-map flags re-tested on realistic sets and the 17 official maps (2026-10-03)
Base: variants/v55. All screens use -D toggles only (no new variants). Raw outputs: session scratchpad `rs/` (s611, r651, r661, r671, r661c).

## Method
1. Screen (seed-base 611000): `tools/unseen_eval.py "variants/v55:<flags>" --base variants/v55 --seeds 1 --jobs 3 --sets real,realhold,blind17` (228 games: real 80, realhold 80, blind17 68).
2. Priority change mid-sweep: judge on the 17 actual maps (10 ranked + 7 Sprint), `tools/pool.py ... --seeds 2 --jobs 3 --seed-base 651000` (68 games).
   **Caveat:** every candidate except HOT_PULL and PEARL_DISTRUST is gated on `!w.known` in main.cpp, so on the 17 maps with
   map knowledge it is a no-op (verified: INFER_SYM known-mode = exactly 34/68 with every map 2/4; games are deterministic, so
   an exact .500 with all maps 2/4 = no behaviour change). The unknown-map flags were therefore run on the 17 maps with
   `-DNO_KNOWN_MAPS=1` on BOTH sides (cand and pool) = the Qualifier-like view. HOT_PULL / PEARL_DISTRUST ran known.
3. >= .56 on the 17-map run -> confirm at 661000 (and I added 671000 for the two best).

## Results (ranked by 17-map blind score, all seeds pooled where available)
| flag(s) | old verdict | screen real / realhold / blind17 (611k) | pooled screen | 17 maps 651k | 661k | 671k | 17-map total |
|---|---|---|---|---|---|---|---|
| INFER_SYM=1 | hold (.52 gen) | .512 / .537 / .574 | .539 | **.574** | .515 | .529 | 149/272 = .548 (+611k) |
| UNK_KING_SEED=300 UNK_KING_FEED=360 (late king) | - | .438 / .512 / .618 | .518 | .500 | .559 | .441 | 144/272 = .529 (+611k) |
| EXPLORE_LEARN=1 | rejected (gen) | .438 / .463 / .441 | .447 | .529 | | | 66/136 = .485 |
| LEARN_PORTALS=1 | rejected (lesson/gen) | .500 / .550 / .574 | .539 | .515 | | | 74/136 = .544 |
| HOT_LEARN=1 | rejected (gen) | .512 / .400 / .485 | .465 | .515 | | | 68/136 = .500 |
| UNK_KING_SEED=200 UNK_KING_FEED=250 (early king) | - | .463 / .537 / .574 | .522 | .500 | | | 73/136 = .537 |
| UNK_SIZE_PARAMS=1 | neutral (gen) | .525 / .537 / .559 | .539 | .485 | | | 71/136 = .522 |
| UPE_HUNGER=8 UPE_MOD=2 (G3 approx: eager portal scouts) | - | .537 / .475 / .456 | .491 | .500 | | | 65/136 = .478 |
| UNK_SEALED_FOOD=1 | neutral | .550 / .450 / .485 | .496 | .471 | | | 65/136 = .478 |
| HOT_PULL=0.6 (known mode) | rejected (ladder) | - | - | .456 | | | .456 |
| UNK_PRIOR=0.0025 (G4 approx: value unseen tiles more) | rejected | .475 / .525 / .368 | .461 | .441 | | | 55/136 = .404 |
| INFER_SYM + late king combo | - | - | - | - | .500 | .471 | 66/136 = .485 |
| UNK_EXPLORE=2 | 0 crossings | .500 / .500 / .500 | .500 | .500 (all maps 2/4) | | | **no-op** |
| PEARL_DISTRUST=1 (known) | - | - | - | .500 (all maps 2/4) | | | **no-op locally** (local maps = built-in pearl data; needs server) |
| NO_KNOWN_MAPS=1 (G1) | - | .500 / .500 / .500 | .500 | - | | | no-op on all three sets (no false adoption happens on real/realhold) |
Blind17 at 611k is also a 17-map blind run (68 games), so it is pooled into the 17-map total.

Per-map (INFER_SYM, 651k+661k+671k, 12 games each): Stripes 12/12, Portals 9/12, Default/Trophy/Australia/Maze 8/12;
Schooltime 3/12, Weakhold 3/12, Trauma 4/12. Without Stripes it is 137/260 = .527.
Late king per-map: Devil 9/12, Islands 9/12; Portals 1/12, Slithery 3/12, Around UNSW 3/12.

## Verdict
- Nothing clears .56 once confirmed. Best: INFER_SYM (.548 over 272 blind 17-map games, .539 on real/realhold); it is
  carried by Stripes (12/12) and costs on Schooltime/Weakhold. Fourth independent run near .52-.55: a small, real-looking
  edge but not decisive. Reasonable to consider for the Qualifier build only with a server blind A/B.
- Late king (300/360) swings .44-.62 by seed: noise. Early king, LEARN_PORTALS, UNK_SIZE_PARAMS: .52-.54, unconfirmed.
- Clear negatives on realistic sets too: UNK_PRIOR=0.0025 (.40), HOT_PULL (.46), UPE eager scouts (.48), UNK_SEALED_FOOD (.48),
  EXPLORE_LEARN (.45-.49). So the G3/G4 approximations by existing params do not work; G3/G4 need new code, not knobs.
- No-ops: UNK_EXPLORE=2 (gate never fires), PEARL_DISTRUST (untestable locally).
