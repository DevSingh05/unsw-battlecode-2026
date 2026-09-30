#!/usr/bin/env python3
"""Make a debug copy of variants/v29/main.cpp (argv[1] = output path) that prints the feed/king state each turn
(FEEDDBG line) plus the KING line when kingship changes. Behaviour is unchanged (only fprintf to BOTDBG)."""
import sys
src = open(sys.argv[2]).read()
a = '''        bool feeding = shouldFeed();
        int target = feeding ? feedTarget() : -1;
'''
assert a in src
add = r'''        if (dbg)
        {
            std::fprintf(dbg, "  FEEDDBG feeding=%d kingId=%d kingLen=%d kingTile=(%d,%d) age=%d target=%d units=%d kingSelf=%d iAmKing=%d myLen=%d nKings=%d seen=", (int)feeding, kingId, kingLen, kingTile >= 0 ? kingTile % w.W : -1, kingTile >= 0 ? kingTile / w.W : -1, round - kingRound, target, units, (int)kingSelf, (int)iAmKing(), myLen, freshKings(-1));
            for (auto& k : kingsSeen)
                std::fprintf(dbg, "[%d L%d age%d]", k.id, k.len, round - k.round);
            std::fprintf(dbg, "\n");
        }
'''
open(sys.argv[1], 'w').write(src.replace(a, a + add))
