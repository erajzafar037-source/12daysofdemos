import dash
from dash import dcc, html, Input, Output, ctx, callback
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
import db_manager as db  # Importing our helper file

# --- INITIAL DATA LOAD ---
df = db.fetch_data()

# --- CONFIGURATION ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# --- COMPONENT HELPERS ---
def create_dropdown(col_name, label, width=3):
    """Helper to generate filter dropdowns cleanly"""
    options = sorted(df[col_name].unique()) if col_name in df else []
    return dbc.Col([
        html.Label(label, className="text-muted small mb-1"),
        dcc.Dropdown(
            id=f'filter-{col_name}',
            options=options,
            multi=True,
            placeholder="All"
        )
    ], width=width)

# Grid Columns Configuration
grid_cols = [
    {"field": "request_id", "hide": True},
    {"field": "child_id", "headerName": "Child ID", "pinned": "left", "width": 150},
    {"field": "country", "headerName": "Country", "filter": True},
    {"field": "primary_gift_category", "headerName": "Category"},
    {"field": "en_route", "editable": True, "cellDataType": "boolean", "width": 120},
    {"field": "delivered", "editable": True, "cellDataType": "boolean", "width": 120},
    {
        "field": "cookies", "editable": True, 
        "cellEditor": "agNumberCellEditor", "cellEditorParams": {"min": 0},
        "cellStyle": {"color": "#0dcaf0", "fontWeight": "bold"}
    },
    {"field": "letter_text", "headerName": "Letter Content", "flex": 1}
]

# --- LAYOUT ---
app.layout = dbc.Container([
    # Header
    html.Div([
        html.H2("North Pole Command Center", className="fw-bold text-white"),
        html.P("Logistics Tracking System", className="text-muted")
    ], className="py-4"),

    # Filters (Using helper function)
    dbc.Card(dbc.CardBody(dbc.Row([
        create_dropdown('country', 'Country'),
        create_dropdown('primary_gift_category', 'Category'),
        create_dropdown('delivery_preference', 'Mode'),
        # Custom logic needed for boolean columns, so we manual add them
        dbc.Col([
            html.Label("En Route", className="text-muted small mb-1"),
            dcc.Dropdown(id='filter-en_route', options=[True, False], multi=True, placeholder="Any")
        ], width=2)
    ], className="g-3")), className="mb-4 shadow-lg"),

    # Map
    dbc.Card(dbc.CardBody(
        dcc.Graph(id='map-graph', style={'height': '35vh'}, config={'displayModeBar': False})
    ), className="mb-4 shadow-lg"),

    # Grid
    html.Div([
        dag.AgGrid(
            id="gift-grid",
            rowData=df.to_dict("records"),
            columnDefs=grid_cols,
            defaultColDef={"resizable": True, "sortable": True, "filter": True},
            dashGridOptions={"pagination": True, "paginationPageSize": 20},
            getRowId="params.data.request_id",
            className="ag-theme-alpine-dark",
            style={"height": "40vh"}
        )
    ], className="shadow-lg rounded overflow-hidden"),

    # Notifications
    dbc.Toast(id="update-toast", header="System Update", is_open=False, duration=4000, 
              style={"position": "fixed", "top": 20, "right": 20, "width": 350, "zIndex": 99}),
], fluid=True)


# --- CALLBACKS ---
@callback(
    [Output('gift-grid', 'rowData'),
     Output('map-graph', 'figure'),
     Output('update-toast', 'is_open'),
     Output('update-toast', 'children')],
    [Input('filter-country', 'value'),
     Input('filter-primary_gift_category', 'value'),
     Input('filter-delivery_preference', 'value'),
     Input('filter-en_route', 'value'),
     Input('gift-grid', 'cellValueChanged')]
)
def update_view(countries, categories, prefs, en_route, cell_change):
    global df
    toast = (False, "")

    # 1. Handle Updates
    if ctx.triggered_id == 'gift-grid' and cell_change:
        change = cell_change[0]
        if db.update_db_record(change['data']['request_id'], change['colId'], change['value']):
            df.loc[df['request_id'] == change['data']['request_id'], change['colId']] = change['value']
            toast = (True, f"Updated record for {change['data'].get('child_id')}")
        else:
            toast = (True, "❌ Database Error")

    # 2. Filter Data
    dff = df.copy()
    if countries: dff = dff[dff['country'].isin(countries)]
    if categories: dff = dff[dff['primary_gift_category'].isin(categories)]
    if prefs: dff = dff[dff['delivery_preference'].isin(prefs)]
    if en_route: dff = dff[dff['en_route'].isin(en_route)]

    # 3. Generate Map
    if not dff.empty:
        fig = px.scatter_mapbox(dff, lat="latitude", lon="longitude", color="primary_gift_category",
                                zoom=1, mapbox_style="carto-darkmatter")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", 
                          plot_bgcolor="rgba(0,0,0,0)", font_color="white", legend_bgcolor="rgba(0,0,0,0)")
    else:
        fig = px.scatter_mapbox(lat=[], lon=[], mapbox_style="carto-darkmatter")
        fig.update_layout(paper_bgcolor="#111", plot_bgcolor="#111", font_color="white")

    return dff.to_dict("records"), fig, toast[0], toast[1]

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)