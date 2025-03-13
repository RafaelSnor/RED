from dash import Dash, dcc, html, Input, Output, callback, ctx, register_page, State
import dash_cytoscape as cyto
import pandas as pd
import dash_bootstrap_components as dbc
import io

url='https://docs.google.com/spreadsheets/d/e/2PACX-1vTU0SdQdcULvuqk9abcnzdW609dHXszo-JEfvp0RkQAyR1maTr5m9eINsli_5iGKQ/pub?output=xlsx'

sheets = pd.read_excel(url, sheet_name=['BD', 'EDGES', 'N_AX'])  
df = sheets['BD']
df_eg = sheets['EDGES']
df_ax = sheets['N_AX']

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

#app.layout = html.Div([
layout = html.Div([
    html.Div([
        dcc.Store(id="store-selected-nodes", data=[]),  #  Almacena nodos seleccionados en memoria
        dcc.Dropdown(
            options=[{'label': dep, 'value': dep} for dep in df['DEPARTAMENTO'].unique()],
            value='HUANCAVELICA',  # Valor inicial
            id='REGION',
            searchable=False,
            clearable=False,
            className="rounded-3 shadow-sm",
            style={'fontSize': '12px'} ,
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
            multi=True,  
            placeholder="Selecionar nodo...",
            style={
                'fontSize': '12px',

            } 
        ),
        html.Hr(),
        html.Label('IMPACTO EN LA RED:', style={'font-weight': 'bold'}), 
        dcc.Markdown(id='column-sums',style={'font-size': '12px'}),
        
        html.Div([
            dbc.Button("Download Excel_AX", color="success", className="me-2 botones", id="btn_ax_xlsx"),
            dbc.Button("Download Excel_TX", color="primary", className="me-2 botones", id="btn_tx_xlsx"), 
        ], className="d-flex"),

        dcc.Download(id="download-dataframe_ax-xlsx"),
        dcc.Download(id="download-dataframe_tx-xlsx"),

    ], style={'width': '24%','height': '100vh', 'display': 'inline-block','font-family': 'Helvetica'},className="mi-div"), 

###############################################
    html.Div([
    html.Div([
        cyto.Cytoscape(
            id='cytoscape-graph',
            responsive=True,
            style={'width': '100%', 'height': '90vh', 'background-color': '#f0f0f0', 'position': 'relative'},
            layout={'name': 'preset', 'fit': True},
            maxZoom=3,
            minZoom=0.15,
            boxSelectionEnabled=True,  
 
        ),
        html.Div(
            id='lst_anillos',
            className='leyenda_anillos',
        )
    ], style={'position': 'relative', 'width': '100%', 'height': '100vh'})  
    ], style={'width': '74%' ,'height': '100vh','display': 'inline-block', 'font-family': 'monospace', 'float': 'right'},className="mi-div")
])

########GENERADOR DE EXCELs
@callback(
    Output("download-dataframe_ax-xlsx", "data"),
    Output("download-dataframe_tx-xlsx", "data"),
    Input("btn_ax_xlsx", "n_clicks"),
    Input("btn_tx_xlsx", "n_clicks"),
    State('REGION', 'value'),
    State('NODO', 'value'),
    State('type_selection', 'value'),
    prevent_initial_call=True 
)
def download_excel(n_ax, n_tx, region, nodos, type_selection):
    triggered_id = ctx.triggered_id  
    if not region or not nodos:
        return None, None  

    df_dw = df[df['DEPARTAMENTO'] == region]

    if type_selection == "ID":
        df_dz = df_dw[df_dw['ID'].isin(nodos)][['DISTRITAL' if triggered_id == "btn_ax_xlsx" else 'CODIGO']].dropna()
    else:
        df_dz = df_dw[df_dw['ANILLO'].isin(nodos)][['DISTRITAL' if triggered_id == "btn_ax_xlsx" else 'CODIGO']].dropna()

    if triggered_id == "btn_ax_xlsx":
        lista_distritales = df_dz['DISTRITAL'].tolist()
        df_filtrado = df_ax[df_ax['SALTO 0'].isin(lista_distritales)]
        df_melted = df_filtrado.melt(value_name="LISTA TOTAL DE AX")["LISTA TOTAL DE AX"].dropna().drop_duplicates().reset_index(drop=True)

        if df_melted.empty:
            return None, None

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_dz.to_excel(writer, sheet_name="NODOS DISTRITALES", index=False)
            df_melted.to_excel(writer, sheet_name="NODOS AX", index=False)

        output.seek(0)
        return dcc.send_bytes(output.getvalue(), filename=f'DATOS_AX_{region}.xlsx'), None

    elif triggered_id == "btn_tx_xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_dz.to_excel(writer, sheet_name="NODOS TX", index=False)

        output.seek(0)
        return None, dcc.send_bytes(output.getvalue(), filename=f'DATOS_TX_{region}.xlsx')

    return None, None 

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
        color = anillo_colors.get(anillo, "#000000") 
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

        return [{'label': value, 'value': value[:11]} for value in filtered_df[selected_type].dropna().unique()]
   



@callback(
    Output('cytoscape-graph', 'elements'),
    Input('REGION', 'value'), 
)
def nodos_edges(selected_region):
    filtered_df = df[df['DEPARTAMENTO'] == selected_region] 
    filtered_eg = df_eg[df_eg['DEPARTAMENTO'] == selected_region]
    nodes = [
        {
        "data": {
        "id": row['ID'],
        "label": f"{str(row['CODIGO'])[:11]}\n{str(row['CODIGO'])[12:]}" if pd.notna(row['CODIGO']) else "",
        "firstname": str(row['ANILLO']).strip(),
        },
            "position": {
                "x": float(row['X']) if pd.notna(row['X']) else 0,
                "y": float(row['Y']) if pd.notna(row['Y']) else 0,
            },
            'classes': row['TIPO NODO'],
        }
        for _, row in filtered_df.iterrows()
    ]

    edges = [{"data": {"source": s, "target": t, 'weight': w }} for s, t, w in filtered_eg[['side_A', 'side_B','weight']].values]
    
    return nodes+edges

@callback(
    Output('cytoscape-graph', 'stylesheet'),
    Output('column-sums', 'children'),      
    Input('REGION', 'value'),  
    Input('NODO', 'value'), 
    Input('type_selection', 'value'),
)
def update_graph(selected_region, selected_nodos, selected_type):

    filtered_df = df[df['DEPARTAMENTO'] == selected_region] ### CANDIDATO A PONERLO EN LA MEMORIA DEL NAVEGADOR
    filtered_eg = df_eg[df_eg['DEPARTAMENTO'] == selected_region]### CANDIDATO A PONERLO EN LA MEMORIA DEL NAVEGADOR
    total_cliente = filtered_df.iloc[:, 7:16].sum().sum()
   

    # Estilos base
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
                'border-width': 1,
                "cy-tooltip": "data(label)",
            }
        },
        {
            "selector": "edge",
            "style": {
                "width": 2.5,
                "line-color": "#808080",
            }
            
        },
        {
                'selector': '[weight = 300]',
                'style': {
                    'mid-source-arrow-color': 'black',
                    'mid-source-arrow-shape': 'diamond',
                    'mid-source-arrow-fill': 'hollow',
                    'line-style': 'dashed',
                    
                
                }
        },
        {
        'selector': '.AGREGADOR',
        'style': {
            'shape': 'hexagon',
            'border-width': 8,  # Borde grueso
            'border-color': 'rgba(0, 0, 0, 0.5)',  
            'border-opacity': 0.3,
        
        } 
        }
    ]
  
    for anillo, color in anillo_colors.items():
        s_stylesheet.append({
            "selector": f'[firstname = "{anillo}"]',
            "style": {"background-color": color}
        })


    if selected_nodos == []:
        return s_stylesheet, "SIN NODOS SELECIONADOS"
   
    if selected_nodos:
        filtered_df = filtered_df[filtered_df[selected_type].isin(selected_nodos)]

    numeric_cols = filtered_df.iloc[:, 7:16].select_dtypes(include='number')
    n_tx = filtered_df['CODIGO'].count()
    n_dist = filtered_df['DISTRITAL'].dropna().count()
    n_ax = int(filtered_df['NODOS AX'].sum())

    sums = numeric_cols.sum()
    non_zero_sums = sums[sums != 0].astype(int)

        ###################
    cliente_select= non_zero_sums.sum().sum()
    sum_label = ", ".join([f"{value} {column}" for column, value in non_zero_sums.items()])

    if not sum_label:
        sum_label = "Nodo/s sin clientes o IAOs dependientes"

    sum_label = f"{sum_label}  \n\n**NODOS TX:** {n_tx}\n**NODOS AX:** {n_ax}  \n\nNODOS DISTRITALES: {n_dist} \n\n AFECTACIÓN EN LA RED(%): {round(((cliente_select/total_cliente)*100),2)}%"


    lst_tx= filtered_df['ID'].tolist()
    if selected_nodos:
        for nodo in lst_tx:
            s_stylesheet.append({
                "selector": f"node[id = '{nodo}']",
                "style": {
                    "background-color": "#FF0000",  # Rojo
                },    
            
            })   

    return s_stylesheet, sum_label


@callback(
    Output('NODO', 'value'),  
    Input('cytoscape-graph', 'tapNodeData'),    
    State('NODO', 'value'),
    prevent_initial_call=True
)
def update_selected_nodes(tapped_node, selected_nodes):
  
    
    if selected_nodes is None:
        selected_nodes = []

    triggered_id = ctx.triggered_id 

    if triggered_id == 'cytoscape-graph' and tapped_node:
        selected_nodes = set(selected_nodes)  

   
        if isinstance(tapped_node, dict):
            tapped_node = [tapped_node]

      
        for node in tapped_node:
            node_id = node['id']
            if node_id in selected_nodes:
                selected_nodes.remove(node_id) 
            else:
                selected_nodes.add(node_id) 

        return list(selected_nodes)

    return selected_nodes 


#####################################
@callback(
    Output('store-selected-nodes', 'data'),
    Input('cytoscape-graph', 'selectedNodeData'),
    prevent_initial_call=True
)
def store_selected_nodes(selected_nodes):
    if not selected_nodes:
        return []  
    return [node['id'] for node in selected_nodes]      







