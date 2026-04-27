import { TrainFront, Map, Route, Flag } from 'lucide-react'
import {
  useCount,
  useTrajetsParType,
  useEmissions,
  useStatsOperateurs,
} from '@/hooks/useTrajets'
import { StatCard } from '@/components/dashboard/StatCard'
import { JourNuitChart } from '@/components/dashboard/JourNuitChart'
import { OperateursChart } from '@/components/dashboard/OperateursChart'
import { EmissionsChart } from '@/components/dashboard/EmissionsChart'
import { DataQuality } from '@/components/dashboard/DataQuality'

export function Dashboard() {
  const trajetsCountQ = useCount('trajets')
  const garesCountQ = useCount('gares')
  const lignesCountQ = useCount('lignes')
  const paysCountQ = useCount('pays')

  const typeQ = useTrajetsParType()
  const opsQ = useStatsOperateurs()
  const emsQ = useEmissions()

  return (
    <div className="container py-12">
      {/* Header */}
      <header>
        <p className="font-mono text-xs uppercase tracking-[0.25em] text-forest-700">
          Observatoire · 02
        </p>
        <h1 className="mt-2 font-display text-5xl md:text-6xl text-forest-900">
          Tableau de bord
        </h1>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          Vue synthétique de l'entrepôt ferroviaire européen — répartition jour / nuit,
          contributions par opérateur, et comparatif carbone face à l'avion.
        </p>
      </header>

      {/*  KPIs headline  */}
      <section aria-labelledby="kpis-title" className="mt-10">
        <h2 id="kpis-title" className="sr-only">Indicateurs clés</h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Trajets recensés"
            value={formatInt(trajetsCountQ.data?.total_trajets)}
            icon={TrainFront}
            hint="toutes sources confondues"
            accent="forest"
            loading={trajetsCountQ.isLoading}
          />
          <StatCard
            label="Gares référencées"
            value={formatInt(garesCountQ.data?.total_gares)}
            icon={Map}
            hint="avec code UIC"
            loading={garesCountQ.isLoading}
          />
          <StatCard
            label="Lignes suivies"
            value={formatInt(lignesCountQ.data?.total_lignes)}
            icon={Route}
            loading={lignesCountQ.isLoading}
          />
          <StatCard
            label="Pays couverts"
            value={formatInt(paysCountQ.data?.total_pays)}
            icon={Flag}
            hint="à travers l'Europe"
            loading={paysCountQ.isLoading}
          />
        </div>
      </section>

      {/* Rangée 1 : Jour/Nuit + Emissions */}
      <section aria-labelledby="mobilite-title" className="mt-10">
        <h2 id="mobilite-title" className="sr-only">Mobilité durable</h2>
        <div className="grid gap-6 lg:grid-cols-2">
          <JourNuitChart data={typeQ.data} loading={typeQ.isLoading} />
          <EmissionsChart data={emsQ.data} loading={emsQ.isLoading} />
        </div>
      </section>

      {/*Rangée 2 : Opérateurs (full width)*/}
      <section className="mt-6">
        <OperateursChart data={opsQ.data} loading={opsQ.isLoading} />
      </section>

      {/* Rangée 3 : Qualité des données */}
      <section className="mt-6">
        <DataQuality />
      </section>

      {/* Note méthodologique */}
      <aside className="mt-10 border-l-2 border-forest-700 pl-4 py-2 max-w-3xl">
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
          Méthodologie
        </p>
        <p className="mt-2 text-sm text-muted-foreground italic leading-relaxed">
          Les données sont agrégées depuis plusieurs sources open data européennes
          (transport.data.gouv.fr, Back-on-Track, Eurostat, Transitland). Les calculs
          d'empreinte carbone utilisent les moyennes publiées par l'ADEME pour le train
          électrique et l'avion de ligne court-courrier.
        </p>
      </aside>
    </div>
  )
}

function formatInt(n: number | undefined): string | undefined {
  if (n === undefined) return undefined
  return new Intl.NumberFormat('fr-FR').format(n)
}
