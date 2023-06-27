from _ast import ClassDef, FunctionDef
from typing import Union
from src.autodocgen.ast_analyzer import ASTAnalyzer
from src.autodocgen.file_visitor import FileVisitor
DocGenDef = Union[ClassDef, FunctionDef]

