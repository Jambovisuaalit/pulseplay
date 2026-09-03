import Link from "next/link";
import { notFound } from "next/navigation";
import { formatEuro, getTenderById } from "@/lib/tenders";

export default async function TenderPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const tender = getTenderById(decodeURIComponent(id));

  if (!tender) {
    notFound();
  }

  const published = tender.publishedAt ?? tender.published_at ?? "Ei ilmoitettu";
  const requirements = tender.pakolliset_vaatimukset ?? [];
  const risks = tender.sopimusriskit ?? [];

  return (
    <main className="shell tenderShell">
      <div className="tenderTopbar">
        <Link className="backLink" href="/">
          ← Takaisin hankintoihin
        </Link>

        <form action="/api/logout" method="post">
          <button className="secondaryButton headerButton" type="submit">
            Kirjaudu ulos
          </button>
        </form>
      </div>

      <section className="tenderHero">
        <div>
          <p className="eyebrow">TARJOUSPYYNTÖ</p>
          <h1>{tender._title}</h1>
          <p className="muted">{tender._buyer}</p>
        </div>

        <span
          className={
            tender._decision === "GO"
              ? "decisionHero decisionGo"
              : tender._decision.includes("NO-GO")
                ? "decisionHero decisionNo"
                : "decisionHero"
          }
        >
          {tender._decision}
        </span>
      </section>

      <section className="tenderFacts">
        <article className="factCard">
          <span>Ostaja</span>
          <strong>{tender._buyer}</strong>
        </article>
        <article className="factCard">
          <span>Julkaistu</span>
          <strong>{published}</strong>
        </article>
        <article className="factCard">
          <span>Liikevaihtoraja</span>
          <strong>{formatEuro(tender._revenue)}</strong>
        </article>
        <article className="factCard">
          <span>Vasteaika</span>
          <strong>{tender.vasteaika_vaatimus ?? "Ei ilmoitettu"}</strong>
        </article>
      </section>

      <section className="decisionPanel">
        <p className="eyebrow">PÄÄTÖSSUOSITUS</p>
        <h2>{tender._decision}</h2>
        <p>{tender.perustelu ?? "Perustelua ei ole kirjattu."}</p>
      </section>

      {tender.tiivistelma && (
        <section className="singlePanel">
          <p className="eyebrow">TIIVISTELMÄ</p>
          <p className="leadText">{tender.tiivistelma}</p>
        </section>
      )}

      <section className="detailGrid tenderColumns">
        <div className="singlePanel">
          <p className="eyebrow">PAKOLLISET VAATIMUKSET</p>
          <h2>{requirements.length} tunnistettua vaatimusta</h2>

          {requirements.length ? (
            requirements.map((requirement) => (
              <div className="successBox" key={requirement}>
                {requirement}
              </div>
            ))
          ) : (
            <div className="neutralBox">
              Julkisesta aineistosta ei tunnistettu varmaa pakollista vaatimusta.
            </div>
          )}

          {tender.vaatimukset_evidenssi && (
            <div className="evidenceBox">
              <strong>Evidenssi</strong>
              <p>{tender.vaatimukset_evidenssi}</p>
            </div>
          )}
        </div>

        <div className="singlePanel">
          <p className="eyebrow">SOPIMUSRISKIT</p>
          <h2>{risks.length} tunnistettua riskiä</h2>

          {risks.length ? (
            risks.map((risk) => (
              <div className="errorBox" key={risk}>
                {risk}
              </div>
            ))
          ) : (
            <div className="neutralBox">Merkittäviä sopimusriskejä ei tunnistettu.</div>
          )}

          {tender.riskit_evidenssi && (
            <div className="evidenceBox">
              <strong>Evidenssi</strong>
              <p>{tender.riskit_evidenssi}</p>
            </div>
          )}
        </div>
      </section>

      <section className="singlePanel">
        <p className="eyebrow">LIIKEVAIHTOVAATIMUS</p>
        <div className="revenueRow">
          <strong className="revenueValue">{formatEuro(tender._revenue)}</strong>
        </div>

        {tender.liikevaihto_evidenssi && (
          <div className="evidenceBox">
            <strong>Evidenssi</strong>
            <p>{tender.liikevaihto_evidenssi}</p>
          </div>
        )}
      </section>
    </main>
  );
}
