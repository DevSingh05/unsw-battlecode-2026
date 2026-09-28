# 03: Competition structure and current meta

Source: https://game.battlecode.au/ public pages and SvelteKit `__data.json` endpoints (/docs/game-format, /docs/elo, /leaderboard, /tournaments, /tournaments/{sprint,qualifier}, /battles, /games, /teams/<id>, /visualiser?match=<id>) plus ~110 downloaded replays. Snapshot taken 2026-09-26 (server clock about 2026-09-27 00:30 UTC). Everything here was read-only.

## 1. Timeline and events

| Date (UTC) | Event | Who | Format | Prize |
|---|---|---|---|---|
| 21 Sep | Ladder opened (every team starts at 1500) | all | autoscrims plus requested scrims | none |
| **1 Oct** (00:00 UTC, i.e. 10:00 AEST) | **Sprint** | **every team** (838 in the tentative bracket) | one-day seeded single-elimination, Bo5 | **$800 first, $400 second** |
| **10 Oct** | **Qualifiers** | **eligible teams only** (294 right now) | seeded knockout, Bo5 | 10 Grand Final places: the 8 quarterfinalists, plus the two finalists of a separate knockout among the 8 Round-of-16 losers (reseeded by original seed) |
| **17 Oct** | **Grand Final** | 10 qualifiers | Bo5, in person at UNSW Sydney | **$8,000 first, $18,500 across the top six** |

- Seeds follow the current rating ladder, with ties broken by total won matches. Top seeds get first-round byes. The brackets are already visible (tentative) at /tournaments/sprint and /tournaments/qualifier. Your rating on 1 Oct and 10 Oct therefore decides your seed and byes.
- **Grand Final eligibility:** a high school or university student in Asia-Pacific, or an APAC citizen studying elsewhere, **with a resume uploaded**. The resume is "shared with our sponsors". Set this on the account Eligibility tab. A team shows `eligible` only when the whole team qualifies. Some strong AU teams (e.g. #12 "bread first search") are currently marked ineligible, most likely because a resume is missing.
- Other prize categories: a **First Year Prize** (team made up only of first-years) and a **WGM Prize** (team with a majority of women and gender minorities). Team flags `unsw`, `highSchool`, `firstYear` and `wgm` also exist. Nothing public gives amounts for these.
- Sponsors: **Jump Trading** and **Hudson River Trading**. Teams have up to 4 members. There is a Discord linked in the site footer.

## 2. How rating works (from /docs/game-format and /docs/elo)

- There is one Elo ladder. Everyone starts at 1500 and the rating belongs to the team, so it carries across submissions.
- **Ranked battle = 5 games on 5 maps the server picks at random.** The rating updates once per battle, using the **share of games won** (a 3-2 win scores 0.6).
  - Expected share = 1/(1+10^((Rb-Ra)/400)). Change = K·(actual - expected), rounded.
  - A favourite 400 points ahead needs 5-0 to gain anything, so a 3-2 or even a 4-1 win loses rating. An underdog gains from a 1-4 loss.
- **K per submission:** K=96 at 0 ranked battles, dropping 7.2 per battle to **K=24 from battle 10 onwards**. Only one "fresh" bot per team every 12 hours starts from 0. A second new bot inside that 12-hour window inherits the count of the last bot that played ranked (capped at 10). Re-uploading identical code (identical file contents; zip metadata and `__pycache__`/`.DS_Store` are ignored) keeps the old count.
  - **Tactic:** upload a big improvement as the first new code after the 12-hour window has expired, so it climbs at K=96. Hold back small tweaks.
- **Autoscrims decide most of your rating.** Every 2 hours, on the UTC boundary, the ladder is sorted. Each team with an active submission is drawn against up to 2 opponents picked from the 8 places above and 8 below, preferring teams it hasn't played recently. Each draw is a ranked Bo5 on random maps. This happens automatically and does not use up your hourly quota.
- **Requested scrims:**
  - Both teams need an active submission.
  - Unranked scrims are open to anyone, against anyone, on **maps you choose** (one game per map).
  - A ranked request needs the ranked switch on for both teams, and the target must be no more than 50 below you (anyone above you is allowed). The switch can only be flipped once every 8 hours.
  - Limit is 60 games per hour, which is 12 ranked scrims.
  - **All battles and replays are public.**
- Tiers: Plankton <1000, Shrimp 1000-1299, Tunafish 1300-1599, Swordfish 1600-1899, Shark 1900-2199, Orca 2200-2499, Leviathan 2500-2799, Fishing Boat 2800+.

## 3. Current standings and distribution (snapshot)

- **854 teams** registered. **498 have a bot** (362 cpp, 130 python, 6 c). 357 teams are still at exactly 1500, i.e. no bot or no ranked games yet.
- Rating by rank: #1 2197, #10 1953, #25 1872, #50 1781, #100 1662, #200 1521. Median among teams with a bot is 1460.
- Tier counts: Shark 21, Swordfish 124, Tuna 587, Shrimp 106, Plankton 16. **Nobody has reached Orca yet.**
- Top 50 languages: 45 cpp, 5 python. Top 100: 89 cpp.
- Countries: AU 412, IN 179, US 44, GB 34, SG 33, KR 30, NZ 26, CN 24. 294 teams are eligible.
- For the Grand Final cut: the **10th-best eligible team is at 1942** (the 20th is at 1869).

Top 12:

| # | Team (id) | Elo (peak) | Lang | Elig | Notes |
|---|---|---|---|---|---|
| 1 | 龙虎豹 (470) | 2197 (2197) | cpp | Y | CN (SJTU/Fudan). 3,907 battles and 13.7k games. Climbed steadily and is still rising. Ranked switch off. |
| 2 | 中国人能飞 (801) | 2067 (2130) | cpp | Y | Only started around 24 Sep and jumped 1500 to 1950 within a day. |
| 3 | Sponge(Albert and Bob) (213) | 2025 (2104) | cpp | Y | AU/UNSW |
| 4 | Sabotage-d (46) | 2014 (2127) | **python** | Y | IN |
| 5 | SHINK AI 6500 (280) | 2004 (2030) | cpp | Y | JP, high school |
| 6 | Vibing++ (306) | 1987 (2028) | cpp | Y | AU/UNSW |
| 7 | STAR (467) | 1987 | cpp | **N** | KR solo |
| 8 | calc (20) | 1987 | cpp | **N** | CZ |
| 9 | Peanut Butter (104) | 1980 | cpp | Y | AU |
| 10 | SSS (91) | 1953 (2172) | cpp | Y | AU/UNSW |
| 11 | forgot to mention (264) | 1952 | cpp | Y | AU/UNSW |
| 12 | bread first search (507) | 1950 | cpp | **N** | AU |

**Activity:**
- Top teams' records run to thousands of games (龙虎豹 9454-4267-4, Sponge 8751-4370, SSS 7119-3293).
- In each top team's latest 50 battles, **42-48 are unranked "challenge" battles**. Most are other teams scrimming against them as a benchmark; the rest are the top teams testing on each other. Only about 2-14 of those 50 are ranked.
- Top teams run 10-map unranked sets against each other every few minutes. Frequent top-team sparring pairs: 中国人能飞 vs STAR, 龙虎豹 vs 中国人能飞, SSS vs everyone.
- The ladder is volatile: ratings swing ±100 within a day, and SSS dropped from a peak of 2172 to 1953.

## 4. Maps in the ranked pool

Counted from ranked games seen, the pool is **10 maps**: Devil, Schooltime, Portals, Default, Queen Of Spades, Trophy, Autarky, Prisoners Dilemma, Slithery Fight, Trauma. Other maps (Arena, Big Empty, Colosseum, Default Small, Help, Small, Stronghold, Queen Of Spades But She Ages, Autarky (deprecated)) only appear in unranked games.

These numbers come from about 110 replays of games among top-20 teams (plus a few older games), all from 25-26 Sep:

| Map | Size | Start (per side) | Typical end | Median rounds | Winner's longest (median) | Winner's final dragon count |
|---|---|---|---|---|---|---|
| Schooltime | 60x40 | 3 dragons of length 4 | round limit 11/11 | 500 | **54** | 17 |
| Slithery Fight | 63x27 | 7 dragons (2-25 long) | round limit 11/11 | 500 | **49** | 18 |
| Portals | 32x16 | 3 of length 3 | round limit 11/12 | 500 | 31 | 3.5 |
| Trauma | 48x24 | 2 of length 4 | round limit 8/9 | 500 | 31 | 9 |
| Autarky | 54x18 | 1x14 + 3x3 | mixed (5 elim / 6 limit) | 500 | 15 | 29 |
| Default | 32x32 | 4 of length 4 | mixed (4/4) | 371 | 11.5 | 20 |
| Queen Of Spades | 25x35 | 2 of length 3 | mostly elimination (6/10) | 275 | 6 | 30 |
| Prisoners Dilemma | 32x16 | 1x11 + 2x3 | elimination (8/10) | 95 | 4 | 7 |
| Devil | 32x16 | 3 of length 4 | **elimination 9/9** | 124 | 4 | 41 |
| Trophy | 25x25 | 2 of length 3 | **elimination 10/10** | 182 | 4 | 56 |

- Win condition confirmed from replays:
  1. Eliminating the other team wins outright.
  2. Otherwise, at round 500 the **longest single dragon** wins. This held in 59 of 60 round-limit games; the one exception was a tie on longest, which total length broke.
- The `score` shown on /games (and `scoresA/B` in /visualiser) is **total length at the end of the game, not the win criterion**. For example, 中国人能飞 won Schooltime with score 50 against Peanut Butter's 347: one 50-long dragon beat 64 dragons whose longest was 42.
- **Half the ranked pool is effectively a combat map**: Devil, Trophy, Prisoners Dilemma, Queen of Spades, and partly Default and Autarky. There the game ends early by wiping out the enemy with a swarm of short dragons (lengths 2-5). The other half (Schooltime, Slithery Fight, Portals, Trauma) are 500-round growth races decided by one giant.

## 5. What top bots do (from replays)

Replay stats come from parsing replays with the site's own visualiser code; see §6. Medians are over 187 team-sides for top-20 teams.

- **Go wide early.**
  - Nearly every top bot splits aggressively: median 150 splits per game, up to 2,000.
  - Most hit the **64-dragon cap** by round 100-150 (median peak 36, often exactly 64).
  - Foraging is almost all single-step moves. Sprints are rare (median 13 multi-step moves per game).
- **Consolidate late on the growth maps.** The winning pattern on Schooltime, Portals and Trauma:
  - Stay wide until about round 300-380.
  - Then kill off most of your own dragons around round 350-420 so their bodies turn into pearls (⌈L/2⌉ each).
  - Grow one "king" dragon until round 500.
  - Examples:
    - 中国人能飞 on Schooltime: 31 dragons at r350, **1 dragon** at r400, longest 24 at r400, 43 at r450, 50 at r500. It won against 64 dragons (longest 42).
    - Vibing++ on Portals: 22 dragons at r350, 2 at r400, finishing with 1 dragon of length 43.
    - SSS on Schooltime: 62 dragons at r350, 27 at r400, 12 at r450. Its longest went 55, 74, 76.
  - Teams use two sacrifice methods:
    - SSS, forgot to mention, calc and Sponge emit the explicit `suicide` action (median 20-40 per game).
    - 中国人能飞 and 龙虎豹 appear to crash into walls or kelp instead: many "HitWall" deaths and no suicide actions.
- **Sonar is used heavily.**
  - Median about 11k sonar pings per game side, up to 112k (sonar value is a u64).
  - 13% of top sides never use sonar (Team SKKU is low at about 500; SHINK AI is near 0).
  - The leading teams presumably coordinate the king, targets and pearl locations over sonar.
- **Deaths are mostly head-to-head and self/body collisions**, with lots of wall deaths from deliberate sacrifice. Head-to-head trades are 1-for-1 whatever the size, so small kamikaze dragons are the main weapon on combat maps.
- **Two main styles:**
  1. Swarm and eliminate. This wins the small maps: Trophy, Devil and Prisoners Dilemma end by round 100-200 with the winner holding 40-60 short dragons.
  2. Farm, then king. This wins the big maps.

  Good bots switch between them by map. For example, 龙虎豹 lost Slithery Fight to Sponge because its longest was still 7-8 at r200-300 while it held 64 small dragons, and it consolidated too late. Losing a 500-round race usually comes from not having a king ready in time.

## 6. Replays and data access (all public GET, no login)

- Leaderboard: `GET /leaderboard/__data.json?page=N` (10 per page, 86 pages). The response is SvelteKit devalue-encoded, so unflatten it; a helper is at `scratchpad/site/fetch.js`. Each team entry includes its full rating history.
- Team pages: `/teams/<id>/__data.json` gives the record, history, peak and the 6 most recent battles.
- Battles and games: `/battles/__data.json?teams=<id>&page=N` and `/games/__data.json?teams=<id>&page=N`. These include ranked/challenge flags and the map. Scores are not included.
- Game detail: `/visualiser/__data.json?match=<gameId>` returns map, scores (total length), seed, both submission ids, the requester, and the other games in the same series.
- **Replay download:** `GET https://game.battlecode.au/api/matches/<gameId>/replay` redirects (302) to a presigned R2 URL. The file is gzip-compressed and contains a text map header followed by a Cap'n Proto event stream.
  - Event types: `dragonUpdate`, `roundStart`, `turnStart`, `dragonAction` (kinds move/split/suicide), `dragonSplit`, `dragonDeath` (reason W/S/O/H/A), `sonarPing`, `tileChange`, `pearlCountdown`.
- **Parser that works:** `scratchpad/site/parse.mjs` imports the site's own visualiser bundle (`js/viz.js`, a patched copy of `_app/immutable/chunks/B0KoR2-T2.js`) under node. It prints per-side stats: splits, deaths by reason, sonar pings, sprints, dragon count / longest / total over time, and action breakdown.
  - Usage: `node parse.mjs file.replay ...`
  - The bundle hash will change when the site redeploys, so re-download it if that happens. For stable offline decoding also see `notes/tools/replay_decode.py`.
- About 110 replays are saved in `scratchpad/replays/`; some were written there by another agent. Parsed output is in `scratchpad/site/parsed.jsonl` and `rows.json`.
- Not public: `/ratings` and `/submissions` require login.

## 7. Actionable takeaways

1. **Get an active bot on the ladder before 1 Oct.** The Sprint is open to everyone and seeded by rating, and a higher seed gets byes. An upload moves fast under K=96 for its first 10 ranked battles, and autoscrims give about 24 ranked battles a day with no effort.
2. **Make every team member Grand-Final-eligible now:** tick the APAC student box and upload a resume. Otherwise the team is shut out of the 10 Oct qualifier, where only 294 teams are currently eligible.
3. **The bot has to be map-adaptive.** On small or dense maps (Devil, Trophy, Prisoners Dilemma, Queen of Spades) play swarm and kill: many length-2-5 dragons, and head-to-head trades against the enemy's biggest dragons. On big maps (Schooltime, Slithery Fight, Portals, Trauma) farm wide to the 64 cap, then **consolidate around round 350-400** into one king. Sacrifice the others next to pearl paths or near the king using `suicide` or walls, protect the king, and win on longest length at round 500.
4. **The target to beat on growth maps:** winners' longest is about 50-55 on Schooltime and Slithery Fight, and about 30 on Portals and Trauma.
5. **Benchmark for free.** Unranked scrims against any top team, on maps you choose, are allowed and public (others already do this to 龙虎豹 constantly). Download the replays and parse them to diff behaviour. Keep in mind that our battles are public too, so rivals can study our bot the same way.
6. **Mind the Elo mechanics:**
   - Don't request ranked scrims against much weaker teams; a 3-2 or 4-1 win costs rating.
   - Requesting upward is free value.
   - Time new-code uploads so a big improvement gets the fresh K=96 window, which resets 12 hours after the last fresh bot.
7. **C++ dominates the top.** Only Sabotage-d (#4) is in Python. With 25 ms per dragon turn and up to 64 dragons, CPU budget matters.
