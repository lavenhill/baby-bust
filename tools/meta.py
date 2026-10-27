#!/usr/bin/env python3
"""Shared Meta Model API helper with spend ledger. Key injected on the wire (MODEL_API_KEY sentinel)."""
import json, os, sys, time, base64, urllib.request, urllib.error
BASE="https://api.meta.ai/v1"; LEDGER="ledger.jsonl"; CAP=140.0
PRICE={"muse-spark-1.3":(1.25,4.25),"muse-spark-1.2":(1.25,4.25),"muse-spark-1.3-contributor":(.10,.20),"muse-wonder-1.0":(4.0,20.0)}
def spent():
    t=0.0
    if os.path.exists(LEDGER):
        for l in open(LEDGER): t+=json.loads(l)["usd"]
    return t
def log(kind,model,usd,note=""):
    open(LEDGER,"a").write(json.dumps({"t":time.strftime("%Y-%m-%d %H:%M:%S"),"kind":kind,"model":model,"usd":round(usd,6),"note":note})+"\n")
def post(path,body,timeout=300):
    if spent()>=CAP: raise SystemExit(f"cap ${CAP} reached")
    req=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+os.environ.get("MODEL_API_KEY",""),"Content-Type":"application/json"})
    for i in range(5):
        try: return json.load(urllib.request.urlopen(req,timeout=timeout))
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503) and i<4: time.sleep(2**i); continue
            raise SystemExit(f"HTTP {e.code}: {e.read()[:500]}")
def chat(messages,model="muse-spark-1.3",max_tokens=4000,json_schema=None,reasoning=None,note=""):
    b={"model":model,"messages":messages,"max_tokens":max_tokens}
    if json_schema: b["response_format"]={"type":"json_schema","json_schema":{"name":"out","schema":json_schema,"strict":False}}
    if reasoning: b["reasoning_effort"]=reasoning
    r=post("/chat/completions",b); u=r.get("usage",{}); pi,po=PRICE.get(model,(1.25,4.25))
    log("chat",model,u.get("prompt_tokens",0)/1e6*pi+u.get("completion_tokens",0)/1e6*po,note)
    return r["choices"][0]["message"]["content"]
def image(prompt,out,size="1024x1536",fmt="webp",note=""):
    r=post("/images/generations",{"model":"muse-image-1.0","prompt":prompt,"n":1,"size":size,"output_format":fmt})
    log("image","muse-image-1.0",0.01,note or out)
    open(out,"wb").write(base64.b64decode(r["data"][0]["b64_json"])); return out
if __name__=="__main__":
    if sys.argv[1:]==["spent"]: print(f"${spent():.4f}")
    else: print(chat([{"role":"user","content":" ".join(sys.argv[1:])}]))
