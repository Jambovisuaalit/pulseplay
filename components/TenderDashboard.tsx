"use client";

import { useMemo, useState } from "react";
import type { Tender } from "@/types/tender";

type NormalizedTender = Tender & {
  _key: string;
  _title: string;
  _buyer: string;
  _revenue: number;
  _decision: string;
};

function normalizeTender(item: Tender, index: number): NormalizedTender {
  const organisationName =
    typeof item.organisation === "object" && item.organisation
      ? item.organisation.name
      : typeof item.organisation === "string"
        ? item.organisation
        : undefined;

  const decision = String(item.go_no_go_suositus ?? "EI ARVIOITU").toUpperCase();

  return {
    ...item,
    _key: String(item.id ?? item.notice_id ?? index),
    _title: item.title ?? item.hankinta ?? "Ei otsikkoa",
    _buyer: item.ostaja ?? item.buyer ?? organisationName ?? "Ei ilmoitettu",
    _revenue: Number(item.liikevaihto_vaatimus_eur ?? 0) || 0,
    _decision: decision,
  };
}

function euro(value: number) {
  return value > 0
    ? new Intl.NumberFormat("fi-FI", {
        style: "currency",
        currency: "EUR",
        maximumFractionDigits: 0,
      }).format(value)
    : "Ei ilmoitettu";
}

export default function TenderDashboard({ notices }: { notices: Tender[] }) {
  const normalized = useMemo(
    () => notices.map((item, index) => normalizeTender(item, index)),
    [notices],
  );

  const buyers = useMemo(
    () => Array.from(new Set(normalized.map((item) => item._buyer))).sort(),
    [normalized],
  );

  const decisions = useMemo(
    () => Array.from(new Set(normalized.map((item) => item._decision))).sort(),
    [normalized],
  );

  const datasetMaxRevenue = useMemo(
    () => Math.max(0, ...normalized.map((item) => item._revenue)),
    [normalized],
  );

  const [buyer, setBuyer] = useState("ALL");
  const [decision, setDecision] = useState("ALL");
  const [revenueLimit, setRevenueLimit] = useState<number>(
    Math.max(datasetMaxRevenue, 1_000_000),
  );
  const [selectedKey, setSelectedKey] = useState<string | null>(null);

  const filtered = useMemo(
    () =>
      normalized.filter((item) => {
        const buyerOk = buyer === "ALL" || item._buyer === buyer;
        const decisionOk = decision === "ALL" || item._decision === decision;
        const revenueOk = item._revenue <= revenueLimit;
        return buyerOk && decisionOk && revenueOk;
      }),
    [normalized, buyer, decision, revenueLimit],
  );

  const selected =
    filtered.find((item) => item._key === selectedKey) ??
    normalized.find((item) => item._key === selectedKey) ??
    null;

  const goCount = normalized.filter((item) => item._decision === "GO").length;
  const goRate = normalized.length ? Math.round((goCount / normalized.length) * 100) : 0;

  return (
    <main className="shell">
      <header className="header">
        <div>
          <p className="eyebrow">TENDERPULSE MVP</p>
          <h1>Hankintojen päätöksentekonäkymä</h1>
          <p className="muted">
            Hilma-aineisto → vaatimukset → riskit → GO / NO-GO
          </p>
        </div>
      </header>

      <section className="metrics" aria-label="Yhteenveto">
        <article className="metric">
          <span>Uusia ilmoituksia</span>
          <strong>{normalized.length}</strong>
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
                <option key={item} value={item}>
                  {item}
                </option>
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
            <select
              value={decision}
              onChange={(event) => setDecision(event.target.value)}
            >
              <option value="ALL">Kaikki</option>
              {decisions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <button
            className="secondaryButton"
            onClick={() => {
              setBuyer("ALL");
              setDecision("ALL");
              setRevenueLimit(Math.max(datasetMaxRevenue, 1_000_000));
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
                  <th>Liikevaihtoraja</th>
                  <th>Suositus</th>
                  <th>Riskit</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item) => {
                  const risks = item.sopimusriskit ?? [];
                  const isSelected = selectedKey === item._key;

                  return (
                    <tr
                      key={item._key}
                      className={isSelected ? "selectedRow" : ""}
                      onClick={() => setSelectedKey(item._key)}
                    >
                      <td>
                        <strong>{item._title}</strong>
                      </td>
                      <td>{item._buyer}</td>
                      <td>{euro(item._revenue)}</td>
                      <td>
                        <span
                          className={
                            item._decision === "GO"
                              ? "badge badgeGo"
                              : item._decision.includes("NO-GO")
                                ? "badge badgeNo"
                                : "badge"
                          }
                        >
                          {item._decision}
                        </span>
                      </td>
                      <td>{risks.length}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {filtered.length === 0 && (
              <div className="emptyState">Ei osumia valituilla suodattimilla.</div>
            )}
          </div>

          {selected ? (
            <section className="detail">
              <div className="detailHeader">
                <div>
                  <p className="eyebrow">VALITTU HANKINTA</p>
                  <h2>{selected._title}</h2>
                  <p className="muted">{selected._buyer}</p>
                </div>
                <span
                  className={
                    selected._decision === "GO"
                      ? "badge badgeGo"
                      : selected._decision.includes("NO-GO")
                        ? "badge badgeNo"
                        : "badge"
                  }
                >
                  {selected._decision}
                </span>
              </div>

              {selected.tiivistelma && (
                <div className="detailBlock">
                  <h3>Tiivistelmä</h3>
                  <p>{selected.tiivistelma}</p>
                </div>
              )}

              {selected.perustelu && (
                <div className="detailBlock">
                  <h3>Perustelu</h3>
                  <p>{selected.perustelu}</p>
                </div>
              )}

              <div className="detailGrid">
                <div>
                  <h3>Pakolliset vaatimukset</h3>
                  {(selected.pakolliset_vaatimukset ?? []).length ? (
                    (selected.pakolliset_vaatimukset ?? []).map((requirement) => (
                      <div className="successBox" key={requirement}>
                        {requirement}
                      </div>
                    ))
                  ) : (
                    <div className="neutralBox">Ei tunnistettuja vaatimuksia.</div>
                  )}
                </div>

                <div>
                  <h3>Sopimusriskit</h3>
                  {(selected.sopimusriskit ?? []).length ? (
                    (selected.sopimusriskit ?? []).map((risk) => (
                      <div className="errorBox" key={risk}>
                        {risk}
                      </div>
                    ))
                  ) : (
                    <div className="neutralBox">Ei tunnistettuja riskejä.</div>
                  )}
                </div>
              </div>
            </section>
          ) : (
            <div className="emptyDetail">
              Valitse taulukosta hankinta nähdäksesi vaatimukset ja riskit.
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
