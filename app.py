from dash import Dash, dcc, html, page_container
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import requests
import threading
import time

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX])
server = app.server  # Necesario para Render

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
        placement="start",
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

# Keep-alive solo si no está en modo debug
def keep_awake():
    while True:
        try:
            requests.get("www.red-yk09.onrender.com")  # Reemplaza con tu URL
            print("Keep-alive ejecutado")
        except Exception as e:
            print("Error en keep-alive:", e)
        time.sleep(40)  # Cada 10 minutos

if __name__ == '__main__':
    if not app.debug:  # Solo ejecuta el keep-alive en producción
        threading.Thread(target=keep_awake, daemon=True).start()

    app.run(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
