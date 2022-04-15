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
from gpio_trigger import GPIOTrigger
from pathlib import Path
import os

X = pickle.load(open("x.pkl", "rb"))
movement = pickle.load(open("y.pkl", "rb"))
distance = pickle.load(open('distances.pkl', 'rb'))

gpio_trigger = GPIOTrigger()

website = dash.Dash(__name__, prevent_initial_callbacks=True, update_title="Aktualizowanie wykresu...")
website.title = 'Pomiar wysokości kostki'

measurements_turned_on_text = "WŁĄCZONY"
measurements_turned_off_text = "WYŁĄCZONY"
choosed_brick = "Kostka 60mm"
measurements_status_file = "status.txt"
color_range = [53,67]
def serve_layout():
    try:
        with open(measurements_status_file, "r") as f:
            measurements_status = f.readline()
        if measurements_status == "enabled":
            measurements_status = measurements_turned_on_text
        else:
            measurements_status = measurements_turned_off_text
    except:
        print(traceback.print_exc())
        print(f"Nie znaleziono pliku {measurements_status_file}")
        os._exit(1)

    return (
        html.Div(
            [

                html.P(id='average-distance-attention',
                       style={"color": "orange"}),

                dcc.Graph(id='plot',
                          style={"text-align": "center",
                                 "display": "inline-block"}),

                html.Div(children=[
                    html.P("Status pomiaru wysokości kostki:",
                           style={"text-align": "center"}),
                    html.P(measurements_status, id="plot-update-status",
                           style={"text-align": "center", "font-size": "5vh"}),

                    html.Div(children=[html.Button("Przełącz lasery pomiarowe",
                                                   id='start-stop-plot-updates-button')],
                             style={"text-align": "center"}),
                    html.P("Wybrana kostka:",
                           style={"text-align": "center", "font-size": "3vh"}),
                    html.P(choosed_brick,id="choosed-brick"),
                    html.Div(children=[html.Button("Kostka 60mm",
                                id='kostka-60-button'),
                    html.Button("Kostka 80mm",
                                id='kostka-80-button'),
                    html.Button("Kostka 100mm",
                                id='kostka-100-button')],style={"text-align": "center"}),
                    html.P("Prawidłowa wartość dystansu i tolerancja:"),
                    html.Div(children=[
                        dcc.Input(id="correct-distance-value",
                                  type="number",
                                  placeholder="Wartość prawidłowa",
                                  style={"width": "10vw"}),
                        dcc.Input(id='tolerance-value',
                                  type='number',
                                  placeholder="Tolerancja",
                                  style={"width": "4.2vw"})],
                        style={'text-align': 'center'}),

                    html.Br(),

                    html.P("Zakres koloru punktów dla wykresu:"),
                    dcc.RangeSlider
                        (
                        id='color-range-slider',
                        min=30,
                        max=170,
                        step=0.5,
                        marks={
                            30: '30',
                            50: '50',
                            70: '70',
                            90: '90',
                            110: '110',
                            130: '130',
                            150: '150',
                            170: '170'},
                        value=[55, 65],
                        allowCross=False
                    ),
                    html.Div(id='color-range-slider-output-text',
                             style={'text-align': 'center'}),

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
                    ),

                    html.P("Wysokość wykresu:"),
                    dcc.Slider
                        (
                        id='plot-height-slider',
                        min=1,
                        max=100,
                        step=0.5,
                        marks={1: '1',
                               10: '10',
                               20: '20',
                               30: '30',
                               40: "40",
                               50: "50",
                               60: "60",
                               70: "70",
                               80: "80",
                               90: "90",
                               100: "100"},
                        value=55,
                    )], style={"float": "right",
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
                html.Div(id='left-bottom'),
                html.Div(id='right-bottom'),
                html.Div(id='left-upper'),
                html.Div(id='right-upper'),
            ], style={"font-family": "Bahnschrift"}
        )
    )


website.layout = serve_layout


@website.callback(
    Output('plot-update-status', 'children'),
    Input('plot-update-status', 'children'),
    Input('start-stop-plot-updates-button', 'n_clicks'),
)
def change_plot_updates_status_text(measurements_status_text, number_of_clicks):
    if isinstance(number_of_clicks, int):
        if measurements_status_text == measurements_turned_on_text:
            with open(measurements_status_file, "w") as f:
                f.write("disabled")
            gpio_trigger.turn_off_lasers()
            return measurements_turned_off_text
        elif measurements_status_text == measurements_turned_off_text:
            with open(measurements_status_file, "w") as f:
                f.write("enabled")
            gpio_trigger.turn_on_lasers()
            return measurements_turned_on_text


@website.callback(
    Output('plot', 'figure'),
    Output('plot', 'style'),
    Output('average-distance', 'children'),
    Output('left-bottom', 'children'),
    Output('right-bottom', 'children'),
    Output('left-upper', 'children'),
    Output('right-upper', 'children'),
    Output('update-interval', 'disabled'),

    Input('kostka-60-button', 'n_clicks'),
    Input('kostka-80-button', 'n_clicks'),
    Input('kostka-100-button', 'n_clicks'),
    Input('plot-update-status', 'children'),
    Input('update-interval', 'n_intervals'),
    Input('point-size-slider', 'value'),
    Input("plot-height-slider", "value"),
    Input('correct-distance-value', 'value'),
    Input('tolerance-value', 'value'),
    State('update-interval', 'disabled'))
def update_graph_scatter(brick_60_button_click,brick_80_button_click,brick_100_button_click,measurements_status_text, n, point_size, height_slider,
                         correct_distance_value, tolerance, disabled_state):
    trigger = callback_context.triggered[0]
    print("You clicked button {}".format(trigger["prop_id"].split(".")[0]))
    if "kostka-60-button" in trigger["prop_id"].split(".")[0]:
        color_range[0] = 53
        color_range[1] = 67
    if "kostka-80-button" in trigger["prop_id"].split(".")[0]:
        color_range[0] = 73
        color_range[1] = 87
    if "kostka-100-button" in trigger["prop_id"].split(".")[0]:
        color_range[0] = 93
        color_range[1] = 107
    if measurements_status_text == measurements_turned_on_text:
        disabled_state = False
    else:
        disabled_state = True
    try:
        X = pickle.load(open("x.pkl", "rb"))
        movement = pickle.load(open("y.pkl", "rb"))
        distance = pickle.load(open('distances.pkl', 'rb'))
    except Exception:
        X = pickle.load(open("x.pkl", "rb"))
        movement = pickle.load(open("y.pkl", "rb"))
        distance = pickle.load(open('distances.pkl', 'rb'))
    fig = px.scatter(
        x=X,
        y=movement,
        color=distance,
        color_continuous_scale=f"rdbu_r",
        range_color=[color_range[0], color_range[1]],
        labels=dict(x="Rząd", y="Oś Y", color="Wysokośc kostki (mm)")
    )

    fig.update_traces(marker=dict(size=point_size, symbol='square'),
                      selector=dict(mode='markers'),
                      )

    if type(correct_distance_value) == int and type(tolerance) == int:

        if correct_distance_value > 0:

            if floor(distance[movement.index(1) - 1]) == correct_distance_value \
                    or (correct_distance_value - tolerance <= floor(
                distance[movement.index(1) - 1]) <= correct_distance_value) \
                    or (correct_distance_value + tolerance >= floor(
                distance[movement.index(1) - 1]) >= correct_distance_value):
                fig.add_annotation(x=X[-1],
                                   y=movement[0],
                                   text=round(distance[movement.index(1) - 1], 2),
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
                fig.add_annotation(x=X[-1],
                                   y=movement[0],
                                   text=round(distance[movement.index(1) - 1], 2),
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
                fig.add_annotation(x=X[0],
                                   y=movement[0],
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
                fig.add_annotation(x=X[0],
                                   y=movement[0],
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

            if floor(distance[movement.index(movement[-1])]) == correct_distance_value \
                    or (correct_distance_value - tolerance <= floor(
                distance[movement.index(movement[-1])]) <= correct_distance_value) \
                    or (correct_distance_value + tolerance >= floor(
                distance[movement.index(movement[-1])]) >= correct_distance_value):
                fig.add_annotation(x=X[movement.index(movement[-1])],
                                   y=movement[-1],
                                   text=round(distance[movement.index(movement[-1])], 2),
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
                fig.add_annotation(x=X[movement.index(movement[-1])],
                                   y=movement[-1],
                                   text=round(distance[movement.index(movement[-1])], 2),
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
                fig.add_annotation(x=X[-1],
                                   y=movement[-1],
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
                fig.add_annotation(x=X[-1],
                                   y=movement[-1],
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
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 255)',
                      xaxis_title="Rząd",
                      yaxis_title="Oś Y",
                      legend_title="Legenda")
    fig.update_layout(xaxis=dict(showgrid=False, zeroline=False),
                      yaxis=dict(showgrid=False, zeroline=False))

    # fig.update_xaxes(autorange="reversed")

    return fig, \
           {'height': str(height_slider) + "vw",
            'width': "59vw",
            "display": "inline-block"}, \
           "Średnia z dystansu: " + str(round(sum(distance) / len(distance))), \
           "Wartość w prawym dolnym rogu wykresu: ", \
           "Wartość w lewym dolnym rogu wykresu: ", \
           "Wartość w prawym górnym rogu wykresu: ", \
           "Wartość w lewym górnym rogu wykresu: ", \
           disabled_state


@website.callback(Output('color-range-slider-output-text', 'children'),
                  Input('color-range-slider', 'value'))
def display_color_range_slider_value(color_range_slider_value):
    slider_min_val = float(color_range_slider_value[0])
    slider_max_val = float(color_range_slider_value[1])
    slider_avg_val = (slider_min_val + slider_max_val) / 2

    return 'Wartość najniższa, środkowa, najwyższa: {} | {} | {}'.format(slider_min_val, slider_avg_val, slider_max_val)


if __name__ == '__main__':
    print("[~] Starting server")
    website.run_server(host="0.0.0.0")
