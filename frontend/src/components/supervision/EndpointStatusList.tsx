import { useQueries } from '@tanstack/react-query'
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'

const ENDPOINTS = [
  { path: '/trajets/',            label: 'Liste des trajets' },
  { path: '/gares/',              label: 'Liste des gares' },
  { path: '/lignes/',             label: 'Liste des lignes' },
  { path: '/stats/trajets/count', label: 'Comptage trajets' },
  { path: '/stats/gares/count',   label: 'Comptage gares' },
  { path: '/stats/trajets/type',  label: 'Répartition jour/nuit' },
  { path: '/stats/operateurs',    label: 'Stats opérateurs' },
  { path: '/stats/emissions',     label: 'Empreinte carbone' },
] as const

export function EndpointStatusList() {
  const queries = useQueries({
    queries: ENDPOINTS.map((ep) => ({
      queryKey: ['endpoint-health', ep.path],
      queryFn: async () => {
        const start = performance.now()
        await api.get(ep.path, { timeout: 5000 })
        return Math.round(performance.now() - start)
      },
      refetchInterval: 30_000,
      retry: 0,
      staleTime: 0,
    })),
  })

  return (
    <article
      aria-labelledby="endpoints-title"
      className="rounded-lg border border-border bg-card p-6"
    >
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Points de contact
        </p>
        <h2 id="endpoints-title" className="mt-1 font-display text-2xl text-forest-900">
          Endpoints surveillés
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Vérification automatique toutes les 30&nbsp;secondes
        </p>
      </header>

      <ul className="mt-6 divide-y divide-border/60">
        {ENDPOINTS.map((ep, i) => {
          const q = queries[i]
          return (
            <li
              key={ep.path}
              className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0"
            >
              <div className="flex items-center gap-3 min-w-0">
                <StatusIndicator
                  state={q.isLoading ? 'loading' : q.isError ? 'error' : 'ok'}
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-forest-900 truncate">
                    {ep.label}
                  </p>
                  <p className="font-mono text-xs text-muted-foreground truncate">
                    GET {ep.path}
                  </p>
                </div>
              </div>
              <div className="text-right shrink-0">
                {q.isLoading ? (
                  <span className="font-mono text-xs text-muted-foreground">…</span>
                ) : q.isError ? (
                  <span className="font-mono text-xs text-destructive">Erreur</span>
                ) : (
                  <span className="font-mono text-sm tabular-nums text-forest-900">
                    {q.data}<span className="text-xs text-muted-foreground ml-0.5">ms</span>
                  </span>
                )}
              </div>
            </li>
          )
        })}
      </ul>
    </article>
  )
}

function StatusIndicator({ state }: { state: 'ok' | 'error' | 'loading' }) {
  if (state === 'ok') return <CheckCircle2 className="h-4 w-4 text-forest-700 shrink-0" aria-label="Opérationnel" />
  if (state === 'error') return <AlertCircle className="h-4 w-4 text-destructive shrink-0" aria-label="Indisponible" />
  return <Loader2 className="h-4 w-4 text-muted-foreground shrink-0 animate-spin" aria-label="Vérification" />
}
