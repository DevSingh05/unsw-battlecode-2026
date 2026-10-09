# tools/analysis

Scripts behind the 3-7 Oct studies. They were written in scratch folders and copied here unchanged for reference, so
paths inside some of them still point at the session scratchpad or variants that are now archived. Adjust the path
constants at the top before rerunning.

| script | what it does | used for |
|---|---|---|
| `permap_model.py`, `permap_report.py`, `permap_flags.py` | Opponent-adjusted logistic model per map and build class (opponent ridge, map, ranked/autoscrim, time-local context). Prints per-map tables. | Per-map portfolio study (notes/newrules/PER_MAP.md) |
| `sandbox_mech.py`, `sandbox_mech_summary.py` | Paired `--sandbox` games of a candidate vs a reference on chosen maps and seeds; units, length at r50/100/200/300, longest at r500, rams, waste. | MIDSIZE, lane queen, crowd tests |
| `waste_ledger.py` | Self-inflicted length loss: ally-boxed deaths, stillborn children, HitSelf. | Dev-team study (notes/top5/DEVTEST1_OCT5.md) |
| `queen_mech.py`, `queen_rams.py` | Queen first split, length at r300/400/500, alive rounds, head-on rams on big units. | Park, crown, lane queen and QK_EG tests |
| `paired_mech.py`, `queen_deaths.py` | Earlier paired harness and queen death cause classifier. | Round 2 builder |
| `death_reasons.py`, `pearls_lying.py`, `length_hist.py` | Replay summaries: death reasons by class, pearls left uneaten, unit length distribution. | Coverage and economy studies |
| `stat_lone_queen.py`, `stat_split_sites.py`, `stat_threat_reach.py`, `approach_trace.py` | Round 2 mechanism stats: lone-queen kills, split sites, rams and threat reach, enemy approach paths. | Round 2 builder |
| `board_view.py`, `sum_results.py`, `economy_per_half.py`, `kill_detail.py` | Board snapshots, result summaries, per-half eating and kill details. | Various |
| `lane_queen_mech.py`, `lane_queen_summary.py` | Lane-map small-queen mechanism runs. | l1 study |
| `ident.sh` | Plays a build and a reference on the same maps and seeds (sandbox) and compares result lines: the flags-off identity check. | Every flag merged into bot/ |
| `idcheck.py` | Full-transcript identity: candidate vs base against base vs base on chosen maps, both sides, `--sandbox -v`, CPU/timing lines dropped. Prints MATCH/DIFF and the first differing line. | qf1/qf2 known-map identity (40/40) |
| `mkstage.sh` | Copies bot/ (no build cache) and forces `#define` lines at the top of params.hpp. | Every server candidate |

Server-side tools stay in `tools/` (`ab_server.py`, `ab_mech.py`, `decision_replay.py`, `auto_challenge.py`).
