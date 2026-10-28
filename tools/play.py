"""Headless playtest for the one-screen-per-beat build.
usage: python3 tools/play.py PATH(7 x U/D) OUTPREFIX [zh|en] [WxH] [shots] [kb] [rm] [wish=TEXT] [expect=同學]
 L1 (2026-10-28): types wish on Lao Yan's lantern (empty allowed: wish=), checks 5 s beat, one reply from a classmate still in the group,
 contrast 燈上/海報上 = masked wish / kept 2026 headline, dark lamps == gone, profanity never on screen.
 rm = prefers-reduced-motion. kb = pick with keys (1/2 and ↑/↓ alternating) + Enter instead of mouse. Wall checks: tap-only (no ⇅), hint only in 2018, pick lands before 發布.
Checks every screen for overflow (content taller than the screen) and page errors.
R4 (2026-10-28): "tap to continue" pill must not overlap other elements or leave the screen (incident: 退群提示蓋到點一下繼續);
poster text over head boxes: cover >=0.05 WARN, >=0.15 fail; poster placement time per wall reported (ms); pages after paging must each fit."""
from playwright.sync_api import sync_playwright
import time,sys,os,json
seq=sys.argv[1];out=sys.argv[2];lang=sys.argv[3] if len(sys.argv)>3 else 'zh'
W,Hh=map(int,(sys.argv[4] if len(sys.argv)>4 else '390x780').split('x'));extra=sys.argv[5:]
opt={a.split('=',1)[0]:a.split('=',1)[1] for a in extra if '=' in a};extra=[a for a in extra if '=' not in a]
kb='kb' in extra;rm='rm' in extra;shots=any(a not in('kb','rm') for a in extra)
WISH=opt.get('wish',{'zh':'想睡一整晚','en':'sleep all night'}[lang]);EXPECT=opt.get('expect')  # L1: text typed on Lao Yan's lantern; expect = responder
url="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),"..","index.html"))
OVER="""()=>{const s=H.list[H.i];if(!s)return null;const bad=[];
 if(s.scrollHeight>s.clientHeight+2)bad.push('screen '+s.scrollHeight+'>'+s.clientHeight);
 s.querySelectorAll('.chat').forEach(c=>{if(c.scrollHeight>c.clientHeight+2&&!s.classList.contains('wall'))bad.push('chat clipped '+c.scrollHeight+'>'+c.clientHeight)});
 s.querySelectorAll('.h1,.sub,.tag,.aside,.bar,.hint').forEach(e=>{if(!e.getClientRects().length)return;const r=e.getBoundingClientRect(),p=s.getBoundingClientRect();if(r.right>p.right+1||r.left<p.left-1)bad.push(e.className+' wide')});
 const tp=s.querySelector('.tapnext');if(tp&&tp.getClientRects().length){const a=tp.getBoundingClientRect(),p=s.getBoundingClientRect();if(a.bottom>p.bottom+1||a.top<p.top-1)bad.push('tapnext offscreen');
  s.querySelectorAll('.sys,.sysin,.phone,.life,.note,.cap,.btn,.wish,.qs,.bub,.memo:not(.fmemo)').forEach(e=>{if(e.contains(tp)||!e.getClientRects().length)return;const b=e.getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>2&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2)bad.push('tapnext overlaps '+e.className)})}
 if(s.classList.contains('wall'))s.querySelectorAll('.half').forEach(h=>{const c=+(h.dataset.cover||0);if(c>=.15)bad.push('poster text on head '+h.className+' '+c);else if(c>=.05)bad.push('WARN poster '+h.className+' '+c)});
 return bad}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/chromium")
    pg=b.new_page(viewport={"width":W,"height":Hh},locale="zh-TW",has_touch=False,reduced_motion="reduce" if rm else "no-preference")
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/fonts.*/**",lambda r:r.abort())
    pg.goto(url,wait_until="domcontentloaded");time.sleep(.6)
    if lang=='en': pg.click("#lang");time.sleep(.3)
    report=[];i=0;n=0;last=None;ms=[]
    def shot(tag):
        if shots: pg.screenshot(path=f"{out}_{n:02d}_{tag}.png")
    for guard in range(500):
        if pg.evaluate("S.ended===true"):
            time.sleep(.6);bad=pg.evaluate(OVER);report.append(('end',bad));shot('end');break
        info=pg.evaluate("()=>{const s=H.list[H.i];return {k:H.i,wall:s.classList.contains('wall')&&!s.classList.contains('done'),btn:!!s.querySelector(':scope>.btn, .title .btn'),tap:!!s.querySelector('.tapnext'),qs:!!s.querySelector('.qs button:not(:disabled)')&&getComputedStyle(s.querySelector('.qs')).visibility!=='hidden'}}")
        if pg.evaluate("()=>!!H.list[H.i].querySelector('.lan:not(.fly) .mate:not(.seen)')&&!H.list[H.i].querySelector('.l26')"):
            for m in pg.locator('.scr:not(.below):not(.above) .lan .mate').all(): m.click();time.sleep(.25)
            bad=pg.evaluate(OVER);report.append(('lanterns',bad));shot('lan');continue
        if pg.evaluate("()=>!!H.list[H.i].querySelector('.wish input:not(:disabled)')"):
            time.sleep(.3);bad=pg.evaluate(OVER);report.append(('lantern input',bad))
            pg.locator('.scr:not(.below):not(.above) .wish input').click()
            if WISH: pg.keyboard.type(WISH,delay=20)
            time.sleep(.2);shot('lin');lin_val=pg.evaluate("()=>H.list[H.i].querySelector('.wish input').value")
            pg.locator('.scr:not(.below):not(.above) .wish button').click();t_sub=time.time();n+=1
            time.sleep(2.4);shot('lmid');time.sleep(.2);continue
        if info['wall']:
            time.sleep(.7);bad=pg.evaluate(OVER);report.append((pg.evaluate("S.node")+' wall',bad));shot('wall')
            ms.append(pg.evaluate("()=>Math.max(0,...[...H.list[H.i].querySelectorAll('.half')].map(h=>+(h.dataset.ms||0)))"))
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
            if info['qs']:  # R4: every follow-up answer must fit at the larger DM type, not just the first
                qb=pg.locator('.scr:not(.below):not(.above) .qs button')
                for qi in range(qb.count()-1,-1,-1):
                    qb.nth(qi).click();time.sleep(.3);bq=pg.evaluate(OVER)
                    if bq: report.append((f"screen {info['k']} q{qi}",bq))
            bad=pg.evaluate(OVER);report.append((f"screen {info['k']}",bad));shot('s')
            pg.mouse.click(pg.locator('#stage').bounding_box()['x']+20,60);n+=1;time.sleep(.7);continue
        time.sleep(.4)
    # lines-r3 checks: ending DMs (gone = cold, hurt once = warm), no blank bubbles, no outsider forward screens
    dm=pg.evaluate("""()=>H.list.filter(s=>s.querySelector('.who')).map(s=>{const b=s.querySelector('.chat .bub');return {who:s.querySelector('.who b').textContent,cold:!!(b&&b.classList.contains('gone')),len:b?b.textContent.length:0}})""")
    exp=pg.evaluate("()=>({gone:S.gone.slice(),once:Object.keys(S.hurt).filter(m=>S.hurt[m]===1&&!S.gone.includes(m))})")
    blank=pg.evaluate("()=>H.list.flatMap(s=>[...s.querySelectorAll('.bub,.sysin')]).filter(b=>{const c=b.cloneNode(true);c.querySelectorAll('i').forEach(i=>i.remove());return !c.textContent.trim()&&!b.querySelector('img,.photo')}).length")
    fw=pg.evaluate("()=>H.list.filter(s=>s.querySelector('.fw')).length")
    if blank: report.append(('blank bubbles',[blank]))
    if fw: report.append(('outsider forward screens',[fw]))
    if len(dm)!=len(exp['gone'])+len(exp['once']) or any(d['len']<20 for d in dm): report.append(('dm mismatch',[dm,exp]))
    LS=pg.evaluate("""()=>{const s=H.list.find(x=>x.classList.contains('lt'));if(!s)return null;return {lan:S.lantern,reps:[...s.querySelectorAll('.lrep')].map(b=>b.dataset.w),
      con:[...s.querySelectorAll('.lcon b')].map(b=>b.textContent),off:s.querySelectorAll('.sl.off').length,photoOff:s.querySelectorAll('.photo u.off').length,lw:s.querySelector('.lw').textContent,
      kept:(()=>{const l=S.path[S.path.length-1];return N[l.node][l.side].h1})(),blank:DATA.lantern.ui.blank,all:s.innerText}}""")
    if not LS or not LS['lan']: report.append(('lantern',['lantern beat missing']))
    else:
        g=exp['gone'];prob=[]
        if len(LS['reps'])!=1: prob.append(f"replies={LS['reps']}")
        elif LS['reps'][0] in g or LS['reps'][0]=='老顏': prob.append(f"responder {LS['reps'][0]} not in group")
        if EXPECT and LS['reps'] and LS['reps'][0]!=EXPECT: prob.append(f"responder {LS['reps'][0]} != expect {EXPECT}")
        if not 4900<=LS['lan']['ms']<=7000: prob.append(f"beat {LS['lan']['ms']}ms")
        if LS['off']!=len(g) or LS['photoOff']!=len(g): prob.append(f"dark lamps {LS['off']}/{LS['photoOff']} != gone {len(g)}")
        L_=1 if lang=='en' else 0
        if LS['con'][1]!=LS['kept'][L_]: prob.append(f"poster {LS['con'][1]!r} != kept {LS['kept'][L_]!r}")
        if LS['con'][0]!=(LS['lan']['w'] or LS['blank'][L_]) or LS['lw']!=LS['lan']['w']: prob.append(f"lantern text {LS['con'][0]!r}/{LS['lw']!r} vs {LS['lan']['w']!r}")
        if any(b in WISH.lower() for b in ['幹','靠北','白癡','去死','fuck','shit']):  # masked: lantern shows ▇, the raw words never appear
            if '▇' not in LS['lan']['w'] or WISH.strip() in LS['all']: prob.append('profanity not masked')
        if prob: report.append(('lantern',prob))
    isw=lambda r:all(str(x).startswith('WARN') for x in r[1])
    warns=[r for r in report if r[1] and isw(r)];fails=[r for r in report if r[1] and not isw(r)]
    print(json.dumps({"vp":f"{W}x{Hh}","lang":lang,"path":seq,"screens":len(report),"ended":pg.evaluate("S.ended===true"),"errors":errs,"overflow":fails,"warn":warns,"place_ms":max(ms or [0]),"dms":dm,"hurt":exp,"lantern":(LS or {}).get('lan'),"reply":(LS or {}).get('reps')},ensure_ascii=False))
