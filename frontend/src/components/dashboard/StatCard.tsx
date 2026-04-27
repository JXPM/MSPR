import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Props {
  label: string
  value: string | number | undefined
  icon?: LucideIcon
  hint?: string
  accent?: 'default' | 'rust' | 'midnight' | 'forest'
  loading?: boolean
  className?: string
}

export function StatCard({ label, value, icon: Icon, hint, accent = 'default', loading, className }: Props) {
  const styles = {
    default:  'bg-card text-foreground border-border',
    rust:     'bg-rust-500/10 text-rust-600 border-rust-500/20',
    midnight: 'bg-midnight-900 text-cream-50 border-midnight-700',
    forest:   'bg-forest-900 text-cream-50 border-forest-900',
  }[accent]

  const subtleText = accent === 'midnight' || accent === 'forest'
    ? 'text-cream-50/60'
    : accent === 'rust'
      ? 'text-rust-600/70'
      : 'text-muted-foreground'

  return (
    <div className={cn('relative overflow-hidden rounded-lg border p-6', styles, className)}>
      <div className="flex items-start justify-between gap-3">
        <p className={cn('font-mono text-[10px] uppercase tracking-[0.2em]', subtleText)}>
          {label}
        </p>
        {Icon && <Icon className="h-4 w-4 opacity-60" aria-hidden="true" />}
      </div>
      <p className="mt-4 font-display text-4xl md:text-5xl tabular-nums leading-none">
        {loading ? <span className="opacity-30">—</span> : value ?? '—'}
      </p>
      {hint && (
        <p className={cn('mt-2 text-xs', subtleText)}>{hint}</p>
      )}
    </div>
  )
}
