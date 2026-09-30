import sys, re, collections, ast
D = sys.argv[2]
cnt = collections.Counter(); net = collections.Counter()
def block(txt, r):
    m = re.search(rf'^R{r} id=.*?(?=^R{r+1} |\Z)', txt, re.S | re.M)
    return m.group(0) if m else ''
def chosen_line(b):
    ch = re.search(r'-> (\w)', b)
    if not ch: return None, ''
    # find which YES preceded chosen cand
    lines = b.split('\n'); prev = ''
    for i, l in enumerate(lines):
        if l.strip().startswith('cand ' + ch.group(1)):
            return l, lines[i-1] if i else ''
    return None, ''
for line in open(sys.argv[1]):
    p = line.split(); r, i = int(p[1]), int(p[2])
    key = ast.literal_eval(line[line.index('('):line.index(')')+1])
    out = int(line.split('out ')[1].split()[0]); lenIn = key[2]
    txt = open(f'{D}/{i}.txt').read()
    b = block(txt, r); c, pre = chosen_line(b)
    b1 = block(txt, r - 1); c1, pre1 = chosen_line(b1)
    ncand = len(re.findall(r'cand ', b))
    now = 'PF_YES' if 'PF YES' in pre else ('PUMP_YES' if 'POCKET YES' in pre else ('forced' if ncand == 1 else 'scored'))
    before = 'prevPUMP' if 'POCKET YES' in pre1 else ('prevPF' if 'PF YES' in pre1 else ('prevDepthBad' if c1 and 'depth=' in c1 and int(re.search(r'depth=(\d+)', c1).group(1)) < 12 else 'prevOK'))
    k = ('small' if key[0] <= 2 else 'p3', now, before if now != 'PF_YES' else '')
    cnt[k] += 1; net[k] += out - lenIn
for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]): print(k, v, 'net/e %+.2f' % (net[k] / v))
