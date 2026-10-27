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
            if c=='U':S['lg']=True
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
    li=2 if S['self']>=3 else (1 if S['self']+(1 if S['lg'] else 0)>=1 else 0)
    S['verdict']=v;S['lao26']=li
    S['reunion']=[m+'|'+','.join(sorted(S['cutIn'][m])) for m in S['gone']]
    return S
paths=[]
for ch in itertools.product('UD',repeat=7):
    s=run(ch);key=''.join(c for _,c in s['path'])
    if key not in [p['key'] for p in paths]:paths.append(dict(key=key,S=s))
P=len(paths)
cnt=lambda f:collections.Counter(f(p['S']) for p in paths)
verdicts=cnt(lambda s:s['verdict']);goneC=cnt(lambda s:len(s['gone']));lao=cnt(lambda s:s['lao26'])
reach=collections.Counter(k for p in paths for k in p['S']['reunion'])
dead=[k for k in D['reunion'] if k not in reach]
leaveC=collections.Counter(m for p in paths for m in p['S']['gone'])
hurtable=collections.defaultdict(list)
for k,n in N.items():
    if not n['final'] and n['D']['named']:hurtable[n['D']['who']].append(k)
# ---------- machine graph ----------
def side(n,h):
    x=n[h];return {k:(v if not isinstance(v,list) else {'zh':v[0],'en':v[1]}) for k,v in x.items()}
graph={'version':'v5 (V=20261027f)','generated_from':'data.js + engine rules in index.html',
 'state':{
  'hurt[m]':'同學 m 被犧牲次數；選上半（文宣）時 +1 給 D.who（下半照片上的人）',
  'gone':'hurt[m]==2 的同學：退群、之後群組不出現、2026 空燈、結局私訊',
  'self':'選下半（現場）次數＝老顏重做晚數；頭像 1–2 半灰、≥3 劃線',
  'laoyanGray':'2026 選上（佩珊的海報）→ 老顏的燈灰',
  'peishanGray':'2026 選下（老顏自己）→ 佩珊的燈灰、願望換成第二版',
  'baby':'新生兒數，隨機步數觸發，與選擇無關（設計：選擇不影響出生人數）'},
 'rules':[
  {'when':'choose U (poster) at non-final node','effect':'hurt[D.who]+=1 if D.named and not gone','shows':['cons[node][0..2]','hurt==1 → 被堵同學回應 cons[2]','hurt==2 → 系統訊息「已退出群組」+ 加入 gone']},
  {'when':'choose D (real) at non-final node','effect':'self+=1','shows':['主管退件 boss.D','life[self-1]；self==3 → ring_off（兩只戒指）；self>4 → again_night']},
  {'when':'group line has deps [x]','effect':'x in gone → 不顯示；dep "!x" → 只有 x in gone 才顯示'},
  {'when':'2026 ending','effect':'verdict = gone if len(gone)>=2 else self if self>=3 and no gone else mix','shows':['wish26[m][hurt>0]','lao26[2 if self>=3 else 1 if self+laoyanGray>=1 else 0]','reunion[m|sorted(cutIn)] for m in gone']}],
 'nodes':{k:{'year':n['year'],'next':n['next'],'final':n['final'],'policy_src':n['src'],
   'ask':[{'zh':a[0],'en':a[1]} for a in n['ask']],
   'U':side(n,'U'),'D':side(n,'D'),
   'U_hurts':(n['D']['who'] if n['D']['named'] and not n['final'] else None),
   'group':[{'id':f'{k}.g{i+1}','who':g[0],'zh':g[1][0],'en':g[1][1],'visible_if':{'present':[g[0]]+[d for d in g[2] if d[0]!='!'],'absent':[d[1:] for d in g[2] if d[0]=='!']}} for i,g in enumerate(D['group'].get(k,[]))],
   'choices':({'U':{'promotes':n['U']['who'],'harm':n['D']['who'] if n['D']['named'] else None,'effect':'hurt[harm]+=1','next':n['next'].get('U')},'D':{'effect':'self+=1','next':n['next'].get('D')}} if not n['final'] else {'U':{'effect':'laoyanGray=true'},'D':{'effect':'peishanGray=true'}}),
   'cons_U':[{'zh':c[0],'en':c[1]} for c in D['cons'].get(k,[])],
   'boss_D':({'zh':n['boss']['D'][0],'en':n['boss']['D'][1]} if isinstance(n.get('boss',{}).get('D'),list) else None)} for k,n in N.items()},
 'endings':{'verdict':{k:{'zh':v[0],'en':v[1]} for k,v in D['verdict'].items()},'lao26':D['lao26'],'wish26':D['wish26'],'wish2018':D['wish'],
   'reunion_keys':list(D['reunion'].keys()),'reunion_unreachable':dead},
 'path_stats':{'paths':P,'verdict':verdicts,'gone_count':goneC,'lao26_index':lao,'leaves_group':leaveC,'reunion_reach':reach},
 'paths':[{'key':p['key'],'nodes':[n for n,_ in p['S']['path']],'gone':p['S']['gone'],'self':p['S']['self'],'verdict':p['S']['verdict'],'lao26':p['S']['lao26']} for p in paths]}
json.dump(graph,open(B+'docs/spec/06-story-graph.json','w'),ensure_ascii=False,indent=1)
# ---------- human doc ----------
L=[]
a=L.append
a('# 06 遊戲敘事與因果（v5，自動生成）\n')
a('> 由 `tools/story_doc.py` 從 data.js 與引擎規則生成；機器版＝`06-story-graph.json`（同一份資料）。台詞全文對照見雲端「我們這一班_文案台詞對照」。改文案或引擎後重跑，勿手改本檔的生成段落。\n')
a('## 1. 一句話\n2018 年平溪放天燈，六個同學各許一個願。老顏進公部門做政策宣傳，每年要從兩張照片裁一張：上半＝政府文宣（某位同學被拍成「受益者」）、下半＝現場（同學真實的處境）。選文宣，海報被轉傳去堵那位同學的嘴；選現場，主管退件、老顏自己重做一晚。2026 年再回平溪，誰還在、誰的燈是空的，就是這八年的帳。\n')
a('## 2. 狀態與因果規則\n')
a('| 狀態 | 意義 | 怎麼變 | 看得到的地方 |\n|---|---|---|---|')
a('| hurt[同學] | 被犧牲次數 | 選上半 → 下半照片上的那位 +1 | 頭像劃線（1）、淡出（2） |')
a('| gone | 退群名單 | hurt 到 2 | 「已退出群組」、之後群組不出現、他和依賴他的句子消失、2026 空燈＋私訊 |')
a('| self | 老顏重做晚數 | 選下半 +1 | 頭像半灰（1–2）、劃線（≥3）；生活框四階 |')
a('| laoyanGray／peishanGray | 2026 最後一刀 | 2026 選上→老顏灰；選下→佩珊灰 | 平溪燈 |')
a('| baby | 本班小朋友數 | 隨機步數，與選擇無關 | 下一年群組貼照片 |\n')
a('**群組台詞的依賴標記**：〔依賴 A〕＝A 還在群組才出現；〔依賴 A、B〕＝兩人都在才出現；〔依賴 !A〕＝A 已退群才出現。說話者本人退群，他的句子全部不出現。\n')
a('**2026 是獨立的最後一刀**：不計入 hurt／gone／self，只決定誰的燈變灰（選上→老顏、選下→佩珊，佩珊願望換第二版），判詞不受影響。\n')
a('## 2.1 真相表（每年選上／選下的直接後果）\n')
a('| 年 | 選上（文宣） | 選下（現場） |\n|---|---|---|')
for k,n in N.items():
    if n['final']:a(f"| {n['year']}{k[5:]} | 捧佩珊 → 老顏的燈灰 | 留老顏 → 佩珊的燈灰 |");continue
    pro=n['U']['who'] if n['U']['named'] else Z(n['U'].get('whoE',n['U']['who']))
    a(f"| {n['year']}{k[5:]} | 捧{pro}；{n['D']['who']} hurt+1（被拿海報堵嘴）→ {n['next']['U'][1:]} | 老顏 self+1 → {n['next']['D'][1:]} |")
a('')
a('## 2.2 角色生死簿（退群要被犧牲 2 次）\n')
for m in CL:
    if m=='老顏':continue
    a(f"- {m}：機會在 {'、'.join(x[1:] for x in hurtable.get(m,[])) or '無（只在 2026 受影響）'}；實際退群 {leaveC.get(m,0)}/{P} 條路徑")
a('')
a('**老顏生活框（選下半後）**')
for i,l in enumerate(D['life']):
    a(f"- 第 {i+1} 晚：{Z(l) or Z(D['ring_off'])}")
a(f"- 第 5 晚以後：{Z(D['ui']['again_night'])}\n")
a('**2026 結局判詞**（gone≥2 → gone；self≥3 且無人退群 → self；其餘 → mix）')
for k,v in D['verdict'].items():a(f'- {k}：{v[0]}（{verdicts.get(k,0)}/{P} 條路徑）')
a('\n**老顏的燈**：self≥3 →「'+(Z(D['lao26'][2]) or '（空白）')+'」；self＋(2026 選上?1:0)≥1 →「'+Z(D['lao26'][1])+'」；都沒有 →「'+Z(D['lao26'][0])+'」\n')
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
    a(f"| {m} | {Z(D['wish'][m])} | {Z(D['wish2'][m])} | {'、'.join(hurtable.get(m,[])) or ('2026（最後一刀）' if m in ('老顏','佩珊') else '—')} | {leaveC.get(m,0)}/{P} | {(Z(w26[0])+'／'+Z(w26[1])) if w26 else '見老顏的燈'} |")
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
        a('- 選上：佩珊的海報留下 → 老顏的燈灰。選下：老顏自己的照片留下 → 佩珊的燈灰、願望換第二版。→ 結局\n');continue
    c=D['cons'].get(k)
    hit=n['D']['who'] if n['D']['named'] else None
    a(f"- 選上 → 犧牲 **{hit}**（hurt+1）→ 下一年 {n['next']['U']}")
    if c:a(f"  - 轉傳：{Z(c[0])}｜施壓：{Z(c[1])}｜{hit}回應（第一次）：{Z(c[2])}｜第二次：{hit}已退出群組")
    a(f"- 選下 → 老顏重做一晚（self+1）→ 主管：{Z(n['boss']['D'])} → 下一年 {n['next']['D']}\n")
a('## 6. 結局私訊（缺席者）\n')
for k,r in D['reunion'].items():
    a(f"- `{k}`（{reach.get(k,0)} 條路徑看得到）：{Z(r['line'])}")
a('\n## 7. 自動檢查發現（給作者／審稿）\n')
a(f'- 全部 {P} 條路徑；退群人數分布：'+'、'.join(f'{k} 人 {v} 條' for k,v in sorted(goneC.items())))
a(f"- 永遠看不到的私訊（{len(dead)}）："+'、'.join(dead))
nev=[m for m in CL if m!='老顏' and not leaveC.get(m)]
a('- 從不會退群的同學：'+'、'.join(nev))
a('- 佩珊只在 2026 受影響，不進 hurt／gone，故 `佩珊|y2026` 私訊不會出現。' if '佩珊|y2026' in dead else '')
a('- 生活框第 3 晚為空，由「兩只戒指」頂替（設計如此）。')
open(B+'docs/spec/06-story-causality.md','w').write('\n'.join(L))
print(P,verdicts,goneC,lao,leaveC,dead)
# ---------- hand-written: pending decisions (edit here, not in the .md) ----------
open(B+'docs/spec/06-story-causality.md','a').write('''

## 8. 待決（Muse 審稿 R1＋經理判斷，2026-10-28）
已直接改（文件層）：分支圖改「捧誰／傷誰」、加真相表與生死簿、定義依賴標記、2026 獨立規則、JSON 加 visible_if／choices。
待作者定（劇情層）：
1. 家豪只有 2018 一次機會，永不退群 → 建議 2024 或 2025 加一次以家豪為下半的機會。
2. 10 封私訊永遠看不到（單次受傷版、三次版、佩珊 2026）→ 建議：受傷 1 次未退群的人，結局也收到「安慰版」私訊；三次版刪除。
3. 判詞 gone 只有 12/128 → 建議 gone≥2 優先，或 self 門檻提高到 4。
4. 分支讓「選下」決定下一年犧牲誰（例：2021 選下進 2022d 只剩阿芳可傷）→ 保留為設計，或在文件／主管句點破。
5. 數字不一致：私訊寫備取 72 號、28K，群組是 87、26K → 統一為 87、26K（私訊另外整批改寫「連上十二天」等舊句）。
6. 2026 群組佩珊叫老顏「顏座」、把案子交給她 → 需交代同部會或改口吻。
7. 老顏生活框第 3 晚只有道具（兩只戒指）→ 是否補事件。
8. 2022d 上下都是阿芳：使用者 10-27 已定保留，不改。
''')
