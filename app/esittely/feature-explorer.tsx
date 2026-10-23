"use client";
import { useState } from "react";
const views = [
 { title: "Rajaa", heading: "Yrityksesi profiili ohjaa seurantaa.", text: "Määritellään palvelut, kunnat, tavoiteltu urakkakoko ja yrityksen käytettävissä oleva näyttö.", facts: ["Palvelut ja työn sisältö", "Kunnat ja toiminta-alue", "Urakkakoko ja kelpoisuuden tarkistukset"] },
 { title: "Ymmärrä", heading: "Faktat ja arviot erottuvat toisistaan.", text: "Kooste erottaa lähteessä todetun tiedon, alustavan soveltuvuusarvion ja puuttuvat tiedot. Epävarmuus jää näkyviin.", facts: ["Lähdeviite ja aineiston päiväys", "Perustelu yritysprofiilin suhteen", "Avoimet ehdot ennen tarjouspäätöstä"] },
 { title: "Päätä", heading: "Selkeä seuraava tarkistus.", text: "Päätät, kannattaako kohteen selvittämistä jatkaa. Lopullinen tarjouspäätös tehdään ajantasaisten tarjousasiakirjojen pohjalta.", facts: ["Jatkoselvitys tai hylkäys perusteluineen", "Määräaikojen tarkistus", "Palaute osuvuudesta seuraavaan koosteeseen"] }
];
export default function FeatureExplorer() {
 const [active,setActive]=useState(0); const view=views[active];
 return <section className="ul-explorer ul-container" aria-labelledby="explorer-title"><div><span className="ul-eyebrow">TYÖNKULKU KÄYTÄNNÖSSÄ</span><h2 id="explorer-title">Ilmoitusvirrasta perusteltuun päätökseen.</h2><p>Valitse vaihe ja tutustu toimituksen sisältöön.</p></div><div className="ul-explorer-card"><div className="ul-explorer-controls" role="group" aria-label="Työnkulun vaihe">{views.map((v,i)=><button key={v.title} type="button" aria-pressed={i===active} onClick={()=>setActive(i)}>{String(i+1).padStart(2,"0")} · {v.title}</button>)}</div><div className="ul-explorer-content" aria-live="polite" aria-atomic="true"><span className="ul-eyebrow">{String(active+1).padStart(2,"0")} / 03</span><h3>{view.heading}</h3><p>{view.text}</p><ul>{view.facts.map(f=><li key={f}>{f}</li>)}</ul></div></div></section>;
}
