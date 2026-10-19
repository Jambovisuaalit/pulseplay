# Urakkaluotsi – PR #4:n ja #8:n yhteensovitusarvio

**19.10.2026 – sisäinen tekninen arvio, ei julkaisuhyväksyntä.**

Tarkastellut luonnosmuutokset:

- [PR #4](https://github.com/Jambovisuaalit/pulseplay/pull/4) – `feature/urakkaluotsi-p0-relevance-validation`, vertailuhetken HEAD `94f316670d691b425d7a2004157064863b689b95`.
- [PR #8](https://github.com/Jambovisuaalit/pulseplay/pull/8) – `fix/urakkaluotsi-p0-validation`, vertailuhetken HEAD `7d2ec31b0ddd90efc0c2896198bfb95619e2d789`.
- Molempien pohjahaara on `tenderpulse-mvp`. **Kumpaakaan ei ole yhdistetty eikä julkaistu.**

## Päätös

**Älä yhdistä PR #4:ää sellaisenaan PR #8:aan tai kehityshaaraan.** PR #4:n hyödyllisiä havaintoja voi käsitellä erillisinä, testattuina muutoksina. PR #8:n 100 ilmoituksen metadataotosta ja PR #4:n aiempaa AI-ennakkoarviota **ei saa yhdistää samaksi tilastolliseksi otokseksi**.

## Todetut erot ja riskit

| Prioriteetti | Havainto | Suositus / hyväksymisehto |
|---|---|---|
| P0 | PR #4:n aluerajaus tulkitsee mm. Hyvinkään, Lohjan, Mäntsälän, Sipoon ja Tuusulan alueen sisäpuolelle. Testiasiakkaan hyväksytty toiminta-alue on vain Helsinki, Espoo, Vantaa, Kauniainen ja Kirkkonummi. | Kovaa asiakkaan aluerajausta ei saa laajentaa ilman asiakkaan nimenomaista hyväksyntää. Lisää täsmällisen viiden kunnan regressiotesti. Kaupungin esiintyminen ostajan nimessä ei vahvista työmaan sijaintia. |
| P0 | Hakutuloksen otsikossa voi olla `KESKEYTETTY`, vaikka tarjousmääräaika näyttäisi vielä tulevalta: lähde-ID `59352`. | Lisää keskeytetyn tilan fail-closed-esto molempiin toimituspolkuihin; varmista regressiotesti. Tarkista lisäksi alkuperäinen ilmoitus ennen asiakasnostoa. |
| P0 | PR #4:n valikoima perustuu 152 hakutulokseen, joista 117 aktiivisia ja 100 järjestykseen valittua (GitHub Actions -ajo `39179825192`); PR #8:n 100:n snapshot on eri lähdeajo (artefakti `12155822339`). | Säilytä otokset erillisinä, yksilöi lähteen aikaleima ja hash. Älä vertaa niiden precision-lukuja suorana malliparannuksena tai siirrä luokkia rivin järjestyksen perusteella. |
| P1 | Viisi päällekkäistä tiedostoa: `.github/workflows/tenderpulse-ingest.yml`, `lib/tenders.ts`, `workers/build_validation_set.py`, `workers/fetch_hilma.py`, `workers/score_validation.py`. | Tee muutokset tiedosto kerrallaan regressiotestein. Vältä yhdistämästä PR #4:n vanhempaa precision-porttia, joka voi heikentää PR #8:n sokkoutuksen ja todentamisen ehtoja. |
| P1 | PR #4 havaitsee CPV-tulkinnassa mahdollisen merkkikohtaisen pilkkomisen. | Testaa CPV:n rakenteen säilyminen lähteen lukemisessa ja normalisoinnissa ennen kuin CPV:llä tehdään hylkäyksiä. |
| P1 | PR #4:n `lib/tenders.ts` voi piilottaa vanhentuneet rivit näkymästä, kun PR #8 antaa niille näkyvän `EXPIRED`-tilan. | Varmista, että päättyneet ilmoitukset jäävät auditointiin, mutta niitä ei suositella asiakkaille. |
| P1 | PR #4 muuttaa Hilma-työnkulun manuaalista käynnistystä. | Ei live-Hilma-kutsuja tai ajastetun tuotantoseurannan käynnistämistä ilman erillistä hyväksyntää. |
| P2 | PR #4:n alustavan AI-arvion luokat (5/8/87) ovat eri aineiston ennakkoarvio, eivät vahvistettu vertailutotuus. | Raportoi havaintona, älä virallisena relevanssina. PR #8:n erillinen AI-silver-kierros ei myöskään täytä riippumattoman gold-standardin hyväksyntäehtoa. |

## Rajattu toimintalinja

1. Pidetään PR #8 luonnoksena ja vahvistetaan vain turvallisuuteen kohdistuvat korjaukset regressiotestein.
2. Pidetään yksilöidyt 100 ilmoituksen dataversiot ja niiden mahdolliset AI-luokitukset toisistaan erillään.
3. Uusi offline-toimitussimulaatio näyttää AI-silver-osuvuuden **kokeellisena** ja jättää vahvistetut GO-nostot nollaan niin kauan kuin asiakirjat ja yrityksen kelpoisuus ovat tarkistamatta.
4. Lopullinen asiakkaalle hyväksyntä vaatii lähteistä tarkistetut vaatimukset, erillisen arviointiprosessin ja ensimmäisen oikean asiakkaan tietojen varmentamisen.
