// Map-specific logic for "Stripes" (Sprint map). Included inside struct Bot.
// R3 STRIPES_LOOP (ROUND2 backlog, default 0): the queen walks to the free 8-tile centre loop of her own stripe
// and laps it (one every-round pearl + one 1-10 pearl per lap, no dead end), like the top-5 queens do from r9-13.
// The far W-vault dive that the queen used to make at r9-13 is handed to another unit (STRIPES_LOOP mode):
//   1 = the second starter dives the W vault (first eat ~r12) instead of the near Y vault
//   2 = the second starter is untouched; the queen's first loop child (born by STRIPES_KID_R) walks to the W vault
// Does nothing unless the recognised map is "Stripes" and STRIPES_LOOP != 0.
// Coordinates are in the frame of the top-right spawn (21,1); the bottom-left spawn rotates 180 degrees.
std::vector<int> stDLoop, stDW; // BFS steps to the loop / into the W vault
int stRole = -1;                // -1 undecided, 0 none, 1 lapper (queen), 2 W diver
int stCyc[8] = {0, 0, 0, 0, 0, 0, 0, 0};
int stPos[4] = {-1, -1, -1, -1}; // my head tile -> index on the loop (tiny cache, per turn)

bool stripesOn() const { return STRIPES_LOOP && w.known && std::strcmp(w.known->name, "Stripes") == 0 && w.W == 24 && w.H == 12; }

void stripesInit()
{
    static constexpr int CYC[8][2] = {{13, 0}, {12, 1}, {11, 1}, {11, 0}, {12, 0}, {13, 1}, {14, 1}, {14, 0}};
    bool rot = (myHead % w.W) < 12; // spawned / born in the left half: bottom-left team
    if (birthRound != 0)
    {
        // a child: the frame is the one whose loop it is born on (only used for STRIPES_LOOP 2)
        rot = (myHead / w.W) >= 6;
    }
    auto T = [&](int x, int y) { return rot ? w.idx(23 - x, 11 - y) : w.idx(x, y); };
    for (int i = 0; i < 8; i++)
        stCyc[i] = T(CYC[i][0], CYC[i][1]);
    std::vector<std::vector<int>> rev(w.N);
    for (int u = 0; u < w.N; u++)
        for (int d = 0; d < 4; d++)
        {
            int v = step(u, d);
            if (v >= 0)
                rev[v].push_back(u);
        }
    auto bfs = [&](std::vector<int>& D, std::vector<int> q) {
        D.assign(w.N, 1 << 20);
        for (int s : q)
            D[s] = 0;
        for (size_t i = 0; i < q.size(); i++)
            for (int u : rev[q[i]])
                if (D[u] > D[q[i]] + 1)
                {
                    D[u] = D[q[i]] + 1;
                    q.push_back(u);
                }
    };
    // the lapper joins the loop on its open side (the 2x2 box is only reachable through the loop's portal)
    bfs(stDLoop, {stCyc[7], stCyc[0]});
    bfs(stDW, {T(3, 0)});
    stRole = 0;
    if (amQueen() && birthRound == 0)
        stRole = 1;
    else if (STRIPES_LOOP == 1 && birthRound == 0 && round <= 3)
        stRole = 2;
    else if (STRIPES_LOOP == 2 && birthRound > 0 && birthRound <= STRIPES_KID_R && w.myId <= 7)
    {
        for (int i = 0; i < 8; i++)
            if (stCyc[i] == myHead)
                stRole = 2;
    }
}

// Extra score for moving onto tile t (direction d). Added to the normal score.
double stripesScore(int t, int d)
{
    (void)d;
    if (stRole == -1)
        stripesInit();
    if (stRole == 0)
        return 0.0;
    if (stRole == 2)
    {
        // W diver: walk into the far vault; once inside (or late) the normal pocket logic takes over
        if (stDW[myHead] == 0 || round - birthRound > STRIPES_DIVE_T || stDW[myHead] >= (1 << 20))
        {
            stRole = 0;
            return 0.0;
        }
        return STRIPES_LOOP_W * (stDW[myHead] - std::min(stDW[t], stDW[myHead] + 1));
    }
    if (round >= STRIPES_LOOP_R)
        return 0.0;
    int i = -1;
    for (int k = 0; k < 8; k++)
        if (stCyc[k] == myHead)
            i = k;
    if (i >= 0)
    {
        if (t == stCyc[(i + 1) & 7])
            return STRIPES_LOOP_W;
        return 0.0;
    }
    if (stDLoop[myHead] >= (1 << 20))
        return 0.0;
    return STRIPES_LOOP_W * (stDLoop[myHead] - std::min(stDLoop[t], stDLoop[myHead] + 1));
}

// the queen while she is on the loop (her own split rule applies, the generic growth split does not)
bool stripesLapper()
{
    if (stRole == -1)
        stripesInit();
    if (stRole != 1 || round >= STRIPES_LOOP_R)
        return false;
    for (int k = 0; k < 8; k++)
        if (stCyc[k] == myHead)
            return true;
    return false;
}

// split 2 off the tail when she is long enough and the tail (= the child's head) is on the open side of the loop,
// so the child is born outside the 2x2 box with a way out that is not the loop itself
bool stripesLapSplit()
{
    if (myLen < STRIPES_SPLIT_L || units >= w.unitLimit || static_cast<int>(trail.size()) < myLen)
        return false;
    int tail = trail[myLen - 1];
    return tail == stCyc[5] || tail == stCyc[6] || tail == stCyc[7] || tail == stCyc[0];
}

// t is the lapping queen's next tile on the loop
bool stripesLapNext(int t)
{
    if (!stripesLapper())
        return false;
    for (int k = 0; k < 8; k++)
        if (stCyc[k] == myHead)
            return t == stCyc[(k + 1) & 7];
    return false;
}
