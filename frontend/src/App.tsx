import { Routes, Route } from 'react-router-dom'
import { RootLayout } from '@/components/layout/RootLayout'
import { Home } from '@/pages/Home'
import { Trajets } from '@/pages/Trajets'
import { TrajetDetail } from '@/pages/TrajetDetail'
import { Dashboard } from '@/pages/Dashboard'
import { Supervision } from '@/pages/Supervision'
import { NotFound } from '@/pages/NotFound'

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<Home />} />
        <Route path="/trajets" element={<Trajets />} />
        <Route path="/trajets/:id" element={<TrajetDetail />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/supervision" element={<Supervision />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
