import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { TrajetsFilters } from './useEnrichedTrajets'

// Clés URL dédiées pour éviter les collisions avec d'autres pages
const KEYS = {
  depart:   'dep',
  arrivee:  'arr',
  type:     'type',
  operateur:'op',
  ligne:    'l',
  heureMin: 'hmin',
  heureMax: 'hmax',
  page:     'page',
} as const

export interface TrajetsUrlState {
  filters: TrajetsFilters
  page: number
}

export function useTrajetsUrlState() {
  const [searchParams, setSearchParams] = useSearchParams()

  // Parse URL → state
  const state = useMemo<TrajetsUrlState>(() => {
    const p = searchParams
    const typeRaw = p.get(KEYS.type)
    const type = typeRaw === 'JOUR' || typeRaw === 'NUIT' ? typeRaw : undefined
    const ligneRaw = p.get(KEYS.ligne)
    const ligne = ligneRaw && !Number.isNaN(Number(ligneRaw)) ? Number(ligneRaw) : undefined
    const pageRaw = p.get(KEYS.page)
    const page = pageRaw && !Number.isNaN(Number(pageRaw)) ? Math.max(1, Number(pageRaw)) : 1

    return {
      filters: {
        depart:    p.get(KEYS.depart)    ?? undefined,
        arrivee:   p.get(KEYS.arrivee)   ?? undefined,
        type,
        operateur: p.get(KEYS.operateur) ?? undefined,
        ligne,
        heureMin:  p.get(KEYS.heureMin)  ?? undefined,
        heureMax:  p.get(KEYS.heureMax)  ?? undefined,
      },
      page,
    }
  }, [searchParams])

  // Merge partiel → URL
  const update = useCallback(
    (patch: Partial<TrajetsFilters> & { page?: number }) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev)
          const apply = (key: string, value: string | number | undefined) => {
            if (value === undefined || value === '' || value === null) {
              next.delete(key)
            } else {
              next.set(key, String(value))
            }
          }

          if ('depart'    in patch) apply(KEYS.depart,    patch.depart)
          if ('arrivee'   in patch) apply(KEYS.arrivee,   patch.arrivee)
          if ('type'      in patch) apply(KEYS.type,      patch.type)
          if ('operateur' in patch) apply(KEYS.operateur, patch.operateur)
          if ('ligne'     in patch) apply(KEYS.ligne,     patch.ligne)
          if ('heureMin'  in patch) apply(KEYS.heureMin,  patch.heureMin)
          if ('heureMax'  in patch) apply(KEYS.heureMax,  patch.heureMax)
          if ('page'      in patch) apply(KEYS.page,      patch.page)

          // Reset page à 1 dès qu'un filtre change (sauf si on change explicitement la page)
          const filterKeys = ['depart', 'arrivee', 'type', 'operateur', 'ligne', 'heureMin', 'heureMax'] as const
          const filterChanged = filterKeys.some((k) => k in patch)
          if (filterChanged && !('page' in patch)) {
            next.delete(KEYS.page)
          }

          return next
        },
        { replace: true },
      )
    },
    [setSearchParams],
  )

  const reset = useCallback(() => {
    setSearchParams(new URLSearchParams(), { replace: true })
  }, [setSearchParams])

  return { ...state, update, reset }
}
