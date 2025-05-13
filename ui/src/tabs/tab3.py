from dash import html, dcc, callback, Input, Output, State
from langchain_community.llms import VLLMOpenAI
from langchain_core.prompts import PromptTemplate

from langchain_core.runnables import Runnable


class TextCheckGuardrail(Runnable):
    def __init__(self, textcheck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textcheck = textcheck

    # https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.Runnable.html#langchain_core.runnables.base.Runnable.invoke
    def invoke(self, input_, config=None, **kwargs):

        if self.textcheck.lower() in input_.lower():
            return f'TextCheckGuardrail triggered. We aren\'t allowed to talk about "{self.textcheck}".'

        return input_


class LLMLogger(Runnable):
    def __init__(self, *args, **kwargs):
        self.llm_raw_response = None
        super().__init__(*args, **kwargs)
        
    
    def invoke(self, input_, config=None, **kwargs):
        # print(f'START-LOG:\n{input}\nEND-LOG')
        
        self.llm_raw_response = input_

        return input_

    def get_response(self):
        if self.llm_raw_response is not None:
            return self.llm_raw_response
        
        return ''

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
                html.Span(
                    children=['Guardrails'],
                    style={
                        'font-size': '150%',
                        'font-weight': 'bold',
                    }
                ),
                dcc.Checklist(
                    id='guardrails-to-apply',
                    options=[
                        {
                            'label': [
                                'Custom Text-checker   ',
                                dcc.Input(
                                    id='custom-textcheck',
                                    value='bird'
                                ),
                            ],
                            'value': 'custom',
                        },
                        {
                            'label': 'placeholder',
                            'value': 'two',
                        },
                        {
                            'label': 'placeholder',
                            'value': 'three',
                        },
                    ]
                ),
            ],
            style={
                'width': '50%',
                'border': '1px solid gray',
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
    State('guardrails-to-apply', 'value'),
    State('custom-textcheck', 'value'),
    prevent_initial_call=True,
)
def call_llm(n_clicks, query_text, guardrails_to_apply, custom_textcheck):
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
    
    llm_log = LLMLogger() 

    # Note: The template is not an f-string.
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate.from_template(template)

    chain = prompt | llm | llm_log

    if guardrails_to_apply is not None:
        if 'custom' in guardrails_to_apply:
            print('apply custom guardrail')
            textcheck_guardrail = TextCheckGuardrail(custom_textcheck)

            chain = chain | textcheck_guardrail
        
        if 'two' in guardrails_to_apply:
            pass
        
        if 'three' in guardrails_to_apply:
            pass

    output_text = chain.invoke({"question": f"{query_text}"})
    # print(f'{query_text=} response={output_text}')
    
    llm_raw_response = llm_log.get_response()
    
    # print(f'{llm_raw_response=}')

    return llm_raw_response, output_text

