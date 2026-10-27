import json, meta
SYS=open('gen_copy.py').read().split('SYS="""')[1].split('"""')[0]
N=json.load(open('nodes.json')); C=open('copy_v1.json').read()
facts="""角色事實：阿芳＝有小孩的媽媽（2018 受惠；2019b 抽公幼只拿到備取，轉私幼；2021 停課在家陪孩子；2022d 離職領津貼在家；2024 六點接小孩）。家豪＝開小型私幼的園長。小芸老師＝家豪園裡的教保員。志豪＝單身上班族，停課時扛兩人份的班，租屋。宜君＝公幼老師，延托後六點還牽著孩子，寒暑假被要求到園。同事＝老顏辦公室同事，有小孩。抽中的家長、家長們、新婚夫妻＝非同學路人。
群組規則：chat_L 發話者＝右半被裁掉的人；chat_R 發話者＝左半那位同學，若左半是路人則由阿芳發話，且內容必須符合阿芳當年的處境。"""
out=meta.chat([{"role":"system","content":SYS},{"role":"user","content":facts+"\n\n卡片：\n"+json.dumps(N,ensure_ascii=False)+"\n\n初稿：\n"+C+"\n\n逐欄檢查初稿：與角色事實或卡片矛盾、發話者錯誤、語意不通、像機器翻譯、超過字數的地方，全部修正。其他保留。輸出完整修正後 JSON（相同結構）。"}],max_tokens=16000,json_schema=None,reasoning="medium",note="copy v2 fix")
s=out[out.find('{'):out.rfind('}')+1]; json.loads(s); open('copy_v2.json','w').write(s)
