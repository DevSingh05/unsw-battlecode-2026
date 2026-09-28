// Map-specific logic for "Slithery Fight". Included inside struct Bot, so it can use
// every Bot member (myHead, myLen, round, units, segs, step(), w, trail, ...).
// Only called when the recognised map is "Slithery Fight".
//
// 63x27, xy symmetry: B's tile = (62-x, 26-y). Zones below are written in A's frame.
// Analysis: notes/maps/slithery_fight.md. Every idea is behind its own flag, off by default.

#ifndef SLI_TRAIL_FIX
#define SLI_TRAIL_FIX 0 // U-turn children: survival DFS with the unseen part of the body padded in
#endif
#ifndef SLI_SS
#define SLI_SS 0 // split-stop round override (0 = keep RP; research value 420)
#endif
#ifndef SLI_COMB
#define SLI_COMB 0 // big dragons avoid the comb cups, staircase corners, hot pockets, portal tube
#endif
#ifndef SLI_RAMZONE
#define SLI_RAMZONE 0 // big dragons / king softly avoid B's feeding ground
#endif
#ifndef SLI_RAMZONE_W
#define SLI_RAMZONE_W 15.0
#endif
#ifndef SLI_RAMZONE_KEEP
#define SLI_RAMZONE_KEEP 0 // also keep 5 (not 4) tiles from enemy heads
#endif
#ifndef SLI_STALEKING
#define SLI_STALEKING 0 // trust our own eyes over sonar for the king's length (stops U-turn children
#endif                  // from feed-suiciding into their L2 parent that still carries the king's id)
#ifndef SLI_CROWN
#define SLI_CROWN 0 // a fresh big split child takes the crown (the parent drops it on a U-turn split)
#endif
#ifndef SLI_COMB_W
#define SLI_COMB_W 40.0
#endif
#ifndef SLI_POCKET_W
#define SLI_POCKET_W 80.0
#endif

int sliBorn = -1; // round this process first ran (split children start late)

// tile -> A-frame coordinates
void sliFrame(int t, int& x, int& y) const
{
    x = t % w.W;
    y = t / w.W;
    if (w.myTeam == 'B')
    {
        x = 62 - x;
        y = 26 - y;
    }
}

// surviveDepth() for a body whose trail is incomplete (a fresh reverse-split child sees only
// part of its chain): simulate the full myLen body, the unseen part as "unknown" slots that
// never block and never free. Known tile i then frees only after myLen - i moves.
int sliSurviveDepthFull(int firstTile, int maxDepth)
{
    if (static_cast<int>(bodyCnt.size()) != w.N)
        bodyCnt.assign(w.N, 0);
    if (static_cast<int>(eatenMark.size()) != w.N)
        eatenMark.assign(w.N, 0);
    const int LT = static_cast<int>(trail.size());
    if (LT == 0)
        return maxDepth;
    int L = std::max(LT, myLen);
    const int cap = L + maxDepth + 4;
    simBody.assign(cap, -1);
    int h = 0;
    for (int i = 0; i < L; i++)
    {
        simBody[i] = i < LT ? trail[i] : -2;
        if (i < LT)
            bodyCnt[trail[i]]++;
    }
    int best = 0;
    nodes = 0;
    struct Frame
    {
        int tile, dir, tailTile; // -1: ate (tail stayed), -2: unknown tail slot moved
    };
    std::vector<Frame> stack;
    auto canEnter = [&](int v, int t) {
        if (v < 0 || bodyCnt[v] > 0)
            return false;
        return freeOther[v] <= t;
    };
    auto eats = [&](int v) {
        if (!DFS_EATS || eatenMark[v])
            return false;
        return (visible[v] && w.pearlMem[v]) || (w.gmax[v] == 1 && w.gmin[v] == 1);
    };
    auto push = [&](int v) {
        h = (h - 1 + cap) % cap;
        simBody[h] = v;
        bodyCnt[v]++;
        if (eats(v))
        {
            eatenMark[v] = 1;
            L++;
            return -1;
        }
        int tailIdx = (h + L) % cap;
        int tail = simBody[tailIdx];
        if (tail == -2)
            return -2;
        bodyCnt[tail]--;
        return tail;
    };
    auto pop = [&](int tail) {
        if (tail == -1)
        {
            eatenMark[simBody[h]] = 0;
            L--;
        }
        else
        {
            int tailIdx = (h + L) % cap;
            simBody[tailIdx] = tail;
            if (tail >= 0)
                bodyCnt[tail]++;
        }
        bodyCnt[simBody[h]]--;
        h = (h + 1) % cap;
    };
    auto cleanup = [&]() {
        while (!stack.empty())
        {
            pop(stack.back().tailTile);
            stack.pop_back();
        }
        for (int i = 0; i < LT; i++)
            bodyCnt[trail[i]]--;
    };
    if (!canEnter(firstTile, 1))
    {
        for (int i = 0; i < LT; i++)
            bodyCnt[trail[i]]--;
        return 0;
    }
    stack.push_back({firstTile, 0, push(firstTile)});
    best = 1;
    while (!stack.empty())
    {
        Frame& f = stack.back();
        int depth = static_cast<int>(stack.size());
        if (depth >= maxDepth || f.dir >= 4 || nodes > 60000)
        {
            if (depth >= maxDepth || nodes > 60000)
            {
                best = std::max(best, depth);
                if (depth >= maxDepth)
                    break;
            }
            pop(f.tailTile);
            stack.pop_back();
            continue;
        }
        int d = f.dir++;
        int v = step(f.tile, d);
        if (!canEnter(v, depth + 1))
            continue;
        nodes++;
        int tail = push(v);
        stack.push_back({v, 0, tail});
        best = std::max(best, depth + 1);
    }
    cleanup();
    return best;
}

// Best survival depth of a child of length k split off our tail (head = our tail, body reversed).
// Our remaining head part is treated as a wall.
int sliChildDepth(int k, int want)
{
    int n = static_cast<int>(trail.size());
    if (n < myLen || k < 1 || k > myLen)
        return 0;
    std::vector<int> saved = trail;
    std::vector<int> rev;
    for (int i = myLen - 1; i >= myLen - k; i--)
        rev.push_back(saved[i]);
    std::vector<std::pair<int, int>> blocked;
    for (int i = 0; i < myLen - k; i++)
    {
        blocked.push_back({saved[i], freeOther[saved[i]]});
        freeOther[saved[i]] = 1000000;
    }
    trail = rev;
    int best = 0;
    int tail = rev[0];
    for (int d = 0; d < 4 && best < want; d++)
    {
        int v = step(tail, d);
        if (v < 0)
            continue;
        best = std::max(best, surviveDepth(v, want));
    }
    trail = saved;
    for (int i = static_cast<int>(blocked.size()) - 1; i >= 0; i--)
        freeOther[blocked[i].first] = blocked[i].second;
    return best;
}

bool slitheryfightOverride()
{
    if (SLI_SS > 0)
        RP.splitStopRound = SLI_SS;
    if (SLI_RAMZONE && SLI_RAMZONE_KEEP)
        RP.kingKeepExtra = 1;
    if (sliBorn < 0)
        sliBorn = round;
    if (SLI_STALEKING && kingId >= 0)
    {
        // a fresh split child (first turns of its process) can't tell a real king from its own
        // just-split parent, which sonar still reports at the old length: never feed then
        if (myLen >= 8 && round - sliBorn < 3 && round > 5)
            kingLen = 0;
        // a visible head whose whole chain is in view has an exact length (freeT = len + 2).
        // After a king reverse-splits, the parent (now L2) keeps the id and sonar still says
        // L30+, so the child (holding the body) would otherwise "feed" itself to its parent.
        for (auto& sg : segs)
            if (sg.head && sg.team == w.myTeam && sg.id != w.myId && (sg.id & 1023) == (kingId & 1023))
            {
                int f = freeT[sg.tile];
                if (f >= 2 && f < 100000)
                    kingLen = f - 2;
            }
    }
    if (SLI_CROWN && RP.kingDeclare && !kingSelf && myLen >= 12 && round - sliBorn < 3 && round > 5 &&
        round >= RP.kingSeedRound)
        kingSelf = true;
    if (SLI_TRAIL_FIX && myHead >= 0 && myLen >= 12 && static_cast<int>(trail.size()) >= myLen && units < w.unitLimit)
    {
        // a trapped big dragon is about to reverse-split (SPLIT myLen-2); if that child is
        // doomed too, split in half instead so the shorter child can get out
        bool trapped = true;
        for (int d = 0; d < 4 && trapped; d++)
        {
            int t = step(myHead, d);
            if (t >= 0 && surviveDepth(t, 4) >= 4)
                trapped = false;
        }
        if (trapped && tailHasExit(myLen - 2))
        {
            int k1 = myLen - 2;
            int want1 = std::min(k1, 16);
            if (sliChildDepth(k1, want1) < want1)
            {
                int k2 = myLen / 2;
                int want2 = std::min(k2, 16);
                if (k2 >= 2 && sliChildDepth(k2, want2) >= want2)
                {
                    out += "SPLIT " + std::to_string(k2) + "\n";
                    pending.clear();
                    pendingSplit = true;
                    kingSelf = false;
                    if (dbg)
                        std::fprintf(dbg, "  -> sli half split %d\n", k2);
                    return true;
                }
            }
        }
    }
    return false;
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double slitheryfightScore(int t, int d)
{
    double s = 0;
    int x, y;
    sliFrame(t, x, y);
    int dA = w.myTeam == 'B' ? (d + 2) % 4 : d;

    if (SLI_TRAIL_FIX && myLen >= 12 && static_cast<int>(trail.size()) < myLen && !trail.empty())
    {
        int want = std::min(myLen, 24);
        int dep = sliSurviveDepthFull(t, want);
        if (dep < want)
            s -= 150.0 + 40.0 * (want - dep);
        // the unseen rest of our body lies beyond the last known chain tile
        if (!visible[t] && wrapDist(t, trail.back()) <= 2)
            s -= 60.0;
    }

    if (SLI_COMB && myLen >= 12)
    {
        if (y <= 2 && x >= 19 && x <= 33)
            s -= SLI_COMB_W;
        static const int stair[][2] = {{18, 3}, {19, 3}, {17, 4}, {16, 4}, {15, 5}, {16, 5}, {14, 6}, {19, 2}, {20, 2}};
        for (auto& p : stair)
            if (p[0] == x && p[1] == y)
                s -= SLI_COMB_W;
        bool pocket = (x == 8 && y >= 8 && y <= 10) || (x == 8 && y >= 16 && y <= 18) || (x == 33 && y <= 2) ||
                      (y == 5 && (x == 31 || x == 32)) || (y == 7 && x >= 16 && x <= 18) || (y == 7 && x >= 21 && x <= 23);
        if (pocket)
            s -= SLI_POCKET_W;
        int hx, hy;
        sliFrame(myHead, hx, hy);
        if ((hx == 4 && hy == 14 && dA == 1) || (hx == 5 && hy == 14 && dA == 3))
            s -= SLI_POCKET_W;
    }

    if (SLI_RAMZONE && (myLen >= 15 || kingSelf))
    {
        if (x >= 34 || (y >= 19 && x >= 18))
            s -= SLI_RAMZONE_W;
    }
    return s;
}
