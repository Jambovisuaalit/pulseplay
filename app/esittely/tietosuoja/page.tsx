import type { Metadata } from "next";
import Link from "next/link";
import "../site.css";

export const metadata: Metadata = {
  title: "Tietosuojatiedot | Urakkaluotsi",
  description: "Miten Urakkaluotsi käsittelee pilottiyhteydenottoihin liittyviä henkilötietoja.",
};

export default function TietosuojaPage() {
  return <div className="ul-site">
    <a className="ul-skip" href="#tietosuoja">Siirry sisältöön</a><header className="ul-top"><div className="ul-container ul-nav"><Link href="/esittely" aria-label="Takaisin Urakkaluotsin etusivulle">← Urakkaluotsi</Link></div></header>
    <main id="tietosuoja" tabIndex={-1} className="ul-container ul-privacy-page">
      <span className="ul-eyebrow">URAKKALUOTSI</span>
      <h1>Tietosuojaseloste</h1>
      <p>Päivitetty 19.10.2026. Nämä tiedot kuvaavat nykyistä sähköpostiin perustuvaa pilottiyhteydenottoa. Palvelun tekninen toteutus tai käsittelytavat voivat muuttua; tällöin myös tiedot päivitetään.</p>
      <h2>1. Rekisterinpitäjä ja yhteydenotot</h2>
      <p>Tmi Jami Harju (Urakkaluotsi), Y-tunnus 3581581-6. Yhteydenotot ja tietosuojaa koskevat pyynnöt: <a href="mailto:visualjambo@gmail.com">visualjambo@gmail.com</a>.</p>
      <h2>2. Mitä tietoja käsittelemme?</h2>
      <p>Jos lähetät pilottiyhteydenoton, käsittelemme antamasi yrityksen nimen, yhteyshenkilön nimen, työsähköpostin, toiminta-alueen, kuvauksen kiinnostavista urakoista sekä viestisi sisällön ja yhteydenpidon.</p>
      <h2>3. Mihin tietoja käytetään ja millä perusteella?</h2>
      <p>Käytämme tietoja pilottikyselyyn vastaamiseen, yrityksen tarpeiden alustavaan kartoittamiseen ja mahdollisen pilotin ehtojen sopimiseen. Käsittely perustuu pyytämiesi sopimusta edeltävien toimien toteuttamiseen silloin, kun olet itse mahdollinen sopimusosapuoli, tai muutoin rekisterinpitäjän oikeutettuun etuun vastata yrityksen puolesta lähetettyyn B2B-yhteydenottoon. Emme käytä lomakkeen tietoja automaattiseen päätöksentekoon.</p>
      <h2>4. Miten yhteydenotto toimii?</h2>
      <p>Tämän sivun lomake muodostaa sähköpostiluonnoksen laitteesi sähköpostisovellukseen. Sivusto ei lähetä lomaketietoja Urakkaluotsin palvelimelle eikä vahvista viestin vastaanottoa. Kun itse lähetät viestin, se käsitellään lähettäjän ja vastaanottajan sähköpostipalveluissa.</p>
      <h2>5. Säilytys ja vastaanottajat</h2>
      <p>Pilotin yhteydenottoja säilytetään vain niin kauan kuin asian käsittely, mahdollinen sopimussuhde tai lakisääteinen velvoite sitä edellyttää. Jos pilottia ei synny, poistamme yhteydenottoviestit viimeistään kuuden kuukauden kuluttua viimeisestä yhteydenotosta, ellei asian selvittäminen tai oikeudellisen vaateen käsittely edellytä pidempää säilytystä. Mahdollisen asiakassuhteen tietojen käsittelystä kerrotaan erikseen ennen pilotin aloitusta. Vastaanottajan sähköpostipalvelu on Google Gmail ja verkkosivun hosting-palvelu Vercel. Sähköpostin lähettäjän oma palveluntarjoaja käsittelee viestin lähettämisen. Viestejä ei myydä eikä lisätä automaattisesti markkinointilistalle.</p>
      <h2>6. Palveluntarjoajat ja kansainvälinen käsittely</h2>
      <p>Google ja Vercel voivat käsitellä palvelun tietoja myös EU:n tai ETA:n ulkopuolella. Palvelukohtaiset käsittelypaikat, vastaanottajat ja siirtojen suojatoimet kuvataan <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Googlen tietosuojakäytännössä</a> ja <a href="https://vercel.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer">Vercelin tietosuojakäytännössä</a>. Voit pyytää lisätietoja yhteysosoitteestamme.</p>
      <h2>7. Oikeutesi</h2>
      <p>Voit pyytää pääsyä tietoihisi, niiden oikaisua tai poistamista, käsittelyn rajoittamista tai vastustaa oikeutettuun etuun perustuvaa käsittelyä. Oikeudet määräytyvät käsittelyperusteen ja tilanteen mukaan. Ota yhteyttä yllä olevaan osoitteeseen. Voit myös tehdä valituksen tietosuojavaltuutetun toimistolle (<a href="https://tietosuoja.fi/" target="_blank" rel="noopener noreferrer">tietosuoja.fi</a>).</p>
      <h2>8. Evästeet ja tekniset tiedot</h2>
      <p>Urakkaluotsin julkisella esittelysivulla ei ole erillistä markkinoinnin seurantakoodia. Sähköpostiluonnosta avattaessa sivusto ei tallenna viestin kenttiä omaan tietokantaansa. Vercel voi käsitellä verkkopyyntöjen teknisiä tietoja, kuten IP-osoitetta, selaintietoja, pyydettyä osoitetta ja ajankohtaa, sivun toimittamiseksi ja tietoturvan ylläpitämiseksi. Lomakkeen kenttiä ei lisätä sivun osoitteeseen tai lähetetä analytiikkaan. Samalla verkkotunnuksella olevan suojatun työkalun kirjautuminen käyttää istuntoevästettä; julkisen esittelysivun käyttö ei edellytä kirjautumista.</p>
      <p><Link href="/esittely">← Takaisin esittelyyn</Link></p>
    </main>
  </div>;
}
