// Synthetic metric rehearsal, not customer validation. No network, mail or LLM.
import { performance } from 'node:perf_hooks';
import { mkdirSync,writeFileSync } from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import { emptyState } from '../lib/domain/model.ts';import { command } from '../lib/domain/commands.ts';
import { contentHash,snapshot,exportSnapshot,qa } from '../lib/domain/workflow.ts';
import { metrics } from '../lib/domain/metrics.ts';import { renderPdf } from '../lib/domain/pdf.ts';import { renderHtml,renderText,renderEml } from '../lib/domain/exports.ts';
const directory=process.argv[2]??'qa-output/pilot';mkdirSync(directory,{recursive:true});
const started=performance.now(),base=Date.now(),state=emptyState(),rows=[];let clock=base,blocked=0;
const run=input=>command(state,{...input,expected_revision:state.revision},'synthetic-pilot-runner',clock);
run({action:'client',name:'Kuvitteellinen Pilotin Rakentajat Oy',delivery_email:'pilot@example.invalid'});const client=state.clients[0];
run({action:'profile',client_id:client.id,services:['Saneeraus'],regions:['Uusimaa'],facts:[]});
// Independent declared fixture outcomes, never derived from a model or the current assessment text.
const cases=[{title:'Saneeraus, Uusimaa',label:'USEFUL',reason:'Synteettinen positiivinen tapaus: vahvistettu palvelu ja alue.'},{title:'Saneeraus, muu alue',label:'NOT_USEFUL',reason:'Synteettinen negatiivinen kontrolli: toiminta-alue ei täsmää.'},{title:'Saneeraus, sijainti avoin',label:'UNKNOWN',reason:'Synteettinen epäselvä tapaus: toteutusalue puuttuu.'}];
function exported(d,format,body){const s=exportSnapshot(state,d,clock),reference=`${d.approved_hash}.${format}`;writeFileSync(path.join(directory,`day-${rows.length+1}-${d.approved_hash.slice(0,8)}.${format}`),body);if(!state.events.some(e=>e.digest_id===d.id&&e.reference===reference)){state.events.push({id:reference,digest_id:d.id,content_hash:d.approved_hash,type:'EXPORTED',snapshot:s,actor:'synthetic-pilot-runner',occurred_at:new Date(clock).toISOString(),reference});}d.status='EXPORTED';}
for(let day=0;day<30;day++){
 clock=base+day*86400000;const tick=performance.now(),ids=[];
 for(let j=0;j<cases.length;j++){
  const f=cases[j];run({action:'notice',notice_id:String(900000+day*10+j),title:`SIMULAATIO ${day+1}: ${f.title}`,buyer:'Kuvitteellinen ostaja',source_url:`https://example.invalid/pilot/${day}/${j}`,deadline:new Date(clock+5*86400000).toISOString(),checked_at:new Date(clock-1000).toISOString(),cancelled:false,evidence:f.reason,missing:j===2?['Toteutusalue puuttuu']:[]});
  const notice=state.notices.at(-1);run({action:'review',client_id:client.id,notice_version_id:notice.id,summary:f.reason,next_action:j===2?'Tarkista sijainti':'Sisäisen mittaritestin kontrolli',missing:j===2?['Sijainti tarkistettava']:[],coverage:j===2?'PARTIAL':'COMPLETE'});ids.push(state.assessments.at(-1).id);
 }
 run({action:'compose',client_id:client.id,assessment_ids:ids});const d=state.digests.at(-1);
 assert.throws(()=>exportSnapshot(state,d,clock));blocked++;
 assert.deepEqual(qa(state,d,clock),[]);run({action:'approve',digest_id:d.id,expected_hash:contentHash(snapshot(state,d))});
 exported(d,'txt',renderText(exportSnapshot(state,d,clock)));
 const injected=[9,19].includes(day);
 if(injected){
  run({action:'correction',digest_id:d.id,content_hash:d.approved_hash,category:'CONTENT',reason:`Tarkoituksella lisätty korjausskenaario ${day+1}`});
  const a=state.assessments.find(a=>a.id===ids[0]);run({action:'review',client_id:client.id,notice_version_id:a.notice_version_id,summary:a.summary+' Korjausskenaario käsitelty.',next_action:a.next_action,missing:[],coverage:'COMPLETE'});
  assert.equal(d.status,'NEEDS_REVIEW');assert.throws(()=>exportSnapshot(state,d,clock));blocked++;
  run({action:'approve',digest_id:d.id,expected_hash:contentHash(snapshot(state,d))});
 }
 const s=exportSnapshot(state,d,clock);
 for(const [format,body] of [['pdf',renderPdf(s)],['html',renderHtml(s)],['txt',renderText(s)],['eml',renderEml(s,d.approved_hash)],['json',JSON.stringify(s,null,2)]])exported(d,format,body);
 for(let j=0;j<cases.length;j++)run({action:'feedback',source:'INTERNAL_SIMULATION',digest_id:d.id,content_hash:d.approved_hash,assessment_id:ids[j],label:cases[j].label,reason:cases[j].reason});
 rows.push({day:day+1,automated_ms:performance.now()-tick,injected_corrections:injected?1:0,final_items:s.items.length});
}
const m=metrics(state),times=rows.map(r=>r.automated_ms).sort((a,b)=>a-b);
assert.equal(m.delivery_count,30);assert.equal(m.correction_events,2);assert.equal(m.internal_feedback.final_items,90);assert.equal(m.internal_feedback.useful,30);assert.equal(m.internal_feedback.not_useful,30);assert.equal(m.internal_feedback.unknown,30);assert.equal(m.active_delivery_seconds,null);assert.equal(m.customer_usefulness.precision,null);
const report={mode:'SIMULATION',run_at:new Date(base).toISOString(),days_simulated:30,actual_elapsed_ms:performance.now()-started,automated_median_ms:(times[14]+times[15])/2,automated_p95_ms:times[Math.ceil(.95*times.length)-1],blocked_export_checks:blocked,metrics:m,rows,limitations:['No live API, LLM, external sending or real customer','Automation wall time is not human delivery time','Two correction scenarios intentionally injected; not observed production defect rate','Internal labels predeclared synthetic fixture outcomes; not real precision or customer usefulness']};
writeFileSync(path.join(directory,'report.json'),JSON.stringify(report,null,2));
const markdown=`# Sisäisen mittaripilotin tulos\n\nAjo: ${report.run_at}. **30 toimituksen synteettinen simulaatio**, ei toteutunut 30 päivän asiakaspilotti.\n\n| Mittari | Toteutunut tulos | Tulkinta |\n|---|---:|---|\n| Toimituksia | ${m.delivery_count} | Kuvitteellinen asiakas |\n| Lopullisia nostoja | ${m.internal_feedback.final_items} | Synteettiset kontrollit |\n| Automaation ajoaika yhteensä | ${report.actual_elapsed_ms.toFixed(2)} ms | Mitattu koneaika, ei ihmistyötä |\n| Automaation mediaani / toimitus | ${report.automated_median_ms.toFixed(2)} ms | Domain, QA ja tiedostoviennit paikallisesti |\n| Automaation p95 / toimitus | ${report.automated_p95_ms.toFixed(2)} ms | Ei API-/selainviivettä |\n| Estettyjä vientiyrityksiä | ${blocked} | 30 ennen hyväksyntää + 2 mitätöinnin jälkeen |\n| Korjaustapahtumia | ${m.correction_events} | Kaksi tarkoituksella lisättyä testiskenaariota |\n| Korjattuja toimituksia | ${m.corrected_deliveries}/30 | Ei arvio oikeasta virheosuudesta |\n| Sisäinen hyötyarvio | 30 kyllä / 30 ei / 30 epäselvää | Ennalta määritetyt kontrollit |\n| Aktiivinen ihmistyöaika | Ei mitattu | Alle 10 min / asiakas / päivä tavoite avoin |\n| Asiakkaan kokema hyöty | Ei mitattu | Edellyttää oikeaa palautetta |\n\n## Havainto ja korjaus\n\nMonipäiväistä simulaatiota valmisteltaessa havaittiin, että hyväksynnän mitätöinti käytti seinäkelloa, vaikka muu työnkulku käytti testin lukittua aikaa. Yhtenäistin kellon välityksen ja lisäsin regressiotestin. Tämä on yksi toteutuksesta löydetty ja korjattu mittaustestauksen virhe; se on erillinen kahdesta tarkoituksella lisätystä korjausskenaariosta.\n\n## Oikean pilotin hyväksyntä\n\n1. Nimetty ja suostunut pilottiasiakas, vahvistettu profiili ja tuotantotallennus.\n2. Ajasta aktiivinen päivittäinen työ, tauota odotusajat; onboarding erikseen.\n3. Kirjaa korjaukset syineen ja toimitusversioineen. Tavoite: 0 kriittistä asiakasvirhettä.\n4. Asiakas arvioi jokaisen oikeasti toimitetun noston: hyödyllinen / ei hyödyllinen / ei vielä ratkaistavissa.\n5. Raportoi osuus vain arvioiduista, arvioimatta jääneet erikseen ja palautteen kattavuus. Tavoite ≥80 % hyödyllisiä arvioiduista; vähintään 80 % palautepeitto ja otoskoko näkyviin. Tämä ei korvaa riippumatonta relevanssitestiä eikä mittaa vääriä negatiivisia.\n6. Hyväksy toimitusmalli, kun todellinen aktiivinen työ jää alle 10 min / asiakas / päivä ja laatu täyttää portin.\n`;
writeFileSync(path.join(directory,'PILOT_REPORT.md'),markdown);console.log(JSON.stringify({report:path.join(directory,'report.json'),deliveries:m.delivery_count,items:90,automated_ms:report.actual_elapsed_ms,human_time:null,customer_usefulness:null}));
