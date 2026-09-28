# 17: Why v18 still dies ~54 times per game crossing portals on Default (28 Sep 2026)

**Data.** The 10 v18 Default games in `replays/ab_v18` (A/B challenges against 10 peer teams, 5 W / 5 L). The baseline is `replays/ab_v16_dt`: 15 v16 Default games, 10 of them against the same 10 opponents ("sameopp").

**Scripts.** All in `notes/tools/v18portal/`, read-only over the replays, run from the project root:
- `extract.py <dir> Default` records every portal crossing by both teams, every sonar ping with its geometric path, and each dragon's head history. It writes `<dir>_Default.pkl`.
- `classify.py [pkl]` answers questions (a) to (e) for our fatal crossings, plus us-vs-them crossing totals.
- `probe.py` asks whether the crosser's own ray through the portal on its previous turn predicted the death. It also simulates the rules.
- `approach.py` measures how each team reacts to what its ray saw, and how often dragons end a turn on a portal mouth.
- `rulecost.py` gives the cost and benefit of the echo rule, for v18 and v16.
- `overlap.py` computes the extra saves from the memo fix and what is left after all rules.

A fatal crossing means we died on the step that crossed a portal (same definition as `tools/portaldeaths.py`: us 53.7/g, them 14.6/g).

## TL;DR

- **Our warn rays can't reach the dragon that is about to cross.** On Default the "line behind the entrance" is 0-3 tiles before kelp. In 67% of our fatal crossings into an ally, the crosser was not on the blocker's warn ray when the warn was sent. It walked onto the entrance tile later.
- **We already have the missing information and throw it away.** Every portal mouth is both an entrance and an exit, so a dragon ending its turn on an entrance tile already casts PORTAL_WARN back through the portal. That ray lands on the exit. The next turn's `ECHOES` line tells us whether it hit a dragon, and `in.echoes` is parsed but never used.
  - When our previous-turn ray hit an ally **head** at the exit, the crossing was fatal **97%** of the time (33/g).
  - When the echo was clean, only **0.6%** of crossings were fatal.
- **The opponents who probe act on it; we don't.** tungtung67 and Weneedmoretokens cross 60-72% of the time after a clean ray and only 3-4% after a ray that hit a dragon. We cross 60-75% of the time whatever the ray hit.
- **Rule 1, `PORTAL_ECHO_GUARD`, should remove about 35 to 47 of our 54 portal deaths per game.** It costs nothing extra: no new sonar, no extra turns.

## 1. Crossing totals, v18 Default (per game)

| | crossings | per 100 dragon-turns | fatal | fatal % | exit in view (%) | fatal % blind / in view | turns ending on a mouth tile |
|---|---|---|---|---|---|---|---|
| **us** | **422** | **6.1** | **53.7** | 12.7 | 6.8 | 13.6 / 0.7 | **14.7% of head-turns** (1024/g) |
| them | 124 | 1.8 | 14.6 | 11.8 | 13.2 | 13.1 / 3.1 | 6.4% (431/g) |

- **Fatality per crossing is about the same for both teams.** We die 3.7× more because we cross 3.4× more often.
- **We spend 2.3× more of our turns on portal mouth tiles.** Mouth tiles are 4.7% of the map. That time on the mouths is also what makes our own dragons the blockers.
- **What kills the opponents:** mostly their own ally head-ons (5.6/g), then ally necks (3.3/g).

**Approach pattern (`approach.py`).**
- Dragons end on a mouth and cross the next turn 40% of the time for us, 28% for them.
- Time spent near the entrance before crossing is the same for both teams: 52-56% of crossers spent exactly 1 of rounds r-6..r-2 within 1 tile of it. Nobody idles at the entrance.
- Directions are balanced for both teams (N/S only on Default).
- We re-cross within 4 rounds 45% of the time; they do 30%.
- The real difference is conditioning:

| P(cross next turn), by what the dragon's own ray through the portal hit | us | them |
|---|---|---|
| clean (kelp / nothing) | 62% | 40% |
| ally body at the exit | 75% | 17% |
| ally head at the exit | 59% | **10%** |
| enemy head at the exit | 37% | 5% |

## 2. Our 537 fatal crossings (53.7/g), classified (`classify.py`)

**(a) What we hit**

| hit | per game | share |
|---|---|---|
| ally neck (segment 1) | 33.8 | 63% |
| ally body (segment 2+) | 8.9 | 17% |
| enemy head-on | 4.0 | 7% |
| ally head-on (**both** die) | 3.1 | 6% |
| enemy neck / body | 3.1 | 6% |
| self | 0.8 | 1.5% |

**(b) The exit at the crosser's previous decision**
- **61.5%:** the same ally's **head** was on the exit tile. It stepped off, and its neck is what we hit.
- 13.4%: the same ally's neck was already there.
- 3.7%: that ally's segment 2 was there.
- 4.3%: a different ally was there.
- Enemy: exit empty the round before, 6.3% (the enemy arrived during the round, which we can't predict). The same enemy segment was already there in 6%.
- Newborn with no previous turn: 2.8%.

**(c) Could the blocker's PORTAL_WARN have reached the crosser?** Ally blockers only; the rest are enemy (13%) or self.
- **67%: the crosser was not on the ray line.**
  - The warn ray leaves the exit, comes back out of the entrance, and runs straight on until it hits kelp. On Default that covers the entrance tile plus 0-2 tiles.
  - The crosser reached the entrance from the side after the warn had been sent.
- 8.8%: no warn was sent, because the blocker's head was never on the exit at the end of a single-step turn.
- **8.2%: the warn reached the crosser in time, but the memo had already expired. This is an off-by-one** (§4 rule 2).
  - Typical case: the blocker has length 2, sends the warn at round r0, and the crosser (lower ID than the blocker) crosses at r0+2.
  - The memo keeps the exit blocked only while `round < r0 + len`.
  - But a lower-ID crosser moves before the blocker in round r0+len, so the blocker's tail is still on the exit.
- 0.9%: the warn reached the crosser in time and the memo was still live. v16 had 9.4/g of these, so PORTAL_WARN_MEMO does work where the geometry allows.
- **Displacement:** same opponents, v16 → v18:
  - newborn self-deaths 9.0 → 0.8 (fixed);
  - memo-live warn deaths 9.4 → 0.5 (fixed);
  - "crosser not on the ray line" deaths 23.9 → 36.0 (+12);
  - crossings 378 → 422/g.
  - Dragons that were saved or held back mostly re-cross later into unguarded exits. Any rule that guards only part of the crossings loses about half its gain to this.

**(d) Forced or chosen?**
- 94.6% were chosen: 51.6% had 2 other safe moves and 43.0% had 1. Only 5.4% were forced (0 safe alternatives).
- None were sprints. Every fatal crossing was an ordinary one-step move from the scoring loop.
- Chasing: in 64%, there was no pearl within 3 steps beyond the exit **and** none near any alternative.
  - In 18%, an alternative had a pearl within 3 steps and we crossed anyway.
  - A pearl on the exit tile itself: 7% of all our crossings, the same rate as the opponents.
  - So the crossing is almost always idle wandering, driven by the `bfsFrom` area/spawn-timer terms, not by a pearl.
- An enemy head within 3 was present in only 15%, so these are not escapes.

**(e) Who dies, and when**
- Length: L2 32.9/g, L3 19.3/g, L4+ 1.5/g (97% are L2-3).
- Rounds: the r150-300 swarm phase (9.6-11.1 per 50 rounds). Four L≥10 deaths in 10 games (L17, L10, L12, L24), all at r456-497 and all into ally or enemy necks.

## 3. The echo is a near-perfect predictor (`probe.py`, our single-step crossings, age > 0, 407/g)

| our own ray through that portal on the previous turn hit … | crossings/g | fatal/g | fatal % |
|---|---|---|---|
| nothing (kelp) | 257.5 | 1.5 | **0.6%** |
| ally head at the exit | 33.9 | 33.0 | **97%** |
| ally body at the exit | 45.9 | 11.6 | 25% |
| ally body / head beyond the exit | 49.2 | 0.0 | 0% |
| enemy head / body at the exit | 5.4 | 3.4 | 63% |
| enemy beyond the exit | 14.4 | 1.9 | 13% |

On Default, 98% of the crossers cast exactly one ray the turn before, so the echo counts belong to that ray alone. The other 2% are kings sending 4 rays.

## 4. Rules (all new `#define`s, default 0)

### Rule 1: `PORTAL_ECHO_GUARD` (1 = heads only, 2 = heads, plus bodies when the exit's ray path is short)

**Where.**
- (i) `emitSonar()` (`bot/main.cpp` ~1607-1641): remember what we probed.
- (ii) `readMessages()`, right after the PORTAL_WARN_MEMO block (~1497, where `freeOther` already exists): read `in.echoes` and mark the exit as occupied.
- (iii) `emitSonar()` condition (~1609), optional: also probe from mouths of unknown-partner portals on unseen maps.

**Code sketch.**
```cpp
// members
int probeTile = -1, probeRound = -1, probeMask = 0, probeRays = 0;

// (i) emitSonar(), just before `warnDirs[0] = ... = false;`
if (PORTAL_ECHO_GUARD) {
    probeMask = 0; probeRays = 0;
    for (int d = 0; d < 4; d++) {
        if (warnDirs[d]) probeMask |= 1 << d;
    }
    // count every SONAR line we emitted this turn (warn + king/relay directions)
    for (size_t p = out.find("SONAR "); p != std::string::npos; p = out.find("SONAR ", p + 1)) probeRays++;
    probeTile = pending.empty() ? myHead : pending.back();
    probeRound = round;
}

// (ii) readMessages(), after the warnMem loop
if (PORTAL_ECHO_GUARD && probeMask && probeRound == round - 1 && probeTile == myHead) {
    int heads = in.echoes[2] + in.echoes[4];          // ally_head + enemy_head
    int bodies = in.echoes[1] + in.echoes[3];         // ally (incl. own) + enemy bodies
    if (probeRays > __builtin_popcount(probeMask)) bodies = 0; // king/relay rays pollute the body count
    for (int d = 0; d < 4; d++) {
        if (!(probeMask >> d & 1)) continue;
        int x = step(myHead, d);
        if (x < 0 || x == w.plainStep(myHead, d) || occId[x] >= 0) continue;
        bool shortPath = false;                        // ray stops at kelp within PORTAL_ECHO_RANGE after the exit
        int y = x;
        for (int k = 0; k <= PORTAL_ECHO_RANGE; k++) {
            y = step(y, d);
            if (y < 0) { shortPath = true; break; }
        }
        if (heads > 0 || (PORTAL_ECHO_GUARD >= 2 && bodies > 0 && shortPath)) {
            occId[x] = 1 << 20; occTeam[x] = w.myTeam; occHead[x] = heads > 0;
            freeT[x] = std::max(freeT[x], 2); freeOther[x] = std::max(freeOther[x], 2);
        }
    }
}
```

**Why it's general.**
- Every portal mouth is both an entrance and an exit, because portals are two-sided.
- Every crossing that isn't a sprint starts from a tile where the head ended its previous turn, so the ray was already cast there.
- `step()` already handles portals learned on unseen maps, and `shortPath` uses only known edges.
- Blocking works through the existing `occId`/`freeT` path, so the candidate loop, `surviveDepth`, `bfsFrom`, `tryRam` and the trapped fallback all respect it. A fully boxed dragon still gets the fallback ranks.

**Estimated effect on Default (v18 data, `probe.py`/`rulecost.py`; v16 sameopp is within ±2).**

| mode | crossings blocked | of which would have died | blocked deaths with 0 safe alternative | direct deaths saved | after displacement (re-tries are probed again) |
|---|---|---|---|---|---|
| 1 (heads) | 60/g | 36.7/g | 1.7 | ~35/g | **~28-35/g** |
| 2 (+ bodies, range 3) | 140/g | 49.5/g | 2.0 | ~47/g | **~40-47/g** |

- The displacement discount is smaller than for the memo, because a re-try is guarded again. Unblocked crossings die at 1.4% (mode 2) or 4.7% (mode 1), against 12.7% now.
- Ally head-ons kill two of our dragons, so mode 1 also saves about 3 more ally deaths per game that the portal count doesn't show.
- **Cost:** mode 2 turns away about 90 safe crossings per game (of 422); only 5/g of those had a pearl on the exit. The opponents cross 124/g and win.
- **Try mode 2 first on Default; use mode 1 for open maps,** where long rays over-block body echoes.
- `PORTAL_ECHO_RANGE` = 3.

### Rule 2: `PORTAL_WARN_MEMO_SLACK` (set to 1)

**Where.** `readMessages()` ~1469-1470. Push `{tile, rnd + lastWarnLen + PORTAL_WARN_MEMO_SLACK}` and use the same slack in the push condition.

**Why.** It is the off-by-one in (c). A receiver with a lower ID than the sender moves before it in round `rnd+len`, so the sender's tail is still on the exit. The warn carries no sender ID, so allow one extra round.

**Estimate.**
- Standalone: **−4.5/g**.
- On top of rule 1 mode 1: −0.9/g. On top of mode 2: ~0.
- It is a one-line fix. It also covers crossers that get the warn but cast several rays (kings), and sprint arrivals.

### Rule 3: `PORTAL_UNPROBED_PEN` (a score penalty, try 40)

**Where.** The candidate loop in `decide()`, inside the blind-portal block at ~2183 (`if (!visible[t] && t != w.plainStep(myHead, d))`).

**Code sketch.**
```cpp
if (PORTAL_UNPROBED_PEN > 0 &&
    !(probeRound == round - 1 && probeTile == myHead && (probeMask >> d & 1)))
    score -= PORTAL_UNPROBED_PEN;  // no fresh echo for this exit: a newborn, or after a sprint/split
```

**Evidence.**
- Newborn children cross 15/g at 10% fatal (1.5/g).
- Crossings with no ray the turn before are 0.8/g, and **100%** of them are fatal.
- A penalty rather than a skip keeps forced escapes possible.

**Estimate.** **−2.3/g**, additive to rule 1.

**Combined estimate:** 53.7 → roughly **6-12 portal deaths per game** (the opponents are at 14.6), plus about 3/g fewer ally head-on partner deaths. Units r150-300 should go up by the same order. Rules 1-3 do nothing on maps without portals.

**Not proposed.**
- A mouth-dwell penalty (MOUTH_CLEAR, notes/16 §7.4). We do spend 2.3× the time on mouths. But a dragon must end a turn on the entrance tile to get a probe, so a dwell penalty works against rule 1. Revisit only if jams show up after rule 1.
- The echo can't remove enemy arrivals during the round (1.4/g, clean echo) or the last newborn cases.

## 5. Test plan
1. **Mechanism check on existing local replays.** The ray-then-cross pattern is already present in any v18 replay, so `probe.py` works on local batches too. After the change, "ray hit allyHead AT exit → crossed" should be about 0. Rebuild the pickle with `extract.py <dir> Default` and read `approach.py`'s table. "Us" should look like tungtung67: P(cross | hit) < 10%.
2. **Server A/B on Default** against the same 10 opponents. Watch `tools/portaldeaths.py` (portal/g us), units at r200, and win rate.
3. **Then Schooltime and Trophy.** notes/16 measured the same ally-body excess there. Then re-test `LEARN_PORTALS=1` on unseen maps with rule 1 on.
