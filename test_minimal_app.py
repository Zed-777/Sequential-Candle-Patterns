import dash
import dash_bootstrap_components as dbc
from dash import html

# Minimal test app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Test Dashboard"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.P("If you can see this, the server works!"), width=12)
    ])
], fluid=True)

if __name__ == '__main__':
    from waitress import serve
    print('Testing minimal Dash app on Waitress...')
    print('Visit http://localhost:8050')
    serve(app.server, host='0.0.0.0', port=8050)
