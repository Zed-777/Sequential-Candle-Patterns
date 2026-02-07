"""Minimal test to verify dbc.Button click callbacks work."""
import sys
sys.path.insert(0, 'src')

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback_context

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Button Click Test"),
    dbc.Button(
        "Click Me",
        id="test-btn",
        color="success",
        size="lg",
        className="mt-3"
    ),
    html.Div(id="output", className="mt-3")
], className="mt-5")

@app.callback(
    Output("output", "children"),
    Input("test-btn", "n_clicks"),
)
def on_click(n_clicks):
    print(f"\n{'='*60}")
    print(f"BUTTON CLICK DETECTED! n_clicks = {n_clicks}")
    print(f"{'='*60}\n")
    
    if n_clicks is None:
        return "Click the button above"
    return f"Button clicked {n_clicks} time(s)"

if __name__ == "__main__":
    print("\n" + "="*60)
    print("STARTING TEST DASHBOARD")
    print("="*60)
    print("Visit: http://127.0.0.1:8051")
    print("Press: Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=False, host='127.0.0.1', port=8051, use_reloader=False)
