"""Sheet ⇄ source sync for the copy table (Google Sheet 1vKymUCHAhbbU3UZBi-HCGx_UHgkYAUddU9zp3iIyh1Q, shingocho).
Rule (user 2026-10-28 22:4x): the user edits the CHINESE column on the sheet by hand; write-back changes Chinese only,
English is never re-translated or touched (unless the user asks). The sheet must never be overwritten over the user's edits.

usage (run from /workspace/work/bb2, Google credentials for shingocho@gmail.com injected by the shell tool):
  python3 tools/sheet_sync.py pull    # regenerate the local table from data.js, read the online sheet, diff 中文 by 資料路徑
                                      #   -> qa/sheet_zh_diff.json ; exit 2 when the sheet has Chinese edits not yet in the source
  python3 tools/sheet_sync.py apply   # write those Chinese edits back into the sources, rebuild data.js, verify:
                                      #   every edited row now shows the new Chinese, and NO English cell changed anywhere (else revert)
  python3 tools/sheet_sync.py push [新標題] [--ok-en]  # pull first; refuses (exit 3) while unapplied Chinese edits, rows only on the sheet,
                                      #   or English cells that differ (unless --ok-en) exist; then uploads and reads back both columns
copy_map.py only builds the local .xlsx; uploading goes through `push` so the guard always runs.
"""
import json,os,re,subprocess,sys,shutil,time
import openpyxl
SID='1vKymUCHAhbbU3UZBi-HCGx_UHgkYAUddU9zp3iIyh1Q'
B=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
META='/workspace/work/meta/v2'   # build_data.py reads en.json / reunion_v3.json from here
XLSX=os.path.join(B,'qa','我們與孩子的距離_文案台詞對照.xlsx');DIFF=os.path.join(B,'qa','sheet_zh_diff.json')
ZH_SRC=[os.path.join(B,'tools','content_zh.py'),os.path.join(B,'tools','sources_zh.py'),os.path.join(META,'reunion_v3.json')]
EN_KEYED=[os.path.join(META,'en.json')]   # dict 中文 -> English: a Chinese edit renames the key, the English value stays
IDX=os.path.join(B,'index.html')

def local_rows():
    subprocess.check_call([sys.executable,os.path.join(B,'tools','copy_map.py')],cwd=B,stdout=subprocess.DEVNULL)
    ws=openpyxl.load_workbook(XLSX)['全部文案']
    return {r[9]:{'zh':r[5] or '','en':r[6] or '','sec':r[1],'status':r[8]} for r in ws.iter_rows(min_row=2,values_only=True)}
def online_rows():
    out=subprocess.check_output(['gws','sheets','spreadsheets','values','get','--params',json.dumps({'spreadsheetId':SID,'range':'全部文案'})],cwd=B)
    v=json.loads(out)['values'];h=v[0];ci,ce,cp=h.index('中文'),h.index('English'),h.index('資料路徑');o={}
    for r in v[1:]:
        r=r+['']*(len(h)-len(r))
        if r[cp]: o[r[cp]]={'zh':r[ci],'en':r[ce]}
    return o
def _data(path):
    return json.loads(subprocess.check_output(['node','-e',"eval(require('fs').readFileSync(process.argv[1],'utf8').replace(/^const DATA/m,'global.DATA'));process.stdout.write(JSON.stringify(DATA))",path]))
def pull():
    L=local_rows();O=online_rows();n=lambda s:(s or '').replace('\r','').strip()
    diffs=[{'path':p,'old':L[p]['zh'],'new':O[p]['zh'],'sec':L[p]['sec']} for p in L if p in O and n(O[p]['zh'])!=n(L[p]['zh'])]
    en_edits=[p for p in L if p in O and n(O[p]['en'])!=n(L[p]['en'])]
    rep={'when':time.strftime('%Y-%m-%d %H:%M'),'zh_diffs':diffs,'en_cells_differ_ignored':en_edits,'rows_only_local':[p for p in L if p not in O],'rows_only_online':[p for p in O if p not in L]}
    json.dump(rep,open(DIFF,'w'),ensure_ascii=False,indent=1)
    print(f"中文差異 {len(diffs)}；英文欄不同 {len(en_edits)}（依規則不回寫）；只在本機 {len(rep['rows_only_local'])}；只在表上 {len(rep['rows_only_online'])} -> {DIFF}")
    return rep
def _replace_json(obj,old,new,cnt):
    if isinstance(obj,str): 
        if obj==old: cnt[0]+=1;return new
        return obj
    if isinstance(obj,list): return [_replace_json(x,old,new,cnt) for x in obj]
    if isinstance(obj,dict): return {k:_replace_json(v,old,new,cnt) for k,v in obj.items()}
    return obj
def apply():
    rep=pull();diffs=rep['zh_diffs']
    if not diffs: print('nothing to apply');return 0
    L0=local_rows();bak=os.path.join(B,'qa','sheet_sync_bak',time.strftime('%m%d%H%M%S'));os.makedirs(bak)
    files=ZH_SRC+EN_KEYED+[IDX,os.path.join(B,'data.js')]
    for f in files: shutil.copy(f,os.path.join(bak,os.path.basename(f)))
    by_old={}
    for d in diffs: by_old.setdefault(d['old'],set()).add(d['new'])
    same_old_rows={o:[p for p,r in L0.items() if r['zh']==o] for o in by_old}
    done,unres=[],[]
    for d in diffs:
        old,new=d['old'],d['new']
        if len(by_old[old])>1 or len(same_old_rows[old])>len([x for x in diffs if x['old']==old]):
            unres.append(d|{'why':'同一句中文出現在多列，但表上只改了部分或改法不同：請人工決定'});continue
        if d['path'].startswith('index.html:'):
            en=d['path'].split(':',1)[1];pat="L?'"+en+"':'"+old+"'";t=open(IDX).read();k=t.count(pat)
            if k>=1 and "'" not in new: open(IDX,'w').write(t.replace(pat,"L?'"+en+"':'"+new+"'"));done.append(d)
            else: unres.append(d|{'why':f'index.html 找到 {k} 處'})
            continue
        hit=0;conflict=None
        for f in ZH_SRC:   # plan first: a sentence is written back everywhere or nowhere
            if f.endswith('.py'):
                t=open(f).read()
                for q in ("'",'"'):
                    if t.count(q+old+q) and q in new: conflict=f'{os.path.basename(f)} 用 {q} 包住這句，新句含同一個引號'
        o_en=[json.load(open(f)) for f in EN_KEYED]
        for o in o_en:
            if old in o and new in o and o[new]!=o[old]: conflict='en.json 已有新句的另一個英文：英文對應衝突'
        if conflict: unres.append(d|{'why':conflict+'：請人工回寫'});continue
        for f in ZH_SRC:
            if f.endswith('.json'):
                o=json.load(open(f));c=[0];o=_replace_json(o,old,new,c)
                if c[0]: json.dump(o,open(f,'w'),ensure_ascii=False,indent=1);hit+=c[0]
            else:
                t=open(f).read()   # only whole quoted strings, never a substring of a longer line
                for q in ("'",'"'):
                    c=t.count(q+old+q)
                    if c and q not in new: t=t.replace(q+old+q,q+new+q);hit+=c
                open(f,'w').write(t)
        for f in EN_KEYED:
            o=json.load(open(f))
            if old in o and (new not in o or o[new]==o[old]):
                o={(new if k==old else k):v for k,v in o.items()};json.dump(o,open(f,'w'),ensure_ascii=False,indent=1)
        (done if hit else unres).append(d if hit else d|{'why':'原始檔找不到這句（可能是程式組字）：請人工回寫'})
    subprocess.check_call([sys.executable,os.path.join(B,'tools','build_data.py')],cwd=META,stdout=subprocess.DEVNULL)
    L1=local_rows();bad=[]
    for p in L0:
        if p in L1 and L1[p]['en']!=L0[p]['en']: bad.append(('英文被動到',p,L0[p]['en'],L1[p]['en']))
    # every string that changed anywhere in data.js must be exactly one of the applied old -> new pairs
    pairs={(d['old'],d['new']) for d in done};D0=_data(os.path.join(bak,'data.js'));D1=_data(os.path.join(B,'data.js'))
    def walk(a,b,p):
        if isinstance(a,dict) and isinstance(b,dict):
            for k in set(a)|set(b): walk(a.get(k),b.get(k),p+'.'+str(k))
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for i,(x,y) in enumerate(zip(a,b)): walk(x,y,f'{p}[{i}]')
        elif a!=b and (a,b) not in pairs: bad.append(('data.js 出現非預期變動',p,str(a)[:60],str(b)[:60]))
    walk(D0,D1,'')
    touched={d['path'] for d in done}
    for p in L0:
        if p in L1 and p not in touched and L1[p]['zh']!=L0[p]['zh']: bad.append(('別列中文被連帶改到',p,L0[p]['zh'],L1[p]['zh']))
    for d in done:
        if L1.get(d['path'],{}).get('zh')!=d['new']: bad.append(('中文沒變成表上版本',d['path'],d['new'],L1.get(d['path'],{}).get('zh')))
    if bad:
        for f in files: shutil.copy(os.path.join(bak,os.path.basename(f)),f)
        subprocess.check_call([sys.executable,os.path.join(B,'tools','copy_map.py')],cwd=B,stdout=subprocess.DEVNULL)
        print('驗證失敗，已全部還原：');[print(' ',b) for b in bad[:20]];return 1
    json.dump({'applied':done,'unresolved':unres,'backup':bak},open(DIFF.replace('.json','_applied.json'),'w'),ensure_ascii=False,indent=1)
    poster=[d for d in done if '海報' in d['path'] or '.h1' in d['path']]
    print(f'已回寫 {len(done)} 句中文（英文 0 變動）；待人工 {len(unres)} 句；備份 {bak}'+('；海報字有改，記得重做 poster.woff2 子集' if poster else ''))
    return 0 if not unres else 2
def push():
    rep=pull()
    if rep['zh_diffs']: print('表上有使用者的中文修改尚未回寫源碼：先跑 apply，不覆蓋');return 3
    if rep['rows_only_online']: print('表上有本機沒有的列（使用者新增？）：不覆蓋，請先人工處理',rep['rows_only_online'][:10]);return 3
    if rep['en_cells_differ_ignored'] and '--ok-en' not in sys.argv: print('表上英文欄與本機不同（規則：英文不回寫）。覆蓋會蓋掉表上的英文，確認可蓋再加 --ok-en',rep['en_cells_differ_ignored'][:10]);return 3
    args=[a for a in sys.argv[2:] if not a.startswith('--')];title=args[0] if args else None
    body={'name':title} if title else {}
    subprocess.check_call(['gws','drive','files','update','--params',json.dumps({'fileId':SID}),'--json',json.dumps(body),'--upload',XLSX,
        '--upload-content-type','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],cwd=B)
    after=online_rows();L=local_rows();miss=[p for p in L if p not in after or after[p]['zh'].strip()!=L[p]['zh'].strip() or after[p]['en'].strip()!=L[p]['en'].strip()]
    print('上傳完成；回讀比對中英文不同',len(miss),miss[:10]);return 0 if not miss else 4
if __name__=='__main__':
    sys.exit({'pull':lambda:2 if pull()['zh_diffs'] else 0,'apply':apply,'push':push}[sys.argv[1]]())
