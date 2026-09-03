export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string; config?: string }>;
}) {
  const query = await searchParams;

  return (
    <main className="loginShell">
      <section className="loginCard">
        <p className="eyebrow">TENDERPULSE</p>
        <h1>Kirjaudu hankintanäkymään</h1>
        <p className="muted">
          Syötä asiakastunnus ja salasana nähdäksesi analysoidut tarjouspyynnöt.
        </p>

        {query.error && (
          <div className="errorBox">Tunnus tai salasana on virheellinen.</div>
        )}

        {query.config && (
          <div className="errorBox">
            Kirjautumista ei ole vielä konfiguroitu palvelimelle.
          </div>
        )}

        <form className="loginForm" action="/api/login" method="post">
          <label>
            Käyttäjätunnus
            <input
              autoComplete="username"
              name="username"
              required
              type="text"
            />
          </label>

          <label>
            Salasana
            <input
              autoComplete="current-password"
              name="password"
              required
              type="password"
            />
          </label>

          <button className="primaryButton" type="submit">
            Kirjaudu
          </button>
        </form>
      </section>
    </main>
  );
}
