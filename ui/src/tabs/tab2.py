from dash import html, dcc

def render_tab_2():
    return html.Div([
        html.H3('Tab content 2'),
        dcc.Graph(
            figure=dict(
                data=[dict(
                    x=[1, 2, 3],
                    y=[5, 10, 6],
                    type='bar'
                )]
            )
        )
    ])
