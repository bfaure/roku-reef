# inat_search.py <outdir> key=Taxon Name ...  -> research-grade, openly licensed photos; contact sheet per key
import json,sys,os,urllib.request,urllib.parse,io,time
from PIL import Image,ImageDraw
UA={'User-Agent':'roku-reef-screensaver-prototype/0.1 (personal project)'}
def get(u):
    for i in range(5):
        try: time.sleep(.6);return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read()
        except Exception as e: print('retry',str(e)[:50]);time.sleep(4*(i+1))
    return None
od=sys.argv[1];os.makedirs(od,exist_ok=True)
for arg in sys.argv[2:]:
    key,q=arg.split('=',1)
    p={'taxon_name':q,'photo_license':'cc0,cc-by,cc-by-sa','quality_grade':'research','per_page':int(os.environ.get('PER',40)),'order_by':'votes','photos':'true'}
    d=json.loads(get('https://api.inaturalist.org/v1/observations?'+urllib.parse.urlencode(p)))
    res=[]
    for o in d['results']:
        for ph in o['photos'][:2]:
            if ph.get('license_code') in ('cc0','cc-by','cc-by-sa'):
                res.append({'url':ph['url'].replace('square','large'),'thumb':ph['url'].replace('square','small'),'license':ph['license_code'],'attribution':ph.get('attribution',''),'obs':o['uri']})
    res=res[:int(os.environ.get('MAXR',30))];json.dump(res,open(f'{od}/{key}.json','w'),indent=1)
    cols=6;cw,ch=300,220;rows=(len(res)+cols-1)//cols;S=Image.new('RGB',(cols*cw,max(1,rows)*ch),'white');dr=ImageDraw.Draw(S)
    for i,r in enumerate(res):
        b=get(r['thumb'])
        if not b: continue
        t=Image.open(io.BytesIO(b)).convert('RGB');t.thumbnail((cw-6,ch-24));x,y=(i%cols)*cw,(i//cols)*ch;S.paste(t,(x+3,y+20));dr.text((x+4,y+3),f"{i} {r['license']}",fill='red')
    S.save(f'{od}/{key}_sheet.jpg',quality=80);print(key,len(res),flush=True)
