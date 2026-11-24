# fetch.py <candidates_dir> <out_dir> key:idx [key:idx ...]  -> downloads a 1280px (standard size) version via imageinfo API
import json,sys,urllib.request,urllib.parse,time,os,re
UA={'User-Agent':'roku-reef-screensaver-prototype/0.1 (personal project)'}
def get(url):
    for i in range(8):
        try: return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read()
        except Exception as e: print('retry',str(e)[:60]);time.sleep(10*(i+1))
    raise RuntimeError('failed '+url)
cd,od=sys.argv[1],sys.argv[2];os.makedirs(od,exist_ok=True)
credits=json.load(open(f'{od}/credits.json')) if os.path.exists(f'{od}/credits.json') else {}
for a in sys.argv[3:]:
    key,idx=a.split(':');r=json.load(open(f'{cd}/{key}.json'))[int(idx)]
    fn=f'{od}/{key}_{idx}.jpg'
    if not os.path.exists(fn):
        p={'action':'query','titles':r['title'],'prop':'imageinfo','iiprop':'url','iiurlwidth':1280,'format':'json'}
        d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)))
        ii=list(d['query']['pages'].values())[0]['imageinfo'][0]
        url=ii.get('thumburl') or ii['url']
        try: open(fn,'wb').write(get(url))
        except Exception as e: print('SKIP',key,idx);continue
        time.sleep(8)
    credits[f'{key}_{idx}']={'title':r['title'],'license':r['license'],'artist':re.sub('<[^>]+>','',r['artist']).strip()}
    print(fn)
json.dump(credits,open(f'{od}/credits.json','w'),indent=1)
