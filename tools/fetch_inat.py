# fetch_inat.py <inat_dir> <raw_dir> key:idx ...   (downloads 'large' 1024px photo, records attribution)
import json,sys,os,urllib.request,time
UA={'User-Agent':'roku-reef-screensaver-prototype/0.1 (personal project)'}
d,od=sys.argv[1],sys.argv[2];os.makedirs(od,exist_ok=True)
cf=f'{od}/credits_inat.json';cr=json.load(open(cf)) if os.path.exists(cf) else {}
for a in sys.argv[3:]:
    k,i=a.split(':');r=json.load(open(f'{d}/{k}.json'))[int(i)];fn=f'{od}/i_{k}_{i}.jpg'
    if not os.path.exists(fn):
        for t in range(4):
            try: open(fn,'wb').write(urllib.request.urlopen(urllib.request.Request(r['url'],headers=UA),timeout=60).read());break
            except Exception as e: print('retry',e);time.sleep(5)
        time.sleep(.8)
    cr[f'i_{k}_{i}']={'license':r['license'],'attribution':r['attribution'],'source':r['obs']};print(fn)
json.dump(cr,open(cf,'w'),indent=1)
