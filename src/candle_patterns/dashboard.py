from __future__ import annotations


import logging
import dash
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output, State, callback_context
from dash.dcc.express import send_data_frame, send_bytes

import plotly.graph_objects as go

import pandas as pd

logger = logging.getLogger(__name__)

from candle_patterns.ingestion import load_csv

from candle_patterns.detection import detect_patterns

from candle_patterns.reporting import summarize_detections

from candle_patterns.opp_miner import top_patterns_across_lengths

# Modern professional stylesheet with custom CSS
external_stylesheets = [dbc.themes.BOOTSTRAP]
external_scripts = ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js']

app = dash.Dash(
    __name__, 
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts
)

server = app.server

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
    content: "📊";
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
                                "AI-Powered Candlestick Pattern Detection & Analysis",
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
                html.H5("⚙️ Configuration", className="card-title"),
                
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
                        [html.I(className="bi bi-star-fill"), " Load Sample Data"],
                        id="load-sample-btn",
                        color="success",
                        className="w-100 mb-3",
                        style={"fontWeight": "700", "padding": "0.85rem 1.5rem", "fontSize": "0.95rem", "background": "linear-gradient(135deg, #10b981 0%, #14b8a6 100%)"}
                    ),
                    html.Small(
                        "Load 200 candlesticks with 21 patterns",
                        style={"marginTop": "8px", "color": "#6b7280", "display": "block", "fontWeight": "500"}
                    ),
                    html.Div(id="upload-status", style={"marginTop": "12px"}),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Filters section
                html.Div([
                    html.H6("📅 Date Range Filter"),
                    dcc.DatePickerRange(
                        id="date-range",
                        display_format="YYYY-MM-DD",
                        start_date_placeholder_text="Start",
                        end_date_placeholder_text="End",
                        style={"width": "100%"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Patterns section
                html.Div([
                    html.H6("🎯 Pattern Filters"),
                    dcc.Checklist(
                        id="pattern-checklist",
                        options=[],
                        value=[],
                        inline=False,
                        style={"marginTop": "0.8rem"}
                    ),
                    html.Small(
                        "Select patterns to display",
                        style={"fontSize": "0.85em", "color": "#6b7280", "fontWeight": "500"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # History section
                html.Div([
                    html.H6("📜 Load from History"),
                    dcc.Dropdown(
                        id="history-select",
                        placeholder="Select a past upload...",
                        clearable=True,
                        style={"marginTop": "0.5rem"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Custom sequence section
                html.Div([
                    html.H6("🔗 Custom Sequence"),
                    dcc.Input(
                        id="custom-seq-input",
                        placeholder="e.g. 3R -> Doji -> G",
                        style={"width": "100%", "borderRadius": "10px", "padding": "0.75rem 1rem", "border": "1.5px solid #e5e7eb"}
                    ),
                    dbc.Button(
                        "▶ Run Sequence",
                        id="run-custom-seq-btn",
                        color="secondary",
                        size="sm",
                        className="mt-3 w-100",
                        style={"fontWeight": "700", "padding": "0.65rem 1rem"}
                    ),
                ], style={"marginBottom": "1.5rem"}),
                
                html.Hr(className="hr-style"),
                
                # Maintenance section
                html.Div([
                    html.H6("🧹 Maintenance"),
                    dbc.Button(
                        "🗑️ Run Cleanup",
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
                    html.H6("💾 Export Data"),
                    dbc.Button(
                        "📊 Detections",
                        id="export-detections-btn",
                        color="info",
                        size="sm",
                        className="w-100 mb-2",
                        style={"fontWeight": "700", "padding": "0.65rem 1rem"}
                    ),
                    dbc.Button(
                        "📈 Aggregated",
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

# Stores to keep the current upload and detections in-browser
store_current = dcc.Store(id='current-data', storage_type='session')

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
                    "✕ Close",
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
            label=[html.I(className="bi bi-graph-up"), " Candlestick Chart"],
            tab_id="tab-chart",
            children=[
                dbc.Container(
                    [
                        dcc.Graph(
                            id="candle-chart",
                            style={"marginTop": "1.5rem"},
                            config={"responsive": True, "displayModeBar": True, "displaylogo": False}
                        )
                    ],
                    fluid=True,
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label=[html.I(className="bi bi-search"), " Individual Patterns"],
            tab_id="tab-patterns",
            children=[
                dbc.Container(
                    [html.Div(id="pattern-table", style={"marginTop": "1.5rem"})],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label=[html.I(className="bi bi-bar-chart"), " Aggregated Summary"],
            tab_id="tab-agg",
            children=[
                dbc.Container(
                    [html.Div(id="aggregated-table", style={"marginTop": "1.5rem"})],
                    fluid=True
                )
            ],
            className="p-4"
        ),
        dbc.Tab(
            label=[html.I(className="bi bi-diagram-3"), " OPP Patterns"],
            tab_id="tab-opp",
            children=[
                dbc.Container(
                    [html.Div(id="opp-table", style={"marginTop": "1.5rem"})],
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

# Main layout
app.layout = dbc.Container(
    [
        navbar,
        store_current,
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

# Keep existing callbacks; they target preserved IDs like 'upload-data','candle-chart','pattern-table' etc.


@app.callback(
    Output("upload-status", "children"),
    Output("current-data", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def on_upload(contents, filename):

    from candle_patterns.storage import save_upload

    if contents is None:
        return "", None

    content_type, content_string = contents.split(",", 1)
    import base64
    import io

    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.BytesIO(decoded))

    try:
        df = load_csv(filename)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as e:
        logger.debug("load_csv fallback parsing for %s: %s", filename, e)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)

    patterns = detect_patterns(df)

    # persist upload and detections
    try:
        upload_id = save_upload(filename, df, patterns)
    except Exception as e:
        logger.exception("save_upload failed: %s", e)
        upload_id = None

    # prepare the data to store in the session
    data = {
        "filename": filename,
        "upload_id": upload_id,
        "df": df.to_dict("records"),
        "patterns": patterns,
    }

    return f"Uploaded: {filename}", data


# new callback: apply filters and update chart/tables whenever current-data, pattern toggles or date range changes
@app.callback(
    Output("candle-chart", "figure"),
    Output("pattern-table", "children"),
    Output("aggregated-table", "children"),
    Output("opp-table", "children"),
    Output("pattern-checklist", "options"),
    Output("pattern-checklist", "value"),
    Input("current-data", "data"),
    Input("pattern-checklist", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def apply_filters(data, selected_patterns, start_date, end_date):
    # If no data is present, display empty-state placeholders so the UI structure is visible
    if not data:
        # Professional empty state
        fig = go.Figure()
        fig.add_annotation(
            text="📊 No data loaded yet",
            xref='paper', yref='paper',
            x=0.5, y=0.6,
            showarrow=False,
            font=dict(size=24, color='#667eea', family="Arial Black")
        )
        fig.add_annotation(
            text="Upload CSV or click 'Load Sample Data' in the sidebar to begin",
            xref='paper', yref='paper',
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#6c757d')
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template='plotly_white',
            margin=dict(l=0, r=0, t=0, b=0),
            height=500,
            bgcolor='rgba(255,255,255,0.5)'
        )

        placeholder_instructions = html.Div([
            html.Div(
                [
                    html.H5("🚀 Getting Started", style={"color": "#667eea", "fontWeight": "700", "marginBottom": "1rem"}),
                    html.Ol([
                        html.Li("Upload a CSV with columns: timestamp, open, high, low, close"),
                        html.Li("Or click 'Load Sample Data' to use demo data"),
                        html.Li("View detected patterns in the Chart tab"),
                        html.Li("Filter by date range or pattern type"),
                        html.Li("Export aggregated data as CSV"),
                    ], style={"color": "#495057", "lineHeight": "1.8"}),
                ],
                className="empty-state"
            )
        ], style={"padding": "1rem"})

        agg_placeholder = html.Div(
            [html.H5("📊 Aggregated Summary", style={"color": "#667eea"}), html.P("Data will appear here once you load a file", style={"color": "#6c757d"})],
            className="empty-state"
        )
        opp_placeholder = html.Div(
            [html.H5("🎯 Top OPP Patterns", style={"color": "#667eea"}), html.P("Data will appear here once you load a file", style={"color": "#6c757d"})],
            className="empty-state"
        )

        return fig, placeholder_instructions, agg_placeholder, opp_placeholder, [], []

    df = pd.DataFrame(data["df"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    patterns = data.get("patterns", [])

    # determine available pattern names
    names = sorted({p["pattern"] for p in patterns})
    options = [{"label": n, "value": n} for n in names]
    if selected_patterns is None or not selected_patterns:
        selected = names.copy()  # default: show all
    else:
        selected = selected_patterns

    # filter by date range
    if start_date:
        df = df[df["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["timestamp"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]

    # build figure with professional styling
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="OHLC",
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    )])

    filtered_patterns = [p for p in patterns if p["pattern"] in selected]

    # Add pattern markers with better styling
    for p in filtered_patterns:
        try:
            high_series = df.loc[df["timestamp"]==p["timestamp"], "high"]
            if isinstance(high_series, pd.Series) and len(high_series) > 0:
                high_value = float(high_series.iloc[0])
                fig.add_trace(go.Scatter(
                    x=[p["timestamp"]],
                    y=[high_value * 1.02],  # Slightly above the candle
                    mode='markers+text',
                    text=[p["pattern"]],
                    textposition="top center",
                    name=p["pattern"],
                    marker=dict(
                        size=12,
                        color='#667eea',
                        symbol='diamond',
                        opacity=0.8,
                        line=dict(color='white', width=2)
                    ),
                    hovertemplate='<b>%{text}</b><br>Price: $%{y:.2f}<extra></extra>',
                    showlegend=False
                ))
        except Exception:
            continue

    # Enhance figure layout
    fig.update_layout(
        title=dict(
            text=f"<b>📈 Candlestick Analysis</b> | {len(filtered_patterns)} patterns detected",
            font=dict(size=18, color='#667eea')
        ),
        template='plotly_white',
        height=600,
        hovermode='x unified',
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(
            rangeslider=dict(visible=False),
            title="Timestamp",
            titlefont=dict(color='#6c757d')
        ),
        yaxis=dict(
            title="Price (USD)",
            titlefont=dict(color='#6c757d')
        )
    )

    # occurrence list with better styling
    list_items = [html.Li(
        f"🎯 {p['timestamp']}: <strong>{p['pattern']}</strong>",
        style={"marginBottom": "0.5rem", "color": "#495057"}
    ) for p in filtered_patterns]

    list_section = dbc.Card(
        dbc.CardBody([
            html.H5("🔍 Detected Patterns", style={"color": "#667eea", "fontWeight": "700", "marginBottom": "1.5rem"}),
            html.Ol(list_items) if list_items else html.P("No patterns match the current filters", style={"color": "#6c757d"})
        ]),
        className="mt-3"
    ) if list_items else html.Div()

    # aggregated
    summary = summarize_detections(pd.DataFrame(data["df"]), patterns)
    if summary:
        # compute sparkline series per pattern
        from candle_patterns.reporting import pattern_sparkline_series

        spark_map = pattern_sparkline_series(pd.DataFrame(data["df"]), patterns, horizon=6)

        rows = [html.Tr([
            html.Th("Pattern", style={"width": "15%"}),
            html.Th("Count", style={"width": "10%"}),
            html.Th("Support", style={"width": "12%"}),
            html.Th("Avg Return", style={"width": "15%"}),
            html.Th("Win Rate", style={"width": "15%"}),
            html.Th("Trend", style={"width": "33%"})
        ])]
        for r in summary:
            pname = r["pattern"]
            series = spark_map.get(pname, [])
            # build mini sparkline
            mini_fig = go.Figure(data=[go.Scatter(
                x=list(range(len(series))),
                y=series,
                mode="lines",
                line=dict(width=2, color='#667eea'),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                hoverinfo='y'
            )])
            mini_fig.update_layout(
                margin=dict(l=0, r=0, t=2, b=0),
                height=60,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                hovermode='closest'
            )

            # info icon with native tooltip (title)
            PATTERN_EXPLANATIONS = {
                "doji": "Small body; open and close are near. Indicates indecision.",
                "hammer": "Small body with long lower wick; potential bullish reversal.",
                "bullish_engulfing": "A bullish candle that fully engulfs the prior bearish candle.",
                "morning_star": "Three-candle bullish reversal pattern.",
            }
            expl = PATTERN_EXPLANATIONS.get(pname, "Candlestick pattern")
            info_icon = html.Span("ℹ️", title=expl, className="info-icon")

            rows.append(
                html.Tr([
                    html.Td([html.Strong(pname), " ", info_icon]),
                    html.Td(str(r["count"])),
                    html.Td(f"{r['support']:.3f}"),
                    html.Td(f"{r['avg_return']:.4f}", style={"color": "#10b981" if r['avg_return'] > 0 else "#ef4444", "fontWeight": "600"}),
                    html.Td(f"{r['win_rate']:.2%}", style={"color": "#10b981" if r['win_rate'] > 0.5 else "#ef4444"}),
                    html.Td(dcc.Graph(figure=mini_fig, config={"displayModeBar": False}, style={"height": "60px"})),
                ])
            )

        agg_table = dbc.Card(
            dbc.CardBody([
                html.H5("📊 Aggregated Pattern Summary", style={"color": "#667eea", "fontWeight": "700", "marginBottom": "1.5rem"}),
                html.Table(rows)
            ]),
            className="mt-3"
        )
    else:
        agg_table = html.Div("No aggregated data available", className="empty-state")

    # OPP
    top_opp = top_patterns_across_lengths(pd.DataFrame(data["df"]), min_len=3, max_len=6, min_support=0.02, top_k=5)
    if top_opp:
        rows = [html.Tr([
            html.Th("Length"),
            html.Th("Pattern"),
            html.Th("Count"),
            html.Th("Support")
        ])]
        rows.extend([
            html.Tr([
                html.Td(str(t['length'])),
                html.Td(str(t['pattern'])),
                html.Td(str(t['count'])),
                html.Td(f"{t['support']:.3f}")
            ]) for t in top_opp
        ])
        opp_table = dbc.Card(
            dbc.CardBody([
                html.H5("🎯 Top OPP Patterns", style={"color": "#667eea", "fontWeight": "700", "marginBottom": "1.5rem"}),
                html.Table(rows)
            ]),
            className="mt-3"
        )
    else:
        opp_table = html.Div("No frequent OPP patterns found", className="empty-state")

    return fig, list_section, agg_table, opp_table, options, selected


@app.callback(
    Output("history-select", "options"),
    Input("upload-status", "children"),
)
def refresh_history(_):
    """Refresh the history dropdown options whenever an upload occurs."""
    from candle_patterns.storage import list_uploads

    rows = list_uploads(limit=200)
    opts = [{"label": f"{r['stored_at']} - {r['filename']}", "value": r["id"]} for r in rows]
    return opts


@app.callback(
    Output("cleanup-result", "children"),
    Input("cleanup-btn", "n_clicks"),
    prevent_initial_call=True,
)
def run_cleanup(n):
    """Run retention cleanup on-demand."""
    from candle_patterns.storage import cleanup_old_uploads

    removed = cleanup_old_uploads(retention_days=30)
    return f"Removed {removed} old uploads/detections"


@app.callback(
    Output("current-data", "data"),
    Output("cleanup-result", "children"),
    Input("run-custom-seq-btn", "n_clicks"),
    State("custom-seq-input", "value"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def run_custom_sequence(n, seq_str, data):
    """Run a custom sequence query and append occurrences to patterns list (best-effort)."""
    if not data or not seq_str:
        return data, "No sequence provided"
    from .patterns import find_sequence_occurrences

    df = pd.DataFrame(data["df"])
    try:
        occ = find_sequence_occurrences(df, seq_str)
    except Exception as e:
        return data, f"Sequence parse error: {e}"

    # append occurrences as pattern name 'Custom: <seq>'
    for i in occ:
        data.setdefault("patterns", []).append({"index": int(i), "timestamp": str(df.iloc[int(i)]["timestamp"]), "pattern": f"Custom: {seq_str}"})

    return data, f"Found {len(occ)} occurrences of custom sequence"


@app.callback(
    Output("pattern-modal", "is_open"),
    Output("pattern-modal-body", "children"),
    Input("candle-chart", "clickData"),
    Input("modal-close", "n_clicks"),
    State("pattern-modal", "is_open"),
)
def show_pattern_detail(clickData, nclose, is_open):
    """Open modal and show details when a pattern marker is clicked."""
    ctx = callback_context
    if not ctx.triggered:
        return False, ""
    trig = ctx.triggered[0]["prop_id"].split(".")[0]
    if trig == "modal-close":
        return False, ""
    if clickData and "points" in clickData:
        pt = clickData["points"][0]
        txt = pt.get("text") or pt.get("data", {}).get("name") or ""
        x = pt.get("x")
        # Build context mini-chart +/- 5 candles around clicked timestamp
        try:
            from datetime import timedelta
            df_all = None
            # get current-data from server-side via storage (best-effort)
            # we will parse out a small window
            cid = callback_context.triggered[0]['value'] if callback_context and callback_context.triggered else None
        except Exception:
            df_all = None
        body_items: list = [html.P(f"Pattern: {txt}"), html.P(f"Timestamp: {x}"), html.P("Click Export to download detections CSV for details.")]
        try:
            # Attempt to create a mini-chart using the global data if accessible via server memory
            data = callback_context.states.get('current-data.data') if callback_context and getattr(callback_context, 'states', None) else None
            if not data:
                # fallback: try loading last upload from storage
                from candle_patterns.storage import list_uploads, get_upload
                rows = list_uploads(limit=1)
                if rows:
                    rec = get_upload(rows[0]['id'])
                    if rec and 'filepath' in rec:
                        import pandas as _pd
                        df_all = _pd.read_csv(rec['filepath'])
            if data and df_all is None:
                import pandas as _pd
                df_all = _pd.DataFrame(data.get('df', []))

            if df_all is not None and len(df_all):
                df_all['timestamp'] = pd.to_datetime(df_all['timestamp'], utc=True)
                # find nearest index by timestamp
                ts = pd.to_datetime(x)
                idx = df_all.index[(df_all['timestamp'] - ts).abs().argsort()[:1]][0]
                start = max(0, idx - 5)
                end = min(len(df_all)-1, idx + 5)
                window = df_all.iloc[start:end+1]
                mini_fig = go.Figure(data=[go.Candlestick(x=window['timestamp'], open=window['open'], high=window['high'], low=window['low'], close=window['close'])])
                mini_fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=220)
                body_items.append(dcc.Graph(figure=mini_fig, config={'displayModeBar': False}))
        except Exception as e:
            logger.debug('mini-chart build error: %s', e)
        body = html.Div(body_items)
        return True, body
    return False, ""


@app.callback(
    Output("stats-cards", "children"),
    Input("upload-status", "children"),
    Input("history-select", "value"),
)
def update_stats(_, __):
    """Show simple statistics in small cards."""
    from candle_patterns.storage import list_uploads

    rows = list_uploads(limit=100)
    total_uploads = len(rows)
    last_upload = rows[0] if rows else None
    last_upload_label = f"{last_upload['stored_at'].split(' ')[0]} - {last_upload['filename']}" if last_upload else "-"

    card_deck = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6("📁 Total Uploads", style={"color": "#6c757d", "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "1px", "fontWeight": "600", "marginBottom": "0.5rem"}),
                        html.H4(str(total_uploads), style={"color": "#667eea", "fontWeight": "700"})
                    ]),
                    className="stat-card"
                ),
                width=6, lg=6
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6("⏰ Last Upload", style={"color": "#6c757d", "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "1px", "fontWeight": "600", "marginBottom": "0.5rem"}),
                        html.P(last_upload_label, style={"color": "#495057", "fontSize": "0.85rem", "margin": "0"})
                    ]),
                    className="stat-card"
                ),
                width=6, lg=6
            ),
        ],
        className="g-2 mt-3"
    )
    return card_deck


@app.callback(
    Output("download-asset", "data"),
    Input("export-detections-btn", "n_clicks"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def export_detections(n, data):
    if not data:
        return dash.no_update
    df = pd.DataFrame(data.get("patterns", []))
    return send_data_frame(df.to_csv, f"detections_{data.get('filename','upload')}.csv", index=False)


@app.callback(
    Output("download-asset", "data"),
    Input("export-aggregated-btn", "n_clicks"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def export_aggregated(n, data):
    if not data:
        return dash.no_update
    summary = summarize_detections(pd.DataFrame(data["df"]), data.get("patterns", []))
    df = pd.DataFrame(summary)
    return send_data_frame(df.to_csv, f"aggregated_{data.get('filename','upload')}.csv", index=False)


@app.callback(
    Output("download-asset", "data"),
    Input("export-chart-btn", "n_clicks"),
    State("current-data", "data"),
    prevent_initial_call=True,
)
def export_chart(n, data):
    """Generate a PNG of the current chart and return as download."""
    if not data:
        return dash.no_update
    import plotly.io as pio
    df = pd.DataFrame(data['df'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    # server-side image export using kaleido
    try:
        img_bytes = fig.to_image(format='png', width=1200, height=600, scale=2)
        return send_bytes(lambda: img_bytes, f"chart_{data.get('filename','upload')}.png")
    except Exception as e:
        logger.exception('export chart failed: %s', e)
        return dash.no_update


@app.callback(
    Output("current-data", "data"),
    Output("upload-status", "children"),
    Input("load-sample-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_sample_data(n_clicks):
    """Load sample data when button is clicked."""
    if n_clicks is None or n_clicks == 0:
        return None, ""
    
    logger.info(f"Load sample button clicked (n_clicks={n_clicks})")
    from pathlib import Path
    from candle_patterns.storage import save_upload

    sample_path = Path("data/samples/sample_synthetic.csv")
    
    if not sample_path.exists():
        logger.info("Generating synthetic sample data...")
        import numpy as np
        import pandas as _pd

        dates = pd.date_range(end=pd.Timestamp.now('UTC'), periods=200, freq='1h')
        price = 20000 + np.cumsum(np.random.randn(len(dates)) * 50)
        open_p = price + np.random.randn(len(dates)) * 5
        close_p = price + np.random.randn(len(dates)) * 5
        high_p = np.maximum(open_p, close_p) + np.abs(np.random.randn(len(dates)) * 10)
        low_p = np.minimum(open_p, close_p) - np.abs(np.random.randn(len(dates)) * 10)
        sdf = _pd.DataFrame({
            "timestamp": dates.astype(str),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p
        })
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sdf.to_csv(sample_path, index=False)
        logger.info(f"Generated synthetic sample to {sample_path}")

    df = pd.read_csv(sample_path)
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Only localize if it's not already timezone-aware
        if df["timestamp"].dt.tz is None:
            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    
    logger.info(f"Detecting patterns in sample data...")
    patterns = detect_patterns(df)
    logger.info(f"Detected {len(patterns)} patterns")
    
    try:
        uid = save_upload(sample_path.name, df, patterns)
        logger.info(f"Saved sample to DB with upload_id: {uid}")
    except Exception as e:
        logger.exception(f"Failed to save sample: {e}")
        uid = None

    data = {
        "filename": sample_path.name,
        "upload_id": uid,
        "df": df.to_dict("records"),
        "patterns": patterns
    }
    msg = f"✓ Loaded sample: {len(patterns)} patterns detected"
    logger.info(msg)
    return data, msg


@app.callback(
    Output("current-data", "data"),
    Output("upload-status", "children"),
    Input("history-select", "value"),
    prevent_initial_call=True,
)
def load_from_history(upload_id):
    """Load data from history when a past upload is selected."""
    if not upload_id:
        logger.debug("No upload_id selected")
        return None, ""
    
    logger.info(f"Loading from history: upload_id={upload_id}")
    from pathlib import Path
    from candle_patterns.storage import get_upload

    rec = get_upload(upload_id)
    if not rec:
        logger.warning(f"No record found for upload_id: {upload_id}")
        return None, ""
    
    df = pd.read_csv(rec["filepath"]) if rec.get("filepath") else pd.DataFrame()
    patterns = []
    detections_path = rec.get("detections_path")
    if detections_path and isinstance(detections_path, str) and Path(detections_path).exists():
        patterns = pd.read_csv(detections_path).to_dict("records")
    
    data = {
        "filename": rec.get("filename"),
        "upload_id": rec.get("id"),
        "df": df.to_dict("records"),
        "patterns": patterns
    }
    msg = f"Loaded: {rec.get('filename')}"
    logger.info(msg)
    return data, msg


if __name__ == "__main__":

    # Bind to all interfaces so the server is reachable from host and container scenarios
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
