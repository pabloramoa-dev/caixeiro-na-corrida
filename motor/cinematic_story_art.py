"""Ilustracoes 2D cinematograficas originais para piloto do Caixeiro (CPU/Pillow)."""
from __future__ import annotations
import io, math, random
from PIL import Image, ImageDraw, ImageFilter

W,H=1440,900
INK="#252439"
PAPER="#fff4e4"
GOLD="#ffc66f"
MINT="#83cebf"
CORAL="#fb8584"

def rr(d,box,fill,r=20,outline=None,width=1):
    d.rounded_rectangle(tuple(map(int,box)),radius=int(r),fill=fill,outline=outline,width=width)

def oval(d,box,fill,outline=None,width=1):
    d.ellipse(tuple(map(int,box)),fill=fill,outline=outline,width=width)

def person(d,x,y,scale=1,coat="#df866b",hair="#282337",facing=1):
    # Big readable cartoon silhouette, face is not a real person.
    s=scale
    def b(a,b,c,e):return (x+a*s,y+b*s,x+c*s,y+e*s)
    rr(d,b(-110,160,112,420),coat,60*s,INK,6)
    rr(d,b(-80,17,81,184),"#e8ab86",72*s,INK,6)
    oval(d,b(-91,-14,91,110),hair)
    rr(d,b(-72,65,74,169),"#e8ab86",51*s)
    oval(d,b(30*facing-10,106,30*facing+5,121),INK)
    d.arc(b(-25,119,40,157),5,160,fill=INK,width=4)
    rr(d,b(-125,216,-60,380),coat,30*s,INK,4)

def radio(d,x,y,s=1):
    def b(a,b,c,e):return(x+a*s,y+b*s,x+c*s,y+e*s)
    # 1950s style portable radio, no branding.
    rr(d,b(-215,-115,215,145),"#f7b66b",27*s,INK,max(1,int(9*s)))
    rr(d,b(-182,-82,40,102),"#634864",22*s,INK,max(1,int(6*s)))
    for k in range(7):
        d.line([(x+(-145+k*28)*s,y-62*s),(x+(-145+k*28)*s,y+78*s)],fill="#e8d0a3",width=max(2,int(8*s)))
    oval(d,b(103,-25,172,45),PAPER,INK,max(2,int(6*s)))
    oval(d,b(120,-8,155,27),CORAL)
    d.line([(x-160*s,y-122*s),(x+142*s,y-235*s)],fill="#eee4cd",width=max(2,int(8*s)))
    d.line([(x+142*s,y-235*s),(x+155*s,y-229*s)],fill=INK,width=max(1,int(4*s)))

def gift(d,x,y,s=1):
    rr(d,(x-255*s,y-135*s,x+255*s,y+180*s),"#d68478",28*s,INK,7)
    rr(d,(x-274*s,y-160*s,x+274*s,y-104*s),"#fac6aa",20*s,INK,7)
    rr(d,(x-38*s,y-161*s,x+38*s,y+180*s),GOLD,4*s)
    d.arc((x-130*s,y-248*s,x+10*s,y-127*s),185,355,fill=GOLD,width=14)
    d.arc((x-10*s,y-248*s,x+130*s,y-127*s),185,355,fill=GOLD,width=14)

def car(d,x,y,s=1):
    rr(d,(x-355*s,y-105*s,x+355*s,y+165*s),"#73b9bb",85*s,INK,8)
    d.polygon([(x-195*s,y-105*s),(x-95*s,y-230*s),(x+165*s,y-230*s),(x+270*s,y-105*s)],fill="#97d5d8")
    d.line([(x-195*s,y-105*s),(x-95*s,y-230*s),(x+165*s,y-230*s),(x+270*s,y-105*s)],fill=INK,width=8)
    for xx in (-225,220):
        oval(d,(x+(xx-58)*s,y+110*s,x+(xx+58)*s,y+235*s),INK)
        oval(d,(x+(xx-27)*s,y+142*s,x+(xx+27)*s,y+202*s),PAPER)

def house(d):
    d.polygon([(300,385),(840,95),(1260,388)],fill="#99667e")
    rr(d,(390,370,1180,900),"#c68d93",16,INK,9)
    rr(d,(790,455,1000,900),"#594964",14,INK,7)
    oval(d,(956,670,982,697),GOLD)
    for x in (450,1060):
        rr(d,(x,460,x+100,600),"#ffc77b",12,INK,6)
        d.line((x+50,460,x+50,600),fill=INK,width=5)

def background(stage,index):
    palettes=[("#1b314c","#626c86"),("#30324b","#86718e"),("#423448","#a16d78"),
              ("#2a3c54","#9a7484"),("#27394e","#bb9293"),("#55435c","#bd8782"),
              ("#273349","#637d91"),("#2f3852","#a5858a")]
    start,end=palettes[stage]
    def rgb(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
    a,b=rgb(start),rgb(end)
    im=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H
        rgb2=tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
        d.line([(0,y),(W,y)],fill=rgb2)
    # depth silhouettes - different planes, original shapes
    for k in range(17):
        x=k*105-40
        h=150+(k*73)%235
        d.rectangle((x,H-h,x+84,H),fill="#26344f")
        for yy in range(H-h+28,H-20,47):
            if (k+yy//47+index)%3!=0:
                d.rectangle((x+18,yy,x+31,yy+17),fill="#c9b084")
    return im

def draw_stage(d,stage,index):
    # Artwork replaces abstract icons with illustrated story beats.
    if stage==0:
        car(d,870,530,.87)
        person(d,390,230,.94,"#e69a91")
        gift(d,410,655,.58)
        for k in range(15):
            x=(k*113+index*29)%1440
            d.line((x,40+(k*71)%400,x-28,140+(k*71)%400),fill="#bad1dc",width=3)
    elif stage==1:
        rr(d,(160,225,1230,730),"#e1b09a",38,INK,10)
        oval(d,(230,300,490,550),"#e6dbba",INK,8)
        radio(d,890,500,.72)
        for k in range(3):
            d.arc((820-k*30,110-k*20,1060+k*30,330+k*20),190,340,fill=GOLD,width=9)
    elif stage==2:
        radio(d,700,515,1.38)
        for k in range(5):
            x=180+k*220
            d.ellipse((x,160,x+15,175),fill="#fff1bc")
        rr(d,(107,640,440,775),"#574868",35)
    elif stage==3:
        person(d,470,235,1.2,"#e09386")
        radio(d,1010,588,.9)
        oval(d,(950,130,1100,280),GOLD)
        d.arc((920,110,1140,335),205,340,fill="#ffe4aa",width=12)
    elif stage==4:
        house(d)
        person(d,270,460,.73,"#7cbbc0")
        oval(d,(1005,296,1135,424),GOLD)
        for k in range(3):
            d.arc((1060-k*50,180-k*42,1210+k*35,370+k*38),180,315,fill="#f7d693",width=8)
    elif stage==5:
        person(d,470,252,1.07,"#f1a789")
        person(d,875,280,.97,"#86bab2",hair="#a29a99",facing=-1)
        radio(d,686,690,.53)
        for k in range(8):
            x=175+k*153
            d.ellipse((x,110+(k%3)*34,x+10,120+(k%3)*34),fill=GOLD)
    elif stage==6:
        person(d,530,310,1.08,"#e49b80")
        person(d,720,315,1.05,"#8cc8b9",hair="#9b9aa7",facing=-1)
        d.arc((380,500,880,830),10,160,fill=GOLD,width=19)
        oval(d,(940,155,1075,290),CORAL)
    else:
        car(d,760,520,1.03)
        for k in range(7):
            x=220+k*171
            d.line((x,120,x+40,180),fill="#fdd5a2",width=6)

def render(scene,ep):
    index=int(scene["scene"])
    stage=index%8
    im=background(stage,index)
    d=ImageDraw.Draw(im)
    draw_stage(d,stage,index)
    # subdued vignette and film grain provide depth and continuity.
    vign=Image.new("RGBA",(W,H),(0,0,0,0))
    vg=ImageDraw.Draw(vign)
    for k in range(14):
        alpha=max(0,20-k*2)
        vg.rounded_rectangle((k*11,k*9,W-k*11,H-k*9),radius=42,outline=(20,18,30,alpha),width=14)
    im=Image.alpha_composite(im.convert("RGBA"),vign)
    rng=random.Random(543+index)
    px=ImageDraw.Draw(im)
    for _ in range(240):
        x=rng.randrange(W);y=rng.randrange(H)
        px.point((x,y),fill=(245,233,209,35))
    output=io.BytesIO()
    im.save(output,"PNG",optimize=True)
    return output.getvalue()
