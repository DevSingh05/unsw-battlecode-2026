"""Parse one turn's debug block from the instrumented v29 (v29x)."""
import re
CAND = re.compile(r'cand (\w) t=\((\d+),(\d+)\) pearls=([-\d.]+) area=(\d+) depth=(\d+) threat=(\d+) freeT=(\d+) score=([-\d.e+]+)')
CX = re.compile(r'cx (\w) pump=(\d) need=(\d+) areaP=([-\d.]+) depthP=([-\d.]+) threatP=([-\d.]+) box=([-\d.]+) feed=([-\d.]+) king=([-\d.]+) portal=([-\d.]+)')
def parse(b):
    cands = {}; pocket = None; lines = b.splitlines(); branch = None; ctx = {}
    for i, l in enumerate(lines):
        mm = CAND.search(l)
        if mm:
            d = mm.group(1)
            cands[d] = dict(t=(int(mm.group(2)), int(mm.group(3))), pearls=float(mm.group(4)), area=int(mm.group(5)), depth=int(mm.group(6)),
                            threat=int(mm.group(7)), score=float(mm.group(9)), pocket=pocket)
            pocket = None; continue
        mm = CX.search(l)
        if mm:
            c = cands[mm.group(1)]
            c.update(pump=int(mm.group(2)), need=int(mm.group(3)), areaP=float(mm.group(4)), depthP=float(mm.group(5)), threatP=float(mm.group(6)),
                     box=float(mm.group(7)), feed=float(mm.group(8)), king=float(mm.group(9)), portal=float(mm.group(10)))
            continue
        mm = re.match(r'POCKET (\w+)', l)
        if mm: pocket = mm.group(1); continue
        mm = re.match(r'\s+-> (.*)', l)
        if mm: branch = mm.group(1).strip()
        mm = re.match(r'\s+ctx feeding=(\d) target=(-?\d+) kingSelf=(\d) units=(\d+)', l)
        if mm: ctx = dict(feeding=int(mm.group(1)), kingSelf=int(mm.group(3)), units=int(mm.group(4)))
    return dict(cands=cands, branch=branch, ctx=ctx)
