import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

import json
import pandas as pd
import psycopg2

import os
import bmemcached

# Create a database connection
user = 'postgres'
host = 'data1050.cdzzrqlrfv5z.us-east-1.rds.amazonaws.com'
dbname = 'covid'
schema = 'public'
password = 'data1050-postgres-fa20!'
con = psycopg2.connect(dbname=dbname, user=user, host=host, 
                       password=password)
query_schema = 'SET search_path to ' + schema + ';'
cur = con.cursor()
cur.execute('SET search_path to {}'.format(schema))

# Get data from database
query = query_schema + '''
SELECT "Country", "Date", "Lat", "Long", "Confirmed", "Deaths", 
"Log10 Confirmed", "Log10 Deaths","Ln Confirmed", "Ln Deaths"
FROM cases c
INNER JOIN location l
ON c.country_code = l.country_code;
'''

df = pd.read_sql_query(query, con)

mc = bmemcached.Client(os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','), os.environ.get('MEMCACHEDCLOUD_USERNAME'), os.environ.get('MEMCACHEDCLOUD_PASSWORD'))
mc.set('foo', 'bar')

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(id='title', children=client.get('foo'),
    dcc.RadioItems(
        id='type-selector',
        options=[{'label': i, 'value': i} for i in ['Confirmed', 'Deaths']],
        value='Confirmed',
        style={'margin-top': '60px'}
    ),
    dcc.Graph(id='covid-map')
], style={'text-align':'center'})

@app.callback(
    Output('covid-map', 'figure'),
    [Input('type-selector', 'value')])
def update_figure(selected_category):
    return px.scatter_geo(df,
        lat = df['Lat'],
        lon = df['Long'],
        color=df[selected_category],
        opacity=0.4,
        hover_name=df['Country'],
        size=df["Ln " + selected_category],
        animation_frame=df['Date'].astype(str),
        projection="natural earth")

if __name__ == "__main__":
    app.run_server(debug=True)