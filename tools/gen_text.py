import json,sys
sys.path.insert(0,'/workspace/work/meta'); import meta
from content_zh import *
from concurrent.futures import ThreadPoolExecutor
combos=json.load(open('combos.json'))
BIBLE="""遊戲《我們這一班》：老顏（女，1992 生）2018 起在少子女化對策辦公室當小編，每年政策上路，宣傳照只能拍一邊。被她留在宣傳照外的國小同學，八年後同學會時自己走出合照。
同學：阿芳（家長，兒子 2017 生，想回去上班）；家豪（私幼園長，爸媽留下的小園）；宜君（2019 在家豪園當教保員月薪 28K，2023 考上公幼老師，顧延托、寒暑假到園）；志豪（單身上班族，租屋，常替有小孩的同事代班）；佩珊（老顏辦公室同事兼同學，兒子 2024 生，2026 按日請育嬰假，案子交給老顏代理）。
每年（妳選了不拍他的那年發生的事）：
y2018 準公共上路，家豪隔壁園變準公共，他少了十五個學生、大班併班。
y2019a 家豪加入準公共後收費被壓，宜君加薪落空，媽媽問她要不要轉行。
y2019b 阿芳公幼抽籤備取沒上，只好先報私幼。
y2021 停課，同事請照顧假，志豪連上十二天班替人代班。
y2022c 租金補貼育兒家庭加碼 1.8 倍，志豪單身被房東漲租，還要代班。
y2022d 育兒津貼 5,000，阿芳被迫離職在家帶孩子。
y2024 延托開到傍晚，宜君六點半才吃得到飯。
y2025e 公幼寒暑假照常開園，宜君假單被退、機票改到過年後。
y2025f 婚育宅新婚育兒優先，志豪單身排最後，租約續一年。
y2026 按日育嬰留停：老顏最後一張拍了自己（替佩珊代理的人），沒拍請假的佩珊。佩珊是請假的那一方：她那幾天請了三個半天，群組裡道歉兩次，回來看到老顏桌上替她堆的卷宗。
寫作規則：繁體中文、聊天口吻、一般人看得懂；對老顏稱「妳」；具體、有一件小物或小事；不說教、不評論真實政治人物；不提「宣傳照」「海報」以外的遊戲機制。"""
SCH={"type":"object","properties":{"line":{"type":"string"},"line_en":{"type":"string"},"qa":{"type":"array","items":{"type":"object","properties":{"a":{"type":"string"},"a_en":{"type":"string"}}}},"offtopic":{"type":"string"},"offtopic_en":{"type":"string"}}}
def J(p,sch,note,mt=6000):
    for i in range(3):
        r=meta.chat([{"role":"user","content":p}],json_schema=sch,max_tokens=mt,reasoning="low",note=note)
        if r:
            try: return json.loads(r)
            except Exception: pass
    raise SystemExit('fail '+note)
def mate(k):
    m,nodes=k.split('|')
    p=BIBLE+f"\n\n同學會上，{m} 要從合照走出去前，對老顏說一句代價（≤45 字），只講妳沒拍他的那些年：{nodes}。若多年，提到累積。再寫三個追問的回答（≤40 字）：Q1 後來呢？ Q2 你怪我嗎？ Q3 那時候你需要的是什麼？ 再寫 offtopic：老顏問了跟這無關的怪問題時，他用角色口吻帶回自身處境的一句（≤35 字）。每句附自然英文翻譯（Lao Yan 用 you）。輸出 JSON。"
    return k,J(p,SCH,"v2 reunion "+k)
def selfline(t):
    s,g=t
    p=BIBLE+f"\n\n寫老顏同學會上的一句內心獨白（≤40 字，第三人稱「老顏」）：她八年裡有 {s}{'+' if s==3 else ''} 次不肯裁同學、自己加班重做（用 {{n}} 代表次數）；最後一張她{'拍了請假的佩珊，裁掉了自己' if g else '拍了自己，裁掉了佩珊'}。具體一件物件（戒指、相框、凍卵回診單、人工生殖法草案影本擇一）。附英文。輸出 JSON {{\"line\":..,\"line_en\":..}}"
    return f"老顏|{s}{'+' if s==3 else ''}{'|gray' if g else ''}",J(p,{"type":"object","properties":{"line":{"type":"string"},"line_en":{"type":"string"}}},"v2 self")
def verdicts():
    p=BIBLE+"\n\n結局斷語：一句 ≤18 字、像報紙標題、先下判斷、帶點苦澀。依三個維度各寫一句：走出人數 few(0-1)/some(2)/many(3+) × 老顏重做次數 none(0)/some(1-2)/many(3+) × 最後一張 gray(拍佩珊、裁自己)/keep(拍自己、裁佩珊)。共 18 句，key 格式 few|none|gray。附英文。輸出 JSON {\"items\":[{\"key\":..,\"zh\":..,\"en\":..}]}"
    return J(p,{"type":"object","properties":{"items":{"type":"array","items":{"type":"object","properties":{"key":{"type":"string"},"zh":{"type":"string"},"en":{"type":"string"}}}}}},"v2 verdicts",9000)
out={"reunion":{},"self":{}}
with ThreadPoolExecutor(8) as ex:
    fv=ex.submit(verdicts)
    for k,v in ex.map(mate,combos): out["reunion"][k]=v
    for k,v in ex.map(selfline,[(s,g) for s in range(4) for g in (False,True)]): out["self"][k]=v
    json.dump(out,open("reunion_partial.json","w"),ensure_ascii=False)
    out["verdict"]={i.get("key"):[i.get("zh",""),i.get("en","")] for i in fv.result()["items"]}
json.dump(out,open('reunion_v3.json','w'),ensure_ascii=False,indent=1);print(len(out["reunion"]),len(out["self"]),len(out["verdict"]))
