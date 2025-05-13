"""
This example uses `dcc.Store` to store an object in-memory in webapp.

Two `callback`s are set up to run on the button click. (Callbacks trigger on the
`Input` DOM object, but we don't explicitly define which client-side event
triggers the callback. Not sure how easy difficult it is to get direct control
over events through Dash. Dash abstracts away a lot of DOM stuff including DOM
events. `n_clicks` is an example of a dash abstraction over the click event.)

One callback updates the text by reading some `State` from the `dcc.Input`s to
update some on-screen text.
The other callback reads the Store, updates it, and writes it back to the Store.
Note that this implementation passes the JSONified store from frontend to
backend server, logs the existing value on the backend, increments the counter
on the backend, then sends it back to the frontend for storage in-memory. A
consequence of trying to abstract away the application in the browser, so that
emphasis is placed on running python code.

In the second callback, we bring in langchain and make a call to vllm.
https://python.langchain.com/docs/integrations/llms/vllm/#openai-compatible-server
"""


from dash import Dash, html, dcc, callback, Output, Input
from tabs import render_tab_1, render_tab_2, render_tab_3

app = Dash()

server = app.server  # "export" for gunicorn

app.layout = html.Div([
    dcc.Tabs(
        id='tabs-example-1',
        value='tab-1',
        children=[
            dcc.Tab(label='Test 1', value='tab-1'),
            dcc.Tab(label='Test Graph', value='tab-2'),
            dcc.Tab(label='Test LLM', value='tab-3'),
        ]
    ),
    html.Div(id='tabs-example-content-1')
])


@callback(
    Output('tabs-example-content-1', 'children'),
    Input('tabs-example-1', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return render_tab_1()
    elif tab == 'tab-2':
        return render_tab_2()
    elif tab == 'tab-3':
        return render_tab_3()



if __name__ == '__main__':
    app.run(debug=True)
    # This runs the debug server.
    # In production, we want to serve the dash app using gunicorn.
    # Refer to Dockerfile for startup command.

