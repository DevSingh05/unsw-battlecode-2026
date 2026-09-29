import sys
p=sys.argv[1]; s=open(p).read()
a='        bool feeding = shouldFeed();\n        int target = feeding ? feedTarget() : -1;\n'
assert a in s
s=s.replace(a,a+'        if (dbg)\n            std::fprintf(dbg, "  FEEDDBG feeding=%d kingId=%d kingLen=%d kingTile=(%d,%d) age=%d target=%d units=%d kingSelf=%d iAmKing=%d myLen=%d nKings=%d\\n", (int)feeding, kingId, kingLen, kingTile%w.W, kingTile/w.W, round - kingRound, target, units, (int)kingSelf, (int)iAmKing(), myLen, freshKings(-1));\n')
open(p,'w').write(s)
# second patch: layout + rusher state on the R line
s = open(p).read()
b = 'std::fprintf(dbg, "R%d id=%d len=%d dir=%c head=(%d,%d) map=%s\\n", round, w.myId, myLen, DIRC[myDir],\n                                 myHead % w.W, myHead / w.W, w.known ? w.known->name : "?");'
assert b in s, 'R line not found'
s = s.replace(b, 'std::fprintf(dbg, "R%d id=%d len=%d dir=%c head=(%d,%d) map=%s schLayout=%d rusher=%d\\n", round, w.myId, myLen, DIRC[myDir],\n                                 myHead % w.W, myHead / w.W, w.known ? w.known->name : "?", schLayout, schRusher);')
open(p, 'w').write(s)
