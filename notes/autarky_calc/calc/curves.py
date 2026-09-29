from common import *
TL = [10, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 499]
for gm in GAMES:
    g = sim(gm['gid']); R = dict(g['rounds']); c = gm['calc']; o = 'B' if c == 'A' else 'A'
    print('%d calc=%s vs %-10s' % (gm['gid'], c, gm['opp']), 'winner', g['result']['winner'], g['result']['endReason'], g['last_round'])
    for T, name in ((c, 'calc'), (o, 'opp ')):
        s = '  %s ' % name
        for r in TL:
            if r in R:
                x = R[r][T]; s += ' %3d:%2d/%3d/%2d' % (r, x['n'], x['total'], x['max'])
        print(s)
