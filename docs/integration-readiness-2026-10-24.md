# Urakkaluotsi — integraatio ja pilottivalmius 24.10.2026

**Päätös: EI VALMIS maksulliseen pilottiin.** Toimivan paikallisen portaalin
ja PostgreSQL-tallennuksen testit eivät korvaa oikeaa Preview-ajoa tai
riippumatonta näyttöä hankintaseurannan osuvuudesta.

## Tarkastettu lähdekoodi ja riippuvuudet

Repossa tai sen yläpuolella ei löytynyt AGENTS.md-ohjeita. Työpuu oli alussa
puhdas. Olemassa olevat commitit, paikalliset asetukset ja muut haarat säilytettiin.

| PR | Tarkistettu kärki | Pohja ja riippuvuus |
| --- | --- | --- |
| #12, Draft | `0537486fc626452ecaef17354cccb4480e14fafe` | `feature/urakkaluotsi-sales-polish`, pysyvä tallennus ja sen testit |
| #14, review-valmis | `beb45d619e68d8d35261fa4d7b3263b3c3e01957` | Sama sales-polish-pohja, täydet julkiset sivut ja materiaalit |
| #15, Draft | `49bf805ac55f14e79d9ff9ff5b65df6a86a66d94` | `feature/urakkaluotsi-delivery-readiness` / `d1d16aa`; eri relevanssihaaran koko toteutus ja arviointiaineisto |

Yksi integraatiohaara: `integration/urakkaluotsi-pilot-readiness-20261024`.
Pohjana PR #12; siihen yhdistettiin #14 ja #15 paikallisesti. Päähaaraan ei
yhdistetty. #15:n mukana tullut vanha synkroninen dashboard, turvaton
ingest-alustus ja laajempi automaatiopolku eivät syrjäyttäneet nykyistä
istuntotarkistusta ja rajattua manuaalista keräintä. Päällekkäiset npm-skriptit
poistettiin. Uusi integraatio-PR kohdistetaan #14:n haaraan, jolloin tuotannon
myyntisivupohja ja siihen tulevat erot ovat arvioitavissa.

## Korjatut esteet

- Tallennuksen tila näytetään palvelimen todellisen onnistuneen lukureitin
  perusteella. Supabase-tilaa ei enää väitetä paikalliseksi tiedostotallennukseksi.
- Tietokantavirhe pysyy 503-virheenä eikä siirry tiedostoon. Epäselvä
  tallennuskuittaus ei väitä, ettei tieto tallentunut: mahdollisesti jo
  sitoutunut kirjoitus pitää tarkistaa lataamalla tila uudelleen.
- Istunnon vanheneminen, HTML-muotoinen tallennus-/vientivirhe ja yhteyskatko
  näkyvät ymmärrettävästi. Virhesivua ei ladata PDF-tiedostona. Saman tapahtuman
  kaksoislähetys estetään synkronisesti.
- Asiakkaan muokkauslomake täyttää nykyiset tiedot. Muokkaus ja uudelleenlataus
  sekä uusi kirjautumisistunto on testattu paikallisesti. Vahvistamaton määräaika
  voidaan kirjata puuttuvaksi; QA estää sen viennin hyväksyttynä kohteena.
- Profiiliversiot, lähdearviot, hyväksytyt snapshotit ja toimitushistoria
  tallennetaan yhtenä atomisena tilana. Perusteen muutos mitätöi hyväksynnän;
  aiempi tapahtumahistoria säilyy.
- Preview-ajuri kattaa luonti–muokkaus–uudelleenlataus–uusi sessio -ketjun ja
  koko profiili–lähde–kooste–hyväksyntä–vienti-ketjun. Se vaatii tyhjän
  synteettisen työtilan ja siivoaa vain oman UUID:nsa tiedot rajatulla RPC:llä.
  Taulun yleistä DELETE-oikeutta ei avata. SQL on valmisteltu ja testattu
  paikallisesti, **ei sovellettu etätietokantaan tässä työssä**.
- Kuntatarkistus ei hyväksy ostajan osoitetta työmaaksi eikä ristiriitaisista
  työmaista valita vain sallittua kuntaa. Urakan arvon vahvistus tarvitsee
  lähteessä esiintyvän yksittäisen urakan euroarvon, ei pelkkää boolean-lippua.
  Lähteessä poissuljettu työ tai suunnitteluhankinta ei ole remonttityön osuma.
  Keräimen todellinen CPV-haku rajataan rakentamisen viralliseen alipuuhun.

## Todentaminen

Paikalliset testit ja CI tekevät oikeita Next HTTP -pyyntöjä ja selainajoja,
mutta PostgreSQL:n Data API -kuljetus on paikallinen PGlite-testikuljetus.
Sitä ei nimetä oikeaksi hosted-Supabase-varmennukseksi. Raportit erotetaan
`qa-output/`-hakemistossa kentillä `scope` ja `hosted`.

- Node- ja Python-regressiot, lint, typecheck ja tuotantokäännös.
- Todellisen Next-tuotantokäännöksen 46 HTTP-tarkistusta paikallista PostgreSQL:ää
  vasten: profiilit, versiot, historia, viisi vientimuotoa, uusi sessio, 409 ja 503.
- PostgreSQL-oikeudet/RLS/CAS; erilliset varmuuskopio-/palautusprosessit;
  siivouksen omistajuus, null-syötteet, versioristiriidat ja roolien estot.
- Mobiili/desktop 375, 390, 768 ja 1440 px: PR #14:n navigaatio, lomakepolku,
  sisältösivut, oma 404, näppäimistö ja 200 % tekstisuurennus.
- Julkinen PDF: neljä sivua ja SHA-256
  `36762a526ae0a7299098c77e8e64a9ca78d15b4a3ac0b9a4624b7b9e4ad1e69b`.
- Operaattorin seitsemän responsiivista tarkistusta ja erilliset viisi
  muokkaus-/virhetilaregressiota. Yhteydenottopalvelu simuloidaan; viestejä ei lähetetä.

Tämän raportin sisältävä integraatio-PR ja loppuraportissa mainittu commit
yksilöivät testiversion. Uuden commitin CI-tulos tarkistetaan erikseen.
Oikea autentikoitu Preview/Supabase-ajo on **ESTYNYT** eikä sitä merkitä PASSiksi.
Vercel-uudelleenkäynnistyksen yli säilyminen ja hosted-palautus ovat avoinna.

## Arviointiaineiston alkuperä ja riippumattomuus

[Nykyinen uusinta](qa/relevance-replay-2026-10-24.json) käyttää jäädytettyä
19.10.2026 52 ilmoituksen aineistoa. Se on tunnisteiden, menettelyjen ja otsikoiden
osalta erillinen aiemmasta sadasta, mutta samaa historiallista ajanjaksoa ja jo
kehityksessä nähty. Se on regressiouusinta, ei uusi riippumaton holdout.

Vertailuluokitukset ovat lähdeotteisiin sidottuja AI-silver-arvioita. Tarkistetaan
otteiden esiintyminen ja lukitut tiivisteet, mutta tämä ei muuta arvioita
riippumattomaksi goldiksi. Ihmisen gold-luokituksia ja täydellisesti tarkistettuja
tarjousasiakirjapaketteja on edelleen 0. Mallin omia päätöksiä ei käytetä goldina.

Uusi lähdesidonnainen V2: 32 pois rajauksesta, 20 puuttuvan tiedon vuoksi
lykättyä, 0 positiivista ennustetta. Precision on null ja virallinen portti
NOT MEASURED. Nolla väärää positiivista ilman positiivisia ennusteita ei ole
osoitus pilotin hyödystä. Aiemman 30 kohteen AI-lähdearvioportin täydellisiä
arvioita on yhä 0/30; [yhteenveto](qa/source-review-summary-2026-10-24.json).
Jäädytettyjä lähtötietoja tai vertailuluokkia ei muokattu onnistumisen luomiseksi.

## Täsmälliset jäljellä olevat esteet

1. Testiajurin sidonnat ovat nyt saatavilla, mutta julkaistusta kokoonpanosta
   luetut kaksi Preview-kohderajausta osoittavat vanhaan hostiin ja työtila on
   testinimiavaruuden ulkopuolella. Node-proxy-yhteys korjattiin ajureihin;
   sen jälkeen rajattu oikea Supabase-luku palauttaa 401:n. Nimet, ympäristöt
   ja toimenpiteet: [integraatioympäristö](integration-environment.md).
   Vercelin integraatiohaaran palvelinasetuksia ja testiprojektin erillisyyttä
   ei ole pystytty varmentamaan hallintapääsyn puuttuessa. Vanha PR #12 -Preview
   ei vastaa tämän integraation sovelluskoodia.
2. Rajattu siivous-SQL on sovellettava vain hyväksyttyyn Preview-testiprojektiin.
   Sen jälkeen tarvitaan oikea autentikoitu koko työnkulku, HTTP-kilpailu,
   erillinen palautus/siivous ja uudelleenkäynnistyksen jälkeinen luku.
3. Tarvitaan ajantasainen, etukäteen lukittu ja kehitysjoukoista riippumaton
   arviointiaineisto, alkuperäiset täydet asiakirjat sekä riippumattomasti
   tuotetut vertailuluokitukset. Positiivisten ja negatiivisten peitto ja
   puuttuva tieto raportoidaan; sovittua tarkkuusrajaa ei lasketa jälkikäteen.
4. Maksullisen asiakkaan profiili ja kelpoisuus, kriittisten faktavirheiden
   puuttuminen, jäljitettävyys ja todellinen aktiivinen toimitustyöaika
   edellyttävät vielä näyttöä. Työtila on edelleen SIMULATION, ei hyväksytty
   oikean asiakastoimituksen järjestelmä.

Näitä näyttöjä ei voi korvata koodikorjauksella tai synteettisellä läpäisyllä.
Tuotantodataa, tuotantoasetuksia, DNS:ää ja asiakasviestejä ei käsitellä tässä työssä.
