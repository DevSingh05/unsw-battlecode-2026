# Stockfish / forgot to mention (ftm): losses since v34 went live (30 Sep 07:35 UTC)
Data: API battles 05:16-09:54 UTC plus replays/auto ledger 29 Sep 22:29 to 30 Sep 04:09. Games between 04:09 and 05:16 are missing, and the window is 11.5h, not 24h. 237 games. All 66 games since 07:35 were replayed through sim2, and every side and result matched. Scripts and pickles: scratchpad sf/{tab,an,deaths,feed,selfk,rams3}.py.
## 1. Per-map W-L (worst maps first)
| window | Stockfish | ftm |
|---|---|---|
| all (11.5h) | 41-55: Sch 2-15, Sli 3-13, Por 5-13, QoS 4-5, Dev 1-5, Tra 4-2, Tro 4-1, Aut 11-1, Def 3-0, PD 4-0 | 72-69: Sch 6-14, Sli 9-12, Aut 4-10, Dev 3-8, Por 13-6, QoS 7-6, Tro 6-5, PD 6-4, Def 11-2, Tra 7-2 |
| since 07:35 (v34) | **7-21**: Sch 1-7, Por 0-5, Sli 0-3, Dev 0-3, QoS 1-2, Tro 1-1, Aut 2-0, Tra 2-0 | 20-18: Sch 1-6, Sli 3-3, QoS 0-3, Dev 1-2, PD 1-2, Por 5-1, Tra 1-1, Tro 3-0, Def 3-0, Aut 2-0 |
Ranked series since 07:35: Stockfish L 2-3, L 2-3, L 2-3, L 0-5. ftm L 2-3, W 3-2.
## 2. Lost replays since 07:35 (Sch 13 L, Por 6 L, Sli 6 L, Dev 5 L, QoS 5 L)
- **Ending.** Sch, Por and Sli losses almost all went to round 500 and were decided on longest dragon (1 Sch game ended in elimination). Dev and QoS losses were eliminations at r109-486; we had 2-6 units at r100 against their 14-31.
- **Medians in losses, longest us/them (units us/them):**
  - Sch: r300 15/13 (45/61), r400 23/32, r450 29/47 (44/29), final 32/54 (9/29).
  - Sli: r300 20/16, r450 37/52, final 41/67.
  - Por: r300 **4/16**, r400 15/35, final 36/49.
  - On Sch and Sli we are level or ahead at r300 and lose the r300-500 race (Sch +17 vs +41).
- **Splitting.** On rich Sch games we sit at the 64-unit cap with about 800 splits, against their about 400. We also eat more (about 2400 vs 1500 pearls). But 6 of the 13 Sch losses were low-pearl games where we already trail by r100 (9-16 units against 13-23).
- **King timing (first round longest >=16).**
  - Por: us 366-427, Stockfish 277-324 in all 6 losses. ftm is late too, which is why we are 5-1 against them there.
  - Sch: ours comes earlier (median about 280 vs 316).
- **Portals.** Traversals are similar or higher for us (Por, early rounds: 303-401 vs 247-396), so portal use is not the gap.
- **Where our dragons died.** Most deaths are small (length 3 or less) self-kills:
  - Sch, r150+: 103 per game trapped with 0 free exits, against their 33.
  - Feeding: only 12% of our r300+ self-kills are within 3 tiles of our longest dragon (theirs 24%). Our king eats 18 of our own dropped pearls per game, theirs 36.
- **Big dragons rammed head-on (length >=8, Sch+Sli losses): us 50 dragons / 881 length lost, them 29 / 408.**
  - 12 of ours were our longest dragon, and 35 of 50 happened at r350 or later.
  - In Sli wins it was 1 vs 1. In Por losses there were none.
  - Their rammers were length 4-7 before the move, sprinting 3-5 steps (steps 3:18, 4:13, 5:6). All 50 were visible (Chebyshev <=3).
  - 39 of 50 were inside the reach our threat model already predicts (length-1, cap 4). 11 went beyond it through pearls or the cap.
  - Our rams on their big dragons were all 1-2 steps by length 2-4 dragons.
## 3. Actionable, general
1. **Keep dragons of length >=8 out of enemy sprint reach, as a hard rule.**
   - Code: `computeThreats` in variants/v34/main.cpp:2287. Reach is `max(1, visibleLen-1)`, capped at `KING_THREAT_REACH=4` (main.cpp:2321). In 39/50 rams we were already inside that reach, so the threat is only a soft penalty today.
   - bot/main.cpp already has `KING_SAFE_PRE` (kspOn at :2299, pearl-extended reach at about :2363), but it defaults to 0. Turn it on for all length >=8 dragons, not only Sch, and raise the cap and `KSP_PEARL_MAX` to cover 5-6 steps.
   - Expected effect: about 50 length per game back on Sch/Sli at r350+. That is the whole final gap: Sch 32 vs 54, Sli 41 vs 67.
2. **Mirror their offence: sprint-ram their big dragons with medium dragons.**
   - Code: `tryRam` (v34 main.cpp:2960, bot :3013) only rams at distance 1-2, with `RAM_MAX_OWN_LEN 3`.
   - Allow 3-5-step rams by length 4-7 dragons when the target is length >=8 and the target is at least 2x our length. Their 50 rams took 881 length for about 250 of their own.
- Map-specific, lower priority: the Portals king starts about 90 rounds after Stockfish's (`v2("Portals",250,360,300,3)`, v34 main.cpp:119). We lost 6/6 to Stockfish there with longest 4 vs 16 at r300.
