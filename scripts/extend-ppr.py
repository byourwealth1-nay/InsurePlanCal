"""Add source-verified traditional products. Usage: python scripts/extend-ppr.py sources.json layout_dir"""
import json,re,sys,pathlib
root=pathlib.Path(__file__).resolve().parents[1];D={d['id']:d for d in json.load(open(sys.argv[1]))};layout=pathlib.Path(sys.argv[2]);P=json.load(open(root/'data/products.json'))
def add(id,name,cat,src,lo,hi,unit=1000,minimum=1000,maximum=None,bands=None,rates=None,plans=None,discounts=None,**extra):
 d=D[src];p=dict(id=id,name=name,category=cat,source=dict(title=d['title'],url=d['url']),minAge=lo,maxAge=hi,unit=unit,minAmount=minimum,maxAmount=maximum,bands=bands,rates=rates,plans=plans,discounts=discounts or [],note='',step=1);p.update(extra);P[:]=[x for x in P if x['id']!=id];P.append(p);return p
# The term sheet prints one complete age row with paired M/F columns.
src='1L3a-tExZMcLUL0dx5Rje3ZI1VZqkHdfJ';rows={}
for l in D[src]['text'].splitlines():
 m=re.match(r'^(\d{2}) ((?:\d+\.\d+ ?)+)$',l)
 if m:rows[int(m[1])]=list(map(float,m[2].split()))
assert set(rows)==set(range(20,60))
for j,(term,hi) in enumerate([(5,59),(10,55),(15,50),(20,45)]):
 add(f'term{term}',f'Term {term}','main',src,20,hi,minimum=350000,bands=list(range(20,hi+1)),rates={s:[rows[a][j*2+k] for a in range(20,hi+1)] for k,s in enumerate(['M','F'])},discounts=[[1000000,1],[500000,.5]],paymentYears=term)
src='1nu4EtjVblWxovDePTQIH9AdQ62DNNljw';v=[float(x) for x in re.findall(r'\d+\.\d+',D[src]['text'][9331:])];assert len(v)==76
add('excellent','Excellent (Non Par)','main',src,0,75,minimum=100000,bands=list(range(76)),rates={'M':v,'F':v},discounts=[[250000,1]],paymentYears=7)
# Printed amount-tier rate columns; use the printed values, not recomputed percentage rounding.
for src,id,name,n,pays,start,end in [('1kABDQipwF71Ih51wYqyvLKti_0x6le43','legacy','Legacy Prestige (New)',66,[10,15],8909,13850),('1q9LaI5oqqgfi3z9h82ybEEFqRXJm16ck','legacyplus','Legacy Prestige Plus (New)',76,[10,15,20],22330,31200)]:
 v=[float(x) for x in re.findall(r'\d+\.\d+',D[src]['text'][start:end])];assert len(v)==n*4*len(pays),(id,len(v))
 for j,pay in enumerate(pays):
  c=[v[(j*4+k)*n:(j*4+k+1)*n] for k in range(4)]
  add(id+str(pay),f'{name} · {pay} Pay','main',src,0,n-1,minimum=10000000,maximum=1000000000,bands=list(range(n)),rates={'M':c[0],'F':c[2]},amountTiers=[dict(minAmount=20000000,rates={'M':c[1],'F':c[3]})],paymentYears=pay,note='เบี้ยมาตรฐาน · ไม่รวม Preferred Rate · ใช้ตารางระดับทุน 20 ล้านบาทขึ้นไปโดยอัตโนมัติ')
src='1ZL26zHwzN7-35mCcMWIGEEkm6pD2PQBD';v=[float(x) for x in re.findall(r'\d+\.\d+',D[src]['text'][15744:18900])];assert len(v)==304
c=[v[i:i+41] for i in range(0,164,41)];tail=[v[i:i+35] for i in range(164,304,35)];c=[c[i]+tail[i] for i in range(4)]
add('legacyprotection5','Legacy Prestige Protection (New) · 5 Pay','main',src,0,75,minimum=15000000,bands=list(range(76)),rates={'M':c[0],'F':c[2]},amountTiers=[dict(minAmount=20000000,rates={'M':c[1],'F':c[3]})],paymentYears=5,note='เบี้ยมาตรฐาน · ไม่รวม Preferred Rate · ใช้ตารางระดับทุน 20 ล้านบาทขึ้นไปโดยอัตโนมัติ')
src='14IgySe93Tbtq1_8X5sFig4RCdcCL9-um';rates={}
for s,a in [('M',43918),('F',45585)]:
 block=re.match(r'(?:\d[\d,.]*\s+){10,}',D[src]['text'][a:])[0];v=list(map(float,re.findall(r'\d+\.\d+',block)));assert len(v)==183
 assert all(abs(v[i]-v[61+i]-v[122+i])<.001 for i in range(61));rates[s]=v[:61]
add('ciprocare','CI ProCare · 20 Pay','main',src,0,60,minimum=200000,bands=list(range(61)),rates=rates,discounts=[[5000000,3],[1000000,2.25],[800000,1.5],[500000,.75]],paymentYears=20)
# Source layout has four adjacent complete age/total/life/CI groups per line.
L=(layout/'super-layout.txt').read_text().splitlines();rows=[]
for l in L:
 cells=l.replace('15 วัน','0').split()
 if len(cells)==16 and all(re.fullmatch(r'\d+(?:\.\d+)?',x) for x in cells) and all(cells[j]==cells[0] for j in [4,8,12]):rows.append(cells)
assert len(rows)==66 and [int(x[0]) for x in rows]==list(range(66))
for j,pay in enumerate([10,20]):
 rates={s:[float(x[j*8+k*4+1]) for x in rows] for k,s in enumerate(['M','F'])}
 src='1yme5OpwuVLo4VXmOlZ58-SLnE8zZOzY9';disc=[[1000000,2.5]] if pay==10 else [[1000000,1.5],[800000,1],[500000,.5]]
 add('cisuper'+str(pay),f'CI SuperCare · {pay}/99','main',src,0,65,minimum=200000,maximum=4999999,bands=list(range(66)),rates=rates,discounts=disc,paymentYears=pay)
 # Prestige brochure confirms each printed amount row equals standard rate minus this tier discount.
 src='1L2NoUdrZ6Fa7HP_KNqmOf05z_B_SBB-a';discount=3.5 if pay==10 else 2
 add('cisuperprestige'+str(pay),f'CI SuperCare Prestige · {pay}/99','main',src,0,65,minimum=5000000,maximum=15000000,bands=list(range(66)),rates=rates,discounts=[[5000000,discount]],paymentYears=pay,note='เบี้ยมาตรฐาน · ทุนสูงสุด 5 ล้านบาทสำหรับผู้ไม่มีรายได้ ต้องตรวจเกณฑ์ทุนรวม')
# Additional room-based plans from native PDF layout (not the scrambled connector text).
L=(layout/'health-layout.txt').read_text().splitlines()
for id,name,start,end,n,rooms in [('hs','H&S (new standard)',135,188,15,[1000,1600,2200,2800,3400,4000,5000]),('hsextra','H&S Extra (new standard)',335,400,18,[1500,2000,2500,3500,4500,5500,6500])]:
 rows=[]
 for l in L[start:end]:
  m=re.match(r'^\s*(\d+)\s*-\s*(\d+)\*?\s+((?:[\d,]+\s*){7})$',l)
  if m:rows.append((int(m[2]),[int(x.replace(',','')) for x in m[3].split()]))
 assert len(rows)==n*2,(id,len(rows));bands=[x[0] for x in rows[:n]]
 add(id,name,'health','1kdHw2KAsXCJ2HXr0BU6Z6HkMgktmtTa1',11,75,unit=0,bands=bands,plans=[dict(id=str(room),name=f'ค่าห้อง {room:,} บาท / วัน',rates={s:[x[1][j] for x in rows[k*n:(k+1)*n]] for k,s in enumerate(['M','F'])}) for j,room in enumerate(rooms)])
src='1c2k-nm59hrB2nZET64zMPI_0WyeItn4o';plans=[]
for deductible,anchor in [(10000,'53,500'),(30000,'33,500')]:
 t=D[src]['text'];v=[int(x.replace(',','')) for x in re.findall(r'\d{1,3}(?:,\d{3})+',t[t.index(anchor):])[:16]];c=[v[i:i+2] for i in range(0,16,2)]
 for j,million in enumerate([1,5,15,25]):
  m,f=([0,1],[2,3],[5,4],[6,7])[j]
  plans.append(dict(id=f'{deductible}-{million}',name=f'{million} ล้านบาท · รับผิดส่วนแรก {deductible:,} บาท/ปี',rates={'M':c[m],'F':c[f]}))
add('happykids','Health Happy Kids','health',src,0,10,unit=0,bands=[5,10],plans=plans,note='ตารางรับใหม่ 15 วัน–10 ปี · ตรวจตำแหน่งชาย/หญิงกับ PDF หน้า 11 แล้ว')
src='13BESkX_p1pAj3cLlvAmvCA3eCm-tKfdE';v=[float(x) for x in re.findall(r'\d+\.\d+',D[src]['text'][28323:29400])];assert len(v)==36
add('citopup','CI Topup (แนบ CI Plus)','rider',src,0,75,bands=[15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,98],rates={'M':v[:18],'F':v[18:]},maximum=5000000,note='ทุนต้องเท่ากับ 40% ของ CI Plus ที่เลือก · ผู้ไม่มีรายได้สูงสุด 3 ล้านบาท ต้องตรวจทุนรวม')
for id,name,hi,bands,r in [('ladycare','Lady Care',60,[24,29,34,39,44,49,54,59,60,64,69],[2.46,3.06,4.84,7.82,11.72,13.73,15.66,17.49,18.64,18.64,19.46]),('ladycareplus','Lady Care Plus',40,[24,29,34,39,40,44,49,54,59,64,69],[4.63,5.23,7.03,10.07,14.16,14.16,13.73,15.66,17.49,18.64,19.46])]:
 add(id,name,'rider',src,16,hi,bands=bands,rates={'M':None,'F':r},sexOnly='F',note='เฉพาะเพศหญิง · ตรวจเกณฑ์ทุนและการรับประกัน')
src='1iTDXgv4SUcrS2RdQ3VHnGub3Ld_pX0uW'
for id,lo,r,rcc in [('ai',16,[5,6,7,9],1.25),('add',0,[2,3,4,5],1),('adb',0,[1.5,2.25,3],.75)]:
 # ADB groups occupation 1+2 in a merged cell, as shown in the PDF.
 if id=='adb':r=[1.5,1.5,2.25,3]
 for extra in [False,True]:
  rates=[x+(rcc if extra else 0) for x in r]
  add(id+('rcc' if extra else ''),id.upper()+(' + RCC' if extra else ''),'rider',src,lo,64,bands=[64],plans=[dict(id=str(i+1),name=f'ขั้นอาชีพ {i+1}',rates={'M':[v],'F':[v]}) for i,v in enumerate(rates)],accidentFamily=id,note='เลือกขั้นอาชีพตามคู่มืออาชีพ · ต้องตรวจทุนรวมอุบัติเหตุ')
src='1kdHw2KAsXCJ2HXr0BU6Z6HkMgktmtTa1'
add('hb','HB','rider',src,6,55,unit=100,minimum=100,bands=[15,55],plans=[dict(id=str(i),name='ขั้นอาชีพ '+('1–2' if i==1 else str(i)),rates={'M':[90,r],'F':[90,r]}) for i,r in [(1,150),(3,187),(4,225)]],step=100,note='จำนวนเงินคือค่าชดเชยรายวัน · ต้องตรวจวงเงินตามรายได้')
# Coverage ledger lists only the traditional scope; UL/UDR and training are omitted.
used={p['source']['url'] for p in P};coverage=[dict(title=p['name'],url=p['source']['url'],status='used',reason='',category=p['category']) for p in P]
for name,src,cat,reason in [('WP','1lXLrKlYosuYDiXuh0vt1pc32m0spUwjR','rider','คู่มือที่ได้รับไม่มีตารางเบี้ย WP ต้องใช้ตารางอัตราเพิ่มเติม'),('PB','1lXLrKlYosuYDiXuh0vt1pc32m0spUwjR','rider','อยู่ระหว่างตรวจสูตรระยะคุ้มครองและข้อมูลผู้ชำระเบี้ย'),('PBCI','1lXLrKlYosuYDiXuh0vt1pc32m0spUwjR','rider','อยู่ระหว่างตรวจสูตรระยะคุ้มครองและข้อมูลผู้ชำระเบี้ย'),('WPCI','1lXLrKlYosuYDiXuh0vt1pc32m0spUwjR','rider','ตารางที่ได้รับระบุเพียงตัวอย่างระยะชำระ ยังต้องยืนยันระยะอื่น'),('Life Protector 70 / 80','1PfO-oPGBnw2R_OAvm--nOb-Np78QhvgW','main','อยู่ระหว่างตรวจตารางเบี้ยและช่วงอายุ'),('Lifetime Income 9/99','1jPscxsgbG0vpPyDIKYJdBJsRw0opaRhm','main','อยู่ระหว่างตรวจตารางและเงื่อนไข'),('Health Cancer',src if False else '13BESkX_p1pAj3cLlvAmvCA3eCm-tKfdE','health','อยู่ระหว่างตรวจตารางอัตราและส่วนลด')]:
 d=D[src];coverage.append(dict(title=name,url=d['url'],category=cat,status='pending',reason=reason))
for p in P:
 for r in ([p['rates']] if p['rates'] else [q['rates'] for q in p['plans']]):
  for sex in ['M','F']:
   if p.get('sexOnly') and sex!=p['sexOnly']:continue
   assert len(r[sex])==len(p['bands']) and all(x>0 for x in r[sex]),p['id']
(root/'data/products.json').write_text(json.dumps(P,ensure_ascii=False,indent=2));(root/'data/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2));print(len(P),'products',len(coverage)-len(P),'pending entries')
