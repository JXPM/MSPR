import { test, expect } from '@playwright/test'

test.describe('Page Trajets', () => {
  test('affiche la liste des trajets après chargement', async ({ page }) => {
    await page.goto('/trajets')

    // Header
    await expect(page.getByRole('heading', { level: 1, name: 'Trajets' })).toBeVisible()

    // Panneau de filtres visible
    await expect(page.getByRole('heading', { name: /Filtres/i })).toBeVisible()

    // Attendre que la liste apparaisse (soit items, soit empty state)
    const liste = page.getByRole('list', { name: /Liste de.*trajets/i })
    const empty = page.getByRole('heading', { name: /Aucun trajet/i })
    await expect(liste.or(empty)).toBeVisible({ timeout: 15_000 })
  })

  test('le filtre départ met à jour l\'URL', async ({ page }) => {
    await page.goto('/trajets')

    // Attendre la fin du chargement initial
    await page
      .getByRole('list', { name: /Liste de.*trajets/i })
      .or(page.getByRole('heading', { name: /Aucun trajet/i }))
      .waitFor({ timeout: 15_000 })

    // Saisie dans le filtre départ
    const departInput = page.getByLabel(/Gare de départ/i)
    await departInput.fill('Paris')

    // URL doit contenir le paramètre
    await expect(page).toHaveURL(/[?&]dep=Paris/)
  })

  test('le filtre type (JOUR/NUIT) fonctionne', async ({ page }) => {
    await page.goto('/trajets')

    await page.waitForLoadState('networkidle')

    const typeSelect = page.getByLabel(/Type de service/i)
    await typeSelect.selectOption('NUIT')

    await expect(page).toHaveURL(/[?&]type=NUIT/)
  })

  test('le bouton réinitialiser nettoie les filtres', async ({ page }) => {
    await page.goto('/trajets?dep=Paris&type=JOUR')

    await page.waitForLoadState('networkidle')

    const resetBtn = page.getByRole('button', { name: /Réinitialiser/i })
    await expect(resetBtn).toBeVisible()
    await resetBtn.click()

    await expect(page).toHaveURL(/\/trajets$/)
  })
})
