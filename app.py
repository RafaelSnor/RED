from dash import Dash, dcc, html, page_container
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container([
    dbc.Button("☰ Menú", id="open-offcanvas", n_clicks=0, className="mb-2"),
    
    dbc.Offcanvas(
        [
            dbc.Nav(
                [
                    dbc.NavLink("RED AX", href="/RED_AX", active="exact"),
                    dbc.NavLink("RED TX", href="/RED_TX", active="exact"),
                ],
                vertical=True,
                pills=True,
            )
        ],
        id="offcanvas-menu",
        title="Menú",
        is_open=False,
        placement="start",  # Se oculta a la izquierda
    ),

    html.Br(),
    page_container  # Contenedor de las páginas dinámicas
], fluid=True)

# Callback para abrir/cerrar el menú
@app.callback(
    Output("offcanvas-menu", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    State("offcanvas-menu", "is_open")
)
def toggle_offcanvas(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run(debug=True,dev_tools_ui=False, dev_tools_props_check=False, host="0.0.0.0", port=8050)
