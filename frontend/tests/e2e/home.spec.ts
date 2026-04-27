import { test, expect } from '@playwright/test'

test.describe('Page d\'accueil', () => {
  test('affiche le hero éditorial avec le bon titre', async ({ page }) => {
    await page.goto('/')

    // Titre principal
    await expect(
      page.getByRole('heading', { level: 1, name: /Le rail européen/i }),
    ).toBeVisible()

    // Label éditorial
    await expect(page.getByText(/Observatoire · Europe/i)).toBeVisible()

    // CTAs
    await expect(page.getByRole('link', { name: /Explorer l'observatoire/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Parcourir les trajets/i })).toBeVisible()
  })

  test('la navigation principale mène aux 3 sections', async ({ page }) => {
    await page.goto('/')

    // Trajets
    await page.getByRole('link', { name: /^Trajets$/ }).first().click()
    await expect(page).toHaveURL(/\/trajets$/)
    await expect(page.getByRole('heading', { level: 1, name: 'Trajets' })).toBeVisible()

    // Observatoire
    await page.getByRole('link', { name: /Observatoire/ }).first().click()
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('heading', { level: 1, name: /Tableau de bord/i })).toBeVisible()

    // Supervision
    await page.getByRole('link', { name: /Supervision/ }).first().click()
    await expect(page).toHaveURL(/\/supervision$/)
    await expect(page.getByRole('heading', { level: 1, name: 'Supervision' })).toBeVisible()
  })

  test('le skip link est présent pour l\'accessibilité clavier', async ({ page }) => {
    await page.goto('/')
    const skipLink = page.getByRole('link', { name: /Aller au contenu principal/i })
    await expect(skipLink).toBeAttached()
  })
})
