"""Generate docs/spec/06-story-causality.md (human) + 06-story-graph.json (machine) from data.js.
Mirrors engine state logic in bb2/index.html (year/publish/reunion). Rerun after any copy or engine change."""
import json,subprocess,itertools,collections
B=__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/../'
D=json.loads(subprocess.check_output(['node','-e',"eval(require('fs').readFileSync('data.js','utf8').replace(/^const DATA/m,'global.DATA'));process.stdout.write(JSON.stringify(DATA))"],cwd=B))
N=D['nodes'];Z=lambda p:p[0] if isinstance(p,list) else p
CL=D['class_']
# ---------- simulate every path (mirror of engine) ----------
def run(choices):
    S=dict(node='y2018',hurt={},cutIn={},gone=[],self=0,lg=False,pg=False,path=[],events=[])
    for c in choices:
        n=N[S['node']];S['path'].append((S['node'],c))
        if n['final']:
            if c=='U':
                S['lg']=True;w=n['U']['who']
                if n['U']['named'] and w not in S['gone'] and str(S['node']) in D.get('gcons',{}):
                    S['hurt'][w]=S['hurt'].get(w,0)+1;S['cutIn'].setdefault(w,[]).append(S['node']);S['events'].append((S['node'],'hurt',w,S['hurt'][w]))
            else:S['pg']=True
            break
        if c=='U':
            w=n['D']['who']
            if n['D']['named'] and w not in S['gone']:
                S['hurt'][w]=S['hurt'].get(w,0)+1;S['cutIn'].setdefault(w,[]).append(S['node'])
                if S['hurt'][w]==2:S['gone'].append(w)
                S['events'].append((S['node'],'hurt',w,S['hurt'][w]))
            else:S['events'].append((S['node'],'nohit',w))
        else:
            S['self']+=1;S['events'].append((S['node'],'self',S['self']))
        S['node']=n['next'][c]
    g=len(S['gone']);v='gone' if g>=2 else ('self' if S['self']>=3 and not g else 'mix')
    S['verdict']=v
    pres=[m for m in CL if m!='老顏' and m not in S['gone']]  # L1 lantern: responder = first in rule order still in the group
    S['lantern']={k:(next((x for x in who if x in pres),'佩珊') if who else '被點名者') for k,zh,en,who in D['lantern']['rules']}
    key=lambda m:m+'|'+','.join(sorted(S['cutIn'][m][:2]))
    S['reunion']=[key(m) for m in S['gone']]+[key(m) for m in CL if m!='老顏' and m not in S['gone'] and S['hurt'].get(m,0)==1]
    return S
paths=[]
for ch in itertools.product('UD',repeat=7):
    s=run(ch);key=''.join(c for _,c in s['path'])
    if key not in [p['key'] for p in paths]:paths.append(dict(key=key,S=s))
P=len(paths)
cnt=lambda f:collections.Counter(f(p['S']) for p in paths)
verdicts=cnt(lambda s:s['verdict']);goneC=cnt(lambda s:len(s['gone']));lan={k:dict(collections.Counter(p['S']['lantern'][k] for p in paths)) for k,*_ in D['lantern']['rules']}
assert all('佩珊' not in p['S']['gone'] for p in paths),'佩珊 must never leave (lantern fallback)'
reach=collections.Counter(k for p in paths for k in p['S']['reunion'])
dead=[k for k in D['reunion'] if k not in reach]
leaveC=collections.Counter(m for p in paths for m in p['S']['gone'])
hurtable=collections.defaultdict(list)
for k,n in N.items():
    if not n['final'] and n['D']['named']:hurtable[n['D']['who']].append(k)
# ---------- machine graph ----------
def side(n,h):
    x=n[h];return {k:(v if not isinstance(v,list) else {'zh':v[0],'en':v[1]}) for k,v in x.items()}
graph={'version':'S7 (V=20261028e)','generated_from':'data.js + engine rules in index.html',
 'state':{
  'hurt[m]':'同學 m 被犧牲次數；選上半（文宣）時 +1 給 D.who（下半照片上的人）',
  'gone':'hurt[m]==2 的同學：退群、之後群組不出現、2026 空燈、結局私訊',
  'self':'選下半（現場）次數＝老顏重做晚數；頭像 1–2 半灰、≥3 劃線',
  'laoyanGray':'2026 選上（佩珊的海報）→ 老顏的燈灰；佩珊 hurt+1（組長拿海報堵她），結局收到受傷一次版私訊',
  'peishanGray':'2026 選下（老顏自己）→ 佩珊的燈灰、願望換成第二版',
  'baby':'新生兒數，隨機步數觸發，與選擇無關（設計：選擇不影響出生人數）'},
 'rules':[
  {'when':'choose U (poster) at non-final node','effect':'hurt[D.who]+=1 if D.named and not gone','shows':['群組後果 gcons[node][hurt]：同學在群組轉述外人的話（不出現外人轉傳畫面）','2022c 先出新聞卡 news[node]','hurt==2 → 系統訊息「已退出群組」+ 加入 gone','D.who 已退群 → 不出後果畫面']},
  {'when':'choose D (real) at non-final node','effect':'self+=1','shows':['主管退件 boss.D','life[self-1]；self==3 → ring_off（兩只戒指）；self>4 → again_night']},
  {'when':'group line has deps [x]','effect':'x in gone → 不顯示；dep "!x" → 只有 x in gone 才顯示'},
  {'when':'2026 ending','effect':'verdict = gone if len(gone)>=2 else self if self>=3 and no gone else mix','shows':['wish26[m][hurt>0]','老顏的燈＝玩家輸入（L1 天燈拍，見 §5）','私訊：先退群者 reunion[m|前兩刀]（冷），再受傷一次仍在群組者 reunion[m|那一刀]（還會酸、約放燈）']}],
 'nodes':{k:{'year':n['year'],'next':n['next'],'final':n['final'],'policy_src':n['src'],
   'ask':[{'zh':a[0],'en':a[1]} for a in n['ask']],
   'U':side(n,'U'),'D':side(n,'D'),
   'U_hurts':(n['D']['who'] if n['D']['named'] and not n['final'] else None),
   'group':[{'id':f'{k}.g{i+1}','who':g[0],'zh':g[1][0],'en':g[1][1],'visible_if':{'present':[g[0]]+[d for d in g[2] if d[0]!='!'],'absent':[d[1:] for d in g[2] if d[0]=='!']}} for i,g in enumerate(D['group'].get(k,[]))],
   'choices':({'U':{'promotes':n['U']['who'],'harm':n['D']['who'] if n['D']['named'] else None,'effect':'hurt[harm]+=1','next':n['next'].get('U')},'D':{'effect':'self+=1','next':n['next'].get('D')}} if not n['final'] else {'U':{'effect':'laoyanGray=true; hurt[U.who]+=1'},'D':{'effect':'peishanGray=true'}}),
   'group_after_U':{h:[{'who':g[0],'time':g[1],'zh':g[2][0],'en':g[2][1],'visible_if':{'present':g[3]}} for g in ls] for h,ls in D.get('gcons',{}).get(k,{}).items()},
   'news_after_U':({'zh':D['news'][k][0][0],'en':D['news'][k][0][1],'src':D['news'][k][1][0]} if k in D.get('news',{}) else None),
   'boss_D':({'zh':n['boss']['D'][0],'en':n['boss']['D'][1]} if isinstance(n.get('boss',{}).get('D'),list) else None)} for k,n in N.items()},
 'endings':{'verdict':{k:{'zh':v[0],'en':v[1]} for k,v in D['verdict'].items()},'lantern':D['lantern'],'wish26':D['wish26'],'wish2018':D['wish'],
   'reunion_keys':list(D['reunion'].keys()),'reunion_unreachable':dead},
 'path_stats':{'paths':P,'verdict':verdicts,'gone_count':goneC,'lantern_responder':lan,'leaves_group':leaveC,'reunion_reach':reach},
 'paths':[{'key':p['key'],'nodes':[n for n,_ in p['S']['path']],'gone':p['S']['gone'],'self':p['S']['self'],'verdict':p['S']['verdict'],'lantern':p['S']['lantern']} for p in paths]}
json.dump(graph,open(B+'docs/spec/06-story-graph.json','w'),ensure_ascii=False,indent=1)
# ---------- human doc ----------
L=[]
a=L.append
a('# 06 遊戲敘事與因果（r4，自動生成）\n')
a('> 由 `tools/story_doc.py` 從 data.js 與引擎規則生成；機器版＝`06-story-graph.json`（同一份資料）。台詞全文對照見雲端「我們這一班_文案台詞對照」。改文案或引擎後重跑，勿手改本檔的生成段落。\n')
a('## 1. 一句話\n2018 年平溪放天燈，六個同學各許一個願。老顏進公部門做政策宣傳，每年要從兩張照片裁一張：上半＝政府文宣（某位同學被拍成「受益者」）、下半＝現場（同學真實的處境）。選文宣，海報被外人拿去堵那位同學的嘴（只由同學在群組轉述）；選現場，主管退件、老顏自己重做一晚。2026 年再回平溪，誰還在、誰的燈是空的，就是這八年的帳。\n')
a('## 2. 狀態與因果規則\n')
a('| 狀態 | 意義 | 怎麼變 | 看得到的地方 |\n|---|---|---|---|')
a('| hurt[同學] | 被犧牲次數 | 選上半 → 下半照片上的那位 +1 | 頭像劃線（1）、淡出（2） |')
a('| gone | 退群名單 | hurt 到 2 | 「已退出群組」、之後群組不出現、他和依賴他的句子消失、2026 空燈＋私訊 |')
a('| self | 老顏重做晚數 | 選下半 +1 | 頭像半灰（1–2）、劃線（≥3）；生活框四階 |')
a('| laoyanGray／peishanGray | 2026 最後一刀 | 2026 選上→老顏灰＋佩珊 hurt+1；選下→佩珊灰 | 平溪燈、佩珊私訊 |')
a('| baby | 本班小朋友數 | 隨機步數，與選擇無關 | 下一年群組貼照片 |\n')
a('**群組台詞的依賴標記**：〔依賴 A〕＝A 還在群組才出現；〔依賴 A、B〕＝兩人都在才出現；〔依賴 !A〕＝A 已退群才出現。說話者本人退群，他的句子全部不出現。\n')
a('**2026 是最後一刀**：不計入 gone／self。選上→老顏的燈灰，佩珊 hurt+1（群組後果＋結局受傷一次版私訊）；選下→佩珊的燈灰、願望換第二版。判詞不受影響。\n')
a('## 2.1 真相表（每年選上／選下的直接後果）\n')
a('| 年 | 選上（文宣） | 選下（現場） |\n|---|---|---|')
for k,n in N.items():
    if n['final']:a(f"| {n['year']}{k[5:]} | 捧佩珊 → 老顏的燈灰；佩珊 hurt+1 | 留老顏 → 佩珊的燈灰 |");continue
    pro=n['U']['who'] if n['U']['named'] else Z(n['U'].get('whoE',n['U']['who']))
    a(f"| {n['year']}{k[5:]} | 捧{pro}；{n['D']['who']} hurt+1（被拿海報堵嘴）→ {n['next']['U'][1:]} | 老顏 self+1 → {n['next']['D'][1:]} |")
a('')
a('## 2.2 角色生死簿（退群要被犧牲 2 次）\n')
for m in CL:
    if m=='老顏':continue
    a(f"- {m}：機會在 {'、'.join(x[1:] for x in hurtable.get(m,[])) or '2026（只會受傷一次）'}；實際退群 {leaveC.get(m,0)}/{P} 條路徑")
a('')
a('**老顏生活框（選下半後）**')
for i,l in enumerate(D['life']):
    a(f"- 第 {i+1} 晚：{Z(l) or Z(D['ring_off'])}")
a(f"- 第 5 晚以後：{Z(D['ui']['again_night'])}\n")
a('**2026 結局判詞**（gone≥2 → gone；self≥3 且無人退群 → self；其餘 → mix）')
for k,v in D['verdict'].items():a(f'- {k}：{v[0]}（{verdicts.get(k,0)}/{P} 條路徑）')
a('\n**老顏的燈（L1 天燈拍，2026-10-28）**：玩家替老顏寫燈（12 字內，中文 1、英數 0.5；可空白；髒話打碼▇）→ 5 秒升空 → 佩珊傳照片 → 一位在群同學回一句 → 對照「燈上／海報上（2026 實際留下那張的主標）」。回應規則依序：')
for k,zh,en,who in D['lantern']['rules']:
    ln=D['lantern']['lines'];ws=who or ['被點名者']
    a(f"- {k}（{zh or ('髒話／空白' if k=='prof' else '燈上最先出現且仍在群組的同學名' if k=='name' else '其他')}）：{'→'.join(ws)}；各路徑回應者 {lan[k]}；台詞："+'／'.join(f"{x}「{ln[k+'_'+x][0]}」" for x in (who or [m for m in CL if 'name_'+m in ln]) if k+'_'+x in ln or 'name_'+x in ln and k=='name' and not ln.get(k+'_'+x) is None))
a('')
a('## 3. 分支圖\n```mermaid\nflowchart TD')
for k,n in N.items():
    lab=f"{n['year']}{k[5:]}"
    if n['final']:a(f'  {k}["{lab} 平溪"]');continue
    a(f'  {k}["{lab}"]')
    for h,t in n['next'].items():
        if h=='U':
            pro=n['U']['who'] if n['U']['named'] else Z(n['U'].get('whoE',n['U']['who']))
            lab2=f"上：捧{pro}／傷{n['D']['who']}"
        else: lab2='下：老顏重做'
        a(f'  {k} -- "{lab2}" --> {t}')
a('```\n')
a('## 4. 角色線\n')
a('| 角色 | 2018 願望 | 頭像標 | 可能被犧牲的年份 | 退群機率 | 2026 願望（沒事／受過傷） |\n|---|---|---|---|---|---|')
for m in CL:
    w26=D['wish26'].get(m)
    a(f"| {m} | {Z(D['wish'][m])} | {Z(D['wish2'][m])} | {'、'.join(hurtable.get(m,[])) or ('2026（最後一刀）' if m in ('老顏','佩珊') else '—')} | {leaveC.get(m,0)}/{P} | {(Z(w26[0])+'／'+Z(w26[1])) if w26 else '玩家寫（L1）'} |")
a('')
for p in []:pass
# per year
a('## 5. 逐年劇情（只列使用中的台詞）\n')
for k,n in N.items():
    a(f"### {n['year']}{k[5:]}　{('最終年・平溪' if n['final'] else '')}")
    a(f"- 政策出處：{n['src']}")
    a(f"- 主管交辦：{Z(n['ask'][0])}／命題：{Z(n['ask'][1])}")
    g=D['group'].get(k,[])
    if g:
        a('- 同學群組：')
        for w,t,d in g:a(f"  - {w}：{t[0]}"+(f"　〔依賴 {'、'.join(d)}〕" if d else ''))
    for h in 'UD':
        x=n[h];who=x['who'] if x['named'] else Z(x.get('whoE',x['who']))
        a(f"- **{'上半・文宣' if h=='U' else '下半・現場'}**（{who}）：「{Z(x['h1'])}」{Z(x['sub'])}；旁註：{Z(x['aside'])}")
    if n['final']:
        a('- 選上：佩珊的海報留下 → 老顏的燈灰；佩珊 hurt+1，群組後果如下。選下：老顏自己的照片留下 → 佩珊的燈灰、願望換第二版。→ 結局')
        for h,ls in D.get('gcons',{}).get(k,{}).items():
            a(f'  - 群組後果（佩珊第{h}次）：')
            for g in ls:a(f"    - {g[0]}{(' '+g[1]) if g[1] else ''}：{g[2][0]}"+(f"　〔依賴 {'、'.join(g[3])}〕" if g[3] else ''))
        a('');continue
    hit=n['D']['who'] if n['D']['named'] else None
    a(f"- 選上 → 犧牲 **{hit}**（hurt+1）→ 下一年 {n['next']['U']}")
    if k in D.get('news',{}):a(f"  - 新聞卡：{D['news'][k][0][0]}（{D['news'][k][1][0]}）")
    for h,ls in D.get('gcons',{}).get(k,{}).items():
        a(f"  - 群組後果（{hit}第{h}次{'，之後退群' if h=='2' else ''}）：")
        for g in ls:a(f"    - {g[0]}{(' '+g[1]) if g[1] else ''}：{g[2][0]}"+(f"　〔依賴 {'、'.join(g[3])}〕" if g[3] else ''))
    a(f"- 選下 → 老顏重做一晚（self+1）→ 主管：{Z(n['boss']['D'])} → 下一年 {n['next']['D']}\n")
a('## 6. 結局私訊（退群者＝冷；受傷一次仍在群組＝還會酸、約放燈）\n')
for k,r in D['reunion'].items():
    a(f"- `{k}`（{'退群' if r.get('kind')=='gone' else '還在群組'}；{reach.get(k,0)} 條路徑看得到）：{Z(r['line'])}")
a('\n## 7. 自動檢查發現（給作者／審稿）\n')
a(f'- 全部 {P} 條路徑；退群人數分布：'+'、'.join(f'{k} 人 {v} 條' for k,v in sorted(goneC.items())))
a(f"- 永遠看不到的私訊（{len(dead)}）："+'、'.join(dead))
nev=[m for m in CL if m!='老顏' and not leaveC.get(m)]
a('- 從不會退群的同學：'+'、'.join(nev))

a('- 生活框第 3 晚為空，由「兩只戒指」頂替（設計如此）。')
open(B+'docs/spec/06-story-causality.md','w').write('\n'.join(L))
print(P,verdicts,goneC,lan,leaveC,dead)
# ---------- hand-written: pending decisions (edit here, not in the .md) ----------
open(B+'docs/spec/06-story-causality.md','a').write('''

## 8. 待決（Muse 審稿 R1＋經理判斷，2026-10-28；r4 後更新）
已處理（lines-r3，使用者核可台詞定稿 notes/lines-muse-r3.md）：
- 家豪第二次機會 → 2025e 下半改為家豪（暑期班）。
- 受傷一次未退群者結局也收到私訊（9 組）；三次版刪除；佩珊 2026 私訊可見。
- 數字統一備取 87、實拿 26K。
- 2026 佩珊改叫「老顏」。
- 外部反饋改由同學在群組轉述，不出現外人轉傳畫面；2022c 加新聞卡（TVBS）。
- r4（使用者 10-28 核可 plan-r4）：2025e 牆前群組改家豪暑期班版；出處改中央社 2024-01-26（聯合新聞網）＋國教署 2025-05-27。
待作者定（劇情層）：
1. 判詞 gone 比例偏低 → 建議 gone≥2 優先，或 self 門檻提高到 4。
2. 分支讓「選下」決定下一年犧牲誰（例：2021 選下進 2022d 只剩阿芳可傷）→ 保留為設計，或在文件／主管句點破。
3. 老顏生活框第 3 晚只有道具（兩只戒指）→ 是否補事件。
4. 2022d 上下都是阿芳：使用者 10-27 已定保留，不改。

## 9. 文案寫作規則（r4 起必守）
- 句型鐵則：講話時每個逗號、句號前最後一個實詞不得是動詞（例外只有語氣詞：啦、欸、齁、QQ…），意思要完整。
  - 退稿實例（2025e 家豪版 d1–d4）：「傳單一百張剛印好」（動詞在句尾）→「剛印好一百張傳單」；「羨慕啦，小太陽的暑期班超搶手啦」（「羨慕」在逗號前）→「小太陽的暑期班一定超搶手啦」；「小太陽加油，我幫家豪轉傳單…」→「我幫家豪把傳單轉給同學們啦」；「傳單我幫忙發同學啦」（受詞提前）退回。
- 不用「酸妳」；外人不直接發言，外界反應只由同學在群組轉述。
- 牆前群組：每條路線最多 6 句；同一路線同一人最多 2 句（主角除外）；每句不超過 24 個中文字。
- 阿芳退群後，不由別人替她說她家的事。
- 字放大後畫面放不下就自動換頁（「點一下看後續」），不靠縮字；同一人連續發言不拆；私訊在句號處切頁，不切小數點與數字。

## 10. 結局出處頁（S7，2026-10-28；規格 01 §11）
- 私訊之後的最後一屏，內容全部來自 DATA.sources（tools/sources_zh.py＋sources_en.json＋sources_rec.json）：虛構聲明 → 猜猜看（本局走過年份挑 3 題）→ 還想查什麼？（8 個建議問題，Muse 預先錄製）→ 這七年留下的海報（本局路徑 7 張）→ 截至 2026 年 10 月的公開進度。
- 和劇情的因果：猜猜看與留下的海報只依本局路徑（S.path）變，不影響判詞與私訊；虛構題只有走過 y2025e 才會出現。
''')
