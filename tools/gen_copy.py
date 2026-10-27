import json, meta
N=json.load(open('nodes.json'))
CTX=open('sources.md').read()[:6000]
SYS="""你是台灣獨立遊戲《我們這一班》的文案作者。寫給一般台灣成年人看，平實、具體、克制，不說教、不嘲諷政府、不出現任何真實官員或政治人物姓名。
遊戲：玩家是老顏（女性，1992 生），在「少子女化對策辦公室」當小編。每年一則真實政策上路，現場照片左半是受惠者、右半是替政策買單的人（都是她的國小同學）。她只能留一半做宣傳照。
- 選左：宣傳照留受惠者；右半的同學變黑白，最後在同學會走出合照。
- 選右：主管退件、老顏加班重做，她自己的生活（女性伴侶，不明說）一格格變黑白。
- 兩邊代價都要有重量；沒有好人壞人。
各欄位規則：
- L_slogan：選左時宣傳照上的官方標語。若卡片給了真實標語就原樣使用；否則寫成像真的政府宣傳標語，12 字內，粉紅海報口吻。
- R_slogan：如果宣傳照改放買單者，標語會是什麼。仍是官方口吻但看見了那個人，14 字內。
- R_aside：買單者第一次出現時寫在照片角落的一句私事，鉛筆手寫感，不表態、不抱怨政策，一個具體生活細節，18 字內。
- chat_L：選左之後同學 LINE 群組 1 則，發話者必須是被裁掉的右半那位（who 用其名字），說自己的日常近況，透露代價但不指責任何人，24 字內。
- chat_R：選右之後群組 1 則，發話者是左半那位（若左半是「家長們／新婚夫妻／抽中的家長」這類非同學，改由阿芳發話），輕描淡寫提到海報或近況，24 字內。
- 每個中文欄位都附英文版（_en），英文自然、簡短，給國際評審看。
只輸出 JSON。"""
schema={"type":"object","properties":{k:{"type":"object","properties":{f:{"type":"string"} for f in ["L_slogan","L_slogan_en","R_slogan","R_slogan_en","R_aside","R_aside_en","chat_L_who","chat_L","chat_L_en","chat_R_who","chat_R","chat_R_en","news_en","L_cap_en","R_cap_en","boss_L_en","boss_R_en"]}} for k in N}}
cards={k:{"year":v["year"],"news":v["news"],"left":v["L"]["who"]+"："+v["L"]["cap"]+("；現有標語："+v["L"]["slogan"] if "待改" not in v["L"]["slogan"] else ""),"right":v["R"]["who"]+"："+v["R"]["cap"],"boss":v["boss"]} for k,v in N.items()}
cards["y2026"]["note"]="最後一張：右半是老顏自己（桌上兩疊卷宗，中間夾著一份《人工生殖法修正草案》影本），左半是請半天陪小孩的同事；主管說『這張你自己裁』。chat_L 發話者為阿芳；chat_R 發話者為同事。"
user="真實背景資料（標語出處）：\n"+CTX+"\n\n卡片：\n"+json.dumps(cards,ensure_ascii=False,indent=1)+"\n\n為每張卡片（鍵名照用）填寫所有欄位。"
out=meta.chat([{"role":"system","content":SYS},{"role":"user","content":user}],max_tokens=16000,json_schema=schema,reasoning="medium",note="copy v1")
open('copy_v1.json','w').write(out)
print(out[:3000])
