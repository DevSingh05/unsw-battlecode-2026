"""Version tagging of our games by time window (UTC). See journal 2026-09-29/30."""
def version(at):
    t = at[:19]
    if t >= '2026-09-30T01:15:00': return 'v31'   # fingerprint: 01:08-01:10 battles were still v30 (see REPORT)
    if t >= '2026-09-30T01:05:00': return 'v30'
    if t >= '2026-09-30T00:54:00': return 'kc31'      # = v31 flags, A/B window
    if t >= '2026-09-30T00:48:30': return 'v30'
    if t >= '2026-09-30T00:42:00': return 'schb31'
    if t >= '2026-09-29T23:47:00': return 'v30'
    if t >= '2026-09-29T23:15:00': return 'pf31'      # = v30 flags, A/B window
    if '2026-09-29T22:41:00' > t >= '2026-09-29T21:56:00': return 'v31c'
    if '2026-09-29T21:29:00' > t >= '2026-09-29T21:23:00': return 'pk30'
    return 'v29'
FAMILY = {'v31': 'v31', 'kc31': 'v31', 'v30': 'v30', 'pf31': 'v30', 'v29': 'v29', 'schb31': 'other', 'v31c': 'other', 'pk30': 'other'}
