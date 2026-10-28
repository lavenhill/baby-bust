// 《我們這一班》出處頁「還想查什麼？」即時查詢中繼（Cloudflare Worker 草稿，尚未部署）。
// 由 tools/sources_muse.py worker 從出處庫產生 tools/ask_worker.js；改出處庫後重跑，提示與句子編號才會同步。
// 金鑰不在這裡：部署時用 `wrangler secret put META_KEY` 放進 Worker secret。repo 不放任何金鑰。
// 需要一個 KV namespace 綁定成 ASK_KV（計次與花費）。設定見 docs/ask-worker.md。
// 遊戲端：index.html 的 ASK_URL 設成這個 Worker 的網址就切成即時；空字串＝只用錄好的答案（預設）。
const SYS=__SYS__;
const IDS=new Set(__IDS__);
const ALLOW=["https://raw.githack.com","https://lavenhill.github.io"];   // 只接受遊戲頁的來源
const PER_IP_DAY=10;        // 每 IP 每日 10 次
const BUDGET_USD=5;         // 總花費上限（美元）；到了就熔斷，回 offline
const PRICE_IN=1.25e-6, PRICE_OUT=4.25e-6;   // muse-spark-1.3 每 token 美元
export default{async fetch(req,env){
  const origin=req.headers.get("origin")||"";
  const cors={"access-control-allow-origin":ALLOW.includes(origin)?origin:ALLOW[0],"access-control-allow-headers":"content-type","vary":"origin"};
  const out=(o,s=200)=>Response.json(o,{status:s,headers:cors});
  if(req.method==="OPTIONS")return new Response(null,{headers:cors});
  if(req.method!=="POST"||!ALLOW.includes(origin))return out({type:"offline",picks:[]},403);
  const {q}=await req.json().catch(()=>({}));
  if(typeof q!=="string"||!q.trim()||q.length>40)return out({type:"none",picks:[]});
  // 花費熔斷與每 IP 次數（只存次數與金額，不存玩家原文）
  const day=new Date().toISOString().slice(0,10),ip=req.headers.get("cf-connecting-ip")||"?";
  const spent=parseFloat(await env.ASK_KV.get("usd_total")||"0");
  if(spent>=BUDGET_USD)return out({type:"offline",picks:[],why:"budget"});
  const k="n:"+day+":"+ip,n=parseInt(await env.ASK_KV.get(k)||"0");
  if(n>=PER_IP_DAY)return out({type:"offline",picks:[],why:"limit"});
  try{await env.ASK_KV.put(k,String(n+1),{expirationTtl:172800})}catch(e){return out({type:"offline",picks:[],why:"kv"})}   // 計數寫不進去就不呼叫 Muse（寧可關、不超支）；KV 免費版每日 1,000 次寫入
  const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),8000);
  let j={type:"none",picks:[]},usd=0;
  try{
    const r=await fetch("https://api.meta.ai/v1/chat/completions",{method:"POST",signal:ctl.signal,headers:{authorization:"Bearer "+env.META_KEY,"content-type":"application/json"},
      body:JSON.stringify({model:"muse-spark-1.3",reasoning_effort:"minimal",max_tokens:3000,messages:[{role:"system",content:SYS},{role:"user",content:"玩家問：「"+q+"」"}]})});
    const x=await r.json();const u=x.usage||{};usd=(u.prompt_tokens||0)*PRICE_IN+(u.completion_tokens||0)*PRICE_OUT;
    j=JSON.parse(x.choices[0].message.content.replace(/^```(json)?|```$/g,"").trim());
  }catch(e){j={type:"offline",picks:[]}}finally{clearTimeout(to)}
  if(usd)await env.ASK_KV.put("usd_total",String(spent+usd)).catch(()=>{});   // 近似累計：併發或超過 KV 寫入額度時會少記，上限要留餘裕（見成本筆記）
  const picks=(Array.isArray(j.picks)?j.picks:[]).filter(p=>IDS.has(p)).slice(0,3);   // 只放行出處庫裡存在的句子編號
  return out({type:["fact","fiction","none","abuse","offline"].includes(j.type)?j.type:"none",picks});
}};
