(function(root){
'use strict';
const round=n=>Math.round((n+Number.EPSILON)*100)/100;
function paymentTerm(main,age){
 const years=main?.paymentYears??(main?.payUntilAge-age);
 if(!Number.isInteger(years)||years<1)throw Error('ยังไม่มีระยะชำระเบี้ยของแบบหลักที่เลือก');
 return years;
}
function linkedAmount(product,items){
 if(product.id!=='citopup')return undefined;
 const base=items.find(i=>i.p?.id==='ciplus');
 if(!base||!Number.isSafeInteger(base.amount)||base.amount<=0)throw Error('กรุณากรอกทุน CI Plus ก่อน');
 return round(base.amount*2/5);
}
function quote(product,{sex,age,amount,plan,infantConfirmed=false,payerSex,payerAge,main,mainAmount,manualPremium}){
 if(!product)throw Error('ยังไม่มีตารางเบี้ยของแบบที่เลือก');
 if(!['M','F'].includes(sex))throw Error('กรุณาเลือกเพศ');
 if(product.sexOnly&&sex!==product.sexOnly)throw Error(product.name+': รับเฉพาะเพศหญิง');
 if(!Number.isInteger(age)||age<product.minAge||age>product.maxAge)throw Error(`${product.name}: รับอายุ ${product.minAge}–${product.maxAge} ปี`);
 if(age===0&&!infantConfirmed)throw Error('กรุณายืนยันว่ามีอายุจริงอย่างน้อย 15 วัน');
 if(product.quoteMode==='manual'){
  if(!Number.isFinite(manualPremium)||manualPremium<0||manualPremium>10000000||Math.abs(manualPremium*100-Math.round(manualPremium*100))>.000001)throw Error('WP: กรอกเบี้ยรายปีจากใบเสนอขายบริษัท (ทศนิยมไม่เกิน 2 ตำแหน่ง)');
  return {premium:manualPremium,rate:null,discount:0,manual:true,source:product.source};
 }
 if(product.waiverType){
  if(!main)throw Error(product.name+': กรุณาเลือกกรมธรรม์หลัก');
  if(main.includedRiders?.includes(product.id))throw Error(main.name+': รวม '+product.name+' ในแบบแล้ว ไม่ต้องเพิ่มเบี้ยซ้ำ');
  const base=quote(main,{sex,age,amount:mainAmount,infantConfirmed});let years=paymentTerm(main,age),rSex=sex,index;
  if(product.waiverType==='payer'){
   if(!['M','F'].includes(payerSex))throw Error(product.name+': กรุณาเลือกเพศผู้ชำระเบี้ย');
   if(!Number.isInteger(payerAge)||payerAge<product.payerMinAge||payerAge>product.payerMaxAge)throw Error(`${product.name}: อายุผู้ชำระเบี้ย ${product.payerMinAge}–${product.payerMaxAge} ปี`);
   years=Math.min(years,25-age,80-payerAge);rSex=payerSex;index=product.payerBands.findIndex(limit=>payerAge<=limit);
  }else index=[20,25,30,35,40,45,50,55,60,65,70,75].findIndex(limit=>age<=limit);
  const rate=product.waiverRates[rSex]?.[years]?.[index];
  if(!Number.isFinite(rate)||rate<=0)throw Error(`${product.name}: ไม่มีอัตราในเอกสารสำหรับอายุนี้และระยะคุ้มครอง ${years} ปี`);
  return {premium:round(base.premium*rate/product.unit),rate,discount:0,basePremium:base.premium,years,payerAge,payerSex,source:product.source};
 }
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
 return {premium:round(raw),rate,discount,source:product.source};
}
function riderRestriction(main,rider){
 if(!main||rider.category==='main')return '';
 if(['5pay10','senior'].includes(main.id))return main.name+' ไม่สามารถแนบสัญญาเพิ่มเติมได้';
 if(main.id.startsWith('annuity')&&!rider.accidentFamily)return main.name+' แนบได้เฉพาะสัญญาอุบัติเหตุ AI / ADD / ADB และ RCC';
 if(['cisuper10','cisuper20'].includes(main.id)&&!rider.accidentFamily)return main.name+' แนบได้เฉพาะสัญญาอุบัติเหตุ AI / ADD / ADB และ RCC';
 if(['cisuperprestige10','cisuperprestige20'].includes(main.id)&&!rider.accidentFamily&&rider.id!=='ciplus')return main.name+' แนบได้เฉพาะสัญญาอุบัติเหตุและ CI Plus';
 if(main.id==='ciprocare'&&['wp','wpci','pb','pbci'].includes(rider.id))return main.name+' ไม่สามารถแนบ WP / WPCI / PB / PBCI ได้';
 if(main.includedRiders?.includes(rider.id))return main.name+' รวม '+rider.name+' ในแบบแล้ว ไม่ต้องเพิ่มซ้ำ';
 return '';
}
function validateSelection(main,selected,items=[]){
 const topup=selected.find(p=>p.id==='citopup');
 if(topup&&!selected.some(p=>p.id==='ciplus'))throw Error('CI Topup ต้องแนบกับ CI Plus');
 if(topup&&items.length){const top=items.find(i=>i.p.id==='citopup'),base=items.find(i=>i.p.id==='ciplus');if(top.amount*5!==base.amount*2)throw Error('ทุน CI Topup ต้องเท่ากับ 40% ของ CI Plus');}
 const families=selected.filter(p=>p.accidentFamily).map(p=>p.accidentFamily);if(new Set(families).size!==families.length)throw Error('เลือกสัญญาอุบัติเหตุเดียวกันซ้ำทั้งแบบมีและไม่มี RCC กรุณาเลือกแบบเดียว');
 for(const p of selected){const reason=riderRestriction(main,p);if(reason)throw Error(reason);}
 if(main?.includedRiders?.some(id=>selected.some(p=>p.id===id)))throw Error(main.name+': รวม WPCI ในแบบแล้ว ไม่ต้องเพิ่มเบี้ยซ้ำ');

}
const api={quote,validateSelection,linkedAmount,paymentTerm,riderRestriction};if(typeof module!=='undefined')module.exports=api;else root.InsureCalculator=api;
})(globalThis);
