import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'

export function RootLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Skip link pour accessibilité clavier — RGAA 12.7 */}
      <a href="#main-content" className="skip-link">
        Aller au contenu principal
      </a>

      <Header />

      <main id="main-content" className="flex-1" tabIndex={-1}>
        <Outlet />
      </main>

      <Footer />
    </div>
  )
}
