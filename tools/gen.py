import json, base64, sys
sys.path.insert(0,'/workspace/work/meta'); import meta
from concurrent.futures import ThreadPoolExecutor
POSTER=("Taiwan government public-service campaign poster illustration: bright cheerful flat vector art, thick clean dark outlines, "
 "sunshine rays background in pastel pink and warm yellow, small hearts and flowers, everyone smiling, glossy optimistic. "
 "Leave the top third fairly simple for a headline. No text, no letters, no numbers, no logos.")
REAL=("Same flat vector art with thick clean dark outlines, but a quiet realistic everyday moment in Taiwan, muted dim colors, ordinary, "
 "no sunshine rays, no hearts. No readable text, no letters, no logos.")
REF=("Character reference sheet, single full-body figure standing on plain off-white background, flat vector art, thick clean dark outlines, soft colors. No text.")
def run(j):
    try:
        p=j["p"]+" "+{"poster":POSTER,"real":REAL,"ref":REF}[j["kind"]]
        size=j.get("size","1024x1024")
        if j.get("refs"):
            imgs=[{"image_url":"data:image/webp;base64,"+base64.b64encode(open(r,'rb').read()).decode()} for r in j["refs"]]
            r=meta.post("/images/edits",{"model":"muse-image-1.0","prompt":p,"images":imgs,"n":1,"size":size,"output_format":"webp"})
            meta.log("image","muse-image-1.0",0.01,j["out"]); open(j["out"],"wb").write(base64.b64decode(r["data"][0]["b64_json"]))
        else: meta.image(p,j["out"],size=size,note=j["out"])
        return j["out"]+" ok"
    except BaseException as e: return j["out"]+" FAIL "+str(e)[:200]
jobs=json.load(open(sys.argv[1]))
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(run,jobs): print(r,flush=True)
