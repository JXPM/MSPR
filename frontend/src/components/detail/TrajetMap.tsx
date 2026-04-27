import { useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import type { LatLngExpression, LatLngBoundsExpression } from 'leaflet'
import L from 'leaflet'
import type { Gare } from '@/types/api'
import { useLeafletCss } from '@/lib/useLeafletCss'

interface Props {
  gareDepart: Gare | null
  gareArrivee: Gare | null
  isNuit?: boolean
}

// Icônes custom — pas besoin des SVG par défaut de Leaflet
const createIcon = (color: string, label: string) =>
  L.divIcon({
    className: 'obrail-marker',
    html: `
      <div style="
        width:28px; height:28px; border-radius:50%;
        background:${color};
        border:3px solid #fbfaf7;
        box-shadow:0 2px 6px rgba(0,0,0,0.3);
        display:flex; align-items:center; justify-content:center;
        font-family: 'IBM Plex Mono', monospace;
        font-size:12px; font-weight:700; color:#fbfaf7;
      ">${label}</div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  })

const DEPART_ICON = createIcon('#1a3d2e', 'D')  // forest-900
const ARRIVEE_ICON = createIcon('#c14d3c', 'A') // rust-500

export function TrajetMap({ gareDepart, gareArrivee, isNuit = false }: Props) {
  useLeafletCss()

  const hasCoords =
    gareDepart?.latitude != null &&
    gareDepart?.longitude != null &&
    gareArrivee?.latitude != null &&
    gareArrivee?.longitude != null

  const depart: LatLngExpression | null = hasCoords
    ? [gareDepart!.latitude!, gareDepart!.longitude!]
    : null
  const arrivee: LatLngExpression | null = hasCoords
    ? [gareArrivee!.latitude!, gareArrivee!.longitude!]
    : null

  const bounds: LatLngBoundsExpression | undefined = useMemo(() => {
    if (!depart || !arrivee) return undefined
    return [depart as [number, number], arrivee as [number, number]]
  }, [depart, arrivee])

  if (!hasCoords) {
    return (
      <div
        role="status"
        className="h-[400px] flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border bg-cream-50 p-8 text-center"
      >
        <p className="font-mono text-[10px] uppercase tracking-widest text-forest-700">
          Géolocalisation indisponible
        </p>
        <p className="text-sm text-muted-foreground max-w-md">
          Les coordonnées GPS d'une ou des deux gares ne sont pas renseignées
          dans l'entrepôt.
        </p>
      </div>
    )
  }

  // Couleur du tracé selon jour/nuit
  const polylineColor = isNuit ? '#1e2a4a' : '#1a3d2e'

  return (
    <div
      className="relative overflow-hidden rounded-lg border border-border"
      aria-label={`Carte du trajet entre ${gareDepart?.nom_gare} et ${gareArrivee?.nom_gare}`}
    >
      <MapContainer
        bounds={bounds}
        boundsOptions={{ padding: [50, 50] }}
        scrollWheelZoom={false}
        style={{ height: '500px', width: '100%', backgroundColor: '#f5f1ea' }}
      >
        {/* Carto light — cohérent avec la palette cream */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />

        {/* Ligne pointillée entre les deux gares */}
        <Polyline
          positions={[depart!, arrivee!]}
          pathOptions={{
            color: polylineColor,
            weight: 3,
            dashArray: '8, 8',
            opacity: 0.7,
          }}
        />

        {/* Marker départ */}
        <Marker position={depart!} icon={DEPART_ICON}>
          <Popup>
            <div className="font-sans">
              <p className="font-mono text-[10px] uppercase tracking-widest text-forest-700 mb-1">
                Départ
              </p>
              <p className="font-medium text-forest-900">{gareDepart?.nom_gare}</p>
              {gareDepart?.iso_pays && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {gareDepart.iso_pays}
                </p>
              )}
            </div>
          </Popup>
        </Marker>

        {/* Marker arrivée */}
        <Marker position={arrivee!} icon={ARRIVEE_ICON}>
          <Popup>
            <div className="font-sans">
              <p className="font-mono text-[10px] uppercase tracking-widest text-rust-500 mb-1">
                Arrivée
              </p>
              <p className="font-medium text-forest-900">{gareArrivee?.nom_gare}</p>
              {gareArrivee?.iso_pays && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {gareArrivee.iso_pays}
                </p>
              )}
            </div>
          </Popup>
        </Marker>
      </MapContainer>

      {/* Note : le tracé est une approximation en ligne droite, pas la voie réelle */}
      <div className="absolute bottom-2 left-2 z-[1000] rounded bg-card/95 backdrop-blur px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-muted-foreground pointer-events-none">
        Tracé indicatif
      </div>
    </div>
  )
}
