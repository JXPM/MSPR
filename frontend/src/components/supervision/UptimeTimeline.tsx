import type { LatencySample } from '@/hooks/useLatencyMonitor'

interface Props {
  samples: LatencySample[]
  maxDots?: number
}

export function UptimeTimeline({ samples, maxDots = 40 }: Props) {
  const recent = samples.slice(-maxDots)
  const padding = Array.from({ length: Math.max(0, maxDots - recent.length) })

  return (
    <article
      aria-labelledby="uptime-timeline-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Historique
        </p>
        <h2 id="uptime-timeline-title" className="mt-1 font-display text-2xl text-forest-900">
          Disponibilité — {maxDots} dernières sondes
        </h2>
      </header>

      <div
        className="mt-6 flex gap-1 flex-wrap"
        role="img"
        aria-label={`${recent.filter(s => s.status === 'ok').length} sondes OK sur ${recent.length}`}
      >
        {padding.map((_, i) => (
          <span key={`pad-${i}`} className="h-8 w-2.5 rounded-sm bg-muted/40" />
        ))}
        {recent.map((s, i) => (
          <span
            key={i}
            title={`${new Date(s.timestamp).toLocaleTimeString('fr-FR')} — ${
              s.status === 'ok' ? `${s.latencyMs}ms` : 'erreur'
            }`}
            className={`h-8 w-2.5 rounded-sm transition-all ${
              s.status === 'ok' ? 'bg-forest-700' : 'bg-destructive'
            }`}
          />
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
        <span>Plus anciennes</span>
        <span>Plus récentes →</span>
      </div>
    </article>
  )
}
