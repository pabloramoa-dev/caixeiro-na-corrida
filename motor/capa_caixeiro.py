import io
import subprocess
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw, ImageFont
from objetos_fala import OBJETOS, objeto

def criar(ep, pasta):
    pasta = Path(pasta)
    base = pasta/'hyperframes/assets/base.mp4'
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(base),'-frames:v','1',
                                   '-f','image2pipe','-vcodec','png','-threads','1','pipe:1'])
    foto = Image.open(io.BytesIO(raw)).convert('RGB')
    w,h = foto.size
    capa = Image.new('RGB',(1080,1920),'#222638')
    rosto = foto.crop((w*.17,h*.49-w*.33,w*.83,h*.49-w*.33+w*.66)).resize((1080,1080),Image.Resampling.LANCZOS)
    capa.paste(rosto,(0,270))
    draw = ImageDraw.Draw(capa)
    fonte = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    nome = objeto(ep['batidas'][0]['fala']) or next((x for b in ep['batidas'] if (x:=objeto(b['fala']))),'porta')
    icone = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=OBJETOS[nome].encode(),output_width=190,output_height=190))).convert('RGBA')
    draw.rounded_rectangle((830,1060,1040,1270),radius=30,fill='#ffcc76')
    capa.paste(icone,(840,1070),icone)
    palavras = ep['titulo'].split()
    corte = min(range(1,len(palavras)),key=lambda i:abs(len(' '.join(palavras[:i]))-len(' '.join(palavras[i:])))) if len(palavras)>1 else 1
    linhas = [' '.join(palavras[:corte]),' '.join(palavras[corte:])]
    for size in range(82,15,-1):
        f=ImageFont.truetype(fonte,size)
        if max(f.getlength(l) for l in linhas)<960: break
    for i,l in enumerate(linhas):
        draw.text((60,1380+100*i),l,font=f,fill='#fff7df')
    draw.text((60,180),'CAIXEIRO NA CORRIDA',font=ImageFont.truetype(fonte,52),fill='#ffcc76')
    capa.save(pasta/'capa.jpg',quality=93)
