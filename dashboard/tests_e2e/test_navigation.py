from playwright.sync_api import Page, expect


def test_home_loads(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    assert "ObRail" in page.content()


def test_nav_trajets(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.locator(".st-key-nav_Trajets button").click()
    page.wait_for_load_state("networkidle")
    expect(page.locator("h1")).to_contain_text("Trajets", timeout=15000)


def test_nav_observatoire(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.locator(".st-key-nav_Observatoire button").click()
    page.wait_for_load_state("networkidle")
    expect(page.locator("h1")).to_contain_text("Observatoir", timeout=15000)


def test_nav_supervision(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.locator(".st-key-nav_Supervision button").click()
    expect(page.locator("h1")).to_contain_text("Supervision", timeout=15000)
