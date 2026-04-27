import { NavLink, Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { TrainFront, BarChart3, Activity, Map } from 'lucide-react'

const navItems = [
  { to: '/trajets',     label: 'Trajets',     icon: Map },
  { to: '/dashboard',   label: 'Observatoire', icon: BarChart3 },
  { to: '/supervision', label: 'Supervision', icon: Activity },
]

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-cream-100/85 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo — marque éditoriale */}
        <Link
          to="/"
          className="flex items-center gap-2.5 group"
          aria-label="ObRail Europe — retour à l'accueil"
        >
          <div className="relative flex h-9 w-9 items-center justify-center rounded-sm bg-forest-900 text-cream-50 transition-transform group-hover:-rotate-3">
            <TrainFront className="h-5 w-5" aria-hidden="true" />
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-display text-lg text-forest-900">ObRail</span>
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-forest-700">
              Europe
            </span>
          </div>
        </Link>

        {/* Navigation — pastilles */}
        <nav aria-label="Navigation principale">
          <ul className="flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    cn(
                      'inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-forest-900 text-cream-50'
                        : 'text-forest-800 hover:bg-cream-200',
                    )
                  }
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  )
}
