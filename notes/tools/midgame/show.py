import sys, sim2
def show(path, rnd, did, R=4):
    st = sim2.simulate(path, stop=(rnd, did)); m = st['map']; b = st['body']; T = st['team'][did]
    hx, hy = b[did][0]
    occ = {}
    for j, bb in b.items():
        for si, s in enumerate(bb): occ[s] = (j, si)
    print(path.split('/')[-1], 'round', rnd, 'id', did, 'len', len(b[did]), 'action', st['act'], 'instr', st['e'].get('instr'))
    for dy in range(-R, R + 1):
        row = ''
        for dx in range(-R, R + 1):
            t = m.wrap(hx + dx, hy + dy)
            if t in occ:
                j, si = occ[t]; c = ('@' if j == did else ('A' if st['team'][j] == T else 'E')) if si == 0 else ('s' if j == did else ('a' if st['team'][j] == T else 'e'))
            else: c = 'o' if t in st['pearls'] else '.'
            # walls: mark E and S edges
            row += c + ('|' if m.step(t, 'E') is None else ' ')
        print(row)
    for j, bb in b.items():
        if any(max(abs(((s[0]-hx+m.w//2)%m.w)-m.w//2), abs(((s[1]-hy+m.h//2)%m.h)-m.h//2)) <= R for s in bb):
            print('  ', j, st['team'][j], bb[:6])
if __name__ == '__main__':
    show(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
