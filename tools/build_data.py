import json, content_zh as C
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
    nodes[k]=o
fix=lambda s:s.replace('Old Yan','Lao Yan')
reu={k:{'line':[v['line'],fix(v.get('line_en',''))],'qa':[[q.get('a',''),fix(q.get('a_en',''))] for q in v.get('qa',[])][:3],'off':[v.get('offtopic',''),fix(v.get('offtopic_en',''))]} for k,v in R['reunion'].items()}
SELF={'0':['八年來老顏從沒退過件。最後一張她留下自己，人工生殖法草案影本還夾在卷宗裡。','In eight years Lao Yan never pushed back once. In the last photo she kept herself; the draft fertility bill is still tucked in the files.'],
'0|gray':['八年來老顏從沒退過件。最後一張她把自己裁掉，合照裡只有她是黑白的。','In eight years Lao Yan never pushed back once. In the last photo she cut herself out; she is the only one in grey.'],
'1':['老顏重做過 {n} 次。最後一張她留下自己，相框裡的照片褪了一點。','Lao Yan redid it {n} times. In the last photo she kept herself; the picture in the frame has faded a little.'],
'1|gray':['老顏重做過 {n} 次。最後一張她把自己裁掉，戒指一直戴在手上。','Lao Yan redid it {n} times. In the last photo she cut herself out; the ring never left her finger.'],
'3+':['老顏重做了 {n} 次。最後一張她留下自己，相框裡只剩一隻手。','Lao Yan redid it {n} times. In the last photo she kept herself; only one hand is left in the frame.'],
'3+|gray':['老顏重做了 {n} 次。最後一張她還是把自己裁掉了，相框裡只剩一隻手。','Lao Yan redid it {n} times. In the last photo she still cut herself out; only one hand is left in the frame.']}
VERDICT={'self':['同學都留在畫面裡，妳的生活被裁掉了','Everyone stayed in the picture. Your life got cropped.'],'gone':['宣傳照張張漂亮，合照空了一半','Every poster looked great. Half the class photo is empty.'],'mix':['誰都沒被放過，包括妳','No one was spared, not even you.']}
ui={k:([E(x) for x in v] if isinstance(v,list) else E(v)) for k,v in C.UI.items()}
ui['credit'][1]='Draft copy & translation: Meta Muse Spark 1.3 · Illustrations: Meta Muse Image 1.0 · Every policy and number is sourced'
ui['credit'][0]=C.UI['credit']
D=dict(nodes=nodes,open=[[w,E(t)] for w,t in C.OPEN],life=[E(x) for x in C.LIFE],ui=ui,reunion=reu,self=SELF,verdict=VERDICT,
 tag={k:E(v) for k,v in C.TAG.items()},names={'老顏':'Lao Yan','阿芳':'A-Fang','家豪':'Jiahao','宜君':'Yijun','志豪':'Zhihao','佩珊':'Peishan','主管':'Boss'},
 slug={'老顏':'laoyan','阿芳':'afang','家豪':'jiahao','宜君':'yijun','志豪':'zhihao','佩珊':'peishan'},
 class_=['阿芳','家豪','宜君','志豪','佩珊','老顏'],babies=['afang','jiahao','yijun','peishan'])
open('/workspace/work/bb2/data.js','w').write('// Copy drafted with Meta Muse Spark 1.3 (translations, reunion lines); insider slogans are drafts for the author to replace. Illustrations: Meta Muse Image 1.0. Built 2026-10-27.\nconst DATA='+json.dumps(D,ensure_ascii=False)+';\n')
chars=set(json.dumps(D,ensure_ascii=False))
open('chars.txt','w').write(''.join(sorted(chars))+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz–—…·・，。？！：「」（）')
print('ok',len(chars))
