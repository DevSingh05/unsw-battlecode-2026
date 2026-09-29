#!/usr/bin/env python3
"""Which replay team is OUR bot? Authenticate sonar values with our checksum (v28/v29 SECRETs).
   python3 notes/forensics/portals/auth.py GAME..."""
import os, sys, json, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'notes/tools'))
import replay_decode as R
M = (1 << 64) - 1
SECRET = 0x5d1c0ffee15b00b5; WSECRET = 0x9a3c55e1d2b47f08


def mix(x):
    x ^= x >> 31; x = (x * 0x7fb5d329728ea185) & M; x ^= x >> 27; x = (x * 0x81dadef4bc2dd44d) & M; x ^= x >> 33
    return x


def kind(v, team):
    for fr in range(3):
        salt = (fr + 1) << 58
        x = v & ((1 << 43) - 1)
        if (v >> 43) == mix(x ^ SECRET ^ (ord(team) << 50) ^ salt) & ((1 << 21) - 1): return 'king', fr
        x = v & ((1 << 27) - 1)
        if (v >> 27) == mix(x ^ WSECRET ^ (ord(team) << 50) ^ salt) & ((1 << 37) - 1): return 'warn', fr
    return None, None


def who(gid):
    o = R.load(os.path.join(ROOT, 'replays/auto/games/%d.replay' % gid))
    team = {}
    for i, l in enumerate([l for l in o['map'].splitlines() if l.startswith('DRAGON ')]):
        team[i] = 'AB'[int(l.split()[1])]
    C = collections.Counter()
    for e in o['events']:
        if e['t'] == 'dragonSplit': team[e['child']] = e['team']
        if e['t'] == 'sonarPing':
            T = team.get(e['sender'])
            for claim in 'AB':
                k, fr = kind(e['value'], claim)
                if k: C[(T, claim, k, fr)] += 1
    return C


if __name__ == '__main__':
    led = {g['game']: g for g in json.load(open(os.path.join(ROOT, 'replays/auto/games/ledger.json')))}
    for a in sys.argv[1:]:
        print(a, 'ledger side', led[int(a)]['side'], dict(who(int(a))))
