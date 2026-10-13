# STATUS (single source of truth)

Last updated: 2026-10-13 19:35 EDT. All updates to the user come from this page. Times are US Eastern.

## Live and mainline
- **LIVE since Tue 13 Oct 7:32 PM: km17 (id 22447)** = qf1 plus, in order:
  - km1-km6 (12 Oct): seven Qualifier maps played as known maps (Atlantis, Maelstrom, Troll Australia, Whale Song,
    Hive, Detention, Ouroboros), Atlantis queen parked inside the pearl field, Troll Australia trap rooms sealed, small
    leashed home queen on Whale Song, Troll Australia, Hive, Ouroboros and unseen mid-size maps, growth splits stop at
    61 units.
  - km7 (3:12 AM): **queen hideout** (`QHIDE`): the queen is cut to 2 in round 0, walks to a quiet corner of her own side
    and circles there. Corners come from an enemy-traffic study of 5,500 server replays (`tools/analysis/oct13/`, table
    `bot/qhide_data.hpp`). Now on Devil, Queen Of Spades, Maelstrom, Australia, Around UNSW, Autarky, Thermopylae.
  - km8 (4:34 AM): a leashed or hiding queen never rams (before round 100 the small queen took head-on trades).
  - km9 (5:15 AM): Slithery Fight gets a **long home queen** instead (starts at 25, fed from r100, 27-60 at the end
    locally); Islands hideout off again.
  - km10 (5:54 AM): **Ezam played as a known map with Maze's settings** (it is a Maze with 30% of the walls changed; it was
    our lowest map; local 5-1 with 2.8 times the food); long home queen on Around UNSW; queen escorts on Maelstrom and
    Australia (every 16th unit stays 3-5 steps from her corner and rams intruders).
  - km11 (6:15 AM): **Metro and Athena played as known maps** with the crowd penalty (they were unseen maps with half
    the opponents' economy at round 100; local 27-5 against km10 and qf1).
  - km12 (6:34 AM): crowd penalty on Maelstrom (local 10-2); **Thermopylae played as a known map** with the crowd penalty
    (local 14-6). Of the 14 Qualifier maps only Caution and the two Trolley Problems are still played unseen (Trolley
    known loses 1-11 locally; Caution is already one of our best).
  - km13 (1:34 PM): **spread fix on Around UNSW** (food further away counts for more, discount 0.92, plus the crowd
    penalty: locally twice km12's length at r200) and the hideout there again instead of the long home queen (0-9 on
    the server); crowd penalty on Islands; **hideout on Metro and Athena** (vs dev test 1 km12 went 0-14 and 3-11 there:
    both queens died and their longest dragon won; on Athena our queen died around r35).
  - km14 (2:56 PM): **lunges.** Server replays show 86% of our long dragons (8+ segments) that die to an enemy head
    are killed by a lunge of two or more steps (Metro: 510 length a game lost this way against the opponents' 259),
    while our units only feared an adjacent head and our own rams reached 1-2 steps. Now a unit of length 7 or less
    takes a certain lunge kill on an enemy with 9+ visible segments (`KING_KILL`), and our dragons of 8+ treat an enemy
    head's lunge reach as a threat (`KREACH`). Local: 257 enemy length killed a game against 154 lost, 9-1 on five maps.
  - km15 (4:09 PM): **queen hunters** on eight maps (Around UNSW, Australia, Islands, Slithery Fight, Maze, Athena,
    Ezam, Maelstrom): from r120 every fifth small unit patrols the enemy queen's home. In 143 of 478 server games our
    queen was dead and theirs alive at the end (0 won); on Around UNSW we now hold twice the opponent's length and
    still lose to a length-2 queen that sits at home. Unproven locally (15-17), so judge by "their queen alive at the
    end". Thermopylae queen back on the start leash (the leashed queen lived in 7 of 8 local games and beat the hideout
    6-2).
  - km16 (5:26 PM), from the four research reports of the afternoon: **threat split** (a dragon of 8+ with an enemy
    head within three steps splits off everything but its front two segments, as larp does: larp loses 44-52 length a
    game to rams, we 400-500); lunge reach now assumes length 5 for an enemy head whose tail is out of view (in 67% of
    our long-dragon deaths the killer was in view at distance 2-3, where only its head shows); hunters keep length 5
    (reach 5 instead of 1-3); the **enclosure test** on Islands, Australia and Maelstrom (a unit no longer eats its way
    into a dead end or a ring of its own body that it cannot leave; Islands locally 1.4-2.7 times km15's length).
  - km17 (7:32 PM): our own units keep out of the queen's hide zone on Athena (10 of her 11 deaths there were her own
    move into an ally's or her own body; local 11-1 with the zone), hunters also on Thermopylae and Tower Defense.
  km16 on the server (two hours): **ranked 162-113, 59%, the best of the builds so far** (+4 points over the
  expectation); Maelstrom 17-2, Metro 9-4, Australia 9-8 with 1.9 times the opponent's length at r300 (0.4-0.5 before);
  our longest dragon was rammed in the last 60 rounds in 2 of 75 games (40 of 381 before, 31 of them lost).
  km15 on the server (75 min): ranked 56-64, but 17-9 on the eight hunter maps (km14 19-21 there); on Around UNSW the
  opponent's queen now survives 2 of 9 games (17 of 29 before).
  km14 on the server (70 min): ranked 85-80, vs dev test 1 41-31 (km12 27-58, km13 6-14).
  km13 on the server (75 min, 74-74): Metro 5-6 with our queen alive in 4 of 10 (0-15 vs dev test 1 before), Islands
  4-6 (4-15 before), Around UNSW 2-6 with half the opponents' length at r100 (a third before).
  Server so far: Ezam 6-2 since km10 (0-10 before); the hideout wins where the opponent's queen dies (Devil 12-2, Queen Of Spades 4-0, Maelstrom 9-8) and
  lost where it lives and is long (Slithery Fight 2-14, Islands 2-15). Copies: `variants/km1`..`km17`.
  **Fallback order: km16 (22435), km15 (22430), km14 (22425), km13 (22420), qf1 (21001)**; activate with
  `POST /api/v1/submissions/<id>/activate`.
- **This session (unsw-battlecode-de) owns the server for now** (user, 12 Oct: battlecode_main's account is out of usage).
- **Not in the Grand Final** (lost the Qualifier round of 32 to Sabotage-d, 3-4). Work now is ladder rating: 2177 #25 at
  the start of 12 Oct; 2205 #21 at 1:00 AM on 13 Oct; 2295 #13 at 3:12 AM when km7 went live (a 35-30 hour against
  top-12 teams); 2302 #12 at 5:50 AM; 2329 at 6:15 AM; **2306 #12 at 6:34 AM** when km12 went live (the rating swings 30-40 after
  every upload); 2255-2275 through the morning (km12 ranked 60-60), 2234 #18 at 1:34 PM when km13 went live; 2281 #15 at 2:56 PM when km14 went live; 2255 #14 at 4:09 PM when km15 went live; 2183 #22 at 5:26 PM when km16 went live; 2268 #16 at 7:08 PM; **2257 at 7:32 PM** when km17 went live. The rating swings by 100+ within minutes on single series (2054 to 2392 between 3:44 and 3:57 PM), so builds are judged by wins against the expectation and by the dev test 1 record, not by the rating. Each
  submission keeps its own rating; the team's is the active one's. The pool has 31 maps since 10 Oct (17 old + the 14 Qualifier maps).
- **Allowances in use:** 60 hand-started games/h go to ranked series (`replays/auto_ranked`). Since 1:13 AM the panel is
  the teams we gain rating against per series (10-13 Oct data): SSS, TTT, horse, WeHaveQuizzes, Settlers, Codehammer,
  plus Cutlery and chat gippy tea; larp, Computers, forgot to mention and the hieroglyph team were dropped (we lose 3 to
  5 points a series against them); since 1:05 PM also without horse (22-43, -46 points) and chat gippy tea (7-23, -51),
  with test4 and Sponge added. The separate 60/h against DEV teams is the test bed: unranked series vs dev test 1
  on Athena, Thermopylae, Tower Defense, Islands, Slithery Fight (`replays/auto_dev26`). Stop either with a `STOP` file in
  its folder. Judge with `tools/analysis/oct12/build_watch.py`, `by_build.py` and `watch_mech.py`.
- **Open after km7:** the hidden queen stays at length 2, so she loses the tiebreak to any living enemy queen that is
  longer; the full late crown (to 25) got her rammed at r394-449 in local play, the small one (to 10) cost wins on
  Maelstrom and Slithery Fight. Not hidden yet: Hive, Ouroboros, Whale Song, Troll Australia, Athena, Metro (no local
  gain), and the two-dragon maps (Trophy, Stripes, Default, Maze, Ezam: she is a needed worker there).
- **How games are decided** (721 server games that reached r440, 13 Oct): our queen dead and theirs alive at r440 in
  185 (17 won); both alive in 145 (57 won; Detention 35 and Schooltime 16 of those, both queens at 3, the longest
  dragon decides; Slithery Fight 29 with theirs at 50 against our 24); ours alive and theirs dead in 99 (93 won, and
  our queen still dies in the last 60 rounds in 16 of them); the rest both dead. Tools: `tools/analysis/oct13/qfate.py`,
  `kingdeath.py`, `fog.py`, `work/oct13/lateq.py`.
- **Research reports of 13 Oct** (four agents, user's suggestion; each ends with ranked rules): `notes/top5/LUNGES_OCT13.md`,
  `notes/top5/QUEEN_OCT13.md`, `notes/top5/ECONOMY_OCT13.md`, `notes/research/ALGORITHMS_OCT13.md`. Shipped from them in km16:
  threat split, unseen-tail reach, length-5 hunters, enclosure test. **Not done yet, in the order I would take them:**
  (1) the queen's own lunge radius for a SMALL queen only (theirs dies in 9-12% of approaches, ours in 30%; the
  version for every queen killed the fed Maze queen locally); (2) never box the queen: 89 of her 404 deaths are her
  own move, and Tower Defense / Trolley Problem (Buffed) are lost that way with 2-10 times the opponent's length;
  (3) weakhold and other maps lost with our queen alive but short (queen as king with a cap: 4-4 locally, she dies
  half the time while fed); (4) Detention and Metro longest-dragon races lost with more total length; (5) a home
  patch per unit with a leave-when-hungry rule, and raids on enemy hot pockets from r50 (Autarky).
- **Worst maps in ranked games since km7 (610 games):** Slithery Fight 2-16, Autarky 2-16, Thermopylae 2-11, Islands 4-15,
  Metro 6-22, Ezam 5-17, Athena 4-12, Whale Song 4-12, Around UNSW 6-13. Best: Trauma 12-4, Default 12-5, Tower Defense
  12-6, Trophy 11-7. Tools for the three leaks found on 13 Oct, all in `tools/analysis/oct13/`: `spread.py` / `econ.py`
  (coverage and early economy), `badsplit.py` (splits that lose a half at once: Slithery Fight 264 a game against the
  opponents' 122, Australia 73 against 8; no fix yet), `bigdeaths.py` (long dragons lost to lunges).
- **Open after km13: our units do not spread.** On Around UNSW our heads have stood on 450-490
  tiles by r100 against the opponents' 1,370-1,690 (34 units against 60, and more corpse pearls eaten than new ones);
  smaller gaps on Australia, Slithery Fight and Thermopylae; on Metro we are ahead. km13's per-map settings close part of
  it on Around UNSW only. Measure with `tools/analysis/oct13/spread.py` (server replay or `--local RUN`) and
  `econ.py RUN stage/NAME`. Also open: on Metro both queens die and we lose the longest-dragon race by a few segments
  with twice the length; Thermopylae (1-13 vs dev test 1: their length-2 queen circles her start tile and lives, ours
  walks to the hideout and dies); Slithery Fight (0-9 with the long queen; a crowd penalty makes the team 35% longer
  but the queen shorter).
- **Uploads are bundled** (about one every two hours): each new upload widens the rating and the first series swing hard.
- `bot/` carries the `QUAL_*` flags (default 0) and a 47-map `maps_data.hpp`. Lines below this point in this section
  are from 9 Oct and describe the build history up to qf1.
- **Mainline = `bot/`** = b4 (b3 + Tower Defense centre pull + Australia queen vault ban); b3 = b2 + Australia crowd penalty: v61 (QS_FROM=100, QSPLIT_ROOM=1) + Portals/Maze queen park and crown + QKILL_FUEL + INFER_SYM (unknown maps only). Every new idea goes into `bot/` as a flag, default 0. No vNN copies; test builds are staged in the scratchpad.
- **Last accepted live build:** f1 (= b2 on known maps; identical copy in `variants/f1` for rating-restoring re-uploads). b1 copy kept in `variants/b1`.
- **Fallbacks:** `variants/v61`, `variants/v44`. Re-uploading an identical build restores its old rating.
- **Kept in `variants/`:** b1 (live), v61, v44 (fallbacks), v35, v38m (local test opponents).
- **Challenge budget:** the server allows 60 challenge games/h (12 series). Unranked series let us choose maps, so map-specific fixes are tested with the loop restricted to their maps.

## Key dates
- **Frozen (Fri 9 Oct 2:00 AM EDT): qf1 is the Qualifier submission.** Post-freeze seeding autoscrims 2-6 AM EDT: 178-147, Elo -2. Final ladder: 2277, #17 (#16 eligible).
- **Official (8 Oct update):** freeze 9 Oct 06:00 UTC = **Fri 9 Oct 2:00 AM EDT**; last active submission = Qualifier submission; then 3-4 h autoscrims on the current 17-map pool set seeds; Qualifier 10 Oct, Bo7, ALL UNSEEN maps; top 10 eligible go to the Grand Final. Strategy: known-map play (seeding) stays b4; Qualifier gains must come from unknown-map-gated changes that keep the 17 maps byte-identical.
- **Submission freeze for the Qualifier:** Fri 9 Oct, 2:00 AM EDT. Seeding comes from the final ladder.
- **Qualifier stream:** Sat 10 Oct, 2:30 AM EDT. Best of 7, knockout, unseen maps.
- **Grand Final:** 17 Oct.

## Rating strategy (8 Oct)
- Ranked challenges go only to teams where our win rate beats the Elo expectation (gain even when we lose 2-3): SSS (W .44 vs E .19), larp (.40 vs .15), horse (.38 vs .24), Cutlery, FTM (.31 vs .23). Dropped Sponge (.32 vs .46), bread first search, Team SKKU (below expectation). Recompute with the snippet in notes/journal.md 8 Oct.

## How we test (lessons, in order of trust)
0. **Ranked challenges only while an accepted build is live.** Test builds get unranked challenges only (u1 lost 69 Elo in its first ranked series because new uploads start with high uncertainty).
1. **Server A/B is the judge.** One build is live at a time, for about 2-3 h (challenge loop at 45/h plus autoscrims).
   - Score it with `python3 tools/ab_server.py <base> <cand>`. It reports PAE: our score minus the Elo expectation per game, so opponent strength is controlled for. See notes/newrules/AB_SERVER.md.
   - Lose → re-upload the identical base, and its rating comes back.
2. **Local self-play on known maps is nearly useless for strategy.** Most maps come out 2/4, because the side decides. Use it only to check a build compiles, doesn't crash, stays under CPU, and has the intended mechanism (stats).
3. **Unseen-map checks for the Qualifier:**
   - `tools/unseen_eval.py --sets real,realhold,blind17`. These are realistic generated maps, plus the official maps with map knowledge off.
   - The old gen/lesson/gated sets don't look like real maps.
4. **Map-identification changes must play identically to the live build on all 17 official maps.** v49 broke this and lost.

## Server A/B scoreboard
| build | change | verdict | numbers |
|---|---|---|---|
| v43 | QALLY_KEEP + QBOX_K2 (allies stay off queen, boxed queen sheds 2) | kept | 2095-2123 |
| v44 | WH_CENTRE (weakhold opening) | kept | ~2094 |
| v49 | MATCH_STRICT full (map gossip on idle sonar) | **LOSS** | -4.8 pp (CI -8.8..-0.7); Stripes/QoS/Devil/Portals collapsed |
| v55 | QS_FROM=100 (queen joins early economy before r100) | **WIN** | +5.7 pp (CI +0.6..+11.4); 2051 → 2133; vs top-10 +13 |
| v60 | QEXIT_LOOK (queen avoids ≤1-exit tiles) | loss | -1.4 pp; 2094 vs 2126 |
| v61 | QSPLIT_ROOM=1 (early queen avoids pocket splits) | **WIN** (leaning) | +3.2 pp; 2126 → 2174; 11/17 maps |
| v64 | LUNGE34 (3-4 step lunges) + INFER_SYM | **LOSS** | -6.8 pp; 2136 vs 2174; lunges cost length |
| v65 | QK_BIG (queen becomes the king on big maps) | **LOSS** | -6.4 pp; 2143; 5/17 maps |
| v69 | QEARLY_PEN (queen portal/blind penalties before r100) | loss (leaning) | -4.8 pp (CI -12.9..+3.3); 2121 vs 2187; 6/17 maps; vs top-10 -1.8 vs +12.2 |
| c1 | SPLIT_NEEDS_EXIT + LATE_HUNT + QKILL_KING | **LOSS** | 81 games: adjusted -9.9 pp, P(better) 0.03. Stillborn splits did fall (11.3 → 4.3 per game) and queen alive at r100 rose (40% → 55%), but total length vs opponent at r300 fell (x0.66). Bundle, so the culprit isn't isolated; SPLIT_NEEDS_EXIT is the suspect. |
| m1 | Map pack: Portals/Maze queen park+crown, Stripes loop, Trophy early split, Schooltime B | partial (95 games): overall adjusted +9.6 pp, P(better) 0.99 | Portals: queen alive at r500 0% → 90%, wins 42% → 70% (n=10). Stripes 92% (n=13). Maze and Trophy flat (n=10-15). **Schooltime worse**: wins 77% → 45% (n=11), r300 length x0.54 → PM_SCHB dropped. |
| m2 | m1 without the Schooltime change | **WIN** | 219 games: adjusted +7.5 pp (CI +1.0..+13.4), P(better) 0.99. Pooled m1+m2 per map vs v61: Portals 54% vs 41% (queen alive r500 85% vs 0%); Maze 40% vs 35% (queen alive 34% vs 10%); Stripes 85% vs 84% (flat → off); Trophy 64% vs 70% (→ off). |
| b1 | v61 + PM_QPARK_PORTALS + PM_QPARK_MAZE (new mainline) | live since Sun 6:55 PM, ranked loop on all maps | baseline block for the next tests |
| q1 | b1 + queen park on Australia/Around UNSW/Slithery/Tower Defense/weakhold | **LOSS** | per map vs v61 (unranked panel vs v61's mixed baseline, so biased against q1, but mechanisms agree): Australia 41% vs 56%, Around UNSW 40% vs 59%, Slithery 16% vs 31%, Tower Defense 43% vs 69% with eliminations 8% → 44% and r100 length ratio x0.29. All five off. Park helps only on Portals/Maze. |
| f1 | b1 + QKILL_FUEL (Codex: pearl-paid steps in the certain queen-kill search) | **accepted** (neutral) | 240 games: adjusted -0.1 pp (CI -12..+11), P 0.50; mechanism: enemy queen killed 39% → 43%, eliminated 27% → 12% (raw, opponent mix differs). Narrow, sound change → kept. Rating-restore copy: variants/f1. |
| h1 | b2 + LATE_HUNT + QKILL_KING (lone enemy queen kill, alone) | **LOSS** | 586 games: adjusted -2.1 pp (CI -9.6..+5.3), P 0.29 → drop at 500. King queen kills 0% → 4% but no gain. f1 restored (2221). |
| k2 | b2 + QK_EG=2 (crowned-queen kamikaze guard) | **LOSS** (mechanism) | 313 games: adjusted -0.9 pp, P 0.41; target stat wrong way: queen alive at r500 Portals 92% → 81%, Maze 56% → 39% (mostly vs dev team). Dropped; f1 restored (2221). |
| cm1 | b2 + CROWD_MAPS=3 (crowd penalty on Around UNSW + Australia) | **accepted for Australia only** | per map (n 12-28, cm1 mostly vs dev team): Australia length ratio r100 1.65 → 2.51, r300 1.21 → 2.07, wins 50% → 57%; Around UNSW stillborn down but ratio flat, wins 67% → 46% → bit off. Mainline b3 = CROWD_MAPS=2. |
| s1 | b3 + SPLIT_DEFER=3 | **LOSS** | 318 games: adjusted -4.8 pp (CI -13.2..+3.8), P 0.14. Stillborn by r100 12.6 → 4.5 per game, but length ratio r100 1.82 → 1.20, eliminated 11% → 24%. Second time that blocking/deferring splits backfired (c1 too): stillborn children are cheap and the extra splits pay off. Don't retry. |
| b3 | mainline: b2 + Australia crowd penalty | live since Mon 10:35 AM (inherited 2232 from cm1) | |
| l1 | b3 + lane-map small queen (TD, Devil late, Autarky, QoS) | **LOSS** | vs dev team on those maps, l1 vs earlier builds (h1+s1): Autarky 0/20 vs 0/19, TD 3/20 vs 4/19, QoS 6/20 vs 5/20, Devil 6/20 vs 11/20. Adjusted -5.0 pp, P 0.13. b3 restored. |
| ms1 | b3 + MIDSIZE (half of units split at L6 from r150) | **LOSS** | 356 games: adjusted -5.8 pp (CI -12.4..+1.3), P 0.05. r300 length ratio x1.18 but wins down. b3 restored. |
| u1 | b3 + 5 map-specific fixes (QVAULT, PM_TROPHY_RG, PM_TD_PULL, QG_RAM, SCH_DOORS/CHAMBER) | **pulled** after 0-5 ranked vs Sponge (2212 → 2131) and weak dev-team games; user call. b3 restored. |
| v1 | b3 + PM_TD_PULL + QVAULT=3 + SCH_DOORS (unranked) | **partly accepted** | per map vs b3: TD wins 41% → 60%, eliminated 48% → 24%, r100 length x2.6 (keep); Australia queen alive r100 18% → 45%, wins 53% → 58% (keep QVAULT bit 2); Slithery queen alive r100 57% → 87% but wins 25% → 21%, r300 length x0.86 (bit 1 off); Schooltime wins 36% → 25% (SCH_DOORS off). New mainline b4. |
| b4 | mainline: b3 + PM_TD_PULL=2 + QVAULT=2 (Australia) | **live (ranked)**, re-uploaded Wed 3:30 PM (2220); copy variants/b4 | |
| qf1 | **Qualifier build, live since Thu 1:00 PM**: b4 + QE_KR=2 (pearl-aware early-queen kamikaze reach) + UNK_PORTAL_SIDES=2, both gated to never-identified maps | known maps: 40/40 full-trace identical to b4 (17 maps + Schooltime B x3, both sides); unseen vs b4: .570 and .518 on two seed bases (pooled .544, 456 games); unknown_neck fixture: queen suicide fixed; CPU same as b4 (rare 40-54M spikes on a 64x64 map, b4 too; judge limit 100M). Copy: variants/qf1. Fallback: variants/b4. |
| stress | qf1 on 20 extreme legal maps + 24 random extreme + real-like 64x64 + 17 official blind (340 games) | **safe** | 0 crashes/timeouts/invalid lines/no-action turns; worst turn 64.7M of 100M (64x64 portal-dense, `tryKingEscape`, no points budget; b4 same code path 54M); 1 'no valid action' in ~9.7M dragon-turns (split child adopted wrong known map 'Big Empty': `consistent` lets a seen portal match a plain edge). Not fixed in qf1 (too rare to justify a pre-freeze upload); flags KE_BUDGET_M and CONSIST_PORTAL added to bot/ (default 0) for the Grand Final. Identity vs qf1 (17 maps + Schooltime B x3, both sides): flags off 40/40; KE_BUDGET_M=55 + CONSIST_PORTAL=1 39/40, with Schooltime side A differing at r272. So CONSIST_PORTAL also rejects a real known-map portal (a portal exiting to its plain neighbour) and needs an explicit portal bit in the known-map data before use; KE_BUDGET_M alone never triggers on known maps (max 34M). Report: work/stress/REPORT.md. |
| kf1 | b4 + QKILL_KING + QKK_FREE | **LOSS** | 392 games (unranked): adjusted -6.0 pp (CI -16..+4), P 0.13. King queen kills barely changed. b4 restored. |
| ag1 | qf1 base + UNK_GOV=50 (aAah split cap, unseen only) | **not shipped** | unseen vs b4: .491 / .531 (pooled .511, 456 games). Mid-size mass spreads away from the king and loses longest-dragon tiebreaks. |
| cx1 | UNK_XP=1 (Cutlery-style portal crossing, unseen only) | **not shipped** | unseen vs b4: .487 / .539 (pooled .513); realhold under .5 on both seeds. Early blind queen crossers die early (ours 8/8, Cutlery 32/43). |
| qn1 | qf1 + QNO_UNKPORTAL (queen never crosses unknown portals, unseen only) | **not shipped** | 17 maps + Schooltime B: 40/40 identical to qf1. Mechanism (10 blind games vs qf1): queen crossings before r100 8 → 0-3, queen alive r150 4 → 8. Unseen vs qf1: value 1 .518 / .500, value 2 .522 / .504 (blind17 .456 at 982000); ship rule needs ≥ .52 on both. Flag in bot/, default 0. |
| pb2 | b4 + QBOX_ONESPLIT | **LOSS** | Portals wins 75% → 60%, queen alive r500 83% → 80%; Maze flat; Trauma 96% → 80%. Off. |
| km2 (22256), km3 (22258), km4 (22267) | km2 = km1 + Atlantis queen parked inside the pearl region (`QUAL_QPARK_IN`); km3 = km2 + queen home leash on Whale Song and Troll Australia (`QUAL_QHOME`); km4 = km3 + Troll Australia trap rooms sealed (`QUAL_TRAPSEAL`, `QUAL_PBLOCK`) + leash on Around UNSW and unseen big maps (`QHOME_OLD=1`, `QHOME_UNK=8`) | **km4 live since Mon 12 Oct 4:34 PM** | Atlantis: qf1 6-24, km1 3-8, km2 6-5 vs ranks 45-80 (queen alive 6 of 11 at L38-85, all six won; five losses = queen rammed), then 2-4 vs dev test 1. Troll Australia vs dev test 1: km3 0-6 with 30 length at r100 against 250 (six of nine starters died in the trap rooms before r50); km4 185 against 47 at r100 in its first game. Maelstrom: 10-1 and 4-2. Whale Song: 5-6, then 1-5 vs dev test 1 (their queen fed to L37-53). km4 ranked so far: 17-18 in games against an Elo expectation of 11.8. |
| km1 (id 22249) | qf1 + QUAL_KNOWN=0x2442 (Atlantis, Maelstrom, Troll Australia, Whale Song known) + QUAL_ROUTE=0x3FFD + QUAL_GOSSIP=1 + QUAL_QPARK=0x2 (Atlantis) | **live since Mon 12 Oct 3:20 PM**, under evaluation | Local vs qf1 on the four maps, fresh seeds: 11-5. First 40 unranked server games on the four maps vs ranks 14-24 (Elo expectation 44%): 18-22 (45%); qf1 on the same maps in the two days before: 40-85 (32% against an expectation of 56%). Per map: Maelstrom 9-1, Whale Song 4-6, Troll Australia 3-7, Atlantis 2-8. Atlantis economy is fixed (2,440 pearls eaten vs 150) but 8 losses came from the queen: theirs alive at L12-34 in 9 of 10, ours parked and unfed at L5-10 or rammed. |

## What the week taught us (summary, 7 Oct)
- **Server wins came from queen handling and map-specific fixes:** QS_FROM=100 (early-economy queen), QSPLIT_ROOM, the Portals/Maze queen park, the Tower Defense centre pull and the Australia vault ban. Every one of them was either a narrow, decision-verified fix or a per-map change judged on its own map.
- **What kept losing:** broad behaviour changes copied from other teams (lunges, queen-as-king on big maps, mid-size units), anything that blocked or delayed splits (c1, s1), and queen-safety penalties that moved her deaths without preventing them.
- **Method:** decision-replay first (does the fix flip the losing decision and leave winning ones alone?), then unranked server tests judged per map. Ranked games only on accepted builds.
- **Per-map portfolio:** across about 6,000 games and 24 builds, b4 was already the best on every map once noise and confounds were removed.

## What we know about why we lose (notes/newrules/LOSS_AUDIT2.md, v55/v61, 250 losses)
- **We lose r500 tiebreaks, not fights.**
  - In 45% of losses to non-top-10 teams, our queen is dead at r500 and theirs is alive.
  - In ~21% of all losses we had the bigger army and their queen came near our heads for 10+ rounds. Example: 141 vs 2 on Devil.
- **59% of our queen deaths follow one pattern:** she eats into a kelp pocket or a 2x2 portal vault, sheds 2 at a time, and dies at L2-3. Since QS_FROM=100 this mostly happens before r100 (Portals, Australia, Around UNSW).
- **Weak maps:** Maze, Devil (early eliminations), Portals, Slithery, Around UNSW. On Around UNSW we lose the longest-dragon race despite 1.5x total length.
- **Top teams** (notes/top5/TOP2_VIBING_FTM.md, TOP1_FORGOT_TO_MENTION.md):
  - Vibing++ = Cutlery renamed, with a strong new build. It grows mid-game on big maps, uses long lunges, and keeps its queen whole until she becomes the king.
  - Copying those features directly (v64, v65) lost on the server.

## Round 2 study (2026-10-04, notes/newrules/ROUND2.md): six lenses, two skeptics
- **We lose on the queen, not on fights.** Against the top 5, combat is even; in r500 games our queen was alive in 4 of 54 and theirs in 26.
- **Most queen deaths are self-inflicted** (shed chains in 103 of 250 losses): an ally body boxes her (47), she splits with one open step (45), the pocket is too small after eating (35), and a false "exit blocked" on portal exits (25, a real bug).
- **We don't finish a lone enemy queen:** 14 of 53 losses to non-top-10 teams, with us holding 45-255 length. The king gate in tryRam returns before the queen-kill call.
- **Stillborn splits:** 14% of our split children die within a round (top 5: 4.8%).
- **A/B method:** every test so far was underpowered. Use v61's stored rating as our standing; score with the adjusted model (opponent + map effects); test in two stages (mechanism gate at ~150 games, then win rate at 250/500/850 games); fixed opponent panel; unranked challenges while a candidate is live.

**Fixes that survived both skeptics (now in bot/ as flags, default 0; staged test copies live in the scratchpad, not in variants/):**
1. P1: kill the lone enemy queen (LATE_HUNT on, king may take the kill, finisher).
2. P3: allies must not seal the queen (hard keep-out including bodies, corridor-plug look-ahead).
3. P5: stop stillborn split children (SPLIT_SAFE).
4. P6: wider threat reach for long dragons, protect the lead from r470.
5. P7: park and crown the queen on Portals and Maze (ladder only).
Refuted: P2 portal-exit bug fix (bug is real, fix doesn't change outcomes), P4 pocket test, P8 Devil queen split.

## Rejected (don't retry as-is)
- **On the server:** QEXIT_LOOK, LUNGE34, QK_BIG, full MATCH_STRICT gossip.
- **Locally, never server-tested** (low priority):
  - EQ_HUNT variants (always-on queen hunt).
  - Queen safety: QKREACH, QWARN, QESCORT, QDEAD2, QSPLIT_MIN4.
  - Economy: COVERAGE, SUICIDE_FEED, HOME_DEFEND, EARLY_PUSH.
  - Harvesters (HARVEST 1/2), EARLY_QSPLIT.
- **REAL_SWEEP** (notes/newrules/REAL_SWEEP.md): old unknown-map flags gave nothing except INFER_SYM.

## Plan from 12 Oct, 5 PM (top-3 studies in: notes/top5/TOP3_SYNTHESIS_OCT12.md)
1. **Kings.** We now out-mass opponents on the fixed maps and still lose the longest-dragon tiebreak: Troll Australia vs
   dev test 1, 292 length against 79 at r300, lost 27 to 30 after an L87 coiled into itself at r436 and an L52 met an
   enemy head on a pearl at r401, both with 62-63 units alive (no slot for the turn-around split). Next build:
   `SPLIT_MAX_UNITS=61` (forgot to mention keeps two slots free; our longest dies boxed 3.3 times a game, theirs 0.3).
2. **Queen, as all three top teams play her:** cut to 2 in round 0, near home, fed late. `QHOME_SMALL=250` is built
   (local: alive at the end 11 of 20 against 16 of 40 with the leash alone); a late capped crown is being tested.
3. **Atlantis:** our queen is still rammed inside (dev test 1 stalks her with length-2 units); guards or a hunt for
   their outside queen are the two options.
4. **Trolley Problem x2, Detention, Thermopylae, Ezam** and the five par maps: unchanged so far.
5. Old weak maps after that: Slithery Fight, Devil, Trophy.

## Plan (7 Oct; one fix at a time, focused on the r500 queen problem)
1. **LATE_HUNT** (in bot/ as flag `LATE_HUNT`, default 0; variants/v68 = on): once our queen is dead, hunt theirs map-wide. Plays identically to v61 until an ally sees our queen die (detects ~60% of deaths, 0 false alarms). Local neutral, as expected. Next server test after v69. Judge it on r500 'our queen dead' losses vs non-top-10.
2. **QEARLY_PEN** (v69): queen portal/blind penalties also before r100. Server test lost (leaning); flag not folded into bot/.
3. **King timing** (v70, SPRINT_KING_PM): Around UNSW seed 190/feed 230. Mixed locally: helps when we out-mass the opponent, hurts against equal mass. Low priority; affects 1/17 of games.
4. **Qualifier build** (before Fri 2 AM): mainline, which now has INFER_SYM on (unseen-only, ~.55 blind in two runs) + MATCH_STRICT-lite. Unseen queen park (QPARK_UNK) rejected: .579, .526, .465 on three seed sets, official-blind always below .50.

## Where things are
- Journal (timestamped log, UTC): notes/journal.md
- Rules: notes/RULES_2026-10-01.md; older references in notes/01-04.
- Active analysis: notes/newrules/{AB_SERVER, LOSS_AUDIT2, UNSEEN_GENERALISATION, REAL_SWEEP}.md, notes/top5/.
- Archived on 2026-10-04: archive/variants_20261004, archive/bot_oldrules_20261004, archive/notes_oldrules_20261004, archive/notes_newrules_20261004, archive/root_misc_20261004.
