import ast
import logging
import random
import time

import astor
from _ast import FunctionDef

from openai.error import RateLimitError

from src.autodocgen.ast_analyzer import ASTAnalyzer


class MethodVisitor(ast.NodeTransformer):

    def __init__(self, ast_analyzer: ASTAnalyzer):
        self.ast_analyzer = ast_analyzer
        self.stop_loop = False

    def obtain_pydoc_wrapper(self, node: FunctionDef, source_code: str) -> str:
        try:
            return self.ast_analyzer.obtain_pydoc(source_code)
        except RateLimitError:
            time.sleep(random.randint(5, 10))
            return self.obtain_pydoc_wrapper(node, source_code)

    def visit_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        # if self.stop_loop:
        #     return node
        # self.stop_loop = True
        time.sleep(random.randint(2, 5))
        logging.info("Method name: %s", node.name)
        source_code = astor.to_source(node)
        response = self.obtain_pydoc_wrapper(node, source_code)
        logging.info(response)
        self.ast_analyzer.add_docstring_to_ast(node, new_docstring=response)
        return node

