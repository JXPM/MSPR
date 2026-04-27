import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { StatsOperateur } from '@/types/api'

interface Props {
  data: StatsOperateur[] | undefined
  loading?: boolean
  maxRows?: number
}

export function OperateursChart({ data, loading, maxRows = 10 }: Props) {
  // Tri décroissant + top N
  const sorted = [...(data ?? [])]
    .filter((o) => o.operateur && o.trajets > 0)
    .sort((a, b) => b.trajets - a.trajets)
    .slice(0, maxRows)

  const max = sorted[0]?.trajets ?? 0

  return (
    <article
      aria-labelledby="chart-operateurs-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Top opérateurs
        </p>
        <h2 id="chart-operateurs-title" className="mt-1 font-display text-2xl text-forest-900">
          Volumes par opérateur
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Nombre de trajets recensés par compagnie ferroviaire
        </p>
      </header>

      <div className="mt-6 h-[28rem]">
        {loading ? (
          <SkeletonBars rows={8} />
        ) : sorted.length === 0 ? (
          <EmptyPlaceholder />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sorted}
              layout="vertical"
              margin={{ top: 4, right: 40, bottom: 4, left: 4 }}
            >
              <XAxis type="number" hide domain={[0, max * 1.1]} />
              <YAxis
                type="category"
                dataKey="operateur"
                width={140}
                tick={{
                  fill: '#2d4a33',    // forest-700
                  fontSize: 12,
                  fontFamily: 'IBM Plex Sans, system-ui, sans-serif',
                }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<BarTooltip />} cursor={{ fill: 'rgba(26, 61, 46, 0.05)' }} />
              <Bar dataKey="trajets" radius={[0, 4, 4, 0]} barSize={18}>
                {sorted.map((_, i) => (
                  <Cell
                    key={i}
                    fill={i === 0 ? '#1a3d2e' : i < 3 ? '#2d4a33' : '#4d7653'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Table accessible — screen readers uniquement */}
      <table className="sr-only">
        <caption>Volumes par opérateur</caption>
        <thead>
          <tr><th>Opérateur</th><th>Trajets</th></tr>
        </thead>
        <tbody>
          {sorted.map((o) => (
            <tr key={o.operateur}>
              <td>{o.operateur}</td>
              <td>{o.trajets}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  )
}

function BarTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const { operateur, trajets } = payload[0].payload
  return (
    <div className="rounded-md border border-border bg-card px-3 py-2 shadow-sm text-sm">
      <p className="font-medium">{operateur}</p>
      <p className="font-mono tabular-nums text-xs text-muted-foreground">
        {new Intl.NumberFormat('fr-FR').format(trajets)} trajets
      </p>
    </div>
  )
}

function SkeletonBars({ rows }: { rows: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 animate-pulse">
          <div className="h-3 w-28 bg-muted rounded" />
          <div
            className="h-5 bg-muted rounded"
            style={{ width: `${Math.max(20, 100 - i * 10)}%` }}
          />
        </div>
      ))}
    </div>
  )
}

function EmptyPlaceholder() {
  return (
    <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
      Aucune donnée d'opérateur disponible
    </div>
  )
}
