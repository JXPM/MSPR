//  Ressources 

export interface Trajet {
  trajet_id: string
  id_ligne: number
  gare_depart: string       // NOM de la gare, pas le code UIC
  gare_arrivee: string
  heure_depart: string
  heure_arrivee: string
}

export interface Gare {
  code_uic: string
  nom_gare: string
  longitude: number | null
  latitude: number | null
  iso_pays: string | null
}

export interface Ligne {
  id_ligne: number
  nom_ligne: string
  distance: number | null
  type_service: string | null   // "JOUR" | "NUIT"
}

export interface Operateur {
  code_operateur: string
  nom_operateur: string
  iso_pays: string
}

// Stats 

export interface TrajetsParType {
  JOUR: number
  NUIT: number
}

export interface StatsEmissions {
  train: number | null
  avion: number | null
}

export interface StatsOperateur {
  operateur: string
  trajets: number
}

export interface TrajetMapSegment {
  lat_depart: number
  lon_depart: number
  lat_arrivee: number
  lon_arrivee: number
}

// Stats 

export interface HealthStatus {
  status: 'ok' | 'degraded' | 'down'
}

// Enrichissements côté frontend 

export interface TrajetEnrichi extends Trajet {
  ligne?: Ligne
  type_service?: 'JOUR' | 'NUIT' | null
  operateur_code?: string          // dérivé de trajet_id (3 premiers caractères)
  gare_depart_coords?: { lat: number; lon: number } | null
  gare_arrivee_coords?: { lat: number; lon: number } | null
}
