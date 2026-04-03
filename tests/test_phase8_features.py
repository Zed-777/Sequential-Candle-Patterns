"""
Phase 8 Feature Tests.

Tests for:
- Portfolio scanner (scan_symbol, scan_portfolio, rank_symbols, portfolio_summary)
- REST API endpoints (health, scan, discover, portfolio/scan, symbols/search)
- CI workflow updates (verified by file content)
"""

from __future__ import annotations

import json
import pandas as pd
import pytest
from unittest.mock import patch
import numpy as np

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ohlcv(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """Build a synthetic OHLCV DataFrame."""
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n))
    open_ = close + rng.normal(0, 0.5, n)
    high = np.maximum(open_, close) + rng.uniform(0, 2, n)
    low = np.minimum(open_, close) - rng.uniform(0, 2, n)
    volume = rng.integers(100, 10000, n).astype(float)
    dates = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame(
        {
            "timestamp": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


# Shared synthetic data for portfolio tests
_FAKE_DF = _make_ohlcv(200, seed=99)


def _mock_fetch(*args, **kwargs):
    """Return the shared synthetic DataFrame regardless of symbol."""
    return _FAKE_DF.copy()


# ===========================================================================
# Portfolio Scanner Tests
# ===========================================================================


class TestScanSymbol:
    """Tests for portfolio.scan_symbol()."""

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=_mock_fetch)
    def test_scan_returns_matches(self, mock_fetch):
        from candle_patterns.portfolio import scan_symbol

        result = scan_symbol("FAKE", ["1R -> 1G"])
        assert result["symbol"] == "FAKE"
        assert result["candles"] == 200
        assert result["error"] is None
        assert len(result["matches"]) == 1
        assert result["matches"][0]["sequence"] == "1R -> 1G"
        assert isinstance(result["matches"][0]["count"], int)

    @patch(
        "candle_patterns.data_feeds.fetch_yahoo_data", side_effect=Exception("network")
    )
    def test_scan_handles_fetch_error(self, mock_fetch):
        from candle_patterns.portfolio import scan_symbol

        result = scan_symbol("BAD", ["1R"])
        assert result["error"] == "network"
        assert result["candles"] == 0

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", return_value=pd.DataFrame())
    def test_scan_handles_empty_data(self, mock_fetch):
        from candle_patterns.portfolio import scan_symbol

        result = scan_symbol("EMPTY", ["1R"])
        assert result["error"] == "No data returned"


class TestScanPortfolio:
    """Tests for portfolio.scan_portfolio()."""

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=_mock_fetch)
    def test_portfolio_multiple_symbols(self, mock_fetch):
        from candle_patterns.portfolio import scan_portfolio

        results = scan_portfolio(["A", "B", "C"], ["1R -> 1G"], max_workers=2)
        assert len(results) == 3
        # Results are sorted by symbol
        symbols = [r["symbol"] for r in results]
        assert symbols == ["A", "B", "C"]

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=_mock_fetch)
    def test_portfolio_multiple_sequences(self, mock_fetch):
        from candle_patterns.portfolio import scan_portfolio

        results = scan_portfolio(["X"], ["1R", "1G", "2R -> 1G"])
        assert len(results) == 1
        assert len(results[0]["matches"]) == 3


class TestRankSymbols:
    """Tests for portfolio.rank_symbols()."""

    def test_rank_by_total_matches(self):
        from candle_patterns.portfolio import rank_symbols

        data = [
            {
                "symbol": "A",
                "matches": [
                    {"count": 5, "stats": {"win_rate": 0.6, "avg_return": 0.01}}
                ],
            },
            {
                "symbol": "B",
                "matches": [
                    {"count": 10, "stats": {"win_rate": 0.4, "avg_return": 0.02}}
                ],
            },
            {"symbol": "C", "matches": [{"count": 0, "stats": {}}]},
        ]
        ranked = rank_symbols(data, sort_by="total_matches")
        assert ranked[0]["symbol"] == "B"
        assert ranked[1]["symbol"] == "A"
        assert ranked[2]["total_matches"] == 0

    def test_rank_by_avg_win_rate(self):
        from candle_patterns.portfolio import rank_symbols

        data = [
            {
                "symbol": "A",
                "matches": [
                    {"count": 5, "stats": {"win_rate": 0.8, "avg_return": 0.01}}
                ],
            },
            {
                "symbol": "B",
                "matches": [
                    {"count": 10, "stats": {"win_rate": 0.4, "avg_return": 0.02}}
                ],
            },
        ]
        ranked = rank_symbols(data, sort_by="avg_win_rate")
        assert ranked[0]["symbol"] == "A"

    def test_rank_by_avg_return(self):
        from candle_patterns.portfolio import rank_symbols

        data = [
            {
                "symbol": "A",
                "matches": [
                    {"count": 5, "stats": {"win_rate": 0.5, "avg_return": 0.05}}
                ],
            },
            {
                "symbol": "B",
                "matches": [
                    {"count": 5, "stats": {"win_rate": 0.5, "avg_return": 0.10}}
                ],
            },
        ]
        ranked = rank_symbols(data, sort_by="avg_return")
        assert ranked[0]["symbol"] == "B"

    def test_rank_handles_no_stats(self):
        from candle_patterns.portfolio import rank_symbols

        data = [{"symbol": "X", "matches": [{"count": 0, "stats": {}}]}]
        ranked = rank_symbols(data)
        assert ranked[0]["avg_win_rate"] is None
        assert ranked[0]["avg_return"] is None


class TestPortfolioSummary:
    """Tests for portfolio.portfolio_summary()."""

    def test_summary_basic(self):
        from candle_patterns.portfolio import portfolio_summary

        data = [
            {"symbol": "A", "matches": [{"count": 3, "sequence": "1R"}]},
            {"symbol": "B", "matches": [{"count": 0, "sequence": "1R"}]},
            {
                "symbol": "C",
                "matches": [
                    {"count": 7, "sequence": "1R"},
                    {"count": 2, "sequence": "2G"},
                ],
            },
        ]
        summary = portfolio_summary(data)
        assert summary["symbols_scanned"] == 3
        assert summary["symbols_with_matches"] == 2
        assert summary["total_matches"] == 12
        assert summary["best_symbol"] == "C"

    def test_summary_empty(self):
        from candle_patterns.portfolio import portfolio_summary

        summary = portfolio_summary([])
        assert summary["symbols_scanned"] == 0
        assert summary["total_matches"] == 0
        assert summary["best_symbol"] is None


# ===========================================================================
# REST API Tests
# ===========================================================================


@pytest.fixture()
def api_client():
    """Create a Flask test client with API routes registered."""
    from flask import Flask
    from candle_patterns.api import register_api_routes

    app = Flask(__name__)
    app.config["TESTING"] = True
    register_api_routes(app)
    with app.test_client() as client:
        yield client


class TestApiHealth:
    """GET /api/health"""

    def test_health_returns_ok(self, api_client):
        resp = api_client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "version" in data


class TestApiScan:
    """GET /api/scan"""

    def test_scan_requires_symbol(self, api_client):
        resp = api_client.get("/api/scan")
        assert resp.status_code == 400
        assert "symbol" in resp.get_json()["error"]

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=_mock_fetch)
    def test_scan_success(self, mock_fetch, api_client):
        resp = api_client.get("/api/scan?symbol=FAKE&sequences=1R%20->%201G")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["symbol"] == "FAKE"
        assert data["candles"] == 200

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=Exception("down"))
    def test_scan_upstream_error(self, mock_fetch, api_client):
        resp = api_client.get("/api/scan?symbol=BAD&sequences=1R")
        assert resp.status_code == 502


class TestApiDiscover:
    """GET /api/discover"""

    def test_discover_requires_symbol(self, api_client):
        resp = api_client.get("/api/discover")
        assert resp.status_code == 400

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=_mock_fetch)
    def test_discover_success(self, mock_fetch, api_client):
        resp = api_client.get("/api/discover?symbol=FAKE")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["symbol"] == "FAKE"
        assert "patterns" in data

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=Exception("fail"))
    def test_discover_fetch_error(self, mock_fetch, api_client):
        resp = api_client.get("/api/discover?symbol=BAD")
        assert resp.status_code == 502


class TestApiPortfolioScan:
    """POST /api/portfolio/scan"""

    def test_portfolio_requires_symbols(self, api_client):
        resp = api_client.post(
            "/api/portfolio/scan",
            data=json.dumps({"sequences": ["1R"]}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_portfolio_max_50_symbols(self, api_client):
        resp = api_client.post(
            "/api/portfolio/scan",
            data=json.dumps(
                {"symbols": [f"S{i}" for i in range(51)], "sequences": ["1R"]}
            ),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "50" in resp.get_json()["error"]

    @patch("candle_patterns.data_feeds.fetch_yahoo_data", side_effect=_mock_fetch)
    def test_portfolio_scan_success(self, mock_fetch, api_client):
        resp = api_client.post(
            "/api/portfolio/scan",
            data=json.dumps({"symbols": ["A", "B"], "sequences": ["1R -> 1G"]}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "summary" in data
        assert "ranked" in data
        assert "details" in data
        assert data["summary"]["symbols_scanned"] == 2


class TestApiSymbolSearch:
    """GET /api/symbols/search"""

    def test_search_requires_q(self, api_client):
        resp = api_client.get("/api/symbols/search")
        assert resp.status_code == 400

    @patch(
        "candle_patterns.data_feeds.search_symbols",
        return_value=[{"symbol": "AAPL", "name": "Apple Inc."}],
    )
    def test_search_success(self, mock_search, api_client):
        resp = api_client.get("/api/symbols/search?q=apple")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["query"] == "apple"
        assert len(data["results"]) == 1

    @patch("candle_patterns.data_feeds.search_symbols", side_effect=Exception("boom"))
    def test_search_upstream_error(self, mock_search, api_client):
        resp = api_client.get("/api/symbols/search?q=test")
        assert resp.status_code == 502


# ===========================================================================
# CI Workflow Verification Tests
# ===========================================================================


class TestWorkflowFiles:
    """Verify CI workflow files have correct content."""

    def test_e2e_uses_python_312(self):
        import pathlib

        content = pathlib.Path(".github/workflows/e2e.yml").read_text()
        assert "python-version: '3.12'" in content
        assert "actions/setup-python@v5" in content

    def test_cleanup_uses_python_312(self):
        import pathlib

        content = pathlib.Path(".github/workflows/cleanup.yml").read_text()
        assert "python-version: '3.12'" in content
        assert "actions/setup-python@v5" in content

    def test_publish_uses_latest_actions(self):
        import pathlib

        content = pathlib.Path(".github/workflows/publish.yml").read_text()
        assert "docker/setup-qemu-action@v3" in content
        assert "docker/login-action@v3" in content
        assert "docker/build-push-action@v6" in content
