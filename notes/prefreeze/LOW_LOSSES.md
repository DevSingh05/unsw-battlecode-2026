# Single-game losses to teams rated below 1950 (v34 era)
Data: `battles?limit=200` only reaches back to 10:52 UTC. Test windows are excluded. That leaves 328 games in the battles that had a loss to a sub-1950 team, and we lost 81 of them. All 81 replays were parsed (scratch pf/low/). We were side B in all 328 games, because they challenge us.
Losses by map: Slithery 12/33, Schooltime 12/33, **Trophy 11/34**, Dilemma 10/38, Portals 10/30, Autarky 9/34, **Devil 9/31**, QoS 4/28, Trauma 3/36, Default 1/31.

## How we lost: 27 eliminations, 54 at the round-500 length tiebreak
- **Eliminations: Trophy 11/11, Devil 9/9**, plus Autarky 2, Dilemma 2, Schooltime 2, QoS 1. On Trophy and Devil the game is over by r87-250. Our longest dragon never goes above L4 (their final swarm is 28-58 dragons of L3-4). About 85% of our deaths are head-on. The last dragons die head-on (as rammer or rammed) or trapped against kelp. There are no portal deaths, and self-hits are rare at the end.
- Pearl race, Trophy losses: we eat 73 by r100 and they eat 121. In wins it is 122 to 38. Devil losses: 51 to 160 (wins 175 to 48). Units at r100: Trophy losses 10 v 29, Devil losses 4 v 26. One side snowballs by about r60.
- Length losses: our longest vs theirs at r300 / r400 / final, averaged by map:
  - Autarky and Dilemma (15 games): 4v23 / 9v30 / 27v41. The opponents keep their long starting dragons and never split them, and we are about L3-5 until r300. This is map- and opponent-style specific.
  - Portals (10): 6v7 / 18v25 / 28v38. Level until r300, then out-grown.
  - Schooltime and Slithery (22): 17v17 / 29v31 / 34v48. Level at r300, then 14 of 22 games lose an L>=20 dragon head-on after r340. This matches the late-growth and king-death story in notes/stockfish/REPORT.md.
  - Only 6 of the 54 length losses had our king peak above their final length. Mostly we are simply smaller, not throwing away a winning king.

## One recurring general cause: 1-for-1 head-on rams taken while locally outnumbered
Every head-on death was classified by who rammed and by the local head count (Chebyshev 3 of the victim), and each ram's corpse pearls were traced to the team that ate them:
| map (games) | our rams while outnumbered /g | corpse pearls per such ram, us v them | their rams while they outnumber us /g |
|---|---|---|---|
| Trophy loss (11) | **19.0** | 0.48 v 2.52 | 6.8 |
| Trophy win (6) | 5.3 | 1.06 v 2.06 | 1.7 |
| Devil loss (9) | 4.6 | 1.15 v 1.95 | **12.3** |
| Devil win (6) | 4.5 | 0.89 v 2.19 | 4.0 |
Each ram is an even unit trade, but the side with more heads nearby eats the corpse: about -2 pearls per ram, which is about **-39 pearls/game on Trophy**. Even-numbers rams on Trophy are also net negative (7.8/g, 1.20 v 2.06). This is the same mechanism notes/19 found on Devil. It was fixed there with `RAM_GUARD_LOCAL=1` (Devil+Dilemma use `RP.ramGuard=2`), but **Trophy was left with the guard fully off**.

Responsible code: `variants/v34/params.hpp:160` has `#define PM_TROPHY_RG 0`, which `applyMapParams` (main.cpp:82) turns into `RP.ramGuard=0`. `tryRam()` (main.cpp:2960-2981) then skips the `allyHeads < enemyHeads + 1` local-odds test: `if (RP.ramGuard && theirs < myLen + 2) {...}` is never entered, so any L<=RAM_MAX_OWN_LEN dragon rams any visible head. The zero dates from the v5-era pool test, when the guard also needed units>=8 and so blocked every early trade on these 6-v-6 maps. Mode 2 removes that units requirement.

**Minimal fix, flag-guarded, 0 code lines:** build with `-DPM_TROPHY_RG=2` (local odds only, same as Devil). A 1-line alternative that keeps the default untouched is at main.cpp:135: `|| (RAM_GUARD_LOCAL == 3 && (n == "Devil" || n == "Prisoners Dilemma" || n == "Trophy"))`.
Caveat: the local self-play result was PM_TROPHY_RG=2 Trophy 10/24 (journal 05:45). Self-play does not reproduce these swarm bots (they die to HitWall/HitSelf a lot), so this needs a server check on Trophy vs 1650-1950 teams. Qualifier work, not pre-freeze: v34 stays.
Secondary (Devil, where they do the ramming): our small dragons walk into zones where they are outnumbered, 12.3 times/g in losses vs 4.0 in wins. SMALL_SPRINT_THREAT was the previous attempt and was rejected as too timid. The next idea to try is an outnumbered-zone penalty for L<=4 dragons (not built).
