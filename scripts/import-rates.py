"""Import explicitly mapped columns from the supplied source text; never infer missing rates.
Usage: python scripts/import-rates.py /path/to/sources.json
"""
import json,re,sys,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
docs=json.load(open(sys.argv[1])); D={d['id']:d for d in docs}; products=[]
def add(id,name,category,source,lo,hi,unit=1000,minimum=1000,maximum=None,bands=None,rates=None,plans=None,discounts=None,note='',step=1):
 d=D[source];products.append(dict(id=id,name=name,category=category,source=dict(title=d['title'],url=d['url']),minAge=lo,maxAge=hi,unit=unit,minAmount=minimum,maxAmount=maximum,bands=bands,rates=rates,plans=plans,discounts=discounts or [],note=note,step=step))
def dec(id,start,n):
 t=D[id]['text'];i=t.index(start);v=[float(s) for s in re.findall(r'(?<![\d.])\d+\.\d+(?![\d.])',t[i:])][:n];assert len(v)==n,(id,start,len(v));return v
p='1VyFKzjbMDv45nPb5YM77uXANLr68XKXk'
# Two halves of the printed age table. Each selector names a confirmed column start.
cols={10:('24.35','17.53','53.43','38.41'),15:('19.37','15.42','47.09','32.26'),20:('14.80','13.31','30.52','25.59')}
for pay,c in cols.items():
 r={'M':dec(p,c[0],38)+dec(p,c[2],38),'F':dec(p,c[1],38)+dec(p,c[3],38)}
 add(f'payplus{pay}',f'Pay Life Plus · {pay} Pay','main',p,0,75,minimum=150000 if pay==20 else 300000,maximum=9999999,bands=list(range(76)),rates=r,discounts=[[700000,1.5],[500000,1]],note='อายุ 0 ต้องมีอายุจริงอย่างน้อย 15 วัน · WPCI/TI รวมในแบบตามเอกสาร')
p='1A148usHQLHLHuvBjFIlDwHa3A_C1Te-V';r=dec(p,'12.76',142);m=[];f=[];offset=0
for n in [16,20,20,15]:m+=r[offset:offset+n];f+=r[offset+n:offset+2*n];offset+=2*n
add('pay20','20 Pay Life (Non Par)','main',p,0,70,minimum=100000,bands=list(range(71)),rates={'M':m,'F':f},discounts=[[600000,2],[250000,1]],note='อายุ 0 ต้องมีอายุจริงอย่างน้อย 15 วัน')
p='1Ei2obYSfM9uUvX9q1aj-ELcX4JxzkDCj';v=dec(p,'22.14',264);c=[v[i:i+33] for i in range(0,264,33)]
for pay,a,b in [(10,0,1),(15,3,2)]:
 add(f'pay{pay}',f'{pay} Pay Life (Non Par)','main',p,0,65,minimum=300000,maximum=9999999,bands=list(range(66)),rates={'M':c[a]+c[a+4],'F':c[b]+c[b+4]},discounts=[[500000,1]],note='อายุ 0 ต้องมีอายุจริงอย่างน้อย 15 วัน')
p='1gVQi1tLb8JIhXbcWjHpqExUBbVGxkpSx'
add('senior','Senior Happy','main',p,50,70,minimum=50000,maximum=200000,bands=list(range(50,71)),rates={'M':[59.80,61.52,63.25,64.97,66.70,68.42,70.15,73.60,77.05,80.50,83.95,87.40,90.85,94.30,98.32,102.35,107.52,112.12,116.72,121.90,127.65],'F':[50.02,51.75,53.47,55.20,56.92,58.07,59.22,61.52,63.82,66.12,68.42,70.72,74.17,77.62,81.07,84.52,87.97,91.42,96.60,102.35,106.95]},note='เงื่อนไขความคุ้มครองช่วงแรกต่างจากประกันชีวิตทั่วไป · ยังไม่ยืนยันการแนบสัญญาเพิ่มเติม')
p='1UEett_Xsyi-ZZ28_l24PKm3azwS-HyGj'
add('annuityfix','Annuity Fix','main',p,20,55,minimum=200000,bands=list(range(20,56)),rates={'M':[16.2,16.9,17.7,18.5,19.3,20.2,21.2,22.2,23.3,24.4,25.7,27,28.4,29.9,31.6,33.4,35.4,37.5,39.9,42.4,45.3,48.5,52,56,60.4,65.6,71.5,78.3,86.3,95.83,107.2,121.1,138.6,161.5,192.4,236.5],'F':[16.5,17.2,18,18.7,19.6,20.5,21.4,22.4,23.5,24.6,25.8,27.1,28.5,30,31.7,33.4,35.4,37.5,39.8,42.4,45.2,48.3,51.7,55.6,60.1,65.2,70.9,77.6,85.6,95.07,106.33,120.1,137.6,160.3,191,234.8]},note='จำนวนเงินที่กรอกคือฐานเงินบำนาญ ไม่ใช่ทุนเสียชีวิต · แนบได้เฉพาะอุบัติเหตุตามเอกสาร')
p='1VFf8NTvHq_gVlINUqSnlOLbUTLclW_AC'
for pay,hi,m,f in [('60',55,[44,46,48,50,51,55,56,59,61,64,70,70,74,79,82,90,92,98,105,111,123,127,137,148,160,178,191,210,232,259,292,333,387,458,557,649],[47,50,51,54,56,58,61,64,67,70,73,77,80,85,89,95,99,106,112,119,129,136,146,157,170,186,201,220,243,270,304,345,398,467,564,676]),('9',50,[154,157,161,164,167,171,175,179,183,187,191,195,200,204,209,213,218,223,228,235,241,247,255,262,270,279,287,296,306,316,328],[168,172,176,179,183,187,190,194,199,202,207,212,216,221,225,230,236,242,247,254,260,267,273,281,288,296,304,313,321,331,340])]:
 add('annuitysure'+pay,'Annuity Sure · '+('ชำระถึงอายุ 60' if pay=='60' else '9 Pay'),'main',p,20,hi,minimum=100000,bands=list(range(20,hi+1)),rates={'M':m,'F':f},note='แนบได้เฉพาะอุบัติเหตุตามเอกสาร')
# Retain the previously checked Health Happy table exactly.
old=(root/'index.html').read_text();oldrates=json.loads(re.search(r'const rates=(\{.*?\});',old).group(1)) if 'const rates=' in old else json.load(open(root/'data/legacy-rates.json'))
(root/'data/legacy-rates.json').write_text(json.dumps(oldrates))
plans=[dict(id=str(i),name=f'{n} ล้านบาท',rates={'M':oldrates['healthM'][i],'F':oldrates['healthF'][i]}) for i,n in enumerate([1,5,15,25])]
add('happy','Health Happy','health','1qb8UFnp26pcXQFhgOk-LlNky13veqTqY',11,75,unit=0,bands=[15,20,25,30,35,40,45,50,55,59,65,70,75],plans=plans,note='ตารางเบี้ย ก.ค. 2025 · ไม่รวมส่วนลด Vitality')
p='1XI7u-my195pAlESJ9T3Myj0bC0Qc35L8';t=D[p]['text'];t=t[t.index('10,100'):];v=[int(s.replace(',','')) for s in re.findall(r'\d{1,3}(?:,\d{3})+',t)][:144];assert len(v)==144;c=[v[i:i+18] for i in range(0,144,18)]
add('saver','Health Saver','health',p,11,75,unit=0,bands=[15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,98],plans=[dict(id=str(i),name=f'{n:,} บาท / ปี',rates={'M':c[i],'F':c[[5,4,6,7][i]]}) for i,n in enumerate([200000,300000,400000,500000])])
p='1s_8NLDnlMOUf1Ty_hzA7gVwP3vB_ERBR';t=D[p]['text']
for mode,start in [('begin','14,700'),('balanced','17,400')]:
 # Balanced first 17,400 occurs inside Begin; anchor after the end of Begin.
 offset=0 if mode=='begin' else t.index('474,600')+len('474,600')
 sub=t[offset:];sub=sub[sub.index(start):];v=[int(s.replace(',','')) for s in re.findall(r'\d{1,3}(?:,\d{3})+',sub)][:120];assert len(v)==120;c=[v[i:i+20] for i in range(0,120,20)]
 add('hero'+mode,'Health CI Hero · '+mode.title(),'health',p,0,65,unit=0,bands=[5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,98],plans=[dict(id=str(i),name=f'{n} ล้านบาท',rates={'M':c[[0,4,5][i]],'F':c[[1,2,3][i]]}) for i,n in enumerate([2,6,12])],note='สุขภาพสำหรับกลุ่มโรคร้ายแรงตามเงื่อนไขแผน · อายุ 0 ต้องมีอายุจริงอย่างน้อย 15 วัน')
b=[15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,98]
add('ciplus','CI Plus','rider','1tH39zurNQeQg_XdTzzWeXUiVpnCl3r0B',0,75,bands=b,rates={'M':[2.62,2.76,2.89,3.16,3.84,5.23,10.19,15.92,25.38,42.31,61.04,81.76,112.64,142.38,183.1,261.54,386.58,503.41],'F':[2.27,2.06,2.15,2.55,3.53,4.60,6.38,10.17,15.92,26.09,35.81,51.71,73.52,104.55,139.66,240.90,384.25,497.74]},note='ทุนที่กรอกใช้ประเมินเบี้ยเท่านั้น ต้องตรวจเกณฑ์ทุนขั้นต่ำ/สูงสุดและทุนรวมโรคร้ายแรงกับคู่มือรับประกัน')
add('mpciplus','Multi-Pay CI Plus + Total Care','rider','1CBCruAAq2kk8AQ2rirNeM9UwGuJNCl3r0B' if False else '1CBCruAAq2kk8AQ2rirNeM9UwGuJNClIC',0,75,bands=[5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,79,80,85,90,95,98],rates={'M':[6.31,4.61,4.55,4.52,5.05,5.56,6.61,8.75,16.87,27.70,49.73,83.62,130.07,163.89,235.83,326.64,295.76,381.57,621.28,909.63,1043.29],'F':[5.13,3.83,3.76,3.49,4.18,4.73,6.23,7.35,10.04,16.31,29.16,45.37,69.55,102.32,157.17,232.32,211.65,322.75,571.36,855.28,1065.97]},note='เบี้ยรวม Multi-Pay CI Plus และ Total Care · ต้องตรวจเกณฑ์ทุนรวมโรคร้ายแรงก่อนเสนอขาย')
add('cancer','Care for Cancer','rider','1I7skxPshRw4HTw6c2jgSlJ0HM_Cc9Mng',0,70,unit=100000,minimum=100000,maximum=10000000,step=100000,bands=[15,20,25,30,35,40,45,50,55,60,65,70,75,79],rates={'M':[119.51,135.16,155.84,189.26,253.51,386.81,512.13,800.92,1282.87,1869.36,2876.04,4676.21,6152.96,7639.52],'F':[119.51,139.33,182.50,253.40,375.68,462.17,669.69,921.10,1247.10,1774.95,2115.73,3143.33,3834.44,4591.68]},note='หนึ่งหน่วย = ทุน 100,000 บาท · เกณฑ์ทุนรวมขึ้นกับการรับประกัน')
add('hbextra','HB Extra','rider','1xDv4x6AdlzAlMFHkRVy4ZrxVbpBC8yr0',0,70,unit=100,minimum=100,step=100,bands=[20,35,40,45,50,55,60,65,70,75,79],rates={'M':[360,210,230,250,290,350,420,510,710,910,1140],'F':[325,280,290,320,370,400,460,490,600,710,840]},note='จำนวนเงินที่กรอกคือค่าชดเชยรายวัน · วงเงินสูงสุดขึ้นกับรายได้และการรับประกัน')
add('tpd','TPD','rider','1a1PhNRZ4uA6jYQ56crBWne60ET1zrOFK',0,70,bands=[5,15,20,25,30,35,40,45,50,55,60,65,70,75,79],rates={'M':[.10,.08,.23,.28,.31,.36,.46,.61,.87,1.25,1.86,2.98,5.03,8.78,14.06],'F':[.08,.06,.08,.09,.10,.12,.16,.24,.36,.55,.91,1.58,3.01,6.01,10.38]},note='ต้องตรวจทุน TPD เทียบทุนหลักและเกณฑ์รับประกัน')
# Shared male/female columns printed as a single rate column.
for id,name,src,lo,hi,minimum,maximum,bands,values,disc in [
 ('protection65','Protection 65','1qRvE1TXq2RMCycZ2ah2jjaHsp2iIKHqi',0,60,100000,None,list(range(61)),[29,30,31,32,33,34,35,36,37,39,40,41,43,44,46,47,49,51,53,55,57,59,61,63,66,69,71,74,77,81,84,88,92,96,100,105,110,116,122,128,135,143,151,160,170,181,193,206,221,238,258,309,338,372,413,461,520,593,689,816,995],[]),
 ('savingsure','Saving Sure','1LVmSLDFq6SpTjC0x08dDf9j5TeN39hXU',0,50,100000,None,list(range(51)),[96.53,99.24,102.02,104.87,107.81,110.83,113.93,117.12,120.40,123.77,127.24,130.80,134.46,138.23,142.10,146.07,150.17,154.37,158.69,163.14,167.70,172.40,177.23,182.19,187.29,192.53,197.92,203.47,209.16,215.02,221.04,227.23,233.59,240.13,246.86,253.77,260.87,268.18,275.69,283.41,291.34,299.50,307.89,316.51,325.37,334.48,343.84,353.47,363.37,373.54,384],[]),
 ('5pay10','5 Pay 10 (Non Par)','1aLsNN4Kwp_f9RZkg_7WM0qZ1X6bKfa-8',16,60,20000,1000000,[40,55,60],[870,880,900],[]),
 ('endowment','Endowment 15/25','1GI1h_DHNPFQKvt7IG8ndQc6uWKX20kMh',0,70,100000,None,[35,40,45,50,55,65,66,67,68,69,70],[82,83,84,86,88,90,91,93,94,95,96],[[600000,1.5],[300000,1]])]:
 add(id,name,'main',src,lo,hi,minimum=minimum,maximum=maximum,bands=bands,rates={'M':values,'F':values},discounts=disc,note='อัตราชายและหญิงเท่ากันตามตาราง · อายุ 0 ต้องมีอายุจริงอย่างน้อย 15 วัน' if lo==0 else '')
p='1TnO8I_8thH2ARse_qv24vMJC5LDFIBZM';t=D[p]['text']
for mode,start,n,lo in [('begin','32,700',20,0),('balanced','9,400',18,11)]:
 offset=t.index('แบบ BEGIN') if mode=='begin' else t.index('แบบ BALANCED')
 sub=t[offset:];sub=sub[sub.index(start):];v=[int(s.replace(',','')) for s in re.findall(r'\d{1,3}(?:,\d{3})+',sub)][:n*10];assert len(v)==n*10;c=[v[i:i+n] for i in range(0,n*10,n)]
 add('starter'+mode,'Health Starter · '+mode.title(),'health',p,lo,75,unit=0,bands=([5,10] if lo==0 else [])+[15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,98],plans=[dict(id=str(i),name=f'ค่าห้อง {room:,} บาท / วัน',rates={'M':c[[0,6,7,9,8][i]],'F':c[[1,2,3,5,4][i]]}) for i,room in enumerate([1500,2000,2500,3500,4500])],note='ตรวจความคุ้มครองและค่าใช้จ่ายร่วมตามเงื่อนไขแผน · อายุ 0 ต้องมีอายุจริงอย่างน้อย 15 วัน')
p='1_ngAaphK5RgI1IcdUy7Q_9qHqndEJXZF';t=D[p]['text'];headers=list(re.finditer('เบี้ยประกันภัยมาตรฐานราย',t));assert len(headers)==3
plans=[]
for index,h in enumerate(headers):
 sub=t[h.start():headers[index+1].start() if index<2 else len(t)]
 # Only line-based premium values; excludes deductible amounts embedded in headers.
 v=[int(s.replace(',','')) for s in re.findall(r'^([0-9]{1,3}(?:,[0-9]{3})+)(?![0-9,])',sub,re.M)];assert len(v)==324,(index,len(v));c=[v[i:i+81] for i in range(0,324,81)]
 for region,label in [(0,'ทั่วโลก'),(1,'ยกเว้นสหรัฐฯ')]:
  deductible=[0,100000,300000][index];plans.append(dict(id=f'{index}-{region}',name=f'120 ล้านบาท · {label} · รับผิดส่วนแรก {deductible:,}',rates={'M':c[region*2],'F':c[region*2+1]}))
add('infinite','Infinite Care (new standard)','health',p,18,75,unit=0,bands=list(range(18,99)),plans=plans)
for p in products:
 assert p['bands']==sorted(set(p['bands']))
 for r in ([p['rates']] if p['rates'] else [plan['rates'] for plan in p['plans']]):
  for sex in ['M','F']:assert len(r[sex])==len(p['bands']) and all(v>0 for v in r[sex]),p['id']
(root/'data/products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2))
used={p['source']['url'] for p in products}
(root/'data/coverage.json').write_text(json.dumps([dict(title=d['title'],url=d['url'],status='used' if d['url'] in used else 'pending',reason='' if d['url'] in used else ('ไม่มีข้อความตารางที่อ่านได้' if not d.get('text','').strip() else 'ยังต้องตรวจตารางอัตราและเงื่อนไขก่อนเปิดคำนวณ')) for d in docs],ensure_ascii=False,indent=2))
print(f'{len(products)} products imported from {len(used)} source documents')
