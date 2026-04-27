export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-cream-50 mt-24">
      <div className="container py-12 grid gap-8 md:grid-cols-3">
        <div>
          <p className="font-display text-xl text-forest-900">ObRail Europe</p>
          <p className="mt-2 text-sm text-muted-foreground max-w-sm">
            Observatoire indépendant du ferroviaire et de la mobilité durable.
            Au service des institutions européennes depuis 2018.
          </p>
        </div>

        <div>
          <h2 className="font-mono text-xs uppercase tracking-widest text-forest-700">
            Partenaires
          </h2>
          <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
            <li>Commission européenne</li>
            <li>Parlement européen</li>
            <li>Transport &amp; Environment</li>
            <li>Back-on-Track</li>
          </ul>
        </div>

        <div>
          <h2 className="font-mono text-xs uppercase tracking-widest text-forest-700">
            Conformité
          </h2>
          <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
            <li>RGPD — aucune donnée personnelle</li>
            <li>RGAA 4.1 — accessibilité numérique</li>
            <li>Données Open Data</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-border/40">
        <div className="container py-4 flex items-center justify-between text-xs text-muted-foreground">
          <p>© {new Date().getFullYear()} ObRail Europe</p>
          <p className="font-mono">MSPR TPRE532 — Bloc E6.3</p>
        </div>
      </div>
    </footer>
  )
}
