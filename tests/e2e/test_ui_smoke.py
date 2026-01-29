import time
import pytest

@pytest.mark.e2e
async def test_basic_ui(page):
    # simple smoke test using Playwright's `page` fixture
    await page.goto('http://127.0.0.1:8050')
    await page.wait_for_selector('nav')
    assert await page.locator('nav').inner_text() is not None
    # check sidebar controls exist
    assert await page.locator('#upload-data').count() == 1
    assert await page.locator('#pattern-checklist').count() == 1
    # check tabs exist
    assert await page.locator('#tabs').count() == 1
    # check export buttons
    assert await page.locator('#export-detections-btn').count() == 1

# simple non-async fallback for pytest-playwright older versions
def test_ui_smoke_sync(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto('http://127.0.0.1:8050')
    page.wait_for_selector('nav')
    assert page.query_selector('nav') is not None
    browser.close()
