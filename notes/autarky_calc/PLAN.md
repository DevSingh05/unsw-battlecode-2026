# Autarky vs calc: forensics plan (synthesis output, saved by main agent)

I did not write `notes/autarky_calc/PLAN.md`: a harness rule blocks subagents from writing report `.md` files, the same thing that stopped both track reports. The plan is below. Everything else is in place: the patched copy of `bot/`, `fix.diff`, the check scripts and the replays.

**Why the dragons bunch at the mouth**
1. **The dive splits one tile too early.** An L4 dragon one tile before the tip does the normal `SPLIT 2`. The L2 child leaves and the L3 parent dies inside. That nets +0.2 length per dive against calc's +0.9, so the queue outside is waiting for a dive that makes no length.
2. **The child is born facing out, and nobody else wants the pocket.** It is born on the mouth tile and can't turn back into its own neck. Heads 4-6 steps away value the pocket at 0.3-1.0, about the size of the random noise, because pearl value drops with distance and again when another head is closer. So they circle. calc does the same thing 3-6x as often; it isn't a veto bug.
3. **We walk off full pockets.** The "POCKET enemy" check turns us away when any enemy head is within 3. That was 13 of the 20 times we stood on a mouth and didn't enter, and those were the rounds where calc took our home pockets. calc enters 75-81% of the time at every enemy distance.
4. **A pocket we do want still loses the vote.** The distance-discounted pearl sum makes 3 certain pearls in a 4-tile dead end score lower than open ground (6 of the 20).

**Fixes** (`notes/autarky_calc/fix/src/`, all new flags default 0, all compile). None use map names; each works from local geometry and nearby heads.
- **`PUMP_TIP2=1`** (`_REGION 6`, `_MAXLEN 7`): when the head is inside a 1-wide kelp dead end of 6 tiles or fewer, and the tail can get out, an L4-7 dragon keeps eating toward the tip. With nothing left ahead it splits k=L-2, so the tail-end child takes most of the body out.
- **`POCKET_ENEMY_LOCAL=2`**: the enemy check only fires when an enemy head is next to the entry tile, or when enemy heads within 3 outnumber ours.
- **`POCKET_CERTAIN=3.0`**: a pocket move that passes the check scores +3 per pocket pearl.

**Mechanism check** (`fix/mech.py` and `fix/mechdiff.py`). I re-ran the reconstructed inputs for all 145 of our dragons in the 4 losses. The flags-off baseline matches the real games on 99.3-99.9% of turns, same as v29.
- **`PUMP_TIP2`:** changed 120 decisions, all early `SPLIT 2` into moving deeper, all inside the 4 pockets. In the user's scene (625768 r102), dragon 17 moves S instead of splitting at (35,16).
- **`POCKET_ENEMY_LOCAL`:** changed 12 turns from walking away to entering, including every known takeover moment: 612737 r22 and r95, 617872 r148, r152 and r238, 608221 r107, 625768 r196, r212 and r248.
- **`POCKET_CERTAIN`:** changed 4 turns to entering, including u171 at 625768 r161.

**Local games on Autarky** (6 single games): net length per dive went from +0.02-0.32 to about +1.0, calc's level.
- Tip fix alone, playing side B: ahead on total length at r499 in both games (65 v 54, 71 v 49).
- All three fixes together: ahead as side A in 1 of 2 games (65 v 47; 47 v 58 in the other), but behind as side B in both. In one of those it was wiped out by r373.
- So two games point at the enemy-check relaxation as a risk.

**Test plan**
1. Local run of `PUMP_TIP2=1` against the baseline on all known maps plus the unseen sets. It changes nothing outside kelp dead ends, so the other maps should come out even.
2. Server A/B on Autarky against calc and the top 10 (at least 10 games): baseline vs `+PUMP_TIP2`. Judge it with `jam/cycles.py` (target: at least +0.6 net per dive, more dives) and `calc/owner.py` (our pocket-round share, currently 15-26%).
3. If step 2 is positive, run a second A/B adding `POCKET_ENEMY_LOCAL=2` and `POCKET_CERTAIN=3`. Judge it with `calc/entrygate.py`, `owner.py` and `corpse2.py`, and ship only if it gains against calc.
4. Next lever after that: more of our heads at the mouths and in calc's half, since calc holds 2-5x our pocket-rounds and we have about 0 heads in its half.

Files are in `/Users/devsingh/Developer/UNSW_Battlecode/notes/autarky_calc/`:
- `fix.diff`
- `fix/src/`
- `fix/mech.py`
- `fix/mechdiff.py`
- `fix/selfcycles.py`
- `fix/mech_*.pkl`
- `fix/games/*.replay`
