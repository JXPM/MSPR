import { Link } from 'react-router-dom'
import { ArrowRight, Moon, Sun, TrainFront, Activity } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useCount, useTrajetsParType } from '@/hooks/useTrajets'

export function Home() {
  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden grain">
        <div className="container py-20 md:py-32 relative">
          {/* Label éditorial */}
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-forest-700 animate-fade-up">
            Observatoire · Europe · {new Date().getFullYear()}
          </p>

          {/* Titre */}
          <h1
            className="mt-6 font-display text-5xl md:text-7xl lg:text-8xl leading-[0.95] text-forest-900 max-w-5xl animate-fade-up"
            style={{ animationDelay: '100ms' }}
          >
            Le rail européen,<br />
            <span className="italic text-rust-500">de jour comme de nuit</span>.
          </h1>

          {/* Sous-titre */}
          <p
            className="mt-8 max-w-2xl text-lg text-forest-800/80 leading-relaxed animate-fade-up"
            style={{ animationDelay: '200ms' }}
          >
            Un référentiel unifié des dessertes ferroviaires européennes —
            pour mesurer la contribution du train à la mobilité bas-carbone
            et éclairer les politiques publiques de demain.
          </p>

          {/* CTAs */}
          <div
            className="mt-10 flex flex-wrap gap-3 animate-fade-up"
            style={{ animationDelay: '300ms' }}
          >
            <Button asChild size="lg">
              <Link to="/dashboard">
                Explorer l'observatoire
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/trajets">Parcourir les trajets</Link>
            </Button>
          </div>
        </div>

        {/* Lignes de rail décoratives en bas */}
        <div className="absolute bottom-0 left-0 right-0 h-px bg-forest-900/20" />
        <div className="absolute bottom-3 left-0 right-0 h-px bg-forest-900/20" />
      </section>

      {/* KPIs */}
      <KpiStrip />

      {/* SECTIONS CARDS */}
      <section className="container py-20">
        <div className="mb-10 flex items-end justify-between">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.25em] text-forest-700">
              Explorer
            </p>
            <h2 className="mt-2 font-display text-4xl text-forest-900">
              Quatre entrées, un seul observatoire
            </h2>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <SectionCard
            to="/trajets"
            kicker="01"
            title="Trajets"
            description="Consulter et filtrer les dessertes ferroviaires par ville, opérateur, type."
            icon={TrainFront}
          />
          <SectionCard
            to="/dashboard"
            kicker="02"
            title="Observatoire"
            description="Répartition jour / nuit, volumes par opérateur, empreinte CO₂ comparée."
            icon={Sun}
          />
          <SectionCard
            to="/trajets"
            kicker="03"
            title="Trains de nuit"
            description="Le renouveau des liaisons nocturnes européennes — ÖBB Nightjet, European Sleeper."
            icon={Moon}
            accent
          />
          <SectionCard
            to="/supervision"
            kicker="04"
            title="Supervision"
            description="État du service en temps réel, latence, disponibilité, incidents."
            icon={Activity}
          />
        </div>
      </section>
    </>
  )
}

// KPIs  bande chiffrée sous le hero 

function KpiStrip() {
  const trajetsQ = useCount('trajets')
  const garesQ = useCount('gares')
  const lignesQ = useCount('lignes')
  const paysQ = useCount('pays')
  const typeQ = useTrajetsParType()

  const items = [
    { label: 'Trajets recensés',  value: trajetsQ.data?.total_trajets },
    { label: 'Gares référencées', value: garesQ.data?.total_gares },
    { label: 'Lignes suivies',    value: lignesQ.data?.total_lignes },
    { label: 'Pays couverts',     value: paysQ.data?.total_pays },
  ]

  const totalType = (typeQ.data?.JOUR ?? 0) + (typeQ.data?.NUIT ?? 0)
  const pctNuit = totalType > 0 ? Math.round(((typeQ.data?.NUIT ?? 0) / totalType) * 100) : null

  return (
    <section className="border-y border-border bg-forest-900 text-cream-50">
      <div className="container grid grid-cols-2 md:grid-cols-5 divide-x divide-forest-800">
        {items.map(({ label, value }) => (
          <div key={label} className="py-8 px-6 first:pl-0 last:pr-0">
            <p className="font-display text-4xl md:text-5xl tabular-nums">
              {value !== undefined ? formatInt(value) : '—'}
            </p>
            <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.2em] text-cream-50/60">
              {label}
            </p>
          </div>
        ))}
        <div className="py-8 px-6 bg-midnight-700 col-span-2 md:col-span-1">
          <p className="font-display text-4xl md:text-5xl tabular-nums italic">
            {pctNuit !== null ? `${pctNuit}%` : '—'}
          </p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.2em] text-cream-50/60">
            Part des trains de nuit
          </p>
        </div>
      </div>
    </section>
  )
}

// Cards navigationnelles

interface SectionCardProps {
  to: string
  kicker: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string; 'aria-hidden'?: boolean }>
  accent?: boolean
}

function SectionCard({ to, kicker, title, description, icon: Icon, accent }: SectionCardProps) {
  return (
    <Link
      to={to}
      className={`
        group relative overflow-hidden rounded-lg border border-border p-6
        transition-all hover:border-forest-900 hover:shadow-lg
        ${accent ? 'bg-midnight-700 text-cream-50 border-midnight-700' : 'bg-card'}
      `}
    >
      <div className="flex items-start justify-between">
        <span className={`font-mono text-xs ${accent ? 'text-cream-50/50' : 'text-muted-foreground'}`}>
          {kicker}
        </span>
        <Icon
          className={`h-5 w-5 ${accent ? 'text-rust-400' : 'text-forest-700'}`}
          aria-hidden={true}
        />
      </div>
      <h3 className={`mt-8 font-display text-2xl ${accent ? 'text-cream-50' : 'text-forest-900'}`}>
        {title}
      </h3>
      <p className={`mt-2 text-sm leading-relaxed ${accent ? 'text-cream-50/70' : 'text-muted-foreground'}`}>
        {description}
      </p>
      <div className="mt-6 inline-flex items-center gap-1.5 text-sm font-medium">
        <span>Ouvrir</span>
        <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" aria-hidden="true" />
      </div>
    </Link>
  )
}

function formatInt(n: number) {
  return new Intl.NumberFormat('fr-FR').format(n)
}
