import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Trajet,
  Gare,
  Ligne,
  TrajetsParType,
  StatsEmissions,
  StatsOperateur,
  TrajetMapSegment,
  HealthStatus,
} from '@/types/api'

// Ressources brutes 

export function useTrajets() {
  return useQuery({
    queryKey: ['trajets'],
    queryFn: async () => {
      const { data } = await api.get<Trajet[]>('/trajets/')
      return data
    },
  })
}

export function useTrajet(id: string | undefined) {
  return useQuery({
    queryKey: ['trajet', id],
    queryFn: async () => {
      const { data } = await api.get<Trajet>(`/trajets/${id}`)
      return data
    },
    enabled: Boolean(id),
  })
}

export function useGares() {
  return useQuery({
    queryKey: ['gares'],
    queryFn: async () => {
      const { data } = await api.get<Gare[]>('/gares/')
      return data
    },
    staleTime: 5 * 60_000,   
  })
}

export function useLignes() {
  return useQuery({
    queryKey: ['lignes'],
    queryFn: async () => {
      const { data } = await api.get<Ligne[]>('/lignes/')
      return data
    },
    staleTime: 5 * 60_000,
  })
}

// Stats 

export function useCount(resource: 'trajets' | 'lignes' | 'gares' | 'pays') {
  return useQuery({
    queryKey: ['stats', 'count', resource],
    queryFn: async () => {
      const { data } = await api.get<Record<string, number>>(`/stats/${resource}/count`)
      return data
    },
  })
}

export function useTrajetsParType() {
  return useQuery({
    queryKey: ['stats', 'trajets', 'type'],
    queryFn: async () => {
      const { data } = await api.get<TrajetsParType>('/stats/trajets/type')
      return data
    },
  })
}

export function useEmissions() {
  return useQuery({
    queryKey: ['stats', 'emissions'],
    queryFn: async () => {
      const { data } = await api.get<StatsEmissions>('/stats/emissions')
      return data
    },
  })
}

export function useStatsOperateurs() {
  return useQuery({
    queryKey: ['stats', 'operateurs'],
    queryFn: async () => {
      const { data } = await api.get<StatsOperateur[]>('/stats/operateurs')
      return data
    },
  })
}

export function useTrajetsMap() {
  return useQuery({
    queryKey: ['stats', 'trajets', 'map'],
    queryFn: async () => {
      const { data } = await api.get<TrajetMapSegment[]>('/stats/trajets/map')
      return data
    },
    staleTime: 5 * 60_000,
  })
}

// Health 

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await api.get<HealthStatus>('/health')
      return data
    },
    refetchInterval: 15_000,
    retry: 0,
  })
}
