import { X, Search, ArrowRight, Clock } from 'lucide-react'
import type { TrajetsFilters } from '@/hooks/useEnrichedTrajets'
import type { Ligne } from '@/types/api'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'

interface Props {
  filters: TrajetsFilters
  onChange: (patch: Partial<TrajetsFilters>) => void
  onReset: () => void
  gares: string[]
  operateurs: string[]
  lignes: Ligne[]
  totalFiltered: number
  totalUnfiltered: number
}

export function TrajetsFiltersPanel({
  filters,
  onChange,
  onReset,
  gares,
  operateurs,
  lignes,
  totalFiltered,
  totalUnfiltered,
}: Props) {
  const hasActiveFilters =
    Object.values(filters).some((v) => v !== undefined && v !== '')

  return (
    <section
      aria-labelledby="filters-heading"
      className="rounded-lg border border-border bg-card p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 id="filters-heading" className="font-mono text-xs uppercase tracking-[0.2em] text-forest-700">
            Filtres
          </h2>
          <p className="mt-1 text-sm text-muted-foreground tabular-nums">
            <span className="font-semibold text-forest-900">
              {formatInt(totalFiltered)}
            </span>{' '}
            {totalFiltered === totalUnfiltered ? 'trajets' : `sur ${formatInt(totalUnfiltered)} trajets`}
          </p>
        </div>

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onReset}>
            <X className="h-3.5 w-3.5" aria-hidden="true" />
            Réinitialiser
          </Button>
        )}
      </div>

      {/* ligne 1 — Départ → Arrivée (combobox via datalist) */}
      <div className="mt-5 grid gap-4 md:grid-cols-[1fr_auto_1fr]">
        <FieldGroup id="filter-depart" label="Gare de départ">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" aria-hidden="true" />
            <Input
              id="filter-depart"
              list="gares-list"
              value={filters.depart ?? ''}
              onChange={(e) => onChange({ depart: e.target.value || undefined })}
              placeholder="Paris, Berlin, Vienna…"
              className="pl-10"
              autoComplete="off"
            />
          </div>
        </FieldGroup>

        <div className="hidden md:flex items-end justify-center pb-2.5 text-muted-foreground" aria-hidden="true">
          <ArrowRight className="h-5 w-5" />
        </div>

        <FieldGroup id="filter-arrivee" label="Gare d'arrivée">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" aria-hidden="true" />
            <Input
              id="filter-arrivee"
              list="gares-list"
              value={filters.arrivee ?? ''}
              onChange={(e) => onChange({ arrivee: e.target.value || undefined })}
              placeholder="Rome, Madrid, Amsterdam…"
              className="pl-10"
              autoComplete="off"
            />
          </div>
        </FieldGroup>

        {/* datalist partagée pour autocomplete */}
        <datalist id="gares-list">
          {gares.map((g) => <option key={g} value={g} />)}
        </datalist>
      </div>

      {/* ligne 2 — Type, Opérateur, Ligne */}
      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <FieldGroup id="filter-type" label="Type de service">
          <Select
            id="filter-type"
            value={filters.type ?? ''}
            onChange={(e) =>
              onChange({ type: (e.target.value || undefined) as 'JOUR' | 'NUIT' | undefined })
            }
          >
            <option value="">Tous les types</option>
            <option value="JOUR">Jour</option>
            <option value="NUIT">Nuit</option>
          </Select>
        </FieldGroup>

        <FieldGroup id="filter-operateur" label="Opérateur">
          <Select
            id="filter-operateur"
            value={filters.operateur ?? ''}
            onChange={(e) => onChange({ operateur: e.target.value || undefined })}
          >
            <option value="">Tous les opérateurs</option>
            {operateurs.map((op) => (
              <option key={op} value={op}>{op}</option>
            ))}
          </Select>
        </FieldGroup>

        <FieldGroup id="filter-ligne" label="Ligne">
          <Select
            id="filter-ligne"
            value={filters.ligne ?? ''}
            onChange={(e) =>
              onChange({ ligne: e.target.value ? Number(e.target.value) : undefined })
            }
          >
            <option value="">Toutes les lignes</option>
            {lignes.map((l) => (
              <option key={l.id_ligne} value={l.id_ligne}>
                {l.nom_ligne}
              </option>
            ))}
          </Select>
        </FieldGroup>
      </div>

      {/* ligne 3 — Plage horaire départ */}
      <fieldset className="mt-5">
        <legend className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-wider text-forest-700 mb-2">
          <Clock className="h-3.5 w-3.5" aria-hidden="true" />
          Plage horaire de départ
        </legend>
        <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr] items-end">
          <FieldGroup id="filter-hmin" label="À partir de" size="sm">
            <Input
              id="filter-hmin"
              type="time"
              value={filters.heureMin ?? ''}
              onChange={(e) => onChange({ heureMin: e.target.value || undefined })}
            />
          </FieldGroup>
          <div className="hidden md:flex items-end justify-center pb-2.5 text-muted-foreground" aria-hidden="true">
            <ArrowRight className="h-4 w-4" />
          </div>
          <FieldGroup id="filter-hmax" label="Jusqu'à" size="sm">
            <Input
              id="filter-hmax"
              type="time"
              value={filters.heureMax ?? ''}
              onChange={(e) => onChange({ heureMax: e.target.value || undefined })}
            />
          </FieldGroup>
        </div>
      </fieldset>
    </section>
  )
}

// ─────────────────────────────────────────────────────────────────

function FieldGroup({
  id,
  label,
  size = 'md',
  children,
}: {
  id: string
  label: string
  size?: 'sm' | 'md'
  children: React.ReactNode
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className={`block font-mono uppercase tracking-wider text-forest-700 mb-1.5 ${
          size === 'sm' ? 'text-[10px]' : 'text-[11px]'
        }`}
      >
        {label}
      </label>
      {children}
    </div>
  )
}

function formatInt(n: number) {
  return new Intl.NumberFormat('fr-FR').format(n)
}
