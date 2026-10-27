import json, meta
N=json.load(open('nodes.json')); combos=json.load(open('combos.json'))
SYS=open('gen_copy.py').read().split('SYS="""')[1].split('"""')[0].split('各欄位規則')[0]
items=[]
for who,lst in combos.items():
    for c in lst:
        items.append({"key":who+"|"+",".join(c),"who":who,"cut_in":[{"year":N[n]["year"],"news":N[n]["news"],"they_were":N[n]["R"]["cap"],"poster_showed_instead":N[n]["L"]["who"]+"："+N[n]["L"]["cap"]} for n in c]})
for tier in ["0","1","2","3+"]:
    for gray in [False,True]:
        items.append({"key":"老顏|"+tier+("|gray" if gray else ""),"who":"老顏","note":f"老顏這幾年為了不裁同學、自己加班重做了 {tier} 次（生活框黑白 {tier} 格；伴侶是女性，不明說）。"+("2026 最後一張她把自己裁掉了，她是拿相機的人，走不了，留在合照裡變黑白。" if gray else "2026 最後一張她留下了自己。")})
RULE="""2026 同學會合照。黑白的同學起身走出合照，走出前對老顏說一句話。
每個 key 寫：
- line：走出前那句代價，30–45 字，第一人稱，平靜具體，必須含一個具體數字（年數、金額、小時、人數、次數皆可，合理即可），不指責老顏，不提政策名稱。
- line_en：英文版。
- qa：玩家可追問的三題固定問題的回答，每題 25–40 字，第一人稱，同一個人的語氣：
  q1「後來呢？」 q2「妳／你怪我嗎？」 q3「那時候你需要的是什麼？」（回答要具體，像真人會要的東西，不是口號）
  每題附英文 a_en。
老顏的 key：line 是老顏自己的內心一句（不是對誰說），qa 也是她回答自己。
只輸出 JSON：{key:{line,line_en,qa:[{a,a_en},{a,a_en},{a,a_en}]}}"""
out=meta.chat([{"role":"system","content":SYS},{"role":"user","content":RULE+"\n\n角色事實：阿芳＝媽媽；家豪＝私幼園長；小芸老師＝家豪園裡的教保員；志豪＝單身租屋上班族；宜君＝公幼老師；同事＝老顏的同事，有小孩，2026 按日請育嬰假。\n\n清單：\n"+json.dumps(items,ensure_ascii=False,indent=1)}],max_tokens=20000,reasoning="medium",json_schema={"type":"object","additionalProperties":{"type":"object","properties":{"line":{"type":"string"},"line_en":{"type":"string"},"qa":{"type":"array","items":{"type":"object","properties":{"a":{"type":"string"},"a_en":{"type":"string"}}}}}}},note="reunion v1")
open('reunion_raw.txt','w').write(out); s=out[out.find('{'):out.rfind('}')+1]; d=json.loads(s); open('reunion_v1.json','w').write(json.dumps(d,ensure_ascii=False,indent=1))
for k,v in d.items(): print(k,'→',v['line'],'||',' / '.join(q['a'] for q in v['qa']))
