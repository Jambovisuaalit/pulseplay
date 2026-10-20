import Image from "next/image";
import type { Metadata } from "next";
import { confirmedPublicOrigin } from "@/lib/public-site";
import { pilotOffer } from "./site-config";
import PilotForm from "./pilot-form";
import "./site.css";

const publicOrigin = confirmedPublicOrigin(process.env.URAKKALUOTSI_PUBLIC_ORIGIN);

export const metadata: Metadata = {
  // Enable canonical only in the separately configured release environment.
  metadataBase: new URL(publicOrigin || "https://tenderpulse-neon.vercel.app"),
  ...(publicOrigin ? { alternates: { canonical: publicOrigin + "/" } } : {}),
  title: "Urakkaluotsi | Julkiset hankinnat yrityksellesi",
  openGraph: { ...(publicOrigin ? { url: publicOrigin + "/" } : {}), title: "Urakkaluotsi | Julkiset hankinnat yrityksellesi", images: [{ url: "/urakkaluotsi/og.png", width: 1200, height: 630, alt: "Urakkaluotsi – Sopivat urakat. Selkeä seuraava askel." }], locale: "fi_FI", type: "website" },
  description: "Urakkaluotsi seuloo Hilman hankintailmoituksia rakennus- ja saneerausyrityksille. Saat koosteen kiinnostavista urakoista, vaatimuksista ja seuraavista toimista.",
};

const demo = "/urakkaluotsi/esimerkkikooste.pdf";

const details = [
  ["Mitä ostetaan?", "Työn sisältö, toteutusalue ja ilmoituksessa kuvattu laajuus."],
  ["Miksi kohde voisi sopia?", "Perustelu suhteessa yrityksesi ilmoittamiin palveluihin ja kyvykkyyksiin."],
  ["Mitä pitää tarkistaa?", "Esimerkiksi referenssit, taloudelliset ehdot, pätevyydet ja kohdekäynnit."],
  ["Milloin pitää toimia?", "Tarjouksen ja lisäkysymysten määräajat."],
  ["Mikä on seuraava askel?", "Konkreettinen suositus jatkoselvitykselle sekä lähdeviitteet havaintojen tarkistamiseen."],
];
const steps = [
  ["Määrittelemme yrityksesi profiilin", "Palvelut, toiminta-alue, tyypilliset urakat ja keskeiset kyvykkyydet."],
  ["Seulomme hankintailmoitukset", "Tarkastelemme sovittuun rajaukseen kuuluvia ilmoituksia virallisesta Hilma-rajapinnasta."],
  ["Saat koosteen sähköpostiisi", "Kiinnostavat kohteet, tarkistettavat ehdot ja seuraavat toimet sovitulla rytmillä."],
  ["Annat palautteen kohteiden osuvuudesta", "Palautteen perusteella tarkennamme seurantaa ja arvioimme palvelun hyötyä."],
];

export default function EsittelyPage() {
  return <div className="ul-site">
    <a className="ul-skip" href="#alku">Siirry sisältöön</a><header className="ul-top"><div className="ul-container ul-nav">
      <a href="#alku" aria-label="Urakkaluotsi – alkuun"><Image src="/urakkaluotsi/logo-primary.svg" alt="Urakkaluotsi" width={194} height={42} priority /></a>
      <nav aria-label="Päänavigaatio"><a href="#toiminta">Näin toimii</a><a href="#esimerkki">Esimerkkikooste</a><a href="#pilotti">Pilotti</a></nav>
      <a className="ul-btn ul-nav-cta" href="#hakemus">Hae pilottiin <span aria-hidden>↗</span></a>
    </div></header>
    <main id="alku" tabIndex={-1}>
      <section className="ul-hero ul-container">
        <div className="ul-hero-copy"><span className="ul-kicker"><span className="ul-dot"/> Julkisten hankintojen seuranta rakennus- ja saneerausyrityksille</span>
          <h1>Mitkä julkiset urakat kannattaa selvittää <em>seuraavaksi?</em></h1>
          <p className="ul-lead">Urakkaluotsi seuloo Hilman hankintailmoituksia yrityksesi palveluiden ja toiminta-alueen perusteella. Saat sähköpostiisi selkeän koosteen kiinnostavista kohteista, niiden keskeisistä vaatimuksista ja seuraavista tarkistuksista.</p>
          <div className="ul-actions"><a className="ul-btn" href="#hakemus">Hae pilottiin <span aria-hidden>↗</span></a><a className="ul-btn ul-outline" href="#esimerkki">Katso esimerkkikooste <span aria-hidden>↓</span></a></div>
          <p className="ul-micro">Sopivat urakat. Selkeä seuraava askel.</p>
        </div>
        <aside className="ul-product" aria-label="Koosteen rakenteellinen esimerkki">
          <div className="ul-product-head"><Image src="/urakkaluotsi/mark-white.svg" alt="" width={24} height={24}/><span>SÄHKÖPOSTIKOOSTE</span></div>
          <div className="ul-product-intro"><span className="ul-label">RAKENTEELLINEN ESIMERKKI</span><h2>Ilmoituksesta seuraavaan askeleeseen.</h2><p>Näin tiedot erotellaan toimituksessa. Kortti ei kuvaa yksittäistä hankintaa.</p></div>
          <dl className="ul-evidence">
            <div><dt><span className="ul-number">01</span> Lähteessä todettu</dt><dd>Työn sisältö, sijainti ja ilmoitetut määräajat lähdeviitteineen.</dd></div>
            <div><dt><span className="ul-number">02</span> Urakkaluotsin arvio</dt><dd>Miksi kohde voisi sopia yrityksesi profiiliin.</dd></div>
            <div><dt><span className="ul-number">03</span> Puuttuva tieto</dt><dd>Avoimet ehdot ja tiedot, joita ei ole vielä varmennettu.</dd></div>
            <div><dt><span className="ul-number">04</span> Seuraava toimi</dt><dd>Mitä selvitetään ennen tarjouspäätöstä.</dd></div>
          </dl>
          <div className="ul-product-foot"><span>Alustava päätöstuki</span><a href={demo} target="_blank" rel="noopener noreferrer">Avaa esimerkkikooste ↗</a></div>
        </aside>
      </section>
      <section className="ul-band" id="ongelma"><div className="ul-container ul-split"><div><span className="ul-eyebrow">ONGELMA</span><h2>Sopiva urakka voi jäädä ilmoitusvirran alle.</h2></div><p>Pelkkä otsikko ei kerro, sopiiko hankinta yrityksellesi. Päätöstä varten pitää selvittää työn sisältö, sijainti, määräajat ja tarjoajalta edellytettävä näyttö. Urakkaluotsi kokoaa nämä tiedot alustavan päätöksenteon tueksi.</p></div></section>
      <section className="ul-section ul-container"><div className="ul-section-head"><span className="ul-eyebrow">KOOSTEEN SISÄLTÖ</span><h2>Jokaisesta nostetusta hankinnasta olennainen.</h2><p>Viisi kysymystä, joihin hyvä seuranta auttaa vastaamaan.</p></div><div className="ul-feature-grid">{details.map(([title, description], i) => <article className="ul-feature" key={title}><span className="ul-index">0{i + 1}</span><h3>{title}</h3><p>{description}</p></article>)}</div></section>
      <section className="ul-section ul-demo-band" id="esimerkki"><div className="ul-container ul-demo"><div><span className="ul-eyebrow">OIKEA AINEISTO · HAVAINNOLLISTAVA TOIMITUS</span><h2>Katso, miltä toimitus näyttää.</h2><p>Tutustu nelisivuiseen esimerkkikoosteeseen: työn sisältö, määräajat, avoimet ehdot ja seuraavat tarkistukset.</p><a className="ul-btn" href={demo} target="_blank" rel="noopener noreferrer">Avaa esimerkkikooste (PDF) ↗</a><p className="ul-disclaimer">Esimerkki perustuu 18.10.2026 tallennettuun aineistoon. Se havainnollistaa toimitustapaa. Hankintojen ajantasainen tila ja yrityskohtainen soveltuvuus tarkistetaan erikseen.</p></div><a className="ul-pdf-preview" href={demo} target="_blank" rel="noopener noreferrer" aria-label="Avaa nelisivuinen esimerkkikooste PDF-tiedostona"><div className="ul-sheet"><span>Urakkaluotsi</span><small>JULKINEN ESIMERKKIKOOSTE</small><strong>Mihin kannattaa käyttää aikaa ensin?</strong><i/><i/><i className="short"/><hr/><b>Työn sisältö ja lähteet</b><i/><b>Määräajat ja avoimet ehdot</b><i/><b>Seuraavat tarkistukset</b><i/></div><span className="ul-pdf-caption">4 SIVUA <span>↗</span></span></a></div></section>
      <section className="ul-section ul-container" id="toiminta"><div className="ul-section-head"><span className="ul-eyebrow">30 PÄIVÄN PILOTTI</span><h2>Näin pilotti toimii.</h2><p>Saat käytännön päätöstukea sähköpostiin ilman uuden ohjelmiston käyttöönottoa.</p></div><div className="ul-step-grid">{steps.map(([title, description],i)=><article className="ul-step" key={title}><span className="ul-step-num">{String(i+1).padStart(2,"0")}</span><h3>{title}</h3><p>{description}</p></article>)}</div></section>
      <section className="ul-section ul-final" id="pilotti"><div className="ul-container ul-final-grid"><div><span className="ul-eyebrow">PILOTTIHAKU</span><h2>Tule mukaan ensimmäisten joukossa.</h2><p>Haemme kahta rakennus- tai saneerausyritystä 30 päivän maksulliseen pilottiin. Pilottiin sisältyvät yritysprofiilin määrittely, sovittu hankintaseuranta, sähköpostikoosteet ja yhteinen loppuarvio.</p><p className="ul-price">{pilotOffer.priceLabel}<span>{pilotOffer.taxNotice}</span></p><div className="ul-pilot-note"><strong>Sovimme ennen aloitusta</strong><span>Seurannan rajauksen, toimitusrytmin ja lopulliset ehdot. Pilotti aloitetaan vasta toimitusvalmiuden varmistamisen jälkeen.</span><span>Hakemus käynnistää keskustelun. Se ei ole sitova tilaus.</span></div></div><PilotForm /></div></section>
      <section className="ul-section ul-container ul-faq"><div><span className="ul-eyebrow">USEIN KYSYTTYÄ</span><h2>Hyvä tietää ennen pilottia.</h2></div><div className="ul-faq-items"><details><summary>Mistä hankintatiedot tulevat?</summary><p>Käytämme virallista Hilma AVP Read API -rajapintaa.</p></details><details><summary>Vahvistaako palvelu tarjouskelpoisuuden?</summary><p>Lopullinen tarjouspäätös edellyttää ajantasaisten tarjousasiakirjojen ja yrityksen tietojen tarkistamista.</p></details><details><summary>Sisältyykö tarjouksen laatiminen?</summary><p>Pilotin sisältö on hankintojen seuranta ja alustava arviointi. Tarjouksen laskenta ja laatiminen eivät sisälly pilottiin.</p></details><details><summary>Tarvitaanko uusi ohjelmisto?</summary><p>Saat koosteet sähköpostiisi. Pilotti ei edellytä uuden järjestelmän käyttöönottoa.</p></details></div></section>
    </main><footer className="ul-footer"><div className="ul-container"><Image src="/urakkaluotsi/logo-white.svg" alt="Urakkaluotsi" width={178} height={38}/><p>Sopivat urakat. Selkeä seuraava askel.</p><small>Palveluntarjoaja: Tmi Jami Harju · Y-tunnus: 3581581-6 · Yhteys: <a href="mailto:visualjambo@gmail.com">visualjambo@gmail.com</a> · Palvelu kehitysvaiheessa.</small><p className="ul-footer-links"><a href="/esittely/tietosuoja">Tietosuojatiedot</a></p></div></footer>
  </div>;
}
