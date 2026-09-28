# 20: Why v22 still dies ~35 times per game crossing portals on Schooltime (28 Sep 2026)

**Data.**
- Main set: the 10 v22 Schooltime games in `replays/ab_v22` (8 on spawn layout A, 2 on layout B).
- Check set: `replays/v19plus`, 18 Schooltime games. It contains the same 10 games plus 8 older v19-v21 games. Every number below reproduces there within ±10%.
- Default comparison: the 10 v22 Default games in `ab_v22`.

**Scripts.** All in `notes/tools/schportal/`, read-only over the replays, run from the project root. They adapt `notes/tools/v18portal`.
- `extract.py <dir> Schooltime` writes `<dir>_Schooltime.pkl`. It records every crossing plus all of the crosser's rays from the previous round.
- `classify.py [pkl]` gives crossing totals, questions (a) to (g), and an exact replay of the live PORTAL_ECHO_GUARD=2.
- `approach.py` measures P(cross next turn | what the crosser's own ray saw), mouth dwell, and use per portal.
- `rulecost.py pkl...` gives the rule cost of the candidate rules.
- `botmargin.py BIN pkl N` and `feedcheck.py BIN` pipe reconstructed views through a compiled v22 binary, via `notes/tools/rams/botview.py`. They use one process per dragon, and no games are played.

**Checks.**
- The guard replay says v22 should have blocked 0 of our 3985 Schooltime crossings, and it did block 0. On Default it matches the 2.3/g forced fallbacks.
- `botview` reproduced 76 of the 78 sampled decisions.

## TL;DR

- **The echo guard works on Schooltime for heads.** After a head echo we cross 0% of the time.
- **It is blind to bodies, because Schooltime's portal exits open onto long straight runs.**
  - Rule `shortPath` needs kelp within 4 steps past the exit. On Default that holds; here it almost never does: 96% of our body-echo crossings have 4-19 tiles of open line past the exit.
  - So `bodies > 0` is ignored, and **23.5 of our 35 portal deaths per game (67%) come right after our own warn ray echoed a dragon body**. In 22.7 of them the body was sitting **on the exit tile**.
- **The echo can't tell "body at the exit" from "body further down the line".**
  - At the exit: 26.6 safe and 25.2 fatal crossings per game.
  - 1-12 tiles past it: 80 safe and 0.8 fatal per game.
  - None of the features we can observe separates the two cases: echo kind, our length, portal, path length, or whether the blocker came through the same portal. P(death) sits at 15-24% in every bucket.
  - So the fix has to be a price, not a filter: **P(death | ambiguous body echo) = 18%.** The bot currently treats that as free. The opponents' fatality over *all* their crossings is 17%.
- **The Schooltime module doesn't force the crossings.**
  - 93% of fatal crossings are at maze portals 2-5 and 8-11. The module doesn't score those.
  - Rush-eligible deaths: 0.1/g. Yard portals 0 and 1: 2.6/g. The SCH_CONTEST zone: 1.7/g.
  - 90% of the fatal crossings had a safe alternative.
- **Proposals:**
  - `PORTAL_ECHO_BODY_PEN` (a score penalty of 30 when the guard lets a body echo through).
  - `PORTAL_PROBE_SOLO` (no king or relay broadcast on a turn when we probe, so body echoes stop being zeroed).
  - Estimate: about **−11 to −13 deaths per game for the penalty alone, and −14 to −17 for both**, plus about 1.5 big dragons (L≥8) per game. The cost is about 70-80 of our 398 crossings per game.

## 1. Crossing totals (ab_v22 Schooltime, per game)

| | crossings | per 100 dragon-turns | fatal | fatal % | head-turns ending on a mouth tile |
|---|---|---|---|---|---|
| **us** | **398** | **2.03** | **35.0** | 8.8 | 6.9% (1355/g), crossed next turn 29% |
| them | 107 | 0.81 | 18.5 | 17.2 | 3.1% (415/g), crossed next turn 26% |

- **Per crossing we are already twice as safe as the opponents. We die more because we cross 3.7× as often,** with 1.5× as many dragon-turns.
- Most of the gap is maze portals 2-5. We cross each of them 44-62 times per game; the opponents cross each 4-7 times.
- **Layout A: 418 crossings and 39.9 deaths per game. Layout B: 320 crossings and 15.5 deaths per game.**
  - A has more units, so there are more of our own bodies on the exits.
  - 253 of our 398 crossings per game happen at 50+ units.
- The exit is never in the 7×7 view when we cross (0%), so the `lastSeen` skip never applies.

**Conditioning (`approach.py`): P(the sender crosses next turn | what its ray through the portal hit)**

| ray hit | us | them |
|---|---|---|
| clean | 44% | 25% |
| ally/enemy **head** (at the exit or beyond) | **0%** (the guard works) | 10-26% |
| ally body AT the exit | **43%** | 22% |
| ally body beyond the exit | 59% | 14% |
| enemy body AT the exit | 31% | 25% |

- The opponents don't condition on the echo at all. They simply cross less.

## 2. Our 350 fatal crossings (35.0/g), classified (`classify.py`)

**(a) What we hit**

| hit | /g | share |
|---|---|---|
| ally body (segment ≥2) | 21.8 | 62% |
| enemy head-on | 5.9 | 17% |
| enemy body | 3.2 | 9% |
| self | 2.0 | 6% |
| ally neck | 0.9 | 3% |
| ally head-on | 0.9 | 3% |
| enemy neck | 0.3 | 1% |

- The "self" deaths aren't accidents. `feedcheck.py` shows **14 of the 20 are the deliberate feed suicide** (`MOVE (myDir+2)`, straight back through the portal the dragon just came through). Five are trapped fallbacks (0-1 free neighbour), and 1 wasn't reproduced.
- So about **1.4/g** of the 35 are intended; discount them. Default's 1.2/g self-crossings in `tools/portaldeaths.py` are probably the same thing (not checked).

**(b) The exit at our previous decision** (the round before the crossing)
- For **21.1 of the 23.6 ally deaths per game (89%)**, the same ally was already lying across the exit: seg ≥2 in 14.2/g, its neck in 6.9/g. It was not arriving; its body was draining off.
  - Different from Default (notes/17), where the blocker's head was on the exit and stepped off.
- The rest of the ally deaths are newborns (1.9/g) and a different ally (0.6/g).
- Enemy deaths: the exit was empty in 5.5/g (the enemy arrived during the round, which is unpredictable). The same enemy was already there in 3.0/g.

**(c) Could the blocker's PORTAL_WARN have reached us?** No:
- the crosser was not on the ray line: 15.6/g;
- the blocker's head was never on the exit: 4.4/g;
- no warn was sent: 1.4/g;
- the warn reached us: 2.0/g (memo live 1.0, memo expired 1.0).

**(d) Forced or chosen?**
- Chosen: 21.7/g with 2 safe alternatives, 9.9/g with 1.
- Forced (0 safe alternatives): 3.0/g (9%).
- No sprints.
- 60% of the time there was no pearl within 3 on either side, so this is idle wandering, as on Default.

**(e) Who dies, and when**
- Length: L2 17.7/g, L3 10.0/g, L4-7 4.5/g, L≥8 2.8/g. The L≥8 deaths include kings of L13-37.
- Rounds: spread over r100-500 at 3-5.5 per 50 rounds, with the peak at r200-350.

**(f) Why PORTAL_ECHO_GUARD=2 didn't block** (our own ray, previous round, replayed with the bot's exact logic)

| reason | fatal/g | share | what the crossing ray hit |
|---|---|---|---|
| **body echo, but `shortPath` false (the ray line runs on 4-19 tiles past the exit)** | **23.5** | **67%** | ally AT exit 19.3, enemy AT exit 3.4, beyond 0.8 |
| echo clean (the dragon arrived after our ray) | 4.6 | 13% | nearly all enemy head-ons |
| body echo zeroed because king/relay rays were sent the same turn (`probeRays > popcount(mask)`) | 2.6 | 7% | ally AT exit 2.4. Includes 5 of the 13 L≥13 deaths |
| no probe: newborn | 2.3 | 7% | |
| no probe: no ray through this portal | 2.0 | 6% | **The feed suicides.** A warn opposite to the facing leaves from the tail (refraction), so the exit isn't probed. |
| guard blocked, crossed anyway | 0 | | |

- So the list of suspects comes out as follows:
  - **The `shortPath` condition is the whole story (67%).**
  - Head echoes from other rays don't cause deaths. They only over-block, which costs us nothing here.
  - Sprints: 0.
  - "Not on the mouth last turn": only newborns.
  - King and relay pollution: 2.6/g, but it falls on the most valuable dragons.
- **Geometry.** The tiles past the exit before kelp, over all our body-echo crossings:
  - 0-3 tiles: 4% (the only case mode 2 covers);
  - 4-6 tiles: 52%;
  - 9-10 tiles: 16%;
  - 13-19 tiles: 28%.
  - On Default the whole line past an exit is 0-3 tiles.

**(g) Does the Schooltime module force crossings?** No.

| where | fatal/g |
|---|---|
| maze portals, not moving closer to the pool | 18.4 |
| maze portals, moving closer to the pool | 14.0 (not rush: rounds ≥90 or L>6) |
| yard portal, into the yard | 1.7 (rush-eligible: 0.1) |
| yard portal, out of the yard | 0.9 |

- `SCH_RUSH` only pulls at r<90 with L≤6, and only on layout A. It accounts for 0.1/g.
- The `SCH_CONTEST` zone (L≤3 near or in the yard, layout A) sees 1.7/g of fatal crossings out of 47 crossings/g there.
- `SCH_FALLBACK` only moves L≥8 dragons.
- The crossings come from the generic scorer: `bfsFrom` area and pearls through portals, and the crowd term. There are many of them because we have many dragons in a maze whose corridors end in portals.

## 3. The echo can't locate the body (`rulecost.py`, and the analysis in §1)

Our crossings after a body echo that v22 let through (long path), per game:

| where the ray stopped | safe | fatal |
|---|---|---|
| on the exit tile | 26.6 | 25.2 (49%) |
| 1-3 tiles past it | 63.9 | 0.8 |
| 4+ tiles past it | 17.0 | 0.1 |

- The bot only gets counts, so it sees all three rows as the same "1 body echo".
- Features the bot knows, none of which separates the rows (P(death) in each bucket):

| feature | P(death) by bucket |
|---|---|
| echo kind | ally 18%, enemy 19% |
| our length | L2 19%, L3 15%, L4-6 17-24% |
| path length past the exit | 0-4 tiles 28%, 5-9 16%, 10-14 15%, 15+ 17% |
| portal | 9-39% (small n) |
| the echoed dragon crossed the same portal in the last 15 rounds | yes 11%, no 19% |

- That leaves one number: **18% death risk per crossing.** The fix is to price that in.

## 4. Candidate rules: rule cost (ab_v22 Schooltime, our single-step crossings, per game)

| rule | blocks | fatal (0-alt, L≥8) | safe (pearl on exit) | direct saves | safe forbidden per save |
|---|---|---|---|---|---|
| v22 live (mode 2, range 3) | 0 | 0 | 0 | 0 | |
| mode 2, range 5 | 37.5 | 7.4 (0.0, 0.0) | 30.1 (0.5) | 7.4 | 4.1 |
| mode 2, range 8 | 61.7 | 12.6 (0.0, 0.1) | 49.1 (0.9) | 12.6 | 3.9 |
| mode 2, range 15 | 102.9 | 17.9 (1.0, 0.2) | 85.0 (2.6) | 16.9 | 5.0 |
| mode 3 (any body echo) | 113.2 | 19.9 (1.0, 0.2) | 93.3 (2.9) | 18.9 | 4.9 |
| solo + mode 2 | 4.9 | 2.6 (1.0, 0.5) | 2.3 (0.1) | 1.6 | 1.4 |
| **solo + mode 3** | 135.5 | **26.1 (2.2, 2.3)** | 109.4 (3.5) | **23.9** | 4.6 |

**v19plus (18 games).**
- Mode 3: 18.6 fatal and 90.1 safe.
- Solo + mode 3: 24.6 fatal and 105.1 safe.

**Default v22.** Mode 3 blocks 3.8 fatal and 18.8 safe. Solo + mode 3 blocks 4.8 fatal and 20.8 safe. That is a small gain for a small cost, so the rule is safe as a general default.

## 5. How big the penalty must be (`botmargin.py`)

We re-ran v22 on 39 fatal and 38 safe crossings from the "solo + mode 3 but not v22" set. The margin is the crossing's score minus the best alternative's score:

| | 25th percentile | median | 75th percentile | share under 30 | share under 60 |
|---|---|---|---|---|---|
| fatal | 2.1 | 9.2 | 18.3 | **85%** | 87% |
| safe | 6.3 | 10.5 | 24.6 | 74% | 87% |

- The margins that don't flip are forced moves (no alternative, margin 999) or big area/pearl differences.
- Expected-value check: 0.18 × the bot's death scale (−150 for `surviveDepth`) ≈ 27. That points to **a penalty of 30.**

## 6. Proposals (all default 0; the code stays additive)

### P1: `PORTAL_ECHO_BODY_PEN` (double, try 30)

**Where.**
- `readMessages()`, in the PORTAL_ECHO_GUARD block (`bot/main.cpp` ~1501-1533).
- The blind-portal block of the candidate loop in `decide()` (~2358).

```cpp
// params.hpp
#ifndef PORTAL_ECHO_BODY_PEN
#define PORTAL_ECHO_BODY_PEN 0.0 // notes/20: price a body echo the guard let through (long ray path); try 30
#endif
// member, next to probeMask
int echoBodyMask = 0;

// readMessages(): reset every turn, just before `if (PORTAL_ECHO_GUARD && probeMask && ...)`
echoBodyMask = 0;
// ... inside the per-direction loop, replace the block test with:
if (heads > 0 || (PORTAL_ECHO_GUARD >= 2 && bodies > 0 && shortPath))
{ /* existing hard block */ }
else if (PORTAL_ECHO_BODY_PEN > 0 && bodies > 0)
    echoBodyMask |= 1 << d; // someone's body is on that line, maybe on the exit (18% fatal, notes/20)

// decide(), inside `if (!visible[t] && t != w.plainStep(myHead, d))`
if (PORTAL_ECHO_BODY_PEN > 0 && ((echoBodyMask >> d) & 1))
    score -= PORTAL_ECHO_BODY_PEN;
```

- A penalty rather than a hard block (a "mode 3") keeps forced crossings possible: 1.0 fatal and 5.3 safe crossings per game have no alternative.
- **Estimate (Schooltime).**
  - Direct: 0.85 × 18.9 ≈ **16 saves/g**. After displacement, **~11-13/g**. On Default, v18 → v22 lost only ~10% of the predicted gain; we assume 20-30% here, because the retries are probed again.
  - Cost: ~0.74 × 93 ≈ 69 fewer crossings per game (17% of ours). Only ~2 of those had a pearl on the exit.
  - Default: about −2/g, at a cost of ~14 crossings per game.

### P2: `PORTAL_PROBE_SOLO` (0/1)

**Where.** `emitSonar()` (~1643-1673).

```cpp
bool solo = PORTAL_PROBE_SOLO && anyWarn; // probing: keep the echo counts clean (notes/20)
if (!solo && iAmKing() && (round >= KING_BROADCAST_START || kingSelf)) { ...king rays... }
else if (!solo && haveRelay) { ...relay rays... }
```

**Why.**
- 24% of our probe turns (246/g) also send king or relay rays. Their body hits, including our own body, make `readMessages()` zero `bodies`.
- That hides 2.6 fatal crossings per game on its own, and 6.2 once P1 is on (26.1 vs 19.9).
- **It hits kings hardest.** Blocked L≥8 portal deaths rise from 0.2 to 2.3 per game, 1.7 of them with an alternative. In ab_v22 those include L13, L14, L17, L27 and L31.

**Cost.**
- About 736 broadcast rays per game go unsent: ~5% of relay/king rays, one skipped turn at a time.
- A king on a mouth tile goes quiet for 1 turn, well inside the 8-round freshness window.

**Estimate.**
- Alone (with mode 2): **−1.6/g** direct, including ~0.5 kings/g.
- With P1: **−14 to −17/g** in total (≈0.85 × 26 direct, minus displacement), plus **~1.5 big dragons/g**.
- Default: −1/g extra.

**Combined target.** Schooltime portal deaths go from 35 to about 18-21 per game, about the opponents' 18.5. Of the remainder:
- ~4.6/g are enemy arrivals after a clean echo (unavoidable);
- ~1.4/g are intended feeds;
- ~2.3/g are newborns (notes/17 rule 3, `PORTAL_UNPROBED_PEN`, still unimplemented, is worth ≤2/g).

**Not proposed.**
- A larger `PORTAL_ECHO_RANGE`. Range 8 gives 12.6 saves for 49 safe crossings forbidden, but it's a hard block, and exits past 8 still leak. P1 dominates it.
- A Schooltime-only crossing cap. The module is not the cause (§2g).

## 7. Test plan

1. Build P1 = 30, P2 = 1 as a variant. Server A/B on Schooltime and Default against the ab_v22 opponents; the user approves challenges.
2. Rebuild the pickles with `extract.py <dir> Schooltime` and read `classify.py` (f):
   - "body echo, long path" should fall from 23.5 to about 3/g;
   - `approach.py` "ally AT exit → crossed" should fall from 43% to under 15%;
   - crossings should be about 320/g.
3. Watch units at r200 and yard eats on layout A. Fewer crossings of maze portals 2-5 must not starve the yard rush; the rush happens at r<90, and only 0.1/g of rush crossings were fatal.
