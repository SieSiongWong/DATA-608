import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import plotly.express as px


################################################################################
# Dash App for Studying the Health of Various Tree Species Across Each Borough #
################################################################################

# Get unique borough and species names for dropdown menu
borough = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
           '$select=distinct boroname').replace(' ', '%20')
borough_name = pd.read_json(borough)

species = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
           '$select=distinct spc_common').replace(' ', '%20')
species_name = pd.read_json(species)
species_name = species_name.dropna(subset=['spc_common'])
species_name = species_name.reset_index(drop=True)

# Apply external stylesheet and add a title
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = "Studying the Health of Various Tree Species!"

# App layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🌳", className="header-emoji"),
                html.H1(
                    children="Tree Species Analytics", className="header-title"
                ),
                html.P(
                    children="Studying the health of various tree species"
                    " across each borough",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Borough", className="menu-title"),
                        dcc.Dropdown(
                            id="borough-filter",
                            options=[
                                {"label": boroname, "value": boroname}
                                for boroname in np.sort(borough_name.boroname.unique())
                            ],
                            value="Bronx",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Species", className="menu-title"),
                        dcc.Dropdown(
                            id="species-filter",
                            options=[
                                {"label": spc_common, "value": spc_common}
                                for spc_common in np.sort(species_name.spc_common.unique())
                            ],
                            value="American beech",
                            clearable=False,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",       
        ),        
                html.Div([
                    html.Div(
                        dcc.Graph(
                            id="health-chart"),
                            className="six columns",
                            style={"width":620,"float":"left","margin": "auto",'display': 'inline-block'}),
                    html.Div(
                        dcc.Graph(
                            id="steward-chart"),
                            className="six columns",
                            style={"width":620,"float":"right","margin": "auto",'display': 'inline-block'}),
                        ],className="row"),
    ]
)

# Call back
@app.callback(
    [Output("health-chart", "figure"), Output("steward-chart", "figure")],
    [
        Input("borough-filter", "value"),
        Input("species-filter", "value"),
    ],
)

def update_charts(boroname, spc_common):
    # Load each borough data for each species health 
    soql_url_health = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
                       '$select=boroname,spc_common,health,count(tree_id)' +\
                       '&$where=boroname=\'borough\'&spc_common=\'species\'' +\
                       '&$group=boroname,spc_common,health').\
                       replace('borough', boroname).replace('species', spc_common).replace(' ', '%20')
    soql_trees_health = pd.read_json(soql_url_health)

    # Load each borough data for steward activities impact on the health of trees
    soql_url_steward = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
                        '$select=boroname,spc_common,steward,health,count(health)' +\
                        '&$where=boroname=\'borough\'&spc_common=\'species\'' +\
                        '&$group=boroname,spc_common,steward,health').\
                        replace('borough', boroname).replace('species', spc_common).replace(' ', '%20')
    soql_trees_steward = pd.read_json(soql_url_steward)
    
    # Calculate proportion of trees are in good, fair, or poor health in percentage    
    soql_trees_health['prop'] = round(soql_trees_health['count_tree_id']*100/soql_trees_health['count_tree_id'].sum(), 2)
    soql_trees_steward['prop'] = round(soql_trees_steward['count_health']*100/soql_trees_steward['count_health'].sum(), 2)
    soql_trees_steward = soql_trees_steward.dropna(subset=['steward'])
    
    health_chart_figure = px.bar(soql_trees_health, x="health", y="prop",
                                 title='Propotion of Species Health',
                                 category_orders={"health": ["Good", "Fair", "Poor"]},
                                 labels={'prop':'%','health':''})
    steward_chart_figure = px.bar(soql_trees_steward, x="steward", y="prop", color="health", barmode="stack",
                                  title='Steward Impact on Species Health',
                                  category_orders={"steward": ["None", "1or2","3or4","4orMore"],
                                                   "health": ["Good", "Fair", "Poor"]},
                                  labels={'prop':'%','steward':'','health':''})
    colors = {'background': '#111111','text': '#7FDBFF'}
    steward_chart_figure.update_layout(legend_title='',
                                       title_x=0.5,
                                       legend=dict(orientation="h", xanchor="center", x=0.5),
                                       plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],font_color=colors['text'])
    health_chart_figure.update_layout(title_x=0.5,
                                      plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],font_color=colors['text'])

    return health_chart_figure, steward_chart_figure


if __name__ == "__main__":
    app.run_server(debug=False)

