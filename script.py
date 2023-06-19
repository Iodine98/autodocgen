import logging
import time

from src.autodocgen.file_visitor import FileVisitor
from src.autodocgen.ast_analyzer import ASTAnalyzer

logging.getLogger().setLevel(logging.INFO)


def main():
    """
    An example script to demonstrate its workings
    :return: None
    """
    start_time = time.time()
    ast_analyzer = ASTAnalyzer()
    ast_analyzer.load_ast_from_file('./src/autodocgen/file_visitor.py')
    file_visitor = FileVisitor(ast_analyzer)
    ast_analyzer.generate_documentation(file_visitor)
    ast_analyzer.write_file_from_ast('./file_visitor_doc.py')
    end_time = time.time()
    logging.info("Executed in %ds", end_time - start_time)


if __name__ == '__main__':
    main()
