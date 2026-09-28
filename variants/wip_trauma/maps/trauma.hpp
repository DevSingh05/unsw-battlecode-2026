// Map-specific logic for "Trauma". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Trauma".
//
// Trauma is 48x24, xy symmetry (180 degree rotation): B's tile is (47-x, 23-y).
// Everything below is written in A's frame; traA() maps a real tile into it.
// Zones (A frame): home pen x 0-10 (only exits: (10,0)E<->(16,7)W and
// (10,20)E<->(26,22)W); hot factory = 1-wide dead end (11,8) S .. (11,14) E (12,14),
// entered only from (12,8) W; hot [1,1] tiles (11,10..14) and (12,14).
// See notes/maps/trauma.md.

#ifndef TRA_PENKING
#define TRA_PENKING 0 // T1: the (4,15) starter never splits and lives in the home pen
#endif
#ifndef TRA_FACTORY
#define TRA_FACTORY 0 // T2: scripted 4-round hot factory + opening rush
#endif
#ifndef TRA_PENFEED
#define TRA_PENFEED 0 // T3: factory-born L2-3 dragons walk into the pen and feed the king
#endif
#ifndef TRA_PF_START
#define TRA_PF_START 60
#endif
#ifndef TRA_PF_RES
#define TRA_PF_RES 16 // feeders only while the team has more units than this
#endif
#ifndef TRA_PF_DIST
#define TRA_PF_DIST 4 // feeders die anywhere within this distance of the king (0: only the KING_V2 spots)
#endif
#ifndef TRA_PF_ANY
#define TRA_PF_ANY 0 // feeders die anywhere inside the pen (A-frame x<=8), king or not
#endif
#ifndef TRA_MERGE
#define TRA_MERGE 0 // T4: late consolidation of maze dragons into the pen king
#endif
#ifndef TRA_MERGE_ROUND
#define TRA_MERGE_ROUND 400
#endif
#ifndef TRA_REENTER
#define TRA_REENTER 1 // factory: the last dragon out of a broken cycle loops back in (needs TRA_FACTORY)
#endif
#ifndef TRA_MOUTH_PEN
#define TRA_MOUTH_PEN 60.0 // factory: outsiders stepping (12,9)->(12,8) onto the mouth (needs TRA_FACTORY)
#endif
#ifndef TRA_PEN_EXIT0
#define TRA_PEN_EXIT0 150.0 // factory: leaving the pen through (10,0)E, which dead-ends on the mouth
#endif
#ifndef TRA_RECROWN
#define TRA_RECROWN 1 // with TRA_PENKING: any L>=8 dragon in the pen is kingSelf
#endif
#ifndef TRA_KDEPTH
#define TRA_KDEPTH 0 // with TRA_PENKING: survival look-ahead for a long pen king (0 = default only)
#endif
#ifndef TRA_KPULL_ALL
#define TRA_KPULL_ALL 1 // 1: every kingSelf dragon is pulled into the pen; 0: only the declared pen king
#endif

std::vector<int> traPenD, traExitD, traFacD;
std::vector<std::vector<int>> traRev;
bool traIsB = false;
int traTurns = 0;
bool traFacBorn = false;
bool traPenKingDeclared = false;
int traRusher = -1;   // 1: walk to the factory and enter it (opening rush / restart)
int traRushUntil = 80;

// real tile <-> A-frame tile (the map is its own inverse)
int traA(int t) const
{
    if (!traIsB || t < 0)
        return t;
    int x = t % w.W, y = t / w.W;
    return w.idx(w.W - 1 - x, w.H - 1 - y);
}
int traT(int x, int y) const { return traA(w.idx(x, y)); } // A-frame coords -> real tile
int traDA(int d) const { return traIsB ? (d + 2) % 4 : d; } // direction <-> A frame
bool traInPen(int t) const { return t >= 0 && traA(t) % w.W <= 10; }
bool traIs(int t, int x, int y) const { return t >= 0 && traA(t) == w.idx(x, y); }
bool traInFac(int t) const
{
    if (t < 0)
        return false;
    int a = traA(t), x = a % w.W, y = a / w.W;
    return (x == 11 && y >= 8 && y <= 14) || (x == 12 && y == 14);
}

void traBfs(std::vector<int>& D, const std::vector<int>& src)
{
    D.assign(w.N, INF);
    std::vector<int> q;
    for (int s : src)
    {
        D[s] = 0;
        q.push_back(s);
    }
    for (size_t i = 0; i < q.size(); i++)
        for (int u : traRev[q[i]])
            if (D[u] > D[q[i]] + 1)
            {
                D[u] = D[q[i]] + 1;
                q.push_back(u);
            }
}

void traInit()
{
    if (!traPenD.empty())
        return;
    traIsB = w.myTeam == 'B';
    traRev.assign(w.N, {});
    for (int u = 0; u < w.N; u++)
        for (int d = 0; d < 4; d++)
        {
            int v = step(u, d);
            if (v >= 0)
                traRev[v].push_back(u);
        }
    std::vector<int> src;
    for (int t = 0; t < w.N; t++)
        if (traInPen(t))
            src.push_back(t);
    traBfs(traPenD, src);
    // leave the pen by the (10,20) portal: the (10,0) one only leads down the 1-wide
    // corridor (16,7)..(12,8) into the factory mouth
    traBfs(traExitD, {traT(26, 22)});
    traBfs(traFacD, {traT(11, 9)});
}

bool traPenKing() const
{
#if TRA_PENKING
    if (TRA_KPULL_ALL)
        return kingSelf || (myLen >= 8 && traInPen(myHead));
    return (kingSelf && (traPenKingDeclared || traInPen(myHead))) || (myLen >= 8 && traInPen(myHead));
#else
    return false;
#endif
}

bool traFeeder() const
{
#if TRA_PENFEED
    return traFacBorn && round >= TRA_PF_START && myLen <= 3 && !traPenKing() && units > TRA_PF_RES && traRusher != 1;
#else
    return false;
#endif
}

bool traMerger() const
{
#if TRA_MERGE
    return round >= TRA_MERGE_ROUND && !traPenKing() && units > 4 && myLen >= 4;
#else
    return false;
#endif
}

// Our pen king as seen from here: the own-team head (not us) with the most
// visible segments, or the sonar king. Returns false if none is known.
bool traKing(int& kt, int& kd, int& kl) const
{
    kt = -1;
    int bestCnt = 0, bestId = -1;
    for (auto& s : segs)
        if (s.head && s.team == w.myTeam && s.id != w.myId)
        {
            int c = enemyVisibleLength(s.id);
            if (c > bestCnt)
            {
                bestCnt = c;
                bestId = s.id;
                kt = s.tile;
                kd = s.facing;
            }
        }
    if (kt >= 0)
    {
        kl = bestCnt;
        if (kingId >= 0 && (bestId & 1023) == (kingId & 1023))
            kl = std::max(kl, kingLen);
        return true;
    }
    if (kingId >= 0 && kingTile >= 0 && round - kingRound <= 3 && traInPen(kingTile))
    {
        kt = kingTile;
        kd = kingDir;
        kl = kingLen;
        return true;
    }
    return false;
}

bool traWrite(const std::string& s)
{
    out += s;
    pending.clear();
    return true;
}

// Return true after writing an action to `out` to override normal play this turn.
bool traumaOverride()
{
    traInit();
    if (myHead < 0)
        return false;
    traTurns++;
    if (traTurns == 1)
        traFacBorn = traInFac(myHead);
    int a = traA(myHead), ax = a % w.W, ay = a / w.W;
#if TRA_PENKING
    if (round <= 2 && myLen >= 4 && w.myId < 4 && ay == 15 && (ax == 4 || ax == 5))
    {
        kingSelf = true;
        traPenKingDeclared = true;
    }
    // a big dragon in the pen (e.g. the bulk of a king that reverse-split) keeps the
    // crown, so the normal split-at-4 rule doesn't peel it apart
    if (TRA_RECROWN && myLen >= 8 && traInPen(myHead) && round >= 3)
        kingSelf = true;
#endif
#if TRA_FACTORY
    if (!traInFac(myHead) && myLen >= 4 && static_cast<int>(trail.size()) >= myLen)
    {
        // no normal split whose child would start in the one-way corridor (16,7)..(12,8)
        // or the factory: it would walk into the traffic head-on
        int ta = traA(trail[myLen - 1]), cx = ta % w.W, cy = ta / w.W;
        bool spur = (cy == 8 && cx >= 12 && cx <= 16) || (cx == 15 && cy == 9) || (cx == 16 && cy == 9) ||
                    (cx == 16 && cy == 7) || traInFac(trail[myLen - 1]);
        if (spur && threatAt.size() == static_cast<size_t>(w.N))
            threatAt[myHead]++; // the split code skips threatened dragons
    }
    if (traInFac(myHead))
    {
        int fd = traDA(myDir); // facing in A frame
        auto mv = [&](int dA) -> bool {
            int d = traDA(dA);
            int t = step(myHead, d);
            if (t >= 0 && occId[t] >= 0 && freeT[t] > 1)
                return false; // someone in the way: let normal play handle it
            emitMove(d);
            return true;
        };
        if (ax == 12 && ay == 14)
        {
            // dead end: peel the tail off, or die here (leaves a pearl for the next one)
            if (myLen >= 4 && units < w.unitLimit)
            {
                int k = myLen >= 6 ? 2 : myLen - 2;
                pendingSplit = true;
                return traWrite("SPLIT " + std::to_string(k) + "\n");
            }
            emitMove(traDA(1));
            return true;
        }
        if (fd == 2 || (fd == 3 && ay == 8))
        {
            if (ay == 14)
                return mv(1);
            return mv(2);
        }
        if (fd == 0)
        {
            // normally at (11,10); anywhere on the way out if the cycle slipped
            if (ay <= 11 && myLen >= 4 && units < w.unitLimit - 1)
            {
                pendingSplit = true;
                return traWrite("SPLIT " + std::to_string(myLen - 2) + "\n");
            }
#if TRA_REENTER
            if (ay == 9 && round < 460)
            {
                // last one out (nobody behind us in the corridor): loop back round and restart it
                bool behind = false;
                for (int y = 10; y <= 12; y++)
                {
                    int u = traT(11, y);
                    if (occId[u] >= 0 && occId[u] != w.myId)
                        behind = true;
                }
                if (!behind)
                {
                    traRusher = 1;
                    traRushUntil = round + 45;
                }
            }
#endif
            if (ay == 8)
                return mv(1);
            return mv(0);
        }
    }
#endif
#if TRA_PENFEED || TRA_MERGE
    if ((traFeeder() || traMerger()) && traInPen(myHead) && trail.size() >= 2 &&
        trail[1] == w.plainStep(myHead, (myDir + 2) % 4))
    {
        if (TRA_PF_ANY && traFeeder() && ax <= 8)
        {
            // die as soon as we're inside: the king collects the pearl later, and the
            // pen stays uncrowded
            bool enemyNear = false;
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, myHead) <= 4)
                    enemyNear = true;
            if (!enemyNear)
            {
                emitMove((myDir + 2) % 4);
                return true;
            }
        }
        int kt, kd, kl;
        if (traKing(kt, kd, kl) && kl >= myLen + 2 && kl >= 5)
        {
            int a1 = step(kt, kd), a2 = a1 >= 0 ? step(a1, kd) : -1;
            int sl = step(kt, (kd + 3) % 4), sr = step(kt, (kd + 1) % 4);
            bool spot = myHead == a1 || myHead == a2 || myHead == sl || myHead == sr;
            if (TRA_PF_DIST > 0)
                spot = wrapDist(myHead, kt) <= TRA_PF_DIST && !traIs(myHead, 10, 0) && !traIs(myHead, 10, 20);
            bool enemyNear = false;
            for (auto& o : segs)
                if (o.head && o.team != w.myTeam && wrapDist(o.tile, kt) <= 4)
                    enemyNear = true;
            if (spot && !enemyNear)
            {
                emitMove((myDir + 2) % 4); // into our own neck: the king eats what we leave
                return true;
            }
        }
    }
#endif
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double traumaScore(int t, int d)
{
    traInit();
    if (myHead < 0 || t < 0)
        return 0.0;
    double s = 0;
    const int ta = traA(t), tx = ta % w.W, ty = ta / w.W;
    const int ha = traA(myHead), hx = ha % w.W, hy = ha / w.W;
    const bool inP = traInPen(myHead), toP = traInPen(t);
    auto diff = [&](const std::vector<int>& D) -> double {
        if (D[myHead] >= INF || D[t] >= INF)
            return 0.0;
        return static_cast<double>(D[myHead] - D[t]);
    };
    const bool pk = traPenKing();
    const bool fe = traFeeder(), mg = traMerger();
#if TRA_PENKING
    if (pk)
    {
        if (inP && !toP)
            s -= 400.0;
        if ((tx == 10 && ty == 0) || (tx == 10 && ty == 20))
            s -= 120.0;
        else if ((tx == 9 && ty == 0) || (tx == 10 && ty == 1) || (tx == 9 && ty == 20) || (tx == 10 && ty == 19) ||
                 (tx == 10 && ty == 21))
            s -= 50.0;
        if (!inP)
            s += 6.0 * diff(traPenD);
        if (TRA_KDEPTH > 0 && myLen >= 14)
        {
            // a long king coils up in the pen's corners: look further ahead than the default 12
            int want = std::min(myLen, TRA_KDEPTH);
            int got = surviveDepth(t, want);
            if (got < want)
                s -= 150.0 + 20.0 * (want - got);
        }
    }
    else if (round < RP.feedStart && !fe && !mg && traRusher != 1)
    {
        // keep the pen's pearls for the king
        if (!inP && toP)
            s -= 60.0;
        if (inP)
            s += 3.0 * diff(traExitD);
    }
#endif
#if TRA_PENFEED || TRA_MERGE
    if (fe || mg)
    {
        double wgt = fe ? 8.0 : 5.0;
        if (!inP)
        {
            s += wgt * diff(traPenD);
            if (toP && t != w.plainStep(myHead, d))
            {
                // crossing blind into the pen: don't queue up with another ally
                for (auto& o : segs)
                    if (o.head && o.team == w.myTeam && o.id != w.myId && wrapDist(o.tile, myHead) <= 2)
                        s -= 40.0;
            }
        }
        else
        {
            int kt, kd, kl;
            if (traKing(kt, kd, kl) && kl >= myLen + 2)
            {
                int a1 = step(kt, kd), a2 = a1 >= 0 ? step(a1, kd) : -1;
                int tgt = a2 >= 0 ? a2 : a1;
                if (tgt >= 0 && tgt < static_cast<int>(bfsDist.size()))
                    s -= wgt * std::min(bfsDist[tgt], 40);
            }
        }
    }
#endif
#if TRA_FACTORY
    {
        if (traRusher < 0)
            traRusher = (round <= 3 && w.myId < 4 && hy <= 3 && hx <= 6) ? 1 : 0;
        if (traRusher == 1 && (traFacD[myHead] <= 1 || round > traRushUntil))
            traRusher = 0;
        if (traRusher == 1)
            s += 8.0 * diff(traFacD);
        auto occ = [&](int x, int y) { return occId[traT(x, y)] >= 0; };
        if (hx == 12 && hy == 8 && tx == 11 && ty == 8)
        {
            bool busy = occ(11, 8) || occ(11, 9) || occ(11, 10) || occ(11, 11);
            if (busy)
            {
                s -= 500.0;
                if (traRusher == 1 && !traInFac(myHead))
                    traRusher = 0; // someone else restarted it
            }
            else if ((myLen <= 3 || traRusher == 1) && units <= 60 && round < 470 && !pk && !fe && !mg)
                s += 40.0;
        }
        if (traRusher != 1 && !fe && !mg && hx == 12 && hy == 9 && tx == 12 && ty == 8)
            s -= TRA_MOUTH_PEN; // keep random traffic off the factory mouth
        if (traRusher != 1 && hx == 10 && hy == 0 && tx == 16 && ty == 7)
            s -= TRA_PEN_EXIT0; // one-way: maze -> pen through (16,7); out through (10,20)
        if (!traInFac(myHead) && ((tx == 12 && ty == 8) || (tx == 13 && ty == 8 && hx == 14)))
        {
            // keep the factory mouth clear for a dragon on its way out
            for (int y = 8; y <= 10; y++)
            {
                int u = traT(11, y);
                int j = segAt[u];
                if (j >= 0 && segs[j].head && segs[j].id != w.myId && traDA(segs[j].facing) == 0)
                    s -= 40.0;
            }
        }
    }
#endif
    if (dbg)
        std::fprintf(dbg, "  tra t=(%d,%d) s=%.1f rusher=%d fe=%d pk=%d facBorn=%d\n", tx, ty, s, traRusher, (int)fe, (int)pk, (int)traFacBorn);
    (void)d;
    (void)hx;
    (void)hy;
    (void)tx;
    (void)ty;
    (void)inP;
    (void)toP;
    (void)pk;
    (void)fe;
    (void)mg;
    return s;
}
