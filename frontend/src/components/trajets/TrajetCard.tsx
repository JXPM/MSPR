import { Link } from 'react-router-dom'
import { ArrowRight, Moon, Sun, TrainFront } from 'lucide-react'
import type { TrajetEnrichi } from '@/types/api'
import { Badge } from '@/components/ui/badge'

interface Props {
  trajet: TrajetEnrichi
}

export function TrajetCard({ trajet }: Props) {
  const isNuit = trajet.type_service === 'NUIT'
  const duree = computeDuree(trajet.heure_depart, trajet.heure_arrivee)

  return (
    <article
      className={`
        group relative overflow-hidden rounded-lg border transition-all
        hover:shadow-md hover:-translate-y-0.5
        ${isNuit
          ? 'bg-midnight-900 text-cream-50 border-midnight-700 hover:border-midnight-500'
          : 'bg-card border-border hover:border-forest-900'
        }
      `}
    >
      {/* Barre d'accent verticale à gauche */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-1 ${
          isNuit ? 'bg-rust-400' : 'bg-forest-700'
        }`}
        aria-hidden="true"
      />

      <div className="p-5 pl-6">
        {/* Header — opérateur + badge type */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <span
              className={`
                font-mono text-[10px] uppercase tracking-widest font-semibold
                ${isNuit ? 'text-cream-50/70' : 'text-forest-700'}
              `}
            >
              {trajet.operateur_code}
            </span>
            <span className={isNuit ? 'text-cream-50/30' : 'text-muted-foreground/40'}>·</span>
            <span
              className={`font-mono text-[10px] tracking-wider truncate ${
                isNuit ? 'text-cream-50/50' : 'text-muted-foreground'
              }`}
              title={trajet.trajet_id}
            >
              {trajet.trajet_id}
            </span>
          </div>

          {trajet.type_service && (
            <Badge variant={isNuit ? 'nuit' : 'jour'}>
              {isNuit ? (
                <Moon className="h-3 w-3" aria-hidden="true" />
              ) : (
                <Sun className="h-3 w-3" aria-hidden="true" />
              )}
              {trajet.type_service === 'JOUR' ? 'Jour' : 'Nuit'}
            </Badge>
          )}
        </div>

        {/* Horaires — composition éditoriale */}
        <div className="mt-5 grid grid-cols-[auto_1fr_auto] items-center gap-3">
          {/* départ */}
          <div className="text-right">
            <p className="font-display text-3xl tabular-nums leading-none">
              {formatTime(trajet.heure_depart)}
            </p>
            <p
              className={`mt-1 text-sm leading-tight line-clamp-2 ${
                isNuit ? 'text-cream-50/80' : 'text-foreground'
              }`}
              title={trajet.gare_depart}
            >
              {trajet.gare_depart}
            </p>
          </div>

          {/* ligne centrale avec durée */}
          <div className="flex flex-col items-center">
            <div className="relative w-full flex items-center">
              <div className={`h-px flex-1 ${isNuit ? 'bg-cream-50/25' : 'bg-border'}`} />
              <TrainFront
                className={`h-4 w-4 mx-2 ${isNuit ? 'text-rust-400' : 'text-forest-700'}`}
                aria-hidden="true"
              />
              <div className={`h-px flex-1 ${isNuit ? 'bg-cream-50/25' : 'bg-border'}`} />
            </div>
            {duree && (
              <p
                className={`mt-1.5 font-mono text-[10px] uppercase tracking-wider tabular-nums ${
                  isNuit ? 'text-cream-50/60' : 'text-muted-foreground'
                }`}
              >
                {duree}
              </p>
            )}
          </div>

          {/* arrivée */}
          <div>
            <p className="font-display text-3xl tabular-nums leading-none">
              {formatTime(trajet.heure_arrivee)}
            </p>
            <p
              className={`mt-1 text-sm leading-tight line-clamp-2 ${
                isNuit ? 'text-cream-50/80' : 'text-foreground'
              }`}
              title={trajet.gare_arrivee}
            >
              {trajet.gare_arrivee}
            </p>
          </div>
        </div>

        {/* Footer — ligne + CTA */}
        <div
          className={`mt-5 pt-4 flex items-center justify-between gap-3 border-t ${
            isNuit ? 'border-cream-50/10' : 'border-border/60'
          }`}
        >
          <div className="min-w-0">
            <p className={`font-mono text-[10px] uppercase tracking-wider ${
              isNuit ? 'text-cream-50/50' : 'text-muted-foreground'
            }`}>
              Ligne
            </p>
            <p className={`text-sm truncate ${isNuit ? 'text-cream-50/90' : 'text-foreground'}`}>
              {trajet.ligne?.nom_ligne ?? `N° ${trajet.id_ligne}`}
            </p>
          </div>

          <Link
            to={`/trajets/${encodeURIComponent(trajet.trajet_id)}`}
            className={`
              inline-flex items-center gap-1.5 text-sm font-medium shrink-0
              rounded-md px-3 py-1.5 transition-colors
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
              ${isNuit
                ? 'text-cream-50 hover:bg-cream-50/10 focus-visible:ring-cream-50 focus-visible:ring-offset-midnight-900'
                : 'text-forest-900 hover:bg-cream-200 focus-visible:ring-ring focus-visible:ring-offset-background'
              }
            `}
            aria-label={`Voir le détail du trajet ${trajet.gare_depart} vers ${trajet.gare_arrivee}`}
          >
            <span>Détail</span>
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
          </Link>
        </div>
      </div>
    </article>
  )
}

// ─────────────────────────────────────────────────────────────────
// Skeleton

export function TrajetCardSkeleton() {
  return (
    <div className="relative overflow-hidden rounded-lg border border-border bg-card p-5 pl-6">
      <div className="absolute left-0 top-0 bottom-0 w-1 bg-border" />
      <div className="animate-pulse space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-3 w-24 bg-muted rounded" />
          <div className="h-5 w-14 bg-muted rounded-full" />
        </div>
        <div className="grid grid-cols-[1fr_2fr_1fr] items-center gap-3">
          <div className="space-y-2">
            <div className="h-8 w-16 bg-muted rounded ml-auto" />
            <div className="h-3 w-20 bg-muted rounded ml-auto" />
          </div>
          <div className="h-px w-full bg-muted" />
          <div className="space-y-2">
            <div className="h-8 w-16 bg-muted rounded" />
            <div className="h-3 w-20 bg-muted rounded" />
          </div>
        </div>
        <div className="h-px w-full bg-border/60" />
        <div className="flex justify-between">
          <div className="h-4 w-32 bg-muted rounded" />
          <div className="h-6 w-16 bg-muted rounded" />
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────
// Helpers

function formatTime(t: string | null | undefined): string {
  if (!t) return '—'
  return t.slice(0, 5) // "21:30:00" → "21:30"
}

/**
 * Calcule la durée entre deux horaires "HH:mm" ou "HH:mm:ss".
 * Gère les trajets qui traversent minuit (arrivée < départ → on ajoute 24h).
 */
function computeDuree(dep: string, arr: string): string | null {
  const d = parseHm(dep)
  const a = parseHm(arr)
  if (d === null || a === null) return null
  let diff = a - d
  if (diff < 0) diff += 24 * 60
  const h = Math.floor(diff / 60)
  const m = diff % 60
  if (h === 0 && m === 0) return null
  return `${h}h${String(m).padStart(2, '0')}`
}

function parseHm(s: string | null | undefined): number | null {
  if (!s) return null
  const parts = s.slice(0, 5).split(':')
  if (parts.length < 2) return null
  const h = Number(parts[0])
  const m = Number(parts[1])
  if (Number.isNaN(h) || Number.isNaN(m)) return null
  return h * 60 + m
}
