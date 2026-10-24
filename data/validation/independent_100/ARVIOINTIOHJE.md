# Urakkaluotsi – riippumattoman 100 ilmoituksen sokkoarvioinnin ohje

**SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS**

Versio 1.0 · aineistopoiminta 19.10.2026 00.12 UTC · GitHub Actions -artefakti 12155822339.

## Riippumattomuuden varmistus

1. Arvioija lukee **ensin vain** `blind_review.csv`-aineiston tai `sokkoarvio_100.xlsx`-työkirjan `Sokkotiedot`-välilehden sekä tarvittavan alkuperäisen Hilma-ilmoituksen. Automaattisia pisteitä tai `predictions.csv`-taulukkoa ei saa nähdä luokitteluvaiheessa.
2. Arvioija merkitsee erilliseen `gold_labels.csv`-tiedostoon (tai työkirjan `Vertailuluokat`-välilehdelle) tunnisteen, luokan, oman arvioijatunnuksensa, tarkistusajan, perustelun sekä tarkan lähdeotteen.
3. `source_checked=YES` merkitään vain, kun lähdeteksti todella luettiin ja ilmoituksen tunniste varmistettiin. Tähän snapshotiin **ei sisälly tarjousliitteitä**. Puuttuvia liitteitä ei saa merkitä tarkistetuiksi.
4. Toinen henkilö tai erillinen sovittu tarkistaja ratkaisee erimielisyydet ennen tulosten lukitsemista. Tarvittaessa käytetään luokkaa `Mahdollinen`. Tässä paketissa ei ole täytetty yhtään ihmisen tekemää vertailuluokkaa.
5. Vasta lukittujen luokkien jälkeen yhdistetään `predictions.csv` ja ajetaan `python workers/score_validation.py`.

## Asiakkaan riippumattomat sopivuussäännöt

- **Palvelut:** huoneisto- ja pintasaneeraukset, maalaus, lattia- ja kalustekorjaukset, pienkorjaukset sekä toimitilojen sisäpuoliset korjaustyöt.
- **Alueet:** Helsinki, Espoo, Vantaa, Kauniainen ja Kirkkonummi. Esim. Hyvinkää, Riihimäki ja Mäntyharju ovat poissuljettuja.
- **Koko:** tavoiteltava yksittäinen urakka noin 10 000–250 000 €. Puitesopimuksen kokonaisarvoa ei saa tulkita yksittäiseksi tilaukseksi.
- **Poissulut:** uudisrakentaminen, laajat talotekniset kokonaisurakat, ikkuna- ja ovikokonaisvaihdot, kattourakat, yli 250 000 € yksittäiset hankkeet ja väärä maantiede.
- **Kelpoisuus:** referenssejä, taloutta, pätevyyksiä ja kapasiteettia **ei ole vahvistettu**. Relevanssiluokka ei koskaan tarkoita todettua tarjouskelpoisuutta.

## Luokan valinta

| Vertailuluokka | Soveltamisperuste | Kirjattava näyttö |
| --- | --- | --- |
| `Relevantti` | Työn laji ja toteutusalue vastaavat selvästi palvelu- ja aluerajausta; ei lähteessä todettua poissulkuperustetta. | Työ- ja aluerajauksen lähdeote; urakkakoon epävarmuus kirjataan erikseen. |
| `Mahdollinen` | Potentiaalisesti sopiva, mutta alue, työn rajaus, yksittäisen tilauksen laajuus tai ratkaiseva hankinta-asiakirja jää epäselväksi. | Täsmällinen avoin kysymys, ei arvailua. |
| `Epärelevantti` | Lähteessä osoitetaan selvä toimiala-, alue- tai kohdekoon poissulku. | Lähdeote sekä poissulun nimi. |

`error_type`-kenttään voi kirjata esimerkiksi `palvelut`, `alue`, `koko`, `vanhentunut`, `puuttuvat_liitteet`, `kelpoisuus` tai `muu`. Virhetyyppi voidaan nimetä myös vasta ennusteen ja lukitun vertailuluokan vertailuvaiheessa, eikä sen puuttuminen oikeuta keksimään perustetta.

## Mittaustapa ja rajoitukset

- 100 riviä ovat oikeiden hakutulosten metadataa, eivät 100 täydellistä tarjousasiakirjaa.
- Jokainen ilmoitus pisteytetään jäädytettyyn järjestykseen **ennen** ihmisen luokkiin yhdistämistä. Top-30-nimittäjä pysyy 30:nä.
- Positiiviseksi ennusteeksi lasketaan vain `Relevantti`. Muut ennusteet jäävät ilman positiivista nostoa, joten niiden ohittamat todelliset relevantit kohteet ovat väärien negatiivisten lähde.
- `Mahdollinen` vertailuluokkana ei anna varmaa oikeaa/virheellistä binäärivastausta. Jos sellaisia tai arvioimattomia rivejä on, koko precision/FP/FN-portti on **NOT MEASURED**. Osittaiset havaitut luvut eivät ole koko otoksen KPI.
- Päättynyt tarjousaika raportoidaan erillisenä toimitusturvallisuuden virheenä; relevanssi ja avoin tarjouskelpoisuus ovat eri mittareita.
- Hakutulos-CV:t ja päättely eivät saa täydentää puuttuvaa todennettavaa näyttöä.
