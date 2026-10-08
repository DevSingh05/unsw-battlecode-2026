import re,sys
def load(p):
    d={}
    for l in open(p):
        m=re.match(r'\s*#define\s+(\w+)\s+(\S+)',l)
        if m and m.group(1) not in d: d[m.group(1)]=m.group(2)
    return d
base=load(sys.argv[1])
for p in sys.argv[2:]:
    d=load(p)
    diff={k:(base.get(k),v) for k,v in d.items() if base.get(k)!=v}
    miss=[k for k in base if k not in d]
    print(p.split('scratchpad/')[-1], {k:f"{a}->{b}" for k,(a,b) in diff.items()}, 'missing:',len(miss))
