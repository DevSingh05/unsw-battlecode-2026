"""Prototype patch (scratch copies only): KING_MERGE_STEPDOWN. After KING_V2_MERGE_ROUND a self-declared
king steps down as soon as ONE fresh king >= myLen+2 is heard (KING_V2 needs two)."""
import sys
p = sys.argv[1]; s = open(p).read()
a = """            if (kingSelf)
            {
                if (freshKings(myLen + 2) >= 2)
                    kingSelf = false;
                return;
            }"""
assert a in s
s = s.replace(a, """            if (kingSelf)
            {
                if (freshKings(myLen + 2) >= 2 || (round >= KING_V2_MERGE_ROUND && freshKings(myLen + 2) >= 1))
                    kingSelf = false;
                return;
            }""")
open(p, 'w').write(s)
