'use strict';
const $=id=>document.getElementById(id),fmt=n=>new Intl.NumberFormat('th-TH',{maximumFractionDigits:2}).format(n);
let products=[],coverage=[],lastSummary='',riderCounter=0;
function option(value,label){const o=document.createElement('option');o.value=value;o.textContent=label;return o;}
function product(id){return products.find(p=>p.id===id);}
function addOptions(select,category,none){select.replaceChildren();if(none)select.append(option('',none));products.filter(p=>p.category===category).forEach(p=>select.append(option(p.id,p.name)));}
function hint(p){return p?`อายุรับใหม่ ${p.minAge}–${p.maxAge} ปี${p.unit?` · จำนวนเงินตั้งแต่ ${fmt(p.minAmount)}${p.maxAmount===null?'':` ถึง ${fmt(p.maxAmount)}`} บาท`:''}${p.note?' · '+p.note:''}`:'';}
function healthPlans(){const p=product($('health').value);$('plan').replaceChildren();p?.plans.forEach(x=>$('plan').append(option(x.id,x.name)));$('healthPlanRow').classList.toggle('hide',!p);$('healthHint').textContent=hint(p);}
function addRider(){
 const node=document.createElement('div');node.className='item';const n=++riderCounter;
 node.innerHTML=`<div class="select-row"><div><label for="rider-${n}">สัญญาเพิ่มเติม</label><select id="rider-${n}" class="rider-product"></select></div><button type="button" class="remove" aria-label="ลบสัญญาเพิ่มเติม">ลบ</button></div><label for="amount-${n}" style="margin-top:14px" class="amount-label">ทุนประกัน (บาท)</label><input id="amount-${n}" class="rider-amount" inputmode="numeric" value="100,000"><p class="small rider-hint"></p>`;
 const select=node.querySelector('select');addOptions(select,'rider');
 function change(){const p=product(select.value);node.querySelector('.rider-hint').textContent=hint(p);node.querySelector('.amount-label').textContent=p.id==='hbextra'?'ค่าชดเชยรายวัน (บาท)':'ทุนประกัน (บาท)';node.querySelector('input').value=fmt(p.id==='hbextra'?1000:100000);update();}
 select.addEventListener('change',change);node.querySelector('input').addEventListener('input',update);node.querySelector('button').addEventListener('click',()=>{node.remove();update();});$('riders').append(node);change();
}
function getAmount(input){const raw=input.value.replaceAll(',','').trim();return raw===''?NaN:Number(raw);}
function update(){
 $('status').textContent='';lastSummary='';$('copy').disabled=true;$('summaryRows').replaceChildren();$('sources').replaceChildren();
 const sex=$('sex').value,age=$('age').value.trim()===''?NaN:Number($('age').value),infantConfirmed=$('infant').checked;
 $('infantRow').classList.toggle('hide',age!==0);$('person').textContent=(sex==='M'?'ชาย':'หญิง')+' · อายุประกัน '+(Number.isFinite(age)?age:'—')+' ปี';
 const main=product($('product').value);$('mainHint').textContent=hint(main);$('sumLabel').textContent=main?.id==='annuityfix'?'ฐานเงินบำนาญ (บาท)':'ทุนประกัน (บาท)';
 const items=[];if(main)items.push({p:main,amount:getAmount($('sum')),output:'mainPremium'});else $('mainPremium').textContent='0 บาท';
 const health=product($('health').value);if(health)items.push({p:health,plan:$('plan').value,output:'healthPremium'});else $('healthPremium').textContent='0 บาท';
 document.querySelectorAll('#riders .item').forEach(n=>items.push({p:product(n.querySelector('select').value),amount:getAmount(n.querySelector('input'))}));
 const errors=[],lines=[],used=new Set();let cents=0;
 if(!items.length)errors.push('กรุณาเลือกอย่างน้อยหนึ่งรายการ');
 const ids=new Set();
 for(const item of items){
  let text='—',description=item.p?.name||'รายการไม่ถูกต้อง';
  if(ids.has(item.p.id))errors.push(item.p.name+': เลือกซ้ำ กรุณารวมทุนในรายการเดียว');ids.add(item.p.id);
  if(item.p.unit)description+=' · '+fmt(item.amount)+' บาท';else description+=' · '+item.p.plans.find(p=>p.id===item.plan)?.name;
  try{const q=InsureCalculator.quote(item.p,{sex,age,infantConfirmed,amount:item.amount,plan:item.plan});text=fmt(q.premium)+' บาท';cents+=Math.round(q.premium*100);lines.push(description+' · '+text+'/ปี');}catch(e){errors.push(e.message);}
  if(item.output)$(item.output).textContent=text;
  const row=document.createElement('div');row.className='row';const label=document.createElement('div'),price=document.createElement('strong');label.textContent=description;price.textContent=text;row.append(label,price);$('summaryRows').append(row);
  if(!used.has(item.p.source.url)){used.add(item.p.source.url);const a=document.createElement('a');a.textContent=item.p.source.title;a.href=item.p.source.url;a.target='_blank';a.rel='noopener';const para=document.createElement('p');para.append(a);$('sources').append(para);}
 }
 if(main&&(main.id.startsWith('annuity')||main.id==='senior')&&(health||items.some(i=>i.p.category==='rider')))errors.push(main.name+': การแนบรายการที่เลือกยังไม่รองรับ กรุณาคำนวณรายตัวโดยเลือก “ไม่เลือกแบบหลัก”');
 $('error').classList.toggle('hide',errors.length===0);$('error').textContent=[...new Set(errors)].join(' · ');$('total').textContent=errors.length?'—':fmt(cents/100);
 if(!errors.length){$('copy').disabled=false;lastSummary=['InsurePlanCal · ประเมินเบี้ยมาตรฐาน',$('person').textContent,...lines,'รวมรายการที่เลือก '+fmt(cents/100)+' บาท/ปี','ยังไม่ยืนยันการแนบสัญญาร่วมกัน / อัตราปัจจุบัน · ไม่รวม Vitality และเบี้ยเพิ่ม','แหล่งข้อมูล:',...[...used]].join('\n');}
}
function catalog(){const query=$('search').value.trim().toLowerCase();$('catalog').replaceChildren();const shown=coverage.filter(d=>d.title.toLowerCase().includes(query));for(const d of shown){const n=document.createElement('div');n.className='catalog-item';const a=document.createElement('a');a.href=d.url;a.target='_blank';a.rel='noopener';a.textContent=d.title;const status=document.createElement('span');status.textContent=d.status==='used'?'ใช้ตารางบางส่วนคำนวณแล้ว':d.reason;status.className=d.status==='used'?'status-pill':'small';n.append(a,status);$('catalog').append(n);}if(!shown.length)$('catalog').textContent='ไม่พบเอกสารที่ตรงกับคำค้น';}
async function init(){try{const responses=await Promise.all([fetch('data/products.json'),fetch('data/coverage.json')]);if(responses.some(r=>!r.ok))throw Error('โหลดข้อมูลไม่สำเร็จ');[products,coverage]=await Promise.all(responses.map(r=>r.json()));
 addOptions($('product'),'main','ไม่เลือกแบบหลัก (คำนวณรายตัว)');addOptions($('health'),'health','ไม่เพิ่มสุขภาพ');$('product').value='payplus20';$('health').value='happy';healthPlans();$('plan').value='1';
 $('coverageStatus').textContent=`เลือกคำนวณได้ ${products.length} แบบ / ระยะชำระ · ตารางที่ยังไม่พร้อมดูได้ในสถานะข้อมูล`;$('catalogCount').textContent=`(${coverage.length} เอกสาร)`;
 for(const id of ['sex','age','sum','plan','infant'])$(id).addEventListener('input',update);$('product').addEventListener('change',()=>{const p=product($('product').value);if(p&&getAmount($('sum'))<p.minAmount)$('sum').value=fmt(p.minAmount);update();});$('health').addEventListener('change',()=>{healthPlans();update();});$('addRider').addEventListener('click',addRider);$('search').addEventListener('input',catalog);
 $('reset').addEventListener('click',()=>{$('sex').value='M';$('age').value='';$('infant').checked=false;$('product').value='payplus20';$('sum').value='150,000';$('health').value='';$('riders').replaceChildren();healthPlans();update();$('age').focus();});
 $('copy').addEventListener('click',async()=>{if(!lastSummary)return;try{await navigator.clipboard.writeText(lastSummary);$('status').textContent='คัดลอกแล้ว พร้อมวางใน LINE';}catch{const t=document.createElement('textarea');t.value=lastSummary;document.body.append(t);t.select();const copied=document.execCommand('copy');t.remove();$('status').textContent=copied?'คัดลอกแล้ว':'คัดลอกไม่สำเร็จ กรุณาอนุญาตการคัดลอกในเบราว์เซอร์';}});
 catalog();update();
 }catch(e){$('coverageStatus').textContent='โหลดตารางไม่สำเร็จ กรุณาลองรีเฟรช';$('error').textContent=e.message;$('error').classList.remove('hide');}}
init();
