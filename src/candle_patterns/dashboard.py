from __future__ import annotations


import dash
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output, State

import plotly.graph_objects as go

import pandas as pd

from candle_patterns.ingestion import load_csv

from candle_patterns.detection import detect_patterns

from candle_patterns.reporting import summarize_detections

from candle_patterns.opp_miner import top_patterns_across_lengths

# Use Bootstrap theme for a more professional UI
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# Top navbar
navbar = dbc.NavbarSimple(
    brand="Candle Patterns",
    brand_href="#",
    color="dark",
    dark=True,
    children=[dbc.Button("Upload CSV", id="upload-button-navbar", color="primary", className="ms-2")],
)

sidebar = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Controls", className="card-title"),
                dcc.Upload(id="upload-data", children=dbc.Button("Select CSV", color="secondary", className="mb-2")),
                dbc.Button("Load sample data", id="load-sample-btn", color="primary", className="ms-2 mb-2"),
                html.Div(html.Small("Tip: click 'Load sample data' to populate the dashboard with a curated BTC-like sample for demo."), style={"marginTop": "6px", "color": "#555"}),
                html.Div(id="upload-status", style={"marginTop": "8px"}),
                html.Hr(),
                html.H6("Filters"),
                dcc.DatePickerRange(id="date-range", display_format="YYYY-MM-DD", start_date_placeholder_text="Start", end_date_placeholder_text="End"),
                html.Br(),
                html.Br(),
                html.H6("Patterns"),
                dcc.Checklist(id="pattern-checklist", options=[], value=[], inline=False),
                html.Div("(toggle patterns to display)", style={"fontSize": "0.85em", "color": "#666"}),
                html.Hr(),
                html.H6("History"),
                dcc.Dropdown(id="history-select", placeholder="Load past upload", clearable=True),
                html.Br(),
                html.H6("Custom sequence"),
                dcc.Input(id="custom-seq-input", placeholder="e.g. 3R -> Doji -> G", style={"width": "100%"}),
                dbc.Button("Run", id="run-custom-seq-btn", color="secondary", size="sm", className="mt-2"),
                html.Hr(),
                dbc.Button("Run Cleanup", id="cleanup-btn", color="danger", size="sm"),
                html.Div(id="cleanup-result", style={"marginTop": "6px", "fontSize": "0.9em"}),
                html.Hr(),
                dbc.Button("Export Detections", id="export-detections-btn", color="info", size="sm", className="me-2"),
                dbc.Button("Export Aggregated", id="export-aggregated-btn", color="info", size="sm"),
                dcc.Download(id="download-asset"),
                html.Hr(),
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
        dbc.ModalHeader(dbc.ModalTitle("Pattern Detail")),
        dbc.ModalBody(id="pattern-modal-body"),
        dbc.ModalFooter(
            [
                dbc.Button("Export Chart PNG", id="export-chart-btn", color="secondary", size="sm"),
                dbc.Button("Close", id="modal-close", className="ms-auto"),
            ]
        ),
    ],
    id="pattern-modal",
    is_open=False,
)

# append store & modal to main layout by injecting into app.layout container

main_content = dbc.Tabs(
    [
        dbc.Tab(label="Chart", tab_id="tab-chart", children=[dcc.Graph(id="candle-chart")]),
        dbc.Tab(label="Patterns", tab_id="tab-patterns", children=[html.Div(id="pattern-table")]),
        dbc.Tab(label="Aggregated", tab_id="tab-agg", children=[html.Div(id="aggregated-table")]),
        dbc.Tab(label="OPP", tab_id="tab-opp", children=[html.Div(id="opp-table")]),
    ], id="tabs", active_tab="tab-chart",
)

app.layout = dbc.Container(
    [navbar, store_current, dbc.Row([dbc.Col(sidebar, width=3), dbc.Col(main_content, width=9)], className="mt-3"), pattern_modal],
    fluid=True,
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
        # placeholder figure with message
        fig = go.Figure()
        fig.add_annotation(text="No data loaded — upload CSV or click 'Load sample data' to begin", showarrow=False, xref='paper', yref='paper', x=0.5, y=0.5, font=dict(size=16, color='gray'))
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), template='simple_white')

        placeholder_instructions = html.Div([
            html.H5("No data loaded"),
            html.P("Upload a CSV or click 'Load sample data' on the left to populate the dashboard for inspection."),
            html.Ul([html.Li("Upload CSV: Provide timestamp/open/high/low/close columns"), html.Li("Load sample: Use curated BTC-like sample"), html.Li("Custom sequence: Enter sequence tokens like '3R -> Doji -> G'")])
        ], style={"padding": "10px"})

        agg_placeholder = html.Div([html.H5("Aggregated pattern summary"), html.P("No data available")])
        opp_placeholder = html.Div([html.H5("Top OPP patterns"), html.P("No data available")])

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

    # build figure
    fig = go.Figure(data=[go.Candlestick(x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"])])

    filtered_patterns = [p for p in patterns if p["pattern"] in selected]

    for p in filtered_patterns:
        try:
            fig.add_trace(go.Scatter(x=[p["timestamp"]], y=[df.loc[df["timestamp"]==p["timestamp"], "high"].iat[0]], mode='markers+text', text=[p["pattern"]], name=p["pattern"], marker=dict(size=10)))
        except Exception:
            continue

    # occurrence list
    list_section = html.Div([html.H5("Detections (per occurrence)"), html.Ul([html.Li(f"{p['timestamp']}: {p['pattern']}") for p in filtered_patterns])])

    # aggregated
    summary = summarize_detections(pd.DataFrame(data["df"]), patterns)
    if summary:
        # compute sparkline series per pattern
        from candle_patterns.reporting import pattern_sparkline_series

        spark_map = pattern_sparkline_series(pd.DataFrame(data["df"]), patterns, horizon=6)

        rows = [html.Tr([html.Th(c) for c in ["pattern", "count", "support", "avg_return", "win_rate", "trend"]])]
        for r in summary:
            pname = r["pattern"]
            series = spark_map.get(pname, [])
            # build mini sparkline
            mini_fig = go.Figure(data=[go.Scatter(x=list(range(len(series))), y=series, mode="lines", line=dict(width=2), hoverinfo='y')])
            mini_fig.update_layout(margin=dict(l=0, r=0, t=2, b=0), height=60, xaxis=dict(visible=False), yaxis=dict(visible=False))

            # info icon with native tooltip (title)
            PATTERN_EXPLANATIONS = {
                "doji": "Small body; open and close are near. Indicates indecision.",
                "hammer": "Small body with long lower wick; potential bullish reversal.",
                "bullish_engulfing": "A bullish candle that fully engulfs the prior bearish candle.",
                "morning_star": "Three-candle bullish reversal pattern.",
            }
            expl = PATTERN_EXPLANATIONS.get(pname, "")
            info_icon = html.Span(" ℹ️", title=expl, style={"cursor": "help"})

            rows.append(
                html.Tr([
                    html.Td([html.Span(pname), info_icon]),
                    html.Td(r["count"]),
                    html.Td(f"{r['support']:.3f}"),
                    html.Td(f"{r['avg_return']:.4f}"),
                    html.Td(f"{r['win_rate']:.2%}"),
                    html.Td(dcc.Graph(figure=mini_fig, config={"displayModeBar": False}, style={"height": "60px"})),
                ])
            )

        agg_table = html.Div([html.H5("Aggregated pattern summary"), html.Table(rows)])
    else:
        agg_table = html.Div("No detections found")

    # OPP
    top_opp = top_patterns_across_lengths(pd.DataFrame(data["df"]), min_len=3, max_len=6, min_support=0.02, top_k=5)
    if top_opp:
        opp_table = html.Div([html.H5("Top OPP patterns"), html.Table([html.Tr([html.Th(c) for c in ["length","pattern","count","support"]])] + [html.Tr([html.Td(t['length']), html.Td(str(t['pattern'])), html.Td(t['count']), html.Td(f"{t['support']:.3f}")]) for t in top_opp])])
    else:
        opp_table = html.Div("No frequent OPP patterns found")

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
    ctx = dash.callback_context
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
            cid = dash.ctx.triggered[0]['value'] if dash.callback_context and dash.callback_context.triggered else None
        except Exception:
            df_all = None
        body_items = [html.P(f"Pattern: {txt}"), html.P(f"Timestamp: {x}"), html.P("Click Export to download detections CSV for details.")]
        try:
            # Attempt to create a mini-chart using the global data if accessible via server memory
            data = dash.callback_context.states.get('current-data.data') if dash.callback_context and getattr(dash.callback_context, 'states', None) else None
            if not data:
                # fallback: try loading last upload from storage
                from candle_patterns.storage import list_uploads, get_upload
                rows = list_uploads(limit=1)
                if rows:
                    rec = get_upload(rows[0]['id'])
                    import pandas as _pd
                    df_all = _pd.read_csv(rec['filepath'])
            if data and not df_all:
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
    last_upload_label = f"{last_upload['stored_at']} - {last_upload['filename']}" if last_upload else "-"

    card_deck = dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([html.H6("Uploads"), html.H4(str(total_uploads))])), width=4),
            dbc.Col(dbc.Card(dbc.CardBody([html.H6("Last Upload"), html.P(last_upload_label)])), width=8),
        ], className="g-2"
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
    return dcc.send_data_frame(df.to_csv, f"detections_{data.get('filename','upload')}.csv", index=False)


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
    return dcc.send_data_frame(df.to_csv, f"aggregated_{data.get('filename','upload')}.csv", index=False)


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
        return dcc.send_bytes(lambda: img_bytes, f"chart_{data.get('filename','upload')}.png")
    except Exception as e:
        logger.exception('export chart failed: %s', e)
        return dash.no_update


@app.callback(
    Output("current-data", "data"),
    Output("upload-status", "children"),
    Input("history-select", "value"),
    Input("load-sample-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_history_or_sample(upload_id, sample_clicks):
    """Load from history (when selected) or load a curated sample when the button is clicked."""
    from pathlib import Path
    from candle_patterns.storage import get_upload, save_upload

    # load from history if dropdown used
    ctx = dash.callback_context
    if not ctx.triggered:
        return None, ""
    trig = ctx.triggered[0]["prop_id"].split(".")[0]
    if trig == "history-select":
        if not upload_id:
            return None, ""
        rec = get_upload(upload_id)
        if not rec:
            return None, ""
        df = pd.read_csv(rec["filepath"]) if rec.get("filepath") else pd.DataFrame()
        patterns = []
        if rec.get("detections_path") and Path(rec.get("detections_path")).exists():
            patterns = pd.read_csv(rec.get("detections_path")).to_dict("records")
        data = {"filename": rec.get("filename"), "upload_id": rec.get("id"), "df": df.to_dict("records"), "patterns": patterns}
        return data, f"Loaded: {rec.get('filename')}"

    # else: load sample
    sample_path = Path("data/samples/sample_synthetic.csv")
    if not sample_path.exists():
        # create a small synthetic BTC-like dataset if missing
        import numpy as np
        import pandas as _pd
        import datetime

        dates = pd.date_range(end=pd.Timestamp.utcnow(), periods=200, freq="H")
        price = 20000 + np.cumsum(np.random.randn(len(dates)) * 50)
        open_p = price + np.random.randn(len(dates)) * 5
        close_p = price + np.random.randn(len(dates)) * 5
        high_p = np.maximum(open_p, close_p) + np.abs(np.random.randn(len(dates)) * 10)
        low_p = np.minimum(open_p, close_p) - np.abs(np.random.randn(len(dates)) * 10)
        sdf = _pd.DataFrame({"timestamp": dates.astype(str), "open": open_p, "high": high_p, "low": low_p, "close": close_p})
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sdf.to_csv(sample_path, index=False)

    df = pd.read_csv(sample_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("UTC") if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]) else df["timestamp"]
    patterns = detect_patterns(df)
    try:
        upload_id = save_upload(sample_path.name, df, patterns)
    except Exception:
        upload_id = None

    data = {"filename": sample_path.name, "upload_id": upload_id, "df": df.to_dict("records"), "patterns": patterns}
    return data, f"Loaded sample: {sample_path.name}"


if __name__ == "__main__":

    # Bind to all interfaces so the server is reachable from host and container scenarios
    app.run(host="0.0.0.0", port=8050, debug=False)
