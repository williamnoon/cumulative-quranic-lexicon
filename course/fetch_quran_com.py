import json,urllib.request,concurrent.futures as cf,os,time
OUT=os.environ.get('QCOM_DIR','/tmp/qcom'); os.makedirs(OUT,exist_ok=True)
def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'curl/8.5.0','Accept':'application/json'}),timeout=40) as r: return json.load(r)
        except Exception as e: time.sleep(2*(i+1)); err=e
    raise err
def chapter(n):
    p=f'{OUT}/{n}.json'
    if os.path.exists(p): return n
    page,verses=1,[]
    while page:
        d=get(f'https://api.quran.com/api/v4/verses/by_chapter/{n}?words=true&word_fields=text_uthmani,location&per_page=50&page={page}')
        for v in d['verses']:
            verses.append({'k':v['verse_key'],'w':[[w['location'],w['text_uthmani'],(w.get('translation') or {}).get('text','')] for w in v['words'] if w['char_type_name']=='word']})
        page=d['pagination']['next_page']
    json.dump(verses,open(p,'w'),ensure_ascii=False); return n
with cf.ThreadPoolExecutor(3) as ex:
    for n in ex.map(chapter,range(1,115)): pass
tot=0
for n in range(1,115): tot+=sum(len(v['w']) for v in json.load(open(f'{OUT}/{n}.json')))
print('words',tot)
