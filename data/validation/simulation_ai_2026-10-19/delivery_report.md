# Urakkaluotsi – AI-silver-uusintatoimitussimulaatio

SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS

Kuvitteellinen Uudenmaan Korjausrakentajat Oy. Tämä on *yksi* jäädytetty 100
ilmoituksen **offline-toimitusharjoitus**, ei 30 päivän toteutunut seuranta eikä
todellisen asiakkaan toimitus. Aineisto kerätty: 2026-10-19T00:12:27.163249+00:00 UTC.

## Toimituksen määrätilanne

- Lähteestä yksilöityjä ilmoituksia: 100 / 100.
- Määräaika avoin lähdehetkellä: 93;
  päättynyt 7.
- Nimenomaan keskeytetyiksi merkittyjä päätöksiä: 1.
- AI-silver-lähdearvio: {'Epärelevantti': 91, 'Mahdollinen': 7, 'NOT_EVALUATED': 1, 'Relevantti': 1}.
- **Vahvistetut asiakasnostot ja turvallisuusportin GO: 0**.
- Tarjousliitteitä täysin tarkistettu: **0 / 100**. Yrityksen kelpoisuuksia
  vahvistettu: **0**. Ulkoisia gold-luokituksia: **0 / 100**.

## AI-virheanalyysi – vain kehityskäyttöön

Sokkoutetun AI-arvion perusteella baseline-seulonnassa alustavia TP/FP/FN:
1 / 10 /
0 ratkaistuissa tapauksissa.
FP:n epävarmuusväli [10, 14], FN:n epävarmuusväli
[0, 4] ja precisionin koko positiivisen
joukon vaihteluväli [0.0667, 0.3333].

**Virallinen precision >= 80 %: NOT MEASURED.** Tekoälyn arviot eivät ole
riippumattoman arvioijan vahvistamia oikeita luokkia. Algoritmin ja AI:n yhteinen
mahdollinen virhe sekä hakumetadatan aukot jäävät avoimiksi.

## Mahdollinen jatkoselvityskohde – ei tarjoussuositus

- Hilma ID **59188**: *Koy Espoon Tietotie 1, BIZ vuokralaismuutos*;
  ilmoituksessa kuvataan tilojen pintaremonttia Espoossa, mutta myös ilmanvaihto-,
  valaistus- ja muita LVIS-muutoksia. Alkuperäisten asiakirjojen urakkakoko,
  laajuus, vastuunjako, kelpoisuusehdot ja yrityksen soveltuvuus ovat **avoinna**.
  Metadata ilmoittaa tarjousmääräajaksi **2026-11-04T10:00:00Z**; tarkista se
  alkuperäisestä lähteestä ennen mitään toimenpidettä. Ei automaattista GO:ta.
- AI-arviossa lisäksi seitsemän *Mahdollinen*-luokkaa, joita ei ole riittävällä
  lähdevarmuudella osoitettu sopiviksi.
- Kohde `59352` sisältää sanan **KESKEYTETTY** vaikka hakumetadatan määräaika
  on tuleva: turvaportti antaa `CANCELLED` eikä GO.

## QA

- expired_recommended_as_GO: **PASS**
- unreviewed_annexes_recommended_as_GO: **PASS**
- all_source_ids_traceable: **PASS**
- independent_precision_gate: **NOT TESTED**
- actual_customer_eligibility: **NOT TESTED**
- customer_send: **NOT TESTED (prohibited for internal pilot)**
- cancelled_recommended_as_GO: **PASS**
- ai_review_never_claims_gold: **PASS**
- source_label_and_metric_hashes: **PASS**
- annexes_actually_reviewed: **NOT TESTED**
- company_eligibility_actually_confirmed: **NOT TESTED**
- unverified_worksite_location: **NOT TESTED**
- published_or_sent: **NOT TESTED (explicitly prohibited)**

Toimituspäätökset, lähdetunnisteet, AI-luokat, avoimet seikat ja seuraavat
toimet löytyvät `classified_notices.csv`-taulukosta. PDF on tuotettu olemassa
olevalla Urakkaluotsin koostepohjalla. Asiakassähköpostia **ei lähetetä**.

**Johtopäätös:** tekninen turvaportti **CONDITIONAL PASS**, mutta ensimmäinen
maksava asiakastoimitus **EI HYVÄKSYTTY**. Puuttuva itsenäinen totuus,
tarjousasiakirjat, asiakaskelpoisuus ja AI-havainnoissa näkyvä heikko osuvuus
estävät valmiusväitteen. PR #4 ja #8 pysyvät yhdistämättä.
