import { useCallback, useEffect, useRef } from 'react'
import { AlertTriangle, SearchX } from 'lucide-react'

import { useEnrichedTrajets } from '@/hooks/useEnrichedTrajets'
import { useTrajetsUrlState } from '@/hooks/useTrajetsUrlState'
import { TrajetsFiltersPanel } from '@/components/trajets/TrajetsFiltersPanel'
import { TrajetCard, TrajetCardSkeleton } from '@/components/trajets/TrajetCard'
import { TrajetsPagination } from '@/components/trajets/TrajetsPagination'
import { Button } from '@/components/ui/button'

const PAGE_SIZE = 50

export function Trajets() {
  const { filters, page, update, reset } = useTrajetsUrlState()

  const {
    items,
    total,
    totalUnfiltered,
    totalPages,
    currentPage,
    lignes,
    gares,
    operateurs,
    isLoading,
    error,
  } = useEnrichedTrajets(filters, page, PAGE_SIZE)

  // Scroll en haut de la liste lors d'un changement de page
  const listRef = useRef<HTMLDivElement>(null)
  const firstRender = useRef(true)
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false
      return
    }
    listRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [currentPage])

  const handlePageChange = useCallback(
    (p: number) => update({ page: p }),
    [update],
  )

  return (
    <div className="container py-12">
      {/* Header */}
      <header>
        <p className="font-mono text-xs uppercase tracking-[0.25em] text-forest-700">
          Exploration · 01
        </p>
        <h1 className="mt-2 font-display text-5xl md:text-6xl text-forest-900">
          Trajets
        </h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          Consultation des dessertes ferroviaires européennes recensées dans l'entrepôt
          unifié. Filtrez par ville, type de service, opérateur ou ligne.
        </p>
      </header>

      {/* Filtres */}
      <div className="mt-10">
        <TrajetsFiltersPanel
          filters={filters}
          onChange={update}
          onReset={reset}
          gares={gares}
          operateurs={operateurs}
          lignes={lignes}
          totalFiltered={total}
          totalUnfiltered={totalUnfiltered}
        />
      </div>

      {/* Liste */}
      <div ref={listRef} className="mt-10 scroll-mt-20">
        {error ? (
          <ErrorState error={error} />
        ) : isLoading ? (
          <LoadingGrid />
        ) : items.length === 0 ? (
          <EmptyState hasFilters={total !== totalUnfiltered} onReset={reset} />
        ) : (
          <>
            <ul
              className="grid gap-4 md:grid-cols-2"
              aria-label={`Liste de ${total} trajets filtrés`}
            >
              {items.map((trajet) => (
                <li key={trajet.trajet_id}>
                  <TrajetCard trajet={trajet} />
                </li>
              ))}
            </ul>

            <div className="mt-10">
              <TrajetsPagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={total}
                pageSize={PAGE_SIZE}
                onPageChange={handlePageChange}
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// États secondaires

function LoadingGrid() {
  return (
    <ul
      className="grid gap-4 md:grid-cols-2"
      aria-label="Chargement des trajets"
      aria-busy="true"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <li key={i}>
          <TrajetCardSkeleton />
        </li>
      ))}
    </ul>
  )
}

function ErrorState({ error }: { error: Error | unknown }) {
  const message = error instanceof Error ? error.message : 'Erreur inattendue'
  return (
    <div
      role="alert"
      className="rounded-lg border border-destructive/30 bg-destructive/5 p-8 text-center"
    >
      <AlertTriangle
        className="h-10 w-10 mx-auto text-destructive"
        aria-hidden="true"
      />
      <h2 className="mt-4 font-display text-2xl text-forest-900">
        Impossible de charger les trajets
      </h2>
      <p className="mt-2 text-sm text-muted-foreground">
        L'API ObRail ne répond pas actuellement.
      </p>
      <p className="mt-2 font-mono text-xs text-destructive">{message}</p>
      <Button
        variant="outline"
        size="sm"
        className="mt-6"
        onClick={() => window.location.reload()}
      >
        Réessayer
      </Button>
    </div>
  )
}

function EmptyState({ hasFilters, onReset }: { hasFilters: boolean; onReset: () => void }) {
  return (
    <div className="rounded-lg border border-dashed border-border bg-cream-50 p-12 text-center">
      <SearchX className="h-10 w-10 mx-auto text-forest-700" aria-hidden="true" />
      <h2 className="mt-4 font-display text-2xl text-forest-900">
        {hasFilters ? 'Aucun trajet ne correspond' : 'Aucun trajet disponible'}
      </h2>
      <p className="mt-2 max-w-sm mx-auto text-sm text-muted-foreground">
        {hasFilters
          ? 'Essayez d\'élargir vos critères de recherche ou de réinitialiser les filtres.'
          : 'La base semble vide — vérifiez que l\'ETL a bien chargé les données.'}
      </p>
      {hasFilters && (
        <Button variant="outline" size="sm" className="mt-6" onClick={onReset}>
          Réinitialiser les filtres
        </Button>
      )}
    </div>
  )
}
