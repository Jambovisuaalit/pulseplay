# P0 – tekoälyavusteinen sokkoarviointi ilman ulkopuolista arvioijaa

Päiväys: 19.10.2026.

## Päätös
Ulkopuolista henkilöä ei tarvita. Käytetään **AI-silver / lähteisiin sidottua tekoälyarviota**, erotettuna ihmisarvioidusta goldista. Mittari nimetään `AI_SOURCE_REVIEWED_PRECISION_AT_30`, eikä sitä markkinoida ihmisen riippumattomasti vahvistamana.

## Lukittu mallijono
- Valintalähde `data/validation/independent_100/predictions.csv`, 100 alkuperäistä ennustetta.
- Järjestys: pisteet laskevaan järjestykseen, tasapisteissä ilmoitustunnus kasvavaan järjestykseen.
- `data/validation/p0_frozen_ranked_100_2026-10-19.json` tallentaa 100-rivisen mallijärjestyksen ilman AI-arviointia.
- `workers/evaluate_p0_blind_ai_source_review.py` lukitsee ensimmäiset 30 ID:tä ja tekee SHA-256-jäljen.
- Sokkoutetun arvioijan syötteeseen EI liitetä alkuperäistä mallipistettä, sijoitusta tai mallin Relevantti/Mahdollinen-luokkaa. Arvioija ei valitse uusia kohteita palautusten mukaan.
- Erilliset julkaisut `59352` (keskeytetty) ja `59399` (uusi kilpailu) säilyvät lukitun rankingin auditoinnissa, mutta peruutus huomioidaan automaattisesti negatiiviseksi vain jos se on varmennettu alkuperäisestä lähteestä kyseisen arviointihetken mukaan.

## Lähdearvion vaatimukset
Jokaiselta 30 kohteelta vaaditaan erikseen ja lähteestä todennettuna: `worksite`, `scope`, `deadline`, `contract_value`, `eligibility`. Tallenna jokaisesta lähde-URL, sanatarkka ote ja pääsyn varmennusstatus. Vain alkuperäiseen hankintaan ja tarjousosaan todistettavasti yhdistetyt asiakirjat kelpaavat täydelliseen AI-arviointiin. Osin puuttuvan tiedon tulos on `UNKNOWN` eikä valheellinen positiivinen tai negatiivinen.

AI-arviot kirjoitetaan erilliseen `data/validation/p0_blind_ai_silver_reviews_2026-10-19.json` -rekisteriin. Lähtötilassa lista on tarkoituksellisesti tyhjä, koska täydellistä 30 alkuperäisen hankinnan aineistoa ei ole toimitettu tai noudettu.

## Hyväksyntä
- Tulos mitataan vasta, kun kaikilla lukituilla 30 kohteella on täydellinen dokumentoitu AI-lähdearvio.
- `PASS` jos vähintään 24/30 `RELEVANT` ilman puuttuvia tarkistuksia.
- `AI-silver PASS` on sisäinen koeportti eikä asiakkaan yrityskohtaisen kelpoisuuden varmistus.
- Ihmisen arvioimaa `gold`-arvoa ei oleteta eikä vaadita tässä AI-only-mallissa; `human_gold_precision_at_30=null`.

## Nykyinen todennettu tila
- Ranking 100/100 lukittu; 30 tarkistus-ID:tä poimittavissa.
- Dokumenttien ja kelpoisuuden täydellisyys 30/30 puuttuu.
- Täysiä sokkoutettuja lähdearvioita 0/30.
- AI Precision@30 = null; 80 %:n raja ei ole vielä testattu.
- PR #8 on luonnos, tuotantoa ja asiakastoimituksia ei muuteta.
