// L1: unit test for the lantern beat's mask + reply rules (node tools/test_lantern.js). Extracts the functions from index.html.
const fs=require('fs');const B=__dirname+'/../';
eval(fs.readFileSync(B+'data.js','utf8').replace(/^const DATA/m,'global.DATA'));
const html=fs.readFileSync(B+'index.html','utf8');
const js=html.slice(html.indexOf('const CJK='),html.indexOf('function lanternInput'))+html.slice(html.indexOf('function lreply'),html.indexOf('async function lanternBeat'));
global.L=0;global.S={gone:[]};global.tx=a=>Array.isArray(a)?(a[L]||a[0]):(a||'');eval(js+';global.lmask=lmask;global.lreply=lreply;global.lclip=lclip;global.lw=lw');
let bad=0;const ok=(c,m)=>{if(!c){bad++;console.log('FAIL',m)}};
const run=(w,gone,lang)=>{S.gone=gone||[];L=lang||0;const m=lmask(w.trim());return [m,...lreply(w,m)]};
const T=[ // [input, gone, expectWho, mustContain]
 ['幹',[],'家豪'],['幹你的海報',[],'家豪'],['幹',['家豪'],'佩珊'],['',[],'家豪'],['   ',['家豪','宜君'],'佩珊'],['fuck this job',[],'家豪'],['FUCK',['家豪'],'佩珊'],
 ['幹嘛又加班',[],'家豪','幹嘛'],['他很能幹',[],'佩珊'],
 ['想睡一整晚',[],'家豪'],['想睡一整晚',['家豪'],'佩珊'],['sleep all night',[],'家豪'],
 ['5/24',[],'佩珊'],['回診下週一定去',[],'宜君'],['回診下週一定去',['宜君'],'佩珊'],
 ['對不起',[],'志豪'],['對不起',['志豪'],'家豪'],['對不起',['志豪','家豪'],'佩珊'],
 ['家豪，招牌撐住',[],'家豪'],['家豪，招牌撐住',['家豪'],'佩珊'],['宜君回來群組好嗎',['宜君'],'佩珊'],['宜君回來群組好嗎',[],'宜君'],
 ['志豪快求婚',[],'志豪'],['佩珊請假別道歉',[],'佩珊'],['阿芳升主任',[],'阿芳'],['Yijun come back',[],'宜君'],['jiahao!',[],'家豪'],
 ['辭職',[],'家豪'],['辭職',['家豪'],'佩珊'],['I quit',[],'家豪'],['I miss you',[],'佩珊'],['今天天氣好',[],'佩珊'],['<b>x</b>',[],'佩珊'],
];
for(const [w,g,who,keep] of T){const [m,x,t]=run(w,g);ok(x===who,`${JSON.stringify(w)} gone=${g} → ${x} want ${who}`);ok(!g.includes(x)&&x!=='老顏',`${w} responder gone`);
  if(/幹(?!嘛)|fuck/i.test(w)&&!/能幹/.test(w)){ok(m.includes('▇')&&!/幹|fuck/i.test(m),`${w} not masked: ${m}`);ok(!t.includes('▇')&&!/幹|fuck/i.test(t),`${w} quoted in reply`)}
  if(keep)ok(m.includes(keep),`${w} over-masked: ${m}`);ok(!/<b>/.test(t),'html not escaped');ok(t&&!t.includes('{w}'),`${w} empty/unfilled reply`)}
ok(lclip('一二三四五六七八九十一二三')==='一二三四五六七八九十一二','clip zh');ok(lclip('abcdefghijklmnopqrstuvwxyz').length===24,'clip en');ok(lw('ab中')===2,'width');
L=1;S.gone=[];const [,te]=lreply('sleep all night','sleep all night');ok(te.includes('&quot;sleep all night&quot;'),'en quote: '+te);
console.log(bad?`${bad} failed`:`all ${T.length} lantern cases ok`);process.exit(bad?1:0);
