# Yhden toimituskerran testipaketti – 20.10.2026

Sisäinen testi kuvitteellisella yrityksellä. Ei asiakastoimitusta tai tarjoussuositusta.

## Tuotokset

- `review.json`: versioitu testiprofiili, kolme hankintaa, alkuperäislähteet,
  Suomen aikavyöhykkeellä kirjatut määräajat, fakta/arvio/puuttuva/seuraava askel.
- `sisainen-testikooste.pdf`: neljä tarkastettua A4-sivua ja toimivat lähdelinkit.
- `sahkopostiluonnos.txt`: lähettämätön saate. Ei vastaanottajaosoitetta.
- `qa.json`: koneluettava rakennustarkistus ja lähderekisterin SHA-256.
- Renderöinti: `python scripts/render-reviewed-dry-run.py`.

## Tulos

1 ensisijainen asiakirjatarkistus: Tietotie 59188.
1 toissijainen asiakirjatarkistus: Dynamicum 59230.
1 pidätetty kohde: Kastevuori 59375, pakollinen kohdekäynti vahvistamatta.
0 tarjouskelpoiseksi varmennettua kohdetta, 0 lähetettyä asiakasviestiä.

Julkiset alkuperäisportaalit avattiin verkkotarkistuksessa 20.10.2026:

- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=631619
- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=611165
- https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=624657

Kaikki näyttivät kilpailutuksen yksilöivän nimen, tarjoamis- ja kysymysmääräajan
sekä julkisen kuvauksen. Täydet tiedot edellyttivät kirjautumista.
Sivupohjan yleisiä piilotettuja virhe-/lisenssimodaaleja ei tulkittu
hankinnan keskeytys- tai maksuvaatimukseksi. Ajantasaisten muutosilmoitusten
tai peruutustilan täydellistä ketjua ei tällä tarkistuksella todistettu.

## QA

- Renderöinnin väitteet/avoimet arvot/tunnisteet/aikavyöhykkeet: PASS.
- PDF: 4 sivua; jokaisella tekstiä; kaikki neljä sivua renderöity ja katsottu.
- Lukujen vastaavuus JSON/PDF/saate: 3 arvioitua, 1 ensisijainen, 0 varmennettua.
- Ei uusia riippuvuuksia sovellukseen, tietokantaa, Hilma-API-kutsuja,
  tarjousliitteiden latauksia, kirjautumisia hankintapalveluihin tai sähköpostilähetyksiä.

## Aika ja rajat

Työn aikana talletetut UTC-tarkistuspisteet olivat 00:47:24 ja 00:48:56:
niiden välinen dokumentin valmistelun/renderöinnin osuus 92 sekuntia.
Tämä ei kata ensimmäistä kontekstin lukua ja kaikkia lähdehakuja eikä ole
ihmisen aktiivisen toimitustyön mittaus. Kokonaiselle toimituskerralle ei
ollut käynnistetty erillistä ajastinta; kokonaisminuutteja ei esitetä mitattuina.
Seuraavalla toistokerralla ajastin käynnistetään ennen seulontaa ja pysäytetään
QA:n jälkeen, työvaiheet ja odotus erotellen. 30 päivän kannattavuus ei ole mitattu.

Tuotos osoittaa, että hyödyllinen seuraava tarkistus voidaan esittää myös
puutteellisella lähtöaineistolla. Se ei osoita riittävää osuvuutta tai
maksullisen asiakaspilotin toimitusvalmiutta.

## Seuraava ratkaiseva työ

Tietotien hankintakohtaisten asiakirjojen saatavuus ja tarkistus: urakkaohjelma,
soveltuvuus/referenssit, LVIS-vastuut, kohdekäyntiehto ja urakan koko.
Käytä käyttäjän olemassa olevaa toimittajapääsyä tai julkista asiakirjalähdettä;
älä luo maksullista tilausta tai hyväksy sopimusehtoja automaattisesti.
Kun tiedot on saatu, päivitä vain lähteellä varmennetut faktat ja laske QA uudelleen.
