import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

covid_df = pd.read_csv("covid_19_clean_complete.csv")
covid_confirmed_df = covid_df[covid_df['Confirmed'] > 0]
covid_deaths_df = covid_df[covid_df['Deaths'] > 0]

# take median of lat and long for each country, sum Confirmed
confirmed_grouped_df = covid_confirmed_df.groupby(["Country/Region", "Date"]).agg({'Lat': 'mean',
    'Long': 'mean', 'Confirmed': 'sum'}).reset_index()

# ensure animation frame is sorted correctly
confirmed_grouped_df['Date'] = pd.to_datetime(confirmed_grouped_df['Date']).dt.date
confirmed_grouped_df = confirmed_grouped_df.sort_values(by=['Date'])
confirmed_grouped_df['log_confirmed'] = np.log(confirmed_grouped_df['Confirmed'])

# same preprocessing for deaths data
deaths_grouped_df = covid_deaths_df.groupby(["Country/Region", "Date"]).agg({'Lat': 'mean',
    'Long': 'mean', 'Deaths': 'sum'}).reset_index()
deaths_grouped_df['Date'] = pd.to_datetime(deaths_grouped_df['Date']).dt.date
deaths_grouped_df = deaths_grouped_df.sort_values(by=['Date'])
deaths_grouped_df['log_deaths'] = np.log(deaths_grouped_df['Deaths'])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Covid-19 Tracker'),
    dcc.RadioItems(
        id='type-selector',
        options=[{'label': i, 'value': i} for i in ['confirmed', 'deaths']],
        value='confirmed',
        style={'margin-top': '60px'}
    ),
    dcc.Graph(id='covid-map')
], style={'text-align':'center'})

@app.callback(
    Output('covid-map', 'figure'),
    [Input('type-selector', 'value')])
def update_figure(selected_type):
    df = confirmed_grouped_df if selected_type == 'confirmed' else deaths_grouped_df
    return (
        px.scatter_geo(df,
            lat = df['Lat'],
            lon = df['Long'],
            color=df['log_' + selected_type],
            opacity=0.4,
            hover_name=df['Country/Region'],
            size=df['log_' + selected_type],
            animation_frame=df['Date'].astype(str),
            projection="natural earth")
    )

if __name__ == '__main__':
    app.run_server(debug=True)