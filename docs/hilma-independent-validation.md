# Hilma 100 — riippumaton relevanssiarviointi

Lähtöaineisto: tallennettu Hilma-keruu, GitHub Actions run 39179825192 (152 hakutulosta, 117 aktiivista, pisteytyksessä 100 ensimmäistä aktiivista). Arviointijoukko on jäädytetty ennen luokittelua.

## Arvioitava saneeraus-ICP (testiolettama)

Kuvitteellinen Uudenmaan pieni tai keskisuuri saneerausurakoitsija: huoneisto-, toimitila-, pinta-, korjaus- ja peruskorjausurakat. Raskas infra ja erityisen suuret kokonaisurakat eivät oletusarvoisesti sovi. Kapasiteetti ja tarjousalue ovat testiolettamia.

## Sokkoutetun arvioijan ohje

1. Avaa vain hilma_100_blind_review.csv. Älä näytä arvioijalle rank-, priority_score-kenttiä, pisteytyskoodia tai ennustettuja luokkia.
2. Arvioi kaikki 100 ilmoitusta tallennetun Hilma-otsikon, kuvauksen, CPV:n ja määräajan pohjalta. Jos tietoa ei riitä, valitse Mahdollinen.
3. Luokat manual_label: Relevantti, Epärelevantti, Mahdollinen.
4. Kirjaa jokaiselle arvioidulle riville manual_reason (perustelu), source_evidence (lainaus/viite Hilma-kenttään), reviewer_id ja independent_attestation = kyllä, jos arvio on aidosti riippumaton pisteytysmallista.
5. Epärelevantille yksi error_type: scope_mismatch, geography_mismatch, scale_mismatch, expired_or_invalid, insufficient_details, duplicate tai other.
6. Älä täytä riippumattomuusvakuutusta AI-mallin omille luokituksille. Epäselvät tapaukset sovitellaan toisen ulkopuolisen arvioijan kanssa ja muutos perustellaan.
7. Säilytä täsmälleen 100 tunnistetta ja arvioi kaikki. Sokkoutus ei yksin todista arvioijan riippumattomuutta.

## Laskenta

Valmistele lomake puretun tallennetun artefaktin hakemistossa:

    python -m workers.independent_validation prepare

Kun arvioija on täyttänyt CSV:n:

    python -m workers.independent_validation score

Tuloksena data/validation/independent_precision_at_30.json.

- TP@30 = sijojen 1–30 Relevantti.
- FP@30 = sijojen 1–30 Epärelevantti.
- FN (joukon sisäinen) = sijojen 31–100 Relevantti.
- Precision@30 = TP@30 / 30, vain jos kaikki top 30 -luokat ovat yksiselitteisiä.
- PASS: kaikki 100 luokiteltu, top 30 yksiselitteinen, vähintään 24/30 relevanttia.
- NOT_VALIDATED: keskeneräinen aineisto tai top 30 sisältää Mahdollinen.
- FAIL: koko joukko arvioitu ja top 30 yksiselitteinen, mutta alle 24 relevanttia.

FN ei mittaa hakuvaiheessa noutamatta jääneitä Hilma-kohteita. Riippumattomuusvakuutus ja lähdenäyttö tarkastetaan erikseen. Todellinen Precision@30 on todentamatta, kunnes riippumaton luokittelu on tehty.
