import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Props {
  currentPage: number
  totalPages: number
  totalItems: number
  pageSize: number
  onPageChange: (page: number) => void
}

export function TrajetsPagination({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
}: Props) {
  if (totalPages <= 1) return null

  const start = (currentPage - 1) * pageSize + 1
  const end = Math.min(currentPage * pageSize, totalItems)

  return (
    <nav
      aria-label="Pagination des trajets"
      className="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-border pt-6"
    >
      {/* Texte descriptif — annonce pour screen readers */}
      <p className="text-sm text-muted-foreground tabular-nums" aria-live="polite">
        Trajets{' '}
        <span className="font-medium text-forest-900">
          {formatInt(start)}–{formatInt(end)}
        </span>{' '}
        sur{' '}
        <span className="font-medium text-forest-900">{formatInt(totalItems)}</span>
      </p>

      {/* Contrôles */}
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          aria-label="Page précédente"
        >
          <ChevronLeft className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">Précédent</span>
        </Button>

        {/* Numéros de page compacts */}
        <div className="flex items-center gap-1 mx-2">
          {buildPageRange(currentPage, totalPages).map((item, i) =>
            item === 'ellipsis' ? (
              <span
                key={`ellipsis-${i}`}
                className="px-2 text-sm text-muted-foreground"
                aria-hidden="true"
              >
                …
              </span>
            ) : (
              <button
                key={item}
                onClick={() => onPageChange(item)}
                aria-label={`Page ${item}`}
                aria-current={item === currentPage ? 'page' : undefined}
                className={`
                  min-w-[2.25rem] h-9 rounded-md px-2 text-sm font-medium tabular-nums
                  transition-colors
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
                  ${
                    item === currentPage
                      ? 'bg-forest-900 text-cream-50'
                      : 'text-foreground hover:bg-muted'
                  }
                `}
              >
                {item}
              </button>
            ),
          )}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          aria-label="Page suivante"
        >
          <span className="hidden sm:inline">Suivant</span>
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </Button>
      </div>
    </nav>
  )
}

/**
 * Construit un range compact : [1, …, 4, 5, 6, …, 42]
 * avec toujours la première et la dernière page visibles.
 */
function buildPageRange(current: number, total: number): Array<number | 'ellipsis'> {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const result: Array<number | 'ellipsis'> = []
  const push = (v: number | 'ellipsis') => result.push(v)

  push(1)
  if (current > 3) push('ellipsis')

  for (let p = Math.max(2, current - 1); p <= Math.min(total - 1, current + 1); p++) {
    push(p)
  }

  if (current < total - 2) push('ellipsis')
  push(total)

  return result
}

function formatInt(n: number) {
  return new Intl.NumberFormat('fr-FR').format(n)
}
