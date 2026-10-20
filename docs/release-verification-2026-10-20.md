# Urakkaluotsi – tuotannon varmennus 20.10.2026

Julkaistu sovelluscommit: `e469658d29b19182fd58b1bc273cf1c797e0dbdf`.
Vercel: `dpl_F7WxE1oVNWwGWZ4toiwJJzhnyeeD`, tenderpulse.
Pääosoite: https://urakkaluotsi.fi/

## Nyt todennettu

- Vercelin DNS-tarkistus: `misconfigured=false`, ei ristiriitoja. Apex A
  `216.198.79.1` ja `64.29.17.1`; vanha `84.34.166.69` ei mukana.
- HTTPS-pääsivu 200; www 308 ja Location `https://urakkaluotsi.fi/`.
- Tietosuojasivu 200, julkinen PDF 200.
- Julkisen PDF:n SHA-256 täsmää repon alkuperäiseen:
  `36762a526ae0a7299098c77e8e64a9ca78d15b4a3ac0b9a4624b7b9e4ad1e69b`.
- Oikeassa tuotantoselaimessa CTA avaa `#hakemus`; tyhjä lomake näyttää
  viisi kenttävirhettä ja kohdistaa fokuksen Yritys-kenttään.
- Tuotannon testilähetys `UL-20261020-0335`: lataustila, sitten oikea
  onnistumisviesti ja kenttien tyhjennys. Gmail-haku vahvisti viestin INBOXissa,
  vastaanottaja visualjambo@gmail.com, Gmail ID `1a156ba446e51da7`.
  Yksi tekninen testiviesti, ei asiakashakemus tai myyntiviesti.
- Kirjautumattoman `/ops` näyttää kirjautumislomakkeen. Tämä ei todista
  onnistunutta operaattorikirjautumista tai tuotantotallennusta.
- Myyntihaaran testit: 23 Node + 18 Python PASS; lint, typecheck ja build PASS.
- 375/390/768/1440 px ja 200 % tekstisuurennus on testattu tämän saman
  sovelluscommitin aiemmassa QA-ajossa (`docs/sales-qa/browser-results.json`).
  Tätä responsiivisuusajoa ei uusittu tässä istunnossa: uuden QA-selaimen
  lataus epäonnistui vioittuneeseen ZIP-vastaukseen. Tuotannon tämänkertainen
  selainajo kattoi CTA:n, kenttävirheet, fokuksen ja oikean lähetyksen desktopilla.
- `scripts/run-pilot.mjs`: 30 synteettistä toimitusta / 90 nostoa PASS.
  Automaation ajoaika ei mittaa ihmistyötä tai asiakashyötyä.

## Portaalin todellinen rajoitus

`lib/server/ops-store.ts` torjuu tuotantokäytön 503-virheellä tarkoituksella.
Paikallista tiedostotallennusta ei oteta käyttöön Vercelissä. Pelkät asetetut
kirjautumistunnukset eivät tee portaalista tuotantovalmiista.
Tarvitaan yksityinen pysyvä tietokanta, sovellusadapteri ja käyttöoikeuksien
varmennus. Oikeita asiakastietoja ei viedä nykyiseen portaaliin.

## Relevanssityön yhteensovitus

Erillisestä haarasta `fix/urakkaluotsi-p0-validation`, commit `c716a15`,
tarkistettiin nykyiset raportit ja ajettiin uudelleen:

```
PYTHONPATH=workers python workers/evaluate_holdout_v2.py
python -m unittest discover -s tests -v
PYTHONPATH=workers python workers/simulate_ai_silver_delivery.py
```

126 Python-testiä PASS. 52 ilmoituksen V2-otos on tunnisteiltaan erillinen
vanhasta 100:sta. Tulos: 31 epärelevanttia ja 21 ei priorisoitua, 0 varmaa
positiivista; AI-silver precision null, virallinen relevanssiportti NOT MEASURED.
Ajallisesti erillinen testi ja täydellisten tarjousasiakirjojen tarkistus puuttuvat.
100 ilmoituksen uusintasimulaatio: 92 NOT_EVALUATED, 7 EXPIRED, 1 CANCELLED,
0 vahvistettua GO:ta. Turvaportit PASS, toimitusvalmius EI HYVÄKSYTTY.
AI-silver-luokat eivät ole riippumaton gold-vertailutotuus.

Näitä haaroja ei yhdistetty eikä seulontakoodia julkaistu tämän tarkistuksen
yhteydessä. Julkaistu myyntisivu ja toimitusmoottorin kehitys pysyvät erillisinä.

## Julkaisun jälkeiset rajat

Myyntisivu voi vastaanottaa alustavia yhteydenottoja. Maksullisen pilotin
aloittaminen edellyttää erillistä toimitusvalmiuden hyväksyntää, yritysprofiilin
varmennusta sekä tietosuojan operatiivisten käytäntöjen käyttöönottoa.
Asiakashankinnan valmistelu: `pilot-intake-preparation-2026-10-20.md`.
Ei kampanjalähetyksiä, asiakaskoosteita tai live-Hilma-kutsuja tässä työssä.
