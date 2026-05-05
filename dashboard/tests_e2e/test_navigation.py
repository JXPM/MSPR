import pytest
from playwright.sync_api import Page, expect


def test_home_loads(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    assert "ObRail" in page.content()


def test_nav_trajets(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Trajets").click()
    page.wait_for_load_state("networkidle")
    # Un tableau ou une liste de trajets doit apparaître
    page.wait_for_selector(
        "[data-testid='stDataFrame'], [data-testid='stTable'], .trajet-row",
        timeout=15000,
        state="attached",
    )


def test_nav_observatoire(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Observatoire").click()
    page.wait_for_load_state("networkidle")
    # La page charge sans erreur Streamlit
    assert "streamlit-error" not in page.content().lower()


def test_nav_supervision(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Supervision").click()
    page.wait_for_load_state("networkidle")
    content = page.content().lower()
    assert "health" in content or "api" in content
