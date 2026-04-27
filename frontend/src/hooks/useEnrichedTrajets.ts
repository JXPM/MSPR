import { useMemo } from 'react'
import {
  useTrajets,
  useLignes,
  useStatsOperateurs,
} from '@/hooks/useTrajets'
import type { Trajet, Ligne, TrajetEnrichi } from '@/types/api'


// Filtres appliqués côté client

export interface TrajetsFilters {
  depart?: string          
  arrivee?: string
  type?: 'JOUR' | 'NUIT'   
  operateur?: string      
  ligne?: number           
  heureMin?: string        
  heureMax?: string        
}

export const EMPTY_FILTERS: TrajetsFilters = {}

// Hook principal — fetch + enrich + filter + paginate

export function useEnrichedTrajets(
  filters: TrajetsFilters,
  page: number,
  pageSize: number,
) {
  const trajetsQ = useTrajets()
  const lignesQ = useLignes()
  const operateursQ = useStatsOperateurs()

  // Index des lignes par id pour O(1) lookup
  const lignesById = useMemo(() => {
    const map = new Map<number, Ligne>()
    lignesQ.data?.forEach((l) => map.set(l.id_ligne, l))
    return map
  }, [lignesQ.data])

  const operateursList = useMemo(() => {
    return operateursQ.data?.map((o) => o.operateur).filter(Boolean) ?? []
  }, [operateursQ.data])

  const enriched = useMemo<TrajetEnrichi[]>(() => {
    if (!trajetsQ.data) return []
    return trajetsQ.data.map((t) => enrichTrajet(t, lignesById))
  }, [trajetsQ.data, lignesById])

  // Listes uniques pour les filtres (combobox)
  const unique = useMemo(() => {
    const gares = new Set<string>()
    const operateurs = new Set<string>()
    for (const t of enriched) {
      if (t.gare_depart) gares.add(t.gare_depart)
      if (t.gare_arrivee) gares.add(t.gare_arrivee)
      if (t.operateur_code) operateurs.add(t.operateur_code)
    }
    return {
      gares: Array.from(gares).sort((a, b) => a.localeCompare(b, 'fr')),
      operateurs: Array.from(operateurs).sort(),
    }
  }, [enriched])

  // Filtrage
  const filtered = useMemo(() => {
    return enriched.filter((t) => matchesFilters(t, filters))
  }, [enriched, filters])

  // Pagination client-side
  const total = filtered.length
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const safePage = Math.min(Math.max(1, page), totalPages)
  const start = (safePage - 1) * pageSize
  const paged = filtered.slice(start, start + pageSize)

  return {
    // données
    items: paged,
    total,
    totalUnfiltered: enriched.length,
    totalPages,
    currentPage: safePage,

    // listes pour les filtres
    lignes: lignesQ.data ?? [],
    gares: unique.gares,
    operateurs: unique.operateurs,
    operateursNames: operateursList,

    // états
    isLoading: trajetsQ.isLoading || lignesQ.isLoading,
    isFetching: trajetsQ.isFetching,
    error: trajetsQ.error ?? lignesQ.error ?? null,
  }
}

// Helpers

function enrichTrajet(t: Trajet, lignesById: Map<number, Ligne>): TrajetEnrichi {
  const ligne = lignesById.get(t.id_ligne)
  const typeService =
    ligne?.type_service === 'JOUR' || ligne?.type_service === 'NUIT'
      ? (ligne.type_service as 'JOUR' | 'NUIT')
      : null
  const operateur_code = t.trajet_id.slice(0, 3).toUpperCase()

  return {
    ...t,
    ligne,
    type_service: typeService,
    operateur_code,
  }
}

function matchesFilters(t: TrajetEnrichi, f: TrajetsFilters): boolean {
  if (f.depart && !includesCi(t.gare_depart, f.depart)) return false
  if (f.arrivee && !includesCi(t.gare_arrivee, f.arrivee)) return false
  if (f.type && t.type_service !== f.type) return false
  if (f.operateur && t.operateur_code !== f.operateur) return false
  if (f.ligne !== undefined && t.id_ligne !== f.ligne) return false
  if (f.heureMin && !isAfterOrEqual(t.heure_depart, f.heureMin)) return false
  if (f.heureMax && !isBeforeOrEqual(t.heure_depart, f.heureMax)) return false
  return true
}

function includesCi(haystack: string, needle: string): boolean {
  return haystack.toLocaleLowerCase('fr').includes(needle.toLocaleLowerCase('fr'))
}

function normalizeHm(s: string): string {
  return (s ?? '').slice(0, 5)
}

function isAfterOrEqual(time: string, ref: string): boolean {
  return normalizeHm(time) >= normalizeHm(ref)
}

function isBeforeOrEqual(time: string, ref: string): boolean {
  return normalizeHm(time) <= normalizeHm(ref)
}
