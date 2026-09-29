#define UNK_PORTAL_SIDES 1
#define main battlecode_program_main
#include "../bot/main.cpp"
#undef main
#include <cassert>

int main()
{
    for (int head : {0, 4 * 31 + 4, 31 * 31 - 1})
    {
        World world;
        world.init(31, 31);
        TurnInput view;
        for (auto& row : view.hEdges) for (auto& edge : row) edge = ".";
        for (auto& row : view.vEdges) for (auto& edge : row) edge = ".";
        view.hEdges[3][3] = "0";
        view.hEdges[4][3] = "1";
        view.vEdges[3][3] = "2";
        view.vEdges[3][4] = "3";
        world.observeEdges(view, head % 31, head / 31);
        for (int d = 0; d < 4; ++d)
        {
            int other = world.plainStep(head, d);
            assert(world.portalSide[head * 4 + d]);
            assert(world.portalSide[other * 4 + (d + 2) % 4]);
            assert(world.nxt[head * 4 + d] == -1); // destination remains unknown
        }
        int open = world.idx(15, 15);
        for (int d = 0; d < 4; ++d) assert(!world.portalSide[open * 4 + d]);
    }
    std::cout << "PASS: both faces in all four directions, including torus seams; no invented portal links\n";
}
