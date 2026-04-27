import { test, expect } from '@playwright/test'

test.describe('Supervision', () => {
  test('affiche le statut et les contrôles', async ({ page }) => {
    await page.goto('/supervision')

    await expect(
      page.getByRole('heading', { level: 1, name: 'Supervision' }),
    ).toBeVisible()

    // Statut général
    await expect(page.getByText(/API backend/i).first()).toBeVisible()

    // Contrôles (Pause / Réinitialiser)
    await expect(
      page.getByRole('button', { name: /Pause|Reprendre/i }),
    ).toBeVisible()
    await expect(
      page.getByRole('button', { name: /Réinitialiser/i }),
    ).toBeVisible()
  })

  test('affiche la liste des endpoints', async ({ page }) => {
    await page.goto('/supervision')

    await expect(page.getByRole('heading', { name: /Endpoints surveillés/i })).toBeVisible()
    await expect(page.getByText('GET /trajets/')).toBeVisible()
    await expect(page.getByText('GET /health').or(page.getByText('/stats/trajets/count'))).toBeVisible()
  })

  test('les graphes temps réel sont présents', async ({ page }) => {
    await page.goto('/supervision')

    await expect(page.getByRole('heading', { name: /Latence \/health/i })).toBeVisible()
    await expect(
      page.getByRole('heading', { name: /Disponibilité/i }).first(),
    ).toBeVisible()
  })

  test('la pause arrête et reprend la sonde', async ({ page }) => {
    await page.goto('/supervision')

    const pauseBtn = page.getByRole('button', { name: /^Pause$/ })
    await expect(pauseBtn).toBeVisible({ timeout: 15_000 })
    await pauseBtn.click()

    await expect(page.getByRole('button', { name: /^Reprendre$/ })).toBeVisible()
  })
})
