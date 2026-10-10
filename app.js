'use strict';
const $=id=>document.getElementById(id),fmt=n=>new Intl.NumberFormat('th-TH',{maximumFractionDigits:2}).format(n);
let products=[],coverage=[],lastSummary='',riderCounter=0;
function option(value,label){const o=document.createElement('option');o.value=value;o.textContent=label;return o;}
function product(id){return products.find(p=>p.id===id);}
function getAmount(input){const raw=input.value.replaceAll(',','').trim();return raw===''?NaN:Number(raw);}
function formatMoneyInput(input){
 const original=input.value,raw=original.replaceAll(',','');
 if(!/^[0-9]*(\.[0-9]*)?$/.test(raw)||raw==='')return;
 const start=input.selectionStart,end=input.selectionEnd;
 const [whole,fraction]=raw.split('.');
 const grouped=whole.replace(/\B(?=(\d{3})+(?!\d))/g,',');
 const formatted=grouped+(fraction===undefined?'':'.'+fraction);
 const position=offset=>{if(offset===null)return null;const count=original.slice(0,offset).replaceAll(',','').length;let seen=0;for(let i=0;i<formatted.length;i++){if(formatted[i]!==',')seen++;if(seen===count)return i+1;}return count===0?0:formatted.length;};
 input.value=formatted;
 if(start!==null&&end!==null)input.setSelectionRange(start===0?0:position(start),end===0?0:position(end));
}
function personLabel(sex,age){const child=Number.isFinite(age)&&age<18;return (sex==='M'?(child?'👦':'👨'):(child?'👧':'👩'))+' '+(sex==='M'?'ชาย':'หญิง')+' · อายุประกัน '+(Number.isFinite(age)?age:'—')+' ปี';}
function copySummary(person,entries,total){
 const section=(title,rows)=>rows.length?['',title,...rows.map(row=>'• '+row.description+'\n  เบี้ย '+fmt(row.premium)+' บาท/ปี')]:[];
 return ['B Your Wealth 1 · ประเมินเบี้ยมาตรฐาน',person,...section('📋 กรมธรรม์หลัก',entries.filter(row=>row.main)),...section('🛡️ สัญญาเพิ่มเติม',entries.filter(row=>!row.main)),'','💰 รวมเบี้ย '+fmt(total)+' บาท/ปี'].join('\n');
}
function addOptions(select,main=false){
 select.replaceChildren();select.append(option('',main?'ไม่เลือกแบบหลัก (คำนวณรายตัว)':'เลือกสัญญาเพิ่มเติม'));
 if(main){products.filter(p=>p.category==='main').forEach(p=>select.append(option(p.id,p.name)));return;}
 const groups=[['สุขภาพ',p=>p.category==='health'],['โรคร้ายแรง',p=>p.category==='rider'&&!p.accidentFamily&&!['hb','hbextra'].includes(p.id)&&!p.waiverType&&p.id!=='wp'],['อุบัติเหตุ',p=>p.accidentFamily],['ชดเชยรายได้',p=>['hb','hbextra'].includes(p.id)],['ยกเว้นเบี้ย',p=>p.waiverType||p.id==='wp']];
 for(const [label,accept] of groups){const group=document.createElement('optgroup');group.label=label;products.filter(accept).forEach(p=>group.append(option(p.id,p.name)));select.append(group);}
}
function hint(p){return p?`อายุรับใหม่ ${p.minAge}–${p.maxAge} ปี${p.unit&&!p.waiverType?` · จำนวนเงินตั้งแต่ ${fmt(p.minAmount)}${p.maxAmount===null?'':` ถึง ${fmt(p.maxAmount)}`} บาท`:''}${p.note?' · '+p.note:''}`:'';}
function riderItems(){return [...document.querySelectorAll('#riders .item')].map(node=>({node,p:product(node.querySelector('.rider-product').value),amount:getAmount(node.querySelector('.rider-amount')),plan:node.querySelector('.rider-plan').value,payerSex:node.querySelector('.payer-sex').value,payerAge:getAmount(node.querySelector('.payer-age'))})).filter(i=>i.p);}
function addRider(id='',initialAmount,initialPlan){
 const node=document.createElement('div');node.className='item';const n=++riderCounter;
 node.innerHTML=`<div class="select-row"><div><label for="rider-${n}">สัญญาเพิ่มเติม</label><select id="rider-${n}" class="rider-product"></select></div><button type="button" class="remove" aria-label="ลบสัญญาเพิ่มเติม">ลบ</button></div><div class="rider-plan-row hide"><label for="rider-plan-${n}">แผน / ขั้นอาชีพ</label><select id="rider-plan-${n}" class="rider-plan"></select></div><div class="amount-row hide"><label for="amount-${n}" class="amount-label">ทุนประกัน (บาท)</label><input id="amount-${n}" class="rider-amount" inputmode="decimal" autocomplete="off"></div><div class="fields payer-row hide"><div><label for="payer-sex-${n}">เพศผู้ชำระเบี้ย</label><select id="payer-sex-${n}" class="payer-sex"><option value="M">ชาย</option><option value="F">หญิง</option></select></div><div><label for="payer-age-${n}">อายุผู้ชำระเบี้ย (ปี)</label><input id="payer-age-${n}" class="payer-age" type="number" min="20" max="70" step="1" inputmode="numeric" placeholder="เช่น 40"></div></div><p class="small rider-hint"></p><p class="small linked-hint"></p><div class="sub"><span>เบี้ยสัญญาเพิ่มเติม / ปี</span><strong class="rider-premium">—</strong></div>`;
 const select=node.querySelector('.rider-product'),input=node.querySelector('.rider-amount');addOptions(select);select.value=id;$('riders').append(node);
 function change(){
  const p=product(select.value),oldAmount=getAmount(input),oldId=node.dataset.product;node.dataset.product=p?.id||'';
  const plans=node.querySelector('.rider-plan');plans.replaceChildren();p?.plans?.forEach(x=>plans.append(option(x.id,x.name)));node.querySelector('.rider-plan-row').classList.toggle('hide',!p?.plans);
  node.querySelector('.amount-row').classList.toggle('hide',!p||(!p.unit&&!p.quoteMode));node.querySelector('.payer-row').classList.toggle('hide',p?.waiverType!=='payer');
  const label=node.querySelector('.amount-label');label.textContent=p?.quoteMode==='manual'?'เบี้ย WP / ปี จากใบเสนอขายบริษัท (บาท)':p?.waiverType?'เบี้ยหลักต่อปี (คำนวณอัตโนมัติ)':p?.id==='citopup'?'ทุน CI Topup = 40% ของ CI Plus (บาท)':['hb','hbextra'].includes(p?.id)?'ค่าชดเชยรายวัน (บาท)':'ทุนประกัน (บาท)';
  input.readOnly=!!p?.waiverType||p?.id==='citopup';input.value=p?.quoteMode==='manual'?'':p?.unit?fmt(['hb','hbextra'].includes(p.id)?1000:Math.max(p.minAmount,100000)):'';
  node.querySelector('.rider-hint').textContent=hint(p);node.querySelector('.linked-hint').textContent='';
  if(p?.id==='citopup'&&!riderItems().some(i=>i.p.id==='ciplus'))addRider('ciplus',oldId==='ciplus'&&Number.isFinite(oldAmount)?oldAmount:100000);
  update();
 }
 select.addEventListener('change',change);for(const control of node.querySelectorAll('input,.rider-plan,.payer-sex'))control.addEventListener('input',()=>{if(control===input)formatMoneyInput(input);update();});
 node.querySelector('button').addEventListener('click',()=>{const base=select.value==='ciplus';node.remove();if(base)riderItems().filter(i=>i.p.id==='citopup').forEach(i=>i.node.remove());update();if(base)$('status').textContent='ลบ CI Plus และ CI Topup ที่แนบอยู่แล้ว';});
 change();if(initialAmount!==undefined)input.value=fmt(initialAmount);if(initialPlan!==undefined)node.querySelector('.rider-plan').value=initialPlan;update();return node;
}
function update(){
 $('status').textContent='';lastSummary='';$('copy').disabled=true;$('summaryRows').replaceChildren();$('sources').replaceChildren();
 const sex=$('sex').value,age=getAmount($('age')),infantConfirmed=$('infant').checked,main=product($('product').value),mainAmount=getAmount($('sum'));
 $('infantRow').classList.toggle('hide',age!==0);$('person').textContent=personLabel(sex,age);$('mainHint').textContent=hint(main);$('sumLabel').textContent=main?.id==='annuityfix'?'ฐานเงินบำนาญ (บาท)':'ทุนประกัน (บาท)';
 const riders=riderItems();let basePremium;
 try{if(main)basePremium=InsureCalculator.quote(main,{sex,age,amount:mainAmount,infantConfirmed}).premium;}catch{}
 for(const i of riders){
  i.node.querySelector('.linked-hint').textContent='';
  if(i.p.id==='citopup'){
   try{i.amount=InsureCalculator.linkedAmount(i.p,riders);i.node.querySelector('.rider-amount').value=fmt(i.amount);i.node.querySelector('.linked-hint').textContent='ปรับตามทุน CI Plus อัตโนมัติ';}
   catch(e){i.amount=NaN;i.node.querySelector('.rider-amount').value='';i.node.querySelector('.linked-hint').textContent=e.message;}
  }
  if(i.p.waiverType){i.node.querySelector('.rider-amount').value=Number.isFinite(basePremium)?fmt(basePremium):'';i.amount=basePremium;}
 }
 const items=main?[{p:main,amount:mainAmount,output:'mainPremium'},...riders]:riders;if(!main)$('mainPremium').textContent='0 บาท';
 const errors=[],lines=[],used=new Set(),ids=new Set();let cents=0;
 if(!Number.isFinite(age))errors.push('กรุณากรอกอายุประกัน');
 if(!items.length)errors.push('กรุณาเลือกอย่างน้อยหนึ่งรายการ');
 for(const item of items){
  let text='—',description=item.p.name;
  if(ids.has(item.p.id))errors.push(item.p.name+': เลือกซ้ำ กรุณารวมทุนในรายการเดียว');ids.add(item.p.id);
  if(item.p.unit&&!item.p.waiverType)description+=' · '+(Number.isFinite(item.amount)?fmt(item.amount):'—')+' บาท';if(item.p.plans)description+=' · '+(item.p.plans.find(p=>p.id===item.plan)?.name||'กรุณาเลือกแผน');
  try{
   const q=InsureCalculator.quote(item.p,{sex,age,infantConfirmed,amount:item.amount,plan:item.plan,payerSex:item.payerSex,payerAge:item.payerAge,main,mainAmount,manualPremium:item.p.quoteMode==='manual'?item.amount:undefined});
   text=fmt(q.premium)+' บาท';cents+=Math.round(q.premium*100);
   if(q.manual)description+=' · เบี้ยตามใบเสนอขายที่กรอก';
   if(q.years){description+=` · คุ้มครอง ${q.years} ปี`;if(item.p.waiverType==='payer')description+=` · ผู้ชำระเบี้ย ${item.payerSex==='M'?'ชาย':'หญิง'} ${item.payerAge} ปี`;item.node.querySelector('.linked-hint').textContent=`ใช้เบี้ยหลัก ${fmt(q.basePremium)} บาท/ปี · ระยะคุ้มครอง ${q.years} ปี`;}
   lines.push({description,premium:q.premium,main:item.p.category==='main'});
  }catch(e){errors.push(e.message);}
  if(item.output)$(item.output).textContent=text;if(item.node)item.node.querySelector('.rider-premium').textContent=text;
  const row=document.createElement('div');row.className='row';const label=document.createElement('div'),price=document.createElement('strong');label.textContent=description;price.textContent=text;row.append(label,price);$('summaryRows').append(row);
  if(!used.has(item.p.source.url)){used.add(item.p.source.url);const a=document.createElement('a');a.textContent=item.p.source.title;a.href=item.p.source.url;a.target='_blank';a.rel='noopener';const para=document.createElement('p');para.append(a);$('sources').append(para);}
 }
 try{InsureCalculator.validateSelection(main,items.map(item=>item.p),items);}catch(e){errors.push(e.message);}
 $('error').classList.toggle('hide',errors.length===0);$('error').textContent=[...new Set(errors)].join(' · ');$('total').textContent=errors.length?'—':fmt(cents/100);
 if(!errors.length){$('copy').disabled=false;lastSummary=copySummary($('person').textContent,lines,cents/100);}
}
function catalog(){const query=$('search').value.trim().toLowerCase();$('catalog').replaceChildren();const shown=coverage.filter(d=>d.title.toLowerCase().includes(query));for(const d of shown){const n=document.createElement('div');n.className='catalog-item';const a=document.createElement('a');a.href=d.url;a.target='_blank';a.rel='noopener';a.textContent=d.title;const status=document.createElement('span');status.textContent=d.status==='used'?'ใช้คำนวณเบี้ยมาตรฐานแล้ว':d.reason;status.className=d.status==='used'?'status-pill':'small';n.append(a,status);$('catalog').append(n);}if(!shown.length)$('catalog').textContent='ไม่พบรายการที่ตรงกับคำค้น';}
async function init(){try{
 const responses=await Promise.all([fetch('data/products.json',{cache:'no-store'}),fetch('data/coverage.json',{cache:'no-store'})]);if(responses.some(r=>!r.ok))throw Error('โหลดข้อมูลไม่สำเร็จ');[products,coverage]=await Promise.all(responses.map(r=>r.json()));
 addOptions($('product'),true);$('product').value='payplus20';
 $('coverageStatus').textContent=`กรมธรรม์หลัก ${products.filter(p=>p.category==='main').length} แบบ/ระยะชำระ · สัญญาเพิ่มเติม PPR ${products.filter(p=>p.category!=='main').length} ตัวเลือก · WP กรอกเบี้ยจากบริษัท`;$('catalogCount').textContent=`(${coverage.length} รายการ)`;
 for(const id of ['sex','age','sum','infant'])$(id).addEventListener('input',()=>{if(id==='sum')formatMoneyInput($(id));update();});$('product').addEventListener('change',()=>{const p=product($('product').value);if(p&&getAmount($('sum'))<p.minAmount)$('sum').value=fmt(p.minAmount);update();});$('addRider').addEventListener('click',()=>addRider());$('search').addEventListener('input',catalog);
 $('reset').addEventListener('click',()=>{$('sex').value='M';$('age').value='';$('infant').checked=false;$('product').value='payplus20';$('sum').value='150,000';$('riders').replaceChildren();update();$('age').focus();});
 $('copy').addEventListener('click',async()=>{if(!lastSummary)return;try{await navigator.clipboard.writeText(lastSummary);$('status').textContent='คัดลอกแล้ว พร้อมวางใน LINE';}catch{const t=document.createElement('textarea');t.value=lastSummary;document.body.append(t);t.select();const copied=document.execCommand('copy');t.remove();$('status').textContent=copied?'คัดลอกแล้ว':'คัดลอกไม่สำเร็จ กรุณาอนุญาตการคัดลอกในเบราว์เซอร์';}});
 addRider('happy',undefined,'1');catalog();update();
 }catch(e){$('coverageStatus').textContent='โหลดตารางไม่สำเร็จ กรุณาลองรีเฟรช';$('error').textContent=e.message;$('error').classList.remove('hide');}}
init();
