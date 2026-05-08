import pytest
from playwright.sync_api import Page


def test_skip_link_exists(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    skip_link = page.locator('a[href="#main-content"]')
    assert skip_link.count() > 0, "Skip link 'Aller au contenu principal' introuvable"


def test_h1_present(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    h1_count = page.locator("h1").count()
    assert h1_count >= 1, "Aucun <h1> trouvé sur la page d'accueil"
