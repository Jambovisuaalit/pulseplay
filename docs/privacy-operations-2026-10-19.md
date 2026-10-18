# Urakkaluotsi – tietosuojakäytäntöjen tarkistus ja toimintaohje

Versio 1.0 · 19.10.2026 · Vastuu: Jami Harju / Tmi Jami Harju, Y-tunnus 3581581-6.

## Johtopäätös

**Osittain varmennettu. Ei kokonaisvahvistusta tietosuojan julkaisuvalmiudelle.** Gmail-vastaanottaja ja sivun mailto-toteutus on varmennettu. Vercelin tilikohtaisiin asetuksiin ei saatu pääsyä. Kuuden kuukauden säilytys on selosteessa määritelty toimintatapa, ei varmennettu Gmailin automaatio. Tässä tarkistuksessa ei muutettu palvelutilien asetuksia, lähetetty sähköpostia tai poistettu viestejä.

## Varmennusmatriisi

| Kohde | Todennettu | Avoin |
|---|---|---|
| Gmail-tili | Yhdistetty profiili: Jami Harju, visualjambo@gmail.com | Profiilityökalu ei palauta tilin MFA-, jako-, delegointi-, edelleenlähetys-, suodatin- tai säilytysasetuksia |
| Sähköpostin palvelumalli | Vastaanottaja on @gmail.com-osoite; Google kertoo, ettei kuluttaja-Gmailiin tarjota DPA:ta eikä Google toimi tässä palvelussa henkilötietojen käsittelijänä | Tilin profiili ei osoita Workspace/CDPA-sopimusta. Osoitteen perusteella kuluttajapalvelu on lähtöoletus, ei erillisen sopimuksen tarkastus |
| Sivun tiedonkulku | contact.ts luo mailto-URL:n; pilot-form.tsx näyttää kopioitavan varaviestitilan; aiempi CI testasi polun | Käyttäjän oma sähköpostipalvelu ja natiivi laite eivät ole sivuston hallittavissa |
| Vercel-projekti | GitHub/Vercel-deployment-yhteys on aiemmin varmennettu projektiksi v0-pulse-play, prj_NUKwL4BbwD8vKTQbDECaAnuJn4XV, tiimi jas-projects-09b09626 | Projektin luku palautti 403 forbidden. Plan, Observability Plus, Drains, Analytics, integraatiot, alueet ja tilikohtainen sopimus jäivät todentamatta |
| Julkinen seloste | Sisältää Gmailin/Vercelin, kuusi kuukautta, mailto-polun ja yhteysosoitteen | Palvelukohtainen käsittelyrooli sekä tilikohtaiset säilytys-/siirtojärjestelyt eivät ole vahvistettuja |
| Poisto | Gmailin dokumentaatio: roskakoriin siirto ei ole välitön lopullinen poisto; viesti poistuu sieltä tavallisesti 30 päivän jälkeen | Oikeiden viestien poistoa, nykyisiä suodattimia tai toteutunutta poistohistoriaa ei tarkastettu |

## Päätetty sisältöraja ja säilytysohje

Alla oleva on **käyttöönotettava sisäinen toimintamalli**, ei väite aiemmin toteutuneista poistoista eikä lakisääteinen oletussäilytysaika.

| Tietoryhmä | Toimintamalli | Vastuuhenkilö / raja |
|---|---|---|
| Pilottikysely, josta ei synny asiakkuutta | Koko yhteydenottoketjun tarpeellisuus arvioidaan; aktiivista käsittelyä ei jatketa pelkän säilytysajan pidentämiseksi | Jami; tavoite poistolle enintään 6 kuukautta viimeisestä asiallisesta yhteydenotosta |
| Aktiivinen asiakas | Asiakasviestit erotetaan yleisistä pilottikyselyistä; asiakkuuden käsittely ja tarpeellisuus määritellään ennen pilotin aloitusta | Jami; ei automaattista kuuden kuukauden massapoistoa |
| Sopimus-, laskutus- ja vaadeaineisto | Tarpeellinen aineisto erotetaan yleisestä yhteydenpidosta; säilytysperuste ja tarkistuspäivä kirjataan | Lakiperusteinen aika vahvistettava erikseen; ei keksittyä yhteistä määräaikaa |
| Luonnokset ja paikalliset kopiot | Tarpeettomat Gmail-luonnokset ja ladatut kopiot huomioidaan samaa asiaa suljettaessa | Jami; ei tarpeettomia varmuuskopioita henkilökohtaisiin pilvipalveluihin |
| Poistoloki | Säilytetään vain toimenpiteen päivä, sisäinen tunniste, tietoryhmä, poiston laajuus ja mahdollinen poikkeusperuste | Ei viestin sisältöä, liitteitä tai tarpeettomia yhteystietoja lokiin; lokille oma tarpeellisuusarvio |

## Gmailin poistosykli

1. Erota Urakkaluotsin pilottiyhteydenotot muista hankkeista. Käytä yksiselitteistä tunnistetta; pelkkä yrityksen nimi tai viestin ikä ei riitä poistopäätökseen.
2. Tarkista suljetut, ei-asiakkuuteen johtaneet ketjut säännöllisesti. Työjonoon nostetaan viimeistään 140 päivää vanhat ketjut, jotta kuuden kuukauden enimmäistavoitteeseen jää käsittely- ja roskakorivara.
3. Varmista viimeisin yhteydenotto, asiakkuuden tila ja mahdollinen avoin selvitys/vaade. Säilytyspoikkeus tarvitsee perusteen ja uuden tarkistuspäivän.
4. Käsittele hyväksytyt poistoehdokkaat viimeistään 150 päivän kohdalla. Tarkista saapuneet, lähetetyt, arkistoidut viestit ja liitteiden erilliskopiot. Gmailin hakurivi ei yksin korvaa koko ketjun tarkistusta.
5. Tavallinen Gmail-poisto siirtää viestin roskakoriin; palvelun dokumentaation mukaan lopullinen poisto tapahtuu 30 päivän jälkeen. Näin 150 + 30 päivän toimintamalli jättää varaa kuuden kalenterikuukauden rajaan. Kirjaa roskakoriin siirto eri tapahtumana kuin lopullisen poiston tarkistus.
6. Jos tarvitaan aikaisempi lopullinen poisto, yksilöi vain kyseiset viestit erikseen; koko henkilökohtaisen postilaatikon roskakoria ei tyhjennetä tämän menettelyn nojalla.
7. Tarkista lopputulos: kohde ei näy aktiivisessa postissa eikä roskakorissa, erilliskopiot on käsitelty ja poistotapahtuma kirjattu. Poisto omasta postilaatikosta ei todista vastaanottajan kopioiden tai Googlen teknisten varmistusten välitöntä poistumista.

**Automaatio ei ole käytössä tämän ohjeen perusteella.** Seuranta, ketjujen luokittelu ja mahdollinen poistoautomaatio on ensin toteutettava ja testattava rajatulla aineistolla. Tässä työssä ei tehty roskakori- eikä lopullisia poistoja.

## Vercelin tarkistettavat asetukset

Kun projektin oikea tiimikonteksti on käytettävissä, tarkista yksi kerrallaan:

- Projektin tilaus ja Observability Plus. Julkisen ohjeen lokirajoja ei pidä kopioida suoraan tilikohtaiseksi säilytysajaksi.
- Runtime Logs, erilliset Log/Telemetry Drains ja niiden kohteet; ulkoisella kohteella voi olla oma pidempi säilytys.
- Web Analytics, Speed Insights, kolmannen osapuolen integraatiot ja palveluun lisätyt seurantakoodit.
- Projektin käyttöoikeudet, deployjen julkisuus sekä henkilötietojen mahdollinen päätyminen build-lokeihin, virheisiin tai esikatseluihin.
- Palveluun sovellettava DPA ja siirtoehdot. Julkaistu sopimuspohja ei yksin ole tilikohtaisen soveltuvuuden tarkistus.

Vercelin Runtime Logs -dokumentaatio ilmoittaa 19.10.2026 tarkistettuna: Hobby 1 tunti; Pro 1 päivä; Enterprise 3 päivää; Observability Plus Pro/Enterprise 30 päivää. Nämä ovat kyseisen runtime-lokipalvelun saatavuus-/säilytysrajoja, eivät kaikkien Vercelin tietojen tai lokivientien yhteinen poistotakuu.

## Seuraavat ratkaisevat toimet

1. Sähköposti: varmista yrityskäyttöön soveltuva palvelumalli ja sopimussuhde. Suositus on käyttää jo olemassa olevaan yrityspalveluun kuuluvaa postilaatikkoa, jonka käsittelyehdot voidaan todentaa, ennen uusien maksullisten työkalujen hankintaa. Nykyistä kuluttaja-Gmailia ei merkitä Workspace/CDPA-ratkaisuksi.
2. Vercel: anna olemassa olevalle yhteydelle projektin oikean tiimin lukuoikeus tai toimita tilikohtaiset asetukset tarkistettavaksi. Nykyinen yhteys palauttaa 403; paikallista Vercel CLI:tä ei ollut saatavilla saman pyynnön vaihtoehdoksi.
3. Poisto: ota yllä oleva työjono ja todentaminen käyttöön. Julkista kuuden kuukauden lupausta ei pidä merkitä automaattisesti toteutuvaksi ennen käytännön testausta.
4. Kun nämä on varmennettu, päivitä julkisen selosteen palvelumalli ja täsmällinen lokikäsittely. Sivuston tekninen QA-hyväksyntä säilyy erillisenä asiana.

## Lähteet ja varmennuksen rajat

Tarkistus 19.10.2026. Tietolähteet: yhdistetyn Gmailin profiili, PR #3:n commit 481260c51d804bff0cbc2be92b4132450aa63e9d, Vercel GET project -pyynnön 403-virhe sekä seuraavat palveluntarjoajien omat ohjeet:

- Google, consumer Gmail / DPA: https://support.google.com/policies/answer/9581826?hl=en (Enterprise customer requests & resources).
- Gmail, poisto ja roskakori: https://support.google.com/mail/answer/7401?hl=en.
- Vercel Runtime Logs: https://vercel.com/docs/logs/runtime.
- Vercel DPA: https://vercel.com/legal/dpa.

Palveluntarjoajien ohjeet on luettu verkkolähteinä. Niiden perusteella ei anneta lainmukaisuuslausuntoa. Lakimies AI -ohjeen edellyttämiä artikla-/ajallisuusvarmennuksen MCP-työkaluja ei ollut saatavilla: **Lähdevarmennus epäonnistui – en voi vahvistaa oikeustilaa.** Virhekoodi `TOOL_UNAVAILABLE`. Tämä rajoitus ei muuta yllä erikseen varmennettuja teknisiä havaintoja.
