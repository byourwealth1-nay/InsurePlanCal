"""Import PPR waiver tables from the supplied native PDF layout. Never interpolate blank cells.
Usage: python scripts/import-waivers.py sources.json /path/to/waiver-layout.txt
"""
import json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];D={d['id']:d for d in json.load(open(sys.argv[1]))};P=json.load(open(R/'data/products.json'));pages=Path(sys.argv[2]).read_text().split('\f');src='1lXLrKlYosuYDiXuh0vt1pc32m0spUwjR'
def add(id,name,lo,hi,**extra):
 p=dict(id=id,name=name,category='rider',source={'title':D[src]['title'],'url':D[src]['url']},minAge=lo,maxAge=hi,unit=100,minAmount=0,maxAmount=None,bands=[hi],rates=None,plans=None,discounts=[],note='',step=1);p.update(extra);P[:]=[x for x in P if x['id']!=id];P.append(p);return p
rates={s:{} for s in ['M','F']}
for line in pages[2].splitlines():
 m=re.match(r'^\s*(\d+)\s+((?:\d+\.\d+\s*)+)$',line)
 if not m:continue
 year=int(m[1]);v=list(map(float,m[2].split()));assert year in range(2,26) and len(v)%2==0
 for j,s in enumerate(['M','F']):rates[s][str(year)]=[(v[k*2+j] if k*2+j<len(v) else None) for k in range(5)]
assert set(rates['M'])==set(map(str,range(2,26)))
add('pb','PB',0,15,waiverType='payer',payerMinAge=20,payerMaxAge=50,payerBands=[30,35,40,45,50],waiverRates=rates,note='ใช้เพศ/อายุผู้ชำระเบี้ย · เบี้ยคิดจากเบี้ยหลัก · ระยะคุ้มครองคำนวณตามคู่มือ')
rates={s:{str(y):[None]*51 for y in range(2,26)} for s in ['M','F']}
for sex,page,first in [('M',6,2),('M',7,14),('F',8,2),('F',9,14)]:
 rows=0
 for line in pages[page].splitlines():
  m=re.match(r'^\s*(\d+)\s+((?:\d+\.\d+\s*)+)$',line)
  if not m:continue
  age=int(m[1]);v=list(map(float,m[2].split()));assert 20<=age<=70 and len(v)<=12
  for j,r in enumerate(v):rates[sex][str(first+j)][age-20]=r
  rows+=1
 assert rows==(51 if first==2 else 47),(page,rows)
add('pbci','PBCI',0,15,waiverType='payer',payerMinAge=20,payerMaxAge=70,payerBands=list(range(20,71)),waiverRates=rates,note='ใช้เพศ/อายุผู้ชำระเบี้ย · เบี้ยคิดจากเบี้ยหลัก · ไม่ใช้เพศ/อายุเด็กแทนผู้ชำระเบี้ย')
rates={s:{str(y):[None]*12 for y in [5,10,15,20,25,30,35,40,50,60,70,80]} for s in ['M','F']};years=None;count=0
for line in pages[14].splitlines():
 if re.search(r'\s5\s+10\s+15\s+20\s+25\s+30\s*$',line):years=[5,10,15,20,25,30]
 if re.search(r'\s35\s+40\s+50\s+60\s+70\s+80\s*$',line):years=[35,40,50,60,70,80]
 m=re.match(r'^\s*(\d+)\s*[–-]\s*(\d+)\s+((?:\d+\.\d+\s*)+)$',line)
 if not m:continue
 v=list(map(float,m[3].split()));assert years and len(v)%2==0
 i=(int(m[2])-20)//5
 for k,r in enumerate(v):rates[['M','F'][k%2]][str(years[k//2])][i]=r
 count+=1
assert count==22,count
add('wpci','WPCI',16,75,unit=1000,waiverType='insured',waiverRates=rates,note='ทุน = เบี้ยหลักต่อปี · ระยะชำระตามแบบหลัก · รองรับเฉพาะระยะที่มีอัตราในตาราง ไม่ประมาณอัตราระยะอื่น')
add('wp','WP (กรอกเบี้ยจากบริษัท)',16,55,unit=0,quoteMode='manual',note='เอกสารไม่มีตารางเบี้ย WP · กรอกเบี้ยตามใบเสนอขายบริษัท รวมถึง 0 บาทเมื่อบริษัทระบุว่าไม่มีเบี้ยเพิ่ม')
src='13BESkX_p1pAj3cLlvAmvCA3eCm-tKfdE'
m=[730,1460,2443,3616,5255,7768,11167,15280,30000,39000,48000];f=m[:8]+[17500,23000,28500];nm=[730,1314,2199,3254,4729,6991,10050,13752]+m[8:];nf=nm[:8]+f[8:]
p=add('healthcancer','Health Cancer · 10 หน่วย',0,70,unit=0,bands=[15,35,40,45,50,55,60,65,70,75,79],plans=[{'id':'standard','name':'10 หน่วย · มาตรฐาน / สูบบุหรี่','rates':{'M':m,'F':f}},{'id':'nonsmoker','name':'10 หน่วย · ไม่สูบบุหรี่ตามเกณฑ์บริษัท','rates':{'M':nm,'F':nf}}],note='ตารางเบี้ย 10 หน่วยตามคู่มือ · แผนไม่สูบบุหรี่ใช้อัตราที่พิมพ์ในตาราง อายุ 16–65 ปี');p['source']={'title':D[src]['title'],'url':D[src]['url']}
fixed={'payplus10':10,'payplus15':15,'payplus20':20,'pay10':10,'pay15':15,'pay20':20,'protection65':10,'savingsure':10,'endowment':15,'excellent':20,'5pay10':5,'annuitysure9':9}
for p in P:
 if p['id'] in fixed:p['paymentYears']=fixed[p['id']]
 if p['id'] in ['annuityfix','annuitysure60']:p['payUntilAge']=60
 if p['id']=='senior':p['payUntilAge']=90
 if p['id'].startswith('payplus'):p['includedRiders']=['wpci']
C=[dict(title=p['name'],url=p['source']['url'],category=p['category'],status='manual' if p.get('quoteMode')=='manual' else 'used',reason=p['note'] if p.get('quoteMode')=='manual' else '') for p in P]
(R/'data/products.json').write_text(json.dumps(P,ensure_ascii=False,indent=2));(R/'data/coverage.json').write_text(json.dumps(C,ensure_ascii=False,indent=2));print(len(P),'options; WP manual only')
