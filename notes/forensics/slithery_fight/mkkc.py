#!/usr/bin/env python3
"""Build the KING_CONSENSUS sketch (REPORT.md RC1/RC2) on top of a copy of variants/v29/main.cpp for decision-level
checks only.  python3 .../mkkc.py IN.cpp OUT.cpp   (IN may be the mkdbg.py debug copy).  Nothing in bot/ changes."""
import sys
s = open(sys.argv[1]).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
# RC1a: kingId = longest king heard within KC_MEM rounds (a short fresh king can't replace it)
rep('''        // we can see the king ourselves: use exact data
        if (kingId >= 0)''', '''        {
            const KingInfo* bk = nullptr;
            for (auto& k : kingsSeen)
                if (round - k.round <= 12 && (!bk || k.len > bk->len))
                    bk = &k;
            if (bk && (bk->len >= kingLen || round - kingRound > 12))
            {
                if (bk->id != (kingId & 1023))
                {
                    haveRelay = round - bk->round <= 4; // relay the longest, not the last heard
                    relayMsg = encodeKing(bk->tile, bk->len, bk->id, 1, bk->dir, bk->round);
                }
                kingId = bk->id; kingLen = bk->len; kingTile = bk->tile; kingDir = bk->dir; kingRound = bk->round;
            }
        }
        // we can see the king ourselves: use exact data
        if (kingId >= 0)''')
# RC1b: step down for one clearly longer king; never crown yourself while a longer king is known
rep('''            if (kingSelf)
            {
                if (freshKings(myLen + 2) >= 2)
                    kingSelf = false;
                return;
            }
            if (round >= RP.kingSeedRound && freshKings(-1) < 2 && myLen >= 3 && rng.uni() < KING_DECLARE_P)
                kingSelf = true;''', '''            int best30 = 0;
            for (auto& k : kingsSeen)
                if (round - k.round <= 30)
                    best30 = std::max(best30, k.len);
            if (kingSelf)
            {
                if (freshKings(myLen + 2) >= 2 || best30 >= myLen + std::max(3, myLen / 4))
                    kingSelf = false;
                return;
            }
            if (round >= RP.kingSeedRound && freshKings(-1) < 2 && myLen >= 3 && best30 < myLen + 2 && rng.uni() < KING_DECLARE_P)
                kingSelf = true;''')
# RC2: feed only a king that is at least 3/4 of the longest king heard in the last 40 rounds
rep('''        if (KING_V2 && RP.kingDeclare)
            return FEED_ENABLE && feedPhase() && kingId >= 0 && kingLen >= myLen + 2 && !iAmKing() &&''', '''        int best40 = 0;
        for (auto& k : kingsSeen)
            if (round - k.round <= 40)
                best40 = std::max(best40, k.len);
        if (KING_V2 && RP.kingDeclare && kingLen * 4 < best40 * 3)
            return false;
        if (KING_V2 && RP.kingDeclare)
            return FEED_ENABLE && feedPhase() && kingId >= 0 && kingLen >= myLen + 2 && !iAmKing() &&''')
open(sys.argv[2], 'w').write(s)
