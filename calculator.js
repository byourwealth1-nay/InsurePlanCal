(function(root){
'use strict';
function quote(product,{sex,age,amount,plan,infantConfirmed=false}){
 if(!product)throw Error('ยังไม่มีตารางเบี้ยของแบบที่เลือก');
 if(!['M','F'].includes(sex))throw Error('กรุณาเลือกเพศ');
 if(!Number.isInteger(age)||age<product.minAge||age>product.maxAge)throw Error(`${product.name}: รับอายุ ${product.minAge}–${product.maxAge} ปี`);
 if(age===0&&!infantConfirmed)throw Error('กรุณายืนยันว่ามีอายุจริงอย่างน้อย 15 วัน');
 const index=product.bands.findIndex(limit=>age<=limit);
 if(index<0)throw Error('ไม่มีอัตราสำหรับอายุนี้');
 let rates=product.rates;
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
const api={quote};if(typeof module!=='undefined')module.exports=api;else root.InsureCalculator=api;
})(globalThis);
