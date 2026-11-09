import csv,json,re,sys
from collections import defaultdict
sys.path.insert(0,'/home/claude/cumulative-quranic-lexicon/scripts')
from build_cumulative_vocab import ar, feat, LOC_RE
QAC='/home/claude/qac/qac.txt'; QC='/home/claude/qcom'
names={r[0]:r for r in json.load(open('/home/claude/cumulative-quranic-lexicon/data/surahs.json'))}
# --- QAC per word ---
wl=defaultdict(list); wtags=defaultdict(list); lroot={}; segs=defaultdict(int)
for row in csv.reader(open(QAC,encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE):
    if len(row)<4: continue
    m=LOC_RE.match(row[0].strip())
    if not m: continue
    s,a,w,g=map(int,m.groups()); k=(s,a,w); segs[k]+=1
    if not row[3].startswith('STEM|'): continue
    t=row[3]
    l=feat(t,'LEM'); r=feat(t,'ROOT')
    if l:
        if l not in wl[k]: wl[k].append(l)
        if r and l not in lroot: lroot[l]=r
    wtags[k].append(t)
# --- quran.com words ---
Q={}; gl={}
for s in range(1,115):
    vs=json.load(open(f'{QC}/{s}.json')); Q[s]=vs
    for v in vs:
        for loc,txt,tr in v['w']:
            s_,a_,w_=map(int,loc.split(':')); gl[(s_,a_,w_)]=(txt,tr)
assert len(gl)==77429
# --- lemma ids in learning order ---
lid={}; L=[]; freq=defaultdict(int)
for k,ls in wl.items():
    for l in ls: freq[l]+=1
from collections import Counter
cands=defaultdict(Counter); anyg=defaultdict(Counter)
for k,ls in wl.items():
    tr=gl[k][1].strip()
    for l in ls:
        anyg[l][tr]+=1
        if segs[k]==1 and len(ls)==1: cands[l][tr]+=1
def clean(g):
    h=re.sub(r'^\s*((\([^)]*\)|\[[^\]]*\])\s*)+','',g).strip()
    return h or g.strip()
def best(l,fallback):
    c=Counter()
    for g,n in (cands[l] or anyg[l]).items(): c[clean(g)]+=n
    return c.most_common(1)[0][0] if c else clean(fallback)
days=[]; known=set()
for day,s in enumerate(range(114,0,-1),1):
    new=[]; keys=sorted(k for k in wl if k[0]==s)
    for k in keys:
        for l in wl[k]:
            if l not in lid:
                lid[l]=len(L); txt,tr=gl[k]
                L.append([ar(l),ar(lroot.get(l)) or '',best(l,tr),day,freq[l],k[1],k[2],tr])
                new.append(lid[l])
    vocab={lid[l] for k in keys for l in wl[k]}
    tok=[k for k in keys if wl[k]]
    kn=sum(1 for k in tok if all(lid[l] in known for l in wl[k]))
    pk=round(100*kn/len(tok),1) if tok else 0
    known|=vocab
    days.append([s,names[s][1],names[s][2],names[s][3],sum(len(v['w']) for v in Q[s]),len(new),len(known),pk,new,sorted(vocab)])
assert len(L)==4832, len(L)
# --- grammar concepts: first appearance in study order ---
CON=[
 ('PERF','Past tense','Something already done. The base shape of the verb: فَعَلَ — he did.',lambda t:'POS:V' in t and '|PERF' in t and '|PASS' not in t),
 ('IMPF','Present / future tense','Something happening or going to happen. A letter is added at the front: يَفْعَلُ — he does, he will do.',lambda t:'POS:V' in t and '|IMPF' in t and '|PASS' not in t),
 ('IMPV','The command','Telling someone to do it now: اِفْعَلْ — do! The Qurʾan opens your study with one: قُلْ — say!',lambda t:'POS:V' in t and '|IMPV' in t),
 ('PASS_V','Passive verb','The doer is hidden; the action is what matters: فُعِلَ — it was done.',lambda t:'POS:V' in t and '|PASS' in t),
 ('II','Verb Form II · فَعَّلَ','Double the middle letter to make the action strong, repeated, or done to someone else.',lambda t:'POS:V' in t and '(II)' in t),
 ('III','Verb Form III · فَاعَلَ','A long ā after the first letter: doing it with or toward someone else.',lambda t:'POS:V' in t and '(III)' in t),
 ('IV','Verb Form IV · أَفْعَلَ','An alif in front makes the verb causative: to make something happen.',lambda t:'POS:V' in t and '(IV)' in t),
 ('V','Verb Form V · تَفَعَّلَ','Form II turned back on yourself: to take something on, step by step.',lambda t:'POS:V' in t and '(V)' in t),
 ('VI','Verb Form VI · تَفَاعَلَ','Doing it to each other, together.',lambda t:'POS:V' in t and '(VI)' in t),
 ('VII','Verb Form VII · اِنْفَعَلَ','Something happens to the subject: it breaks, it splits.',lambda t:'POS:V' in t and '(VII)' in t),
 ('VIII','Verb Form VIII · اِفْتَعَلَ','A tā inside the word: doing it for yourself, with effort.',lambda t:'POS:V' in t and '(VIII)' in t),
 ('X','Verb Form X · اِسْتَفْعَلَ','Istaf- in front: to seek, to ask for, to consider something so.',lambda t:'POS:V' in t and '(X)' in t),
 ('ACT','Active participle · فَاعِل','The one who does it: كَاتِب — a writer.',lambda t:'|ACT_PCPL' in t or ('POS:N|ACT' in t) or ('POS:ADJ|ACT' in t)),
 ('PASS_P','Passive participle · مَفْعُول','The one it is done to: مَكْتُوب — written.',lambda t:'|PASS_PCPL' in t or ('POS:N|PASS' in t) or ('POS:ADJ|PASS' in t)),
 ('VN','Verbal noun · مَصْدَر','The action as a noun: كِتَابَة — writing.',lambda t:'POS:N|VN' in t),
 ('DUAL','The dual','Arabic has a form for exactly two: ـَانِ / ـَيْنِ.',lambda t:re.search(r'\|[123]?[MF]?D($|\|)',t) is not None),
]
G=[]
for code,title,expl,test in CON:
    hit=None
    for day,s in enumerate(range(114,0,-1),1):
        for k in sorted(k for k in wtags if k[0]==s):
            if any(test(t) for t in wtags[k]): hit=(day,k); break
        if hit: break
    if hit:
        day,k=hit; txt,tr=gl[k]; G.append([code,day,title,expl,txt,tr,k[0],k[1]])
G.sort(key=lambda g:g[1])
# --- full text: per surah list of ayahs, each list of [text, lemmaId|-1, gloss] ---
T={}
for s in range(1,115):
    T[s]=[[[txt,(lid[wl[(s,a,w)][0]] if wl[(s,a,w)] else -1),tr] for loc,txt,tr in v['w'] for a,w in [tuple(map(int,loc.split(':')[1:]))]] for v in Q[s]]
out={'days':days,'L':L,'G':G,'T':T}
js=json.dumps(out,ensure_ascii=False,separators=(',',':'))
open('/home/claude/proto/course.json','w').write(js)
print(len(js)/1e6,'MB', 'concepts',[(g[0],g[1]) for g in G])
print(days[0][:8], L[:3])
