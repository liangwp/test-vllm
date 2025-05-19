from dash import html, dcc, callback, Input, Output, State
from langchain_community.llms import VLLMOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.prompt_values import PromptValue

from langchain_core.runnables import Runnable


class InputGuardRailTriggered(ValueError):
    """
    Custom Exception type to indicate that a Input Guardrail caught something.
    
    For more elegance, this could be expanded upon for a real implementation.
    Eg. To include some type of wrapper around the guardrail object instead of
    just the error message.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OutputGuardRailTriggered(ValueError):
    """
    Custom Exception type to indicate that a Output Guardrail caught something.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TextCheckGuardrail(Runnable):
    def __init__(self, textcheck, exception_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textcheck = textcheck
        self.exception_class = exception_class

    # https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.Runnable.html#langchain_core.runnables.base.Runnable.invoke
    def invoke(self, input_, config=None, **kwargs):

        if isinstance(input_, PromptValue):
            # This is a prompt.
            check_str = input_.to_string().lower()
        else:
            # This is an output from the LLM
            check_str = input_.lower()

        if self.textcheck.lower() in check_str:
            err_msg = f'{self.exception_class.__name__} triggered. We aren\'t allowed to talk about "{self.textcheck}".'
            raise self.exception_class(err_msg)

        return input_


class ChainLogger(Runnable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._input = None
    
    def invoke(self, input_, config=None, **kwargs):
        # print(f'START-LOG:\n{input}\nEND-LOG')
        
        self._input = input_

        return input_

    def get_response(self):
        if self._input is not None:
            return self._input
        
        return '<No input captured>'


# Components must be accessible when the @callback decorator is called.
# Alternative is to pass around hard-coded string ids.

input_textcheck_component = dcc.Input(
    value='bird'
)
input_guardrails_component = dcc.Checklist(
    options=[
        {
            'label': [
                'Custom Text-checker',
                input_textcheck_component
            ],
            'value': 'custom',
        },
        {
            'label': 'placeholder1',
            'value': 'two',
        },
        {
            'label': 'placeholder1',
            'value': 'three',
        },
    ]
)

output_textcheck_component = dcc.Input(
    value='bird'
)
output_guardrails_component = dcc.Checklist(
    options=[
        {
            'label': [
                'Custom Text-checker',
                output_textcheck_component
            ],
            'value': 'custom',
        },
        {
            'label': 'placeholder2',
            'value': 'two',
        },
        {
            'label': 'placeholder2',
            'value': 'three',
        },
    ]
)

def render_tab_3():
    return html.Div([
        dcc.Textarea(
            id='text-for-llm',
            value='What is a capybara?',
            style={
                'width': '100%',
                'height': 150,
            },
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Span(
                            children=['Input Guardrails'],
                            style={
                                'font-size': '150%',
                                'font-weight': 'bold',
                            }
                        ),
                        input_guardrails_component,
                    ],
                    style={
                        'width': '50%',
                        'border': '1px solid gray',
                    },
                ),
                html.Div(
                    children=[
                        html.Span(
                            children=['Output Guardrails'],
                            style={
                                'font-size': '150%',
                                'font-weight': 'bold',
                            }
                        ),
                        output_guardrails_component,
                    ],
                    style={
                        'width': '50%',
                        'border': '1px solid gray',
                    },
                ),
            ],
            style={
                'display': 'flex',
            },
        ),
        html.Button(
            id='query-llm',
            n_clicks=0,
            children='Query LLM',
        ),
        dcc.Textarea(
            id='text-from-llm',
            value='<LLM response>',
            style={
                'width': '100%',
                'height': 150,
            },
        ),
        dcc.Textarea(
            id='text-after-guard',
            value='<Guardrail response>',
            style={
                'width': '100%',
                'height': 150,
            },
        ),
    ])

@callback(
    Output('text-from-llm', 'value', allow_duplicate=True),
    Output('text-after-guard', 'value', allow_duplicate=True),
    Input('query-llm', 'n_clicks'),
    prevent_initial_call=True,
)
def clear_llm_response(n_clicks):
    """
    Clear the textfield once the "Query LLM" button is clicked.
    """
    return '...', '...'

@callback(
    Output('text-from-llm', 'value'),
    Output('text-after-guard', 'value'),
    Input('query-llm', 'n_clicks'),
    State('text-for-llm', 'value'),
    State(input_guardrails_component, 'value'),
    State(input_textcheck_component, 'value'),
    State(output_guardrails_component, 'value'),
    State(output_textcheck_component, 'value'),
    prevent_initial_call=True,
)
def call_llm(
    n_clicks,
    query_text,
    input_guardrails,
    input_textcheck,
    output_guardrails,
    output_textcheck
):
    """
    Populate the textfield after "Query LLM" button is clicked and after LLM
    response has been retrieved.
    """

    llm = VLLMOpenAI(
        openai_api_key="EMPTY",
        openai_api_base="http://vllm-tester:8000/v1",
        model_name="Qwen/Qwen2.5-1.5B-Instruct",
        # model_kwargs={"stop": ["."]},
        model_kwargs={"seed": 45},
        max_tokens=500,
    )
    
    llm_log = ChainLogger()

    # Note: The template is not an f-string.
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate.from_template(template)

    # The `chain` variable is mutated by chaining Runnables and reassigning
    # these new Runnables back to the `chain` variable. More precise handling is
    # possible but not necessary for this demonstration.

    chain = prompt | llm_log

    if input_guardrails is not None:
        if 'custom' in input_guardrails:
            textcheck_guardrail = TextCheckGuardrail(
                input_textcheck,
                InputGuardRailTriggered,
            )

            chain = chain | textcheck_guardrail
        
        if 'two' in input_guardrails:
            pass
        
        if 'three' in input_guardrails:
            pass

    chain = chain | llm | llm_log

    if output_guardrails is not None:
        if 'custom' in output_guardrails:
            textcheck_guardrail = TextCheckGuardrail(
                output_textcheck,
                OutputGuardRailTriggered,
            )

            chain = chain | textcheck_guardrail
        
        if 'two' in output_guardrails:
            pass
        
        if 'three' in output_guardrails:
            pass

    try:
        output_text = chain.invoke({"question": f"{query_text}"})
        
        # print(f'{query_text=} response={output_text}')
    except InputGuardRailTriggered as e:

        print(f'Input Guardrail captured an error: {repr(e)}')
        return str(e), '<LLM was not called.>'
    
    except OutputGuardRailTriggered as e:

        print(f'Output Guardrail captured an error: {repr(e)}')

        llm_raw_response = llm_log.get_response()
        # print(f'{llm_raw_response=}')

        return llm_raw_response, str(e)

    except Exception as e:
        print(repr(e))
        return (
            '<A general failure has occurred.>',
            '<Please contact your system adminstrator...>'
        )

    # No exceptions thrown from the chain
    llm_raw_response = llm_log.get_response()

    return llm_raw_response, output_text

