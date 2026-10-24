"""Independent source-table audit. Run with cached original PDF layouts and sources.json.

python scripts/audit-all-rates.py ../tmp/rate-audit ../sources.json [--write]
No rate is inferred from the current product data. Column mappings are explicit.
"""
import copy
import json
import re
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = Path(sys.argv[1]).resolve()
SOURCE = Path(sys.argv[2]).resolve()
WRITE = '--write' in sys.argv
P = {p['id']: p for p in json.loads((ROOT/'data/products.json').read_text())}
ORIGINAL = copy.deepcopy(P)
EXPECTED = {}
DETAILS = {}
N = r'\d[\d,]*(?:\.\d+)?'

def text(id, alias=None):
    sid = P[id]['source']['url'].split('/d/')[1].split('/')[0]
    return (LAYOUT/((alias or sid)+'.txt')).read_text()

def numbers(s):
    return [float(v.replace(',', '')) for v in re.findall(N,s)]

def rate(id, values, plan=None, tier=False):
    p = EXPECTED.setdefault(id, {'rates': {}, 'plans': {}, 'tiers': {}})
    assert set(values) <= {'M','F'}
    for sex, cells in values.items():
        assert len(cells) == len(P[id]['bands']), (id,plan,sex,len(cells),len(P[id]['bands']))
        assert all(v is None or v>0 for v in cells),id
    if tier: p['tiers'][str(plan)] = values
    elif plan is not None: p['plans'][str(plan)] = values
    else: p['rates'] = values

def ranges(s,n):
    # A bounded age cell followed by exactly n rate cells. Several groups may share a line.
    pat = rf'(?:15\s*วัน\s*[-–]\s*|(?<![\d.])(\d{{1,2}})\s*[-–]\s*)(\d{{1,2}})\*?\s*(?:\([^)]*\)\s*)?((?:{N}\s+){{{n-1}}}{N})(?![\d,.])'
    return [(int(m[2]),numbers(m[3])) for m in re.finditer(pat,s)]

def annual_rows(s,n):
    out=[]
    for l in s.splitlines():
        l=l.replace('15 วัน','0').replace('*','')
        cells=l.split()
        if len(cells)==n+1 and all(re.fullmatch(N,c) for c in cells):
            out.append((int(cells[0]),numbers(' '.join(cells[1:]))))
    return out

def matrix_plans(id, rows, cols, sex_order=('M','F')):
    assert [a for a,_ in rows] == P[id]['bands'], (id,'age labels',len(rows))
    for j,plan in enumerate(P[id]['plans']):
        rate(id,{sex:[v[cols[k][j]] for _,v in rows] for k,sex in enumerate(sex_order)},plan['id'])

# Health Happy and Saver: one age row, four male then four female columns.
for id in ['happy','saver']:
    rows=ranges(text(id),8)
    assert len(rows)==18,(id,len(rows))
    rows=[row for row in rows if row[0] in P[id]['bands']]
    matrix_plans(id,rows,[[0,1,2,3],[4,5,6,7]])

# Hero: two adjacent age/three-plan groups per row; separate Begin/Balanced pages.
s=text('herobegin')
for id,mode in [('herobegin','Begin'),('herobalanced','Balanced')]:
    pages=[p for p in s.split('\f') if re.search(r'เบี้ยประกันภัยมาตรฐานราย.{0,8}แบบ\s+'+mode,p)]
    assert len(pages)==1,(id,len(pages))
    groups=ranges(pages[0],3)
    assert len(groups)==40,(id,len(groups))
    male=groups[::2];female=groups[1::2]
    assert [x[0] for x in male]==P[id]['bands']==[x[0] for x in female]
    for j,plan in enumerate(P[id]['plans']):rate(id,{'M':[v[j] for _,v in male],'F':[v[j] for _,v in female]},plan['id'])

# Starter: saved independently transcribed row/column fixture (all 380 printed cells).
starter=json.loads((ROOT/'tests/health-starter-source.json').read_text())['products']
for id,table in starter.items():
    assert table['bands']==P[id]['bands']
    for plan in table['plans']:rate(id,plan['rates'],plan['id'])

# Simple paired-sex tables, including multiple age groups on the same printed row.
for id in ['ciplus','cancer','tpd','hbextra']:
    rows=ranges(text(id),2)
    by={age:v for age,v in rows}
    assert set(P[id]['bands'])<=set(by),(id,sorted(by))
    rate(id,{sex:[by[a][k] for a in P[id]['bands']] for k,sex in enumerate(['M','F'])})

# Multi-Pay: printed total already includes Total Care; never add it a second time.
block=next(page for page in text('mpciplus').split('\f') if '3.96' in page and '6.31' in page)
rows=ranges(block,6)
single=re.search(r'^\s*80\*\s+((?:\d+\.\d+\s+){5}\d+\.\d+)',block,re.M)
assert single
rows.append((80,numbers(single[1])))
rows.sort()
assert len(rows)==21,('mpciplus',len(rows))
assert [a for a,_ in rows]==P['mpciplus']['bands']
rate('mpciplus',{'M':[v[2] for _,v in rows],'F':[v[5] for _,v in rows]})

# Infinite: 3 deductible blocks, 81 ages, four geography/sex columns.
s=text('infinite','infinite');headers=list(re.finditer('เบี้ยประกันภัยมาตรฐานราย',s))
assert len(headers)==3
for deductible in range(3):
    block=s[headers[deductible].start():headers[deductible+1].start() if deductible<2 else len(s)]
    rows=annual_rows(block,4)
    assert [a for a,_ in rows]==list(range(18,99)),('infinite',deductible,len(rows))
    for geography in range(2):rate('infinite',{'M':[v[geography*2] for _,v in rows],'F':[v[geography*2+1] for _,v in rows]},f'{deductible}-{geography}')

# Traditional term sheet: four paired M/F columns; explicit column per term.
rows=sorted([row for n in [2,4,6,8] for row in annual_rows(text('term5'),n) if 20<=row[0]<=59 and all(v<100 for v in row[1])])
assert [a for a,_ in rows]==list(range(20,60)),('term rows',len(rows))
for j,term in enumerate([5,10,15,20]):
    id=f'term{term}';r=[r for r in rows if r[0]<=P[id]['maxAge']]
    rate(id,{sex:[v[j*2+k] for _,v in r] for k,sex in enumerate(['M','F'])})

# Excellent: three side-by-side age/single-rate groups, shared male/female rate.
pat=rf'(?<![\d.])(\d{{1,2}}|15\s*วัน)\s+(\d+\.\d{{2}})(?!\d)'
rows={0 if m[1].startswith('15') and 'วัน' in m[1] else int(m[1]):float(m[2]) for m in re.finditer(pat,text('excellent'))}
assert set(range(76))<=set(rows)
rate('excellent',{s:[rows[a] for a in range(76)] for s in ['M','F']})

# Lifetime Income: age/whole-number annual rate; same rate for M/F.
rows={}
for l in text('lifetimeincome').splitlines():
    cells=l.split()
    if len(cells) in [2,4] and all(re.fullmatch(r'\d+',c) for c in cells):
        for j in range(0,len(cells),2):
            a,v=map(int,cells[j:j+2])
            if 0<=a<=65 and v>=600:rows[a]=v
assert set(rows)==set(range(66)),('lifetimeincome',len(rows))
rate('lifetimeincome',{s:[rows[a] for a in range(66)] for s in ['M','F']})

# Dense HNW tables: plain PDF text avoids wrapped line ordering of layout extraction.
import pdfplumber
def plain(id):
    sid=P[id]['source']['url'].split('/d/')[1].split('/')[0]
    with pdfplumber.open(LAYOUT/(sid+'.pdf')) as pdf:
        return '\n'.join(page.extract_text() or '' for page in pdf.pages)

def decimal_groups(s,n):
    pat=rf'(?<![\d.])(15\s*วัน|\d{{1,2}})\s+((?:\d+\.\d{{2}}\s+){{{n-1}}}\d+\.\d{{2}})(?!\d)'
    return [(0 if 'วัน' in m[1] else int(m[1]),numbers(m[2])) for m in re.finditer(pat,s)]

for base,terms in [('legacy',[10,15]),('legacyplus',[10,15,20])]:
    groups=decimal_groups(plain(base+str(terms[0])),4)
    assert len(groups)==len(terms)*len(P[base+str(terms[0])]['bands']),(base,len(groups))
    for j,term in enumerate(terms):
        id=base+str(term);rows=groups[j::len(terms)]
        assert [a for a,_ in rows]==P[id]['bands']
        rate(id,{'M':[v[0] for _,v in rows],'F':[v[1] for _,v in rows]})
        rate(id,{'M':[v[2] for _,v in rows],'F':[v[3] for _,v in rows]},20000000,True)
rows=dict(decimal_groups(plain('legacyprotection5'),4))
assert set(rows)==set(range(76)),('legacyprotection5',len(rows))
rate('legacyprotection5',{'M':[rows[a][0] for a in range(76)],'F':[rows[a][1] for a in range(76)]})
rate('legacyprotection5',{'M':[rows[a][2] for a in range(76)],'F':[rows[a][3] for a in range(76)]},20000000,True)

# ProCare: age, total, life, CI; total must be life+CI, not either component alone.
groups=decimal_groups(plain('ciprocare'),3)
assert len(groups)==122,('ciprocare',len(groups))
for _,v in groups:assert abs(v[0]-v[1]-v[2])<.001
rate('ciprocare',{'M':[v[0] for _,v in groups[::2]],'F':[v[0] for _,v in groups[1::2]]})

# Benefit Plus is a second source for the fourteen previously cross-checked main tables.
audit_code=(ROOT/'scripts/audit-benefit-plus.py').read_text()
audit_code=audit_code.split("(root/'data/benefit-plus-audit.json').write_text")[0]
audit_code=audit_code.replace(' p=P[id];diff=[];count=0',' CAPTURE[id]=r; p=P[id];diff=[];count=0')
capture={};argv=sys.argv
try:
    sys.argv=['audit-benefit-plus.py',str(SOURCE)]
    exec(compile(audit_code,str(ROOT/'scripts/audit-benefit-plus.py'),'exec'),{'__file__':str(ROOT/'scripts/audit-benefit-plus.py'),'CAPTURE':capture})
finally:sys.argv=argv
assert len(capture)==14
for id,r in capture.items():rate(id,r)

# Standard SuperCare: four repeated age/total/life/CI column groups.
groups=[]
for line in text('cisuper10','super').splitlines():
    cells=line.replace('15 วัน','0').split()
    if len(cells)==16 and all(re.fullmatch(N,c) for c in cells) and all(cells[j]==cells[0] for j in [4,8,12]):groups.append(numbers(' '.join(cells)))
assert len(groups)==66
for j,pay in enumerate([10,20]):
    rate('cisuper'+str(pay),{s:[row[j*8+k*4+1] for row in groups] for k,s in enumerate(['M','F'])})
    # Prestige is checked against its own absolute-premium tables at 5m, 10m, 15m.
    rows=annual_rows(text('cisuperprestige'+str(pay),'prestige'),6)
    assert len(rows)==396
    table=rows[j*198:j*198+66];discount=3.5 if pay==10 else 2
    assert [a for a,_ in table]==list(range(66))
    base={s:[round(v[k*3]/5000+discount,2) for _,v in table] for k,s in enumerate(['M','F'])}
    for band in range(3):
        for i,(age,v) in enumerate(rows[j*198+band*66:j*198+(band+1)*66]):
            for k,s in enumerate(['M','F']):assert abs((base[s][i]-discount)*(band+1)*5000-v[k*3])<.001
    rate('cisuperprestige'+str(pay),base)

# H&S and H&S Extra: one table page with the male block followed by the female block.
for id,label,count in [('hs','AIA H&S (new standard)',15),('hsextra','AIA H&S Extra (new standard)',18)]:
    pages=[p for p in text(id).split('\f') if 'เบี้ยประกันภัยมาตรฐานราย' in p and label in p]
    assert len(pages)==1,(id,len(pages))
    rows=ranges(pages[0],7);assert len(rows)==count*2,(id,len(rows))
    assert [a for a,_ in rows[:count]]==[a for a,_ in rows[count:]]==P[id]['bands']
    for j,plan in enumerate(P[id]['plans']):rate(id,{sex:[v[j] for _,v in rows[k*count:(k+1)*count]] for k,sex in enumerate(['M','F'])},plan['id'])

# Kids: only the two new-business age rows for each deductible, with paired M/F by plan.
s=text('happykids');headers=list(re.finditer(r'กรณีมีความรับผิดสวนแรก\s+(10,000|30,000)',s))
assert len(headers)==2,('kids headings',len(headers))
for k,h in enumerate(headers):
    block=s[h.start():headers[k+1].start() if k==0 else len(s)]
    rows=ranges(block,8)[:2];assert [a for a,_ in rows]==[5,10]
    deductible=h[1].replace(',','')
    for j,million in enumerate([1,5,15,25]):rate('happykids',{sex:[v[j*2+i] for _,v in rows] for i,sex in enumerate(['M','F'])},deductible+'-'+str(million))

# Topup and cancer tables in the CI rider book. Topup is per 1,000 of Topup capital.
s=text('citopup');page=next(p for p in s.split('\f') if 'อัตราเบี้ยประกันภัยมาตรฐานราย' in p and 'AIA CI Top Up' in p)
rows=ranges(page,2);assert [a for a,_ in rows]==P['citopup']['bands']
rate('citopup',{sex:[v[k] for _,v in rows] for k,sex in enumerate(['M','F'])})
page=next(p for p in s.split('\f') if 'เบี้ยประกันภัยมาตรฐานราย' in p and 'AIA Health Cancer' in p)
rows=ranges(page,4);assert [a for a,_ in rows]==P['healthcancer']['bands']
for j,plan in enumerate(['standard','nonsmoker']):rate('healthcancer',{sex:[v[j*2+k] for _,v in rows] for k,sex in enumerate(['M','F'])},plan)

# Lady Care has one single-age row (60), Plus has a single-age row (40).
page=next(p for p in s.split('\f') if 'อัตราเบี้ยประกันภัยมาตรฐานราย' in p and 'Lady Care & Lady Care Plus' in p)
columns=[[],[]]
for line in page.splitlines():
    groups=list(re.finditer(r'(\d{2})(?:\s*-\s*(\d{2}))?\s*(?:\([^)]*\)\s*)?(\d+\.\d+)',line))
    if len(groups)==2:
        for j,m in enumerate(groups):columns[j].append((int(m[2] or m[1]),float(m[3])))
for j,id in enumerate(['ladycare','ladycareplus']):
    assert [a for a,_ in columns[j]]==P[id]['bands'],(id,columns[j])
    rate(id,{'F':[v for _,v in columns[j]]})

# Accident occupation rates: the PDF prints ADB occupation 1+2 as a merged cell.
s=text('ai');block=s[s.index('อัตราเบี้ยประกันภัยมาตรฐานราย'):]
dec=[float(v) for v in re.findall(r'\d+\.\d+',block)]
assert dec==[5,6,7,9,2,3,4,5,1.5,2.25,3,1.25,1,.75],dec
for id,r,rcc in [('ai',dec[:4],dec[11]),('add',dec[4:8],dec[12]),('adb',[dec[8],dec[8],dec[9],dec[10]],dec[13])]:
    for suffix in ['', 'rcc']:
        for j,value in enumerate(r):rate(id+suffix,{s:[value+(rcc if suffix else 0)] for s in ['M','F']},str(j+1))

# HB: childhood shared rate and printed adult occupation rates; no percentage rounding.
s=text('hb');block=s[s.index('อัตราเบี้ยประกันภัยมาตรฐานรายปของสัญญาเพิ่มเติม HB'):];block=block[:block.index('สัญญาเพิ่มเติมเปน')]
assert re.search(r'6\s*-\s*15\s+90',block)
assert re.search(r'1,2\s+150',block) and re.search(r'3\s+187',block) and re.search(r'4\s+225',block)
for plan,adult in [('1',150),('3',187),('4',225)]:rate('hb',{s:[90,adult] for s in ['M','F']},plan)

# Life Protector: extract the two age/M/F groups on their dedicated Benefit Plus pages.
pages=text('protector70','benefit').split('\f')
for id,page_index in [('protector70',6),('protector80',7)]:
    rows={}
    for m in re.finditer(r'(?<![\d.])(\d{1,2}|15\s*วัน)\s+(\d+\.\d{2})\s+(\d+\.\d{2})(?!\d)',pages[page_index]):
        age=0 if 'วัน' in m[1] else int(m[1]);rows[age]=[float(m[2]),float(m[3])]
    assert set(P[id]['bands'])<=set(rows),(id,len(rows))
    rate(id,{sex:[rows[a][k] for a in P[id]['bands']] for k,sex in enumerate(['M','F'])})

# Re-read every printed waiver matrix, retaining nulls rather than filling unavailable cells.
code=(ROOT/'scripts/import-waivers.py').read_text().split("add('wp',")[0]
ctx={'__file__':str(ROOT/'scripts/import-waivers.py')};argv=sys.argv
try:
    sys.argv=['import-waivers.py',str(SOURCE),str(LAYOUT/'waiver.txt')]
    exec(compile(code,str(ROOT/'scripts/import-waivers.py'),'exec'),ctx)
finally:sys.argv=argv
for id in ['pb','pbci','wpci']:
    r=next(p for p in ctx['P'] if p['id']==id)
    EXPECTED[id]={'rates':{},'plans':{},'tiers':{},'waiverRates':r['waiverRates']}

# WP has no purchase-premium table in the supplied book. It must remain explicitly manual.
assert P['wp'].get('quoteMode')=='manual' and not P['wp'].get('rates')
EXPECTED['wp']={'rates':{},'plans':{},'tiers':{},'manual':True}

# Printed units and discount brackets (currency per 1,000 capital, unless stated).
DISCOUNTS={
 'payplus10':[[700000,1.5],[500000,1]],'payplus15':[[700000,1.5],[500000,1]],'payplus20':[[700000,1.5],[500000,1]],
 'pay20':[[600000,2],[250000,1]],'pay10':[[500000,1]],'pay15':[[500000,1]],
 'endowment':[[600000,1.5],[300000,1]],'excellent':[[250000,1]],
 'term5':[[1000000,1],[500000,.5]],'term10':[[1000000,1],[500000,.5]],'term15':[[1000000,1],[500000,.5]],'term20':[[1000000,1],[500000,.5]],
 'ciprocare':[[5000000,3],[1000000,2.25],[800000,1.5],[500000,.75]],
 'cisuper10':[[1000000,2.5]],'cisuper20':[[1000000,1.5],[800000,1],[500000,.5]],
 'cisuperprestige10':[[5000000,3.5]],'cisuperprestige20':[[5000000,2]],
 'protector70':[[1500000,1.5]],'protector80':[[1500000,1.5]],
}
FLAT={'happy','saver','herobegin','herobalanced','starterbegin','starterbalanced','infinite','hs','hsextra','happykids','wp'}
for id,e in EXPECTED.items():
    e['unit']=10 if id=='healthcancer' else 0 if id in FLAT else 100 if id in ['pb','pbci','hb','hbextra'] else 100000 if id=='cancer' else 1000
    e['discounts']=DISCOUNTS.get(id,[])
    e['source']=P[id]['source']
assert set(EXPECTED)==set(P),('Not all products audited',set(P)-set(EXPECTED))

def finish():
    differences=[];count=0;numeric=0;blank=0
    for id,e in EXPECTED.items():
        p=P[id]
        pairs=[]
        if e['rates']:pairs.append(('rates',p['rates'],e['rates']))
        for key,r in e['plans'].items():pairs.append(('plan:'+key,next(x for x in p['plans'] if x['id']==key)['rates'],r))
        for key,r in e['tiers'].items():pairs.append(('tier:'+key,next(x for x in p['amountTiers'] if x['minAmount']==int(key))['rates'],r))
        for label,current,expected in pairs:
            for sex,values in expected.items():
                for i,v in enumerate(values):
                    count+=1
                    numeric+=v is not None
                    blank+=v is None
                    if current[sex][i]!=v:
                        differences.append({'id':id,'table':label,'sex':sex,'ageBand':p['bands'][i],'before':current[sex][i],'after':v})
                if WRITE:current[sex]=values
        if 'waiverRates' in e:
            for sex,terms in e['waiverRates'].items():
                for term,values in terms.items():
                    for i,v in enumerate(values):
                        count+=1
                        numeric+=v is not None
                        blank+=v is None
                        if p['waiverRates'][sex][term][i]!=v:differences.append({'id':id,'table':'waiver:'+term,'sex':sex,'column':i,'before':p['waiverRates'][sex][term][i],'after':v})
            if WRITE:p['waiverRates']=e['waiverRates']
        for field in ['unit','discounts']:
            if p[field]!=e[field]:differences.append({'id':id,'field':field,'before':p[field],'after':e[field]})
            if WRITE:p[field]=e[field]
    report={'date':'2026-10-21','scope':'Existing traditional main/PPR products; source-edition match, not confirmation of currently offered company rates','productsChecked':len(EXPECTED),'automaticRateProducts':62,'manualOnly':['wp'],'rateCellsChecked':count,'numericRateCells':numeric,'unavailableCellsPreserved':blank,'products':[{'id':id,'name':P[id]['name'],'status':'manual-no-rate-table' if id=='wp' else 'source-matched','source':P[id]['source']} for id in P],'differences':differences,'pending':[id for id in P if id not in EXPECTED]}
    (ROOT/'data/full-rate-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (ROOT/'tests/source-rate-fixtures.json').write_text(json.dumps(EXPECTED,ensure_ascii=False,indent=2))
    if WRITE:(ROOT/'data/products.json').write_text(json.dumps(list(P.values()),ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='products'},ensure_ascii=False,indent=2))
    if differences and not WRITE:raise SystemExit('Source differences found: rerun with --write only after review')
finish()
