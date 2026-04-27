import { Activity, CheckCircle2, AlertCircle, Loader2, Pause, Play, RotateCcw } from 'lucide-react'
import { useLatencyMonitor } from '@/hooks/useLatencyMonitor'
import { LatencyChart } from '@/components/supervision/LatencyChart'
import { UptimeTimeline } from '@/components/supervision/UptimeTimeline'
import { EndpointStatusList } from '@/components/supervision/EndpointStatusList'
import { StatCard } from '@/components/dashboard/StatCard'
import { Button } from '@/components/ui/button'

export function Supervision() {
  const {
    samples,
    uptime,
    avgLatency,
    okCount,
    errorCount,
    lastSample,
    isRunning,
    pause,
    resume,
    reset,
  } = useLatencyMonitor(10_000, 60)

  const currentStatus: 'ok' | 'down' | 'unknown' = !lastSample
    ? 'unknown'
    : lastSample.status === 'ok'
      ? 'ok'
      : 'down'

  return (
    <div className="container py-12">
      {/* Header */}
      <header>
        <p className="font-mono text-xs uppercase tracking-[0.25em] text-forest-700">
          Observabilité · 04
        </p>
        <h1 className="mt-2 font-display text-5xl md:text-6xl text-forest-900">
          Supervision
        </h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          Surveillance en temps réel de l'API ObRail. Une sonde{' '}
          <code className="font-mono text-xs bg-muted px-1 py-0.5 rounded">/health</code>
          {' '}est émise toutes les 10 secondes. L'historique glissant retient les 60
          dernières sondes (soit 10 minutes).
        </p>
      </header>

      {/* Bandeau principal : statut + contrôles */}
      <section
        aria-labelledby="status-title"
        className={`mt-10 rounded-lg border p-6 transition-colors ${
          currentStatus === 'ok'
            ? 'bg-forest-900 text-cream-50 border-forest-900'
            : currentStatus === 'down'
              ? 'bg-destructive/10 border-destructive/30'
              : 'bg-muted border-border'
        }`}
      >
        <h2 id="status-title" className="sr-only">Statut général</h2>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="flex items-center gap-5">
            <StatusBadge status={currentStatus} />
            <div>
              <p
                className={`font-mono text-[10px] uppercase tracking-[0.2em] ${
                  currentStatus === 'ok' ? 'text-cream-50/60' : 'text-muted-foreground'
                }`}
              >
                API backend
              </p>
              <p className="mt-1 font-display text-3xl md:text-4xl">
                {currentStatus === 'ok' && 'Opérationnel'}
                {currentStatus === 'down' && 'Indisponible'}
                {currentStatus === 'unknown' && 'Vérification…'}
              </p>
              {lastSample && (
                <p
                  className={`mt-2 font-mono text-xs ${
                    currentStatus === 'ok' ? 'text-cream-50/50' : 'text-muted-foreground'
                  }`}
                >
                  Dernière sonde :{' '}
                  {new Date(lastSample.timestamp).toLocaleTimeString('fr-FR')} —{' '}
                  {lastSample.status === 'ok' ? `${lastSample.latencyMs}ms` : lastSample.error}
                </p>
              )}
            </div>
          </div>

          {/* Contrôles monitoring */}
          <div className="flex items-center gap-2">
            {isRunning ? (
              <Button
                variant={currentStatus === 'ok' ? 'secondary' : 'outline'}
                size="sm"
                onClick={pause}
              >
                <Pause className="h-4 w-4" aria-hidden="true" />
                Pause
              </Button>
            ) : (
              <Button
                variant={currentStatus === 'ok' ? 'secondary' : 'outline'}
                size="sm"
                onClick={resume}
              >
                <Play className="h-4 w-4" aria-hidden="true" />
                Reprendre
              </Button>
            )}
            <Button
              variant={currentStatus === 'ok' ? 'secondary' : 'outline'}
              size="sm"
              onClick={reset}
            >
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
              Réinitialiser
            </Button>
          </div>
        </div>
      </section>

      {/* KPIs monitoring */}
      <section className="mt-6 grid gap-4 grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Disponibilité"
          value={uptime !== null ? `${uptime}%` : '—'}
          icon={Activity}
          hint={`${okCount}/${samples.length} sondes OK`}
          accent={uptime !== null && uptime >= 99 ? 'forest' : 'default'}
        />
        <StatCard
          label="Latence moyenne"
          value={avgLatency !== null ? `${avgLatency} ms` : '—'}
          icon={Activity}
          hint="moyenne des sondes OK"
        />
        <StatCard
          label="Erreurs"
          value={errorCount}
          icon={AlertCircle}
          hint="sur la fenêtre glissante"
          accent={errorCount > 0 ? 'rust' : 'default'}
        />
        <StatCard
          label="Sondes collectées"
          value={samples.length}
          icon={Activity}
          hint="sur 60 max."
        />
      </section>

      {/* Graphes */}
      <section className="mt-6 grid gap-6 lg:grid-cols-2">
        <LatencyChart samples={samples} avgLatency={avgLatency} />
        <UptimeTimeline samples={samples} maxDots={40} />
      </section>

      {/* Endpoints */}
      <section className="mt-6">
        <EndpointStatusList />
      </section>

      {/* Note MLOps */}
      <aside className="mt-10 border-l-2 border-forest-700 pl-4 py-2 max-w-3xl">
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Observabilité native
        </p>
        <p className="mt-2 text-sm text-muted-foreground italic leading-relaxed">
          Cette page fournit une supervision légère côté client. Pour une observabilité
          industrielle conforme aux exigences MLOps du cahier des charges (métriques
          persistées, alerting, logs centralisés), l'écosystème{' '}
          <span className="font-mono not-italic">Prometheus + Grafana + Loki</span>{' '}
          est intégré dans la stack Docker Compose et dédiée à l'équipe Ops.
        </p>
      </aside>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════

function StatusBadge({ status }: { status: 'ok' | 'down' | 'unknown' }) {
  if (status === 'ok')
    return (
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-cream-50/10 ring-2 ring-cream-50/20">
        <CheckCircle2 className="h-7 w-7 text-cream-50" aria-label="Opérationnel" />
      </div>
    )
  if (status === 'down')
    return (
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-destructive/20">
        <AlertCircle className="h-7 w-7 text-destructive" aria-label="Indisponible" />
      </div>
    )
  return (
    <div className="flex h-14 w-14 items-center justify-center rounded-full bg-muted">
      <Loader2 className="h-7 w-7 text-muted-foreground animate-spin" aria-label="Chargement" />
    </div>
  )
}
