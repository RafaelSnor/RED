from dash import Dash, dcc, html, Input, Output, callback, ctx, register_page, State
import dash_cytoscape as cyto
import pandas as pd
import dash_bootstrap_components as dbc
import io

url='https://docs.google.com/spreadsheets/d/e/2PACX-1vTU0SdQdcULvuqk9abcnzdW609dHXszo-JEfvp0RkQAyR1maTr5m9eINsli_5iGKQ/pub?output=xlsx'

df = pd.read_excel(url, sheet_name='BD')
df_eg =pd.read_excel(url, sheet_name='EDGES')
df_ax=pd.read_excel(url, sheet_name='N_AX')


register_page(__name__, path="/RED_TX")

anillo_colors = {
        "ANILLO - 01": "#f39c12",
        "ANILLO - 02": "#9932CC",
        "ANILLO - 03": "#00BFFF",
        "ANILLO - 04": "#FFD700",
        "ANILLO - 05": "#FFB6C1",
        "ANILLO - 06": "#4169E1",
        "ANILLO - 07": "#A0522D",
        "ANILLO - 08": "#273746",
    }

layout = html.Div([
    html.Div([
        dcc.Dropdown(
            options=[{'label': dep, 'value': dep} for dep in df['DEPARTAMENTO'].unique()],
            value='HUANCAVELICA', 
            id='REGION',
            className="rounded-3 shadow-sm",
            
        ),
        html.Br(),
        html.Div([
            dbc.RadioItems(
            options=[{'label': 'ID', 'value': 'ID'},
                    {'label': 'ANILLO', 'value': 'ANILLO'}],
            value='ID',
            id='type_selection',
            className="btn-group",  
            inputClassName="btn-check",
            labelClassName="btn btn-outline-dark",
            labelCheckedClassName="active",
            )
            
        ]),
        
        html.Br(),
        dcc.Dropdown(
            id='NODO', 
            multi=True  
        ),
        html.Hr(),
        html.Label('IMPACTO EN LA RED:', style={'font-weight': 'bold'}),  # Título
        dcc.Markdown(id='column-sums',style={'font-size': '12px'}),
        html.Div([
        dbc.Button("Download Excel_AX", color="success", className="me-2 botones", id="btn_ax_xlsx"),
        dbc.Button("Download Excel_TX", color="primary", className="me-2 botones", id="btn_tx_xlsx"), 
        ], className="d-flex"),
        dcc.Download(id="download-dataframe_ax-xlsx"),
        dcc.Download(id="download-dataframe_tx-xlsx"),

    ], style={'width': '25%', 'display': 'inline-block','font-family': 'Georgia'}), 

###############################################
    html.Div([
    html.Div([
        cyto.Cytoscape(
            id='cytoscape-graph',
            responsive=True,
            style={'width': '100%', 'height': '550px', 'background-color': '#f0f0f0', 'position': 'relative'},
            layout={'name': 'preset', 'fit': True},
            maxZoom=3,
            minZoom=0.15,
        ),
        html.Div(
            id='lst_anillos',
            className='leyenda_anillos',
        )
    ], style={'position': 'relative', 'width': '100%', 'height': '550px'}) 
    ], style={'width': '75%' ,'display': 'inline-block', 'font-family': 'monospace', 'float': 'right'})
])

########GENERADOR DE EXCEL AX

@callback(
    Output("download-dataframe_ax-xlsx", "data"),
    Input("btn_ax_xlsx", "n_clicks"),
    State('REGION', 'value'),
    State('NODO', 'value'),
    State('type_selection', 'value'),
    prevent_initial_call=True 
)
def func(n_clicks, region, nodos,type_selection):
    # Verificar si hay región seleccionada
    if not region or not nodos:
        return None  # No genera el archivo si no hay datos
    
    df_dw = df[df['DEPARTAMENTO'] == region]

    if type_selection == "ID":
        df_dz = df_dw[df_dw['ID'].isin(nodos)][['DISTRITAL']].dropna()
    else:
        df_dz = df_dw[df_dw['ANILLO'].isin(nodos)][['DISTRITAL']].dropna()

    lista_distritales = df_dz['DISTRITAL'].tolist()
    df_filtrado = df_ax[df_ax['SALTO 0'].isin(lista_distritales)]


    df_melted = df_filtrado.melt(value_name="LISTA TOTAL DE AX")["LISTA TOTAL DE AX"].dropna().drop_duplicates().reset_index(drop=True) #crea un nuevo dataframe 
    df_distritales= df_dz['DISTRITAL']
    if df_melted.empty:
        return None  

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_distritales.to_excel(writer, sheet_name="NODOS DISTRITALES", index=False)
        df_melted.to_excel(writer, sheet_name="NODOS AX", index=False)

    output.seek(0)
    return dcc.send_bytes(output.getvalue(), filename=f'DATOS_AX_{region}.xlsx')

####################### EXCEL TX

@callback(
    Output("download-dataframe_tx-xlsx", "data"),
    Input("btn_tx_xlsx", "n_clicks"),
    State('REGION', 'value'),
    State('NODO', 'value'),
    State('type_selection', 'value'),
    prevent_initial_call=True 
)
def func(n_clicks, region, nodos,type_selection):

    if not region or not nodos:
        return None  
    
    df_dw = df[df['DEPARTAMENTO'] == region]

    if type_selection == "ID":
        df_dz = df_dw[df_dw['ID'].isin(nodos)][['CODIGO']].dropna()
    else:
        df_dz = df_dw[df_dw['ANILLO'].isin(nodos)][['CODIGO']].dropna()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_dz.to_excel(writer, sheet_name="NODOS TX", index=False)
    
    output.seek(0)
    return dcc.send_bytes(output.getvalue(), filename=f'DATOS_TX_{region}.xlsx')
##################################
@callback(
    Output('lst_anillos', 'children'),
    Input('REGION', 'value')
)
def lista_de_anillos(selected_region):
    filtered_anillos = df[(df['DEPARTAMENTO'] == selected_region) & 
                           (df['ANILLO'].str.contains("ANILLO", na=False))]['ANILLO'].unique()
    
    legend_elements = [html.Strong("Leyenda:",style={'font-size': '12px'})]

    for anillo in filtered_anillos:
        color = anillo_colors.get(anillo, "#000000")  # Negro por defecto
        legend_elements.append(
            html.Div([
                html.Span(style={'display': 'inline-block', 'width': '12px', 'height': '12px', 
                                 'backgroundColor': color, 'marginRight': '5px'}),
                html.Span(anillo, style={'font-size': '11px'}),                 
            ], style={'display': 'flex', 'alignItems': 'center'})
        )
    return legend_elements

@callback(
    Output('NODO', 'options'),
    [Input('REGION', 'value'), Input('type_selection', 'value')]
)
def update_nodo_options(selected_region, selected_type):
   
    filtered_df = df[df['DEPARTAMENTO'] == selected_region]
 
    if selected_type=="ID":
        return [{'label': cod, 'value': id} for cod, id in filtered_df[['CODIGO', 'ID']].values]

    elif selected_type=="ANILLO":
        return [{'label': value, 'value': value} for value in filtered_df[selected_type].dropna().unique()]
   

@callback(
    Output('cytoscape-graph', 'elements'),
    Output('cytoscape-graph', 'stylesheet'),
    Output('column-sums', 'children'),
    Input('REGION', 'value'), 
    Input('NODO', 'value'), 
    Input('type_selection', 'value'),
    
)
def update_graph(selected_region, selected_nodos, selected_type):

    
    filtered_df = df[df['DEPARTAMENTO'] == selected_region] ### CANDIDATO A PONERLO EN LA MEMORIA DEL NAVEGADOR
    filtered_eg = df_eg[df_eg['DEPARTAMENTO'] == selected_region]### CANDIDATO A PONERLO EN LA MEMORIA DEL NAVEGADOR
   

    nodes = [
        {
        "data": {
        "id": row['ID'],
        "label": f"{str(row['CODIGO'])[:11]}\n{str(row['CODIGO'])[12:]}" if pd.notna(row['CODIGO']) else "",
        "firstname": str(row['ANILLO']).strip()
        },
            "position": {
                "x": float(row['X']) if pd.notna(row['X']) else 0,
                "y": float(row['Y']) if pd.notna(row['Y']) else 0,
            }
        }
        for _, row in filtered_df.iterrows()
    ]
   
    edges = [{"data": {"source": s, "target": t}} for s, t in filtered_eg[['side_A', 'side_B']].dropna().values]

  
    s_stylesheet = [
        {
            "selector": "node",
            "style": {
                "content": "data(label)",
                "background-color": "#229954",
                "color": "#000000",
                "text-valign": "top",
                "text-halign": "center",
                "width": "40px",
                "height": "40px",
                "font-size": "15px",
                "white-space": "pre",
                "text-wrap": "wrap",
            }
        },
        {
            "selector": "edge",
            "style": {
                "width": 2.5,
                "line-color": "#808080",
            }
        }
    ]
  
    for anillo, color in anillo_colors.items():
        s_stylesheet.append({
            "selector": f'[firstname = "{anillo}"]',
            "style": {"background-color": color}
        })


    if selected_nodos == []:
        return nodes + edges, s_stylesheet, "SIN NODOS SELECIONADOS"
   
    if selected_nodos:
        filtered_df = filtered_df[filtered_df[selected_type].isin(selected_nodos)]

    numeric_cols = filtered_df.iloc[:, 7:20].select_dtypes(include='number')
    n_tx = filtered_df['CODIGO'].count()
    n_dist = filtered_df['DISTRITAL'].dropna().count()
    n_ax = int(filtered_df['NODOS AX'].sum())

    sums = numeric_cols.sum()
    non_zero_sums = sums[sums != 0].astype(int)
    sum_label = ", ".join([f"{value} {column}" for column, value in non_zero_sums.items()])

    if not sum_label:
        sum_label = "Nodo/s sin clientes o IAOs dependientes"

    sum_label = f"{sum_label}  \n\n**NODOS TX:** {n_tx} \n\nNODOS DISTRITALES: {n_dist} \n\n**NODOS AX:** {n_ax}"

    lst_tx= filtered_df['ID'].tolist()
    if selected_nodos:
        for nodo in lst_tx:
            s_stylesheet.append({
                "selector": f"node[id = '{nodo}']",
                "style": {
                    "background-color": "#FF0000",  # Rojo
                    "width": "40px",
                    "height": "40px",
                }
            })   

    return nodes + edges, s_stylesheet, sum_label


@callback(
    Output('NODO', 'value'),
    [Input('cytoscape-graph', 'tapNodeData'), Input('NODO', 'value')],
    prevent_initial_call=True
)
def update_selected_nodes(tapped_node, selected_nodes):
    if selected_nodes is None:
        selected_nodes = []

    if not ctx.triggered:
        return selected_nodes

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'cytoscape-graph' and tapped_node:
        node_id = tapped_node['id']
        selected_nodes = set(selected_nodes)
        selected_nodes ^= {node_id}  # Agregar si no está, eliminar si está
        return list(selected_nodes)

    return selected_nodes

