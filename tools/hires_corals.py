# hires_corals.py: re-fetch coral source photos at iNaturalist "original" size and re-run the Vision cut-out
import json,os,re,subprocess,urllib.request,time
UA={'User-Agent':'roku-reef-screensaver-prototype/0.1 (personal project)'}
srcs=sorted({v['src'] for v in json.load(open('assets_src/coral_config.json')).values()})
for src in srcs:
    out=f'assets_src/cut_hi/{src}.png'
    if os.path.exists(out): continue
    m=re.match(r'i_(.+)_(\d+)$',src)
    if not m: continue
    r=json.load(open(f'assets_src/inat/{m.group(1)}.json'))[int(m.group(2))]
    url=r['url'].replace('/large.','/original.');fn=f'assets_src/raw_hi/{src}.jpg'
    if src=='i_fan_13':  # black background -> luma key instead of Vision
        pass
    try:
        if not os.path.exists(fn): open(fn,'wb').write(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90).read());time.sleep(.6)
    except Exception as e: print('skip',src,e);continue
    if src=='i_fan_13': r2=subprocess.run(['python3','tools/lumakey.py',fn,out,'28','60'],capture_output=True,text=True)
    else: r2=subprocess.run(['osascript','-l','JavaScript','tools/cutout.js',os.path.abspath(fn),os.path.abspath(out),'all'],capture_output=True,text=True)
    print(src,(r2.stdout+r2.stderr).strip()[:60],flush=True)
