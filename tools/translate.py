import json,sys
sys.path.insert(0,'/workspace/work/meta'); import meta
import content_zh as C
strs=set()
def add(s):
    if isinstance(s,str) and s: strs.add(s)
for w,t in C.OPEN: add(t)
for n in C.NODES.values():
    for s in n['ask']: add(s)
    for w,t in n['setup']: add(t)
    for h in 'UD':
        for k in ('who','h1','sub','aside','tag'): add(n[h].get(k))
        add(n['boss'][h]); c=n['chat'][h]; c and add(c[1])
for s in C.LIFE: add(s)
for k,v in C.UI.items():
    if isinstance(v,list): [add(x) for x in v]
    else: add(v)
for k,v in C.TAG.items(): add(v); add(k)
strs=sorted(strs)
p=("Translate each Traditional Chinese string from a Taiwanese narrative game into natural, concise English. Names romanize as: 老顏 Lao Yan, 阿芳 A-Fang, 家豪 Jiahao, 宜君 Yijun, 志豪 Zhihao, 佩珊 Peishan. "
 "Poster headlines (short slogans) should read like punchy government campaign slogans. Keep {n} and {who} placeholders. 妳 means you (Lao Yan). Output JSON {\"en\":[...]} with exactly one English string per input, same order.\n\n"+json.dumps(strs,ensure_ascii=False))
for i in range(3):
    r=meta.chat([{"role":"user","content":p}],json_schema={"type":"object","properties":{"en":{"type":"array","items":{"type":"string"}}}},max_tokens=16000,reasoning="low",note="v2 translate")
    if r:
        e=json.loads(r)['en']; print(len(e)); d=dict(zip(strs,e)) if len(e)==len(strs) else {}; miss=[s for s in strs if not d.get(s)]
        print(len(strs),'missing',len(miss),miss[:5]); json.dump(d,open('en.json','w'),ensure_ascii=False,indent=0); break
