from __future__ import annotations


import dash

from dash import html, dcc, Input, Output, State

import plotly.graph_objects as go

import pandas as pd

from candle_patterns.ingestion import load_csv

from candle_patterns.detection import detect_patterns

from candle_patterns.reporting import summarize_detections

from candle_patterns.opp_miner import top_patterns_across_lengths

app = dash.Dash(__name__)

server = app.server


app.layout = html.Div(
    [
        html.H3("Candle Patterns ÔÇö Demo Dashboard"),
        dcc.Upload(id="upload-data", children=html.Button("Upload CSV")),
        html.Div(id="upload-status"),
        dcc.Dropdown(id='history-select', placeholder='Load past upload', clearable=True),
        dcc.Graph(id="candle-chart"),
        html.Div(id="pattern-table"),
    ]
)


@app.callback(
    Output("upload-status", "children"),
    Output("candle-chart", "figure"),
    Output("pattern-table", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def on_upload(contents, filename):

    from candle_patterns.storage import save_upload

    if contents is None:
        return "", go.Figure(), ""

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

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["timestamp"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
            )
        ]
    )

    patterns = detect_patterns(df)

    for p in patterns:
        fig.add_trace(
            go.Scatter(
                x=[p["timestamp"]],
                y=[df.iloc[p["index"]]["high"]],
                mode="markers+text",
                marker=dict(size=10),
                text=[p["pattern"]],
                textposition="top center",
            )
        )

    # persist upload and detections
    try:
        upload_id = save_upload(filename, df, patterns)
    except Exception as e:
        logger.exception("save_upload failed: %s", e)
        upload_id = None

    # update history dropdown options (handled by separate callback)

    # basic per-occurrence list
    list_section = html.Div(
        [
            html.H5("Detections (per occurrence)"),
            html.Ul([html.Li(f"{p['timestamp']}: {p['pattern']}") for p in patterns]),
        ]
    )

    # aggregated summary per pattern
    summary = summarize_detections(df, patterns)

    if summary:
        summary_table = html.Table(
            [
                html.Tr(
                    [
                        html.Th(c)
                        for c in [
                            "pattern",
                            "count",
                            "support",
                            "avg_return",
                            "win_rate",
                        ]
                    ]
                )
            ]
            + [
                html.Tr(
                    [
                        html.Td(r["pattern"]),
                        html.Td(r["count"]),
                        html.Td(f"{r['support']:.3f}"),
                        html.Td(f"{r['avg_return']:.4f}"),
                        html.Td(f"{r['win_rate']:.2%}"),
                    ]
                )
                for r in summary
            ]
        )
    else:
        summary_table = html.Div("No detections found")

    # OPP top patterns (small sample)
    top_opp = top_patterns_across_lengths(
        df, min_len=3, max_len=6, min_support=0.02, top_k=5
    )

    if top_opp:
        opp_table = html.Table(
            [html.Tr([html.Th(c) for c in ["length", "pattern", "count", "support"]])]
            + [
                html.Tr(
                    [
                        html.Td(t["length"]),
                        html.Td(str(t["pattern"])),
                        html.Td(t["count"]),
                        html.Td(f"{t['support']:.3f}"),
                    ]
                )
                for t in top_opp
            ]
        )
    else:
        opp_table = html.Div("No frequent OPP patterns found")

    container = html.Div(
        [
            html.H4(f"Uploaded: {filename}"),
            list_section,
            html.H5("Aggregated pattern summary"),
            summary_table,
            html.H5("Top OPP patterns"),
            opp_table,
            html.Div(f"Upload ID: {upload_id}" if upload_id else "", style={"marginTop": "10px"}),
        ]
    )

    return f"Uploaded: {filename}", fig, container


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
    Output("candle-chart", "figure"),
    Output("pattern-table", "children"),
    Input("history-select", "value"),
)
def load_history(upload_id):
    if not upload_id:
        return go.Figure(), ""
    from candle_patterns.storage import get_upload

    rec = get_upload(upload_id)
    if not rec:
        return go.Figure(), ""
    df = pd.read_csv(rec["filepath"]) if rec.get("filepath") else pd.DataFrame()
    patterns = []
    from pathlib import Path

    if rec.get("detections_path") and Path(rec.get("detections_path")).exists():
        patterns = pd.read_csv(rec.get("detections_path")).to_dict("records")
    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    for p in patterns:
        try:
            fig.add_trace(go.Scatter(x=[p['timestamp']], y=[df.loc[df['timestamp']==p['timestamp'],'high'].iat[0]], mode='markers+text', text=[p['pattern']], textposition='top center', marker=dict(size=10)))
        except (IndexError, KeyError) as e:
            logger.debug("skipping pattern %s when rendering: %s", p.get('pattern'), e)
            continue
    list_section = html.Div([html.H5("Detections (per occurrence)"), html.Ul([html.Li(f"{p['timestamp']}: {p['pattern']}") for p in patterns])])
    return fig, list_section


if __name__ == "__main__":

    # Bind to all interfaces so the server is reachable from host and container scenarios
    app.run(host="0.0.0.0", port=8050, debug=False)
