# 檔案狀態索引（2026-10-28，L1 天燈拍）

- **當前**：遊戲正在用、或正在維護的文件。有衝突以當前為準。
- **參考**：設計理由或舊版規格，可查，不以它為準。
- **歷史**：已被取代，只保留紀錄。

內容以這個順序為準：`data.js`（遊戲實際內容）→ `docs/spec/06-story-causality.md`（由 data.js 自動生成）→ 其他 spec。

| 檔案 | 狀態 | 說明 |
|---|---|---|
| index.html | 當前 | 遊戲引擎（單檔） |
| data.js | 當前 | 全部文案、英譯、群組、結局；由 tools/build_data.py 生成，勿手改 |
| poster.woff2 | 當前 | 海報字型子集（Noto Sans TC Black） |
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
| tools/play.py | 當前 | 自動試玩＋溢出／錯誤檢查＋截圖；`wish=` 輸入老顏的燈、`expect=` 檢查回應者 |
| tools/test_lantern.js | 當前 | 結局天燈拍：打碼與回應規則單元測試（node tools/test_lantern.js） |
| tools/setup_qa.sh | 當前 | 安裝試玩測試環境 |
| tools/gen.py、tools/mkjobs.py | 當前 | 生圖工作與執行 |
| tools/gen_text.py、tools/translate.py | 參考 | 初版文案／英譯生成用，之後改為手動與 Muse 審稿 |
