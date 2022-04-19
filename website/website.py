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
    background_color = 'rgba(0, 0, 0, 255)'
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
                           style={"text-align": "center", "font-size": "5vh","color":status_color}),

                    html.Div(children=[html.Button("Przełącz lasery pomiarowe",
                                                   id='turn-off-on-lasers')],
                             style={"text-align": "center"}),
                    html.Br(),
                    html.Hr(),
                    html.P("Wybrana kostka:",
                           style={"text-align": "center", "font-size": "2vh", "margin-top": "2vh"}),
                    html.P(default_selected_brick, id="choosed-brick-height",
                           style={"text-align": "center", "font-size": "4vh", "padding": "0px"}),
                    html.Div(children=[html.Button("Kostka 60mm",
                                                   id='kostka-60mm-button'),
                                       html.Button("Kostka 80mm",
                                                   id='kostka-80mm-button'),
                                       html.Button("Kostka 100mm",
                                                   id='kostka-100mm-button')], style={"text-align": "center"}),
                    html.Br(),
                    html.Hr(),
                    html.P("Prawidłowa wysokość i tolerancja:"),
                    html.Div(children=[
                        dcc.Input(id="correct-distance-value",
                                  type="number",
                                  placeholder="Prawidłowa wysokość",
                                  style={"width": "10vw"}),
                        dcc.Input(id='tolerance-value',
                                  type='number',
                                  placeholder="Tolerancja",
                                  style={"width": "4.2vw"})],
                        style={'text-align': 'center'}),

                    html.Br(),

                    html.Br(),

                    html.P("Rozmiar punktów wykresu:"),
                    dcc.Slider
                        (
                        id='point-size-slider',
                        min=1,
                        max=40,
                        step=1,
                        marks={1: '1',
                               5: '5',
                               10: '10',
                               15: '15',
                               20: '20',
                               25: '25',
                               30: '30',
                               35: '35',
                               40: '40'},
                        value=13,
                    )

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

                html.P(id="average-distance"),
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
        return lasers.turned_off_text, {"text-align": "center", "font-size": "5vh","color":"red"}
    elif lasers_are_disabled:
        lasers.turn_on()
        return lasers.turned_on_text, {"text-align": "center", "font-size": "5vh","color":"green"}


@website.callback(
    Output('choosed-brick-height', "children"),

    Input('kostka-60mm-button', 'n_clicks'),
    Input('kostka-80mm-button', 'n_clicks'),
    Input('kostka-100mm-button', 'n_clicks'),
)
def brick_height_changer(b1, b2, b3):
    trigger = callback_context.triggered[0]
    print("You clicked button {}".format(trigger["prop_id"].split(".")[0]))
    if "kostka-60mm-button" in trigger["prop_id"].split(".")[0]:
        Plot.color_range[0] = Plot.color_range_for_60mm_brick[0]
        Plot.color_range[1] = Plot.color_range_for_60mm_brick[1]
        kostka = "Kostka 60mm"
    elif "kostka-80mm-button" in trigger["prop_id"].split(".")[0]:
        Plot.color_range[0] = Plot.color_range_for_80mm_brick[0]
        Plot.color_range[1] = Plot.color_range_for_80mm_brick[1]
        kostka = "Kostka 80mm"
    elif "kostka-100mm-button" in trigger["prop_id"].split(".")[0]:
        Plot.color_range[0] = Plot.color_range_for_100mm_brick[0]
        Plot.color_range[1] = Plot.color_range_for_100mm_brick[1]
        kostka = "Kostka 100mm"
    else:
        kostka = "-"

    return kostka


@website.callback(
    Output('plot', 'figure'),
    Output('plot', 'style'),
    Output('average-distance', 'children'),

    Input('update-interval', 'n_intervals'),
    Input('point-size-slider', 'value'),
    Input('correct-distance-value', 'value'),
    Input('tolerance-value', 'value'),

    State('update-interval', 'disabled'))
def update_graph_scatter(n, point_size,
                         correct_distance_value, tolerance, disabled_state):
    try:
        X = pickle.load(open(x_data, "rb"))
        y = pickle.load(open(y_data, "rb"))
        distance = pickle.load(open(distances_data, 'rb'))
    except Exception:
        X =  [0]
        y = [0]
        distance = [0]
        print("[-] Failed to load Pickle files")
    plot = px.scatter(
        x=X,
        y=y,
        color=distance,
        color_continuous_scale=Plot.color_scheme,
        range_color=[plot_color_range[0], plot_color_range[1]],
        labels=dict(x=Plot.x_label, y=Plot.y_label, color=Plot.color_label)
    )
    plot.update_traces(marker=dict(size=point_size, symbol='square'),
                       selector=dict(mode='markers'),
                       )

    if type(correct_distance_value) == int and type(tolerance) == int:

        if correct_distance_value > 0:

            if floor(distance[y.index(1) - 1]) == correct_distance_value \
                    or (correct_distance_value - tolerance <= floor(
                distance[y.index(1) - 1]) <= correct_distance_value) \
                    or (correct_distance_value + tolerance >= floor(
                distance[y.index(1) - 1]) >= correct_distance_value):
                plot.add_annotation(x=X[-1],
                                    y=y[0],
                                    text=round(distance[y.index(1) - 1], 2),
                                    showarrow=True,
                                    arrowhead=3,
                                    ax=20,
                                    ay=50,
                                    arrowcolor="#ffffff",
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="white"
                                    ),
                                    )
            else:
                plot.add_annotation(x=X[-1],
                                    y=y[0],
                                    text=round(distance[y.index(1) - 1], 2),
                                    showarrow=True,
                                    ax=20,
                                    ay=50,
                                    arrowhead=3,
                                    arrowcolor="#ffffff",
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="red"
                                    ),
                                    )

            if floor(distance[0]) == correct_distance_value \
                    or (correct_distance_value - tolerance <= floor(distance[0]) <= correct_distance_value) \
                    or (correct_distance_value + tolerance >= floor(distance[0]) >= correct_distance_value):
                plot.add_annotation(x=X[0],
                                    y=y[0],
                                    text=round(distance[0], 2),
                                    arrowhead=3,
                                    ax=20,
                                    ay=50,
                                    showarrow=True,
                                    arrowcolor="#ffffff",
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="white"
                                    ),
                                    )
            else:
                plot.add_annotation(x=X[0],
                                    y=y[0],
                                    text=round(distance[0], 2),
                                    arrowhead=3,
                                    arrowcolor="#ffffff",
                                    ax=20,
                                    ay=50,
                                    showarrow=True,
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="red"
                                    ),
                                    )

            if floor(distance[y.index(y[-1])]) == correct_distance_value \
                    or (correct_distance_value - tolerance <= floor(
                distance[y.index(y[-1])]) <= correct_distance_value) \
                    or (correct_distance_value + tolerance >= floor(
                distance[y.index(y[-1])]) >= correct_distance_value):
                plot.add_annotation(x=X[y.index(y[-1])],
                                    y=y[-1],
                                    text=round(distance[y.index(y[-1])], 2),
                                    showarrow=True,
                                    arrowcolor="#ffffff",
                                    arrowhead=3,
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="white"
                                    ),
                                    )
            else:
                plot.add_annotation(x=X[y.index(y[-1])],
                                    y=y[-1],
                                    text=round(distance[y.index(y[-1])], 2),
                                    showarrow=True,
                                    arrowhead=3,
                                    arrowcolor="#ffffff",
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="red"
                                    ),
                                    )

            if floor(distance[-1]) == correct_distance_value \
                    or (correct_distance_value - tolerance <= floor(distance[-1]) <= correct_distance_value) \
                    or (correct_distance_value + tolerance >= floor(distance[-1]) >= correct_distance_value):
                plot.add_annotation(x=X[-1],
                                    y=y[-1],
                                    text=round(distance[-1], 2),
                                    showarrow=True,
                                    arrowhead=3,
                                    arrowcolor="#ffffff",
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="white"
                                    ),
                                    )
            else:
                plot.add_annotation(x=X[-1],
                                    y=y[-1],
                                    text=round(distance[-1], 2),
                                    showarrow=True,
                                    arrowhead=3,
                                    arrowcolor="#ffffff",
                                    font=dict
                                        (
                                        family="Arial",
                                        size=18,
                                        color="red"
                                    ),
                                    )
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
           "Średnia z dystansu: " + str(round(sum(distance) / len(distance)))


if __name__ == '__main__':
    print("[~] Starting website...")
    website.run_server(host="0.0.0.0")
