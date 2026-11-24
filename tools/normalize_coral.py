# coral cutouts -> poc/assets/coral/*.png (+ coral.js metadata)
import json
from PIL import Image
C=json.load(open('assets_src/coral_config.json'));out={}
for name,c in C.items():
    import os
    hp=f"assets_src/cut_hi/{c['src']}.png";im=Image.open(hp if os.path.exists(hp) else f"assets_src/cut/{c['src']}.png").convert('RGBA')
    # defringe: erode alpha ~2px (removes the halo of original photo background) and darken the new rim slightly
    from PIL import ImageFilter,ImageChops
    a0=im.split()[3];a1=a0.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2));rim=ImageChops.subtract(a0.filter(ImageFilter.MinFilter(3)),a0.filter(ImageFilter.MinFilter(9)))
    rgb=im.convert('RGB');dark=Image.eval(rgb,lambda v:int(v*.72));rgb=Image.composite(dark,rgb,rim.point(lambda v:int(v*.6)));im=rgb.convert('RGBA');im.putalpha(a1)
    if c.get('crop'):
        x0,y0,x1,y1=c['crop'];im=im.crop((int(x0*im.width),int(y0*im.height),int(x1*im.width),int(y1*im.height)))
    a=im.split()[3].point(lambda v:0 if v<20 else v);im.putalpha(a);im=im.crop(im.getbbox())
    # feather edges that were cut by the photo frame (left/right/top), so nothing looks rectangular
    W_,H_=im.size;f=max(4,int(min(W_,H_)*.05));A=im.split()[3].load()
    for y in range(H_):
        for x in list(range(min(f,W_)))+list(range(max(0,W_-f),W_)):
            d=min(x,W_-1-x);A[x,y]=int(A[x,y]*min(1,d/f))
    for y in range(min(f,H_)):
        for x in range(W_): A[x,y]=int(A[x,y]*min(1,y/f))
    # photometric normalization: pull every photo toward a common exposure, contrast and saturation
    from PIL import ImageStat,ImageEnhance
    m=im.split()[3].point(lambda v:255 if v>128 else 0);rgb=im.convert('RGB')
    st=ImageStat.Stat(rgb.convert('L'),m);mean,sd=st.mean[0],max(st.stddev[0],1)
    rgb=ImageEnhance.Contrast(rgb).enhance(max(.75,min(1.3,(sd*.5+44*.5)/sd)))
    mean2=ImageStat.Stat(rgb.convert('L'),m).mean[0];rgb=ImageEnhance.Brightness(rgb).enhance(max(.75,min(1.35,(mean2*.45+120*.55)/max(mean2,1))))
    sat=ImageStat.Stat(rgb.convert('HSV').split()[1],m).mean[0];rgb=ImageEnhance.Color(rgb).enhance(.95 if c['kind']=='star' else max(.45,min(1.0,(sat*.35+72*.65)/max(sat,1))))
    a=im.split()[3];im=rgb.convert('RGBA');im.putalpha(a)
    mh=c.get('maxh',900)
    if im.height>mh: im=im.resize((round(im.width*mh/im.height),mh),Image.LANCZOS)
    if im.width>1400: im=im.resize((1400,round(im.height*1400/im.width)),Image.LANCZOS)
    im.save(f'poc/assets/coral/{name}.png',optimize=True)
    out[name]={'kind':c['kind'],'h':c['h'],'w':im.width,'hp':im.height};print(name,im.size)
open('poc/assets/coral/coral.js','w').write('window.CORAL_ASSETS='+json.dumps(out,indent=1)+';\n')
