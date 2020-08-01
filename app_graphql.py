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
summary_df = pd.read_csv('./data/graphql.csv')

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
    dcc.Graph(id='covid-map')
], style={'text-align':'center'})

@app.callback(
    Output('covid-map', 'figure'),
    [Input('type-selector', 'value')])
def update_figure(selected_category):
    return px.scatter_geo(summary_df,
        lat = summary_df['Lat'],
        lon = summary_df['Long'],
        color=summary_df[selected_category],
        opacity=0.4,
        hover_name=summary_df['Country'],
        size=summary_df["Ln " + selected_category],
        animation_frame=summary_df['Date'].astype(str),
        projection="natural earth")

if __name__ == "__main__":
    app.run_server(debug=True)