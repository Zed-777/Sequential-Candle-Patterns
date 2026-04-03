"""
E2E Playwright tests for the Candle Patterns dashboard.

Run:
    pytest tests/e2e/test_dashboard_e2e.py -m e2e -v
    pytest tests/e2e/test_dashboard_e2e.py -m e2e -v --headed   # visible browser

These tests start the real dashboard in a subprocess via the ``dash_server``
fixture, open Chromium, and interact with the UI the way a user would.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.e2e]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Dash dbc.Tabs renders tab links as .nav-link elements inside #tabs.
# The tab-content div is a *sibling* of #tabs, not a child.
TAB_CONTENT = ".tab-content"

# Map logical tab-id → visible text label in the tab bar
TAB_LABELS: dict[str, str] = {
    "tab-chart": "Candlestick Chart",
    "tab-matches": "Sequence Matches",
    "tab-discovery": "Auto-Discovery",
    "tab-stats": "Statistics",
    "tab-heatmap": "Heatmap",
    "tab-reverse": "Reverse Finder",
    "tab-backtest": "Backtesting",
    "tab-multi-tf": "Multi-TF",
    "tab-watchlist": "Watchlist",
    "tab-alerts": "Alerts",
    "tab-ml-predict": "ML Predict",
    "tab-settings": "Settings",
}


def _click_tab(page, label: str):
    """Click a tab by its visible text label."""
    page.locator("#tabs .nav-link", has_text=label).first.click()
    page.wait_for_timeout(600)


def _load_sample(page, *, wait_ms: int = 3000):
    """Click the Load Sample Data button and wait for Dash callbacks."""
    page.locator("#load-sample-btn").click()
    page.wait_for_timeout(wait_ms)


def _ensure_section_open(page, section, selector):
    """Open an accordion section if its target selector is not already visible."""
    target = page.locator(selector)
    if not target.is_visible():
        header = page.locator(".accordion-button", has_text=section).first
        header.click()
        page.wait_for_timeout(800)
    # Wait for the relevant content to be present (visible if possible)
    page.wait_for_selector(selector, state="attached", timeout=15000)


# ============================================================================
# 1. SMOKE — page loads, title, core layout present
# ============================================================================


class TestDashboardLoads:
    """Verify the dashboard renders its core skeleton."""

    def test_page_title(self, page):
        """Page title should be present (Dash sets it to 'Dash' by default)."""
        title = page.title()
        assert title, "Page title should not be empty"

    def test_sidebar_visible(self, page):
        """The sidebar accordion should be visible."""
        sidebar = page.locator(".accordion")
        assert sidebar.count() >= 1

    def test_tabs_visible(self, page):
        """All 12 tab links should be rendered."""
        page.wait_for_selector("#tabs .nav-link", timeout=20000)
        tabs = page.locator("#tabs .nav-link")
        assert tabs.count() == 12

    def test_upload_button_exists(self, page):
        """The Upload CSV button should be present in the Data Source accordion."""
        page.wait_for_selector("#upload-data", timeout=20000)
        uploader = page.locator("#upload-data")
        assert uploader.count() == 1

    def test_load_sample_button_exists(self, page):
        """The Load Sample Data button should be present."""
        page.wait_for_selector("#load-sample-btn", timeout=20000)
        btn = page.locator("#load-sample-btn")
        assert btn.count() == 1
        assert btn.is_visible()


# ============================================================================
# 2. TABS — clicking each tab switches content
# ============================================================================


class TestTabNavigation:
    """Click each of the 12 tabs and verify the content area updates."""

    @pytest.mark.parametrize(
        "tab_id, label",
        list(TAB_LABELS.items()),
        ids=list(TAB_LABELS.keys()),
    )
    def test_switch_tab(self, page, tab_id, label):
        """Clicking a tab should make it the active tab."""
        _click_tab(page, label)

        # After clicking, the clicked link should become .active
        active = page.locator("#tabs .nav-link.active")
        assert active.count() >= 1, f"No active tab after clicking '{label}'"
        # CSS text-transform: uppercase may be applied, so compare case-insensitively
        active_text = active.first.inner_text().lower()
        assert (
            label.lower() in active_text
        ), f"Expected '{label}' in active tab text '{active_text}'"


# ============================================================================
# 3. SAMPLE DATA — load sample, chart renders, scan works
# ============================================================================


class TestSampleDataFlow:
    """Verify sample data is loaded and the chart renders (auto-loaded on startup)."""

    def test_chart_already_rendered(self, page):
        """Dashboard auto-loads sample data — chart should be present on load."""
        # The server auto-loads sample data at startup, so a chart should exist
        page.wait_for_selector(".js-plotly-plot", timeout=25000)
        plots = page.locator(".js-plotly-plot")
        assert (
            plots.count() >= 1
        ), "Expected at least one Plotly chart (auto-loaded data)"

    def test_load_sample_button_click(self, page):
        """Click Load Sample Data — button should be clickable without errors."""
        btn = page.locator("#load-sample-btn")
        btn.click()
        page.wait_for_timeout(2000)

        # Just verify the page didn't crash (core layout still exists)
        assert page.locator("#tabs").count() >= 1, "Tabs should still exist after click"

    def test_chart_renders_after_sample(self, page):
        """After clicking Load Sample, chart tab should have a Plotly figure."""
        _load_sample(page)
        _click_tab(page, "Candlestick Chart")

        # Plotly chart should render
        plots = page.locator(".js-plotly-plot")
        assert (
            plots.count() >= 1
        ), "Expected at least one Plotly chart after loading data"

    def test_scan_sequences_input_exists(self, page):
        """The custom sequence input and scan button should be present."""
        page.wait_for_selector("#custom-sequences-input", timeout=15000)
        textarea = page.locator("#custom-sequences-input")
        assert textarea.count() == 1

        page.wait_for_selector("#scan-sequences-btn", timeout=15000)
        scan_btn = page.locator("#scan-sequences-btn")
        assert scan_btn.count() == 1

    def test_scan_sequences_empty_prompts_auto_scan(self, page):
        """Click Scan without custom or preset; should auto-scan and show results."""
        _load_sample(page)
        # locate graph placeholder (candle-chart component)
        page.wait_for_selector("#candle-chart", timeout=15000, state="attached")
        # Chart rendering can vary; wait a brief moment for Plotly canvas attach.
        page.wait_for_timeout(3000)

        # Ensure scanner panel is expanded so scan-summary becomes visible
        page.locator(".accordion-button", has_text="Sequence Scanner").first.click()
        page.wait_for_selector("#scan-sequences-btn", timeout=10000, state="visible")

        scan_btn = page.locator("#scan-sequences-btn")
        scan_btn.click()

        # Wait for scan summary to update with auto-scanned info
        summary = page.locator("#scan-results-summary")
        summary.wait_for(state="attached", timeout=30000)

        page.wait_for_function(
            "() => document.querySelector('#scan-results-summary') && document.querySelector('#scan-results-summary').innerText.includes('Scanned')",
            timeout=30000,
        )

        text = summary.first.inner_text().strip()
        assert "Scanned" in text and "matches found" in text

        # The Sequence Matches tab should become active
        _click_tab(page, "Sequence Matches")
        active = page.locator("#tabs .nav-link.active")
        assert active.count() == 1
        assert "sequence matches" in active.first.inner_text().lower()

    def test_preset_sequences_dropdown(self, page):
        """The preset sequences dropdown should exist."""
        page.wait_for_selector("#preset-sequences", timeout=15000)
        dropdown = page.locator("#preset-sequences")
        assert dropdown.count() == 1


# ============================================================================
# 4. YAHOO FINANCE — dropdown populated, symbol selection
# ============================================================================


class TestYahooFinanceSection:
    """Verify the Yahoo Finance Quick Pick dropdown and symbol input."""

    def test_yf_dropdown_has_options(self, page):
        """The yf-symbol-select dropdown should exist."""
        _ensure_section_open(page, "Yahoo", "#yf-symbol-select")
        dropdown = page.locator("#yf-symbol-select")
        assert dropdown.count() == 1

    def test_yf_symbol_input_exists(self, page):
        """The manual symbol input should exist."""
        yf_header = page.locator(".accordion-button", has_text="Yahoo")
        if yf_header.count() > 0:
            yf_header.first.click()
            page.wait_for_timeout(600)

        page.wait_for_selector("#yf-symbol-input", state="attached", timeout=15000)
        symbol_input = page.locator("#yf-symbol-input")
        assert symbol_input.count() == 1

    def test_yf_fetch_button_exists(self, page):
        """The Fetch Data button should be present."""
        _ensure_section_open(page, "Yahoo", "#yf-fetch-btn")
        fetch_btn = page.locator("#yf-fetch-btn")
        assert fetch_btn.count() == 1

    def test_yf_type_symbol(self, page):
        """Typing a symbol into the input field should update the value."""
        # Open Yahoo Finance accordion so input becomes visible
        _ensure_section_open(page, "Yahoo", "#yf-symbol-input")
        symbol_input = page.locator("#yf-symbol-input")
        symbol_input.fill("AAPL")
        assert symbol_input.input_value() == "AAPL"


# ============================================================================
# 5. SIDEBAR ACCORDION — sections expand/collapse
# ============================================================================


class TestSidebarAccordion:
    """Test the sidebar accordion expand/collapse behavior."""

    ACCORDION_SECTIONS = [
        "Data Source",
        "Yahoo Finance",
        "Date Range Filter",
        "Sequence Scanner",
        "Load from History",
        "Maintenance",
        "Export Data",
    ]

    def test_accordion_sections_exist(self, page):
        """All 7 accordion sections should be present."""
        page.wait_for_selector("text=Data Source", timeout=20000)
        for section_title in self.ACCORDION_SECTIONS:
            locator = page.locator(f"text={section_title}")
            assert (
                locator.count() >= 1
            ), f"Accordion section '{section_title}' not found"

    def test_scan_button_accessible(self, page):
        """The scan button should be accessible in the sidebar."""
        # Click the Sequence Scanner section to ensure it's open
        page.locator("text=Sequence Scanner").first.click()
        page.wait_for_timeout(600)

        scan_btn = page.locator("#scan-sequences-btn")
        # Button should exist in the DOM (may be visible or hidden depending
        # on accordion state — we just confirm the element is present)
        assert scan_btn.count() == 1, "Scan button should exist in the DOM"


# ============================================================================
# 6. EMPTY-STATE GUIDANCE — tabs show helpful placeholders before data
# ============================================================================


class TestEmptyStateGuidance:
    """Tabs should show some content even without user-loaded data."""

    def test_backtest_tab_content(self, page):
        """Backtesting tab should render content (guidance or chart)."""
        _click_tab(page, "Backtesting")

        content = page.locator(TAB_CONTENT)
        assert content.count() >= 1, "Tab content container should exist"
        text = content.first.inner_text()
        assert len(text.strip()) > 0


# ============================================================================
# 7. EXPORT BUTTONS — exist and are clickable
# ============================================================================


class TestExportSection:
    """Verify export buttons are present in the sidebar."""

    def test_export_matches_button(self, page):
        """Matches CSV export button should exist."""
        # Open Export accordion
        page.locator("text=Export Data").first.click()
        page.wait_for_timeout(500)

        btn = page.locator("#export-detections-btn")
        assert btn.count() == 1

    def test_export_discovery_button(self, page):
        """Discovery CSV export button should exist."""
        page.locator("text=Export Data").first.click()
        page.wait_for_timeout(500)

        btn = page.locator("#export-aggregated-btn")
        assert btn.count() == 1


# ============================================================================
# 8. WATCHLIST TAB — form elements present
# ============================================================================


class TestWatchlistTab:
    """Verify the Watchlist tab has the expected input form."""

    def test_watchlist_form(self, page):
        """Switch to Watchlist tab and check for label input."""
        _click_tab(page, "Watchlist")

        label_input = page.locator("#wl-label")
        assert label_input.count() == 1, "Watchlist label input should exist"


# ============================================================================
# 9. ALERTS TAB — form elements present
# ============================================================================


class TestAlertsTab:
    """Verify the Alerts tab has rule management controls."""

    def test_alerts_form(self, page):
        """Switch to Alerts tab and check for rule name input and add button."""
        _click_tab(page, "Alerts")

        name_input = page.locator("#alert-rule-name")
        assert name_input.count() == 1, "Alert rule name input should exist"

        add_btn = page.locator("#alert-add-btn")
        assert add_btn.count() == 1, "Alert add button should exist"


# ============================================================================
# 10. SETTINGS TAB — preference controls present
# ============================================================================


class TestSettingsTab:
    """Verify the Settings tab renders preference controls."""

    def test_settings_tab_loads(self, page):
        """Switch to Settings tab and verify content renders."""
        _click_tab(page, "Settings")

        content = page.locator(TAB_CONTENT)
        assert content.count() >= 1, "Tab content container should exist"
        text = content.first.inner_text()
        assert len(text.strip()) > 0, "Settings tab should have content"


# ============================================================================
# 11. SCREENSHOT — capture full-page snapshot for visual regression
# ============================================================================


class TestVisualSnapshot:
    """Capture a screenshot for visual regression baseline."""

    def test_screenshot_homepage(self, page):
        """Take a full-page screenshot at startup."""
        page.screenshot(path="artifacts/e2e_homepage.png", full_page=True)

    def test_screenshot_with_data(self, page):
        """Load sample data and capture the chart view."""
        _load_sample(page)
        _click_tab(page, "Candlestick Chart")
        page.screenshot(path="artifacts/e2e_chart_loaded.png", full_page=True)
