from dash import Dash, dcc, html, page_container
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import requests
import threading
import time

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX])
server = app.server  # Necesario para Render

app.layout = dbc.Container([
    dbc.DropdownMenu(
    label="☰ Menú",
    direction="end",
    children=[
        dbc.Nav(
                [
                    dbc.NavLink("RED AX", href="/RED_AX", active="exact"),
                    dbc.NavLink("RED TX", href="/RED_TX", active="exact"),
                    #dbc.NavLink("RED TX TEST", href="/RED_TX_TES", active="exact"),
                    
                ],
                vertical=True,
                pills=True,
            )
    ],
    ),
    page_container  # Contenedor de las páginas dinámicas
], fluid=True,style={'background-color': '#f0f0f0'} )
 
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


    
