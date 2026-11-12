def dlc_len(d):
    return d if d <= 8 else {9:12,10:16,11:20,12:24,13:32,14:48,15:64}[d]

def stuff_bits(bits):
    out=[]; last=None; run=0; pos=[]
    for i,b in enumerate(bits):
        out.append(b)
        if b==last: run+=1
        else: last=b; run=1
        if run==5:
            sb=1-b; out.append(sb); pos.append((i,len(out)-1,sb)); last=sb; run=1
    return out,pos

def calculate_crc(bitstream, payload_len_bytes):
    # Чистый алгоритм (init=0) — для совместимости с test_crc17/test_crc21
    w,poly = (21,0x102899) if payload_len_bytes>16 else (17,0x1685B)
    m=(1<<w)-1; c=0
    for b in bitstream:
        msb=(c>>(w-1))&1; c=(c<<1)&m
        if msb^b: c^=poly
    return [(c>>i)&1 for i in range(w-1,-1,-1)]

def _crc_val(bits,w,poly,init):
    m=(1<<w)-1; c=init&m
    for b in bits:
        msb=(c>>(w-1))&1; c=(c<<1)&m
        if msb^b: c^=poly
    return c

def _gray_sc(n):
    n&=7; g=n^(n>>1); p=((g>>2)^(g>>1)^g)&1
    return [(g>>2)&1,(g>>1)&1,g&1,p]

def generate_can_fd_frame(fid, dlc, data, brs=True):
    raw=[0]+[(fid>>i)&1 for i in range(10,-1,-1)]
    raw+=[0,0,1,0,1 if brs else 0,0]                 # RRS,IDE,FDF,res,BRS,ESI
    raw+=[(dlc>>i)&1 for i in range(3,-1,-1)]
    for by in data: raw+=[(by>>i)&1 for i in range(7,-1,-1)]
    st,pos=stuff_bits(raw)
    boundary = pos and pos[-1][0]==len(raw)-1
    if boundary: fsb=st[-1]; st=st[:-1]; pos=pos[:-1]
    else: fsb=None
    sc=_gray_sc(len(pos))
    w,poly=(21,0x102899) if dlc_len(dlc)>16 else (17,0x1685B)
    crc=_crc_val(st+sc,w,poly,1<<(w-1))              # ISO init = MSB
    cb=[(crc>>i)&1 for i in range(w-1,-1,-1)]
    field=[fsb if boundary else 1-(st[-1] if st else 0)]
    seq=sc+cb; i=0
    while i<len(seq):
        g=seq[i:i+4]; field+=g; i+=4
        if i<len(seq): field.append(1-g[-1])
    return st+field+[1,1,1]+[1]*7

if __name__=="__main__":
    fr=generate_can_fd_frame(0x5AA,8,[0xFF]*8,True)
    print("anchor frame bits:",len(fr))
