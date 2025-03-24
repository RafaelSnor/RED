from dash import Dash, dcc, html, page_container
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


app = Dash(__name__, use_pages=True,suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])

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


if __name__ == '__main__':
    app.run(debug=True, dev_tools_ui=False, dev_tools_props_check=False)


    


    
