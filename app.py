import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale 

#TODO need to work around this, bad implementation
temp = pd.read_csv('data/aggregated_data.csv')

description_key = {}
description_key['GDP'] = """\
    The value of goods and services produced in the U.S.
"""
description_key['Debt'] = """\
    Debt held by State and Local governments in the State.
"""
description_key['GDP per Capita'] = """\
    State's gross output per resident
"""
description_key['Debt per Capita'] = """\
    Amount of state and local debt per resident.
"""
description_key['Per Capita GDP/Debt'] = """\
    State's per capita gross output per dollar of of State's debt.
"""

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=external_stylesheets
)

server = app.server

app.title = 'State Economy Dashboard'
app.layout = html.Div([
    
    dcc.Store(id='data-store'),
    
    html.Div([
        html.H3('State Economy Quickview'),
    ]),
    
    html.Div([
        html.Div([
            dcc.RadioItems(id='picker-radio',
                           options=[
                               {'label': i, 'value': i} for i in temp.columns[-5:]
                           ],
                           value='GDP',
                           labelStyle={'display': 'inline-block'}),
        ], className='twelve columns')
    ]),
    
    html.Div([
        html.Div([
            html.Br(),
            html.P('State values in the figure have been scaled around the mean',
                   style={'fontSize': 9}),
            dcc.Graph(id='map',
                      style={'margin-top': 0}),
            html.P(id='description'),
            html.Br(),
            html.A("Code Repository", href='https://github.com/damansc/state_economy_dashboard', target="_blank", style={'margin-right': 12}),
            html.A("LinkedIn", href='https://www.linkedin.com/in/damancox/', target="_blank"),
        ], className='seven columns'),
        html.Div([
            dash_table.DataTable(id='data-table',
                                 style_cell={'textAlign': 'left',
                                             'width': '40%'},
                                 style_as_list_view=True,
                                 virtualization=True,
                                 fixed_rows={ 'headers': True, 'data': 0 },
                                 )
        ], className='four columns'),
    ]),
    
])

# adding callback to continuously read in the csv file #TODO
# currently having issue where when returning to a previous radiotiem
# The tabled data becomes scaled which should only be done for the map. (4/22)
@app.callback(
    Output('data-store', 'data'),
    [Input('picker-radio', 'value')]
)
def read_in_csv(picker_value):
    data_store = pd.read_csv('data/aggregated_data.csv')
    return data_store.to_json()

@app.callback(
    [Output('map', 'figure'),
     Output('description', 'children')],
    [Input('picker-radio', 'value'),
     Input('data-store', 'data')]
)
def update_map(column, data):
    df_1 = pd.read_json(data)
    df_1[column] = scale(df_1[column].values)
    fig = px.choropleth(df_1, locations='Code', locationmode="USA-states", 
                        color=column, scope="usa")
    return fig, description_key[column]

#updating column names
@app.callback(
    [Output('data-table', 'columns'),
    Output('data-table', 'data')],
    [Input('picker-radio', 'value'),
     Input('data-store', 'data')]
)
def update_update_cols(column, data):
    df = pd.read_json(data)
    df = df[['State', column]].sort_values(by=column, ascending=False)
    df[column] = df[column].map(lambda x: '$' + '{:,}'.format(x))
    return [{'name': i, 'id': i} for i in df.columns], df.to_dict('records')
    
if __name__ == "__main__":
    app.run_server(debug=True) 