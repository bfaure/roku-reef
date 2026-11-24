# make_credits.py -> CREDITS.md : attribution for every photo used in poc/assets (from saved search results)
import json,os,re,glob
used=set()
for cfg in ['assets_src/fish_config.json','assets_src/coral_config.json']:
    for v in json.load(open(cfg)).values(): used.add(v['src'])
# fx assets (rays, turtles, jellies, crustaceans, octopus) are recorded by source name in this list
fx_src=['i_turtle_15','i_turtle_23','i_hawksbill_29','i_jelly_18','i_jelly2_2','i_eagleray_6','i_eagleray_19','i_eagleray_23','i_manta_3','i_manta_9',
        'i_crab_7','i_crab_8','i_crab2_3','i_hermit_22','i_lobster2_1','i_shrimp_5','i_octopus2_23','i_octopus3_22','i_octopus4_20','i_moray_27','i_fan_13',
        'i_f_yellowtang_31','puffer_0','lion_1']  # + frontal photos (poc/assets/front)
used.update(fx_src)
rows=[]
for src in sorted(used):
    if src.startswith('i_'):
        m=re.match(r'i_(.+)_(\d+)$',src);k,i=m.group(1),int(m.group(2));import os;jp=f'assets_src/inat/{k}.json';jp=jp if os.path.exists(jp) else f'assets_src/inat_front/{k}.json';r=json.load(open(jp))[i]
        rows.append((src,'iNaturalist',r['license'].upper().replace('CC-','CC '),r['attribution'],r['obs']))
    else:
        m=re.match(r'(.+)_(\d+)$',src);k,i=m.group(1),int(m.group(2));r=json.load(open(f'assets_src/candidates/{k}.json'))[i]
        artist=re.sub('<[^>]*$','',re.sub('<[^>]+>','',r['artist'])).strip() or 'see source page'
        rows.append((src,'Wikimedia Commons',r['license'],artist,'https://commons.wikimedia.org/wiki/'+r['title'].replace(' ','_')))
with open('CREDITS.md','w') as f:
    f.write('# Photo credits\n\nAll creature and coral imagery is cut out from openly licensed photographs (CC0, CC BY, CC BY-SA, or public domain).\n')
    f.write('Cut-outs were made automatically (Apple Vision subject lifting), then flipped/rotated/trimmed and colour-graded.\n')
    f.write('CC BY / BY-SA licenses require attribution if this project is distributed; BY-SA derivatives must keep the same license.\n\n')
    f.write('| Source id | From | License | Author / attribution | Original |\n|---|---|---|---|---|\n')
    for s,frm,lic,a,url in rows: f.write(f'| {s} | {frm} | {lic} | {a.replace("|","/")} | {url} |\n')
print(len(rows),'credits written')
