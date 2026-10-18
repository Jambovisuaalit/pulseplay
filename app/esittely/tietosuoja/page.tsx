import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Tietosuojatiedot | Urakkaluotsi",
  description: "Miten Urakkaluotsi käsittelee pilottiyhteydenottoihin liittyviä henkilötietoja.",
};

export default function TietosuojaPage() {
  return <div className="ul-site">
    <header className="ul-top"><div className="ul-container ul-nav"><Link href="/esittely" aria-label="Takaisin Urakkaluotsin etusivulle">← Urakkaluotsi</Link></div></header>
    <main className="ul-container ul-privacy-page">
      <span className="ul-eyebrow">URAKKALUOTSI</span>
      <h1>Tietosuojatiedot</h1>
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
      <p>Pilotin yhteydenottoja säilytetään vain niin kauan kuin asian käsittely, mahdollinen sopimussuhde tai lakisääteinen velvoite sitä edellyttää. Jos pilottia ei synny, viestit poistetaan, kun yhteydenoton käsittely ja kohtuullinen jälkiseuranta ovat päättyneet. Sähköpostin ja verkkosivuston tekniset palveluntarjoajat voivat käsitellä tietoja palveluiden toteuttamiseksi omien ehtojensa mukaisesti.</p>
      <h2>6. Oikeutesi</h2>
      <p>Voit pyytää pääsyä tietoihisi, niiden oikaisua tai poistamista, käsittelyn rajoittamista tai vastustaa oikeutettuun etuun perustuvaa käsittelyä. Oikeudet määräytyvät käsittelyperusteen ja tilanteen mukaan. Ota yhteyttä yllä olevaan osoitteeseen. Voit myös tehdä valituksen tietosuojavaltuutetun toimistolle (<a href="https://tietosuoja.fi/" target="_blank" rel="noopener noreferrer">tietosuoja.fi</a>).</p>
      <h2>7. Evästeet ja kävijäseuranta</h2>
      <p>Urakkaluotsin julkisella esittelysivulla ei ole erillistä markkinoinnin seurantakoodia. Sähköpostiluonnosta avattaessa sivusto ei tallenna viestin kenttiä omaan tietokantaansa. Verkkopalvelimen tekniset lokit ja mahdolliset muualla samalla verkkotunnuksella käytettävät evästeet arvioidaan erikseen ennen julkaisua.</p>
      <p><Link href="/esittely">← Takaisin esittelyyn</Link></p>
    </main>
  </div>;
}
