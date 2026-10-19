# Pilotin mittarointi

Uusi `/ops`-osion mittaripaneeli tallentaa aktiivisen työn ajastimet, korjaustapahtumat ja toimitusversion nostokohtaisen palautteen. Paikallinen käyttö on edelleen SIMULATION. Tuotantotietokantaa, oikeaa pilottiasiakasta tai ulkoista lähettämistä ei ole kytketty.

## Mittarien määritelmät

- **Ihmistyöaika:** vain päättyneet, käyttäjän käynnistämät DELIVERY-ajastinjaksot. Tauot pysäytetään. ONBOARDING on erillinen. Avoin ajastin ei vielä kasvata tulosta. Yksi aktiivinen ajastin estää päällekkäisen laskennan. Työajan kohdistus on aloituspäivään Helsingin ajassa; pysäytä ajastin viimeistään päivän vaihtuessa.
- **Minuutit / asiakas / päivä:** aktiiviset toimitussekunnit / ajastettujen asiakaspäivien lukumäärä / 60. Ajastamattomia päiviä ei merkitä nollaksi. Yhden automatisoidun ajon kesto ei ole ihmistyöaika. Tavoite alle 10 min tarvitsee oikean työpilotoinnin näytön.
- **Korjausten määrä:** eksplisiittiset korjauskirjaukset vietyä sisältöversiota kohden. Syyt SOURCE/PROFILE/CONTENT/EXPORT. Useampi syy on useampi tapahtuma; korjattujen toimitusten osuus lasketaan erikseen. Rutiininomainen uuden tiedon päivitys ei automaattisesti ole virhekorjaus.
- **Hyödylliset osumat:** palaute on sidottu digest-ID:hen, sisältöhashiin ja assessment-ID:hen. Uusin palaute korvaa mittarissa aiemman, mutta alkuperäiset rivit säilyvät. Vanhan sisältöversion palaute ei siirry korjattuun versioon.
- **Nimittäjä:** kunkin koosteen viimeisimmän viedyn version nostot. Saman version PDF/HTML/EML-uusintavienti ei moninkertaista nostoja. Kaikki viedyt sisältöversiot näkyvät erillisenä lukuna.
- **Arvioimatta:** UNKNOWN ja puuttuva palaute erotetaan. Hyödyllisyysosuus on USEFUL / (USEFUL + NOT_USEFUL); älä piilota palautteen kattavuutta.
- **Asiakashyöty:** paikallisessa simulaatiossa aina NOT_MEASURED. INTERNAL_SIMULATION ei ole asiakaspalaute, mallin precision, tarjousvoitto tai kysynnän validointi. CUSTOMER-kirjaus hylätään tässä työtilassa.

Tietokantasopimukseen lisätty `work_sessions`, `delivery_corrections` ja `feedback` RLS-sääntöineen (`database/05-measurements.sql`). Ajastin saa vain päättymisajan kerran; korjaukset ja palautteet ovat lisättäviä historiarivejä. Pilviskeeman CUSTOMER-palaute vaatii REAL-toimituksen, saman noston ja kirjatun lähetyksen. Sovellusadapteri ei ole vielä kytketty pilveen.

## Suoritettu simulaatio

Aja `node --experimental-strip-types scripts/run-pilot.mjs`.

Ajo simuloi 30 toimituspäivää, 90 synteettistä nostoa ja kaksi tarkoituksella lisättyä korjausskenaariota. Se mittaa oikean automaation seinäkelloajan perf_hooks-kellolla, generoi PDF/HTML/TXT/EML/JSON-viennit ja tarkistaa mittarilaskennan. Ei API-, LLM- tai sähköpostikutsuja. Työnkulun virtuaaliaika ja automaation todellinen ajoaika pidetään erillään.

Nostojen hyötyluokat ovat skriptin alussa ilmoitettuja testikontrolleja, eivät mallin arvioita tai oikeaa hankinta-aineistoa. 30 positiivista, 30 negatiivista ja 30 epäselvää kontrollia todentavat laskennan. Niiden 50 %:n osuus arvioiduista ei mittaa tuotteen todellista relevanssia. Vääriä negatiivisia ei mitata, koska tämä ei ole riippumaton ilmoitusuniversumin relevanssitesti.

Tulokset: `docs/pilot-measurement-report.md` ja koneluettava `docs/pilot-measurement-results.json`. Viennit ovat `qa-output/pilot/`-hakemistossa ja CI-artifactissa. Raportin kaksi korjausskenaariota eivät ole kaksi tuotannosta havaittua virhettä. Valmistelussa havaittiin erillinen kellonvälityksen virhe, joka korjattiin ja regressiotestattiin.

## Todellisen pilotin aloitus

Vahvistettu pilottiasiakas ja profiili, yksityinen tuotantotallennus sekä käyttöoikeudet ovat riippuvuuksia. Mittaa vähintään viisi todellista toimituskertaa ennen työaikaa koskevaa arviota; raportoi mediaani, p95 ja otoskoko, ei pelkkää tavoitetta. Kerää palautetta jokaisesta nostosta. Tavoite ≥80 % hyödyllisiä arvioiduista, ≥80 % palautepeitto ja nolla kriittistä asiakasvirhettä; pienellä otoksella tulos on suuntaa antava. Alkuperäinen riippumaton 100 ilmoituksen relevanssitesti on erillinen hyväksyntä.
