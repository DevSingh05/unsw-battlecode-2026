# Pre-freeze synthesis (written 2026-09-30 17:42 UTC)
Freeze is 23:00 UTC (19:00 EDT), about 5h15m from now. The time comes from the public Sprint page (RULES.md #1) and matches the "6 hours" in the announcement.

## A. Ranked: turn it OFF now (mild recommendation; the user makes the call)
- Elo is scored per game with K≈5: change = 5·(W − n·E). Against a team 400 below us, 4-1 is −3 and 5-0 is +2 (ELO.md). The loss is real.
- Being challenged is about break-even with a selection bias against us. The reports disagree slightly: challenges since 10:53 were +9 over 39 battles (RULES), and since 14:00 −3 over 30 (ELO). Teams that beat expectation come back (SHINK ×8, −12; okbro ×5, −15).
- Risk shape: about 11 challenges/h × ~5h is ~55 more series. The expected value is about 0 to −6, with a typical swing of ±35. The top 7 are within 49 Elo, so the upside is roughly one place and the downside is about five.
- Docs [G]: the switch only controls requested battles, so autoscrims and seeding continue either way. It can only be flipped once every 8h, so switching OFF now keeps it off until about 01:45 UTC. That is harmless, because manual requests end at the freeze anyway. ELO.md's "turn back ON 30 min before the freeze" is not possible because of this cooldown.
- Cost: our own ranked requests are blocked. We have no reason to make any now.
- Side benefit: with ranked OFF, putting a test build live only risks the hourly :00 autoscrim, so A/B windows become cheap. Avoid :55-:10.
- Stakes check: 931 teams in a 1024 bracket means about 93 byes. The #2 vs #7 seed does not change bye status, only where in the bracket we meet the top teams. Do not over-invest in this.

## B. Bot: ship v34 as final
Key point: **every Sprint map is unseen** (RULES #4). Map-keyed flags (Trophy, Schooltime, Devil) cannot affect Sprint games. At most they help post-freeze autoscrims, and the pool may get new maps there too. Several forensic fixes also lost on the server today.
1. `-DPM_TROPHY_RG=2`. The evidence is forensic only (19 outnumbered rams per Trophy loss vs 5.3 per win), and self-play was 10/24. Only worth running if the user wants to use spare slots: a Trophy-only unranked A/B, 20 games per arm vs 1650-1950 teams. Ship only if it wins by ≥5 games. Low value.
2. Schooltime `RP.diveStopRound=360`, a one-line applyMapParams change (TOP5.md). Low confidence, since we also split late in games we win. It would need a Schooltime A/B vs the top 10, 20 per arm. Low value for the same unseen-maps reason.
3. Nothing else. The Devil left/right start bias (1-14 from the right vs the top 5; notes/19 agrees) is the only finding that might carry over to unseen maps, for example a direction tie-break. It is undiagnosed, and TOP5 found no consistent side bias on other maps. It is Qualifier work, not a pre-freeze change.
Before 23:00: confirm the active submission is v34 (a test build left live at the freeze would play the Sprint).

## C. Unknowns for the user to check (Discord or organisers)
- Is ranked-OFF really still paired in autoscrims, both before and after the freeze? The docs say yes. The journal (SSS/Cutlery) is inconclusive.
- The post-freeze constant K and the autoscrim rate ("continuously" vs hourly). This decides how much pre-freeze Elo matters.
- Will new or unseen maps be added to the post-freeze autoscrim pool?
- The challenge-range N (how far below you a ranked target can be) and the tie-break for equal ratings.
- The start time of each Sprint round (stream at 07:30 UTC Oct 1 = 03:30 EDT).
- Keep the Codex SERVER_LOCK convention if any A/B runs.
