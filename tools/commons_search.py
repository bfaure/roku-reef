# Search Wikimedia Commons for species photos, download thumbnails, build numbered contact sheets.
import json, sys, os, urllib.request, urllib.error, urllib.parse, io
from PIL import Image, ImageDraw
UA={'User-Agent':'roku-reef-screensaver-prototype/0.1 (personal project)'}
import time
def get(url):
    for i in range(6):
        try:
            time.sleep(0.4)
            return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code!=429: raise
            time.sleep(5*(i+1))
    raise RuntimeError('rate limited')
def search(q,n=24):
    p={'action':'query','generator':'search','gsrsearch':q+' filetype:bitmap','gsrnamespace':6,'gsrlimit':n,
       'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':480,'format':'json'}
    d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)))
    out=[]
    for pg in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda x:x.get('index',0)):
        ii=pg['imageinfo'][0];m=ii.get('extmetadata',{})
        out.append({'title':pg['title'],'thumb':ii['thumburl'],'url':ii['url'],'w':ii['width'],'h':ii['height'],
                    'license':m.get('LicenseShortName',{}).get('value',''),'artist':m.get('Artist',{}).get('value','')[:120]})
    return out
outdir=sys.argv[1]; os.makedirs(outdir,exist_ok=True)
for arg in sys.argv[2:]:
    key,q=arg.split('=',1)
    res=search(q)
    json.dump(res,open(f'{outdir}/{key}.json','w'),indent=1)
    thumbs=[]
    for r in res:
        try: thumbs.append(Image.open(io.BytesIO(get(r['thumb']))).convert('RGB'))
        except Exception as e: thumbs.append(Image.new('RGB',(10,10)))
    cols=6;cw,ch=300,220;rows=(len(thumbs)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cw,rows*ch),'white');d=ImageDraw.Draw(sheet)
    for i,t in enumerate(thumbs):
        t.thumbnail((cw-6,ch-24));x,y=(i%cols)*cw,(i//cols)*ch;sheet.paste(t,(x+3,y+20))
        d.text((x+4,y+3),f"{i} {res[i]['license'][:22]}",fill='red')
    sheet.save(f'{outdir}/{key}_sheet.jpg',quality=80)
    print(key,len(res))
