"""REST API for headless / programmatic integrations.

Provides JSON endpoints backed by the same pattern engine used by the Dash
dashboard.  All routes are mounted on Dash's underlying Flask ``server``
object so they share the same host:port (default ``localhost:8050``).

Usage
-----
Import and call :func:`register_api_routes` once after the Dash app is created:

    >>> from candle_patterns.api import register_api_routes
    >>> register_api_routes(app.server)

Endpoints
---------
GET  /api/health             — liveness check
GET  /api/scan               — scan a symbol for sequences
GET  /api/discover           — auto-discover patterns for a symbol
POST /api/portfolio/scan     — scan multiple symbols
GET  /api/symbols/search     — search for ticker symbols
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from flask import Flask, jsonify, request

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------


def register_api_routes(server: Flask) -> None:
    """Mount all ``/api/*`` routes on the given Flask server."""

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------
    @server.route("/api/health", methods=["GET"])
    def api_health() -> Any:
        """Return service status."""
        from candle_patterns import __version__

        return jsonify({"status": "ok", "version": __version__})

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------
    @server.route("/api/scan", methods=["GET"])
    def api_scan() -> Any:
        """Scan a single symbol for sequences.

        Query params:
            symbol   (str)  — ticker, e.g. AAPL  (required)
            sequences (str) — comma-separated list, e.g. "3R -> 2G,Hammer -> 1G"
            period   (str)  — default "6mo"
            interval (str)  — default "1d"
            hold     (int)  — hold candles for stats, default 5
        """
        symbol = request.args.get("symbol")
        if not symbol:
            return jsonify({"error": "symbol is required"}), 400

        raw_seqs = request.args.get("sequences", "3R -> 2G")
        sequences = [s.strip() for s in raw_seqs.split(",") if s.strip()]
        if not sequences:
            return jsonify({"error": "at least one sequence is required"}), 400

        period = request.args.get("period", "6mo")
        interval = request.args.get("interval", "1d")
        hold = int(request.args.get("hold", "5"))

        from .portfolio import scan_symbol

        result = scan_symbol(
            symbol, sequences, period=period, interval=interval, hold_candles=hold
        )
        if result.get("error"):
            return jsonify(result), 502

        return jsonify(result)

    # ------------------------------------------------------------------
    # Discover
    # ------------------------------------------------------------------
    @server.route("/api/discover", methods=["GET"])
    def api_discover() -> Any:
        """Auto-discover recurring patterns for a symbol.

        Query params:
            symbol   (str) — required
            period   (str) — default "6mo"
            interval (str) — default "1d"
            min_len  (int) — minimum sequence length (default 3)
            max_len  (int) — maximum sequence length (default 8)
            top_n    (int) — max results (default 25)
        """
        symbol = request.args.get("symbol")
        if not symbol:
            return jsonify({"error": "symbol is required"}), 400

        period = request.args.get("period", "6mo")
        interval = request.args.get("interval", "1d")
        min_len = int(request.args.get("min_len", "3"))
        max_len = int(request.args.get("max_len", "8"))
        top_n = int(request.args.get("top_n", "25"))

        from .data_feeds import fetch_yahoo_data
        from .patterns import discover_color_sequences

        try:
            df = fetch_yahoo_data(symbol, period=period, interval=interval)
        except Exception as exc:
            return jsonify({"error": f"fetch failed: {exc}"}), 502

        if df is None or df.empty:
            return jsonify({"error": "no data for symbol"}), 404

        discovered = discover_color_sequences(
            df, min_len=min_len, max_len=max_len, top_k=top_n
        )
        return jsonify(
            {
                "symbol": symbol,
                "candles": len(df),
                "patterns": discovered,
            }
        )

    # ------------------------------------------------------------------
    # Portfolio scan
    # ------------------------------------------------------------------
    @server.route("/api/portfolio/scan", methods=["POST"])
    def api_portfolio_scan() -> Any:
        """Scan multiple symbols for patterns.

        JSON body:
            {
                "symbols": ["AAPL", "MSFT"],
                "sequences": ["3R -> 2G", "Hammer -> 1G"],
                "period": "6mo",   (optional)
                "interval": "1d",  (optional)
                "hold": 5,         (optional)
                "max_workers": 4   (optional)
            }
        """
        body: Dict = request.get_json(silent=True) or {}

        symbols = body.get("symbols", [])
        if not symbols:
            return jsonify({"error": "symbols list is required"}), 400
        if len(symbols) > 50:
            return jsonify({"error": "max 50 symbols per request"}), 400

        sequences = body.get("sequences", ["3R -> 2G"])
        if not sequences:
            return jsonify({"error": "sequences list is required"}), 400

        period = body.get("period", "6mo")
        interval = body.get("interval", "1d")
        hold = int(body.get("hold", 5))
        max_workers = min(int(body.get("max_workers", 4)), 8)

        from .portfolio import portfolio_summary, rank_symbols, scan_portfolio

        results = scan_portfolio(
            symbols,
            sequences,
            period=period,
            interval=interval,
            hold_candles=hold,
            max_workers=max_workers,
        )
        ranked = rank_symbols(results)
        summary = portfolio_summary(results)

        return jsonify(
            {
                "summary": summary,
                "ranked": ranked,
                "details": results,
            }
        )

    # ------------------------------------------------------------------
    # Symbol search
    # ------------------------------------------------------------------
    @server.route("/api/symbols/search", methods=["GET"])
    def api_symbol_search() -> Any:
        """Search for ticker symbols.

        Query params:
            q (str) — search term (required)
        """
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "q is required"}), 400

        from .data_feeds import search_symbols

        try:
            results = search_symbols(query)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 502

        return jsonify({"query": query, "results": results})

    logger.info("API routes registered on Flask server")
