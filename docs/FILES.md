# 檔案狀態索引（2026-10-28，出處頁＋誰在倡議，V=20261028f）

- **當前**：遊戲正在用、或正在維護的文件。有衝突以當前為準。
- **參考**：設計理由或舊版規格，可查，不以它為準。
- **歷史**：已被取代，只保留紀錄。

內容以這個順序為準：`data.js`（遊戲實際內容）→ `docs/spec/06-story-causality.md`（由 data.js 自動生成）→ 其他 spec。

| 檔案 | 狀態 | 說明 |
|---|---|---|
| index.html | 當前 | 遊戲引擎（單檔） |
| data.js | 當前 | 全部文案、英譯、群組、結局；由 tools/build_data.py 生成，勿手改 |
| poster.woff2 | 當前 | 海報字型子集（Noto Sans TC Black；pyftsubset，舊字集＋chars.txt 聯集） |
| img/ | 當前 | Muse Image 生成的插圖（tools/gen.py） |
| README.md | 當前 | 專案說明 |
| docs/FILES.md | 當前 | 本索引 |
| docs/spec/06-story-causality.md | 當前 | 敘事與因果（人讀版）：狀態規則、分支圖、角色線、逐年劇情、自動檢查 |
| docs/spec/06-story-graph.json | 當前 | 同上（機器版）：節點、規則、128 條路徑結果 |
| docs/spec/00-requirements.md | 當前 | 需求書（v5 條目待補） |
| docs/spec/01-game-spec.md | 當前（待同步 v5；§10 結局天燈拍為 L1 當前規格） | 狀態機、驗收測試 |
| docs/spec/03-ui-layout.md | 當前（待同步 v5） | 版面 |
| docs/spec/05-design-principles.md | 當前 | 設計準則 |
| docs/spec/02-narrative.md | 參考 | v2 逐節點腳本，已被 06 取代 |
| docs/spec/04-defects-and-plan.md | 參考 | v2 缺陷表與重構計畫 |
| docs/devlog/ | 當前 | 開發日記（每 12 小時自動補寫） |
| tools/content_zh.py | 當前 | 中文文案原始檔 |
| tools/build_data.py | 當前 | content_zh＋en.json＋reunion → data.js |
| tools/story_doc.py | 當前 | 從 data.js 生成 06 文件與 JSON |
| tools/copy_map.py | 當前 | 從 data.js 生成文案台詞對照表（xlsx） |
| tools/play.py | 當前 | 自動試玩＋溢出／錯誤檢查＋截圖；`wish=` 輸入老顏的燈、`expect=` 檢查回應者；S7 起逐項驗出處頁（猜猜看全選項、建議問題全點、連結、斷網），`live=mock|down|slow` 測即時開關 |
| tools/sources_zh.py | 當前 | 出處頁：出處庫 22 張政策卡（含放回的 F07）＋56 張倡議者卡（A01–A57，A43 空號），共 122 句，每句開過原文核對；NODE_ADV＝每個選項的倡議者；猜猜看、9 個建議問題、公開進度、介面字 |
| tools/sources_en.json | 當前 | 出處頁英文（Muse 初譯、Hark 審） |
| tools/sources_rec.json | 當前 | 建議問題的錄製答案（Muse 只挑句子編號；每題 3 次挑 1 次，理由在 why；2026-10-28 出處庫擴充後重錄，挑選腳本 qa/adv/pick_rec.py） |
| qa/adv/ | 當前 | 誰在倡議的研究與 QA：原文快取 pages.json、Muse 摘要初稿 muse_sum.json、英譯 en_muse.json、重錄與成本實測 jsonl、審稿 review_r1/r2＋review_disposition.md、試玩結果 run/、推版前備份 bak/*.apre.bak |
| tools/sources_muse.py | 當前 | Muse 檢索：錄製（record）、成本實測（cost）、產生 Worker（worker） |
| tools/ask_worker.tpl.js、tools/ask_worker.js | 當前（未部署） | 即時查詢 Cloudflare Worker 草稿；不含金鑰；ask_worker.js 由 sources_muse.py 產生 |
| docs/ask-worker.md | 當前 | 即時查詢開關與部署步驟（預設關） |
| tools/test_lantern.js | 當前 | 結局天燈拍：打碼與回應規則單元測試（node tools/test_lantern.js） |
| tools/setup_qa.sh | 當前 | 安裝試玩測試環境 |
| tools/gen.py、tools/mkjobs.py | 當前 | 生圖工作與執行 |
| tools/gen_text.py、tools/translate.py | 參考 | 初版文案／英譯生成用，之後改為手動與 Muse 審稿 |
