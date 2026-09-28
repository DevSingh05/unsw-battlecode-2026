# Schooltime (ranked map id 9): map-specific plan

Data: 66 of our games (v7 13, ch5 5, ch6 15, ch7 30, ch8 3), plus 21 top-team games (`notes/replays/permap` 10 and `notes/replays/kings` 11). Scripts are in the session scratchpad (`sch_an.py` builds per-game caches with `replay_sim`; `sch_rep.py` prints the reports). Every number below comes from those runs.

## 1. The map

- Size 60x40, mirrored left-right (x ↔ 59-x; the file says `SYMMETRY y`). Mirrored tiles share a pearl countdown.
- Starts (head first). Team 0/A: (3,2), (16,3), (23,3). Team 1/B: (56,2), (43,3), (36,3). They all start in the top strip. Each starter makes a 3+2 split at round 0, so each team has 6 dragons.
- **The yard.** This is the key feature, and it is new in our notes. The centre-bottom region, 204 tiles at x 22-37 and y 24-39, **can only be reached through portals 0 and 1**. Without portals, no start can reach it.
  - There are exactly 4 inside mouth tiles, all on row 25: (28,25), (29,25), (30,25), (31,25).
  - Outside mouths, portal 0: (11,25) moving W arrives at (28,25); (10,25) moving E arrives at (29,25).
  - Outside mouths, portal 1: (49,25) moving W arrives at (30,25); (48,25) moving E arrives at (31,25).
  - Vision does not pass through portals, so an enemy can appear on a mouth tile without warning.
- **The pool** sits inside the yard: 26 tiles at x 27-32, y 34-38, with gap [1,20]. That is about **2.5 pearls per round**, roughly a third of all spawn income on the map, packed into 1% of its area.
  - The rest of the map spawns slowly: 54 tiles at [20,50], 122 at [20,80] (the maze 'o' clusters) and 124 at [20,200].
  - The pool has no [1,1] tiles, which is why notes/10 said "no hot tiles here". The pool is the equivalent.
  - The pool is a full, open room (degree 4 almost everywhere). That makes it a good home for a king.
- The two 115-tile side rooms (x 3-18 and 41-56, y 23-34) and the 32-tile box at (27-32, 4-9) cannot be reached at all.
- **Shortest paths**, from a portal-aware BFS on the known map:
  - Team A inner (23,3): S to (21,10), then portal 4 to (46,18), S to (48,25), portal 1 to (31,25), then S to the pool at (32,35).
  - Yard entry takes about 21 steps; the first pool tile takes 33. The middle start (16,3) takes 36 and the outer (3,2) takes 39.
  - Team B mirrors this through portal 5 to (13,18) and portal 0 to (28,25).
- The maze band (y 8-20) is full of 1-wide corridors and portal ends: portals 2-5 and 8-11 all end at y 11-21.

## 2. How we lose here

Record in this data: 20 wins and 47 losses.

**Split by who used the yard** (≥100 eats inside the yard):

| | we win | we lose |
|---|---|---|
| neither team | 15 | 34 |
| opponent only | 2 | **13** |
| us only | **2** | 0 |

**We almost never go to the yard.**
- Our longest (L≥10) spent **0% of rounds 250-499 in the yard in 36 of 38 round-limit losses**.
- In 16 of those losses, the opponent's king spent 41-100% of those rounds there.
- The opponent kings that reached 70, 76 and 84 were all yard kings: 411168, 403827 and 380694.
- Our few yard games were big wins: 411181 (king in yard 90%, won 61 v 43), 386379 (97%, 49 v 21), 415842 (99%, 44 v 17).

**Why our bot ignores the yard.** Pearl value is discounted by `PEARL_GAMMA` 0.82 per step, and 0.82^21 ≈ 0.015. The yard is also behind two blind portal crossings, and on Schooltime `RP.kingPortal=100` keeps L≥10 dragons from crossing any portal at all.

**Income and swarm size, v9/v10 (ch7/ch8), 24 losses:**

| round | 100 | 200 | 300 | 400 | 499 |
|---|---|---|---|---|---|
| units us / them | 14.5 / 21.5 | 31 / 45.5 | 18.5 / 62 | 4 / 47 | 2 / 22 |
| longest us / them | 3 / 3 | 4 / 4 | 8.5 / 6 | 14 / 17 | 17 / 26 |

- Spawn eats per game: us **190**, them **445**.
- Loss types: 5 of 24 were eliminations (Yyy, BANG, Matcha Latte, Just Keep Swimming, Hypr Series), and 9 more ended with ≤2 units.
- In those games we make only 8-25 splits per 100 rounds, against 50-80 for the opponent.
- They grind us down with rams at r100-300. Our deaths per 100 rounds there are mostly `ram (we moved)` 5-20 and `rammed` 5-15; see the elimination table in the scratchpad output.
- So the root problem is food. We never reach the unit cap, so we lose the swarm war, and the king race after it.

**Big dragons.**
- ch7/8 losses: L≥10 deaths are 1 per game (few big dragons exist).
- v7/ch5/ch6 losses: 11 per game, 172 length, **10.2 of them in the maze band**. Causes: HitSelf 5.0, ally body 3.2, rammed 3.0.
- Our king (L≥10, r≥200) is in the maze band 61-65% of the time. Winning kings in top games are there 23% of the time and in the yard or bottom about 45%.

## 3. How top teams play Schooltime

**Opening rush to the yard.**
- In 9 of 16 top round-limit games, the winner (or both teams) sends dragons into the yard from turn 0. They arrive at **r21-22** (zitian/"dev test 1", 中国人能飞, 龙虎豹) or r27-36 (second and third runners).
- The runner is the length-2 split half of the **inner starter**. It follows the exact BFS path in §1: (23,3) → (21,10) → portal 4 → (46,18) → (48,24) → portal 1 → (31,25) → S to the pool by r33. Team B mirrors this through portals 5 and 0.
- Only **2-5 dragons walk into the yard by r100** (中国人能飞 is the exception with 12-15). Everything else is **born inside** by splitting on pool food.
- Distinct dragons in the yard per 50 rounds: 11-16 by r50, then 39-55 during r50-350.

**Yard income** (eats inside the yard per 100 rounds, owners):

| r0-100 | r100-200 | r200-300 | r300-400 |
|---|---|---|---|
| 77-113 | 130-240 | 150-240 | 140-200 |

That is 30-45% of the team's eats. Units at r100 are 46-64, against our 14.5.

**Kings.**
- The winner's longest spends **47-93% of rounds 250-499 in the yard** in 10 of 16 round-limit games.
- Final kings there: 56, 58, 61, 62 and 62.
- The king is simply one of the yard-born split children.

**Contested yard.**
- In 352669 both teams arrived at r21. STAR took it over at r125-175 with a mass of L3 rammers: A's L6-11 dragons died head-on in the pool. From then on STAR held 30 units in the yard until r350.
- Yard control is decided by the number of small rammers, not by size.

**Enemy intrusions** into an owned yard are rare: 1-5 distinct enemy dragons per 50 rounds.

## 4. Proposed behaviours

`D[t]` is a static, portal-aware BFS distance from the 26 pool tiles, computed once with `step()`. `yard[t]` is the flood fill from (29,36) using only non-portal steps (`step(u,d)==w.plainStep(u,d)`). Both are static members of the module.

### S1. Opening yard rush (the main fix): SCH_RUSH
- **Hook:** `schooltimeScore`.
- **Who.** Decide once per process (each dragon is its own process):
  - `rusher = (round <= 3 && D[myHead] <= 37) || (!yard[myHead] && D[myHead] <= 14)`.
  - With 37, the inner and middle starters' r0 halves qualify, which gives about 4 runners and matches the top teams' 2-5 walk-ins. The outer starter (D 39-40) stays to farm the maze.
  - The second clause catches split children born near the mouths.
- **Pull.** While `rusher && !yard[myHead] && round < 90 && myLen <= 6`, add `score += 8.0 * (D[myHead] - D[t])` (+8 for a step closer, -8 for a step away).
  - 8 is below one adjacent pearl (about 8.2) and far below the death and threat penalties (12-150+), so rushers still grab food on the way and still dodge.
- **Stop.** Clear `rusher` on first entering the yard. From then on, normal pearl scoring keeps the dragon at the pool, because 26 tiles of food sit within about 5 steps.
- **Evidence.**
  - The 13-2 split in §2.
  - Top rushers arrive at r21 on exactly this path.
  - The pool holds all 26 pearls at r21-33, because every tile fires within its first 20 rounds and then holds its pearl.
  - Yard owners have 46-64 units at r100; we have 14.5.
- **Expected effect.** Doubles our early income; fixes the swarm-war losses (elimination or ≤2 units, 14 of 24 ch7/8 losses) and the king race.

### S2. Keep the factory: one-way yard doors (SCH_HOLD)
- **Hook:** `schooltimeScore`.
- **Rule.** For `round < 350`: if `yard[myHead] && !yard[t]` (stepping out through a mouth), add `score -= 30`.
  - Exempt dragons when `feedPhase()` is on and the known king (`kingTile`) is outside the yard.
- Also, from r0: if `yard[t]` and t is one of the 4 inside mouth tiles, add `score -= 6` so we don't park on arrival tiles (inbound allies arrive blind).
- **Evidence.**
  - Owners keep about 30 units in the yard steadily from r175 to r350.
  - All of our ally head-on deaths are through portals (notes/09: 19.6 per game, 100% portal).
  - Portals 0 and 1 are the yard's only doors, so two-way traffic there is exactly the blind head-on case.

### S3. Yard king (SCH_YKING)
- **Hook:** `schooltimeScore`, plus one RP line.
- **Who.** From `round >= RP.kingSeedRound` (150), for `kingSelf || iAmKing() || myLen >= 10`.
- **Outside the yard.** Add `score += 5.0 * (D[myHead] - D[t])`.
  - Cancel the Schooltime big-dragon portal penalty for the crossing into the yard: `if (!yard[myHead] && yard[t]) score += RP.kingPortal;`. Otherwise `kingPortal=100` blocks the only entrance.
  - Drop the pull on any turn when a visible enemy head is within 3 of the king's head. The normal threat and keep-away terms then decide the move.
- **Inside the yard.** Let `m` be the min Manhattan distance from t to {(28,25),(29,25),(30,25),(31,25)}. If `m <= 3`, add `score -= (4 - m) * (10 + myLen)`. This keeps the king out of the row 25-28 band, where intruders appear blind.
  - No other pull is needed: the pool feeds it.
- **Evidence.**
  - Top winners' kings are in the yard 47-93% of rounds 250-499, and their final kings there reach 56-62.
  - Ours are there 0% in 36 of 38 losses.
  - Our three yard-king games were all wins, 44-61 long.
  - 10.2 of our 11 big deaths per loss (v7-ch6) happen in the maze band, which the yard king avoids.

### S4. RP settings to test with S1-S3
- Keep `RP.crowd=3` (it spreads the yard swarm).
- Test `PM_SCH_KPORTAL` 100 against 0 once S3 exists. The penalty was a maze-portal fix, and S3 cancels it for the yard door anyway.
- Test `PM_SCH_KS` 150 against 120. Yard-born children reach L10 by r140-200 in the top games; the notes/08 winners reached 10 at about r140.

## 5. Implementation sketch (`bot/maps/schooltime.hpp`)

```cpp
std::vector<int> schD, schYard; int schRusher = -1;
void schInit() {
    if (!schD.empty()) return;
    schD.assign(w.N, 1 << 20); schYard.assign(w.N, 0);
    std::vector<int> q;
    for (int y = 34; y <= 38; y++) for (int x = 27; x <= 32; x++) {
        int t = w.idx(x, y); if (w.gmin[t] == 1 && w.gmax[t] == 20) { schD[t] = 0; q.push_back(t); } }
    for (size_t i = 0; i < q.size(); i++) for (int d = 0; d < 4; d++) {
        int v = step(q[i], d); if (v >= 0 && schD[v] > schD[q[i]] + 1) { schD[v] = schD[q[i]] + 1; q.push_back(v); } }
    q.assign(1, w.idx(29, 36)); schYard[q[0]] = 1;
    for (size_t i = 0; i < q.size(); i++) for (int d = 0; d < 4; d++) {
        int v = step(q[i], d); if (v >= 0 && v == w.plainStep(q[i], d) && !schYard[v]) { schYard[v] = 1; q.push_back(v); } }
}
double schooltimeScore(int t, int d) {
    schInit(); double s = 0;
    if (schRusher < 0) schRusher = (round <= 3 && schD[myHead] <= 37) || (!schYard[myHead] && schD[myHead] <= 14);
    if (schYard[myHead]) schRusher = 0;
    if (schRusher && round < 90 && myLen <= 6) s += 8.0 * (schD[myHead] - schD[t]);          // S1
    if (round < 350 && schYard[myHead] && !schYard[t] && !(feedPhase() && !schYard[kingTile])) s -= 30; // S2
    ... // S3 as above
    return s;
}
```
The sketch has two unchecked details:
- It assumes `w.gmin` and `w.gmax` are filled for the known map. They are: `adopt()` copies them.
- `kingTile` may be -1 before any king ping. Guard that before indexing.

## 6. Test plan
1. Build S1 alone as a flag. Run `tools/pool.py` on Schooltime only (one batch, `--jobs 6`) against v10h.
   - Check with `replay_sim` that yard eats per game are above 100 and that runners arrive by r25.
2. Add S2, then S3, one at a time, same batch size.
3. Self-play cannot show the contest against yard-rushing opponents. Validate with Schooltime challenges against ranks 40-100.
   - Opponents that rush: err404, :3, uhhhhhhhh, winner or quitter, Deer Park, QgQ.
   - Opponents that don't: Yyy, BANG, Matcha Latte.
   - The user must approve before any challenges are launched.
