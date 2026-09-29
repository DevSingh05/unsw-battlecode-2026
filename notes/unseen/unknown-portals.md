# Unknown portals on unseen maps (track: safe portal use, 28 Sep 2026)

Scripts (read-only, run from the project root):
- `notes/unseen/tools/portal_stats.py maps/*.map` (add `--summary` for the aggregate only): per map, portal pairs, share of mouth tiles, share of exits in view from the entrance, whether the partner is the mirror image, dead-end exits, and **territory and pearl rate lost when portals are treated as kelp** (what v24 does on unknown maps). It also gives the rate-weighted spawn-to-pearl distance with and without portals.
- `notes/unseen/tools/learnable.py maps/*.map`: which portal pairs LEARN_PORTALS could learn by walking. A pair counts if both ends come into 7x7 view from tiles reachable from spawn without crossing.
- `notes/unseen/tools/cross_hunger.py [jobs]`: over the top10b replays (top-10 teams vs peers) and v16 ladder games. It reports crossings per game, the share that are first-time crossings, fatality, and crossing rate against "hunger" (rounds since the dragon last ate or was born). It writes `cross_hunger.pkl`.

## 0. What v24 actually does on an unknown map

The task text says step() treats a portal edge as plain. That is only true **before the edge has been seen**.

- `World::observeEdges`, when `!known`: every visible portal edge gets `nxt = -1`, unless LEARN_PORTALS is on and both ends are known. So on unseen maps **a portal is kelp**. `w.portalSide[tile*4+d]` records that it is a portal.
- The only crossing is the `UNK_PORTAL_ESCAPE` fallback rank 3, used when every other move is lethal.
- `computePortalExits()` builds `portalExit` from `step()`, so unknown mouths are never exits. That means `PORTAL_WARN`, `PORTAL_WARN_MEMO`, `PORTAL_ECHO_GUARD`, `PORTAL_ECHO_BODY_PEN` and `NEWBORN_NECK_GUARD` never fire, and the echo-guard block in `readMessages()` `continue`s on `x < 0`.
- Consequence: **zero portal deaths, and zero portal territory.**

## 1. How common portals are, and what treating them as kelp costs

`portal_stats.py`. "Rate lost" is the share of the map's total pearl spawn rate (sum of 2/(min+max)) that can't be reached from team A's spawn heads without crossing a portal. Maps are symmetric, so B loses the same.

| set | maps with portals | pairs (mean) | mouth tiles | exit visible from entrance | partner = mirror image | rate lost as kelp (mean) | maps losing >5% rate |
|---|---|---|---|---|---|---|---|
| ranked 10 | **9/10** | 7.4 | 5.7% | 1.9% | 0% | **35.5%** | **5/9** |
| gen (40) | 24/40 (60%) | 5.5 | 5.4% | 8.3% | 0% | 10.2% | 6/24 |
| genhold (40) | 30/40 (75%) | 5.7 | 4.1% | 3.3% | 0% | 4.9% | 4/30 |
| lesson (24) | 7/24 | 9.4 | 3.5% | 9.8% | 0% | 62.2% | 5/7 |

Ranked maps, one by one (rate lost / territory lost with portals as kelp):
- Trauma **99.3% / 76.9%**. The start room at x0-10 is kelp-sealed, and its only exits are portals V(11,0) and V(11,20).
- QoS **73%**, Portals **59%**, Default **50%** (the 3x3 block of sealed central cells, plus the 5x5 corner rooms), Schooltime **33%**.
- Slithery 4%. Autarky, Dilemma and Trophy 0%, where portals are only shortcuts.
- Also Stronghold 93% and Colosseum 0% (not ranked).

Lesson maps: islands_a 97%, islands_b 75%, vault_a/b/c 83/89/91%. webs_a/b 0%, but there portals cut the rate-weighted distance from 11.3 to 13.9. Gen maps g23 50%, g28 75%, g32 97%, g37 11%, g39 6%, g18 5%.

- **Portal links always respect the map symmetry.** On all 1740 portal crossings across the ranked, gen, genhold and lesson maps, crossing (mirror(t), mirror(d)) lands on mirror(dest(t, d)).
- **The partner is never the mirror image of the edge (0%),** so seeing one end tells you nothing about the other.
- Ranked portal ids have no usable parity rule. Mirror pairs are often, but not always, id^1.
- On ranked maps 40.6% of exits face kelp straight ahead, which costs a turn but is not fatal. **2.2% of exits are dead ends** (all 20% on the Portals map; gen and lesson 0%). A dead-end exit is fatal for any length, because the only way back is into your own neck.

**Why LEARN_PORTALS could not fix this** (`learnable.py`: share of crossings from the spawn region whose far end is ever in view from that region). Vision passes over kelp, so:
- Default, QoS, vaults, webs, Schooltime, Autarky: 100% learnable by walking. That needs one process to see both ends; newborns start blank.
- **Trauma 0%, g32 0%, Portals 20%, islands_a 33%.** There, the far end lies deep inside the sealed region, so no amount of walking teaches it.
- LEARN_PORTALS also put learned links straight into `nxt`, so bfsFrom's area and pearl terms routed idle wanderers through them. That is the same 3.4x over-crossing we have on known maps (notes/17). It lost 0.31-0.48.

**Why our unseen evaluation cannot see this.** The `blind` set turns map knowledge off on *both* sides. On blind Trauma both teams starve in their start rooms, and on blind Default both skip the centre. The handicap cancels out. Real tournament opponents cross portals on every map: top-10 teams make 1.72% of their moves through portals. So the blind and gen sets **systematically hide the cost of never crossing**. The test plan below adds an asymmetric check.

## 2. How good teams cross (`cross_hunger.py`, 78 top team-games, 78 peer, 148 us-v16)

| group | crossings/g | % of moves | first-time for that dragon | fatal | pearl eaten on the crossing move |
|---|---|---|---|---|---|
| top-10 | 160 | 1.72% | 109/g (68%) | **9.4%** | 21% |
| peers | 65 | 0.88% | 44/g | 16.4% | 25% |
| us (v16, known maps) | 221 | 2.37% | 147/g | 15.8% | 12% |

- **Crossings are not hunger-driven.** For the top-10, 42% of crossings come within 5 rounds of eating (28% of turns).
- P(cross | head on a mouth tile) is flat at 33-37% up to hunger 60, then 20-30%.
- So a hunger trigger will not mimic the top teams. It is still the right *safety valve* for us: we are not trying to match their crossing rate, only to stop starving in sealed regions.
- **Blind-crossing fatality is about 9-16% per crossing on busy maps.**
- notes/17 (v18 Default): when our own ray through the portal on the previous turn hit **nothing or kelp**, the crossing was fatal **0.6%** of the time (257 crossings/g). An ally head at the exit: 97%. An ally body at the exit: 25%. A dragon beyond the exit: 0-13%.
- A probe cannot tell *where* along the line the hit was, so any dragon echo has to count as "dirty". The pooled fatality after a dirty echo is 33.5% (49.9 fatal of 148.8 per game), which is worth giving up.

## 3. The policy: "a portal is a door you knock on before opening"

This is one coherent rule set, behind a new flag, and it is active only when `!w.known`:

1. **Unknown mouths are exits.** A tile A with `portalSide[A*4+d]` is where anyone crossing the partner edge in direction d^2 arrives, so A is an exit even though we don't know the partner. A dragon ending a single-step turn on A casts a **probe** in direction d, provided d is not the reverse of its facing, where the ray would leave from the tail.
   - The payload is the existing WARN, so an ally on the far side learns that A is occupied.
   - Kings and relays stay quiet that turn (`PORTAL_PROBE_SOLO`), which keeps the echo count clean.
   - This is exactly the notes/17 warn geometry, which is portal-symmetric, so it needs no destination.
2. **Cross only on a fresh clean knock.** The unknown crossing (A, d) is a candidate only if all of these hold:
   - the probe went out last turn from this tile in this direction, and it was the only ray;
   - the echoes show no ally, ally head, enemy or enemy head (kelp or nothing counts as clean);
   - myLen < KING_MIN_LEN;
   - this dragon has not crossed this edge in the last `UNK_EXPLORE_COOLDOWN` rounds;
   - the dragon *wants to explore* (item 4).

   Expected fatality is about 1%, against the 9-16% of blind crossing. There is no extra turn cost: the knock is cast on the turn the dragon arrives on the mouth.
3. **Learn on crossing, not on sight.** The turn after an explore move, if `myHead != plainStep(A, d)`, the dragon now knows all four crossings of that edge pair: (A,d)→X, (X,d^2)→A, (plain(A,d),d^2)→plain(X,d^2), and (plain(X,d^2),d)→plain(A,d).
   - Store them in a separate `learnDest[]`, **not in `nxt`**, so bfsFrom never routes idle wanderers through them. That is the LEARN_PORTALS failure mode.
   - Learned links feed `portalExit`, so the v18-v23 guards (WARN, MEMO, ECHO_GUARD, NEWBORN_NECK_GUARD) start covering those exits.
   - A learned link is still crossed only through rule 2. That caps crossings *by construction*: each one needs a clean knock and a reason.
   - Also rebuild the body across the portal: `trail.insert(trail.begin(), myHead)` instead of relying on vision, which can't see the neck.
4. **Why explore (the desire gate).** Explore when either:
   - (a) the dragon's walkable component (bfs over `nxt` with portals as kelp) holds no tile this process has never seen, so the region is closed and fully scouted, and hunger ≥ `UNK_EXPLORE_HUNGER_CLOSED` (default 3); or
   - (b) hunger ≥ `UNK_EXPLORE_HUNGER` (default 25), and there is no pearl in view within bfs distance 6.

   While the gate is open, mouth tiles of unexplored or cooled-down unknown portals get a small lure value in `pearlValue()` (`UNK_EXPLORE_LURE`, 0.4 pearl), so dragons actually walk to the doors. Case (a) fires on Trauma's start room, Default's central cells and island interiors. Case (b) is the long-idle safety valve on open maps with a poor region.
5. **Newborns next to an unknown portal: no special rule is needed.**
   - A newborn has no probe history, so it can't cross until it has knocked from a mouth itself.
   - If it was born straddling a portal, its own knock hits its own body (the "ally" echo), so it never crosses into its neck.
   - The unknown edge is already `nxt=-1`, so it never walks into it.
   - Optional extra (proposal 5): don't split within `myLen` rounds of an explore crossing, so no child is born with its neck across a portal it doesn't know.

How much it can matter:
- On Trauma-like, Default-like, vault and island maps, blind v24 gets 1-67% of the pearl rate an opponent that crosses gets. That is 5 of the 9 ranked portal maps and 5 of the 7 lesson portal maps.
- On gen and genhold maps portals are mostly shortcuts (6/24 and 4/30 maps lose >5%). There, expect the gate to fire rarely and the result to be neutral.
- Risk budget, rough: with the hunger gate, maybe 5-30 explore crossings per team-game on sealed maps, at about 1-3% fatality (0.6% clean-echo base, plus arrivals by lower-ID dragons, plus 2% dead-end exits). That is under 1 death per game.

## 4. Proposals (ranked)

### 1. `UNK_EXPLORE` (the policy above; params `UNK_EXPLORE_HUNGER` 25, `UNK_EXPLORE_HUNGER_CLOSED` 3, `UNK_EXPLORE_COOLDOWN` 8, `UNK_EXPLORE_LURE` 0.4, `UNK_EXPLORE_SCORE` 15)

**Where.**
- `Bot::emitSonar()`: add unknown mouths to `warnDirs`.
- `Bot::readMessages()`: record the clean or dirty echo for unknown directions.
- `Bot::decide()`: an extra candidate after the scoring loop, before `tryKingEscape`.
- `Bot::emitMove()` and `updateTrail()`: remember the explore move, then learn the link and rebuild the trail.
- `computePortalExits()`: also mark `learnDest` targets and unknown mouths.
- `pearlValue()`: the lure.

**Sketch.**
```cpp
// members
std::vector<int> learnDest;          // N*4, -1 unknown; filled only by crossing (never copied into w.nxt)
std::vector<int> edgeCrossRound;     // N*4, last round we crossed this unknown edge
int lastGrowRound = -1, prevLen = 0; // hunger
int exploreFrom = -1, exploreDir = -1, exploreRound = -100;
int unkEchoRound = -100, unkEchoTile = -1, unkEchoMask = 0; bool unkEchoClean = false;
bool exploreDesire = false;

// analyse(): hunger bookkeeping (after myLen is read)
if (lastGrowRound < 0) lastGrowRound = round;            // process start (newborn/original)
if (myLen > prevLen && prevLen > 0 && !pendingSplitLastTurn) lastGrowRound = round;
prevLen = myLen;

// computePortalExits(): add learned exits and unknown mouths
if (UNK_EXPLORE && !w.known && !w.portalSide.empty())
    for (int t = 0; t < w.N; t++) for (int d = 0; d < 4; d++) {
        if (w.portalSide[t*4+d]) portalExit[t] = 1;                    // someone can arrive here
        if (learnDest[t*4+d] >= 0) portalExit[learnDest[t*4+d]] = 1;
    }

// updateTrail(), before the rebuild: learn from last turn's explore move
if (UNK_EXPLORE && exploreRound == round - 1) {
    int A = exploreFrom, d = exploreDir, X = myHead;
    if (X != w.plainStep(A, d)) {
        int A2 = w.plainStep(A, d), C = w.plainStep(X, d ^ 2);
        learnDest[A*4+d] = X;  learnDest[X*4+(d^2)] = A;
        learnDest[A2*4+(d^2)] = C; learnDest[C*4+d] = A2;
        // (proposal 3 mirrors these four through w.sym)
        if (!trail.empty() && trail.front() == A) trail.insert(trail.begin(), X); // body continues behind the portal
    }
    exploreRound = -100;
}

// emitSonar(), next to the PORTAL_WARN block (single-step or no move)
if (UNK_EXPLORE && !w.known && pending.size() <= 1 && !w.portalSide.empty()) {
    int at = pending.empty() ? myHead : pending.back();
    int face = lastMoveDir >= 0 ? lastMoveDir : myDir;
    for (int d = 0; d < 4; d++)
        if (w.portalSide[at*4+d] && d != (face + 2) % 4) warnDirs[d] = true;   // knock
}
// (the existing PORTAL_ECHO_GUARD bookkeeping then records probeMask/probeTile/probeRays)

// readMessages(), after the echo-guard block
if (UNK_EXPLORE && probeMask && probeRound == round - 1 && probeTile == myHead) {
    unkEchoRound = round; unkEchoTile = myHead; unkEchoMask = probeMask;
    unkEchoClean = probeRays == __builtin_popcount((unsigned)probeMask) &&
                   in.echoes[1] + in.echoes[2] + in.echoes[3] + in.echoes[4] == 0;
}

// decide(): desire gate, computed before the scoring loop (it also feeds the lure in pearlValue)
int hunger = round - lastGrowRound;
exploreDesire = UNK_EXPLORE && !w.known && myLen < KING_MIN_LEN &&
    ((regionClosed() && hunger >= UNK_EXPLORE_HUNGER_CLOSED) ||
     (hunger >= UNK_EXPLORE_HUNGER && nearestVisiblePearlDist() > 6));
// regionClosed(): BFS over w.nxt from myHead (portals are -1 there), stop at 600 tiles;
//                 true if no reached tile has w.lastSeen < 0.

// decide(): after the per-direction loop, before KING_ESCAPE
bool exploreMove = false;
if (exploreDesire && unkEchoRound == round && unkEchoTile == myHead && unkEchoClean)
    for (int d = 0; d < 4; d++) {
        if (!((unkEchoMask >> d) & 1) || step(myHead, d) >= 0) continue;     // only unknown portal sides
        if (round - edgeCrossRound[myHead*4+d] < UNK_EXPLORE_COOLDOWN) continue;
        if (threatAt[myHead] > 0 && myLen >= 6) continue;                      // don't explore while a big dragon is hunted
        double sc = UNK_EXPLORE_SCORE + 0.3 * std::min(hunger, 60);
        if (sc > best) { best = sc; bestD = d; bestDepth = SURVIVE_DEPTH; exploreMove = true; }
    }
if (exploreMove) { exploreFrom = myHead; exploreDir = bestD; exploreRound = round;
                   edgeCrossRound[myHead*4+bestD] = round; lastPortalRound = round; }
// emitMove(bestD) already handles t<0 (pending stays empty); updateTrail's rebuild then keeps the old trail.

// pearlValue(t, s): lure mouths while the gate is open
if (UNK_EXPLORE_LURE > 0 && exploreDesire && lureTile[t]) v = std::max(v, UNK_EXPLORE_LURE);
// lureTile[t] (per turn): t has a portalSide d with round - edgeCrossRound[t*4+d] >= UNK_EXPLORE_COOLDOWN
//                        and no dirty knock from t in the last 5 rounds.
```

**Expected effect.**
- Blind Trauma/Default/Portals/QoS/Schooltime, and lesson islands/vaults: large wins against the no-cross baseline. On Trauma the baseline starves: its start room holds 0.7% of the pearl rate.
- Gen and genhold: roughly neutral (±2%).
- Ladder (known maps): bit-identical, since everything is gated on `!w.known`.
- Explore-crossing fatality should come out at 1-3%.

**Risks.**
- Convoy jams at single-edge doors. The knock sees an ally head, so both sides back off, but the lure could pull them back: cap it with the 5-round dirty memory.
- Dead-end exits (2% ranked; Portals map 20%).
- The sealed side of a door may be where the enemy is. The threat check is blind across the portal.
- `probeRays` pollution from king or relay rays: kings are excluded by myLen < 10, and relays are dropped by PROBE_SOLO.
- CPU: regionClosed BFS once per turn, O(N) ≤ 4096. Fine.

### 2. `UNK_EXPLORE_RETURN` (let learned links carry *value*, not movement)

After proposal 1, a dragon that has explored into a vault knows the door. Today bfsFrom can't value what lies behind it, so the dragon returns only through the hunger gate.

**Where.** `bfsFrom()`.

**Change.** When it pops a tile u with `learnDest[u*4+d] >= 0` and `d` is not blocked, push `learnDest` with distance `du + 1 + UNK_RETURN_EXTRA` (6). Mark the candidate as "via door" rather than moving there. The actual crossing still needs rule 2's clean knock. This lets pearl memory behind a known door pull the dragon to the mouth (the lure), and the door opens only on a clean knock.

**Expected effect.** Fewer idle rounds between trips into vaults and islands, with no change to the crossing safety.

**Risk.** Reintroduces some of LEARN_PORTALS' pull. Keep `UNK_RETURN_EXTRA` large.

### 3. `UNK_LINK_MIRROR` (a learned link teaches its mirror)

- **Evidence.** Links respect symmetry on 1740/1740 crossings (section 1).
- **Where.** At the learn-on-cross point in `updateTrail()`. It needs `w.sym`.
- **Change.** Split `inferSymmetry()` into infer-only (no wall mirroring; the wall mirroring is what INFER_SYM tested at 0.519 vs 0.544) plus the existing apply step. When `sym > 0`, also set `learnDest[mirror(A)*4+mirrorDir(d)] = mirror(X)` and the other three crossings.
- **Effect.** It doubles learned doors, and the mirrored door is the *enemy's* copy: warn and probe coverage there, plus raid routes.
- **Risk.** A wrong symmetry guess could create a false door. INFER_SYM was correct on all tested maps, and a false door is still knock-gated.

### 4. `UNK_LINK_SHARE` (knocks carry the portal id, so allies learn doors they never crossed)

- **Where.** `encodeWarn`/`decodeWarn` (an unknown-map variant) and `readMessages()`.
- **Change.** A knock payload carries (A, d, portal id k), using the WARN bits: tile 12, dir 2, id 7, round 9. The receiver sits on the ray line beyond the partner edge, so it has usually seen the partner edge with id k in its vision (portalSeen). If it has, it links both edges exactly (`notePortal`, but writing into learnDest).
- **Effect.** Newborns and neighbours learn doors without paying a crossing.
- **Risk.** The check bits drop from 37 to 30: fine. It also changes the known-map warn format unless it is kept to `!w.known`.

### 5. `UNK_EXPLORE_NOSPLIT` (no split while our body straddles a door we only just learned)

- **Where.** The split gate in `decide()`: `threatened ||= UNK_EXPLORE_NOSPLIT && round - lastPortalRound < myLen`.
- **Why.** The child is the rear k segments. If the crossing happened within the last myLen rounds, the child may be born with its neck across a portal. On unknown maps NEWBORN_NECK_GUARD only helps where learnDest is known to that child, which it never is, because the child is a fresh process.
- **Effect.** Small. Removes a rare newborn death mode that proposal 1 creates.

## 5. Test plan (for the main agent)

1. **Mechanism check (1 game per map, with debug on).** Run blind Trauma, Default, Portals and QoS, plus lesson islands_a and vault_a.
   - Count explore crossings per game, their fatality, knocks per game, and the dirty share.
   - Pass: fatality ≤ 3%, and dragons leave the Trauma start room within about 40 rounds.
2. **`unseen_eval.py "bot:-DUNK_EXPLORE=1" --base variants/v24 --sets gen,blind,lesson`**, seeds 2.
   - Expect: blind and lesson clearly above 0.5, with Trauma, Default, islands and vaults near 1.0; gen about 0.5.
   - Then `--holdout`.
3. **The asymmetric check (the key one; the self-play sets hide the cost of not crossing).** On the 9 ranked portal maps, 4 seeds each (72 games per run, 144 total):
   - `pool.py "bot:-DNO_KNOWN_MAPS=1 -DUNK_EXPLORE=1" --pool variants/v24` against `pool.py "bot:-DNO_KNOWN_MAPS=1" --pool variants/v24`. The opponent knows the maps and crosses.
   - The difference is how much of the portal gap proposal 1 recovers against a portal-competent opponent. That is the tournament situation.
4. **Ladder with map knowledge:** must be identical. A quick sanity run of 10 games is enough.
5. **Sweeps, only if step 2 passes:** `UNK_EXPLORE_HUNGER` 15/25/40, and `UNK_EXPLORE_LURE` 0/0.4/1.0. Then add proposals 3, 2, 4 and 5 one at a time, on the blind + lesson + asymmetric sets.
6. **Server:** if local steps 2-3 look good, one small batch of about 10 challenges on Trauma and Default with `NO_KNOWN_MAPS=1` builds would show real-opponent behaviour. Leave that decision to the main agent (60 games/hr budget).
