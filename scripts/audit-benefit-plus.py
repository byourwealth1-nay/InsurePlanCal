import json,re
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
D=json.load(open(sys.argv[1]));L=next(d['text'] for d in D if d['id']=='1PfO-oPGBnw2R_OAvm--nOb-Np78QhvgW').splitlines();P={p['id']:p for p in json.load(open(root/'data/products.json'))};result=[]
def nums(a,b,decimal=True):
 pat=r'^\s*(\d+\.\d+)\s*$' if decimal else r'^\s*(\d+)\s*$'
 return [float(m.group(1)) for l in L[a-1:b] if (m:=re.match(pat,l))]
def check(id,r):
 p=P[id];diff=[];count=0
 for sex,v in r.items():
  assert len(v)==len(p['rates'][sex]),(id,sex,len(v),len(p['rates'][sex]))
  for i,(actual,expected) in enumerate(zip(p['rates'][sex],v)):
   count+=1
   if actual!=expected:diff.append(dict(sex=sex,ageBand=p['bands'][i],web=actual,benefitPlus=expected))
 result.append(dict(id=id,name=p['name'],compared=count,differences=diff))
v=nums(4805,5080);assert len(v)==264
check('pay10',{'M':v[:66],'F':v[66:132]});check('pay15',{'M':v[132:198],'F':v[198:]})
v=nums(6125,6687);assert len(v)==456
r={id:{sex:[] for sex in ['M','F']} for id in ['payplus10','payplus15','payplus20']};offset=0
for n in [26,25,25]:
 for j,(id,sex) in enumerate([('payplus10','M'),('payplus15','M'),('payplus10','F'),('payplus15','F'),('payplus20','M'),('payplus20','F')]):r[id][sex]+=v[offset+j*n:offset+(j+1)*n]
 offset+=n*6
for id in r:check(id,r[id])
v=nums(7957,8134);assert len(v)==142;check('pay20',{'M':v[:36]+v[72:107],'F':v[36:72]+v[107:]})
v=nums(8182,8304);assert len(v)==61;check('protection65',{'M':v,'F':v})
v=nums(8355,8480);assert len(v)==51;check('savingsure',{'M':v,'F':v})
v=nums(8550,8593);assert len(v)==42;check('senior',{'M':v[:21],'F':v[21:]})
v=nums(8727,8820);assert len(v)==72;
check('annuityfix',{'M':v[:36],'F':v[36:]})
# Whole numeric table blocks contain age columns. Keep known printed column boundaries.
v=nums(9278,9383,False);assert len(v)==93,(len(v),v[:3]);check('annuitysure9',{'M':v[16:32]+v[63:78],'F':v[32:48]+v[78:93]})
# From the first male annual rate 44 to the final female rate 676 (merged into next page's heading).
a=next(i for i in range(9390,9500) if L[i].strip()=='44');b=next(i for i in range(a,9520) if L[i].startswith('6761 '));v=nums(a+1,b,False)+[676];assert len(v)==90,(len(v),v[:3]);check('annuitysure60',{'M':v[:18]+v[54:72],'F':v[18:36]+v[72:]})
a=next(i for i in range(9500,9590) if L[i].strip()=='870');v=nums(a+1,a+3,False);assert v==[870,880,900];check('5pay10',{'M':v,'F':v})
a=next(i for i in range(9580,9750) if L[i].strip()=='82');v=nums(a+1,a+11,False);assert len(v)==11;check('endowment',{'M':v,'F':v})
(root/'data/benefit-plus-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
assert all(not x['differences'] for x in result), 'Benefit Plus rate mismatch: see data/benefit-plus-audit.json'
print(f"PASS: {len(result)} products, {sum(x['compared'] for x in result)} sex/age-band entries match Benefit Plus")
