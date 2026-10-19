# P0: ehdollisten osumien tarkentaminen

Tila: toteutuksen vaatimusmäärittely; ei väitetä koodikorjaukseksi.

## Kenttäkohtainen näyttö

- worksite_location: kunta, lähdekenttä, täsmällinen lainaus, asiakirjan tunniste; ostajan kotipaikka ei kelpaa.
- contract_value: euroarvo, alv-status, arvon tyyppi (single_contract / framework_total / lot_total / unknown), lähdelainaus; pelkkä arvioitu kokonaishinta ei kelpaa yksittäiseksi urakaksi.
- scope: primary_work, included_minor_work, excluded_primary_work, evidence; uudisrakentaminen, infra, kattourakka, laajat LVISA-työt ja ikkuna-/ovikokonaisvaihto poissuljettu.

## Päätössäännöt

1. Todistettu toiminta-alueen ulkopuolinen työmaa, kielletty pääasiallinen työ tai todistettu yksittäisen urakan raja-arvon ylitys => Epärelevantti.
2. Vain lähteessä osoitetut viisi kuntaa + sopiva päätyö + vahvistettu yksittäisen urakan arvo 10 000–250 000 EUR => Relevantti (ei asiakastoimituksen GO).
3. Puuttuva ratkaiseva näyttö => Mahdollinen, mutta reason-code kertoo, mitä tietoa tarvitaan; ei automaattista asiakasnostoa.
4. Puitejärjestelyn kokonaisarvoa ei saa tulkita yksittäisen työn arvoksi.
5. Keskeytetty tai päättynyt tarjous => ei asiakasnostoa.

## Testi- ja hyväksyntäportti

- Käytä jäädytettyä 52 ilmoituksen otosta vain regressiotestinä; uusi ajallisesti erillinen holdout tarvitaan vaikutuksen vahvistamiseen.
- Mittaa conditional_total, conditional_ai_negative, confirmed_positive, FP, FN, unknown ja työaika.
- Tavoite conditional_total <=10/52 ja conditional_ai_negative <=5/52; nolla FP:tä ei riitä, jos kaikki relevantit jäävät nostamatta.
- AI-silver on alustava vertailu; ei virallinen riippumaton gold.
- Ei mergeä, live-kutsuja, sähköposteja tai tuotantojulkaisua.
