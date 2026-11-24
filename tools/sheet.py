# sheet.py <out.jpg> <png...>  -> contact sheet of cutouts on water-blue bg
import sys
from PIL import Image, ImageDraw
fs=sys.argv[2:];cols=4;cw,ch=450,300;rows=(len(fs)+cols-1)//cols
S=Image.new('RGB',(cols*cw,rows*ch),(20,90,140));d=ImageDraw.Draw(S)
for i,f in enumerate(fs):
    im=Image.open(f).convert('RGBA');im.thumbnail((cw-10,ch-30));x,y=(i%cols)*cw,(i//cols)*ch
    S.paste(im,(x+5,y+25),im);d.text((x+5,y+5),f.split('/')[-1],fill='white')
S.save(sys.argv[1],quality=85)
