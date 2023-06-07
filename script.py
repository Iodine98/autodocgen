import logging
import time

from src.autodocgen.method_visitor import FileVisitor
from src.autodocgen.ast_analyzer import ASTAnalyzer

logging.getLogger().setLevel(logging.INFO)


def main():
    start_time = time.time()
    ast_analyzer = ASTAnalyzer()
    ast_analyzer.load_ast_from_file('./src/autodocgen/ast_analyzer.py')
    method_visitor = FileVisitor(ast_analyzer)
    ast_analyzer.generate_documentation(method_visitor)
    ast_analyzer.write_file_from_ast('./ast_analyzer_documented.py')
    end_time = time.time()
    logging.info("Executed in %ds", end_time - start_time)


if __name__ == '__main__':
    main()
