import ast
import astor
from _ast import FunctionDef

from src.autodocgen import ASTAnalyzer


class MethodVisitor(ast.NodeVisitor):

    def __init__(self, ast_analyzer: ASTAnalyzer):
        self.ast_analyzer = ast_analyzer

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        function_code = astor.to_source(node)
        response, _ = self.ast_analyzer.obtain_pydoc(function_code)
        self.ast_analyzer.add_docstring_to_ast(node, docstring=response)


