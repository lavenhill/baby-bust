# Changelog / 版本紀錄

Moved here from README.md on 2026-10-29 (original text kept as written). Newer, detailed notes: [docs/devlog/](devlog/).
以下段落於 2026-10-29 從 README 原文搬來，未改寫。更細的開發紀錄見 docs/devlog/。

## Status (from README)
- 2026-10-27: repo created; minimal playable build; scrolling-desk layout; Meta AI copy, translations, reunion lines and illustrations wired in.
- 2026-10-28 (V=20261028h): 2025 lower half is Jessica again (public preschool teachers working through summer break, sourced); title changed to 我們與孩子的距離 / Between Us and the Kids; English version uses English names (Vivian, Amy, Kevin, Jessica, Jason, Penny) and plain-English childcare terms.

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

## Ending lantern (d29, 2026-10-29; replaced the L1 free-text lantern)
- Ending: at the 2026 Pingxi reunion the player picks what Vivian writes on her own sky lantern from 2–3 options built from this run: her own life (the last life frame she saw), one friend (the one hurt most: "{Name}, come back" if they left the group, "Sorry, {Name}" if hurt once), and "All back in 8 years". A fixed 5-second release follows, Penny posts a photo to the group chat, and one classmate still in the group answers.
- Runs entirely in the page from pre-written lines (`tools/content_zh.py` `LANTERN_OPT`, `data.js` `lantern.opt`). No AI call, no key, no server, no text input.
- Lines: drafted with Muse Spark 1.3 and reviewed by Hark.
- 結局天燈拍：老顏的燈改成 2–3 顆限定選項（她自己／一位朋友／八年後），按鈕字＝燈上字 → 5 秒升空 → 佩珊傳照片到群組 → 一位在群同學回一句。全部本機運行，不接 AI、不放金鑰、沒有輸入框。規格：`docs/spec/01-game-spec.md` §10。

## Later versions / 之後的版本
- 2026-10-29 (V=20261029f): sources page rewritten with Wikipedia-style citations; local archive pages `sources/R01–R91.html`. See `docs/devlog/2026-10-29-1730.md`.
- 2026-10-29: `relay/` live-ask relay added (not switched on; `ASK_URL` empty).
