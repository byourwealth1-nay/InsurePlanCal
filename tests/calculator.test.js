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
 for(const sex of ['M','F'])for(let age=p.minAge;age<=p.maxAge;age++)for(const plan of p.plans||[{id:undefined}]){
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
