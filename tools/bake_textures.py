# bake_textures.py: ambientCG PBR sets (CC0) -> lit, tileable textures for the reef (poc/assets/tex/*.jpg)
# lighting = albedo * AO * (ambient + diffuse(N . L)) * cavity(displacement); light from above, slightly left & toward camera
import os,math,json
from PIL import Image,ImageMath
SRC='assets_src/acg';OUT='poc/assets/tex';os.makedirs(OUT,exist_ok=True)
L=(-.3,.75,.6);n=math.sqrt(sum(v*v for v in L));L=[v/n for v in L]
SETS={'rock_a':'Rock062','rock_b':'Rock060','pebbles_a':'Gravel022','pebbles_b':'Rocks022','rubble':'Gravel026','sand_a':'Ground097','sand_b':'Ground093A'}
meta={}
for name,aid in SETS.items():
    p=f'{SRC}/{aid}/{aid}_2K-JPG_';col=Image.open(p+'Color.jpg').convert('RGB');nm=Image.open(p+'NormalGL.jpg').convert('RGB')
    ao=Image.open(p+'AmbientOcclusion.jpg').convert('L') if os.path.exists(p+'AmbientOcclusion.jpg') else Image.new('L',col.size,255)
    dp=Image.open(p+'Displacement.jpg').convert('L')
    r,g,b=[c.convert('F') for c in nm.split()]
    ndl=ImageMath.eval(f"max((r/127.5-1)*{L[0]}+(g/127.5-1)*{L[1]}+(b/127.5-1)*{L[2]},0.0)",r=r,g=g,b=b)
    sh=ImageMath.eval("a/255.0*(0.38+0.9*n)*(0.62+0.38*d/255.0)",a=ao.convert('F'),n=ndl,d=dp.convert('F'))
    out=Image.merge('RGB',[ImageMath.eval("convert(min(c*s*1.15,255.0),'L')",c=c.convert('F'),s=sh) for c in col.split()])
    out.save(f'{OUT}/{name}.jpg',quality=86,optimize=True);meta[name]={'src':aid,'w':out.width,'h':out.height};print(name,out.size)
open(f'{OUT}/tex.js','w').write('window.TEX_ASSETS='+json.dumps(meta)+';\n')
