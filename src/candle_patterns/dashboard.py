from __future__ import annotations


import logging
import dash
import dash_bootstrap_components as dbc
from pathlib import Path

from dash import html, dcc, Input, Output, State, callback_context
from dash.dcc.express import send_data_frame, send_bytes

import plotly.graph_objects as go

import pandas as pd

logger = logging.getLogger(__name__)

from candle_patterns.ingestion import load_csv

from candle_patterns.patterns import (
    find_sequence_occurrences,
    parse_sequence,
    sequence_length,
    discover_color_sequences,
)

from candle_patterns.storage import save_upload

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

app = dash.Dash(
    __name__, 
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts
)

server = app.server


def load_sample_data(trigger_data=None):
    """Load the built-in sample dataset and return the payload + status message."""
    logger.info("[INFO] Loading sample data (trigger=%s)", trigger_data)
    sample_path = Path("data/samples/sample_synthetic.csv")

    if not sample_path.exists():
        msg = html.Div(
            "[ERROR] Sample file not found. Please ensure data/samples/sample_synthetic.csv exists.",
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

        data = {
            "filename": str(sample_path.name),
            "upload_id": upload_id,
            "df": df.to_dict("records"),
        }

        status_html = html.Div(
            f"[OK] Loaded sample: {len(df)} candles",
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
        app.default_sample_data = data
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
                
                # Upload section
                html.Div([
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
                    html.Div(id="upload-status", style={"marginTop": "12px"}),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Date range filter
                html.Div([
                    html.H6([html.I(className="bi bi-calendar-range"), " Date Range Filter"]),
                    dcc.DatePickerRange(
                        id="date-range",
                        display_format="YYYY-MM-DD",
                        start_date_placeholder_text="Start",
                        end_date_placeholder_text="End",
                        style={"width": "100%"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # ==========================================
                # SEQUENCE SCANNER — the main feature
                # ==========================================
                html.Div([
                    html.H6([html.I(className="bi bi-search"), " Sequence Scanner"]),
                    html.Small(
                        "Define colour sequences and scan 200 candles for matches.",
                        style={"color": "#6b7280", "display": "block", "marginBottom": "0.75rem", "fontWeight": "500"}
                    ),
                    
                    # Preset sequences (multi-select dropdown)
                    html.Label("Preset Sequences", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151"}),
                    dcc.Dropdown(
                        id="preset-sequences",
                        options=[{"label": k, "value": v} for k, v in PRESET_SEQUENCES.items()],
                        multi=True,
                        placeholder="Pick common sequences...",
                        style={"marginBottom": "0.75rem"},
                    ),
                    
                    # Custom sequences textarea
                    html.Label("Custom Sequences (one per line)", style={"fontWeight": "700", "fontSize": "0.8rem", "color": "#374151", "marginTop": "0.25rem"}),
                    dcc.Textarea(
                        id="custom-sequences-input",
                        placeholder="5R -> 3G\n2R -> Doji -> 1G\n4G -> 2R",
                        style={
                            "width": "100%", "height": "80px", "borderRadius": "10px",
                            "padding": "0.75rem", "border": "1.5px solid #e5e7eb",
                            "fontSize": "0.85rem", "fontFamily": "monospace",
                        },
                    ),
                    html.Small(
                        "Syntax: NR = N red, NG = N green, Doji, Hammer. Arrow separators: ->",
                        style={"color": "#9ca3af", "display": "block", "marginTop": "4px", "fontSize": "0.7rem"},
                    ),
                    
                    # Scan button
                    dbc.Button(
                        [html.I(className="bi bi-play-fill"), " Scan Sequences"],
                        id="scan-sequences-btn",
                        color="primary",
                        className="w-100 mt-3",
                        style={"fontWeight": "700", "padding": "0.85rem 1.5rem"},
                    ),
                    
                    # Results summary
                    html.Div(id="scan-results-summary", style={"marginTop": "0.75rem"}),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # History section
                html.Div([
                    html.H6([html.I(className="bi bi-clock-history"), " Load from History"]),
                    dcc.Dropdown(
                        id="history-select",
                        placeholder="Select a past upload...",
                        clearable=True,
                        style={"marginTop": "0.5rem"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Maintenance section
                html.Div([
                    html.H6([html.I(className="bi bi-wrench"), " Maintenance"]),
                    dbc.Button(
                        [html.I(className="bi bi-trash"), " Run Cleanup"],
                        id="cleanup-btn",
                        color="danger",
                        size="sm",
                        className="w-100",
                        style={"fontWeight": "700", "padding": "0.65rem 1rem"}
                    ),
                    html.Div(
                        id="cleanup-result",
                        style={"marginTop": "10px", "fontSize": "0.9em", "color": "#6b7280", "fontWeight": "500"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Export section
                html.Div([
                    html.H6([html.I(className="bi bi-download"), " Export Data"]),
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
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Statistics cards
                html.Div(id="stats-cards"),
            ]
        )
    ],
    className="sidebar-card",
)

# Stores to keep the current upload and scan results in-browser
store_current = dcc.Store(id='current-data', data=(app.default_sample_data if app.default_sample_data is not None else None), storage_type='memory')
store_scan = dcc.Store(id='scan-results', data=None, storage_type='memory')

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
                        dcc.Loading(
                            dcc.Graph(
                                id="candle-chart",
                                style={"marginTop": "1.5rem"},
                                config={"responsive": True, "displayModeBar": True, "displaylogo": False}
                            ),
                            type="circle", color="#6366f1"
                        )
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
                    [dcc.Loading(html.Div(id="matches-content", style={"marginTop": "1.5rem"}), type="circle", color="#6366f1")],
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
                    [dcc.Loading(html.Div(id="discovery-content", style={"marginTop": "1.5rem"}), type="circle", color="#6366f1")],
                    fluid=True
                )
            ],
            className="p-4"
        ),
    ],
    id="tabs",
    active_tab="tab-chart",
    className="mt-4"
)

# Flask API endpoint for loading sample data
@server.route('/api/load-sample')
def api_load_sample():
    """API endpoint to load sample data directly."""
    import json
    from flask import jsonify
    from pathlib import Path
    from candle_patterns.detection import detect_patterns as _detect
    from candle_patterns.storage import save_upload
    import pandas as pd
    
    try:
        sample_path = Path("data/samples/sample_synthetic.csv")
        
        if not sample_path.exists():
            return jsonify({"error": "Sample data file not found"}), 404
        
        # Load the sample data
        df = pd.read_csv(sample_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Detect patterns
        patterns = _detect(df)
        
        # Save to storage
        upload_info = save_upload(f"sample_synthetic_automated_{pd.Timestamp.now().isoformat()}", df, patterns)
        
        return jsonify({
            "success": True,
            "message": f"[OK] Loaded sample: {len(patterns)} patterns detected",
            "patterns": len(patterns),
            "rows": len(df),
            "upload_id": upload_info.get('upload_id')
        })
    except Exception as e:
        logger.exception('API load sample failed: %s', e)
        return jsonify({"error": str(e)}), 500

# Main layout
app.layout = dbc.Container(
    [
        navbar,
        store_current,
        store_scan,
        dcc.Location(id='url', refresh=False),  # Track page location
        html.Div(id='page-load-signal', children=1, style={'display': 'none'}),  # Trigger initial render
        dbc.Row(
            [
                dbc.Col(sidebar, width=12, lg=3, className="mb-4 mb-lg-0", style={"paddingRight": "1.5rem"}),
                dbc.Col(main_content, width=12, lg=9, style={"paddingLeft": "0.5rem"}),
            ],
            className="mt-4 g-0",
            style={"gap": "2rem"}
        ),
        pattern_modal
    ],
    fluid=True,
    style={"background": "linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)", "minHeight": "100vh", "paddingBottom": "3rem", "paddingTop": "0"}
)

# =========================================================================
# CALLBACKS
# =========================================================================

# Handle file upload --------------------------------------------------
@app.callback(
    Output("upload-status", "children"),
    Output("current-data", "data", allow_duplicate=True),
    Output("scan-results", "data", allow_duplicate=True),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def on_upload(contents, filename):
    from candle_patterns.storage import save_upload

    if contents is None:
        return "", dash.no_update, dash.no_update

    content_type, content_string = contents.split(",", 1)
    import base64, io

    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.BytesIO(decoded))

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)

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

    return f"Uploaded: {filename} ({len(df)} candles)", data, None  # reset scan


# Handle "Load Sample Data" button ------------------------------------
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Output("upload-status", "children", allow_duplicate=True),
    Output("scan-results", "data", allow_duplicate=True),
    Input("load-sample-btn", "n_clicks"),
    prevent_initial_call=True,
)
def on_load_sample_click(n_clicks):
    if n_clicks and n_clicks > 0:
        logger.info("Load Sample Data button clicked")
        data, status = load_sample_data()
        if data:
            logger.info("Sample data loaded: %d candles", len(data['df']))
            return data, status, None  # reset scan
        return None, status, None
    return None, "", None


# Scan sequences  -------------------------------------------------------
@app.callback(
    Output("scan-results", "data", allow_duplicate=True),
    Output("scan-results-summary", "children"),
    Input("scan-sequences-btn", "n_clicks"),
    State("preset-sequences", "value"),
    State("custom-sequences-input", "value"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def scan_sequences(n_clicks, presets, custom_text, data):
    """Run all selected sequences against the loaded candle data."""
    if not data:
        return None, html.Div("No data loaded. Upload a CSV or load sample data first.",
                              style={"color": "#ef4444", "fontWeight": "600"})

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
        return None, html.Div("No sequences defined. Pick presets or type custom ones.",
                              style={"color": "#f59e0b", "fontWeight": "600"})

    df = pd.DataFrame(data["df"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    results = []
    total_matches = 0
    for seq_str in seqs:
        try:
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
            results.append({"seq_str": seq_str, "length": seq_len, "matches": matches})
            total_matches += len(matches)
        except Exception as e:
            results.append({"seq_str": seq_str, "length": 0, "matches": [], "error": str(e)})

    summary = html.Div(
        f"Scanned {len(seqs)} sequence(s) — {total_matches} total matches found",
        style={
            "color": "#059669" if total_matches else "#f59e0b",
            "fontWeight": "600", "padding": "10px",
            "backgroundColor": "#ecfdf5" if total_matches else "#fffbeb",
            "borderRadius": "8px", "fontSize": "0.85rem",
        },
    )
    return results, summary


# Update chart + matches table when data or scan-results change --------
@app.callback(
    Output("candle-chart", "figure"),
    Output("matches-content", "children"),
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
        )
        empty = html.Div(
            [html.I(className="bi bi-inbox", style={"fontSize": "2rem", "color": "#c7d2fe"}),
             html.P("No data loaded", style={"marginTop": "0.5rem", "color": "#9ca3af", "fontWeight": "600"})],
            style={"padding": "3rem", "textAlign": "center"},
        )
        return fig, empty

    # ---- process data ----
    try:
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        if start_date:
            df = df[df["timestamp"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["timestamp"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]

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

        fig.update_layout(
            title=dict(text=title_text, font=dict(size=16, color='#1f2937')),
            template='plotly_white', height=550, hovermode='x unified',
            xaxis=dict(rangeslider=dict(visible=False)),
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
                    body = dbc.Table(
                        [html.Thead(html.Tr([html.Th("#"), html.Th("Candle Range"), html.Th("Start"), html.Th("End")])),
                         html.Tbody(rows)],
                        bordered=True, hover=True, responsive=True, striped=True, size="sm",
                        style={"fontSize": "0.85rem"},
                    )

                card = dbc.Card([
                    dbc.CardHeader([
                        html.Span(
                            "\u25A0 ",
                            style={"color": color, "fontSize": "1rem"},
                        ),
                        html.Strong(seq_str, style={"fontFamily": "monospace"}),
                        badge,
                        html.Span(f"  ({res.get('length', '?')} candles)", style={"color": "#9ca3af", "fontSize": "0.8rem", "marginLeft": "0.5rem"}),
                    ]),
                    dbc.CardBody(body),
                ], className="mb-3")

                cards.append(card)

            matches_div = html.Div(cards)

        return fig, matches_div

    except Exception as e:
        logger.exception("[CALLBACK ERROR] update_chart: %s", e)
        err_fig = go.Figure()
        err_fig.add_annotation(text=f"ERROR: {str(e)[:80]}", xref='paper', yref='paper',
                               x=0.5, y=0.5, showarrow=False, font=dict(size=14, color='#ef4444'))
        err_fig.update_layout(height=400, template='plotly_white')
        err_div = html.Div(f"Error: {str(e)[:100]}", style={"color": "#ef4444", "padding": "1rem"})
        return err_fig, err_div


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
            rows.append(html.Tr([
                html.Td(str(i + 1), style={"color": "#9ca3af", "width": "40px"}),
                html.Td(
                    html.Code(d["sequence"], style={"fontSize": "0.85rem"}),
                ),
                html.Td(str(d["length"])),
                html.Td(str(d["count"]), style={"fontWeight": "700"}),
                html.Td(f"{d['support']:.4f}"),
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
            [html.Thead(html.Tr([html.Th("#"), html.Th("Sequence"), html.Th("Length"), html.Th("Count"), html.Th("Support")])),
             html.Tbody(rows)],
            bordered=True, hover=True, responsive=True, striped=True, size="sm",
            style={"fontSize": "0.9rem"},
        )

        tip = html.Small(
            "Tip: Copy a discovered sequence into the Custom Sequences box and click Scan to see matches on the chart.",
            style={"color": "#9ca3af", "display": "block", "marginTop": "0.75rem"},
        )

        return html.Div([header, table, tip])

    except Exception as e:
        logger.exception("auto_discover error: %s", e)
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


# Run cleanup  --------------------------------------------------------
@app.callback(
    Output("cleanup-result", "children", allow_duplicate=True),
    Input("cleanup-btn", "n_clicks"),
    prevent_initial_call=True,
)
def run_cleanup(n):
    from candle_patterns.storage import cleanup_old_uploads
    removed = cleanup_old_uploads(retention_days=30)
    return f"Removed {removed} old uploads/detections"


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
    Input("export-detections-btn", "n_clicks"),
    Input("export-aggregated-btn", "n_clicks"),
    Input("export-chart-btn", "n_clicks"),
    State("scan-results", "data"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def export_data(n_matches, n_discovery, n_chart, scan_results, data):
    """Export matches CSV, discovery CSV, or chart PNG."""
    if not data:
        return dash.no_update
    triggered = callback_context.triggered_id

    if triggered == "export-detections-btn" and scan_results:
        rows = []
        for res in scan_results:
            for m in res.get("matches", []):
                rows.append({"sequence": res["seq_str"], **m})
        if rows:
            return send_data_frame(pd.DataFrame(rows).to_csv, "sequence_matches.csv", index=False)

    elif triggered == "export-aggregated-btn":
        df = pd.DataFrame(data["df"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        discovered = discover_color_sequences(df, min_len=3, max_len=8, top_k=25)
        if discovered:
            return send_data_frame(pd.DataFrame(discovered).to_csv, "discovered_sequences.csv", index=False)

    elif triggered == "export-chart-btn":
        df = pd.DataFrame(data['df'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'],
                                              high=df['high'], low=df['low'], close=df['close'])])
        try:
            img_bytes = fig.to_image(format='png', width=1200, height=600, scale=2)
            return send_bytes(lambda: img_bytes, "chart.png")
        except Exception as e:
            logger.exception('export chart failed: %s', e)
            return dash.no_update

    return dash.no_update


# Load from history  ---------------------------------------------------
@app.callback(
    Output("current-data", "data", allow_duplicate=True),
    Output("upload-status", "children", allow_duplicate=True),
    Output("scan-results", "data", allow_duplicate=True),
    Input("history-select", "value"),
    prevent_initial_call=True,
)
def load_from_history(upload_id):
    if not upload_id:
        return None, "", None
    from pathlib import Path
    from candle_patterns.storage import get_upload

    rec = get_upload(upload_id)
    if not rec:
        return None, "", None

    df = pd.read_csv(rec["filepath"]) if rec.get("filepath") else pd.DataFrame()
    data = {
        "filename": rec.get("filename"),
        "upload_id": rec.get("id"),
        "df": df.to_dict("records"),
    }
    return data, f"Loaded: {rec.get('filename')}", None  # reset scan


# ======================================================================

if __name__ == "__main__":
    import sys
    try:
        app.run(host="0.0.0.0", port=8050, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutdown requested.")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
