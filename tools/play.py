"""Headless playtest for the one-screen-per-beat build.
usage: python3 tools/play.py PATH(7 x U/D) OUTPREFIX [zh|en] [WxH] [shots] [kb] [rm]
 rm = prefers-reduced-motion. kb = pick with keys (1/2 and ↑/↓ alternating) + Enter instead of mouse. Wall checks: tap-only (no ⇅), hint only in 2018, pick lands before 發布.
Checks every screen for overflow (content taller than the screen) and page errors."""
from playwright.sync_api import sync_playwright
import time,sys,os,json
seq=sys.argv[1];out=sys.argv[2];lang=sys.argv[3] if len(sys.argv)>3 else 'zh'
W,Hh=map(int,(sys.argv[4] if len(sys.argv)>4 else '390x780').split('x'));extra=sys.argv[5:];kb='kb' in extra;rm='rm' in extra;shots=any(a not in('kb','rm') for a in extra)
url="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),"..","index.html"))
OVER="""()=>{const s=H.list[H.i];if(!s)return null;const bad=[];
 if(s.scrollHeight>s.clientHeight+2)bad.push('screen '+s.scrollHeight+'>'+s.clientHeight);
 s.querySelectorAll('.chat').forEach(c=>{if(c.scrollHeight>c.clientHeight+2&&!s.classList.contains('wall'))bad.push('chat clipped '+c.scrollHeight+'>'+c.clientHeight)});
 s.querySelectorAll('.h1,.sub,.tag,.aside,.bar,.hint').forEach(e=>{if(!e.getClientRects().length)return;const r=e.getBoundingClientRect(),p=s.getBoundingClientRect();if(r.right>p.right+1||r.left<p.left-1)bad.push(e.className+' wide')});
 return bad}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/chromium")
    pg=b.new_page(viewport={"width":W,"height":Hh},locale="zh-TW",has_touch=False,reduced_motion="reduce" if rm else "no-preference")
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/fonts.*/**",lambda r:r.abort())
    pg.goto(url,wait_until="domcontentloaded");time.sleep(.6)
    if lang=='en': pg.click("#lang");time.sleep(.3)
    report=[];i=0;n=0;last=None
    def shot(tag):
        if shots: pg.screenshot(path=f"{out}_{n:02d}_{tag}.png")
    for guard in range(500):
        if pg.evaluate("S.ended===true"):
            time.sleep(.6);bad=pg.evaluate(OVER);report.append(('end',bad));shot('end');break
        info=pg.evaluate("()=>{const s=H.list[H.i];return {k:H.i,wall:s.classList.contains('wall')&&!s.classList.contains('done'),btn:!!s.querySelector(':scope>.btn, .title .btn'),tap:!!s.querySelector('.tapnext'),qs:!!s.querySelector('.qs button:not(:disabled)')}}")
        if pg.evaluate("()=>!!H.list[H.i].querySelector('.lan:not(.fly) .mate:not(.seen)')&&!H.list[H.i].querySelector('.l26')"):
            for m in pg.locator('.scr:not(.below):not(.above) .lan .mate').all(): m.click();time.sleep(.25)
            bad=pg.evaluate(OVER);report.append(('lanterns',bad));shot('lan');continue
        if info['wall']:
            time.sleep(.7);bad=pg.evaluate(OVER);report.append((pg.evaluate("S.node")+' wall',bad));shot('wall')
            nd,ht,glyph=pg.evaluate("()=>{const s=H.list[H.i],h=s.querySelector('.hint');return [S.node,h?h.textContent.trim():null,[...s.querySelectorAll('.hint,.bar')].some(e=>e.textContent.includes('⇅'))]}")
            want={'zh':'點一張留下','en':'Tap one to keep'}[lang] if nd=='y2018' else None
            if ht!=want or glyph: report.append((nd+' hint',[f'hint={ht!r} want={want!r} glyph={glyph}']))
            if kb: pg.keyboard.press(('1' if seq[i]=='U' else '2') if i%2==0 else ('ArrowUp' if seq[i]=='U' else 'ArrowDown'))
            else:
                box=pg.locator('#stage').bounding_box();y=box['y']+box['height']*(.25 if seq[i]=='U' else .75)
                pg.mouse.click(box['x']+box['width']/2,y)
            time.sleep(.5);shot('pick')
            if not pg.evaluate(f"()=>!!H.list[H.i].querySelector('.half.{seq[i]}.on')"): report.append((nd+' pick',['pick did not select '+seq[i]]))
            if kb: pg.keyboard.press('Enter')
            else: pg.locator('.scr.wall:not(.done) .bar button').click()
            time.sleep(.3);shot('snip');i+=1;n+=1;time.sleep(.9);continue
        if info['btn']:
            time.sleep(.4);pg.locator('.scr:not(.below):not(.above) .btn').last.click();n+=1;time.sleep(.9);continue
        if info['tap']:
            if info['qs'] and not pg.evaluate("()=>!!H.list[H.i].querySelector('.qs button:disabled')"): shot('dm')
            if info['qs']: pg.locator('.scr:not(.below):not(.above) .qs button').first.click();time.sleep(.3)
            bad=pg.evaluate(OVER);report.append((f"screen {info['k']}",bad));shot('s')
            pg.mouse.click(pg.locator('#stage').bounding_box()['x']+20,60);n+=1;time.sleep(.7);continue
        time.sleep(.4)
    # lines-r3 checks: ending DMs (gone = cold, hurt once = warm), no blank bubbles, no outsider forward screens
    dm=pg.evaluate("""()=>H.list.filter(s=>s.querySelector('.who')).map(s=>{const b=s.querySelector('.chat .bub');return {who:s.querySelector('.who b').textContent,cold:!!(b&&b.classList.contains('gone')),len:b?b.textContent.length:0}})""")
    exp=pg.evaluate("()=>({gone:S.gone.slice(),once:Object.keys(S.hurt).filter(m=>S.hurt[m]===1&&!S.gone.includes(m))})")
    blank=pg.evaluate("()=>H.list.flatMap(s=>[...s.querySelectorAll('.bub')]).filter(b=>{const c=b.cloneNode(true);c.querySelectorAll('i').forEach(i=>i.remove());return !c.textContent.trim()&&!b.querySelector('img')}).length")
    fw=pg.evaluate("()=>H.list.filter(s=>s.querySelector('.fw')).length")
    if blank: report.append(('blank bubbles',[blank]))
    if fw: report.append(('outsider forward screens',[fw]))
    if len(dm)!=len(exp['gone'])+len(exp['once']) or any(d['len']<20 for d in dm): report.append(('dm mismatch',[dm,exp]))
    fails=[r for r in report if r[1]]
    print(json.dumps({"vp":f"{W}x{Hh}","lang":lang,"path":seq,"screens":len(report),"ended":pg.evaluate("S.ended===true"),"errors":errs,"overflow":fails,"dms":dm,"hurt":exp},ensure_ascii=False))
