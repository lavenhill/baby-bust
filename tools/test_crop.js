// R4-4 unit test: poster crop math (object-fit:cover of the 960x640 poster into a half-screen).
// Runs the real cropBoxes()/headCover() from index.html. usage: node tools/test_crop.js
const fs=require('fs'),path=require('path');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const grab=name=>{const m=html.match(new RegExp('function '+name+'\\([^)]*\\)\\{.*\\}(?=\\n)'));if(!m)throw new Error('missing '+name);return m[0]};
const cropBoxes=new Function(grab('cropBoxes')+';return cropBoxes')(),headCover=new Function(grab('headCover')+';return headCover')();
const heads=JSON.parse(fs.readFileSync(path.join(__dirname,'heads.json'),'utf8'));
let fail=0;const near=(a,b,msg)=>{if(Math.abs(a-b)>0.05){fail++;console.log('FAIL',msg,a,'!=',b)}};
// Worked by hand (see comments). Head box y2022c_D = [0.4471,0.2434,0.1172,0.2325].
const C=[
 // 390x780 phone: half = 390 x (780/2-26=364). s=max(390/960,364/640)=0.56875 -> poster 546x364, cut 78px each side.
 // x=-78+0.4471*546=166.12  y=0.2434*364=88.60  w=0.1172*546=63.99  h=0.2325*364=84.63
 {W:390,H:364,k:'y2022c_D',i:0,want:[166.12,88.60,63.99,84.63]},
 // 375x548 phone: half = 375 x 248. s=max(0.390625,0.3875)=0.390625 -> poster 375x250, cut 1px top and bottom.
 // x=0.4471*375=167.66  y=-1+0.2434*250=59.85  w=0.1172*375=43.95  h=0.2325*250=58.13
 {W:375,H:248,k:'y2022c_D',i:0,want:[167.66,59.85,43.95,58.13]},
 // 1280x800 desktop stage 496 wide: half = 496 x 374. s=max(0.51667,0.584375)=0.584375 -> poster 561x374, cut 32.5px each side.
 // y2018_D[0] = [0.5521,0.2948,0.0938,0.1792]: x=-32.5+0.5521*561=277.23  y=0.2948*374=110.26  w=0.0938*561=52.62  h=0.1792*374=67.02
 {W:496,H:374,k:'y2018_D',i:0,want:[277.23,110.26,52.62,67.02]},
];
for(const c of C){const got=cropBoxes([heads[c.k][c.i]],c.W,c.H)[0];['x','y','w','h'].forEach((n,j)=>near(got[j],c.want[j],c.k+' '+c.W+'x'+c.H+' '+n))}
// cover: a text box exactly over the head = 1; half of it = 0.5; elsewhere = 0; capped at 1 per head
const R=[[10,10,20,20]];near(headCover(R,[[10,10,20,20]]),1,'cover full');near(headCover(R,[[10,10,10,20]]),.5,'cover half');
near(headCover(R,[[100,100,5,5]]),0,'cover none');near(headCover(R,[[0,0,50,50],[0,0,50,50]]),1,'cover cap');
console.log(fail?fail+' failed':'crop tests ok ('+(C.length*4+4)+' checks)');process.exit(fail?1:0);
