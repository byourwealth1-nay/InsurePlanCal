const assert=require('node:assert/strict');
const {quote,validateSelection}=require('../calculator');
const products=require('../data/products.json');
const old=require('../data/legacy-rates.json');
const byId=id=>products.find(p=>p.id===id);
const q=(id,sex,age,amount,plan)=>quote(byId(id),{sex,age,amount,plan,infantConfirmed:true}).premium;
// Fixed examples from brochures / original quote. These check column order and unit conversions.
assert.equal(q('payplus20','M',57,150000),8118);
assert.equal(q('happy','M',57,undefined,'1'),42300);
assert.equal(q('happy','F',57,undefined,'1'),42500);
assert.equal(q('pay10','M',35,1000000),43950);
assert.equal(q('pay15','M',35,1000000),31290);
assert.equal(q('pay15','M',45,5000000),207000);
assert.equal(q('annuityfix','M',35,1920000),64128);
assert.equal(q('annuitysure60','M',40,1700000),209100);
assert.equal(q('protection65','M',35,400000),42000);
assert.equal(q('savingsure','F',35,400000),101508);
assert.equal(q('endowment','M',35,1000000),80500);
assert.equal(q('5pay10','F',40,20000),17400);
assert.equal(q('5pay10','F',41,20000),17600);
assert.equal(q('hbextra','M',35,1000),2100);
assert.equal(q('hbextra','M',36,1000),2300);
assert.equal(q('cancer','M',57,1000000),18693.6);
assert.equal(q('tpd','F',60,1000000),910);
assert.equal(q('saver','M',11,undefined,'0'),10100);
assert.equal(q('saver','F',11,undefined,'0'),8500);
assert.equal(q('saver','F',11,undefined,'1'),10500);
assert.equal(q('starterbegin','M',0,undefined,'0'),32700);
assert.equal(q('starterbalanced','M',11,undefined,'0'),9400);
assert.equal(q('herobegin','M',0,undefined,'0'),14700);
assert.equal(q('herobalanced','F',0,undefined,'2'),19200);
assert.equal(q('infinite','M',18,undefined,'2-0'),71640);
assert.equal(q('infinite','F',18,undefined,'2-1'),47940);
for(const sex of ['M','F'])assert.deepEqual(byId('payplus20').rates[sex],old['pay'+sex]);
let checks=0;
// Every accepted new-business age and sex/plan must have a valid quote; reject adjacent ages.
for(const p of products){
 if(p.waiverType||p.quoteMode)continue;
 for(const sex of p.sexOnly?[p.sexOnly]:['M','F'])for(let age=p.minAge;age<=p.maxAge;age++)for(const plan of p.plans||[{id:undefined}]){
  const premium=q(p.id,sex,age,p.minAmount,plan.id);assert.ok(Number.isFinite(premium)&&premium>0);checks++;
 }
 for(const age of [p.minAge-1,p.maxAge+1,NaN,57.5])assert.throws(()=>quote(p,{sex:'M',age,amount:p.minAmount,plan:p.plans?.[0].id,infantConfirmed:true}));
 assert.throws(()=>quote(p,{sex:'X',age:p.minAge,amount:p.minAmount,plan:p.plans?.[0].id,infantConfirmed:true}));
 if(p.unit)for(const amount of [NaN,-1,p.minAmount-1,100000.5,Infinity])assert.throws(()=>quote(p,{sex:'M',age:p.minAge,amount,infantConfirmed:true}));
 if(p.plans)assert.throws(()=>quote(p,{sex:'M',age:p.minAge,plan:'missing',infantConfirmed:true}));
}
assert.throws(()=>quote(byId('payplus20'),{sex:'M',age:0,amount:150000}));
assert.throws(()=>q('cancer','M',57,150000));
assert.throws(()=>q('5pay10','M',40,1000001));
for(const sum of [499999,500000,699999,700000])assert.equal(quote(byId('payplus20'),{sex:'M',age:57,amount:sum}).discount,sum>=700000?1.5:sum>=500000?1:0);
console.log(`PASS: ${checks} age/sex/plan combinations, brochure examples, units, thresholds, and rejected inputs`);

// Benefit Plus p46 explicitly prohibits riders on 5 Pay 10.
assert.throws(()=>validateSelection(byId('5pay10'),[byId('5pay10'),byId('happy')]));
assert.throws(()=>validateSelection(byId('5pay10'),[byId('5pay10'),byId('tpd')]));
assert.doesNotThrow(()=>validateSelection(byId('5pay10'),[byId('5pay10')]));
assert.doesNotThrow(()=>validateSelection(null,[byId('happy')]));
assert.doesNotThrow(()=>validateSelection(byId('payplus20'),[byId('payplus20'),byId('happy')]));
console.log('PASS: Benefit Plus 5 Pay 10 rider restrictions');

assert.equal(q('happykids','M',5,undefined,'10000-15'),104700);
assert.equal(q('happykids','F',5,undefined,'10000-15'),88500);
assert.equal(q('happykids','M',6,undefined,'30000-15'),40500);
assert.equal(q('happykids','F',6,undefined,'30000-15'),29700);
assert.equal(q('term20','M',20,350000),1596);
assert.equal(q('excellent','M',35,250000),37975);
assert.equal(q('legacy10','M',0,20000000),399600);
assert.equal(q('legacy10','M',0,19999999),420599.98);
assert.equal(q('ciprocare','M',0,200000),7104);
assert.equal(q('cisuperprestige10','M',0,5000000),179450);
assert.equal(q('ai','M',40,100000,'4'),900);
assert.equal(q('aircc','M',40,100000,'4'),1025);
assert.equal(q('adb','F',40,100000,'2'),150);
assert.equal(q('citopup','M',35,40000),66);
assert.equal(q('hs','M',11,undefined,'1000'),4030);
assert.equal(q('hsextra','M',11,undefined,'1500'),7370);
assert.equal(q('hb','M',16,1000,'4'),2250);
assert.throws(()=>q('ladycare','M',20,100000));
assert.throws(()=>validateSelection(null,[byId('citopup')]));
assert.throws(()=>validateSelection(null,[byId('ciplus'),byId('citopup')],[{p:byId('ciplus'),amount:100000},{p:byId('citopup'),amount:39000}]));
assert.doesNotThrow(()=>validateSelection(null,[byId('ciplus'),byId('citopup')],[{p:byId('ciplus'),amount:100000},{p:byId('citopup'),amount:40000}]));
assert.throws(()=>validateSelection(null,[byId('ai'),byId('aircc')]));
console.log('PASS: additional main/PPR source examples and dependency restrictions');

const {linkedAmount,paymentTerm}=require('../calculator');
const main=byId('pay10');
function w(id,sex,age,payerSex,payerAge,base=main,mainAmount=300000){return quote(byId(id),{sex,age,payerSex,payerAge,main:base,mainAmount,infantConfirmed:true});}
assert.equal(w('pb','M',0,'M',30).rate,3.08);
assert.equal(w('pb','M',0,'M',30).premium,204.57);
assert.equal(w('pb','M',0,'F',30).rate,.88);
assert.equal(w('pb','M',0,'F',30).premium,58.45);
assert.equal(w('pbci','M',0,'M',30).rate,3.03);
assert.equal(w('pbci','F',15,'M',30).years,10);
assert.equal(w('pbci','F',0,'M',70,{...main,paymentYears:20}).years,10);
assert.equal(w('wpci','M',35,undefined,undefined).rate,11.9);
assert.throws(()=>w('wpci','M',35,undefined,undefined,byId('payplus20'),150000));
assert.throws(()=>w('wpci','M',35,undefined,undefined,{...main,paymentYears:9}));
assert.throws(()=>w('pb','M',0,'M',19));
assert.throws(()=>w('pb','M',16,'M',30));
assert.throws(()=>w('pbci','M',0,'M',71));
assert.throws(()=>w('pb','M',0,'M',50,{...main,paymentYears:20}));
assert.throws(()=>quote(byId('pb'),{sex:'M',age:0,payerSex:'M',payerAge:30,infantConfirmed:true}));
assert.equal(paymentTerm(byId('excellent'),35),20);
assert.equal(paymentTerm(byId('protector80'),57),23);
assert.equal(quote(byId('wp'),{sex:'M',age:35,manualPremium:0}).premium,0);
assert.equal(quote(byId('wp'),{sex:'F',age:35,manualPremium:99.12}).premium,99.12);
for(const manualPremium of [undefined,NaN,-1,Infinity,1.001])assert.throws(()=>quote(byId('wp'),{sex:'M',age:35,manualPremium}));
assert.equal(q('healthcancer','M',57,undefined,'standard'),11167);
assert.equal(q('healthcancer','F',67,undefined,'nonsmoker'),17500);
assert.equal(q('healthcancer','M',35,undefined,'nonsmoker'),1314);
for(const amount of [100000,250000,500000])assert.equal(linkedAmount(byId('citopup'),[{p:byId('ciplus'),amount}]),amount*.4);
assert.throws(()=>linkedAmount(byId('citopup'),[]));
assert.throws(()=>linkedAmount(byId('citopup'),[{p:byId('ciplus'),amount:NaN}]));
let waiverChecks=0;
for(const p of products.filter(p=>p.waiverType))for(const sex of ['M','F'])for(const [term,rates] of Object.entries(p.waiverRates[sex]))for(let i=0;i<rates.length;i++){
 if(rates[i]===null)continue;
 const payerAge=p.waiverType==='payer'?p.payerBands[i]:undefined;
 const age=p.waiverType==='payer'?0:[20,25,30,35,40,45,50,55,60,65,70,75][i];
 const q=w(p.id,sex,age,sex,payerAge,{...main,paymentYears:Number(term),maxAge:75,bands:[75],rates:{M:[22.14],F:[17.71]}});
 assert.equal(q.rate,rates[i]);assert.equal(q.years,Number(term));assert.ok(Number.isFinite(q.premium));waiverChecks++;
}
console.log(`PASS: ${waiverChecks} printed waiver rate cells, payer/insured separation, linked CI capital, manual WP and missing-rate rejection`);
