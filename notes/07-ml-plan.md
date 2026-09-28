# 07 - ML / optimisation plan (written 27 Sep 2026)

Where we are: v3, hand-written C++ heuristics, ladder about 1600. Top teams are at 2000-2200. We use 5-9M of the 100M points per turn.
Deadlines:
- **Sprint**: 1 Oct, 00:00 UTC (10:00 AEST). Seeded from ladder rating. 4 days away.
- **Qualifier**: 10 Oct. You need to be eligible, which means a resume uploaded.
- **Grand Final**: 17 Oct.

Short answer: **don't replace the heuristic bot with a learned policy.** Use ML in three places:
1. Automated, statistically sound tuning of the parameters we already have, per map.
2. Small models trained on top-team replays, used as extra features and priors inside the heuristic, plus a "where do we disagree with the top teams" diagnostic.
3. Better use of our unused compute: a local head-to-head search for fights.

RL from scratch is the wrong bet at this scale and on this timeline.

---

## 1. What past winners did

| Competition | Winner / top approach | Relevance to us |
|---|---|---|
| **Kaggle Hungry Geese** (2021, 4-player snake on 7x11) | **1st: HandyRL team.** Self-play RL (policy gradient with off-policy correction; V-trace/UPGO/TD(λ) options). Their public starter model took about 1 day on 1 GPU + 64 CPUs. **2nd (Goosebumps):** behaviour cloning on top-agent replays (daily download; the minimum-Elo filter was raised over time, and each raise helped) + PUCT MCTS on top. Their hand-written Rust MCTS (300-400k states/s) led early but finished just outside the top 10. Its main weakness was *mispredicting opponent moves, especially head-on collisions*. **3rd:** BC then RL + MCTS, with a big GPU fleet. **5th:** AlphaZero-style self-play (DUCT search) with dead-end filtering heuristics. | The closest analogue. Pure heuristics got close but not first. BC from top replays + search was a strong, cheap-compute recipe. Opponent head-move prediction was the failure point. |
| **Lux AI S1** (2021) | 1st Toad Brigade: IMPALA + UPGO + TD(λ), a 20M-parameter ResNet, a frozen teacher with a KL loss against strategy cycling, reward shaping for the first 20M steps. Trained on a home 2-GPU PC over weeks. They said RL beat their own rule-based bot. | RL can win, but it took weeks, a centralised full-map policy and GPUs. |
| **Lux AI S2** (2023) | 1st ry_andy_: rule-based Python with forward simulation and a role system (646 teams). RL teams placed lower (FLG 4th). | Heuristics + simulation can still win. |
| **Lux AI S3** (2025) | 1st Flat Neurons: IMPALA/V-trace, ResNet + ConvLSTM + transformer, **pool of frozen past opponents + teacher KL** against self-play overfitting, 1.5B steps (3-4 days) for the final model and more than 20B steps total. **3rd (andreyd41): pure imitation learning** on replays of the top 2 teams (U-Net). The hard part was rebuilding each agent's partial-view observation from replays. | IL from top replays reached 3rd place with modest compute. RL needed industrial compute. |
| **Halite III / IV** (2018 / 2020) | Both winners were rule-based. The Halite IV winner (an ex-DeepMind RL researcher) spent a month on deep RL, couldn't make ships do anything useful, and switched to rules. The Halite II/III ML starter bots (IL) reached mid-table (about #640/5800). | Many units + shared policy + sparse reward = RL is hard to make work. |
| **Battlesnake** | The classic top bots use paranoid minimax / alpha-beta, 4-7 plies, with a flood-fill evaluation. Asymptotic Labs topped the global arena with PPO self-play (4-layer CNN, reward ±1, 524M turns over 4 days on a Titan RTX, promote only if win rate over 30% vs 3 previous bests). | Head-to-head local search is the standard snake tool. RL needs about 10^8-10^9 steps. |
| **MIT Battlecode** | Postmortems (2020-2025): almost all heuristic. Lessons: generalise rather than overfit the ladder maps, copy what top teams do, test heavily with scrims. | Same as our situation. |
| **Chess engines** (Stockfish/Fishtest) | Hundreds of search constants tuned with **SPSA** from self-play game pairs (θ+ vs θ-), and every change accepted by **SPRT**. | The right tool for tuning our ~25 `params.hpp` constants. |
| **Generals.io** (2026 paper) | Superhuman via self-play PPO, 4 days on 4xH200. It found BC pretraining not required at that scale. | Confirms the compute needed for RL. |

**Pattern.** With weeks of time and GPUs, RL wins. With days and a laptop, the winners are heuristics + search + automated tuning, sometimes with a BC prior from top replays. We have 4 days (Sprint) and 20 days (Final), one M5 Pro (18 cores, 24 GB) and no GPU cluster. We also have a decentralised 64-agent, 7x7-view, sonar-coupled game whose winning macro-strategy (swarm, factories, feeding the king, beacons) needs team protocols that RL would have to discover from scratch.

---

## 2. Our constraints, and what they allow

- **Runtime.** No torch at runtime; weights go in as C++ `constexpr float[]`. The zip limit is 4 MB, so even 500k int8/fp16 parameters fit. Memory is 48 MB.
- **Inference cost.** A 7x7xC CNN/MLP of about 50k parameters costs about 100k MAC per call. At a few wasm points per MAC, 4-12 calls per turn (one per candidate move) is under 5M points. **Compute is not the constraint.**
- **Training.** Offline only. `pip install torch` locally is fine for training (neither torch nor numpy is installed now). Training on MPS/CPU with 10^6-10^7 samples and a small net takes minutes.
- **Simulation.** `unswbc run` takes about 1-4 s/game, so 18 cores give about 5-10 games/s, **about 20-30k games/day**. That is plenty for tuning and **far too little for RL**: one game is about 10^4 dragon-steps, so 30k games/day is about 3x10^8 dragon-steps/day, but in heavily correlated batches, and it goes through subprocess/pipe I/O rather than a batched env. A native batched env built from the public engine C++ (about 1.8k lines) would take 1-2 days to build before any learning.
- **Data.** About 333k public games, and replays are downloadable without auth. They hold the full board each round, every action and **every sonar value**. `notes/tools/replay_sim.py` already rebuilds full state exactly. From that we can rebuild any dragon's 7x7 view + length + facing + round + map, and label it with the team's actual action. Top-team games (both sides Elo ≥ 1950) should give tens of thousands of games, i.e. about 10^8 labelled dragon-steps. Tens of thousands of downloads is heavy, so rate-limit them. **This is our biggest untapped asset.**
- **External evaluation.** Unranked scrims against *any* team on maps we choose, up to 60 games/hour. This is the only ground truth against real top bots. **Ask the user before running server matches.**

---

## 3. Ranked options

Gains are rough ladder-Elo guesses for a well-executed version. Scale: 100 Elo ≈ a 64% head-to-head win rate.

| # | Option | Expected gain | Effort | Risk | When |
|---|---|---|---|---|---|
| **A** | **Proper tuning harness: SPRT-gated A/B + SPSA over continuous params + per-map param tables.** Our past sweeps (40-60 games) were underpowered: 26-14 is only p≈0.08. | +50-120 | 0.5-1 day infra, then runs overnight | Low, if opponent-pool validated (see §5) | **Now (Sprint)** |
| **B** | **Top-team replay "disagreement mining".** Train a small BC model of top teams' moves (or just use their logged states), run our bot's move scorer on the same states, and list high-confidence disagreements by situation (ram/flee, split timing, feeding, dead ends). Fix the heuristics by hand. | +50-150 (finds real bugs and missing tactics) | 1.5-2 days (dataset builder is most of it) | Low: advisory only, nothing learned ships | Start the download now; analysis after Sprint |
| **C** | **Enemy head-move model** (P(enemy head goes to tile x) given the local view, their length and nearby heads), learned from replays, used in ram and king-threat logic. Hungry Geese's hand-written MCTS lost mainly to mispredicted head-ons, and 55/63 of big-dragon deaths here are rams by L≤5 dragons. | +40-100 (combat maps, king safety) | 1-1.5 days | Low-medium | After Sprint (by 5 Oct) |
| **D** | **Local fight search**: paranoid/BRS minimax over our head(s) + enemy heads within the 7x7, 2-4 plies, with a C-model or uniform prior for enemies and the existing flood-fill/room as leaf evaluation. Uses the idle 90M points. The standard Battlesnake technique. | +40-120 on the 5-6 elimination-prone maps | 2-3 days | Medium: correctness bugs, wasm timing | 3-12 Oct |
| **E** | **BC policy prior as a feature**: add `w * log p_BC(move)` to the heuristic move score, with `w` tuned by SPSA. Also a learned "dies within k turns" danger head. Same data as B/C. | +30-100, uncertain | +1 day on top of B | Medium: BC copies average mistakes, and the weight must be tuned | 5-12 Oct |
| F | Full BC policy replacing the heuristics (andreyd41-style) + safety filter | Unknown; likely worse than the heuristics without search | 3-5 days | High: the sonar/feeding/beacon protocols won't be learned from single-dragon views | Not recommended |
| G | Evolution strategies / CMA-ES over *many* weights (e.g. a linear evaluation on 30-50 features) | +20-60 over A | Needs A's harness; 2-3 days of compute | Medium: noisy fitness, overfitting to the pool | Optional, Oct |
| H | PPO/IMPALA self-play (full RL, shared decentralised policy) | Could be large *eventually* | 2 days env + weeks of compute | **Very high**: 10^8-10^9 steps needed (Battlesnake 5x10^8, Lux S3 1.5x10^9), must rediscover swarm/feeding/sonar, no GPU fleet | **Not before 17 Oct** |

Not ML, but the replay notes (05) say these are worth as much as any ML item: factories on Trauma/Autarky/Portals/Dilemma (not done yet), king head safety, and feeding volume (top teams feed about 50 own-corpse pearls to the king). The disagreement mining in B should confirm how much each is worth.

---

## 4. Recommended plan

### Sprint: 27 Sep to 30 Sep (freeze about 30 Sep 12:00 UTC)

**Day 1 (27-28 Sep): tuning infrastructure**
1. **Runtime params for local builds.** Wrap every `params.hpp` constant so a local-only env var (e.g. `BOTPARAMS="AREA_WEIGHT=45,FEED_START=340"`) overrides it. Put this behind `#ifndef SUBMISSION`, so the submitted bot keeps its constants. This avoids a recompile per candidate.
2. **Per-map parameter tables.** The bot already knows the map, so make the key params `param[map_id]` with a global default for unknown maps. The pool splits into combat maps (Devil, Trophy, Dilemma, QoS) and growth maps (Schooltime, Slithery, Portals, Trauma), and the best `SPLIT_STOP_ROUND`, `FEED_START`, `RAM_MAX_OWN_LEN`, `AREA_WEIGHT` and `KING_THREAT_REACH` almost certainly differ between them.
3. **SPRT in arena.py.** Use the Fishtest-style Bayesian/GSPRT on win/draw/loss with elo0=0, elo1=+30, α=β=0.05. Play paired seeds with sides swapped. Stop early when decided. Report per map.
4. **Opponent pool:** v1, v2, v3 + 3-4 "style" variants of v3 (no feeding, split at 6, max aggression `RAM_MAX_OWN_LEN=5`, early feeding). Fitness is the **mean over the pool**, never only v3.
5. Measure real throughput (games/s per map). Then start **SPSA overnight** on about 8-12 continuous params, one run per map group. Fishtest recipe: θ+ vs θ- games, c_k chosen so ±c is worth a few Elo, and a_k decaying.

**Day 2 (28-29 Sep)**
- Read the SPSA results. SPRT-test each map group's tuned set vs v3 **against the pool**.
- In parallel, start the **replay download** in the background (rate-limited). Take the top-~30 teams' games from the last 7 days, both sides Elo ≥ 1900, and store them compressed. This feeds B, C and E later.
- If there is time, add one tactic from 05 that tuning can't create: a factory loop on the 4 hot-tile maps, or the king never within Manhattan 3 of an enemy head of length ≤ 5.

**Day 3 (29-30 Sep)**
- Final candidate vs v3: SPRT over all 10 maps + a **held-out seed range** that was never used in tuning. Also run 5-10 games with `--sandbox` to check wasm timing and memory.
- **Ask the user** before this step: run 2-3 unranked 10-map scrim sets against teams at about 1800-2100 (e.g. Peanut Butter, Vibing++, SSS) with v3 and with the candidate. Promote the candidate only if it is at least as good there.

**Day 4 (30 Sep, before 12:00 UTC): freeze and submit (with user OK)**
- Rating at 1 Oct decides the seed. A new bot runs at K=96 for its first battles, so a real improvement climbs fast and a regression falls fast. Only submit if it passes SPRT against the pool *and* the server check. Submitting 12+ hours before the Sprint lets autoscrims settle the rating.

### Qualifier: 1 Oct to 10 Oct
- **1-3 Oct: dataset builder.** Extend `replay_sim.py` (or write a C++ port for speed) to emit one sample per dragon-step for top teams:
  - the exact 7x7 view the engine gives (channels: wall/kelp, pearl + value, own body/head, ally body/head, enemy body/head, portal, segment age);
  - scalars: length, facing, round/500, map id one-hot, units alive, recent sonar bits;
  - labels: first move direction (relative: F/L/R/B), split k, sprint flag, and "died within 1/3/10 turns".
  - Canonicalise the rotation to the facing direction (as the Hungry Geese 5th-place solution did). Keep only the winning team's samples, or weight them, and skip decided positions (as Lux S3's 3rd place did).
- **3-5 Oct: train small models** (PyTorch locally, e.g. conv 3x3 32ch x2 → FC128 → heads; about 30-60k params). Export to `bot/nn_weights.hpp` with a 60-line hand-written C++ forward pass, and unit-test against PyTorch outputs.
  - (C) Enemy head-move model, trained on *enemy* dragons from the viewer's perspective.
  - (B) Disagreement report: top-team move vs our argmax, grouped by situation. Fix the top 3-5 categories by hand.
- **5-8 Oct:** plug C into ram/threat logic and E as a prior term. Re-run SPSA including the new weights. SPRT vs the pool (now including the Sprint build). Server check (with user OK).
- **8-9 Oct:** freeze and submit about 24 h before the 10 Oct seeding. Check that the **resume/eligibility flag** is set, since the Qualifier is eligible-only.

### Grand Final: 10 Oct to 17 Oct
- **Robustness first.** The final may use new or changed maps. Tune and test the unknown-map mode (`NO_KNOWN_MAPS=1`) on the 10 non-ranked maps as a held-out set, and make sure the per-map tables fall back to good globals.
- **Option D, local fight search.** Paranoid 2-4-ply search over heads in view, using the C model for enemy move ordering. Gate it behind SPRT on the combat maps.
- **Anti-exploitation.** Watch finalists' recent replays for their ram and feed patterns (for example, Sabotage-d's beacon is decodable, see 05 §5). Check that our king survives their rammers.
- Last submit about 36 h before the final, then only bug fixes.

---

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Overfitting to self-play.** SPSA's θ+ vs θ- games only measure strength against near-copies. Our self-play gains (v2→v3 63%) have not shown up as ladder gains (still about 1600). | Fitness = mean vs a **diverse pool** (past versions + style variants + later a BC-policy bot as a "top-team-like" opponent). Accept changes only via SPRT vs the pool. Final gate = server scrims against real top teams (with user OK). Keep an **Elo league table** of all versions, and never promote a version that loses to an older one by more than about 55/45. |
| **Noisy evaluation / false positives** | SPRT instead of fixed 40-60 game samples. Paired seeds + side swap. Separate tuning and validation seed ranges. Report per map, because a +10% average can hide a -30% map. |
| **Overfitting to 10 maps / seeds** | Per-map params only on ranked maps with generic fallbacks. Held-out seeds. Hold-out maps (the 10 non-ranked maps) for the unknown-map mode. |
| **BC copies average mistakes / distribution shift** | Use BC only as features/priors with a tuned weight (Goosebumps: BC alone was weak, BC + search was strong). Filter to winners and high Elo. Keep the safety filter and survival DFS as hard constraints. |
| **Replay decoding errors → garbage labels** | `replay_sim.py` already reproduces the 40 test replays exactly. Add assertions that the rebuilt 7x7 matches the engine's view logic (`engine/` source), and spot-check with `BOTDBG` dumps of our own games. |
| **Wasm compute/time regressions** | Every candidate runs `--sandbox` games. Keep the NN under 5M points per turn. Keep the fallback path if the budget is exceeded. |
| **Throughput** | 18 cores ≈ 20-30k games/day. Budget: SPSA about 10-15k games/night; each SPRT about 300-1500 games. Don't start RL. |
| **Submitting at the wrong time** | Only validated builds. Remember K=96 on fresh bots (fast moves both ways) and the 12 h fresh-bot window. Freeze well before 1 Oct 00:00 UTC and before the 10 Oct seeding. |
| **Scraping load / ToS** | Rate-limit downloads (e.g. 1-2 req/s) and cache locally. Only public, unauthenticated endpoints. |

---

## 6. Sources
- Kaggle Hungry Geese:
  - 2nd place (Goosebumps), BC + MCTS and hand-written MCTS notes: https://www.kaggle.com/competitions/hungry-geese/writeups/goosebumps-goosebumps-solution-2nd-place
  - 5th place GeeseZero (AlphaZero/DUCT): https://www.kaggle.com/competitions/hungry-geese/discussion/263702
  - 3rd place slides (BC + RL + MCTS): https://speakerdeck.com/hoxomaxwell/kaggle-hungry-geese
  - 1st place (HandyRL team), linked from https://github.com/DeNA/HandyRL → https://www.kaggle.com/c/hungry-geese/discussion/263279
  - HandyRL starter compute (1 day, 1 GPU + 64 CPUs): https://www.kaggle.com/competitions/hungry-geese/discussion/218190
  - DQN study: https://arxiv.org/abs/2109.01954
- Lux AI:
  - S1 Toad Brigade (IMPALA, teacher KL): https://www.kaggle.com/competitions/lux-ai-2021/writeups/toad-brigade-toad-brigade-s-approach-deep-reinforc and https://github.com/IsaiahPressman/Kaggle_Lux_AI_2021
  - S2 1st (ry_andy_): https://github.com/ryandy/Lux-S2-public
  - S2 FLG 4th (RL): https://www.kaggle.com/competitions/lux-ai-season-2/discussion/406702
  - S3 1st Flat Neurons (IMPALA, opponent pool, teacher KL, 1.5B steps): https://www.kaggle.com/competitions/lux-ai-season-3/writeups/flat-neurons-1st-place-approach-by-flat-neurons
  - S3 3rd, imitation learning: https://github.com/andreyd41/lux3-bot
- Halite:
  - IV winner: https://github.com/ttvand/Halite and https://www.kaggle.com/c/halite/discussion/183543
  - III winner (rule-based): https://github.com/teccles-halite/halite3-bot
  - ML starter bot results: https://www.twosigma.com/articles/best-practices-from-building-a-machine-learning-bot-for-halite/
- Battlesnake:
  - PPO self-play postmortem: https://medium.com/asymptoticlabs/battlesnake-post-mortem-a5917f9a3428
  - Paranoid minimax: https://coreyja.com/posts/BattlesnakeMinimax/Minimax%20in%20Battlesnake/
  - Multi-player search survey (paranoid/BRS vs MCTS at small budgets): https://dke.maastrichtuniversity.nl/pim.nijssen/pub/cgw.pdf
- MIT Battlecode postmortems:
  - https://battlecode.org/assets/files/postmortem-2025-just-woke-up.pdf
  - https://battlecode.org/assets/files/postmortem-2025-confused.pdf
  - https://web.mit.edu/agrebe/www/battlecode/21/index.html
  - https://blog.stoneztao.com/posts/bc21/
- Tuning:
  - SPSA: https://www.chessprogramming.org/SPSA and https://www.chessprogramming.org/Automated_Tuning
  - Fishtest SPRT maths: https://official-stockfish.github.io/docs/fishtest-wiki/Fishtest-Mathematics.html
  - CMA-ES: https://cma-es.github.io/
- Generals.io self-play RL (2026): https://arxiv.org/abs/2606.23348
