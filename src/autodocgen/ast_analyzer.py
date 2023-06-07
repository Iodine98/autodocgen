import ast
import os
import re
from _ast import FunctionDef, AST
from pathlib import Path
from typing import Tuple, Union, Optional, Literal, TypedDict

import black
import dotenv
import openai

dotenv.load_dotenv()


class ChatMessage(TypedDict):
    """
    ChatMessage class for type hints in OpenAI
    """
    role: Union[Literal["user"], Literal["system"], Literal["assistant"]]
    content: str


class ModelKwargs(TypedDict):
    """
    ModelKwargs class for type hints in OpenAI
    """
    max_tokens: int
    model: str
    messages: list[ChatMessage]
    n: Optional[int]
    stop: Optional[Union[str, list]]
    temperature: int


class ASTAnalyzer:
    default_messages: list[ChatMessage] = [
        ChatMessage(
            role="user",
            content="Act as a Python software engineer that needs to write PyDoc for their "
                    "modules, classes and methods.\n"
                    "The PyDoc should be formatted as specified in PEP 257.\n"
                    "The line length of 100 characters should not be exceeded if possible.\n"
                    "The example will follow."
        )
    ]
    default_model_kwargs = ModelKwargs(
        max_tokens=1024,
        model="gpt-3.5-turbo",
        messages=default_messages,
        n=1,
        stop=None,
        temperature=0
    )
    default_prepend_prompt = 'Write Pydoc for the function below and only return the PyDoc:\n\n'

    def __init__(self, model_kwargs: ModelKwargs = None,
                 prepend_prompt: str = default_prepend_prompt, **kwargs):
        self.messages = self.default_messages
        self.model_kwargs: ModelKwargs = model_kwargs or self.default_model_kwargs
        self.prepend_prompt = prepend_prompt

        self.source_code: Optional[str] = None
        self.tree: Optional[AST] = None
        self.latest_response = None
        self.total_token_usage = 0

        openai.api_key = os.getenv("OPENAI_KEY", None)
        if openai.api_key is None:
            raise EnvironmentError("OPENAI_KEY is missing")
        if 'file_path' in kwargs:
            self.load_ast_from_file(kwargs['file_path'])
        if 'line_length' in kwargs:
            self.line_length = kwargs["line_length"]
        else:
            self.line_length = 100

    def load_ast_from_file(self, file_path: Union[(str, Path)]):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
        self.tree: AST = ast.parse(self.source_code)

    def trigger_chat_completion(self) -> None:
        self.latest_response = openai.ChatCompletion.create(**self.model_kwargs)

    def obtain_pydoc(self, text: str = None) -> str:
        if text:
            self.model_kwargs['messages'].append(
                ChatMessage(
                    role='user',
                    content=self.prepend_prompt + text,
                )
            )
        self.trigger_chat_completion()
        latest_message = self.latest_response.choices[0].message
        self.messages.append(ChatMessage(
            role=latest_message.role,
            content=latest_message.content
        ))
        self.total_token_usage += self.latest_response.usage['total_tokens']
        return latest_message.content.strip()

    @staticmethod
    def get_signature(current_method: FunctionDef) -> str:
        method_name: str = current_method.name
        method_arguments: list[str] = list(map((lambda x: x.arg), current_method.args.args))
        method_return_type = (
            None if (current_method.returns is None) else current_method.returns.id)
        return str(tuple((method_name, method_arguments, method_return_type)))

    def write_file_from_ast(self, file_path: Union[(str, Path)], str_return=False) -> Optional[str]:
        new_code: str = ast.unparse(ast_obj=self.tree)
        new_code: str = black.format_str(new_code,
                                         mode=black.Mode(line_length=self.line_length))

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_code)
        if str_return:
            return new_code
        return None

    def add_docstring_to_ast(self, node: FunctionDef, new_docstring: str):
        existing_docstring = ast.get_docstring(node)
        regex_match = re.search(r"\"\"\"([A-Za-z0-9-_\s(),:=*.'->]+)\"\"\"", new_docstring)
        alt_match = re.search(r"```([A-Za-z0-9-_\s(),:=*.'->\"]+)```", new_docstring)
        if regex_match:
            clean_docstring = regex_match.group(1)
        elif alt_match:
            clean_docstring = alt_match.group(1)
        else:
            clean_docstring = "The docstring could not be extracted."
        docstring_node = ast.Expr(value=ast.Str(s=clean_docstring))
        if existing_docstring:
            node.body[0] = docstring_node
        else:
            node.body.insert(0, docstring_node)

    def generate_documentation(self, method_visitor):
        method_visitor.visit(self.tree)
