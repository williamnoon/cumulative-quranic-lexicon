#!/usr/bin/env python3
"""Generate the 114-day reverse-surah cumulative Qur'anic vocabulary model."""

from __future__ import annotations
import argparse,csv,hashlib,json,re
from collections import defaultdict
from pathlib import Path

SOURCE_URL="https://raw.githubusercontent.com/bnjasim/quranic-corpus/master/quranic-corpus-morphology-0.4.txt"
SOURCE_REPO="bnjasim/quranic-corpus"; SOURCE_PATH="quranic-corpus-morphology-0.4.txt"
SOURCE_BLOB_SHA="b91cec6e95d5e0306550b4aedacc7380dc71152a"; SOURCE_VERSION="Quranic Arabic Corpus v0.4"
LOC_RE=re.compile(r"^\((\d+):(\d+):(\d+):(\d+)\)$"); FEATURE_KV_RE=re.compile(r"(?:^|\|)(LEM|ROOT):([^|]+)")
BW_TO_AR={"'":"ء",">":"أ","&":"ؤ","<":"إ","}":"ئ","A":"ا","b":"ب","p":"ة","t":"ت","v":"ث","j":"ج","H":"ح","x":"خ","d":"د","*":"ذ","r":"ر","z":"ز","s":"س","$":"ش","S":"ص","D":"ض","T":"ط","Z":"ظ","E":"ع","g":"غ","_":"ـ","f":"ف","q":"ق","k":"ك","l":"ل","m":"م","n":"ن","h":"ه","w":"و","Y":"ى","y":"ي","F":"ً","N":"ٌ","K":"ٍ","a":"َ","u":"ُ","i":"ِ","~":"ّ","o":"ْ","^":"ٓ","#":"ٔ","`":"ٰ","{":"ٱ",":":"ۜ","@":"۟",'"':"۠","[":"ۢ",";":"ۣ",",":"ۥ",".":"ۦ","!":"ۨ","-":"۪","+":"۫","%":"۬","]":"ۭ"}
def ar(v): return None if v is None else ''.join(BW_TO_AR.get(c,c) for c in v)
def feat(s,k):
    for a,b in FEATURE_KV_RE.findall(s):
        if a==k:return b

def parse(path):
    ss=defaultdict(list); ww=defaultdict(set); seg=miss=0
    with path.open(encoding='utf-8') as f:
        for row in csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE):
            if len(row)<4: continue
            m=LOC_RE.match(row[0].strip())
            if not m: continue
            s,a,w,g=map(int,m.groups()); seg+=1; key=(s,a,w); ww[s].add(key)
            if not row[3].startswith('STEM|'): continue
            l=feat(row[3],'LEM'); r=feat(row[3],'ROOT'); miss += (l is None)
            ss[s].append({'word_key':key,'stem_form':row[1],'lemma':l,'root':r})
    return ss,ww,seg,miss

def display(vals): return [{'buckwalter':v,'arabic':ar(v)} for v in sorted(vals)]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1048576),b''): h.update(c)
    return h.hexdigest()

def build(ss,ww):
    kv,kr,ks=set(),set(),set(); days=[]
    for day,s in enumerate(range(114,0,-1),1):
        stems=ss.get(s,[]); occ=[x['lemma'] for x in stems if x['lemma']]; vocab=set(occ); roots={x['root'] for x in stems if x['root']}; raws={x['stem_form'] for x in stems}
        nv=vocab-kv; cv=vocab&kv; nr=roots-kr; cr=roots&kr; ns=raws-ks; cs=raws&ks
        wl=defaultdict(set)
        for x in stems:
            if x['lemma']: wl[x['word_key']].add(x['lemma'])
        known_tokens=sum(1 for z in wl.values() if z and z.issubset(kv)); total_tokens=len(wl)
        # Direct verification mapping: every new lemma -> every QAC root attached to that lemma in this surah.
        lemma_roots=defaultdict(set)
        for x in stems:
            if x['lemma'] in nv and x['root']: lemma_roots[x['lemma']].add(x['root'])
        new_vocab_with_new_root={l for l,rs in lemma_roots.items() if rs & nr}
        new_vocab_with_known_root={l for l,rs in lemma_roots.items() if rs and not (rs & nr)}
        new_vocab_without_root={l for l in nv if not lemma_roots.get(l)}
        root_novelty_map=[{'lemma_buckwalter':l,'lemma_arabic':ar(l),'roots':[{'buckwalter':r,'arabic':ar(r),'root_is_new':r in nr} for r in sorted(lemma_roots.get(l,set()))]} for l in sorted(nv)]
        d={'day':day,'surah':s,'orthographic_word_tokens':len(ww.get(s,set())),'lexical_word_tokens':total_tokens,'distinct_vocabulary_items':len(vocab),'carried_vocabulary_items':len(cv),'new_vocabulary_items':len(nv),'known_before_vocabulary_items':len(kv),'known_after_vocabulary_items':len(kv|vocab),'known_lexical_word_tokens':known_tokens,'new_lexical_word_tokens':total_tokens-known_tokens,'known_lexical_word_token_coverage_pct':round(100*known_tokens/total_tokens,4) if total_tokens else 0,'distinct_roots':len(roots),'carried_roots':len(cr),'new_roots':len(nr),'known_before_roots':len(kr),'known_after_roots':len(kr|roots),'distinct_raw_stem_forms':len(raws),'carried_raw_stem_forms':len(cs),'new_raw_stem_forms':len(ns),'known_before_raw_stem_forms':len(ks),'known_after_raw_stem_forms':len(ks|raws),'new_vocabulary_item_list':display(nv),'new_root_list':display(nr),'new_vocabulary_with_new_root_count':len(new_vocab_with_new_root),'new_vocabulary_with_known_root_count':len(new_vocab_with_known_root),'new_vocabulary_without_root_count':len(new_vocab_without_root),'new_vocabulary_root_novelty_map':root_novelty_map}
        days.append(d); kv|=vocab; kr|=roots; ks|=raws
    return days

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True,type=Path); ap.add_argument('--out-dir',default=Path('data/generated'),type=Path); a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    ss,ww,seg,miss=parse(a.source); days=build(ss,ww)
    assert len(days)==114 and [d['surah'] for d in days]==list(range(114,0,-1)); assert seg==128219 and sum(len(x) for x in ww.values())==77429; assert days[-1]['known_after_vocabulary_items']==4832 and days[-1]['known_after_roots']==1642
    b=days[112]; assert b['new_vocabulary_items']==145 and b['new_roots']==22
    assert b['new_vocabulary_with_new_root_count']+b['new_vocabulary_with_known_root_count']+b['new_vocabulary_without_root_count']==145
    meta={'study_order':'114->1','source':{'name':SOURCE_VERSION,'repository':SOURCE_REPO,'path':SOURCE_PATH,'blob_sha':SOURCE_BLOB_SHA,'download_url':SOURCE_URL,'download_sha256':sha(a.source)},'parsed_segment_rows':seg,'parsed_stem_rows':sum(len(v) for v in ss.values()),'stems_missing_lemma':miss,'orthographic_word_positions':sum(len(x) for x in ww.values())}
    (a.out_dir/'cumulative-vocabulary.json').write_text(json.dumps({'metadata':meta,'days':days},ensure_ascii=False,indent=2)+'\n')
    bb=dict(b); bb['benchmark']='Surah 2 Day 113 after Surahs 114 through 3'; (a.out_dir/'baqarah-day-113.json').write_text(json.dumps({'metadata':meta,'result':bb},ensure_ascii=False,indent=2)+'\n')
    summary={'whole_quran':{'orthographic_word_positions':77429,'canonical_vocabulary_items':4832,'roots':1642},'baqarah_day_113':{k:v for k,v in b.items() if not k.endswith('_list') and not k.endswith('_map')}}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(summary,ensure_ascii=False,indent=2))
    fields=[k for k,v in days[0].items() if not isinstance(v,(list,dict))]
    with (a.out_dir/'cumulative-vocabulary.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow({k:d[k] for k in fields}) for d in days]
if __name__=='__main__': main()
