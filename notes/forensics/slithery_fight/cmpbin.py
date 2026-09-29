#!/usr/bin/env python3
"""Decision-level A/B (no games): run two binaries on the same reconstructed inputs and print both decision blocks.
    python3 .../cmpbin.py BIN_A BIN_B GAME:ID:R_FROM:R_TO [...]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx
a, b = sys.argv[1], sys.argv[2]
for spec in sys.argv[3:]:
    g, i, r0, r1 = map(int, spec.split(':'))
    for bn in (a, b):
        o = fx.run(bn, g, i, r0, r1)
        keep = [l for l in o.splitlines() if l.startswith('real') or ' cand ' in l or '->' in l]
        print('%s %s\n   ' % (spec, os.path.basename(bn)) + '\n   '.join(keep))
