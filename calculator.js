(function(root){
'use strict';
function quote(product,{sex,age,amount,plan,infantConfirmed=false}){
 if(!product)throw Error('ยังไม่มีตารางเบี้ยของแบบที่เลือก');
 if(!['M','F'].includes(sex))throw Error('กรุณาเลือกเพศ');
 if(product.sexOnly&&sex!==product.sexOnly)throw Error(product.name+': รับเฉพาะเพศหญิง');
 if(!Number.isInteger(age)||age<product.minAge||age>product.maxAge)throw Error(`${product.name}: รับอายุ ${product.minAge}–${product.maxAge} ปี`);
 if(age===0&&!infantConfirmed)throw Error('กรุณายืนยันว่ามีอายุจริงอย่างน้อย 15 วัน');
 const index=product.bands.findIndex(limit=>age<=limit);
 if(index<0)throw Error('ไม่มีอัตราสำหรับอายุนี้');
 let rates=product.rates;
 if(product.amountTiers){const tier=product.amountTiers.find(t=>amount>=t.minAmount);if(tier)rates=tier.rates;}
 if(product.plans){const selected=product.plans.find(p=>p.id===plan);if(!selected)throw Error('กรุณาเลือกแผนความคุ้มครอง');rates=selected.rates;}
 const rate=rates?.[sex]?.[index];
 if(!Number.isFinite(rate)||rate<=0)throw Error('ตารางอัตราไม่ครบ ยังไม่สามารถคำนวณได้');
 let discount=0,raw=rate;
 if(product.unit){
  if(!Number.isSafeInteger(amount)||amount<product.minAmount||(product.maxAmount!==null&&amount>product.maxAmount)||amount%product.step!==0)throw Error(`${product.name}: จำนวนเงินต้องเป็นจำนวนเต็ม ตั้งแต่ ${product.minAmount.toLocaleString('th-TH')}${product.maxAmount===null?'':` ถึง ${product.maxAmount.toLocaleString('th-TH')}`} บาท${product.step>1?` และเป็นหน่วยละ ${product.step.toLocaleString('th-TH')} บาท`:''}`);
  discount=product.discounts.find(([threshold])=>amount>=threshold)?.[1]||0;
  raw=(rate-discount)*amount/product.unit;
 }
 if(!Number.isFinite(raw)||raw<=0)throw Error('ไม่สามารถคำนวณเบี้ยได้');
 return {premium:Math.round((raw+Number.EPSILON)*100)/100,rate,discount,source:product.source};
}
function validateSelection(main,selected,items=[]){
 const topup=selected.find(p=>p.id==='citopup');
 if(topup&&!selected.some(p=>p.id==='ciplus'))throw Error('CI Topup ต้องแนบกับ CI Plus');
 if(topup&&items.length){const top=items.find(i=>i.p.id==='citopup'),base=items.find(i=>i.p.id==='ciplus');if(top.amount*5!==base.amount*2)throw Error('ทุน CI Topup ต้องเท่ากับ 40% ของ CI Plus');}
 const families=selected.filter(p=>p.accidentFamily).map(p=>p.accidentFamily);if(new Set(families).size!==families.length)throw Error('เลือกสัญญาอุบัติเหตุเดียวกันซ้ำทั้งแบบมีและไม่มี RCC กรุณาเลือกแบบเดียว');
 if(main?.id==='5pay10'&&selected.some(p=>p.category==='health'||p.category==='rider'))throw Error('5 Pay 10 ไม่สามารถแนบสัญญาเพิ่มเติมได้ กรุณาแยกคำนวณแต่ละรายการ');
}
const api={quote,validateSelection};if(typeof module!=='undefined')module.exports=api;else root.InsureCalculator=api;
})(globalThis);
