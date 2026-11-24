# normalize.py: cutouts -> poc/assets/fish/*.png, all facing RIGHT, horizontal, trimmed, max width W.
import json,sys
from PIL import Image
CFG=json.load(open('assets_src/fish_config.json'))
out={}
for name,c in CFG.items():
    im=Image.open(f"assets_src/cut/{c['src']}.png").convert('RGBA')
    if c.get('crop'):
        x0,y0,x1,y1=c['crop'];im=im.crop((int(x0*im.width),int(y0*im.height),int(x1*im.width),int(y1*im.height)))
    if c.get('flip'): im=im.transpose(Image.FLIP_LEFT_RIGHT)
    if c.get('rot'): im=im.rotate(c['rot'],resample=Image.BICUBIC,expand=True)
    # clean faint halo alpha then trim
    a=im.split()[3].point(lambda v:0 if v<24 else v);im.putalpha(a)
    im=im.crop(im.getbbox())
    mw=c.get('maxw',640)
    if im.width>mw: im=im.resize((mw,round(im.height*mw/im.width)),Image.LANCZOS)
    im.save(f'poc/assets/fish/{name}.png',optimize=True)
    out[name]={k:v for k,v in c.items() if k not in('src','flip','rot','maxw','crop')}
    out[name].update(w=im.width,h=im.height)
    # body-height profile per column bin (for the 2.5D slice renderer): [top,bottom] as fractions of image height
    NB=48;A=im.split()[3].load();prof=[]
    for bi in range(NB):
        x0=int(bi*im.width/NB);x1=max(x0+1,int((bi+1)*im.width/NB));top,bot=None,None
        for y in range(im.height):
            if any(A[x,y]>40 for x in range(x0,x1)):top=y;break
        for y in range(im.height-1,-1,-1):
            if any(A[x,y]>40 for x in range(x0,x1)):bot=y;break
        prof.append([round(top/im.height,3),round(bot/im.height,3)] if top is not None else None)
    for i in range(NB):
        if prof[i] is None:
            j=min((j for j in range(NB) if prof[j] is not None),key=lambda j:abs(j-i));prof[i]=prof[j]
    out[name]['prof']=prof
    print(name,im.size)
open('poc/assets/fish/fish.js','w').write('window.FISH_ASSETS='+json.dumps(out,indent=1)+';\n')
