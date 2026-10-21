'use strict';
const assert=require('node:assert/strict');
const {quote}=require('../calculator');
const products=require('../data/products.json');
const source=require('./source-rate-fixtures.json');
const round=n=>Math.round((n+Number.EPSILON)*100)/100;
assert.deepEqual(Object.keys(source).sort(),products.map(p=>p.id).sort());
let sourceCells=0,quoteChecks=0,waiverChecks=0,discountChecks=0;
for(const p of products){
 const e=source[p.id];
 assert.equal(p.unit,e.unit,p.id+' unit');assert.deepEqual(p.discounts,e.discounts,p.id+' discounts');
 if(e.manual){assert.equal(p.quoteMode,'manual');assert.throws(()=>quote(p,{sex:'M',age:35}));continue;}
 const tables=[];
 if(Object.keys(e.rates).length)tables.push({actual:p.rates,expected:e.rates});
 for(const [id,rates] of Object.entries(e.plans))tables.push({plan:id,actual:p.plans.find(plan=>plan.id===id).rates,expected:rates});
 for(const [amount,rates] of Object.entries(e.tiers))tables.push({amount:Number(amount),actual:p.amountTiers.find(tier=>tier.minAmount===Number(amount)).rates,expected:rates});
 for(const table of tables)for(const [sex,rates] of Object.entries(table.expected)){
  assert.deepEqual(table.actual[sex],rates,p.id+' '+sex+' '+(table.plan||table.amount||''));sourceCells+=rates.length;
  for(let index=0;index<rates.length;index++){
   const low=index===0?p.minAge:p.bands[index-1]+1,high=Math.min(p.bands[index],p.maxAge);
   for(let age=low;age<=high;age++){
    const amount=table.amount||p.minAmount;
    const discount=e.discounts.find(([threshold])=>amount>=threshold)?.[1]||0;
    const premium=round(p.unit?(rates[index]-discount)*amount/e.unit:rates[index]);
    assert.equal(quote(p,{sex,age,amount,plan:table.plan,infantConfirmed:true}).premium,premium,p.id+' '+age+' '+sex);quoteChecks++;
   }
  }
 }
 if(e.waiverRates){
  assert.deepEqual(p.waiverRates,e.waiverRates,p.id+' printed waiver matrix');
  for(const [sex,terms] of Object.entries(e.waiverRates))for(const [term,rates] of Object.entries(terms))for(let index=0;index<rates.length;index++){
   sourceCells++;
   if(rates[index]===null)continue;
   const payer=p.waiverType==='payer';
   const age=payer?0:[20,25,30,35,40,45,50,55,60,65,70,75][index];
   const main={...products.find(p=>p.id==='pay10'),minAge:0,maxAge:75,paymentYears:Number(term),bands:[75],rates:{M:[20],F:[20]},discounts:[]};
   const q=quote(p,{sex,age,payerSex:sex,payerAge:payer?p.payerBands[index]:undefined,main,mainAmount:300000,infantConfirmed:true});
   assert.equal(q.rate,rates[index]);assert.equal(q.premium,round(6000*rates[index]/e.unit));waiverChecks++;
  }
 }
 // Exercise both sides of every printed discount bracket, for both sexes.
 if(p.unit&&!p.waiverType){
  for(const [threshold] of e.discounts)for(const amount of [threshold-1,threshold,threshold+1])for(const sex of p.sexOnly?[p.sexOnly]:['M','F']){
   if(amount<p.minAmount||(p.maxAmount!==null&&amount>p.maxAmount)||amount%p.step)continue;
   const age=Math.min(Math.max(35,p.minAge),p.maxAge),index=p.bands.findIndex(limit=>age<=limit);
   const expectedRate=e.rates[sex][index],discount=e.discounts.find(([minimum])=>amount>=minimum)?.[1]||0;
   const actual=quote(p,{sex,age,amount,infantConfirmed:true});assert.equal(actual.discount,discount);assert.equal(actual.premium,round((expectedRate-discount)*amount/e.unit));discountChecks++;
  }
 }
}
assert.equal(sourceCells,10108);assert.equal(waiverChecks,2624);
console.log(`PASS: all 63 options; ${sourceCells} source cells, ${quoteChecks} source-based age/sex/plan quotes, ${waiverChecks} waiver formulas, ${discountChecks} discount-boundary checks; WP explicitly manual`);
