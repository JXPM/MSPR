import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('affiche le titre et les sections clés', async ({ page }) => {
    await page.goto('/dashboard')

    await expect(
      page.getByRole('heading', { level: 1, name: /Tableau de bord/i }),
    ).toBeVisible()

    // Section "Jour vs Nuit"
    await expect(page.getByRole('heading', { name: /Jour vs Nuit/i })).toBeVisible({
      timeout: 15_000,
    })

    // Section empreinte CO2
    await expect(page.getByRole('heading', { name: /Empreinte CO₂/i })).toBeVisible()

    // Section opérateurs
    await expect(page.getByRole('heading', { name: /Volumes par opérateur/i })).toBeVisible()

    // Section qualité
    await expect(page.getByRole('heading', { name: /Complétude par dimension/i })).toBeVisible()
  })

  test('affiche la note méthodologique', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText(/Méthodologie/i)).toBeVisible()
    await expect(page.getByText(/transport.data.gouv.fr/i)).toBeVisible()
  })
})
