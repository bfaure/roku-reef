# lumakey.py <in.jpg> <out.png> [lo] [hi]  -> alpha from luminance (for subjects shot on black)
import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB');lo=int(sys.argv[3]) if len(sys.argv)>3 else 30;hi=int(sys.argv[4]) if len(sys.argv)>4 else 70
L=im.convert('L').point(lambda v:0 if v<lo else 255 if v>hi else int((v-lo)*255/(hi-lo)))
o=im.convert('RGBA');o.putalpha(L);o=o.crop(L.getbbox());o.save(sys.argv[2]);print('ok',o.size)
