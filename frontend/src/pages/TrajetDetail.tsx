import { useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Moon,
  Sun,
  TrainFront,
  Clock,
  Route as RouteIcon,
  MapPin,
  Building2,
  AlertTriangle,
} from 'lucide-react'

import { useTrajet, useGares, useLignes } from '@/hooks/useTrajets'
import type { Gare } from '@/types/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { TrajetMap } from '@/components/detail/TrajetMap'

export function TrajetDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: trajet, isLoading, error } = useTrajet(id)
  const { data: gares } = useGares()
  const { data: lignes } = useLignes()

  const ligne = useMemo(
    () => lignes?.find((l) => l.id_ligne === trajet?.id_ligne),
    [lignes, trajet?.id_ligne],
  )

  // Recherche des gares par NOM (le backend renvoie les noms dans trajet, pas les codes UIC)
  const gareDepart = useMemo(
    () => gares?.find((g) => g.nom_gare === trajet?.gare_depart) ?? null,
    [gares, trajet?.gare_depart],
  )
  const gareArrivee = useMemo(
    () => gares?.find((g) => g.nom_gare === trajet?.gare_arrivee) ?? null,
    [gares, trajet?.gare_arrivee],
  )

  const typeService =
    ligne?.type_service === 'JOUR' || ligne?.type_service === 'NUIT'
      ? (ligne.type_service as 'JOUR' | 'NUIT')
      : null
  const isNuit = typeService === 'NUIT'
  const operateurCode = trajet?.trajet_id.slice(0, 3).toUpperCase() ?? '—'
  const duree = trajet ? computeDuree(trajet.heure_depart, trajet.heure_arrivee) : null

  return (
    <div className="container py-12">
      {/* Back link */}
      <Button asChild variant="ghost" size="sm">
        <Link to="/trajets">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Retour aux trajets
        </Link>
      </Button>

      {/* États */}
      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}

      {/* Contenu */}
      {trajet && (
        <>
          {/* Header édito */}
          <header className="mt-8">
            <div className="flex flex-wrap items-center gap-3 font-mono text-xs uppercase tracking-[0.2em] text-forest-700">
              <span>Trajet</span>
              <span className="text-muted-foreground/40">·</span>
              <span className="text-muted-foreground">{trajet.trajet_id}</span>
              {typeService && (
                <Badge variant={isNuit ? 'nuit' : 'jour'}>
                  {isNuit ? (
                    <Moon className="h-3 w-3" aria-hidden="true" />
                  ) : (
                    <Sun className="h-3 w-3" aria-hidden="true" />
                  )}
                  {isNuit ? 'Nuit' : 'Jour'}
                </Badge>
              )}
            </div>

            <h1 className="mt-4 font-display text-4xl md:text-6xl lg:text-7xl text-forest-900 leading-[1.05]">
              {trajet.gare_depart}
              <br className="md:hidden" />
              <ArrowRight
                className="inline-block h-8 w-8 md:h-10 md:w-10 mx-3 md:mx-5 text-rust-500 align-middle"
                aria-hidden="true"
              />
              <span className={isNuit ? 'italic' : ''}>{trajet.gare_arrivee}</span>
            </h1>
          </header>

          {/* Horaires en bande */}
          <section
            aria-labelledby="horaires-title"
            className="mt-10 rounded-lg border border-border bg-forest-900 text-cream-50 overflow-hidden"
          >
            <h2 id="horaires-title" className="sr-only">Horaires et durée</h2>
            <div className="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-forest-800">
              <HoraireBlock
                label="Départ"
                time={trajet.heure_depart}
                location={trajet.gare_depart}
                country={gareDepart?.iso_pays}
              />
              <DureeBlock duree={duree} />
              <HoraireBlock
                label="Arrivée"
                time={trajet.heure_arrivee}
                location={trajet.gare_arrivee}
                country={gareArrivee?.iso_pays}
              />
            </div>
          </section>

          {/* Infos + Carte */}
          <section className="mt-10 grid gap-6 lg:grid-cols-[340px_1fr]">
            {/* Panneau infos */}
            <div className="space-y-4">
              <InfoCard
                label="Opérateur"
                value={operateurCode}
                icon={Building2}
                hint="code à 3 lettres dérivé du trajet_id"
              />
              <InfoCard
                label="Ligne"
                value={ligne?.nom_ligne ?? `N° ${trajet.id_ligne}`}
                icon={RouteIcon}
                hint={ligne?.distance ? `${Number(ligne.distance).toFixed(0)} km` : undefined}
              />
              <InfoCard
                label="Type de service"
                value={typeService === 'JOUR' ? 'Train de jour' : typeService === 'NUIT' ? 'Train de nuit' : '—'}
                icon={isNuit ? Moon : Sun}
              />
              {duree && (
                <InfoCard label="Durée" value={duree} icon={Clock} />
              )}
            </div>

            {/* Carte */}
            <TrajetMap
              gareDepart={gareDepart}
              gareArrivee={gareArrivee}
              isNuit={isNuit}
            />
          </section>

          {/* Détails gares */}
          {(gareDepart || gareArrivee) && (
            <section aria-labelledby="gares-title" className="mt-10">
              <h2
                id="gares-title"
                className="font-mono text-xs uppercase tracking-[0.25em] text-forest-700"
              >
                Gares desservies
              </h2>
              <div className="mt-4 grid md:grid-cols-2 gap-4">
                {gareDepart && <GareDetailCard gare={gareDepart} role="Départ" />}
                {gareArrivee && <GareDetailCard gare={gareArrivee} role="Arrivée" />}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// Sub-components

function HoraireBlock({
  label,
  time,
  location,
  country,
}: {
  label: string
  time: string
  location: string
  country?: string | null
}) {
  return (
    <div className="p-8">
      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-cream-50/60">
        {label}
      </p>
      <p className="mt-3 font-display text-6xl tabular-nums leading-none">
        {formatTime(time)}
      </p>
      <p className="mt-4 text-sm text-cream-50/90">{location}</p>
      {country && (
        <p className="mt-1 font-mono text-[10px] uppercase tracking-widest text-cream-50/50">
          {country}
        </p>
      )}
    </div>
  )
}

function DureeBlock({ duree }: { duree: string | null }) {
  return (
    <div className="p-8 flex flex-col items-center justify-center bg-midnight-700">
      <TrainFront className="h-8 w-8 text-rust-400" aria-hidden="true" />
      <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.2em] text-cream-50/60">
        Durée
      </p>
      <p className="mt-1 font-display text-4xl tabular-nums">{duree ?? '—'}</p>
    </div>
  )
}

function InfoCard({
  label,
  value,
  icon: Icon,
  hint,
}: {
  label: string
  value: string | number
  icon: typeof TrainFront
  hint?: string
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
        <Icon className="h-3.5 w-3.5" aria-hidden="true" />
        {label}
      </div>
      <p className="mt-2 font-display text-xl text-forest-900">{value}</p>
      {hint && <p className="mt-0.5 text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

function GareDetailCard({
  gare,
  role,
}: {
  gare: Gare
  role: 'Départ' | 'Arrivée'
}) {
  const isDepart = role === 'Départ'
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p
            className={`font-mono text-[10px] uppercase tracking-widest ${
              isDepart ? 'text-forest-700' : 'text-rust-500'
            }`}
          >
            {role}
          </p>
          <p className="mt-1 font-display text-xl text-forest-900">{gare.nom_gare}</p>
        </div>
        <MapPin
          className={`h-5 w-5 shrink-0 ${isDepart ? 'text-forest-700' : 'text-rust-500'}`}
          aria-hidden="true"
        />
      </div>

      <dl className="mt-4 space-y-2 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">Code UIC</dt>
          <dd className="font-mono text-forest-900">{gare.code_uic}</dd>
        </div>
        {gare.iso_pays && (
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Pays</dt>
            <dd className="font-mono text-forest-900">{gare.iso_pays}</dd>
          </div>
        )}
        {gare.latitude != null && gare.longitude != null && (
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Coordonnées</dt>
            <dd className="font-mono text-xs text-forest-900 tabular-nums">
              {gare.latitude.toFixed(4)}, {gare.longitude.toFixed(4)}
            </dd>
          </div>
        )}
      </dl>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="mt-10 animate-pulse">
      <div className="h-4 w-40 bg-muted rounded" />
      <div className="mt-4 h-20 w-full max-w-4xl bg-muted rounded" />
      <div className="mt-10 h-64 bg-muted rounded-lg" />
    </div>
  )
}

function ErrorState({ error }: { error: unknown }) {
  const message = error instanceof Error ? error.message : 'Erreur inattendue'
  return (
    <div
      role="alert"
      className="mt-10 rounded-lg border border-destructive/30 bg-destructive/5 p-8 text-center"
    >
      <AlertTriangle className="h-10 w-10 mx-auto text-destructive" aria-hidden="true" />
      <h2 className="mt-4 font-display text-2xl text-forest-900">
        Impossible de charger ce trajet
      </h2>
      <p className="mt-2 font-mono text-xs text-destructive">{message}</p>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// Helpers

function formatTime(t: string | null | undefined): string {
  if (!t) return '—'
  return t.slice(0, 5)
}

function computeDuree(dep: string, arr: string): string | null {
  const d = parseHm(dep)
  const a = parseHm(arr)
  if (d === null || a === null) return null
  let diff = a - d
  if (diff < 0) diff += 24 * 60
  if (diff === 0) return null
  const h = Math.floor(diff / 60)
  const m = diff % 60
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
