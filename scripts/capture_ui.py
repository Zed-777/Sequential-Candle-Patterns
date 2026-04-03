from pathlib import Path
from playwright.sync_api import sync_playwright

Path("artifacts").mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:8050")
    page.wait_for_selector("nav", timeout=10000)
    page.screenshot(path="artifacts/ui_snapshot.png", full_page=True)
    print("Captured screenshot: artifacts/ui_snapshot.png")
    load_sample_count = page.locator("text=Load sample data").count()
    no_data_count = page.locator("text=No data loaded").count()
    print("Load sample count:", load_sample_count)
    print("No data loaded count:", no_data_count)
    browser.close()
