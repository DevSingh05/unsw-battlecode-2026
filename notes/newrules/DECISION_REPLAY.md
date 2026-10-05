# Decision replay: re-run our bot on any turn of a server game

Written 2026-10-05 (EDT). Tools: `tools/decision_replay.py`, `tools/pearl_infer.py`. Nothing in `bot/` changed.

## What it does
Give it a server game id, a dragon and a round. It rebuilds the exact stdin that dragon's process got on the judge,
from its birth up to that round, feeds it to a fresh build of the bot, and prints what the bot answers and why
(the bot's own BOTDBG trace: every candidate move with its score, area, depth, threat; free-path sprints; splits;
queen vetoes).

The input is not approximated. The harness runs the real engine (`unswbc_engine.wasm` from the toolkit, the
same code the judge runs) with the replay's seed. Every dragon on both teams is a puppet that answers each turn
with exactly the action and sonars recorded in the server replay. The engine then produces the init block and
every round block byte for byte: vision, pearl countdowns, bodies, edges, sonar inbox and ECHOES. The rebuilt
game is compared event by event with the server replay (moves, splits, deaths, pearl spawns, sonar pings).
`IDENTICAL` means the input is exact.

The bot then runs in the toolkit's judge sandbox by default: the wasm build from the judge's clang, CPU points
as the clock, the judge's memory limit and RNG. So the budget cutoffs (REPLY_BUDGET_M, FS_BUDGET_M,
QK_SURV_BUDGET_M) fire exactly as they did on the server. `--engine native` is a clang++ build: faster, but its
clock is wall time, so budget-limited searches can differ.

## Usage (run from the project root)
```
python3 tools/decision_replay.py show 1165000 --sub b3 --dragon q --round 59 --to 66 --debug
python3 tools/decision_replay.py show GAME --dragon 12 --round 140 --input      # + the raw protocol block
python3 tools/decision_replay.py show GAME --dragon q --round 200 --debug --sonar --topn 10 --segs
python3 tools/decision_replay.py verify GAME --sub b3 [--engine native] [--dragons 0,7] [--json out.json]
python3 tools/decision_replay.py check GAME          # rebuilt game == server game? lists our dragons + lifespans
python3 tools/decision_replay.py dump GAME --dragon 7 --upto 120 -o d7.txt     # raw stdin stream
```
- `GAME`: a game id (replay looked up under `replays/**/<id>.replay`, else downloaded from the public replay
  endpoint) or a `.replay` path. Our side comes from `replays/ab_server/games.json` (team 952); `--side A|B` overrides.
- `--dragon q` is our queen. Use `check` to list our dragon ids with the rounds they were alive.
- Bot source: `--src DIR` (default `bot/`), or `--sub NAME|ID` for the exact zip of one of our server submissions
  (downloaded once into `replays/decision_replay/subs/<id>/`; NAME means the newest upload with that name). Use
  `--sub` for fidelity: `bot/` has moved on since b3 (new flags at their defaults still change some code paths).
- `-D FLAG=V` (repeatable) defines compile-time flags (prepended to a staged copy of main.cpp; never edits
  `bot/`). This is a counterfactual: the same input history with different code. The history still reflects
  what the server bot did, so a changed bot's internal plans can drift from what it would have seen in a real
  game. Read it as "what would this code do in exactly this position".
- `--debug` builds with `-DDECISION_DEBUG=1` (a marker; the bot's tracing is the existing BOTDBG mechanism) and
  runs it in the sandbox with BOTDBG pointing at a scratch folder. Writes to the trace file are not charged CPU
  points, but formatting the trace inside the bot is, so a turn near a budget cutoff could still change. The
  harness also runs a build without the trace and prints a WARNING if the two disagree.
- Builds and traces go to the scratch dir (`$DR_BUILD`, default `.../scratchpad/dgu/harness/build`). Rebuilt
  streams are cached in `replays/decision_replay/<gameId>/streams.pkl.gz`.
- Cost: rebuilding a game takes 0.1-2 s. `verify` on a whole game (every one of our dragons, 10-17k turns)
  takes 5-15 s in the sandbox. It uses one CPU core.

## Fidelity (measured 2026-10-05, b3 submission zip id 17887, every one of our dragons over every turn)
16 b3 games (9 losses, 7 wins; 15 maps; 4 on the server's second pearl layout), all of our dragons, every turn. Every rebuild was IDENTICAL to the server replay, event for event.

| game | map | result | pearl layout | turns | sandbox actions | sandbox sonar | native actions |
|---|---|---|---|---|---|---|---|
| 1166037 | Portals | L | live | 10518 | 10518/10518 | 2774/2774 | 10518/10518 (100.00%) |
| 1165000 | Australia | L | live | 17573 | 17573/17573 | 2934/2934 | 17374/17573 (98.87%) |
| 1164522 | Prisoners Dilemma | W | live | 517 | 517/517 | 0/0 | 517/517 (100.00%) |
| 1166014 | Trophy | W | live | 546 | 546/546 | 40/40 | 546/546 (100.00%) |
| 1152194 | Devil | L | fitted 2nd layout | 169 | 169/169 | 0/0 | 169/169 (100.00%) |
| 1165829 | Devil | W | fitted 2nd layout | 10428 | 10428/10428 | 0/0 | 10428/10428 (100.00%) |
| 1151986 | Schooltime | L | schooltime_b3 | 3949 | 3949/3949 | 598/598 | 3949/3949 (100.00%) |
| 1166762 | Schooltime | W | schooltime_b3 | 14501 | 14501/14501 | 3629/3629 | 14364/14501 (99.06%) |
| 1152152 | Slithery Fight | L | fitted 2nd layout | 23563 | 23563/23563 | 4297/4297 | 23563/23563 (100.00%) |
| 1164104 | Slithery Fight | W | fitted 2nd layout | 25193 | 25193/25193 | 4214/4214 | 25193/25193 (100.00%) |
| 1165646 | Stripes | L | live | 554 | 554/554 | 102/102 | 554/554 (100.00%) |
| 1166577 | Trauma | W | live | 14565 | 14565/14565 | 1335/1335 | 14565/14565 (100.00%) |
| 1164990 | Autarky | L | live | 7142 | 7142/7142 | 446/446 | 7142/7142 (100.00%) |
| 1162276 | Around UNSW | L | live | 24324 | 24324/24324 | 3602/3602 | 24097/24324 (99.07%) |
| 1162277 | Default | L | live | 1235 | 1235/1235 | 134/134 | 1235/1235 (100.00%) |
| 1166766 | Tower Defense | W | live | 4797 | 4797/4797 | 0/0 | 4797/4797 (100.00%) |
| **all 16** | | | | 159574 | **159574/159574 = 100.00%** | 24105/24105 | 159011/159574 = 99.65% |

Sonar match is the share of turns whose four directed sonar values all equal the server's (turns where the
dragon died during its move have no recorded sonar and are skipped).

What mismatches when it does:
- **Native engine only: CPU budget.** Australia 1165000: 199 of 17573 turns differ natively, 0 in the sandbox.
  These are turns where the reply search or free-path search hit its points budget on the judge. Natively the
  clock is wall time (faster), so the search goes further and picks something else. Use the sandbox (the
  default) whenever the exact move matters.
- **Unknown pearl layout.** Server replays carry the map with every pearl spawn gap zeroed. The harness takes
  the gaps from a local map file and checks each candidate by emulating the pearl tick (the engine draws gaps
  with `std::mt19937_64(seed)`: one draw per owner bed at init and per spawn attempt; mirrored beds share a
  countdown). If no known layout reproduces the game, the pearls in the rebuild drift from that round on, and
  the tool says so (`REBUILD DIVERGES ...` plus a WARNING naming the round).

## Finding: the server plays two versions of five maps
Checked against all cached replays (25-237 per map). The live API map text (`/api/v1/maps`, = `maps/server_live/`)
explains only part of the games on these maps. The rest come from a second layout with the same mapId. The two
are interleaved through the whole day, so they are not an update over time:

| map | games on the 2nd layout | what differs |
|---|---|---|
| Schooltime | 57 of 120 | different kelp walls and pearls: this is exactly `maps/schooltime_b3.map` (reproduces all 57); known as "Schooltime B" |
| Devil | 66 of 120 | pearl beds only: the 1-600 / 1-300 / 1-30 centre columns are gone, and (15,1)/(16,1) spawn every round (1-1) |
| Slithery Fight | 107 of 237 | pearl beds only: 166 new beds (several with gaps such as 100-300), 149 removed, 48 with new gaps |
| Prisoners Dilemma | 52 of 116 | pearl beds only; fitted, reproduces all 52 |
| Queen Of Spades | 55 of 120 | pearl beds; **NOT fitted yet**: the fitter gets stuck at round 9 even with 16 games (probably beds that never spawned and aren't in our base file). Rebuilds of these games diverge in pearls from about round 0-9, so their input is approximate after that and moves will drift. |

The fitted layouts are in `replays/decision_replay/maps/*_alt.map`; for Schooltime the harness uses `maps/schooltime_b3.map`. Their geometry is the live geometry; the
harness only takes the TILE lines from them and the walls from the replay. They reproduce every tick spawn of
every cached game on that layout. Relevance for the bot: any per-map pearl knowledge (pearl routes, spawn tiles
in `maps_data.hpp` / `pearl_route.hpp`) is wrong in about half of the games on these maps. For Schooltime this is the known "Schooltime B" (`maps/schooltime_b3.map`). The other four second layouts were
new to us. I have not checked how our map identification and pearl routes react to them. That check is the
next step.

Refit or extend: `python3 tools/pearl_infer.py --auto --base maps/server_live/<map>.map` fits from every cached
replay that the live layout does not explain, and writes `replays/decision_replay/maps/<map>_alt.map`.
`pearl_infer.py GAME... --base FILE` checks a layout against games. The fitter works like this:
1. Beds are the tiles that ever spawned at a tick, plus base beds that never spawned (kept only if their gaps
   fit). Hidden beds of any other kind can't be seen, but they would break the check below.
2. A depth-first search over the init draws: owner k takes draw k, and its first attempt must land on its first
   observed spawn, or on a round where both tiles were blocked.
3. A greedy repair at the first round where the emulated spawns differ.

## Worked example: why our queen died on Australia (game 1165000, b3, loss)
`show 1165000 --sub b3 --dragon q --round 59 --to 66 --debug`, all moves MATCH the server:
- r59-r61: queen L5 in the open (area ~3500, depth 12), eating normally.
- **r62 at (35,24): the bot picks W, which goes through a portal to (56,40): `cand W t=(56,40) pearls=3.88
  area=12 depth=12 score=38.81`, against `cand E area=3756 score=15.65`.** That is a 12-tile region chosen for
  2.3 more expected pearls. The area term did not weigh a 12-tile pocket enough against pearls for the queen.
- r63: one candidate left, `area=1 depth=1 score=-1151`. It is trapped.
- r64, r65: `reverse split` twice (L7 to 5 to 3). Each split puts a child into the same pocket.
- r66: no candidates (`top 0/0`), fallback MOVE N, dies HitOtherBody at L3.
This is the "queen eats into a pocket" pattern from LOSS_AUDIT2, now down to the one decision and its numbers.
Here it entered through a portal. The concrete lever is the queen's score for a candidate whose reachable area
is below some multiple of her length, when an open alternative exists.

## Limitations
- Opponent processes are not re-run (we don't have their code). Their moves are puppets, which is all the
  rebuild needs.
- A bot crash, timeout or restart on the server shows only as a suicide action. Such dragons die on that turn,
  so no surviving dragon ever had a restarted process, and the stream for every dragon we replay is one process.
- Queen Of Spades games on its second layout (about half) can't be rebuilt exactly yet (see above).
- Pearl gaps: games on an unknown layout are flagged. Their input is exact up to the first wrong spawn and
  approximate after it.
- `--debug` traces cost CPU points inside the bot. The harness warns when that changes the move.
- `--engine native` differs on budget-limited turns (0-1% of turns in the games tested).
