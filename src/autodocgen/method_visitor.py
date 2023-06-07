import ast
import logging
import random
import time

import astor
from _ast import FunctionDef, ClassDef, AST

from openai.error import RateLimitError

from src.autodocgen import DocGenDef
from src.autodocgen.ast_analyzer import ASTAnalyzer


class MethodVisitor(ast.NodeTransformer):

    def __init__(self, file_visitor: 'FileVisitor'):
        self.file_visitor = file_visitor

    def visit_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        return self.file_visitor.visit_def(node, 'Function')


class ClassVisitor(ast.NodeTransformer):
    def __init__(self, file_visitor: 'FileVisitor'):
        self.file_visitor = file_visitor

    def visit_ClassDef(self, node: ClassDef) -> ClassDef:
        return self.file_visitor.visit_def(node, 'Class')


class FileVisitor:

    def __init__(self, ast_analyzer: ASTAnalyzer):
        self.ast_analyzer = ast_analyzer
        self.class_visitor = ClassVisitor(self)
        self.method_visitor = MethodVisitor(self)

    def obtain_pydoc_wrapper(self, node: DocGenDef, source_code: str) -> str:
        try:
            return self.ast_analyzer.obtain_pydoc(source_code)
        except RateLimitError:
            time.sleep(random.randint(5, 10))
            return self.obtain_pydoc_wrapper(node, source_code)

    def visit_def(self, node: DocGenDef, str_type: str) -> DocGenDef:
        time.sleep(random.randint(2, 5))
        logging.info("%s name: %s", str_type, node.name)
        source_code = astor.to_source(node)
        response = self.obtain_pydoc_wrapper(node, source_code)
        logging.info(response)
        self.ast_analyzer.add_docstring_to_ast(node, new_docstring=response)
        return node

    def visit(self, tree: AST):
        self.class_visitor.visit(tree)
        self.ast_analyzer.remove_messages()
        self.method_visitor.visit(tree)
        self.ast_analyzer.remove_messages()
