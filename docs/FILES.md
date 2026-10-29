# 檔案狀態索引（2026-10-28，2025e 宜君方案 A＋新標題＋英文名與白話英譯，V=20261028h）

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
| sources/ | 當前 | 出處本地存檔頁 R01–R91.html（f29，2026-10-29）；Rxx＝tools/sources_zh.py REFS 順序。政府新聞稿、公告、問答、行政規則（著作權法第9條公文）存正文全文 15 筆；媒體、NGO、醫院與自聲明著作權的勞動部調查報告共 76 筆只存支持遊戲句子的原文摘錄（第52條）；附原文網址與 Wayback 存檔連結。由 qa/f29/mkpages.py 產生（不在 repo），build_data.py 檢查每筆都有、play.py 檢查連結 |
| README.md | 當前 | 專案說明 |
| docs/FILES.md | 當前 | 本索引 |
| docs/spec/06-story-causality.md | 當前 | 敘事與因果（人讀版）：狀態規則、分支圖、角色線、逐年劇情、自動檢查 |
| docs/spec/06-story-graph.json | 當前 | 同上（機器版）：節點、規則、128 條路徑結果 |
| docs/spec/00-requirements.md | 當前 | 需求書（v5 條目待補） |
| docs/spec/01-game-spec.md | 當前（待同步 v5；§10 結局天燈拍為 d29「三盞」限定選項當前規格） | 狀態機、驗收測試 |
| docs/spec/03-ui-layout.md | 當前（待同步 v5） | 版面 |
| docs/spec/05-design-principles.md | 當前 | 設計準則 |
| docs/spec/02-narrative.md | 參考 | v2 逐節點腳本，已被 06 取代 |
| docs/spec/04-defects-and-plan.md | 參考 | v2 缺陷表與重構計畫 |
| docs/devlog/ | 當前 | 開發日記（每 12 小時自動補寫） |
| tools/content_zh.py | 當前 | 中文文案原始檔 |
| tools/build_data.py | 當前 | content_zh＋en.json＋reunion → data.js |
| tools/story_doc.py | 當前 | 從 data.js 生成 06 文件與 JSON |
| tools/copy_map.py | 當前 | 從 data.js（＋index.html 內建介面字）生成文案台詞對照表（xlsx，只在本機） |
| tools/sheet_sync.py | 當前 | 文案表與源碼同步：pull／apply（只回寫中文、英文不動）／push（有使用者未回寫修改時拒絕覆蓋） |
| tools/play.py | 當前 | 自動試玩＋溢出／錯誤檢查＋截圖；2026-10-28 h 版起另查：標題頁（中文一行、不溢出）、正文禁「暑期班」「我們這一班」、2025e 下半必須是宜君、英文畫面禁舊拼音名／quasi／拼音術語、英文出處頁不得殘留中文；`wish=` 輸入老顏的燈、`expect=` 檢查回應者；FX 起檢查情節依據卡（.spfact.basis）與遊戲正文禁用說法（議員、考上中央、考績乙等、請半天、凍卵回診、婆婆把…）；S7 起逐項驗出處頁（猜猜看全選項、建議問題全點、連結、斷網），`live=mock|down|slow` 測即時開關；c29（2026-10-29）起另查「無空資料」：猜猜看每個選項、每個建議問題、海報展開／依據卡／倡議、私訊追問都必須有內容且無 undefined／null，另對全部題目與出處做靜態檢查 |
| tools/sources_zh.py | 當前 | 出處頁：出處庫 22 張政策卡（含放回的 F07）＋11 張情節依據卡（F23–F33，kind=basis，多連結 refs；FX 2026-10-28）＋61 張倡議者卡（A01–A62，A43 空號），共 152 句，每句開過原文核對；NODE_ADV＝每個選項的倡議者；猜猜看、9 個建議問題、公開進度、介面字 |
| tools/sources_en.json | 當前 | 出處頁英文（Muse 初譯、Hark 審） |
| tools/sources_rec.json | 當前 | 建議問題的錄製答案（Muse 只挑句子編號；每題 3 次挑 1 次，理由在 why；2026-10-28 出處庫擴充後重錄，挑選腳本 qa/adv/pick_rec.py） |
| qa/yj/ | 當前 | 2025e 方案 A＋標題＋英文名／白話英譯（2026-10-28 21:3x–22:xx）：原文摘錄 pages.json、Muse 初稿 muse_r1.json、審譯 muse_r2.json、英文白話掃描 en_r1.json／en_r2.json、套用腳本 apply*.py、names.py、試玩結果 run/、標題檢查 title_check.py、推前備份 bak/*.ypre.bak |
| qa/fx/ | 當前 | FX 情節依據與約聘改寫（2026-10-28）：原文快取 pages.json＋cand.json、Muse 台詞初稿 muse_lines_r1.json／審稿 muse_rev_r2.json、英譯 en_basis_muse.json、diff 審稿 muse_diff_r1/r2.json、試玩 run/、推版前備份 bak/*.fpre.bak |
| qa/adv/ | 當前 | 誰在倡議的研究與 QA：原文快取 pages.json、Muse 摘要初稿 muse_sum.json、英譯 en_muse.json、重錄與成本實測 jsonl、審稿 review_r1/r2＋review_disposition.md、試玩結果 run/、推版前備份 bak/*.apre.bak |
| tools/sources_muse.py | 當前 | Muse 檢索：錄製（record）、成本實測（cost）、產生 Worker（worker） |
| tools/ask_worker.tpl.js、tools/ask_worker.js | 當前（未部署） | 即時查詢 Cloudflare Worker 草稿；不含金鑰；ask_worker.js 由 sources_muse.py 產生 |
| relay/server.py | 當前（未上線） | 出處頁即時查詢中繼（Python 3.13 標準庫；Botkeep 主案）：只打寫死的 api.meta.ai、只回 data.js 現有的句子編號最多 3 個；每 IP 段每日 30、全站每分鐘 20、總 700 次（ASK_CAP_N）＋US$10 雙上限，SQLite 先扣再打；計數檔在 DATA_DIR（預設 repo 外）；不記問句。index.html 的 ASK_URL 仍空字串 |
| relay/test_relay.py | 當前 | 中繼測試（本機假 Meta，不花錢）：health、超長、多餘欄位、非法編號、700 次熔斷、每 IP 限額、每分鐘、US$ 上限、無金鑰、逾時、CORS、隱私、併發 |
| docs/ask-worker.md | 當前 | 即時查詢開關與部署步驟（預設關） |
| tools/test_lantern.js | 歷史（d29 起不適用） | L1 自由輸入的打碼與關鍵字回應規則單元測試；d29 改限定選項後由 tools/play.py 的選項靜態檢查（128 條路徑×中英）取代 |
| tools/lantern_opts_128.json | 當前 | 老顏的燈 128 條路徑按鈕組合參考答案（鍵、目標、回覆者；d29 r2 試做產生），play.py 靜態檢查比對用 |
| tools/setup_qa.sh | 當前 | 安裝試玩測試環境 |
| tools/gen.py、tools/mkjobs.py | 當前 | 生圖工作與執行 |
| tools/gen_text.py、tools/translate.py | 參考 | 初版文案／英譯生成用，之後改為手動與 Muse 審稿 |
