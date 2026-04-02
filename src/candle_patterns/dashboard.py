from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from pathlib import Path
from dash import html, dcc, Input, Output, State, callback_context, ALL
from dash.dcc.express import send_data_frame, send_bytes
import plotly.graph_objects as go
import json
import logging
import base64
import io
import pandas as pd
from flask import Flask
from typing import Any, cast

from candle_patterns.patterns import (
    find_sequence_occurrences,
    find_wildcard_sequence,
    sequence_length,
    discover_color_sequences,
    what_comes_next,
    sequence_outcome_stats,
    reverse_pattern_finder,
    sequence_confidence,
    sequence_heatmap_data,
    count_followup_pattern,
    find_followup_outcomes,
)

from candle_patterns.data_feeds import (
    fetch_yahoo_data,
    POPULAR_SYMBOLS,
    VALID_INTERVALS,
    VALID_PERIODS,
)

from candle_patterns.multi_timeframe import (
    multi_timeframe_summary,
)

from candle_patterns.watchlist import (
    list_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    update_last_used,
)

from candle_patterns.backtesting import BacktestEngine

from candle_patterns.storage import save_upload

from candle_patterns.alerts import (
    add_alert_rule,
    list_alert_rules,
    get_alert_history,
    clear_alert_history,
    get_unread_count,
)

from candle_patterns.ml_sequence import (
    train_sequence_predictor,
)

from candle_patterns.preferences import (
    load_preferences,
    save_preferences,
    reset_preferences,
)

from candle_patterns.performance import (
    dataset_info,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PRESET SEQUENCE LIBRARY — common colour-based candle sequences
# ============================================================================
PRESET_SEQUENCES = {
    "3R -> 2G":               "3R -> 2G",
    "3G -> 2R":               "3G -> 2R",
    "5R -> 3G":               "5R -> 3G",
    "5G -> 3R":               "5G -> 3R",
    "2R -> 1G -> 2R":         "2R -> 1G -> 2R",
    "2G -> 1R -> 2G":         "2G -> 1R -> 2G",
    "4R -> 1G -> 3R":         "4R -> 1G -> 3R",
    "3G -> 1R -> 3G":         "3G -> 1R -> 3G",
    "2R -> Doji -> 2G":       "2R -> Doji -> 2G",
    "3G -> Doji -> 3R":       "3G -> Doji -> 3R",
    "1R -> 1G -> 1R -> 1G":   "1R -> 1G -> 1R -> 1G",
    "5R -> 5G":               "5R -> 5G",
    "4G -> 4R":               "4G -> 4R",
    "3R -> 1G -> 1R -> 1G":   "3R -> 1G -> 1R -> 1G",
    "2G -> 2R -> 2G":         "2G -> 2R -> 2G",
}

# Distinct colours for up to 15 simultaneous sequences on the chart
SEQUENCE_COLORS = [
    "#6366f1", "#ec4899", "#f59e0b", "#10b981", "#3b82f6",
    "#8b5cf6", "#ef4444", "#14b8a6", "#f97316", "#06b6d4",
    "#84cc16", "#e879f9", "#fb923c", "#22d3ee", "#a78bfa",
]

# Modern professional stylesheet with custom CSS
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
]
external_scripts = ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js']

class CustomDash(dash.Dash):
    default_sample_data: Any = None


app = CustomDash(
    __name__, 
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts
)

if app.server is None:
    raise RuntimeError("Dash server is unavailable")

server: Flask = cast(Flask, app.server)

# Register REST API endpoints on the Flask server
try:
    from candle_patterns.api import register_api_routes
    register_api_routes(server)
except Exception as _api_err:
    logger.warning("Could not register API routes: %s", _api_err)


def load_sample_data(trigger_data=None):
    """Load the built-in sample dataset and return the payload + status message."""
    logger.info("[INFO] Loading sample data (trigger=%s)", trigger_data)
    sample_path = Path("data/samples/sample.csv")

    if not sample_path.exists():
        msg = html.Div(
            "[ERROR] Sample file not found. Please ensure data/samples/sample.csv exists.",
            style={"color": "#dc2626", "fontWeight": "600"}
        )
        return None, msg

    try:
        df = pd.read_csv(sample_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        try:
            upload_meta = save_upload(sample_path.name, df, [])
            upload_id = upload_meta.get("upload_id") if isinstance(upload_meta, dict) else upload_meta
        except Exception as db_error:
            logger.warning("Could not save to DB: %s", db_error)
            upload_id = None

        # Convert timestamps to ISO strings for safe JSON serialisation
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        data = {
            "filename": str(sample_path.name),
            "upload_id": upload_id,
            "df": df.to_dict("records"),
        }

        status_html = html.Div(
            [html.I(className="bi bi-check-circle-fill me-2"),
             f"Loaded: {sample_path.name} ({len(df)} candles)"],
            style={
                "color": "#059669",
                "fontWeight": "600",
                "padding": "12px",
                "backgroundColor": "#ecfdf5",
                "borderRadius": "6px",
                "marginTop": "8px"
            }
        )

        return data, status_html
    except Exception as exc:
        logger.exception("[ERROR] Failed to load sample data: %s", exc)
        return None, html.Div(
            f"[ERROR] Error loading sample data: {exc}",
            style={"color": "#dc2626", "fontWeight": "600", "whiteSpace": "pre-wrap"}
        )


def build_candle_figure(data):
    """Build a candlestick figure from provided data payload."""
    if not data or "df" not in data or not data["df"]:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#6366f1", family="sans-serif"),
        )
        fig.update_layout(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            template="plotly_white", height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    df = pd.DataFrame(data["df"])
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    else:
        return go.Figure()

    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])
    if df.empty:
        return go.Figure()

    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color="#10b981",
        decreasing_line_color="#ef4444",
    )])
    fig.update_layout(
        title=f"Candlestick Chart | {len(df)} candles",
        template="plotly_white",
        height=550,
        xaxis=dict(type="date"),
    )
    return fig


def build_default_scan_results(data, max_sequences=3):
    """Generate scan-results from the top discovered sequences (for initial sample load)."""
    if not data or "df" not in data or not data["df"]:
        return None

    df = pd.DataFrame(data["df"])
    if df.empty or "timestamp" not in df.columns:
        return None

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    if df.empty:
        return None

    discovered = discover_color_sequences(df, min_len=3, max_len=8, top_k=max_sequences)
    if not discovered:
        return None

    results = []
    for seq in discovered:
        seq_str = seq.get("sequence")
        if not seq_str:
            continue

        try:
            occ_ends = find_sequence_occurrences(df, seq_str)
            seq_len = sequence_length(seq_str)
            matches = []
            for end_idx in occ_ends:
                start_idx = max(0, end_idx - seq_len + 1)
                matches.append({
                    "start_idx": int(start_idx),
                    "end_idx": int(end_idx),
                    "start_ts": str(df.iloc[start_idx]["timestamp"]),
                    "end_ts": str(df.iloc[end_idx]["timestamp"]),
                })

            results.append({"seq_str": seq_str, "length": seq_len, "matches": matches})

        except Exception as e:
            results.append({"seq_str": seq_str, "length": 0, "matches": [], "error": str(e)})

    return results


def section_banner(title: str, description: str):
    """Create an info banner with tooltip at the top of a tab section."""
    return html.Div(
        [
            html.Strong(title + ": ", style={"fontWeight": "700"}),
            html.Span(description)
        ],
        className="alert alert-info mb-3",
        style={"fontSize": "0.95rem", "padding": "0.7rem 0.9rem", "borderRadius": "10px", "marginBottom": "1rem"},
        title=description,
    )


# ============================================================================
# AUTO-LOAD SAMPLE DATA ON STARTUP
# ============================================================================
print("\n" + "="*80)
print("AUTO-LOADING SAMPLE DATA ON STARTUP...")
print("="*80 + "\n")

app.default_sample_data = None

try:
    data, _ = load_sample_data()
    if data:
        app.default_sample_data = data  # type: ignore[attr-defined]
        logger.info("[OK] Sample auto-loaded for layout")
        try:
            print(f"\n[OK] LOADED: {len(data['df'])} candles\n")
        except (UnicodeEncodeError, UnicodeDecodeError):
            print(f"\n[OK] LOADED: {len(data['df'])} candles\n")
except Exception as e:
    logger.exception(f"Failed to auto-load: {e}")

print("="*80)
print("DASHBOARD READY")
print("="*80 + "\n")

# NOTE: Clientside callback removed - load-sample-btn handled by on_load_sample_click server callback

# Modern, professional, visually appealing stylesheet
custom_css = """
<style>
:root {
    --primary-color: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --secondary-color: #ec4899;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --info-color: #3b82f6;
    
    --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    --secondary-gradient: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
    --success-gradient: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
    --info-gradient: linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%);
    
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-light: #9ca3af;
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    --border-color: #e5e7eb;
    
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.theme-light {
    --background-gradient: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    --panel-bg: #ffffff;
    --panel-border: #e5e7eb;
    --text-primary: #1f2937;
    --text-secondary: #475569;
    --card-bg: #ffffff;
    --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.theme-dark {
    --background-gradient: linear-gradient(135deg, #0b1220 0%, #172135 100%);
    --panel-bg: #0f172a;
    --panel-border: #334155;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --card-bg: #1e293b;
    --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.65);
}

.theme-blue {
    --background-gradient: linear-gradient(135deg, #a5c8ff 0%, #3b82f6 100%);
    --panel-bg: #1e3a8a;
    --panel-border: #2563eb;
    --text-primary: #e0f2fe;
    --text-secondary: #bae6fd;
    --card-bg: #1e40af;
    --card-shadow: 0 1px 16px rgba(30, 64, 175, 0.5);
}

.theme-blue #theme-wrapper .btn-primary {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
    border-color: #1d4ed8 !important;
    color: #e0f2fe !important;
}

.theme-blue .nav-tabs .nav-link.active {
    color: #ffffff !important;
    border-bottom-color: #93c5fd !important;
}


.theme-solar {
    --background-gradient: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%);
    --panel-bg: #fffaf0;
    --panel-border: #facc15;
    --text-primary: #7c2d12;
    --text-secondary: #9a3412;
    --card-bg: #fef3c7;
    --card-shadow: 0 1px 3px rgba(251, 191, 36, 0.2);
}

* {
    box-sizing: border-box;
}

html, body {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    color: var(--text-primary);
    min-height: 100vh;
}

body {
    background-attachment: fixed;
}

#theme-wrapper {
    background: var(--background-gradient);
    color: var(--text-primary);
}

#theme-wrapper .sidebar-card,
#theme-wrapper .card,
#theme-wrapper .chart-card {
    background: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border-color: var(--panel-border) !important;
    box-shadow: var(--card-shadow) !important;
}

#theme-wrapper .accordion-button,
#theme-wrapper .form-control,
#theme-wrapper .btn,
#theme-wrapper .navbar,
#theme-wrapper .nav-tabs .nav-link {
    color: var(--text-primary) !important;
}

#theme-wrapper .navbar {
    background: linear-gradient(135deg, rgba(99,102,241,0.9) 0%, rgba(139,92,246,0.9) 100%) !important;
}

.theme-dark .navbar {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
}

.theme-blue .navbar {
    background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
}

.theme-solar .navbar {
    background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%) !important;
}

/* Navbar & Header Styling */
.navbar {
    background: var(--primary-gradient) !important;
    box-shadow: var(--shadow-lg);
    padding: 1.25rem 2rem !important;
    border-bottom: none !important;
}

.navbar-brand {
    font-weight: 800 !important;
    font-size: 1.5rem !important;
    letter-spacing: -0.025em;
    color: white !important;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.navbar-brand::before {
    content: '';
    font-size: 1.75rem;
}

/* Main Container */
.container-fluid {
    padding: 2rem 1.5rem;
    max-width: 1920px;
    margin: 0 auto;
}

/* Sidebar Card Styling */
.sidebar-card {
    background: var(--bg-primary);
    border-radius: 16px;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
    transition: var(--transition);
    overflow: hidden;
    position: sticky;
    top: 100px;
}

.sidebar-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.sidebar-card .card-body {
    padding: 2rem 1.5rem;
}

.sidebar-card .card-title {
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    letter-spacing: -0.025em;
}

.sidebar-card h6 {
    color: var(--text-secondary);
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Button Styling - Enhanced */
.btn {
    border: none;
    border-radius: 10px;
    font-weight: 700;
    padding: 0.75rem 1.5rem;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.875rem;
    cursor: pointer;
}

.btn::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.btn:hover::before {
    width: 300px;
    height: 300px;
}

.btn:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}

.btn-primary {
    background: var(--primary-gradient) !important;
    color: white !important;
    border: none !important;
}

.btn-success {
    background: var(--success-gradient) !important;
    color: white !important;
    border: none !important;
}

.btn-info {
    background: var(--info-gradient) !important;
    color: white !important;
    border: none !important;
}

.btn-danger {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: white !important;
    border: none !important;
}

.btn-secondary {
    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%) !important;
    color: white !important;
    border: none !important;
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
}

/* Input Fields */
.form-control, input[type="text"], input[type="date"], input[type="datetime"], input[type="datetime-local"], input[type="month"], input[type="number"], input[type="email"], input[type="password"], select, textarea {
    border-radius: 10px !important;
    border: 1.5px solid var(--border-color) !important;
    padding: 0.75rem 1rem !important;
    font-weight: 500;
    transition: var(--transition) !important;
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

.form-control:focus, input:focus, select:focus, textarea:focus {
    border-color: var(--primary-color) !important;
    background: var(--bg-primary) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}

input::placeholder, textarea::placeholder {
    color: var(--text-light) !important;
}

/* Tabs Styling */
.nav-tabs {
    border-bottom: 2px solid var(--border-color) !important;
    gap: 0.5rem;
    padding: 0;
}

.nav-tabs .nav-link {
    color: var(--text-secondary) !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    font-weight: 700 !important;
    padding: 1rem 1.5rem !important;
    transition: var(--transition) !important;
    position: relative;
    text-transform: uppercase;
    font-size: 0.875rem;
    letter-spacing: 0.05em;
}

.nav-tabs .nav-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 3px;
    background: var(--primary-gradient);
    transition: width var(--transition);
}

.nav-tabs .nav-link:hover {
    color: var(--primary-color) !important;
}

.nav-tabs .nav-link:hover::after {
    width: 100%;
}

.nav-tabs .nav-link.active {
    color: var(--primary-color) !important;
    border-bottom-color: var(--primary-color) !important;
}

.nav-tabs .nav-link.active::after {
    width: 100%;
}

/* Tab Icons via CSS ::before using Bootstrap Icons font */
.nav-tabs .nav-item:nth-child(1) .nav-link::before  { content: "\\F2CD"; }  /* bi-graph-up */
.nav-tabs .nav-item:nth-child(2) .nav-link::before  { content: "\\F26A"; }  /* bi-list-check */
.nav-tabs .nav-item:nth-child(3) .nav-link::before  { content: "\\F52A"; }  /* bi-search */
.nav-tabs .nav-item:nth-child(4) .nav-link::before  { content: "\\F17A"; }  /* bi-bar-chart-line */
.nav-tabs .nav-item:nth-child(5) .nav-link::before  { content: "\\F2FE"; }  /* bi-grid-3x3 */
.nav-tabs .nav-item:nth-child(6) .nav-link::before  { content: "\\F124"; }  /* bi-arrow-return-left */
.nav-tabs .nav-item:nth-child(7) .nav-link::before  { content: "\\F1C3"; }  /* bi-calculator */
.nav-tabs .nav-item:nth-child(8) .nav-link::before  { content: "\\F357"; }  /* bi-layers */
.nav-tabs .nav-item:nth-child(9) .nav-link::before  { content: "\\F17F"; }  /* bi-bookmark-star */
.nav-tabs .nav-item:nth-child(10) .nav-link::before { content: "\\F15A"; }  /* bi-bell */
.nav-tabs .nav-item:nth-child(11) .nav-link::before { content: "\\F4F5"; }  /* bi-robot */
.nav-tabs .nav-item:nth-child(12) .nav-link::before { content: "\\F3E5"; }  /* bi-gear */

.nav-tabs .nav-link::before {
    font-family: 'bootstrap-icons' !important;
    margin-right: 0.4em;
    font-size: 0.95em;
    vertical-align: -0.1em;
}

/* Sidebar Accordion */
.sidebar-card .accordion-item {
    border: none !important;
    background: transparent !important;
}
.sidebar-card .accordion-button {
    padding: 0.6rem 0.25rem !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #374151 !important;
    background: transparent !important;
    box-shadow: none !important;
}
.sidebar-card .accordion-button::after {
    width: 0.85rem;
    height: 0.85rem;
    background-size: 0.85rem;
}
.sidebar-card .accordion-button:not(.collapsed) {
    color: #6366f1 !important;
}
.sidebar-card .accordion-body {
    padding: 0.25rem 0 0.75rem 0 !important;
}

/* Card Styling */
.card {
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    box-shadow: var(--shadow-md) !important;
    transition: var(--transition) !important;
    background: var(--bg-primary) !important;
    overflow: hidden;
}

.card:hover {
    box-shadow: var(--shadow-lg) !important;
    transform: translateY(-4px);
}

.card-body {
    padding: 1.5rem !important;
}

.card-header {
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%) !important;
    border-bottom: 1px solid var(--border-color) !important;
    border-radius: 16px 16px 0 0 !important;
    padding: 1.25rem 1.5rem !important;
    font-weight: 700;
    color: var(--text-primary);
}

/* Statistics Cards */
.stat-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: var(--transition);
    box-shadow: var(--shadow-sm);
}

.stat-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.stat-card h6 {
    color: var(--text-secondary);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

.stat-card h4 {
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2rem;
    margin: 0.5rem 0;
}

.stat-card .stat-icon {
    font-size: 2rem;
    margin-bottom: 0.75rem;
}

/* Checklist Items */
.form-check {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--bg-tertiary);
}

.form-check:last-child {
    border-bottom: none;
}

.form-check-input {
    border-radius: 6px;
    border: 2px solid var(--border-color);
    cursor: pointer;
    transition: var(--transition);
}

.form-check-input:checked {
    background: var(--primary-gradient) !important;
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.form-check-label {
    color: var(--text-primary);
    font-weight: 600;
    cursor: pointer;
    margin-left: 0.75rem;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
}

table thead {
    background: var(--primary-gradient);
}

table th {
    color: white;
    padding: 1.25rem;
    font-weight: 700;
    text-align: left;
    border: none;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
}

table td {
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
    font-weight: 500;
}

table tbody tr {
    transition: var(--transition);
    background: var(--bg-primary);
}

table tbody tr:hover {
    background: var(--bg-secondary);
    box-shadow: inset 0 0 10px rgba(99, 102, 241, 0.1);
}

table tbody tr:last-child td {
    border-bottom: none;
}

/* Graphs */
.plotly-graph-div {
    border-radius: 16px !important;
    box-shadow: var(--shadow-md) !important;
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color);
    overflow: hidden !important;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
    border-radius: 16px;
    border: 2px dashed var(--border-color);
    transition: var(--transition);
}

.empty-state:hover {
    border-color: var(--primary-color);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%);
}

.empty-state .empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.empty-state h5 {
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    margin-top: 1rem;
    font-size: 1.5rem;
}

.empty-state p {
    color: var(--text-secondary);
    font-weight: 500;
    margin-top: 0.75rem;
}

/* Modal Styling */
.modal-content {
    border-radius: 16px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-xl) !important;
}

.modal-header {
    background: var(--primary-gradient) !important;
    border-bottom: none !important;
    border-radius: 16px 16px 0 0 !important;
    padding: 1.5rem !important;
}

.modal-header .modal-title {
    color: white !important;
    font-weight: 800 !important;
    font-size: 1.25rem !important;
}

.modal-header .btn-close {
    filter: invert(1) brightness(2);
}

.modal-body {
    padding: 2rem !important;
    background: var(--bg-primary);
}

.modal-footer {
    background: var(--bg-secondary) !important;
    border-top: 1px solid var(--border-color) !important;
    border-radius: 0 0 16px 16px !important;
    padding: 1.5rem !important;
}

/* Upload Feedback */
.upload-feedback {
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #d1fae5 0%, #ccfbf1 100%);
    color: #047857;
    border-radius: 10px;
    border: 1px solid #a7f3d0;
    font-weight: 600;
    margin-top: 1rem;
    box-shadow: var(--shadow-sm);
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Divider */
.hr-style {
    margin: 1.75rem 0;
    border: none;
    border-top: 1px solid var(--border-color);
    opacity: 0.5;
}

/* Responsive */
@media (max-width: 992px) {
    .sidebar-card {
        position: sticky;
        top: auto;
    }
    
    .navbar-brand {
        font-size: 1.25rem;
    }
    
    .btn {
        padding: 0.6rem 1.2rem;
        font-size: 0.8rem;
    }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-gradient);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
}

/* Selection */
::selection {
    background: var(--primary-gradient);
    color: white;
}

::-moz-selection {
    background: var(--primary-gradient);
    color: white;
}
</style>
"""

app.index_string = f'''
<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    {custom_css}
</head>
<body>
    {{%app_entry%}}
    <footer>
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </footer>
</body>
</html>
'''

# Modern gradient navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Span(
                                "Candle Patterns",
                                className="navbar-brand",
                                style={"color": "white", "fontWeight": "800", "fontSize": "1.5rem", "letterSpacing": "-0.5px"}
                            )
                        ],
                        width="auto",
                    ),
                    dbc.Col(
                        [
                            html.Span(
                                "Sequential Candle Pattern Scanner",
                                style={"color": "rgba(255,255,255,0.85)", "fontSize": "0.95rem", "fontWeight": "500"}
                            )
                        ],
                        width="auto",
                    ),
                    dbc.Col(
                        html.Span(
                            id="alert-badge",
                            style={"cursor": "pointer"},
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                align="center",
                className="w-100",
            )
        ],
        fluid=True,
    ),
    sticky="top",
    style={
        "background": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
        "boxShadow": "0 10px 25px rgba(99, 102, 241, 0.15)",
        "padding": "1.25rem 0",
        "zIndex": 1030,
    },
)

sidebar = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5([html.I(className="bi bi-gear-fill"), " Configuration"], className="card-title"),

                dbc.Accordion(
                    [
                        # --- Data Source ---
                        dbc.AccordionItem(
                            [
                                dcc.Upload(
                                    id="upload-data",
                                    children=dbc.Button(
                                        [html.I(className="bi bi-upload"), " Upload CSV"],
                                        color="primary",
                                        className="w-100 mb-3",
                                        style={"fontWeight": "700", "padding": "0.85rem 1.5rem", "fontSize": "0.95rem"}
                                    ),
                                    style={"cursor": "pointer"}
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-database-fill"), " Load Sample Data"],
                                    id="load-sample-btn",
                                    color="success",
                                    className="w-100 mb-3",
                                    style={"fontWeight": "700", "padding": "0.85rem 1.5rem", "fontSize": "0.95rem", "background": "linear-gradient(135deg, #10b981 0%, #14b8a6 100%)", "color": "white", "border": "none", "cursor": "pointer", "borderRadius": "10px"},
                                    n_clicks=0
                                ),
                                dcc.Store(id="load-sample-data-store"),
                                html.Small(
                                    "Load sample dataset (200 candlesticks)",
                                    style={"marginTop": "8px", "color": "#6b7280", "display": "block", "fontWeight": "500"}
                                ),
                                dcc.Loading(
                                    html.Div(
                                        id="upload-status",
                                        style={"marginTop": "12px"},
                                    ),
                                    type="circle", color="#6366f1",
                                ),
                            ],
                            title="Data Source",
                            item_id="acc-data-source",
                        ),

                        # --- Yahoo Finance ---
                        dbc.AccordionItem(
                            [
                                html.Small(
                                    "Fetch real stock, crypto, or index data directly.",
                                    style={"color": "#6b7280", "display": "block", "marginBottom": "0.75rem", "fontWeight": "500"}
                                ),
                                html.Label("Quick Pick Symbol", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151"}),
                                dcc.Dropdown(
                                    id="yf-symbol-select",
                                    options=[
                                        {"label": f"\U0001F4C8 {s}", "value": s}
                                        for s in POPULAR_SYMBOLS["Stocks"]
                                    ] + [
                                        {"label": f"\U0001FA99 {s}", "value": s}
                                        for s in POPULAR_SYMBOLS["Crypto"]
                                    ] + [
                                        {"label": f"\U0001F4CA {s}", "value": s}
                                        for s in POPULAR_SYMBOLS["Indices"]
                                    ] + [
                                        {"label": f"\U0001F4E6 {s}", "value": s}
                                        for s in POPULAR_SYMBOLS["ETFs"]
                                    ] + [
                                        {"label": f"\U0001F4B1 {s}", "value": s}
                                        for s in POPULAR_SYMBOLS["Forex"]
                                    ],
                                    placeholder="Search or pick a symbol...",
                                    searchable=True,
                                    clearable=True,
                                    style={"marginBottom": "0.75rem", "fontSize": "0.85rem"},
                                ),
                                html.Hr(style={"margin": "0.5rem 0", "borderColor": "#e5e7eb"}),
                                html.Label("Or type any symbol", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151"}),
                                dcc.Input(
                                    id="yf-symbol-input",
                                    type="text",
                                    placeholder="e.g. AAPL, BTC-USD, ^GSPC",
                                    style={"width": "100%", "marginBottom": "0.5rem"},
                                    debounce=True,
                                ),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Period", style={"fontWeight": "700", "fontSize": "0.75rem", "color": "#374151"}),
                                        dcc.Dropdown(
                                            id="yf-period",
                                            options=[{"label": p, "value": p} for p in VALID_PERIODS],
                                            value="6mo",
                                            clearable=False,
                                            style={"fontSize": "0.85rem"},
                                        ),
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Interval", style={"fontWeight": "700", "fontSize": "0.75rem", "color": "#374151"}),
                                        dcc.Dropdown(
                                            id="yf-interval",
                                            options=[{"label": i, "value": i} for i in ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]],
                                            value="1d",
                                            clearable=False,
                                            style={"fontSize": "0.85rem"},
                                        ),
                                    ], width=6),
                                ], className="g-2 mb-2"),
                                dcc.Loading(
                                    dbc.Button(
                                        [html.I(className="bi bi-cloud-download"), " Fetch Data"],
                                        id="yf-fetch-btn",
                                        color="info",
                                        className="w-100 mt-2",
                                        style={"fontWeight": "700", "padding": "0.85rem 1.5rem"},
                                    ),
                                    type="circle", color="#6366f1",
                                ),
                                dcc.Loading(
                                    html.Div(id="yf-fetch-status", style={"marginTop": "0.5rem"}),
                                    type="circle", color="#6366f1",
                                ),
                            ],
                            title="Yahoo Finance",
                            item_id="acc-yahoo",
                        ),

                        # --- Date Range Filter ---
                        dbc.AccordionItem(
                            [
                                dcc.DatePickerRange(
                                    id="date-range",
                                    display_format="YYYY-MM-DD",
                                    start_date_placeholder_text="Start",
                                    end_date_placeholder_text="End",
                                    style={"width": "100%"}
                                ),
                            ],
                            title="Date Range Filter",
                            item_id="acc-date-range",
                        ),

                        # --- Sequence Scanner ---
                        dbc.AccordionItem(
                            [
                                html.Small(
                                    "Define colour sequences and scan 200 candles for matches.",
                                    style={"color": "#6b7280", "display": "block", "marginBottom": "0.75rem", "fontWeight": "500"}
                                ),
                                html.Label("Preset Sequences", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151"}),
                                dcc.Dropdown(
                                    id="preset-sequences",
                                    options=[{"label": k, "value": v} for k, v in PRESET_SEQUENCES.items()],
                                    multi=True,
                                    placeholder="Pick common sequences...",
                                    style={"marginBottom": "0.75rem"},
                                ),
                                html.Label("Custom Sequences (one per line)", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151", "marginTop": "0.25rem"}),
                                dcc.Textarea(
                                    id="custom-sequences-input",
                                    placeholder="5R -> 3G\n2R -> Doji -> 1G\n3R -> * -> 2G",
                                    style={
                                        "width": "100%", "height": "80px", "borderRadius": "10px",
                                        "padding": "0.75rem", "border": "1.5px solid #e5e7eb",
                                        "fontSize": "0.85rem", "fontFamily": "monospace",
                                    },
                                ),
                                html.Small(
                                    [
                                        "Syntax: NR = N red, NG = N green. ",
                                        html.A(
                                            [html.I(className="bi bi-question-circle"), " Full reference"],
                                            id="syntax-help-btn",
                                            href="#",
                                            style={"color": "#6366f1", "cursor": "pointer", "textDecoration": "none", "fontWeight": "600"},
                                        ),
                                    ],
                                    style={"color": "#9ca3af", "display": "block", "marginTop": "4px", "fontSize": "0.7rem"},
                                ),
                                html.Div([
                                    html.Div([
                                        html.Span("Enable follow-up match tracking", style={"fontSize": "0.95rem", "fontWeight": "500", "color": "#1f2937", "display": "block", "textAlign": "center", "marginBottom": "0.5rem"}),
                                        html.Div([
                                            dbc.Checklist(
                                                id="followup-enabled",
                                                options=[{"label": "", "value": "enabled"}],
                                                value=[],
                                                switch=True,
                                                style={"marginBottom": "0rem"},
                                            ),
                                            dbc.Tooltip(
                                                "Check this to analyze what candle patterns follow your base sequence. Example: After finding 3R→2G, what typically comes next?",
                                                target="followup-enabled",
                                                placement="bottom",
                                                style={"fontSize": "0.8rem", "maxWidth": "280px"},
                                            ),
                                        ], style={"display": "flex", "justifyContent": "center"}),
                                    ]),
                                ], style={"padding": "0.75rem 0", "borderBottom": "2px solid #e5e7eb", "marginBottom": "1rem"}),
                                dbc.Alert(
                                    [
                                        html.I(className="bi bi-info-circle me-2"),
                                        html.Span("When enabled, the follow-up sequence is searched within the next N candles after each base match (not just the immediate next candle).", style={"fontSize": "0.75rem"}),
                                    ],
                                    color="info",
                                    style={"padding": "0.5rem 0.7rem", "marginBottom": "0.75rem", "fontSize": "0.75rem"},
                                ),
                                html.Div([
                                    html.Label("Follow-up Sequence (e.g. 5R)", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151", "marginTop": "0.25rem", "display": "inline-block"}),
                                    html.I(className="bi bi-question-circle", id="followup-seq-help", style={"fontSize": "0.75rem", "color": "#9ca3af", "marginLeft": "0.4rem", "cursor": "pointer"}),
                                ]),
                                dbc.Tooltip(
                                    [
                                        html.P("The pattern you want to find after the base sequence.", style={"marginBottom": "0.4rem", "fontSize": "0.75rem"}),
                                        html.Strong("Examples:", style={"fontSize": "0.75rem"}),
                                        html.Ul([
                                            html.Li("5R = five consecutive red candles", style={"fontSize": "0.7rem"}),
                                            html.Li("3G = three consecutive green candles", style={"fontSize": "0.7rem"}),
                                            html.Li("2R → 1G = two reds then one green", style={"fontSize": "0.7rem"}),
                                            html.Li("Doji = doji candle pattern", style={"fontSize": "0.7rem"}),
                                        ], style={"paddingLeft": "1.2rem", "marginBottom": "0.4rem"}),
                                        html.Small("Uses same syntax as base sequence patterns.", style={"color": "#9ca3af"}),
                                    ],
                                    target="followup-seq-help",
                                    placement="right",
                                    style={"fontSize": "0.8rem", "maxWidth": "320px"},
                                ),
                                dcc.Input(
                                    id="followup-sequence",
                                    type="text",
                                    placeholder="5R",
                                    style={"width": "100%", "marginBottom": "0.5rem"},
                                ),
                                html.Div([
                                    html.Label("Follow-up Length (candles)", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151", "display": "inline-block"}),
                                    html.I(className="bi bi-question-circle", id="followup-len-help", style={"fontSize": "0.75rem", "color": "#9ca3af", "marginLeft": "0.4rem", "cursor": "pointer"}),
                                ]),
                                dbc.Tooltip(
                                    [
                                        html.P("How many candles to scan after the base match ends.", style={"marginBottom": "0.4rem", "fontSize": "0.75rem"}),
                                        html.Strong("Examples:", style={"fontSize": "0.75rem"}),
                                        html.Ul([
                                            html.Li("Length=5: scan next 5 candles for the follow-up pattern", style={"fontSize": "0.7rem"}),
                                            html.Li("Length=10: scan next 10 candles (wider window)", style={"fontSize": "0.7rem"}),
                                            html.Li("If sequence is 5R and length is 3, they're independent", style={"fontSize": "0.7rem"}),
                                        ], style={"paddingLeft": "1.2rem", "marginBottom": "0.4rem"}),
                                        html.Small("Larger values catch delayed patterns; smaller values catch immediate reactions.", style={"color": "#9ca3af"}),
                                    ],
                                    target="followup-len-help",
                                    placement="right",
                                    style={"fontSize": "0.8rem", "maxWidth": "320px"},
                                ),
                                dcc.Input(
                                    id="followup-length",
                                    type="number",
                                    min=1,
                                    max=50,
                                    step=1,
                                    value=5,
                                    style={"width": "100%", "marginBottom": "0.75rem"},
                                ),
                                dbc.Popover(
                                    dbc.PopoverBody([
                                        html.H6("Sequence Syntax Cheat-Sheet", style={"fontWeight": "800", "marginBottom": "0.5rem"}),
                                        html.Table([
                                            html.Tbody([
                                                html.Tr([html.Td(html.Code("NR"), style={"paddingRight": "0.75rem"}), html.Td("N consecutive red (bearish) candles")]),
                                                html.Tr([html.Td(html.Code("NG"), style={"paddingRight": "0.75rem"}), html.Td("N consecutive green (bullish) candles")]),
                                                html.Tr([html.Td(html.Code("Doji"), style={"paddingRight": "0.75rem"}), html.Td("Doji candle (open \u2248 close)")]),
                                                html.Tr([html.Td(html.Code("Hammer"), style={"paddingRight": "0.75rem"}), html.Td("Hammer candle pattern")]),
                                                html.Tr([html.Td(html.Code("->"), style={"paddingRight": "0.75rem"}), html.Td("Separator between elements")]),
                                                html.Tr([html.Td(html.Code("*"), style={"paddingRight": "0.75rem"}), html.Td("Wildcard (1-3 candles)")]),
                                            ])
                                        ], style={"fontSize": "0.8rem", "width": "100%", "marginBottom": "0.5rem"}),
                                        html.Hr(style={"margin": "0.5rem 0"}),
                                        html.P("Examples:", style={"fontWeight": "700", "marginBottom": "0.25rem", "fontSize": "0.8rem"}),
                                        html.Code("5R -> 3G", style={"display": "block", "fontSize": "0.78rem"}),
                                        html.Code("2R -> Doji -> 1G", style={"display": "block", "fontSize": "0.78rem"}),
                                        html.Code("3R -> * -> 2G", style={"display": "block", "fontSize": "0.78rem"}),
                                    ]),
                                    target="syntax-help-btn",
                                    trigger="hover",
                                    placement="right",
                                    style={"maxWidth": "360px"},
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-play-fill"), " Scan Sequences"],
                                    id="scan-sequences-btn",
                                    color="primary",
                                    className="w-100 mt-3",
                                    style={"fontWeight": "700", "padding": "0.85rem 1.5rem"},
                                ),
                                dcc.Loading(
                                    html.Div(id="scan-results-summary", style={"marginTop": "0.75rem"}),
                                    id="scan-loading",
                                    type="circle",
                                    color="#6366f1",
                                    style={"marginTop": "1rem"},
                                ),
                            ],
                            title="Sequence Scanner",
                            item_id="acc-scanner",
                        ),

                        # --- History ---
                        dbc.AccordionItem(
                            [
                                dcc.Dropdown(
                                    id="history-select",
                                    placeholder="Select a past upload...",
                                    clearable=True,
                                    style={"marginTop": "0.5rem"}
                                ),
                            ],
                            title="Load from History",
                            item_id="acc-history",
                        ),

                        # --- Maintenance ---
                        dbc.AccordionItem(
                            [
                                dbc.Button(
                                    [html.I(className="bi bi-trash"), " Run Cleanup"],
                                    id="cleanup-btn",
                                    color="danger",
                                    size="sm",
                                    className="w-100",
                                    style={"fontWeight": "700", "padding": "0.65rem 1rem"}
                                ),
                                dcc.ConfirmDialog(
                                    id="cleanup-confirm",
                                    message="This will permanently delete uploads older than 30 days. Continue?",
                                ),
                                html.Div(
                                    id="cleanup-result",
                                    style={"marginTop": "10px", "fontSize": "0.9em", "color": "#6b7280", "fontWeight": "500"}
                                ),
                            ],
                            title="Maintenance",
                            item_id="acc-maintenance",
                        ),

                        # --- Export ---
                        dbc.AccordionItem(
                            [
                                dbc.Button(
                                    [html.I(className="bi bi-table"), " Matches CSV"],
                                    id="export-detections-btn",
                                    color="info",
                                    size="sm",
                                    className="w-100 mb-2",
                                    style={"fontWeight": "700", "padding": "0.65rem 1rem"}
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-bar-chart"), " Discovery CSV"],
                                    id="export-aggregated-btn",
                                    color="info",
                                    size="sm",
                                    className="w-100",
                                    style={"fontWeight": "700", "padding": "0.65rem 1rem"}
                                ),
                                dcc.Download(id="download-asset"),
                                html.Div(id="export-status", style={"marginTop": "0.5rem"}),
                            ],
                            title="Export Data",
                            item_id="acc-export",
                        ),
                    ],
                    always_open=True,
                    active_item=["acc-data-source", "acc-scanner"],
                    flush=True,
                    style={"marginTop": "0.5rem"},
                ),

                # Statistics cards always visible at bottom
                html.Hr(className="hr-style"),
                html.Div(id="stats-cards"),
            ]
        )
    ],
    className="sidebar-card",
)

# Stores to keep the current upload and scan results in-browser
# NOTE: store starts empty; the page-load callback populates it with sample data
store_current = dcc.Store(id='current-data', data=None, storage_type='memory')
store_scan = dcc.Store(id='scan-results', data=None, storage_type='memory')
store_hold_period = dcc.Store(id='hold-period-store', data=5, storage_type='memory')

# Live-refresh interval component (disabled by default, 60s when enabled)
live_interval = dcc.Interval(
    id='live-interval',
    interval=60 * 1000,  # milliseconds
    n_intervals=0,
    disabled=True,
)
store_live_symbol = dcc.Store(id='live-symbol', data='', storage_type='memory')
store_ml_model = dcc.Store(id='ml-model-store', data=None, storage_type='memory')
store_theme = dcc.Store(id='theme-store', data='light', storage_type='local')

# Modal for pattern detail
pattern_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle(
                [html.I(className="bi bi-graph-up"), " Pattern Analysis"],
                style={"fontWeight": "800", "fontSize": "1.25rem"}
            ),
            close_button=True,
            style={"padding": "1.5rem"}
        ),
        dbc.ModalBody(id="pattern-modal-body", style={"padding": "2rem"}),
        dbc.ModalFooter(
            [
                dbc.Button(
                    [html.I(className="bi bi-image"), " Export PNG"],
                    id="export-chart-btn",
                    color="info",
                    size="sm",
                    style={"fontWeight": "700", "padding": "0.65rem 1.2rem"}
                ),
                dbc.Button(
                    [html.I(className="bi bi-x-circle"), " Close"],
                    id="modal-close",
                    color="secondary",
                    size="sm",
                    className="ms-auto",
                    style={"fontWeight": "700", "padding": "0.65rem 1.2rem"}
                ),
            ],
            style={"padding": "1.5rem"}
        ),
    ],
    id="pattern-modal",
    is_open=False,
    size="lg",
)

# Modern tabbed layout with enhanced styling
main_content = dbc.Tabs(
    [
        dbc.Tab(
            label="Candlestick Chart",
            tab_id="tab-chart",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Candlestick Chart",
                            "Explore loaded candle data in an interactive chart. Zoom, pan, and verify data quality before running scans; this is your baseline view for price action and support/resistance context."
                        ),
                        html.Div(
                            id="candle-count-badge",
                            style={"textAlign": "right", "marginTop": "0.75rem", "minHeight": "1.5rem"},
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="candle-chart",
                                figure=build_candle_figure(app.default_sample_data if app.default_sample_data is not None else None),
                                style={"marginTop": "0.25rem"},
                                config={
                                    "responsive": True,
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    "scrollZoom": True,
                                    "toImageButtonOptions": {
                                        "format": "png",
                                        "filename": "candle_chart.png",
                                        "height": 600,
                                        "width": 1200,
                                        "scale": 1,
                                    },
                                    "modeBarButtonsToRemove": ["pan2d", "zoom2d", "zoomIn2d", "zoomOut2d", "lasso2d", "select2d", "autoScale2d", "toggleSpikelines"],
                                }
                            ),
                            type="circle", color="#6366f1"
                        ),
                        html.Div(id="current-data-debug", style={"marginTop": "0.5rem", "color": "#6b7280", "fontSize": "0.85rem"}),
                    ],
                    fluid=True,
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label="Sequence Matches",
            tab_id="tab-matches",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Sequence Matches",
                            "Displays all matched sequences found in the current dataset with details on start/end points and confidence. Use the filter controls in the scan panel to refine results in real time."
                        ),
                        dcc.Loading(html.Div(id="matches-content", style={"marginTop": "1.5rem"}), type="circle", color="#6366f1")
                    ],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label="Auto-Discovery",
            tab_id="tab-discovery",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Auto-Discovery",
                            "Automatically identifies the most frequent and statistically significant sequences for the current data. Use this first to discover candidate patterns and then drill into matching and backtesting."
                        ),
                        dcc.Loading(html.Div(id="discovery-content", style={"marginTop": "1.5rem"}), type="circle", color="#6366f1")
                    ],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label="Statistics & Predictions",
            tab_id="tab-stats",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Statistics & Predictions",
                            "Set your lookahead and hold period, then inspect outcome charts, expected returns, and prediction probabilities. This section quantifies sequence performance and helps choose trading parameters."
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Hold Period (candles)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Slider(
                                    id="hold-period-slider",
                                    min=1, max=20, step=1, value=5,
                                    marks={1: "1", 3: "3", 5: "5", 10: "10", 15: "15", 20: "20"},
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ], width=6),
                            dbc.Col([
                                html.Label("Lookahead Candles", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Slider(
                                    id="lookahead-slider",
                                    min=1, max=10, step=1, value=3,
                                    marks={1: "1", 3: "3", 5: "5", 7: "7", 10: "10"},
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ], width=6),
                        ], className="g-3 mb-3", style={"marginTop": "1rem"}),
                        dcc.Loading(html.Div(id="stats-content", style={"marginTop": "0.5rem"}), type="circle", color="#6366f1"),
                    ],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label="Heatmap",
            tab_id="tab-heatmap",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Heatmap",
                            "Visualize frequency and confidence of sequence occurrences in a heatmap matrix. Use this for spotting high-probability clusters and regime shifts in the data."
                        ),
                        dcc.Loading(html.Div(id="heatmap-content", style={"marginTop": "1.5rem"}), type="circle", color="#6366f1")
                    ],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label="Reverse Finder",
            tab_id="tab-reverse",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Reverse Finder",
                            "Search for patterns that showed up before large price moves. Configure direction, move threshold, and candle lookback to identify high-impact pre-move signatures."
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Move Threshold (%)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="reverse-threshold", type="number", value=1.5, min=0.1, max=20, step=0.1,
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Direction", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Dropdown(
                                    id="reverse-direction",
                                    options=[
                                        {"label": "Big Gains (Up)", "value": "up"},
                                        {"label": "Big Losses (Down)", "value": "down"},
                                        {"label": "Both", "value": "both"},
                                    ],
                                    value="up", clearable=False,
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Lookback Candles", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="reverse-lookback", type="number", value=5, min=2, max=20, step=1,
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-search"), " Find Patterns"],
                                    id="reverse-find-btn",
                                    color="primary",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3", style={"marginTop": "1rem"}),
                        dcc.Loading(html.Div(id="reverse-content", children=[
                            html.Div([
                                html.I(className="bi bi-arrow-repeat", style={"fontSize": "2rem", "color": "#c7d2fe"}),
                                html.P("Set parameters above and click Find Patterns to discover sequences preceding big price moves.",
                                       style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600", "maxWidth": "420px", "margin": "0.5rem auto 0"}),
                            ], style={"padding": "3rem", "textAlign": "center"}),
                        ]), type="circle", color="#6366f1"),
                    ],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        # ==========================================
        # BACKTESTING TAB
        # ==========================================
        dbc.Tab(
            label="Backtesting",
            tab_id="tab-backtest",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Backtesting",
                            "Run historical simulation on sequence trades. Choose hold period, capital allocation, and entry signals; review equity curve, win rate, drawdown, and return metrics."
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Hold Period (candles)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Slider(id="bt-hold-slider", min=1, max=20, step=1, value=5,
                                           marks={i: str(i) for i in [1, 5, 10, 15, 20]}),
                            ], width=4),
                            dbc.Col([
                                html.Label("Initial Capital ($)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="bt-capital", type="number", value=10000, min=100, step=100,
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-calculator"), " Run Backtest"],
                                    id="bt-run-btn",
                                    color="success",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3", style={"marginTop": "1rem"}),
                        dcc.Loading(html.Div(id="backtest-content", children=[
                            html.Div([
                                html.I(className="bi bi-graph-up-arrow", style={"fontSize": "2rem", "color": "#bbf7d0"}),
                                html.P("Load data and scan sequences first, then click Run Backtest to see equity curves and performance metrics.",
                                       style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600", "maxWidth": "420px", "margin": "0.5rem auto 0"}),
                            ], style={"padding": "3rem", "textAlign": "center"}),
                        ]), type="circle", color="#10b981"),
                    ],
                    fluid=True,
                )
            ],
            className="p-4",
        ),
        # ==========================================
        # MULTI-TIMEFRAME TAB
        # ==========================================
        dbc.Tab(
            label="Multi-TF",
            tab_id="tab-multi-tf",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Multi-TF",
                            "Analyze the same patterns across multiple timeframes in one place. Select intervals, symbol, and lookback to reveal cross-timeframe confirmations and stronger setups."
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Symbol", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="mtf-symbol", type="text", placeholder="AAPL",
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Timeframes", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Dropdown(
                                    id="mtf-intervals",
                                    options=[{"label": iv, "value": iv} for iv in ["1h", "4h", "1d", "1wk"]],
                                    value=["1h", "1d"],
                                    multi=True,
                                    placeholder="Select timeframes...",
                                ),
                            ], width=4),
                            dbc.Col([
                                html.Label("Lookback (recent candles)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="mtf-lookback", type="number", value=5, min=1, max=50, step=1,
                                          style={"width": "100%"}),
                            ], width=2),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-layers"), " Analyse"],
                                    id="mtf-run-btn",
                                    color="primary",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3", style={"marginTop": "1rem"}),
                        dcc.Loading(html.Div(id="mtf-content", children=[
                            html.Div([
                                html.I(className="bi bi-layers", style={"fontSize": "2rem", "color": "#c7d2fe"}),
                                html.P("Enter a symbol, select timeframes, and click Analyse to check sequence alignment across intervals.",
                                       style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600", "maxWidth": "420px", "margin": "0.5rem auto 0"}),
                            ], style={"padding": "3rem", "textAlign": "center"}),
                        ]), type="circle", color="#6366f1"),
                    ],
                    fluid=True,
                )
            ],
            className="p-4",
        ),
        # ==========================================
        # WATCHLIST TAB
        # ==========================================
        dbc.Tab(
            label="Watchlist",
            tab_id="tab-watchlist",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Watchlist",
                            "Create reusable sequence filters and symbol watchlists. Save rules for fast recall and automated scanning in other tabs; this supports ongoing strategy tracking."
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Label", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="wl-label", type="text", placeholder="My Bull Setup",
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Sequences (comma-separated)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="wl-sequences", type="text",
                                          placeholder="3R -> 2G, 5R -> 3G",
                                          style={"width": "100%"}),
                            ], width=4),
                            dbc.Col([
                                html.Label("Symbol (optional)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="wl-symbol", type="text", placeholder="AAPL",
                                          style={"width": "100%"}),
                            ], width=2),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-bookmark-plus"), " Save"],
                                    id="wl-add-btn",
                                    color="success",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3", style={"marginTop": "1rem"}),
                        html.Div(id="wl-status", style={"marginBottom": "0.75rem"}),
                        dcc.Loading(html.Div(id="wl-content"), type="circle", color="#f59e0b"),
                        dcc.Store(id="wl-refresh-trigger", data=0),
                    ],
                    fluid=True,
                )
            ],
            className="p-4",
        ),
        # ==========================================
        # ALERTS TAB  (Phase 6)
        # ==========================================
        dbc.Tab(
            label="Alerts",
            tab_id="tab-alerts",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Alerts",
                            "Configure condition-based alerts for sequences and optional webhook destinations. Monitor active rules and review trigger history to validate signal timing and reliability."
                        ),
                        html.H5(
                            [html.I(className="bi bi-bell me-2"), "Sequence Alerts"],
                            style={"fontWeight": "800", "marginTop": "1rem", "marginBottom": "1rem"},
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Rule Name", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="alert-rule-name", type="text", placeholder="My Alert",
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Sequences (comma-separated)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="alert-sequences", type="text",
                                          placeholder="3R -> 2G, 5R -> 3G",
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Symbol (optional)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="alert-symbol", type="text", placeholder="AAPL",
                                          style={"width": "100%"}),
                            ], width=2),
                            dbc.Col([
                                html.Label("Webhook URL (optional)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="alert-webhook", type="text", placeholder="https://...",
                                          style={"width": "100%"}),
                            ], width=2),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-plus-circle"), " Add Rule"],
                                    id="alert-add-btn",
                                    color="warning",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=2),
                        ], className="g-3 mb-3"),
                        html.Div(id="alert-add-status", style={"marginBottom": "0.5rem"}),
                        html.Hr(),
                        html.H6("Active Rules", style={"fontWeight": "700"}),
                        dcc.Loading(html.Div(id="alert-rules-content"), type="circle", color="#f59e0b"),
                        html.Hr(),
                        html.H6("Alert History", style={"fontWeight": "700"}),
                        dbc.Button(
                            [html.I(className="bi bi-trash me-1"), "Clear History"],
                            id="alert-clear-history-btn",
                            color="outline-danger", size="sm",
                            className="mb-2",
                            style={"fontWeight": "600"},
                        ),
                        html.Div(id="alert-clear-status", style={"marginBottom": "0.5rem"}),
                        dcc.Loading(html.Div(id="alert-history-content"), type="circle", color="#f59e0b"),
                        dcc.Store(id="alert-refresh-trigger", data=0),
                    ],
                    fluid=True,
                )
            ],
            className="p-4",
        ),
        # ==========================================
        # ML PREDICTIONS TAB  (Phase 6)
        # ==========================================
        dbc.Tab(
            label="ML Predict",
            tab_id="tab-ml-predict",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "ML Predict",
                            "Build a machine learning model on historical sequence outcomes; train, score, and inspect predicted next-step moves along with probability/confidence. This helps evaluate whether ML can improve signal timing."
                        ),
                        html.H5(
                            [html.I(className="bi bi-robot me-2"), "Sequence Outcome Predictor"],
                            style={"fontWeight": "800", "marginTop": "1rem", "marginBottom": "0.5rem"},
                        ),
                        html.P(
                            "Train a GradientBoosting model on the loaded data to predict whether "
                            "the price will rise or fall after current conditions.",
                            style={"color": "#6b7280", "fontSize": "0.85rem"},
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Hold Period (candles)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Slider(id="ml-hold-slider", min=1, max=20, step=1, value=5,
                                           marks={i: str(i) for i in [1, 5, 10, 15, 20]}),
                            ], width=5),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-lightning-charge"), " Train & Predict"],
                                    id="ml-train-btn",
                                    color="primary",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3", style={"marginTop": "1rem"}),
                        dcc.Loading(html.Div(id="ml-predict-content", children=[
                            html.Div([
                                html.I(className="bi bi-robot", style={"fontSize": "2rem", "color": "#c7d2fe"}),
                                html.P("Load data first, then click Train & Predict to build a model and see outcome predictions.",
                                       style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600", "maxWidth": "420px", "margin": "0.5rem auto 0"}),
                            ], style={"padding": "3rem", "textAlign": "center"}),
                        ]), type="circle", color="#6366f1"),
                    ],
                    fluid=True,
                )
            ],
            className="p-4",
        ),
        # ==========================================
        # SETTINGS / PREFERENCES TAB  (Phase 6)
        # ==========================================
        dbc.Tab(
            label="Settings",
            tab_id="tab-settings",
            children=[
                dbc.Container(
                    [
                        section_banner(
                            "Settings",
                            "Set user preferences for default symbol, interval, refresh behavior, and discovery limits so your workflow is reproducible. Includes reset and dataset info for audit."
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Theme", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Dropdown(
                                    id="theme-selector",
                                    options=[
                                        {"label": "Light", "value": "theme-light"},
                                        {"label": "Dark", "value": "theme-dark"},
                                        {"label": "Ocean Blue", "value": "theme-blue"},
                                        {"label": "Solar", "value": "theme-solar"},
                                    ],
                                    value="theme-light",
                                    clearable=False,
                                    style={"width": "100%"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3"),
                        html.H5(
                            [html.I(className="bi bi-gear me-2"), "Preferences"],
                            style={"fontWeight": "800", "marginTop": "1rem", "marginBottom": "1rem"},
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Default Symbol", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="pref-default-symbol", type="text", placeholder="AAPL",
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Default Period", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Dropdown(
                                    id="pref-default-period",
                                    options=[{"label": p, "value": p} for p in VALID_PERIODS],
                                    value="6mo", clearable=False,
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Default Interval", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Dropdown(
                                    id="pref-default-interval",
                                    options=[{"label": i, "value": i} for i in VALID_INTERVALS],
                                    value="1d", clearable=False,
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Hold Period", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="pref-hold-period", type="number", value=5, min=1, max=20,
                                          style={"width": "100%"}),
                            ], width=3),
                        ], className="g-3 mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Live Refresh", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dbc.Checklist(
                                    id="pref-live-enabled",
                                    options=[{"label": " Enable auto-refresh", "value": "enabled"}],
                                    value=[],
                                    switch=True,
                                ),
                            ], width=3),
                            dbc.Col([
                                html.Label("Refresh Interval (sec)", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="pref-live-interval", type="number", value=60, min=10, max=600, step=10,
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("Discovery Max Results", style={"fontWeight": "700", "fontSize": "0.8rem"}),
                                dcc.Input(id="pref-discovery-max", type="number", value=25, min=5, max=100,
                                          style={"width": "100%"}),
                            ], width=3),
                            dbc.Col([
                                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem"}),
                                dbc.Button(
                                    [html.I(className="bi bi-save"), " Save Preferences"],
                                    id="pref-save-btn",
                                    color="success",
                                    className="w-100",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=3),
                        ], className="g-3 mb-3"),
                        html.Div(id="pref-save-status", style={"marginTop": "0.5rem"}),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="bi bi-arrow-counterclockwise"), " Reset to Defaults"],
                                    id="pref-reset-btn",
                                    color="outline-danger",
                                    size="sm",
                                    style={"fontWeight": "700"},
                                ),
                            ], width=4),
                        ]),
                        html.Div(id="pref-reset-status", style={"marginTop": "0.5rem"}),
                        html.Hr(),
                        html.H6("Dataset Info", style={"fontWeight": "700"}),
                        html.Div(id="dataset-info-content"),
                    ],
                    fluid=True,
                )
            ],
            className="p-4",
        ),
    ],
    id="tabs",
    active_tab="tab-chart",
    className="mt-2"
)

# Flask API endpoint for loading sample data
@server.route('/__debug_app_path')
def debug_app_path():
    return f"dashboard module path: {__file__}"


@server.route('/__debug_callback_map')
def debug_callback_map():
    return json.dumps(list(app.callback_map.keys()))


@server.route('/api/load-sample')  # type: ignore[union-attr]
def api_load_sample():
    """API endpoint to load sample data directly."""
    from flask import jsonify
    from pathlib import Path
    from candle_patterns.detection import detect_patterns as _detect
    from candle_patterns.storage import save_upload
    import pandas as pd
    
    try:
        sample_path = Path("data/samples/sample.csv")
        
        if not sample_path.exists():
            return jsonify({"error": "Sample data file not found"}), 404
        
        # Load the sample data
        df = pd.read_csv(sample_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Detect patterns
        patterns = _detect(df)
        
        # Save to storage
        upload_info = save_upload(f"sample_synthetic_automated_{pd.Timestamp.now().isoformat()}", df, patterns)
        
        return jsonify({
            "success": True,
            "message": f"[OK] Loaded sample: {len(patterns)} patterns detected",
            "patterns": len(patterns),
            "rows": len(df),
            "upload_id": upload_info
        })
    except Exception as e:
        logger.exception('API load sample failed: %s', e)
        return jsonify({"error": str(e)}), 500

# Main layout
app.layout = html.Div(
    [
        navbar,
        store_current,
        store_scan,
        store_hold_period,
        live_interval,
        store_live_symbol,
        store_ml_model,
        store_theme,
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-load-signal', children=1, style={'display': 'none'}),
        # Main body: sidebar LEFT + content RIGHT, each independently scrollable
        html.Div(
            [
                # LEFT panel — config sidebar (fixed-width, scrollable)
                html.Div(
                    sidebar,
                    style={
                        "width": "340px",
                        "minWidth": "340px",
                        "overflowY": "auto",
                        "height": "calc(100vh - 80px)",
                        "padding": "1rem 1rem 2rem 1rem",
                        "borderRight": "1px solid var(--panel-border)",
                        "background": "var(--panel-bg)",
                    },
                ),
                # RIGHT panel — chart + tabs (fills remaining width, scrollable)
                html.Div(
                    main_content,
                    style={
                        "flex": "1",
                        "overflowY": "auto",
                        "height": "calc(100vh - 80px)",
                        "padding": "0.75rem 1rem 2rem 1rem",
                        "margin": "0.5rem 0.5rem 0.5rem 0",
                        "border": "1px solid var(--panel-border)",
                        "borderRadius": "12px",
                        "background": "var(--panel-bg)",
                        "boxShadow": "var(--card-shadow)",
                    },
                ),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "height": "calc(100vh - 80px)",
                "overflow": "hidden",
            },
        ),
        pattern_modal,

        # ---- Form-control Tooltips (Phase 9 UX) ----
        dbc.Tooltip("Choose a trading pair / ticker symbol to fetch from Yahoo Finance.",
                    target="yf-symbol-select", placement="right"),
        dbc.Tooltip("How far back to fetch data (e.g. 6mo = six months).",
                    target="yf-period", placement="right"),
        dbc.Tooltip("Candle interval / timeframe for the fetched data.",
                    target="yf-interval", placement="right"),
        dbc.Tooltip("Filter the chart to a specific date window.",
                    target="date-range", placement="right"),
        dbc.Tooltip("Pick from commonly-used candle sequences.",
                    target="preset-sequences", placement="right"),
        dbc.Tooltip("Write custom candle sequences, one per line. Syntax: NR (N red), NG (N green), Doji, Hammer. Use -> as separator and * as wildcard.",
                    target="custom-sequences-input", placement="right"),
        dbc.Tooltip("Reload a previously uploaded dataset.",
                    target="history-select", placement="right"),
        dbc.Tooltip("How many candles ahead to analyse for move statistics.",
                    target="lookahead-slider", placement="top"),
        dbc.Tooltip("Minimum price move (%) that qualifies as a 'big move'.",
                    target="reverse-threshold", placement="top"),
        dbc.Tooltip("Look for big gains, big losses, or both.",
                    target="reverse-direction", placement="top"),
        dbc.Tooltip("How many candles to look back before the big move for pattern discovery.",
                    target="reverse-lookback", placement="top"),
        dbc.Tooltip("Number of candles to hold each trade in the backtest.",
                    target="bt-hold-slider", placement="top"),
        dbc.Tooltip("Starting portfolio value for the backtest simulation.",
                    target="bt-capital", placement="top"),
        dbc.Tooltip("Ticker symbol to fetch multi-timeframe data for (e.g. AAPL, BTC-USD).",
                    target="mtf-symbol", placement="top"),
        dbc.Tooltip("Select one or more timeframes to compare sequence alignment.",
                    target="mtf-intervals", placement="top"),
        dbc.Tooltip("Number of recent candles to scan on each timeframe.",
                    target="mtf-lookback", placement="top"),
        dbc.Tooltip("A friendly name for this watchlist entry.",
                    target="wl-label", placement="top"),
        dbc.Tooltip("Comma-separated sequences to watch (e.g. 3R -> 2G, 5R -> 3G).",
                    target="wl-sequences", placement="top"),
        dbc.Tooltip("Optional ticker to associate with these sequences.",
                    target="wl-symbol", placement="top"),
        dbc.Tooltip("A name for this alert rule.",
                    target="alert-rule-name", placement="top"),
        dbc.Tooltip("Comma-separated sequences that trigger the alert.",
                    target="alert-sequences", placement="top"),
        dbc.Tooltip("Optional ticker filter for the alert.",
                    target="alert-symbol", placement="top"),
        dbc.Tooltip("Optional webhook URL to POST alert payloads to.",
                    target="alert-webhook", placement="top"),
        dbc.Tooltip("How many candles ahead the ML model predicts.",
                    target="ml-hold-slider", placement="top"),
    ],
    id="theme-wrapper",
    className="theme-light",
    style={
        "background": "var(--background-gradient, linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%))",
        "height": "100vh",
        "overflow": "hidden",
        "margin": "0",
        "padding": "0",
    },
)

# =========================================================================
# CALLBACKS
# =========================================================================

# Theme switcher: propagate selected theme across UI wrapper ----------
@app.callback(
    Output("theme-wrapper", "className"),
    Output("theme-store", "data"),
    Input("theme-selector", "value"),
    prevent_initial_call=True,
)
def update_theme(theme_value):
    if theme_value not in {"theme-light", "theme-dark", "theme-blue", "theme-solar"}:
        theme_value = "theme-light"
    return theme_value, theme_value


@app.callback(
    Output("theme-selector", "value"),
    Input("theme-store", "data"),
    prevent_initial_call=False,
)
def load_theme(saved_theme):
    if saved_theme in {"theme-light", "theme-dark", "theme-blue", "theme-solar"}:
        return saved_theme
    return "theme-light"


# Page-load: auto-populate chart with sample data ---------------------
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Output("upload-status", "children", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call='initial_duplicate',
)
def on_page_load(_pathname):
    """Fires on page load (when URL is set) to seed the chart with sample data."""
    data, status = load_sample_data()
    return data, status


# Handle file upload --------------------------------------------------
@app.callback(
    Output("upload-status", "children", allow_duplicate=True),
    Output("current-data", "data", allow_duplicate=True),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def on_upload(contents, filename):
    def _err(msg):
        return (
            html.Div(
                [html.I(className="bi bi-exclamation-triangle-fill me-2"), msg],
                style={"color": "#ef4444", "fontWeight": "600", "padding": "10px",
                       "backgroundColor": "#fef2f2", "borderRadius": "8px"},
            ),
            dash.no_update,
        )

    if contents is None:
        return dash.no_update, dash.no_update

    try:
        _content_type, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.BytesIO(decoded))

        # Normalise column names to lowercase
        df.columns = [c.lower() for c in df.columns]

        # Accept 'time' as an alias for 'timestamp' (e.g. TradingView exports)
        if "timestamp" not in df.columns and "time" in df.columns:
            df = df.rename(columns={"time": "timestamp"})

        # Validate required columns
        required_cols = {"open", "high", "low", "close"}
        missing = required_cols - set(df.columns)
        if missing:
            return _err(f"CSV missing required columns: {', '.join(sorted(missing))}")

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
            df = df.dropna(subset=["timestamp"])
            df = df.sort_values("timestamp").reset_index(drop=True)
            # Convert to ISO string for safe JSON serialisation
            df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        try:
            upload_id = save_upload(filename, df, [])
        except Exception as e:
            logger.exception("save_upload failed: %s", e)
            upload_id = None

        data = {
            "filename": filename,
            "upload_id": upload_id,
            "df": df.to_dict("records"),
        }

        status = html.Div(
            [html.I(className="bi bi-check-circle-fill me-2"),
             f"Loaded: {filename} ({len(df)} candles)"],
            style={"color": "#059669", "fontWeight": "600", "padding": "10px",
                   "backgroundColor": "#ecfdf5", "borderRadius": "8px"},
        )
        return status, data

    except Exception as exc:
        logger.exception("on_upload failed: %s", exc)
        return _err(f"Failed to parse CSV: {exc}")


# Handle "Load Sample Data" button ------------------------------------
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Output("upload-status", "children", allow_duplicate=True),
    Output("tabs", "active_tab", allow_duplicate=True),
    Input("load-sample-btn", "n_clicks"),
    prevent_initial_call=True,
)
def on_load_sample_click(n_clicks):
    if n_clicks and n_clicks > 0:
        logger.info("Load Sample Data button clicked")
        data, status = load_sample_data()
        if data:
            logger.info("Sample data loaded: %d candles", len(data['df']))
            return data, status, "tab-chart"
        return None, status, "tab-chart"
    return None, "", "tab-chart"


# Scan sequences  -------------------------------------------------------
@app.callback(
    Output("scan-results", "data", allow_duplicate=True),
    Output("scan-results-summary", "children"),
    Output("tabs", "active_tab", allow_duplicate=True),
    Input("scan-sequences-btn", "n_clicks"),
    State("preset-sequences", "value"),
    State("custom-sequences-input", "value"),
    State("followup-enabled", "value"),
    State("followup-sequence", "value"),
    State("followup-length", "value"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def scan_sequences(n_clicks, presets, custom_text, followup_enabled, followup_seq, followup_length, data):
    """Run all selected sequences against the loaded candle data.
    
    Supports wildcard sequences containing '*' (e.g. '3R -> * -> 2G').
    """
    logger.info("[CALLBACK] scan_sequences triggered: n_clicks=%s presets=%s custom_text=%s data=%s", n_clicks, presets, custom_text, 'present' if data else 'none')
    try:
        if not data:
            return None, html.Div("No data loaded. Upload a CSV or load sample data first.",
                                  style={"color": "#ef4444", "fontWeight": "600"}), "tab-chart"

        # Collect sequences from presets + custom
        seqs: list = []
        if presets:
            seqs.extend(presets)
        if custom_text:
            for line in custom_text.strip().splitlines():
                line = line.strip()
                if line:
                    seqs.append(line)

        if not seqs:
            # Auto-apply top discovered sequences when no sequence is explicitly set.
            default_scan = build_default_scan_results(data, max_sequences=4)
            if default_scan:
                seqs = [r["seq_str"] for r in default_scan if r.get("seq_str")]
            if not seqs:
                return None, html.Div("No sequences defined. Pick presets or type custom ones.",
                                      style={"color": "#f59e0b", "fontWeight": "600"}), "tab-matches"

        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        results = []
        total_matches = 0
        for seq_str in seqs:
            try:
                # Use wildcard matcher if '*' is present
                if "*" in seq_str:
                    wild_hits = find_wildcard_sequence(df, seq_str, wildcard_min=1, wildcard_max=3)
                    matches = []
                    for h in wild_hits:
                        si, ei = h["start_idx"], h["end_idx"]
                        matches.append({
                            "start_idx": si,
                            "end_idx": ei,
                            "start_ts": str(df.iloc[si]["timestamp"]),
                            "end_ts": str(df.iloc[ei]["timestamp"]),
                        })
                    seq_len = sequence_length(seq_str.replace("*", "1R"))  # approx
                else:
                    occ_ends = find_sequence_occurrences(df, seq_str)
                    seq_len = sequence_length(seq_str)
                    matches = []
                    for end_idx in occ_ends:
                        start_idx = end_idx - seq_len + 1
                        if start_idx < 0:
                            start_idx = 0
                        matches.append({
                            "start_idx": int(start_idx),
                            "end_idx": int(end_idx),
                            "start_ts": str(df.iloc[start_idx]["timestamp"]),
                            "end_ts": str(df.iloc[end_idx]["timestamp"]),
                        })
                entry = {"seq_str": seq_str, "length": seq_len, "matches": matches}

                followup_enabled_flag = bool(followup_enabled and "enabled" in followup_enabled)
                followup_len = None
                if followup_length is not None:
                    try:
                        followup_len = int(followup_length)
                    except (TypeError, ValueError):
                        followup_len = None

                if followup_enabled_flag:
                    if not followup_seq or not isinstance(followup_seq, str) or not followup_seq.strip():
                        entry.update({
                            "followup_error": "Enable follow-up with a valid follow-up sequence (e.g. 5R)",
                        })
                    elif followup_len is None or followup_len <= 0:
                        entry.update({
                            "followup_error": "Enable follow-up with a valid follow-up length (positive integer)",
                        })
                    else:
                        follow_stats = count_followup_pattern(df, seq_str, followup_seq.strip(), followup_len)
                        followup_outcomes = find_followup_outcomes(df, seq_str, max_follow_len=followup_len, top_k=5)
                        entry.update({
                            "followup_seq": followup_seq.strip(),
                            "followup_length": followup_len,
                            "followup_success": follow_stats["followup_success"],
                            "followup_rate": follow_stats["followup_rate"],
                            "followup_total": follow_stats["total_matches"],
                            "followup_outcomes": followup_outcomes,
                        })

                results.append(entry)
                total_matches += len(matches)

            except Exception as seq_err:
                results.append({"seq_str": seq_str, "length": 0, "matches": [], "error": str(seq_err)})

        summary = html.Div(
            f"Scanned {len(seqs)} sequence(s) — {total_matches} total matches found",
            style={
                "color": "#059669" if total_matches else "#f59e0b",
                "fontWeight": "600", "padding": "10px",
                "backgroundColor": "#ecfdf5" if total_matches else "#fffbeb",
                "borderRadius": "8px", "fontSize": "0.85rem",
            },
        )
        return results, summary, "tab-matches"

    except Exception as e:
        logger.exception("scan_sequences error: %s", e)
        err_msg = html.Div(
            f"Scan failed: {e}",
            style={"color": "#ef4444", "fontWeight": "600", "padding": "10px", "backgroundColor": "#fff1f2", "borderRadius": "8px"},
        )
        return None, err_msg, "tab-matches"


# Update chart + matches table when data or scan-results change --------
@app.callback(
    Output("candle-chart", "figure"),
    Output("matches-content", "children"),
    Output("candle-count-badge", "children"),
    Output("current-data-debug", "children"),
    Input("current-data", "data"),
    Input("scan-results", "data"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    prevent_initial_call=False,
)
def update_chart(data, scan_results, start_date, end_date):
    """Draw the candlestick chart and populate the Sequence Matches tab."""
    logger.info("[CALLBACK] update_chart called: data=%s scan=%s",
                'set' if data else 'None', 'set' if scan_results else 'None')
    print(f"[DEBUG] update_chart: data={'set' if data else 'None'}, scan={'set' if scan_results else 'None'}")

    # Fallback to app.default_sample_data if the store is empty
    if not data and hasattr(app, 'default_sample_data') and app.default_sample_data:
        data = app.default_sample_data
        logger.info("[CALLBACK] update_chart: using app.default_sample_data fallback")
        print("[DEBUG] update_chart: using app.default_sample_data fallback")

    # ---- empty state ----
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="Upload a CSV or click  Load Sample Data  to begin",
            xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color='#6366f1', family='sans-serif'),
        )
        fig.update_layout(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            template='plotly_white', height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            dragmode='pan',
        )
        empty = html.Div(
            [html.I(className="bi bi-inbox", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("No data loaded", style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )
        debug_text = html.Div("No data available (current-data store empty)", style={"color": "#6b7280", "fontSize": "0.8rem"})
        return fig, empty, "", debug_text

    # ---- process data ----
    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        if start_date:
            df = df[df["timestamp"] >= pd.to_datetime(start_date, utc=True)]
        if end_date:
            df = df[df["timestamp"] <= pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1)]

        # ---- candlestick ----
        fig = go.Figure(data=[go.Candlestick(
            x=df["timestamp"], open=df["open"], high=df["high"],
            low=df["low"], close=df["close"],
            name="OHLC",
            increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        )])

        total_matches = 0

        # ---- sequence match highlights ----
        if scan_results:
            for idx, res in enumerate(scan_results):
                color = SEQUENCE_COLORS[idx % len(SEQUENCE_COLORS)]
                seq_str = res["seq_str"]
                matches = res.get("matches", [])
                total_matches += len(matches)

                # Add translucent rectangles for each match span
                for m in matches:
                    si, ei = m["start_idx"], m["end_idx"]
                    if si >= len(df) or ei >= len(df):
                        continue
                    x0 = df.iloc[si]["timestamp"]
                    x1 = df.iloc[ei]["timestamp"]
                    fig.add_vrect(
                        x0=x0, x1=x1,
                        fillcolor=color, opacity=0.12,
                        line_width=2, line_color=color,
                        annotation_text=seq_str if len(matches) <= 6 else None,
                        annotation_position="top left",
                        annotation_font_size=9,
                        annotation_font_color=color,
                    )

                # Also add a single invisible scatter for the legend entry
                if matches:
                    fig.add_trace(go.Scatter(
                        x=[None], y=[None], mode='markers',
                        marker=dict(size=10, color=color, symbol="square"),
                        name=f"{seq_str} ({len(matches)})",
                        showlegend=True,
                    ))

        title_text = f"Candlestick Chart | {len(df)} candles"
        if scan_results:
            title_text += f" | {total_matches} sequence matches"

        debug_text = html.Div(
            f"Loaded {len(df)} candles ({df['timestamp'].iloc[0]} → {df['timestamp'].iloc[-1]})",
            style={"color": "#6b7280", "fontSize": "0.8rem"},
        )

        fig.update_layout(
            title=dict(text=title_text, font=dict(size=16, color='#1f2937')),
            template='plotly_white',
            height=550,
            hovermode='x unified',
            dragmode='pan',
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date',
                fixedrange=False,
            ),
            yaxis=dict(
                fixedrange=False,
            ),
            margin=dict(l=50, r=20, t=70, b=40),
            legend=dict(
                orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                font=dict(size=11), bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#e5e7eb', borderwidth=1,
            ),
        )

        # ---- Sequence Matches tab content ----
        if not scan_results:
            matches_div = html.Div(
                [html.I(className="bi bi-search", style={"fontSize": "2rem", "color": "#c7d2fe"}),
                 html.P("Define sequences in the sidebar and click Scan to find matches.",
                        style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
                style={"padding": "3rem", "textAlign": "center"},
            )
        else:
            cards = []
            for idx, res in enumerate(scan_results):
                color = SEQUENCE_COLORS[idx % len(SEQUENCE_COLORS)]
                seq_str = res["seq_str"]
                matches = res.get("matches", [])
                error = res.get("error")

                if error:
                    badge = dbc.Badge("ERROR", color="danger", className="ms-2")
                    body = html.P(f"Parse error: {error}", style={"color": "#ef4444"})
                elif not matches:
                    badge = dbc.Badge("0 matches", color="warning", className="ms-2")
                    body = html.P("No matches found in the loaded data.", style={"color": "#6b7280"})
                else:
                    badge = dbc.Badge(f"{len(matches)} matches", color="success", className="ms-2")
                    rows = []
                    for i, m in enumerate(matches[:50]):
                        rows.append(html.Tr([
                            html.Td(str(i + 1), style={"color": "#9ca3af", "width": "40px"}),
                            html.Td(f"Candle {m['start_idx']} → {m['end_idx']}"),
                            html.Td(m["start_ts"][:19]),
                            html.Td(m["end_ts"][:19]),
                        ]))
                    body_children: list = [
                        dbc.Table(
                            [html.Thead(html.Tr([html.Th("#"), html.Th("Candle Range"), html.Th("Start"), html.Th("End")])),
                             html.Tbody(rows)],
                            bordered=True, hover=True, responsive=True, striped=True, size="sm",
                            style={"fontSize": "0.85rem"},
                        )
                    ]
                    
                    # Add followup outcomes table if available
                    if res.get("followup_outcomes"):
                        outcomes = res.get("followup_outcomes", [])
                        if outcomes:
                            outcome_rows = []
                            for outcome in outcomes:
                                outcome_rows.append(html.Tr([
                                    html.Td(outcome.get("followup", ""), style={"fontFamily": "monospace", "fontWeight": "600"}),
                                    html.Td(str(outcome.get("count", 0))),
                                    html.Td(f"{outcome.get('rate', 0.0):.1%}", style={"color": "#2563eb", "fontWeight": "600"}),
                                ]))
                            
                            body_children.append(html.Hr(style={"margin": "0.75rem 0"}))
                            body_children.append(html.H6("Top Follow-up Outcomes", style={"fontSize": "0.85rem", "fontWeight": "700", "marginBottom": "0.5rem", "color": "#1f2937"}))
                            body_children.append(
                                dbc.Table(
                                    [html.Thead(html.Tr([html.Th("Sequence"), html.Th("Count"), html.Th("Rate")])),
                                     html.Tbody(outcome_rows)],
                                    bordered=True, hover=True, responsive=True, striped=True, size="sm",
                                    style={"fontSize": "0.8rem"},
                                )
                            )
                    
                    body = html.Div(body_children)

                card = dbc.Card([
                    dbc.CardHeader([
                        html.Span(
                            "\u25A0 ",
                            style={"color": color, "fontSize": "1rem"},
                        ),
                        html.Strong(seq_str, style={"fontFamily": "monospace"}),
                        badge,
                        html.Span(f"  ({res.get('length', '?')} candles)", style={"color": "#9ca3af", "fontSize": "0.8rem", "marginLeft": "0.5rem"}),
                        (html.Span(f"Followup: {res.get('followup_seq', '')} ({res.get('followup_success', 0)}/{res.get('followup_total', 0)}) {res.get('followup_rate', 0.0):.0%}", style={"color": "#2563eb", "fontSize": "0.75rem", "marginLeft": "0.5rem"}) if res.get('followup_seq') else None),
                        (html.Span(res.get('followup_error', ''), style={"color": "#b91c1c", "fontSize": "0.75rem", "marginLeft": "0.5rem"}) if res.get('followup_error') else None),
                        # Quick-action buttons
                        html.Span([
                            dbc.Button(
                                [html.I(className="bi bi-bar-chart-steps me-1"), "Backtest"],
                                id={"type": "goto-tab-btn", "tab": "tab-backtest", "idx": idx},
                                color="link", size="sm",
                                style={"fontSize": "0.7rem", "padding": "0.15rem 0.4rem", "fontWeight": "600"},
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-grid-3x3 me-1"), "Heatmap"],
                                id={"type": "goto-tab-btn", "tab": "tab-heatmap", "idx": idx},
                                color="link", size="sm",
                                style={"fontSize": "0.7rem", "padding": "0.15rem 0.4rem", "fontWeight": "600"},
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-graph-up me-1"), "Stats"],
                                id={"type": "goto-tab-btn", "tab": "tab-stats", "idx": idx},
                                color="link", size="sm",
                                style={"fontSize": "0.7rem", "padding": "0.15rem 0.4rem", "fontWeight": "600"},
                            ),
                        ], style={"float": "right"}),
                    ]),
                    dbc.CardBody(body),
                ], className="mb-3")

                cards.append(card)

            matches_div = html.Div(cards)

        candle_badge = dbc.Badge(
            [html.I(className="bi bi-bar-chart-steps me-1"), f"{len(df)} candles"],
            color="light", text_color="secondary",
            style={"fontSize": "0.78rem", "fontWeight": "600"},
        )
        return fig, matches_div, candle_badge, debug_text

    except Exception as e:
        logger.exception("[CALLBACK ERROR] update_chart: %s", e)
        err_fig = go.Figure()
        err_fig.add_annotation(text=f"ERROR: {str(e)[:80]}", xref='paper', yref='paper',
                               x=0.5, y=0.5, showarrow=False, font=dict(size=14, color='#ef4444'))
        err_fig.update_layout(height=400, template='plotly_white', dragmode='pan')
        err_div = html.Div(f"Error: {str(e)[:100]}", style={"color": "#ef4444", "padding": "1rem"})
        err_debug = html.Div(f"update_chart error: {str(e)}", style={"color": "#ef4444", "fontSize": "0.8rem"})
        return err_fig, err_div, "", err_debug


# Quick-action tab-switch from match cards ----------------------------
@app.callback(
    Output("tabs", "active_tab", allow_duplicate=True),
    Input({"type": "goto-tab-btn", "tab": ALL, "idx": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def switch_tab_from_match(n_clicks_list):
    """Switch to the target tab when a quick-action button is clicked."""
    ctx = callback_context
    if not ctx.triggered or not any(n_clicks_list):
        return dash.no_update
    # Extract which button was clicked
    triggered_id = ctx.triggered[0]["prop_id"].rsplit(".", 1)[0]
    import json as _json
    btn_info = _json.loads(triggered_id)
    return btn_info["tab"]


# Auto-Discovery tab — discover common R/G sequences ------------------
@app.callback(
    Output("discovery-content", "children"),
    Input("current-data", "data"),
    prevent_initial_call=False,
)
def auto_discover(data):
    """Automatically discover the most common colour sequences in the loaded data."""
    if not data:
        return html.Div(
            [html.I(className="bi bi-lightbulb", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("Load data to auto-discover common candle sequences.",
                    style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )

    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        discovered = discover_color_sequences(df, min_len=3, max_len=8, top_k=25)

        if not discovered:
            return html.Div("No recurring sequences found.", style={"color": "#6b7280", "padding": "1rem"})

        rows = []
        for i, d in enumerate(discovered):
            # Quick-stats for each discovered sequence
            try:
                stats = sequence_outcome_stats(df, d["sequence"], hold_candles=5)
                wr = f"{stats['win_rate']*100:.0f}%"
                avg_ret = f"{stats['avg_return_pct']:+.2f}%"
                wr_color = "#10b981" if stats["win_rate"] >= 0.5 else "#ef4444"
                ret_color = "#10b981" if stats["avg_return_pct"] >= 0 else "#ef4444"
            except Exception:
                wr = "—"
                avg_ret = "—"
                wr_color = "#9ca3af"
                ret_color = "#9ca3af"

            rows.append(html.Tr([
                html.Td(str(i + 1), style={"color": "#9ca3af", "width": "40px"}),
                html.Td(
                    html.Code(d["sequence"], style={"fontSize": "0.85rem"}),
                ),
                html.Td(str(d["length"])),
                html.Td(str(d["count"]), style={"fontWeight": "700"}),
                html.Td(f"{d['support']:.4f}"),
                html.Td(wr, style={"fontWeight": "700", "color": wr_color}),
                html.Td(avg_ret, style={"fontWeight": "700", "color": ret_color}),
            ]))

        header = html.Div(
            [html.I(className="bi bi-stars me-2"),
             f"Top {len(discovered)} recurring colour sequences (length 3-8)"],
            style={
                "padding": "0.75rem 1rem", "backgroundColor": "#f0f0ff",
                "borderRadius": "8px", "fontWeight": "600", "color": "#4f46e5",
                "marginBottom": "0.75rem",
            },
        )

        table = dbc.Table(
            [html.Thead(html.Tr([html.Th("#"), html.Th("Sequence"), html.Th("Length"), html.Th("Count"), html.Th("Support"), html.Th("Win Rate"), html.Th("Avg Return")])),
             html.Tbody(rows)],
            bordered=True, hover=True, responsive=True, striped=True, size="sm",
            style={"fontSize": "0.9rem"},
        )

        tip = html.Small(
            "Tip: Copy a discovered sequence into the Custom Sequences box and click Scan to see chart highlights and full statistics.",
            style={"color": "#9ca3af", "display": "block", "marginTop": "0.75rem"},
        )

        legend = html.Div([
            html.Small("Win Rate & Avg Return are calculated over a 5-candle hold period following each occurrence.", style={"color": "#6b7280", "display": "block", "marginTop": "0.25rem"}),
        ])

        return html.Div([header, table, tip, legend])

    except Exception as e:
        logger.exception("auto_discover error: %s", e)
        return html.Div(f"Error: {str(e)[:120]}", style={"color": "#ef4444", "padding": "1rem"})


# Statistics & Predictions tab -----------------------------------------
@app.callback(
    Output("stats-content", "children"),
    Input("scan-results", "data"),
    Input("current-data", "data"),
    Input("hold-period-slider", "value"),
    Input("lookahead-slider", "value"),
    prevent_initial_call=False,
)
def update_stats_tab(scan_results, data, hold_candles, lookahead):
    """Display outcome statistics and what-comes-next predictions for scanned sequences."""
    hold_candles = hold_candles or 5
    lookahead = lookahead or 3

    if not data:
        return html.Div(
            [html.I(className="bi bi-bar-chart-line", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("Load data to see sequence statistics.",
                    style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )

    if not scan_results:
        return html.Div(
            [html.I(className="bi bi-graph-up-arrow", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("Scan sequences first to see statistics and predictions.",
                    style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )

    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        sections = []

        for idx, res in enumerate(scan_results):
            seq_str = res["seq_str"]
            color = SEQUENCE_COLORS[idx % len(SEQUENCE_COLORS)]
            matches = res.get("matches", [])

            if res.get("error") or not matches:
                continue

            # --- Outcome statistics ---
            try:
                stats = sequence_outcome_stats(df, seq_str, hold_candles=hold_candles)
            except Exception:
                stats = None

            # --- What comes next ---
            try:
                prediction = what_comes_next(df, seq_str, lookahead=lookahead)
            except Exception:
                prediction = None

            # --- Confidence scoring ---
            try:
                conf = sequence_confidence(df, seq_str, hold_candles=hold_candles)
            except Exception:
                conf = None

            # Build stats card
            stats_items = []
            if stats and stats["occurrences"] > 0:
                wr = stats["win_rate"] * 100
                wr_color = "#10b981" if wr >= 50 else "#ef4444"
                avg_ret = stats["avg_return_pct"]
                ret_color = "#10b981" if avg_ret >= 0 else "#ef4444"

                stats_items.append(
                    dbc.Row([
                        dbc.Col(html.Div([
                            html.H6(f"Win Rate ({hold_candles}-candle hold)", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                            html.H4(f"{wr:.1f}%", style={"color": wr_color, "fontWeight": "800", "margin": "0"}),
                        ], className="stat-card"), width=3),
                        dbc.Col(html.Div([
                            html.H6("Avg Return", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                            html.H4(f"{avg_ret:+.2f}%", style={"color": ret_color, "fontWeight": "800", "margin": "0"}),
                        ], className="stat-card"), width=2),
                        dbc.Col(html.Div([
                            html.H6("Max Gain", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                            html.H4(f"{stats['max_gain_pct']:+.2f}%", style={"color": "#10b981", "fontWeight": "800", "margin": "0"}),
                        ], className="stat-card"), width=2),
                        dbc.Col(html.Div([
                            html.H6("Max Loss", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                            html.H4(f"{stats['max_loss_pct']:+.2f}%", style={"color": "#ef4444", "fontWeight": "800", "margin": "0"}),
                        ], className="stat-card"), width=2),
                    ], className="g-2 mb-2")
                )

                # Confidence scoring row
                if conf:
                    conf_color = "#10b981" if conf["is_significant"] else "#f59e0b"
                    z_color = "#10b981" if abs(conf.get("z_score", 0)) > 1.96 else "#6b7280"
                    stats_items.append(
                        dbc.Row([
                            dbc.Col(html.Div([
                                html.H6("Confidence", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                                html.Span(conf["confidence_level"], style={"color": conf_color, "fontWeight": "700", "fontSize": "0.85rem"}),
                            ], className="stat-card"), width=3),
                            dbc.Col(html.Div([
                                html.H6("Z-Score", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                                html.H4(f"{conf.get('z_score', 0):.2f}", style={"color": z_color, "fontWeight": "800", "margin": "0", "fontSize": "1.5rem"}),
                            ], className="stat-card"), width=2),
                            dbc.Col(html.Div([
                                html.H6("P-Value", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                                html.H4(f"{conf.get('p_value', 1):.4f}", style={"color": "#374151", "fontWeight": "700", "margin": "0", "fontSize": "1.2rem"}),
                            ], className="stat-card"), width=2),
                            dbc.Col(html.Div([
                                html.H6("Baseline Avg", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                                html.H4(f"{conf.get('baseline_avg', 0):+.2f}%", style={"color": "#6b7280", "fontWeight": "700", "margin": "0", "fontSize": "1.2rem"}),
                            ], className="stat-card"), width=2),
                            dbc.Col(html.Div([
                                html.H6("Significant?", style={"color": "#6b7280", "fontSize": "0.7rem", "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "4px"}),
                                html.H4(
                                    "YES" if conf["is_significant"] else "NO",
                                    style={"color": "#10b981" if conf["is_significant"] else "#ef4444", "fontWeight": "800", "margin": "0", "fontSize": "1.5rem"},
                                ),
                            ], className="stat-card"), width=2),
                        ], className="g-2 mb-3")
                    )

            # Build prediction table
            pred_items = []
            if prediction and prediction["total_occurrences"] > 0:
                pred_rows = []
                for d in prediction["distribution"]:
                    r_pct = d.get("R_pct", 0) * 100
                    g_pct = d.get("G_pct", 0) * 100
                    doji_pct = d.get("Doji_pct", 0) * 100
                    best = max(("R", "G", "Doji"), key=lambda k: d.get(f"{k}_pct", 0))
                    pred_rows.append(html.Tr([
                        html.Td(f"+{d['position']}", style={"fontWeight": "700"}),
                        html.Td(
                            html.Div(
                                style={"display": "flex", "gap": "4px", "alignItems": "center"},
                                children=[
                                    html.Div(style={"width": f"{r_pct}%", "minWidth": "2px" if r_pct > 0 else "0", "height": "18px", "background": "#ef4444", "borderRadius": "4px"}),
                                    html.Div(style={"width": f"{g_pct}%", "minWidth": "2px" if g_pct > 0 else "0", "height": "18px", "background": "#10b981", "borderRadius": "4px"}),
                                    html.Div(style={"width": f"{doji_pct}%", "minWidth": "2px" if doji_pct > 0 else "0", "height": "18px", "background": "#6366f1", "borderRadius": "4px"}),
                                ]
                            )
                        ),
                        html.Td(f"{r_pct:.0f}%", style={"color": "#ef4444", "fontWeight": "600"}),
                        html.Td(f"{g_pct:.0f}%", style={"color": "#10b981", "fontWeight": "600"}),
                        html.Td(f"{doji_pct:.0f}%", style={"color": "#6366f1", "fontWeight": "600"}),
                        html.Td(html.Strong(best), style={"color": "#1f2937"}),
                    ]))

                pred_items.append(
                    html.Div([
                        html.H6([
                            html.I(className="bi bi-lightning-fill me-1"),
                            f"What Comes Next? (predicted from {prediction['total_occurrences']} occurrences)"
                        ], style={"fontWeight": "700", "color": "#4f46e5", "marginBottom": "0.5rem"}),
                        html.P([
                            "Most likely continuation: ",
                            html.Code(prediction["most_likely_next"] or "—", style={"fontSize": "0.9rem"}),
                        ], style={"marginBottom": "0.5rem", "color": "#374151"}),
                        dbc.Table(
                            [html.Thead(html.Tr([
                                html.Th("Candle"), html.Th("Distribution"),
                                html.Th("Red"), html.Th("Green"), html.Th("Doji"), html.Th("Likely"),
                            ])),
                             html.Tbody(pred_rows)],
                            bordered=True, hover=True, responsive=True, striped=True, size="sm",
                            style={"fontSize": "0.85rem"},
                        ),
                    ], style={"marginTop": "0.75rem"})
                )

            card = dbc.Card([
                dbc.CardHeader([
                    html.Span("\u25A0 ", style={"color": color, "fontSize": "1rem"}),
                    html.Strong(seq_str, style={"fontFamily": "monospace"}),
                    dbc.Badge(f"{len(matches)} matches", color="success", className="ms-2"),
                ]),
                dbc.CardBody(stats_items + pred_items if (stats_items or pred_items) else [
                    html.P("Not enough data for analysis.", style={"color": "#9ca3af"})
                ]),
            ], className="mb-3")

            sections.append(card)

        if not sections:
            return html.Div(
                [html.I(className="bi bi-exclamation-circle", style={"fontSize": "1.5rem", "color": "#f59e0b"}),
                 html.P("No matched sequences to analyze. Try scanning for sequences with at least 1 match.",
                        style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
                style={"padding": "3rem", "textAlign": "center"},
            )

        header = html.Div(
            [html.I(className="bi bi-bar-chart-line me-2"),
             "Sequence Outcome Statistics & Predictions"],
            style={
                "padding": "0.75rem 1rem", "backgroundColor": "#fefce8",
                "borderRadius": "8px", "fontWeight": "600", "color": "#854d0e",
                "marginBottom": "0.75rem",
            },
        )

        return html.Div([header] + sections)

    except Exception as e:
        logger.exception("update_stats_tab error: %s", e)
        return html.Div(f"Error: {str(e)[:120]}", style={"color": "#ef4444", "padding": "1rem"})


# History dropdown refresh  -------------------------------------------
@app.callback(
    Output("history-select", "options"),
    Input("upload-status", "children"),
)
def refresh_history(_):
    from candle_patterns.storage import list_uploads
    rows = list_uploads(limit=200)
    return [{"label": f"{r['stored_at']} - {r['filename']}", "value": r["id"]} for r in rows]


# Run cleanup (with confirmation) ------------------------------------
@app.callback(
    Output("cleanup-confirm", "displayed"),
    Input("cleanup-btn", "n_clicks"),
    prevent_initial_call=True,
)
def confirm_cleanup(n):
    return True


@app.callback(
    Output("cleanup-result", "children", allow_duplicate=True),
    Input("cleanup-confirm", "submit_n_clicks"),
    prevent_initial_call=True,
)
def run_cleanup(submit_n):
    if not submit_n:
        return dash.no_update
    from candle_patterns.storage import cleanup_old_uploads
    removed = cleanup_old_uploads(retention_days=30)
    return html.Div(
        [html.I(className="bi bi-check-circle me-1"), f"Removed {removed} old uploads/detections"],
        style={"color": "#10b981", "fontWeight": "600"},
    )


# Pattern detail modal (click on chart) --------------------------------
@app.callback(
    Output("pattern-modal", "is_open"),
    Output("pattern-modal-body", "children"),
    Input("candle-chart", "clickData"),
    Input("modal-close", "n_clicks"),
    State("pattern-modal", "is_open"),
    State("current-data", "data"),
)
def show_pattern_detail(clickData, nclose, is_open, current_data):
    ctx = callback_context
    if not ctx.triggered:
        return False, ""
    trig = ctx.triggered[0]["prop_id"].split(".")[0]
    if trig == "modal-close":
        return False, ""
    if clickData and "points" in clickData:
        pt = clickData["points"][0]
        x = pt.get("x")
        body_items = [
            html.H5("Candle Detail", style={"fontWeight": "700", "color": "#4f46e5"}),
            html.P([html.I(className="bi bi-clock me-2"), f"Timestamp: {x}"], style={"color": "#6b7280"}),
        ]
        try:
            if current_data:
                df_all = pd.DataFrame(current_data.get('df', []))
                if len(df_all):
                    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'], utc=True)
                    ts = pd.to_datetime(x, utc=True)
                    idx = df_all.index[(df_all['timestamp'] - ts).abs().argsort()[:1]][0]
                    start = max(0, idx - 5)
                    end = min(len(df_all) - 1, idx + 5)
                    window = df_all.iloc[start:end + 1]
                    mini_fig = go.Figure(data=[go.Candlestick(
                        x=window['timestamp'], open=window['open'],
                        high=window['high'], low=window['low'], close=window['close'],
                        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
                    )])
                    mini_fig.update_layout(
                        margin=dict(l=40, r=10, t=10, b=30), height=250,
                        template='plotly_white',
                        xaxis=dict(rangeslider=dict(visible=False)),
                    )
                    body_items.append(dcc.Graph(figure=mini_fig, config={'displayModeBar': False}))
        except Exception as e:
            logger.debug('mini-chart build error: %s', e)
        return True, html.Div(body_items)
    return False, ""


# Stats cards  ---------------------------------------------------------
@app.callback(
    Output("stats-cards", "children"),
    Input("upload-status", "children"),
    Input("history-select", "value"),
)
def update_stats(_, __):
    from candle_patterns.storage import list_uploads
    rows = list_uploads(limit=100)
    total_uploads = len(rows)
    last_upload = rows[0] if rows else None
    last_label = f"{last_upload['stored_at'].split(' ')[0]} - {last_upload['filename']}" if last_upload else "-"

    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Total Uploads", style={"color": "#6c757d", "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "1px", "fontWeight": "600", "marginBottom": "0.5rem"}),
            html.H4(str(total_uploads), style={"color": "#667eea", "fontWeight": "700"}),
        ]), className="stat-card"), width=6),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Last Upload", style={"color": "#6c757d", "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "1px", "fontWeight": "600", "marginBottom": "0.5rem"}),
            html.P(last_label, style={"color": "#495057", "fontSize": "0.85rem", "margin": "0"}),
        ]), className="stat-card"), width=6),
    ], className="g-2 mt-3")


# Export ---------------------------------------------------------------
@app.callback(
    Output("download-asset", "data"),
    Output("export-status", "children"),
    Input("export-detections-btn", "n_clicks"),
    Input("export-aggregated-btn", "n_clicks"),
    Input("export-chart-btn", "n_clicks"),
    State("scan-results", "data"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def export_data(n_matches, n_discovery, n_chart, scan_results, data):
    """Export matches CSV, discovery CSV, or chart PNG."""
    no_data_msg = html.Div(
        [html.I(className="bi bi-exclamation-circle me-1"), "No data to export"],
        style={"color": "#f59e0b", "fontWeight": "600", "fontSize": "0.8rem"},
    )
    if not data:
        return dash.no_update, no_data_msg
    triggered = callback_context.triggered_id

    if triggered == "export-detections-btn":
        if not scan_results:
            return dash.no_update, no_data_msg
        rows = []
        for res in scan_results:
            for m in res.get("matches", []):
                rows.append({"sequence": res["seq_str"], **m})
        if rows:
            ok_msg = html.Div(
                [html.I(className="bi bi-check-circle me-1"), f"Exported {len(rows)} matches"],
                style={"color": "#10b981", "fontWeight": "600", "fontSize": "0.8rem"},
            )
            return send_data_frame(pd.DataFrame(rows).to_csv, "sequence_matches.csv", index=False), ok_msg
        return dash.no_update, no_data_msg

    elif triggered == "export-aggregated-btn":
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        discovered = discover_color_sequences(df, min_len=3, max_len=8, top_k=25)
        if discovered:
            ok_msg = html.Div(
                [html.I(className="bi bi-check-circle me-1"), f"Exported {len(discovered)} sequences"],
                style={"color": "#10b981", "fontWeight": "600", "fontSize": "0.8rem"},
            )
            return send_data_frame(pd.DataFrame(discovered).to_csv, "discovered_sequences.csv", index=False), ok_msg
        return dash.no_update, no_data_msg

    elif triggered == "export-chart-btn":
        df = pd.DataFrame(data['df'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'],
                                              high=df['high'], low=df['low'], close=df['close'])])
        try:
            img_bytes = fig.to_image(format='png', width=1200, height=600, scale=2)
            ok_msg = html.Div(
                [html.I(className="bi bi-check-circle me-1"), "Chart PNG exported"],
                style={"color": "#10b981", "fontWeight": "600", "fontSize": "0.8rem"},
            )
            return send_bytes(lambda: img_bytes, "chart.png"), ok_msg
        except Exception as e:
            logger.exception('export chart failed: %s', e)
            err_msg = html.Div(
                [html.I(className="bi bi-exclamation-triangle me-1"),
                 "PNG export requires the 'kaleido' package. Install with: pip install kaleido"],
                style={"color": "#ef4444", "fontWeight": "600", "fontSize": "0.8rem"},
            )
            return dash.no_update, err_msg

    return dash.no_update, ""


# Load from history  ---------------------------------------------------
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Output("upload-status", "children", allow_duplicate=True),
    Input("history-select", "value"),
    prevent_initial_call=True,
)
def load_from_history(upload_id):
    if not upload_id:
        return None, ""
    from candle_patterns.storage import get_upload

    rec = get_upload(upload_id)
    if not rec:
        return None, ""

    df = pd.read_csv(rec["filepath"]) if rec.get("filepath") else pd.DataFrame()
    data = {
        "filename": rec.get("filename"),
        "upload_id": rec.get("id"),
        "df": df.to_dict("records"),
    }
    return data, f"Loaded: {rec.get('filename')}"


# =========================================================================
# YAHOO FINANCE CALLBACKS
# =========================================================================

# Set symbol input when a popular symbol is selected
@app.callback(
    Output("yf-symbol-input", "value"),
    Input("yf-symbol-select", "value"),
    prevent_initial_call=True,
)
def set_yf_symbol(symbol):
    if symbol:
        return symbol
    return dash.no_update


# Fetch data from Yahoo Finance
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Output("yf-fetch-status", "children"),
    Output("upload-status", "children", allow_duplicate=True),
    Input("yf-fetch-btn", "n_clicks"),
    State("yf-symbol-input", "value"),
    State("yf-period", "value"),
    State("yf-interval", "value"),
    prevent_initial_call=True,
)
def on_yf_fetch(n_clicks, symbol, period, interval):
    if not n_clicks or not symbol:
        return dash.no_update, html.Div("Enter a symbol first.", style={"color": "#f59e0b", "fontWeight": "600", "fontSize": "0.85rem"}), dash.no_update

    try:
        df = fetch_yahoo_data(symbol.strip(), period=period, interval=interval)

        try:
            upload_meta = save_upload(f"yf_{symbol}_{period}_{interval}", df, [])
            upload_id = upload_meta.get("upload_id") if isinstance(upload_meta, dict) else upload_meta
        except Exception:
            upload_id = None

        data = {
            "filename": f"{symbol} ({period}, {interval})",
            "upload_id": upload_id,
            "df": df.to_dict("records"),
        }

        status = html.Div(
            f"Fetched {len(df)} candles for {symbol} ({period}, {interval})",
            style={
                "color": "#059669", "fontWeight": "600", "padding": "10px",
                "backgroundColor": "#ecfdf5", "borderRadius": "8px", "fontSize": "0.85rem",
            },
        )
        upload_status = html.Div(
            [html.I(className="bi bi-cloud-check me-1"),
             f"Yahoo Finance: {symbol} — {len(df)} candles loaded"],
            style={"color": "#059669", "fontWeight": "600", "padding": "12px",
                   "backgroundColor": "#ecfdf5", "borderRadius": "6px", "marginTop": "8px"},
        )
        return data, status, upload_status

    except (ValueError, ConnectionError) as e:
        err = html.Div(
            f"Error: {str(e)[:100]}",
            style={"color": "#ef4444", "fontWeight": "600", "fontSize": "0.85rem", "padding": "8px",
                   "backgroundColor": "#fef2f2", "borderRadius": "8px"},
        )
        return dash.no_update, err, dash.no_update
    except Exception as e:
        err = html.Div(
            f"Unexpected error: {str(e)[:100]}",
            style={"color": "#ef4444", "fontWeight": "600", "fontSize": "0.85rem"},
        )
        return dash.no_update, err, dash.no_update


# =========================================================================
# HEATMAP TAB CALLBACK
# =========================================================================

@app.callback(
    Output("heatmap-content", "children"),
    Input("scan-results", "data"),
    Input("current-data", "data"),
    prevent_initial_call=False,
)
def update_heatmap(scan_results, data):
    """Render a heatmap showing sequence match density across time buckets."""
    if not data:
        return html.Div(
            [html.I(className="bi bi-grid-3x3", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("Load data to see the sequence heatmap.",
                    style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )

    if not scan_results:
        return html.Div(
            [html.I(className="bi bi-grid-3x3-gap", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("Scan sequences first to see pattern density heatmap.",
                    style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )

    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        seq_strs = [r["seq_str"] for r in scan_results if not r.get("error")]
        if not seq_strs:
            return html.Div("No valid sequences to heatmap.", style={"color": "#9ca3af", "padding": "1rem"})

        heatmap = sequence_heatmap_data(df, seq_strs, bucket_size=10)

        # Build Plotly heatmap
        z_data = []
        y_labels = []
        for seq_str in seq_strs:
            counts = heatmap["sequences"].get(seq_str, [])
            z_data.append(counts)
            y_labels.append(seq_str)

        # X-axis: bucket timestamps (shortened)
        x_labels = []
        for ts in heatmap["timestamps"]:
            if ts:
                x_labels.append(ts[:10])  # date only
            else:
                x_labels.append("")

        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale=[
                [0, "#f9fafb"],
                [0.25, "#c7d2fe"],
                [0.5, "#818cf8"],
                [0.75, "#6366f1"],
                [1, "#4338ca"],
            ],
            hoverongaps=False,
            hovertemplate="Bucket: %{x}<br>Sequence: %{y}<br>Matches: %{z}<extra></extra>",
        ))

        fig.update_layout(
            title=dict(text="Sequence Match Density Over Time", font=dict(size=16, color="#1f2937")),
            xaxis=dict(title="Time Bucket (start date)", tickangle=-45),
            yaxis=dict(title="Sequence", autorange="reversed"),
            template="plotly_white",
            height=max(300, 50 * len(y_labels) + 150),
            margin=dict(l=150, r=20, t=60, b=80),
        )

        header = html.Div(
            [html.I(className="bi bi-grid-3x3 me-2"),
             f"Pattern Density Heatmap — {len(seq_strs)} sequences across {len(x_labels)} time buckets (10 candles each)"],
            style={
                "padding": "0.75rem 1rem", "backgroundColor": "#ede9fe",
                "borderRadius": "8px", "fontWeight": "600", "color": "#5b21b6",
                "marginBottom": "0.75rem",
            },
        )

        return html.Div([
            header,
            dcc.Graph(figure=fig, config={"responsive": True, "displayModeBar": True, "displaylogo": False}),
            html.Small(
                "Each cell shows how many times a sequence matched within that 10-candle time bucket. "
                "Darker cells indicate higher pattern concentration.",
                style={"color": "#6b7280", "display": "block", "marginTop": "0.75rem"},
            ),
        ])

    except Exception as e:
        logger.exception("heatmap error: %s", e)
        return html.Div(f"Error: {str(e)[:120]}", style={"color": "#ef4444", "padding": "1rem"})


# =========================================================================
# REVERSE PATTERN FINDER CALLBACK
# =========================================================================

@app.callback(
    Output("reverse-content", "children"),
    Input("reverse-find-btn", "n_clicks"),
    State("reverse-threshold", "value"),
    State("reverse-direction", "value"),
    State("reverse-lookback", "value"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def update_reverse_finder(n_clicks, threshold, direction, lookback, data):
    """Find sequences that preceded big price moves."""
    if not data:
        return html.Div("Load data first.", style={"color": "#f59e0b", "fontWeight": "600", "padding": "1rem"})

    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        threshold = float(threshold or 1.5)
        lookback = int(lookback or 5)
        direction = direction or "up"

        results = reverse_pattern_finder(
            df, threshold_pct=threshold, direction=direction,
            lookback=lookback, min_len=3, max_len=6, top_k=15,
        )

        if not results:
            dir_label = {"up": "gains", "down": "losses", "both": "moves"}.get(direction, "moves")
            return html.Div(
                [html.I(className="bi bi-info-circle me-2", style={"fontSize": "1.2rem"}),
                 f"No big {dir_label} (>{threshold}%) found. Try lowering the threshold or loading more data."],
                style={"color": "#6b7280", "padding": "2rem", "textAlign": "center", "fontWeight": "600"},
            )

        # Build confidence data for each discovered preceding sequence
        rows = []
        for i, r in enumerate(results):
            avg_move_color = "#10b981" if r["avg_move_pct"] > 0 else "#ef4444"

            # Quick confidence check
            try:
                conf = sequence_confidence(df, r["sequence"], hold_candles=5)
                conf_badge_color = "success" if conf["is_significant"] else "warning"
                conf_text = conf["confidence_level"]
                p_val = f"{conf['p_value']:.4f}"
            except Exception:
                conf_badge_color = "secondary"
                conf_text = "N/A"
                p_val = "—"

            rows.append(html.Tr([
                html.Td(str(i + 1), style={"color": "#9ca3af", "width": "40px"}),
                html.Td(html.Code(r["sequence"], style={"fontSize": "0.85rem"})),
                html.Td(str(r["length"])),
                html.Td(str(r["count"]), style={"fontWeight": "700"}),
                html.Td(f"{r['avg_move_pct']:+.2f}%", style={"fontWeight": "700", "color": avg_move_color}),
                html.Td(dbc.Badge(conf_text, color=conf_badge_color, style={"fontSize": "0.7rem"})),
                html.Td(p_val, style={"fontSize": "0.8rem", "color": "#6b7280"}),
            ]))

        dir_label = {"up": "big gains", "down": "big losses", "both": "big moves"}.get(direction, "moves")
        header = html.Div(
            [html.I(className="bi bi-arrow-return-left me-2"),
             f"Top {len(results)} sequences preceding {dir_label} (>{threshold}% threshold, {lookback}-candle lookback)"],
            style={
                "padding": "0.75rem 1rem", "backgroundColor": "#fef3c7",
                "borderRadius": "8px", "fontWeight": "600", "color": "#92400e",
                "marginBottom": "0.75rem",
            },
        )

        table = dbc.Table(
            [html.Thead(html.Tr([
                html.Th("#"), html.Th("Sequence"), html.Th("Length"),
                html.Th("Occurrences"), html.Th("Avg Move"),
                html.Th("Confidence"), html.Th("p-value"),
            ])),
             html.Tbody(rows)],
            bordered=True, hover=True, responsive=True, striped=True, size="sm",
            style={"fontSize": "0.9rem"},
        )

        tip = html.Small(
            "These are the most common colour sequences found in the candles immediately before big price moves. "
            "Copy a sequence into the Custom Sequences box and scan to see it on the chart.",
            style={"color": "#9ca3af", "display": "block", "marginTop": "0.75rem"},
        )

        return html.Div([header, table, tip])

    except Exception as e:
        logger.exception("reverse_finder error: %s", e)
        return html.Div(f"Error: {str(e)[:120]}", style={"color": "#ef4444", "padding": "1rem"})


# ======================================================================
# CALLBACK 18: BACKTESTING TAB
# ======================================================================

@app.callback(
    Output("backtest-content", "children"),
    Input("bt-run-btn", "n_clicks"),
    State("bt-hold-slider", "value"),
    State("bt-capital", "value"),
    State("scan-results", "data"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def run_backtest(n_clicks, hold_periods, initial_capital, scan_results, data):
    """Backtest each scanned sequence: equity curve, Sharpe, drawdown."""
    if not n_clicks or not data or not scan_results:
        return html.Div("Load data and scan sequences first.", style={"color": "#6b7280", "padding": "1rem"})

    try:
        df = pd.DataFrame(data["df"])
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        hold_periods = int(hold_periods or 5)
        initial_capital = float(initial_capital or 10000)
        engine = BacktestEngine()
        cards: list = []

        for res in scan_results:
            seq_str = res.get("seq_str", "")
            matches_info = res.get("matches", [])
            # matches_info is a list of match dicts
            if isinstance(matches_info, list):
                indices = [m if isinstance(m, int) else m.get("end_idx", 0) for m in matches_info]
            else:
                continue
            if not indices:
                continue

            trades = engine.calculate_returns(df, indices, hold_periods)
            if trades.empty:
                continue

            returns = trades["return"]
            win_rate, n_wins, n_losses = engine.calculate_win_rate(trades)
            sharpe = engine.calculate_sharpe_ratio(returns)
            max_dd = engine.calculate_max_drawdown(returns)
            pf = engine.calculate_profit_factor(trades)
            eq = engine.calculate_equity_curve(trades, initial_capital)

            # Mini equity curve
            eq_fig = go.Figure()
            eq_fig.add_trace(go.Scatter(
                y=eq.values, mode="lines+markers",
                line=dict(color="#6366f1", width=2),
                marker=dict(size=4),
                name="Equity",
            ))
            eq_fig.update_layout(
                height=180, margin=dict(l=30, r=10, t=10, b=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f9fafb",
                yaxis=dict(title="$", gridcolor="#e5e7eb"),
                xaxis=dict(title="Trade #", gridcolor="#e5e7eb"),
                showlegend=False,
            )

            wr_color = "#10b981" if win_rate > 0.5 else "#ef4444"
            sh_color = "#10b981" if sharpe > 0 else "#ef4444"

            card = dbc.Card(
                dbc.CardBody([
                    html.H6(html.Code(seq_str), className="mb-2"),
                    dbc.Row([
                        dbc.Col(html.Div([
                            html.Small("Trades", style={"color": "#6b7280"},
                                       title="Total number of simulated trades"),
                            html.H5(str(len(trades)), style={"fontWeight": "700"}),
                        ]), width=2),
                        dbc.Col(html.Div([
                            html.Small("Win Rate", style={"color": "#6b7280"},
                                       title="Percentage of trades that ended in profit"),
                            html.H5(f"{win_rate:.1%}", style={"fontWeight": "700", "color": wr_color}),
                        ]), width=2),
                        dbc.Col(html.Div([
                            html.Small("Sharpe", style={"color": "#6b7280"},
                                       title="Risk-adjusted return (Sharpe Ratio). >1 is good, >2 is excellent"),
                            html.H5(f"{sharpe:.2f}", style={"fontWeight": "700", "color": sh_color}),
                        ]), width=2),
                        dbc.Col(html.Div([
                            html.Small("Max DD", style={"color": "#6b7280"},
                                       title="Maximum drawdown — largest peak-to-trough decline"),
                            html.H5(f"{max_dd:.1%}", style={"fontWeight": "700", "color": "#ef4444"}),
                        ]), width=2),
                        dbc.Col(html.Div([
                            html.Small("Profit Factor", style={"color": "#6b7280"},
                                       title="Gross profit / Gross loss. >1 means profitable, >2 is strong"),
                            html.H5(f"{pf:.2f}" if pf != float("inf") else "∞",
                                    style={"fontWeight": "700", "color": "#6366f1"}),
                        ]), width=2),
                        dbc.Col(html.Div([
                            html.Small("Final Equity", style={"color": "#6b7280"},
                                       title="Portfolio value at the end of the backtest"),
                            html.H5(f"${eq.iloc[-1]:,.0f}", style={"fontWeight": "700"}),
                        ]), width=2),
                    ]),
                    dcc.Graph(figure=eq_fig, config={"displayModeBar": False},
                              style={"marginTop": "0.5rem"}),
                ]),
                className="mb-3",
                style={"border": "1px solid #e5e7eb", "borderRadius": "12px"},
            )
            cards.append(card)

        if not cards:
            return html.Div("No trades generated from scanned sequences. Try scanning first.",
                            style={"color": "#6b7280", "padding": "1rem"})

        header = html.Div(
            [html.I(className="bi bi-calculator me-2"),
             f"Backtest Results — {hold_periods}-candle hold, ${initial_capital:,.0f} capital"],
            style={
                "padding": "0.75rem 1rem", "backgroundColor": "#dcfce7",
                "borderRadius": "8px", "fontWeight": "600", "color": "#166534",
                "marginBottom": "1rem",
            },
        )
        return html.Div([header] + cards)

    except Exception as e:
        logger.exception("backtest error: %s", e)
        return html.Div(f"Error: {str(e)[:120]}", style={"color": "#ef4444", "padding": "1rem"})


# ======================================================================
# CALLBACK 19: MULTI-TIMEFRAME ANALYSIS
# ======================================================================

@app.callback(
    Output("mtf-content", "children"),
    Input("mtf-run-btn", "n_clicks"),
    State("mtf-symbol", "value"),
    State("mtf-intervals", "value"),
    State("mtf-lookback", "value"),
    State("scan-results", "data"),
    prevent_initial_call=True,
)
def run_multi_timeframe(n_clicks, symbol, intervals, lookback, scan_results):
    """Cross-timeframe sequence alignment analysis."""
    if not n_clicks:
        return html.Div()
    if not symbol or not symbol.strip():
        return html.Div("Enter a symbol (e.g. AAPL, BTC-USD).", style={"color": "#ef4444", "padding": "1rem"})
    if not intervals:
        return html.Div("Select at least one timeframe.", style={"color": "#ef4444", "padding": "1rem"})

    # Gather sequences from scan results (scan_results is a list of dicts)
    sequences = [r["seq_str"] for r in scan_results if r.get("seq_str")] if scan_results else []
    if not sequences:
        return html.Div("Scan sequences first so we know what to look for across timeframes.",
                        style={"color": "#6b7280", "padding": "1rem"})

    try:
        lookback = int(lookback or 5)
        # Map common aliases for yfinance
        interval_map: dict[str, str] = {"4h": "60m"}  # yfinance 4h workaround
        yf_intervals = [interval_map.get(str(iv), str(iv)) for iv in intervals if iv is not None]

        result = multi_timeframe_summary(
            symbol=symbol.strip(),
            intervals=yf_intervals,
            sequences=sequences,
            lookback=lookback,
        )

        # Per-timeframe stats table
        tf_rows = []
        for iv, stats in result["per_timeframe_stats"].items():
            tf_rows.append(html.Tr([
                html.Td(html.Code(iv), style={"fontWeight": "700"}),
                html.Td(str(stats["candle_count"])),
                html.Td(str(stats["total_matches"]), style={"fontWeight": "700"}),
                html.Td(str(stats["sequences_found"])),
            ]))

        tf_table = dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Timeframe"), html.Th("Candles"), html.Th("Total Matches"), html.Th("Sequences Found"),
            ])),
             html.Tbody(tf_rows)],
            bordered=True, hover=True, responsive=True, striped=True, size="sm",
        )

        # Alignment table
        align_rows = []
        for a in result["alignment"]:
            count = a["alignment_count"]
            total = a["total_timeframes"]
            pct = (count / total * 100) if total else 0
            color = "#10b981" if pct >= 50 else ("#f59e0b" if pct >= 25 else "#ef4444")
            align_rows.append(html.Tr([
                html.Td(html.Code(a["sequence"], style={"fontSize": "0.85rem"})),
                html.Td(", ".join(a["aligned_timeframes"]) if a["aligned_timeframes"] else "—",
                         style={"fontSize": "0.85rem"}),
                html.Td(f"{count}/{total}", style={"fontWeight": "700"}),
                html.Td(f"{pct:.0f}%", style={"fontWeight": "700", "color": color}),
            ]))

        align_table = dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Sequence"), html.Th("Aligned TFs"), html.Th("Count"), html.Th("Alignment %"),
            ])),
             html.Tbody(align_rows)],
            bordered=True, hover=True, responsive=True, striped=True, size="sm",
        )

        header = html.Div(
            [html.I(className="bi bi-layers me-2"),
             f"Multi-Timeframe Analysis: {symbol.upper()} — {', '.join(intervals)}"],
            style={
                "padding": "0.75rem 1rem", "backgroundColor": "#dbeafe",
                "borderRadius": "8px", "fontWeight": "600", "color": "#1e40af",
                "marginBottom": "1rem",
            },
        )

        return html.Div([
            header,
            html.H6("Per-Timeframe Summary", className="mt-3 mb-2"),
            tf_table,
            html.H6("Sequence Alignment (recent matches)", className="mt-4 mb-2"),
            html.Small(
                f"A sequence is 'aligned' if it matched within the last {lookback} candles of a timeframe.",
                style={"color": "#6b7280", "display": "block", "marginBottom": "0.5rem"},
            ),
            align_table,
        ])

    except Exception as e:
        logger.exception("mtf error: %s", e)
        return html.Div(f"Error: {str(e)[:120]}", style={"color": "#ef4444", "padding": "1rem"})


# ======================================================================
# CALLBACK 20 & 21: WATCHLIST — Save / Display
# ======================================================================

@app.callback(
    Output("wl-status", "children"),
    Output("wl-refresh-trigger", "data"),
    Input("wl-add-btn", "n_clicks"),
    State("wl-label", "value"),
    State("wl-sequences", "value"),
    State("wl-symbol", "value"),
    State("wl-refresh-trigger", "data"),
    prevent_initial_call=True,
)
def save_watchlist_entry(n_clicks, label, sequences_str, symbol, trigger):
    """Save a new entry to the watchlist."""
    if not n_clicks:
        return "", trigger
    if not label or not label.strip():
        return html.Div("Label is required.", style={"color": "#ef4444"}), trigger
    if not sequences_str or not sequences_str.strip():
        return html.Div("Enter at least one sequence.", style={"color": "#ef4444"}), trigger

    seqs = [s.strip() for s in sequences_str.split(",") if s.strip()]
    try:
        add_to_watchlist(label=label, sequences=seqs, symbol=symbol or "")
        msg = html.Div(
            [html.I(className="bi bi-check-circle me-1"), f"Saved '{label}' ({len(seqs)} sequences)"],
            style={"color": "#10b981", "fontWeight": "600"},
        )
        return msg, (trigger or 0) + 1
    except Exception as e:
        return html.Div(f"Error: {e}", style={"color": "#ef4444"}), trigger


@app.callback(
    Output("wl-content", "children"),
    Input("wl-refresh-trigger", "data"),
    Input("tabs", "active_tab"),
)
def display_watchlist(trigger, active_tab):
    """Render the watchlist table whenever the tab is shown or an entry is added."""
    if active_tab != "tab-watchlist":
        return html.Div()

    try:
        entries = list_watchlist()
    except Exception:
        entries = []

    if not entries:
        return html.Div(
            [html.I(className="bi bi-bookmark"), " No saved sequences yet. Add one above!"],
            style={"color": "#6b7280", "padding": "1rem", "textAlign": "center"},
        )

    rows = []
    for e in entries:
        import datetime
        created = datetime.datetime.fromtimestamp(e.get("created_at", 0)).strftime("%Y-%m-%d %H:%M")
        seqs_str = ", ".join(e.get("sequences", []))
        entry_id = e.get("id", 0)
        rows.append(html.Tr([
            html.Td(e.get("label", ""), style={"fontWeight": "700"}),
            html.Td(html.Code(seqs_str, style={"fontSize": "0.8rem"})),
            html.Td(e.get("symbol", "") or "—"),
            html.Td(created, style={"fontSize": "0.8rem", "color": "#6b7280"}),
            html.Td([
                dbc.Button(
                    html.I(className="bi bi-play-circle"),
                    id={"type": "wl-load-btn", "index": entry_id},
                    color="primary", size="sm", className="me-1",
                    title="Load into scanner",
                ),
                dbc.Button(
                    html.I(className="bi bi-trash"),
                    id={"type": "wl-delete-btn", "index": entry_id},
                    color="danger", size="sm", outline=True,
                    title="Delete entry",
                ),
            ], style={"whiteSpace": "nowrap"}),
        ]))

    table = dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Label"), html.Th("Sequences"), html.Th("Symbol"), html.Th("Created"), html.Th("Actions"),
        ])),
         html.Tbody(rows)],
        bordered=True, hover=True, responsive=True, striped=True, size="sm",
        style={"fontSize": "0.9rem"},
    )

    header = html.Div(
        [html.I(className="bi bi-bookmarks me-2"), f"{len(entries)} Saved Sequence{'s' if len(entries) != 1 else ''}"],
        style={
            "padding": "0.75rem 1rem", "backgroundColor": "#fef3c7",
            "borderRadius": "8px", "fontWeight": "600", "color": "#92400e",
            "marginBottom": "0.75rem",
        },
    )

    return html.Div([header, table])


# --- WATCHLIST: Delete entry via pattern-matching callback ---
@app.callback(
    Output("wl-refresh-trigger", "data", allow_duplicate=True),
    Input({"type": "wl-delete-btn", "index": ALL}, "n_clicks"),
    State({"type": "wl-delete-btn", "index": ALL}, "id"),
    State("wl-refresh-trigger", "data"),
    prevent_initial_call=True,
)
def delete_watchlist_entry(n_clicks_list, btn_ids, trigger):
    triggered = callback_context.triggered
    if not triggered or not any(n_clicks_list):
        return dash.no_update

    # Find the first button that changed
    for idx, tc in enumerate(triggered):
        if tc["value"] and tc["value"] > 0:
            if idx < len(btn_ids):
                entry_id = btn_ids[idx]["index"]
                remove_from_watchlist(entry_id)
                return (trigger or 0) + 1

    return dash.no_update


# --- WATCHLIST: Load entry into custom-sequences-input ---
@app.callback(
    Output("custom-sequences-input", "value"),
    Output("wl-status", "children", allow_duplicate=True),
    Input({"type": "wl-load-btn", "index": ALL}, "n_clicks"),
    State({"type": "wl-load-btn", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def load_watchlist_entry(n_clicks_list, btn_ids):
    triggered = callback_context.triggered
    if not triggered or not any(n_clicks_list):
        return dash.no_update, dash.no_update

    # Find which button was clicked
    for idx, tc in enumerate(triggered):
        if tc["value"] and tc["value"] > 0:
            if idx < len(btn_ids):
                entry_id = btn_ids[idx]["index"]
                entries = list_watchlist()
                for e in entries:
                    if e.get("id") == entry_id:
                        update_last_used(entry_id)
                        seqs = "\n".join(e.get("sequences", []))
                        msg = html.Div(
                            [html.I(className="bi bi-check-circle me-1"),
                             f"Loaded '{e.get('label', '')}' into scanner"],
                            style={"color": "#10b981", "fontWeight": "600"},
                        )
                        return seqs, msg
    return dash.no_update, dash.no_update


# =========================================================================
# PHASE 6 CALLBACKS — Alerts, ML Predict, Settings, Live Refresh
# =========================================================================

# --- ALERTS: Add Rule ---
@app.callback(
    Output("alert-add-status", "children"),
    Output("alert-refresh-trigger", "data"),
    Input("alert-add-btn", "n_clicks"),
    State("alert-rule-name", "value"),
    State("alert-sequences", "value"),
    State("alert-symbol", "value"),
    State("alert-webhook", "value"),
    State("alert-refresh-trigger", "data"),
    prevent_initial_call=True,
)
def on_add_alert_rule(n_clicks, name, sequences_str, symbol, webhook, trigger):
    if not n_clicks:
        return "", trigger
    if not name or not name.strip():
        return html.Div("Rule name is required.", style={"color": "#ef4444"}), trigger
    if not sequences_str or not sequences_str.strip():
        return html.Div("Enter at least one sequence.", style={"color": "#ef4444"}), trigger
    seqs = [s.strip() for s in sequences_str.split(",") if s.strip()]
    try:
        add_alert_rule(name=name.strip(), sequences=seqs,
                       symbol=symbol or "", webhook_url=webhook or "")
        msg = html.Div(
            [html.I(className="bi bi-check-circle me-1"),
             f"Alert rule '{name}' created ({len(seqs)} sequences)"],
            style={"color": "#10b981", "fontWeight": "600"},
        )
        return msg, (trigger or 0) + 1
    except Exception as e:
        return html.Div(f"Error: {e}", style={"color": "#ef4444"}), trigger


# --- ALERTS: Display Rules ---
@app.callback(
    Output("alert-rules-content", "children"),
    Input("alert-refresh-trigger", "data"),
    Input("tabs", "active_tab"),
)
def display_alert_rules(trigger, active_tab):
    if active_tab != "tab-alerts":
        return html.Div()
    try:
        rules = list_alert_rules()
    except Exception:
        rules = []
    if not rules:
        return html.Div(
            [html.I(className="bi bi-bell-slash me-1"), " No alert rules yet."],
            style={"color": "#6b7280", "padding": "1rem", "textAlign": "center"},
        )
    rows = []
    for r in rules:
        import datetime as _dt
        created = _dt.datetime.fromtimestamp(r.get("created_at", 0)).strftime("%Y-%m-%d %H:%M")
        seqs_str = ", ".join(r.get("sequences", []))
        rule_id = r.get("id", 0)
        status_badge = html.Span(
            "Active" if r["enabled"] else "Disabled",
            style={
                "backgroundColor": "#10b981" if r["enabled"] else "#9ca3af",
                "color": "white", "padding": "2px 8px", "borderRadius": "4px",
                "fontSize": "0.75rem", "fontWeight": "700",
            },
        )
        rows.append(html.Tr([
            html.Td(r.get("name", ""), style={"fontWeight": "700"}),
            html.Td(html.Code(seqs_str, style={"fontSize": "0.8rem"})),
            html.Td(r.get("symbol", "") or "Any"),
            html.Td(status_badge),
            html.Td(created, style={"fontSize": "0.8rem", "color": "#6b7280"}),
            html.Td(
                dbc.Button(
                    html.I(className="bi bi-trash"),
                    id={"type": "alert-delete-btn", "index": rule_id},
                    color="danger", size="sm", outline=True,
                    title="Delete rule",
                ),
                style={"whiteSpace": "nowrap"},
            ),
        ]))
    table = dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Name"), html.Th("Sequences"), html.Th("Symbol"),
            html.Th("Status"), html.Th("Created"), html.Th(""),
        ])),
         html.Tbody(rows)],
        bordered=True, hover=True, responsive=True, striped=True, size="sm",
    )
    return table


# --- ALERTS: Delete Rule via pattern-matching callback ---
# Disabled due to Dash wildcard restriction causing callback failure.
# @app.callback(
#     Output("alert-refresh-trigger", "data", allow_duplicate=True),
#     Input({"type": "alert-delete-btn", "index": MATCH}, "n_clicks"),
#     State({"type": "alert-delete-btn", "index": MATCH}, "id"),
#     State("alert-refresh-trigger", "data"),
#     prevent_initial_call=True,
# )
# def delete_alert_rule(n_clicks, btn_id, trigger):
#     if not n_clicks:
#         return dash.no_update
#     rule_id = btn_id["index"]
#     remove_alert_rule(rule_id)
#     return (trigger or 0) + 1


# --- ALERTS: Display History ---
@app.callback(
    Output("alert-history-content", "children"),
    Input("alert-refresh-trigger", "data"),
    Input("tabs", "active_tab"),
)
def display_alert_history(trigger, active_tab):
    if active_tab != "tab-alerts":
        return html.Div()
    try:
        history = get_alert_history(limit=30)
    except Exception:
        history = []
    if not history:
        return html.Div(
            [html.I(className="bi bi-inbox me-1"), " No alerts triggered yet."],
            style={"color": "#6b7280", "padding": "1rem", "textAlign": "center"},
        )
    rows = []
    for a in history:
        import datetime as _dt
        ts = _dt.datetime.fromtimestamp(a.get("triggered_at", 0)).strftime("%Y-%m-%d %H:%M:%S")
        sev = a.get("severity", "info")
        sev_color = {"warning": "#f59e0b", "info": "#3b82f6"}.get(sev, "#6b7280")
        rows.append(html.Tr([
            html.Td(html.Span(sev.upper(), style={"color": sev_color, "fontWeight": "700", "fontSize": "0.75rem"})),
            html.Td(a.get("rule_name", ""), style={"fontWeight": "600"}),
            html.Td(html.Code(a.get("sequence", ""), style={"fontSize": "0.8rem"})),
            html.Td(a.get("symbol", "") or "—"),
            html.Td(str(a.get("match_count", 0)), style={"fontWeight": "700"}),
            html.Td(ts, style={"fontSize": "0.8rem", "color": "#6b7280"}),
        ]))
    table = dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Severity"), html.Th("Rule"), html.Th("Sequence"),
            html.Th("Symbol"), html.Th("Matches"), html.Th("Time"),
        ])),
         html.Tbody(rows)],
        bordered=True, hover=True, responsive=True, striped=True, size="sm",
    )
    return table


# --- ALERTS: Badge (unread count in navbar) ---
@app.callback(
    Output("alert-badge", "children"),
    Input("alert-refresh-trigger", "data"),
    Input("tabs", "active_tab"),
)
def update_alert_badge(trigger, active_tab):
    try:
        count = get_unread_count()
    except Exception:
        count = 0
    if count > 0:
        return html.Span(
            [html.I(className="bi bi-bell-fill me-1"),
             dbc.Badge(str(count), color="danger", pill=True, className="ms-1")],
            style={"color": "white", "fontSize": "1rem"},
        )
    return html.Span(
        html.I(className="bi bi-bell", style={"color": "rgba(255,255,255,0.7)", "fontSize": "1rem"}),
    )


# --- ALERTS: Clear History ---
@app.callback(
    Output("alert-clear-status", "children"),
    Output("alert-refresh-trigger", "data", allow_duplicate=True),
    Input("alert-clear-history-btn", "n_clicks"),
    State("alert-refresh-trigger", "data"),
    prevent_initial_call=True,
)
def on_clear_alert_history(n_clicks, trigger):
    if not n_clicks:
        return dash.no_update, dash.no_update
    try:
        removed = clear_alert_history()
        return (
            html.Div(
                [html.I(className="bi bi-check-circle me-1"),
                 f"Cleared {removed} alert(s) from history"],
                style={"color": "#10b981", "fontWeight": "600"},
            ),
            (trigger or 0) + 1,
        )
    except Exception as e:
        return html.Div(f"Error: {e}", style={"color": "#ef4444"}), trigger


# --- ML PREDICTIONS: Train & Predict ---
@app.callback(
    Output("ml-predict-content", "children"),
    Input("ml-train-btn", "n_clicks"),
    State("current-data", "data"),
    State("ml-hold-slider", "value"),
    prevent_initial_call=True,
)
def on_ml_train_predict(n_clicks, data, hold_candles):
    if not n_clicks or not data:
        return html.Div("Load data first.", style={"color": "#6b7280", "padding": "1rem"})

    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        hold = int(hold_candles or 5)

        result = train_sequence_predictor(df, hold_candles=hold)
        if "error" in result:
            return html.Div(result["error"], style={"color": "#ef4444", "padding": "1rem"})

        metrics = result["metrics"]
        predictor = result["model"]

        # Current prediction
        prediction = predictor.predict_next_outcome(df, hold_candles=hold)

        # Metrics cards
        metric_cards = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Accuracy", style={"color": "#6b7280", "fontSize": "0.75rem", "textTransform": "uppercase"}),
                    html.H4(f"{metrics['accuracy']:.1%}", style={"fontWeight": "800", "color": "#6366f1"}),
                ])
            ], style={"borderRadius": "12px", "border": "1px solid #e5e7eb"}), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("ROC AUC", style={"color": "#6b7280", "fontSize": "0.75rem", "textTransform": "uppercase"}),
                    html.H4(f"{metrics['roc_auc']:.3f}", style={"fontWeight": "800", "color": "#3b82f6"}),
                ])
            ], style={"borderRadius": "12px", "border": "1px solid #e5e7eb"}), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Precision", style={"color": "#6b7280", "fontSize": "0.75rem", "textTransform": "uppercase"}),
                    html.H4(f"{metrics['precision']:.1%}", style={"fontWeight": "800", "color": "#10b981"}),
                ])
            ], style={"borderRadius": "12px", "border": "1px solid #e5e7eb"}), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Recall", style={"color": "#6b7280", "fontSize": "0.75rem", "textTransform": "uppercase"}),
                    html.H4(f"{metrics['recall']:.1%}", style={"fontWeight": "800", "color": "#f59e0b"}),
                ])
            ], style={"borderRadius": "12px", "border": "1px solid #e5e7eb"}), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("F1 Score", style={"color": "#6b7280", "fontSize": "0.75rem", "textTransform": "uppercase"}),
                    html.H4(f"{metrics['f1']:.3f}", style={"fontWeight": "800", "color": "#ec4899"}),
                ])
            ], style={"borderRadius": "12px", "border": "1px solid #e5e7eb"}), width=2),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Samples", style={"color": "#6b7280", "fontSize": "0.75rem", "textTransform": "uppercase"}),
                    html.H4(str(result["n_samples"]), style={"fontWeight": "800", "color": "#6b7280"}),
                ])
            ], style={"borderRadius": "12px", "border": "1px solid #e5e7eb"}), width=2),
        ], className="g-3 mb-4")

        # Prediction result
        direction = prediction.get("direction", "unknown")
        confidence = prediction.get("confidence", 0)
        pred_color = "#10b981" if direction == "bullish" else "#ef4444" if direction == "bearish" else "#6b7280"
        pred_icon = "bi-arrow-up-circle" if direction == "bullish" else "bi-arrow-down-circle"

        pred_card = dbc.Card([
            dbc.CardBody([
                html.H5([html.I(className=f"bi {pred_icon} me-2"), "Current Prediction"],
                         style={"fontWeight": "800"}),
                html.H3(
                    f"{direction.upper()} ({confidence:.1%} confidence)",
                    style={"fontWeight": "800", "color": pred_color, "marginTop": "0.5rem"},
                ),
                html.Small(
                    f"Based on {result['n_features']} features, {hold}-candle hold period • "
                    f"{'Calibrated' if metrics.get('calibrated') else 'Uncalibrated'} probabilities",
                    style={"color": "#6b7280"},
                ),
            ])
        ], style={"borderRadius": "12px", "border": f"2px solid {pred_color}", "marginBottom": "1.5rem"})

        # Feature importance
        fi = result.get("feature_importance", [])
        fi_section = html.Div()
        if fi:
            fi_rows = []
            for feat in fi[:10]:
                fi_rows.append(html.Tr([
                    html.Td(feat["feature"], style={"fontWeight": "600"}),
                    html.Td(f"{feat['importance']:.4f}"),
                    html.Td(
                        html.Div(style={
                            "width": f"{feat['importance'] * 400}px",
                            "height": "8px",
                            "backgroundColor": "#6366f1",
                            "borderRadius": "4px",
                        })
                    ),
                ]))
            fi_section = html.Div([
                html.H6("Feature Importance (Top 10)", style={"fontWeight": "700", "marginTop": "1rem"}),
                dbc.Table(
                    [html.Thead(html.Tr([html.Th("Feature"), html.Th("Importance"), html.Th("")])),
                     html.Tbody(fi_rows)],
                    bordered=True, hover=True, size="sm",
                ),
            ])

        return html.Div([metric_cards, pred_card, fi_section])

    except Exception as e:
        logger.exception("ML prediction failed: %s", e)
        return html.Div(f"Error: {e}", style={"color": "#ef4444", "padding": "1rem"})


# --- SETTINGS: Load Saved Preferences into form ---
@app.callback(
    Output("pref-default-symbol", "value"),
    Output("pref-default-period", "value"),
    Output("pref-default-interval", "value"),
    Output("pref-hold-period", "value"),
    Output("pref-live-enabled", "value"),
    Output("pref-live-interval", "value"),
    Output("pref-discovery-max", "value"),
    Input("tabs", "active_tab"),
)
def load_settings_on_tab(active_tab):
    if active_tab != "tab-settings":
        return (dash.no_update,) * 7
    try:
        prefs = load_preferences()
        return (
            prefs.get("default_symbol", ""),
            prefs.get("default_period", "6mo"),
            prefs.get("default_interval", "1d"),
            prefs.get("hold_period", 5),
            ["enabled"] if prefs.get("live_refresh_enabled") else [],
            prefs.get("live_refresh_interval", 60),
            prefs.get("discovery_max_results", 25),
        )
    except Exception:
        return (dash.no_update,) * 7


# --- SETTINGS: Save Preferences ---
@app.callback(
    Output("pref-save-status", "children"),
    Input("pref-save-btn", "n_clicks"),
    State("pref-default-symbol", "value"),
    State("pref-default-period", "value"),
    State("pref-default-interval", "value"),
    State("pref-hold-period", "value"),
    State("pref-live-enabled", "value"),
    State("pref-live-interval", "value"),
    State("pref-discovery-max", "value"),
    prevent_initial_call=True,
)
def on_save_preferences(n_clicks, symbol, period, interval, hold, live_enabled, live_interval_sec, discovery_max):
    if not n_clicks:
        return ""
    try:
        prefs = load_preferences()
        if symbol:
            prefs["default_symbol"] = symbol
        if period:
            prefs["default_period"] = period
        if interval:
            prefs["default_interval"] = interval
        if hold:
            prefs["hold_period"] = int(hold)
        prefs["live_refresh_enabled"] = "enabled" in (live_enabled or [])
        if live_interval_sec:
            prefs["live_refresh_interval"] = int(live_interval_sec)
        if discovery_max:
            prefs["discovery_max_results"] = int(discovery_max)
        save_preferences(prefs)
        return html.Div(
            [html.I(className="bi bi-check-circle me-1"), "Preferences saved!"],
            style={"color": "#10b981", "fontWeight": "600"},
        )
    except Exception as e:
        return html.Div(f"Error: {e}", style={"color": "#ef4444"})


# --- SETTINGS: Reset Preferences ---
@app.callback(
    Output("pref-reset-status", "children"),
    Input("pref-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def on_reset_preferences(n_clicks):
    if not n_clicks:
        return ""
    reset_preferences()
    return html.Div(
        [html.I(className="bi bi-check-circle me-1"), "Preferences reset to defaults."],
        style={"color": "#f59e0b", "fontWeight": "600"},
    )


# --- SETTINGS: Dataset Info ---
@app.callback(
    Output("dataset-info-content", "children"),
    Input("tabs", "active_tab"),
    State("current-data", "data"),
)
def show_dataset_info(active_tab, data):
    if active_tab != "tab-settings":
        return html.Div()
    if not data:
        return html.Div("No data loaded.", style={"color": "#6b7280"})
    try:
        df = pd.DataFrame(data["df"])
        info = dataset_info(df)
        return html.Div([
            html.Div(f"Rows: {info['rows']}", style={"fontWeight": "600"}),
            html.Div(f"Memory: {info['memory_mb']} MB"),
            html.Div(f"Needs downsampling: {'Yes' if info['needs_downsampling'] else 'No'}"),
            html.Div(f"Needs chunking: {'Yes' if info['needs_chunking'] else 'No'}"),
        ], style={"padding": "0.5rem", "color": "#374151"})
    except Exception:
        return html.Div("Could not compute dataset info.", style={"color": "#6b7280"})


# --- LIVE REFRESH: Toggle interval based on preferences ---
@app.callback(
    Output("live-interval", "disabled"),
    Output("live-interval", "interval"),
    Input("pref-save-btn", "n_clicks"),
    State("pref-live-enabled", "value"),
    State("pref-live-interval", "value"),
    prevent_initial_call=True,
)
def toggle_live_interval(n_clicks, live_enabled, live_interval_sec):
    if not n_clicks:
        return dash.no_update, dash.no_update
    enabled = "enabled" in (live_enabled or [])
    interval_ms = int(live_interval_sec or 60) * 1000
    return not enabled, interval_ms


# --- LIVE REFRESH: Auto-fetch on interval tick ---
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Input("live-interval", "n_intervals"),
    State("yf-symbol-input", "value"),
    State("yf-period", "value"),
    State("yf-interval", "value"),
    prevent_initial_call=True,
)
def on_live_refresh(n_intervals, symbol, period, interval):
    """Auto-refresh data from Yahoo Finance using the current sidebar symbol."""
    if not symbol or not symbol.strip():
        from dash.exceptions import PreventUpdate
        raise PreventUpdate
    try:
        df = fetch_yahoo_data(symbol.strip(), period=period or "1d", interval=interval or "1d")
        if df is None or df.empty:
            from dash.exceptions import PreventUpdate
            raise PreventUpdate
        data = {
            "filename": f"live_{symbol.strip()}",
            "upload_id": None,
            "df": df.to_dict("records"),
        }
        return data
    except Exception:
        from dash.exceptions import PreventUpdate
        raise PreventUpdate


if __name__ == "__main__":
    import sys
    try:
        app.run(host="0.0.0.0", port="8050", debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutdown requested.")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
