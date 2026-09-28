import struct,sys,json
def unpack(b):
    out=bytearray(); i=0; n=len(b)
    while i<n:
        tag=b[i]; i+=1
        for bit in range(8):
            if tag>>bit&1: out.append(b[i]); i+=1
            else: out.append(0)
        if tag==0:
            c=b[i]; i+=1; out+=bytes(8*c)
        elif tag==0xff:
            c=b[i]; i+=1; out+=b[i:i+8*c]; i+=8*c
    return bytes(out)
class Msg:
    def __init__(s,raw):
        nseg=struct.unpack_from('<I',raw,0)[0]+1
        sizes=struct.unpack_from('<%dI'%nseg,raw,4)
        off=4+4*nseg; off+= (8-off%8)%8
        s.segs=[]
        for z in sizes: s.segs.append(raw[off:off+8*z]); off+=8*z
    def word(s,seg,w): return struct.unpack_from('<Q',s.segs[seg],8*w)[0]
    def resolve(s,seg,w):
        p=s.word(seg,w)
        if p==0: return None
        t=p&3
        if t==2:
            land=(p>>2)&1; po=(p>>3)&0x1fffffff; sid=p>>32
            if land==0: return s.resolve_at(sid,po)
            # double far
            p2=s.word(sid,po); tag=s.word(sid,po+1)
            tpo=(p2>>3)&0x1fffffff; tsid=p2>>32
            return s.decode(tsid,tpo-0,tag,absolute=True)
        return s.resolve_at(seg,w)
    def resolve_at(s,seg,w):
        p=s.word(seg,w); return s.decode(seg,w,p)
    def decode(s,seg,w,p,absolute=False):
        t=p&3; off=((p>>2)&0x3fffffff);
        if off&0x20000000: off-=0x40000000
        start = (off if absolute else w+1+off)
        if absolute: start=( (p>>2)&0x3fffffff ) if False else start
        if t==0: return ('s',seg,start,(p>>32)&0xffff,p>>48)
        if t==1: return ('l',seg,start,(p>>32)&7,p>>35)
        raise Exception('ptr type %d'%t)
class S:
    def __init__(s,m,ref): _,s.seg,s.w,s.dw,s.pw=ref; s.m=m
    def data(s,fmt,byteoff):
        if byteoff+struct.calcsize(fmt)>s.dw*8: return 0
        return struct.unpack_from('<'+fmt,s.m.segs[s.seg],s.w*8+byteoff)[0]
    def bit(s,b): return (s.data('B',b//8)>>(b%8))&1 if b//8<s.dw*8 else 0
    def ptr(s,i):
        if i>=s.pw: return None
        return s.m.resolve(s.seg,s.w+s.dw+i)
    def struct(s,i):
        r=s.ptr(i); return S(s.m,r) if r else None
    def text(s,i):
        r=s.ptr(i)
        if not r: return ''
        _,seg,st,es,cnt=r; return s.m.segs[seg][st*8:st*8+cnt-1].decode()
    def list(s,i):
        r=s.ptr(i)
        if not r: return []
        _,seg,st,es,cnt=r
        if es==7:
            tag=s.m.word(seg,st); n=(tag>>2)&0x3fffffff; dw=(tag>>32)&0xffff; pw=tag>>48
            return [S(s.m,('s',seg,st+1+k*(dw+pw),dw,pw)) for k in range(n)]
        if es==3: return list(struct.unpack_from('<%dH'%cnt,s.m.segs[seg],st*8))
        raise Exception('es %d'%es)
D='NESW'; T='AB'; REASON=['HitWall','HitSelf','HitOtherBody','HitHeadToHead','NoValidAction']
HK=[None,'empty','kelp','ally','allyHead','enemy','enemyHead']
def pt(x): return (x.data('i',0),x.data('i',4)) if x else None
def ev(e,fv):
    k=e.data('H',0); b=e.struct(0)
    if k==0: return {'t':'roundStart','round':b.data('i',0)}
    if k==1: return {'t':'turnStart','id':b.data('i',0)}
    if k==2: return {'t':'pearlCountdown','tile':pt(b.struct(0)),'countdown':b.data('i',0)}
    if k==3: return {'t':'tileChange','tile':pt(b.struct(0)),'hasPearl':b.bit(0)}
    if k==4:
        a=b.struct(0); act=None
        if a:
            w=a.data('H',0)
            act={'move':[D[x] for x in a.list(0)]} if w==0 else {'split':a.data('i',4)} if w==1 else {'suicide':1}
        ins=b.struct(1)
        return {'t':'dragonAction','id':b.data('i',0),'action':act,'instr':(ins.data('Q',0),ins.bit(64)) if ins else None,'tle':b.bit(32)}
    if k in(5,6,7):
        return {'t':['engineLog','dragonLog','dragonIndicator'][k-5],'id':b.data('i',0),'text':b.text(0)}
    if k==8:
        d=b.struct(0); return {'t':'debugDraw','id':b.data('i',0),'shape':d.data('H',0),'from':pt(d.struct(0)),'to':pt(d.struct(1)),'rgb':(d.data('B',2),d.data('B',3),d.data('B',4))}
    if k==9: return {'t':'dragonUpdate','id':b.data('i',0),'facing':D[b.data('H',4)],'head':pt(b.struct(0)),'tail':pt(b.struct(1))}
    if k==10: return {'t':'dragonSplit','parent':b.data('i',0),'child':b.data('i',4),'team':T[b.data('H',8)],'childFacing':D[b.data('H',10)],'parentBody':[pt(x) for x in b.list(0)],'childBody':[pt(x) for x in b.list(1)]}
    if k==11: return {'t':'dragonDeath','id':b.data('i',0),'reason':REASON[b.data('H',4)]}
    if k==12:
        return {'t':'sonarPing','sender':b.data('i',0),'dir':D[b.data('H',4)],'value':b.data('I',8) if fv<2 else b.data('Q',16),'origin':pt(b.struct(0)),'end':pt(b.struct(1)),'hitId':b.data('i',12) if b.data('H',6)==1 else None,'hitKind':HK[b.data('H',24)]}
    return {'t':'unknown%d'%k}
def load(path):
    raw=open(path,'rb').read()
    if raw[:2]==b'\x1f\x8b':
        import gzip; raw=gzip.decompress(raw)
    m=Msg(unpack(raw)); r=S(m,m.resolve(0,0))
    fv=r.data('I',0)
    res=r.struct(4)
    def ts(x): return {'dragonCount':x.data('i',0),'longest':x.data('i',4),'total':x.data('i',8)}
    out={'formatVersion':fv,'seed':r.data('Q',8) if r.data('H',4)==1 else None,'map':r.text(0),'botA':r.text(1),'botB':r.text(2),
         'result':{'terminated':res.bit(0),'endReason':['teamEliminated','roundLimit'][res.data('H',2)],'winner':T[res.data('H',6)] if res.data('H',4)==1 else None,'A':ts(res.struct(0)),'B':ts(res.struct(1))},
         'events':[ev(e,fv) for e in r.list(3)]}
    return out
if __name__=='__main__':
    o=load(sys.argv[1]); ev_=o.pop('events'); mp=o.pop('map')
    print(json.dumps(o)); print(mp[:400]); print(len(ev_),'events')
    from collections import Counter; print(Counter(e['t'] for e in ev_))
    for e in ev_[:60]: print(e)
