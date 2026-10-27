"""Headless playtest for the one-screen-per-beat build.
usage: python3 tools/play.py PATH(7 x U/D) OUTPREFIX [zh|en] [WxH] [shots]
Checks every screen for overflow (content taller than the screen) and page errors."""
from playwright.sync_api import sync_playwright
import time,sys,os,json
seq=sys.argv[1];out=sys.argv[2];lang=sys.argv[3] if len(sys.argv)>3 else 'zh'
W,Hh=map(int,(sys.argv[4] if len(sys.argv)>4 else '390x780').split('x'));shots=len(sys.argv)>5
url="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),"..","index.html"))
OVER="""()=>{const s=H.list[H.i];if(!s)return null;const bad=[];
 if(s.scrollHeight>s.clientHeight+2)bad.push('screen '+s.scrollHeight+'>'+s.clientHeight);
 s.querySelectorAll('.chat').forEach(c=>{if(c.scrollHeight>c.clientHeight+2&&!s.classList.contains('wall'))bad.push('chat clipped '+c.scrollHeight+'>'+c.clientHeight)});
 s.querySelectorAll('.h1,.sub,.tag,.aside,.bar').forEach(e=>{const r=e.getBoundingClientRect(),p=s.getBoundingClientRect();if(r.right>p.right+1||r.left<p.left-1)bad.push(e.className+' wide')});
 return bad}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/chromium")
    pg=b.new_page(viewport={"width":W,"height":Hh},locale="zh-TW",has_touch=False)
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/fonts.*/**",lambda r:r.abort())
    pg.goto(url,wait_until="domcontentloaded");time.sleep(.6)
    if lang=='en': pg.click("#lang");time.sleep(.3)
    report=[];i=0;n=0;last=None
    def shot(tag):
        if shots: pg.screenshot(path=f"{out}_{n:02d}_{tag}.png")
    for guard in range(160):
        if pg.evaluate("S.ended===true"):
            time.sleep(.6);bad=pg.evaluate(OVER);report.append(('end',bad));shot('end');break
        info=pg.evaluate("()=>{const s=H.list[H.i];return {k:H.i,wall:s.classList.contains('wall')&&!s.classList.contains('done'),btn:!!s.querySelector(':scope>.btn, .title .btn'),tap:!!s.querySelector('.tapnext'),qs:!!s.querySelector('.qs button:not(:disabled)')}}")
        if pg.evaluate("()=>!!H.list[H.i].querySelector('.lan:not(.fly) .mate:not(.seen)')"):
            for m in pg.locator('.scr:not(.below):not(.above) .lan .mate').all(): m.click();time.sleep(.25)
            bad=pg.evaluate(OVER);report.append(('lanterns',bad));shot('lan');continue
        if info['wall']:
            time.sleep(.7);bad=pg.evaluate(OVER);report.append((pg.evaluate("S.node")+' wall',bad));shot('wall')
            box=pg.locator('#stage').bounding_box();y=box['y']+box['height']*(.25 if seq[i]=='U' else .75)
            pg.mouse.click(box['x']+box['width']/2,y);time.sleep(.5);shot('pick')
            pg.locator('.scr.wall:not(.done) .bar button').click();i+=1;n+=1;time.sleep(.9);continue
        if info['btn']:
            time.sleep(.4);pg.locator('.scr:not(.below):not(.above) .btn').last.click();n+=1;time.sleep(.9);continue
        if info['tap']:
            if info['qs']: pg.locator('.scr:not(.below):not(.above) .qs button').first.click();time.sleep(.3)
            bad=pg.evaluate(OVER);report.append((f"screen {info['k']}",bad));shot('s')
            pg.mouse.click(pg.locator('#stage').bounding_box()['x']+20,60);n+=1;time.sleep(.7);continue
        time.sleep(.4)
    fails=[r for r in report if r[1]]
    print(json.dumps({"vp":f"{W}x{Hh}","lang":lang,"path":seq,"screens":len(report),"ended":pg.evaluate("S.ended===true"),"errors":errs,"overflow":fails},ensure_ascii=False))
