import sys
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import traceback

import flask
import pandas as pd
import os


def timedelt_to_float_h(timedeltas):
    seconds = timedeltas.total_seconds()
    return seconds/3600


server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')


stechkarte = pd.read_csv('../../mydata/.stechkarte_local.csv',
                         sep="\t", parse_dates=["start", "end"])
stechkarte["worktime"] = stechkarte["end"] - stechkarte["start"]

min_date = stechkarte["start"].min()
max_date = stechkarte["start"].max() + pd.Timedelta(days=31)

occupations = stechkarte["occupation"].unique()
option_list = []
for occupation in occupations:
    option_list.append({"label": occupation, "value": occupation})

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
    html.H1('Worktracker plot'),
    dcc.Dropdown(
        id='my-dropdown',
        options=option_list,
        value=occupations,
        multi=True,
    ),
    dcc.DatePickerSingle(
        id="min-date",
        date=min_date,
        display_format='YYYY-MM-DD'
    ),
    dcc.DatePickerSingle(
        id="max-date",
        date=max_date,
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='my-graph')
], className="container")


@app.callback(Output('my-graph', 'figure'),
              [Input('my-dropdown', 'value'),
               Input('min-date', 'date'),
               Input('max-date', 'date')])
def update_graph(selected_dropdown_value, sel_min_date, sel_max_date):
    # dff = df[df['Stock'] == selected_dropdown_value]
    # plotdata = stechkarte[stechkarte["occupation"] == selected_dropdown_value]
    # worktime = plotdata.resample('M', on='start').sum()["worktime"]\
    #     .apply(timedelt_to_float_h).reset_index()
    plot_list = []
    # if selected_dropdown_value == "Total":
    #     for occupation in occupations:
    #         plotdata = stechkarte[stechkarte["occupation"] == occupation]
    #         worktime = plotdata.resample('M', on='start').sum()["worktime"]\
    #             .apply(timedelt_to_float_h).reset_index()
    #         plot_list.append({
    #             'x': worktime.start,
    #             'y': worktime.worktime,
    #             'name': occupation,
    #             'type': 'bar'
    #         })
    # else:
    #     plotdata = stechkarte[stechkarte["occupation"] == selected_dropdown_value]
    #     worktime = plotdata.resample('M', on='start').sum()["worktime"]\
    #         .apply(timedelt_to_float_h).reset_index()
    #     plot_list.append({
    #         'x': worktime.start,
    #         'y': worktime.worktime,
    #         'name': selected_dropdown_value,
    #         'type': 'bar'
    #     })
    print("sel_min_date", sel_min_date, file=sys.stderr)
    print("type(sel_min_date)", type(sel_min_date), file=sys.stderr)
    sel_min_date = pd.to_datetime(sel_min_date)
    sel_max_date = pd.to_datetime(sel_max_date)
    try:
        ranged_stechkarte = stechkarte[((stechkarte["start"] >= sel_min_date) &
                                        (stechkarte["start"] <= sel_max_date))]
        for occupation in selected_dropdown_value:
            plotdata = ranged_stechkarte[ranged_stechkarte["occupation"] == occupation]
            worktime = plotdata.resample('M', on='start').sum()["worktime"]\
                .apply(timedelt_to_float_h).round(2)
            if not worktime.empty:
                plot_list.append({
                    'x': worktime.index,
                    'y': worktime.values,
                    'name': occupation,
                    'type': 'bar'
                })
        # Total
        worktime = ranged_stechkarte.resample('M', on='start').sum()["worktime"]\
            .apply(timedelt_to_float_h).round(2)

        print("worktime", worktime, file=sys.stderr)

        plot_list.append(go.Scatter(
            x=worktime.index,
            y=worktime.values,
            name="Total",
            mode='markers',
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
        ))

        plot_list.append({
            'x': [sel_min_date, sel_max_date],
            'y': [80, 80],
            'name': "contract time",
            'type': 'line'
        })
    except Exception:
        traceback.print_exc()
        print(ranged_stechkarte.head(), file=sys.stderr)
        print(worktime.head(), file=sys.stderr)

    return {
        'data': plot_list,
        'layout': {
            'barmode': 'stack',
            "xaxis": {'title': 'Date'},
            "yaxis": {'title': 'Work Time'},
            "margin": {'l': 40, 'b': 40, 't': 10, 'r': 10},
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
