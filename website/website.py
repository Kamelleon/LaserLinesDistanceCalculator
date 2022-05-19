import traceback
import dash
from dash import dcc
import dash_daq as daq
from dash.dependencies import Output, Input, State
from dash import html
from math import floor
from dash import callback_context
import pickle
import time
import plotly.express as px
from pathlib import Path
import lasers_manager
import os

website = dash.Dash(__name__, prevent_initial_callbacks=True, update_title="Aktualizowanie...")
website.title = 'Pomiar wysokości kostki'

default_selected_brick = "Kostka 60mm"

x_data = "../pickle_files/x.pkl"
y_data = "../pickle_files/y.pkl"
distances_data = '../pickle_files/distances.pkl'


class Plot:
    height = "100vh"
    width = "59vw"
    x_label = "Rząd"
    y_label = "Oś Y"
    color_label = "Wysokośc kostki (mm)"
    color_scheme = "rdbu_r"
    color_range = [53, 67]
    marker = 'square'
    background_color = 'rgba(186, 186, 186, 255)'
    background_grid = False
    reversed_xaxes = True

    color_range_for_60mm_brick = [53, 67]
    color_range_for_80mm_brick = [73, 87]
    color_range_for_100mm_brick = [93, 107]


plot_color_range = Plot.color_range

lasers = lasers_manager.Lasers()


def website_layout():
    lasers_status = lasers.get_status()

    if lasers_status == lasers.turned_on_text:
        status_color = "green"
    else:
        status_color = "red"

    return (
        html.Div(
            [

                html.P(id='average-distance-attention',
                       style={"color": "orange"}),

                dcc.Graph(id='plot',
                          style={"text-align": "center",
                                 "display": "inline-block"}),

                html.Div(children=[
                    html.Br(),
                    html.Br(),
                    html.Hr(),
                    html.P("Status laserów pomiarowych:",
                           style={"text-align": "center"}),
                    html.P(lasers_status, id="lasers-status",
                           style={"text-align": "center", "font-size": "5vh", "color": status_color}),

                    html.Div(children=[html.Button("Przełącz lasery pomiarowe",
                                                   id='turn-off-on-lasers')],
                             style={"text-align": "center"}),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.P(id="average-distance"),
                    html.Br(),
                    html.P(id="max-distance"),
                    html.Br(),
                    html.P(id="min-distance"),

                ], style={"float": "right",
                          "width": "25vw",
                          "height": "20vw",
                          "margin-right": "120px"}),

                dcc.Interval
                    (
                    id='update-interval',
                    interval=1000,
                    n_intervals=0,
                    disabled=False
                ),

                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

            ], style={"font-family": "Bahnschrift"}
        )
    )


website.layout = website_layout


@website.callback(
    Output('lasers-status', 'children'),
    Output('lasers-status', 'style'),

    Input('lasers-status', 'children'),
    Input('turn-off-on-lasers', 'n_clicks'),
)
def change_plot_updates_status_text(lasers_status, number_of_clicks):
    lasers_are_enabled = lasers_status == lasers.turned_on_text
    lasers_are_disabled = lasers_status == lasers.turned_off_text

    if lasers_are_enabled:
        lasers.turn_off()
        return lasers.turned_off_text, {"text-align": "center", "font-size": "5vh", "color": "red"}
    elif lasers_are_disabled:
        lasers.turn_on()
        return lasers.turned_on_text, {"text-align": "center", "font-size": "5vh", "color": "green"}


@website.callback(
    Output('plot', 'figure'),
    Output('plot', 'style'),
    Output('average-distance', 'children'),
    Output('max-distance', 'children'),
    Output('min-distance', 'children'),

    Input('update-interval', 'n_intervals'),

    State('update-interval', 'disabled'))
def update_graph_scatter(n, disabled_state):
    try:
        X = pickle.load(open(x_data, "rb"))
        y = pickle.load(open(y_data, "rb"))
        distance = pickle.load(open(distances_data, 'rb'))
        #y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
        #     29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
        #X = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        #distance = [63, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
        #            60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
        #            60, 60, 60, 57]
        #distance = [84,80,80,80,80,75,74,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,75]
    except Exception:
        X = [0]
        y = [0]
        distance = [0]
        print("[-] Failed to load Pickle files")

    distances_sum = sum(distance)
    max_distance = max(distance)
    min_distance = min(distance)
    brick_height = distances_sum / len(distance)

    if brick_height > 50 and brick_height < 70:
        # brick_height = 60
        Plot.color_range[0] = Plot.color_range_for_60mm_brick[0]
        Plot.color_range[1] = Plot.color_range_for_60mm_brick[1]
    elif brick_height > 70 and brick_height < 90:
        # brick_height = 80
        Plot.color_range[0] = Plot.color_range_for_80mm_brick[0]
        Plot.color_range[1] = Plot.color_range_for_80mm_brick[1]
    elif brick_height > 90 and brick_height < 110:
        # brick_height = 100
        Plot.color_range[0] = Plot.color_range_for_100mm_brick[0]
        Plot.color_range[1] = Plot.color_range_for_100mm_brick[1]
    else:
        brick_height = 0

    plot = px.scatter(
        x=X,
        y=y,
        color=distance,
        color_continuous_scale=Plot.color_scheme,
        range_color=[plot_color_range[0], plot_color_range[1]],
        labels=dict(x=Plot.x_label, y=Plot.y_label, color=Plot.color_label)
    )
    plot.update_traces(marker=dict(size=13, symbol='square'),
                       selector=dict(mode='markers'),
                       )

    previous_line_values = (-1, -1, -1)

    for line_number, y_coord, distance_value in zip(X, y, distance):
        previous_y_coord = previous_line_values[1]
        if distance_value > (brick_height + 2) or distance_value < (brick_height - 2):
            color = "red"
        else:
            color = "black"
        if y_coord == 25 or y_coord == 13 or y_coord == 38:
            plot.add_annotation(x=line_number,
                                y=y_coord,
                                text=distance_value,
                                ax=0,
                                ay=0,
                                font=dict
                                    (
                                    family="Arial",
                                    size=20,
                                    color=color
                                ),
                                )
        elif y_coord == 0:
            plot.add_annotation(x=line_number,
                                y=y_coord,
                                text=distance_value,
                                ax=0,
                                ay=20,
                                font=dict
                                    (
                                    family="Arial",
                                    size=20,
                                    color=color
                                ),
                                )

        if y_coord < previous_y_coord or (X[-1], y[-1], distance[-1]) == (line_number, y_coord, distance_value):
            x_value = previous_line_values[0]
            y_value = previous_line_values[1]
            text_value = previous_line_values[2]

            if (X[-1], y[-1], distance[-1]) == (line_number, y_coord, distance_value):
                x_value = line_number
                y_value = y_coord
                text_value = distance_value

            plot.add_annotation(x=x_value,
                                y=y_value,
                                text=text_value,
                                ax=0,
                                ay=-20,
                                font=dict
                                    (
                                    family="Arial",
                                    size=20,
                                    color=color
                                ),
                                )
        previous_line_values = (line_number, y_coord, distance_value)

    plot.update_layout(plot_bgcolor=Plot.background_color,
                       legend_title="Legenda")
    plot.update_layout(xaxis=dict(showgrid=Plot.background_grid, zeroline=Plot.background_grid),
                       yaxis=dict(showgrid=Plot.background_grid, zeroline=Plot.background_grid))

    if Plot.reversed_xaxes:
        plot.update_xaxes(autorange="reversed")

    return plot, \
           {'height': Plot.height,
            'width': Plot.width,
            "display": "inline-block"}, \
           f"Średnia wysokość aktualnej kostki: {round(brick_height,2)}", \
           f"Największa wartość wysokości: {max_distance}", \
            f"Najmniejsza wartość wysokości: {min_distance}"


if __name__ == '__main__':
    print("[~] Starting website...")
    website.run_server(host="0.0.0.0")
