from __future__ import annotations

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from candle_patterns.ingestion import load_csv
from candle_patterns.detection import detect_patterns

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.H3("Candle Patterns — Demo Dashboard"),
        dcc.Upload(id="upload-data", children=html.Button("Upload CSV")),
        html.Div(id="upload-status"),
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
    if contents is None:
        return "", go.Figure(), ""
    content_type, content_string = contents.split(",", 1)
    import base64

    decoded = base64.b64decode(content_string)
    import io

    df = pd.read_csv(io.BytesIO(decoded))
    try:
        df = load_csv(filename)
    except Exception:
        # fallback: parse from uploaded bytes
        df = pd.read_csv(io.BytesIO(decoded))
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
    # overlay markers
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
    table = html.Ul([html.Li(f"{p['timestamp']}: {p['pattern']}") for p in patterns])
    return f"Uploaded: {filename}", fig, table


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
