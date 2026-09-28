# 09: Why we lose (ch1 batch: v4 vs ranks 16-20, 50 unranked games)

Record: 16 W / 34 L. The losses split evenly: 17 eliminations and 17 losses on longest dragon at round 500. We are always team A.

| Map | W/5 | Elim losses | Size | Notes |
|---|---|---|---|---|
| Queen Of Spades | 1 | 4 | 25x35 | small, kelp-heavy |
| Default | 1 | 4 | 32x32 | |
| Devil | 2 | 3 | 32x16 | |
| Trophy | 3 | 2 | 25x25 | |
| Prisoners Dilemma | 2 | 2 | 32x16 | |
| Schooltime | 0 | 1 | 60x40 | largest map; all 4 other losses are on length |
| Slithery Fight | 1 | 0 | 63x27 | |
| Trauma | 1 | 0 | 48x24 | |
| Autarky | 2 | 1 | 54x18 | |
| Portals | 3 | 0 | 32x16 | |

Small maps end in eliminations. Big maps go to round 500 and are lost on king length.

Scripts (all in `notes/tools/`, all read-only over `replays/ch1/`):
- `loss_diag.py`: per-group timelines (count, maxlen, eats per dragon-round, deaths by cause, idle, sprints, splits). Run it with `--game ID` for a single game.
- `death_detail.py`: classifies every death: backwards move, age, kin/sibling, portal, rams while outnumbered.
- `split_waste.py`: split children that die within 3 rounds, and trapped vs. not-trapped deaths.
- `ram_value.py`: who eats the corpses a ram leaves behind, and how our last 5 dragons die in eliminations.
- `king_feed.py`, `king_peak.py`, `king_eats.py`, `king_deaths.py`, `big_selfkill.py`, `feed_eff.py`: king growth, feeding and king deaths.
- `replay_sim.py` gained one additive field: `deaths[i]['nbrs']`, the status of each of the 4 neighbours of the dying head (free, pearl, kelp, self, ally or enemy).

---

## Elimination losses (17)

Mean over the 17 games:

| round | 10 | 25 | 50 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|
| our dragons | 5.7 | 5.7 | 6.9 | 8.1 | 6.8 | 4.9 | 1.2 |
| their dragons | 5.4 | 6.3 | 9.9 | 14.2 | 16.4 | 15.5 | 13.7 |

- Both sides lose about the same number of dragons before round 100 (us 22.9, them 24.3). Their deaths are mostly their own mistakes (HitWall 30.9 and NoValidAction 19.4 per game).
- They out-split us from round 25 onwards: 24 vs 16.5 splits in rounds 50-100, and 43.5 vs 13.9 in rounds 200-300. Their pearls eaten per dragon-round is no better (0.09 vs 0.10). They simply have more heads, and more heads compound into even more heads.
- **Our rams are the biggest single cause of death: 34.6 per game.** That is 65% of all our deaths in these games. They ram us only 9.1 times per game.
  - **24.7 of our 34.6 rams happen while we have the same number of dragons or fewer.** In our wins only 5.6 of 26.5 do.
  - A ram trades one dragon for one. In a count race that is neutral at best, and the corpse pearls go to whichever side has more heads nearby. After our rams in elimination losses, **they eat 58.5 of the pearls per game and we eat 48.7**. In wins we eat 63% of them (52.6 vs 31.2).
  - Of our last 5 deaths in each elimination (85 in total), **40 are our own rams** and 31 are their rams.
  - Examples: 351237 (Devil), rams at r29, r31, r33, r36 and r44 with our count going 5→4→3→2 while they had 5-7; the game was lost by r44. 351215 (Default), rams at r191-r281 with 5 dragons against 28-56. 351225 (Default), 24 rams while outnumbered, e.g. r164 at 2 vs 31.
- Gating on our own count separates the two cases well. A "units < 8 → no ram" rule would block **11.5 rams per game in elimination losses** but only **1.8 per game in wins** (and 0.2 in length losses).

## Length losses at round 500 (17)

| round | 25 | 100 | 200 | 300 | 400 | 499 |
|---|---|---|---|---|---|---|
| our longest | 2.8 | 3.5 | 3.6 | 4.0 | 11.2 | 17.4 |
| their longest | 6.1 | 5.9 | 7.2 | 10.0 | 18.3 | 32.5 |

- **We start the king too late.** Every dragon splits at length 4 until round 350, so our longest stays at 4-5 until then. On Trauma and Schooltime the opponent reaches length 8 at round 24-363 (median about r130) and length 15 at round 181-404. We reach 8 at round 355-486.
- **Our king grows more slowly.** The team's current longest ate 27.9 pearls per game from round 300 on; theirs ate 42.8, of which 29.8 were own-team corpses. Their longest gains +22.5 from r300 to the end; ours gains +13.4.
- **Our kings die, mostly to themselves.** 26 deaths of our current longest dragon at length 10 or more cost 499 length in total. The opponents' equivalent deaths cost 286.
  - Self-trapped, all 4 neighbours blocked: 8. With our own swarm's bodies: +4 more.
  - Rammed by an enemy: 6.
  - Friendly head-on through a portal: 4.
  - The king killed itself by feeding: 2.
  - Trapped kings nearly always spent their last turns eating on every step in a tight curl. Examples:
    - 351219 r458: length **38**, walled in by kelp and its own body after eating on 11 of its last 13 moves. The team ended at 6 against 55.
    - 351210 r443: length 27 lost; final 21 vs 27.
    - 351231 r448: length 26 lost; final 24 vs 34.
    - 351201 r468: length 26 lost; final 20 vs 35.
  - Root cause: `surviveDepth()` is documented as "Assumes we don't eat". When a move eats, the tail does not advance, so the body tiles the look-ahead expects to be vacated are still occupied.
  - Across all length-limit games, 36 of our length-8+ dragons died HitSelf while trapped (451 length).
- **Feeding is mostly wasted.** There were 509 feed suicides in the 23 length-limit games, totalling 2,196 length and 1,213 pearls dropped. The actual longest dragon ate only **218 (18%)**, other allies ate 843, and enemies ate 33.
  - **246 of the 509 feeders were more than 8 tiles from the real longest dragon.** They fed a local "king": any dragon of length 8+ that broadcasts because it hasn't heard of a bigger one.
  - 55 feeders were length 8+. At r466 in 351229, feeders of length 18 and 17 died for a king of length 24.
- **Heavy churn in the swarm.** In length losses 113 of our 481 splits per game have the child dead within 3 rounds, and 59 die on their birth round. In 111 splits per game the parent's head has no free exit.
  - A normal split never checks `tailHasExit()`. Only the reverse split does.
  - We lose 102 dragons per game to friendly bodies (96 of them boxed in) and 19.6 friendly head-on pairs per game, **100% of them through portals**.
- Idling (no eat for 30+ rounds) is about the same for both sides (us 48%, them 42%). It is not a differentiator. Our pearls per dragon-round in rounds 0-25 are consistently below theirs (0.096 vs 0.123 in length losses, 0.079 vs 0.117 in wins). This is a small effect that compounds.

---

## Top 5 fixable causes (ranked by estimated impact)

1. **Rams when we don't have the numbers (elimination losses; about 17 games' worth).** 24.7 rams per game while outnumbered or even, and 40 of 85 final deaths are self-inflicted rams.
   - Fix in `tryRam()`: return false when `units < RAM_MIN_UNITS` (8).
   - Also require local superiority: count visible allied heads against enemy heads in the 7x7 view, or use `ECHOES ally_head` vs `enemy_head`, and ram only if ours ≥ theirs + 1 or the target is longer than us (`theirs >= myLen + 2`).
   - Also never pick the "take an enemy head with us" fallback in `decide()` when `units <= 2`.
   - Expected effect: blocks about 11.5 rams per game in these losses and 1.8 in wins.
2. **King starts at round 350 on big maps (Schooltime 0/5, Slithery 1/5, Trauma 1/5).** Our longest is about 4 until r350, while theirs is 10 by r300.
   - Fix: make the king start depend on map size. On maps with `W*H >= 1000` (Trauma, Schooltime, Slithery, Autarky), turn on the existing `KING_DECLARE` path with `KING_SEED_ROUND` about 150-200 instead of 250.
   - Also apply the no-split rule in `decide()` to a dragon that `iAmKing()` or `kingSelf` from that round on. Keep `SPLIT_STOP_ROUND` 350 for everyone else.
   - Allow two declared kings for insurance. The smaller one steps down after round 450.
3. **King self-trap: the look-ahead ignores eating.** 8 self-trapped kings (plus 4 boxed in by allies), including lengths 38, 27, 26 and 26, each of which cost a game or most of one.
   - Fix in `surviveDepth()`: when the simulated head steps onto a tile with `w.pearlMem` set (or a known corpse), skip the tail advance on that step (grow the ring by 1, undo on pop).
   - In `decide()`, for `myLen >= KING_MIN_LEN`, raise the depth to `min(myLen, 24)` and require `area >= myLen + pearls on path`.
4. **Feeding goes to the wrong dragon and lands off its path.** The king gets 18% of feeder pearls, and 48% of feeders are more than 8 tiles from the real king.
   - Fix in `readMessages()` and `iAmKing()`: a king that hears a longer king stops broadcasting and relays the bigger one, so there is only one king.
   - In `shouldFeed()`: require `kingRound == round` (the king is visible now), `myLen <= min(5, kingLen/3)`, and the king's next 1-2 tiles along `kingDir` free.
   - In `feedTarget()`: die with the body lying along the king's heading, so the pearls on alternating segments sit in its path.
5. **Self-inflicted churn: splits into dead ends and blind portal crossings.** 113 child deaths within 3 rounds per game, 59 on the birth round, and 19.6 friendly head-on pairs per game, all through portals, including 4 king deaths.
   - Fix in the `decide()` split branch: add `tailHasExit(k)` and require at least 2 free neighbours of the tail.
   - For kings only (`myLen >= 8`): apply `PORTAL_BLIND_PENALTY` (about 200) and treat allied heads within 2 of a portal exit as blocking. The global version hurt, but the king-only version costs little.
