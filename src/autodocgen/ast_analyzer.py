
import ast
import re
from pathlib import Path
import astunparse
from _ast import FunctionDef, AST
from typing import Tuple, Union, Optional
import openai
import dotenv
import os

class MethodVisitor(ast.NodeVisitor):

    def __init__(self):
        self.methods = []

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        self.methods.append(node)

class ASTAnalyzer():

    def __init__(self, model_name='text-davinci-003', model_kwargs: dict=None, method_visitor: MethodVisitor=MethodVisitor(), prepend_prompt: str='Write Pydoc for the function below and only return the PyDoc:\n\n', **kwargs):
        self.source_code: str = None
        self.tree: AST = None
        self.tree_visitor: MethodVisitor = method_visitor
        dotenv.load_dotenv()
        openai.api_key = os.getenv('OPENAI_KEY', None)
        if (openai.api_key is None):
            raise EnvironmentError('OPENAI_KEY is missing')
        self.prepend_prompt = prepend_prompt
        self.model_kwargs = ({'engine': model_name, 'max_tokens': 1024, 'n': 1, 'stop': None, 'temperature': 0} | ({} if (model_kwargs is None) else model_kwargs))
        if ('file_path' in kwargs):
            self.load_ast_from_file(kwargs['file_path'])

    def load_ast_from_file(self, file_path: Union[(str, Path)]):
        with open(file_path) as file:
            self.source_code = file.read()
        self.tree: AST = ast.parse(self.source_code)
        self.tree_visitor.visit(self.tree)

    def obtain_pydoc(self, text) -> Tuple[(str, int)]:
        response = openai.Completion.create(self.model_kwargs, prompt=(self.prepend_prompt + text))
        return (response.choices[0].text.strip(), response.usage['total_tokens'])

    @staticmethod
    def get_signature(current_method: FunctionDef) -> str:
        method_name = current_method.name
        method_arguments = list(map((lambda x: x.arg), current_method.args.args))
        method_return_type = (None if (current_method.returns is None) else current_method.returns.id)
        return str(tuple(method_name, method_arguments, method_return_type))

    @staticmethod
    def add_docstring_to_ast(node, docstring):
        clean_docstring = re.sub('\\\\n', '\n', docstring.strip().replace("'", ''), 0, re.MULTILINE)
        docstring_node = ast.parse(clean_docstring)
        node.body.insert(0, docstring_node)

    def write_file_from_ast(self, file_path: Union[(str, Path)], str_return=False) -> Optional[str]:
        new_code: str = astunparse.unparse(tree=self.tree)
        with open(file_path, 'w') as file:
            file.write(new_code)
        if str_return:
            return new_code

    def generate_documentation(self):
        for method in self.tree_visitor.methods[:1]:
            method_body = ast.get_source_segment(self.source_code, method)
            (documentation, token_count) = self.obtain_pydoc(method_body)
            print(method.name)
            print('\n')
            print(('Tokens: ' + str(token_count)))
            print(documentation)
            self.add_docstring_to_ast(method, documentation)
