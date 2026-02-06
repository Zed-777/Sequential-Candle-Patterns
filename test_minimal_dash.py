#!/usr/bin/env python
"""
Ultra-minimal Dash app to isolate the issue.
"""
import sys
sys.path.insert(0, 'src')

import dash
from dash import html
import dash_bootstrap_components as dbc

# Minimal app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Super minimal layout - just text
app.layout = html.Div("Hello from Dash!")

if __name__ == '__main__':
    print("Running minimal Dash app...")
    print("Open browser to http://localhost:8050")
    print("Press Ctrl+C to stop\n")
    
    app.run(
        host='0.0.0.0',
        port=8050,
        debug=False,
        dev_tools_ui=False,
        dev_tools_props_check=False,
        dev_tools_serve_dev_bundles=False,
        dev_tools_hot_reload=False,
    )
