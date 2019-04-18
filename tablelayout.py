import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import dash_html_components as html
import pandas as pd
import numpy as np
from flask import Flask
import urllib.request
import json
import plotly.plotly as py
import plotly.graph_objs as go
import dash_table

def get_graph_from_data(dataSetCSVInt,dataSetJSONInt,app):

    """Get the graphs for a particular dataset. Invoked from dashapp.

  The graph is defined by the layout. Yo add a new type of plot, add a plot to the layout.

    Parameters
    ----------

    :param dataSetCSVInt: The integer corresponding to the CSV ID on the OpenML server
    :param dataSetJSONInt: The integer corresponding to the JSON ID on the OpenML server

    Returns
    -------
    the page layout with graphs corresponding to the dataset

    """
    url = "https://www.openml.org/data/v1/get_csv/{}".format(dataSetCSVInt)
    df = pd.read_csv(url)


    for column in df:
        df[column].fillna(df[column].mode())
    url = 'https://www.openml.org/api/v1/json/data/features/{}'.format(dataSetJSONInt)
    response = urllib.request.urlopen(url)
    encoding = response.info().get_content_charset('utf8')
    metadata = json.loads(response.read().decode(encoding))
    metadata = pd.DataFrame.from_dict(metadata["data_features"])
    d= metadata["feature"]
    featureinfo = pd.DataFrame.from_records(d)
    numericals = []
    nominals = []
    labels = []
    for feature in metadata["feature"]:
        if feature["is_target"] == "true":
            target = feature["name"]
        if feature["data_type"] == "nominal":
            nominals.append(feature["name"])
        else:
            numericals.append(feature["name"])
        labels.append(feature["name"])
    if target not in numericals:
        numtar = {}
        counter = 0
        for i in set(df[target]):
            numtar[i] = counter
            counter += 1
        aplist = []
        for i in df[target]:
            aplist.append(numtar[i])
        df["numerical_target"] = aplist

    layout = html.Div([
        html.H4('Gapminder DataTable'),
        dt.DataTable(
            rows=featureinfo.to_dict('records'),

            # optional - sets the order of columns
            columns=sorted(featureinfo.columns),

            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='datatable-gapminder'
        ),
        html.Div(id='selected-indexes'),
        dcc.Graph(
            id='graph-gapminder'
        ),

        #scatter
        html.Div([
            html.Div(children=[
                html.Div(
                    [dcc.Dropdown(
                        id='dualVariableDropdownNum1',
                        options=[
                            {'label': i, 'value': i} for i in numericals
                        ],
                        multi=False,
                        clearable=False,
                        placeholder="Select an attribute",
                        value=numericals[0]
                    )],
                    style={'width': '30%', 'display': 'inline-block', 'position': 'relative'}
                ),
                html.Div(
                    [dcc.Dropdown(
                        id='dualVariableDropdownNum2',
                        options=[
                            {'label': i, 'value': i} for i in numericals
                        ],
                        multi=False,
                        clearable=False,
                        placeholder="Select an attribute",
                        value=numericals[1]
                    )],
                    style={'width': '30%', 'display': 'inline-block', 'left': '33%', 'position': 'absolute'}),
                html.Div(
                    [dcc.Dropdown(
                        id='dualVariableDropdownNom',
                        options=[
                            {'label': i, 'value': i} for i in nominals
                        ],
                        multi=False,
                        clearable=False,
                        placeholder="Color Code based on",
                        value=nominals[0]
                    )],
                   # style={'width': '30%', 'display': 'inline-block', 'left': '66%', 'position': 'absolute'}
                ),
            ],
                # style={'height': '5%', 'position': 'absolute', 'display': 'inline-block', 'width': '100%',
                #        'top': '33%'}
                ),
            html.Div([
                dcc.Graph(id='scatterPlotGraph',
                          style={'height': '100%', 'width': '100%', 'position': 'absolute'})],
                #style={'height': '27%', 'position': 'absolute', 'display': 'inline-block', 'bottom': '5%',
                 #      'width': '100%'}
            )]
        ),





    ], className="container")

    return layout