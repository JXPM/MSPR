import { CheckCircle2, AlertCircle } from 'lucide-react'
import { useTrajets, useLignes, useGares } from '@/hooks/useTrajets'

interface MetricRow {
  label: string
  complete: number
  total: number
}

export function DataQuality() {
  const trajetsQ = useTrajets()
  const lignesQ = useLignes()
  const garesQ = useGares()

  const loading = trajetsQ.isLoading || lignesQ.isLoading || garesQ.isLoading

  // Calculs de complétude client-side
  const metrics: MetricRow[] = []

  if (trajetsQ.data) {
    metrics.push({
      label: 'Trajets avec horaires',
      complete: trajetsQ.data.filter(
        (t) => t.heure_depart && t.heure_arrivee,
      ).length,
      total: trajetsQ.data.length,
    })
  }

  if (lignesQ.data) {
    metrics.push({
      label: 'Lignes avec type de service',
      complete: lignesQ.data.filter((l) => l.type_service).length,
      total: lignesQ.data.length,
    })
    metrics.push({
      label: 'Lignes avec distance',
      complete: lignesQ.data.filter((l) => l.distance != null).length,
      total: lignesQ.data.length,
    })
  }

  if (garesQ.data) {
    metrics.push({
      label: 'Gares géolocalisées',
      complete: garesQ.data.filter(
        (g) => g.latitude != null && g.longitude != null,
      ).length,
      total: garesQ.data.length,
    })
    metrics.push({
      label: 'Gares avec pays rattaché',
      complete: garesQ.data.filter((g) => g.iso_pays).length,
      total: garesQ.data.length,
    })
  }

  return (
    <article
      aria-labelledby="quality-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Qualité des données
        </p>
        <h2 id="quality-title" className="mt-1 font-display text-2xl text-forest-900">
          Complétude par dimension
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Taux de remplissage des champs critiques dans l'entrepôt
        </p>
      </header>

      <ul className="mt-6 space-y-5">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => <QualitySkeleton key={i} />)
          : metrics.map((m) => <QualityBar key={m.label} {...m} />)
        }
      </ul>
    </article>
  )
}

function QualityBar({ label, complete, total }: MetricRow) {
  const pct = total > 0 ? Math.round((complete / total) * 100) : 0
  const isGood = pct >= 90
  const isOk = pct >= 70

  const color = isGood ? 'bg-forest-700' : isOk ? 'bg-rust-500' : 'bg-destructive'

  return (
    <li>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-sm">
          {isGood ? (
            <CheckCircle2 className="h-4 w-4 text-forest-700 shrink-0" aria-hidden="true" />
          ) : (
            <AlertCircle className="h-4 w-4 text-rust-500 shrink-0" aria-hidden="true" />
          )}
          <span className="text-foreground">{label}</span>
        </div>
        <div className="font-mono text-sm tabular-nums shrink-0">
          <span className="text-forest-900 font-semibold">{pct}%</span>
          <span className="ml-2 text-xs text-muted-foreground">
            {new Intl.NumberFormat('fr-FR').format(complete)}/
            {new Intl.NumberFormat('fr-FR').format(total)}
          </span>
        </div>
      </div>
      <div
        className="mt-2 h-1.5 w-full rounded-full bg-muted overflow-hidden"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label} : ${pct}%`}
      >
        <div
          className={`h-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </li>
  )
}

function QualitySkeleton() {
  return (
    <li className="animate-pulse">
      <div className="flex justify-between">
        <div className="h-4 w-48 bg-muted rounded" />
        <div className="h-4 w-16 bg-muted rounded" />
      </div>
      <div className="mt-2 h-1.5 w-full bg-muted rounded-full" />
    </li>
  )
}
