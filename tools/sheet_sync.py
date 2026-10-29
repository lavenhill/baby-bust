"""Sheet ⇄ source sync for the copy table (Google Sheet 1vKymUCHAhbbU3UZBi-HCGx_UHgkYAUddU9zp3iIyh1Q, shingocho;
the user may also edit a copy: pass --sheet=<id>, e.g. 1agTpMfP… "2026-10-29 修訂版").
Rule (user 2026-10-28 22:4x, revised 2026-10-29 10:39): the user edits the sheet by hand. We never re-translate English ourselves,
but whatever the user typed — Chinese AND English — is written back as is. The sheet must never be overwritten over the user's edits.

usage (run from /workspace/work/bb2, Google credentials for shingocho@gmail.com injected by the shell tool):
  python3 tools/sheet_sync.py pull    # regenerate the local table from data.js, read the online sheet, diff 中文 by 資料路徑
                                      #   -> qa/sheet_zh_diff.json ; exit 2 when the sheet has Chinese edits not yet in the source
  python3 tools/sheet_sync.py apply   # write the sheet's Chinese and English edits back into the sources, rebuild data.js, verify:
                                      #   each edited row shows exactly the sheet's text, no other row's 中文/English moved, and data.js changed
                                      #   only by the applied old->new pairs; otherwise EVERYTHING is restored from the backup.
                                      #   Rows it cannot place safely (same sentence in several rows edited differently, English built by code,
                                      #   {placeholder} changed) are listed in qa/sheet_zh_diff_applied.json "unresolved" for manual handling.
                                      #   reunion rows are written by path; a .h1s row's Chinese is the poster title (.h1) itself.
  python3 tools/sheet_sync.py push [新標題] [--ok-en] [--behind=qa/sheet-r1/diff.json]  # --behind: rows equal to that file's old text = sheet is behind, not edited  # pull first; refuses (exit 3) while unapplied 中文 or English edits or rows only
                                      #   on the sheet exist (--ok-en = deliberately overwrite the sheet's English); then uploads, reads back
copy_map.py only builds the local .xlsx; uploading goes through `push` so the guard always runs.
"""
import json,os,re,subprocess,sys,shutil,time
import openpyxl
SID='1vKymUCHAhbbU3UZBi-HCGx_UHgkYAUddU9zp3iIyh1Q'
for _a in sys.argv:
    if _a.startswith('--sheet='): SID=_a.split('=',1)[1]   # the user may edit a copy of the table (e.g. 1agTpMfP… 2026-10-29)
B=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
META='/workspace/work/meta/v2'   # build_data.py reads en.json / reunion_v3.json from here
XLSX=os.path.join(B,'qa','我們與孩子的距離_文案台詞對照.xlsx');DIFF=os.path.join(B,'qa','sheet_zh_diff.json')
ZH_SRC=[os.path.join(B,'tools','content_zh.py'),os.path.join(B,'tools','sources_zh.py'),os.path.join(META,'reunion_v3.json')]
EN_KEYED=[os.path.join(META,'en.json')]   # dict 中文 -> English: a Chinese edit renames the key, the English value stays
IDX=os.path.join(B,'index.html')
BUILD=os.path.join(B,'tools','build_data.py')   # holds EN3 (中文 -> English for open2/wish/life/ring) and SELF/VERDICT
ZH_SRC.append(BUILD)   # a Chinese edit must also rename its EN3 key, or the English falls back to Chinese
EN_SRC=[os.path.join(META,'en.json'),os.path.join(B,'tools','sources_en.json'),BUILD,os.path.join(B,'tools','content_zh.py'),IDX]   # where English literals live

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
    en=[{'path':p,'old':L[p]['en'],'new':O[p]['en'],'sec':L[p]['sec']} for p in L if p in O and n(O[p]['en'])!=n(L[p]['en'])]
    rep={'when':time.strftime('%Y-%m-%d %H:%M'),'sheet':SID,'zh_diffs':diffs,'en_diffs':en,'rows_only_local':[p for p in L if p not in O],'rows_only_online':[p for p in O if p not in L]}
    json.dump(rep,open(DIFF,'w'),ensure_ascii=False,indent=1)
    print(f"[{SID[:8]}] 中文差異 {len(diffs)}；英文差異 {len(en)}；只在本機 {len(rep['rows_only_local'])}；只在表上 {len(rep['rows_only_online'])} -> {DIFF}")
    return rep
def _replace_json(obj,old,new,cnt):
    if isinstance(obj,str): 
        if obj==old: cnt[0]+=1;return new
        return obj
    if isinstance(obj,list): return [_replace_json(x,old,new,cnt) for x in obj]
    if isinstance(obj,dict): return {k:_replace_json(v,old,new,cnt) for k,v in obj.items()}
    return obj
_esc=lambda s,q:s.replace('\\','\\\\').replace(q,'\\'+q)
def _replace_lit(t,old,new,pipe=False):
    """replace whole quoted string literals 'old' / "old" (py / js) -> same quote, new escaped; returns (text,count)"""
    c=0
    for q in ("'",'"'):
        pat=q+_esc(old,q)+q;k=t.count(pat)
        if k: t=t.replace(pat,q+_esc(new,q)+q);c+=k
    if pipe and '|' not in new and '\n' not in new:   # content_zh.py GROUP/GCONS blocks: one line per message, fields split by |
        pat='|'+old+'|';k=t.count(pat)
        if k: t=t.replace(pat,'|'+new+'|');c+=k
    return t,c
_REU=re.compile(r'reunion\.(.+?)\.(line|off|qa\[(\d)\])$')
def _reu_set(path,old,new,lang):
    """reunion rows are addressed by path (same sentence may sit in several endings): set exactly that cell in reunion_v3.json"""
    m=_REU.match(path);f=os.path.join(META,'reunion_v3.json');o=json.load(open(f));v=o['reunion'].get(m.group(1)) if m else None
    if v is None: return False
    if m.group(2)=='line': c,k=v,('line' if lang=='zh' else 'line_en')
    elif m.group(2)=='off': c,k=v,('offtopic' if lang=='zh' else 'offtopic_en')
    else: c,k=v['qa'][int(m.group(3))],('a' if lang=='zh' else 'a_en')
    cur=c.get(k,'');fx=cur.replace('Old Yan','Vivian').replace('Lao Yan','Vivian')
    if cur!=old and fx!=old: return False
    c[k]=new;json.dump(o,open(f,'w'),ensure_ascii=False,indent=1);return True
def apply():
    """write the sheet's edits (中文 and, since 2026-10-29, English the user typed) back into the sources, rebuild, verify, else revert all"""
    rep=pull();diffs=rep['zh_diffs'];ens=rep['en_diffs']
    if not diffs and not ens: print('nothing to apply');return 0
    L0=local_rows();bak=os.path.join(B,'qa','sheet_sync_bak',time.strftime('%m%d%H%M%S'));os.makedirs(bak)
    files=sorted(set(ZH_SRC+EN_SRC+EN_KEYED+[IDX,os.path.join(B,'data.js')]))
    for f in files: shutil.copy(f,os.path.join(bak,os.path.basename(f)))
    # h1s rows show the poster's Chinese title (a mirror of the .h1 row): an edit there is an edit of the title itself
    for d in list(diffs):
        if d['path'].endswith('.h1s'):
            h=d['path'][:-1]
            if h in L0 and L0[h]['zh']==d['old'] and not any(x['path']==h for x in diffs): diffs.append({'path':h,'old':d['old'],'new':d['new'],'sec':d['sec'],'alias_of':d['path']})
    by_old={}
    for d in diffs:
        if not _REU.match(d['path']): by_old.setdefault(d['old'],set()).add(d['new'])
    same_old_rows={o:[p for p,r in L0.items() if r['zh']==o and not _REU.match(p)] for o in by_old}
    done,unres=[],[]
    for d in diffs:
        old,new=d['old'],d['new']
        if _REU.match(d['path']):
            if _reu_set(d['path'],old,new,'zh'): done.append(d)
            else: unres.append(d|{'why':'reunion 路徑對不上原始檔'})
            continue
        if len(by_old[old])>1 or len(same_old_rows[old])>len([x for x in diffs if x['old']==old]):
            unres.append(d|{'why':'同一句中文出現在多列，但表上只改了部分或改法不同：請人工決定'});continue
        if d['path'].startswith('index.html:'):
            en=d['path'].split(':',1)[1];pat="L?'"+en+"':'"+old+"'";t=open(IDX).read();k=t.count(pat)
            if k>=1 and "'" not in new: open(IDX,'w').write(t.replace(pat,"L?'"+en+"':'"+new+"'"));done.append(d)
            else: unres.append(d|{'why':f'index.html 找到 {k} 處'})
            continue
        if any(x['old']==old and x['new']==new for x in done): done.append(d);continue   # same sentence, already written back by an earlier row
        conflict=None
        for o in [json.load(open(f)) for f in EN_KEYED]:
            if old in o and new in o and o[new]!=o[old]: conflict='en.json 已有新句的另一個英文：英文對應衝突'
        if conflict: unres.append(d|{'why':conflict+'：請人工回寫'});continue
        hit=0
        for f in ZH_SRC:
            if f.endswith('.json'):
                o=json.load(open(f));c=[0];o=_replace_json(o,old,new,c)
                if c[0]: json.dump(o,open(f,'w'),ensure_ascii=False,indent=1);hit+=c[0]
            else:
                t,c=_replace_lit(open(f).read(),old,new,pipe=f.endswith('content_zh.py'))   # whole quoted strings / whole | fields only (incl. EN3 keys in build_data.py)
                if c: open(f,'w').write(t);hit+=c
        for f in EN_KEYED if hit else []:
            o=json.load(open(f))
            if old in o and (new not in o or o[new]==o[old]):
                o={(new if k==old else k):v for k,v in o.items()};json.dump(o,open(f,'w'),ensure_ascii=False,indent=1)
        (done if hit else unres).append(d if hit else d|{'why':'原始檔找不到這句（可能是程式組字）：請人工回寫'})
    # English the user typed (rule 15 revised 2026-10-29: we never re-translate, but the user's own English edits are written back)
    en_done=[]
    en_by_old={}
    for d in ens:
        if not _REU.match(d['path']): en_by_old.setdefault(d['old'],set()).add(d['new'])
    for d in ens:
        old,new=d['old'],d['new']
        if '{' in old or '{' in new:
            if old.count('{')!=new.count('{') or set(re.findall(r'\{\w+\}',old))!=set(re.findall(r'\{\w+\}',new)): unres.append(d|{'lang':'en','why':'占位符 {…} 被改動'});continue
        if _REU.match(d['path']):
            if _reu_set(d['path'],old,new,'en'): en_done.append(d)
            else: unres.append(d|{'lang':'en','why':'reunion 英文對不上原始檔'})
            continue
        rows=[p for p,r in L0.items() if r['en']==old and not _REU.match(p)]
        if len(en_by_old[old])>1 or len(rows)>len([x for x in ens if x['old']==old]):
            unres.append(d|{'lang':'en','why':'同一句英文出現在多列，但表上只改了部分或改法不同：請人工決定'});continue
        hit=0
        for f in EN_SRC:
            if f.endswith('.json'):
                o=json.load(open(f));c=[0];o=_replace_json(o,old,new,c)
                if c[0]: json.dump(o,open(f,'w'),ensure_ascii=False,indent=1);hit+=c[0]
            else:
                t,c=_replace_lit(open(f).read(),old,new)
                if c: open(f,'w').write(t);hit+=c
        (en_done if hit else unres).append(d if hit else d|{'lang':'en','why':'原始檔找不到這句英文（程式拼字）：請人工回寫'})
    subprocess.check_call([sys.executable,os.path.join(B,'tools','build_data.py')],cwd=META,stdout=subprocess.DEVNULL)
    L1=local_rows();bad=[]
    en_touch={d['path']:d['new'] for d in en_done}
    for p in L0:
        if p not in L1: bad.append(('列消失',p,'',''));continue
        want=en_touch.get(p,L0[p]['en'])
        if p not in en_touch and L1[p]['en']!=L0[p]['en']:
            # a row sharing the same English sentence as an edited row moves with it (allowed only if that row is in the sheet's edits too)
            bad.append(('英文被動到',p,L0[p]['en'],L1[p]['en']))
        elif p in en_touch and L1[p]['en'].strip()!=want.strip(): bad.append(('英文沒變成表上版本',p,want,L1[p]['en']))
    pairs={(d['old'],d['new']) for d in done+en_done};D0=_data(os.path.join(bak,'data.js'));D1=_data(os.path.join(B,'data.js'))
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
        json.dump({'bad':bad,'done':done,'en_done':en_done,'unresolved':unres},open(DIFF.replace('.json','_failed.json'),'w'),ensure_ascii=False,indent=1)
        print('驗證失敗，已全部還原：');[print(' ',b) for b in bad[:30]];return 1
    json.dump({'applied':done,'applied_en':en_done,'unresolved':unres,'backup':bak},open(DIFF.replace('.json','_applied.json'),'w'),ensure_ascii=False,indent=1)
    poster=[d for d in done if '.h1' in d['path']]
    print(f'已回寫中文 {len(done)} 句、英文 {len(en_done)} 句；待人工 {len(unres)} 句；備份 {bak}'+('；海報字有改，記得重做 poster.woff2 子集' if poster else ''))
    return 0 if not unres else 2
def _behind(rep):
    """drop diffs where the sheet simply shows the PREVIOUS source text (sheet is behind, not edited):
    --behind=<diff.json from an earlier apply> lists old values per path; a .h1 row whose .h1s mirror on the sheet already shows the new title is behind too"""
    base={}
    for a in sys.argv:
        if a.startswith('--behind='):
            for r in json.load(open(a.split('=',1)[1])): base[r['path']]=(r.get('zh_old'),r.get('en_old'))
    O=None;n=lambda s:(s or '').replace('\r','').strip()
    for k,i in (('zh_diffs',0),('en_diffs',1)):
        keep=[]
        for d in rep[k]:
            if d['path'] in base and n(base[d['path']][i])==n(d['new']): continue
            if k=='zh_diffs' and d['path'].endswith('.h1'):
                O=O or online_rows();m=O.get(d['path']+'s')
                if m and n(m['zh'])==n(d['old']): continue
            keep.append(d)
        rep[k]=keep
    return rep
def push():
    rep=_behind(pull())
    if rep['zh_diffs']: print('表上有使用者的中文修改尚未回寫源碼：先跑 apply，不覆蓋',[d['path'] for d in rep['zh_diffs']][:10]);return 3
    if rep['rows_only_online']: print('表上有本機沒有的列（使用者新增？）：不覆蓋，請先人工處理',rep['rows_only_online'][:10]);return 3
    if rep['en_diffs'] and '--ok-en' not in sys.argv: print('表上有英文修改尚未回寫源碼：先跑 apply（使用者改的英文照收）；確定要用源碼英文蓋掉表上英文才加 --ok-en',[d['path'] for d in rep['en_diffs']][:10]);return 3
    args=[a for a in sys.argv[2:] if not a.startswith('--')];title=args[0] if args else None
    body={'name':title} if title else {}
    subprocess.check_call(['gws','drive','files','update','--params',json.dumps({'fileId':SID}),'--json',json.dumps(body),'--upload',XLSX,
        '--upload-content-type','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],cwd=B)
    after=online_rows();L=local_rows();miss=[p for p in L if p not in after or after[p]['zh'].strip()!=L[p]['zh'].strip() or after[p]['en'].strip()!=L[p]['en'].strip()]
    print('上傳完成；回讀比對中英文不同',len(miss),miss[:10]);return 0 if not miss else 4
if __name__=='__main__':
    sys.exit({'pull':lambda:2 if (lambda r:r['zh_diffs'] or r['en_diffs'])(pull()) else 0,'apply':apply,'push':push}[sys.argv[1]]())
