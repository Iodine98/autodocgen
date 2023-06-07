import ast
import astor
import re
from pathlib import Path
import astunparse
from _ast import FunctionDef, AST
from typing import Tuple, Union, Optional, List, Any
import openai
import dotenv
import os

from src.autodocgen.method_visitor import MethodVisitor


class ASTAnalyzer:

    def __init__(self, model_name='text-davinci-003', model_kwargs: dict = None,
                 prepend_prompt: str = 'Write Pydoc for the function below and only return the '
                                       'PyDoc:\n\n',
                 **kwargs):
        self.source_code: Optional[str] = None
        self.tree: Optional[AST] = None
        dotenv.load_dotenv()
        openai.api_key = os.getenv('OPENAI_KEY', None)
        if openai.api_key is None:
            raise EnvironmentError('OPENAI_KEY is missing')
        self.prepend_prompt = prepend_prompt
        self.model_kwargs = ({'engine': model_name, 'max_tokens': 1024, 'n': 1, 'stop': None,
                              'temperature': 0} | ({} if (model_kwargs is None) else model_kwargs))
        if 'file_path' in kwargs:
            self.load_ast_from_file(kwargs['file_path'])

    def load_ast_from_file(self, file_path: Union[(str, Path)]):
        with open(file_path) as file:
            self.source_code = file.read()
        self.tree: AST = ast.parse(self.source_code)

    def obtain_pydoc(self, text) -> Tuple[str, int]:
        response = openai.Completion.create(
            prompt=(self.prepend_prompt + text),
            **self.model_kwargs)
        return response.choices[0].text.strip(), response.usage['total_tokens']

    @staticmethod
    def get_signature(current_method: FunctionDef) -> str:
        method_name: str = current_method.name
        method_arguments: list[str] = list(map((lambda x: x.arg), current_method.args.args))
        method_return_type = (
            None if (current_method.returns is None) else current_method.returns.id)
        return str(tuple((method_name, method_arguments, method_return_type)))

    def write_file_from_ast(self, file_path: Union[(str, Path)], str_return=False) -> Optional[str]:
        new_code: str = astunparse.unparse(tree=self.tree)
        with open(file_path, 'w') as file:
            file.write(new_code)
        if str_return:
            return new_code

    @staticmethod
    def add_docstring_to_ast(node, docstring):
        clean_docstring = docstring.replace("\"\"\"", "")
        docstring_node = ast.Expr(value=ast.Str(s=clean_docstring))
        node.body.insert(0, docstring_node)

    def generate_documentation(self, method_visitor: 'MethodVisitor'):
        method_visitor.visit(self.tree)
