// Map-specific logic for "Queen Of Spades" (all ideas off by default; see notes/maps/queen_of_spades.md).
// 25x35, xy symmetry: rot(x,y) = (24-x, 34-y). Two sealed "spade rooms" (16 tiles, gap [1,50]):
//   bottom room x6-11 y31-33, reachable only through the portal edge (3,3)|(4,3) <-> (8,33)|(9,33)
//   top room    x13-18 y1-3,  reachable only through (20,31)|(21,31) <-> (16,1)|(15,1)
// Bottom-room doors (top room = rotated):
//   IN : (4,3) move W -> (8,33), then forced N to (8,32)
//   OUT: (9,33) move W -> (3,3), then forced N to (3,2)
// See notes/maps/queen_of_spades.md.

#ifndef QOS_NECK
#define QOS_NECK 1 // Q1: a split child whose neck is across a portal never steps back through it
#endif
#ifndef QOS_DOOR_NOSPLIT
#define QOS_DOOR_NOSPLIT 0 // Q2: no split while any of our segments is on a door tile
#endif
#ifndef QOS_ONEWAY
#define QOS_ONEWAY 1 // Q3: one-way doors + keep landing lanes clear
#endif
#ifndef QOS_ONEWAY_PEN
#define QOS_ONEWAY_PEN 150.0
#endif
#ifndef QOS_LANE_PEN
#define QOS_LANE_PEN 30.0
#endif
#ifndef QOS_SPACING
#define QOS_SPACING 4 // Q3b (use 4 when on): don't follow another of ours through the IN door within this many rounds
#endif
#ifndef QOS_SPACE_PEN
#define QOS_SPACE_PEN 80.0
#endif
#ifndef QOS_GATE
#define QOS_GATE 1 // Q4a: only ids with id%QOS_GATE_MOD==0 may enter a room
#endif
#ifndef QOS_GATE_MOD
#define QOS_GATE_MOD 3
#endif
#ifndef QOS_GATE_PEN
#define QOS_GATE_PEN 60.0
#endif
#ifndef QOS_OPENER
#define QOS_OPENER 0 // Q4b: the (5,11) starter stays out of the rooms until this round
#endif

int qosR(int r, int x, int y) const { return r == 0 ? w.idx(x, y) : w.idx(24 - x, 34 - y); }
bool qosInRoom(int r, int t) const
{
    if (t < 0)
        return false;
    int x = t % w.W, y = t / w.W;
    if (r == 1)
    {
        x = 24 - x;
        y = 34 - y;
    }
    return x >= 6 && x <= 11 && y >= 31 && y <= 33;
}
bool qosDoor(int t) const
{
    for (int r = 0; r < 2; r++)
        if (t == qosR(r, 4, 3) || t == qosR(r, 3, 3) || t == qosR(r, 8, 33) || t == qosR(r, 9, 33))
            return true;
    return false;
}

int qosDoorBusy[2] = {-100, -100};

bool queenofspadesOverride()
{
    for (auto& sg : segs)
        if (sg.team == w.myTeam && sg.id != w.myId)
            for (int r = 0; r < 2; r++)
                if (sg.tile == qosR(r, 4, 3))
                    qosDoorBusy[r] = round;
#if QOS_DOOR_NOSPLIT
    // a child born on a door tile has its neck across the portal and usually dies at once
    for (int t : trail)
        if (qosDoor(t))
        {
            threatAt[myHead] = std::max(threatAt[myHead], 1); // suppresses the normal split
            break;
        }
#endif
    return false;
}

double queenofspadesScore(int t, int d)
{
    double s = 0;
    bool portal = t != w.plainStep(myHead, d);
#if QOS_NECK
    // neck not visible => it is across our head's portal edge; going through it is a backwards move
    if (portal && myLen >= 2 && static_cast<int>(trail.size()) < 2)
        s -= 1000.0;
#endif
    for (int r = 0; r < 2; r++)
    {
#if QOS_ONEWAY
        if (myHead == qosR(r, 8, 32) && t == qosR(r, 8, 33))
            s -= QOS_ONEWAY_PEN; // would leave through the IN door, onto whoever waits at (4,3)
        if (myHead == qosR(r, 3, 2) && t == qosR(r, 3, 3))
            s -= QOS_ONEWAY_PEN; // would enter through the OUT door
        if (qosInRoom(r, myHead) && myHead != qosR(r, 8, 33) && t == qosR(r, 8, 32))
            s -= QOS_LANE_PEN; // keep the landing tile of the IN door clear
        if (myHead != qosR(r, 3, 3) && t == qosR(r, 3, 2))
            s -= QOS_LANE_PEN; // keep the landing tile of the OUT door clear
#endif
        bool entering = myHead == qosR(r, 4, 3) && t == qosR(r, 8, 33);
#if QOS_SPACING
        if ((entering || (t == qosR(r, 4, 3) && myHead != qosR(r, 8, 33))) && round - qosDoorBusy[r] <= QOS_SPACING)
            s -= QOS_SPACE_PEN;
#endif
#if QOS_GATE
        if (entering && (w.myId % QOS_GATE_MOD) != 0 && units > 3)
            s -= QOS_GATE_PEN;
#endif
#if QOS_OPENER
        if (entering && round < QOS_OPENER && w.myId == (w.myTeam == 'A' ? 0 : 1))
            s -= 200.0;
#endif
        (void)entering;
    }
    return s;
}
