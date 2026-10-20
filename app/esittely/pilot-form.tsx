"use client";

import { useRef, useState } from "react";
import { contactFields, PILOT_EMAIL, validateContact, type ContactErrors } from "./contact";

export default function PilotForm() {
  const pending = useRef(false);
  const [errors, setErrors] = useState<ContactErrors>({});
  const [notice, setNotice] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;
    const form = event.currentTarget;
    const result = validateContact(new FormData(form));
    setErrors(result.errors);
    setNotice("");
    if (Object.keys(result.errors).length) {
      setNotice("");
      const firstInvalid = contactFields.find(field => result.errors[field.name]);
      if (firstInvalid) form.querySelector<HTMLElement>(`[name="${firstInvalid.name}"]`)?.focus();
      return;
    }
    pending.current = true;
    setSending(true);
    try {
      const response = await fetch("/esittely/api/contact", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...result.values, website: (new FormData(form).get("website") || "") }), signal: AbortSignal.timeout(15000) });
      const payload = await response.json().catch(() => null);
      if (!response.ok || !payload?.success) {
        if (payload?.errors) {
          setErrors(payload.errors);
          const first = contactFields.find(field => payload.errors[field.name]);
          if (first) form.querySelector<HTMLElement>(`[name="${first.name}"]`)?.focus();
        }
        setNotice(payload?.error || "Viestin lähetys epäonnistui."); return;
      }
      setNotice("Kiitos yhteydenotosta. Käymme tiedot läpi ja palaamme pilotin soveltuvuuteen, sisältöön ja hintaan.");
      form.reset();
    } catch { setNotice("Lähetys epäonnistui. Lähetä sähköpostia suoraan."); }
    finally { pending.current = false; setSending(false); }
  }

  return <form id="hakemus" tabIndex={-1} aria-busy={sending} className="ul-form" onSubmit={handleSubmit} noValidate method="post" aria-labelledby="form-title">
    <span className="ul-form-tag">PILOTTIKESKUSTELU</span><h2 id="form-title">Selvitetään, sopiiko pilotti yrityksellesi.</h2>
    <p>Kerro lyhyesti, millaisia töitä teette ja millä alueella toimitte. Kaikki kentät ovat pakollisia. Älä kirjoita arkaluonteisia henkilötietoja.</p>
    <noscript><p>Lomakkeen lähetys tarvitsee JavaScriptin. Voit lähettää yhteydenoton suoraan osoitteeseen <a href={`mailto:${PILOT_EMAIL}`}>{PILOT_EMAIL}</a>.</p><style>{".ul-form-fields{display:none}"}</style></noscript>
    <div className="ul-form-fields">
      {Object.keys(errors).length > 0 ? <p className="ul-error-summary" role="alert">Tarkista merkityt kentät. Viestiä ei lähetetty.</p> : null}
      <div className="ul-form-grid">
        {contactFields.map(field => {
          const id = `pilot-${field.name}`;
          const props = { id, name: field.name, required: true, maxLength: field.max, autoComplete: field.autoComplete, placeholder: field.placeholder,
            "aria-invalid": Boolean(errors[field.name]), "aria-describedby": errors[field.name] ? `${id}-error` : undefined,
            onChange: () => { setNotice(""); setErrors(current => ({ ...current, [field.name]: undefined })); },
          };
          return <div className={field.name === "company" || field.name === "name" ? "ul-field" : "ul-field ul-field-wide"} key={field.name}>
            <label htmlFor={id}>{field.label}</label>
            {field.name === "work" ? <textarea {...props} rows={3} /> : <input {...props} type={field.name === "email" ? "email" : "text"} />}
            {errors[field.name] ? <p className="ul-field-error" id={`${id}-error`}>{errors[field.name]}</p> : null}
          </div>;
        })}
      </div>
      <div className="ul-honeypot" aria-hidden="true" style={{position:"absolute",left:"-10000px"}}><label htmlFor="pilot-website">Verkkosivu</label><input id="pilot-website" name="website" type="text" tabIndex={-1} autoComplete="off" /></div>
      <p className="ul-privacy-inline">Tietojasi käytetään pilottiyhteydenoton käsittelyyn. Lue <a href="/esittely/tietosuoja">tietosuojaseloste</a> ennen viestin lähettämistä.</p>
      <button className="ul-btn" type="submit" disabled={sending}>{sending ? "Lähetetään…" : "Lähetä pilottihakemus"}</button>
      <p className="ul-form-info" role="status" aria-live="polite">{notice || "Hakemus ei ole sitova tilaus."}</p>
    </div>
    <p className="ul-contact-fallback">Voit myös kirjoittaa suoraan: <a href={`mailto:${PILOT_EMAIL}`}>{PILOT_EMAIL}</a>.</p>
  </form>;
}
