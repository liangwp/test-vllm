from dash import html, dcc, callback, Output, Input, State

def render_tab_1():
    return html.Div([
        dcc.Input(id='input-1-state', type='text', value='Montréal'),
        dcc.Input(id='input-2-state', type='text', value='Canada'),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
        html.Div(id='output-state'),
        dcc.Store(id='value-store', data={ 'c': 120075 }),
    ])


@callback(
    Output('output-state', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('input-1-state', 'value'),
    State('input-2-state', 'value'),
)
def update_output(n_clicks, input1, input2):
    print('update_output')
    return f'''
        The Button has been pressed {n_clicks} times,
        Input 1 is "{input1}",
        and Input 2 is "{input2}"
    '''

@callback(
    Output('value-store', 'data'),
    Input('submit-button-state', 'n_clicks'),
    Input('value-store', 'data'),
)
def print_value_store(n_clicks, data):
    print(f'{n_clicks=}, {data=}')
    data['c'] += 1
    print(f'post-increment {data=}')

    return data