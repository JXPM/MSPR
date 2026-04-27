import { useEffect } from 'react'

/**
 * Injecte la CSS de Leaflet une seule fois au premier montage.
 * Évite de l'ajouter globalement alors qu'on n'en a besoin que sur 1-2 pages.
 */
let injected = false

export function useLeafletCss() {
  useEffect(() => {
    if (injected) return
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY='
    link.crossOrigin = ''
    document.head.appendChild(link)
    injected = true
  }, [])
}
