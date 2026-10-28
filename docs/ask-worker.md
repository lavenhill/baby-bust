# 出處頁「還想查什麼？」即時查詢（目前關閉）

現在遊戲只用**錄好的答案**：8 個建議問題的答案是 Meta Muse 事先挑好的出處原句（tools/sources_rec.json），畫面標「預先錄製」，不連任何伺服器、不需要金鑰。

## 開關
`index.html` 裡：

```js
const ASK_URL=window.BB_ASK_URL||'';
```

- 空字串（預設）＝關：只有建議問題，沒有輸入框。
- 改成 Worker 網址（例如 `'https://bb-ask.<帳號>.workers.dev'`）＝開：多一個輸入框（≤40 字），玩家自己打的問題送 Worker 由 Muse 即時挑句；建議問題仍用錄好的答案。

## Worker（tools/ask_worker.js，未部署）
- 由出處庫產生：改了 tools/sources_zh.py 之後跑 `python3 tools/sources_muse.py worker`，系統提示與 64 個句子編號才會同步。
- 只做一件事：把玩家問題和整個出處庫送 Muse（muse-spark-1.3，reasoning minimal），只回 `{"type","picks"}`；不在出處庫裡的編號會被丟掉，最多 3 句。Muse 不寫任何事實。
- 護欄：只收 raw.githack.com、lavenhill.github.io 來源；每 IP 每日 10 次；總花費到 US$5 就熔斷（之後回 offline，遊戲顯示「離線查證模式」）；不存玩家原文，只存次數與金額。
- 金鑰：不在 repo。部署時放 Worker secret `META_KEY`。

## 部署步驟（需使用者帳號與金鑰，由使用者決定）
1. 開 Cloudflare 帳號，安裝 wrangler。
2. `wrangler kv namespace create ASK_KV`，把 id 寫進 wrangler.toml 的 `kv_namespaces`（binding = "ASK_KV"）。
3. `wrangler secret put META_KEY`（貼上 Meta API 金鑰）。
4. `wrangler deploy tools/ask_worker.js`，拿到網址。
5. 把網址填進 index.html 的 `ASK_URL`，跑 tools/play.py（`live=mock|down|slow` 已測過開關），再推版。

成本與上限的估算：notes/ai-sources-cost-2026-10-28.md（專案筆記，不在 repo）。
