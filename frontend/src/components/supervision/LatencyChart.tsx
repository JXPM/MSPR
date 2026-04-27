import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import type { LatencySample } from '@/hooks/useLatencyMonitor'

interface Props {
  samples: LatencySample[]
  avgLatency: number | null
}

export function LatencyChart({ samples, avgLatency }: Props) {
  const data = samples.map((s) => ({
    time: new Date(s.timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }),
    latency: s.status === 'ok' ? s.latencyMs : null,
    status: s.status,
  }))

  return (
    <article
      aria-labelledby="latency-chart-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
            Temps de réponse
          </p>
          <h2 id="latency-chart-title" className="mt-1 font-display text-2xl text-forest-900">
            Latence /health
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            {samples.length} sondes · actualisées en temps réel
          </p>
        </div>
        {avgLatency !== null && (
          <div className="text-right shrink-0">
            <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              Moyenne
            </p>
            <p className="font-display text-2xl tabular-nums text-forest-900">
              {avgLatency}
              <span className="ml-1 text-sm text-muted-foreground">ms</span>
            </p>
          </div>
        )}
      </header>

      <div className="mt-6 h-56">
        {samples.length < 2 ? (
          <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
            Collecte en cours… {samples.length}/2 sondes reçues
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <XAxis
                dataKey="time"
                tick={{ fill: '#6f9474', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                interval="preserveStartEnd"
                minTickGap={40}
              />
              <YAxis
                tick={{ fill: '#6f9474', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                unit=" ms"
                width={56}
              />
              <Tooltip content={<LatencyTooltip />} />
              {avgLatency !== null && (
                <ReferenceLine
                  y={avgLatency}
                  stroke="#6f9474"
                  strokeDasharray="3 3"
                  strokeOpacity={0.5}
                />
              )}
              <Line
                type="monotone"
                dataKey="latency"
                stroke="#1a3d2e"
                strokeWidth={2}
                dot={{ r: 2.5, fill: '#1a3d2e' }}
                activeDot={{ r: 5 }}
                connectNulls={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </article>
  )
}

function LatencyTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return (
    <div className="rounded-md border border-border bg-card px-3 py-2 shadow-sm text-sm">
      <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
        {label}
      </p>
      <p className="mt-1 font-medium tabular-nums">
        {point.status === 'ok' ? `${point.latency} ms` : 'Erreur'}
      </p>
    </div>
  )
}
