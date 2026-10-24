# P0.3d – Hilman todellisen aineiston alustava Uusimaa-seulonta (19.10.2026)

## Lähteet ja otantamenettely
Tallennetut alkuperäiset Hilman metatieto-otokset:
- `data/validation/snapshot_2026-10-19/hilma_raw.json` – 100 todellista ilmoitusta.
- `data/validation/holdout_52_2026-10-19/holdout_raw.json` – 52 todellista ilmoitusta.

Yhdistelmässä on **152 uniikkia ilmoitustunnusta**. Työkohteeseen viittaava nimistö tunnistettiin otsikon tai kuvauksen tekstistä heuristiikalla; näin löytyi **30 alustavaa tarkistuskohdetta**. Valinta ei ole satunnaisotos eikä itsessään riippumaton 30:n positiivisen osuman Precision@30-holdout.

Varmennettava koneellinen rekisteri: `data/validation/p0_3d_uusimaa_30_candidate_review_queue_2026-10-19.json`.

## Luokittelun tulos
- 30 aitoa, nimetyllä ID:llä tallennettua hankintailmoitusta.
- 8 alustavaa korjaus-/saneerausavainsanan sisältävää vihjettä.
- 12 alustavasti rajauksen ulkopuolista infra-/uudisrakennus-/ympäristötyö-vihjettä.
- 9 epäselvää tai luokittelematonta.
- 1 otsikon perusteella keskeytetty ilmoitus.

Kategorioilla on vain **AI-heuristiikan** asema, ei alkuperäisiin tarjousasiakirjoihin perustuva riippumaton gold-luokka. Mukana voi olla myös *vääriä sijaintiosumia* (paikannimi organisaatiossa tai muualla kuvauksessa) ja keskeytyneitä/vanhentuneita tapauksia. Osan määräaika on päättynyt, joten mitään riviä ei saa lähettää aktiivisena asiakasliidinä pelkän rekisterin perusteella. Työkohteen sijaintia, yksittäisen urakan kokoa ja tarjoajan kelpoisuutta ei ole tämän seulonnan yhteydessä itsenäisesti vahvistettu.

**Ei ole todistettu, että 30 riviä olisi 30 todellista Uudenmaan työkohdetta.** Seuraava vaihe on lähdekohtainen kohteen sijainnin ja korjaustyön sisällön varmennus, jonka jälkeen voidaan laskea aidosti kelvollisen alueellisen aineiston määrä ja laajentaa lähdeotantaa, jos alle 30.

## Toimituskelpoisuuden raja
- Varmennettuja Uudenmaan työkohteita tässä seulonnassa: **0** (ei arvioitu, ei todettu alueen ulkopuolisiksi).
- Täydellisiä tarjouspaketteja: **0**.
- Riippumattomia gold-positiivisia: **0**.
- Precision@30: **null**.
- Ei automaattista kelpoisuus-GO:ta, ei asiakastoimitusta, ei tuotantojulkaisua eikä PR-mergeä.

## Seuraavat tehtävät
1. Lähteiden ensivarmennus: erottele julkiset työkohteeseen osoittavat eksplisiittiset ilmaukset hankintayksikön osoitteesta; tee versiotettu näyttölista (ilmoitus-ID, lähdekenttä, ote, paikkakunta).
2. Tarkista saman menettelyn keskeytetyt, korvaavat ja julkaistut versiot sekä määräajat. Estä vanhat/toistetut ilmoitukset aktiivisina osumina.
3. Tarkista julkisen tarjousportaalin ilmoituskohtaiset kuvaukset ja liitesaatavuus. Kirjautumisen takaiset liitteet jäävät ehdollisiksi.
4. Laajenna aineistohakua todennetulla työmaa-alueella niin kauan, että 30–50 **todistettavaa Uudenmaan työkohdetta** on saatu; älä korvaa puuttuvia näennäisesti sopivilla tapauksilla.
5. Erota myöhempi riippumaton relevanssiluokittelu ja Precision@30 erilliseksi, sokkoutetuksi arvioinniksi.
