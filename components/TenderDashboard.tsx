"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { NormalizedTender } from "@/lib/tenders";

function euro(value: number | null) {
  return typeof value === "number"
    ? new Intl.NumberFormat("fi-FI", {
        style: "currency",
        currency: "EUR",
        maximumFractionDigits: 0,
      }).format(value)
    : "Ei löydetty";
}

export default function TenderDashboard({
  notices,
}: {
  notices: NormalizedTender[];
}) {
  const router = useRouter();

  const buyers = useMemo(
    () => Array.from(new Set(notices.map((item) => item._buyer))).sort(),
    [notices],
  );

  const decisions = useMemo(
    () => Array.from(new Set(notices.map((item) => item._decision))).sort(),
    [notices],
  );

  const maxRevenue = useMemo(
    () => Math.max(0, ...notices.map((item) => item._revenue ?? 0)),
    [notices],
  );

  const [buyer, setBuyer] = useState("ALL");
  const [decision, setDecision] = useState("ALL");
  const [revenueLimit, setRevenueLimit] = useState(
    Math.max(maxRevenue, 1_000_000),
  );

  const filtered = useMemo(
    () =>
      notices.filter((item) => {
        const buyerOk = buyer === "ALL" || item._buyer === buyer;
        const decisionOk = decision === "ALL" || item._decision === decision;
        const revenueOk = item._revenue == null || item._revenue <= revenueLimit;
        return buyerOk && decisionOk && revenueOk;
      }),
    [notices, buyer, decision, revenueLimit],
  );

  const goCount = notices.filter((item) => item._decision === "GO").length;
  const goRate = notices.length
    ? Math.round((goCount / notices.length) * 100)
    : 0;

  return (
    <main className="shell">
      <header className="header">
        <div>
          <p className="eyebrow">TENDERPULSE</p>
          <h1>Hankintojen päätöksentekonäkymä</h1>
          <p className="muted">
            Yksi näkymä per tarjouspyyntö: vaatimukset, riskit ja GO / NO-GO.
          </p>
        </div>

        <form action="/api/logout" method="post">
          <button className="secondaryButton headerButton" type="submit">
            Kirjaudu ulos
          </button>
        </form>
      </header>

      <section className="metrics" aria-label="Yhteenveto">
        <article className="metric">
          <span>Uusia ilmoituksia</span>
          <strong>{notices.length}</strong>
        </article>
        <article className="metric">
          <span>GO-suositukset</span>
          <strong>{goCount}</strong>
        </article>
        <article className="metric">
          <span>GO-osuus</span>
          <strong>{goRate}%</strong>
        </article>
      </section>

      <div className="workspace">
        <aside className="filters">
          <h2>Suodattimet</h2>

          <label>
            Ostaja
            <select value={buyer} onChange={(event) => setBuyer(event.target.value)}>
              <option value="ALL">Kaikki</option>
              {buyers.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>

          <label>
            Liikevaihtoraja enintään
            <input
              type="number"
              min={0}
              step={100000}
              value={revenueLimit}
              onChange={(event) => setRevenueLimit(Number(event.target.value) || 0)}
            />
          </label>

          <label>
            GO / NO-GO
            <select value={decision} onChange={(event) => setDecision(event.target.value)}>
              <option value="ALL">Kaikki</option>
              {decisions.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>

          <button
            className="secondaryButton"
            onClick={() => {
              setBuyer("ALL");
              setDecision("ALL");
              setRevenueLimit(Math.max(maxRevenue, 1_000_000));
            }}
          >
            Tyhjennä suodattimet
          </button>
        </aside>

        <section className="content">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">TULOKSET</p>
              <h2>{filtered.length} hankintaa</h2>
            </div>
          </div>

          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>Hankinta</th>
                  <th>Ostaja</th>
                  <th>Deadline</th>
                  <th>Liikevaihtoraja</th>
                  <th>Suositus</th>
                  <th>Riskit</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => (
                  <tr
                    key={item._key}
                    onClick={() => router.push(`/tender/${encodeURIComponent(item._key)}`)}
                  >
                    <td><strong>{item._title}</strong></td>
                    <td>{item._buyer}</td>
                    <td>{item.deadline ?? "Ei löydetty"}</td>
                    <td>{euro(item._revenue)}</td>
                    <td>
                      <span className={
                        item._decision === "GO"
                          ? "badge badgeGo"
                          : item._decision.includes("NO-GO")
                            ? "badge badgeNo"
                            : "badge"
                      }>
                        {item._decision}
                      </span>
                    </td>
                    <td>{(item.sopimusriskit ?? []).length}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filtered.length === 0 && (
              <div className="emptyState">Ei osumia valituilla suodattimilla.</div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
