import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import plotly.express as px


# Avoid warning message
pd.options.mode.chained_assignment = None


#############################################################
# Dash App for Studying the Motor Vehicle Collisions in NYC #
#############################################################

# Get unique boroughs, zip codes, and years for dropdown menu
borough_name = ('https://data.cityofnewyork.us/resource/h9gi-nx95.json?' +\
               '$select=distinct borough' +\
               '&$where=borough !=\'NAN\'').replace(' ', '%20')
borough_name = pd.read_json(borough_name)

zipcode = ('https://data.cityofnewyork.us/resource/h9gi-nx95.json?' +\
           '$select=distinct zip_code' +\
           '&$where=zip_code !=\'NAN\'and zip_code !=\'     \' and zip_code !=\'10000\'').replace(' ', '%20')
zipcode = pd.read_json(zipcode)


# Apply external stylesheet and add a title
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = "Studying the Motor Vehicle Collisions in NYC!"

# App layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🚘💥🚗🚕", className="header-emoji"),
                html.H1(
                    children="Motor Vehicle Collision Analytics", className="header-title"
                ),
                html.P(
                    children="Studying the NYC Motor Vehicle Collisions"
                    " across each borough and zip code",
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
                                {"label": borough, "value": borough}
                                for borough in np.sort(borough_name.borough.str.title())
                            ],
                            value="Manhattan",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Zip Code", className="menu-title"),
                        dcc.Dropdown(
                            id="zipcode-filter",
                            options=[
                                {"label": zip_code, "value": zip_code}
                                for zip_code in np.sort(zipcode.zip_code.unique())
                            ],
                            value="10001",
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
                            id="bar-chart-injured"),
                            className="six columns",
                            style={"width":660,"float":"left","margin": "auto",'display': 'inline-block'}),
                    html.Div(
                        dcc.Graph(
                            id="bar-chart-killed"),
                            className="six columns",
                            style={"width":660,"float":"right","margin": "auto",'display': 'inline-block'}),
                        ],className="row"),
                    html.Div([
                        html.Iframe(id = 'map',
                                    srcDoc = open('NYC_MVC_Map.html', 'r').read(),
                                    width='100%', height='600')]),
    ]
)

# Call back
@app.callback(
    [Output("bar-chart-injured", "figure"), Output("bar-chart-killed", "figure")],
    [
        Input("borough-filter", "value"),
        Input("zipcode-filter", "value"),
    ],
)


def update_charts(borough, zip_code):

    # Load motor vehicle collision data aggregation data
    soql_mvc_zip = ('https://data.cityofnewyork.us/resource/h9gi-nx95.json?' +\
                    '$limit=5000' +\
                    '&$select=borough, zip_code, date_extract_y(crash_date) as year, count(collision_id) as collision_count,' +\
                    'sum(number_of_persons_injured) as total_injured, sum(number_of_persons_killed) as total_killed,' +\
                    'sum(number_of_pedestrians_injured) as pedi, sum(number_of_pedestrians_killed) as peds,' +\
                    'sum(number_of_cyclist_injured) as cyi, sum(number_of_cyclist_killed) as cyk,' +\
                    'sum(number_of_motorist_injured) as mti, sum(number_of_motorist_killed) as mtk' +\
                    '&$where=borough !=\'NAN\' and borough =\'{}\' and zip_code !=\'     \' and zip_code !=\'10000\' and zip_code =\'{}\' and year between \'2013\' and  \'2020\'' +\
                    '&$group=zip_code, year, borough').format(borough.upper(), zip_code).replace(' ', '%20')

    soql_mvc_zip = pd.read_json(soql_mvc_zip)

    soql_mvc_zip = soql_mvc_zip.rename(columns={'borough':'Borough','zip_code':'Zip Code','year':'Year',\
                                                'collision_count':'Total Collision','total_killed':'Total Killed',\
                                                'total_injured':'Total Injured','pedi':'Pedestrians Injured',\
                                                'cyi':'Cyclist Injured','mti':'Motorist Injured','peds':'Pedestrians Killed',\
                                                'cyk':'Cyclist Killed','mtk':'Motorist Killed'})

    #soql_mvc_zip['ZIP'] = soql_mvc_zip['Zip Code'].astype(str) 
    
    soql_mvc_zip = soql_mvc_zip.sort_values(['Year', 'Total Collision'], axis = 0, ascending = False)

    colors = {'background': '#111111','text': '#7FDBFF'}

    data = [
        go.Bar(name = 'Pedestrians',
        x=soql_mvc_zip['Year'], 
        y=soql_mvc_zip['Pedestrians Injured'],  yaxis='y1'),
        
        go.Bar(name = 'Cyclist',
        x=soql_mvc_zip['Year'],
        y=soql_mvc_zip['Cyclist Injured'],  yaxis='y1'),

        go.Bar(name = 'Motorist',
        x=soql_mvc_zip['Year'],
        y=soql_mvc_zip['Motorist Injured'],  yaxis='y1'),

        go.Scatter(name = 'Total Collision',
        x=soql_mvc_zip['Year'],
        y=soql_mvc_zip['Total Collision'],  yaxis='y2')]

    layout = go.Layout(
        barmode = 'stack',
        title = 'Total Persons Injured By Types: {}'.format(borough),
        xaxis=dict(tickvals=soql_mvc_zip['Year']),
        yaxis = dict(showgrid=False),
        yaxis2 = dict(title='Total Collision',
                      overlaying = 'y',
                      side = 'right', showgrid=False),
        legend = dict(orientation = 'h', xanchor="center", x=0.5),
        plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],font_color=colors['text'])

    fig = go.Figure(data=data, layout=layout)

    data2 = [
         go.Bar(name = 'Pedestrians',
         x=soql_mvc_zip['Year'], 
         y=soql_mvc_zip['Pedestrians Killed'],  yaxis='y1'),
        
         go.Bar(name = 'Cyclist',
         x=soql_mvc_zip['Year'],
         y=soql_mvc_zip['Cyclist Killed'],  yaxis='y1'),

         go.Bar(name = 'Motorist',
         x=soql_mvc_zip['Year'],
         y=soql_mvc_zip['Motorist Killed'],  yaxis='y1'),

         go.Scatter(name = 'Total Collision',
         x=soql_mvc_zip['Year'],
         y=soql_mvc_zip['Total Collision'],  yaxis='y2')]

    layout2 = go.Layout(
         barmode = 'stack',
         title = 'Total Persons Killed By Types: {}'.format(borough),
         xaxis=dict(tickvals=soql_mvc_zip['Year']),
         yaxis = dict(showgrid=False),
         yaxis2 = dict(title='Total Collision',
                       overlaying = 'y',
                       side = 'right', showgrid=False),
         legend = dict(orientation = 'h', xanchor="center", x=0.5),
         plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],font_color=colors['text'])

    fig2 = go.Figure(data=data2, layout=layout2)

    return fig, fig2


if __name__ == "__main__":
    app.run_server(debug=False)

