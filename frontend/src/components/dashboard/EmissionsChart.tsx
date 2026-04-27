import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { TrainFront, Plane, TrendingDown } from 'lucide-react'
import type { StatsEmissions } from '@/types/api'

interface Props {
  data: StatsEmissions | undefined
  loading?: boolean
}

export function EmissionsChart({ data, loading }: Props) {
  const train = data?.train ?? 0
  const avion = data?.avion ?? 0
  const reduction = avion > 0 ? Math.round(((avion - train) / avion) * 100) : null

  const chartData = [
    { mode: 'Train',  co2: train, color: '#1a3d2e' },   // forest-900
    { mode: 'Avion',  co2: avion, color: '#c14d3c' },   // rust-500
  ]

  return (
    <article
      aria-labelledby="chart-emissions-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
            Impact carbone
          </p>
          <h2 id="chart-emissions-title" className="mt-1 font-display text-2xl text-forest-900">
            Empreinte CO₂ comparée
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Moyenne par trajet · kilogrammes de CO₂ équivalent
          </p>
        </div>

        {reduction !== null && !loading && (
          <div className="shrink-0 flex items-center gap-2 rounded-md bg-forest-900 text-cream-50 px-3 py-1.5">
            <TrendingDown className="h-4 w-4" aria-hidden="true" />
            <span className="font-mono text-sm tabular-nums">−{reduction}%</span>
          </div>
        )}
      </header>

      {/* Cards récap */}
      <div className="mt-6 grid grid-cols-2 gap-3">
        <ModeCard
          icon={<TrainFront className="h-4 w-4" aria-hidden="true" />}
          label="Train"
          value={train}
          loading={loading}
          accent="forest"
        />
        <ModeCard
          icon={<Plane className="h-4 w-4" aria-hidden="true" />}
          label="Avion"
          value={avion}
          loading={loading}
          accent="rust"
        />
      </div>

      {/* Graph barres */}
      <div className="mt-6 h-48">
        {loading ? (
          <div className="h-full animate-pulse bg-muted rounded-md" />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
            >
              <XAxis
                dataKey="mode"
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#2d4a33', fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#6f9474', fontSize: 11 }}
                unit=" kg"
              />
              <Tooltip content={<EmissionTooltip />} cursor={{ fill: 'rgba(26, 61, 46, 0.05)' }} />
              <Bar dataKey="co2" radius={[6, 6, 0, 0]} barSize={80}>
                {chartData.map((entry) => (
                  <Cell key={entry.mode} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Narration éditoriale */}
      {reduction !== null && !loading && reduction > 0 && (
        <p className="mt-4 text-xs italic text-muted-foreground">
          Le train émet en moyenne{' '}
          <span className="font-semibold text-forest-900">{reduction}%</span> de CO₂ en moins
          que l'avion sur les trajets intra-européens étudiés.
        </p>
      )}
    </article>
  )
}

function ModeCard({ icon, label, value, loading, accent }: {
  icon: React.ReactNode
  label: string
  value: number
  loading?: boolean
  accent: 'forest' | 'rust'
}) {
  const accentClass = accent === 'forest'
    ? 'border-forest-900/20 bg-forest-50'
    : 'border-rust-500/20 bg-rust-500/5'
  const textClass = accent === 'forest' ? 'text-forest-900' : 'text-rust-600'

  return (
    <div className={`rounded-md border p-3 ${accentClass}`}>
      <p className={`flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider ${textClass}`}>
        {icon}
        {label}
      </p>
      <p className="mt-1 font-display text-2xl tabular-nums text-forest-900">
        {loading ? '—' : value.toFixed(1)}
        <span className="ml-1 text-xs text-muted-foreground">kg CO₂</span>
      </p>
    </div>
  )
}

function EmissionTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const { mode, co2 } = payload[0].payload
  return (
    <div className="rounded-md border border-border bg-card px-3 py-2 shadow-sm text-sm">
      <p className="font-medium">{mode}</p>
      <p className="font-mono tabular-nums text-xs text-muted-foreground">
        {co2.toFixed(1)} kg CO₂
      </p>
    </div>
  )
}
