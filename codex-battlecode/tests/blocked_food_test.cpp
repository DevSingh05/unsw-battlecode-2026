#define main battlecode_program_main
#include "../bot/main.cpp"
#undef main
#include <cassert>

int main()
{
    Bot b;
    b.w.init(16, 16);
    b.myHead = b.w.idx(5, 5);
    b.w.portalSide.assign(b.w.N * 4, 0);
    for (int i = 0; i < 49; ++i)
    {
        b.in.tx[i] = 2 + i % 7;
        b.in.ty[i] = 2 + i / 7;
        b.in.tpearl[i] = 0;
    }
    int food = 3 * 7 + 4; // (6,5), one ordinary step from the head
    b.in.tpearl[food] = 1;
    assert(!b.blockedFoodNeedsDoor()); // no door
    int door = b.myHead * 4;
    b.w.portalSide[door] = 1;
    b.w.nxt[door] = -1;
    assert(!b.blockedFoodNeedsDoor()); // food is walkable
    b.occId.assign(b.w.N, 123);
    b.freeT.assign(b.w.N, INF);
    assert(!b.blockedFoodNeedsDoor()); // bodies do not masquerade as walls
    for (int y = 0; y < 16; ++y)
    {
        b.w.nxt[b.w.idx(5, y) * 4 + 1] = -1;
        b.w.nxt[b.w.idx(6, y) * 4 + 3] = -1;
    }
    assert(b.blockedFoodNeedsDoor()); // optimistic detour is at least ten
    b.in.tpearl[food] = 0;
    assert(!b.blockedFoodNeedsDoor()); // current food evidence is mandatory
    std::cout << "PASS: door, actual food, static detour, and congestion controls\n";
}
