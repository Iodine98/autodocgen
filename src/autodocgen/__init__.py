from _ast import ClassDef, FunctionDef
from typing import Union
from .ast_analyzer import ASTAnalyzer
from .file_visitor import FileVisitor
DocGenDef = Union[ClassDef, FunctionDef]

