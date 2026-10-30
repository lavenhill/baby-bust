import json, re, content_zh as C
en=json.load(open('en.json')); R=json.load(open('reunion_v3.json'))
E=lambda s:[s,en.get(s,s)] if isinstance(s,str) and s else s
nodes={}
for k,n in C.NODES.items():
    o=dict(year=n['year'],src=n['src'],flood=n.get('flood',False),final=n.get('final',False),next=n['next'],ask=[E(x) for x in n['ask']],
           setup=[[w,E(t)] for w,t in n['setup']],boss={h:E(n['boss'][h]) for h in 'UD'},
           chat={h:([n['chat'][h][0],E(n['chat'][h][1])] if n['chat'][h] else None) for h in 'UD'})
    for h in 'UD':
        x=n[h]; o[h]={'who':x['who'],'named':x['who'] in C.TAG,'tag':E(x.get('tag') or C.TAG.get(x['who'],'')),'h1':E(x['h1']),'sub':E(x['sub']),'aside':E(x['aside'])}
        if not o[h]['named']: o[h]['whoE']=E(x['who'])
        if x.get('aside_ring'): o[h]['aside_ring']=[x['aside_ring'],'She\'s waiting downstairs, engine running']
        if getattr(C,'H1S_EN',{}).get(k+'_'+h): o[h]['h1s']=C.H1S_EN[k+'_'+h]
    nodes[k]=o
fix=lambda s:s.replace('Old Yan','Vivian').replace('Lao Yan','Vivian')
reu={k:{'line':[v['line'],fix(v.get('line_en',''))],'qa':[[q.get('a',''),fix(q.get('a_en',''))] for q in v.get('qa',[])][:3],'off':[v.get('offtopic',''),fix(v.get('offtopic_en',''))],'kind':v.get('kind','')} for k,v in R['reunion'].items()}
for k,v in reu.items(): assert v['line'][0] and v['line'][1] and v['off'][0] and v['off'][1] and all(a and b for a,b in v['qa']) and len(v['qa'])==3,('reunion missing text',k)
SELF={'0':['八年來老顏從沒退過件。最後一張她留下自己，人工生殖法草案影本還夾在卷宗裡。','In eight years Vivian never pushed back once. In the last photo she kept herself; the draft fertility bill is still tucked in the files.'],
'0|gray':['八年來老顏從沒退過件。最後一張她把自己裁掉，合照裡只有她是黑白的。','In eight years Vivian never pushed back once. In the last photo she cut herself out; she is the only one in grey.'],
'1':['老顏重做過 {n} 次。最後一張她留下自己，相框裡的照片褪了一點。','Vivian redid it {n} times. In the last photo she kept herself; the picture in the frame has faded a little.'],
'1|gray':['老顏重做過 {n} 次。最後一張她把自己裁掉，戒指一直戴在手上。','Vivian redid it {n} times. In the last photo she cut herself out; the ring never left her finger.'],
'3+':['老顏重做了 {n} 次。最後一張她留下自己，手上沒有戒指。','Vivian redid it {n} times. In the last photo she kept herself; there is no ring on her hand.'],
'3+|gray':['老顏重做了 {n} 次。最後一張她還是把自己裁掉了，手上沒有戒指。','Vivian redid it {n} times. In the last photo she still cut herself out; there is no ring on her hand.']}
VERDICT={'self':['同學都留在畫面裡，妳的生活被裁掉了','Everyone stayed in the picture. Your life got cropped.'],'gone':['宣傳照張張漂亮，天燈少了好幾盞','Every poster looked great. Several lanterns never went up.'],'mix':['誰都沒被放過，包括妳','No one was spared, not even you.']}
ui={k:([E(x) for x in v] if isinstance(v,list) else E(v)) for k,v in C.UI.items()}
ui['credit'][1]='Draft copy & translation: Meta Muse Spark 1.3 · Illustrations: Meta Muse Image 1.0 · Every policy and number is sourced'
ui['credit'][0]=C.UI['credit']
ui['qf']=[E(x) for x in C.UI_QF]
EN3={'家裡桌上一碗蓋著保鮮膜的飯，紙條寫「微波三分鐘」。':'At home, a bowl of rice under cling film. The note says "3 minutes in the microwave."',
'年終考核乙等。取卵那天的格子，改成「再約」兩個字。':'Year-end review: B. On the calendar, egg-retrieval day now says "reschedule."',
'桌上的相框，只剩一個人。':'In the frame on the desk, only one is left.','鍵盤旁邊，兩只戒指，沒有人戴了。':'Next to the keyboard, two rings. No one wears them now.',
'小芋頭明年抽到公幼。我回事務所上班，三十五歲升主任。':'Little Taro wins the lottery for a cheap public preschool next year. I go back to the firm and make manager by 35.',
'小太陽幼兒園招生滿 60 個。爸寫的招牌要撐過第 30 年。':'"Little Sun" fills all 60 places. Dad\'s hand-painted sign makes it to year 30.',
'月薪到 30,000。暑假帶我媽去富士山，機票我都先買好了啦。':'Pay goes to NT$30,000 a month. Taking Mom to Mt. Fuji this summer, tickets already booked.',
'九點前下班。存到 80 萬頭期款，到時跟小雯求婚。':'Off work before 9. Save NT$800,000 for a down payment, then I can finally propose to Wendy.',
'三十歲前生第一個。請假不用跟任何人道歉。':'First baby before 30. Taking leave without apologizing to anyone.','明年 5/24 ♡':'Next year, 5/24 ♡',
'海報上那間準公共，就開在我對面。':'That subsidized private preschool on your poster opened right across from mine.','這學期少了十五個。':'I lost fifteen kids this term.','妳在平溪看過我寫什麼。':'You saw what I wrote in Pingxi.',
'妳又把老師畫成笑著的。':'You drew the teachers smiling again.','我媽昨天又問我要不要轉行。':'Mom asked me again yesterday if I should quit.','下次畫我的時候，寫真的。':'Next time you draw me, tell the truth.',
'你們每張圖都在叫我快生。':'Every one of your posters tells me to have kids.','我連房租都快付不起。':'I can barely pay rent.','妳自己覺得公平嗎？':'Do you think that\'s fair?',
'海報上那個媽媽在笑。':'The mom on your poster is smiling.','我是在事務所廁所看到的。':'I saw it in the office bathroom.','妳知道我不是她。':'You know that\'s not me.',
'平溪，2018 年元宵':'Pingxi, Lantern Festival 2018','老顏要去中央當約聘小編了，我們來放天燈。':'Vivian got a contract job running social media for the central government. Let\'s fly sky lanterns.','點每一盞燈，看上面寫什麼':'Tap each lantern to read it','放！':'Let go!',
'八年後，大家都要回來喔！':'In eight years, we\'ll all be back here!','上班第一天':'First day at work','一年一聘的約，續不續看年終考核。':'One-year contract. Whether it\'s renewed depends on your year-end review.',
'妳做的每一張圖，都會出現在同學的手機裡，加油。':'Every picture we make ends up on your classmates\' phones.','房租(禮拜五交)　訂喜宴(禮拜六)':'Rent (Fri.) · Banquet (Sat.)','來電':'Incoming call',
'{who} 已退出群組。':'{who} left the group.','2026，平溪':'Pingxi, 2026','她在樓下等，車沒熄火':'She\'s waiting downstairs, engine running'}
E3=lambda s:[s,EN3.get(s) or en.get(s,s)]
D=dict(nodes=nodes,wish={k:E3(v) for k,v in C.WISH.items()},call={k:[E3(x) for x in v] for k,v in C.CALL.items()},callN={k:[E(x) for x in v] for k,v in C.CALLN.items()},open2={k:E3(v) for k,v in C.OPEN2.items()},ring_off=E3(C.RING_OFF),open=[[w,E(t)] for w,t in C.OPEN],life=[E3(x) for x in C.LIFE],ui=ui,reunion=reu,self=SELF,verdict=VERDICT,
 tag={k:E(v) for k,v in C.TAG.items()},names={'老顏':'Vivian','阿芳':'Amy','家豪':'Kevin','宜君':'Jessica','志豪':'Jason','佩珊':'Penny','主管':'Boss'},
 slug={'老顏':'laoyan','阿芳':'afang','家豪':'jiahao','宜君':'yijun','志豪':'zhihao','佩珊':'peishan'},
 group={k:[[w,E(t),d] for w,t,d in v] for k,v in C.GROUP.items()},gcons={k:{str(n):[[w,t,E(x),d] for w,t,x,d in ls] for n,ls in v.items()} for k,v in C.GCONS.items()},news={k:[E(h),E(src)] for k,(h,src) in C.NEWS.items()},wish2={k:E(v) for k,v in C.WISH2.items()},wish26={k:[E(x) for x in v] for k,v in C.WISH26.items()},v5={k:E(v) for k,v in C.V5UI.items()},
 lantern=dict(opt=C.LANTERN_OPT),
 class_=['阿芳','家豪','宜君','志豪','佩珊','老顏'],babies=['afang','jiahao','yijun','peishan'])
# S7 (2026-10-28): 出處頁新版——出處庫、猜猜看、建議問題（錄好的 Muse 答案）、公開進度。缺這塊時引擎退回舊出處頁。
import os,sources_zh as SZ
_T=os.path.dirname(os.path.abspath(__file__));SEN=json.load(open(os.path.join(_T,'sources_en.json')));SREC=json.load(open(os.path.join(_T,'sources_rec.json')))
def se(key,zh):
    v=SEN.get(key);assert v,('sources_en missing',key);return [zh,v]
# S29（2026-10-29）：每句＝[中, 英]，出處另放 r（REFS 索引）；REFS＝[網址, [作者, 標題, 媒體, 日期]中, 同英]。引擎依頁面出現順序給 [n]。
_RU=list(SZ.REFS);_RI={u:i for i,u in enumerate(_RU)};_RE=SEN['REFS']
def _au(au,pub): return '' if (au in pub or pub in au) else au
refs=[[u,[_au(SZ.REFS[u][0],SZ.REFS[u][2]),SZ.REFS[u][1],SZ.REFS[u][2],SZ.REFS[u][3]],[_au(_RE[u][0],_RE[u][2]),_RE[u][1],_RE[u][2],_RE[u][3]]] for u in _RU]
for u in _RU: assert u.startswith('https://') and all(SZ.REFS[u][1:3]) and all(_RE[u][1:3]),('ref incomplete',u)
cards={}
for c in SZ.CARDS:
    o=dict(t=se(c['id']+'.title',c['title']),kind=c['kind'],f=[se(f"{c['id']}-{i+1}",f) for i,(f,_) in enumerate(c['facts'])],r=[[_RI[u] for u in us] for _,us in c['facts']])
    if c.get('game'): o['g']=se(c['id']+'.game',c['game'])
    if c['kind']!='meta': assert all(o['r']),('fact without source',c['id'])
    o['url']=_RU[o['r'][0][0]] if c['kind']!='meta' else ''
    cards[c['id']]=o
ids={f"{k}-{i+1}" for k,c in cards.items() for i in range(len(c['f']))}
assert len(SEN['REFS'])==len(SZ.REFS)
for k,q in SZ.QUIZ.items(): assert all(p in ids for p in q['picks']),k
quiz={k:dict(c=se('quiz.'+k+'.claim',q['claim']),who=q.get('who',''),kind=q['kind'],note=(se('quiz.'+k+'.note',q['note']) if q['note'] else ['','']),picks=q['picks']) for k,q in SZ.QUIZ.items()}
# c29（2026-10-29）：猜猜看每題答案都是「真實」，題目必須是該年遊戲原句的一段（中英各自一字不差），且至少一句出處、出處卡要有 https 連結
for k,q in quiz.items():
    n=nodes[k];T=list(n['ask'])+[s[1] for s in n['setup']]+[n[h]['h1'] for h in 'UD']
    assert q['kind']=='real' and q['picks'],('quiz must be real with picks',k)
    for L in (0,1): assert q['c'][L] and any(q['c'][L] in x[L] for x in T),('quiz claim not in game text',k,L,q['c'][L])
    for p_ in q['picks']: assert (cards[p_.split('-')[0]].get('url') or '').startswith('https://'),('quiz pick without https link',k,p_)
rec=[]
for i,c in enumerate(SZ.CHIPS):
    r=SREC[c];assert all(p in ids for p in r['picks']),c;assert r['type'] in ('fact','fiction') and r['picks'],('suggested question has no recorded answer',c)  # c29: 日本那題 0 句出包
    rec.append(dict(type=r['type'],picks=r['picks']))
# L（2026-10-28 19:44）：nadv＝每個選項（牆的上下兩半）的倡議者卡（A01–A57），展開海報時列「誰在倡議這一張」與「沒留下的另一張」
for k,d in SZ.NODE_ADV.items():
    assert k in C.NODES and set(d)<={'U','D'},k
    for h,v in d.items(): assert 1<=len(v)<=3 and all(cards[a]['kind']=='adv' and cards[a]['url'].startswith('http') for a in v),(k,h)
D['sources']=dict(N=len(ids),order=[c['id'] for c in SZ.CARDS],cards=cards,refs=refs,ncard=SZ.NODE_CARD,nadv=SZ.NODE_ADV,quiz=quiz,
  prog=[[p,se('prog.'+st,st)] for p,st in SZ.PROGRESS],chips=[se(f'chip.{i}',c) for i,c in enumerate(SZ.CHIPS)],rec=rec,
  ui={k:se('ui.'+k,v) for k,v in SZ.UI.items()})
for p,_ in SZ.PROGRESS: assert p in ids,p
# f29（2026-10-29）：每筆出處都有本地存檔頁 sources/Rxx.html（xx＝REFS 順序，從 01 起），頁內必須寫著原文網址；引擎的「存檔」與引用卡按鈕連到這頁
import html as _h
_SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','sources')
for i,u in enumerate(_RU):
    _f=f'{_SD}/R{i+1:02d}.html';assert os.path.exists(_f),('missing local archive page',_f)
    _t=open(_f).read();assert _h.escape(u,quote=True) in _t,('archive page does not name its URL',_f);assert not re.search(r'<(script|link|img|iframe|object|embed)\b|url\(|@import|@font-face',_t,re.I),('archive page loads external resources',_f)
    assert ('<a href="'+_h.escape(u,quote=True)+'"') in _t and ('web.archive.org/web/' in _t or '未存檔' in _t),('archive page lacks clickable original or Wayback line',_f)
D['sources']['arch']=dict(dir='sources/',d='2026-10-29')
import os
HP='/workspace/work/bb2/tools/heads.json'  # R4-4a: YuNet head boxes (tools/heads.py)
if os.path.exists(HP): D['heads']=json.load(open(HP))
if getattr(C,'POSTER_TEXT',None): D['posterText']={k:{kk:vv for kk,vv in v.items() if kk!='note'} for k,v in C.POSTER_TEXT.items()}
# d29：老顏的燈選項靜態檢查（字數上限；{n} 只出現在 gone/once）
_LO=C.LANTERN_OPT;_cw=lambda s:len(s)
for k,o in _LO.items():
    lamps=[o] if k=='plamp' else ([o['lamp']] if 'lamp' in o else [])
    for z,e in lamps: assert z and e and len(z.replace('{n}','阿芳'))<=12 and len(e.replace('{n}','Jessica'))<=20,('lantern lamp too long',k,z,e)
    reps=o.get('rep') if isinstance(o,dict) else None;reps=[reps] if isinstance(reps,list) else list((reps or {}).values())
    for z,e in reps: assert z and e and len(z.replace('{n}','阿芳'))<=25 and len(e.replace('{n}','Jessica'))<=70,('lantern reply too long',k,z,e)
    if isinstance(o,dict) and 'who' in o: assert all(w in o['rep'] for w in o['who']),k
# d29：資料版本＝index.html 的 V（頁面與資料不一致時 data.js 尾端自動重載一次，防 githack 快取空窗）
# q30 (2026-10-30): curly quotes/apostrophes in English render full-width in the CJK fonts (Huninn / LXGW WenKai TC) and read as "Let’ s".
# English copy must use ASCII ' and " (Chinese uses 「」); fail the build if any string still has U+2018/2019/201C/201D.
def _q30(x,p=''):
    if isinstance(x,str):
        assert not re.search('[\u2018\u2019\u201c\u201d]',x),('curly quote in copy (English: use ASCII; Chinese: 「」):',p,x)
    elif isinstance(x,list): [_q30(v,p+'/'+str(i)) for i,v in enumerate(x)]
    elif isinstance(x,dict): [_q30(v,p+'/'+str(k)) for k,v in x.items()]
_q30(D)
# u30 (2026-10-30, demo video): English money amounts all carry NT$ in one style (NT$ + full digits, "a month"): no "800k", "30K", "4,500/month",
# and no bare 1,000+ number unless the next word says it is a count (classes, places, households, ...). URLs and 4-digit years are skipped.
_U30_COUNT={'new','more','classes','subsidized','places','homes','households','applied','had','public','private','affordable','kids','children','preschools','teachers','people','survey','job','3-year-olds'}
def _u30(x,p=''):
    if isinstance(x,str):
        if re.search('[\u3400-\u9fff]',x) or x.startswith('http'): return
        assert not re.search(r'(?<![\w$])\d+[kK]\b',x),('money as "k" (use NT$ + full digits):',p,x)
        assert not re.search(r'\d/\s?month',x),('"/month" (use "NT$x a month"):',p,x)
        for m in re.finditer(r'(?<![\w$.,/\u2013-])(\d{1,3}(?:,\d{3})+)(?:[-\s]+([\w-]+))?',x):
            if x[max(0,m.start()-3):m.start()]=='NT$': continue
            nxt=(m.group(2) or '').lower()
            assert nxt in _U30_COUNT or nxt=='plus' and x[m.end():m.end()+12].lstrip().startswith('3-year'),('English amount without NT$ (or add the count word to _U30_COUNT):',p,x)
    elif isinstance(x,list): [_u30(v,p+'/'+str(i)) for i,v in enumerate(x)]
    elif isinstance(x,dict): [_u30(v,p+'/'+str(k)) for k,v in x.items()]
_u30(D)
_V=re.search(r"const V='([^']+)'",open('/workspace/work/bb2/index.html').read()).group(1);D['v']=_V
open('/workspace/work/bb2/data.js','w').write('// Copy drafted with Meta Muse Spark 1.3 (translations, reunion lines); insider slogans are drafts for the author to replace. Illustrations: Meta Muse Image 1.0. Built 2026-10-29 (d29: lantern options, quiz true/false).\nconst DATA='+json.dumps(D,ensure_ascii=False)+';\n'+"typeof window!=='undefined'&&window.addEventListener('DOMContentLoaded',()=>{try{if(typeof V!=='undefined'&&V!==DATA.v&&!/reload=/.test(location.search))location.replace(location.pathname+'?reload='+Date.now())}catch(e){}});\n")
chars=set(json.dumps(D,ensure_ascii=False))
open('chars.txt','w').write(''.join(sorted(chars))+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz–—…·・，。？！：「」（）')
print('ok',len(chars))
