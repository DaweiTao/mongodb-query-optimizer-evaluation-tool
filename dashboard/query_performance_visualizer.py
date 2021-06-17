import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.dash import no_update

import plotly.graph_objects as go

from experiment.save_load import load_grid
from experiment.save_load import load_t_grid
from os import path
import heapq

# Create Dash APP via flask
app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server


grid_path = "../results/processed-result-original/uniform/"
mongo_choice_grid = load_grid(path.join(grid_path, "comprehensive_mongo_choice_plan_grid.txt"))
optimal_plan_grid = load_grid(path.join(grid_path, "comprehensive_optimal_plan_grid.txt"))
impact_grid = load_grid(path.join(grid_path, "comprehensive_impact_grid.txt"))

app.layout = html.Div(
    [
        dcc.Store(id='optimal-plan-matrix'),

        html.Div(
            [
                html.Label("MongoDB Query Plan Visualization")
            ], style={
                'width': '100%',
                'fontSize': 23,
                'text-align': 'center',
                'padding-top': '1%',
                'padding-bottom': '1%',
                'display': 'inline-block',
                'background-color': 'yellow'
            }
        ),

        # Mongo's choice
        html.Div(
            [
                dcc.Graph(figure=go.Figure(data=go.Heatmap(z=mongo_choice_grid,
                                                 zmin=0,
                                                 zmax=4,
                                                 zauto=False)))
            ], style={
                'width': '50%',
                'fontSize': 17,
                'padding-top': '1%',
                'padding-bottom': '1%',
                'display': 'inline-block',
                'background-color': 'pink'
            }

        ),

        # optimal query plans
        html.Div(
            [
                dcc.Graph(id='optimal-plan',
                          config={
                              'scrollZoom': False,
                              'displayModeBar': False,
                              'displaylogo': False
                          })
            ], style={
                'width': '50%',
                'fontSize': 17,
                'padding-top': '1%',
                'padding-bottom': '1%',
                'display': 'inline-block',
                'background-color': 'green',
            }
        ),

        # impact
        html.Div(
            [
                dcc.Graph(figure=go.Figure(data=go.Heatmap(z=impact_grid)))
            ], style={
                'width': '50%',
                'fontSize': 17,
                'padding-top': '1%',
                'padding-bottom': '1%',
                'display': 'inline-block',
                'background-color': 'red',
            }
        ),

        # info panel
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Please select a threshold to display ties:")
                    ], style={
                        'width': '100%',
                        'text-align': 'left',
                        'padding-top': '1%',
                        'padding-bottom': '1%',
                        'display': 'inline-block',
                        'background-color': 'green'
                    }
                ),

                dcc.Slider(
                    id='tie-threshold-slider',
                    min=0,
                    max=1,
                    step=0.02,
                    marks={
                        0: "0",
                        0.2: "0.2",
                        0.4: "0.4",
                        0.6: "0.6",
                        0.8: "0.8",
                        1: "1"
                    },
                    value=0
                ),

                html.Div(id='slider-drag-output',
                         style={
                            'padding-top': '1%',
                            'padding-bottom': '1%',
                            'display': 'inline-block',
                            'background-color': 'blue'
                        }
                ),


            ], style={
                'width': '50%',
                'fontSize': 17,
                # 'padding-left': '5%',
                # 'padding-right': '5%',
                'padding-top': '1%',
                'padding-bottom': '1%',
                'display': 'inline-block',
                'background-color': 'white',
            }
        )
    ], style={
        'display': 'inline-block',
        'padding-left': '2%',
        'padding-right': '2%',
        'padding-top': '0%',
        'padding-bottom': '1%',
        'width': '96%',
        'height': '96%',
        'background-color': 'black',
    }
)


@app.callback(
    Output('optimal-plan-matrix', 'data'),
    [
        Input('tie-threshold-slider', 'value'),
    ]
)
def update_optimal_plan_grid(threshold):
    granularity = len(a_time_grid)
    optimal_plan_temp = [[None for c in range(granularity)] for r in range(granularity)]

    for r in range(granularity):
        for c in range(granularity):
            optimal_plan_temp[r][c] = optimal_plan_grid[r][c]

    for r in range(granularity):
        for c in range(granularity):
            a_t = a_time_grid[r][c]
            b_t = b_time_grid[r][c]
            cover_t = cover_time_grid[r][c]
            coll_t = coll_time_grid[r][c]
            h = []
            if a_t is not None:
                heapq.heappush(h, (a_t, 1))
            if b_t is not None:
                heapq.heappush(h, (b_t, 2))
            if cover_t is not None:
                heapq.heappush(h, (cover_t, 3))
            if coll_t is not None:
                heapq.heappush(h, (coll_t, 4))
            first_t, first = heapq.heappop(h)
            second_t, second = heapq.heappop(h)
            percent_diff = abs(first_t - second_t) / ((first_t + second_t) / 2)

            if percent_diff <= threshold:
                optimal_plan_temp[r][c] = 0

    return json.dumps(optimal_plan_temp)


@app.callback(
    Output('slider-drag-output', 'children'),
    [
        Input('tie-threshold-slider', 'value'),
    ]
)
def update_slider_output_msg(threshold):
    return "Threshold value selected: {}%".format(int(threshold * 100))


@app.callback(
    Output('optimal-plan', 'figure'),
    [
        Input('optimal-plan-matrix', 'data'),
    ]
)
def update_mongo_choice(matrix):
    if not matrix:
        return no_update

    optimal_plan_matrix = json.loads(matrix)
    mongo_choice_fig = go.Figure(data=go.Heatmap(z=optimal_plan_matrix,
                                                 zmin=0,
                                                 zmax=4,
                                                 zauto=False))
    return mongo_choice_fig


# @app.callback(
#     Output('mongo-choice', 'figure'),
#     [
#         Input('mongo-choice-matrix', 'data'),
#     ]
# )
# def update_mongo_choice(matrix):
#     if not matrix:
#         return no_update
#
#     # mongo_choice_matrix = json.loads(matrix)
#     mongo_choice_fig = go.Figure(data=go.Heatmap(z=mongo_choice_grid,
#                                                  zmin=0,
#                                                  zmax=4,
#                                                  zauto=False))
#     return mongo_choice_fig


if __name__ == '__main__':
    grid_path = "../results/processed-result-original/uniform/"
    mongo_choice_grid = load_grid(path.join(grid_path, "comprehensive_mongo_choice_plan_grid.txt"))
    optimal_plan_grid = load_grid(path.join(grid_path, "comprehensive_optimal_plan_grid.txt"))
    a_time_grid, b_time_grid, cover_time_grid, coll_time_grid = load_t_grid(path.join(grid_path, "comprehensive_time_grid.txt"))
    app.run_server(debug=True)