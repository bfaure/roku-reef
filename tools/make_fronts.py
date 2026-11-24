# make_fronts.py: head-on/front-3/4 photos -> poc/assets/front, colour-matched to each side-view asset they pair with
import json
from PIL import Image,ImageStat
# only pairs whose colouring genuinely matches the side-view photo; FACES: +1 head toward right, -1 left, 0 symmetric head-on
PAIRS={"puffer_a":"puffer_0","yellowtang_a":"i_f_yellowtang_31","yellowtang_b":"i_f_yellowtang_31","lion_a":"lion_1"}
FACES={"puffer_0":0,"i_f_clown_38":1,"i_f_yellowtang_31":-1,"lion_1":0}
fish=json.loads(open('poc/assets/fish/fish.js').read().split('=',1)[1].rstrip(';\n'));out={}
for side,src in PAIRS.items():
    try: fr=Image.open(f'assets_src/cut/{src}.png').convert('RGBA')
    except FileNotFoundError: continue
    sd=Image.open(f'poc/assets/fish/{side}.png').convert('RGBA')
    fr=fr.crop(fr.getbbox());ma=fr.split()[3].point(lambda v:255 if v>128 else 0);ms=sd.split()[3].point(lambda v:255 if v>128 else 0)
    S1=ImageStat.Stat(fr.convert('RGB'),ma);S2=ImageStat.Stat(sd.convert('RGB'),ms)
    bands=[]
    for i,b in enumerate(fr.convert('RGB').split()):
        mf,sf,mt,st=S1.mean[i],max(S1.stddev[i],1),S2.mean[i],max(S2.stddev[i],1)
        g=mt/max(mf,1);bands.append(b.point(lambda v,g=g:int(max(0,min(255,.15*v+.85*v*g)))))
    im=Image.merge('RGB',bands).convert('RGBA');im.putalpha(fr.split()[3])
    if im.height>420: im=im.resize((round(im.width*420/im.height),420),Image.LANCZOS)
    k='f_'+side;im.save(f'poc/assets/front/{k}.png',optimize=True);out[k]={'species':fish[side]['species'],'side':side,'faces':FACES.get(src,0),'w':im.width,'h':im.height};print(k,im.size)
open('poc/assets/front/front.js','w').write('window.FRONT_ASSETS='+json.dumps(out)+';\n')
