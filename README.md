# Baby or Bust（我們與孩子的距離 / Between Us and the Kids）

A short story game about who pays for Taiwan’s childcare and family policies, built for the Meta AI Developer Hackathon 2026.

**Play:** https://raw.githack.com/lavenhill/baby-bust/main/index.html (mobile first; tap EN for English)

**Built from scratch during the hackathon.** This repository was created on 2026-10-27 (Asia/Taipei), after the event opened (2026-10-26 12:00 PM ET). Every file here is new work made during the event period (Oct 27 – Nov 4, 2026). No earlier codebase is reused; earlier prototypes by the same author served only as inspiration.

## How it plays
You are Vivian, a contract worker who runs social media for a government office on low birth rates. Each year a real policy launches. The photo from the scene has two halves: the people it helps, and the classmate who pays for it. You can only publish one half.
- Keep the beneficiaries: your classmate on the other half fades to grey, and walks out of the class reunion photo at the end.
- Keep the one who pays: your boss rejects it, you redo it overnight, and your own life fades one frame at a time.
- The feed scrolls down like your desk piling up. You can look back, but never re-crop.
- At the 2026 reunion, everyone you cropped out says what it cost them. Ask them three questions.

Every policy, number and date in the game is real and sourced at the end of each run.

## How Meta AI is used
| Model | Used for |
|---|---|
| Muse Spark 1.3 (`muse-spark-1.3`) | Draft slogans, private asides, group-chat lines, a self-review pass for consistency, and all English translations (`tools/gen_copy.py`, `tools/fix_copy.py`) |
| Muse Spark 1.3 | Reunion: one cost line + answers to 3 follow-up questions for every classmate × every path they could have been cut on (14 combinations) and Vivian's own line for 8 endings (`tools/gen_reunion.py`) |
| Muse Spark 1.3 | Sources page “Anything else to check?”: Muse only **picks sentence IDs** from a 64-line library of verified source quotes (it never writes a fact); the screen shows those exact lines with links. The 8 suggested questions use answers **pre-recorded** with Muse and checked by hand, and are labelled “pre-recorded”. A live mode exists behind a switch (`ASK_URL` in `index.html`, Cloudflare Worker draft `tools/ask_worker.js`, no key in this repo) and is **off** (`tools/sources_muse.py`, `docs/ask-worker.md`) |
| Muse Image 1.0 (`muse-image-1.0`) | 7 character reference sheets, then 20 scene halves and 5 objects generated with `images/edits` from those references, so characters stay consistent across years (`tools/gen_img.py`) |

All generation runs at build time through `tools/meta.py` (Meta Model API, `https://api.meta.ai/v1`, key from `MODEL_API_KEY`, spend ledger). Total build cost on day 1: about US$0.60. The page itself is static and contains no key. Human review: the author edits the final copy; AI drafts are kept in `data.js`.

## Files
- `index.html` — the game (no framework)
- `data.js` — all copy (zh + en), reunion lines, AI-generated
- `img/` — Muse Image illustrations
- `poster.woff2` — poster headline font: a subset of Noto Sans TC Black (weight 900), SIL Open Font License 1.1 (license text: `poster-font-OFL.txt`)
- `tools/` — generation scripts

## Status
- 2026-10-27: repo created; minimal playable build; scrolling-desk layout; Meta AI copy, translations, reunion lines and illustrations wired in.
- 2026-10-28 (V=20261028h): 2025 lower half is Jessica again (public preschool teachers working through summer break, sourced); title changed to 我們與孩子的距離 / Between Us and the Kids; English version uses English names (Vivian, Amy, Kevin, Jessica, Jason, Penny) and plain-English childcare terms.

---

## 中文說明
家庭照顧政策取捨敘事遊戲，為 Meta AI Developer Hackathon 2026 製作。你是少子女化對策辦公室的小編老顏，每年一張現場照，只能留一半：留受惠者，另一半的同學變黑白、在同學會走出合照；留買單的人，主管退件、你加班重做，自己的生活一格格褪色。文字初稿、英文翻譯、同學會台詞由 Meta Muse Spark 1.3 生成，插畫由 Muse Image 1.0 生成，作者審稿。

本 repo 於 2026-10-27（台北時間）活動開始後新建，所有檔案皆為活動期間的新作，未沿用任何舊 codebase；作者先前的試作僅作為靈感參考。

## v2 (2026-10-27)
- Design principles (author's rules): `docs/spec/05-design-principles.md`
- Requirements → spec → narrative → UI → defects: `docs/spec/00`–`04`
- Portrait-first: each policy photo is split top/bottom; push away the half you don't keep (swipe up keeps the bottom). The kept half becomes a government-style campaign poster; the other stays a grey real-life photo.
- Six classmates, an opening promise photo and a reunion at the same building.
- Tools: `tools/` (Meta Muse Image / Muse Spark generation scripts, `play.py` headless playtest).

## lines-r3 (2026-10-28)
- 台詞定稿 r3：每年選上半後的「群組後果」改由同學在群組轉述外人的話（不出現外人轉傳畫面）；2022c 加新聞卡（TVBS 2022-07-20、2022-09-28）；2025e 下半改為家豪的暑期班。
- 結局私訊：退群者（受傷兩次）5 組冷調；受傷一次仍在群組者 9 組（含佩珊 2026）。
- 標題字型 `poster.woff2`：Noto Sans TC Black 子集，SIL OFL 1.1。

## L1 lantern (2026-10-28)
- Ending: at the 2026 Pingxi reunion the player writes Vivian's own sky lantern (up to 12 characters, Chinese or English; blank allowed). A fixed 5-second release follows, Penny posts a photo to the group chat, and one classmate still in the group answers.
- Runs entirely in the page: keyword rules + pre-written lines (`tools/content_zh.py` `LANTERN_*`, `data.js` `lantern`). No AI call, no key, no server. Profanity is masked as ▇.
- Lines: drafted by Muse Spark 1.3 and reviewed by Hark; English by Muse Spark, reviewed.
- 結局天燈拍：玩家替老顏寫燈（12 字內，可中英、可空白）→ 5 秒升空 → 佩珊傳照片到群組 → 一位在群同學回一句。全部本機運行，不接 AI、不放金鑰；髒話打碼成▇。規格：`docs/spec/01-game-spec.md` §10。

## 檔案狀態
見 [docs/FILES.md](docs/FILES.md)：哪些是當前文件、參考、歷史。
