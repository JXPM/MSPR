import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export function NotFound() {
  return (
    <div className="container py-32 text-center">
      <p className="font-mono text-xs uppercase tracking-[0.25em] text-muted-foreground">
        Erreur · 404
      </p>
      <h1 className="mt-4 font-display text-7xl text-forest-900">
        Terminus inconnu
      </h1>
      <p className="mt-6 max-w-md mx-auto text-muted-foreground">
        Cette page n'existe pas dans notre observatoire.
        Peut-être une ligne fantôme ?
      </p>
      <Button asChild className="mt-8">
        <Link to="/">Retour à l'accueil</Link>
      </Button>
    </div>
  )
}
