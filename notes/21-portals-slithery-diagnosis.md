# 21: Why we lose on Portals and Slithery Fight (29 Sep 2026)

**Data.**
- **v28 (main set):** every Portals and Slithery game in `replays/v28` (ledger). That is 56 games:
  - Portals: 28 games, 14 W / 14 L. Ranked 2/7 (L 562383, 571913, 576413, 591003, 595262; W 576787, 603462).
  - Slithery: 28 games, 9 W / 19 L. Ranked 5/11.
- **Older versions, for comparison:**
  - There are no v24-v27 Portals or Slithery replays locally: `v19plus` ends 09-28 23:19 and `v28` starts 09-29 05:18.
  - So "old" means v16-v23, from the `v16` and `v19plus` ledgers: Portals 14 (12 W / 2 L), Slithery 11 (6 W / 5 L).
  - Where it matters, old is split into v16-v20 (before `LATE_SPLIT_ROUND`) and v21-v23.
- All 81 games went to round 500. Neither map has had an elimination.
- The `ab_*` batches have no Portals or Slithery games.

**Scripts.** All in `notes/tools/porsli/`. They are read-only over the replays and run from the project root.
- `collect.py` builds `games.pkl`: timelines, eats by phase and source, every death classified, splits.
- `report.py MAP VER` prints the per-game table and the loss/win aggregates.
- `king.py`, `kingflow.py` and `kingloss.py` cover king growth, where feeder pearls go, and where the king's length goes. `drops.py` finds king collapses.
- `kings_n.py` counts how many of our dragons broadcast as king. It decodes our own sonar values: the bit layout is known, but the checksum isn't checked, so it uses plausibility tests only.
- `informed.py` shows who has heard a king. `feeders.py` shows what feed-eligible dragons do.
- `kingtube.py` covers big-dragon tube use on Portals.
- `bigportal.py` and `exitscan.py` cover fatal portal crossings together with the crosser's own echo from the previous round. `exitscan.py` covers all maps.
- `newborn.py` and `kingsuicide.py` cover new split children of L≥10 that die. They cover all maps.
- `board.py GAME ROUND ID [box]` prints an ASCII board just before that dragon acts.
- `botrun.py BIN GAME ID R0 R1`, `feedbot.py` and `feeddbg.py` re-run a compiled v28 on reconstructed views, via `rams/botview.py`. No games are played.
  - `v28dbg.diff` adds two debug prints (feed state and echo state) and nothing else.
  - v28 reproduced 97% of 60 sampled feeder decisions and every one of the 9 key decisions quoted below.

**Caveats.**
- `sim2` counts original starters one segment too long until their first split, so the Slithery r50 "longest" is inflated by 1.
- Samples are small: 14 or 19 losses per map. Per-game sd of the final longest is 7-10.

---

## TL;DR

**How games end.** Every game on both maps is decided on the longest dragon at r500, and **we lose with more total mass**:
- Portals losses: longest 23.7 against 37.1, but total mass 86 against 61.
- Slithery losses: longest 41 against 57, total 151 against 159.

Our king forms on time and then starves. Four mechanisms account for this: three are general, and one is specific to Portals.

**M1. King fragmentation (GENERAL).** The feed stream is split across 8-19 self-declared "kings", so the real king gets a fraction of it.
- Evidence:
  - We have 8-14 distinct king broadcasters per 50 rounds on Portals and 14-19 on Slithery, and 5-10 of them are L≤5.
  - Only 11% (Slithery) and 32% (Portals) of our small dragons in r380-480 have heard the *real* king. Yet 65-72% have heard *some* king.
  - Bot re-runs: 79% (Slithery) and 43% (Portals) of feed decisions target a lesser king.
  - King corpse intake r400-500: 8.8 per 100 rounds on Slithery against 20.5 for the opponents.
- Fix: new flag `KING_FOCUS`. A small candidate steps down once it hears one clearly longer king, and feeders and relays follow the longest fresh king.

**M2. Portals: the swarm never consolidates (MAP-SPECIFIC).**
- Evidence:
  - `LATE_SPLIT_ROUND=450` and the pocket churn keep 22-24 small units holding 55 mass at r450, against 5 units and 13 mass for the opponent.
  - Our king holds 20% of our mass at r450 (theirs 51%) and 28% at r499 (theirs 66%).
  - We do 92-98 open small splits per game in r360-450; opponents do 25-43.
  - By era: units at r450 went 4.8 (v16-v20), 14.7 (v21-v23), 22.7 (v28), while the final longest went 35.6, 31.4, 28.0.
- Fix: `PM_POR_LATESPLIT=0`, plus the general variant `LATE_SPLIT_NEEDS_ENEMY`.

**M3. New reverse-split children of big dragons kill themselves (GENERAL).**
- Evidence:
  - Across all v28 games there are 72 deaths of L≥10 children within 3 rounds of birth. 47 of them are a deliberate backward move into their own neck:
    - Slithery 24 (434 length, 0.86 per game);
    - Schooltime 21;
    - Portals, Default and Trophy 1 each.
  - 43 of the 46 on Slithery, Schooltime and Portals happen at r≥420.
  - In 20 of the 24 Slithery cases the real king was 7 or more tiles away. The child "feeds" a stale king broadcast whose only visible dragon is its own L2 parent.
  - Game 581135 was lost this way: an L48 child at r490, final 24 v 38.
- Fix: `FEED_STALE_GUARD`.

**M4. Big dragons walk out of 1-wide portal corridors into an echoed body (GENERAL; the Portals tubes are the worst case).**
- Evidence:
  - In 33 big (L≥8) fatal crossings on Portals, 31 had no alternative move.
  - In 24 of them our own ray on the previous turn had already hit a dragon at the exit. In 8 there was no ray, because the dragon was newborn.
  - The −30 body-echo penalty is irrelevant when the crossing is the only move.
  - v28 L≥8 losses per game: Portals 0.43 (6.1 length), Schooltime 0.77 (12.5 length).
- Fix: `ECHO_EXIT_HOLD`. Split 2 off and stay one turn, probe again, and only then cross.

**Portals module verdict.**
- **Keep POR_PULL.** The economy is ours: units at r100 are 31 against 25, and r0-100 hot+spawn eats are 159 against 105.
- **Keep POR_KING_PULL and `PM_POR_KPORTAL=0`.** Our big dragons eat 17.6-22.9 tube pearls per game, 0.11 per move against the opponents' 0.044. That is worth more than the roughly 5 length per game we lose at exits, and M4 recovers most of that loss.
- **POR_EXIT is fine but insufficient.** It checks the exit only when the dragon enters the tube; the exit comes 5 blind moves later.
- **The losses do not come from the module.** They come from the generic endgame: M1-M3 plus LATE_SPLIT.

| # | mechanism | scope | where it bites | fix (flag, default 0) |
|---|---|---|---|---|
| M1 | king fragmentation: zombie small kings + feeders follow the last-heard king | general (big / walled / portal maps, any partial sonar coverage) | Slithery r400-500 king growth 10 v 22; Portals 17 v 37 | `KING_FOCUS` |
| M2 | late small splitting + pocket churn to r450 on a no-contact map | Portals (general variant) | Portals r450: king share 0.20 v 0.51 | `PM_POR_LATESPLIT`, `LATE_SPLIT_NEEDS_ENEMY` |
| M3 | newborn big child feeds a stale king (its L2 parent) | general | Slithery 0.86/g (15.5 length/g), Schooltime 0.68/g | `FEED_STALE_GUARD` |
| M4 | blind exit with no alternative after an echoed body; newborn at a mouth unprobed | general (portal corridors) | Portals tubes, Schooltime | `ECHO_EXIT_HOLD` (+ `ECHO_BIG_MULT`) |

---

## 1. Records and timelines (v28; means; cells are us / them)

### Portals (28 games: 14 L, 14 W)

| | r50 units | r100 units | r200 units | r300 units | r400 units | r450 units | r499 units | total r100 | total r300 | total r499 | longest r300 | longest r400 | longest r450 | longest r499 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **L (14)** | 24.9 / 13.1 | 31.4 / 25.1 | 33.9 / 34.3 | 34.4 / 31.3 | 27.0 / 15.4 | 23.9 / 7.5 | 12.7 / 5.0 | 74 / 62 | 84 / 89 | 86 / 61 | 4.4 / 7.9 | 13.1 / 19.1 | 16.7 / 30.1 | **23.7 / 37.1** |
| **W (14)** | 24.1 / 10.4 | 31.6 / 18.1 | 34.9 / 27.5 | 33.9 / 31.1 | 25.4 / 23.9 | 21.5 / 15.1 | 11.5 / 9.1 | 74 / 45 | 84 / 81 | 95 / 52 | 4.9 / 5.2 | 15.6 / 8.9 | 21.9 / 12.7 | 32.2 / 17.6 |
| old W (12) | 20.6 / 13.8 | 31.0 / 22.6 | 35.3 / 27.2 | 33.1 / 26.1 | 18.0 / 12.2 | **9.7** / 9.1 | 6.1 / 7.4 | 73 / 56 | 82 / 73 | 72 / 54 | 4.9 / 6.2 | 16.8 / 13.7 | 27.3 / 18.0 | **34.8** / 20.5 |

- **Eats per game, losses** (hot / spawn / corpse; there are no enemy corpses, because the halves never touch):

  | phase | us | them |
  |---|---|---|
  | r0-100 | 50 / 109 / 104 | 31 / 74 / 48 |
  | r100-200 | 51 / 118 / 215 | 41 / 132 / 191 |
  | r200-300 | 51 / 121 / 234 | 39 / 121 / 214 |
  | r300-400 | 51 / 114 / 223 | 26 / 90 / 160 |
  | r400-500 | 42 / 100 / 173 | 14 / 29 / 72 |

  We out-eat every opponent in every phase.
- **Round the longest reaches 10 / 20 / 30** (median): losses us r346 / 436 / never, them r315 / 401 / 458.
- **King share of team mass:**
  - r450: 0.20 against 0.51.
  - r499: 0.28 against 0.66.
  - Mass in non-king dragons of L≥6 at r499: 40 against 17. Our 2nd longest is 13.7.
- **Deaths per game, losses** (count and length). Only 8/g are "rammed", and all of those are allies coming through portals.

  | | us | them |
  |---|---|---|
  | total | 693 | 474 |
  | pocket and sock churn | trapped/chose self 459, trapped by allies 72 | wall dives 161, trapped 134 |
  | portal crossings | 119 | 117 |
  | feed suicides | 32 | 13 |

  L≥8 deaths per game: us 1.8 (portal_ally 0.57), them 3.9 (portal_self 0.57, feed 1.29).
- **King collapses** (longest drops by 9 or more in one round) in the 14 losses:
  - 562383, r387: 26 → 4, a reverse-split cascade (§5);
  - 575213, r447: 27 → 6, a cascade plus a newborn blind tube entry (§5);
  - 565428, r434: 24 → 14, an ally L2 came through a portal head-on into the king parked on a mouth tile;
  - 595262, r495: 31 → 22, a newborn feed suicide (M3).

  The other 10 losses have no collapse; they are pure slow growth (M1, M2).

### Slithery Fight (28 games: 19 L, 9 W)

| | r100 units | r200 units | r300 units | r350 units | r400 units | r450 units | r499 units | total r200 | total r300 | total r400 | total r450 | total r499 | longest r300 | longest r350 | longest r400 | longest r450 | longest r499 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **L (19)** | 58 / 58 | 62 / 61 | 46 / 59 | 36 / 56 | 30 / 38 | 28 / 19 | 15 / 14 | 158 / 198 | 156 / 213 | 161 / 188 | 168 / 158 | 151 / 159 | 17.8 / 17.1 | 26.1 / 23.7 | 31.4 / 34.1 | 36.6 / 46.2 | **41.0 / 56.6** |
| **W (9)** | 56 / 55 | 62 / 59 | 45 / 61 | 34 / 60 | 29 / 43 | 25 / 25 | 17 / 23 | 156 / 180 | 153 / 199 | 166 / 185 | 163 / 162 | 167 / 178 | 22.8 / 13.7 | 28.7 / 17.3 | 34.3 / 22.0 | 42.2 / 33.4 | 47.9 / 32.9 |

- **We reach L30 first** (median r381 against r403) **and then stall.**
- **Longest gain per 50 rounds, losses:**

  | window | us | them |
  |---|---|---|
  | r250-300 | +10.3 | +2.7 |
  | r300-350 | +8.2 | +6.6 |
  | r350-400 | +5.3 | +10.4 |
  | r400-450 | +5.2 | +12.2 |
  | r450-500 | +4.4 | +10.4 |

  The opponent keeps 56 units at r350 and pours them into its king in r400-500. Their units go 38 → 19 → 14, and their king eats 10.7 and 9.8 corpses per 50 rounds against our 4.2 and 4.6.
- **Mass split at the end:** king share 0.28 against 0.37; 2nd longest 28.6 against 32.5.
  - Game 571912 at r450: we had [40, 36, 24, 23] (123 length in 4 dragons) against [51, 22, 16].
- **Eats, losses:** we out-eat them r0-400 (spawn 258-280 per 100 rounds against 149-223). In r400-500 we eat 186 spawn + 222 corpse, but little of it reaches the king.
- **L≥15 deaths per loss:**
  - us: rammed 1.0 (20 length), feed 0.74 (17), chose-self 0.47 (11), trapped 0.42 (10), about 58 length in all;
  - them: about 35 length.

  Most of our feed and chose-self deaths are M3 newborns (§3).
- **Rams on big dragons** (notes/maps/slithery_fight.md, Finding C) are still there: 1.0 per game on L≥15. They are secondary here and not re-analysed.

---

## 2. M1: king fragmentation (general)

**Code.**
- `updateKingship()` (`bot/main.cpp` ~1709), KING_V2 branch:
  - A dragon declares itself king at 2% per turn if `round >= kingSeedRound`, `myLen >= 3` and it has heard **fewer than 2** fresh kings.
  - It steps down only when it hears **two** fresh kings longer than `myLen+2`.
- `readMessages()` (~1660): `better = len > kingLen || id == kingId || round - kingRound > 6`. So once the current king has been silent for 6 rounds, the next king heard wins, however short it is.
- Relays forward only the current `kingId` (~1669).

On a 63×27 walled map, or on Portals, sonar reaches only part of the swarm (rays stop at kelp and at the first dragon). The result:

**King broadcasters.** Distinct dragons sending hop-0 king messages per 50 rounds (`kings_n.py`); the number in brackets is how many were L≤5:

| window | Portals L | Portals W | Slithery L | Slithery W |
|---|---|---|---|---|
| r250-300 | 8.1 (7.6) | 6.7 (5.6) | 17.5 (10.5) | 16.6 (10.3) |
| r300-350 | 9.2 (6.8) | 8.3 (5.7) | 16.4 (8.5) | 17.1 (8.7) |
| r350-400 | 9.8 (5.1) | 9.6 (5.9) | 16.4 (7.2) | 18.8 (7.3) |
| r400-450 | 10.6 (5.9) | 11.0 (4.6) | 15.7 (5.8) | 16.0 (5.2) |
| r450-500 | 13.6 (4.2) | 13.6 (4.1) | 14.2 (4.7) | 14.4 (2.8) |

- **Messages received that name a dragon of at least (longest − 2):**
  - Portals: 96% at r250, falling to 42% by r450-500.
  - Slithery: 15-28% all game.
- **Small dragons (L≤6) in r380-480 of losses:** heard any king within 12 rounds 65% (Portals) and 72% (Slithery); **heard the real king 32% and 11%.**
- **Bot state on sampled feed-eligible dragons** (`feeddbg.py`, v28 + debug prints):
  - Slithery (80 samples): 63 are feeding and **50 of them (79%) target a king shorter than (real longest − 2)**. For example, they head for L16, L11, L9 or L19 "kings" while the real king is L38-42. 10 of the 80 are themselves `kingSelf` (7 of them L≤5).
  - Portals (60 samples): 42 feeding, 18 (43%) at a lesser king, 11 `kingSelf`.
- **Feeders barely converge.** Per turn, a feed-eligible dragon steps closer to the real king 45-51% of the time and farther 40-46% (walls and portals BFS, `feeders.py`).
  - Eligible dragons that end by feeding near the real king: Portals 26%, Slithery 13-15%.
  - King corpse eats per 50 rounds r400-500: Slithery 4.2 / 4.6 against 10.7 / 9.8; Portals 7.7 / 7.4 against 11.8 / 7.4.
  - Feeder pearls that reach the king: Portals 22-31% (theirs 34-58%). Our other dragons eat the rest.

**Fix: `KING_FOCUS` (general; default 0).**
1. `updateKingship()`, KING_V2 branch:
   - A candidate steps down when it hears **one** fresh king with `len >= max(myLen + KING_FOCUS_GAP, 2*myLen)`.
   - A dragon may not declare while it hears such a king.
   - Two comparable big candidates are still allowed, which keeps the ram insurance on Slithery (their 2nd is 32.5 too). Zombie L3-5 kings go away.
2. `readMessages()`, after the message loop: `kingId`, `kingLen`, `kingTile` = the **longest** fresh (≤8 rounds) entry of `kingsSeen`, not the last one heard.
   - Relays already forward `kingId`, so the real king's message now travels 3 hops instead of competing with the small kings.

```cpp
// params.hpp
#ifndef KING_FOCUS
#define KING_FOCUS 0 // notes/21: small candidates step down for one clearly longer king; feed/relay the longest
#endif
#ifndef KING_FOCUS_GAP
#define KING_FOCUS_GAP 6
#endif

// updateKingship(), KING_V2 branch
int clear = std::max(myLen + KING_FOCUS_GAP, 2 * myLen);
if (kingSelf)
{
    if (freshKings(myLen + 2) >= 2 || (KING_FOCUS && freshKings(clear - 1) >= 1))
        kingSelf = false;
    return;
}
if (round >= RP.kingSeedRound && freshKings(-1) < 2 && myLen >= 3 && !(KING_FOCUS && freshKings(clear - 1) >= 1) &&
    rng.uni() < KING_DECLARE_P)
    kingSelf = true;

// readMessages(), right after the `for (uint64_t m : in.msgs)` loop, before "we can see the king ourselves"
if (KING_FOCUS)
{
    const KingInfo* bk = nullptr;
    for (auto& k : kingsSeen)
        if (round - k.round <= 8 && (!bk || k.len > bk->len))
            bk = &k;
    if (bk && (bk->len > kingLen || round - kingRound > 2))
    {
        if (bk->id != (kingId & 1023))
        {
            haveRelay = bk->round >= round - 4; // relay the longest one
            relayMsg = encodeKing(bk->tile, bk->len, bk->id, 1, bk->dir, bk->round);
        }
        kingId = bk->id; kingLen = bk->len; kingTile = bk->tile; kingDir = bk->dir; kingRound = bk->round;
    }
}
```
(When the relay switches kings, the hop count is reset to 1. That is slightly optimistic; keeping the original hop per `kingsSeen` entry is the exact version.)

**Expected effect.**
- Real-king coverage for small dragons rises from 11% (Slithery) and 32% (Portals) toward the 65-72% any-king coverage.
- If our r400-500 king corpse intake reaches the opponents' level, that is about +12 on Slithery and +4 to +8 on Portals at r499.
  - That would flip most Portals losses, whose median gap is 8.
  - It would flip about half the Slithery losses (gaps 4-28, median 15).
- **Risk.** A big second candidate can still step down and merge (lose half) if the king is at least twice its length. That is intended.

**General?** Yes: any map where sonar doesn't cover the swarm (walls, portals, big boards, unseen maps). On open maps like Default, relays already cover everyone and the rule rarely fires.

---

## 3. M3: new reverse-split children feed themselves to a stale king (general)

**Mechanism.**
1. A big dragon U-turns (trapped reverse split, `SPLIT L-2`, ~2725). The child is a fresh process.
2. On its first turn it reads the parent's (or another relayed) king broadcast, still carrying the parent's pre-split length.
3. It sees that "king" in view: the ids alias `&1023`, and the parent is right there, now L2.
4. From r420 (`KING_V2_MERGE_ROUND`) any length may feed, and `KING_V2_LOOSE` lets it die within 4 tiles. So `dieNow` fires: `MOVE (myDir+2)`, straight back into its own neck.

**Numbers** (`newborn.py`, all v28 games): L≥10 children dead within 3 rounds of birth.

| map | backward into neck (feed) | other causes |
|---|---|---|
| Slithery | 24 (434 length) | rammed 5, trapped 2 |
| Schooltime | 21 (430 length) | rammed 8, trapped 5 |
| Portals | 1 (L29) | portal 4 |
| Default, Trophy | 1 each | |

- 43 of the 46 backward moves on Slithery, Schooltime and Portals were at r≥420.
- In **20 of the 24** Slithery cases the real longest ally was 11-41 tiles away, so the corpse is not eaten by the king. Only 4 were real merges at distance ≤3.
- The bot re-run reproduces `-> feed suicide` in 6/6 sampled cases (`botrun.py`; FEEDDBG shows `kingLen` 14-50 at `age=0`).

**Key moment: 581135 (Slithery, Yueci Li; final 24 v 38).**
- r489: our L49 king (1810) at (21,12) steps N onto a pearl at (21,11), a tile boxed in by its own body at (20,11) and (22,11) and its tail at (21,10).
- Eating freezes the tail, so it has 0 exits at r490 and does `SPLIT 48`.
- The child 1816 (L48, head (21,10)) sees `kingId=1810&1023, kingLen=50` in its inbox and the L2 parent in view, so it plays `MOVE E` into its own neck.
- Our longest drops to 24. With 48 we would have won 48 v 38.

Same pattern:
- 585330 (Slithery): 5 children of L10-16 in r428-498, 63 length.
- 583961: L23 at r433.
- 578359: L38 at r471.
- 595262 (Portals): L29 at r495.
- Schooltime 597581 (L51, r476) and 567311 (L48, r450): won anyway.

**Fix: `FEED_STALE_GUARD` (general; default 0).**
- (a) When the king's head is in view and every visible segment of it lies at Chebyshev ≤2 from our head, the whole body is in view: set `kingLen` to the visible count. A further segment would be adjacent, so it would be visible too.
- (b) A child of L≥8 does not feed-suicide in its first 3 rounds.

```cpp
// member
int birthRound = -1; // first round this process played
// top of decide(): if (birthRound < 0) birthRound = round;

// readMessages(), inside "we can see the king ourselves"
if (FEED_STALE_GUARD && kingId >= 0)
{
    int vis = 0; bool inside = true;
    for (auto& sg : segs)
        if (sg.team == w.myTeam && (sg.id & 1023) == (kingId & 1023) && sg.id != w.myId)
        {
            vis++;
            int dx = std::abs(sg.tile % w.W - myHead % w.W), dy = std::abs(sg.tile / w.W - myHead / w.W);
            dx = std::min(dx, w.W - dx); dy = std::min(dy, w.H - dy);
            if (std::max(dx, dy) > 2 || portalExit[sg.tile]) inside = false; // body may continue out of view
        }
    if (vis > 0 && inside && vis < kingLen)
        kingLen = vis; // what we see is all there is (a 2-long parent, not the old king)
}

// shouldFeed(), first line
if (FEED_STALE_GUARD && myLen >= 8 && birthRound >= 0 && round - birthRound < 3)
    return false;
```

**Expected effect.**
- Slithery: about 20 wasted big-child deaths saved per 28 games, about 13 length per game of L10-48 dragons. That flips 581135-type games outright.
- Schooltime: about 18 events.
- The 4 true merges (king within 3) are kept by (a) whenever the king is really big and in view.

**General?** Yes. It is independent of the map, and any map with late U-turns is affected.

---

## 4. M2: Portals swarm keeps splitting and pumping to r450 (map-specific)

Portals is a solo race: the two halves are separate components (notes/maps/portals.md), so there are no enemy heads, no rams and no need for a reserve swarm. Still:

- **Late small splits.** Splitting stops at r360 on Portals (KING_V2 table), but `LATE_SPLIT_ROUND=450` (v21, `LATE_SPLIT_MAXLEN 5`) keeps every L≤5 splitting.
  - Open small splits r360-450: **v28 92-98 per game, opponents 25-43.**
  - Dead-end (pocket-pump) splits: 17-22 against 10-18.
- **Units and mass at r450, losses:** 24 units holding 80 mass, 55 of it in L<6 dragons, against 7.5 units, 62 mass and 13 in L<6.
  - Over the last 50 rounds, 33 of those 55 mass end up in *other* mid dragons, not the king: L≥6 non-king mass goes 9 → 40.
- **By era** (small n, but monotone):

  | | units r450 | longest r499 | total r499 |
  |---|---|---|---|
  | v16-v20 (no late split), 5 games | 4.8 | 35.6 | 67 |
  | v21-v23, 9 games | 14.7 | 31.4 | 78 |
  | v28, 28 games | 22.7 | 28.0 | 90 |

- The king seeds from any L3 at r250 and has to be fed by a swarm that is still busy splitting and diving into pockets. Our longest reaches 20 at r436, against r401 for the opponent.

**Key moment: 569009 (DESTINY 3; final 17 v 33; no big death at all).**
- r350: us [8, 4, 4, 3, …], 29 units; them [18, 4, 4, …].
- r450: us 32 units, 88 mass, longest **6**; them 4 units [25, 21, 18, 4].
- King broadcasters r450-499: 17 of ours, max L17.

**Fix: `PM_POR_LATESPLIT` (Portals; default -1 = keep 450, set 0).** Also a general variant `LATE_SPLIT_NEEDS_ENEMY` (N rounds; default 0): late splits only if this dragon saw an enemy head within N rounds. That is never true on Portals, and it keeps the swarm on contact maps.

```cpp
// RuntimeParams
int lateSplitRound = LATE_SPLIT_ROUND;
// applyMapParams(), after the KING_V2 table
if (n == "Portals" && PM_POR_LATESPLIT >= 0)
    RP.lateSplitRound = PM_POR_LATESPLIT;
// member, set while reading the view: any enemy segment visible -> lastEnemySeen = round
int lastEnemySeen = -1000;
// split condition (bot/main.cpp ~2529): replace the LATE_SPLIT_ROUND clause with
bool lateOk = RP.lateSplitRound > 0 && round < RP.lateSplitRound && myLen <= LATE_SPLIT_MAXLEN &&
              (!LATE_SPLIT_NEEDS_ENEMY || round - lastEnemySeen <= LATE_SPLIT_NEEDS_ENEMY);
... (round < RP.splitStopRound || lateOk) ...
```

- **Consider also `POR_ONEKING=1`** (it exists; local 0.55 on 120 samples). Portals has no rams, so a second candidate is pure waste. `KING_FOCUS` covers most of this.
- **Expected effect:** units at r450 back toward 5-15, and +4 to +7 on the final longest (the era trend). It is additive with M1.
- **Test locally first.** Portals is a solo race, so local self-play measures it exactly. Use `notes/tools/portals/prun.py`, which gives per-side finals.

---

## 5. M4: blind exits with no alternative (general; worst on Portals tubes)

**Portals tubes.** Each tube is spliced into one main-area edge: e → 4 pearl tiles → x, with 1-wide blind tiles in between. Once inside, the dragon has exactly one forward move out of the last tile.

`bigportal.py`, every L≥8 fatal crossing on Portals (v16-v28, 33 cases):
- **31 had 0 free alternatives.**
- The previous turn's own warn ray had hit an ally at the exit in 19 cases, an ally head in 5, no ray at all in 8 (all newborns), and kelp in 1.
- The blockers were usually passing through the exit: L3 at segment 2, or L6-7 at segment 3.
- Typical cases:
  - 590353 r471, L12 at (27,9): only move N to (3,6), which holds L6 1036 at segment 3.
  - 576413: L10 at r441 and L12 at r472, same geometry.
  - 571913 r461, L22 king.
- **Bot re-run of 571913 r461.** The echo state shows `mask=S, rays=1, echoes 0,1,0,0,0`, so `echoBodyDir[S]` is set (the path is long). But S is the only candidate, so the bot crosses. The bot re-run of 590353 is identical (`cand N score=-52`, the only candidate).
- Both our v28 losses and the opponents' show this. Our L≥8 deaths from it: 0.57 per game in losses, 0.14 in wins.

**Key moment: 575213 (ComTamSuonNuong; final 13 v 38).**
1. r446: our L28 king, 0 exits, `SPLIT 26`. The child is also trapped and does `SPLIT 25` at r447.
2. The newborn L25 is at tube mouth (8,11) with no probe of its own.
3. `portalsScore` pulls it into T3 (`cand E score=+35`, reproduced).
4. Its grandparent (the L3 1209) had walked into that same tube 3 rounds earlier. The L25 hits it at the first tube tile.
5. Our longest: 27 → 6.

**Same family: 562383 (Kamikaze, ranked; 15 v 38).**
- r387: the L26 king coils in (16-21, 10-15), with its head at (13,7) through a portal.
- It has 0 exits and does `SPLIT 24`. The L24 child also has 0 exits and does `SPLIT 22`, and so on through 20 and 18.
- The L18 steps W through the portal into the L22 child's neck: 26 → 4 L2s.
- Reverse-split cascades like this are rare (0.3-0.4 per game, opponents 0.2-3.0), but each one costs the king.

**All maps** (`exitscan.py`, v28, L≥8 fatal one-step crossings per game, with length in brackets):

| map | 0 alternatives, echo at exit | 0 alternatives, no ray | with alternatives, echo at exit |
|---|---|---|---|
| Portals | 0.29 [3.9] | 0.11 [1.8] | |
| Schooltime | 0.19 [2.9] | | **0.45 [8.5]** |
| Slithery | 0.11 [1.0] | | |
| Default | 0.04 | | |

**Minor: kings parked on a portal mouth.** 3 Portals king deaths (565428 L24, 576787 L21, 602415 L16) were an ally L2 crossing blind, head-on into the king standing on the exit tile.

**Fix: `ECHO_EXIT_HOLD` (general; default 0).**
- Suppose the chosen move is a blind portal crossing (`!visible[t] && t != plainStep`) and all of these hold:
  - `myLen >= ECHO_HOLD_MINLEN` (8);
  - the exit was echo-flagged (`echoBodyDir[d]`, or a head echo) **or not probed last turn** (newborn, or after a sprint);
  - no other candidate scores above −100.
- Then play `SPLIT 2`: the parent does not move, the warn ray re-probes from the same mouth, and the L2 child is a future feeder.
  - At most `ECHO_HOLD_MAX` (2) holds in a row. After that, reverse-split if `tailHasExit`, else cross.
- `ECHO_BIG_MULT` (try 4): multiply `PORTAL_ECHO_BODY_PEN` for L≥8, for the Schooltime cases that *had* alternatives.
- Optional `KING_MOUTH_PEN` (try 20): L≥10 dragons pay this to end a turn on a `portalExit` tile they are not about to cross from.

```cpp
// readMessages(): keep last turn's probe for decide()
probedMask = (probeRound == round - 1 && probeTile == myHead) ? probeMask : 0; // before probeMask is reused
// decide(), after `if (KING_ESCAPE && tryKingEscape(bestD)) return;`
if (ECHO_EXIT_HOLD && bestD >= 0 && myLen >= ECHO_HOLD_MINLEN && units < w.unitLimit)
{
    int t = step(myHead, bestD);
    bool blind = t >= 0 && !visible[t] && t != w.plainStep(myHead, bestD);
    bool risky = echoBodyDir[bestD] || !((probedMask >> bestD) & 1);
    if (blind && risky && secondBest < -100 && holdStreak < ECHO_HOLD_MAX)
    {
        out += "SPLIT 2\n"; pending.clear(); pendingSplit = true; holdStreak++;
        return; // emitSonar() still sends the warn ray from this mouth: next turn's echo decides
    }
}
holdStreak = 0;
// candidate loop, blind-portal block (~2634)
if (PORTAL_ECHO_BODY_PEN > 0 && echoBodyDir[d])
    score -= PORTAL_ECHO_BODY_PEN * (myLen >= 8 ? ECHO_BIG_MULT : 1.0);
```
(`secondBest` is the best score among the other directions, tracked in the candidate loop.)

**Expected effect.** Big deaths per game: about −0.35 on Portals (5 length), −0.5 on Schooltime (10 length), −0.1 on Slithery.
- 571913 (38 v 44) had an L22 lost this way. 575213 (13 v 38) had its L25 king lost to an unprobed tube entry.
- Each hold costs 2 length, as an L2 that can feed back.

**General?** Yes: any portal whose mouth is a 1-wide corridor. Unseen maps too, since `step()` knows learned portals.

---

## 6. Is the Portals module helping?

| part | verdict | evidence |
|---|---|---|
| `POR_PULL` (tube and sock valuation) | **helping, keep** | r0-100 hot+spawn eats 159 v 105; units at r50 25 v 13, at r100 31 v 25. Pre-module (notes/maps/portals.md): units at r100 = 3, first eat r160 |
| `POR_EXIT` (exit tile checked at entry) | neutral, insufficient | exit deaths happen 5 blind moves after entry: M4 |
| `POR_KING_PULL=1` + `PM_POR_KPORTAL=0` | **helping, keep** | L≥10 dragons: tube pearls 17.6 (L) / 22.9 (W) per game, 0.106 per move against the opponents' 0.044. Tube-related L≥10 deaths cost about 5-9 length per game; M4 removes most. Re-enabling `KING_PORTAL_PENALTY` on Portals would forfeit about 20 pearls per game |
| `POR_ONEKING=0` | mildly hurting | no rams on Portals; a second candidate only splits the feed. Turn on, or use `KING_FOCUS` |
| RP table (seed 250, split stop 360, feed 300, reserve 3) | undermined | `LATE_SPLIT_ROUND=450` overrides split stop 360 for L≤5: M2 |

---

## 7. General vs map-specific

- **General (apply to every map; they matter most on large, walled and portal maps, including unseen ones):**
  - M1 `KING_FOCUS`;
  - M3 `FEED_STALE_GUARD`;
  - M4 `ECHO_EXIT_HOLD` / `ECHO_BIG_MULT`;
  - the `LATE_SPLIT_NEEDS_ENEMY` variant of M2.
- **Portals-specific:**
  - M2 `PM_POR_LATESPLIT=0`;
  - `POR_ONEKING` (optional).
- **Slithery-specific, not addressed here:**
  - big-dragon rams in B's territory, 1.0 L≥15 per game (notes/maps/slithery_fight.md, S4 zones);
  - the comb and staircase self-traps (S3).

  These are secondary to M1 and M3 on the current evidence: our L≥15 losses split into rams 20 length, M3-type 28 length, and traps 10 length per loss.

## 8. Test plan (no batches were run for this note)

1. **Mechanism checks without games.** Re-run `feeddbg.py` and `botrun.py` with each flag on:
   - `KING_FOCUS`: the share of feeding decisions aimed at the real king (79% lesser now) should fall below 30%, and `kingSelf` among small dragons should fall to about 0.
   - `FEED_STALE_GUARD`: the 6 reproduced newborn suicides should stop.
   - `ECHO_EXIT_HOLD`: 590353 r471, 571913 r461 and 575213 r447 should print `SPLIT 2`.
2. **Local, when CPU is free:**
   - `notes/tools/portals/prun.py` on Portals, per-side finals, 60+ seeds. It is a solo race, so it is exact. Run M2 alone, then M1+M2.
   - The usual pool for regressions.
3. **Server A/B on Portals and Slithery** against the v28 opponents (bread first search, C--, SSS, DESTINY 3, Settlers, Outsider Traders). Judge by mechanism metrics as well as W/L:
   - `kings_n.py`: broadcasters and real-king share;
   - `kingflow.py`: king corpse eats r400-500;
   - `newborn.py` and `exitscan.py`;
   - king share of mass at r450 and r499.
