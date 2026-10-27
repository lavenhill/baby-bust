from playwright.sync_api import sync_playwright
import time,sys
seq=sys.argv[1];out=sys.argv[2];lang=sys.argv[3] if len(sys.argv)>3 else 'zh'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/chromium")
    pg=b.new_page(viewport={"width":390,"height":780},locale="zh-TW")
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/fonts.*/**",lambda r:r.abort())
    pg.goto("file://"+__import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__file__),"..","index.html"))+"",wait_until="domcontentloaded");time.sleep(.5)
    if lang=='en': pg.click("#lang");time.sleep(.3)
    pg.click(".title button");time.sleep(5)
    pg.click(".ctl .btn");time.sleep(4);i=0;shots=0
    while i<7:
        w=pg.locator(".wall:not(.done)")
        if w.count():
            time.sleep(1.2);box=w.last.bounding_box();y=box["y"]+(box["height"]*.25 if seq[i]=="U" else box["height"]*.75)
            pg.mouse.click(box["x"]+190,y);time.sleep(.5)
            if i==0: pg.screenshot(path=out+"_wall0.png")
            try: pg.locator(".ctl .btn").last.click(timeout=4000)
            except Exception as e: pg.screenshot(path=out+"_err.png");print("ERR at",i,pg.evaluate("S.node"),errs);break
            i+=1;time.sleep(5)
        else: time.sleep(.5)
    time.sleep(14)
    for bt in pg.locator(".qs button").all(): bt.click()
    time.sleep(.5);pg.screenshot(path=out+"_full.png",full_page=True);print(errs,pg.evaluate("document.body.scrollHeight"))
