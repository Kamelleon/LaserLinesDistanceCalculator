import dash
import dash_core_components as dcc
import dash_daq as daq
from dash.dependencies import Output, Input, State
import dash_html_components as html
from math import floor
import pickle
import time
import plotly.express as px
from gpio_trigger import GPIOTrigger
from pathlib import Path

X = pickle.load(open("x.pkl", "rb"))
movement = pickle.load(open("y.pkl", "rb"))
distance = pickle.load(open('distances.pkl', 'rb'))
gpio_trigger = GPIOTrigger()
app = dash.Dash(__name__, prevent_initial_callbacks=True, update_title=None)

# Website title
app.title = 'Pomiar wysokości kostki'


def serve_layout():
    with open("status.txt", "r") as f:
        status = f.readline()
    if status == "enabled":
        status = "WŁĄCZONE"
    elif status == "disabled":
        status = "WYŁĄCZONE"

    return (
        html.Div(
            [

                html.P(id='average-distance-attention',
                       style={"color": "orange"}),

                dcc.Graph(id='plot',
                          style={"text-align": "center",
                                 "display": "inline-block"}),

                html.Div(children=[
                    html.P("Stan laserów pomiarowych:",
                           style={"text-align": "center"}),
                    html.P(status, id="plot-update-status", style={"text-align": "center", "font-size": "5vh"}),
                    html.Div(children=[html.Button("Przełącz lasery pomiarowe",
                                                   id='start-stop-plot-updates-button')],
                             style={"text-align": "center"}),

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


app.layout = serve_layout


# @app.callback(Output("plot-update-parent", "children"),
#             [Input('update-interval', 'n_intervals')])
# def status_changer(input_data):
#     with open("status.txt","r") as f:
#         status = f.readline()
#     if status == "enabled":
#         status = "WŁĄCZONA"
#     elif status == "disabled":
#         status = "WYŁĄCZONA"
#     print(status)
#     return [html.P(status,
#                         id='plot-update-status',
#                         style={
#                             "text-align": "center",
#                             "font-size": "30px"})]

@app.callback(
    Output('plot-update-status', 'children'),
    Input('plot-update-status', 'children'),
    Input('start-stop-plot-updates-button', 'n_clicks'),
)
def change_plot_updates_status_text(status_text, number_of_clicks):
    if type(number_of_clicks) == int:
        if status_text == "WŁĄCZONE":
            with open("status.txt", "w") as f:
                f.write("disabled")
            gpio_trigger.turn_off_lasers()
            return "WYŁĄCZONE"
        else:
            with open("status.txt", "w") as f:
                f.write("enabled")
            gpio_trigger.turn_on_lasers()
            return "WŁĄCZONE"
        #
        # if number_of_clicks % 2 == 0:
        #     with open("status.txt", "w") as f:
        #         f.write("enabled")
        #     return "WŁĄCZONA",\
        #            {"color": "green",
        #             "text-align": "center",
        #             "font-size": "30px"}
        # else:
        #     with open("status.txt", "w") as f:
        #         f.write("disabled")
        #     return "WYŁĄCZONA",\
        #            {"color": "red",
        #             "text-align": "center",
        #             "font-size": "30px"}


# @app.callback(
#     Output('update-interval', 'disabled'),
#
#     Input('plot-update-status', 'children'),
#
#     State('update-interval', 'disabled'),
# )
# def enable_disable_plot_updates(status_text, disabled_state):
#     if status_text == "WŁĄCZONA":
#         print(status_text)
#         return not disabled_state
#     else:
#         print(status_text)
#         return disabled_state


@app.callback(
    Output('average-distance-attention', 'children'),

    Input('correct-distance-value', 'value')
)
def average_distance_alert(correct_distance_value):
    if type(correct_distance_value) == int:
        if correct_distance_value > 0:
            if round(sum(distance) / len(distance)) > correct_distance_value:
                return "UWAGA: Średnia z dystansu (" + str(
                    round(sum(distance) / len(distance))) + ") jest wyższa niż podana " \
                                                            "prawidłowa wartość dystansu!"
            elif round(sum(distance) / len(distance)) < correct_distance_value:
                return "UWAGA: Średnia z dystansu (" + str(
                    round(sum(distance) / len(distance))) + ") jest niższa niż podana " \
                                                            "prawidłowa wartość dystansu!"
            else:
                return ""
        else:
            return ""


@app.callback(
    Output('plot', 'figure'),
    Output('plot', 'style'),
    Output('average-distance', 'children'),
    Output('left-bottom', 'children'),
    Output('right-bottom', 'children'),
    Output('left-upper', 'children'),
    Output('right-upper', 'children'),
    Output('update-interval', 'disabled'),

    Input('plot-update-status', 'children'),
    Input('update-interval', 'n_intervals'),
    Input('color-range-slider', 'value'),

    Input('point-size-slider', 'value'),
    Input("plot-height-slider", "value"),
    Input('correct-distance-value', 'value'),
    Input('tolerance-value', 'value'),
    State('update-interval', 'disabled'))
def update_graph_scatter(status_text, n, color_range, point_size, height_slider,
                         correct_distance_value, tolerance, disabled_state):
    if status_text == "WŁĄCZONE":
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
                fig.add_annotation(x=X[movement.index(1) - 1],
                                   y=movement[movement.index(1) - 1],
                                   text=round(distance[movement.index(1) - 1], 2),
                                   showarrow=True,
                                   arrowhead=3,
                                   font=dict
                                       (
                                       family="Arial",
                                       size=18,
                                       color="black"
                                   ),
                                   )
            else:
                fig.add_annotation(x=X[movement.index(1) - 1],
                                   y=movement[movement.index(1) - 1],
                                   text=round(distance[movement.index(1) - 1], 2),
                                   showarrow=True,
                                   arrowhead=3,
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
                                   showarrow=True,
                                   font=dict
                                       (
                                       family="Arial",
                                       size=18,
                                       color="black"
                                   ),
                                   )
            else:
                fig.add_annotation(x=X[0],
                                   y=movement[0],
                                   text=round(distance[0], 2),
                                   arrowhead=3,
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
                                   arrowhead=3,
                                   font=dict
                                       (
                                       family="Arial",
                                       size=18,
                                       color="black"
                                   ),
                                   )
            else:
                fig.add_annotation(x=X[movement.index(movement[-1])],
                                   y=movement[-1],
                                   text=round(distance[movement.index(movement[-1])], 2),
                                   showarrow=True,
                                   arrowhead=3,
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
                                   font=dict
                                       (
                                       family="Arial",
                                       size=18,
                                       color="black"
                                   ),
                                   )
            else:
                fig.add_annotation(x=X[-1],
                                   y=movement[-1],
                                   text=round(distance[-1], 2),
                                   showarrow=True,
                                   arrowhead=3,
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
    fig.update_layout(xaxis=dict(showgrid=False,zeroline=False),
                      yaxis=dict(showgrid=False,zeroline=False))


    fig.update_xaxes(autorange="reversed")

    return fig, \
           {'height': str(height_slider) + "vw",
            'width': "57vw",
            "display": "inline-block"}, \
           "Średnia z dystansu: " + str(round(sum(distance) / len(distance))), \
           "Wartość w prawym dolnym rogu wykresu: ", \
           "Wartość w lewym dolnym rogu wykresu: ", \
           "Wartość w prawym górnym rogu wykresu: ", \
           "Wartość w lewym górnym rogu wykresu: ", \
           disabled_state


@app.callback(Output('color-range-slider-output-text', 'children'),
              Input('color-range-slider', 'value'))
def display_color_range_slider_value(color_range_slider_value):
    slider_min_val = float(color_range_slider_value[0])
    slider_max_val = float(color_range_slider_value[1])
    slider_avg_val = (slider_min_val + slider_max_val) / 2

    return 'Wartość najniższa, środkowa, najwyższa: {} | {} | {}'.format(slider_min_val, slider_avg_val, slider_max_val)


if __name__ == '__main__':
    print("[~] Starting server")
    app.run_server(host="0.0.0.0")
