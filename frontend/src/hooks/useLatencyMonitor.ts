import { useEffect, useRef, useState } from 'react'
import { api } from '@/lib/api'

export interface LatencySample {
  timestamp: number
  latencyMs: number
  status: 'ok' | 'error'
  error?: string
}

/**
 * Sonde l'endpoint /health à intervalle régulier et garde un historique
 * glissant des N derniers échantillons en mémoire (pas de persistance).
 * Calcule latence/disponibilité/taux d'erreurs.
 */
export function useLatencyMonitor(
  intervalMs = 10_000,
  maxSamples = 60,
) {
  const [samples, setSamples] = useState<LatencySample[]>([])
  const [isRunning, setIsRunning] = useState(true)
  const cancelled = useRef(false)

  useEffect(() => {
    cancelled.current = false

    const probe = async () => {
      if (cancelled.current || !isRunning) return
      const start = performance.now()
      let sample: LatencySample
      try {
        await api.get('/health', { timeout: 5000 })
        sample = {
          timestamp: Date.now(),
          latencyMs: Math.round(performance.now() - start),
          status: 'ok',
        }
      } catch (e) {
        sample = {
          timestamp: Date.now(),
          latencyMs: Math.round(performance.now() - start),
          status: 'error',
          error: e instanceof Error ? e.message : 'unknown',
        }
      }
      if (!cancelled.current) {
        setSamples((prev) => {
          const next = [...prev, sample]
          return next.length > maxSamples ? next.slice(-maxSamples) : next
        })
      }
    }

    // Première sonde immédiate
    void probe()
    const interval = window.setInterval(probe, intervalMs)

    return () => {
      cancelled.current = true
      window.clearInterval(interval)
    }
  }, [intervalMs, maxSamples, isRunning])

  // Agrégats
  const okCount = samples.filter((s) => s.status === 'ok').length
  const errorCount = samples.length - okCount
  const uptime = samples.length > 0 ? Math.round((okCount / samples.length) * 100) : null
  const avgLatency = okCount > 0
    ? Math.round(samples.filter((s) => s.status === 'ok').reduce((sum, s) => sum + s.latencyMs, 0) / okCount)
    : null
  const lastSample = samples[samples.length - 1]

  return {
    samples,
    okCount,
    errorCount,
    uptime,
    avgLatency,
    lastSample,
    isRunning,
    pause: () => setIsRunning(false),
    resume: () => setIsRunning(true),
    reset: () => setSamples([]),
  }
}
