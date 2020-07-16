import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

import requests
import json
import numpy as np
import pandas as pd

url = "https://api-corona.azurewebsites.net/graphql"

def get_country_codes():
    country_codes_query = '''
    {
        summary {
            countries {
                Code
        }
      }
    }

    '''
    country_codes_request = requests.post(url, json={"query": country_codes_query})
    if country_codes_request.status_code != 200:
        raise Exception("Query failed")
        
    country_codes = country_codes_request.json()['data']['summary']['countries']
    return [e['Code'] for e in country_codes if e['Code'] is not None]

def get_country_name(country_code): 
    country_name_query = ''' 
    query getCountryName($countryCode: ID!) {
        country(country: $countryCode) {
            Summary {
                Slug
            }
        }
    }
    '''
    body = {
        "query": country_name_query,
        "variables": {"countryCode": country_code}
    }
    
    country_name_request = requests.post(url, json=body)
    
    if country_name_request.status_code != 200:
        raise Exception("Query failed.")
    return country_name_request.json()['data']['country']['Summary']['Slug']

def get_country_data(country_code):
    country_data_query = ''' 
    query getCountryData($countryCode: ID!) {
        timelineCountry(country: $countryCode) {
            Country
            Date
            Confirmed
            Deaths
            Lat
            Long
        }
    } 
    '''
    body = {
        "query": country_data_query,
        "variables": {"countryCode": country_code}
    }

    country_data_request = requests.post(url, json=body)

    if country_data_request.status_code != 200:
        raise Exception("Query failed")
        
    country_info = country_data_request.json()['data']['timelineCountry']
    location_info = {"Lat": country_info[0]["Lat"], "Long": country_info[0]["Long"]}
    cases_info = {e['Date']: {"Confirmed": e['Confirmed'], "Deaths": e['Deaths']} for e in country_info} 
    return location_info, cases_info

def fetchData(): 
    country_codes = get_country_codes()[:20]
    rows = []
    for code in country_codes:
        country_name = get_country_name(code)
        print("fetching data for country: ", country_name)
        location_info, cases_info = get_country_data(code)

        for date in cases_info.keys():
            
            confirmed = cases_info[date]["Confirmed"]
            log_confirmed = max(0, np.log10(confirmed))

            deaths = cases_info[date]["Deaths"]
            log_deaths = max(0, np.log10(deaths))

            rows.append([country_name, location_info["Lat"], location_info["Long"], date, 
                              confirmed, deaths, log_confirmed, log_deaths])

    return pd.DataFrame(rows, columns=['Country', 'Lat', 'Long', 'Date', 'Confirmed', "Deaths",
                                              "Log Confirmed", "Log Deaths"])

def createMap(df, selected_category):
    return px.scatter_geo(df,
        lat = df['Lat'],
        lon = df['Long'],
        color=df[selected_category],
        opacity=0.4,
        hover_name=df['Country'],
        size=df[selected_category],
        animation_frame=df['Date'].astype(str),
        projection="natural earth")
    
summary_df = fetchData()

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
    df = summary_df
    ctx = dash.callback_context
    if ctx.triggered:
        if ctx.triggered[0]['prop_id'] == 'interval-component.n_intervals':
            df = fetchData()
    return createMap(df, selected_type)

if __name__ == "__main__":
  app.run_server(debug=True)