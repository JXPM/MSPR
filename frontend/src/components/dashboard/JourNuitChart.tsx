import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { Sun, Moon } from 'lucide-react'
import type { TrajetsParType } from '@/types/api'

interface Props {
  data: TrajetsParType | undefined
  loading?: boolean
}

// Couleurs tirées de tailwind.config.js
const COLOR_JOUR = '#c14d3c'     
const COLOR_NUIT = '#1e2a4a'     

export function JourNuitChart({ data, loading }: Props) {
  const total = (data?.JOUR ?? 0) + (data?.NUIT ?? 0)
  const pctJour = total > 0 ? Math.round(((data?.JOUR ?? 0) / total) * 100) : 0
  const pctNuit = total > 0 ? Math.round(((data?.NUIT ?? 0) / total) * 100) : 0

  const chartData = [
    { name: 'Jour', value: data?.JOUR ?? 0, color: COLOR_JOUR },
    { name: 'Nuit', value: data?.NUIT ?? 0, color: COLOR_NUIT },
  ]

  return (
    <article
      aria-labelledby="chart-jour-nuit-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Répartition
        </p>
        <h2 id="chart-jour-nuit-title" className="mt-1 font-display text-2xl text-forest-900">
          Jour vs Nuit
        </h2>
      </header>

      <div className="mt-6 grid md:grid-cols-[1fr_auto] gap-6 items-center">
        {/* Donut */}
        <div
          className="relative h-56"
          role="img"
          aria-label={`Répartition : ${pctJour}% trajets de jour, ${pctNuit}% trajets de nuit`}
        >
          {loading ? (
            <div className="h-full w-full rounded-full bg-muted animate-pulse" />
          ) : (
            <>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    stroke="none"
                    isAnimationActive={false}
                  >
                    {chartData.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<DonutTooltip total={total} />} />
                </PieChart>
              </ResponsiveContainer>
              {/* Centre du donut */}
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <p className="font-display text-3xl tabular-nums text-forest-900">
                  {formatInt(total)}
                </p>
                <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  trajets
                </p>
              </div>
            </>
          )}
        </div>

        {/* Légende */}
        <dl className="space-y-4 md:w-40">
          <LegendRow
            icon={<Sun className="h-4 w-4 text-rust-500" aria-hidden="true" />}
            label="Trajets de jour"
            value={data?.JOUR}
            pct={pctJour}
            color={COLOR_JOUR}
          />
          <LegendRow
            icon={<Moon className="h-4 w-4 text-midnight-700" aria-hidden="true" />}
            label="Trajets de nuit"
            value={data?.NUIT}
            pct={pctNuit}
            color={COLOR_NUIT}
          />
        </dl>
      </div>
    </article>
  )
}

function LegendRow({ icon, label, value, pct, color }: {
  icon: React.ReactNode
  label: string
  value: number | undefined
  pct: number
  color: string
}) {
  return (
    <div className="border-l-2 pl-3" style={{ borderColor: color }}>
      <dt className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
        {icon}
        {label}
      </dt>
      <dd className="mt-1">
        <span className="font-display text-2xl tabular-nums text-forest-900">
          {value !== undefined ? formatInt(value) : '—'}
        </span>
        <span className="ml-2 font-mono text-xs text-muted-foreground tabular-nums">
          {pct}%
        </span>
      </dd>
    </div>
  )
}

function DonutTooltip({ active, payload, total }: any) {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  const pct = total > 0 ? Math.round((value / total) * 100) : 0
  return (
    <div className="rounded-md border border-border bg-card px-3 py-2 shadow-sm text-sm">
      <p className="font-medium">{name}</p>
      <p className="font-mono tabular-nums text-xs text-muted-foreground">
        {formatInt(value)} · {pct}%
      </p>
    </div>
  )
}

function formatInt(n: number) {
  return new Intl.NumberFormat('fr-FR').format(n)
}
