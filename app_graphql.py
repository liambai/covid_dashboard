import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime

url = "https://api-corona.azurewebsites.net/graphql"
with open('./data/graphql_country_locations.json', 'r') as fp:
    location_dict = json.load(fp)
summary_df = pd.read_csv('./data/graphql.csv')

def fetch_new_data():
    new_data_query = '''
    {
        summary {
            countries {
                Code
                Confirmed
                Deaths
                Last_Update
                Slug
            }
        }
    }
    '''
    
    new_data_request = requests.post(url, json={"query": new_data_query,})
    
    if new_data_request.status_code != 200:
        raise Exception("Query failed.")
    return new_data_request.json()['data']['summary']['countries']

def update_data(df):
    new_data = fetch_new_data()
    for country_data in new_data:
        country_code = country_data['Code']
        if not country_code:
            continue
        current_date = datetime.strptime(country_data['Last_Update'].split(" ")[0], '%Y-%m-%d')
        current_date_formatted = current_date.strftime("%m-%d-%Y")
        current_date_df = df[(df['Date'] == current_date_formatted) & (df['Country Code'] == country_code)]
        
        # add new row if data corresponding to the current country and date does not exist
        if current_date_df.empty:
            row = {}
            row['Country Code'] = country_code
            row['Country'] = country_data['Slug']
            row['Lat'] = location_dict[country_code]['Lat']
            row['Long'] = location_dict[country_code]['Long']
            row['Date'] = current_date_formatted
            row['Confirmed'] = country_data['Confirmed']
            row['Deaths'] = country_data['Deaths']
            row['Log10 Confirmed'] = max(0, np.log10(country_data['Confirmed']))
            row['Log10 Deaths'] = max(0, np.log10(country_data['Deaths']))
            row['Ln Confirmed'] = max(0, np.log(country_data['Confirmed']))
            row['Ln Deaths'] = max(0, np.log(country_data['Deaths']))
            
            df = df.append(row, ignore_index=True)
    return df

def createMap(df, selected_category):
    return px.scatter_geo(df,
        lat = df['Lat'],
        lon = df['Long'],
        color=df["Log10 " + selected_category],
        opacity=0.4,
        hover_name=df['Country'],
        size=df["Ln " + selected_category],
        animation_frame=df['Date'].astype(str),
        projection="natural earth")

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(id='title', children='Covid-19 Tracker'),
    dcc.RadioItems(
        id='type-selector',
        options=[{'label': i, 'value': i} for i in ['Confirmed', 'Deaths']],
        value='Confirmed',
        style={'margin-top': '60px'}
    ),
    dcc.Graph(id='covid-map'),
    dcc.Interval(
        id='interval-component',
        interval=24*60*60*1000, # in milliseconds
        n_intervals=0
    )
], style={'text-align':'center'})

@app.callback(
    Output('covid-map', 'figure'),
    [Input('type-selector', 'value'),
    Input('interval-component', 'n_intervals')])
def update_map(selected_type, n):
    global summary_df
    ctx = dash.callback_context
    if ctx.triggered:
        if ctx.triggered[0]['prop_id'] == 'interval-component.n_intervals':
            summary_df = update_data(summary_df)
    return createMap(summary_df, selected_type)

if __name__ == "__main__":
  app.run_server(debug=True)