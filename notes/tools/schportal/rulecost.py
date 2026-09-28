#!/usr/bin/env python3
"""Rule cost of candidate PORTAL_ECHO_GUARD refinements on our single-step crossings (notes/20).
For each rule: crossings it would forbid per game, how many of those were fatal / safe, safe ones with a
pearl on the exit, fatal ones with 0 safe alternatives (a hard block can't save those), blocked kings.
The replay of the live rule (v22 = mode 2, range 3) must block 0 crossings (sanity check).

usage (from project root): python3 notes/tools/schportal/rulecost.py ab_v22_Schooltime [ab_v22_Default ...]
"""
import collections
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import fatal, guard_inputs, short_path, guard  # noqa: E402


def echoes(r, solo):
    gi = guard_inputs(None, r)
    if not solo:
        return gi['heads'], gi['bodies'], gi
    w = gi['warn']
    h = sum(p['hitKind'] in ('allyHead', 'enemyHead') for p in w)
    b = sum(p['hitKind'] in ('ally', 'enemy') for p in w)
    return h, b, gi


def rule(m, r, rng=3, mode=2, solo=False, notself=False):
    """True if the rule forbids this crossing. mode 2: bodies need shortPath(rng); mode 3: any body echo."""
    if len(r['move']) > 1 or r['age'] == 0:
        return False
    pa = r['prev_act']
    if pa is None or pa[0] != r['round'] - 1 or pa[1] > 1:
        return False
    h, b, gi = echoes(r, solo)
    if r['dir'] not in gi['mask'] or r['sighted']:
        return False
    if notself and b > 0:
        # PORTAL_ECHO_SELFSKIP idea: own-body hits are predictable; count only rays not ending in our body
        w = gi['warn'] if solo else r['prevpings']
        b = sum(p['hitKind'] in ('ally', 'enemy') and p['hitId'] != r['id'] for p in w)
    if h > 0:
        return True
    if b > 0 and (mode >= 3 or short_path(m, r['exit'], r['dir'], rng)):
        return True
    return False


RULES = {
    'v22 live (mode2, range3)': dict(),
    'mode2 range5': dict(rng=5),
    'mode2 range8': dict(rng=8),
    'mode2 range15': dict(rng=15),
    'mode3 (any body echo)': dict(mode=3),
    'solo + mode2 range3': dict(solo=True),
    'solo + mode3': dict(solo=True, mode=3),
}


def main():
  for name in sys.argv[1:] or ['ab_v22_Schooltime']:
      common._M.clear()
      G, m = common.load(name)
      NG = len(G)
      base_f = sum(fatal(r) for g in G for r in g['recs'] if r['us'])
      base_c = sum(1 for g in G for r in g['recs'] if r['us'])
      print(f'== {name}: {NG} games, our crossings {base_c / NG:.1f}/g, fatal {base_f / NG:.1f}/g')
      for rn, kw in RULES.items():
          c = collections.Counter()
          for g in G:
              for r in g['recs']:
                  if not r['us']:
                      continue
                  if not rule(m, r, **kw):
                      continue
                  safe_alt = sum(1 for d, a in r['alts'].items() if d != r['dir'] and a['st'] == 'free')
                  c['blocked'] += 1
                  if fatal(r):
                      c['fatal'] += 1
                      c['fatal_noalt'] += safe_alt == 0
                      c['fatal_L8+'] += r['L'] >= 8
                  else:
                      c['safe'] += 1
                      c['safe_pearl_exit'] += r['exit_pearl']
                      c['safe_noalt'] += safe_alt == 0
          net = c['fatal'] - c['fatal_noalt']
          print(f'   {rn:28s} blocks {c["blocked"] / NG:6.1f}/g: fatal {c["fatal"] / NG:5.1f} (0-alt {c["fatal_noalt"] / NG:4.1f}, L>=8 {c["fatal_L8+"] / NG:4.1f})'
                f'  safe {c["safe"] / NG:6.1f} (pearl on exit {c["safe_pearl_exit"] / NG:4.1f}, 0-alt {c["safe_noalt"] / NG:4.1f})'
                f'  direct saves ~{net / NG:4.1f}/g  safe forbidden per save {c["safe"] / max(1, net):4.1f}')


if __name__ == '__main__':
    main()
