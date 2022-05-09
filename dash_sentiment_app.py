import dash #Nos permite hacer dashboards con python
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly #Permite hacer graficas interactivas
import random 
import plotly.graph_objs as go
from collections import deque
import sqlite3 #Es una base de datos SQL que viene integrada en Python
import pandas as pd #Permite el manejo de DataFrames


app = dash.Dash(__name__)
app.layout = html.Div( #Definimos el formato en el que estara el dashboard
    [   html.H2('Morena'),
        dcc.Graph(id='live-graph-Morena', animate=True),
        dcc.Interval(
            id='graph-update-Morena',
            interval=1*1000
        ),
        html.H2('PAN'),
        dcc.Graph(id='live-graph-PAN', animate=True),
        dcc.Interval(
            id='graph-update-PAN',
            interval=1*1000
        ),
        html.H2('PRI'),
        dcc.Graph(id='live-graph-PRI', animate=True),
        dcc.Interval(
            id='graph-update-PRI',
            interval=1*1000
        ),
        html.H2('PES'),
        dcc.Graph(id='live-graph-PES', animate=True),
        dcc.Interval(
            id='graph-update-PES',
            interval=1*1000
        ),
        html.H2('Global'),
        dcc.Graph(id='live-graph-Global', animate=True),
        dcc.Interval(
            id='graph-update-Global',
            interval=1*1000
        ),
        html.Div(id="recent-tweets-table", className='col s12 m6 l6'),  
        dcc.Interval(
            id='recent-table-update',
            interval=1*1000
        ),

    ]
)

#Declaramos algunos colores de la APP
app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

def quick_color(s): #Esta funcion nos dara el color para los tweets dependiendo de si son positivos o negativos
    if s >= 0:
        # positive
        return "#009900"
    elif s <= -0:
        # negative:
        return "#CB3234"

    else:
        return app_colors['background']

def generate_table(df, max_rows=10): #Generamos una tabla HTML a partir de un DataFrame
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color':app_colors['text']}
                                  )
                              ),
                          html.Tbody(
                              [
                                  
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'color':app_colors['text'],
                                                'background-color':quick_color(d[2])}
                                  )
                               for d in df.values.tolist()])
                          ]
    )
#Hacemos la actualizacion de la tabla
@app.callback(Output('recent-tweets-table', 'children'),
              [Input('recent-table-update', 'n_intervals')])
def update_recent_tweets(input_value):
    conn = sqlite3.connect('twitter.db')
    df = pd.read_sql("SELECT * FROM sentiment ORDER BY unix DESC LIMIT 10", conn) #Consultamos la tabla y traemos los ultimos 10 tweets, esto se hace cada segundo

    df['date'] = pd.to_datetime(df['unix'], unit='ms')

    df = df.drop(['unix'], axis=1)
    df = df[['date','tweet','sentiment']]

    return generate_table(df, max_rows=10)

#Hacemos la actualizacion de la serie de tiempo de Morena
@app.callback(Output('live-graph-Morena', 'figure'),
              [Input('graph-update-Morena', 'n_intervals')])
def update_graph_scatter(input_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE teewtlimpio LIKE '%morena%' ORDER BY unix DESC LIMIT 1000", conn) #Traemos cada segundo los tweets que incluyen la palabra morena
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean() #Hacemos un suavizado del sentimiento, para tener una curva un poco mas suave
        df.dropna(inplace=True)

        X = df.unix.values[-100:]
        Y = df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(#Generamos la grafica con Plotly
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[-1,1]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')
# A partir de aqui, hacemos lo mismo para los demas partidos, y para la grafica general de todos los tweets relacionados con las votaciones
@app.callback(Output('live-graph-PAN', 'figure'),
              [Input('graph-update-PAN', 'n_intervals')])
def update_graph_scatter(input_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE teewtlimpio LIKE '%pan%' ORDER BY unix DESC LIMIT 1000", conn)
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)

        X = df.unix.values[-100:]
        Y = df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[-1,1]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('live-graph-PRI', 'figure'),
              [Input('graph-update-PRI', 'n_intervals')])
def update_graph_scatter(input_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE teewtlimpio LIKE '%pri%' ORDER BY unix DESC LIMIT 1000", conn)
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)

        X = df.unix.values[-100:]
        Y = df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[-1,1]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('live-graph-PES', 'figure'),
              [Input('graph-update-PES', 'n_intervals')])
def update_graph_scatter(input_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE teewtlimpio LIKE '%pes%' ORDER BY unix DESC LIMIT 1000", conn)
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)

        X = df.unix.values[-100:]
        Y = df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[-1,1]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('live-graph-Global', 'figure'),
              [Input('graph-update-Global', 'n_intervals')])
def update_graph_scatter(input_value):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment ORDER BY unix DESC LIMIT 1000", conn)
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)

        X = df.unix.values[-100:]
        Y = df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[-1,1]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')
# Desplegamos el servidor, por default se crea en el puerto 8050
if __name__ == '__main__':
    app.run_server(debug=True)
#Este archivo tambien lo corremos en una terminal en segundo plano, y podemos ver el analisis en tiempo real en el navegador