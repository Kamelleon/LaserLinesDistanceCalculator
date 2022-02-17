import plotly.express as px
import _pickle as cpickle

x = cpickle.load(open("x.pkl", "rb"))
y = cpickle.load(open("y.pkl", "rb"))
distances = cpickle.load(open("distances.pkl", "rb"))
color_range = [57,75]
x_axis_range_slider = [-70,90]
fig = px.scatter(x=x, y=y, color=distances,color_continuous_scale='rdbu_r',range_color=color_range,labels=dict(x="X", y="Rząd", color="Wysokość kostki (mm)"))
fig.update_layout(plot_bgcolor='rgba(173, 173, 173, 230)',
                          xaxis_title="Oś X",
                          yaxis_title="Rząd",
                          legend_title="Legenda")
fig.update_traces(marker=dict(size=10, symbol="square"))
fig.update_xaxes(range=[x_axis_range_slider[0], x_axis_range_slider[1]])
fig.show()