import json, base64, sys, meta
from concurrent.futures import ThreadPoolExecutor
STYLE=("Soft colored-pencil illustration on off-white paper, loose hand-drawn lines, muted palette of faded propaganda pink (#E8A9B0), warm grey and ink (#3A3434), "
"gentle and humane, like a picture-book about ordinary Taiwanese people in Kaohsiung/Taipei. No text, no letters, no numbers, no logos anywhere. ")
TALL="Tall vertical composition, figure centered, empty paper margins. "
def edit(prompt,refs,out,size="1024x2048"):
    imgs=[{"image_url":"data:image/webp;base64,"+base64.b64encode(open(r,'rb').read()).decode()} for r in refs]
    r=meta.post("/images/edits",{"model":"muse-image-1.0","prompt":prompt,"images":imgs,"n":1,"size":size,"output_format":"webp"})
    meta.log("image","muse-image-1.0",0.01,out); open(out,"wb").write(base64.b64decode(r["data"][0]["b64_json"])); return out
def job(j):
    try:
        if j.get("refs"): edit(j["p"],j["refs"],j["out"],j.get("size","1024x2048"))
        else: meta.image(j["p"],j["out"],size=j.get("size","1024x2048"))
        return j["out"]+" ok"
    except BaseException as e: return j["out"]+" FAIL "+str(e)[:200]
jobs=json.load(open(sys.argv[1]))
for j in jobs: j["p"]=j["p"]+" "+STYLE+(TALL if j.get("size","1024x2048")=="1024x2048" else "")
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(job,jobs): print(r,flush=True)
