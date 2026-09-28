# 12 - Discord #strategy channel digest

Source: UNSW Battlecode 2026 Discord, #strategy. Read-only pass on 2026-09-28, covering the whole
channel from its first message (3 Sep) to 28 Sep 01:49 UTC, roughly 350 messages. Nothing was posted, reacted to or voted on.
Timestamps below are UTC. The channel was almost empty until 21 Sep. Most of the useful content is from 21-28 Sep.
Pinned messages were not opened (that would need a click).

Not discussed anywhere in #strategy: specific map names (Schooltime, yard, trauma, slithery, devil,
trophy, portals map), symmetry, timeouts, merge mechanics in detail. Look in #ask-devs / #map-ideas / #changelog for those.

---

## 1. Strategy insights and tricks

### Macro vocabulary (xCirno / team Stockfish, 25 Sep 04:55)
xCirno posted a glossary, and No. 1 larper replied that it covered "like 80% of all my strats". This is a good
checklist of what top bots do:
- **Map:** *Fountain* = high-spawn pearl area; *Pocket* = narrow area you can enter but only leave by splitting; *Corridor* = 1-wide path.
- **Offense:** *Ram* = move head-on into an enemy head, both die; *Swarm* = long dragon splits into many small ones; *Contest* = two teams fighting over a fountain.
- **Defense:** *Danger zone* = tiles an enemy head can reach next turn; *Crowding* = too many own dragons in one area; *Escape-split* = split to reverse direction when stuck or attacked (the tail becomes the new head).
- **Development:** *Yield* = leave a pearl for a nearer teammate; *Scout* = short dragon sent blind through an unexplored portal; *Breeding* = split as fast as food allows to grow numbers.
- **Endgame:** *Champion* = the single longest dragon the team plays the tiebreak for; *Donor* = a dragon sacrificed so the champion can eat it.
- ILikCoding's alternative names for the same ideas: "Kamikaze", "Cannibalise".

### King / champion growth and feeding
- **The #1 leaderboard bot self-coils and sacrifices minis to feed the big one.** Dearest You asked about this on 24 Sep 23:11 with photos of a replay, and Kieran answered with his over-yonder roles/tactics articles (see links).
- **Don't hard-assign a champion** (No. 1 larper, 25 Sep 06:24): use relative lengths. Each local maximum gets fed, and as dragons merge you end up with one champion. He said a fixed single champion is "really risky".
- **Champion election** (xCirno, 06:28): champions are elected and have authority over short and mid-length dragons. Some rounds have no champion because of information delay. A new one is elected once the old one is confirmed dead.
- **Queen protection** (xCirno, 21 Sep 07:06): "late-game growth mode" means identifying the queen (the longer, more valuable half after a split, including reversed children) and keeping small dragons near it to kill nearby enemies.
- **Don't trap your own mother dragon** (xCirno, 24 Sep 11:18): small dragons must stay away from the mother's head. If they have no legal option, they self-destruct.
- **No. 1 larper (25 Sep 05:18):** these macro strategies are easy to implement and strong, so soon every bot will have a strong baseline.

### Ramming
- **Ram:** a 2-length dragon driven into an enemy head kills both "regardless of length" (BlueInferno1445, 21 Sep 07:42).
- **Combat rules are frozen:** rtrgrd (dev, 22 Sep 14:36) said head-to-head combat mechanics are very unlikely to change, so ram logic is a stable investment.

### Pearls and pathing
- **Target pearls before they spawn:** go for tiles where a pearl will spawn by the time you arrive. They are effectively the same as tiles that already have a pearl (RyanThe27th, 24 Sep 23:52).
- **Use the timer:** rtrgrd (24 Sep 03:00): "You should make use of timer info!" This most likely means the pearl spawn timer.
- **Pick rich areas:** xCirno says to work out which area is rich in pearls (fountains) and not just chase the nearest pearl.
- **Pathfinding:** xCirno (25 Sep 14:14) runs Dijkstra over the whole map, with different weights for kelp, portals and so on. It costs about 3M CPU points. Several people noted there is far more compute than in normal Battlecode, so whole-map Dijkstra every turn is affordable.
- **Seeds:** pearl spawn seeds used to be fixed, which made them deterministic and possible to hardcode. RoryFromUnisa hints that an update randomised them.
- **Portals:** portals appear to be visible to dragons (sungodtemple: "Should be", 26 Sep 21:59).
- **Other tips:** "look at enemy's homework" (Kieran), meaning watch top-team replays. Rory: many top bots use sprinting, so look at the top feed games.

### Sonar / comms
- **Message size:** a sonar message is a 32-bit integer, 4 bytes (CMA / xCirno, 22-23 Sep).
- **Range:** the message travels as a 1-cell-wide line, so another dragon rarely receives it without prior coordination (RyanThe27th). Players on 21-22 Sep called it "almost useless" or "useless" for coordination.
- **Upgrade promised:** rtrgrd, 22 Sep 14:31: "we're def upgrading sonar tmrw". Check #changelog for the new sonar rules.
- **Sonar as a distance bound:** after the update, RoryFromUnisa (25 Sep 12:38) said the sonar response gives an upper bound on how far away another dragon is, assuming a wall there. rtrgrd called sonar "def unconventional comms for bc".
- **Joke protocols:** "SONAR 67 you instantly win" (rtrgrd) and "if you receive 22 then suicide" (Rory). These are jokes, not real.

### RL / ML
- **xCirno (26 Sep):** tried RL and it didn't work well. It needs hundreds of varied, unbiased maps plus a strong starting bot.
- **rtrgrd's options (26 Sep 11:34):**
  - (1, hard) a pure RL bot, which overfits to maps.
  - (2, easier) RL a bot hyper-optimised for one map, then make your classical bot beat it.
  - (medium) RL an extremely good dragon policy per map, then tune the classical bot to beat all of them without overfitting.
  - Use RL "to find interesting new metas" and copy the behaviour.
- **xCirno's macro/micro split:** RL for *macro* means hand-written modes (offense, defense, scout) with RL choosing the mode from live variables. He says this is easier to train. *Micro* RL (pearl scoring, portal choice) barely changes results.
- **Who uses RL:** calc (Miran) says they use ML but won't give details. lmkæ (28 Sep): "a lot of good teams have figured out RL".
- **Architectures:** Kieran's poll on 27 Sep had utility systems in the lead (2/6), then behaviour trees, BDI, HSM and rules-based at 1 each. Kieran plans to move to GOAP by the end of ladder.

---

## 2. Dev statements about rules and maps (rtrgrd, sungodtemple, Kieran)

- **rtrgrd, 25 Sep 05:17:** more map updates are coming to encourage macro, "expect things similar to autarky and dilemma".
- **Probably rtrgrd, same thread:** "tldr anything 'cool' that the ruleset allows for we'll probably implement". The message is grouped under sungodtemple in the DOM, so attribution is uncertain.
- **rtrgrd, 05:19:** current maps hand-hold (they "literally make the dragons for you"), but the crutches will be removed as the level of play rises.
- **rtrgrd, 06:27:**
  - Look for loopholes and edge cases in the kelp, portal and pearl rules.
  - A good bot switches between strategies depending on the situation.
  - "There is no one single dominant strategy." The map pool is diverse on purpose, and teams are encouraged to make their own maps.
- **rtrgrd, 08:31 - hardcoding:** hardcoding maps may gain ladder Elo but "won't help at all for sprint/qual". The sprint and qualifier pools use unseen maps, so write dynamic heuristics.
- **rtrgrd, 08:32 - map lessons:** the later maps are each designed to teach a "lesson" about some emergent part of the game.
- **rtrgrd, 22 Sep 14:31-14:36:**
  - Sonar upgrade coming.
  - Reworks will be as minimal as possible and won't destroy existing progress.
  - Head-to-head combat is very unlikely to change.
  - "planning to add some adversarial maps".
- **Kieran (writes the over-yonder blog):** will share one or two more articles during ladder, then go quiet during the serious competition to avoid influencing it.
- **Tournament format:** double elimination (HerbertTheBird, 22 Sep).

---

## 3. External links

URLs are given without query strings.
- over-yonder.tech/games/loong/ : Kieran's "The Loong Game" series index. It covers strategy and tooling for this game.
- over-yonder.tech/games/loong/the-wishlist/ : post 2, what a bot needs, a plan for building a solid foundation.
- over-yonder.tech/games/loong/the-choice/ : a "weekend reading" post (25 Sep).
- over-yonder.tech/games/loong/the-shape-of-the-problem/ : how to structure the problem.
- over-yonder.tech/games/loong/roles/ : wyrm "jobs" and roles, the answer to "how does #1 feed the big one".
- over-yonder.tech/games/loong/tactics/ : curling and coil tactics.
- Upcoming tooling post "Playing to win... sometimes": a judge replica written in Zig with memory optimisations, run on a 256-vCPU EC2 machine. Kieran says the tooling posts go up on the "over|yonder - The Loong Game" open-source channel/thread.
- game.battlecode.au/teams/25 : a team page shared by aespo, showing that the replay "round mode" viewer exists.

---

## 4. What we should try

1. **Donor/champion endgame without a fixed champion.** Treat the longest dragon in each local cluster as champion. Smaller dragons yield pearls to it or coil and get eaten (donor) late in the game. Re-elect the champion when it dies. Match the #1 bot's "self-coil and sacrifice minis" pattern (read over-yonder roles/tactics first).
2. **Ram as a primitive.** Keep 2-length dragons as dedicated rammers against the head of the enemy's largest dragon. Combat rules are frozen, so tune this aggressively.
3. **Danger-zone and escape-split.** Never step into tiles an enemy head can reach next turn unless trading favourably. When boxed in, split to reverse direction.
4. **Timer-aware pearl targeting.** Score tiles by expected spawn time against our arrival ETA, and favour fountains over lone pearls. Use yield so two of our dragons don't chase the same pearl.
5. **Weighted whole-map Dijkstra.** Weight kelp, portals and danger. There is enough compute for this every turn, so check our budget and cache distance fields.
6. **Sonar, after checking the new rules in #changelog.** At minimum, use sonar returns as a distance or wall bound. The 32-bit payload is enough for "champion id + position" or "fountain here".
7. **Don't overfit to ladder maps.** Sprint and qualifier use unseen maps, including upcoming "adversarial" and autarky/dilemma-style macro maps. Test on self-made maps: pockets, corridors, isolated regions.
8. **Mode-based macro controller.** Use offense, defense, scout and breed modes chosen by a utility score. We could tune this later with self-play or RL instead of RL on micro.
