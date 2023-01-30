import pandas as pd
import requests
import json
from pandas.io.json import json_normalize

import dash
import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from datetime import datetime, timezone, timedelta

r = requests.get("http://api.coincap.io/v2/assets/bitcoin/history?interval=d1")
data = r.json()
df = pd.json_normalize(data["data"])

df['priceUsd'] = df['priceUsd'].astype(float)
df['time'] = df['time'].astype(int)
df['time'] = pd.to_datetime(df['time'], unit='ms')
fig = px.bar(df, x="time", y="priceUsd", title="Graph")
r_asserts = requests.get("http://api.coincap.io/v2/assets")
data = r_asserts.json()
df_asset = pd.json_normalize(data["data"])

df_asset = df_asset[['id', 'symbol']]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Row([
    dbc.Col(
        [
            html.Label('Select asset'),
            dcc.Dropdown(
                id='fig_dropdown',
                options=[{'label': x, 'value': x} for x in df_asset['symbol']],
                value='BTC'
            ),
            html.Label('Date From '),
            html.Br(),
            dcc.Input(id="input1", value="01.01.1969", type="text", placeholder="01.01.1969",
                      style={'marginRight': '10px'}),
            html.Br(),
            html.Label('Date To  '),
            html.Br(),
            dcc.Input(id="input2", value="01.01.1970", type="text", placeholder="01.01.1970", debounce=True),
        ],
        width={"size": 2, "offset": 0}
    ),

    dbc.Col(
        dcc.Graph(
            id='example-graph',
            figure=fig
        ),
        width={"size": 9, "offset": 0}
    )
]
)


@app.callback(
    Output("example-graph", "figure"),
    Input("input1", "value"),
    Input("input2", "value"),
    Input('fig_dropdown', 'value')
)
def update_graph(input1, input2, fig_name):
    asset = df_asset.loc[df_asset['symbol'].isin([fig_name])]
    item = asset['id'].values.tolist()[0]

    if item:

        try:
            r = requests.get("http://api.coincap.io/v2/assets/" + item + "/history?interval=d1")
            data = r.json()
            df = pd.json_normalize(data['data'])
            df['priceUsd'] = df['priceUsd'].astype(float)
            df['time'] = df['time'].astype(int)
            df['time'] = pd.to_datetime(df['time'], unit='ms')

            input1 = datetime.strptime(input1, '%d.%m.%Y')
            input2 = datetime.strptime(input2, '%d.%m.%Y')
            input2 += timedelta(days=1)
            print("input2", input2)

            mask = (df['time'] >= input1) & (df['time'] < input2)

            df_new = df.loc[mask]
            print(df_new)


            fig = px.bar(df_new, x="time", y="priceUsd", title="Graph")
            return fig
        except:
            print("wrong input")


if __name__ == "__main__":
    app.run_server(debug=True,
                   host='127.0.0.1')
